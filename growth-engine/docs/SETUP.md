# Setup

~30 minutes, one time. You already have X, LinkedIn, Telegram, and an LLM key — this
walks you through wiring them together.

## 0. Install

```bash
cd growth-engine
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Keep `.env` private — it's gitignored. Fill it in as you go through the steps below.

Reels (turning your screen recordings into branded 9:16 videos via the bot's 🎬
button) need **ffmpeg** on the machine the bot runs on: `brew install ffmpeg` on
macOS; the Hetzner deploy script installs it automatically. Verify with
`python -m src.selftest reel`.

## 1. Claude API key (drafting engine)

You said you have an LLM key. This project uses **Claude** (`claude-opus-4-8`).

- If it's an Anthropic key, paste it into `.env` as `ANTHROPIC_API_KEY`.
- Get/manage keys at <https://console.anthropic.com> → API keys.
- Cost is small: each draft is a short generation (~cents). At 2–3 posts/day you're
  looking at a couple of euros a month, well inside your budget.

> Using a non-Anthropic key? The drafting code is Claude-specific. Easiest path is to add
> a small Anthropic key; if you'd rather reuse another provider, tell me and I'll swap the
> `src/generate.py` engine.

## 2. Telegram bot (one-tap approvals)

1. In Telegram, message **@BotFather** → `/newbot` → follow prompts. It gives you a
   **bot token** like `123456:ABC-DEF...`. Put it in `.env` as `TELEGRAM_BOT_TOKEN`.
2. Open a chat with your new bot and send it any message (e.g. "hi"). This is required so
   the bot is allowed to message you.
3. Get your **chat id**: message **@userinfobot** (it replies with your numeric id), or
   visit `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` in a browser after step 2
   and read `chat.id`. Put it in `.env` as `TELEGRAM_CHAT_ID`.

## 3. X (Twitter) API (auto-posting)

X's write API needs a developer app with OAuth 1.0a user context.

1. Go to <https://developer.x.com> → sign up for a developer account (Free tier is fine
   for a personal brand's posting volume).
2. Create a **Project** and an **App** inside it.
3. In the app's **User authentication settings**, enable OAuth 1.0a with **Read and
   write** permissions. (Read-only tokens can't post.)
4. From **Keys and tokens**, copy:
   - API Key + Secret → `.env` as `X_API_KEY` / `X_API_SECRET`
   - Access Token + Secret → `.env` as `X_ACCESS_TOKEN` / `X_ACCESS_TOKEN_SECRET`
   - ⚠️ If you generated the access token *before* setting Read+Write, regenerate it after,
     or posts will 403.

> Free-tier write limits are modest but enough for daily posting. If you outgrow them, the
> Basic tier raises the cap — but don't pay for it until you actually need to.

## 4. LinkedIn & Reddit

No API keys needed — these are **assisted**: the engine drafts and hands you the text to
paste. This is deliberate (their ToS forbid automated posting, and native posts perform
better anyway). Just be logged in on your phone/desktop when you approve.

## 5. Run it

Dry-run first (generates and messages you, but never actually posts to X):

```bash
GROWTH_ENGINE_DRY_RUN=1 python -m src.run
```

In Telegram, send your bot `/now` — you should get a draft with ✅ / ✏️ / ❌ buttons.
Approving in dry-run shows what *would* post. When you're happy, run for real:

```bash
python -m src.run
```

It schedules generation per `config/content_strategy.yaml` (starts at the "starter"
cadence) and runs until you stop it.

## Where to run it long-term

`src/run.py` is a long-running process. Options, cheapest first:

- **Your laptop**, while you're warming up. Simplest; just leave it running.
- **A small VPS** (Hetzner/Netcup, ~€4/mo) with `systemd` or `tmux` keeping it alive.
- **Fly.io / Railway** free/'hobby' tier as a worker process.
- **No always-on host?** Use the GitHub Actions path in `deploy/github-actions.yml` — it
  generates drafts on a cron and pushes them to Telegram for manual posting (no X
  auto-post in that mode).

## Tuning

- Change cadence: edit `cadence.active` in `config/content_strategy.yaml`
  (`starter` → `growth` → `aggressive`), then send `/start` to reschedule.
- Change voice, pillars, or the offer: edit the same YAML. No code changes needed.
- The `docs/STRATEGY.md` file explains the reasoning behind each default.

## Running a second vertical (e.g. fitness)

One engine process per vertical — each with its own strategy YAML, its own Telegram bot,
and its own `data/<vertical>/` state:

1. Create the bot: @BotFather → new bot → put its token (and your chat id) in
   `.env.fitness`. Never reuse another vertical's token — two pollers on one token
   conflict.
2. Run: `GROWTH_CONFIG=config/fitness.yaml python -m src.run`.
3. On the server: `systemctl enable --now growth-engine@fitness` (the templated unit
   sets `GROWTH_CONFIG` from the instance name; the plain `growth-engine` unit stays
   the trades vertical).

`.env` holds shared secrets (Anthropic, X); `.env.<vertical>` overrides per vertical.
