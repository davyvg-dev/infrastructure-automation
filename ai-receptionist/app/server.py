"""FastAPI server: serves the web chat widget and hosts the WhatsApp (Twilio) webhook.

All channels share the conversation store in `sessions.py`, so the web widget, Telegram
bot, and WhatsApp all talk to the same receptionist.
"""

from __future__ import annotations

import logging
import os
import threading
import time
import uuid
from collections import deque
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from . import sessions
from .channels import whatsapp
from .settings import business, ensure_dirs

log = logging.getLogger(__name__)

app = FastAPI(title="AI Receptionist demo")
_WEB = Path(__file__).resolve().parent.parent / "web"

# Per-IP sliding-window rate limit on /chat: every request is a paid Claude call, so an
# open endpoint is a token-cost hole. Behind Caddy/nginx the client IP comes from
# X-Forwarded-For; bare-exposed, request.client is used (spoofable — deploy behind a proxy).
_RATE_LIMIT_PER_MINUTE = int(os.getenv("CHAT_RATE_LIMIT_PER_MINUTE", "20"))
_rate_lock = threading.Lock()
_hits: dict[str, deque[float]] = {}


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _rate_ok(ip: str) -> bool:
    now = time.monotonic()
    with _rate_lock:
        if len(_hits) > 10_000:  # crude memory bound under address-spraying
            _hits.clear()
        window = _hits.setdefault(ip, deque())
        while window and now - window[0] > 60:
            window.popleft()
        if len(window) >= _RATE_LIMIT_PER_MINUTE:
            return False
        window.append(now)
        return True


class ChatIn(BaseModel):
    session_id: str | None = None
    message: str = Field(max_length=2000)


class ChatOut(BaseModel):
    session_id: str
    reply: str


@app.get("/")
def index() -> FileResponse:
    return FileResponse(_WEB / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    # Liveness probe for Caddy/Uptime Kuma; also confirms the config loads.
    return {"status": "ok", "business": business()["business"]["name"]}


@app.get("/config")
def config() -> dict[str, str]:
    b = business()["business"]
    return {"name": b["name"], "greeting": sessions.greeting()}


@app.post("/chat", response_model=ChatOut)
def chat(body: ChatIn, request: Request) -> ChatOut:
    # Sync def → FastAPI runs it in a threadpool, so the blocking Claude call is fine.
    api_key = os.getenv("CHAT_API_KEY")
    if api_key and request.headers.get("x-api-key") != api_key:
        raise HTTPException(status_code=401, detail="Invalid API key.")
    if not _rate_ok(_client_ip(request)):
        raise HTTPException(status_code=429, detail="Too many messages — try again in a minute.")
    session_id = body.session_id or uuid.uuid4().hex
    try:
        reply = sessions.respond("web", session_id, body.message)
    except Exception:
        log.exception("chat turn failed (session %s)", session_id)
        raise HTTPException(status_code=503, detail="The receptionist is temporarily unavailable.")
    return ChatOut(session_id=session_id, reply=reply)


@app.post("/whatsapp")
async def whatsapp_webhook(request: Request) -> Response:
    form = await request.form()
    params = {k: str(v) for k, v in form.items()}
    signature = request.headers.get("X-Twilio-Signature")
    body, status = await run_in_threadpool(
        whatsapp.handle, str(request.url), signature, params
    )
    return Response(content=body, media_type="application/xml", status_code=status)


def main() -> None:
    import uvicorn

    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    ensure_dirs()
    # Default binds localhost; set HOST=0.0.0.0 when serving behind Caddy on the VPS.
    uvicorn.run(
        "app.server:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
        reload=False,
    )


if __name__ == "__main__":
    main()
