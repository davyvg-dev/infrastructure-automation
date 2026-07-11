# Claude — operating rules for this repo

## Project
Two active parts, one business — Klantkraan (klantkraan.nl), AI receptionists for Dutch trades:
- `/klantkraan/` — the product + marketing site + sales docs.
- `/growth-engine/` — the content pipeline that markets Klantkraan (Claude drafts → Telegram approval → X auto-post, LinkedIn/Reddit paste-ready). Self-contained Python app.

All other folders are unrelated legacy.

## Workflow — Ralph Higgums loop
- Small step → verify → next step. No multi-step leaps.
- Every code change: build, lint, run, eyeball the result, then commit.
- Every doc change: commit per subfolder, surface what changed in chat, wait for user confirmation before moving on.
- If a step fails: stop. Fix root cause. Do not bypass.
- Progress: `/klantkraan/TODO.md` for the product, `/growth-engine/TASK.md` for the pipeline. Tick boxes as you go.

## Docs source of truth — context7
- Before writing code that uses any external library/SDK (Astro, n8n, CM.com, Mollie, Cloudflare, Hetzner, Attio, Cal.com, ElevenLabs, Resend, Neon, Anthropic SDK, Tally, PandaDoc, SignWell, LiveKit, python-telegram-bot, tweepy, etc.), fetch current docs via the **context7 MCP**.
- If context7 is not connected, ask the user to enable it. Do not guess from training data.
- Cite the context7-fetched version in the PR / commit message when API surface matters.

## Branch
- All work on `claude/business-marketing-planning-FArXV`.
- Commit messages describe the *why*. Push with `-u origin <branch>`.

## Style
- Dutch in customer-facing artefacts (including social posts the growth engine drafts). English in code, internal docs, and CLAUDE.md.
- Never use the founder's name in customer-facing artefacts — "de oprichter" / "Klantkraan" instead.
- No emojis in code or commits unless explicitly requested.
- Lean files, no fluff. If a section can be removed without losing meaning, remove it.

## growth-engine rules
- `config/content_strategy.yaml` is the single source of truth for offer, voice, pillars, platforms, cadence, model. **Config over code**: only touch `.py` files for *how* it works, never for *what* it says.
- One module, one job: `settings` / `store` / `ideas` / `prompts` / `generate` / `formatting` / `publish_x` / `bot` / `push` / `selftest`. Don't merge them.
- Test layers in isolation: `python -m src.selftest <config|generate|telegram|x|all>`. Follow `TASK.md` gates in order.
- **Never post during development** — set `GROWTH_ENGINE_DRY_RUN=1` when running the bot.
- Secrets live in `.env` (gitignored, as is `data/`). New secret → also add to `.env.example`.
- X auto-posts via API; LinkedIn and Reddit are assisted-only (their ToS forbid automation). Never add auto-posting for those.
- Surface errors to the user (Telegram or selftest output); the only swallow allowed is keeping a scheduled loop alive after reporting.
- Claude API: model + effort come from config (`model.id`, currently `claude-opus-4-8`); adaptive thinking + `output_config.effort`; no `budget_tokens`/`temperature`/`top_p`. Keep the JSON schema and system prompt static (prompt caching); per-request variation goes in the user message.
- Python 3.11+, stdlib first, type hints, no heavyweight deps. After edits: `python -m py_compile src/*.py` + the relevant selftest.

## Forbidden
- Cold-call automation (founder constraint).
- HeyGen/Synthesia avatars (Dutch viewers reject).
- Disabling the EU AI Act art. 50 disclosure in the voice agent — ever.
- Cold email to eenmanszaak/VOF without opt-in. BV filter is non-negotiable.
- Automated replies/comments/DMs on any platform — drafting original posts is the automation ceiling.

## Pre-launch verification
See `/klantkraan/docs/00-MASTER-PLAN.md § 5`. Items 1–10 require real-world action by the founder.
