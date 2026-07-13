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

## Step 4a — Embeddable bubble (put the chat on a client's own site)

Full guide in `docs/WIDGET.md`. The chat stays same-origin inside an iframe → no CORS, no key leak.

- [ ] ▶ With the server running, paste on any test page:
      `<script src="http://127.0.0.1:8000/widget.js" defer data-label="Chat"></script>`
- [ ] ✓ A floating bubble appears bottom-right; clicking it opens the chat with the business
      greeting, and the host page's CSS doesn't leak in (shadow-root isolation).
- [ ] ✓ The hosted full-page link (`/`) still works as the no-code fallback.

---

## Step 4b — Multi-client routing (host many clients on one server)

Full convention in `config/clients/README.md`. `python -m app.selftest routing` covers it offline.

- [ ] ▶ Drop a config as `config/clients/<slug>.yaml`, restart the server.
- [ ] ✓ `curl -H "Host: <slug>.klantkraan.nl" .../config` returns that client; an unknown host
      falls back to `BUSINESS_CONFIG`. (Locally, `?client=<slug>` or `X-Client-Slug` works too.)

---

## Step 4c — Extra channels (optional, but great for demos)

Full setup in `docs/CHANNELS.md`. All channels share one brain, so if Step 3 passed these
"just work".

**Telegram:**
- [ ] ▶ Create a *second* bot with @BotFather; put its token in `.env` as
      `TELEGRAM_BOT_TOKEN`.
- [ ] ▶ `python -m app.channels.telegram_bot`
- [ ] ✓ Message the bot, send `/start`, and complete a booking in Telegram.

**WhatsApp (Twilio sandbox):**
- [ ] ▶ `python -m app.server`, then `ngrok http 8000` for a public URL.
- [ ] ▶ Join the Twilio WhatsApp sandbox and set its inbound webhook to
      `https://<ngrok>/whatsapp`.
- [ ] ✓ Message the sandbox number from your phone and complete a booking over WhatsApp.

---

## Step 5 — Rebrand test (the scaffolder)

- [ ] ▶ `python -m app.scaffold "Demo Plumbing Co" --phone "+31 20 555 0111"`
- [ ] ✓ It writes `config/demo-plumbing-co.yaml` and prints the run command.
- [ ] ▶ `BUSINESS_CONFIG=config/demo-plumbing-co.yaml python -m app.server`, restart.
- [ ] ✓ The widget + receptionist are now that business, no code changes. (Also try the
      ready-made `config/home-services-example.yaml`.)

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
