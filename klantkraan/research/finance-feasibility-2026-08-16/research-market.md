# Klantkraan — market size & competitive pricing stress test

Research date: **2026-08-16**. All CBS figures pulled live from the StatLine OData API on this date.
Competitor prices fetched live from vendor pages on this date unless marked otherwise.

> **Method note / limitation.** This session's WebSearch budget (200 calls) was exhausted partway
> through. CBS/StatLine work is unaffected (direct OData API + curl). Competitor and incumbent
> coverage is therefore anchored on (a) live WebFetch of known vendor URLs, (b) the repo's own
> prior research files, re-verified where a URL was known. Discovery of *unknown* new entrants is
> the weakest part of this report and is flagged as such in §3.

---

## 1. Addressable market, computed from CBS

### 1.1 Business counts — DIRECTLY SOURCED

Source: CBS StatLine **81589NED** "Bedrijven; bedrijfstak", reference **2026 Q3** (voorlopig).
https://opendata.cbs.nl/statline/#/CBS/nl/dataset/81589NED/table
API: `https://opendata.cbs.nl/ODataApi/odata/81589NED/TypedDataSet?$filter=Perioden eq '2026KW03'`

All CBS counts are rounded to multiples of 5. **There is no "0 werkzame personen" class** — the
smallest class is 1 wp, and the working owner counts as 1. So "zzp" ≈ the 1-wp column, and
"has at least 1 employee" ≈ **≥2 werkzame personen**.

| SBI | Description | Totaal | 1 wp | 2 wp | 3-5 | 5-10 | 10-20 | 20-50 | ≥2 wp |
|---|---|---|---|---|---|---|---|---|---|
| F | Bouwnijverheid | 269,845 | 233,700 | 18,595 | 6,990 | 5,045 | 2,870 | 1,695 | 36,145 |
| 41 | Algemene bouw | 110,050 | 97,895 | 6,885 | 2,175 | 1,445 | 835 | 495 | 12,155 |
| 42 | Grond-/water-/wegenbouw | 16,530 | 14,195 | 1,065 | 475 | 330 | 165 | 155 | 2,335 |
| **43** | **Gespecialiseerde bouw** | **143,265** | 121,610 | 10,640 | 4,340 | 3,270 | 1,865 | 1,040 | **21,655** |
| 431 | Sloop + grondwerk | 10,565 | 8,900 | 745 | 315 | 245 | 175 | 130 | 1,665 |
| 432 | Bouwinstallatie | 42,410 | 34,715 | 3,200 | 1,530 | 1,295 | 870 | 500 | 7,695 |
| **4321** | **Elektrotechnische installatie** | **20,660** | 17,505 | 1,300 | 645 | 530 | 360 | 185 | **3,155** |
| **4322** | **Loodgieters + installatiebedrijven** | **18,515** | 14,545 | 1,660 | 805 | 665 | 440 | 270 | **3,970** |
| 43221 | Loodgieters- en fittersbedrijven | 10,855 | 8,625 | 950 | 435 | 385 | 260 | 135 | 2,230 |
| 43222 | Verwarmingsinstallatie | 7,665 | 5,920 | 715 | 365 | 280 | 180 | 130 | 1,745 |
| 4329 | Overige bouwinstallatie | 3,235 | 2,670 | 235 | 85 | 100 | 70 | 45 | 565 |
| 433 | Afwerkingsbedrijven (schilders etc.) | 64,120 | 55,395 | 4,940 | 1,830 | 1,155 | 495 | 245 | 8,725 |
| 439 | Overige gespecialiseerde bouw | 26,170 | 22,605 | 1,750 | 665 | 575 | 325 | 170 | 3,565 |
| **4391** | **Dakbouwbedrijven** | **6,370** | 5,245 | 525 | 245 | 200 | 90 | 45 | **1,125** |
| **813** | **Hoveniersbedrijven** | **16,490** | 12,785 | 1,595 | 935 | 700 | 290 | 125 | **3,705** |

**The dominant fact: 85% of specialized-construction businesses are one-person firms.**
SBI 43 = 121,610 of 143,265 at 1 wp. Hoveniers = 12,785 of 16,490. The headline "143k trade
businesses" number is ~85% out of scope before any other filter is applied.

### 1.2 Legal form — DIRECTLY SOURCED

Source: CBS StatLine **81588NED** "Bedrijven; bedrijfsgrootte en rechtsvorm", **2026 Q3**.
https://opendata.cbs.nl/statline/#/CBS/nl/dataset/81588NED/table
Caps out at **3-digit SBI** — CBS publishes no 4321/4322 legal-form split anywhere.

| SBI | Totaal | Eenmanszaak | VOF | Maatschap | BV | Totaal rechtspers. |
|---|---|---|---|---|---|---|
| F Bouwnijverheid | 269,845 | 214,380 (79.4%) | 15,760 (5.8%) | 130 | 38,775 (14.4%) | 39,135 |
| 41 | 110,050 | 86,620 | 6,010 | 80 | 16,845 | 17,035 |
| 42 | 16,530 | 13,125 | 920 | 5 | 2,430 | 2,465 |
| **43** | **143,265** | **114,640 (80.0%)** | **8,830 (6.2%)** | 45 | **19,495 (13.6%)** | 19,640 |
| 431 | 10,565 | 8,390 | 610 | 10 | 1,540 | 1,545 |
| **432 Bouwinstallatie** | 42,410 | 31,125 (73.4%) | 2,525 | 10 | **8,645 (20.4%)** | 8,720 |
| 433 Afwerking | 64,120 | 54,000 (84.2%) | 4,235 | 15 | 5,795 (9.0%) | 5,825 |
| 439 | 26,170 | 21,125 | 1,465 | 10 | 3,515 | 3,550 |
| **813 Hoveniers** | **16,490** | **13,385 (81.2%)** | **1,440 (8.7%)** | 20 | **1,585 (9.6%)** | 1,630 |

**The BV filter alone removes ~86% of the market.** Only 13.6% of SBI 43 and 9.6% of hoveniers
are BVs. Installatie (432) is the most BV-heavy sub-sector at 20.4% — which validates the choice
of loodgieters/installateurs as the beachhead on this axis specifically.

ZZP context (CBS **85077NED**, 2024, F Bouwnijverheid, persons):
zelfstandigen 258,500 · **ZZP zonder personeel 222,800** · ZMP met personeel 25,600 · DGA zonder
personeel 10,400. https://opendata.cbs.nl/statline/#/CBS/nl/dataset/85077NED/table

### 1.3 The key number: trade BVs with ≥1 employee — DERIVED

**CBS does not cross-tabulate legal form × size class × SBI.** Verified against 81588NED,
81589NED, 86281NED and 81644NED: in every table, size class and legal form are *parallel column
sets* over the same SBI × period dimension, never crossed. The marginals alone leave SBI 43
anywhere between 0 and 19,495, so a derivation with a stated assumption is unavoidable.

Two independent derivations were run and they converge.

**Method A — Eurostat employer × legal-form anchor.**
CBS **85206NED** "Werkgeversdemografie, Europese norm; rechtsvorm, SBI2008" *is* a genuine
cross-tab (employers × legal form × SBI) but only at section level plus 813, latest year 2023.
https://opendata.cbs.nl/statline/#/CBS/nl/dataset/85206NED/table

```
F Bouwnijverheid 2023: 26,055 employers, of which NV+BV = 16,924 (65.0%)
Rechtspersonen F, 2023Q4 (81589NED)                      = 32,530
BV-employer rate = 16,924 / 32,530                       = 0.5203
Apply to 2026Q3 rechtspersonen per sub-sector:
   432 Bouwinstallatie  8,720 x 0.5203 = 4,537
   4391 Dakbouw         1,125 x 0.5203 =   585
   813 Hoveniers        (own 2023 datapoint, 914-1,182)  = ~1,050
                                          CORE ICP TOTAL = ~6,170
```

**Method B — VOF-occupancy constraint.** A VOF has ≥2 partners by definition, so it necessarily
occupies a ≥2-wp slot. This bounds how many ≥2-wp slots are left for BVs.

```
Firms with >=2 wp across 4321+4322+4329+4391+8130 (81589NED 2026Q3) = 12,520
minus VOF + maatschap in scope                                      =  -4,345
= strict UPPER BOUND on BVs with >=1 employee                       =   8,215
minus eenmanszaken met personeel (~4% of ~49,500 in scope)          =  -1,980
= central estimate                                                  =   6,235
```

**Convergence: Method A ≈ 6,170, Method B ≈ 6,235.**

| Definition | Trade BVs with ≥1 employee |
|---|---|
| Broad — all SBI 43 + 813 | **~11,300** (range 10,500–12,200) |
| ICP-relevant — SBI 43 excl. afwerking/schilders (433) + 813 | **~8,200** |
| **Core ICP — 432 installatie + 4391 dakbouw + 813 hoveniers** | **~6,200** |

The founder's ICP explicitly excludes schilders, so **~6,200 is the honest filtered TAM**, and
~8,200 is the generous reading. Not 143,000.

### 1.4 From TAM to SAM

**Website filter — DIRECTLY SOURCED.** CBS **86116NED** "ICT-gebruik bij kleine bedrijven;
bedrijfstak en bedrijfsgrootte, 2025", F Bouwnijverheid:
https://opendata.cbs.nl/statline/#/CBS/nl/dataset/86116NED/table

| Size class | Has website | Uses AI | Uses social media |
|---|---|---|---|
| 2+ wp | **63%** | **8%** | 46% |
| **2–10 wp** | **57%** | **5%** | 41% |
| 10–50 wp | 91% | 16% | 74% |
| 50–250 wp | 98% | 41% | 96% |

Two things this says. First, **43% of small construction firms have no website at all** — for a
product whose entry channel is a web chat widget, that is a hard gate, not a soft one. Second,
**only 5% of 2–10 wp construction firms use AI of any kind**. This is a market that has to be
educated before it can be sold to; it is not a market waiting for a better AI receptionist.

**Inbound-volume filter.** A large share of 4321 elektrotechniek and 43222 verwarmingsinstallatie
revenue is B2B / nieuwbouw onderaanneming with no consumer inbound funnel at all — those firms
have a purchasing contact, not a switchboard. The founder's own disqualifier is ≤1 call/week.
Estimated 40–55% of the filtered set is genuinely consumer-inbound-driven. This is the softest
assumption in the chain and is not directly sourced.

```
Core filtered TAM (trade BV, >=1 employee)                   6,200
x has a website (CBS 86116NED, 63%)                          3,900
x consumer-inbound-driven enough to justify EUR299/mo (~45%) 1,760
=> DEFENSIBLE SAM                                            ~1,500 - 2,150
```

**SAM ≈ 2,000 businesses.** At €299/mo that is a theoretical ceiling of ~€7.2M ARR if the founder
won *100%* of the served market. At a more realistic 3–5% penetration of the SAM, it is
60–100 clients, i.e. **€215k–€360k ARR** — which is a real solo-founder business, but it is a
lifestyle-business ceiling, not a venture-scale one.

---

## 2. Is €299/mo affordable for this buyer?

Source: CBS **81156ned** "Bedrijfsleven; arbeids- en financiële gegevens, per branche, SBI 2008",
**2024** (latest), SBI **4322 Loodgieters en installatiebedrijven**.
https://opendata.cbs.nl/statline/#/CBS/nl/dataset/81156ned/table

| Metric | SBI 4322 (2024) | SBI 432 | SBI 813 | SBI 43 |
|---|---|---|---|---|
| Netto omzet | €14,605 mln | €33,174 mln | €5,467 mln | €67,916 mln |
| Bedrijfsresultaat | €1,928 mln = **13.2%** | 12.9% | 16.4% | 15.8% |
| **Communicatiekosten** | €36 mln = **0.25% of omzet** | 0.24% | 0.29% | 0.26% |
| Werkzame personen | 81,700 | 190,900 | 53,500 | 428,200 |
| **Omzet per werkzaam persoon** | **€178,764** | €173,777 | €102,187 | €158,608 |

Margins are healthy (13–16%) — this is not a poor sector. Applying revenue-per-head to firm sizes:

| Firm size | Omzet | Bedrijfsresultaat | Communicatiekosten | €3,588/yr as % omzet | % of profit | **% of TOTAL comms budget** |
|---|---|---|---|---|---|---|
| 2 persons | €358k | €47k | €881 | 1.00% | 7.6% | **407%** |
| 3 persons | €536k | €71k | €1,322 | 0.67% | 5.1% | **271%** |
| 5 persons | €894k | €118k | €2,203 | 0.40% | 3.0% | **163%** |
| 9 persons | €1.61M | €212k | €3,966 | 0.22% | 1.7% | **90%** |

**The sharpest finding in the affordability analysis:** at €3,588/yr, Klantkraan costs
**1.6× to 4× the entire annual communications budget** of a 2–5 person installatiebedrijf. Below
about 8–9 staff, the product costs more than everything the firm currently spends on phones,
mobile, internet and connectivity *combined*.

That does not make it unaffordable — 3–7.6% of operating profit is a defensible ask, and one
recovered €400 spoed job per month covers it outright. But it does mean:

1. **This is a new budget line, not a substitution sale** — unless the prospect already pays for
   a human antwoordservice. The pitch must be revenue-recovery ("one saved job pays for it"),
   never cost-saving ("cheaper than a telefoniste"), because against their *actual current spend*
   it is a 2–4× increase.
2. **The €299 price point pushes the ICP up-market.** The comfortable zone is 5–9 staff, not 2–3.
   In the core ICP universe the 5–50 wp band is only ~4,500 firms *before* the BV and website
   filters — which tightens the SAM further.
3. **A €149–199 tier would sit inside the existing comms budget** for a 3–5 person firm. That is
   a materially easier sale and matches where the competition has moved (see §3).

### Incumbent alternative: human antwoordservice

Live-fetched pricing was only partially obtainable this session (search budget exhausted; several
providers moved domains — telefoonservice.nl now 302s to directklantcontact.nl, bizzview.nl 301s
to bizzview.com). Known-good anchors from the repo's own prior research, to be re-verified:

- Human antwoordservices in the riool/spoed branch bill **€100–500/mo** (repo research
  `first-client-market-research-2026-08-10.md`, §2) — so where a firm *already* buys one,
  Klantkraan at €299 is a genuine substitution sale and the affordability objection disappears.
- **Antwoordservice Nederland** has itself gone hybrid-AI via "Bonnie" (AI handles ~75%, human
  takes over) — the incumbents are absorbing AI rather than being displaced by it.
- A part-time telefoniste is not a real alternative at this wage level: 67–68% of technical firms
  report staff shortage, 75,600 open technical vacancies end-2024, 121,000 vakmensen needed in
  5 years (Techniek Nederland, via repo research).

**The substitution-sale subset — firms already paying for an antwoordservice — is the highest-value
segment in the entire SAM**, and it is much smaller than the SAM itself.

---

## 3. Competitive landscape, August 2026

### 3.1 Live-fetched prices (2026-08-16)

| Vendor | URL | Price | Setup | Channels | Targets trades? | Fetched |
|---|---|---|---|---|---|---|
| **LoodgieterAI** | loodgieterai.nl | **€79 Basis / €297 Pro / €497 Elite** (+€197 unlimited add-on); 14 days for €1 | — | Voice AI + chatbot + WhatsApp/SMS + CRM + email + social + SEO + image/video gen | **YES — loodgieters only** | live |
| **InstallatieTelefoniste** | installatietelefoniste.nl | **€0,15/min, geen abonnement** | from €250 | Voice only | **YES — installateurs + loodgieters** | live |
| **Klusio** | klusio.nl | €199 Start / €399 Pro / €699 Marktleider | — | AI telefonist (voice) **included in all tiers, no per-call cost** + AI chatbot + WhatsApp + SEO content | **YES — vakmensen/MKB** | live |
| **Watermelon** | watermelon.ai/nl/prijzen | **Free (50 conv.) / €99 (250) / €199 (500) / €399 (1,000)**; -15% annual | — | Webchat, email, WhatsApp, Messenger, IG DM. No voice tier. | Horizontal | live |
| **Trengo** (NL) | trengo.com/nl/prijzen | **€299 Boost** (10 users, 6,000 conv/yr) / €499 Pro (20 users, 18,000 conv/yr) | — | WhatsApp + voice + SMS; AI agent (HelpMate) **included in all plans**; +€0,30/AI conversation | Horizontal | live |
| **Voicelabs (Robin)** | voicelabs.nl | Public pricing **removed** — now demo/contact only (was €299/1,000 min) | — | Phone + WhatsApp + webchat | **YES — dedicated loodgieters + elektriciens pages** | live |
| **Secretaresse.ai** | secretaresse.ai | Page is JS-rendered; price not retrievable this session (was €397/mo + €497 setup) | — | Voice | Was targeting vakspecialisten | **not verified** |

Not re-verified this session (from repo research, 2026-07-30 / 2026-08-10 — treat as stale):
Gold Lemon €199 + €899 setup · Cowcierge €150 · MyAutoPilot €350 + €1,350 · VoxFlow from €99 ·
LokaleAI €125–195 ("pay only after you approve go-live") · Growguide €349–497 · Places.nl "AI Daan"
(30 days free) · MIKE365 €14,99 entry.

### 3.2 Is "€299 chat-only has no direct competitor" still true?

**NO. The claim is dead, and it is dead in three separate directions.**

1. **Priced below on chat.** Watermelon sells webchat + WhatsApp + Messenger + IG at **€199 for
   500 conversations**, with a **free tier at 50 conversations**. A 3-person loodgieter doing
   <500 conversations/month pays €199, or €0. Klantkraan's €299 chat tier is ~50% above a
   better-known Dutch vendor with a free entry point.
2. **Out-featured at the same price.** Trengo — a Dutch company — sells €299 for 10 users,
   6,000 conversations/year, WhatsApp *and* voice *and* SMS, AI agent included.
3. **Undercut inside the vertical.** LoodgieterAI sells a loodgieter-specific bundle at
   **€297 Pro and €497 Elite** — within €2 of Klantkraan's €299 and within €2 of the planned
   €499 — while bundling voice, chat, CRM, SEO, social and video. Its entry tier is **€79**.

**Price compression is visibly happening in real time.** InstallatieTelefoniste was **€0,25/min**
in the repo's own research dated **2026-08-10**; it is **€0,15/min** today, **2026-08-16** — a
**40% cut in six days**. At €0,15/min a firm taking 200 calls/month at 3 minutes pays **€90/mo**
against Klantkraan's planned €499 voice tier.

### 3.3 The art. 50 differentiator

Verified: EU AI Act **Article 50 became applicable 2 August 2026** — two weeks ago.
https://artificialintelligenceact.eu/article/50/
The obligation is that natural persons are informed they are interacting with an AI system,
"at the latest at the time of the first interaction", unless it is obvious.

This is a **one-line disclosure that every competitor can add in an afternoon**, and it is now
mandatory for all of them. It was a differentiator while it was optional; since 2026-08-02 it is
a compliance floor. The repo's own research reached the same conclusion on 2026-08-10 ("reframe
from 'the compliant one' to 'compliant by design from day one'"). **Do not build pricing on it.**

The founder's stated positioning — "the ONLY text-first + trades + art.50-compliant player in NL"
— is now false on the "only" and worthless on the "art.50". Text-first + trades remains
*distinctive* but is not a moat: Klusio and LoodgieterAI both ship chat + WhatsApp for trades.

---

## 4. Has the category commoditised? Incumbent bundling

*(populated below from parallel research)*

---

## 5. Trade-software platforms embedding AI answering

*(populated below from parallel research)*

---

## 6. Verdict

*(populated below)*
