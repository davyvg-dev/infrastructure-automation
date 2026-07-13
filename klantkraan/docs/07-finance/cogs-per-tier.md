# COGS per Tier — Detailed Breakdown

> Herzien 2026-07-13 for the two-tier text-first pricing (€299 Chat / €499 Compleet). What it actually costs us to deliver one client-month at each tier. **All numbers are conservative estimates pending real usage data** — text conversations via the Claude API cost cents each, so even these estimates carry buffer.

## Chat — €299/mo

Assumption: ~300 text conversations/mo (web chat + WhatsApp), a few thousand tokens each.

| Cost item | Detail | Cost |
|---|---|---|
| Claude API | ~300 conversations + monthly report, tool-use turns included | €3.00 |
| WhatsApp Business API | Meta conversation fees via BSP; service conversations mostly free-entry, utility templates ~€0.05 | €3.00 |
| Hetzner amortised | shared box runs ai-receptionist + n8n, ~30 clients per box | €0.50 |
| Storage (calendar/session data) | SQLite/Postgres on same box | €0.00 |
| Mollie SEPA fee | €0.25 / collection | €0.25 |
| Misc + buffer | monitoring, notify pings, retries | €3.25 |
| **Total Chat COGS** | | **€10.00** |
| **Chat GM** | | **96.7%** |

## Compleet — €499/mo (provisional — voice not yet live)

Chat base + self-hosted LiveKit voice stack. Assumption: ~150 voice minutes/mo. **Do not treat as validated until the voice agent runs in production.**

| Cost item | Detail | Cost |
|---|---|---|
| Chat base (above) | | €10.00 |
| Dutch number + SIP trunk lease | | €5.00 |
| Telephony per-minute | ~150 min × ~€0.01 | €1.50 |
| STT | ~150 min × ~€0.006 (Deepgram-class) | €1.00 |
| TTS | ~150 min × ~€0.08 (ElevenLabs-class Dutch) | €12.00 |
| Claude API (voice turns) | latency-optimised, shorter context | €3.00 |
| LiveKit self-hosted compute amortised | | €2.00 |
| Misc + buffer | | €0.50 |
| **Total Compleet COGS** | | **€35.00** |
| **Compleet GM** | | **93.0%** |

## Blended (70% Chat / 30% Compleet, once voice is live)

`Blended COGS = 0.70×10 + 0.30×35 = €17.50`
`Blended ARPU (list) = 0.70×299 + 0.30×499 = €359`
`Blended GM = (359-17.50) / 359 = 95.1%`

Until voice ships: 100% Chat → ARPU €299, GM ~96.7%.

## Setup fee

€249 one-time (waived for pilots). Covers founder setup/tuning time (~2h) — effectively cost recovery, not margin. Not part of MRR or COGS.

## Where COGS could grow

| Risk | Effect | Mitigation |
|---|---|---|
| Heavy chat users (>>300 conversations/mo) | +€2-5 Claude API per outlier client | Monitor per-client token spend; fair-use clause in MSA if needed |
| Meta raises WhatsApp conversation fees | minor | Web chat is fee-free fallback; SMS via CM.com as backup channel |
| TTS pricing (Compleet) | voice is the dominant COGS line | Validate real €/min before selling Compleet; swap TTS vendor if needed |
| EU AI Act compliance audit costs | one-off ~€2-3k legal | Allocate against year-1 P&L, not COGS |

## What's NOT in COGS

- Founder time
- Outbound stack (CAC, not COGS)
- Content stack (S&M, not COGS)
- Insurance (G&A, not COGS)
- Bookkeeping (G&A, not COGS)

These are fixed monthly overhead (~€450/mo total) and live in the unit-economics fixed-cost section.

## Source

- Anthropic Claude API pricing: https://www.anthropic.com/pricing
- WhatsApp Business Platform conversation pricing: https://developers.facebook.com/docs/whatsapp/pricing/
- CM.com messaging pricing: https://www.cm.com/pricing/
- ElevenLabs pricing: https://elevenlabs.io/pricing
- Deepgram pricing: https://deepgram.com/pricing
- Mollie SEPA pricing: https://www.mollie.com/products/sepa-direct-debit
