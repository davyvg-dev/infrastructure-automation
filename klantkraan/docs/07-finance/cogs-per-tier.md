# COGS per Tier — Detailed Breakdown

> Herzien 2026-07-13 for the two-tier text-first pricing (€299 Chat / €499 Compleet).
> **Claude API line re-measured 2026-08-17** against the one real production session in
> `ai-receptionist/data/analytics.db`; workings, caveats (n=1) and the caching maths in
> `research/finance-feasibility-2026-08-16/research-cogs.md`. Every other line is still an
> estimate, and the WhatsApp line is the one known suspect.

## Chat — €299/mo

Assumption: ~300 text conversations/mo (web chat + WhatsApp). **Not "a few thousand tokens
each":** measured at ~3,900 tokens of system prompt plus tool definitions re-sent on *every
turn*, so a 3-turn conversation costs 12,309 input and 319 output tokens. Cost scales with
turn count, not conversation count.

| Cost item                       | Detail                                                                                            | Cost       |
| ------------------------------- | ------------------------------------------------------------------------------------------------- | ---------- |
| Claude API                      | measured: 300 conversations x 3 turns on `claude-opus-4-8`, which is what every client config and both scaffold defaults ship. No prompt caching implemented. | **€19.00** |
| WhatsApp Business API           | **UNVERIFIED, prime suspect.** Meta moved to per-message pricing during 2025 and this line assumes the old free-entry service conversation. | €3.00 ?    |
| Hetzner amortised               | CX22 €3.79 + 40 GB volume €1.60 = €5.39/mo over ~30 clients (`docs/08-tech/infra-setup.md`). At 0-1 clients this is fixed overhead, not COGS. | €0.18      |
| Storage (calendar/session data) | SQLite/Postgres on same box                                                                       | €0.00      |
| Mollie SEPA fee                 | €0.25 / collection                                                                                | €0.25      |
| Misc + buffer                   | monitoring, notify pings, retries                                                                 | €3.25      |
| **Total Chat COGS**             |                                                                                                   | **~€26**   |
| **Chat GM**                     |                                                                                                   | **~91%**   |

**The margin is a decision, not a property.** The same session costs €19 on Opus 4.8, €11 with
prompt caching added, and €3.90 on Haiku 4.5 — which is what the original €3.00 estimate was
implicitly pricing, and `config/business.yaml:73` names Haiku as an option nobody selected.
One trap before switching: Haiku 4.5 will not cache a prefix under 4,096 tokens and ours is
~3,900, so "Haiku plus caching" does not compose today. Decide the model per tier first, then
cache.

## Compleet — €499/mo (provisional — voice not yet live)

Chat base + self-hosted LiveKit voice stack. Assumption: ~150 voice minutes/mo. **Do not treat as validated until the voice agent runs in production.**

| Cost item                             | Detail                                     | Cost       |
| ------------------------------------- | ------------------------------------------ | ---------- |
| Chat base (above, re-measured)         |                                            | €26.00     |
| Dutch number + SIP trunk lease        |                                            | €5.00      |
| Telephony per-minute                  | ~150 min × ~€0.01                          | €1.50      |
| STT                                   | ~150 min × ~€0.006 (Deepgram-class)        | €1.00      |
| TTS                                   | ~150 min × ~€0.08 (ElevenLabs-class Dutch) | €12.00     |
| Claude API (voice turns)              | latency-optimised, shorter context         | €3.00      |
| LiveKit self-hosted compute amortised |                                            | €2.00      |
| Misc + buffer                         |                                            | €0.50      |
| **Total Compleet COGS**               |                                            | **~€51**   |
| **Compleet GM**                       |                                            | **~90%**   |

Two reasons this number is worse than it looks, both recorded elsewhere and neither fixed
here: the voice lines above assume the **LiveKit stack, which is not live**, while both real
offers on the table are served by a vendor ElevenLabs agent — DRS at 1,500 included minutes
is ~€192/mo COGS on €685, i.e. **~72% GM, not 90%** (TODO §U6). And the Claude API line here
inherits the same model question as Chat: it was estimated, not measured.

## Blended (70% Chat / 30% Compleet, once voice is live)

`Blended COGS = 0.70×26 + 0.30×51 = ~€33.50`
`Blended ARPU (list) = 0.70×299 + 0.30×499 = €359`
`Blended GM = (359-33.50) / 359 = ~90.7%`

Until voice ships: 100% Chat → ARPU €299, GM **~91%** (was 96.7% on the estimated Claude
line). Both figures assume the unverified WhatsApp line is right.

## Setup fee

€249 one-time (waived for pilots). Covers founder setup/tuning time (~2h) — effectively cost recovery, not margin. Not part of MRR or COGS.

## Where COGS could grow

| Risk                                      | Effect                              | Mitigation                                                             |
| ----------------------------------------- | ----------------------------------- | ---------------------------------------------------------------------- |
| Heavy chat users (>>300 conversations/mo) | +€2-5 Claude API per outlier client | Monitor per-client token spend; fair-use clause in MSA if needed       |
| Meta raises WhatsApp conversation fees    | minor                               | Web chat is fee-free fallback; SMS via CM.com as backup channel        |
| TTS pricing (Compleet)                    | voice is the dominant COGS line     | Validate real €/min before selling Compleet; swap TTS vendor if needed |
| EU AI Act compliance audit costs          | one-off ~€2-3k legal                | Allocate against year-1 P&L, not COGS                                  |

## What's NOT in COGS

- Founder time
- Outbound stack (CAC, not COGS)
- Content stack (S&M, not COGS)
- Insurance (G&A, not COGS)
- Bookkeeping (G&A, not COGS)

These are fixed monthly overhead (~€450/mo total) and live in the unit-economics fixed-cost section.

## Source

- Measured usage: `ai-receptionist/data/analytics.db`, session `comfortec:webchat:ff3775bca2982cc9` (2026-07-25). Workings: `research/finance-feasibility-2026-08-16/research-cogs.md`.
- Anthropic Claude API pricing: https://www.anthropic.com/pricing — Opus 4.8 and Opus 5 $5/$25 per MTok, Sonnet 5 $3/$15 (intro $2/$10 t/m 2026-08-31), Haiku 4.5 $1/$5. Prompt caching: write 1.25x base (5 min TTL) or 2x (1 h), read ~0.1x. Minimum cacheable prefix is per-model and NOT monotonic: Opus 5 512, Opus 4.8 1,024, Haiku 4.5 4,096.
- Hetzner CX22 + 40 GB volume: `docs/08-tech/infra-setup.md`, `docs/08-tech/stack-decisions.md`.
- WhatsApp Business Platform conversation pricing: https://developers.facebook.com/docs/whatsapp/pricing/ — **not re-checked since Meta's 2025 move to per-message pricing.**
- CM.com messaging pricing: https://www.cm.com/pricing/
- ElevenLabs pricing: https://elevenlabs.io/pricing
- Deepgram pricing: https://deepgram.com/pricing
- Mollie SEPA pricing: https://www.mollie.com/products/sepa-direct-debit
