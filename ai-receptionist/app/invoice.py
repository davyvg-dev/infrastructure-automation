"""BTW-compliant factuur for a Mollie payment: numbering, rendering, archiving, sending.

A Dutch B2B customer needs a factuur for every charge, not just a welcome mail — it is what
their bookkeeper puts in the administration and what lets them reclaim the BTW. Until this
existed the invoice renderer lived in the separate, undeployed `billing/` app and had never
been connected to a real payment, so nobody who paid us ever received one.

Three things this owes the Belastingdienst, and how each is met:

  * a gap-free sequential number  -- allocated once per payment_id and persisted, so a
    Mollie webhook replay reuses the number instead of burning the next one. Gaps in an
    invoice sequence are the thing an auditor asks about.
  * the seller's full identity    -- KvK, BTW-identificatienummer and address. The BTW
    number and address are still placeholders (see SELLER); `identity_complete()` reports
    that so every send can say so out loud rather than quietly issuing an invalid factuur.
  * a correct BTW split           -- derived by billing.split_gross from the amount that
    actually left the customer's account, so the factuur reconciles to the bank statement
    to the cent even for a discounted or test charge.

The document is built from mail_layout blocks, the same ones the welcome mail uses. That is
deliberate: the factuur is emailed before it is ever opened in a browser, so it has to be
built the way mail is built, and sharing the layout means the invoice cannot drift away from
the brand the customer just bought from. The archived copy under data/invoices/ is byte-for-
byte the HTML that was mailed, so the record and the customer's copy can never disagree.
"""

from __future__ import annotations

import json
import os
import threading
from dataclasses import dataclass
from datetime import date, datetime

from . import mail_layout, mailer, settings

_LOCK = threading.Lock()


# Resolved per call, never captured at import: settings.DATA_DIR is rebound by the test
# fixtures, and a module-level `DATA_DIR / ...` would keep pointing at the real store and
# write test invoices into it (see tests/conftest.py).
def _ledger_path():
    return settings.DATA_DIR / "invoices.json"


def _archive_dir():
    return settings.DATA_DIR / "invoices"


# --- Seller ------------------------------------------------------------------------------
# Name and KvK are registered and final (marketing-site/src/data/company.ts). The BTW-id and
# the address are not filed yet, so they carry obvious placeholders: an invoice that says
# "NL000000000B00" is visibly provisional, where a blank line just looks like a bug. Set the
# real values in .env the moment they exist -- nothing else has to change.

PLACEHOLDER_BTW = "NL000000000B00"
PLACEHOLDER_ADDRESS = "Adresgegevens volgen"

SELLER = {
    "name": "T4 Software Consulting BV",
    "trade_name": "Klantkraan",
    "kvk": "90232135",
    "btw": os.getenv("BILLING_SELLER_BTW", "") or PLACEHOLDER_BTW,
    "address": os.getenv("BILLING_SELLER_ADDRESS", "") or PLACEHOLDER_ADDRESS,
    "email": os.getenv("BILLING_SELLER_EMAIL", "hallo@klantkraan.nl"),
    "iban": os.getenv("BILLING_SELLER_IBAN", ""),
}


def seller() -> dict[str, str]:
    """Read at call time, not import time, so a .env edit takes effect on the next send."""
    return {
        **SELLER,
        "btw": os.getenv("BILLING_SELLER_BTW", "") or PLACEHOLDER_BTW,
        "address": os.getenv("BILLING_SELLER_ADDRESS", "") or PLACEHOLDER_ADDRESS,
        "iban": os.getenv("BILLING_SELLER_IBAN", ""),
    }


def identity_complete() -> tuple[bool, list[str]]:
    """(ok, missing). A factuur with a placeholder BTW-id is not legally valid, so callers
    surface this to the founder on every send instead of failing the webhook over it."""
    current = seller()
    missing = []
    if current["btw"] == PLACEHOLDER_BTW:
        missing.append("BILLING_SELLER_BTW")
    if current["address"] == PLACEHOLDER_ADDRESS:
        missing.append("BILLING_SELLER_ADDRESS")
    return (not missing), missing


# --- Numbering ---------------------------------------------------------------------------

_MONTHS_NL = [
    "januari", "februari", "maart", "april", "mei", "juni",
    "juli", "augustus", "september", "oktober", "november", "december",
]  # fmt: skip


def _read_ledger() -> dict:
    ledger = _ledger_path()
    if not ledger.exists():
        return {"counter": {}, "payments": {}}
    try:
        data = json.loads(ledger.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"counter": {}, "payments": {}}
    data.setdefault("counter", {})
    data.setdefault("payments", {})
    return data


def number_for_payment(payment_id: str, on: date | None = None) -> str:
    """The invoice number for this payment, allocating one only the first time.

    Counter and payment map live in ONE file under ONE lock: if they were separate, a crash
    between the two writes would either skip a number or issue the same one twice.
    """
    on = on or date.today()
    year = str(on.year)
    with _LOCK:
        ledger = _read_ledger()
        existing = ledger["payments"].get(payment_id)
        if existing:
            return existing
        nth = int(ledger["counter"].get(year, 0)) + 1
        number = f"{year}-{nth:04d}"
        ledger["counter"][year] = nth
        ledger["payments"][payment_id] = number
        path = _ledger_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return number


# --- Document ----------------------------------------------------------------------------


@dataclass(frozen=True)
class Invoice:
    number: str
    invoice_date: date
    buyer: dict
    description: str
    period: str
    net: str
    btw: str
    gross: str
    payment_id: str


def _eur_nl(amount: str) -> str:
    """'361.79' as a Dutch reader expects it: '€ 361,79'."""
    return "€ " + str(amount).replace(".", ",")


def build(
    *,
    payment_id: str,
    gross_eur: str,
    buyer: dict,
    description: str,
    on: date | None = None,
    period: str | None = None,
) -> Invoice:
    """Split the charged gross and stamp it with a number. Pure apart from the number, which
    is idempotent per payment, so calling this twice for one payment yields the same factuur.
    """
    from . import billing  # local: billing imports nothing from here, keeps the cycle out

    on = on or date.today()
    net, btw = billing.split_gross(gross_eur)
    return Invoice(
        number=number_for_payment(payment_id, on),
        invoice_date=on,
        buyer=buyer,
        description=description,
        period=period or f"{_MONTHS_NL[on.month - 1]} {on.year}",
        net=net,
        btw=btw,
        gross=billing._eur(gross_eur),
        payment_id=payment_id,
    )


def subject(inv: Invoice) -> str:
    return f"Factuur {inv.number} van Klantkraan"


def blocks(inv: Invoice) -> list[mail_layout.Block]:
    from . import billing

    current = seller()
    btw_pct = f"{billing.BTW_RATE:.0%}"
    paid = f"Betaald via automatische incasso (Mollie), referentie {inv.payment_id}."
    if current["iban"]:
        paid += f" IBAN {current['iban']}."

    return [
        # The archived copy is opened on its own, outside any mail subject, so the document
        # has to name itself.
        mail_layout.Heading("Factuur"),
        mail_layout.Para(
            f"Factuurnummer {inv.number} · Factuurdatum {inv.invoice_date.strftime('%d-%m-%Y')}"
        ),
        mail_layout.Columns(
            "Van",
            [
                current["name"],
                current["address"],
                f"KvK {current['kvk']}",
                f"BTW {current['btw']}",
            ],
            "Aan",
            [line for line in (inv.buyer.get("name"), inv.buyer.get("email")) if line],
        ),
        mail_layout.Table(
            ["Omschrijving", "Periode", "Bedrag excl. BTW"],
            [[inv.description, inv.period, _eur_nl(inv.net)]],
        ),
        mail_layout.Totals(
            [("Subtotaal excl. BTW", _eur_nl(inv.net)), (f"BTW {btw_pct}", _eur_nl(inv.btw))],
            ("Totaal", _eur_nl(inv.gross)),
        ),
        mail_layout.Para(paid),
        mail_layout.Para(
            "Deze factuur is automatisch aangemaakt en is zonder handtekening geldig."
        ),
        mail_layout.Signoff("Klantkraan", current["email"]),
    ]


def to_html(inv: Invoice) -> str:
    return mail_layout.to_html(
        blocks(inv),
        subject=subject(inv),
        preheader=f"Factuur {inv.number} · {_eur_nl(inv.gross)} · betaald via automatische incasso",
    )


def to_text(inv: Invoice) -> str:
    return mail_layout.to_text(blocks(inv))


def archive(inv: Invoice, rendered: str) -> str:
    """Keep the exact document that was mailed. NL law wants 7 years of these."""
    archive_dir = _archive_dir()
    archive_dir.mkdir(parents=True, exist_ok=True)
    path = archive_dir / f"factuur-{inv.number}.html"
    path.write_text(rendered, encoding="utf-8")
    return str(path)


def send(
    *,
    payment_id: str,
    gross_eur: str,
    to: str,
    buyer_name: str,
    description: str,
    on: date | None = None,
) -> dict:
    """Build, archive and mail the factuur. Never raises — the money has already moved.

    Returns {"sent", "to", "number", "path", "reason", "placeholder_identity"}.
    """
    result: dict = {
        "sent": False,
        "to": to,
        "number": None,
        "path": None,
        "reason": "",
        "placeholder_identity": [],
    }
    if not to.strip():
        result["reason"] = "no e-mail address to invoice"
        return result
    try:
        inv = build(
            payment_id=payment_id,
            gross_eur=gross_eur,
            buyer={"name": buyer_name, "email": to},
            description=description,
            on=on,
        )
        rendered = to_html(inv)
        result["number"] = inv.number
        result["path"] = archive(inv, rendered)
        ok, missing = identity_complete()
        if not ok:
            result["placeholder_identity"] = missing
        # Keyed on the payment: a webhook replay inside Resend's 24h window cannot send a
        # second copy of the same factuur.
        result["sent"] = mailer.send(
            to,
            subject(inv),
            to_text(inv),
            html=rendered,
            idempotency_key=f"factuur-{payment_id}",
        )
        if not result["sent"]:
            result["reason"] = "mailer refused or is not configured"
    except Exception as exc:  # noqa: BLE001 — a broken factuur must not fail a paid webhook
        result["reason"] = f"{type(exc).__name__}: {exc}"
    return result


def _cli(argv: list[str]) -> int:
    """Preview a factuur offline: python -m app.invoice [--html out.html]"""
    import argparse

    parser = argparse.ArgumentParser(prog="app.invoice", description="Preview a factuur.")
    parser.add_argument("--gross", default="361.79", help="Charged amount incl. BTW.")
    parser.add_argument("--html", default="", help="Write the HTML part here and print the path.")
    args = parser.parse_args(argv[1:])

    from . import billing

    net, btw = billing.split_gross(args.gross)
    inv = Invoice(
        number="CONCEPT",
        invoice_date=datetime.now().date(),
        buyer={"name": "Jan de Vries BV", "email": "jan@devries.nl"},
        description="Klantkraan Chat maandabonnement",
        period=f"{_MONTHS_NL[datetime.now().month - 1]} {datetime.now().year}",
        net=net,
        btw=btw,
        gross=billing._eur(args.gross),
        payment_id="tr_voorbeeld",
    )
    print(f"Onderwerp: {subject(inv)}\n")
    print(to_text(inv))
    ok, missing = identity_complete()
    if not ok:
        print(f"\n⚠️  Nog niet rechtsgeldig: {', '.join(missing)} staat nog op een placeholder.")
    if args.html:
        from pathlib import Path

        target = Path(args.html).expanduser()
        target.write_text(to_html(inv), encoding="utf-8")
        print(f"HTML: {target}")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(_cli(sys.argv))
