# TASK.md — build & test, one process at a time

Work through this top to bottom. **Each step has a check you must pass before moving on.**
Don't wire the whole thing up and debug it as a blob — verify each layer in isolation
first. Tick the boxes as you go.

Legend: `▶` = do this · `✓` = passes when… · commands assume you're in `growth-engine/`
with the virtualenv active.

---

## Step 0 — Install & environment

- [x] ▶ `python -m venv .venv && source .venv/bin/activate` (Python 3.12)
- [x] ▶ `pip install -r requirements.txt`
- [x] ▶ `cp .env.example .env`
- [x] ✓ `python -m py_compile src/*.py` prints nothing (all modules compile)

---

## Step 1 — Config loads and is sane

No keys needed yet. This proves the strategy file parses and the cadence is valid.

- [x] ▶ `python -m src.selftest config`
- [x] ✓ It prints your offer, the four pillars, and the active cadence with no errors.
- [ ] ▶ (optional) Edit `config/content_strategy.yaml` — tweak `brand`, `voice`, or
      `cadence.active` — and re-run. Confirm your change shows up.

**Only continue once config prints cleanly.**

---

## Step 2 — Claude drafting (the engine core)

Needs `ANTHROPIC_API_KEY` in `.env`. This tests generation end to end with **no** Telegram
or X involved — pure "does Claude produce good drafts."

- [x] ▶ Put your Anthropic key in `.env` (see `docs/SETUP.md` §1) — real key in place,
      auth passes (credits purchased 2026-07-11)
- [x] ▶ `python -m src.selftest generate`
- [x] ✓ You get a pillar, a topic, and an X + LinkedIn variant printed, X under 280 chars.
      (Dutch, proof_demo pillar, X at 262 chars.)
- [x] ✓ **Read the output.** Does it sound like you and match the offer? If not, tune
      `voice` / `pillars` in the YAML (Step 1) and re-run until the drafts are good.
      (Founder reviewed drafts in the dry-run loop 2026-07-11: "works great".)

**This is the most important gate. Don't move on until the drafts are ones you'd post.**

---

## Step 3 — Telegram delivery

Needs `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID`. Tests that the bot can reach *you*.

- [x] ▶ Create the bot and get your chat id (see `docs/SETUP.md` §2). **Message your bot
      once** first, or it can't message you.
- [x] ▶ `python -m src.selftest telegram`
- [x] ✓ A "Telegram is wired up" test message lands in your chat (@davy_growth_bot).

---

## Step 4 — X authentication (no posting yet)

Needs the four `X_*` values. Verifies auth **without** publishing anything.

- [x] ▶ Create the X app with **Read + Write** and fill in `.env` (see `docs/SETUP.md` §3)
- [x] ▶ `python -m src.selftest x`
- [x] ✓ It prints "authenticated as @you". If it fails on auth, regenerate the access
      token *after* enabling Read+Write (the usual culprit). (Passed as @davy22036589.)

- [x] ▶ Run everything together: `python -m src.selftest all` → ✓ all four pass.

---

## Step 5 — Full approval flow in DRY-RUN (nothing goes live)

Now wire the pieces together, but with posting disabled so mistakes are harmless.

- [x] ▶ `GROWTH_ENGINE_DRY_RUN=1 python -m src.run`
- [x] ✓ You get a "Growth Engine started" message in Telegram.
- [x] ▶ Send the bot `/now`.
- [x] ✓ A draft arrives with ✅ / ✏️ / ❌ buttons.
- [x] ▶ Tap **✏️**, send a note like "punchier hook" → ✓ it returns a rewritten draft.
- [x] ▶ Tap **✅** → ✓ it reports the X post as a **dry-run** (not actually posted) and
      hands you the LinkedIn text to paste.
- [x] ▶ Tap **❌** on another draft → ✓ it marks it skipped.
      (Founder walked the full loop in dry-run, 2026-07-11.)

**Everything above happens without a single real post. Confirm the whole loop feels right.**

---

## Step 6 — First real post

- [x] ▶ Stop the dry-run. Start for real: `python -m src.run`
- [x] ▶ `/now`, review a draft, tap **✅**.
- [x] ✓ It posts to X and returns the live URL; LinkedIn text arrives to paste.
- [x] ▶ Check the post actually on X. 🎉

(Done 2026-07-12 — first live post approved via the bot; URL recorded in
`data/queue.json`, draft `20260712-85ed`.)

---

## Step 7 — Scheduling & cadence

- [ ] ✓ With the bot running, scheduled runs fire per `cadence.active` (starts at
      `starter`). You'll get drafts automatically inside the waking-hours window.
- [ ] ▶ When the drafts are consistently good, raise cadence: set `cadence.active` to
      `growth` (or `aggressive`) in the YAML, then send `/start` to reschedule.

---

## Step 8 — Decide where it runs long-term

- [ ] ▶ Pick a home for the always-on process (laptop → small VPS → free Fly/Railway).
      See `docs/SETUP.md` "Where to run it long-term". A ready systemd unit + deploy
      script for Hetzner already exists at `../ops/hetzner/` (growth-engine.service).
- [ ] ▶ No always-on host? Activate the headless path: copy `deploy/github-actions.yml`
      to `.github/workflows/` and add the secrets. It generates + pushes drafts for manual
      posting (no X auto-post in that mode).

---

## Regression check (run any time you change code)

- [ ] `python -m py_compile src/*.py`
- [ ] `python -m src.selftest all` (or `config` if you only touched config)
- [ ] One dry-run `/now` cycle if you touched `bot.py`, `generate.py`, or `publish_x.py`.
