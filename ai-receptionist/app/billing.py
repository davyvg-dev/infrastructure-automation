"""Mollie billing: turn a signed client into a running monthly subscription.

The recurring flow (verified against current Mollie docs via context7, 2026-07-28):
create a customer, send them a first payment (sequenceType=first) through Mollie
checkout (iDEAL etc.), and when the paid webhook arrives create the ongoing monthly
subscription on that customer. Mollie webhooks POST a form-encoded `id=tr_...` only;
we fetch the payment back from the API for truth — that fetch-back IS the security
model (classic Mollie webhooks carry no HMAC).

On that same paid-first-payment event the customer gets their welcome e-mail (mailer.py):
the founder's Telegram ping is not a reply to the buyer, and a self-serve payer who hears
nothing is the one failure mode that is entirely ours.

Every paid payment — the first one AND each recurring month — also gets a factuur
(invoice.py). A Dutch B2B client needs one per charge to reclaim the BTW, and month two is
the one their bookkeeper chases us for.

All Mollie knowledge lives here; server.py only owns the thin webhook route. The API
key (MOLLIE_API_KEY) is optional at boot: the app runs fine without it, billing calls
raise a clear MissingSetting instead. Every webhook event is appended to
data/billing.jsonl, and the founder gets a best-effort Telegram ping via notify.

Sell from the terminal:

    python -m app.billing checkout "Jan de Vries BV" jan@devries.nl
    python -m app.billing checkout "Jan de Vries BV" jan@devries.nl --amount 299.00 --plan chat
    python -m app.billing status
    python -m app.billing welcome                  # preview the welcome copy, offline
    python -m app.billing welcome cst_123 --send   # re-send it by hand

Stop selling from the terminal too — the playbook's decline path, without the dashboard:

    python -m app.billing subs cst_123             # what is running, what was paid
    python -m app.billing cancel cst_123           # stop the charges, refund nothing
    python -m app.billing refund tr_abc            # refund in full
    python -m app.billing offboard cst_123         # cancel AND refund the first payment
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import threading
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import httpx

from . import mail_layout, mailer, notify, settings
from .settings import MissingSetting, ensure_dirs

MOLLIE_API = "https://api.mollie.com/v2"

# --- Money -------------------------------------------------------------------------------
# Every price in this module is the NET (ex-BTW) price, because that is what we advertise:
# klantkraan.nl/prijzen says "Alle bedragen excl. 21% BTW", and the buyers are BV's that
# reclaim the BTW, so ex-BTW is the normal B2B quote. Mollie has no concept of BTW — it
# charges one number — so the gross is computed at the Mollie boundary and nowhere else, and
# the factuur splits that same gross back into net + BTW so the two can never disagree.
#
# Setting PRICES_INCLUDE_BTW=1 treats the advertised price as the gross instead. Nothing else
# has to change: the charge and the invoice split both follow from this one switch.
BTW_RATE = Decimal("0.21")
# Monthly NET price per plan. The first payment can differ (the founding-member first month
# is half); the subscription always charges the plan price.
PLAN_MONTHLY_NET = {"chat": "299.00", "compleet": "499.00"}
DEFAULT_PLAN = "chat"
# Founding offer: first month 50% off €299 net. The site's /aanmelden copy quotes this
# number — change them together.
FIRST_MONTH_NET_EUR = "149.50"

_EVENTS_LOCK = threading.Lock()


class MollieError(RuntimeError):
    """Mollie answered but refused (4xx) — retrying the same call will not help."""


class MollieUnreachable(MollieError):
    """Mollie could not be reached (network error or 5xx) — worth retrying later."""


def _api_key() -> str:
    key = os.getenv("MOLLIE_API_KEY")
    if not key:
        raise MissingSetting(
            "MOLLIE_API_KEY is not set — billing is disabled. The live key is in the prod "
            ".env on the ops server; add it to .env here to use billing."
        )
    return key


def _webhook_url() -> str:
    return os.getenv("MOLLIE_WEBHOOK_URL", "https://demo.klantkraan.nl/api/mollie/webhook")


def _redirect_url() -> str:
    # Where the customer lands after checkout — note Mollie sends them here on paid,
    # canceled AND failed alike; /bedankt/ copy handles all three.
    return os.getenv("MOLLIE_REDIRECT_URL", "https://klantkraan.nl/bedankt/")


def _eur(amount: str | float | Decimal) -> str:
    """Mollie wants amounts as exact two-decimal strings ('149.50').

    Rounds half-UP, not Python's default half-even: this is money on a legal document, and
    half-even would settle a 180.895 gross to a different cent than any accountant expects.
    """
    try:
        return str(Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    except InvalidOperation as exc:
        raise ValueError(f"not an amount: {amount!r}") from exc


def prices_include_btw() -> bool:
    """False (the default) means the advertised price is ex-BTW and gets grossed up."""
    return os.getenv("PRICES_INCLUDE_BTW", "").strip().lower() in ("1", "true", "ja", "yes")


def gross_eur(net_eur: str | float | Decimal) -> str:
    """The amount Mollie actually charges for an advertised (net) price."""
    if prices_include_btw():
        return _eur(net_eur)
    return _eur(Decimal(str(net_eur)) * (Decimal("1") + BTW_RATE))


def split_gross(gross: str | float | Decimal) -> tuple[str, str]:
    """A charged gross back into (net, btw), which always sum to the gross exactly.

    Derived from the gross rather than recomputed from the list price on purpose: the
    factuur must add up to what actually left the customer's account, including for a
    discounted or test amount that no list price would reproduce.
    """
    total = Decimal(_eur(gross))
    net = Decimal(_eur(total / (Decimal("1") + BTW_RATE)))
    return _eur(net), _eur(total - net)


def plan_monthly_gross(plan: str) -> str:
    return gross_eur(PLAN_MONTHLY_NET.get(plan, PLAN_MONTHLY_NET[DEFAULT_PLAN]))


def _plan_label(plan: str) -> str:
    return plan.strip().capitalize() or "Chat"


def _request(method: str, path: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
    """One Mollie REST call. The single seam the offline tests monkeypatch."""
    headers = {"Authorization": f"Bearer {_api_key()}"}
    try:
        resp = httpx.request(method, MOLLIE_API + path, json=data, headers=headers, timeout=15)
    except httpx.HTTPError as exc:
        raise MollieUnreachable(f"Mollie unreachable: {exc}") from exc
    if resp.status_code >= 500:
        raise MollieUnreachable(f"Mollie server error {resp.status_code} on {method} {path}")
    if resp.status_code >= 400:
        try:
            detail = resp.json().get("detail", "")
        except Exception:
            detail = ""
        raise MollieError(f"Mollie {resp.status_code} on {method} {path}: {detail}")
    return resp.json()


# --- API operations ----------------------------------------------------------------------


def create_customer(name: str, email: str) -> str:
    """Register the client as a Mollie customer; returns the cst_... id."""
    customer = _request("POST", "/customers", {"name": name, "email": email, "locale": "nl_NL"})
    return customer["id"]


def create_first_payment(
    customer_id: str,
    net_amount_eur: str | float | Decimal,
    description: str,
    plan: str,
    monthly_net_eur: str | float | Decimal | None = None,
) -> str:
    """Create the sequenceType=first payment that both charges the first month AND creates
    the mandate for the subscription. Returns the checkout URL to send to the client.

    Both amounts are NET (ex-BTW) and are grossed up here — this is the only place a charge
    is computed, so no caller can forget the BTW.

    The plan and both monthly figures ride along as payment metadata, so the webhook can
    create the subscription AND invoice statelessly — no local pending-checkout state to lose.

    monthly_net_eur overrides the plan price for THIS checkout only. It exists so a test
    checkout can charge cents on both legs: without it a EUR 1 first payment still starts a
    EUR 299/month subscription, because the webhook reads the monthly off this metadata.
    """
    monthly_net = (
        _eur(monthly_net_eur)
        if monthly_net_eur
        else PLAN_MONTHLY_NET.get(plan, PLAN_MONTHLY_NET[DEFAULT_PLAN])
    )
    monthly_gross = gross_eur(monthly_net)
    charged = gross_eur(net_amount_eur)
    payment = _request(
        "POST",
        "/payments",
        {
            "amount": {"currency": "EUR", "value": charged},
            "description": description,
            "customerId": customer_id,
            "sequenceType": "first",
            "redirectUrl": _redirect_url(),
            "webhookUrl": _webhook_url(),
            "locale": "nl_NL",
            # monthly_eur stays the GROSS: it is what the subscription must charge. The net
            # rides along beside it for the factuur and the welcome copy.
            "metadata": {
                "plan": plan,
                "monthly_eur": monthly_gross,
                "monthly_net_eur": monthly_net,
            },
        },
    )
    checkout_url = payment["_links"]["checkout"]["href"]
    _log_event(
        {
            "event": "checkout_created",
            "payment_id": payment.get("id"),
            "customer_id": customer_id,
            "amount_eur": charged,
            "net_amount_eur": _eur(net_amount_eur),
            "plan": plan,
            "monthly_eur": monthly_gross,
            "monthly_net_eur": monthly_net,
            "checkout_url": checkout_url,
        }
    )
    return checkout_url


def create_subscription(
    customer_id: str, amount_eur: str | float | Decimal, description: str
) -> dict[str, Any]:
    """Start the ongoing monthly charge on a customer with a valid mandate."""
    return _request(
        "POST",
        f"/customers/{customer_id}/subscriptions",
        {
            "amount": {"currency": "EUR", "value": _eur(amount_eur)},
            "interval": "1 month",
            "description": description,
        },
    )


def fetch_payment(payment_id: str) -> dict[str, Any]:
    return _request("GET", f"/payments/{payment_id}")


def fetch_customer(customer_id: str) -> dict[str, Any]:
    """Name + e-mail of a Mollie customer. Mollie is the source of truth for who paid, so
    the welcome goes to the address that is actually on the mandate."""
    return _request("GET", f"/customers/{customer_id}")


def list_subscriptions(customer_id: str) -> list[dict[str, Any]]:
    listing = _request("GET", f"/customers/{customer_id}/subscriptions")
    return (listing.get("_embedded") or {}).get("subscriptions") or []


def list_customer_payments(customer_id: str) -> list[dict[str, Any]]:
    listing = _request("GET", f"/customers/{customer_id}/payments")
    return (listing.get("_embedded") or {}).get("payments") or []


def first_paid_payment(customer_id: str) -> dict[str, Any] | None:
    """The sequenceType=first payment that started this customer's mandate — the one the
    decline path refunds. Mollie lists newest first, so the last match is the original."""
    firsts = [
        p
        for p in list_customer_payments(customer_id)
        if p.get("sequenceType") == "first" and p.get("status") == "paid"
    ]
    return firsts[-1] if firsts else None


def cancel_subscription(customer_id: str, subscription_id: str) -> dict[str, Any]:
    """Stop an ongoing monthly charge. Nothing is refunded; the mandate simply stops.

    Mollie's own docs disagree on the verb: the classic v2 REST reference documents DELETE
    on this path, while their generated Python SDK documents POST. Rather than bet the
    off-boarding path on which one this account speaks, try DELETE and fall back to POST on
    a method error — a cancel that silently does not happen is money we keep taking.
    """
    path = f"/customers/{customer_id}/subscriptions/{subscription_id}"
    try:
        return _request("DELETE", path)
    except MollieUnreachable:
        raise
    except MollieError as exc:
        if "405" not in str(exc) and "404" not in str(exc):
            raise
        return _request("POST", path)


def refund_payment(
    payment_id: str, amount_eur: str | float | Decimal | None = None, description: str = ""
) -> dict[str, Any]:
    """Refund a payment. Without an amount this refunds the full amount that was charged,
    read back from Mollie rather than assumed, so a founding-member EUR 149.50 first month
    is never accidentally refunded as EUR 299."""
    payment = fetch_payment(payment_id)
    charged = (payment.get("amount") or {}).get("value")
    body: dict[str, Any] = {
        "amount": {"currency": "EUR", "value": _eur(amount_eur if amount_eur else charged)},
        "description": description or "Klantkraan terugbetaling",
    }
    refund = _request("POST", f"/payments/{payment_id}/refunds", body)
    _log_event(
        {
            "event": "refund",
            "payment_id": payment_id,
            "refund_id": refund.get("id"),
            "amount_eur": body["amount"]["value"],
            "charged_eur": charged,
            "description": body["description"],
        }
    )
    return refund


def _is_live(subscription: dict[str, Any]) -> bool:
    return subscription.get("status") not in ("canceled", "completed")


def _has_live_subscription(customer_id: str) -> bool:
    """Idempotency check against Mollie itself (survives local disk loss): does this
    customer already have a subscription that isn't canceled/completed?"""
    return any(_is_live(sub) for sub in list_subscriptions(customer_id))


def offboard(customer_id: str, refund: bool = True) -> dict[str, Any]:
    """The playbook's decline path in one call: stop every live subscription, then refund
    the first payment in full.

    Cancel before refund on purpose. If the refund fails we have at least stopped taking
    money; the reverse order can leave a refunded customer on a live mandate, which is the
    one outcome that turns into a chargeback.
    """
    result: dict[str, Any] = {"customer_id": customer_id, "canceled": [], "refund": None}
    for sub in list_subscriptions(customer_id):
        if _is_live(sub):
            cancel_subscription(customer_id, sub["id"])
            result["canceled"].append(sub["id"])
    _log_event({"event": "offboard", "customer_id": customer_id, "canceled": result["canceled"]})
    if refund:
        payment = first_paid_payment(customer_id)
        if not payment:
            result["refund"] = {"error": "no paid first payment found to refund"}
        else:
            refunded = refund_payment(
                payment["id"], description="Klantkraan volledige terugbetaling"
            )
            result["refund"] = {
                "payment_id": payment["id"],
                "refund_id": refunded.get("id"),
                "amount_eur": (payment.get("amount") or {}).get("value"),
            }
    return result


# --- Welcome -----------------------------------------------------------------------------
# The customer's first word from us after paying. Until this existed, a stranger could start
# a EUR 299/mo SEPA subscription at 03:00 and hear nothing back: /bedankt/ is a receipt, not
# a welcome. Onboarding playbook 1b step 1 wants exactly three things said (we have it, what
# happens next, and when) and one promise: ONE WORKING DAY, never "direct" — that is what a
# pre-build plus founder sleep actually supports.
#
# Written in "u", like the rest of klantkraan.nl. The playbook drafted it in "je"; the site
# is formal throughout, and a welcome in the wrong register reads like a different company.

WELCOME_SUBJECT = "Welkom bij Klantkraan, uw betaling is binnen"


def _eur_nl(amount: str) -> str:
    """Mollie's '149.50' as a Dutch reader expects it: '€ 149,50'."""
    return "€ " + str(amount).replace(".", ",")


WELCOME_PREHEADER = "Wij bouwen uw receptionist. Binnen één werkdag praat u zelf met hem."

# A closing image band, the way the site runs photos: full-bleed and decorative. Nothing in
# the mail depends on the reader seeing it -- most clients block images until asked.
WELCOME_PHOTO = mail_layout.Photo(
    src=f"{mail_layout.SITE}/photos/home-hero-sm.jpg",
    alt="Een vakvrouw bij haar bestelbus.",
)


def welcome_blocks(
    *,
    person: str,
    plan: str,
    monthly_eur: str,
    first_amount_eur: str | None = None,
    ask_website: bool = True,
) -> list[mail_layout.Block]:
    """The welcome, as blocks. Pure function of what we know, so it is readable in a test
    and previewable from the CLI before a real buyer ever gets it. mail_layout turns this
    into the branded HTML and the plain-text alternative, from this one description."""
    greeting = f"Hoi {person.split()[0]}," if person.strip() else "Hoi,"
    needs = []
    if ask_website:
        needs.append("De link naar uw website.")
    needs.append("Waar nieuwe aanvragen naartoe moeten: e-mail of WhatsApp.")
    needs.append("Welke agenda hij mag inplannen, als u afspraken wilt laten boeken.")

    plan_lines = [f"Klantkraan {_plan_label(plan)}, {_eur_nl(monthly_eur)} per maand."]
    if first_amount_eur and first_amount_eur != monthly_eur:
        plan_lines.append(f"De eerste maand is {_eur_nl(first_amount_eur)} gerekend.")

    return [
        mail_layout.Para(greeting),
        mail_layout.Para("Uw betaling is binnen. Dank u wel."),
        mail_layout.Heading("Wat er nu gebeurt"),
        mail_layout.Para(
            "Wij bouwen uw digitale receptionist. Binnen één werkdag krijgt u een link "
            "waarmee u zelf met hem kunt praten: u stelt hem vragen zoals een klant dat "
            "zou doen. Klopt er iets niet, een dienst, een werkgebied, de toon, dan past "
            "u dat aan in één bericht terug."
        ),
        mail_layout.Heading("Wat wij nog van u nodig hebben"),
        mail_layout.Steps(needs),
        mail_layout.Para(
            "Antwoord gewoon op deze mail. Wat u vandaag stuurt, zit in de eerste versie."
        ),
        # The mail asks for three things; this makes answering one tap instead of a
        # copied address. It opens a reply -- it never leads anywhere they have to log in.
        mail_layout.Button(
            "Stuur uw gegevens",
            "mailto:hallo@klantkraan.nl?subject=Mijn%20gegevens%20voor%20Klantkraan",
        ),
        mail_layout.Heading("Uw abonnement"),
        mail_layout.Panel(plan_lines),
        mail_layout.Para(
            "Maandelijks opzegbaar: één mail naar hallo@klantkraan.nl en er wordt niets "
            "meer geïncasseerd. De facturen komen van Mollie."
        ),
        WELCOME_PHOTO,
        mail_layout.Signoff("Klantkraan", "hallo@klantkraan.nl"),
    ]


def welcome_text(**kwargs: Any) -> str:
    """The plain-text part, kept as its own name because the CLI preview and the founder's
    terminal fallback both read this one."""
    return mail_layout.to_text(welcome_blocks(**kwargs))


def welcome_html(**kwargs: Any) -> str:
    return mail_layout.to_html(
        welcome_blocks(**kwargs), subject=WELCOME_SUBJECT, preheader=WELCOME_PREHEADER
    )


def _write_html_preview(path: str, html: str) -> None:
    """Drop the HTML part on disk so it can be opened and looked at. The images point at
    klantkraan.nl, so a local preview shows exactly what a reader gets -- provided the
    assets are deployed."""
    target = Path(path).expanduser()
    target.write_text(html, encoding="utf-8")
    print(f"HTML: {target}")


def send_welcome(
    customer_id: str, plan: str, monthly_eur: str, first_amount_eur: str | None = None
) -> dict[str, Any]:
    """Mail the paying customer their welcome. Returns {"sent", "to", "reason"}.

    Never raises: the money has already moved by the time this runs, so a mail problem is
    something the founder must hear about, not something that fails the webhook.
    """
    result: dict[str, Any] = {"sent": False, "to": None, "reason": ""}
    try:
        customer = fetch_customer(customer_id)
    except (MollieError, MissingSetting) as exc:
        result["reason"] = f"could not fetch customer: {exc}"
        return result

    email = str(customer.get("email") or "").strip()
    if not email:
        result["reason"] = "customer has no e-mail address on file"
        return result
    result["to"] = email

    lead = notify.find_lead(email) or {}
    person = str(lead.get("naam") or customer.get("name") or "")
    # Don't ask for something they already typed into the signup form.
    ask_website = not str(lead.get("site") or "").strip()

    copy = {
        "person": person,
        "plan": plan,
        "monthly_eur": monthly_eur,
        "first_amount_eur": first_amount_eur,
        "ask_website": ask_website,
    }
    # Keyed on the customer, so a webhook replay inside Resend's 24h window cannot send a
    # second copy even if our own idempotency check ever regressed.
    sent = mailer.send(
        email,
        WELCOME_SUBJECT,
        welcome_text(**copy),
        html=welcome_html(**copy),
        idempotency_key=f"welcome-{customer_id}",
    )
    result["sent"] = sent
    if not sent:
        result["reason"] = (
            "RESEND_API_KEY not configured"
            if not mailer.configured()
            else "Resend refused the send"
        )
    return result


# --- Factuur -----------------------------------------------------------------------------


def _invoice_paid_payment(payment: dict[str, Any], plan: str, result: dict[str, Any]) -> None:
    """Send the factuur for a payment that is already paid, recording the outcome on `result`.

    Never raises and never changes `action`: the subscription and the welcome are the
    webhook's real work, and a factuur that fails is something the founder must hear about,
    not something that makes Mollie retry a payment we have already banked.
    """
    try:
        _invoice_paid_payment_inner(payment, plan, result)
    except Exception as exc:  # noqa: BLE001
        # Deliberately swallowed HERE rather than at the route: an escape would skip
        # _log_event and _notify below it, so a factuur bug would also cost the founder the
        # ping telling him a subscription just started.
        result["invoice_sent"] = False
        result["invoice_reason"] = f"{type(exc).__name__}: {exc}"


def _invoice_paid_payment_inner(payment: dict[str, Any], plan: str, result: dict[str, Any]) -> None:
    from . import invoice  # local: invoice imports billing back for the BTW split

    customer_id = str(payment.get("customerId") or "")
    gross = (payment.get("amount") or {}).get("value")
    if not (customer_id and gross):
        result["invoice_reason"] = "payment has no customer or amount"
        return
    try:
        customer = fetch_customer(customer_id)
    except (MollieError, MissingSetting) as exc:
        result["invoice_reason"] = f"could not fetch customer: {exc}"
        return

    # Invoice-date the payment, not the webhook: a retry days later must not shift the date
    # on a document that is already in someone's bookkeeping.
    on = None
    paid_at = str(payment.get("paidAt") or "")[:10]
    if paid_at:
        try:
            on = datetime.strptime(paid_at, "%Y-%m-%d").date()
        except ValueError:
            on = None

    first = payment.get("sequenceType") == "first"
    label = _plan_label(plan)
    outcome = invoice.send(
        payment_id=str(payment.get("id") or ""),
        gross_eur=str(gross),
        to=str(customer.get("email") or ""),
        buyer_name=str(customer.get("name") or ""),
        description=f"Klantkraan {label} {'eerste maand' if first else 'maandabonnement'}",
        on=on,
    )
    result["invoice_sent"] = outcome["sent"]
    result["invoice_number"] = outcome["number"]
    if outcome["placeholder_identity"]:
        result["invoice_placeholder_identity"] = outcome["placeholder_identity"]
    if not outcome["sent"]:
        result["invoice_reason"] = outcome["reason"]


# --- Webhook -----------------------------------------------------------------------------


def handle_webhook(payment_id: str) -> dict[str, Any]:
    """Process one Mollie webhook ping: fetch the payment for truth, and on a paid first
    payment create the monthly subscription (unless the customer already has one).

    Raises MollieUnreachable (and MissingSetting) so the route can 503 and let Mollie
    retry; an unknown/refused payment id is swallowed into an "ignored" result so the
    route can 200 and stop hopeless retries. Every event lands in data/billing.jsonl.
    """
    try:
        payment = fetch_payment(payment_id)
    except MollieUnreachable:
        raise
    except MollieError as exc:
        result = {"payment_id": payment_id, "action": "ignored", "reason": str(exc)}
        _log_event({"event": "webhook", **result})
        return result

    status = payment.get("status")
    sequence_type = payment.get("sequenceType")
    customer_id = payment.get("customerId")
    result: dict[str, Any] = {
        "payment_id": payment_id,
        "status": status,
        "sequence_type": sequence_type,
        "customer_id": customer_id,
        "action": "ignored",
    }
    if status == "paid" and sequence_type == "first" and customer_id:
        if _has_live_subscription(customer_id):
            result["action"] = "already_subscribed"
        else:
            metadata = payment.get("metadata") or {}
            plan = str(metadata.get("plan") or DEFAULT_PLAN)
            monthly = metadata.get("monthly_eur") or plan_monthly_gross(plan)
            subscription = create_subscription(
                customer_id, monthly, f"Klantkraan {_plan_label(plan)} maandabonnement"
            )
            result["action"] = "subscription_created"
            result["subscription_id"] = subscription.get("id")
            result["plan"] = plan
            result["monthly_eur"] = _eur(monthly)
            # First word to the customer. Deliberately after the subscription exists: this
            # branch runs once per customer, so the welcome inherits that idempotency.
            paid = (payment.get("amount") or {}).get("value")
            welcome = send_welcome(customer_id, plan, _eur(monthly), paid)
            result["welcome_sent"] = welcome["sent"]
            result["welcome_to"] = welcome["to"]
            if not welcome["sent"]:
                result["welcome_reason"] = welcome["reason"]
            _invoice_paid_payment(payment, plan, result)
    elif status == "paid":
        result["action"] = "recurring_paid" if sequence_type == "recurring" else "paid"
        # Every charge needs its own factuur, not just the first: month two is what the
        # client's bookkeeper chases us for, and nobody is watching a recurring SEPA debit.
        if customer_id:
            metadata = payment.get("metadata") or {}
            _invoice_paid_payment(payment, str(metadata.get("plan") or DEFAULT_PLAN), result)

    _log_event({"event": "webhook", **result})
    _notify(result)
    return result


def _invoice_line(result: dict[str, Any]) -> str:
    """One line about the factuur for the founder ping. A placeholder BTW-id is called out
    every single time on purpose: it is the one thing that makes the document invalid, and a
    warning that only appears once is a warning that gets missed."""
    if "invoice_sent" not in result and "invoice_reason" not in result:
        return "Geen factuur voor deze gebeurtenis."
    if result.get("invoice_sent"):
        line = f"Factuur {result.get('invoice_number')} verstuurd."
    else:
        line = (
            f"GEEN factuur verstuurd ({result.get('invoice_reason') or 'onbekend'}) — "
            f"nummer {result.get('invoice_number') or 'niet toegekend'}."
        )
    placeholders = result.get("invoice_placeholder_identity") or []
    if placeholders:
        line += (
            f"\n⚠️ NIET RECHTSGELDIG: {', '.join(placeholders)} staat nog op een placeholder. "
            f"Zet de echte waarde in .env op de server."
        )
    return line


def _notify(result: dict[str, Any]) -> None:
    """Best-effort founder ping — a notification failure must never fail the webhook."""
    try:
        action = result.get("action")
        if action == "subscription_created":
            # Whether the customer heard from us is the actionable half of this ping: if the
            # welcome did not go out, the founder is the fallback and must know immediately.
            if result.get("welcome_sent"):
                welcome_line = f"Welkomstmail verstuurd naar {result.get('welcome_to')}."
            else:
                welcome_line = (
                    "GEEN welkomstmail verstuurd ({reason}) — stuur zelf een bericht naar "
                    "{to}, of draai: python -m app.billing welcome {cust}".format(
                        reason=result.get("welcome_reason") or "onbekend",
                        to=result.get("welcome_to") or "de klant",
                        cust=result.get("customer_id"),
                    )
                )
            notify.owner(
                "[billing] Eerste betaling binnen ({payment}) — maandabonnement gestart: "
                "{sub} ({plan}, €{monthly}/maand)\n{welcome}\n{factuur}".format(
                    payment=result.get("payment_id"),
                    sub=result.get("subscription_id"),
                    plan=result.get("plan"),
                    monthly=result.get("monthly_eur"),
                    welcome=welcome_line,
                    factuur=_invoice_line(result),
                )
            )
        elif action in ("recurring_paid", "paid", "already_subscribed"):
            notify.owner(
                f"[billing] Betaling ontvangen: {result.get('payment_id')} "
                f"({result.get('sequence_type')}, klant {result.get('customer_id')})\n"
                f"{_invoice_line(result)}"
            )
    except Exception as exc:
        print(f"[billing:notify] failed ({exc}); event was: {result}")


# --- Event log ---------------------------------------------------------------------------


def _events_path():
    # settings.DATA_DIR at call time (not import time) so tests can redirect it, like notify.
    return settings.DATA_DIR / "billing.jsonl"


def _log_event(record: dict[str, Any]) -> bool:
    """Append one event to data/billing.jsonl. Append-only (a concurrent write can never
    truncate the file), and never raises — the log must not decide a webhook's fate."""
    entry = {"at": datetime.now().isoformat(timespec="seconds"), **record}
    try:
        with _EVENTS_LOCK:
            ensure_dirs()
            with _events_path().open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return True
    except Exception as exc:
        print(f"[billing:log] persist failed ({exc}); event was: {entry}")
        return False


def recent_events(limit: int = 20) -> list[dict[str, Any]]:
    path = _events_path()
    if not path.exists():
        return []
    events = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events[-limit:]


# --- CLI ---------------------------------------------------------------------------------


def _confirm(assume_yes: bool, question: str) -> bool:
    """Ask before moving real money. A non-interactive caller (cron, a script) must pass
    --yes explicitly rather than have a prompt silently auto-answer itself."""
    if assume_yes:
        return True
    if not sys.stdin.isatty():
        print(f"❌ {question}\n   Niet-interactief: voeg --yes toe als je dit echt wilt.")
        return False
    return input(f"{question} [j/N] ").strip().lower() in ("j", "ja", "y", "yes")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="app.billing", description="Mollie billing: sell a subscription from the terminal."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_co = sub.add_parser(
        "checkout", help="Create a customer + first payment; prints the checkout URL to send."
    )
    p_co.add_argument("name", help="The client's business name (appears in Mollie).")
    p_co.add_argument("email", help="The client's billing email.")
    p_co.add_argument(
        "--amount",
        default=FIRST_MONTH_NET_EUR,
        help=f"First payment in EUR EX BTW (default {FIRST_MONTH_NET_EUR}: first month 50%% "
        f"off). BTW is added on top, so this is what the factuur says, not what is charged.",
    )
    p_co.add_argument(
        "--plan",
        default=DEFAULT_PLAN,
        choices=sorted(PLAN_MONTHLY_NET),
        help="Plan for the ongoing subscription (default chat, €299/month ex BTW).",
    )
    p_co.add_argument(
        "--monthly",
        default="",
        help="Override the monthly subscription price (EX BTW) for this checkout only. "
        "Use with --amount to run a live end-to-end test for cents "
        "(--amount 1.00 --monthly 1.00); the public /aanmelden price is unaffected.",
    )

    p_status = sub.add_parser("status", help="List recent billing events from data/billing.jsonl.")
    p_status.add_argument("--limit", type=int, default=20)

    p_wel = sub.add_parser(
        "welcome",
        help="Preview the welcome mail, or re-send it to a paying customer (--send).",
    )
    p_wel.add_argument(
        "customer_id",
        nargs="?",
        help="Mollie customer id (cst_...). Omit to preview the copy offline with sample data.",
    )
    p_wel.add_argument("--plan", default=DEFAULT_PLAN, choices=sorted(PLAN_MONTHLY_NET))
    p_wel.add_argument(
        "--send",
        action="store_true",
        help="Actually send it. Without this the mail is only printed.",
    )
    p_wel.add_argument(
        "--html",
        metavar="PATH",
        help="Write the branded HTML part to a file and open it in a browser to check it.",
    )

    p_subs = sub.add_parser("subs", help="List a customer's subscriptions and paid payments.")
    p_subs.add_argument("customer_id", help="Mollie customer id (cst_...).")

    p_cancel = sub.add_parser(
        "cancel", help="Cancel a subscription. Stops future charges; refunds nothing."
    )
    p_cancel.add_argument("customer_id", help="Mollie customer id (cst_...).")
    p_cancel.add_argument(
        "--subscription", default="", help="One sub_... id. Default: every live subscription."
    )
    p_cancel.add_argument("--yes", action="store_true", help="Skip the confirmation prompt.")

    p_refund = sub.add_parser(
        "refund", help="Refund a payment, in full unless --amount says otherwise."
    )
    p_refund.add_argument("payment_id", help="Mollie payment id (tr_...).")
    p_refund.add_argument(
        "--amount", default="", help="Partial refund in EUR. Default: the full amount charged."
    )
    p_refund.add_argument(
        "--reason", default="", help="Description on the refund (visible in Mollie)."
    )
    p_refund.add_argument("--yes", action="store_true", help="Skip the confirmation prompt.")

    p_off = sub.add_parser(
        "offboard",
        help="Decline path: cancel every live subscription AND refund the first payment.",
    )
    p_off.add_argument("customer_id", help="Mollie customer id (cst_...).")
    p_off.add_argument("--no-refund", action="store_true", help="Cancel only; keep the money.")
    p_off.add_argument("--yes", action="store_true", help="Skip the confirmation prompt.")

    args = parser.parse_args(argv[1:])

    if args.cmd == "checkout":
        label = _plan_label(args.plan)
        try:
            amount = _eur(args.amount)
            monthly = _eur(args.monthly) if args.monthly else PLAN_MONTHLY_NET[args.plan]
        except ValueError as exc:
            parser.error(str(exc))
        try:
            customer_id = create_customer(args.name, args.email)
            checkout_url = create_first_payment(
                customer_id, amount, f"Klantkraan {label} eerste maand", args.plan, monthly
            )
        except (MollieError, MissingSetting) as exc:
            print(f"❌ {exc}")
            return 1
        btw_note = "incl. BTW" if prices_include_btw() else f"incl. {BTW_RATE:.0%} BTW"
        print(f"✅ klant aangemaakt: {customer_id}")
        print(f"   checkout: {checkout_url}")
        print(f"   eerste betaling: €{gross_eur(amount)} ({btw_note}) — €{amount} ex BTW")
        print(
            f"   Stuur deze link naar de klant. Na betaling start het abonnement "
            f"Klantkraan {label}: €{gross_eur(monthly)} per maand ({btw_note}), "
            f"€{monthly} ex BTW."
        )
        if monthly != PLAN_MONTHLY_NET[args.plan]:
            # A test checkout is a REAL mandate on REAL money — say so, and hand over the
            # cleanup command now, while the customer id is still on screen.
            print(
                f"   ⚠️  TEST: €{monthly}/maand in plaats van €{PLAN_MONTHLY_NET[args.plan]}. "
                f"Dit is een echte incasso.\n"
                f"       Opruimen na de test: python -m app.billing offboard {customer_id}"
            )
        return 0
    if args.cmd == "status":
        events = recent_events(args.limit)
        if not events:
            print(f"no billing events yet ({_events_path()})")
            return 0
        for event in events:
            extra = event.get("action") or event.get("checkout_url") or ""
            print(
                f"{event.get('at', '?'):19}  {event.get('event', '?'):16} "
                f"{event.get('payment_id') or '-':16}  {extra}"
            )
        return 0
    if args.cmd == "welcome":
        monthly = PLAN_MONTHLY_NET[args.plan]
        if not args.customer_id:
            copy = {
                "person": "Jan de Vries",
                "plan": args.plan,
                "monthly_eur": monthly,
                "first_amount_eur": FIRST_MONTH_NET_EUR,
            }
            print(f"Onderwerp: {WELCOME_SUBJECT}\n")
            print(welcome_text(**copy))
            if args.html:
                _write_html_preview(args.html, welcome_html(**copy))
            print("(voorbeeld — geef een cst_... mee om de echte mail te zien of te sturen)")
            return 0
        if not args.send:
            try:
                customer = fetch_customer(args.customer_id)
            except (MollieError, MissingSetting) as exc:
                print(f"❌ {exc}")
                return 1
            lead = notify.find_lead(str(customer.get("email") or "")) or {}
            copy = {
                "person": str(lead.get("naam") or customer.get("name") or ""),
                "plan": args.plan,
                "monthly_eur": monthly,
                "first_amount_eur": FIRST_MONTH_NET_EUR,
                "ask_website": not str(lead.get("site") or "").strip(),
            }
            print(f"Aan: {customer.get('email')}")
            print(f"Onderwerp: {WELCOME_SUBJECT}\n")
            print(welcome_text(**copy))
            if args.html:
                _write_html_preview(args.html, welcome_html(**copy))
            print("(niet verstuurd — voeg --send toe om te sturen)")
            return 0
        result = send_welcome(args.customer_id, args.plan, monthly, FIRST_MONTH_NET_EUR)
        if result["sent"]:
            print(f"✅ welkomstmail verstuurd naar {result['to']}")
            return 0
        print(f"❌ niet verstuurd ({result['reason']}); klant: {result['to'] or args.customer_id}")
        return 1
    if args.cmd == "subs":
        try:
            subs = list_subscriptions(args.customer_id)
            payments = list_customer_payments(args.customer_id)
        except (MollieError, MissingSetting) as exc:
            print(f"❌ {exc}")
            return 1
        if not subs:
            print("geen abonnementen")
        for s in subs:
            live = "LIVE  " if _is_live(s) else "      "
            amount = (s.get("amount") or {}).get("value", "?")
            print(
                f"{live}{s.get('id', '?'):16} {s.get('status', '?'):10} €{amount:>8} "
                f"{s.get('interval', '?'):10} volgende: {s.get('nextPaymentDate') or '-'}"
            )
        for p in payments:
            if p.get("status") == "paid":
                amount = (p.get("amount") or {}).get("value", "?")
                print(
                    f"      {p.get('id', '?'):16} {p.get('status', '?'):10} €{amount:>8} "
                    f"{p.get('sequenceType', '?'):10} {p.get('paidAt', '')[:10]}"
                )
        return 0
    if args.cmd == "cancel":
        try:
            subs = [s for s in list_subscriptions(args.customer_id) if _is_live(s)]
        except (MollieError, MissingSetting) as exc:
            print(f"❌ {exc}")
            return 1
        if args.subscription:
            subs = [s for s in subs if s.get("id") == args.subscription]
        if not subs:
            print("niets te annuleren (geen lopend abonnement)")
            return 0
        what = ", ".join(
            f"{s['id']} (€{(s.get('amount') or {}).get('value', '?')}/mnd)" for s in subs
        )
        if not _confirm(args.yes, f"Abonnement stopzetten voor {args.customer_id}: {what}?"):
            return 1
        for s in subs:
            try:
                cancel_subscription(args.customer_id, s["id"])
            except (MollieError, MissingSetting) as exc:
                print(f"❌ {s['id']}: {exc}")
                return 1
            print(f"✅ gestopt: {s['id']}")
        _log_event(
            {
                "event": "cancel",
                "customer_id": args.customer_id,
                "canceled": [s["id"] for s in subs],
            }
        )
        return 0
    if args.cmd == "refund":
        try:
            payment = fetch_payment(args.payment_id)
        except (MollieError, MissingSetting) as exc:
            print(f"❌ {exc}")
            return 1
        charged = (payment.get("amount") or {}).get("value", "?")
        try:
            amount = _eur(args.amount) if args.amount else charged
        except ValueError as exc:
            parser.error(str(exc))
        if payment.get("status") != "paid":
            print(
                f"❌ {args.payment_id} heeft status {payment.get('status')}; alleen een betaalde betaling kan terug"
            )
            return 1
        if not _confirm(
            args.yes, f"€{amount} terugbetalen van {args.payment_id} (betaald: €{charged})?"
        ):
            return 1
        try:
            refunded = refund_payment(args.payment_id, amount, args.reason)
        except (MollieError, MissingSetting) as exc:
            print(f"❌ {exc}")
            return 1
        print(f"✅ terugbetaald: €{amount} ({refunded.get('id')})")
        return 0
    if args.cmd == "offboard":
        want_refund = not args.no_refund
        action = "stopzetten en volledig terugbetalen" if want_refund else "alleen stopzetten"
        if not _confirm(args.yes, f"Klant {args.customer_id} {action}?"):
            return 1
        try:
            result = offboard(args.customer_id, refund=want_refund)
        except (MollieError, MissingSetting) as exc:
            print(f"❌ {exc}")
            return 1
        if result["canceled"]:
            print(f"✅ gestopt: {', '.join(result['canceled'])}")
        else:
            print("   geen lopend abonnement om te stoppen")
        refund_result = result.get("refund") or {}
        if refund_result.get("error"):
            print(f"⚠  niet terugbetaald: {refund_result['error']} — controleer handmatig")
            return 1
        if refund_result:
            print(f"✅ terugbetaald: €{refund_result['amount_eur']} ({refund_result['refund_id']})")
        print("   Stuur de klant vandaag nog een schriftelijke uitleg (playbook §1b decline path).")
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
