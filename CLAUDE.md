# Claude — operating rules for this repo

## Project
Three active parts, one business — Klantkraan (klantkraan.nl), AI receptionists for Dutch trades:
- `/klantkraan/` — the product + marketing site + sales docs (voice agent on LiveKit lives here; currently blocked on founder creds).
- `/ai-receptionist/` — the text-first receptionist (web chat + Telegram + WhatsApp, FastAPI + Claude tool use). The sellable demo and the starting point for client builds; text-first is the delivery path, voice is the upsell.
- `/growth-engine/` — the content pipeline that markets Klantkraan (Claude drafts → Telegram approval → X auto-post + LinkedIn/Instagram/X via Buffer queue, Reddit paste-ready). Self-contained Python app.

All other folders are unrelated legacy.

Per-app rules live in `.claude/rules/` (`growth-engine.md`, `ai-receptionist.md`) and load automatically when you touch files there.

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

## Forbidden
- Cold-call automation (founder constraint).
- HeyGen/Synthesia avatars (Dutch viewers reject).
- Disabling the EU AI Act art. 50 disclosure in the voice agent — ever.
- Cold email to eenmanszaak/VOF without opt-in. BV filter is non-negotiable.
- Automated replies/comments/DMs on any platform — drafting original posts is the automation ceiling.
- Posting anything live during development — growth-engine runs with `GROWTH_ENGINE_DRY_RUN=1`.

## Pre-launch verification
See `/klantkraan/docs/00-MASTER-PLAN.md § 5`. Items 1–10 require real-world action by the founder.
