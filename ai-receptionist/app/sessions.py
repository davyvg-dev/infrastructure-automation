"""Shared conversation store used by every channel (web, Telegram, WhatsApp).

One receptionist, one place that maps a channel + user to their history. Channels stay
thin: they receive a message, call `respond`, and send the reply back.

In-memory is fine for a demo. To productionize, back `_STORE` with Redis/Postgres — the
seam is just these three functions.
"""

from __future__ import annotations

from typing import Any

from . import receptionist

# key = "<channel>:<user_id>"  ->  conversation history
_STORE: dict[str, list[dict[str, Any]]] = {}

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
    key = f"{channel}:{user_id}"
    history = _STORE.get(key, [])
    reply, history = receptionist.run_turn(history, text)
    _STORE[key] = _trim(history)
    return reply


def reset(channel: str, user_id: str) -> None:
    _STORE.pop(f"{channel}:{user_id}", None)


def greeting() -> str:
    return receptionist.greeting()
