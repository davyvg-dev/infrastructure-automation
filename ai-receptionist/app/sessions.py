"""Shared conversation store used by every channel (web, Telegram, WhatsApp).

One receptionist, one place that maps a channel + user to their history. Channels stay
thin: they receive a message, call `respond`, and send the reply back.

In-memory is fine for a demo. To productionize, back `_STORE` with Redis/Postgres — the
seam is just these three functions. Because the store is per-process, the server must run
as a SINGLE worker (uvicorn default); multiple workers would each hold their own sessions.

Turns are serialized per conversation: a rapid double-send from the same user waits for
the first turn instead of racing it and losing history. Different users run concurrently.
"""

from __future__ import annotations

import threading
from typing import Any

from . import analytics, receptionist
from .settings import active_client, business

# key = "<client>:<channel>:<user_id>"  ->  conversation history
_STORE: dict[str, list[dict[str, Any]]] = {}
_locks: dict[str, threading.Lock] = {}
_meta_lock = threading.Lock()


def _lock_for(key: str) -> threading.Lock:
    with _meta_lock:
        return _locks.setdefault(key, threading.Lock())

# Keep memory (and token cost) bounded on long-running channels. Trims to a safe boundary
# so we never split a tool_use / tool_result pair.
_MAX_MESSAGES = 40


def _trim(history: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(history) <= _MAX_MESSAGES:
        return history
    # Cut at the start of an exchange: a user turn whose content is a plain string
    # (customer message), never a tool_result list.
    for i in range(len(history) - _MAX_MESSAGES, len(history)):
        m = history[i]
        if m["role"] == "user" and isinstance(m["content"], str):
            return history[i:]
    return history[-_MAX_MESSAGES:]


def respond(channel: str, user_id: str, text: str) -> str:
    client = active_client()
    key = f"{client}:{channel}:{user_id}"
    telemetry: dict[str, Any] = {"input_tokens": 0, "output_tokens": 0, "tools": [], "model": ""}
    with _lock_for(key):
        history = _STORE.get(key, [])
        reply, history = receptionist.run_turn(history, text, telemetry=telemetry)
        _STORE[key] = _trim(history)
    # Durable capture happens outside the conversation lock (its own store, its own lock) and
    # never raises — a capture failure must not cost the customer a reply.
    analytics.record_turn(
        client=client,
        channel=channel,
        user_id=user_id,
        user_text=text,
        reply=reply,
        input_tokens=telemetry["input_tokens"],
        output_tokens=telemetry["output_tokens"],
        model=telemetry["model"],
        tools=telemetry["tools"],
        after_hours=analytics.is_after_hours(business()),
    )
    return reply


def reset(channel: str, user_id: str) -> None:
    key = f"{active_client()}:{channel}:{user_id}"
    with _lock_for(key):
        _STORE.pop(key, None)


def greeting() -> str:
    return receptionist.greeting()
