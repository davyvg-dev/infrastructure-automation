# TASK.md — build & test, one process at a time

Work top to bottom. Each step has a check to pass before moving on. Commands assume you're
in `ai-receptionist/` with the virtualenv active.

---

## Step 0 — Install

- [ ] ▶ `python -m venv .venv && source .venv/bin/activate`
- [ ] ▶ `pip install -r requirements.txt`
- [ ] ▶ `cp .env.example .env`
- [ ] ✓ `python -m py_compile app/*.py` prints nothing.

---

## Step 1 — Config (no keys, no network)

- [ ] ▶ `python -m app.selftest config`
- [ ] ✓ Prints the business, persona, services, and model with no errors.

---

## Step 2 — Calendar logic (no keys, no network)

Proves slot generation and booking work before any AI is involved.

- [ ] ▶ `python -m app.selftest calendar`
- [ ] ✓ Generates open days, books the first slot, and confirms it's no longer offered
      (double-booking prevented).

---

## Step 3 — The receptionist agent (needs `ANTHROPIC_API_KEY`)

Tests Claude + tools end to end, in the terminal, no web UI yet.

- [ ] ▶ Put your Anthropic key in `.env`.
- [ ] ▶ `python -m app.selftest agent`
- [ ] ✓ A scripted 3-message conversation results in a booking with a confirmation code.
- [ ] ▶ Then go free-form: `python -m app.selftest chat`
- [ ] ✓ Try to break it — ask for hours, prices, a closed day, an unavailable time. It
      should stay in character, only offer real slots, and collect name+contact before
      booking. Tune `persona` / `guardrails` / `faq` in the YAML until it feels right.

**This is the quality gate — the demo is only as good as this conversation.**

---

## Step 4 — Web widget

- [ ] ▶ `python -m app.server`
- [ ] ▶ Open <http://127.0.0.1:8000>
- [ ] ✓ The widget shows your business name and greeting, and a full booking works through
      the chat UI (check `data/bookings.json` for the record).
- [ ] ✓ Looks right on a phone-width window (it's mobile-first).

---

## Step 5 — Rebrand test

- [ ] ▶ Copy `config/business.yaml` → `config/demo2.yaml`, change the business to a
      different type (e.g. a salon or a garage), set `BUSINESS_CONFIG=config/demo2.yaml`.
- [ ] ▶ Restart the server.
- [ ] ✓ The widget + receptionist are now the new business, with no code changes.

---

## Step 6 — Make it content & pitch material

- [ ] ▶ Follow `docs/DEMO.md` to record a short clip of a booking happening.
- [ ] ▶ Drop the clip / screenshots into the `growth-engine/` approval flow as a
      `proof_demo` post.
- [ ] ▶ For a prospect: rebrand to their business, screen-share, and offer to wire it to
      their real calendar.

---

## Regression check (after any code change)

- [ ] `python -m py_compile app/*.py`
- [ ] `python -m app.selftest config` and `calendar` (offline)
- [ ] `python -m app.selftest agent` if you touched `receptionist.py` or `tools.py`.
