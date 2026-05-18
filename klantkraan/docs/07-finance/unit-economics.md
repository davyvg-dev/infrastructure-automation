# Unit Economics

> **Headline**: 95% gross margin, <1 month payback, LTV/CAC > 30× even in pessimistic scenarios. The constraint is not economics — it's distribution and founder throughput.

## ARPU (blended)

Mix assumption: 30% Lite / 55% Pro / 15% Max.

| Tier | List price | Annual-prepay drag (-15% on 15% of mix) | Net ARPU |
|---|---|---|---|
| Lite | €299 | – | €299 |
| Pro | €599 | – | €599 |
| Max | €999 | – | €999 |
| **Blended (list)** | **€569** | | |
| **Blended (net)** | | ~5% prepay drag | **~€540** |

## COGS per tier

| Cost item | Lite | Pro | Max |
|---|---|---|---|
| CM.com SMS (~50/mo @ €0.08) | €4 | €4 | €4 |
| CM.com Dutch local number | €1 | €1 | €1 |
| Synthflow voice (~150 min Pro, ~350 min Max × €0.12) | – | €18 | €42 |
| Claude API (receptionist + reports) | – | €4 | €5 |
| Attio contact slot | ~€0 | ~€0 | ~€0 |
| Hetzner amortised per client | €0.50 | €0.50 | €0.50 |
| Cloudflare R2 storage amortised | €0.10 | €0.30 | €0.50 |
| Misc + buffer | €0.40 | €2.20 | €2.00 |
| **Total COGS** | **€6** | **€30** | **€55** |
| **Gross margin** | **98.0%** | **95.0%** | **94.5%** |
| **Blended GM** | | | **95.1%** |

Overage voice minutes (>200 Pro / >500 Max) billed at €0.50/min with ~€0.12 cost → 76% margin on overage. Bonus.

## CAC by channel

Volume math based on 2026 benchmarks (Apollo, Smartlead, Cleverly, HeyReach):

| Channel | Funnel | Output | Direct $ cost | CAC (cash) | CAC (fully loaded) |
|---|---|---|---|---|---|
| Cold email (5,300/mo, 0.10-0.15% send→client) | 5-8 clients/mo | €146 outbound stack | €18-29 | ~€450 (50% founder time tagged) |
| LinkedIn (600 invites/mo, 35%→6%→25%→25%) | ~3 clients/mo | €170 (HeyReach + Sales Nav) | €57 | ~€250 |
| Organic content (LinkedIn personal + SEO) | grows to 3/mo by M6 | €162 content tools | €50-140 | very low at scale |
| Google Ads "AI telefoniste loodgieter" (CPC €2.50-4.50, CVR 6%) | 2-4 clients @ €400/mo | €400 | €100-200 | similar |
| Partnerships (10% rev-share Y1) | grows to 1-3/mo by M6 | rev-share only | ~€60 effective | ~€60 |

**Blended target CAC**: €150-250 cash, ~€400 fully loaded.

## LTV

LTV = ARPU × GM% ÷ monthly churn.

| Churn scenario | Annual | Monthly | Avg life | LTV (net) |
|---|---|---|---|---|
| High | 30% | 2.9% | 34 mo | **€17,750** |
| Realistic | 20% | 1.84% | 54 mo | **€27,900** |
| Best-in-class | 12% | 1.06% | 94 mo | **€48,200** |

## LTV / CAC

| Scenario | LTV | CAC (cash €200) | Ratio |
|---|---|---|---|
| High churn | 17,750 | 200 | **89×** |
| Realistic | 27,900 | 200 | **140×** |
| Best | 48,200 | 200 | **241×** |

Even at fully-loaded CAC of €600, LTV/CAC stays 30×+. Industry "healthy" benchmark is 3-5×.

## Payback period

`Payback = CAC / (ARPU × GM%)`

- CAC €200 / €513 contribution = **<1 month**
- Even at fully-loaded CAC €600 → **~1.2 months**
- Industry SMB SaaS benchmark: 9-12 months

The reason is structural: high price relative to channel cost. Klantkraan isn't a $20/mo product fighting on PPC — it's a €540/mo product where one demo can be closed in 14 days.

## Fixed monthly overhead (ex founder draw)

| Item | Cost |
|---|---|
| Infra + tools baseline | €51 |
| Outbound stack (KvK + Outscraper + Google Workspace + Smartlead + verifier) | €146 |
| Content stack (Claude API + Buffer + Canva + ElevenLabs + Loom + Descript + Perplexity + Plausible + Buttondown) | €140 |
| Bookkeeping (Moneybird) | €12 |
| Insurance amortised (€1,200-2,000/yr stack) | €100-170 |
| Misc | €10 |
| **Total fixed (ex-salary)** | **~€450-500/mo** |
| + ad budget (Google Ads from M3) | +€400 |
| **Total cash burn pre-revenue** | **~€900-1,000/mo** |

Breakeven on burn: MRR × 95% > €950 → ~€1,000 MRR (month 2 in base case).

Breakeven incl. €3,500 founder draw: ~€4,700 MRR → month 4-5 in base case.

## Why this works as a business (vs. consulting)

| Option | Year 1 take-home | Asset value at year-end |
|---|---|---|
| Contract work at €85/hr × 12.5h/wk | ~€55k | €0 |
| Klantkraan base case | ~€60-80k after founder draw (M5 on) | ~€280k-550k EV (2-4× ARR) |
| Klantkraan risk-adjusted EV (60% base / 25% bear / 15% bull) | | **~€290k EV + €60k take-home** |

Expected value of building > expected value of contracting, unless founder discounts very heavily for execution risk.

## Key sensitivities

| Input | Base | Sensitivity test | Effect on M12 MRR |
|---|---|---|---|
| ARPU | €540 | -20% (€432) | Bear case |
| Annual churn | 20% | +30% (26%) | Bear case |
| CAC | €200 | +50% (€300) | Bear case |
| New clients / month profile | 2→3→5→7→8 | -25% | Bear case |
| (Combined Bear) | | | **€13.0k** |
| (Base) | | | **€31.3k** |
| (Combined Bull: +15% ARPU, -40% churn, -30% CAC) | | | **€52.8k** |

Even the bear case clears the €10k MRR target by ~month 9-11.

## Source

- B2B SaaS CAC benchmarks (Prospeo): https://prospeo.io/s/b2b-saas-cac
- LTV benchmarks (Optifai 939-company sample): https://optif.ai/learn/questions/b2b-saas-ltv-benchmark/
- Churn benchmarks (Vanta): https://vantainsights.com/insights/saas-churn-rate
- Google Ads CPC/CVR 2026: https://www.digitalapplied.com/blog/google-ads-benchmarks-2026-cpc-ctr-cvr-industry
- LTV/CAC ratio benchmarks: https://www.saashero.net/strategy/b2b-saas-ltv-cac-benchmarks/
