# billing — Mollie recurring subscriptions

Mollie-only billing for Klantkraan clients: a client authorises one payment,
Mollie then charges €299/€499 per month automatically. Invoicing (BTW facturen
emailed on each payment) is the scaffold step — see `TASK.md`.

Mollie is a payment processor, **not** an accounting tool: it does not issue BTW
invoices to your clients. This app does that itself (scaffold step), so from you
and the client's side it stays "Mollie only".

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

## Test

```sh
python -m app.selftest        # offline: plan math + payloads, no key needed
python -m py_compile app/*.py
```

Secrets live in `.env` (gitignored). The `data/` dir holds the local
slug → Mollie-customer map (gitignored). Start on a `test_` key; go live only
after Mollie has verified the account.
