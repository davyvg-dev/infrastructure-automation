# MRR Projections — Bear / Base / Bull

> Herzien 2026-07-13 — recomputed for the two-tier text-first pricing (€299 Chat / €499 Compleet). Voice is not yet live, so base and bear assume **Chat-only ARPU**; Compleet upsell appears only in bull. Month-by-month MRR with three scenarios. Used to set monthly targets and decide hiring triggers.

## Assumptions

- ARPU: €299 Chat-only (base), €228 net (bear, -20% + prepay drag), ~€341 net (bull, 70/30 Chat/Compleet mix once voice ships)
- Monthly churn: 1.84% (base = 20% annual), 2.45% (bear = 26%), 1.06% (bull = 12%)
- New-client month at 50%-off (€149.50); subsequent months at full rate
- Setup fee €249 per non-pilot new client = one-off cash, excluded from MRR
- Client pacing unchanged from the pre-repricing model

## Base case (Chat-only, €299)

Pacing: 2 → 3 → 3 → 5 → 5 → 5 → 6 → 7 → 7 → 8 → 8 → 8 new clients per month.

| Month | New | Churn | Active end | MRR (€) | ARR (€) |
|---|---|---|---|---|---|
| 1 | 2 (pilots) | 0 | 2 | 300 | 3,6k |
| 2 | 3 | 0 | 5 | 1,046 | 12,6k |
| 3 | 3 | 0 | 8 | 1,944 | 23,3k |
| 4 | 5 | 0 | 13 | 3,140 | 37,7k |
| 5 | 5 | 0 | 18 | 4,635 | 55,6k |
| 6 | 5 | 1 | 22 | 5,831 | 70,0k |
| 7 | 6 | 1 | 27 | 7,176 | 86,1k |
| 8 | 7 | 1 | 33 | 8,821 | 105,9k |
| 9 | 7 | 1 | 39 | **10,615** | 127,4k |
| 10 | 8 | 1 | 46 | 12,558 | 150,7k |
| 11 | 8 | 1 | 53 | 14,651 | 175,8k |
| 12 | 8 | 1 | 60 | **16,744** | **200,9k** |

**Base hits €10k MRR in month 9, ~€16.7k by month 12.** Every 30% of the book upgraded to Compleet adds ~€200 × those clients (e.g. +€3.6k at M12) — tracked as upside, not plan.

## Bear case

75% of base pacing at €228 net ARPU and 2.45% monthly churn.

| Month | Active end | MRR (€) |
|---|---|---|
| 1 | 2 | ~230 |
| 3 | 6 | ~1,150 |
| 6 | 16 | ~3,300 |
| 9 | 25 | **~5,100** |
| 12 | 30 | **~6,900** |

**Bear does NOT clear €10k MRR in year 1 at Chat-only pricing.** This is the honest cost of the lower price point; mitigations are the Compleet upsell and pacing above plan.

## Bull case

30% above base pacing at ~€341 net blended ARPU (voice live from ~M6, 30% Compleet mix) and 1.06% monthly churn.

| Month | Active end | MRR (€) |
|---|---|---|
| 1 | 3 | ~500 |
| 3 | 11 | ~3,100 |
| 6 | 30 | **~9,500** |
| 9 | 55 | **~18,000** |
| 12 | 85 | **~28,500** |

## Cash flow per month (base case, no founder draw months 1-5)

| Month | MRR | Cash in (97%) | Fixed burn | Net | Cumulative |
|---|---|---|---|---|---|
| 1 | 300 | 291 | -950 | -659 | -659 |
| 2 | 1,046 | 1,015 | -950 | +65 | -594 |
| 3 | 1,944 | 1,886 | -1,350 (add €400 ads) | +536 | -58 |
| 4 | 3,140 | 3,046 | -1,350 | +1,696 | +1,638 |
| 5 | 4,635 | 4,496 | -1,350 | +3,146 | +4,784 |
| 6 | 5,831 | 5,656 | -4,850 (draw €3,500 starts) | +806 | +5,590 |
| 12 | 16,744 | 16,242 | -5,850 (incl. VA) | +10,392 | ~€50k cumulative |

Setup fees (€249 × non-pilot signings, ~60 in year 1) add ~€14k one-off cash on top of this table.

**Personal cash bridge needed: ~€1,500-2,000** for the month 1-3 dip in base case. Founder draw moves from M5 to **M6** vs the old model.

## Worst-month cash dip

Bear case, no founder draw: cumulative dip bottoms around **-€4,500 to -€5,500** mid-year before slowly recovering. Keep the **€5-6k personal injection** recommendation. If founder needs full draw from M1, bear-case bridge is ~€20k+ — don't.

## Trigger thresholds

| Threshold | Action |
|---|---|
| €1,000 MRR (M2) | Cover infra burn; safe to scale outbound |
| €4,700 MRR (M5-6) | Cover founder draw; consider Google Ads test |
| €10,000 MRR (M9 base) | **Goal hit**. Trigger VA hire (€600/mo). |
| €15,000 MRR (M11) | Trigger SDR hire decision (€1,500-2,000/mo). |
| €20,000 MRR (M12+ with Compleet mix) | Stretch goal. Consider second vertical (hoveniers / elektriciens). |

## What can push base → bull?

1. **Compleet (voice) live + 30% upsell mix: +€200 per upgraded client — the single biggest lever.**
2. Partnership channel firing (accountant referrals): +2-3 clients/mo at near-zero CAC.
3. Google Ads scaled (€400 → €1,500/mo): +2-3 clients/mo at proven payback.
4. Second vertical (hoveniers / elektriciens) launched M6: doubles addressable pipeline.
5. SDR hire M7: roughly doubles outbound throughput.

## What can push base → bear?

1. Cold-email deliverability collapse (Google suspension) — recovery 4-6 weeks
2. Chat quality issues (wrong answers, missed bookings) → trust hit + churn spike
3. EU AI Act enforcement (Aug 2026) creates buyer anxiety → cycle stretches
4. Recession / sector slowdown for trades (low likelihood)
5. Founder hits delivery wall earlier than month 6 (high likelihood without VA)

## Source

- Base/bear/bull modelling: assumptions derived from research in `02-sales/funnel-benchmarks.md` and `07-finance/unit-economics.md`
- B2B SaaS churn benchmarks (Vanta): https://vantainsights.com/insights/saas-churn-rate
- SMB SaaS growth rate benchmarks: https://www.bvp.com/atlas/state-of-the-cloud-2024
