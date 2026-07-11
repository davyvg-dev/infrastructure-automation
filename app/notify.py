"""Notify the owner (you) about bookings and anything the bot can't handle.

Sends a Telegram message via the HTTP API (no extra dependency). If the owner's chat isn't
configured, it falls back to printing — so the demo never breaks, it just logs.

Config (in .env):
  OWNER_TELEGRAM_CHAT_ID   your personal chat id (message the bot once, then get it)
  NOTIFY_TELEGRAM_TOKEN    optional; defaults to TELEGRAM_BOT_TOKEN (the receptionist bot)
"""

from __future__ import annotations

import json
import os
import urllib.request


def owner(text: str) -> None:
    token = os.getenv("NOTIFY_TELEGRAM_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("OWNER_TELEGRAM_CHAT_ID")
    if not (token and chat_id):
        print(f"[notify:owner] {text}")  # dev fallback — configure OWNER_TELEGRAM_CHAT_ID
        return
    try:
        data = json.dumps({"chat_id": chat_id, "text": text}).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=10).read()
    except Exception as exc:  # never let a notification failure break the conversation
        print(f"[notify:owner] send failed ({exc}); message was: {text}")
