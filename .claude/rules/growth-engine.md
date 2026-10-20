---
paths:
  - "growth-engine/**"
---

# growth-engine rules

- `config/content_strategy.yaml` is the single source of truth for offer, voice, pillars, platforms, cadence, model. **Config over code**: only touch `.py` files for *how* it works, never for *what* it says.
- One module, one job: `settings` / `store` / `ideas` / `prompts` / `generate` / `formatting` / `publish_x` / `publish_buffer` / `bot` / `push` / `buildlog` / `selftest`. Don't merge them.
- Test layers in isolation: `python -m src.selftest <config|generate|telegram|x|all>`. Follow `TASK.md` gates in order.
- **Never post during development** — set `GROWTH_ENGINE_DRY_RUN=1` when running the bot.
- Secrets live in `.env` (gitignored, as is `data/`). New secret → also add to `.env.example`.
- Delivery is per-platform, set in `config/content_strategy.yaml`: `auto` (direct API) / `buffer` (queued via Buffer) / `assisted` (paste) / `draft` (upload, finish in-app).
- X auto-posts direct. LinkedIn, Instagram and X also go through **Buffer** (`publish_buffer.py`, GraphQL at `api.buffer.com`, `mode: addToQueue`) — decided 2026-07-30. Buffer is an official LinkedIn publishing partner, so the old "LinkedIn ToS forbid automation" rule does NOT apply to posting through Buffer. Direct LinkedIn API posting is still forbidden.
- Buffer's per-channel queue owns the SCHEDULE. Cadence per platform is tuned in Buffer's UI, never by adding scheduling code here.
- **Reddit stays manual, permanently** — not a Buffer channel, and its culture punishes automation. Assisted-only, 1-2 high-effort posts/week.
- Surface errors to the user (Telegram or selftest output); the only swallow allowed is keeping a scheduled loop alive after reporting.
- Claude API: model + effort come from config (`model.id`, currently `claude-opus-4-8`); adaptive thinking + `output_config.effort`; no `budget_tokens`/`temperature`/`top_p`. Keep the JSON schema and system prompt static (prompt caching); per-request variation goes in the user message.
- Python 3.11+, stdlib first, type hints, no heavyweight deps. After edits: `python -m py_compile src/*.py` + the relevant selftest.
