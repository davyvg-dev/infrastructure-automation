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
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from . import notify, sessions
from .channels import whatsapp
from .settings import business, clear_slug, ensure_dirs, resolve_slug, use_slug

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


def _activate(request: Request):
    """Bind the request to a client config (by Host subdomain, or an explicit override) for
    the rest of this call. Returns a token to pass to clear_slug() in a finally block."""
    override = request.query_params.get("client") or request.headers.get("x-client-slug")
    return use_slug(resolve_slug(request.headers.get("host"), override))


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


@app.get("/widget.js")
def widget_js() -> FileResponse:
    # The one-line loader a client pastes on their own site. It injects a floating bubble
    # and an iframe back to this origin, so the chat stays same-origin (no CORS, no key
    # leak). index.html is frameable by default (we never send X-Frame-Options); if a proxy
    # sits in front, don't let it add one. Short cache so updates still propagate.
    return FileResponse(
        _WEB / "widget.js",
        media_type="text/javascript",
        headers={"Cache-Control": "public, max-age=300"},
    )


@app.get("/health")
def health(request: Request) -> dict[str, str]:
    # Liveness probe for Caddy/Uptime Kuma; also confirms the (routed) config loads.
    token = _activate(request)
    try:
        return {"status": "ok", "business": business()["business"]["name"]}
    finally:
        clear_slug(token)


@app.get("/config")
def config(request: Request) -> dict[str, str]:
    token = _activate(request)
    try:
        cfg = business()
        return {
            "name": cfg["business"]["name"],
            "greeting": sessions.greeting(),
            # Drives the widget's UI chrome only; defaults to Dutch (the target market).
            "locale": cfg.get("locale", "nl"),
        }
    finally:
        clear_slug(token)


@app.post("/chat", response_model=ChatOut)
def chat(body: ChatIn, request: Request) -> ChatOut:
    # Sync def → FastAPI runs it in a threadpool, so the blocking Claude call is fine.
    api_key = os.getenv("CHAT_API_KEY")
    if api_key and request.headers.get("x-api-key") != api_key:
        raise HTTPException(status_code=401, detail="Invalid API key.")
    if not _rate_ok(_client_ip(request)):
        raise HTTPException(status_code=429, detail="Too many messages — try again in a minute.")
    session_id = body.session_id or uuid.uuid4().hex
    token = _activate(request)
    try:
        reply = sessions.respond("web", session_id, body.message)
    except Exception as exc:
        log.exception("chat turn failed (session %s)", session_id)
        notify.owner_exception(exc, context="chat")
        raise HTTPException(
            status_code=503, detail="The receptionist is temporarily unavailable."
        ) from exc
    finally:
        clear_slug(token)
    return ChatOut(session_id=session_id, reply=reply)


@app.post("/whatsapp")
async def whatsapp_webhook(request: Request) -> Response:
    form = await request.form()
    params = {k: str(v) for k, v in form.items()}
    signature = request.headers.get("X-Twilio-Signature")
    body, status = await run_in_threadpool(whatsapp.handle, str(request.url), signature, params)
    return Response(content=body, media_type="application/xml", status_code=status)


@app.exception_handler(Exception)
async def _report_unhandled(request: Request, exc: Exception) -> Response:
    # Backstop for any route that doesn't report on its own. HTTPException keeps its default
    # handler, so /chat's 503 (already reported above) never reaches here — no double-fire.
    notify.owner_exception(exc, context=request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})


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
