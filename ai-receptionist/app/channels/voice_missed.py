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
from ..settings import business, clear_slug, current_slug, env, resolve_whatsapp_slug, use_slug
from .whatsapp import send, send_template, signature_ok

log = logging.getLogger(__name__)

# Caller-facing strings per config locale (`locale:` key, default nl). The founder alerts
# on Telegram stay Dutch — those are internal ops, not customer-facing.
_STRINGS = {
    "nl": {
        "say_lang": "nl-NL",
        "no_caller": (
            "U belt met {name}. We kunnen nu niet opnemen. "
            "Stuur ons een WhatsApp-bericht, dan helpen we u direct verder."
        ),
        "answered": (
            "U belt met {name}. We kunnen nu niet opnemen. U ontvangt direct een "
            "WhatsApp-bericht van ons, daar helpen we u meteen verder."
        ),
        "followup": (
            "Hallo, u belde net met {name} en we konden niet opnemen. "
            "Waar kunnen we u mee helpen? Stuur hier uw bericht, dan pakken we het direct op."
        ),
    },
    "en": {
        "say_lang": "en-GB",
        "no_caller": (
            "You have reached {name}. We can't take your call right now. "
            "Send us a WhatsApp message and we'll help you straight away."
        ),
        "answered": (
            "You have reached {name}. We can't take your call right now. You'll receive "
            "a WhatsApp message from us in a moment — we'll help you from there."
        ),
        "followup": (
            "Hello, you just called {name} and we couldn't pick up. "
            "How can we help? Reply here and we'll get right on it."
        ),
    },
    "es": {
        "say_lang": "es-ES",
        "no_caller": (
            "Ha llamado a {name}. Ahora mismo no podemos atenderle. "
            "Envíenos un mensaje de WhatsApp y le ayudamos enseguida."
        ),
        "answered": (
            "Ha llamado a {name}. Ahora mismo no podemos atenderle. En un momento "
            "recibirá un mensaje nuestro por WhatsApp; ahí le seguimos ayudando."
        ),
        "followup": (
            "Hola, acaba de llamar a {name} y no hemos podido atenderle. "
            "¿En qué podemos ayudarle? Responda a este mensaje y lo gestionamos enseguida."
        ),
    },
}


def _strings() -> dict[str, str]:
    try:
        locale = str(business().get("locale") or "nl").strip().lower()[:2]
    except Exception:
        locale = "nl"
    return _STRINGS.get(locale, _STRINGS["nl"])


def _business_name() -> str:
    try:
        return business()["business"]["name"]
    except Exception:
        return "Klantkraan"


def _twiml(text: str, say_lang: str = "nl-NL") -> str:
    say = f'<Say language="{say_lang}">{escape(text)}</Say>' if text else ""
    return f'<?xml version="1.0" encoding="UTF-8"?><Response>{say}<Hangup/></Response>'


def _send_followup(caller: str, slug: str | None) -> None:
    # Runs on its own thread, which starts with a fresh contextvar context — the tenant
    # from the webhook must be re-activated here or the default config's text goes out.
    token = use_slug(slug)
    try:
        name = _business_name()
        content_sid = env("WHATSAPP_MISSED_CALL_CONTENT_SID", required=False)
        try:
            if content_sid:
                send_template(caller, content_sid, {"1": name})
            else:
                send(caller, _strings()["followup"].format(name=name))
        except Exception as exc:
            log.warning("missed-call WhatsApp to %s failed: %s", caller, exc)
            notify.owner(
                f"Gemiste oproep van {caller} — WhatsApp-opvang NIET afgeleverd ({exc}). "
                "Deze beller moet je terugbellen."
            )
            return
        notify.owner(f"Gemiste oproep van {caller} — WhatsApp-opvang verstuurd.")
    finally:
        clear_slug(token)


def handle(url: str, signature: str | None, params: dict[str, str]) -> tuple[str, int]:
    """Returns (twiml_body, http_status)."""
    if not signature_ok(url, signature, params):
        return _twiml(""), 403
    # Route to the tenant whose number was called — same seam as the WhatsApp channel:
    # the client config declares it under `whatsapp.number`. No match => default config.
    token = use_slug(resolve_whatsapp_slug(params.get("To")))
    try:
        s = _strings()
        name = _business_name()
        caller = (params.get("From") or "").strip()
        if not caller or caller.lower().startswith("anonymous"):
            # No caller ID, nothing to message. Still answer politely.
            return _twiml(s["no_caller"].format(name=name), s["say_lang"]), 200
        # Answer the call first; the WhatsApp send happens off the webhook thread so a slow
        # Twilio REST round-trip can never delay the spoken message.
        threading.Thread(
            target=_send_followup, args=(caller, current_slug()), daemon=True
        ).start()
        return _twiml(s["answered"].format(name=name), s["say_lang"]), 200
    finally:
        clear_slug(token)
