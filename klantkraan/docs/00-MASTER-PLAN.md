# Klantkraan — Master Plan

> **One-line summary.** Productized "AI receptionist + missed-call recovery + Google review automation" for Dutch loodgieters and dakdekkers, priced €299 / €599 / €999 per month, no setup fee, monthly cancel. Target €10k MRR by month 6, €20k+ by month 9, scaling toward €30k+ ARR by end of year 1.

## 1. Why this works (one paragraph)

Dutch trade owner-operators miss 27–40% of inbound calls. Each missed plumbing emergency is worth €450–600. There is no Dutch competitor that bundles AI receptionist + missed-call SMS + Google review automation for one specific trade vertical with tariff-aware Dutch scripts. UK incumbent Invox (£99) is vertical-locked but lacks the bundle. Dutch incumbents (Voicelabs, Cowcierge, Agentfabriek) sell horizontal voice tools without verticalisation. EU AI Act 2026 raises trust barriers for foreign providers — being NL-hosted and Dutch-native is a moat. Unit economics are exceptional: ~95% gross margin, sub-1-month payback.

## 2. The decisions, locked

| Layer | Decision |
|---|---|
| Brand | **Klantkraan** (Dutch metaphor: "customer tap"). Held under T4 Software Consulting handelsnaam. |
| Vertical | **Loodgieters + dakdekkers** in parallel (shared product, separate landing pages). |
| ICP | Owner-operators of 2–8 staff trade businesses, **registered as BV** for cold outbound (eenmanszaak/VOF are opt-in only under Dutch law). |
| Geography | NL primary (Randstad first). UK from month 6+. Spain deferred to month 12+ pending NL/UK proof. |
| Offer | Three tiers: Lite €299 (SMS+reviews) / Pro €599 (+AI receptionist) / Max €999 (+integrations+priority). No setup. Monthly cancel. First month 50% off. Annual or 6-mo commit: 15% off. |
| Sales | 14-day cycle, 20-min Zoom discovery, 1-page offerte PDF, SignWell e-sign, Mollie SEPA recurring. |
| Delivery | 2h 10m founder time per onboarding, conditional call forwarding (not porting), 30-day go-live. |
| Tech | pnpm + Turborepo monorepo / Astro on Cloudflare Pages / n8n self-hosted on Hetzner CX22 (€3.79/mo) / Attio CRM free / CM.com SMS / Synthflow Dutch voice / Mollie billing / Moneybird invoicing. |
| Acquisition mix (M1–3) | Cold email to BV-filtered list (KvK API + Outscraper, ~5,300/mo via Smartlead) + LinkedIn DM via HeyReach + founder LinkedIn personal content + Dutch SEO + partnerships (accountants, Techniek Nederland). |
| Compliance | EU AI Act Art. 50 mandatory disclosure at call start, AVG controller/processor split via DPA, Art. 30 RoPA, DPIA per service tier, Hiscox PI+AVB+cyber ~€150/mo. |

## 3. The numbers (base case, see `07-finance/`)

| Month | New | Active end | MRR (€) |
|---|---|---|---|
| 1 | 2 (pilots, half ARPU) | 2 | 540 |
| 3 | 3 | 8 | 3,780 |
| 6 | 5 | 22 | **10,800** |
| 9 | 7 | 39 | **19,980** |
| 12 | 8 | 60 | **31,320** |

- Gross margin: ~95% blended.
- Payback period: <1 month at €200 cash CAC.
- Bear case (20% lower ARPU, +30% churn, +50% CAC): still €13k MRR by month 12. Even pessimism hits the €10k goal.
- Required personal cash injection: **€5–6k** to bridge months 1–4 (founder draws nothing those months).

## 4. The 90-day sequence

| Month | Theme | Concrete outputs |
|---|---|---|
| **M1 — Foundation** | Don't sell; build the unfair advantage | Domain registered, KvK handelsnaam filed, Astro site live with 2 landing pages (`/loodgieters`, `/dakdekkers`), public AI demo number (+31 ...) live, ROI calculator live, MSA+DPA+SLA+AI-disclosure pages live, n8n + Synthflow agent + missed-call + review flows working end-to-end on a personal test number, 2 free pilot clients onboarded from network, first 4 LinkedIn posts + first 2 SEO cornerstones in Dutch published. |
| **M2 — Proof + outbound on** | Turn the pilots into case studies, ignite outbound | First 2 anonymised case studies published, Smartlead inbox warmup complete, cold email Sequence A live to ~1,500 BV-filtered loodgieters/dakdekkers, LinkedIn cadence active, 3–5 new clients signed at full price, content engine producing 5 LI + 1 blog + 1 newsletter per week. |
| **M3 — Compound** | Hit step-change on lead flow | 8 clients live, Google Ads test campaign live at €400/mo on high-intent keywords, first accountant referral partner signed, second SEO cornerstone wave (8 articles), first weekly YouTube screen-rec series, KPI dashboard automated. Trigger: at 12 active clients, document the first hire plan for VA (€600/mo). |

## 5. Pre-launch verification — only you can do these

These items are **not researched** because they require real identity, payment, or a click I can't simulate. Do them before we go to Phase 1 (scaffolding code).

| # | Action | Where | Why |
|---|---|---|---|
| 1 | Verify `klantkraan.nl` available | `https://www.sidn.nl/en/whois` | Domain blocks all branding work |
| 2 | Verify `klantkraan.com` available | `https://lookup.icann.org/en/lookup` | Defensive registration |
| 3 | KvK handelsnaam search for "Klantkraan" | `https://www.kvk.nl/zoeken/` | NL trade-name uniqueness |
| 4 | BOIP trademark search "Klantkraan" class 35 + 42 | `https://www.boip.int/en/trademarks-register` | Trademark conflicts |
| 5 | Register `.nl` + `.com` if all clear | TransIP or Namecheap | ~€15–20/yr total |
| 6 | File `handelsnaamwijziging` for "Klantkraan" under T4 | KvK | Legal entity ready |
| 7 | Get Hiscox PI quote for ICT consultant (€500k cover) | `https://www.hiscox.nl/beroepsaansprakelijkheidsverzekering-ICT` | Confirm ~€40–80/mo budget |
| 8 | Sign up Synthflow trial + test 30 min of Dutch voice quality | `https://synthflow.ai` | Validate the core product promise before selling it |
| 9 | Sign up CM.com + reserve 1 Dutch landline | `https://www.cm.com/` | Demo number for public AI |
| 10 | Open Moneybird trial, configure 21% + reverse charge | `https://moneybird.com/` | Ready to invoice pilot #1 |

If any of items 1–4 come back blocked, fall back to **Vakflow** (priority 2) or **Afspraakmotor** (priority 3) and repeat the checks.

## 6. The known risks (full register in `10-ops/risk-register.md`)

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Synthflow Dutch voice quality insufficient | M | High | Verify in trial before pricing. Fallback: VAPI + ElevenLabs v3 Dutch. |
| Cold-email deliverability collapse (Google/MS suspension) | M | High | 9-inbox rotation, 25/day cap, warm-up, DMARC p=reject. Channel diversification onto LinkedIn + content. |
| AP / GDPR enforcement on outbound to eenmanszaak | M | High | BV-only filter on cold list. LIA + Art. 30 RoPA documented from day one. |
| Founder delivery wall at ~30 active clients | H | Med | Productized onboarding to <2h. VA hire at month 6 (not 8). |
| One critical sub-processor outage (Synthflow, CM.com) | L | Med | 99% SLA only (not 99.9%); telephony adapter pattern lets us swap providers. |
| Pricing too high vs. NL voice-only tools (€149) | M | Med | Tier structure anchors at €999, real money at €599. Killer demo destroys the comparison. |
| EU AI Act non-compliance (missing Art. 50 disclosure) | L | High (€15M fine ceiling) | Disclosure baked into Synthflow prompt; MSA makes it non-waivable. |

## 7. What's missing / open questions for the founder

1. **Visual identity** — logo, colour palette, typography. Brief is in `09-brand/visual-identity-brief.md`. Recommend Fiverr/v0 design at €100–300 once domain locked.
2. **Founder cash runway** — confirm €5–6k bridge is available. If not, slow onboarding pace in months 1–3.
3. **Personal LinkedIn audit** — `linkedin.com/in/<you>` becomes a sales surface. Update headline + about section to match Klantkraan positioning before first outbound.
4. **Trade-association outreach plan** — Techniek Nederland, Bouwend Nederland, OnderhoudNL membership / sponsorship cost not yet researched; deferred until month 3.
5. **Initial 5 pilot prospects** — who in your network is a loodgieter or dakdekker? Two warm intros short-circuit month 1.

## 8. How to use this repo

1. Read this file end-to-end. Bookmark.
2. Read `01-strategy/icp.md` and `01-strategy/offer-and-pricing.md` next — these are the most-changed-when-you-learn docs.
3. When a customer-facing decision needs to be made, write the rationale into the relevant doc *before* shipping. The repo is a write-ahead log of strategy.
4. Weekly KPI review (Friday 16:00) is documented in `10-ops/weekly-kpi-review.md`.

## 9. References to deeper docs

- Strategy: [`01-strategy/`](01-strategy/)
- Sales scripts and benchmarks: [`02-sales/`](02-sales/)
- Onboarding playbook: [`03-delivery/`](03-delivery/)
- Legal templates and compliance: [`04-legal/`](04-legal/)
- Content + SEO calendar: [`05-content/`](05-content/)
- Outbound infrastructure: [`06-outbound/`](06-outbound/)
- Unit economics: [`07-finance/`](07-finance/)
- Tech stack and infra: [`08-tech/`](08-tech/)
- Brand and naming: [`09-brand/`](09-brand/)
- Operations: [`10-ops/`](10-ops/)
