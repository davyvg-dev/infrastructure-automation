"""Mollie billing: turn a signed client into a running monthly subscription.

The recurring flow (verified against current Mollie docs via context7, 2026-07-28):
create a customer, send them a first payment (sequenceType=first) through Mollie
checkout (iDEAL etc.), and when the paid webhook arrives create the ongoing monthly
subscription on that customer. Mollie webhooks POST a form-encoded `id=tr_...` only;
we fetch the payment back from the API for truth — that fetch-back IS the security
model (classic Mollie webhooks carry no HMAC).

All Mollie knowledge lives here; server.py only owns the thin webhook route. The API
key (MOLLIE_API_KEY) is optional at boot: the app runs fine without it, billing calls
raise a clear MissingSetting instead. Every webhook event is appended to
data/billing.jsonl, and the founder gets a best-effort Telegram ping via notify.

Sell from the terminal:

    python -m app.billing checkout "Jan de Vries BV" jan@devries.nl
    python -m app.billing checkout "Jan de Vries BV" jan@devries.nl --amount 299.00 --plan chat
    python -m app.billing status
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import threading
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any

import httpx

from . import notify, settings
from .settings import MissingSetting, ensure_dirs

MOLLIE_API = "https://api.mollie.com/v2"

# Monthly price per plan (EUR, Mollie string format). The first payment can differ (the
# founding-member first month is 149.50); the subscription always charges the plan price.
PLAN_MONTHLY = {"chat": "299.00", "compleet": "499.00"}
DEFAULT_PLAN = "chat"

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
    # Where the customer lands after checkout. klantkraan.nl has no /bedankt/ page yet, so
    # the default is the homepage; set MOLLIE_REDIRECT_URL once a thank-you page ships.
    return os.getenv("MOLLIE_REDIRECT_URL", "https://klantkraan.nl/")


def _eur(amount: str | float | Decimal) -> str:
    """Mollie wants amounts as exact two-decimal strings ('149.50')."""
    try:
        return str(Decimal(str(amount)).quantize(Decimal("0.01")))
    except InvalidOperation as exc:
        raise ValueError(f"not an amount: {amount!r}") from exc


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
    customer_id: str, amount_eur: str | float | Decimal, description: str, plan: str
) -> str:
    """Create the sequenceType=first payment that both charges the first month AND creates
    the mandate for the subscription. Returns the checkout URL to send to the client.

    The plan + monthly price ride along as payment metadata, so the webhook can create the
    subscription statelessly — no local pending-checkout state to lose.
    """
    monthly = PLAN_MONTHLY.get(plan, PLAN_MONTHLY[DEFAULT_PLAN])
    payment = _request(
        "POST",
        "/payments",
        {
            "amount": {"currency": "EUR", "value": _eur(amount_eur)},
            "description": description,
            "customerId": customer_id,
            "sequenceType": "first",
            "redirectUrl": _redirect_url(),
            "webhookUrl": _webhook_url(),
            "locale": "nl_NL",
            "metadata": {"plan": plan, "monthly_eur": monthly},
        },
    )
    checkout_url = payment["_links"]["checkout"]["href"]
    _log_event(
        {
            "event": "checkout_created",
            "payment_id": payment.get("id"),
            "customer_id": customer_id,
            "amount_eur": _eur(amount_eur),
            "plan": plan,
            "monthly_eur": monthly,
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


def _has_live_subscription(customer_id: str) -> bool:
    """Idempotency check against Mollie itself (survives local disk loss): does this
    customer already have a subscription that isn't canceled/completed?"""
    listing = _request("GET", f"/customers/{customer_id}/subscriptions")
    subs = (listing.get("_embedded") or {}).get("subscriptions") or []
    return any(sub.get("status") not in ("canceled", "completed") for sub in subs)


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
            monthly = metadata.get("monthly_eur") or PLAN_MONTHLY.get(plan, PLAN_MONTHLY["chat"])
            subscription = create_subscription(
                customer_id, monthly, f"Klantkraan {_plan_label(plan)} maandabonnement"
            )
            result["action"] = "subscription_created"
            result["subscription_id"] = subscription.get("id")
            result["plan"] = plan
            result["monthly_eur"] = _eur(monthly)
    elif status == "paid":
        result["action"] = "recurring_paid" if sequence_type == "recurring" else "paid"

    _log_event({"event": "webhook", **result})
    _notify(result)
    return result


def _notify(result: dict[str, Any]) -> None:
    """Best-effort founder ping — a notification failure must never fail the webhook."""
    try:
        action = result.get("action")
        if action == "subscription_created":
            notify.owner(
                "[billing] Eerste betaling binnen ({payment}) — maandabonnement gestart: "
                "{sub} ({plan}, €{monthly}/maand)".format(
                    payment=result.get("payment_id"),
                    sub=result.get("subscription_id"),
                    plan=result.get("plan"),
                    monthly=result.get("monthly_eur"),
                )
            )
        elif action in ("recurring_paid", "paid", "already_subscribed"):
            notify.owner(
                f"[billing] Betaling ontvangen: {result.get('payment_id')} "
                f"({result.get('sequence_type')}, klant {result.get('customer_id')})"
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
        default="149.50",
        help="First payment in EUR (default 149.50: first month 50%% off).",
    )
    p_co.add_argument(
        "--plan",
        default=DEFAULT_PLAN,
        choices=sorted(PLAN_MONTHLY),
        help="Plan for the ongoing subscription (default chat, €299/month).",
    )

    p_status = sub.add_parser("status", help="List recent billing events from data/billing.jsonl.")
    p_status.add_argument("--limit", type=int, default=20)

    args = parser.parse_args(argv[1:])

    if args.cmd == "checkout":
        label = _plan_label(args.plan)
        try:
            amount = _eur(args.amount)
        except ValueError as exc:
            parser.error(str(exc))
        try:
            customer_id = create_customer(args.name, args.email)
            checkout_url = create_first_payment(
                customer_id, amount, f"Klantkraan {label} eerste maand", args.plan
            )
        except (MollieError, MissingSetting) as exc:
            print(f"❌ {exc}")
            return 1
        print(f"✅ klant aangemaakt: {customer_id}")
        print(f"   checkout (€{amount}): {checkout_url}")
        print(
            f"   Stuur deze link naar de klant. Na betaling start het abonnement "
            f"Klantkraan {label} (€{PLAN_MONTHLY[args.plan]}/maand) automatisch."
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
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
