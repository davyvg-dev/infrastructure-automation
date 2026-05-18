# Offer & Pricing

## The product

**Klantkraan** is a productized monthly service combining three modules:

1. **Missed-call-back SMS** — when a call is missed, an automated Dutch SMS reaches the caller within 60 seconds with a Cal.com booking link.
2. **Review automation** — when a job is marked done, the customer receives a Dutch SMS asking for a Google review (Trustpilot secondary), with a soft email follow-up at day 7.
3. **AI receptionist (Pro/Max)** — a Synthflow Dutch voice agent answers inbound calls 24/7, classifies intent (SPOED / NIEUW_WERK / BESTAANDE_KLANT / LEVERANCIER / SPAM), books appointments into Cal.com, and escalates to the owner.

All three modules run on a per-client n8n workflow with credentials isolated by `client_id` in Postgres. Per-client COGS averages €6 (Lite) / €30 (Pro) / €55 (Max).

## The tiers

| | **Lite** | **Pro** ⭐ | **Max** |
|---|---|---|---|
| **Price** | €299 / mo | €599 / mo | €999 / mo |
| Missed-call SMS | ✅ | ✅ | ✅ |
| Google + Trustpilot review automation | ✅ | ✅ | ✅ |
| Monthly stats email | ✅ | ✅ | ✅ |
| Cloudflare-hosted dashboard | ✅ | ✅ | ✅ |
| AI Receptionist (Dutch, 24/7) | — | ✅ 200 min | ✅ 500 min |
| Cal.com booking flow | — | ✅ | ✅ |
| Custom integrations (Snelstart, Werkbon, Skoon) | — | — | ✅ |
| Monthly strategy call | — | — | ✅ |
| Priority support (WhatsApp Business) | — | — | ✅ |
| Overage minutes | n/a | €0.50/min | €0.50/min |

**All tiers include:**
- No setup fee
- Monthly cancel (30-day opzegtermijn)
- First month 50% off (NOT free — preserves perceived value)
- 30-day satisfaction guarantee (full refund of first month if not satisfied)
- All prices excl. 21% BTW

**Commitment discounts:**
- 6-month prepay: 15% off
- 12-month prepay: 20% off (and locked-in pricing if annual rate index changes)

## Why this structure wins

| Lever | Effect |
|---|---|
| Tiered (€299/€599/€999) | Anchors high at Max → makes Pro feel like the safe choice. Lite catches the skeptical. |
| No setup fee | Beats UK Invox (~£99/mo but with setup) and NL Gold Lemon (€199 + €899 setup). |
| Monthly cancel | Destroys the Podium-style 12-mo lock-in objection — a known #1 NL trade pain. |
| First month 50% off | Better than "free" — paid attention is more honest than free anything. |
| 30-day guarantee | Risk reversal. Costs us almost nothing because COGS is tiny. |
| Annual prepay 15% off | Pulls cash forward, predicts MRR, signals strong intent. |

## What we do NOT offer

- ❌ Free trial. The 50%-off month replaces it.
- ❌ Pay-per-lead pricing. We don't compete with Werkspot / Gigaleads.
- ❌ "Starting at" pricing. Dutch buyers demand the full number up front.
- ❌ One-off projects. Productized only.
- ❌ Long contracts < €999. (Available as a discount, not a default.)

## Per-tier ARPU + margin

Assumed mix 30% Lite / 55% Pro / 15% Max → blended ARPU **€569** list, **~€540 net** after small prepay discount drag.

| Tier | ARPU | COGS | GM% |
|---|---|---|---|
| Lite | €299 | €6 | 98.0% |
| Pro | €599 | €30 | 95.0% |
| Max | €999 | €55 | 94.5% |
| **Blended** | **€569** | **€26.55** | **95.1%** |

## How to handle pricing in sales

- Always quote **incl. BTW** if the prospect is a BV that can reclaim it (avoids friction). Quote excl. BTW if eenmanszaak.
- Default recommendation = **Pro**. Lite is "if you want to try the SMS layer first." Max is "if you want it to feel like a real ops upgrade."
- When asked "kan ik korting?": offer the 6-month prepay (15% off) — never discount the monthly rate.
- When asked "kan ik later upgraden?": yes, same-day, prorated. Downgrade only at month boundary.

## Tier upgrade triggers (account-management lever)

A Lite client is a Pro candidate when:
- Recovered 3+ missed calls in their first month, OR
- Their dashboard shows ≥10 inbound calls/week, OR
- They mention "ik kan mijn telefoon niet bijhouden" in a check-in.

A Pro client is a Max candidate when:
- Their voice minutes consistently exceed 180/mo (90% of cap), OR
- They have an existing CRM/ERP integration request, OR
- They've added staff and need WhatsApp Business priority lane.

## Future tiers (roadmap, not yet sold)

- **Klantkraan UK** — Pro equivalent in English, separate landing page, separate Synthflow voice library. Month 6+.
- **Klantkraan Multi-site** (€1,499/mo) — for groups of 2+ branches sharing the AI receptionist. Month 9+.
- **Klantkraan White-label** (€2,499/mo + rev share) — license to other agencies / accountants. Year 2.

## Sources

- Competitor pricing (Cowcierge €150, Voicelabs €149, Gold Lemon €199+€899, MyAutoPilot €350+€1,350): research in `09-brand/naming-and-domain.md` references and `02-sales/funnel-benchmarks.md`.
- US benchmarks (LeadTruffle $229, Podium from $399 with lock-in): https://www.intrysys.com/compare/best-missed-call-text-back-contractors
- UK Invox £99/mo with 30-day guarantee: https://invoxai.uk/
