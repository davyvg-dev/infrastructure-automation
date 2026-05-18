# COGS per Tier — Detailed Breakdown

> What it actually costs us to deliver one client-month at each tier. Critical for pricing decisions and overage rate-setting.

## Lite — €299/mo

| Cost item | Detail | Cost |
|---|---|---|
| CM.com SMS — outbound | ~30 missed-call-back + ~20 review-request SMS @ €0.08 | €4 |
| CM.com Dutch number lease | 1 local number | €1 |
| Postgres rows (Neon free → paid threshold) | <100k rows / client / yr → free tier | €0 |
| Cloudflare R2 (no audio for Lite) | dashboard JSON only, ~1 MB / mo | €0 |
| Hetzner amortised | shared 4 GB CX22, ~30 clients per box → €3.79 ÷ 30 | €0.13 |
| Mollie SEPA fee | €0.25 / collection | €0.25 |
| Attio contact | free tier | €0 |
| Misc + buffer | review-link redirect, monitoring | €0.62 |
| **Total Lite COGS** | | **€6.00** |
| **Lite GM** | | **98.0%** |

## Pro — €599/mo

| Cost item | Detail | Cost |
|---|---|---|
| CM.com SMS | ~50/mo @ €0.08 | €4 |
| CM.com number lease | 1 local number | €1 |
| Synthflow voice | ~150 min × €0.12 (NL pipeline incl. Eleven + telephony) | €18 |
| Cloudflare R2 | ~3 GB recordings + transcripts (180-day retention) | €0.10 |
| Claude API | ~150k tokens / mo (transcripts, summaries, owner-weekly) | €4 |
| Postgres | ~250k rows / yr | €0.50 |
| Hetzner amortised | as above | €0.50 |
| Mollie SEPA fee | €0.25 | €0.25 |
| Attio | free tier | €0 |
| Misc + buffer | n8n executions, healthchecks pings, retries | €1.65 |
| **Total Pro COGS** | | **€30.00** |
| **Pro GM** | | **95.0%** |

## Max — €999/mo

| Cost item | Detail | Cost |
|---|---|---|
| CM.com SMS | ~80/mo (higher volume + priority) | €6.40 |
| CM.com number lease | 1 local number | €1 |
| Synthflow voice | ~350 min × €0.12 | €42 |
| Cloudflare R2 | ~8 GB recordings | €0.30 |
| Claude API | ~400k tokens / mo (incl. custom integration work) | €5 |
| Postgres | ~500k rows / yr | €1 |
| Hetzner amortised | as above | €0.50 |
| Mollie SEPA fee | €0.25 | €0.25 |
| Attio | free tier | €0 |
| Custom-integration support time | amortised: ~30 min / mo of founder + ~15 min of VA | (counted in fixed overhead, not COGS) |
| Misc + buffer | integration error retries, monitoring, priority WhatsApp lane | €0.30 |
| **Total Max COGS** | | **€55.00** |
| **Max GM** | | **94.5%** |

## Overage voice minutes

Charged at **€0.50/min**. Our cost ~€0.12/min → ~76% margin on overage. Built-in upsell signal: clients with consistent overage = Max-tier candidates.

## Blended (30% Lite / 55% Pro / 15% Max)

`Blended COGS = 0.30×6 + 0.55×30 + 0.15×55 = €26.55`
`Blended ARPU (net) = €540`
`Blended GM = (540-26.55) / 540 = 95.1%`

## Where COGS could grow

| Risk | Effect | Mitigation |
|---|---|---|
| Synthflow raises per-minute price | +20% on voice COGS → -1% blended GM | Telephony adapter (`packages/telephony`) lets us swap to VAPI / Retell in days |
| CM.com SMS tariff increase | minor | Switch to MessageBird/Bird as backup; rare |
| Claude API price cut (positive) | -€1-2 per Pro client | Re-invest in better Dutch quality |
| EU AI Act compliance audit costs | one-off ~€2-3k legal | Allocate against year-1 P&L, not COGS |

## What's NOT in COGS

- Founder time
- Outbound stack (CAC, not COGS)
- Content stack (S&M, not COGS)
- Insurance (G&A, not COGS)
- Bookkeeping (G&A, not COGS)

These are fixed monthly overhead (~€450/mo total) and live in the unit-economics fixed-cost section.

## Source

- CM.com SMS pricing: https://www.cm.com/pricing/sms/
- Synthflow voice pricing: https://synthflow.ai/pricing
- Cloudflare R2 pricing: https://www.cloudflare.com/products/r2/
- Neon Postgres pricing: https://neon.tech/pricing
- Anthropic Claude API pricing: https://www.anthropic.com/pricing
- Mollie SEPA pricing: https://www.mollie.com/products/sepa-direct-debit
