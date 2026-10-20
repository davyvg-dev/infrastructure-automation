# COGS, measured (2026-08-17)

The dimension U12 said was never measured, because the agent assigned to it died before
writing a line. This replaces the estimate, not the whole doc: two lines are now measured
from production data, one is corrected from the repo's own infra doc, and one is still
unverified and labelled as such.

## The finding

`cogs-per-tier.md` prices the Claude API at **EUR 3.00** for ~300 conversations a month.
The one real production session in `ai-receptionist/data/analytics.db` prices out at
**USD 20.86** for the same volume — about 7x — for one reason: **every client config and
both scaffold defaults run `claude-opus-4-8`, not Haiku.**

The EUR 3.00 estimate is not careless. It is very nearly correct **for Haiku 4.5**
(USD 4.17 at the same volume). `config/business.yaml:73` even carries the comment "For very
high call volume you can switch to claude-haiku-4-5 for lower cost/latency" — the cheaper
model was considered, written down as an option, and never selected. The estimate priced the
option; production ships the default.

## The measurement

One session, the only one in the database: `comfortec:webchat:ff3775bca2982cc9`,
2026-07-25, 3 turns, outcome `answered`, model `claude-opus-4-8`.

| Turn | Input tokens | Output tokens |
| ---- | ------------ | ------------- |
| 1    | 3,951        | 137           |
| 2    | 4,112        | 115           |
| 3    | 4,246        | 67            |
| **Total** | **12,309** | **319**    |

The shape matters more than the total. Input grows ~150 tokens a turn while the first turn
already costs 3,951, so roughly **3,900 tokens of system prompt plus tool definitions are
re-sent on every single turn** and the actual conversation is the rounding error. A
"conversation" is not a few thousand tokens as `cogs-per-tier.md` assumes; it is the prefix
multiplied by the turn count.

Caveat, stated plainly: **n = 1.** Three turns is a short conversation and this one asked
about zonnepanelen, prices and whether the agent was human. It fixes the per-turn prefix
cost, which is the dominant term and is structural. It does not fix the average turn count,
and the model scales linearly in that.

## Priced at current rates

Anthropic first-party rates, from the `claude-api` skill's pricing table (cached 2026-06-24).
Same 12,309 input / 319 output, no caching:

| Model | In $/MTok | Out $/MTok | Per conversation | 300 conversations |
| ----- | --------- | ---------- | ---------------- | ----------------- |
| Opus 4.8 (**what ships today**) | 5.00 | 25.00 | $0.0695 | **$20.86** |
| Opus 5 | 5.00 | 25.00 | $0.0695 | $20.86 |
| Sonnet 5 (list) | 3.00 | 15.00 | $0.0417 | $12.51 |
| Sonnet 5 (intro, t/m 2026-08-31) | 2.00 | 10.00 | $0.0278 | $8.34 |
| Haiku 4.5 | 1.00 | 5.00 | $0.0139 | **$4.17** |

Output is 2.6% of the token count and 11% of the cost. Anything that shortens replies is
not the lever; the prefix is.

## Prompt caching: the lever, with two traps

`grep -rl cache_control app/` returns nothing. **No prompt caching is implemented.** The
~3,900-token prefix is stable across every turn and every client, which is exactly the shape
caching exists for. Cache write costs 1.25x base (5-minute TTL) or 2x (1-hour); cache read
costs ~0.1x.

Opus 4.8 with 5-minute caching, same session: **$0.0393 a conversation, $11.79 at 300** —
43% off, not the 90% the read multiplier suggests. Two reasons, and both are traps worth
knowing before anyone budgets on the 90%:

1. **The TTL is shorter than the gap between conversations.** 300 conversations a month is
   ~10 a day; they are hours apart, so each one pays its own cache write and only turns 2+
   read from it. The saving is intra-conversation. It improves with turn count and with
   volume, so it gets *better* as a client gets busier, which is the right direction.
2. **The minimum cacheable prefix is model-dependent and not monotonic.** Opus 5 caches from
   512 tokens, Opus 4.8 from 1,024 — but **Haiku 4.5 requires 4,096, and our prefix is
   ~3,900.** Below the minimum, caching silently does nothing: no error, just
   `cache_creation_input_tokens: 0`. So "move to Haiku and add caching" does not compose at
   the current prompt size. Haiku alone is still the cheapest option on the table; Haiku plus
   caching would need the prefix to cross 4,096 tokens, which is the opposite of the usual
   advice.

Order of operations, cheapest first: pick the model deliberately, then cache. Do not cache
first and assume the model no longer matters.

## Hetzner: both figures were wrong, in the same direction

U12 says "Hetzner amortised at 30 clients/box is EUR 0.50, at 10 clients EUR 1.50, at 1
client ~EUR 15", which implies a EUR 15/mo box. `docs/08-tech/infra-setup.md:266` and
`stack-decisions.md:15` both price the actual box: **CX22 at EUR 3.79 plus a 40 GB volume at
EUR 1.60 = EUR 5.39/mo.**

| Clients on the box | Per client |
| ------------------ | ---------- |
| 30 | EUR 0.18 |
| 10 | EUR 0.54 |
| 5  | EUR 1.08 |
| 1  | EUR 5.39 |
| 0  | EUR 5.39 of fixed overhead, and not COGS at all |

So `cogs-per-tier.md`'s EUR 0.50 overstates by ~3x and U12's EUR 15 overstates by ~3x. The
line is too small to matter either way, which is the finding: **it is not worth modelling.**
At 0 paying clients the box is overhead, and it belongs in the fixed-cost section rather than
in per-client COGS.

## Still unverified

**WhatsApp, EUR 3.00.** U12 named this the prime suspect and it stays unverified: this
session's web-search budget was exhausted before it could be checked, and I will not put a
number here I did not read. What has to be confirmed, in this order:

1. Whether Meta's 2025 shift to per-message pricing removed the free-entry service
   conversation the EUR 3.00 line depends on.
2. Current NL per-message rates by category (utility / authentication / marketing).
3. Whether the BSP in front of it (CM.com or Twilio) adds a per-message margin on top.

Also unmeasured, and all small: Neon, Cloudflare, Resend, and the Dutch number lease. None of
them is a plausible EUR 3.00 error the way WhatsApp is.

**Compleet is not costed here at all.** Its dominant line is TTS and the voice stack is not
live; U6 already records that both live offers are served by a vendor ElevenLabs agent rather
than the LiveKit stack the EUR 35 assumes, and that DRS at 1,500 included minutes is ~72% GM
rather than 93%. Nothing in this file changes that.

## Corrected Chat COGS

Chat at EUR 299, 300 conversations, the Claude line measured and everything else left as it
was pending the WhatsApp check. Rates are USD; the EUR figure moves with the rate, which is
itself a small unhedged FX exposure nobody has written down.

| Model shipped | Claude API | Rest of the stack (unverified) | Total | GM at EUR 299 |
| ------------- | ---------- | ------------------------------ | ----- | ------------- |
| Opus 4.8, no caching (**today**) | ~$20.86 | ~EUR 7 | ~EUR 26 | **~91%** |
| Opus 4.8 + caching | ~$11.79 | ~EUR 7 | ~EUR 18 | ~94% |
| Haiku 4.5, no caching | ~$4.17 | ~EUR 7 | ~EUR 11 | ~96% |

The headline number survives: Chat is a high-gross-margin product at every model choice, and
96.7% was never wildly wrong. What changes is that the margin is a **decision**, not a
property. Today's default quietly spends 5x the estimate, and nobody would have noticed,
because a per-client token bill is only visible if something looks at it.

## What to do about it

1. **Decide the model per tier, in writing.** Opus 4.8 for a demo that must impress and Haiku
   for volume is a defensible split; shipping Opus everywhere by scaffold default is not a
   decision, it is an omission.
2. **Implement prompt caching** on the ~3,900-token prefix, then verify with
   `usage.cache_read_input_tokens`. If it reads zero, the prefix is either below the model's
   minimum or something volatile is being interpolated into it.
3. **Record the per-client token spend** where a human sees it. `analytics.py` already stores
   `input_tokens`, `output_tokens` and `model` per session and per turn, so the data exists;
   nothing reports on it. One line on the status dashboard closes the loop that let a 5x
   overspend sit unnoticed for three weeks.
4. **Finish the WhatsApp check** with the three questions above, and re-run this file's Chat
   table afterwards.
