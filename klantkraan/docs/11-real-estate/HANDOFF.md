# Real Estate pilot — session handoff

> Rewrite this file at every ⏸ CHECKPOINT in `TASKS.md`, then commit.
> A fresh session starts here: read this, then `TASKS.md`, then `00-PLAN.md`.

## State (2026-08-09)

- **Rescoped to a narrow 30-day pilot** (founder decision, supersedes
  "full MVP before outreach"): one problem (after-hours/missed enquiries go
  cold), one result (every enquiry answered <1 min, qualified, hot leads
  flagged same-hour), one before/after demo. ~1 week build, then owner
  conversations. Voice, viewing booking, metrics CLI etc. all deferred.
- Done: 0.3 (art. 50 disclosure EN/ES/DE, `art50-disclosure.md`).
- Next task: **0.1 lead schema v1** (then 0.2 temperature rules).

## Engine map (from the 2026-08-09 exploration — trust these seams)

- Buyer lead path: `ai-receptionist/app/listings_store.py` —
  `register_lead()` at ~l.210, record built ~l.223-232, persisted as JSONL
  `data/listing-leads-<client>.jsonl`, Telegram ping composed ~l.243-263
  (per-agent chat_id → client notify → OWNER_TELEGRAM_CHAT_ID).
- New fields added to the `register_buyer_lead` tool schema
  (`app/tools.py` LISTINGS_TOOLS, ~l.123-159) flow into the persisted
  `criteria` dict automatically via the comprehension at tools.py ~l.195-199
  (exclusion tuple: customer_name/contact/references/notes).
- Tool gating: `tools.for_business()` — presence of a `listings:` config key.
- Qualification script today = prose in `persona.goals` in
  `config/clients/solvista-demo.yaml`; conditional prompt blocks use the
  onsite_block seam in `receptionist.build_system_prompt` (~l.55-66/86).
- No `tests/test_listings.py` exists; listings coverage only in
  `selftest.check_listings` (selftest.py ~l.717-783, uses
  `settings.use_slug("solvista-demo")` + temp DATA_DIR).
- pytest: `tests/conftest.py` fixtures `data_dir` (patches settings AND
  calendar_store DATA_DIR) + `clients_dir`; flat test modules, offline only.
- Missed-call funnel: `app/channels/voice_missed.py` — hard-coded Dutch, no
  tenant resolution; fix = call `settings.resolve_whatsapp_slug(params["To"])`
  like `whatsapp.py:66` does, + locale-aware text (config has `locale:`).
- No chat-side evals exist anywhere; ElevenLabs `evals.py` SCENARIOS/criteria
  shape is the pattern to mirror with a local judge.
- Analytics gap (matters for deferred metrics): `_outcome_from_tools`
  ignores `register_buyer_lead`.

## Decisions in force

Narrow pilot (above); Costa del Sol / Resales-Online; EN primary ES/DE
secondary; text-first, voice = upsell; no live transfer ever in this
vertical's voice future; art. 50 disclosure non-negotiable; config pack on
the shared engine, NOT a fork.

## Open / blocked (founder)

Pricing sign-off; LSSI-CE check before cold email; Resales test key.

## Gotchas

- Run python via `./.venv/bin/python` inside ai-receptionist; pytest = `-q`.
- Solvista config tracked via gitignore exception (fictional client).
- Narrow-pilot principle is a standing memory
  (feedback_narrow_pilot_principle_2026_08_09) — challenge build-creep.
