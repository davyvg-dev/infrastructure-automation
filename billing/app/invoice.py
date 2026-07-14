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


def render_html(inv: Invoice) -> str:
    e = html.escape

    def euro(v: Decimal) -> str:
        return f"&euro; {v:.2f}".replace(".", ",")

    seller_lines = "<br>".join(
        e(x) for x in [
            inv.seller["name"], inv.seller["address"],
            f"KvK {inv.seller['kvk']}", f"BTW {inv.seller['btw']}",
        ] if x
    )
    buyer_lines = "<br>".join(
        e(str(x)) for x in [inv.buyer.get("name"), inv.buyer.get("address"),
                            inv.buyer.get("email")] if x
    )
    btw_pct = f"{(inv.btw_rate * 100).quantize(Decimal('1'))}%"
    return f"""<!doctype html>
<html lang="nl"><head><meta charset="utf-8"><title>Factuur {e(inv.number)}</title>
<style>
  body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;color:#1a2b3c;max-width:720px;margin:32px auto;padding:0 24px;line-height:1.5}}
  h1{{font-size:24px;margin:0 0 4px}} .muted{{color:#6b7684}}
  .row{{display:flex;justify-content:space-between;gap:24px;margin-top:24px}}
  table{{width:100%;border-collapse:collapse;margin-top:28px}}
  th,td{{text-align:left;padding:10px 8px;border-bottom:1px solid #e3e8ee}}
  td.n,th.n{{text-align:right}} .totals td{{border:0;padding:4px 8px}}
  .totals .grand{{font-weight:700;border-top:2px solid #1a2b3c}}
</style></head><body>
  <h1>Factuur</h1>
  <div class="muted">Factuurnummer {e(inv.number)} &middot; Factuurdatum {inv.invoice_date.strftime('%d-%m-%Y')}</div>
  <div class="row">
    <div><strong>Van</strong><br>{seller_lines}</div>
    <div><strong>Aan</strong><br>{buyer_lines}</div>
  </div>
  <table>
    <thead><tr><th>Omschrijving</th><th>Periode</th><th class="n">Bedrag (excl. BTW)</th></tr></thead>
    <tbody><tr><td>{e(inv.description)}</td><td>{e(inv.period)}</td><td class="n">{euro(inv.net)}</td></tr></tbody>
  </table>
  <table class="totals">
    <tr><td>Subtotaal (excl. BTW)</td><td class="n">{euro(inv.net)}</td></tr>
    <tr><td>BTW {btw_pct}</td><td class="n">{euro(inv.btw)}</td></tr>
    <tr class="grand"><td>Totaal</td><td class="n">{euro(inv.gross)}</td></tr>
  </table>
  <p class="muted" style="margin-top:28px">
    Betaald via automatische incasso (Mollie){f' &middot; ref {e(inv.payment_id)}' if inv.payment_id else ''}.
    {('IBAN ' + e(inv.seller['iban'])) if inv.seller.get('iban') else ''}
  </p>
</body></html>"""


def save(inv: Invoice, rendered: str) -> str:
    """Persist the invoice HTML for record-keeping; returns the path."""
    _INVOICE_DIR.mkdir(parents=True, exist_ok=True)
    path = _INVOICE_DIR / f"factuur-{inv.number}.html"
    path.write_text(rendered)
    return str(path)
