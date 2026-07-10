"""FastAPI server: serves the chat widget and a /chat endpoint.

Conversation history is kept in memory per session_id — fine for a demo. For production
you'd move sessions to Redis/Postgres, but the seam is just `_SESSIONS`.
"""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from . import receptionist
from .settings import business, ensure_dirs

app = FastAPI(title="AI Receptionist demo")
_WEB = Path(__file__).resolve().parent.parent / "web"

# session_id -> conversation history
_SESSIONS: dict[str, list[dict[str, Any]]] = {}


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
    return {"name": b["name"], "greeting": receptionist.greeting()}


@app.post("/chat", response_model=ChatOut)
def chat(body: ChatIn) -> ChatOut:
    session_id = body.session_id or uuid.uuid4().hex
    history = _SESSIONS.get(session_id, [])
    reply, history = receptionist.run_turn(history, body.message)
    _SESSIONS[session_id] = history
    return ChatOut(session_id=session_id, reply=reply)


def main() -> None:
    import uvicorn

    ensure_dirs()
    uvicorn.run("app.server:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
