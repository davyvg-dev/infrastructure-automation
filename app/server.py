"""FastAPI server: serves the web chat widget and hosts the WhatsApp (Twilio) webhook.

All channels share the conversation store in `sessions.py`, so the web widget, Telegram
bot, and WhatsApp all talk to the same receptionist.
"""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from . import sessions
from .channels import whatsapp
from .settings import business, ensure_dirs

app = FastAPI(title="AI Receptionist demo")
_WEB = Path(__file__).resolve().parent.parent / "web"


class ChatIn(BaseModel):
    session_id: str | None = None
    message: str


class ChatOut(BaseModel):
    session_id: str
    reply: str


@app.get("/")
def index() -> FileResponse:
    return FileResponse(_WEB / "index.html")


@app.get("/config")
def config() -> dict[str, str]:
    b = business()["business"]
    return {"name": b["name"], "greeting": sessions.greeting()}


@app.post("/chat", response_model=ChatOut)
def chat(body: ChatIn) -> ChatOut:
    # Sync def → FastAPI runs it in a threadpool, so the blocking Claude call is fine.
    session_id = body.session_id or uuid.uuid4().hex
    reply = sessions.respond("web", session_id, body.message)
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

    ensure_dirs()
    uvicorn.run("app.server:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
