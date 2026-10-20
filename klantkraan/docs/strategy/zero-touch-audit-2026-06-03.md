# Zero-touch product audit

> **Update 2026-07-13:** pricing has since been decided at €299 (Chat) / €499 (Compleet), text-first. Numbers below are the historical 2026-06-03 snapshot — left intact.

> Date: 2026-06-03
> Source: Founder constraint — "the product needs to operate without recurring manual intervention. Ideally no support, customisation, or delivery work."

## TL;DR

**Klantkraan as currently designed is NOT a zero-touch product. It's a high-touch service wrapped in tech.** The 30-day onboarding playbook (`03-delivery/onboarding-30-day.md`) requires **2h 10m founder time per client**, and the churn-prevention playbook adds another **~45 min/client/month** ongoing (Loom recordings, case-study calls, prompt tuning, edge-case support). At 30 active clients, that's **23 hours per month just on retention** — before any sales, marketing, or admin work. At 50 clients you're past 35 hours/month and the founder is the bottleneck.

There are **three paths to zero-touch**, each with explicit trade-offs:

1. **Drop the voice tier. Sell SMS+reviews only.** Lowest engineering cost; ARPU collapses from €540 blended to ~€149.
2. **Build heavy self-serve infrastructure for voice.** 60-90 days of engineering. ARPU preserved. Quality risk on the AI receptionist edge cases that today are masked by founder intervention.
3. **Two-product split: DIY Lite + DFY Premium.** Run Klantkraan as a managed service (current design) for €599-849/mo with explicit human-touch promise, AND launch a separate self-serve "Klantkraan Lite" at €99-149/mo for SMS+reviews only. Customer self-selects.

**Recommendation: Path 2, combined with ruthless feature pruning.** Build the self-serve voice product, keep Tier 2 (€599) as the flagship, kill Tier 3 (custom integrations were never going to be zero-touch). Drop the founder Loom from churn prevention and replace with automated value emails. Accept that pilots 1-5 are manual while you're building the self-serve; transition is mandatory by client #10.

The rest of this document audits every touchpoint, classifies it, and proposes the specific build to eliminate it.

---

## 1. The full touchpoint audit

Every recurring founder activity in the current design, classified by automation status.

### 1.1 Pre-sale + sale

| Touchpoint                 | Current owner | Time/client | Status      | Automation path                                             |
| -------------------------- | ------------- | ----------- | ----------- | ----------------------------------------------------------- |
| Lead reply (WhatsApp/form) | Founder       | 5-15 min    | Manual      | AI BDR with Claude API, qualifies and books                 |
| Discovery call (20 min)    | Founder       | 20 min      | Manual      | Recorded sales video + structured Tally → if-qualified path |
| Offerte generation         | Founder       | 10 min      | Manual      | Self-serve pricing page → Mollie subscription link          |
| Contract signing           | Manual chase  | 5 min       | Semi-manual | Documenso/SignWell templated, auto-sent on signup           |
| Payment setup              | Founder       | 5 min       | Manual      | Mollie SEPA mandate self-serve at signup                    |

**Total pre-sale: ~45-55 min per closed deal**

### 1.2 Onboarding (the 30-day playbook)

| Day | Touchpoint                                   | Current time | Status | Automation path                                                    |
| --- | -------------------------------------------- | ------------ | ------ | ------------------------------------------------------------------ |
| 1   | Intake review + gap-fill via WhatsApp        | 15 min       | Manual | Tally → validate-and-prompt with AI for missing fields             |
| 2   | Kickoff call                                 | 15 min       | Manual | Skip; replace with 90-sec welcome video + auto-WhatsApp confirm    |
| 3   | Synthflow prompt fine-tune (regio/FAQ/tone)  | 30 min       | Manual | AI-generated prompt from intake + 3 templates per branche          |
| 5   | Founder test calls (5 scenarios)             | 20 min       | Manual | Synthetic test calls via Synthflow API + automated quality scoring |
| 7   | Prompt adjustments based on testbel feedback | 10 min       | Manual | Client self-edits 5 highlighted variables in dashboard             |
| 14  | Check-in call                                | 5 min        | Manual | Auto-NPS prompt in dashboard + email if score <8                   |
| 30  | Month-1 review + case-study Loom             | 45 min       | Manual | Auto-generated PDF report + opt-in case-study form                 |

**Total onboarding: 2h 10m per client (per the doc).**
**After full automation: ~15 min residual (edge-case escalations only).**

### 1.3 Daily / weekly operation (happy path)

These are ALREADY zero-touch in the current design:

- ✅ Synthflow handles incoming calls
- ✅ n8n sends missed-call SMS
- ✅ n8n sends review requests after marked-complete jobs
- ✅ Daily stats SMS to client owner (automated)
- ✅ Weekly Monday dashboard email (automated)
- ✅ Dashboard at `/r/[slug]` (auto-renders from Postgres)

**This is the part that works. Don't touch.**

### 1.4 Recurring retention (the hidden cost)

Per the churn-prevention doc:

| Touchpoint                            | Frequency       | Time/client        | Status                                                       | Automation path                                                                                     |
| ------------------------------------- | --------------- | ------------------ | ------------------------------------------------------------ | --------------------------------------------------------------------------------------------------- |
| Monthly Loom of top-3 recovered calls | Monthly         | 30 min             | **Manual — explicitly the highest-leverage retention asset** | Replace with auto-generated email: "Vandaag had je gesprek X om Y. Naar onze schatting was dat €Z." |
| Day-45 case-study capture call        | Once per client | 10 min             | Manual                                                       | Replace with auto-NPS + opt-in case-study form                                                      |
| Quarterly check-in calls              | Quarterly       | 15 min             | Manual                                                       | Auto-NPS at day 90/180/270 → only call if score drops                                               |
| Reactive WhatsApp support             | Variable        | 5-20 min/incident  | Manual                                                       | AI support agent on docs + community Discord                                                        |
| Edge-case Synthflow prompt tweaks     | Ad-hoc          | 10-30 min/incident | Manual                                                       | Self-edit dashboard for safe fields; AI assistant for complex                                       |
| Carrier-forwarding troubleshoots      | Ad-hoc          | 10-15 min/incident | Manual                                                       | Pre-recorded Loom library per carrier (already in onboarding doc) + AI support agent                |

**Realistic monthly load at 30 clients (per current design):**

- Monthly Loom: 30 × 30 min = 900 min = 15 hrs
- Quarterly check-ins (1/3 per month): 10 × 15 = 150 min = 2.5 hrs
- Support: ~30 incidents × 12 min avg = 6 hrs
- **Total: ~23.5 hrs/month at 30 clients on retention alone**

At 50 clients: ~39 hrs/month. **Founder becomes the bottleneck before MRR even hits €25k.**

### 1.5 Admin + finance

| Touchpoint             | Current owner        | Frequency        | Status               | Automation path                                                 |
| ---------------------- | -------------------- | ---------------- | -------------------- | --------------------------------------------------------------- |
| Monthly invoicing      | Mollie + Moneybird   | Monthly          | ✅ Auto (once wired) | —                                                               |
| Payment reconciliation | Moneybird            | Monthly          | ✅ Auto              | —                                                               |
| BTW return + ICP       | Founder + accountant | Quarterly        | Semi-auto            | Accountant handles; founder reviews                             |
| Churn off-boarding     | Founder              | Per cancellation | Manual               | Self-serve cancel button + auto data export + auto DPA wipe job |
| MRR / KPI review       | Founder              | Weekly           | Manual               | Auto-Slack weekly digest from Postgres                          |

---

## 2. The fundamental tension: voice AI is good, not perfect

This is the load-bearing assumption that determines everything downstream.

**What voice AI does well in 2026 (Synthflow class):**

- Standard inbound: name capture, problem description, postcode/huisnummer, callback scheduling
- Known FAQs from the prompt
- Stays within scripted flow for 80-90% of calls

**What it fumbles:**

- Strong dialects (Limburgs, Brabants, Twents) — degraded transcription
- Frustrated/angry callers — agent doesn't de-escalate as well as humans
- Multi-issue calls ("I have a leak AND need a quote for a new boiler AND...")
- High-stakes calls where misunderstanding costs €1.000+
- Background noise (caller on a construction site)
- Novel request types not in the prompt (e.g., "do you do solar panels too?")

**Per the existing risk register (`10-ops/risk-register.md`) and onboarding doc § "What can go wrong":**

> "Synthflow agent says wrong thing on first day | Daily review of first 50 calls, manual prompt tweak, redeploy in <30 min"

This is the founder's current safety net. **Eliminating this without replacing it is a churn risk.** The replacement options:

1. **AI-supervised AI** — a second LLM reviews call transcripts, flags low-confidence ones for the client (not founder) to review and adjust the prompt.
2. **Automatic fallback to human callback** — when confidence drops, the AI says "een collega belt u binnen het uur terug" and triggers an SMS to the client owner. Founder has zero involvement.
3. **Confidence-threshold call routing** — if the agent detects keywords/sentiment that signal trouble, route the call to the client's personal mobile immediately.
4. **Accept some failures + transparent SLA** — publish "the AI handles ~85% cleanly; ~15% fall back to your direct line" and let buyers self-select.

The honest answer: **a combination of 2 and 4**. Build the auto-fallback (low engineering effort, n8n + Synthflow webhook + CM.com SMS) and set expectations transparently.

---

## 3. Three strategic paths

### Path A: Drop voice. Sell SMS+reviews only.

**Product:** missed-call-back SMS, automatic review requests after marked-complete jobs, simple dashboard. No AI receptionist.

**Pricing:** €99-149/mo flat.

**Pros:**

- Truly zero-touch — n8n + CM.com + Postgres run themselves, no per-client config
- No voice AI edge cases to handle
- Onboarding shrinks to a Tally form + an automated CM.com number provision
- ~98% gross margin (per current COGS estimate)
- Scales to 500+ clients with no founder involvement
- Compliance simpler (no AI Act art. 50 exposure on voice)

**Cons:**

- ARPU drops from €540 blended to ~€129. At 20% churn, LTV drops from €27,900 → ~€6,400.
- You need ~4× more clients for the same MRR.
- Competitive moat is weak — SMS+review automation is commoditized.
- You'd be one of several similar products (Trustoo, Bouwgarant, etc.)
- The "AI receptionist that knows voorrijkosten" is the marketing wedge. Dropping it weakens the pitch.

**Verdict:** Viable as a _second_ product (see Path C). Not great as the only product.

### Path B: Build heavy self-serve for the full stack.

**Product:** identical to today, but every founder touchpoint is replaced by software.

**Engineering required (in order of effort):**

| Build                                                                           | Effort          | Eliminates                             |
| ------------------------------------------------------------------------------- | --------------- | -------------------------------------- |
| AI-generated Synthflow prompt from intake (Claude API + 3 branche templates)    | 1-2 weeks       | Day-3 prompt tuning, ongoing tweaks    |
| Self-serve dashboard config (8 safe fields: pricing, hours, FAQs, holiday mode) | 1 week          | Ongoing customer-driven prompt tweaks  |
| Auto-fallback on low-confidence calls (Synthflow webhook → SMS to client)       | 2-3 days        | Edge-case escalations to founder       |
| Automated test-call suite (5 synthetic calls per onboarding, quality-scored)    | 1 week          | Day-5 founder test calls               |
| AI support agent on docs (Claude on the docs/ folder)                           | 3-5 days        | Tier-1 WhatsApp support                |
| Pre-recorded carrier Loom library                                               | Already in plan | Forwarding troubleshoots               |
| Auto-value emails replacing Loom reviews (monthly stats with €-estimates)       | 1 week          | The 30-min/client/month Loom recording |
| Self-serve cancellation + auto data export                                      | 3-5 days        | Off-boarding                           |
| AI-generated case study draft (Claude on call transcripts + dashboard data)     | 1 week          | Day-45 case-study call                 |
| Self-serve onboarding wizard (15-min flow, no human)                            | 2 weeks         | Most of the 30-day playbook            |
| In-app NPS + auto-rescue triggers                                               | 1 week          | Check-in calls                         |

**Total: ~8-10 weeks focused engineering, doable in 12-14 calendar weeks alongside support of early pilots.**

**Pros:**

- Preserves €540 ARPU and the marketing wedge
- Voice AI as the differentiator stays
- Compounding asset: every fix improves the product for all current and future clients
- Founder eliminates self from the loop progressively

**Cons:**

- Hard. Lots of integration work. Each piece has edge cases.
- AI-generated prompts can produce worse Synthflow quality than founder-tuned (in early phase)
- The "founder personally tunes your agent" promise becomes a lie if it's actually AI-generated. Be honest about it in copy.
- During the build, you're still doing the manual work for pilots 1-10.

**Verdict:** This is the right path if voice is the moat. **But sequence matters.** Build the highest-leverage automations first (auto-value emails, AI prompt generation, self-serve config), don't try to ship all 11 builds before reaching customer #5.

### Path C: Two-product split — DIY Lite + DFY Premium

**Lite (zero-touch):** SMS + reviews + basic dashboard. €99/mo. Self-serve. No human contact ever.

**Premium (managed):** Voice AI + custom onboarding + monthly founder Loom + quarterly review calls. €849-1,499/mo. Positioned as a managed service.

**Pros:**

- Zero-touch product exists immediately (Lite is easy to build)
- Premium captures the "founder hands-on" buyers at higher ARPU than today
- Customer self-selects; you don't have to defend either positioning
- Premium funds the engineering needed to gradually move Premium → Lite features

**Cons:**

- Two products = two marketing pages, two sales motions, two onboarding flows
- Premium ARPU has a ceiling because there's only one of you (~30 Premium clients = full-time)
- The "Klantkraan brand" gets split-personality risk
- Founder still has the same retention burden on Premium; just at higher per-client revenue

**Verdict:** A good _transitional_ model. Use Premium as a profitable bridge while building Lite. Long-term, migrate everyone toward Lite as it matures.

---

## 4. Recommended path: B + ruthless pruning + transitional pricing

The right answer is **Path B with three modifications**:

### 4.1 Prune the product first

Before building anything: **decide what to KILL.**

| Feature                                   | Action                                                                                                                    |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Tier 3 Max (€849) — custom integrations   | **Kill.** Custom integrations were never going to be zero-touch. Anyone who needs them buys consulting from someone else. |
| Monthly founder Loom reviews              | **Kill.** Replace with auto-generated stats + sample-clip emails.                                                         |
| Day-45 case-study capture call            | **Kill.** Replace with auto-form after 60 days.                                                                           |
| Founder fine-tuned prompts                | **Kill.** Replace with AI-generated prompts + 8 self-editable fields.                                                     |
| 15-min kickoff call                       | **Kill.** Replace with 90-sec welcome video + WhatsApp confirm.                                                           |
| Founder testbellen                        | **Kill.** Replace with automated synthetic test calls.                                                                    |
| "Spreek de oprichter" promise on the site | **Reframe.** Keep it for sales, but explicit that it's pre-sale only. Post-sale support is the AI agent + Discord.        |

This is the **single most important step.** Every feature you keep is a touchpoint to automate or maintain. Ship a smaller product.

### 4.2 Build the 6 highest-leverage automations first

In sequence, with rough effort and ROI:

1. **AI-generated Synthflow prompts** (1-2 weeks) — eliminates the biggest per-onboarding cost. Use Claude API + 3 branche templates + 8 intake fields. Output a working prompt that's 90% as good as founder-tuned, plus a "preview & approve" button for the client.
2. **Auto-fallback on low-confidence calls** (3 days) — eliminates the highest support-cost category (edge-case calls). Synthflow webhook on low-confidence transcript → CM.com SMS to client → AI says "een collega belt u binnen het uur terug."
3. **Self-serve onboarding wizard** (2 weeks) — eliminates the kickoff call + intake review. 15-min flow: Tally form → AI prompt generation → preview → forwarding instructions (carrier-specific Loom library) → go-live.
4. **AI support agent on docs** (3-5 days) — eliminates Tier-1 WhatsApp tickets. Claude API on the `docs/` folder + transcripts of past founder DM responses.
5. **Auto-value emails** (1 week) — eliminates the monthly founder Loom. Cron job: query Postgres for top-3 recovered calls in the past 30 days, compose email with concrete €-estimates, send via Resend.
6. **Self-serve cancellation + data export + DPA wipe** (3-5 days) — eliminates churn off-boarding. Button in dashboard → triggers Mollie cancel + n8n export + scheduled wipe.

**Total: ~7-8 weeks engineering. ~80% of founder touchpoints gone.**

### 4.3 Transitional pricing during the build

While you're at clients 1-10 and the automation isn't done yet:

- Charge €599 (Pro tier) as "managed setup" — explicit that you do the onboarding hands-on for the first month
- After day 30, drop to €399/mo "self-serve mode" if they don't want continued hands-on (most won't — they don't actually want monthly Loom reviews, they just want the product to work)
- This is honest: high price during the manual phase, lower price once it's truly self-serve

By the time you hit client #20, the price should be a flat €349/mo with zero "managed" promise. The brand becomes "the SaaS for vakmensen", not "the founder who'll tune your agent."

---

## 5. What you'll have to give up

This is the hardest part. Zero-touch costs you specific advantages:

| What you lose                                         | Why it hurts                                                                                            | Worth it?                                                                                                                                                                            |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **The "founder personally tunes your agent" promise** | This was the differentiation against US tools (Podium etc.)                                             | YES — at scale, this promise becomes a lie anyway                                                                                                                                    |
| **The Tier 3 Max revenue**                            | ~15% of mix at €849 = ~€127/blended-ARPU                                                                | YES — Tier 3 was always going to be a manual loss-leader                                                                                                                             |
| **The monthly Loom retention asset**                  | Churn-prevention doc calls this the "single highest-leverage retention artifact in the entire business" | RISKY — replace with auto-value emails and _measure churn impact_. If churn rises >2pp, rebuild a semi-automated Loom (AI-generated from call transcript + 30-sec founder voiceover) |
| **The personal touch in sales**                       | Discovery calls convert well                                                                            | YES — replace with self-serve trial + Mollie self-checkout. Conversion will drop, but volume will scale.                                                                             |
| **High blended ARPU**                                 | €540 → probably €299-349 once Tier 3 is killed and Pro becomes self-serve                               | NEUTRAL — at scale, this is fine. The math (LTV/CAC) still works at €299.                                                                                                            |
| **The control over voice quality**                    | Each manual prompt tune protected against fumbles                                                       | RISKY — needs the auto-fallback as a safety net                                                                                                                                      |

---

## 6. Honest revised economics under zero-touch

Comparison: current design vs. zero-touch Path B + pruning.

| Metric                       | Current design               | Zero-touch (Path B)                                 |
| ---------------------------- | ---------------------------- | --------------------------------------------------- |
| Tier mix                     | 30% Lite / 55% Pro / 15% Max | 40% Lite / 60% Pro / 0% Max                         |
| Blended ARPU                 | €540                         | €299                                                |
| GM                           | 95%                          | 92% (AI generation + storage costs slightly higher) |
| Founder time per client / mo | ~45 min                      | ~5 min (residual edge cases only)                   |
| Onboarding founder time      | 130 min                      | 0 min                                               |
| Realistic ceiling            | 50 clients before bottleneck | 500+ clients before bottleneck                      |
| MRR for breakeven            | ~€4,700 (~9 clients)         | ~€4,700 (~16 clients)                               |
| MRR at the ceiling           | ~€27k (current)              | ~€150k (zero-touch)                                 |
| LTV / CAC at €200 CAC        | 140×                         | ~78×                                                |
| Time to first €10k MRR       | ~M5-6                        | ~M8-10 (more clients needed)                        |
| Risk profile                 | Hits founder ceiling fast    | Long ramp but no ceiling                            |

**Take-away:** zero-touch is _slower_ to revenue per client but has _no ceiling_. It's the right model if you want a real software business. The current high-touch model maxes out at a higher per-client revenue but caps you at a 30-50 client bottleneck.

---

## 7. The 90-day build sequence

Weeks 1-2: **AI-generated Synthflow prompts.**

- 3 templates per branche (loodgieter, dakdekker, elektricien)
- Claude API call with intake form data → fills in 12 variables
- Preview & approve UI in client dashboard
- DELIVERS: eliminates Day-3 founder time (30 min × N clients)

Week 3: **Auto-fallback on low-confidence calls.**

- Synthflow webhook → confidence score parsing → if < threshold, SMS client owner
- Documented as "the human safety net" in the FAQ
- DELIVERS: eliminates ~80% of edge-case support tickets

Weeks 4-5: **Self-serve onboarding wizard.**

- Tally intake → n8n → CM.com number provision → Synthflow agent creation → forwarding Loom → "ready" page
- 15 min end-to-end, no human in the loop
- DELIVERS: kills the 2h 10m playbook entirely

Week 6: **AI support agent.**

- Claude API on `docs/` folder + 100 sample WhatsApp answers
- Embedded in dashboard widget + WhatsApp Business Bot
- Escalation to founder only if AI confidence < threshold
- DELIVERS: eliminates ~70% of Tier-1 support load

Weeks 7-8: **Auto-value emails replacing Loom.**

- Cron: query Postgres → top-3 calls → €-estimate → Resend
- DELIVERS: eliminates the monthly 30-min/client/month retention work

Weeks 9-10: **Self-serve cancellation, data export, DPA wipe.**

- Button in dashboard → Mollie cancel → n8n export → scheduled wipe job
- DELIVERS: closes the loop; no human touch needed at any lifecycle stage

Weeks 11-12: **Migrate the first 10 manual clients to the new self-serve plumbing + drop pricing to the new flat €349.**

---

## 8. What stays manual forever (the irreducible 5%)

Even after Path B is fully built:

- **Initial brand trust** — for the first 50-100 clients, the founder needs to be visibly present in LinkedIn posts, occasional client calls, public appearances. Not "support work" — this is marketing / brand work. Build into the personal LinkedIn cadence.
- **Carrier-specific weirdness** — KPN Zakelijk VoIP has edge cases the Loom can't cover. Allocate ~2 hrs/month forever.
- **Edge legal/compliance** — AVG complaints, AP audits, GDPR DSARs. Allocate ~2 hrs/quarter.
- **Major product decisions** — pricing changes, new features, new branches. Not recurring; bursty.

Total irreducible: maybe **5-10 hrs/month at any scale**. That's the asymptote.

---

## 9. The single hardest question

**Are you willing to give up the "founder-touch" brand promise?**

That promise is in your marketing copy, in `/over`, in the discovery script, in the offerte template. It's what differentiates you from US tools. Removing it costs you a specific kind of buyer.

The replacement positioning is: **"Built by one Dutch ICT founder, runs by itself. AVG-by-default, EU-hosted, monthly cancelable, real product not a service."** That's still differentiated against Podium et al — they're foreign + lock-in + no AVG. You don't actually need the personal-touch claim to win Dutch trades.

Decide this before writing line one of code.

---

## 10. Recommended next decisions

If you commit to Path B:

1. **Update `09-brand/voice-and-tone.md`** to remove personal-touch positioning. Reframe as "product" not "service."
2. **Update `01-strategy/offer-and-pricing.md`** to kill Tier 3 and document transitional pricing.
3. **Update `03-delivery/onboarding-30-day.md`** to either delete or label as "manual mode for clients 1-10 only."
4. **Update `03-delivery/churn-prevention.md`** to swap manual Loom for auto-value email.
5. **Build the AI-generated Synthflow prompt service first** — single highest-leverage automation.

If you're not sure: pilot one client _with the current manual playbook_. Track exact time spent. Validate or invalidate the 2h 10m assumption with a real data point before committing to the engineering investment.

---

## Sources consulted

- `docs/03-delivery/onboarding-30-day.md` (the 2h 10m founder-time benchmark)
- `docs/03-delivery/churn-prevention.md` (monthly Loom asset + churn signals)
- `docs/07-finance/unit-economics.md` (ARPU, COGS, GM, LTV/CAC)
- `docs/01-strategy/offer-and-pricing.md` (tier definitions)
- `docs/03-delivery/synthflow-system-prompt.md` (the per-client config burden)
- Real-world references implicit in the analysis: ServiceM8 / Tradify / Jobber (self-serve trade SaaS patterns), Calendly / Loom / Tally (self-serve B2B SaaS patterns), Podium / Goodcall / Numa (current voice-AI competitive set).
