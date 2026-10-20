"""WhatsApp channel via Twilio.

Twilio delivers inbound WhatsApp messages as a form-encoded webhook POST. We run a
receptionist turn and reply with TwiML, which Twilio sends back to the customer. Wired
into the FastAPI server at POST /whatsapp.

Outbound (business-initiated) sending lives here too: `send` for freeform replies inside
the 24h service window, `send_template` for approved Content API templates outside it.
Both need TWILIO_ACCOUNT_SID + TWILIO_WHATSAPP_FROM and raise on failure — the caller
decides how to surface it (Telegram, notify), never swallow it.

Signature validation is fail-closed: requests are rejected unless TWILIO_AUTH_TOKEN is
set and the signature verifies. For local development without Twilio, set
WHATSAPP_ALLOW_UNSIGNED=1 explicitly.
"""

from __future__ import annotations

import json
import logging
import os
from xml.sax.saxutils import escape

from .. import notify, sessions, takeover
from ..settings import clear_slug, env, resolve_whatsapp_slug, use_slug

log = logging.getLogger(__name__)


def signature_ok(url: str, signature: str | None, params: dict[str, str]) -> bool:
    token = os.getenv("TWILIO_AUTH_TOKEN")
    if not token:
        if os.getenv("WHATSAPP_ALLOW_UNSIGNED") == "1":
            return True
        log.warning(
            "Rejected /whatsapp request: TWILIO_AUTH_TOKEN not set "
            "(set WHATSAPP_ALLOW_UNSIGNED=1 for local dev)"
        )
        return False
    try:
        from twilio.request_validator import RequestValidator
    except ModuleNotFoundError:
        log.warning(
            "Rejected /whatsapp request: twilio package not installed, cannot validate signature"
        )
        return False
    return RequestValidator(token).validate(url, params, signature or "")


def _twiml(text: str) -> str:
    message = f"<Message>{escape(text)}</Message>" if text else ""
    return f'<?xml version="1.0" encoding="UTF-8"?><Response>{message}</Response>'


def handle(url: str, signature: str | None, params: dict[str, str]) -> tuple[str, int]:
    """Returns (twiml_body, http_status)."""
    if not signature_ok(url, signature, params):
        return _twiml(""), 403
    body = (params.get("Body") or "").strip()
    sender = params.get("From") or "unknown"  # e.g. "whatsapp:+3161..." (the customer)
    if not body:
        return _twiml(""), 200
    # Route to the client whose WhatsApp number this message was sent TO. Unknown/undeclared
    # numbers fall back to the default config, so single-tenant setups are unchanged. Setting
    # the tenant here namespaces the session, the analytics capture, and the lead recipient.
    token = use_slug(resolve_whatsapp_slug(params.get("To")))
    try:
        # A conversation the founder took over is theirs until released: relay the customer
        # message to their Telegram and stay silent — no bot reply racing the human's.
        if takeover.handle_inbound(sender, body):
            return _twiml(""), 200
        reply = sessions.respond("whatsapp", sender, body)
    except Exception as exc:
        # Report to the founder, then degrade gracefully: a friendly 200 (no Twilio retry
        # storm) beats a 500 that leaves the customer with silence.
        log.exception("whatsapp turn failed")
        notify.owner_exception(exc, context="whatsapp")
        reply = "Sorry, er ging even iets mis. Probeer het zo nog eens."
    finally:
        clear_slug(token)
    return _twiml(reply), 200


# --- outbound ----------------------------------------------------------------------------


def _wa_addr(number: str) -> str:
    number = number.strip()
    return number if number.startswith("whatsapp:") else f"whatsapp:{number}"


def _rest_client():
    from twilio.rest import Client

    return Client(env("TWILIO_ACCOUNT_SID"), env("TWILIO_AUTH_TOKEN"))


def send(to: str, text: str) -> str:
    """Freeform outbound message — only deliverable inside the 24h service window (i.e. as
    a reply to a customer who recently messaged). Returns the message SID; raises on
    missing config or Twilio rejection so the caller can tell the founder it didn't land."""
    message = _rest_client().messages.create(
        from_=_wa_addr(env("TWILIO_WHATSAPP_FROM")), to=_wa_addr(to), body=text
    )
    return message.sid


def send_template(to: str, content_sid: str, variables: dict[str, str] | None = None) -> str:
    """Business-initiated message via an approved Content API template. This is the only
    thing WhatsApp delivers outside the 24h window (docs/whatsapp-templates.md)."""
    message = _rest_client().messages.create(
        from_=_wa_addr(env("TWILIO_WHATSAPP_FROM")),
        to=_wa_addr(to),
        content_sid=content_sid,
        content_variables=json.dumps(variables or {}),
    )
    return message.sid
