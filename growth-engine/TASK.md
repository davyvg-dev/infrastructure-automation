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

- [ ] ▶ Put your Anthropic key in `.env` (see `docs/SETUP.md` §1) — **BLOCKED: the current
      value is the `sk-ant-...` placeholder; founder must paste a real key**
- [ ] ▶ `python -m src.selftest generate`
- [ ] ✓ You get a pillar, a topic, and an X + LinkedIn variant printed, X under 280 chars.
- [ ] ✓ **Read the output.** Does it sound like you and match the offer? If not, tune
      `voice` / `pillars` in the YAML (Step 1) and re-run until the drafts are good.

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

- [ ] ▶ Run everything together: `python -m src.selftest all` → ✓ all four pass.

---

## Step 5 — Full approval flow in DRY-RUN (nothing goes live)

Now wire the pieces together, but with posting disabled so mistakes are harmless.

- [ ] ▶ `GROWTH_ENGINE_DRY_RUN=1 python -m src.run`
- [ ] ✓ You get a "Growth Engine started" message in Telegram.
- [ ] ▶ Send the bot `/now`.
- [ ] ✓ A draft arrives with ✅ / ✏️ / ❌ buttons.
- [ ] ▶ Tap **✏️**, send a note like "punchier hook" → ✓ it returns a rewritten draft.
- [ ] ▶ Tap **✅** → ✓ it reports the X post as a **dry-run** (not actually posted) and
      hands you the LinkedIn text to paste.
- [ ] ▶ Tap **❌** on another draft → ✓ it marks it skipped.

**Everything above happens without a single real post. Confirm the whole loop feels right.**

---

## Step 6 — First real post

- [ ] ▶ Stop the dry-run. Start for real: `python -m src.run`
- [ ] ▶ `/now`, review a draft, tap **✅**.
- [ ] ✓ It posts to X and returns the live URL; LinkedIn text arrives to paste.
- [ ] ▶ Check the post actually on X. 🎉

---

## Step 7 — Scheduling & cadence

- [ ] ✓ With the bot running, scheduled runs fire per `cadence.active` (starts at
      `starter`). You'll get drafts automatically inside the waking-hours window.
- [ ] ▶ When the drafts are consistently good, raise cadence: set `cadence.active` to
      `growth` (or `aggressive`) in the YAML, then send `/start` to reschedule.

---

## Step 8 — Decide where it runs long-term

- [ ] ▶ Pick a home for the always-on process (laptop → small VPS → free Fly/Railway).
      See `docs/SETUP.md` "Where to run it long-term".
- [ ] ▶ No always-on host? Activate the headless path: copy `deploy/github-actions.yml`
      to `.github/workflows/` and add the secrets. It generates + pushes drafts for manual
      posting (no X auto-post in that mode).

---

## Regression check (run any time you change code)

- [ ] `python -m py_compile src/*.py`
- [ ] `python -m src.selftest all` (or `config` if you only touched config)
- [ ] One dry-run `/now` cycle if you touched `bot.py`, `generate.py`, or `publish_x.py`.
