# Real Estate narrow pilot — task ledger

Working ledger for `00-PLAN.md` (narrow 30-day pilot). Ralph Wiggums loop: one
task → verify gate → tick → commit → next. Never skip a gate. If a gate fails,
stop and fix root cause before the next box.

**Context-clear protocol**: at every `⏸ CHECKPOINT`, update `HANDOFF.md`,
commit, tell the user to `/clear`. A fresh session reads `HANDOFF.md` → this
file → `00-PLAN.md` and continues from the first unticked box.

Subagents: fan out independent tasks; serialize commits and same-file work in
the main loop.

---

## Phase 0 — Foundations

- [x] 0.1 Lead schema v1 in the buyer-lead path.
      **Gate met**: `register_buyer_lead` schema now carries intent/timeline/
      financing/property_address/valuation_booked; `register_lead` stamps
      resolved intent + temperature on the record; `tests/test_listings.py`
      persists a lead per intent type. 226 tests green.
- [x] 0.2 Temperature rules v1 — `app/lead_score.py`, pure functions.
      **Gate met**: table-driven pytest (17 cases, all four intents,
      malformed input degrades to nurture).
- [x] 0.3 Art. 50 disclosure EN/ES/DE.
      **Gate met**: `art50-disclosure.md` — DRS/Cool Global first_message
      pattern + ai_disclosure eval criterion.

⏸ CHECKPOINT A — update HANDOFF.md, commit, /clear.

## Week 1 — build (only what the before/after demo needs)

- [x] 1.1 Branched qualification in the Solvista config: buyer / seller /
      renter / existing-client flows, per-type required fields (buyer: area,
      budget, bedrooms, timeline, financing; seller: property address +
      readback, condition, timeline; renter: area, monthly budget, move-in
      date). Lives in `persona.goals` prose + conditional prompt block if
      needed (onsite_block seam in `receptionist.build_system_prompt`).
      **Gate met**: four live scripted chats (buyer/seller/renter/existing)
      each showed the branch, asked every required field, and called
      register_buyer_lead with structured fields — buyer: timeline=0-3 +
      financing=cash; seller: property_address (read back) + timeline=3-12 +
      valuation_booked=true; renter: timeline=0-3 + references; existing: no
      re-qualifying, clear note for the agent. Prompt prose only, no
      onsite_block needed; 226 tests stayed green.
- [x] 1.2 Timeline mandatory in every flow; temperature computed on the lead
      and visible in the agent Telegram ping (`listings_store.py` ping text).
      **Gate met**: ping now opens "[Business] 🔥 HOT buyer lead for Maria:"
      (🏠 for warm/nurture); selftest listings registers a hot and a nurture
      lead and asserts both tags; pytest asserts the tag per intent.
      Timeline-mandatory shipped with 1.1's prompt (all four live flows
      asked it). 226 tests green, ruff clean.
- [x] 1.3 Missed-call text-back ported for this vertical: tenant resolution
      via `settings.resolve_whatsapp_slug` (seam exists, `voice_missed.py`
      doesn't call it yet) + locale-aware EN/ES text (currently hard-coded
      Dutch).
      **Gate met**: `handle()` routes on the called number (same
      `whatsapp.number` seam as the WhatsApp channel) and the follow-up
      thread re-activates the tenant (contextvars don't cross threads);
      spoken TwiML + WhatsApp text now nl/en/es by config `locale:`. Pytest:
      solvista number → en-GB/es-ES text-back, unknown number → still Dutch.
      229 tests green, ruff clean.
- [x] 1.4 Before/after demo asset: one page/script an owner sees — "9pm
      enquiry today: silence" vs live Solvista chat answering, qualifying,
      temperature ping. **Gate met**: klantkraan.nl/demo/solvista LIVE
      (noindex, share by link) — timeline of the unanswered 21:04 enquiry
      vs the real transcript + real 🔥 HOT ping from the 1.1 gate run,
      then the live chat CTA + per-flow try-this list. Built, deployed
      (--branch=production), verified on prod by screenshot.
- [ ] 1.5 Selftest extended + full pytest green + text evals for the four
      flows (new — no chat evals exist yet; judge needed, mirror the
      ElevenLabs SCENARIOS/criteria shape).
      **Gate**: `app.selftest all` + pytest + evals all green.

⏸ CHECKPOINT B — update HANDOFF.md, commit, /clear.

## Weeks 2–4 — owner conversations

- [ ] 2.1 Prospect list: Costa del Sol agencies on Resales-Online, source
      per row; phone/manual only until LSSI-CE check clears email.
      **Gate**: list reviewed by founder.
- [ ] 2.2 Discovery script (EN/ES) around the before/after demo, incl. the
      Resales API-key ask. **Gate**: founder dry-run.
- [ ] 2.3 Pricing proposal. **Gate**: founder sign-off — never improvise.
- [ ] 2.4 Conversation loop: prospects tracked in the pipeline CLI, notes
      per call, demo sent same-day. **Gate**: first 10 conversations logged.

⏸ CHECKPOINT C — update HANDOFF.md, commit, /clear.

## Deferred until owners ask / first client

Full voice agent (Cool Global mold, DRS readback ladder, no live transfer,
disclosure per `art50-disclosure.md`), viewing scheduling (propose-only rule;
NB propose-only mode doesn't exist in `calendar_store` yet), metrics CLI
(NB `analytics._outcome_from_tools` ignores `register_buyer_lead` — extend
`_OUTCOME_RANK` or read the JSONL), follow-up paths by temperature, daily
digests, HubSpot push, Idealista API, Spanish inbound number.

## Founder items (blocking)

1. Pricing sign-off before any pitch (blocks 2.3).
2. LSSI-CE outreach legality check (blocks any cold email).
3. Resales WebAPI test key (sim provider is the demo fallback).
4. (With voice, deferred) ElevenLabs plan headroom.
