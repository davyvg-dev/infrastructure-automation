# First clients: pricing strategy + operational reality

**Date:** 2026-07-24 · **Method:** deep-research harness (adversarial 3-vote verification). Pilot/pricing, GDPR and liability claims are triple-verified (marked ✓ 3-0). Cost-to-serve figures are source-extracted (vendor/blog) and directional, not all triple-verified — the margin gap is large enough that the conclusion holds regardless.

---

## Q1: Should the first ~5 clients be free? No — charge, but discount.

The most one-sided finding in the research. YC, SaaStr/Lemkin, Atlanta Ventures and practitioner sources all agree; the "give the first 1–2 away free" counter-claim was **refuted** in verification.

- **YC (✓):** *"If you don't charge your customers, they are not a customer, and you don't have a company."* For B2B: *"you should not offer free trials in B2B sales. Go for a money-back guarantee and the ability to opt out instead."* A prospect who won't pay is *"a great sign you should move on to the next customer."*
- **Jason Lemkin / SaaStr (✓):** *"Charge for any true pilot. If you don't charge, it's not a pilot. It's an extended demo."* · *"I almost never see 'Free Pilots' convert to paid. They are usually a sign of desperation."*
- **Commitment, not the money, is the point (✓):** *"A customer paying €50 for a €100 product is a far more valuable customer for validation than one paying €0."* Payment screens for motivated buyers and makes them actually use it and give honest feedback. Free-pilot users under-engage and feel social pressure to be positive → you learn nothing real, which defeats the whole "get a feel for it" goal.
- **Protect long-term pricing (✓):** habitual discounting anchors value low forever, but a *named, time-limited* "founding member rate" protects future full price.

### The "pro move" deal structure (✓, YC sales playbook)
> A recurring monthly contract with a **30–60 day money-back / opt-out period** at the start that **auto-converts to full recurring revenue** if the client does nothing and is happy. One sales process, not two.

### Concrete play for the first 5
- **Oprichtersklant (founding-member) rate**, explicitly time-boxed: e.g. **€149/mo for 6 months** on the €299 Chat tier, then steps to standard. Framed as founding-member, not an open-ended discount.
- **30-day money-back guarantee** instead of a free trial.
- **Trade the discount for non-cash value, written into the deal:** testimonial, case study with real numbers (leads captured, calls not missed), and a reference call for the next prospect.
- **Zero €0 clients.** A trade that won't pay €149 for 24/7 lead-capture was never going to pay €299.
- Fits the existing `pipeline.py sign` gate — the founding rate is a config price, not a code change.

---

## Q2: What it actually takes to run this

### (a) Cost-to-serve — text is the quiet superpower

**Voice (€499 Compleet):** managed voice stacks run **$0.25–0.50/min all-in** (STT + LLM + premium TTS + telephony; advertised "$0.05/min" is fiction). *"Most AI voice deployments at moderate scale cost $400–1,200/month in usage"* — enough to **fully consume or exceed a flat €499/mo plan** at real volume. TTS (ElevenLabs $0.03–0.10/min) is the biggest line item. → **Meter voice minutes or cap them; don't sell flat €499 to a heavy-call client.**

**Text (€299 Chat) — structurally high margin:**
- **Inbound WhatsApp is effectively free.** Since Jul 2025 WhatsApp is per-message, but user-initiated service replies inside the 24h window are free and inbound messages carry no Meta cost. Twilio (BSP) markup ≈ **$0.005/message** — a rounding error at a trade's volume.
- **LLM (Claude Sonnet-tier, $3/M in, $15/M out):** a bot doing **1,000 conversations *per day*** costs ~$2,070/mo (less with caching). A single loodgieter does ~10–40 conversations *per day* → **per-client Claude cost is single-digit-to-low-double-digit €/month.** Keep the static-prompt caching CLAUDE.md already mandates (~90% off the cached prefix).
- **Bottom line: the €299 text tier is genuinely 90%+ gross margin per client.** That's a strength to defend, not apologize for versus €99–149 voice rivals.

### (b) Operating 24/7 solo
The service is 24/7 but you aren't. What matters is **graceful failure**, not five-nines: when the API is down or the bot is unsure, it must fall back to *"ik laat iemand je zo snel mogelijk terugbellen"* and capture the lead — never go silent or hallucinate. The outage watchdog is table stakes; **deploy it, don't just commit it.** Set contract SLA expectations low ("best-effort, lead always captured") so one 2am outage isn't a breach.

### (c) Onboarding effort — budget more than the tokens
A verified reference point: a single B2B pilot ≈ **27 founder-hours** (8h setup + 3h/week × 5 + 4h review) before engineering. A solo automation founder who charged a flat $500 saw her effective rate **collapse below $10/hr** once discovery, data-gathering and integration were counted. **The real cost is onboarding labor, not API spend.** Standardize a per-trade starter config (loodgieter, dakdekker) so onboarding is *editing*, not *building* — the config-file-per-client architecture already supports this; protect it.

### (d) Failure modes & liability — the one that can actually hurt
- **You are liable for what the bot says. (✓)** *Moffatt v. Air Canada*: the tribunal held the company responsible for its chatbot's wrong info and **rejected** the "chatbot is a separate entity" defense. Correct info elsewhere on the site was **no defense**.
- **Five hallucination failure modes to hard-block:** inventing policies, inventing prices/discounts, making binding promises/SLAs, describing services not offered, giving medical/legal/financial advice.
- Klantkraan's system-prompt rule ("only offer slots `check_availability` returned — never invent times, prices, or advice") is exactly right. **Never let the bot quote a firm price or promise a firm appointment time it can't verify** — for a trade, a wrong price quote is a real dispute. Keep a **human in the loop on anything binding.**

### (e) Why SMB clients cancel
- **Standalone = easy to cancel; embedded = sticky.** Can't bundle with UCaaS, but embed into their daily workflow (their calendar, their WhatsApp, their lead notifications) so ripping it out hurts.
- **Silent failure = surprise churn.** A green "health score" while delivery quietly fails is a known churn driver. **Ship a weekly per-client "here's what the bot captured for you" digest** — the daily-digest oversight slice already built is a retention tool.
- **Time-to-value (✓):** onboarding must hit the "aha" fast. For a trade, the aha is the first real lead captured at night. Make week 1 produce a visible captured lead.

### (f) AVG/GDPR — mandatory, and it's on you
- **A DPA (verwerkersovereenkomst) with every client is legally mandatory (✓).** The Dutch AP: both controller and processor are liable if it's missing (Art. 28(3)). Klantkraan = processor; the trade = controller.
- **Sub-processors need prior written permission and you stay fully liable for them (✓, Art. 28(4)).** List them in the DPA: **Anthropic/Claude, Twilio/WhatsApp, Hetzner/hosting** — get client sign-off.
- **On offboarding you must delete or return all personal data (✓).** Configure conversation retention short (guidance: never-to-1-year, short = better for data minimisation).
- **This is also a sales weapon:** ready-made DPA + short retention + EU hosting is a story most voice rivals don't foreground. Bundle it into the close pack.

### (g) The lesson founders repeat
> *"Automating a broken process amplifies the dysfunction."* A studio that automated a broken intake ended up emailing non-clients; the founder spent more time cleaning up than doing it manually.

**Do the receptionist's job manually (or shadow the client's intake) for a few days before going live.** Configure from observed reality, not assumption.

---

## Recommendation for the first 5
1. **No free clients.** Founding-member rate: **€149/mo for 6 months on Chat, 30-day money-back, auto-converts to €299.** Trade the discount for testimonial + case-study numbers + reference call, in writing.
2. **Sell text as the hero** (high-margin, low-risk, EU-compliant); voice as a metered upsell — no flat €499 to heavy-call clients without a minute cap.
3. **Shadow each client's intake for a few days before going live.**
4. **Ship the weekly value digest** — the #1 retention lever.
5. **DPA + sub-processor list + short retention from day one**, and make it a selling point.

## Pre-launch checklist (before client #1 goes live)
- [ ] DPA / verwerkersovereenkomst template (NL), sub-processors listed: Anthropic, Twilio, Hetzner
- [ ] Conversation-data retention set short + client-offboarding deletion routine
- [ ] Bot hard-blocked from inventing prices / firm appointment times / advice (verify in `receptionist` system prompt)
- [ ] Graceful-failure fallback ("we bellen je terug") + outage watchdog **deployed** (not just committed)
- [ ] Founding-member agreement w/ money-back + testimonial clause
- [ ] Per-trade starter config so onboarding is editing, not building
- [ ] Weekly per-client digest enabled
- [ ] Art. 50 disclosure in the greeting confirmed live (also legally mandatory for everyone from **2 Aug 2026**)

## Sources
YC Library (how-to-get-first-customers, sales-playbook-for-founders), SaaStr/Jason Lemkin, Atlanta Ventures, Mercury, Headway, Autoriteit Persoonsgegevens (DPA guidance), American Bar Association (Moffatt v. Air Canada), PortaOne / Retell / RingLogix (voice cost), respond.io (WhatsApp pricing), benchmarks on LLM token cost. Full URL list in the round-2 research transcript.
