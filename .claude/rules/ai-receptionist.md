---
paths:
  - "ai-receptionist/**"
---

# ai-receptionist rules

- `config/<business>.yaml` is the single source of truth (business, persona, services, hours, FAQ, booking rules, model); `BUSINESS_CONFIG` in `.env` selects it. Rebranding for a prospect = a new config file, zero code. The Klantkraan showcase is `config/klantkraan-demo.yaml` (Dutch).
- One module, one job: `settings` / `calendar_store` / `tools` / `receptionist` / `scaffold` / `notify` / `sessions` / `server` / `channels/` / `selftest`. Channels stay thin: adapters call `sessions.respond(...)`, never `receptionist.run_turn` directly.
- Test layers in isolation: `python -m app.selftest {config,calendar,agent,chat}` — `config` and `calendar` must stay offline-testable.
- `calendar_store.py` is the real-integration seam: swap the bodies of `availability()`/`book()` for a client's calendar API, never the signatures.
- The receptionist only offers slots `check_availability` returned — never invented times, prices, or advice. Enforced in the system prompt; keep it.
- The greeting always discloses it's a digital assistant (EU AI Act art. 50) — in every config file, every prospect demo.
- Claude API conventions (same as growth-engine): model + effort from config; adaptive thinking + `output_config.effort`; no `budget_tokens`/`temperature`/`top_p`; manual bounded tool loop.
- The receptionist's Telegram channel needs its OWN bot token — never reuse the growth-engine approval bot (two pollers on one token conflict).
