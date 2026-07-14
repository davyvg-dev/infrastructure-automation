# billing — TASK

Mollie-only recurring billing + BTW invoicing. Tick as you go.

## Built
- [x] `app.subscribe` — link / activate / status CLI (Mollie customers, first
      payment, mandate, monthly subscription). Plans ex BTW; Mollie charged gross.
- [x] `app.invoice` — BTW factuur: sequential numbering, net/BTW split back from the
      charged gross, print-ready HTML, saved to `data/invoices/`, refuses on blank seller.
- [x] `app.mailer` — email the factuur via Resend.
- [x] `app.webhook` — Mollie webhook: on each paid recurring charge, build + email the
      factuur (idempotent per payment id). stdlib http.server.
- [x] `app.selftest` — offline: plan math, invoice split, factuur render + guardrail.

## Founder inputs to go live (Claude can't do these)
- [ ] Finish Mollie account verification (KYC: KvK, bank, ID) — needed before `live_` keys.
- [ ] Create a Mollie **test** key, then a **live** key → `billing/.env` `MOLLIE_API_KEY`.
- [ ] Supply KvK number + BTW-id + business address + IBAN → `BILLING_SELLER_*` in `.env`
      (these also unblock the site's company data — klantkraan TODO-D).
- [ ] Resend: verify the sending domain for `BILLING_SELLER_EMAIL`; put the key in `.env`.

## Wire the automatic invoicing (after the inputs)
- [ ] Deploy `app.webhook` behind Caddy at a stable URL; set `BILLING_WEBHOOK_BASE`
      to it (then `subscribe` registers the webhook with Mollie automatically).
- [ ] End-to-end on the **test** key: `link` a test client, pay the checkout link,
      `activate`, confirm the webhook issues + emails a factuur, check `data/invoices/`.

## Later
- [ ] PDF attachment (currently HTML factuur) — add a light renderer if clients want PDF.
- [ ] Dunning: handle failed/charged-back payments (Mollie `subscription`/`payment` webhooks).
- [ ] Reconciliation export for the boekhouder (CSV of invoices + Mollie settlements).

## Gates
- [ ] `python -m py_compile app/*.py`
- [ ] `python -m app.selftest`
- [ ] `python -m app.subscribe link <slug> --plan chat --dry-run` (no key needed)
