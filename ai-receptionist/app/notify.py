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
  OWNER_TELEGRAM_CHAT_ID   your personal chat id — message the bot once, then run
                           `python -m app.notify chatid` and paste what it prints
  NOTIFY_TELEGRAM_TOKEN    optional; defaults to TELEGRAM_BOT_TOKEN (the receptionist bot)
  OWNER_EMAIL              fallback inbox for long reports when Telegram is unconfigured
Per-client override (in config/clients/<slug>.yaml):
  notify:
    telegram_chat_id: "..."   # this client's own recipient for their leads/bookings
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
import traceback
import urllib.request
from datetime import datetime
from typing import Any

from . import mailer, settings
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


# --- Long-form ops reports: Telegram first, e-mail as the fallback -----------------------
# The nightly digest timers were delivering into a void: without OWNER_TELEGRAM_CHAT_ID,
# owner() prints to stdout and systemd swallows it into the journal, where nobody looks. A
# report nobody reads is the same as no report. Now that mailer.py exists, e-mail is the
# fallback, so one Resend key (which the welcome mail needs anyway) is enough to make the
# timers real — the Telegram chat id becomes an upgrade instead of a prerequisite.

_TELEGRAM_LIMIT = 4096  # Telegram rejects longer sendMessage bodies outright


def owner_report(subject: str, text: str) -> dict[str, bool]:
    """Deliver a long report to the founder. Returns which channels took it.

    Telegram first, because that is where he actually reads things. E-mail only when
    Telegram did not take it, so a working chat id does not produce two of everything.
    """
    result = {"telegram": False, "email": False}
    if len(text) <= _TELEGRAM_LIMIT:
        result["telegram"] = owner(text)
    if result["telegram"]:
        return result

    recipient = os.getenv("OWNER_EMAIL", "").strip()
    if recipient:
        result["email"] = mailer.send(recipient, subject, text)
    if not result["email"] and len(text) > _TELEGRAM_LIMIT:
        # Too long for Telegram and no mailbox to fall back to. A cut-off digest still
        # beats silence, so send what fits rather than nothing.
        result["telegram"] = owner(text[: _TELEGRAM_LIMIT - 60] + "\n\n[afgekapt: te lang]")
    return result


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


def site_lead(lead: dict[str, Any]) -> dict[str, Any]:
    """Persist a marketing-site signup lead, then ping the founder. Same contract as
    take_message: returns {"ok", "saved", "notified"} so the caller can be honest.

    Leads append to data/leads.jsonl (one JSON object per line) — append-only, so a
    concurrent write can never truncate the file the way a rewrite-in-place could.
    """
    record = {"at": datetime.now().isoformat(timespec="seconds"), **lead}
    saved = _save_lead(record)
    lines = [f"Nieuwe aanmelding via klantkraan.nl — plan: {lead.get('plan', '?')}"]
    for label, key in (
        ("Naam", "naam"),
        ("Bedrijf", "bedrijf"),
        ("Telefoon", "telefoon"),
        ("E-mail", "email"),
        ("Vak", "vak"),
        ("Website", "site"),
        ("Bericht", "bericht"),
    ):
        if lead.get(key):
            lines.append(f"{label}: {lead[key]}")
    try:
        notified = owner("\n".join(lines))
    except Exception as exc:  # notify must never decide the request's fate
        print(f"[notify:site_lead] notify failed ({exc})")
        notified = False
    return {"ok": saved or notified, "saved": saved, "notified": notified}


def find_lead(email: str) -> dict[str, Any] | None:
    """The most recent signup lead for this e-mail, or None. Billing uses it to avoid asking
    a paying customer for something they already typed into the form. Never raises — a
    missing or corrupt lead log means "we don't know", not a failed webhook."""
    wanted = email.strip().lower()
    if not wanted:
        return None
    try:
        path = settings.DATA_DIR / "leads.jsonl"
        if not path.exists():
            return None
        found = None
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if str(record.get("email", "")).strip().lower() == wanted:
                found = record  # keep scanning: the last match is the current one
        return found
    except Exception as exc:
        print(f"[notify:find_lead] lookup failed ({exc})")
        return None


def _save_lead(record: dict[str, Any]) -> bool:
    try:
        with _LOCK:
            ensure_dirs()
            path = settings.DATA_DIR / "leads.jsonl"
            with path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        return True
    except Exception as exc:
        print(f"[notify:site_lead] persist failed ({exc})")
        return False


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


# --- CLI -----------------------------------------------------------------------------------


def chat_ids() -> list[dict[str, str]]:
    """Every chat that has messaged the bot recently, from Telegram's getUpdates.

    This exists so finding OWNER_TELEGRAM_CHAT_ID is one command instead of a hunt through
    a third-party bot. Note getUpdates only returns updates the bot has not consumed, so it
    stays empty while the receptionist's own poller is running — send the message with the
    service stopped, or use a bot that nothing polls.
    """
    token = os.getenv("NOTIFY_TELEGRAM_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("no bot token: set TELEGRAM_BOT_TOKEN (or NOTIFY_TELEGRAM_TOKEN)")
    with urllib.request.urlopen(
        f"https://api.telegram.org/bot{token}/getUpdates", timeout=10
    ) as resp:
        payload = json.loads(resp.read())
    seen: dict[str, dict[str, str]] = {}
    for update in payload.get("result") or []:
        chat = ((update.get("message") or update.get("channel_post") or {}).get("chat")) or {}
        if chat.get("id") is not None:
            seen[str(chat["id"])] = {
                "id": str(chat["id"]),
                "name": chat.get("username") or chat.get("first_name") or chat.get("title") or "",
                "type": chat.get("type", ""),
            }
    return list(seen.values())


# --- Unit-failure alerts: systemd OnFailure= -> founder ----------------------------------
# kk-alert@.service (ops/hetzner) fires `python -m app.notify alert <unit>` whenever any
# Klantkraan unit enters failed state. The alert carries the unit's journal tail so the
# founder sees WHY from his phone, PII-scrubbed through the same redact() the digest uses.
# Delivery via owner_report: Telegram first, e-mail fallback — a failure alert that only
# lands in the journal is the silent-failure hole this exists to close.

_ALERT_JOURNAL_LINES = 20


def _journal_tail(unit: str, lines: int = _ALERT_JOURNAL_LINES) -> str:
    try:
        proc = subprocess.run(
            ["journalctl", "-u", unit, "-n", str(lines), "--no-pager", "-o", "cat"],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        return proc.stdout.strip() or proc.stderr.strip() or "(journal empty)"
    except Exception as exc:  # no journalctl (dev box) must not kill the alert itself
        return f"(journal unavailable: {exc})"


def unit_failed_alert(unit: str) -> dict[str, bool]:
    """Tell the founder a systemd unit failed, with its redacted journal tail attached."""
    # Lazy import: oversight imports notify, so importing it at module top is circular.
    from .oversight import redact

    text = f"⚠ server: {unit} failed\n\n{redact(_journal_tail(unit))}"
    return owner_report(f"[server] {unit} failed", text)


def main(argv: list[str]) -> int:
    cmd = (argv[1:2] or [""])[0]
    if cmd == "alert":
        unit = (argv[2:3] or [""])[0]
        if not unit:
            print("usage: python -m app.notify alert <unit>")
            return 2
        delivered = unit_failed_alert(unit)
        took = [channel for channel, ok in delivered.items() if ok]
        if took:
            print(f"[sent via {', '.join(took)}]")
            return 0
        # owner() already printed the message to stdout as its dev fallback; exit 1 so
        # `systemctl status kk-alert@<unit>` shows the alert itself could not deliver.
        print(
            "[NOT sent — nowhere to deliver it. Set OWNER_TELEGRAM_CHAT_ID "
            "(python -m app.notify chatid), or OWNER_EMAIL + RESEND_API_KEY.]"
        )
        return 1
    if cmd != "chatid":
        print("usage: python -m app.notify {chatid | alert <unit>}")
        return 2
    try:
        found = chat_ids()
    except Exception as exc:
        print(f"❌ {exc}")
        return 1
    if not found:
        print(
            "Geen chats gevonden. Stuur je bot eerst een bericht in Telegram.\n"
            "Draait de receptionist-bot? Die consumeert dezelfde updates — stop hem even "
            "(systemctl stop ai-receptionist) en probeer opnieuw."
        )
        return 1
    for chat in found:
        print(f"OWNER_TELEGRAM_CHAT_ID={chat['id']}    # {chat['type']} {chat['name']}".rstrip())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
