# 90-Day Roadmap

> Three months from $0 → ~€4–6k MRR with 8–14 active clients, all systems instrumented, brand and content engine compounding.

## Month 1 — Foundation (build the unfair advantage, no selling)

### Outcomes
- Brand registered, domain live, legal docs published.
- Astro marketing site live with two vertical landing pages.
- AI demo number live (+31 ...) and answers in Dutch.
- ROI calculator live.
- n8n + Synthflow + CM.com + Attio fully wired end-to-end on a personal test number.
- 2 pilot clients onboarded from network at 50% off month 1 (or free if needed for case study).
- First 4 LinkedIn posts + first 2 SEO cornerstones published in Dutch.

### Week-by-week

**Week 1 — Brand & legal**
- Verify + register `klantkraan.nl` + `klantkraan.com`. (Founder action — see `00-MASTER-PLAN.md` § 5.)
- File `handelsnaamwijziging` "Klantkraan" under T4 at KvK.
- Hiscox PI quote + bind (target ≤€80/mo).
- Sign Anthropic/Synthflow/CM.com/Attio/Hetzner/Cloudflare/Neon click-DPAs.
- Draft + publish MSA, DPA, SLA, Privacy, AI-disclosure pages on `klantkraan.nl/legal`.
- Open Moneybird, configure 21% + reverse-charge + ICP.
- Spin up Hetzner CX22 + Cloudflare + Neon. n8n + Caddy running.

**Week 2 — Product**
- Astro monorepo scaffolded (pnpm + Turborepo).
- Marketing site: `/`, `/loodgieters`, `/dakdekkers`, `/prijzen`, `/rekentool`, `/demo`, `/over`, `/legal/*`.
- Build the **public AI demo number**: Synthflow Dutch agent answering as "Demo Loodgieter Den Haag", scripted to handle 3–4 common scenarios. Number printed on every page.
- Build the **ROI calculator** (3 fields → "u verliest €X/jaar"). Astro form → Cloudflare Worker → Attio lead create.
- Wire missed-call + review automation in n8n using founder's personal phone as a "fake client" to dogfood.

**Week 3 — Pilots**
- Identify 5 warm prospects (network: friends-of-friends who are loodgieters/dakdekkers).
- Onboard pilot 1 (preferably loodgieter, BV). 2h 10m founder time.
- Capture a 4-min Loom of the first month projection.
- Begin LinkedIn content: 3 posts (problem-statement carousel, demo-screenrec clip, founder intro).

**Week 4 — Content + outbound prep**
- Onboard pilot 2 (preferably dakdekker for vertical breadth).
- Publish 2 SEO cornerstones in Dutch:
  - `crm-voor-installatiebedrijf-eerlijke-gids-2026`
  - `ai-telefoniste-voor-loodgieters-wat-werkt`
- Set up Smartlead + 9 inboxes + 3 .nl domains. Begin warm-up (3 weeks).
- Build BV-filtered list of 1,500 loodgieters + 500 dakdekkers via KvK API + Outscraper.

### Month 1 stop-gate
Cannot proceed to month 2 outbound until:
- (a) demo number is live and rated "natuurlijk" by 5 outside listeners
- (b) at least 1 pilot has gone live successfully (calls being recovered)
- (c) MSA + DPA on the site, and signed with the pilots
- (d) Mollie + Moneybird invoicing path tested end-to-end

## Month 2 — Proof + outbound ignition

### Outcomes
- First 2 anonymised case studies live on the site.
- Cold email Sequence A live to ~1,500 prospects via Smartlead.
- LinkedIn outreach (HeyReach) live.
- 3–5 new paying clients signed (Pro tier mix expected).
- MRR end of month: ~€3,000–4,000.

### Week-by-week

**Week 5**
- Cold email warm-up complete → first batch of 200 sends/day live with Sequence A.
- LinkedIn cadence active (300 connection requests/week via HeyReach).
- Anonymised case-study #1 published (Loom + 1-pager + LinkedIn carousel).
- Content cadence: 5 LinkedIn posts (founder personal, real name, no face), 1 blog, 1 newsletter.

**Week 6**
- Discovery calls from week-5 outbound (target: 8–12 booked, 6–10 shown).
- Close 1–2 clients at Pro tier.
- Publish 2 more SEO cornerstones.
- First YouTube long-form (10-min screen-rec: "Live demo van onze AI-receptionist").
- Run a Sequence A → Sequence B A/B in Smartlead.

**Week 7**
- Discovery calls + close 2–3 more.
- Publish case-study #2.
- Add Sequence C (value-first) to Smartlead.
- 3 Shorts repurposed from YouTube long-form.

**Week 8**
- Close 1–2 more (cumulative 4–6 new clients in M2).
- Outreach to first 5 accountant referral partners (Tellow/Moneybird ecosystem).
- Begin Google Business Profile setup for SEO.

### Month 2 stop-gate
- Smartlead deliverability >95% (open rate >35%, reply >5%).
- LinkedIn acceptance rate >25%.
- At least 1 new client signed without a personal introduction (proves the engine works).

## Month 3 — Compound

### Outcomes
- 8 paying clients minimum (bear case: 6; base: 8; bull: 11).
- MRR end of month: ~€4,000–6,500.
- Google Ads campaign live at €400/mo on Dutch high-intent.
- First accountant partnership signed (10% rev-share, 12 months).
- KPI dashboard automated and reviewed weekly.

### Week-by-week

**Week 9**
- Launch Google Ads campaign: `crm voor installatiebedrijf`, `ai telefoniste loodgieter`, `werkbonnen app monteur`, etc.
- 3rd case study published.
- Discovery calls from month-2 outbound continue closing.

**Week 10**
- Sign accountant referral partner #1. Provide them a referral landing page + tracking code.
- First weekly YouTube screen-rec series episode (will continue weekly).
- KPI dashboard automated: Attio + n8n → Notion page generated every Friday 15:45.

**Week 11**
- 2nd accountant or trade-association approach (Techniek Nederland membership outreach).
- Begin English-language repurposing of top-3 LinkedIn posts for UK seed audience.

**Week 12 (Day 89)**
- Run 90-day retrospective. Compare to base case (MRR €3,780 at month 3). Document learnings.
- Trigger criteria for hiring a VA (€600/mo) is at 12 active clients — set a Linear ticket if hit.

## Cumulative deliverables (end of M3)

| Asset | Count |
|---|---|
| Paying clients | 8 (base) |
| MRR | ~€4,500 (base) |
| Case studies published | 3 |
| LinkedIn posts | ~60 |
| YouTube videos | 3 (1 long-form + 2 weekly series) |
| Blog cornerstones | 8 |
| Newsletter issues | 12 |
| Cold emails sent | ~10,000 |
| LinkedIn connection requests | ~900 |
| Discovery calls done | ~25 |
| First-month-50%-off used | All 8 clients |
| Partnership signed | 1 (accountant) |
| Google Ads spend | €800 over M3 |

## What gets deferred to month 4+

- Hiring (VA): triggered at 12 active clients, likely month 4.
- UK launch: month 6+ once NL proven.
- TikTok/Instagram: never (low B2B intent for trades).
- Spain: deferred to month 12+.
- Klantkraan Multi-site tier: month 9+.

## How to know if we're off track

| Signal | Threshold | Action |
|---|---|---|
| Pilot client #1 churns in M1 | Any | Stop outbound. Diagnose root cause (product, delivery, expectation-setting). |
| Cold email reply <2% positive at week 6 | < 1.5% positive | Rotate hooks; consider switching to Sequence C-style value-first. |
| Discovery → close rate <15% in M2 | < 15% | Review script, the offerte template, and pricing presentation. |
| MRR end of M3 < €3,000 | < €3k | Slow content, accelerate outbound, get founder on every call personally. |
| Founder hours / week > 25h | > 25h | Productize harder. Onboarding must be ≤2h, not 3h. |

## Source

This roadmap is derived from the unit-economics model in `07-finance/unit-economics.md` (base case). It is updated at the end of each month based on actual conversion rates and learnings.
