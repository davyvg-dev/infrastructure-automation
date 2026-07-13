"""Notify the owner (you) about bookings and anything the bot can't handle.

Sends a Telegram message via the HTTP API (no extra dependency). Customer messages taken
by the bot are additionally persisted to data/messages.json, so a lead survives even when
Telegram is down or unconfigured — the bot must never claim "delivered" for a message
that only hit stdout.

Config (in .env):
  OWNER_TELEGRAM_CHAT_ID   your personal chat id (message the bot once, then get it)
  NOTIFY_TELEGRAM_TOKEN    optional; defaults to TELEGRAM_BOT_TOKEN (the receptionist bot)
"""

from __future__ import annotations

import json
import os
import threading
import urllib.request
from datetime import datetime
from typing import Any

from .settings import DATA_DIR, ensure_dirs

_MESSAGES_PATH = DATA_DIR / "messages.json"
_LOCK = threading.Lock()


def owner(text: str) -> bool:
    """Ping the owner on Telegram. Returns True only when the send succeeded."""
    token = os.getenv("NOTIFY_TELEGRAM_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("OWNER_TELEGRAM_CHAT_ID")
    if not (token and chat_id):
        print(f"[notify:owner] {text}")  # dev fallback — configure OWNER_TELEGRAM_CHAT_ID
        return False
    try:
        data = json.dumps({"chat_id": chat_id, "text": text}).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=10).read()
        return True
    except Exception as exc:  # never let a notification failure break the conversation
        print(f"[notify:owner] send failed ({exc}); message was: {text}")
        return False


def take_message(customer: str, contact: str, message: str) -> dict[str, Any]:
    """Persist a customer message to disk, then ping the owner.

    Returns {"ok", "saved", "notified"} reflecting what actually happened, so the
    receptionist can be honest with the customer when neither channel worked.
    """
    saved = _save_message(customer, contact, message)
    notified = owner(f"📨 Message from {customer} ({contact}):\n{message}")
    return {"ok": saved or notified, "saved": saved, "notified": notified}


def _save_message(customer: str, contact: str, message: str) -> bool:
    try:
        with _LOCK:
            ensure_dirs()
            messages: list[dict[str, Any]] = []
            if _MESSAGES_PATH.exists():
                with _MESSAGES_PATH.open(encoding="utf-8") as fh:
                    messages = json.load(fh)
            messages.append({
                "at": datetime.now().isoformat(timespec="seconds"),
                "customer_name": customer,
                "contact": contact,
                "message": message,
            })
            tmp = _MESSAGES_PATH.with_suffix(".json.tmp")
            with tmp.open("w", encoding="utf-8") as fh:
                json.dump(messages, fh, ensure_ascii=False, indent=2)
            tmp.replace(_MESSAGES_PATH)
        return True
    except Exception as exc:
        print(f"[notify:take_message] persist failed ({exc})")
        return False
