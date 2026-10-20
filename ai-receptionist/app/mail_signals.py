"""Read-only IMAP mail signals for the morning oversight digest.

Absorbs the one thing the retired Mac launchd briefing (ops/briefing/, deleted in the
same commit) had that the 07:30 server digest lacked: inbound replies and DSN/bounces
from the outreach mailbox. Everything else that briefing collected already has a home
(`kk board` for the boards, the status page for queues/timers), so the founder gets one
morning Telegram message from one machine instead of two half-briefings.

Strictly read-only: INBOX is opened readonly and fetched with BODY.PEEK, so nothing gets
marked as read and nothing is ever sent from here. Reuses the Gmail app password the
outreach sender already needs (GMAIL_USER/GMAIL_APP_PASSWORD; IMAP_* overrides for a
non-Gmail mailbox). Optional MAIL_WATCH_SENDERS (comma-separated substrings) puts live
deals at the top of the list.
"""

from __future__ import annotations

import email
import email.policy
import email.utils
import imaplib
import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta

_DSN_SENDER_HINTS = ("mailer-daemon", "postmaster", "mail delivery")
_MAX_MESSAGES = 50  # newest N of the last 24h; a busier inbox than this needs a human
_MAX_LISTED = 12    # one-liners in the digest; the rest becomes a "+N more" count


@dataclass
class MailItem:
    sender: str
    subject: str
    is_dsn: bool = False
    bounced: str = ""  # failed recipient extracted from the DSN, when found
    watched: bool = False


def _creds() -> tuple[str, str, str]:
    user = os.getenv("IMAP_USER") or os.getenv("GMAIL_USER") or ""
    password = os.getenv("IMAP_APP_PASSWORD") or os.getenv("GMAIL_APP_PASSWORD") or ""
    host = os.getenv("IMAP_HOST", "imap.gmail.com")
    return user, password.replace(" ", ""), host


def configured() -> bool:
    user, password, _ = _creds()
    return bool(user and password)


def _watch_list() -> tuple[str, ...]:
    raw = os.getenv("MAIL_WATCH_SENDERS", "")
    return tuple(s.strip().lower() for s in raw.split(",") if s.strip())


def _is_dsn(msg: email.message.EmailMessage, sender: str) -> bool:
    if msg.get_content_type() == "multipart/report":
        return True
    return any(hint in sender.lower() for hint in _DSN_SENDER_HINTS)


def _bounced_recipient(msg: email.message.EmailMessage) -> str:
    """The address the outreach mail failed to reach — the actionable bit of a DSN."""
    addr = str(msg.get("X-Failed-Recipients", "")).strip()  # Gmail's shortcut header
    if addr:
        return addr.splitlines()[0].strip()
    for part in msg.walk():
        if part.get_content_type() != "message/delivery-status":
            continue
        payload = part.get_payload()
        for block in payload if isinstance(payload, list) else []:
            for header in ("Final-Recipient", "Original-Recipient"):
                value = str(block.get(header, "") or "")
                if value:
                    return value.split(";")[-1].strip()
        if isinstance(payload, str):
            found = re.search(r"(?:Final|Original)-Recipient:.*?;\s*(\S+)", payload)
            if found:
                return found.group(1)
    return ""


def _classify(msg: email.message.EmailMessage, watch: tuple[str, ...]) -> MailItem:
    sender = str(msg.get("From", "?"))
    item = MailItem(sender=sender, subject=str(msg.get("Subject", "(no subject)")))
    if _is_dsn(msg, sender):
        item.is_dsn = True
        item.bounced = _bounced_recipient(msg)
    item.watched = any(w in sender.lower() for w in watch)
    return item


def fetch_items(now: datetime | None = None) -> list[MailItem]:
    """Last 24h of INBOX, newest first. Read-only; raises on a broken mailbox."""
    user, password, host = _creds()
    watch = _watch_list()
    since = ((now or datetime.now()) - timedelta(days=1)).strftime("%d-%b-%Y")
    items: list[MailItem] = []
    imap = imaplib.IMAP4_SSL(host, timeout=30)
    try:
        imap.login(user, password)
        imap.select("INBOX", readonly=True)  # geen flags: nothing gets marked as read
        _, data = imap.search(None, f"(SINCE {since})")
        ids = data[0].split()[-_MAX_MESSAGES:]
        for msg_id in reversed(ids):
            _, fetched = imap.fetch(msg_id, "(BODY.PEEK[])")
            raw = next((p[1] for p in fetched if isinstance(p, tuple)), None)
            if raw is None:
                continue
            msg = email.message_from_bytes(raw, policy=email.policy.default)
            items.append(_classify(msg, watch))
    finally:
        try:
            imap.logout()
        except Exception:
            pass
    return items


def _short(header: str, limit: int = 48) -> str:
    name, addr = email.utils.parseaddr(header)
    text = f"{name} <{addr}>" if name and addr else (addr or header)
    return text if len(text) <= limit else text[: limit - 1] + "…"


def render(items: list[MailItem]) -> list[str]:
    lines = ["MAIL (last 24h)"]
    if not items:
        lines.append("  no inbound mail")
        return lines
    bounces = [i for i in items if i.is_dsn]
    rest = [i for i in items if not i.is_dsn]
    watched = [i for i in rest if i.watched]
    lines.append(f"  {len(items)} inbound · {len(bounces)} bounce · {len(watched)} watched")
    for i in bounces:
        lines.append(f"  ⚠ BOUNCE → {i.bounced or _short(i.sender)}")
    listed = watched + [i for i in rest if not i.watched]  # live deals first
    for i in listed[:_MAX_LISTED]:
        marker = "●" if i.watched else "•"
        lines.append(f"  {marker} {_short(i.sender)} — {_short(i.subject, 60)}")
    if len(listed) > _MAX_LISTED:
        lines.append(f"  … +{len(listed) - _MAX_LISTED} more in the inbox")
    return lines


def digest_section(now: datetime | None = None) -> list[str]:
    """Digest lines for the mailbox. Never raises — the digest must still ship."""
    if not configured():
        return ["MAIL: skipped (set GMAIL_USER + GMAIL_APP_PASSWORD, or IMAP_USER/IMAP_APP_PASSWORD)"]
    try:
        return render(fetch_items(now))
    except Exception as exc:  # configured but broken must be visible, not fatal
        return [f"MAIL: collector broken ({type(exc).__name__}: {exc}) — check IMAP creds"]
