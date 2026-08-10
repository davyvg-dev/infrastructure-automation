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

## Step 9 — Buffer delivery (LinkedIn)

`delivery: buffer` hands an approved variant to Buffer's queue instead of posting it.
Buffer is an official LinkedIn partner, so this is sanctioned where a direct API call
is not. **Buffer owns the schedule** — cadence is tuned in Buffer's UI, never here.

- [x] ▶ `BUFFER_API_KEY` in `.env`; connect the channels at buffer.com
- [x] ▶ `python -m src.publish_buffer` → ✓ lists the channels and resolves each
      `delivery: buffer` platform to one of them (X appears as `twitter`)
- [x] ▶ `python -m src.selftest buffer` → ✓ passes, and reports slots/day per channel
- [x] ▶ `python -m src.publish_buffer --test-draft linkedin` → ✓ "write path OK": it
      creates a real post as a Buffer *draft* (which never sends), asserts Buffer honoured
      `saveToDraft`, then deletes it. Repeatable, leaves nothing behind.
- [x] ✓ Approval loop in dry-run: X reports a dry-run post, LinkedIn reports a dry-run
      queue, Reddit/Facebook come back as paste text, and the draft's status stays
      `posted` rather than being downgraded to `queued`.
- [ ] ▶ **Founder, in Buffer's UI:** cut the LinkedIn posting schedule to **1 slot/day**
      (it ships with 2, and `selftest buffer` warns about it) and move the slot into
      working hours — the defaults land at 21:28 / 22:44, which is not when Dutch
      business owners read LinkedIn.
- [ ] ▶ First real queue: run the bot for real, `/now`, tap ✅ → ✓ Telegram reports
      "🗓 Queued in Buffer: <channel> — goes out <time>", and the post is visible in
      Buffer's queue.

Not yet possible: **media through Buffer.** Buffer fetches assets by URL, and rendered
cards/reels live only in local `data/`. Until that directory is served over public HTTPS,
buffer posts go out text-only and say so. Instagram therefore stays `assisted` (a
caption-only IG post is rejected).

---

## Regression check (run any time you change code)

- [ ] `python -m py_compile src/*.py`
- [ ] `python -m pytest` (offline unit tests, tests/ — API calls mocked)
- [ ] `python -m src.selftest all` (or `config` if you only touched config)
- [ ] One dry-run `/now` cycle if you touched `bot.py`, `generate.py`, or `publish_x.py`.
- [ ] `python -m src.publish_buffer --test-draft <platform>` if you touched
      `publish_buffer.py` — it proves the write path without publishing.
