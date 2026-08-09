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

- [ ] 0.1 Lead schema v1 in the buyer-lead path: intent
      (buyer/seller/renter/existing), areas, budget, bedrooms, timeline,
      financing, temperature, language, channel, property refs. New
      `register_buyer_lead` schema fields flow into `criteria` automatically
      (`app/tools.py` criteria comprehension) — standardize keys + compute
      temperature server-side in `listings_store.register_lead`.
      **Gate**: new `tests/test_listings.py` constructs + persists a lead per
      intent type; pytest green.
- [ ] 0.2 Temperature rules v1 — pure function lead → hot/warm/nurture
      (timeline <3mo + concrete criteria = hot; 3–12mo warm; else nurture;
      seller with valuation booked = hot).
      **Gate**: table-driven pytest, all four intents covered.
- [x] 0.3 Art. 50 disclosure EN/ES/DE.
      **Gate met**: `art50-disclosure.md` — DRS/Cool Global first_message
      pattern + ai_disclosure eval criterion.

⏸ CHECKPOINT A — update HANDOFF.md, commit, /clear.

## Week 1 — build (only what the before/after demo needs)

- [ ] 1.1 Branched qualification in the Solvista config: buyer / seller /
      renter / existing-client flows, per-type required fields (buyer: area,
      budget, bedrooms, timeline, financing; seller: property address +
      readback, condition, timeline; renter: area, monthly budget, move-in
      date). Lives in `persona.goals` prose + conditional prompt block if
      needed (onsite_block seam in `receptionist.build_system_prompt`).
      **Gate**: live chat transcript per flow shows the branch + all required
      fields asked; no field skipped.
- [ ] 1.2 Timeline mandatory in every flow; temperature computed on the lead
      and visible in the agent Telegram ping (`listings_store.py` ping text).
      **Gate**: selftest shows temperature on the ping for a hot and a
      nurture lead.
- [ ] 1.3 Missed-call text-back ported for this vertical: tenant resolution
      via `settings.resolve_whatsapp_slug` (seam exists, `voice_missed.py`
      doesn't call it yet) + locale-aware EN/ES text (currently hard-coded
      Dutch).
      **Gate**: simulated missed call (pytest, `test_voice_missed.py`
      pattern) produces the right-language text-back for a solvista number
      and still Dutch for trades.
- [ ] 1.4 Before/after demo asset: one page/script an owner sees — "9pm
      enquiry today: silence" vs live Solvista chat answering, qualifying,
      temperature ping. **Gate**: renders end-to-end with real demo data;
      founder can run it in one link/command.
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
