"""Set up a Mollie recurring subscription for a Klantkraan client.

Two steps, because the client must authorise the mandate themselves:

  link      create/find the Mollie customer and a first-payment checkout link.
            Send the printed URL to the client; paying it authorises the SEPA/
            card mandate (and, unless --mandate-only, charges the first month).

  activate  once the client has paid the link (a valid mandate exists), create
            the monthly subscription. Recurring charges run automatically from
            --start-date (default: one month out if the first month was already
            charged, else today).

  status    show the customer, mandate state and subscriptions for a client.

Plans are priced EX BTW; Mollie is charged the 21%-inclusive gross. Use --dry-run
on link/activate to print exactly what would be sent without calling Mollie.

Run from the billing/ directory, e.g.:
  python -m app.subscribe link meijer --plan chat --first-month-discount 0.5
  python -m app.subscribe activate meijer --plan chat
"""
from __future__ import annotations

import argparse
import json
from datetime import date
from decimal import Decimal

from . import clients, plans, settings, store
from .mollie import Mollie


def _plus_one_month(d: date) -> date:
    month = d.month + 1
    year = d.year + (month - 1) // 12
    month = (month - 1) % 12 + 1
    return date(year, month, min(d.day, 28))  # clamp to keep the billing anchor valid


def cmd_link(args: argparse.Namespace) -> None:
    p = plans.plan(args.plan)
    who = clients.resolve(args.slug, args.name, args.email)

    if args.mandate_only:
        amount = Decimal("0.00")
        kind = "mandate-only"
        desc = f"{p.label} — {who['name']} — machtiging"
    else:
        amount = p.gross
        if args.first_month_discount is not None:
            amount = plans.discounted(amount, Decimal(str(args.first_month_discount)))
        kind = "first-month"
        desc = f"{p.label} — {who['name']} — eerste maand"
    value = f"{amount:.2f}"
    webhook = f"{settings.WEBHOOK_BASE}/mollie/payment" if settings.WEBHOOK_BASE else None

    print(f"Client   : {who['name']} <{who['email']}>  (slug: {args.slug})")
    print(f"Plan     : {p.label} — EUR {p.net} ex BTW  ->  EUR {p.gross} incl 21% BTW / maand")
    print(f"First pay: EUR {value}  ({kind})")

    if args.dry_run:
        print("\n[dry-run] would create the customer (if new) and POST /payments:")
        print(json.dumps(
            {
                "amount": {"currency": "EUR", "value": value},
                "customerId": "<cst_...>",
                "sequenceType": "first",
                "description": desc,
                "redirectUrl": settings.REDIRECT_URL,
                "webhookUrl": webhook,
            },
            indent=2,
            ensure_ascii=False,
        ))
        return

    m = Mollie()
    rec = store.get(args.slug) or {}
    customer_id = rec.get("customer_id")
    if customer_id:
        print(f"Customer : reuse {customer_id}")
    else:
        cust = m.create_customer(who["name"], who["email"], metadata={"slug": args.slug})
        customer_id = cust["id"]
        print(f"Customer : created {customer_id}")

    pay = m.create_first_payment(
        customer_id=customer_id,
        amount_value=value,
        description=desc,
        redirect_url=settings.REDIRECT_URL,
        webhook_url=webhook,
    )
    store.put(args.slug, {
        **rec,
        "customer_id": customer_id,
        "name": who["name"],
        "email": who["email"],
        "plan": p.key,
        "first_payment": {"kind": kind, "value": value, "id": pay.get("id")},
    })
    url = pay.get("_links", {}).get("checkout", {}).get("href")
    print(f"\nSend this checkout link to the client:\n  {url}\n")
    print(f"After they pay it, run:  python -m app.subscribe activate {args.slug} --plan {p.key}")


def cmd_activate(args: argparse.Namespace) -> None:
    p = plans.plan(args.plan)
    rec = store.get(args.slug) or {}
    # If the first payment already covered month 1, start the subscription a month
    # out so we don't double-charge; a mandate-only setup starts today.
    mandate_only = (rec.get("first_payment") or {}).get("kind") == "mandate-only"
    default_start = date.today() if mandate_only else _plus_one_month(date.today())
    start = args.start_date or default_start.isoformat()
    webhook = f"{settings.WEBHOOK_BASE}/mollie/subscription" if settings.WEBHOOK_BASE else None
    value = p.gross_value()
    name = rec.get("name", args.slug)
    desc = f"{p.label} — {name} — maandabonnement"

    if args.dry_run:
        print(f"[dry-run] would create subscription: EUR {value}/maand, interval "
              f"{p.interval}, start {start}\n")
        print(json.dumps(
            {
                "amount": {"currency": "EUR", "value": value},
                "interval": p.interval,
                "description": desc,
                "startDate": start,
                "webhookUrl": webhook,
            },
            indent=2,
            ensure_ascii=False,
        ))
        return

    if not rec.get("customer_id"):
        raise SystemExit(f"No Mollie customer for '{args.slug}'. Run 'link' first.")
    customer_id = rec["customer_id"]

    m = Mollie()
    if not m.has_valid_mandate(customer_id):
        raise SystemExit(
            f"No valid mandate for {customer_id} yet — the client hasn't completed the "
            f"checkout link. Have them pay it, then re-run activate."
        )
    sub = m.create_subscription(
        customer_id=customer_id,
        amount_value=value,
        interval=p.interval,
        description=desc,
        start_date=start,
        webhook_url=webhook,
    )
    store.put(args.slug, {**rec, "subscription_id": sub.get("id"), "plan": p.key})
    print(f"Subscription live: {sub.get('id')} — EUR {value}/maand vanaf {start}.")


def cmd_status(args: argparse.Namespace) -> None:
    rec = store.get(args.slug) or {}
    if not rec.get("customer_id"):
        raise SystemExit(f"No Mollie customer recorded for '{args.slug}'.")
    customer_id = rec["customer_id"]
    m = Mollie()
    print(f"Client {args.slug}: customer {customer_id} ({rec.get('name', '?')})")
    print(f"  valid mandate : {m.has_valid_mandate(customer_id)}")
    subs = m.list_subscriptions(customer_id)
    if not subs:
        print("  subscriptions : none")
    for s in subs:
        amount = s.get("amount", {}).get("value", "?")
        print(f"  subscription {s.get('id')}: {s.get('status')} "
              f"EUR {amount}/{s.get('interval')} (next {s.get('nextPaymentDate', '-')})")


def _add_common(sp: argparse.ArgumentParser) -> None:
    sp.add_argument("slug", help="client slug (matches ai-receptionist/config/clients/<slug>.yaml)")
    sp.add_argument("--plan", required=True, choices=list(plans.PLANS), help="chat or compleet")
    sp.add_argument("--name", help="override customer name (else from the client config)")
    sp.add_argument("--email", help="override customer email (else from the client config)")
    sp.add_argument("--dry-run", action="store_true", help="print the request, call nothing")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="app.subscribe", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    link = sub.add_parser("link", help="create customer + first-payment checkout link")
    _add_common(link)
    link.add_argument("--first-month-discount", type=float, default=None,
                      help="e.g. 0.5 for 50%% off the first month")
    link.add_argument("--mandate-only", action="store_true",
                      help="charge EUR 0.00 (mandate only; no first-month charge)")
    link.set_defaults(func=cmd_link)

    act = sub.add_parser("activate", help="create the monthly subscription (after mandate)")
    _add_common(act)
    act.add_argument("--start-date", help="YYYY-MM-DD; default depends on the first payment")
    act.set_defaults(func=cmd_activate)

    st = sub.add_parser("status", help="show customer, mandate and subscriptions")
    st.add_argument("slug", help="client slug")
    st.set_defaults(func=cmd_status)

    args = ap.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
