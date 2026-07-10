# CLAUDE.md — growth-engine

Guidance for Claude Code (and any AI coding agent) working in the `growth-engine/`
project. This is a self-contained Python app; it is unrelated to the website in the
repo root. Keep changes inside `growth-engine/`.

## What this is

A personal-brand content pipeline: Claude drafts social posts → you approve them on
Telegram with one tap → approved posts auto-publish to X, while LinkedIn/Reddit come back
as paste-ready text. See `README.md` for the overview and `docs/STRATEGY.md` for the
product thinking.

## Read this first

- `docs/STRATEGY.md` — positioning, content pillars, cadence. The "why" behind defaults.
- `config/content_strategy.yaml` — **the single source of truth for behavior.** Offer,
  voice, pillars, platforms, cadence, and model all live here. Prefer editing this over
  changing code.
- `TASK.md` — the build/test checklist. Work through it top to bottom, verifying each
  process before moving to the next.

## Working principles

1. **Config over code.** If a change is about *what* the engine says or *how often*, it
   belongs in `content_strategy.yaml`, not in a `.py` file. Only touch code for *how* it
   works.
2. **One module, one job.** Keep the existing separation: `settings` (config/env),
   `store` (persistence), `ideas` (pillar rotation), `prompts` (prompt text), `generate`
   (Claude calls), `formatting` (display), `publish_x` (X API), `bot` (Telegram +
   scheduler), `push` (headless), `selftest` (isolated checks). Don't merge these.
3. **Test each layer in isolation before wiring.** Use `python -m src.selftest <layer>`.
   Follow `TASK.md` — don't jump ahead to the full run before the pieces pass.
4. **Never post during development.** Set `GROWTH_ENGINE_DRY_RUN=1` whenever you run the
   bot while testing. `selftest x` verifies auth without posting.
5. **Secrets stay in `.env`** (gitignored). Never hardcode keys, never commit `.env` or
   anything under `data/`. If you add a new secret, add it to `.env.example` too.
6. **Respect platform ToS.** X auto-posts via its API. LinkedIn and Reddit are
   *assisted only* (drafted, you paste) because their terms forbid automated posting and
   Reddit bans it aggressively. Do not add auto-posting for those.
7. **Surface errors, don't swallow them.** Generation/posting failures should be reported
   to the user (via Telegram or the selftest output), not silently dropped. The one
   allowed exception is keeping a scheduled loop alive after reporting a failure.

## Claude API conventions (this project)

- Model is `claude-opus-4-8`, read from config (`model.id`). Don't hardcode a model
  string in code.
- Use adaptive thinking (`thinking={"type": "adaptive"}`) and `output_config.effort`
  (config `model.effort`). Do **not** use `budget_tokens`, `temperature`, or `top_p` —
  they error on this model.
- Structured drafts use `output_config.format` with a JSON schema (see `generate.py`).
  Keep the schema static so it stays cached.
- The system prompt is stable and cache-controlled; per-request variation goes in the
  user message. Don't interpolate volatile values into the system prompt.

## Conventions

- Python 3.11+, standard library first, type hints, `from __future__ import annotations`.
- No new heavyweight dependencies without a reason — this runs on a tiny budget/host.
- Keep functions small and readable; match the style of the surrounding code.
- Run `python -m py_compile src/*.py` after edits; run the relevant `selftest` layer to
  verify behavior before declaring done.

## Common tasks

- **Change voice/offer/pillars/cadence** → edit `config/content_strategy.yaml`, then
  `python -m src.selftest config` and `python -m src.selftest generate` to sanity-check.
- **Add a platform** → extend `platforms` in the YAML, add a spec in `prompts.py`, and
  (if it has a write API you're allowed to use) a publisher module like `publish_x.py`.
- **Swap the LLM provider** → replace `generate.py` only; keep its function signatures
  (`generate_draft`, `regenerate_variant`) so callers don't change.
