# CLAUDE.md — ai-receptionist

Guidance for AI coding agents working in `ai-receptionist/`. Self-contained Python demo;
unrelated to the website in the repo root. Keep changes inside this folder.

## What this is

A demo AI receptionist: a web chat widget → FastAPI → Claude (tool use) that answers a
business's customers and books appointments against a simulated calendar. It's a sales
demo and a build-in-public content source, and the starting point for real client builds.
See `README.md` and `docs/DEMO.md`.

## Read this first

- `config/business.yaml` — **the single source of truth.** Business, persona, services,
  hours, FAQ, booking rules, and model all live here. Rebranding = editing this file only.
- `TASK.md` — the gated build/test checklist. Verify each layer before the next.

## Working principles

1. **Config over code.** Anything about *which business* or *how it behaves* belongs in
   `business.yaml`, not in `.py`. Only touch code for *how it works*.
2. **One module, one job.** Keep the seams: `settings` (config), `calendar_store`
   (persistence + the real-integration seam), `tools` (definitions + handlers),
   `receptionist` (Claude loop + persona), `server` (FastAPI), `selftest` (checks).
3. **Test each layer in isolation.** `python -m app.selftest {config,calendar,agent,chat}`.
   `config` and `calendar` need no network — keep them that way so logic is testable offline.
4. **`calendar_store.py` is the integration seam.** For a real client, replace the bodies
   of `availability()` / `book()` with a real calendar API; do not change their signatures
   (tools and the agent depend on them).
5. **Secrets stay in `.env`** (gitignored). Never commit `.env` or `data/`. New secret →
   add it to `.env.example`.
6. **Surface errors.** Booking/agent failures should return a clear message to the
   customer, never a stack trace or silent drop.

## Claude API conventions (this project)

- Model is read from `business.yaml` (`model.id`, default `claude-opus-4-8`); don't
  hardcode a model string. `model.effort` (default `low`) keeps replies fast/cheap.
- Manual tool-use loop in `receptionist.py`: append the full `response.content` each turn,
  return every `tool_result` with its `tool_use_id`, handle `tool_use`/`pause_turn`/
  `end_turn`. Keep the loop bounded (the `for _ in range(8)` cap).
- Adaptive thinking (`thinking={"type": "adaptive"}`). No `budget_tokens`/`temperature`/
  `top_p` — they error on this model.
- The receptionist must only offer slots returned by `check_availability` — never invent
  times, prices, or clinical advice. This is enforced by the system prompt; keep it.

## Conventions

- Python 3.11+, stdlib first, type hints, `from __future__ import annotations`.
- Run `python -m py_compile app/*.py` and the relevant `selftest` layer after edits.
- Match the surrounding style; keep functions small.
