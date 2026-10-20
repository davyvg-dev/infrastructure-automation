"""Human takeover for WhatsApp conversations, driven from the founder's Telegram.

The bot answers every WhatsApp message until the founder says otherwise. Taking over pauses
the bot for ONE conversation: customer messages relay to the founder's Telegram, and what
the founder types there goes back to the customer over WhatsApp (freeform — the customer
just messaged, so we are inside the 24h service window). Releasing resets that session, so
the bot re-enters fresh instead of with a hole in its memory where the human spoke.

Commands (message the notify bot on Telegram, owner chat only):
    wa                     list recent WhatsApp conversations
    takeover <n|+316...>   pause the bot there; your next messages go to that customer
    release [n|all]        hand the conversation back to the bot
    <anything else>        relayed to the customer you took over

Runs as a getUpdates long-poll thread inside the FastAPI server (started from server.py),
so no extra process or systemd unit. It consumes updates for its token: if the customer
-facing Telegram channel ever runs on the same token, give this its own bot via
TAKEOVER_TELEGRAM_TOKEN — two pollers on one token conflict.

State survives restarts in data/takeover.json: a forgotten pause must not silently
resurrect the bot mid-human-conversation. TAKEOVER_AUTO_RELEASE_HOURS (default 12) is the
backstop for the opposite failure — a pause forgotten for good.
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
import urllib.parse
import urllib.request
from datetime import datetime
from typing import Any

from . import notify, sessions, settings
from .settings import active_client, clear_slug, ensure_dirs, use_slug

log = logging.getLogger(__name__)

_LOCK = threading.Lock()
_MAX_CONTACTS = 20
_PREVIEW_LEN = 60


def _path():
    return settings.DATA_DIR / "takeover.json"


def _load() -> dict[str, Any]:
    try:
        with _path().open(encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return {}


def _save(state: dict[str, Any]) -> None:
    ensure_dirs()
    tmp = _path().with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(state, fh, ensure_ascii=False, indent=2)
    tmp.replace(_path())


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _auto_release_hours() -> float:
    try:
        return float(os.getenv("TAKEOVER_AUTO_RELEASE_HOURS", "12"))
    except ValueError:
        return 12.0


def _key(client: str, sender: str) -> str:
    return f"{client}:whatsapp:{sender}"


def _short(number: str) -> str:
    return number.split(":", 1)[-1]


# --- state transitions (shared by webhook thread and poller thread) ----------------------


def _record_contact(state: dict[str, Any], client: str, sender: str, preview: str) -> None:
    contacts = [c for c in state.get("contacts", []) if c.get("sender") != sender]
    contacts.insert(
        0,
        {"client": client, "sender": sender, "at": _now(), "preview": preview[:_PREVIEW_LEN]},
    )
    state["contacts"] = contacts[:_MAX_CONTACTS]


def _release(state: dict[str, Any], key: str) -> None:
    entry = state.get("paused", {}).pop(key, None)
    if state.get("target") == key:
        state["target"] = None
    if entry:
        # Fresh session on hand-back: the bot never saw the human exchange, so continuing
        # the old history would mean answering with a hole in its memory. Setting the slug
        # to the recorded client label reproduces the session key exactly (active_client()
        # returns the raw contextvar value, default stem included).
        token = use_slug(entry["client"])
        try:
            sessions.reset("whatsapp", entry["sender"])
        finally:
            clear_slug(token)


def _stale(entry: dict[str, Any]) -> bool:
    try:
        last = datetime.fromisoformat(entry.get("last") or entry.get("since"))
    except (TypeError, ValueError):
        return True
    return (datetime.now() - last).total_seconds() > _auto_release_hours() * 3600


def handle_inbound(sender: str, text: str) -> bool:
    """Called by the WhatsApp webhook for every inbound message (inside the tenant slug
    context). True = conversation is taken over: message relayed to the founder, bot must
    stay silent. False = bot answers normally."""
    client = active_client()
    key = _key(client, sender)
    with _LOCK:
        state = _load()
        _record_contact(state, client, sender, text)
        entry = (state.get("paused") or {}).get(key)
        if entry and _stale(entry):
            _release(state, key)
            entry = None
            notify.owner(
                f"Overname van {_short(sender)} automatisch beëindigd "
                f"(> {_auto_release_hours():g} uur stil) — de bot antwoordt weer."
            )
        if entry:
            entry["last"] = _now()
        _save(state)
    if not entry:
        return False
    delivered = notify.owner(f"[{client}] {_short(sender)}:\n{text}")
    if not delivered:
        # The founder can't see the relay — better a bot answer than silence at both ends.
        log.warning("takeover relay to founder failed; releasing %s", key)
        with _LOCK:
            state = _load()
            _release(state, key)
            _save(state)
        return False
    return True


# --- founder commands (Telegram poller thread) -------------------------------------------


def _fmt_contacts(state: dict[str, Any]) -> str:
    contacts = state.get("contacts", [])
    if not contacts:
        return "Nog geen WhatsApp-gesprekken gezien."
    paused = state.get("paused") or {}
    lines = ["WhatsApp-gesprekken:"]
    for i, c in enumerate(contacts, 1):
        mark = "  ← overgenomen" if _key(c["client"], c["sender"]) in paused else ""
        when = c["at"][11:16] if len(c.get("at", "")) >= 16 else c.get("at", "")
        lines.append(f"{i}. {_short(c['sender'])} · {c['client']} · {when} · “{c['preview']}”{mark}")
    lines.append("\ntakeover <nr> om over te nemen · release [nr|all] om terug te geven")
    return "\n".join(lines)


def _find_contact(state: dict[str, Any], ref: str) -> dict[str, Any] | None:
    contacts = state.get("contacts", [])
    if ref.isdigit() and 1 <= int(ref) <= len(contacts):
        return contacts[int(ref) - 1]
    wanted = settings._normalize_number(ref)
    for c in contacts:
        if wanted and settings._normalize_number(c["sender"]) == wanted:
            return c
    return None


def handle_owner_command(text: str) -> str:
    """One founder message in, one reply out. Pure state logic — the poller does Telegram."""
    words = text.strip().lstrip("/").split()
    cmd = words[0].lower() if words else ""
    arg = " ".join(words[1:])  # one argument, so "+31 6 12 34 56 78" survives the split
    with _LOCK:
        state = _load()

        if cmd == "wa":
            return _fmt_contacts(state)

        if cmd == "takeover":
            if not arg:
                return "Gebruik: takeover <nr uit 'wa'> of takeover +316..."
            contact = _find_contact(state, arg)
            if not contact:
                return f"Geen gesprek gevonden voor '{arg}'. Typ 'wa' voor de lijst."
            key = _key(contact["client"], contact["sender"])
            state.setdefault("paused", {})[key] = {
                "client": contact["client"],
                "sender": contact["sender"],
                "since": _now(),
                "last": _now(),
            }
            state["target"] = key
            _save(state)
            return (
                f"Overgenomen: {_short(contact['sender'])} ({contact['client']}).\n"
                f"Laatste bericht: “{contact['preview']}”\n"
                "Alles wat je hier typt gaat nu naar deze klant. 'release' geeft terug."
            )

        if cmd == "release":
            paused = state.get("paused") or {}
            if not paused:
                return "Er is niets overgenomen."
            if arg.lower() == "all":
                for key in list(paused):
                    _release(state, key)
                _save(state)
                return "Alle gesprekken terug naar de bot."
            key = state.get("target")
            if arg:
                contact = _find_contact(state, arg)
                key = _key(contact["client"], contact["sender"]) if contact else None
            if not key or key not in paused:
                return "Geen (actief) overgenomen gesprek gevonden. Typ 'wa' voor de lijst."
            sender = paused[key]["sender"]
            _release(state, key)
            _save(state)
            return f"{_short(sender)} terug naar de bot (sessie opnieuw gestart)."

        if cmd == "help":
            return (
                "wa — recente WhatsApp-gesprekken\n"
                "takeover <nr|+316...> — bot pauzeren, jij antwoordt\n"
                "release [nr|all] — terug naar de bot\n"
                "Alle andere tekst gaat naar de klant die je hebt overgenomen."
            )

        target = state.get("target")
        entry = (state.get("paused") or {}).get(target) if target else None
        if not entry:
            return (
                "Geen gesprek overgenomen — dit bericht is nergens heen gestuurd.\n"
                "Typ 'wa' voor gesprekken, 'help' voor uitleg."
            )
        entry["last"] = _now()
        _save(state)
        sender = entry["sender"]
    # Send outside the lock: a slow Twilio call must not block the WhatsApp webhook.
    from .channels import whatsapp

    try:
        whatsapp.send(sender, text)
    except Exception as exc:
        log.warning("takeover send to %s failed: %s", sender, exc)
        return f"NIET afgeleverd bij {_short(sender)}: {exc}"
    return f"→ {_short(sender)}"


# --- Telegram long-poll thread ------------------------------------------------------------


def _token() -> str | None:
    return (
        os.getenv("TAKEOVER_TELEGRAM_TOKEN")
        or os.getenv("NOTIFY_TELEGRAM_TOKEN")
        or os.getenv("TELEGRAM_BOT_TOKEN")
    )


def _api(token: str, method: str, **params: Any) -> dict[str, Any]:
    query = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    with urllib.request.urlopen(
        f"https://api.telegram.org/bot{token}/{method}?{query}", timeout=70
    ) as resp:
        return json.loads(resp.read())


def _poll_once(token: str, owner_chat: str, offset: int, execute: bool = True) -> int:
    """One getUpdates round. Returns the next offset. With execute=False, updates are only
    consumed — the very first run fast-forwards past whatever predates the poller, so stale
    chat messages never replay as commands."""
    payload = _api(token, "getUpdates", timeout=50, offset=offset or None)
    for update in payload.get("result") or []:
        offset = max(offset, int(update["update_id"]) + 1)
        message = update.get("message") or {}
        chat_id = str((message.get("chat") or {}).get("id", ""))
        text = message.get("text") or ""
        if not execute or chat_id != owner_chat or not text:
            continue  # not the founder (or not text) — takeover only listens to the owner
        try:
            reply = handle_owner_command(text)
        except Exception as exc:
            log.exception("takeover command failed")
            reply = f"Er ging iets mis: {exc}"
        notify.owner(reply)
    return offset


def _run() -> None:
    token, owner_chat = _token(), os.getenv("OWNER_TELEGRAM_CHAT_ID", "")
    with _LOCK:
        state = _load()
        offset = int(state.get("offset", 0))
        first_run = "offset" not in state
    log.info("takeover poller running (owner chat %s)", owner_chat)
    while True:
        try:
            new_offset = _poll_once(token, owner_chat, offset, execute=not first_run)
            first_run = False
            if new_offset != offset:
                offset = new_offset
                with _LOCK:
                    state = _load()
                    state["offset"] = offset
                    _save(state)
        except Exception as exc:
            # Keep the loop alive (network blips, Telegram hiccups) but say so once in the
            # journal; the webhook side keeps working regardless.
            log.warning("takeover poll error: %s", exc)
            time.sleep(5)


def start() -> bool:
    """Start the owner-command poller if Telegram is configured. Called from server startup;
    False (with a log line) when unconfigured, so the server runs fine without it."""
    if os.getenv("TAKEOVER_DISABLED") == "1":
        log.info("takeover poller disabled (TAKEOVER_DISABLED=1)")
        return False
    if not (_token() and os.getenv("OWNER_TELEGRAM_CHAT_ID")):
        log.info("takeover poller not started: set OWNER_TELEGRAM_CHAT_ID + a bot token")
        return False
    threading.Thread(target=_run, name="takeover-poller", daemon=True).start()
    return True
