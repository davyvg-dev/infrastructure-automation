"""Transactional e-mail to customers, via Resend.

Resend is already the declared transactional-email sub-processor in the register
(klantkraan.nl/legal/subprocessors), so this adds no vendor and no legal-page change. The
REST surface used here was verified against current Resend docs via context7 (2026-07-29):
POST https://api.resend.com/emails with a Bearer key and {from, to[], subject, text,
reply_to}, plus an optional `Idempotency-Key` header that de-duplicates identical sends for
24 hours.

This module is transport only — it knows how to put a message on the wire, never what the
message says. Callers own the copy (billing.py owns the welcome).

Two rules, both because the caller is usually a webhook that has already taken money:
send() never raises, and an unconfigured mailer is not an error — it prints the message and
returns False, so a dev box and a key-less server both stay usable.

Config (in .env):
  RESEND_API_KEY   unset = mailing disabled (prints instead of sends)
  MAIL_FROM        default "Klantkraan <hallo@klantkraan.nl>" (domain must be verified in Resend)
  MAIL_REPLY_TO    default "hallo@klantkraan.nl"
"""

from __future__ import annotations

import os

import httpx

RESEND_API = "https://api.resend.com/emails"

DEFAULT_FROM = "Klantkraan <hallo@klantkraan.nl>"
DEFAULT_REPLY_TO = "hallo@klantkraan.nl"


def configured() -> bool:
    """True when a real send is possible. Callers use this to tell the founder whether the
    customer actually heard from us, or whether he has to send it by hand."""
    return bool(os.getenv("RESEND_API_KEY"))


def send(
    to: str,
    subject: str,
    text: str,
    *,
    reply_to: str | None = None,
    idempotency_key: str | None = None,
) -> bool:
    """Send one plain-text e-mail. True only if Resend accepted it.

    `idempotency_key` makes a retried caller (a Mollie webhook replay, a re-run CLI) safe:
    Resend returns the original result instead of sending a second copy.
    """
    api_key = os.getenv("RESEND_API_KEY")
    if not (api_key and to.strip()):
        # Dev fallback, and the honest path on a server without the key: show, don't send.
        print(f"[mailer] (not sent — RESEND_API_KEY unset) to={to} subject={subject}\n{text}")
        return False

    payload = {
        "from": os.getenv("MAIL_FROM", DEFAULT_FROM),
        "to": [to.strip()],
        "subject": subject,
        "text": text,
        "reply_to": reply_to or os.getenv("MAIL_REPLY_TO", DEFAULT_REPLY_TO),
    }
    headers = {"Authorization": f"Bearer {api_key}"}
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key[:256]
    try:
        resp = httpx.post(RESEND_API, json=payload, headers=headers, timeout=15)
    except httpx.HTTPError as exc:
        print(f"[mailer] send failed (unreachable: {exc}); to={to} subject={subject}")
        return False
    if resp.status_code >= 400:
        # Body carries Resend's reason (unverified domain, bad address); worth printing once.
        print(f"[mailer] send refused ({resp.status_code}): {resp.text[:300]}")
        return False
    return True
