# Real Estate MVP — task ledger

Working ledger for the build in `00-PLAN.md`. Ralph Wiggums loop: one task →
verify gate → tick → commit → next. Never skip a gate. If a gate fails, stop
and fix root cause before touching the next box.

**Context-clear protocol**: at every `⏸ CHECKPOINT`, update `HANDOFF.md` with
current state, commit, tell the user to `/clear`. The next session reads
`HANDOFF.md` + this file and continues from the first unticked box.

Subagents: fan out independent tasks (research, isolated modules, eval
authoring) to parallel subagents; serialize commits and anything touching the
same files in the main loop.

---

## Phase 0 — Foundations

- [ ] 0.1 Lead schema v1 — dataclass/dict shape in the receptionist app:
      intent (buyer/seller/renter/existing), areas, budget, bedrooms, timeline,
      financing, temperature, language, channel, property refs discussed.
      **Gate**: unit test constructs + serializes a lead of each intent type.
- [ ] 0.2 Temperature rules v1 — pure function lead → hot/warm/nurture
      (timeline <3mo + concrete criteria = hot; 3–12mo = warm; else nurture;
      seller with valuation booked = hot).
      **Gate**: pytest table-driven cases, all four intents covered.
- [x] 0.3 Art. 50 disclosure text EN/ES/DE checked into the vertical docs +
      wired location identified for the voice prompt (Phase 2 consumes it).
      **Gate met**: `art50-disclosure.md` — EN/ES/DE, DRS/Cool Global
      first_message pattern + ai_disclosure eval criterion.

⏸ CHECKPOINT A — update HANDOFF.md, commit, /clear.

## Phase 1 — Text MVP hardening

- [ ] 1.1 Branched qualification in the Solvista config: buyer / seller /
      renter / existing-client flows, per-type required fields (buyer: area,
      budget, bedrooms, timeline, financing; seller: address + readback,
      condition, timeline; renter: area, monthly budget, move-in date).
      **Gate**: live chat transcript per flow shows the branch + required
      fields asked; no field skipped.
- [ ] 1.2 Timeline mandatory everywhere; temperature computed on the lead and
      visible in the agent Telegram ping.
      **Gate**: selftest shows temperature on the ping payload for a hot and
      a nurture lead.
- [ ] 1.3 Viewing scheduling via calendar provider with property ref attached;
      after-hours = propose slots + "confirmation follows", never hard-book.
      **Gate**: eval proves after-hours request gets propose-only response;
      in-hours books with the ref on the event.
- [ ] 1.4 Metrics CLI (existing CLI pattern, no dashboard): leads by
      type/temperature, viewings, response time, handoffs, per client.
      **Gate**: CLI runs against real demo data and prints correct counts.
- [ ] 1.5 Selftest + pytest for all new tool paths; text evals for the four
      flows green.
      **Gate**: full pytest suite + `app.selftest` green, evals pass.

⏸ CHECKPOINT B — update HANDOFF.md, commit, /clear.

## Phase 2 — Voice agent (ElevenLabs)

- [ ] 2.1 Solvista voice agent cloned from Cool Global mold (EN default,
      ES/DE switch, call-me-back only). **Founder gate: plan headroom.**
      **Gate**: agent exists, disclosure uninterruptible, config vars baked.
- [ ] 2.2 Webhook tools on FastAPI: search_listings, register_buyer_lead,
      viewing booking (DHZ pattern).
      **Gate**: WS-verified tool round-trips from the ElevenLabs side.
- [ ] 2.3 Voice hardening: readback confirms (names, phones, urbanización
      names — adapt DRS ladder, no postcode-first in ES), no price promises,
      after-hours boundaries.
      **Gate**: real test call transcript reviewed against each rule.
- [ ] 2.4 Handoff = callback promise + instant lead alert; no live transfer.
      **Gate**: eval case proves no transfer is ever offered.
- [ ] 2.5 Eval set 5/5: hot buyer, seller valuation, renter, wrong-fit,
      after-hours viewing, mangled-address recovery.
      **Gate**: `evals.py run all` style suite = 5/5.

⏸ CHECKPOINT C — update HANDOFF.md, commit, /clear.

## Phase 3 — Missed-call recovery + follow-up

- [ ] 3.1 Port trades missed-call funnel (missed call → WhatsApp/SMS
      text-back → text qualification → booking) for the vertical.
      **Gate**: simulated missed call produces the text-back + a qualified
      lead end-to-end.
- [ ] 3.2 Follow-up by temperature: hot → instant ping; warm → next-morning
      digest; nurture → email captured. No other automated outbound.
      **Gate**: selftest covers all three paths.
- [ ] 3.3 Call summary into lead record + daily digest to agency.
      **Gate**: digest renders from a day of demo data.

⏸ CHECKPOINT D — update HANDOFF.md, commit, /clear.

## Phase 4 — Package + sales prep

- [ ] 4.1 Demo page on the site (chat + call-me-back, EN/ES).
      **Gate**: deployed, verified via deploy alias, links work.
- [ ] 4.2 Sales pack EN/ES: one-pager, discovery script incl. Resales API-key
      ask, metrics story. **Gate**: founder review.
- [ ] 4.3 Prospect list: Costa del Sol agencies on Resales-Online.
      **Gate**: list with source per row; BV-equivalent/opt-in rules noted.
- [ ] 4.4 Pricing proposal. **Gate**: founder sign-off — do not improvise.

## Founder items (blocking)

1. ElevenLabs plan headroom (blocks 2.1).
2. Resales WebAPI test key (blocks live resales provider test; sim is the
   demo fallback).
3. Spanish outreach legality check (blocks any cold email in Phase 4).
4. Pricing sign-off (blocks 4.4).
