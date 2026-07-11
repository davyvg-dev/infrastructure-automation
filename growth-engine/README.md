# Growth Engine

The content pipeline for **Klantkraan** (klantkraan.nl) — AI receptionists for Dutch
trade businesses. It markets the business build-in-public from the founder's personal
accounts.

It generates high-quality drafts with Claude, pushes them to you on Telegram for a
one-tap approval, auto-posts approved posts to X, and hands you ready-to-paste versions
for LinkedIn and Reddit.

```
 idea bank ──▶ Claude drafting ──▶ per-platform formatting
      │                                     │
      │                                     ▼
      │                        Telegram one-tap approval
      │                        (✅ approve / ✏️ rewrite / ❌ skip)
      │                                     │
      ▼                        ┌────────────┴────────────┐
  pillar rotation              ▼                         ▼
                        auto-post to X            ready-to-paste
                        (API)                     LinkedIn + Reddit
```

## What this is (and isn't)

- **Is:** a self-hosted content engine you own end to end. It doubles as a live demo of
  the automation work you sell.
- **Isn't:** a spam cannon. LinkedIn and Reddit ban obvious automation, so those two are
  *assisted* (drafted + scheduled to you, you paste). Only X auto-posts via its API.

## Quick start

```bash
cd growth-engine
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # then fill in your keys — see docs/SETUP.md
python -m src.run
```

Read **`docs/SETUP.md`** for the exact steps to create your Telegram bot and X API app,
and **`docs/STRATEGY.md`** for the positioning, content pillars, and 30-day plan.

## Build & test order

Don't wire it all up at once. **`TASK.md`** is a gated checklist that tests each process
in isolation before moving on — config → drafting → Telegram → X auth → full dry-run →
first real post. Each layer has an isolated self-test:

```bash
python -m src.selftest config      # config sanity, no network
python -m src.selftest generate    # Claude drafting only
python -m src.selftest telegram    # send a test message
python -m src.selftest x           # verify X auth (never posts)
python -m src.selftest all         # all of the above, in order
```

The repo-root **`CLAUDE.md`** (§ growth-engine rules) documents the conventions for working
in this project (config-over-code, one-module-one-job, never post in dev, respect platform ToS).

## How it runs

`src/run.py` starts one long-running process that:

1. On a schedule (see `config/content_strategy.yaml`), picks the next content pillar,
   generates a batch of drafts with Claude, and stores them in `data/queue.json`.
2. Sends each draft to your Telegram with inline buttons.
3. On **✅** it auto-posts the X version and marks LinkedIn/Reddit "ready to paste";
   on **✏️** it regenerates with your note; on **❌** it drops the draft.

Send **/buildlog** any time to draft a build-in-public post straight from your recent git
commits — real work in, honest post out (configured under `buildlog:` in the strategy YAML).

Run it on any always-on host — your laptop overnight, a €4/mo VPS, or a free
Fly.io/Railway instance. A GitHub Actions workflow for headless generation is included
in `deploy/` as an alternative if you don't have an always-on host (see SETUP).

## Layout

```
growth-engine/
├── README.md
├── requirements.txt
├── .env.example
├── config/
│   └── content_strategy.yaml   # offer, voice, pillars, cadence — edit this
├── docs/
│   ├── STRATEGY.md             # positioning, pillars, 30-day plan
│   └── SETUP.md                # step-by-step account + key setup
├── src/
│   ├── settings.py             # env + config loading
│   ├── store.py                # draft queue persistence
│   ├── ideas.py                # pillar rotation + idea bank
│   ├── prompts.py              # prompt templates per platform
│   ├── generate.py             # Claude drafting engine
│   ├── formatting.py           # per-platform formatting
│   ├── publish_x.py            # X (Twitter) posting
│   ├── bot.py                  # Telegram approval bot + scheduler
│   └── run.py                  # entrypoint
├── deploy/
│   └── github-actions.yml      # optional headless generation workflow
└── data/                       # runtime state (gitignored)
```
