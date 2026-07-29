"""BTW-compliant invoice (factuur) generation.

Given the GROSS amount Mollie actually charged, we back-compute net + 21% BTW so
the two always sum exactly to the charged amount, assign a gap-free sequential
invoice number, and render a clean print-ready HTML factuur. Each invoice is also
saved under data/invoices/ (7-year retention is a legal requirement in NL).

We deliberately refuse to build an invoice while the seller's KvK/BTW-id/address
are blank — an incomplete factuur is not legally valid, so it must fail loudly
rather than go out wrong.
"""
from __future__ import annotations

import html
import json
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from . import settings

CENTS = Decimal("0.01")
BTW_RATE = Decimal("0.21")
_COUNTER = settings.DATA_DIR / "invoice-counter.json"
_INVOICE_DIR = settings.DATA_DIR / "invoices"


def _cents(amount: Decimal) -> Decimal:
    return amount.quantize(CENTS, rounding=ROUND_HALF_UP)


def split_gross(gross: Decimal, rate: Decimal = BTW_RATE) -> tuple[Decimal, Decimal]:
    """net, btw from a fixed gross so net + btw == gross exactly."""
    net = _cents(gross / (Decimal("1") + rate))
    return net, _cents(gross - net)


def next_number(on: date | None = None) -> str:
    """Gap-free per-year sequence, e.g. '2026-0001'. Persisted so it never repeats."""
    on = on or date.today()
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    counters = json.loads(_COUNTER.read_text()) if _COUNTER.exists() else {}
    year = str(on.year)
    counters[year] = int(counters.get(year, 0)) + 1
    _COUNTER.write_text(json.dumps(counters, indent=2) + "\n")
    return f"{year}-{counters[year]:04d}"


def _require_seller() -> dict:
    seller = settings.SELLER
    missing = [k for k in ("name", "kvk", "btw", "address") if not seller.get(k)]
    if missing:
        raise SystemExit(
            "Seller identity incomplete for a legal factuur — set "
            + ", ".join(f"BILLING_SELLER_{k.upper()}" for k in missing)
            + " in billing/.env (from your KvK/BTW registration)."
        )
    return seller


@dataclass(frozen=True)
class Invoice:
    number: str
    invoice_date: date
    seller: dict
    buyer: dict
    description: str
    period: str
    net: Decimal
    btw: Decimal
    gross: Decimal
    btw_rate: Decimal
    payment_id: str | None = None


def build(
    *,
    gross: Decimal,
    buyer: dict,
    description: str,
    period: str,
    payment_id: str | None = None,
    on: date | None = None,
    number: str | None = None,
    assign_number: bool = True,
) -> Invoice:
    seller = _require_seller()
    net, btw = split_gross(gross)
    on = on or date.today()
    # An explicit number (webhook: pre-allocated + persisted per payment, so retries
    # reuse it) wins; else allocate a fresh sequential one; else a draft placeholder.
    if number is None:
        number = next_number(on) if assign_number else "CONCEPT"
    return Invoice(
        number=number,
        invoice_date=on,
        seller=seller,
        buyer=buyer,
        description=description,
        period=period,
        net=net,
        btw=btw,
        gross=_cents(gross),
        btw_rate=BTW_RATE,
        payment_id=payment_id,
    )


# --- Rendering ---------------------------------------------------------------
# The factuur is both an e-mail and the archived record, so it is built the way
# mail has to be built: nested tables and inline styles. The previous version used
# a <head> stylesheet and flexbox, neither of which Outlook honours -- the two
# address columns collapsed into one and the totals lost their rule. It also still
# carried the pre-redesign navy, so the invoice looked like a different company
# from the site the client had just bought from.
#
# Palette mirrors ai-receptionist/app/mail_layout.py. Duplicated rather than
# imported: these are two independently deployed apps with separate requirements,
# and a shared Python package for six colour constants is not worth the coupling.

_BAND = "#0f1c1e"
_INK = "#16292b"
_BODY = "#35474a"
_MUTED = "#5f7371"
_RULE = "#e2e8e7"
_FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif"
_LOGO = "https://klantkraan.nl/email/logo.png"


def render_html(inv: Invoice) -> str:
    e = html.escape

    def euro(v: Decimal) -> str:
        return f"&euro; {v:.2f}".replace(".", ",")

    def party(label: str, lines: list) -> str:
        rows = "<br>".join(e(str(x)) for x in lines if x)
        return (
            f'<td width="50%" valign="top" style="font-family:{_FONT};font-size:14px;'
            f'line-height:1.6;color:{_BODY};padding-right:16px;">'
            f'<div style="font-size:11px;letter-spacing:0.08em;text-transform:uppercase;'
            f'color:{_MUTED};padding-bottom:6px;">{e(label)}</div>{rows}</td>'
        )

    def total(label: str, value: str, *, grand: bool = False) -> str:
        weight = "700" if grand else "400"
        border = f"border-top:2px solid {_INK};" if grand else ""
        colour = _INK if grand else _BODY
        return (
            f'<tr><td style="font-family:{_FONT};font-size:14px;color:{colour};'
            f'font-weight:{weight};padding:8px 8px 8px 0;{border}">{label}</td>'
            f'<td align="right" style="font-family:{_FONT};font-size:14px;color:{colour};'
            f'font-weight:{weight};padding:8px 0;{border}">{value}</td></tr>'
        )

    btw_pct = f"{(inv.btw_rate * 100).quantize(Decimal('1'))}%"
    paid = "Betaald via automatische incasso (Mollie)"
    if inv.payment_id:
        paid += f" &middot; ref {e(inv.payment_id)}"
    iban = f"IBAN {e(inv.seller['iban'])}" if inv.seller.get("iban") else ""

    th = (
        f'font-family:{_FONT};font-size:11px;letter-spacing:0.08em;'
        f"text-transform:uppercase;color:{_MUTED};padding:0 8px 8px 0;"
        f"border-bottom:1px solid {_RULE};text-align:left;"
    )
    td = f"font-family:{_FONT};font-size:14px;color:{_BODY};padding:14px 8px 14px 0;"

    return f"""<!doctype html>
<html lang="nl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light">
<title>Factuur {e(inv.number)}</title></head>
<body style="margin:0;padding:0;background:#e9eeed;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#e9eeed;">
<tr><td align="center" style="padding:24px 12px;">
<table role="presentation" width="640" cellpadding="0" cellspacing="0" border="0" style="width:640px;max-width:100%;background:#ffffff;border-radius:14px;overflow:hidden;">
  <tr><td style="background:{_BAND};padding:26px 32px;">
    <img src="{_LOGO}" width="163" height="21" alt="Klantkraan" style="display:block;border:0;width:163px;height:21px;">
  </td></tr>
  <tr><td style="padding:32px 32px 0 32px;">
    <div style="font-family:{_FONT};font-size:24px;font-weight:700;color:{_INK};">Factuur</div>
    <div style="font-family:{_FONT};font-size:13px;color:{_MUTED};padding-top:4px;">
      Factuurnummer {e(inv.number)} &middot; Factuurdatum {inv.invoice_date.strftime('%d-%m-%Y')}
    </div>
  </td></tr>
  <tr><td style="padding:26px 32px 0 32px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
      {party("Van", [inv.seller["name"], inv.seller["address"], f"KvK {inv.seller['kvk']}", f"BTW {inv.seller['btw']}"])}
      {party("Aan", [inv.buyer.get("name"), inv.buyer.get("address"), inv.buyer.get("email")])}
    </tr></table>
  </td></tr>
  <tr><td style="padding:30px 32px 0 32px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
      <tr><th style="{th}">Omschrijving</th><th style="{th}">Periode</th>
          <th style="{th}text-align:right;padding-right:0;">Bedrag (excl. BTW)</th></tr>
      <tr><td style="{td}">{e(inv.description)}</td><td style="{td}">{e(inv.period)}</td>
          <td align="right" style="{td}padding-right:0;">{euro(inv.net)}</td></tr>
    </table>
  </td></tr>
  <tr><td style="padding:10px 32px 0 32px;">
    <table role="presentation" width="260" cellpadding="0" cellspacing="0" border="0" align="right" style="width:260px;">
      {total("Subtotaal (excl. BTW)", euro(inv.net))}
      {total(f"BTW {btw_pct}", euro(inv.btw))}
      {total("Totaal", euro(inv.gross), grand=True)}
    </table>
  </td></tr>
  <tr><td style="padding:34px 32px 28px 32px;">
    <div style="height:1px;background:{_RULE};margin-bottom:16px;"></div>
    <div style="font-family:{_FONT};font-size:12px;line-height:1.7;color:{_MUTED};">
      {paid}.<br>{iban}
    </div>
  </td></tr>
</table>
</td></tr></table>
</body></html>"""


def save(inv: Invoice, rendered: str) -> str:
    """Persist the invoice HTML for record-keeping; returns the path."""
    _INVOICE_DIR.mkdir(parents=True, exist_ok=True)
    path = _INVOICE_DIR / f"factuur-{inv.number}.html"
    path.write_text(rendered)
    return str(path)
