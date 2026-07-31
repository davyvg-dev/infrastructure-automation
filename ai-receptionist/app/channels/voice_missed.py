"""Missed-call catcher: an unanswered phone call becomes a WhatsApp conversation.

The founder's phone forwards unanswered calls (conditional forwarding) to a Twilio voice
number, whose webhook points here. We answer with a short Dutch message, hang up, and send
the caller a WhatsApp message so the receptionist picks the conversation up from there.
Wired into the FastAPI server at POST /voice/missed.

The WhatsApp send is business-initiated, so outside a 24h service window it only delivers
as an approved template: set WHATSAPP_MISSED_CALL_CONTENT_SID once the template from
docs/whatsapp-templates.md §2.6 is approved. Without it we attempt a freeform send, which
works on the Twilio sandbox and inside an open service window — good enough for testing,
not for production.

Either way the founder hears about the missed call on Telegram, including when the WhatsApp
message could not be delivered (landline, no WhatsApp) — that caller needs a callback, and
a funnel that can silently drop a hot lead is worse than no funnel.
"""

from __future__ import annotations

import logging
import threading
from xml.sax.saxutils import escape

from .. import notify
from ..settings import business, env
from .whatsapp import send, send_template, signature_ok

log = logging.getLogger(__name__)


def _business_name() -> str:
    try:
        return business()["business"]["name"]
    except Exception:
        return "Klantkraan"


def _twiml(text: str) -> str:
    say = f'<Say language="nl-NL">{escape(text)}</Say>' if text else ""
    return f'<?xml version="1.0" encoding="UTF-8"?><Response>{say}<Hangup/></Response>'


def _followup_text(name: str) -> str:
    return (
        f"Hallo, u belde net met {name} en we konden niet opnemen. "
        "Waar kunnen we u mee helpen? Stuur hier uw bericht, dan pakken we het direct op."
    )


def _send_followup(caller: str) -> None:
    name = _business_name()
    content_sid = env("WHATSAPP_MISSED_CALL_CONTENT_SID", required=False)
    try:
        if content_sid:
            send_template(caller, content_sid, {"1": name})
        else:
            send(caller, _followup_text(name))
    except Exception as exc:
        log.warning("missed-call WhatsApp to %s failed: %s", caller, exc)
        notify.owner(
            f"Gemiste oproep van {caller} — WhatsApp-opvang NIET afgeleverd ({exc}). "
            "Deze beller moet je terugbellen."
        )
        return
    notify.owner(f"Gemiste oproep van {caller} — WhatsApp-opvang verstuurd.")


def handle(url: str, signature: str | None, params: dict[str, str]) -> tuple[str, int]:
    """Returns (twiml_body, http_status)."""
    if not signature_ok(url, signature, params):
        return _twiml(""), 403
    caller = (params.get("From") or "").strip()
    if not caller or caller.lower().startswith("anonymous"):
        # No caller ID, nothing to message. Still answer politely.
        return _twiml(
            f"U belt met {_business_name()}. We kunnen nu niet opnemen. "
            "Stuur ons een WhatsApp-bericht, dan helpen we u direct verder."
        ), 200
    # Answer the call first; the WhatsApp send happens off the webhook thread so a slow
    # Twilio REST round-trip can never delay the spoken message.
    threading.Thread(target=_send_followup, args=(caller,), daemon=True).start()
    return _twiml(
        f"U belt met {_business_name()}. We kunnen nu niet opnemen. "
        "U ontvangt direct een WhatsApp-bericht van ons, daar helpen we u meteen verder."
    ), 200
