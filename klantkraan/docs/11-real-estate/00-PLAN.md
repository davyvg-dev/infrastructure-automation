# Real Estate Receptionist — MVP plan

Side-project track of Klantkraan: AI receptionist (text + voice) for real-estate
agencies. Shares the `ai-receptionist` engine; separate at the sales/docs/demo
level. This folder is its home.

Decisions (founder, 2026-08-09):
- **Voice stack: ElevenLabs** — reuse DHZ/Cool Global agent patterns now; LiveKit
  migration stays a later margin play.
- **Market: Spain / Costa del Sol** — Resales-Online agencies. EN primary, ES/DE
  secondary. Dutch makelaars are a later vertical (no open listings API).
- **Sequence: full MVP before outreach** — everything below builds and verifies
  before the first pitch. Target: sellable package in ~4 weeks part-time.

Existing assets this builds on: `app/listings_store.py` (sim|resales seam,
search + RegisterLead + agent routing), Solvista Estates demo
(`demo.klantkraan.nl/?client=solvista-demo`), calendar provider with proven live
booking, missed-call funnel (trades), WhatsApp/Telegram takeover + alerts,
ElevenLabs eval harness + `calls.py`, DRS address-capture ladder. Research:
`klantkraan/research/real-estate-demo-research-2026-08.md`.

Field intel (Skool AI Automation Society thread, 2026-08-09): after-hours is the
whole product; voice transfer loops back on small phone systems — don't promise
it; address capture needs readback confirm; move-timeline question separates
call-now leads from nurture; missed-call recovery + lead temperature are the two
features that sell; measurable outcomes beat feature count.

---

## Phase 0 — Foundations (days 1–2)

- [ ] Lead schema v1 in the lead record: intent (buyer/seller/renter/existing),
      areas, budget, bedrooms, timeline, financing status, temperature
      (hot/warm/nurture), language, channel, property refs discussed.
- [ ] Temperature rules v1: timeline <3 months + concrete criteria = hot;
      3–12 months = warm; >12 months / browsing = nurture. Sellers with a
      valuation booked = hot by default.
- [ ] EU AI Act art. 50 disclosure text (EN/ES/DE) for the voice prompt —
      uninterruptible, same pattern as DRS. Non-negotiable.

## Phase 1 — Text MVP hardening (week 1)

- [ ] Branched qualification in the Solvista config: buyer / seller / renter /
      existing-client flows with per-type required fields (buyer: area, budget,
      bedrooms, timeline, financing; seller: property address + readback,
      condition, timeline; renter: area, monthly budget, move-in date).
- [ ] Timeline question mandatory in every flow; temperature computed and stored
      on the lead, shown in the agent Telegram ping.
- [ ] Viewing scheduling via the calendar provider with property ref attached.
      After-hours rule: propose slots + "confirmation follows", never hard-book.
- [ ] Metrics CLI (extend the existing CLI pattern, no dashboard): leads by
      type/temperature, viewings booked, response time, handoffs, per client.
- [ ] Selftest + pytest for new tool paths; text evals for the four flows.

## Phase 2 — Voice agent on ElevenLabs (week 2)

- [ ] Solvista voice agent cloned from the Cool Global mold: EN default,
      ES/DE switch, call-me-back demo first (no public number yet).
- [ ] Webhook tools on the existing FastAPI: search_listings,
      register_buyer_lead, viewing booking (DHZ RDW-lookup pattern).
- [ ] Voice hardening: readback confirm on names, phone numbers, addresses and
      urbanización names (adapt the DRS ladder — Spanish addresses have no
      postcode-first equivalent, so readback + spell-out is the tool); no price
      promises beyond listing data; after-hours boundaries in the prompt.
- [ ] Human handoff = callback promise + instant lead alert. No live transfer
      in MVP (transfer-loop trap).
- [ ] Eval set, target 5/5: hot buyer, seller valuation, renter, wrong-fit
      caller, after-hours viewing request, mangled-address recovery.

## Phase 3 — Missed-call recovery + follow-up (week 3)

- [ ] Port the trades missed-call funnel: missed call → instant WhatsApp/SMS
      text-back → text qualification → booking.
- [ ] Follow-up paths by temperature: hot → immediate agent ping; warm →
      next-morning digest; nurture → email captured for the agency's own list.
      No automated outbound beyond the missed-call text-back.
- [ ] Call summary per call into the lead record + daily digest to the agency.

## Phase 4 — Package + sales prep (week 4)

- [ ] Demo page on the site (`/en/demo/solvista` or similar): chat widget +
      call-me-back voice, EN/ES.
- [ ] Sales pack (EN/ES): one-pager, discovery-call script including the
      Resales API-key ask (dashboard → Properties → Feed Out → API Keys;
      keys are IP-locked to our server), metrics story from the CLI.
- [ ] Prospect list: Costa del Sol agencies running Resales-Online.
- [ ] Pricing proposal for founder sign-off (voice tier basis; agency call
      values are higher than trades — do not improvise on calls).

## Founder items (blocking, in order of need)

1. ElevenLabs plan headroom for a second demo agent (Phase 2).
2. Resales WebAPI test key — the resales provider is written but untested until
   a real agency key exists; ask in the first discovery call, or request a
   sandbox key from Resales-Online support (Phase 2/4).
3. Spanish outreach legality check (LSSI-CE opt-in rules ≈ Dutch regime;
   phone/manual outreach is the safe default) before any cold email (Phase 4).
4. Pricing sign-off (Phase 4).
5. Later: inbound Spanish number strategy (Twilio ES regulatory bundle) — only
   needed at first client go-live, not for the MVP.

## Risks

- Resales provider untested against the live API until a real key exists —
  keep the sim provider demo-ready as fallback.
- ElevenLabs margin pressure at volume — accepted for speed; LiveKit-EU
  migration remains the margin fix, unchanged from the trades track.
- After-hours viewing bookings nobody honours — mitigated by propose-only rule;
  verify in evals, not just prompt text.
