# Klantkraan — churn & LTV stress test

Date: 2026-08-16. Subject: AI receptionist, €299/mo ex BTW, Dutch trade micro-BVs, month-to-month + 30-day opzegtermijn + 30-day money-back guarantee.

**Method note.** The session's WebSearch budget was exhausted before this task began, and DuckDuckGo/Mojeek both served CAPTCHA/403 to direct fetches. So this analysis is built on **primary sources fetched directly**: SEC 10-K filings (ServiceTitan, Weave, EverCommerce, all FY2025/FY2026, filed Mar 2026) and the **CBS Netherlands OData API** (live, queried today). These are stronger than the blog benchmarks anyway. Where I could not obtain a citable figure — notably a published "first 90 days" statistic — I say so explicitly and label the number as **modelled, not sourced**. Nothing below is invented.

---

## 0. Headline

| | Plan | Corrected |
|---|---|---|
| Monthly churn | 1.84% | **4.0%** (band 3.0–5.5%) |
| Annual logo churn | 20% | **38.7%** (band 30.6–49.3%) |
| Avg client life | 54 mo | **25 mo** (band 18–33) |
| LTV @96.7% GM | €15,000 | **€7,228** |
| LTV/CAC @€400 | 48–130x | **18.1x** |
| LTV/CAC @€800 | — | **9.0x** |

The plan's "realistic" 20%/yr is not the realistic case. Measured against the only public benchmark that segments by price point, **20%/yr annual churn at this ARPA is roughly the top-quartile outcome**, and the plan's "best in class" 12%/yr is better than anything observed in that band. The plan has labelled its ceiling as its base case.

**The good news, stated up front:** CAC payback is 1.4–2.8 months and LTV/CAC stays above 3x in every scenario tested. The unit economics are *not* broken. What breaks is the **terminal size of the business** (§7) — the churn error is a 2.2x overstatement of how big Klantkraan can ever get at a given sales rate.

---

## 1. Real churn for micro-SMB SaaS at €200–400/mo, month-to-month

### Is "3–7% monthly" right? — Partly. It is right for the *category*, too pessimistic for a *€299 B2B* product specifically.

The 3–7%/month figure is real but is usually quoted from datasets dominated by sub-$50 self-serve and B2C subscriptions. Segmenting by price point moves it materially.

**ChartMogul SaaS Retention Report** (2,100+ SaaS businesses) — the single most useful source, because it segments by ARPA:

| ARPA band | Top-quartile **customer** retention (annual) | Implied top-quartile churn |
|---|---|---|
| < $10/mo | 63.1% | 36.9%/yr = 3.76%/mo |
| > $500/mo | 85.7% | 14.3%/yr = 1.28%/mo |

Bands published: <$10, $10–50, $50–100, **$100–500**, >$500. Klantkraan at €299 (~$325) sits in the $100–500 band. Interpolating between the two published endpoints puts **top-quartile annual customer retention for Klantkraan's band at roughly 75–80%** — i.e. 20–25%/yr churn *for the best quartile*. The **median** operator in that band is materially worse; ChartMogul publishes only top-quartile, which is itself the tell.

Also from ChartMogul: only **2.7%** of businesses with ARPA <$10/mo achieve NRR >100%, vs **41.1%** above $500/mo. Gross revenue retention top quartile: 60–70% for <$50/mo ARPA, 90%+ above $500/mo.
Source: https://chartmogul.com/reports/saas-retention-report/

**Cobloom meta-analysis** (aggregating Baremetrics, Groove, Buffer datasets — all sub-$1M MRR SaaS): **3–5% monthly churn is "typical" for SaaS targeting small businesses**, ≈32–46% annual. Explicitly attributes the gap to monthly billing, low switching costs, and SMB cashflow volatility.
Source: https://www.cobloom.com/blog/churn-rate-how-high-is-too-high

**Vitally / Baremetrics Open Benchmarks** — churn by ARPU band:

| ARPU | User churn | Revenue churn |
|---|---|---|
| $100–250 | 7.1% | 7.8% |
| Over $250 | 5.0% | 6.5% |

⚠️ **Caveat I could not resolve:** the page does not state whether these are monthly or annual, and Baremetrics' own Open Benchmarks page would not render the figures. Baremetrics Open Benchmarks are conventionally monthly, which would make the >$250 band 5.0%/mo — consistent with Cobloom's 3–5%. But since I could not verify the period from source, **I do not lean on this table**; it is corroborative only.
Source: https://www.vitally.io/post/saas-churn-benchmarks

**Recurly network data (July 2026)** — SaaS 3.22% total churn (2.16% voluntary / 1.06% involuntary), Business & Professional Services 3.44%, top quartile ≤1.78%. ⚠️ The page as fetched labels these **annual**, which would be implausibly low for a subscription network median (a 31-year customer life); Recurly's historically published figures of this magnitude are **monthly**. The page is self-contradictory, so **I exclude Recurly from the estimate**. Flagged only so the founder doesn't cite it.
Source: https://www.recurly.com/research/churn-rate-benchmarks/

### Logo vs revenue churn — a distinction that does NOT help Klantkraan

For most SaaS, revenue churn < logo churn because expansion offsets losses. **Klantkraan has no expansion vector**: one flat €299 price, one seat, no usage tier, no upsell inside the tier. Voice is a separate product and not yet live.

Consequence: **logo churn = gross revenue churn = net revenue churn.** Klantkraan's NRR is structurally capped at 100% and will always print below it. Every benchmark that quotes NRR of 96–110% (ServiceTitan, EverCommerce) is quoting a number Klantkraan mathematically cannot reach. This is the most under-appreciated item in the plan.

**Verdict on Q1:** the real range for month-to-month SaaS to micro-SMBs at €200–400 is **2.5–5.5% monthly (26–49% annual)**. "3–7% monthly" overstates the top of the range for a B2B product at this price; the honest band is **3–5%/mo**, and 20%/yr (1.84%/mo) is a top-quartile outcome, not a median one.

---

## 2. Trades / home-services comparables — what the public filings actually say

I pulled the three relevant public companies' latest 10-Ks directly from SEC EDGAR. Podium, Housecall Pro, Jobber, LeadTruffle, Slang.ai, Rosie, Numa and Goodcall are **all private and publish no retention data** — I checked Sacra's research profiles for Podium and Jobber and both explicitly lack churn/retention/ARPU figures. Do not trust any blog citing a churn number for these companies.

### Weave Communications (NYSE: WEAV) — **the closest structural comparable**

Why it matters: communications/messaging/phone platform sold to **small** healthcare and service practices, **contractually month-to-month for the majority of customers**, ARPU ≈ **$503/mo** ($239.0M revenue ÷ 39,625 locations).

| FY | Locations | Net dollar retention | **Gross dollar retention** |
|---|---|---|---|
| 2022 | 27,193 | 99% | **94%** |
| 2023 | 31,002 | 95% | **92%** |
| 2024 | 34,997 | 98% | **91%** |
| 2025 | 39,625 | 93% | **89%** |

FY2025 gross dollar churn = **11%/yr ≈ 0.97%/mo**. Note the **monotonic four-year decay: 94 → 92 → 91 → 89**. Retention is getting worse as the base grows, not better.

Verbatim risk factor: *"We have historically experienced customer turnover as a result, in part, of our focus on the SMB market, where businesses are categorically more susceptible than larger businesses to general economic conditions, higher levels of churn, consolidation…"*

**Why Klantkraan cannot borrow Weave's 0.97%/mo.** Weave has, and Klantkraan has none of:
- **Physical hardware lock-in** — Weave ships VoIP desk phones on embedded leases ($6.8M lease revenue FY2025); cancelling means returning the phone system the practice answers calls on.
- **Deep PMS/EHR integration** — the platform is wired into the practice management system.
- **10+ years of brand**, a US-plus-India-plus-Philippines customer success org, and certifications.
- **A stable customer base** — US healthcare practices, not micro-contractors in a sector where closures tripled (§5).

Klantkraan is a chat widget plus a WhatsApp number. Switching cost ≈ zero. **Weave's 11%/yr is the realistic ceiling for a mature, sticky version of this product, not a base case for a new one.**
Source: https://www.sec.gov/Archives/edgar/data/1609151/000160915126000016/weav-20251231.htm (FY2025 10-K, filed 2026-03-05); FY2023 10-K: https://www.sec.gov/Archives/edgar/data/1609151/000160915124000021/weav-20231231.htm

### EverCommerce (NASDAQ: EVCM) — **the closest customer comparable**

Vertical SaaS for service SMBs. **745,000+ customers** as of 2025-12-31, EverPro vertical explicitly covers *"HVAC/plumbing, electrical professionals, remodeling and home improvement contractors, … landscaping design services … pest control"* — Klantkraan's exact verticals.

Decisive detail: **~93% of EverCommerce's customers contribute less than $2,000/year in revenue** (<$167/mo). This is a genuine micro-SMB book, and the closest public read on how micro-trades retain.

Annualized **net** revenue retention: **96%** (Q4 2025), **91%** (Q4 2024), **93%** (Q4 2023).

⚠️ Read this carefully: that is **net**, and EverCommerce's whole strategy is cross-sell — *"we have leveraged our land and expand strategy to cross sell solutions to our existing customers, which has supported our high net pro forma revenue retention rate."* Their calculation explicitly nets expansion against *"contraction and attrition."* **Gross** retention on a 745k micro-SMB book is therefore materially below 91–96% — the filing does not disclose it, and I will not invent it, but for a base that skews this small, gross logo churn in the high teens to twenties annually is the natural reading.

Also relevant: EverCommerce **acquired ZyraTalk on 2025-09-15** — an AI chat/text agent for home services. Klantkraan's category is being consolidated into incumbent suites that already own the customer relationship. That is a competitive fact with churn consequences.
Source: https://www.sec.gov/Archives/edgar/data/1853145/000185314526000010/evcm-20251231.htm (FY2025 10-K, filed 2026-03-12)

### ServiceTitan (NASDAQ: TTAN) — **do NOT use this benchmark**

Gross dollar retention **>95%** and NDR **>110%** for FY2024, FY2025, FY2026. This number circulates as "trades software retains at 95%+" and it is being misapplied.

Three disqualifiers, all verbatim from the filing:
1. **"We define SMBs in the context of our customer base as customers that have fewer than 1,000 employees."** ServiceTitan's "SMB" is up to 1,000 employees. Klantkraan's client has 1–10.
2. **"we primarily enter into either annual or multi-year subscription agreements with contract terms typically ranging from 12 to 36 months."** This is the exact lock-in Klantkraan has deliberately given up.
3. Active customer = **>$10,000 annualized billings**; revenue per active customer ≈ **$78K/yr**; accounts >$100K/yr are >50% of billings.

ServiceTitan is a 260x-higher-ACV product on multi-year contracts. Its retention says nothing about a €299/mo month-to-month tool. Its own risk factor concedes the direction of travel: *"Selling to and retaining SMBs can be more difficult than retaining large businesses, as SMBs often have higher rates of business failure and more limited resources."*
Source: https://www.sec.gov/Archives/edgar/data/1638826/000163882626000028/ttan-20260131.htm (FY2026 10-K, filed 2026-03-25)

### Typical client life, comparables

| Company | Structure | Gross annual churn | Implied life |
|---|---|---|---|
| ServiceTitan | 12–36mo contracts, $78k ACV | ~5% | ~20 yr (irrelevant) |
| Weave | month-to-month, ~$500/mo, hardware lock-in | 11% | ~103 mo |
| EverCommerce | micro-SMB, cross-sell | 4–9% *net* | gross materially shorter |
| **ChartMogul top quartile, $100–500 ARPA** | mixed | **~20–25%** | **~48–60 mo (top quartile)** |
| **Klantkraan (corrected, §6)** | month-to-month, no lock-in, new vendor | **38.7%** | **25 mo** |

---

## 3. Early-life churn — the first 90 days

**Honest answer: I could not obtain a citable published "% of month-to-month SMB clients that cancel in the first 3 months" statistic.** The pages that carry that kind of cohort data (Paddle/ProfitWell, Chargebee, Userpilot, Custify, Baremetrics Open Benchmarks) returned 404/410/blocked, and I will not attach a number to a source that does not say it.

**What is well-evidenced, and what it implies:**

The *existence* of a front-loaded churn curve is not in dispute — it is why cohort retention curves are convex and why ChartMogul, Baremetrics and Recurly all report retention as a decaying curve rather than a constant hazard. Churn is highest in months 1–3 and decays toward an asymptote as the surviving cohort self-selects for fit. A single blended "average monthly churn" number, which the plan uses, **systematically overstates early-cohort survival** for a company whose entire book is new cohorts.

This matters more for Klantkraan than for almost any other case, because **every client will be in months 1–3 during the period the plan covers.** A founder going from 0 to 20 clients has no mature cohort at all. The blended steady-state rate is the wrong rate to plan the first two years with.

**Klantkraan-specific mechanisms that concentrate risk in months 1–3** (reasoning, not citation):

1. **The value is contingent on inbound volume the client may not have.** This is the single largest risk in the whole plan. A 1–10 person Dutch loodgietersbedrijf may receive only a handful of web-chat/WhatsApp enquiries per month. If the AI handles 4 conversations in month 1, the client has paid €75 per conversation and will do that arithmetic. The product cannot create demand it only captures — and 85% of the addressable sector is one-person firms (§5) whose websites get very little traffic.
2. **No track record.** A first-time vendor gets no benefit of the doubt in month 2.
3. **The guarantee actively invites the month-1 exit** (§4).
4. **No switching cost.** Turning it off is removing a script tag and a WhatsApp forward.

**Modelled planning assumption (NOT sourced):** front-load the curve — **6–8%/month for months 1–3**, decaying to ~3%/month by month 12+. Blended over 24 months this lands at the ~4%/mo central case in §6. The founder should treat this as a hypothesis to **measure**, not a fact — see §8.

---

## 4. Does the guarantee + monthly cancel measurably increase churn?

I could not reach a controlled study isolating money-back guarantees. But the filings give a genuine **cross-company** quantification of the contract-structure half of the question, and one **within-company** signal.

**Cross-company (contract length):**

| | Contract structure | Gross dollar retention |
|---|---|---|
| ServiceTitan FY2026 | 12–36 month terms | **>95%** |
| Weave FY2025 | majority month-to-month | **89%** |

≈**6 percentage points** of annual gross retention. This is confounded by customer size (ServiceTitan's customers are vastly larger), so it is an upper bound on the contract effect, not a clean estimate.

**Within-company (Weave, the cleaner signal):** Weave discloses the share of customer locations electing annual prepayment:
- FY2024: **34%** annual prepay → GRR **91%**
- FY2025: **27%** annual prepay → GRR **89%**

A 7-point fall in the annually-prepaid share coincided with a 2-point fall in gross retention, in the same book, same product, same year. Directionally consistent, same order of magnitude. Weave also states it *"may offer pricing concessions"* to incentivise annual payment — a mature operator at this exact price point is paying real discount margin to move customers off month-to-month, which is itself evidence about the size of the effect.

**Quantified trade-off for Klantkraan:**

Best estimate: monthly-cancel costs roughly **5–8 percentage points of annual gross retention** versus a 12-month contract — i.e. ~30% churn instead of ~23%, or in monthly terms ~4.0% vs ~2.2–2.5%. In LTV terms that is the difference between **€7,228 and roughly €12,000–13,000** per client. **The no-lock-in differentiator is costing on the order of €5,000 of LTV per client.**

**The guarantee is a separate, additive cost.** A 30-day full refund means a month-1 canceller yields **zero revenue and a full CAC write-off** — strictly worse than an ordinary churner, who at least paid one month. Effective CAC becomes CAC/(1−g) where g is the refund rate:

| Month-1 refund rate | Effective CAC (nominal €400) | (nominal €800) |
|---|---|---|
| 5% | €421 | €842 |
| 10% | €444 | €889 |
| 15% | €471 | €941 |
| 20% | €500 | €1,000 |

**Is the trade-off worth it? Probably yes, but not for the reason stated.** No-lock-in is a genuine sales-conversion asset against 12-month competitors and it lowers the risk of the sale for a vendor with no track record — which is exactly Klantkraan's position. The error is not the policy; it is **modelling the policy's benefit (easier sales) without modelling its cost (higher churn).** The plan takes the conversion upside and then also assumes top-quartile retention. It cannot have both.

---

## 5. Dutch seasonality and sector stress — CBS primary data

Queried live today from the CBS OData API.

### Bouwvak is real and structural
Three **consecutive weeks**, staggered across regions **Noord / Midden / Zuid** to spread road congestion, ordering rotates annually, timed ~1–2 weeks after regional school summer holidays. No longer legally mandatory since 1981 but still governed by **CAO** and the advisory dates set by **Bouwend Nederland**; most construction firms still follow them.
Source: https://nl.wikipedia.org/wiki/Bouwvakvakantie — ⚠️ I could not verify the **exact 2026 dates** from an authoritative source (Bouwend Nederland's page did not carry them, bouwvakantie.nl is a parked domain). Founder should confirm dates directly with Bouwend Nederland.

**Churn implication:** during a client's 3-week shutdown, inbound enquiries are answered by an AI for a business that is closed. A client reviewing a €299 invoice in the month they were shut for three weeks is a live cancellation risk — and with a **30-day opzegtermijn**, the cancellation must be lodged *before* the quiet month to take effect. This creates a **pre-bouwvak cancellation window in June/early July**.

### Bankruptcy seasonality — SBI 43 *Gespecialiseerde bouw* (plumbers, electricians, roofers)
Monthly bankruptcies, 2022–2025 pooled (n=662), index 100 = average month:

| Month | Index | | Month | Index |
|---|---|---|---|---|
| Jan | 85 | | Jul | 109 |
| Feb | 96 | | Aug | 103 |
| **Mar** | **76** | | Sep | 100 |
| Apr | 109 | | **Oct** | **127** |
| May | 91 | | **Nov** | **123** |
| Jun | 94 | | Dec | 87 |

**Clear Q4 peak (Oct–Nov, index 123–127), trough in March (76).** Autumn is when Dutch trade businesses fail. Seasonality is real but moderate — a ±25% swing, not a cliff.
Source: CBS table 82244NED, https://opendata.cbs.nl/ODataApi/OData/82244NED/

### The sector is under real stress — this is the bigger finding
SBI 43 bankruptcies by year: **2022: 108 → 2023: 131 → 2024: 235 → 2025: 188** (2026 YTD Jan–Jul: 94). 2024 ran **2.2x** 2022.

Business **closures** (opheffingen, a far broader measure than bankruptcy) in SBI 43, CBS table 83149NED:

| Year | Total closures |
|---|---|
| 2021 | 3,695 |
| 2022 | 5,565 |
| 2023 | 5,895 |
| 2024 | 9,305 |
| **2025** | **10,395** |

**Closures have nearly tripled since 2021.**

### Involuntary churn floor
Against the stock of SBI 43 businesses at 2026 Q1 (CBS 81589NED — 143,395 total; 121,825 are one-person firms; only 18,735 are rechtspersonen):

- Closures among **2–10 employee** firms, 2025: 565 / 18,170 = **3.11%/yr**
- Closures among **rechtspersonen (BV)**, 2025: 940 / 18,735 = **5.02%/yr**

**→ Business-death alone is ~3–5%/yr ≈ 0.34%/mo of involuntary churn, before a single voluntary cancellation.** Add payment/SEPA failure (~0.2–0.4%/mo) and the involuntary floor is ~0.6–0.7%/mo. The plan's *entire* churn budget is 1.84%/mo — meaning it implicitly assumes voluntary churn of only ~1.2%/mo from micro-businesses with zero switching cost. That is not credible.

### Bonus finding relevant to the BV filter and TAM
Of 143,395 specialised-construction businesses, only **18,735 (13.1%) are rechtspersonen**, and **121,825 (85%) are one-person firms**. With the non-negotiable BV filter, the addressable pool inside SBI 43 is ~18.7k, not 143k. For the two core verticals: elektrotechnische bouwinstallatie (4321) 20,625 businesses / 3,880 BV; loodgieters en installatiebedrijven (4322) 18,230 / 3,755 BV.
Source: CBS 81589NED, 2026 Q1.

---

## 6. Corrected LTV and LTV/CAC

### Deriving the corrected rate

Bottom-up:
- Involuntary floor (business death + payment failure): **0.6–0.7%/mo**
- Voluntary: the dominant term. No hardware, no data lock-in, no integration moat, no track record, monthly cancel, 30-day refund, and value contingent on inbound volume the client may not have.

Top-down triangulation:
- ChartMogul $100–500 ARPA band, **top quartile** ≈ 20–25%/yr → median plausibly **35–45%/yr**
- Cobloom SMB-focused SaaS: **3–5%/mo** = 31–46%/yr
- Weave (mature, hardware-locked, stable customers) = 11%/yr — **the ceiling, not the case**

Both routes converge on **≈4%/month**.

### Corrected model

| | 3.0%/mo (optimistic) | **4.0%/mo (CENTRAL)** | 5.5%/mo (downside) |
|---|---|---|---|
| Annual churn | 30.6% | **38.7%** | 49.3% |
| **Avg client life** | 33 mo | **25 mo** | 18 mo |
| **LTV @96.7% GM** | €9,638 | **€7,228** | €5,257 |
| LTV @85% GM | €8,472 | €6,354 | €4,621 |
| **LTV/CAC @€400** | 24.1x | **18.1x** | 13.1x |
| LTV/CAC @€600 | 16.1x | 12.0x | 8.8x |
| **LTV/CAC @€800** | 12.0x | **9.0x** | 6.6x |
| CAC payback @€400 | 1.4 mo | 1.4 mo | 1.4 mo |
| CAC payback @€800 | 2.8 mo | 2.8 mo | 2.8 mo |

**Against the plan's claims:**
- "LTV €15,000" → **€7,228**, a **2.1x overstatement**.
- "LTV/CAC of 48–130x" → **18.1x at €400**. The 48–130x range implies CAC of €115–310 at the plan's own LTV; at corrected LTV it implies CAC of €56–150. Not achievable for a founder-sold €299/mo product.
- **"Even at fully-loaded CAC of €600, LTV/CAC stays 15x+"** → at corrected churn this is **12.0x**. The claim **fails**. (Note the plan's own arithmetic was conservative here: €15,000/€600 = 25x, not 15x.)

### The 96.7% gross margin is also too high
96.7% GM implies COGS of €9.87/client/month. That must cover Claude API inference, WhatsApp Business API conversation fees (CM.com), hosting, telephony, **and — critically — onboarding and support labour for a non-technical micro-business owner**. A serviced AI product sold to Dutch trades realistically runs **80–88% GM** once founder time on onboarding and support is costed at any non-zero rate. At 85% GM the central LTV is **€6,354**, and LTV/CAC at €800 is **7.9x**. Still viable — but the plan's LTV is overstated by churn and margin **compounding to ~2.4x**.

**Payback is the plan's genuine strength and it survives correction.** 1.4–2.8 months payback means churn cannot make this business insolvent — a client who stays 3 months is already profitable. The risk is not unit-economic. It is structural, and it is §7.

---

## 7. THE KEY QUESTION — the replacement treadmill

Gross new clients per month required **just to stay flat**:

| Client base | Plan (1.84%/mo) | **Corrected (4.0%/mo)** | Downside (5.5%/mo) |
|---|---|---|---|
| **10 clients** | 0.18/mo (2.2/yr) | **0.40/mo → 4.8/yr** | 0.55/mo (6.6/yr) |
| **20 clients** | 0.37/mo (4.4/yr) | **0.80/mo → 9.6/yr** | 1.10/mo (13.2/yr) |
| 50 clients | 0.92/mo (11/yr) | 2.00/mo (24/yr) | 2.75/mo (33/yr) |
| 100 clients | 1.84/mo (22/yr) | 4.00/mo (48/yr) | 5.50/mo (66/yr) |

**Direct answer: at 10 clients he must close ~0.4 new clients/month (about 1 every 2.5 months, ~5/year) just to stand still. At 20 clients, ~0.8/month (about 1 every 5 weeks, ~10/year).**

**At 10–20 clients this is NOT a treadmill.** One sale every 5–10 weeks to hold position is comfortably inside a solo founder's capacity. The plan's early phase is safe on this metric, and the founder should not panic about the corrected churn rate at this scale.

### Where it actually bites: the ceiling

The binding constraint is not replacement — it is the **steady-state ceiling N\* = (sales per month) ÷ (monthly churn)**. Every acquisition engine has a maximum sustainable book size, and churn sets it:

| Sales/month | c=3.0% | **c=4.0%** | c=5.5% | *Plan c=1.84%* |
|---|---|---|---|---|
| 1 | 33 | **25** | 18 | *54* |
| 2 | 67 | **50** | 36 | *109* |
| 3 | 100 | **75** | 55 | *163* |
| 4 | 133 | **100** | 73 | *217* |

In MRR:

| Sales/month | Ceiling MRR @4.0% churn | Ceiling MRR @plan 1.84% | Overstatement |
|---|---|---|---|
| 1 | €7,475/mo | €16,250/mo | **2.2x** |
| 2 | €14,950/mo | €32,500/mo | **2.2x** |
| 3 | €22,425/mo | €48,750/mo | **2.2x** |

**This is the real finding.** A solo founder sustainably closing **2 deals/month plateaus at 50 clients ≈ €14,950 MRR (~€179k ARR)** at corrected churn — not the 109 clients / €32,500 MRR the plan's churn rate implies. **The churn assumption error is a 2.2x error in the terminal size of the entire business**, and it is invisible in year 1 because at 10–20 clients the treadmill is trivially easy. The plan will look on-track for 18 months and then stop growing at roughly half the assumed ceiling.

Growth rate required to go **10 → 20 clients in 12 months**:

| | Sales/month needed |
|---|---|
| Plan (1.84%) | 1.11 |
| Optimistic (3.0%) | 1.28 |
| **Central (4.0%)** | **1.43** |
| Downside (5.5%) | 1.67 |

The near-term difference is small (1.11 vs 1.43/month). The long-term difference is the whole business.

---

## 8. What the founder should do

1. **Reset the base case to 4%/mo (25-month life, LTV €7,228).** Keep 1.84% as the *best-case* label it actually is, and 5.5% as downside. Delete the 12%/yr "best in class" scenario — nothing at this ARPA supports it.
2. **Stop quoting NRR-style benchmarks.** With one flat price and no expansion path, Klantkraan's NRR is capped at 100%. Either accept it or build an expansion vector (per-location, per-seat, usage tier, voice upsell) — that is the single highest-leverage change to LTV available, and it is a pricing decision, not a retention one.
3. **Qualify hard on inbound volume before selling.** The plan's biggest hidden churn driver is selling to trades with too little website traffic for the product to demonstrate value. Make measured monthly web/WhatsApp enquiry volume a **disqualification gate**, not a nice-to-have. This is the one intervention that most moves the corrected rate back toward 3%/mo. The existing `enrich.py` work (21/23 hit rate when handed a website) is the right tool for this.
4. **Instrument cohort churn from client #1.** Track month-1/2/3 survival by signup cohort, separately from blended churn. §3's front-loaded curve is a hypothesis; with 10–20 clients he can measure it within two quarters and should not plan on a blended constant.
5. **Track refund rate as a distinct metric from churn.** A 30-day refund is a full CAC write-off, not a churn event. Effective CAC = CAC/(1−refund rate).
6. **Keep month-to-month — but price the option.** Offer an optional 12-month prepay at a discount (Weave uses exactly this device and still buys only 27% adoption). Any client who takes it converts ~5–8 points of annual churn into cash up front, without losing the no-lock-in sales message for those who want it.
7. **Watch June/early July.** The 30-day opzegtermijn means bouwvak cancellations are lodged *before* the shutdown. Plan a proactive value-review touch in late May / early June.
8. **Do not cite ServiceTitan's >95% retention.** Their "SMB" is up to 1,000 employees on 12–36 month contracts at ~$78K/yr. If it appears anywhere in the plan or in investor/partner material, remove it.

---

## Sources

**SEC filings (primary):**
- ServiceTitan FY2026 10-K (filed 2026-03-25): https://www.sec.gov/Archives/edgar/data/1638826/000163882626000028/ttan-20260131.htm
- Weave Communications FY2025 10-K (filed 2026-03-05): https://www.sec.gov/Archives/edgar/data/1609151/000160915126000016/weav-20251231.htm
- Weave Communications FY2023 10-K (filed 2024-03-13): https://www.sec.gov/Archives/edgar/data/1609151/000160915124000021/weav-20231231.htm
- EverCommerce FY2025 10-K (filed 2026-03-12): https://www.sec.gov/Archives/edgar/data/1853145/000185314526000010/evcm-20251231.htm

**CBS Netherlands (primary, queried 2026-08-16):**
- Faillissementen; bedrijven, SBI 2008 (82244NED): https://opendata.cbs.nl/ODataApi/OData/82244NED/
- Bedrijven; opheffingen, bedrijfsgrootte, rechtsvorm, bedrijfstak (83149NED): https://opendata.cbs.nl/ODataApi/OData/83149NED/
- Bedrijven; bedrijfstak (81589NED): https://opendata.cbs.nl/ODataApi/OData/81589NED/

**Benchmarks:**
- ChartMogul SaaS Retention Report: https://chartmogul.com/reports/saas-retention-report/
- Cobloom, "Churn Rate: How High Is Too High?": https://www.cobloom.com/blog/churn-rate-how-high-is-too-high
- Vitally SaaS Churn Benchmarks (Baremetrics-derived; period unverified): https://www.vitally.io/post/saas-churn-benchmarks
- Recurly churn benchmarks (⚠️ period self-contradictory, excluded): https://www.recurly.com/research/churn-rate-benchmarks/

**Other:**
- Bouwvakvakantie: https://nl.wikipedia.org/wiki/Bouwvakvakantie
- Sacra profiles confirming Podium/Jobber publish no retention data: https://sacra.com/c/podium/ , https://sacra.com/c/jobber/
