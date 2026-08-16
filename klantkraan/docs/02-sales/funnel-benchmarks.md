# Funnel Conversion Benchmarks

> 2025–2026 NL B2B SMB SaaS benchmarks (Apollo, Smartlead, Cleverly, Belkins, Optifai, Instantly). Use these as the line that pipeline performance must clear. Anything below is a signal to investigate.

## Cold email (Smartlead, 9 inboxes, ~225/day)

| Stage                                          | EU/NL benchmark | Klantkraan target | Notes                                  |
| ---------------------------------------------- | --------------- | ----------------- | -------------------------------------- |
| Inbox placement (after warm-up)                | 85–95%          | 95%               | DMARC p=reject + .nl secondary domains |
| Open rate (privacy-protected so this is noisy) | 25–50%          | n/a (noisy)       | Don't optimise for opens               |
| Reply rate                                     | 5–6%            | 7%                | Reply rate is the real signal          |
| Positive reply                                 | 1–2%            | 1.5%              | Demo-booked next step                  |
| Demo booked                                    | 0.8–1.2%        | 1%                | Of total sends                         |
| Sequence completion (4 touches)                | 100%            | 100%              | Always finish the sequence             |

**Math**: 4,500 sends/mo → 315 replies → 67 positive → 45 demos booked. At 30% close = 13 deals/mo from cold email alone (if all 4 touches deliver).

## LinkedIn (HeyReach, 1 seat)

| Stage                         | Benchmark           | Klantkraan target                   |
| ----------------------------- | ------------------- | ----------------------------------- |
| Connection request acceptance | 26–30%              | 35% (niche-specific + warm content) |
| Reply on T2 (post-acceptance) | 10–15%              | 15%                                 |
| Demo booked                   | 2–4% of connections | 3%                                  |

**Math**: 300 connection requests/wk → 90 accept/wk → 14 reply/wk → 3 demos/wk = ~12 demos/mo.

## Inbound (LP form / DM)

| Stage                                                          | Benchmark  | Klantkraan target            |
| -------------------------------------------------------------- | ---------- | ---------------------------- |
| LP visit → form submit                                         | 2–4%       | 3%                           |
| Form → demo booked (with auto-reply + manual ≤15 min response) | 35–50%     | 45%                          |
| Demo show rate                                                 | 70–80%     | 80% (WhatsApp T-2h reminder) |
| Demo → won                                                     | 20–30% SMB | 30%                          |

**End-to-end**: site visit → won = ~0.4%. Means 5,000 monthly visits = ~20 deals. SEO + content + Google Ads driving 2,000-3,000 monthly visits is realistic by month 6.

## Discovery / demo

| Stage                          | Benchmark        | Klantkraan target | Lever                                                    |
| ------------------------------ | ---------------- | ----------------- | -------------------------------------------------------- |
| Show rate                      | 70–80%           | 80%               | WhatsApp T-2h + same-day Cal.com confirm                 |
| Discovery → Proposal Sent      | 75%              | 80%               | Tight qualification before booking                       |
| Proposal → Won                 | 25–35%           | 35%               | 1-page offerte + risk reversal (refund + monthly cancel) |
| Average sales cycle (< €1k/mo) | 7–21 days NL B2B | 14 days           | <14d if owner is sole DM                                 |

## Speed-to-lead

- Reply <5 min: 32% close (best-in-class)
- Reply 5–15 min: 28%
- Reply 15–60 min: 18%
- Reply 1–4 hr: 13%
- Reply >24 hr: 8% (and below)

**Implication**: WhatsApp Business + n8n auto-reply + Slack ping is non-optional from day 1.

## Funnel waterfall (combined, monthly steady-state by M3)

Inputs:

- Cold email: 4,500 sends/mo
- LinkedIn: 1,200 connection requests/mo (300/wk)
- Inbound: ~1,500 visits/mo (M3 starting baseline)

Outputs:

| Source          | Demos booked / mo | Demos shown | Closed |
| --------------- | ----------------- | ----------- | ------ |
| Cold email      | 45                | 36          | 11     |
| LinkedIn        | 12                | 10          | 3      |
| Inbound         | 8                 | 6           | 2      |
| Referrals (M3+) | 2                 | 2           | 1      |
| **Total**       | **67**            | **54**      | **17** |

That's 17 deals/month at M3 steady-state — well above the model's required 5/month for €10k MRR at M6.

## When to suspect each metric is off

| Metric below              | What's likely wrong                                         |
| ------------------------- | ----------------------------------------------------------- |
| Open rate < 25%           | Subject lines or warm-up insufficient                       |
| Reply rate < 4%           | Hook is wrong; offer/audience mismatch                      |
| Positive reply < 1%       | Message is too pitchy or audience too cold                  |
| LinkedIn acceptance < 18% | Profile or targeting is off                                 |
| Demo show < 65%           | Reminder cadence; Cal.com confirmation flow                 |
| Demo → won < 18%          | Sales script weak, pricing presentation, demo not impactful |
| Inbound form → demo < 30% | Auto-reply slow, page not building trust                    |

## Weekly KPI review (full doc `10-ops/weekly-kpi-review.md`)

Every Friday 16:00, check:

1. Sends, replies, positive replies (and their delta vs. last week)
2. Demos booked, shown, won
3. Conversion by stage vs. benchmarks above
4. Cycle time (median)
5. Top objection that came up

## Sources

- Apollo Outbound Reply Rate 2026: https://www.apollo.io/insights/whats-the-expected-reply-rate-for-a-well-run-outbound-cold-email-campaign
- Smartlead Open Rate Benchmarks: https://www.smartlead.ai/blog/cold-email-open-rates
- Instantly Cold Email Benchmark Report 2026: https://instantly.ai/cold-email-benchmark-report-2026
- Cleverly LinkedIn Benchmarks: https://www.cleverly.co/blog/linkedin-benchmarks
- Belkins LinkedIn Outreach Study: https://belkins.io/blog/linkedin-outreach-study
- Optifai (B2B SaaS, 939 companies): https://optif.ai/learn/
- LeanData Speed-to-Lead: https://www.leandata.com/blog/speed-to-lead-speed-is-the-key-to-lead-conversion/
- Digital Bloom 2025 NL/EU benchmarks: https://thedigitalbloom.com/learn/cold-outbound-reply-rate-benchmarks/
