"""Mollie webhook: issue the factuur automatically on each paid charge.

Mollie POSTs `id=<payment id>` to this endpoint; we re-fetch the payment (never
trust the POST body), and when it is a paid recurring charge we build a BTW
factuur, save it, and email it to the client. Idempotent: each payment id is
invoiced at most once.

Runs on stdlib http.server (deploy behind Caddy/nginx like the receptionist):
  export BILLING_WEBHOOK_BASE=https://billing.klantkraan.nl
  python -m app.webhook            # binds 0.0.0.0:8090

Once BILLING_WEBHOOK_BASE is set, the subscribe CLI points Mollie's webhookUrl
here automatically. Requires MOLLIE_API_KEY, RESEND_API_KEY, and the seller's
KvK/BTW-id in .env to actually send invoices.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import date, datetime
from decimal import Decimal
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

from . import clients, invoice, mailer, plans, settings, store
from .mollie import Mollie

log = logging.getLogger("billing.webhook")

# payment id -> {number, emailed}. Persisted so a retried webhook reuses the SAME
# invoice number (never burns a fresh one or emails a duplicate).
_ISSUED = settings.DATA_DIR / "issued-invoices.json"
_DUTCH_MONTHS = ["", "januari", "februari", "maart", "april", "mei", "juni",
                 "juli", "augustus", "september", "oktober", "november", "december"]


def _issued_load() -> dict:
    return json.loads(_ISSUED.read_text()) if _ISSUED.exists() else {}


def _issued_save(data: dict) -> None:
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    _ISSUED.write_text(json.dumps(data, indent=2) + "\n")


def _period_label(iso: str | None) -> str:
    d = date.today()
    if iso:
        try:
            d = datetime.fromisoformat(iso.replace("Z", "+00:00")).date()
        except ValueError:
            pass
    return f"{_DUTCH_MONTHS[d.month]} {d.year}"


def _is_recurring(payment: dict) -> bool:
    return bool(payment.get("subscriptionId")) or payment.get("sequenceType") in ("first", "recurring")


def process_payment(payment_id: str) -> str:
    """Fetch, validate, invoice, email. Returns a short status. Idempotent:
    one payment -> one invoice number, reused (and email re-sent) on any retry."""
    issued = _issued_load()
    entry = issued.get(payment_id)
    if entry and entry.get("emailed"):
        return "already-invoiced"

    payment = Mollie().get_payment(payment_id)
    if payment.get("status") != "paid":
        return f"ignored ({payment.get('status')})"
    if not _is_recurring(payment):
        return "ignored (not recurring)"

    customer_id = payment.get("customerId")
    slug = clients.by_customer_id(customer_id) if customer_id else None
    rec = store.get(slug) if slug else None
    if not rec:
        raise RuntimeError(f"no local client for Mollie customer {customer_id} (payment {payment_id})")

    # Allocate the invoice number once and persist BEFORE emailing, so a failed
    # email -> Mollie retry reuses this number instead of burning a new one.
    if entry is None:
        entry = {"number": invoice.next_number(), "emailed": False}
        issued[payment_id] = entry
        _issued_save(issued)

    buyer = clients.from_config(slug) or {}
    buyer.setdefault("name", rec.get("name"))
    buyer.setdefault("email", rec.get("email"))
    plan = plans.PLANS.get(rec.get("plan", ""))
    description = plan.label if plan else "Klantkraan-abonnement"
    gross = Decimal(payment["amount"]["value"])
    period = _period_label(payment.get("paidAt"))

    inv = invoice.build(gross=gross, buyer=buyer, description=description,
                        period=period, payment_id=payment_id, number=entry["number"])
    rendered = invoice.render_html(inv)
    path = invoice.save(inv, rendered)
    msg_id = mailer.send_invoice(
        to=buyer["email"],
        subject=f"Factuur {inv.number} — {settings.SELLER['name']}",
        html_body=rendered,
    )
    entry["emailed"] = True
    _issued_save(issued)
    log.info("invoiced %s -> %s (%s), emailed %s", payment_id, inv.number, path, msg_id)
    return f"invoiced {inv.number}"


class _Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: str = "") -> None:
        self.send_response(code)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(body.encode())

    def do_GET(self) -> None:  # noqa: N802
        if self.path.rstrip("/") == "/health":
            self._send(200, "ok")
        else:
            self._send(404, "not found")

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(length).decode() if length else ""
        payment_id = (parse_qs(raw).get("id") or [""])[0]
        if not payment_id:
            self._send(400, "missing id")
            return
        try:
            self._send(200, process_payment(payment_id))
        except Exception as e:  # keep the server up; 500 => Mollie retries later
            log.exception("webhook failed for %s", payment_id)
            self._send(500, f"error: {e}")

    def log_message(self, *args) -> None:  # silence the default per-request logging
        pass


def main() -> None:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8090"))
    log.info("billing webhook on %s:%s (health: GET /health, Mollie: POST /mollie/payment)", host, port)
    ThreadingHTTPServer((host, port), _Handler).serve_forever()


if __name__ == "__main__":
    main()
