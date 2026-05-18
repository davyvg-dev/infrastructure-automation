# MRR Projections — Bear / Base / Bull

> Month-by-month MRR with three scenarios. Used to set monthly targets and decide hiring triggers.

## Assumptions

- ARPU net: €540 (base), €432 (bear), €621 (bull)
- Monthly churn: 1.84% (base = 20% annual), 2.45% (bear = 26%), 1.06% (bull = 12%)
- New-clients pacing per month (see table below per scenario)
- New-client month is at 50%-off ARPU; subsequent months at full ARPU
- Annual prepay clients (15% of mix) get -15% list → blended drag ~5%

## Base case

Pacing: 2 → 3 → 3 → 5 → 5 → 5 → 6 → 7 → 7 → 8 → 8 → 8 new clients per month.

| Month | New | Churn | Active end | MRR (€) | ARR (€) |
|---|---|---|---|---|---|
| 1 | 2 (pilots) | 0 | 2 | 540 | 6,5k |
| 2 | 3 | 0 | 5 | 2,160 | 25,9k |
| 3 | 3 | 0 | 8 | 3,780 | 45,4k |
| 4 | 5 | 0 | 13 | 5,940 | 71,3k |
| 5 | 5 | 0 | 18 | 8,640 | 103,7k |
| 6 | 5 | 1 | 22 | **10,800** | 129,6k |
| 7 | 6 | 1 | 27 | 13,500 | 162,0k |
| 8 | 7 | 1 | 33 | 16,740 | 200,8k |
| 9 | 7 | 1 | 39 | **19,980** | 239,8k |
| 10 | 8 | 1 | 46 | 23,760 | 285,1k |
| 11 | 8 | 1 | 53 | 27,540 | 330,5k |
| 12 | 8 | 1 | 60 | **31,320** | **375,8k** |

**Base hits €10k MRR in month 6, €20k in month 9, €31k by month 12.**

## Bear case

Pacing: 1.5 → 2 → 2 → 3 → 4 → 4 → 4 → 5 → 5 → 5 → 5 → 5 new clients per month (75% of base) at €432 ARPU and 2.45% monthly churn.

| Month | New | Churn | Active end | MRR (€) |
|---|---|---|---|---|
| 1 | 2 | 0 | 2 | 432 |
| 3 | 2 | 0 | 6 | 2,160 |
| 6 | 4 | 1 | 16 | 6,300 |
| 9 | 5 | 1 | 25 | **9,720** |
| 12 | 5 | 1 | 30 | **13,000** |

Bear clears €10k MRR around month 9-11, €13k by month 12. **Goal hit even under pessimism.**

## Bull case

Pacing: 3 → 4 → 4 → 6 → 7 → 7 → 8 → 9 → 9 → 11 → 11 → 11 new clients per month (30% above base) at €621 ARPU and 1.06% monthly churn.

| Month | New | Churn | Active end | MRR (€) |
|---|---|---|---|---|
| 1 | 3 | 0 | 3 | 932 |
| 3 | 4 | 0 | 11 | 6,200 |
| 6 | 7 | 0 | 30 | **17,400** |
| 9 | 9 | 1 | 55 | **32,000** |
| 12 | 11 | 1 | 85 | **52,800** |

## Cash flow per month (base case, no founder draw months 1-4)

| Month | MRR | Cash in (95%) | Fixed burn | Cash out | Net | Cumulative |
|---|---|---|---|---|---|---|
| 1 | 540 | 513 | -950 | | -437 | -437 |
| 2 | 2,160 | 2,052 | -950 | | +1,102 | +665 |
| 3 | 3,780 | 3,591 | -1,350 (add €400 ads) | | +2,241 | +2,906 |
| 4 | 5,940 | 5,643 | -1,350 | | +4,293 | +7,199 |
| 5 | 8,640 | 8,208 | -1,350 -3,500 draw | -4,850 | +3,358 | +10,557 |
| 6 | 10,800 | 10,260 | -4,850 | | +5,410 | +15,967 |
| 12 | 31,320 | 29,754 | -4,850 -1,000 hires | -5,850 | +23,904 | ~€120k cumulative |

**Personal cash bridge needed: €1,000-1,500** to cover the month-1 deficit + buffer. Less than the €5-6k initially estimated because outbound starts mid-M2 (not full-blast from day 1).

## Worst-month cash dip

Bear case, no founder draw months 1-4: cumulative dip bottoms at roughly **-€3,800** end of M3 before turning positive. Add a €1,500 buffer for surprises → **€5-6k personal injection** is sufficient.

Bear case with founder draw from M5: cumulative dip bottoms at ~**-€8-10k** end of M5 before recovering. If founder needs full draw from M1 → bridge funding needs to cover M1-M5 = ~€15k.

## Trigger thresholds

| Threshold | Action |
|---|---|
| €1,000 MRR (M2) | Cover infra burn; safe to scale outbound |
| €4,700 MRR (M4-5) | Cover founder draw; consider Google Ads test |
| €10,000 MRR (M6 base) | **Goal hit**. Trigger VA hire (€600/mo). |
| €15,000 MRR (M8) | Trigger SDR hire decision (€1,500-2,000/mo). |
| €20,000 MRR (M9 base) | Stretch goal hit. Consider second vertical (hoveniers / elektriciens). |
| €25,000 MRR (M11) | Trigger part-time engineer decision. |

## What can push base → bull?

1. Mix shift Lite → Pro → Max (vertical packages): +8% ARPU.
2. Partnership channel firing (accountant referrals): +2-3 clients/mo at near-zero CAC.
3. Google Ads scaled (€400 → €1,500/mo): +2-3 clients/mo at proven payback.
4. Second vertical (hoveniers / elektriciens) launched M6: doubles addressable pipeline.
5. SDR hire M7: roughly doubles outbound throughput.

## What can push base → bear?

1. Cold-email deliverability collapse (Google suspension) — recovery 4-6 weeks
2. Synthflow Dutch quality issues → trust hit + churn spike
3. EU AI Act enforcement (Aug 2026) creates buyer anxiety → cycle stretches
4. Recession / sector slowdown for trades (low likelihood)
5. Founder hits delivery wall earlier than month 6 (high likelihood without VA)

## Source

- Base/bear/bull modelling: assumptions derived from research in `02-sales/funnel-benchmarks.md` and `07-finance/unit-economics.md`
- B2B SaaS churn benchmarks (Vanta): https://vantainsights.com/insights/saas-churn-rate
- SMB SaaS growth rate benchmarks: https://www.bvp.com/atlas/state-of-the-cloud-2024
