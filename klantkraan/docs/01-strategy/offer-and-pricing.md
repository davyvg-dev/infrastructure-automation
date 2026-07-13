# Offer & Pricing

> Herzien 2026-07-13 — repriced to two tiers (€299 Chat / €499 Compleet) and reframed text-first after the 2026-07-11 pivot. Replaces the old €299/€599/€999 structure.

## The product

**Klantkraan** is a productized monthly service: a Dutch AI-receptionist for trade businesses, delivered text-first.

1. **AI-receptionist (websitechat + WhatsApp)** — answers customer questions 24/7 in Dutch, books appointments straight into the calendar, captures leads and terugbelverzoeken, and escalates to the owner. Built on the `ai-receptionist` app (FastAPI + Claude tool use); per-client rebrand is a config file, zero code.
2. **Done-for-you setup and tuning** — Klantkraan configures services, tariffs, FAQ, and booking rules per business and keeps tuning them. The client does nothing technical.
3. **AI-telefonist (voice) — the upsell** — the same receptionist answering inbound calls on the client's own Dutch number. The voice agent (LiveKit) is built but **not yet live**; Compleet is sold only once voice is production-ready.

The receptionist only offers real calendar slots, never invents prices or advice, and always discloses it is a digital assistant (EU AI Act art. 50).

## The tiers

| | **Chat** | **Compleet** (upsell) |
|---|---|---|
| **Price** | €299 / mo | €499 / mo |
| Websitechat + WhatsApp receptionist (24/7, Dutch) | ✅ | ✅ |
| Beantwoordt vragen (diensten, tarieven, FAQ) | ✅ | ✅ |
| Plant afspraken in de agenda | ✅ | ✅ |
| Vangt leads en terugbelverzoeken | ✅ | ✅ |
| Done-for-you setup en tuning | ✅ | ✅ |
| Maandelijks rapport | ✅ | ✅ |
| AI-telefonist (voice) op eigen Nederlands nummer | — | ✅ |

**Both tiers include:**
- Eenmalige setup €249 (waived for pilot clients)
- Monthly cancel (30-day opzegtermijn)
- First month 50% off (NOT free — preserves perceived value)
- 30-day satisfaction guarantee (full refund of first month if not satisfied)
- All prices excl. 21% BTW

**Commitment discounts:**
- 6-month prepay: 15% off
- 12-month prepay: 20% off (and locked-in pricing if annual rate index changes)

**Status (2026-07-13):** only Chat is sellable today. The voice agent is dormant; Compleet is quoted as the upgrade path, never sold before voice is verified live. No third tier — the old €999/€849 Premium is killed.

## Why this structure wins

| Lever | Effect |
|---|---|
| Two tiers (€299/€499) | No decoy needed. Chat is a low-friction entry under every NL voice-tool bundle; Compleet anchors the value of voice at +€200. |
| Low setup (€249, waived for pilots) | Beats NL Gold Lemon (€199 + €899 setup) and agency setups of €1,500+. |
| Monthly cancel | Destroys the Podium-style 12-mo lock-in objection — a known #1 NL trade pain. |
| First month 50% off | Better than "free" — paid attention is more honest than free anything. |
| 30-day guarantee | Risk reversal. Costs us almost nothing because COGS is tiny. |
| Prepay 15–20% off | Pulls cash forward, predicts MRR, signals strong intent. |

## What we do NOT offer

- ❌ Free trial. The 50%-off month replaces it.
- ❌ Pay-per-lead pricing. We don't compete with Werkspot / Gigaleads.
- ❌ "Starting at" pricing. Dutch buyers demand the full number up front.
- ❌ One-off projects. Productized only.
- ❌ Selling Compleet before voice is live. Honest upsell only.

## Per-tier ARPU + margin

COGS assumptions are provisional (see `07-finance/cogs-per-tier.md`); text conversations via the Claude API cost cents, so Chat margin is structurally higher than the old voice-first tiers.

| Tier | List | COGS (est.) | GM% |
|---|---|---|---|
| Chat | €299 | ~€10 | ~96.7% |
| Compleet | €499 | ~€35 | ~93.0% |
| **Blended (70% Chat / 30% Compleet, once voice live)** | **€359** | **~€17.50** | **~95.1%** |

Until voice ships, the realistic planning ARPU is **€299** (100% Chat); net ~€285 after ~5% prepay-discount drag.

## How to handle pricing in sales

- Always quote **incl. BTW** if the prospect is a BV that can reclaim it (avoids friction). Quote excl. BTW if eenmanszaak.
- Default recommendation = **Chat**. Compleet is mentioned as the upgrade path ("zodra de telefonist live is, zet ik je bovenaan de lijst") — never promised with a date.
- When asked "kan ik korting?": offer the 6-month prepay (15% off) — never discount the monthly rate.
- When asked "kan ik later upgraden?": yes, same-day once voice is live, prorated. Downgrade only at month boundary.

## Tier upgrade triggers (account-management lever)

A Chat client is a Compleet candidate when:
- They mention missed calls or "ik kan mijn telefoon niet bijhouden" in a check-in, OR
- Their chat log shows repeated "kan ik iemand bellen?" requests, OR
- They have staff answering phones during work hours.

Log candidates now; convert them the week voice goes live.

## Future tiers (roadmap, not yet sold)

- **Klantkraan UK** — Chat equivalent in English, separate landing page. Month 6+.
- **Klantkraan Multi-site** — for groups of 2+ branches sharing the receptionist. Priced on request. Month 9+.
- **Klantkraan White-label** — license to other agencies / accountants. Year 2.

## Sources

- Competitor pricing (Cowcierge €150, Voicelabs €149, Gold Lemon €199+€899, MyAutoPilot €350+€1,350): research in `09-brand/naming-and-domain.md` references and `02-sales/funnel-benchmarks.md`.
- US benchmarks (LeadTruffle $229, Podium from $399 with lock-in): https://www.intrysys.com/compare/best-missed-call-text-back-contractors
- UK Invox £99/mo with 30-day guarantee: https://invoxai.uk/
