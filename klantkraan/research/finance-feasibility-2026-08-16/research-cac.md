# Klantkraan CAC assumptions — stress test against 2026 data

Date: 2026-08-16. All figures sourced 2026 unless noted. Method note: the session's
WebSearch budget was exhausted, so research was run through a live Chrome session
against Google, plus direct WebFetch of primary sources (statute text, Google/Yahoo
sender guidelines) and the Ahrefs free keyword tool for NL search volume.

---

## 0. Verdict table

| Line | Plan | Corrected | Error |
|---|---|---|---|
| Cold email clients/mo | 5–8 | 0.3–1.5 (central 1.0) | 5–20x over |
| Cold email send→client | 0.10–0.15% | 0.005–0.028% | 5–20x over |
| Cold email stack cost | €146/mo | €200–350/mo | 1.5–2.4x under |
| LinkedIn invites/mo | 600 | ~400 (hard cap) | 1.5x over |
| LinkedIn clients/mo | ~3 | ~0.2 | 12–15x over (plan also mis-multiplies its own funnel by 4x) |
| Google Ads clients/mo | 2–4 | 0.2–0.5, inventory-capped | 5–10x over; channel structurally void |
| Organic clients/mo by M6 | 3 | 0.2–0.5 | 6–15x over |
| Partnerships/mo by M6 | 1–3 | 0.3–1.0 | 2–3x over on speed |
| Blended cash CAC | €150–250 | €300–700 | 2–3x under |
| Blended fully loaded CAC | ~€400 | €2,000–3,500 | 5–9x under |
| Payback | <1 month | 1.3–2.9 mo cash; 8–15 mo fully loaded | — |
| Months to 10 clients | (implied ~1–2) | 9–12 (range 6–18) | — |

---

## 1. Cold email feasibility in 2026

### 1a. Authentication / bulk-sender regime — what changed

**Google** (https://support.google.com/a/answer/81126) — all senders, mandatory since
1 Feb 2024:
- SPF **or** DKIM on sending domains
- valid forward and reverse DNS (PTR)
- TLS for transmission
- RFC 5322 compliance
- **spam rate below 0.3%** in Postmaster Tools

Senders of **5,000+ messages/day to Gmail** additionally need: DMARC; From: header
aligned with SPF or DKIM domain; DKIM key ≥1024 bits (2048 recommended); one-click
unsubscribe (`List-Unsubscribe-Post: List-Unsubscribe=One-Click` + `List-Unsubscribe`).

**Yahoo** (https://senders.yahooinc.com/best-practices/) — enforcement from Feb 2024:
all senders SPF or DKIM, spam rate <0.3%, valid forward/reverse DNS, RFC 5321/5322.
Bulk senders additionally: SPF **and** DKIM, **DMARC p=none minimum and DMARC must
pass**, working one-click list-unsubscribe (RFC 8058 Post method recommended), visible
unsubscribe link, **honour unsubscribes within 2 days**.

**Microsoft / Outlook.com** — the 2025 change. Effective **5 May 2025**, domains
sending **more than 5,000 emails/day** to Outlook consumer mailboxes must have SPF,
DKIM **and** DMARC. Non-compliant mail is **first routed to Junk, then rejected**.
- Announcement: https://techcommunity.microsoft.com/blog/exchange/strengthening-email-ecosystem-outlooks-new-requirements-for-highvolume-senders/4399730 (2 Apr 2025)
- Corroborated: https://www.mailgun.com/blog/deliverability/microsoft-outlook-sender-requirements-2025/ (1 May 2025), https://dmarcwise.io/blog/outlook-new-requirements (4 May 2025), https://mailtrap.io/blog/outlook-new-email-sender-requirements/ (24 Apr 2025)

### 1b. Does the bulk regime actually bind Klantkraan? No — and that matters

5,300 sends/month ÷ ~21 working days = **~250 sends/day total**, spread over 6–12
domains = **~20–40 per domain per day**. That is two orders of magnitude below every
5,000/day bulk threshold. **The Gmail/Yahoo/Microsoft bulk-sender rules are not the
binding constraint.**

The binding constraint is the **0.3% spam-complaint ceiling**, which applies to *all*
senders. 0.3% of 5,300 = **16 complaints per month across the entire programme — one
complaint per 333 emails**. Cold email to a scraped list of trade businesses reliably
generates complaints above that rate unless targeting and copy are excellent. This,
not authentication, is what kills domains.

### 1c. Infrastructure actually required

2026 safe per-inbox sending rates (consensus across sources):
- 10–20 emails/inbox/day — https://www.scaledmail.com/blogs/cold-email-infrastructure (8 Apr 2026)
- 25–30/inbox/day at full maturity — https://leadhaste.com/blog/complete-guide-cold-email-2026 (9 Apr 2026)
- 25–40/inbox/day mature — https://emailbison.com/blogs/dedicated-ip-clusters (20 May 2026)
- 2–3 mailboxes per domain — https://www.genflows.com/blog/how-many-domains-mailboxes-cold-email-2026 (24 Jul 2026), https://howmanydomainsforcoldmail.com (28 Jan 2026)

At 250/day: **9–11 mailboxes** at the aggressive 25–30/day rate, **13–25 mailboxes**
at the safe 10–20/day rate. Call it **15–25 mailboxes across 6–12 domains**, plus
3–4 weeks of warmup before real volume.

### 1d. Real monthly cost

| Item | Cost |
|---|---|
| 8–12 domains @ ~€12/yr | ~€10/mo |
| 18 mailboxes — Google Workspace @ ~€7 | €126/mo |
| 18 mailboxes — cold-email reseller @ ~€2.50 | €45/mo |
| Smartlead (base $39, https://www.landbase.com/blog/smartlead-pricing) | €36/mo |
| Email verification, 5,300 records | ~€20/mo |
| Outscraper + KvK API | €30–60/mo |
| **Total (reseller mailboxes)** | **€200–350/mo** |
| **Total (Google Workspace as planned)** | **€300–450/mo** |

Plan says €146/mo. **Understated 1.5–3x.** MarketBetter puts real all-in Smartlead
outbound at $500–700/mo once mailboxes, domains and warmup are added
(https://marketbetter.ai/blog/smartlead-pricing-breakdown).

### 1e. Is 0.10–0.15% send-to-client defensible? No.

The single best dataset is **Belkins' 2026 study** — https://belkins.io/blog/cold-email-response-rates
Methodology (stated): Jan–Dec 2025, **7,530,489 emails**, **34,393 replies**,
**1,200+ appointments booked**. Reply rate = unique replies ÷ emails sent, excluding
auto-replies and bounces. Open-rate tracking disabled.

- Reply rate: **0.457%**
- **Send → appointment: 1,200 / 7,530,489 = 0.0159%**

That is send-to-MEETING. The plan claims 0.10–0.15% send-to-CLOSED-CLIENT — i.e.
**6–9x higher than the measured meeting rate, before any close rate is applied.**

Geography (Belkins): Poland 1.43% (best), Ireland 0.74%, Denmark 0.73%, Canada 0.63%,
US 0.51% (5.6M emails), UK 0.48%. European markets outperform because of lower
saturation. NL is not broken out but plausibly sits in the 0.6–0.8% band.

Vendor benchmarks are much higher and much softer:
- 3.4% platform-wide, down from 5% in 2025 — https://agentic-demand.com/blog/b2b-cold-email-benchmarks-2026 (24 Jun 2026)
- 3.1–3.7% on managed infrastructure — https://www.lacleo.ai/blog (4 Aug 2026)
- B2B SaaS 3–8%, blended B2B 5.8% (down from 6.8% in 2023) — https://saleshive.com/blog/
- 3–5.1% across 2024–2025 — https://thedigitalbloom.com (10 Nov 2025)

The gap is methodological: vendors measure campaign-level bests on warm/verified,
heavily personalised low-volume sends; Belkins measures unique replies ÷ **sent** over
7.5M strictly cold net-new contacts. The plan's situation is the Belkins situation.

**Two corrected funnels at 5,300 sends/month:**

*Pessimistic (Belkins-grounded, NL uplift 1.5x):*
5,300 × 0.024% send→appointment = **1.27 meetings/mo** × 20% close = **0.25 clients/mo**
→ send→client = 0.0048%.

*Realistic (solo founder, low volume, tight NL trade niche, good personalisation —
reply rate 2%):*
5,300 × 2% = 106 replies × 15% positive = 16 positive × 50% → meeting = 8 meetings
× 15% close (no case studies, skeptical trade owners) = **1.2 clients/mo**
→ send→client = 0.023%.

**Cold email realistic: 0.3–1.5 clients/month, central ~1.0. Plan says 5–8. Overstated
5–20x.**

Close rate note: 15–20% meeting→paying is the right number for a founder with zero
case studies selling €299/mo to conservative Dutch trade BVs. It rises to 25–30% once
2–3 referenceable clients exist.

### 1f. List exhaustion — a constraint the plan ignores

NL installer/trade universe: **30,827 installateurs** (loodgieters, elektriciens,
CV-monteurs) — https://companydata.com/bedrijven/installateurs; ~45,000 installatie-
bedrijven including ZZP — https://installatie-shop.nl/blogs/nieuws/installatietechniek-statistieken-2025.
Across the five target vaks, generously ~50–60k businesses; the **BV-only** slice is
roughly 20–30% → **10,000–18,000 addressable companies**.

At 5,300 sends/month on a 4-touch sequence = **~1,325 new companies/month**. The entire
BV-filtered national list is **exhausted in 8–14 months**. Cold email is not a
perpetual channel here; it is a one-pass resource.

### 1g. GDPR / ePrivacy / Telecommunicatiewet — the actual Dutch rule

Statute read directly: https://wetten.overheid.nl/BWBR0009950 art. 11.7

**Lid 1** — unsolicited electronic messages for commercial, ideological or charitable
purposes are **prohibited unless the sender can prove the eindgebruiker gave prior
consent**. "Eindgebruiker" is defined in the Tw as *natuurlijke persoon **of
rechtspersoon***. So the opt-in ban **does** cover BVs. NL is stricter than most of the
EU here.

**Lid 3** — the B2B carve-out, quoted verbatim:

> "In afwijking van het eerste en tweede lid, is geen voorafgaande toestemming vereist
> voor het overbrengen van ongevraagde communicatie voor commerciële, ideële of
> charitatieve doeleinden aan een rechtspersoon of een natuurlijke persoon die handelt
> in de uitoefening van zijn beroep of bedrijf, indien:
> a. de verzender gebruik maakt van elektronische contactgegevens die door de
> desbetreffende eindgebruiker **voor het ontvangen van ongevraagde communicatie voor
> commerciële, ideële of charitatieve doeleinden zijn bestemd en bekendgemaakt** en
> deze worden gebruikt **in overeenstemming met de door de eindgebruiker aan de
> contactgegevens verbonden doeleinden**, of
> b. de desbetreffende eindgebruiker is gevestigd buiten de Europese Economische
> Ruimte en voldaan wordt aan de in het desbetreffende land geldende voorschriften..."

**Reading this correctly.** Lid 3a is **two cumulative conditions**, not one:
1. the address is **bestemd én bekendgemaakt** *for receiving unsolicited commercial
   communication*, and
2. it is used **in accordance with the purposes the end user attached to it**.

Merely being published is not enough — it must be published *for that purpose*. A
generic `info@loodgietersbedrijf.nl` on a contact page is published for **customer
enquiries**, not for receiving marketing. Scraping info@ addresses from Google
Maps/KvK and cold-emailing them does **not** cleanly satisfy lid 3a.

Sources split on how permissive this is:
- Conservative: DDMA's e-mail wetgeving page (https://ddma.nl/legal/wetgeving/e-mail/)
  lists only three exceptions — existing customer relationship (5 cumulative
  conditions), service messages, and requested communication — and **no exception for
  publicly published addresses**. Security.NL likewise: "De wet kent geen uitzondering
  voor 'zelf openbaar gemaakte gegevens'."
- Permissive (vendor, commercially motivated): https://www.reachiq.nl/gids/cold-email-avg-b2b
  (30 Jun 2026) reads lid 3a as permitting cold email to a BV's deliberately published
  business address provided every message carries a free one-click opt-out.
- ACM's own guidance (https://www.acm.nl/nl/verkoop-aan-consumenten/reclame-en-verleiden/spam-voorkomen-uw-reclame)
  states the rule as consent-first, allows only the existing-customer exception, and
  requires an identifiable sender (no alias) and a **quick, free** unsubscribe.

**Practical conclusion: legally grey, defensible only with a narrow, well-documented
approach — not a clean green light.** Requirements to be as defensible as possible:
- BV / rechtspersoon only (already in the plan)
- role addresses the company published for business contact; never scraped personal
  named mailboxes
- content strictly relevant to the recipient's trade (satisfies "in overeenstemming met
  de doeleinden")
- identifiable sender, working free opt-out in every message, one-click
  `List-Unsubscribe` (RFC 8058)
- GDPR layer on top: art. 6(1)(f) legitimate interest **with a written LIA**, plus the
  art. 14 information duty because the data is scraped rather than collected from the
  person
- suppression list honoured within 2 days

**Enforcement:** ACM. Fines up to **€900,000 or 1% of turnover**. ACM has a live
precedent for e-mail spam enforcement (Boetebesluit e-mailspam Companeo,
https://www.acm.nl — 41-page decision).

**Correction to the plan's own reasoning:** the BV-only filter is **not required by
art. 11.7** — lid 3 covers "een natuurlijke persoon die handelt in de uitoefening van
zijn beroep of bedrijf" on exactly the same terms as a rechtspersoon. Excluding
eenmanszaak/VOF is justified under the **GDPR** (a sole trader's business address is
personal data, so the full art. 6/14 burden lands), not under the Telecommunicatiewet.

---

## 2. Google Ads — the category has no inventory

### 2a. NL search volume, measured

Ahrefs free Keyword Generator, country = Netherlands (Google):

| Seed | Keywords returned | Volumes |
|---|---|---|
| `AI telefoniste` | **2 total** ("ai telefoniste", "ai telefoniste mkb") | **both <100/mo** |
| `antwoordservice` | 71 | only **2 above 100/mo** ("antwoordservice", "antwoordservice nederland"); every other term <100/mo, including "professionele antwoordservice", "antwoordservice 24 7", "tarieven antwoordservice", and every city variant |

Two of the *two* keywords that exist in Dutch for "AI telefoniste" are sub-100/month.
The established human answering-service category — which has existed for decades —
tops out at a single head term in the 100–1,000 bucket.

**Estimated total NL monthly search volume for the whole category** (AI receptionist /
AI telefoniste / AI receptioniste / antwoordservice / telefoonservice + variants):
**~500–1,500 searches/month nationally.** The slice that is both trade-qualified and
commercially intent-bearing ("antwoordservice loodgieter", "AI telefoniste
installatiebedrijf") is **~100–300 searches/month**.

**The plan's example term "AI receptionist loodgieter" has effectively zero volume.**
Nobody in the Dutch market searches for this yet — buyers do not know the category
exists. This is a category-creation problem, and search advertising cannot solve
category creation; it can only harvest existing demand.

### 2b. CPC

- NL average CPC **~€2.15**, up **18% vs 2024** on increased competition — https://searchlab.nl/blog/google-ads-statistieken/ (8 Mar 2026)
- NL range €0.60–€12 depending on branche/keyword/quality score — https://www.empowers.nl/blogs
- NL B2B **€3–15** — https://www.picoyellow.nl/blog (Google Ads gids MKB 2026)
- NL general €1.50–3.50 — https://brightbrands.online

For a contested B2B category the realistic CPC is **€4–7**. The plan's €2.50–4.50 is
low but not the problem.

### 2c. Conversion rate

- Google Ads all-industry average CVR **8.18%** (all networks) — https://www.wordstream.com/blog/google-ads-benchmarks (19 May 2026), corroborated https://www.searchenginejournal.com (16 Jun 2026)
- **Search only, all industries: 3.75%**; **B2B search: 3.04%** — https://www.wordstream.com/blog/ws/2016/02/29/google-adwords-industry-benchmarks (6 Jul 2026)
- B2B SaaS search **3–5%** for well-structured accounts — https://www.kampaio.com/blog (1 Jun 2026)
- Search CVR down 9.28% YoY — https://foundrycro.com/blog (13 Apr 2026)

Plan assumes 6%. Correct figure is **3–4%**.

### 2d. Corrected Ads line

At ~200 trade-qualified searches/month, 50% impression share, ~5% CTR → **5–15
clicks/month**. Bidding the entire wider category (~1,000 searches) → **30–60
clicks/month**.

- 30–60 clicks × €5 = **€150–300/month — the €400 budget cannot be spent**
- 30–60 clicks × 4% CVR = **1.2–2.4 leads/month**
- × 20% close = **0.24–0.5 clients/month**

**Plan says 2–4. Corrected: 0.2–0.5, and hard-capped by inventory rather than budget.
This is the assumption that is wrong in kind, not just in degree.**

### 2e. The category is already contested in NL

A single SERP for AI receptionist terms + vakmensen returns at least nine Dutch
competitors already selling this exact product to this exact ICP: palside.com,
voicelabs.nl, callingbird.nl, staffifyai.com (€250), vocito.ai, contactons.ai,
getsam.nl, blovio.com, solixa.ai — plus secretaresse.ai at €397/mo and bellen.app.
KPN has launched "Mobiel AI" for ondernemers
(https://www.kpn.com/zakelijk/thedigitaldutch/blog/telefoon-opnemen-mobiel-ai).

So: near-zero search volume **and** a crowded bid landscape. Worst possible
combination for paid search. (Note: this also invalidates the repo's July 2026 memory
that Klantkraan is the only text-first trades player.)

---

## 3. LinkedIn

### 3a. Limits — 600 invites/month is not achievable

- **~100 connection requests/week** for free and Premium; Sales Navigator may allow
  somewhat higher — https://phantombuster.com/blog/social-selling/linkedin-connection-request-limits
- 100–200/week depending on account trust, subscription and acceptance rate — https://www.linkedhelper.com/blog/linkedin-automation-limits/
- Accounts under 90 days old: **50–100/week**, and 20–30/week for the first 0–3 months
  — https://evaboot.com/blog/linkedin-weekly-invitation-limit, https://useembers.com/blog/linkedin-weekly-invitation-limit
- Safe zone 2026: 60–100/week

**Ceiling is ~400 invites/month**, not 600 — and for the first quarter of a new/low-
activity account, ~100–150/month.

### 3b. Real accept and reply rates

**Expandi 2026** — https://expandi.io/blog/linkedin-outreach-benchmarks/ — 13,218,869
connection requests, 6,730,447 outbound messages, 3,766,161 accepted connections,
13,302 accounts, May 2025–Apr 2026:
- **connection acceptance 28.5%**
- connection-note reply **3.0%** (down 37% over 12 months, 3.5% → 2.2%)
- **message reply 10.4%** (stable)

**Belkins 2026** (15M+ contacts) — https://belkins.io/blog/ — connection rate **26%**,
overall reply **7.2%** (range 4.2–10.5%).

Others: 28–30% acceptance, ~45% personalised vs ~15% generic — https://overloop.com/blog/linkedin-outreach-benchmarks;
25–35% acceptance and **meeting conversion 1–3% of total outreach** — https://www.salescaptain.io/blog/cold-linkedin-outreach;
pure cold outreach reply ~5.1% — Expandi via LinkedIn/Serge Bulaev.

Plan assumes 35% accept / 6% reply. Accept is optimistic (28.5% measured), reply is
roughly right if measured on accepted connections.

### 3c. The plan's LinkedIn arithmetic is internally wrong

Plan: 600 × 35% × 6% × 25% × 25% = **0.79 clients/month**, not the ~3 stated. The
plan's own funnel, multiplied out, is **4x** below its own headline.

**Corrected with measured 2026 inputs:**
400 invites × 28.5% = 114 connections × 10.4% message reply = 11.9 replies
× ~20% positive = 2.4 positive → 50% to meeting = 1.2 meetings × 15–20% close
= **0.18–0.24 clients/month**.

Cross-check against salescaptain's 1–3% meeting-per-outreach: 400 × 1–3% = 4–12
meetings/mo × 15% = 0.6–1.8 clients — more generous, but that figure is for
established senders with social proof. Take **0.2–0.5 clients/month**.

**Plan says ~3. Overstated 6–15x.**

### 3d. Is the ICP even on LinkedIn?

NL LinkedIn is large in aggregate: **5.8M users in 2026** (Newcom, +1% YoY) —
https://socialblooming.com/linkedin-gebruik-in-nederland/; 6.2M and ~35% penetration
per https://searchlab.nl/statistieken/linkedin-statistieken; 1.7M daily active (2025) —
https://fingerspitz.nl/blog/.

But aggregate penetration is not ICP presence. LinkedIn's NL base skews white-collar
(recruitment, corporate, professional services). Owner-operators of small loodgieter/
dakdekker/slotenmaker BVs are, as a population, light or absent LinkedIn users — their
professional social usage sits on WhatsApp, Facebook groups and Instagram. No source
found quantifying LinkedIn penetration among Dutch trade-business owners specifically,
which itself is telling. Expect a **materially thinner and staler targetable pool**
than Sales Navigator's filter counts imply, and treat Sales Navigator company-size/
industry counts as an upper bound that includes dormant profiles.

### 3e. Tooling conflicts with a stated founder constraint

The plan budgets **HeyReach** ($79–199/mo — https://www.heyreach.io, https://moderninbound.com/blog)
plus **Sales Navigator Core $99.99/mo** (https://smartreach.io/blog/linkedin-sales-navigator-cost)
≈ €165–250/mo. HeyReach **automates connection requests and follow-up DMs**. The
founder's stated constraints are *manual connection requests only* and *no automated
replies/DMs on any platform*. **HeyReach violates the founder's own rule.** Manual-only
means the tool line disappears (~€100/mo for Sales Navigator alone) and 4–6 h/week of
founder time appears instead.

---

## 4. CAC benchmarks — €299/mo SaaS to European micro-SMB trades

- **SMB SaaS (<$15K ACV): CAC $200–$700** — https://ltvcacbook.com/blog/cac-benchmarks (4 Apr 2026)
- **SMB SaaS $200–$400** — https://pmtoolkit.ai/benchmarks (CAC benchmarks by industry 2026)
- **Self-serve SMB products: $100–$500 CAC ceiling set by ACV** — https://www.saashero.net/google-ppc/saas-cac-benchmarks (27 Jul 2026)
- For SMB SaaS with low ACV, **CAC must stay below $500** — https://signado.io/tools/cac-calculator
- **Self-serve CAC $702; sales-led $11,400; up 9% since 2024** — https://www.digitalapplied.com/blog/customer-acquisition-cost-benchmarks (21 Apr 2026)
- **Median B2B paid-search CAC $802 in 2026, payback stretched to 20 months** — First Page Sage 2026 via https://semmonks.com/saas-cac-calculator
- **Median SaaS CAC payback 16 months** (2025 data) — https://www.getaleph.com/answers/cac-payback-period-benchmarks (25 Jun 2026)
- CAC payback target 12 months, 18–24 tolerated — Digital Applied 2026

Klantkraan ACV = €3,588/yr (€299 × 12), squarely in the "self-serve SMB / low ACV"
band. The benchmark band that applies is **€200–700 cash CAC**, with the caveat that
those benchmarks are for companies with a brand, a website that ranks, and existing
customers — none of which apply at zero clients.

The plan's €150–250 cash CAC sits **below the floor** of every SMB SaaS benchmark
found, and it is claimed by a founder with no case studies in a category with no search
demand. Not defensible.

---

## 5. Corrected model

### 5a. Steady-state channel table (months 4–6, solo founder, no case studies)

| Channel | Cash/mo | Clients/mo | Cash CAC |
|---|---|---|---|
| Cold email | €275 | 1.0 (0.3–1.5) | €275 (€180–900) |
| LinkedIn (manual, Sales Nav only) | €100 | 0.2 (0.2–0.5) | €500 |
| Google Ads | €300 (cannot spend €400) | 0.35 (0.2–0.5) | €860 |
| Organic content | €0 | 0.3 (0.2–0.5) | €0 cash |
| Partnerships (10% rev-share) | ~€65 rev-share | 0.5 (0.3–1.0) | ~€130 |
| **Blended** | **~€740** | **~2.35** | **~€315** |

Including ramp months and underperformance, the honest blended range is
**€300–700 cash CAC**.

### 5b. Fully loaded CAC

A solo founder realistically spends **20–25 h/week** on acquisition (list building,
writing sequences, manual LinkedIn, demos, follow-up, content) = 87–108 h/month. At a
€45/h notional cost = **€3,900–4,900/month** of founder time.

(€740 cash + €4,400 time) ÷ 2.35 clients = **~€2,190/client**.

**Corrected fully loaded CAC: €2,000–3,500.** Plan says ~€400. **Understated 5–9x.**

### 5c. Payback and LTV

€299/mo ex BTW at ~80% gross margin (LLM inference, hosting, WhatsApp conversation
fees, support) = **€239/mo contribution**.

- Cash CAC €300–700 → **payback 1.3–2.9 months** (plan's "<1 month" is wrong, but this
  is the least damaging error)
- Fully loaded CAC €2,000–3,500 → **payback 8.4–14.6 months**
- Micro-SMB monthly churn 3–5% → 20–33 month lifetime → **LTV €4,780–7,890**
- LTV:CAC — **7–26x on cash**, **1.4–3.9x fully loaded**

The business model works on cash. The founder's *time* is the real cost, and on a
fully loaded basis this is a marginal-to-acceptable, not a spectacular, unit economic.

### 5d. Corrected new clients per month

| Period | Clients/mo | Cumulative |
|---|---|---|
| M1 | 0 (setup, domain warmup 3–4 wks) | 0 |
| M2 | 0.5 | 0.5 |
| M3 | 1.0 | 1.5 |
| M4 | 1.5 | 3.0 |
| M5 | 2.0 | 5.0 |
| M6 | 2.4 | 7.4 |
| M7 | 2.5 | 9.9 |
| M8 | 2.5 (less ~0.3 churn) | ~12 |

**Steady-state realistic: 2–3 new clients/month from month 6, not 11–18.**

### 5e. Months to 10 paying clients from zero

- Optimistic (partnerships land by M2, 2 case studies by M4, founder full-time on
  sales): **6 months**
- **Realistic central: 9–12 months**
- Pessimistic (Belkins-grade cold email, no partner traction, part-time execution):
  **14–18 months**

### 5f. Which assumption is most wrong

1. **Google Ads — wrong in kind.** Measured NL volume: "ai telefoniste" = 2 keywords,
   both <100/mo; the entire antwoordservice cluster has 2 terms above 100/mo out of 71.
   The €400/mo line cannot be spent and the 2–4 clients/mo cannot exist. This is not a
   mis-parameterised channel, it is a channel with no inventory.
2. **Cold email — most damaging.** It carries 5–8 of the plan's claimed clients and is
   overstated 5–20x against a 7.5M-email measured dataset. Correcting it removes the
   majority of the plan's projected growth.
3. **LinkedIn — wrong twice over.** The 600 invites/month exceeds LinkedIn's ~400/month
   ceiling; the plan's own funnel multiplies to 0.79 not 3; the measured funnel gives
   ~0.2; and the budgeted tool (HeyReach) breaks the founder's no-automated-DM rule.

### 5g. Sequencing correction

The plan says "turn on paid ads once 5 clients are closed." Given the volume data,
paid search should be **deleted, not deferred** — reallocate that €400/mo to
partnerships (highest-quality channel, warm, pre-trusted) and to a real referral
incentive. A 10% rev-share on €299 = €29.90/mo per referral, which is too small to
motivate a boekhouder or VoIP reseller; a €300–500 one-off bounty converts far better.

Also: with zero clients today, the first 1–3 customers will almost certainly come from
the founder's warm network or a partner, not from cold email — cold channels need
case studies to convert, and case studies need first clients. Plan for that ordering.

---

## Sources

- https://support.google.com/a/answer/81126
- https://senders.yahooinc.com/best-practices/
- https://techcommunity.microsoft.com/blog/exchange/strengthening-email-ecosystem-outlooks-new-requirements-for-highvolume-senders/4399730
- https://www.mailgun.com/blog/deliverability/microsoft-outlook-sender-requirements-2025/
- https://dmarcwise.io/blog/outlook-new-requirements
- https://belkins.io/blog/cold-email-response-rates
- https://expandi.io/blog/linkedin-outreach-benchmarks/
- https://agentic-demand.com/blog/b2b-cold-email-benchmarks-2026
- https://www.lacleo.ai/blog
- https://www.scaledmail.com/blogs/cold-email-infrastructure
- https://leadhaste.com/blog/complete-guide-cold-email-2026
- https://www.genflows.com/blog/how-many-domains-mailboxes-cold-email-2026
- https://wetten.overheid.nl/BWBR0009950 (Telecommunicatiewet art. 11.7)
- https://www.acm.nl/nl/verkoop-aan-consumenten/reclame-en-verleiden/spam-voorkomen-uw-reclame
- https://ddma.nl/legal/wetgeving/e-mail/
- https://www.reachiq.nl/gids/cold-email-avg-b2b
- https://searchlab.nl/blog/google-ads-statistieken/
- https://www.wordstream.com/blog/google-ads-benchmarks
- https://www.kampaio.com/blog (B2B SaaS Google Ads benchmarks 2026)
- https://phantombuster.com/blog/social-selling/linkedin-connection-request-limits
- https://www.linkedhelper.com/blog/linkedin-automation-limits/
- https://evaboot.com/blog/linkedin-weekly-invitation-limit
- https://ltvcacbook.com/blog/cac-benchmarks
- https://www.saashero.net/google-ppc/saas-cac-benchmarks
- https://www.digitalapplied.com/blog/customer-acquisition-cost-benchmarks
- https://www.getaleph.com/answers/cac-payback-period-benchmarks
- https://socialblooming.com/linkedin-gebruik-in-nederland/
- https://companydata.com/bedrijven/installateurs
- Ahrefs free Keyword Generator, country=Netherlands (seeds: "AI telefoniste", "antwoordservice"), queried 2026-08-16
