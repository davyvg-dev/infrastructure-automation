"""WhatsApp channel via Twilio.

Twilio delivers inbound WhatsApp messages as a form-encoded webhook POST. We run a
receptionist turn and reply with TwiML, which Twilio sends back to the customer. Wired
into the FastAPI server at POST /whatsapp.

Signature validation is on when TWILIO_AUTH_TOKEN is set (recommended in production) and
the twilio package is installed; otherwise it's skipped so local/dev works out of the box.
"""

from __future__ import annotations

import os
from xml.sax.saxutils import escape

from .. import sessions


def _signature_ok(url: str, signature: str | None, params: dict[str, str]) -> bool:
    token = os.getenv("TWILIO_AUTH_TOKEN")
    if not token:
        return True  # validation disabled (dev)
    try:
        from twilio.request_validator import RequestValidator
    except ModuleNotFoundError:
        return True  # twilio not installed; don't hard-block the demo
    return RequestValidator(token).validate(url, params, signature or "")


def _twiml(text: str) -> str:
    message = f"<Message>{escape(text)}</Message>" if text else ""
    return f'<?xml version="1.0" encoding="UTF-8"?><Response>{message}</Response>'


def handle(url: str, signature: str | None, params: dict[str, str]) -> tuple[str, int]:
    """Returns (twiml_body, http_status)."""
    if not _signature_ok(url, signature, params):
        return _twiml(""), 403
    body = (params.get("Body") or "").strip()
    sender = params.get("From") or "unknown"  # e.g. "whatsapp:+3161..."
    if not body:
        return _twiml(""), 200
    reply = sessions.respond("whatsapp", sender, body)
    return _twiml(reply), 200
