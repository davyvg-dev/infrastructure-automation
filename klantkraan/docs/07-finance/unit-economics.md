# Unit Economics

> Herzien 2026-07-13 for the two-tier text-first pricing (€299 Chat / €499 Compleet, €249 setup waived for pilots). **Headline**: ~97% gross margin on Chat, <1 month payback, LTV/CAC > 40× even in pessimistic scenarios. The constraint is not economics — it's distribution and founder throughput.

## ARPU

Voice (Compleet) is not yet live, so the planning ARPU is **Chat-only €299**. Once voice ships, target mix 70% Chat / 30% Compleet.

| Scenario                    | List ARPU | Net ARPU (~5% prepay drag) |
| --------------------------- | --------- | -------------------------- |
| Today (100% Chat)           | €299      | **~€285**                  |
| Once voice live (70/30 mix) | €359      | ~€341                      |

Setup fee €249 (one-time, waived for pilots) is cash on top, not ARPU.

## COGS per tier

Conservative estimates, pending real usage data — see `07-finance/cogs-per-tier.md` for line items.

| Tier                             | List | COGS    | GM%       |
| -------------------------------- | ---- | ------- | --------- |
| Chat                             | €299 | ~€10    | **96.7%** |
| Compleet (provisional)           | €499 | ~€35    | **93.0%** |
| Blended (70/30, once voice live) | €359 | ~€17.50 | **95.1%** |

Text is the structural win: a Claude API chat conversation costs cents; voice minutes (TTS/STT/telephony) were the dominant COGS line of the old model.

## CAC by channel

Volume math based on 2026 benchmarks (Apollo, Smartlead, Cleverly, HeyReach):

| Channel                                                          | Funnel                | Output                      | Direct $ cost  | CAC (cash)                      | CAC (fully loaded) |
| ---------------------------------------------------------------- | --------------------- | --------------------------- | -------------- | ------------------------------- | ------------------ |
| Cold email (5,300/mo, 0.10-0.15% send→client)                    | 5-8 clients/mo        | €146 outbound stack         | €18-29         | ~€450 (50% founder time tagged) |
| LinkedIn (600 invites/mo, 35%→6%→25%→25%)                        | ~3 clients/mo         | €170 (HeyReach + Sales Nav) | €57            | ~€250                           |
| Organic content (LinkedIn personal + SEO)                        | grows to 3/mo by M6   | €162 content tools          | €50-140        | very low at scale               |
| Google Ads "AI receptionist loodgieter" (CPC €2.50-4.50, CVR 6%) | 2-4 clients @ €400/mo | €400                        | €100-200       | similar                         |
| Partnerships (10% rev-share Y1)                                  | grows to 1-3/mo by M6 | rev-share only              | ~€60 effective | ~€60                            |

**Blended target CAC**: €150-250 cash, ~€400 fully loaded.

## LTV

LTV = net ARPU × GM% ÷ monthly churn. At Chat-only net ARPU €285, GM 96.7%:

| Churn scenario | Annual | Monthly | Avg life | LTV (net)   |
| -------------- | ------ | ------- | -------- | ----------- |
| High           | 30%    | 2.9%    | 34 mo    | **€9,500**  |
| Realistic      | 20%    | 1.84%   | 54 mo    | **€15,000** |
| Best-in-class  | 12%    | 1.06%   | 94 mo    | **€26,000** |

Compleet upsell raises each of these ~20% at the 70/30 mix.

## LTV / CAC

| Scenario   | LTV    | CAC (cash €200) | Ratio    |
| ---------- | ------ | --------------- | -------- |
| High churn | 9,500  | 200             | **48×**  |
| Realistic  | 15,000 | 200             | **75×**  |
| Best       | 26,000 | 200             | **130×** |

Even at fully-loaded CAC of €600, LTV/CAC stays 15×+. Industry "healthy" benchmark is 3-5×.

## Payback period

`Payback = CAC / (net ARPU × GM%)` → contribution ≈ €275/mo (Chat).

- CAC €200 / €275 contribution = **<1 month**
- Fully-loaded CAC €600 → **~2.2 months**
- Industry SMB SaaS benchmark: 9-12 months

The reason is structural: high price relative to channel cost. Klantkraan isn't a $20/mo product fighting on PPC — it's a €299/mo product where one demo can be closed in 14 days. The €249 setup fee (non-pilot clients) additionally covers most of cash CAC in month 0.

## Fixed monthly overhead (ex founder draw)

| Item                                                                                                             | Cost               |
| ---------------------------------------------------------------------------------------------------------------- | ------------------ |
| Infra + tools baseline                                                                                           | €51                |
| Outbound stack (KvK + Outscraper + Google Workspace + Smartlead + verifier)                                      | €146               |
| Content stack (Claude API + Buffer + Canva + ElevenLabs + Loom + Descript + Perplexity + Plausible + Buttondown) | €140               |
| Bookkeeping (Moneybird)                                                                                          | €12                |
| Insurance amortised (€1,200-2,000/yr stack)                                                                      | €100-170           |
| Misc                                                                                                             | €10                |
| **Total fixed (ex-salary)**                                                                                      | **~€450-500/mo**   |
| + ad budget (Google Ads from M3)                                                                                 | +€400              |
| **Total cash burn pre-revenue**                                                                                  | **~€900-1,000/mo** |

Breakeven on burn: MRR × 97% > €950 → ~€1,000 MRR (month 2-3 in the repriced base case).

Breakeven incl. €3,500 founder draw: ~€4,700 MRR → month 5-6 in the repriced base case.

## Why this works as a business (vs. consulting)

| Option                                                      | Year 1 take-home                    | Asset value at year-end                         |
| ----------------------------------------------------------- | ----------------------------------- | ----------------------------------------------- |
| Contract work at €85/hr × 12.5h/wk                          | ~€55k                               | €0                                              |
| Klantkraan repriced base case (~€16.7k MRR M12 ≈ €200k ARR) | ~€35-55k after founder draw (M6 on) | ~€150k-400k EV (2-4× ARR excl. Compleet upside) |

Expected value of building > expected value of contracting, unless founder discounts very heavily for execution risk. The old €540-ARPU EV table overstated both; this is the honest repriced version.

## Key sensitivities

| Input                                              | Base      | Sensitivity test | Effect on M12 MRR |
| -------------------------------------------------- | --------- | ---------------- | ----------------- |
| ARPU (net)                                         | €285      | -20% (€228)      | Bear case         |
| Annual churn                                       | 20%       | +30% (26%)       | Bear case         |
| CAC                                                | €200      | +50% (€300)      | Bear case         |
| New clients / month profile                        | 2→3→5→7→8 | -25%             | Bear case         |
| (Combined Bear)                                    |           |                  | **~€7k**          |
| (Base, Chat-only)                                  |           |                  | **~€16.7k**       |
| (Bull: +30% pacing, -40% churn, +30% Compleet mix) |           |                  | **~€28k**         |

At Chat-only pricing the **bear case no longer clears €10k MRR within year 1** — the base case clears it around month 9. The lever that restores headroom is the Compleet upsell (+€200/client) once voice is live.

## Source

- B2B SaaS CAC benchmarks (Prospeo): https://prospeo.io/s/b2b-saas-cac
- LTV benchmarks (Optifai 939-company sample): https://optif.ai/learn/questions/b2b-saas-ltv-benchmark/
- Churn benchmarks (Vanta): https://vantainsights.com/insights/saas-churn-rate
- Google Ads CPC/CVR 2026: https://www.digitalapplied.com/blog/google-ads-benchmarks-2026-cpc-ctr-cvr-industry
- LTV/CAC ratio benchmarks: https://www.saashero.net/strategy/b2b-saas-ltv-cac-benchmarks/
