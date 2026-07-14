# billing — Mollie recurring subscriptions

Mollie-only billing for Klantkraan clients: a client authorises one payment,
Mollie then charges €299/€499 per month automatically, and on each charge this
app emails the client a BTW-compliant factuur.

Mollie is a payment processor, **not** an accounting tool: it does not issue BTW
invoices to your clients. This app does that itself, so from you and the client's
side it stays "Mollie only". Go-live steps are in `TASK.md`.

## Setup (once)

```sh
cd billing
python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
cp .env.example .env         # then paste your Mollie TEST key into MOLLIE_API_KEY
```

Prices are quoted **ex BTW**; Mollie is charged the 21%-inclusive gross
(Chat €299 → €361.79, Compleet €499 → €603.79).

## Onboard a client

```sh
# 1) create the customer + a first-payment checkout link (50% off first month here)
python -m app.subscribe link meijer --plan chat --first-month-discount 0.5
#    -> prints a checkout URL. Send it to the client. Paying it sets up the mandate.

# 2) once they've paid, turn on the monthly subscription
python -m app.subscribe activate meijer --plan chat

# check state any time
python -m app.subscribe status meijer
```

`link`/`activate` accept `--dry-run` to print the exact Mollie request without
sending it. `--mandate-only` sets up the mandate with a €0.00 first payment (no
first-month charge). Client name/email come from
`ai-receptionist/config/clients/<slug>.yaml`; override with `--name`/`--email`.

## Automatic invoicing

`app.webhook` is a small server Mollie calls on every paid charge; it builds a
BTW factuur (net + 21% BTW, sequential number, saved to `data/invoices/`) and
emails it to the client via Resend. To turn it on: fill the seller identity +
`RESEND_API_KEY` in `.env`, deploy the webhook, and set `BILLING_WEBHOOK_BASE`
so `subscribe` registers the webhook URL with Mollie. See `TASK.md`.

```sh
python -m app.webhook          # POST /mollie/payment, GET /health (default :8090)
```

## Test

```sh
python -m app.selftest        # offline: plan math + payloads, no key needed
python -m py_compile app/*.py
```

Secrets live in `.env` (gitignored). The `data/` dir holds the local
slug → Mollie-customer map (gitignored). Start on a `test_` key; go live only
after Mollie has verified the account.
