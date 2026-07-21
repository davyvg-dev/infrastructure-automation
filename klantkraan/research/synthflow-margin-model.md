# Synthflow → Klantkraan Voice-Receptionist Margin Model

**Date:** 2026-07-21
**Scope:** What Klantkraan must charge for a resold Synthflow voice receptionist (Compleet tier) to hold a healthy reseller margin. Driven by the first voice client: an English-speaking air-conditioning / HVAC company in Mallorca.
**FX assumption:** EUR/USD ~1.14 (21 Jul 2026), i.e. $1 ≈ €0.88. Model planned at **€0.14/min** (typical cost + buffer).

---

## Bottom line

- Keep the **€499 headline**, but restructure it as **€499 base / 750 included minutes / €0.40 per overage minute + a €250–500 one-time setup fee.** This holds **71–79% gross margin across the full HVAC volume range**, including a busy Mallorca summer.
- Run **pay-as-you-go on a single Synthflow workspace.** Do **not** buy the ~$2,000/mo white-label toolkit for one client — it needs ~6 clients just to break even. Revisit at ~10+ voice clients.
- Flat €499 is fine at low/typical volume (72–86% margin) but **collapses to 30–44% in a busy AC summer** — that seasonal swing is the whole reason to move to base + included minutes + overage.

---

## 1. Synthflow pricing (2026)

Synthflow retired its old fixed tiers after its Series A. Current public model:

| Plan | Monthly | Included minutes | Per-minute | Notes |
|---|---|---|---|---|
| **Pay-as-you-go** (our plan) | **$0 to start** | none (pure usage) | component sum, **~$0.11–0.24/min** | 5 concurrent calls, unlimited agents, API/integrations included |
| **Enterprise** | **from $30,000/yr** | custom | ~$0.12/min @20k min → ~$0.07 @400k+ | white-label, SIP, SLA, HIPAA included |

Third-party sites still quoting "Starter $29 / Pro $450 / Growth $900 / Agency $1,400" are citing **stale snapshots — do not price off those.**

## 2. What's bundled vs. separate (pay-as-you-go)

Per-minute price = sum of three components, plus fixed add-ons:

| Component | Cost | Notes |
|---|---|---|
| Voice engine (STT + TTS + orchestration) | **$0.09/min** | core; standard voices included |
| LLM tokens | GPT-4.1-mini **$0.02** · GPT-5-class **$0.04** · GPT-4.1 **$0.05** · BYO **$0** | separate line item |
| Telephony | managed Twilio **$0.02/min** · BYO Twilio **$0** | Synthflow resells Twilio |
| Phone number | **$1.50/mo** each | add-on |
| Extra concurrency (>5) | **$20/mo** per slot | only bites on shared multi-client workspaces |
| Low-latency / performance routing | **+$0.04/min** each | optional quality upgrade |
| White-label & reseller toolkit | **~$2,000/mo** (medium confidence; Enterprise-included) | skip for now |

**Verify before quoting:**
- **Premium / ElevenLabs voices** may be a BYOK passthrough (~$0.04–0.10/min extra) — *not confirmed on Synthflow's own page.* If the Mallorca client wants a specific premium voice, get the exact rate first; it can push cost into the "high" band.
- **White-label $2,000/mo** appears in third-party breakdowns but not Synthflow's own pricing page — confirm before ever pitching client-portal access.
- **Minute rounding** (per-second vs per-minute) not confirmed — per-minute rounding inflates short-call cost.

## 3. All-in cost per minute

| Scenario | Config | USD/min | EUR/min |
|---|---|---|---|
| Low | GPT-4.1-mini + BYO Twilio | ~$0.11 | ~€0.10 |
| Typical | mid LLM + managed Twilio | ~$0.13–0.16 | ~€0.12–0.14 |
| High | GPT-4.1 + managed Twilio + low-latency (or premium voice) | ~$0.19–0.24 | ~€0.17–0.21 |

Synthflow's own FAQ: most PAYG setups land **$0.15–0.24/min.** Model planned at **€0.14/min.**

## 4. Volume — small HVAC front desk

AI answers all inbound; avg call 3–3.5 min.

| Scenario | Calls/day | Avg min | Days/mo | Minutes/mo |
|---|---|---|---|---|
| Conservative | 8 | 3.0 | 22 | ~500 |
| Typical | 15 | 3.0 | 22 | ~1,000 |
| Busy (Mallorca AC summer) | 25 | 3.5 | 26 | ~2,000–2,500 |

HVAC is highly seasonal. **Ask the client for their current call volume to tighten this.**

## 5. Cost to serve one client / month (PAYG, no white-label, €0.14/min)

| Volume | Minutes | Minutes cost | Number | Total COGS/mo |
|---|---|---|---|---|
| Conservative | 500 | €70 | €1.30 | **~€71** |
| Typical | 1,000 | €140 | €1.30 | **~€141** |
| Busy | 2,000 | €280 | €1.30 | **~€281** |
| Peak | 2,500 | €350 | €1.30 | **~€351** |

PAYG has no monthly base fee, so per-minute COGS is identical whether clients share one workspace or get one each — the difference is operational (isolation, billing) plus the shared 5-concurrent-call limit (+$20/mo per extra slot) once several clients share a workspace.

## 6. Margin at a flat €499

| Volume | COGS | Gross profit | Margin |
|---|---|---|---|
| Conservative (500) | €71 | €428 | **86%** |
| Typical (1,000) | €141 | €358 | **72%** |
| Busy (2,000) | €281 | €218 | **44%** |
| Peak (2,500) | €351 | €148 | **30%** |

Great until the client gets busy, then Klantkraan eats the seasonal volume risk.

## 7. Recommended structure — €499 base / 750 min / €0.40 overage

| Actual volume | Revenue | COGS | Margin |
|---|---|---|---|
| 750 (at cap) | €499 | €106 | **79%** |
| 1,500 (750 over) | €499 + €300 = €799 | €211 | **74%** |
| 2,500 (1,750 over) | €499 + €700 = €1,199 | €351 | **71%** |

- ≥70% gross margin at every volume; keeps the already-quoted €499 headline; passes seasonal upside through to revenue instead of eating it.
- €0.40 overage = ~2.9x markup on ~€0.14 cost; still an easy sell ("40 cents a minute over your bundle"). €0.35 is more client-friendly and stays ~68–72%.
- 750 included minutes covers a normal HVAC month; overage only triggers in busy season, when the client is making money.
- **Add a €250–500 one-time setup fee** — config-per-client makes setup cheap; the fee funds build labour without touching recurring margin.
- Margins above are **platform COGS only** — they still must absorb Klantkraan's own support/monitoring time (comfortable at €358–700 gross profit/client, but factor labour when scaling headcount).
- If/when adopting sub-accounts, **bill in EUR via Synthflow's Stripe rebilling** (supports EUR) to avoid FX leakage.

## 8. Risks / assumptions

- **FX:** Synthflow bills USD, Klantkraan invoices EUR. Euro slide to ~1.05 raises EUR COGS ~8%; overage markup absorbs it. Re-check quarterly.
- **Legacy-tier confusion:** G2 / retell / autocalls show old bundled-minute tiers — inconsistent snapshots; price only off the PAYG component model.
- **White-label price** medium confidence; doesn't affect the recommendation (not buying it yet).
- **Premium voice / rounding / concurrency** — see §2 "verify before quoting."
- **Enterprise cliff** above ~10,000 min/mo pushes to Enterprise ($30k/yr), which then *lowers* per-minute COGS ($0.07–0.12). Irrelevant for one client; relevant for a busy portfolio on one account.
- **No annual commit on PAYG** — no contract/lock-in; Enterprise starts at a $30k annual commit.

**Sources:** synthflow.ai/pricing · docs.synthflow.ai/set-up-pricing-and-rebilling · synthflow.ai/blog/voice-ai-cost · ringly.io/blog/synthflow-pricing · quiq.com/blog/synthflow-pricing · cloudtalk.io/synthflow-pricing · retellai.com · autocalls.ai · tradingeconomics EUR/USD.

**Confidence:** high on the two-model structure and the $0.11–0.24/min envelope; low on premium-voice passthrough, minute rounding, and the exact white-label price (verify all three directly with Synthflow before quoting a client).
