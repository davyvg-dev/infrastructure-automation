# Weekly KPI Review

> Friday 16:00–16:45 CEST, 45-minute hard timebox, founder-owned (VA-shadowed from M6). Twelve KPIs across sales, activation, revenue, retention, unit economics, delivery quality and compliance. The output is one Notion page per ISO week (`kpi-{ISO-week}`), one root-caused number, one action assigned to one owner with one deadline. Trajectory deltas vs. `00-MASTER-PLAN.md § 3` are pushed back into the master plan when they diverge materially. Dashboard automation lands in M3; until then the table is hand-typed from Attio, Smartlead, Mollie and Postgres.

## 1. Why a weekly review

A weekly cadence is the smallest interval that catches a metric two consecutive weeks before damage compounds (cold-email deliverability, churn, MRR vs. plan). Without it, the founder optimises whichever number is loudest that day. The review is also the write-ahead log against silent drift in the master plan — anything off by >20% for two weeks forces an edit to `00-MASTER-PLAN.md § 3`. Owner is the founder through M5; the VA shadows from M6 and runs the data-pull half from M7 (master plan § 4, VA-hire trigger at 12 active clients).

## 2. Cadence and format

| Aspect | Decision |
|---|---|
| Day / time | Friday 16:00–16:45 CEST |
| Duration | 45 minutes, hard stop |
| Owner | Founder M1–M5; founder + VA M6+ (VA pulls data, founder decides) |
| Output | One Notion page per ISO week titled `kpi-{ISO-week}` (e.g. `kpi-2026-W21`) |
| Source of numbers M1–M2 | Manual: Attio reports, Smartlead dashboard, Mollie dashboard, n8n Postgres views via `psql` |
| Source of numbers M3+ | Automated: n8n nightly cron → Postgres `events` views → Astro `/r/internal` page (`08-tech/observability.md § Layer 3`) |
| Notion template | One row per KPI, columns: value, target, RAG, delta vs. last week, notes |
| Distribution | Page link pasted into Slack `#weekly-review` thread; archived in Notion KPI database |

The 45-minute timebox is non-negotiable. Reviews that run >60 min become postmortems and lose decisiveness.

## 3. The twelve KPIs that matter

Colour bands: green = at/above target, amber = within 20% below target, red = >20% below target or any compliance breach. Trigger threshold is the value that forces an action this week, not "soon".

| # | Domain | KPI | Definition | M1 | M3 | M6 | M9 | Source | Trigger threshold |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Sales | Cold-email reply rate | (replies ÷ delivered) over last 7 days | n/a (warm-up) | >5% | >5% | >5% | Smartlead | <4% two weeks running → audit hook/inbox health |
| 2 | Sales | Discoveries booked / week | New `discovery_booked` events in Attio, last 7 days | 0–1 | 4–6 | 8–12 | 12–16 | Attio | <60% of band for 2 weeks → escalate outbound volume or channel |
| 3 | Sales | Win rate (discovery → won) | won ÷ discoveries shown over trailing 30 days | n/a | >25% | >25% | >30% | Attio | <20% for 2 weeks → script + offerte audit |
| 4 | Sales | Sales cycle (days) | Median days from `discovery_booked` to `won`, last 30 days | n/a | <14 | <14 | <12 | Attio | >18 → tighten qualification + offerte same-day |
| 5 | Activation | Pilots / clients live | Count of clients with status `live` (calls routed) | 2 | 8 | 22 | 39 | Postgres `clients` | Below master plan § 3 by 2 → see escalation table |
| 6 | Activation | Time-to-go-live | Median days from `won` to `live`, trailing 30 | n/a | <30 | <30 | <21 | Postgres `clients` | >35 → onboarding bottleneck, productize further |
| 7 | Activation | First-week call volume | Mean inbound calls per client in days 1–7 after `live` | n/a | >15 | >15 | >20 | Synthflow + CM.com logs | <8 → forwarding misconfigured, audit each new client |
| 8 | Revenue | MRR (€) | Sum of active recurring subscriptions, net of prepay drag | 300 | 1,940 | 5,830 | 10,600 | Mollie + Postgres `subscriptions` | <80% of plan 2 weeks → emergency reposition (see § 5). Targets herzien 2026-07-13 (€299 Chat-only ARPU). |
| 9 | Retention | Gross logo churn (monthly) | (cancellations this month) ÷ (active at month start) | 0% | <3% | <3% | <2.5% | Mollie + Postgres | >5% in any month → churn postmortem doc |
| 10 | Unit economics | CAC (cash, blended) | (outbound + ads spend this month) ÷ new clients this month | n/a | <€250 | <€200 | <€200 | Smartlead + Google Ads + Postgres | >€350 → cut weakest channel |
| 11 | Delivery quality | % calls answered by AI (after-hours) | AI-answered calls ÷ inbound calls between 18:00–08:00 + weekends | n/a | >85% | >85% | >90% | Synthflow + CM.com | <75% → escalate Synthflow incident or routing fix |
| 12 | Compliance | AI Act Art. 50 disclosure failure rate | Calls without disclosure played ÷ total calls | 0% | 0% | 0% | 0% | Synthflow recording sample (10/wk) | Any failure → S1, file incident, freeze new clients until fixed |

Notes on KPIs deliberately bundled into others:
- ARPU is tracked under MRR (KPI 8) — divergence shows up as MRR-without-volume.
- Net MRR (new + expansion − contraction − churn) is computed in the Notion table footer but isn't its own row until M6, when expansion exists.
- Net revenue retention (>100%) is reviewed monthly, not weekly, until M9 (insufficient cohort size).
- Payback period (<1 month) and gross margin (>90%) are checked monthly against `07-finance/unit-economics.md`; they don't move week-to-week.
- Review-request response rate and median missed-call-SMS latency (<60s) are tracked as quality signals in the Notion page but only escalated if KPI 11 also flags.
- DPA-signed coverage (100% of paid clients) is a binary monthly check, not weekly.

## 4. The 45-minute agenda

```
[ ] 16:00–16:10  Pull numbers into kpi-{ISO-week} Notion page
                 - M1–M2: manual from Attio / Smartlead / Mollie / psql
                 - M3+:   copy automated table from /r/internal
[ ] 16:10–16:15  Apply RAG colour to each row vs. target band
[ ] 16:15–16:25  Identify the ONE number most off-track
                 - "Most off-track" = largest negative delta vs. target, ties broken
                   by impact on MRR
                 - Root-cause it: write 3 lines of "why" in the Notion row
[ ] 16:25–16:35  Decide ONE action for next week
                 - Single owner, single deadline (next Friday 16:00)
                 - Logged as a Linear ticket linked from the Notion page
[ ] 16:35–16:40  If trajectory diverged >20% for 2 weeks: edit
                 00-MASTER-PLAN.md § 3 numbers and commit
[ ] 16:40–16:45  Pick the ONE stat for Monday's LinkedIn build-in-public post
                 (raw number + lesson, no spin)
```

Rules:
- Never decide more than one action per review. Multiple actions = no action.
- The "one number" cannot be the same as last week unless it's still red after a deliberate action — in which case escalate per § 5.
- If everything is green, the action is "double down on the channel producing the most MRR-per-hour" and the LinkedIn post is the win.

## 5. Escalation rules

A weekly review is enough for normal drift. These triggers force action outside the 45-minute window.

| Trigger | Escalation | Doc to produce |
|---|---|---|
| MRR <80% of plan for 2 consecutive weeks | Emergency reposition workshop (3h, founder solo, M1–M5; founder + advisor from M6) | `01-strategy/repositioning-notes-{date}.md` |
| Cold-email reply rate halves week-over-week | Pause all sends within 24h, audit deliverability (DMARC, blacklists, inbox warmup) | `06-outbound/deliverability-audit-{date}.md` |
| Gross monthly churn >5% | Churn postmortem within 7 days; founder calls every churned client personally | `03-delivery/churn-postmortem-{date}.md` |
| Synthflow Dutch quality incident (NPS complaint or recording flagged) | S1 incident: switch to VAPI + ElevenLabs adapter within 48h if recurring | `10-ops/incidents/{date}-synthflow.md` |
| Any AI Act Art. 50 disclosure failure | S1: freeze new client onboarding, audit all live agents within 24h | `10-ops/incidents/{date}-ai-act.md` |
| Time-to-go-live median >35 days | Productize onboarding harder; founder runs the next onboarding solo with stopwatch | `03-delivery/onboarding-v{n}.md` |
| CAC >€350 for the month | Cut the lowest-payback channel for 30 days; reallocate budget | Note in `07-finance/unit-economics.md` |
| Two weeks of red on the same KPI after an action was taken | Action wasn't the root cause; escalate to founder + first advisor call | None — verbal |
| Mollie failed-payment rate >2% / week | SEPA mandate audit; check Mollie webhooks; manual outreach to affected clients | `08-tech/incidents/{date}-mollie.md` |
| Founder hours/week >25 for 2 consecutive weeks | Hire trigger pulled forward; post VA job within 7 days | Update `00-MASTER-PLAN.md § 4` |

Incident docs follow the postmortem template in `10-ops/incidents/_template.md` (to be created on first incident, per `08-tech/observability.md § When to add what`).

## 6. Data sources

Match to `08-tech/observability.md` and `08-tech/stack-decisions.md`. The KPI dashboard is a thin Postgres-view layer; everything else is the system of record.

| KPI | Upstream system of record | Collection method | Latency |
|---|---|---|---|
| Cold-email reply rate | Smartlead | Manual dashboard M1–M2; Smartlead API → n8n → Postgres `events` from M3 | Daily |
| Discoveries booked | Attio (`discovery_booked` event) | Attio API → n8n → Postgres nightly | <1h |
| Win rate | Attio (`won` event ÷ shown) | Attio API → n8n → Postgres nightly | <1h |
| Sales cycle days | Attio event log | SQL on Postgres `events`, median over 30d | Nightly |
| Pilots / clients live | Postgres `clients.status = 'live'` | Direct SQL view | Real-time |
| Time-to-go-live | Postgres `clients(won_at, live_at)` | SQL view, median over 30d | Nightly |
| First-week call volume | Synthflow webhook → n8n → Postgres `calls`; CM.com CDR for non-AI calls | Webhook + nightly reconciliation | <15 min |
| MRR | Mollie subscriptions + Postgres `subscriptions` | Mollie API → n8n → Postgres nightly | Daily |
| Gross logo churn | Mollie cancellations + Postgres `subscriptions` | SQL view, monthly window | Daily |
| CAC (cash) | Smartlead spend + Google Ads spend + Postgres `clients.created_at` | Manual aggregation M1–M2; n8n from M3 | Weekly |
| % calls answered by AI (after-hours) | Synthflow webhook + CM.com CDR | n8n joins, filtered to 18:00–08:00 + weekends | <15 min |
| AI Act disclosure failure rate | Sampled Synthflow recordings (10/wk minimum) | Manual review M1–M6; Claude API spot-check from M7 | Weekly |

All views live in Neon Postgres (`08-tech/stack-decisions.md`); the dashboard endpoint is `apps/automation-api` on Cloudflare Workers, the page is `apps/marketing-site/src/pages/r/internal.astro` (Astro, password-gated). Healthchecks pings on the nightly cron so a missed pull alerts via WhatsApp (`08-tech/observability.md § Layer 2`).

## 7. What we explicitly DON'T track weekly

Listing what's out of scope is as important as what's in.

| Not tracked weekly | Why |
|---|---|
| LinkedIn follower count | Vanity; only inbound demos from LinkedIn matter (counted under KPI 2) |
| Page views without conversion | Vanity; covered monthly in `05-content/` review |
| Brand sentiment / NPS score | Sample size too small <30 clients; revisit at M9 |
| Cash flow detail | Monthly close in `07-finance/` is the system of record |
| Cohort retention curves | <60 clients = every churn is a 1:1 conversation, no statistical pattern yet |
| Full-funnel attribution per channel | Heuristic in Attio is enough until €20k MRR (`08-tech/observability.md § Layer 3`) |
| Per-tier ARPU breakdown | Monthly view; weekly noise too high |
| Hours/client delivery time | Monthly review unless founder hours/week trigger (§ 5) fires |
| Domain authority / SEO rankings | Monthly in `05-content/` |
| Twitter, Instagram, TikTok metrics | Not used (master plan § 4 — TikTok/Instagram explicitly out) |

Anything in this table that becomes load-bearing for a decision graduates into § 3 and an existing KPI gets demoted to monthly. The list is a maximum of 12.

## 8. Quarterly review (90-day layer)

Every 13 weeks the founder runs a deeper retrospective: weekly KPIs are aggregated into trend lines, the master plan numbers are rebased against actuals, and the docs themselves get edited where reality diverged. The quarterly review is the only forum where targets in `00-MASTER-PLAN.md § 3` and `07-finance/mrr-projections.md` get rewritten — weekly reviews never rewrite plan numbers, they only flag divergence. Output is a one-page memo in `01-strategy/quarterly-{YYYY-Qn}.md` plus updates to the affected docs in the same commit. Sequence and triggers live in `01-strategy/90-day-roadmap.md` (week 12 retrospective).

## 9. Sources

Internal cross-references:
- [`../00-MASTER-PLAN.md`](../00-MASTER-PLAN.md) § 3 (numbers), § 4 (90-day sequence), § 8 (Friday 16:00 cadence)
- [`../01-strategy/90-day-roadmap.md`](../01-strategy/90-day-roadmap.md) — month-by-month outcomes and stop-gates
- [`../02-sales/funnel-benchmarks.md`](../02-sales/funnel-benchmarks.md) — pipeline benchmarks for KPIs 1–4
- [`../07-finance/mrr-projections.md`](../07-finance/mrr-projections.md) — MRR targets per month (KPI 8)
- [`../07-finance/unit-economics.md`](../07-finance/unit-economics.md) — CAC, payback, gross margin formulas (KPIs 10, monthly checks)
- [`../08-tech/observability.md`](../08-tech/observability.md) — Layer 3 business-KPI pipeline, audit log, dashboard automation
- [`../08-tech/stack-decisions.md`](../08-tech/stack-decisions.md) — Attio, Smartlead, Mollie, Neon, Synthflow, CM.com as systems of record

External references:
- ISO 8601 week numbering (for Notion page naming): https://en.wikipedia.org/wiki/ISO_week_date
- EU AI Act Art. 50 transparency obligations: https://artificialintelligenceact.eu/article/50/
- Atlassian SLA vs SLO vs SLI (RAG band model): https://www.atlassian.com/incident-management/kpis/sla-vs-slo-vs-sli
