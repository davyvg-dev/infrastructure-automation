"""Notify the owner (you) about bookings and anything the bot can't handle.

Sends a Telegram message via the HTTP API (no extra dependency). Customer messages taken
by the bot are additionally persisted to a per-client data/messages-<slug>.json, so a lead
survives even when Telegram is down or unconfigured — the bot must never claim "delivered"
for a message that only hit stdout — AND every lead carries the client it belongs to, so
one client's leads never pile into another's.

Alerts are tenant-aware: a client config may set its own recipient, else the alert goes to
the founder's OWNER_TELEGRAM_CHAT_ID. Either way the message is prefixed with the business
name so a multi-client founder always knows which bot fired.

Config (in .env):
  OWNER_TELEGRAM_CHAT_ID   your personal chat id (message the bot once, then get it)
  NOTIFY_TELEGRAM_TOKEN    optional; defaults to TELEGRAM_BOT_TOKEN (the receptionist bot)
Per-client override (in config/clients/<slug>.yaml):
  notify:
    telegram_chat_id: "..."   # this client's own recipient for their leads/bookings
"""

from __future__ import annotations

import json
import os
import threading
import time
import traceback
import urllib.request
from datetime import datetime
from typing import Any

from . import settings
from .settings import active_client, business, ensure_dirs

_LOCK = threading.Lock()


def _messages_path(client: str):
    # settings.DATA_DIR at call time (not import time) so tests can redirect it, like analytics.
    return settings.DATA_DIR / f"messages-{client}.json"


def _client_chat_id() -> str | None:
    """This client's own Telegram recipient, if their config sets notify.telegram_chat_id."""
    try:
        return ((business().get("notify") or {}).get("telegram_chat_id")) or None
    except Exception:
        return None


def _business_name(client: str) -> str:
    try:
        return business()["business"]["name"]
    except Exception:
        return client


def owner(text: str, chat_id: str | None = None) -> bool:
    """Ping a recipient on Telegram (a specific chat_id, else the founder). True on success."""
    token = os.getenv("NOTIFY_TELEGRAM_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = chat_id or os.getenv("OWNER_TELEGRAM_CHAT_ID")
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


# --- Error reporting: PII-scrubbed stack traces to the founder ---------------------------
# When the receptionist hits an unhandled error, send the founder the stack trace (exception
# type + message + frames, NEVER local-variable values — that omission is the privacy win
# over Sentry) through the same owner() Telegram seam. €0, no new vendor, no GDPR
# sub-processor. Kept behind this one helper so a later swap to Sentry/GlitchTip, if error
# volume ever justifies it, is a small change.

# Dedup so a crash loop can't spam Telegram. Signature = exc type + the innermost frame's
# location; the same error is suppressed for this many seconds after it first fires.
_ERR_DEDUP_SECONDS = int(os.getenv("NOTIFY_ERROR_DEDUP_SECONDS", "600"))
_err_lock = threading.Lock()
_err_last_sent: dict[str, float] = {}


def _error_signature(exc: BaseException) -> str:
    """Stable key for an error: its type + the file:line where it was raised. Two crashes at
    the same site with the same type dedup together; a crash elsewhere still gets through."""
    tb = exc.__traceback__
    innermost = None
    while tb is not None:
        innermost = tb
        tb = tb.tb_next
    where = f"{innermost.tb_frame.f_code.co_filename}:{innermost.tb_lineno}" if innermost else "?"
    return f"{type(exc).__name__}@{where}"


def _dedup_ok(signature: str) -> bool:
    """True (and records now) if this signature hasn't fired inside the dedup window."""
    now = time.monotonic()
    with _err_lock:
        if len(_err_last_sent) > 1000:  # crude memory bound against many distinct crash sites
            _err_last_sent.clear()
        last = _err_last_sent.get(signature)
        if last is not None and now - last < _ERR_DEDUP_SECONDS:
            return False
        _err_last_sent[signature] = now
        return True


def owner_exception(exc: BaseException, *, context: str = "") -> bool:
    """Report an unhandled receptionist error to the founder as a PII-scrubbed stack trace.

    Formats type + message + stack (never local-variable values), masks any phone/email that
    leaked into the text, and dedups so a crash loop can't spam Telegram. Never raises — a
    reporting failure must not break the conversation that triggered it.
    """
    try:
        if not _dedup_ok(_error_signature(exc)):
            return False
        trace = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        # Lazy import: oversight imports notify, so importing it at module top is circular.
        from .oversight import redact

        header = f"⚠ receptionist error [{context}]" if context else "⚠ receptionist error"
        return owner(f"{header}\n{redact(trace)}")
    except Exception as report_exc:  # reporting must never break a conversation
        print(f"[notify:owner_exception] failed to report ({report_exc})")
        return False


def take_message(customer: str, contact: str, message: str) -> dict[str, Any]:
    """Persist a customer message for the active client, then ping that client's recipient.

    Returns {"ok", "saved", "notified"} reflecting what actually happened, so the
    receptionist can be honest with the customer when neither channel worked.
    """
    client = active_client()
    saved = _save_message(client, customer, contact, message)
    notified = owner(
        f"[{_business_name(client)}] Message from {customer} ({contact}):\n{message}",
        chat_id=_client_chat_id(),
    )
    return {"ok": saved or notified, "saved": saved, "notified": notified}


def _save_message(client: str, customer: str, contact: str, message: str) -> bool:
    try:
        with _LOCK:
            ensure_dirs()
            path = _messages_path(client)
            messages: list[dict[str, Any]] = []
            if path.exists():
                with path.open(encoding="utf-8") as fh:
                    messages = json.load(fh)
            messages.append(
                {
                    "at": datetime.now().isoformat(timespec="seconds"),
                    "client": client,
                    "customer_name": customer,
                    "contact": contact,
                    "message": message,
                }
            )
            tmp = path.with_suffix(".json.tmp")
            with tmp.open("w", encoding="utf-8") as fh:
                json.dump(messages, fh, ensure_ascii=False, indent=2)
            tmp.replace(path)
        return True
    except Exception as exc:
        print(f"[notify:take_message] persist failed ({exc})")
        return False
