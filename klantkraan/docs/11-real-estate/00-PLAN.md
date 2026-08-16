# Real Estate Receptionist — 30-day narrow pilot

Side-project track of Klantkraan: AI receptionist for real-estate agencies.
Shares the `ai-receptionist` engine; separate at the sales/docs/demo level.

Decisions (founder):

- 2026-08-09: ElevenLabs for voice when voice comes (LiveKit stays the later
  margin play). Market: Spain / Costa del Sol, Resales-Online agencies. EN
  primary, ES/DE secondary.
- 2026-08-09 (supersedes "full MVP before outreach"): **painfully narrow
  30-day pilot** — one problem, one result, one before/after demo; the rest
  of the time talking to owners who already feel that exact pain.

## The pilot

- **One problem:** after-hours and missed enquiries on listings go cold before
  an agent ever sees them. (Field intel, AIS Skool 2026-08-09: after-hours is
  the whole product; missed-call recovery + lead temperature are the two
  features that sell; measurable outcomes beat feature count.)
- **One result:** every enquiry answered within a minute, qualified, and hot
  leads flagged to an agent the same hour.
- **One demo:** before/after, side by side. Before: enquire on a listing at
  9pm, silence until morning. After: instant answer, branched qualification,
  temperature-scored lead in the agent's pocket. The live Solvista demo
  (`demo.klantkraan.nl/?client=solvista-demo`) is most of the "after" side.

## Week 1 — build (only what the demo needs)

Foundations: lead schema v1, temperature rules v1 (timeline <3mo + concrete
criteria = hot; 3–12mo = warm; else nurture; seller with valuation booked =
hot), art. 50 disclosure EN/ES/DE (done — `art50-disclosure.md`).

Core: branched buyer/seller/renter/existing qualification in the Solvista
config with per-type required fields; timeline mandatory; temperature computed
and shown in the agent ping. Missed-call text-back ported from trades (missed
call → instant text → qualification). Before/after demo asset. Selftest,
pytest, text evals for the four flows.

## Weeks 2–4 — owner conversations

Prospect list of Costa del Sol agencies on Resales-Online; discovery script
(incl. the Resales API-key ask: dashboard → Properties → Feed Out → API Keys,
keys IP-locked to our server); before/after demo as the centerpiece; pricing
proposal for founder sign-off. Phone/manual outreach only until the LSSI-CE
opt-in check clears cold email.

## Deferred until owners ask / first client

Full voice agent (ElevenLabs, Cool Global mold + DRS readback ladder + no live
transfer), viewing scheduling (propose-only after hours), metrics CLI,
follow-up paths by temperature, daily digests, HubSpot push, Idealista API,
Spanish inbound number (Twilio ES bundle). Design constraints for these are
locked in git history (a65376f) and `art50-disclosure.md`.

## Founder items (blocking)

1. Pricing sign-off before any pitch (do not improvise on calls).
2. Spanish outreach legality check (LSSI-CE) before any cold email;
   phone/manual is the safe default.
3. Resales WebAPI test key — provider written but untested; ask in the first
   discovery call. Sim provider stays the demo fallback.
4. (Deferred with voice) ElevenLabs plan headroom for a second agent.

## Risks

- Resales provider untested against the live API until a real key exists —
  keep the sim provider demo-ready as fallback.
- Narrow scope means owners may ask for voice on the first call — answer:
  voice is the upsell, text pilot proves the result first (same play as
  trades).
