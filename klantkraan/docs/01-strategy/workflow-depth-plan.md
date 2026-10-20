# Workflow depth — how to approach it

**Date:** 2026-07-28 · **Decides:** sequencing, gates, and what gets tested before anything gets built.

Companion docs. Why: `research/automation-expansion-2026-07.md`. What to build: `ai-receptionist/docs/WORKFLOW-MOAT.md`. This is the _how_ — the order, the gates, and the things that must start early because someone else controls the clock.

---

## The shape of this plan

Two rules drive everything below.

**Gates, not dates.** Every phase has an entry condition, an exit condition, and a kill criterion. Nothing is scheduled by calendar, because client count is the real clock and it is not under our control. The only date-driven items are the three in §2, where an external party sets the deadline.

**Founder hours are the bottleneck, not build hours.** At 3–7 h/week the scarce resource is the founder talking to clients — selling, onboarding, asking questions. Code is comparatively cheap. So every phase below states what it costs _the founder_, and the plan is arranged to spend as few of those hours as possible before the riskiest assumption is tested.

---

## 1. Test the load-bearing assumption first, by hand, this month

Everything downstream of a booking depends on one unproven belief:

> **A Dutch trade owner will reply to a bot that messages him at the end of the day.**

If that holds, the owner channel supplies the job state and the whole roadmap works with zero integrations. If it does not hold, `completed` / `quoted` / `invoiced` never get set, every module after stage 1 has no trigger, and the build order in `WORKFLOW-MOAT.md` is wrong from stage 2 onward. It is the single highest-consequence unknown in the plan and it can be tested for **under an hour of total founder time and no code at all.**

### The 14-day closeout test

With the first pilot client, from the day they go live, the founder sends the closeout message **by hand** from WhatsApp at ~17:30 on working days:

```
2 klussen vandaag. Klaar?
1. Van Ostadestraat 44 — lekkage keuken
2. Bilderdijkkade 12 — cv-onderhoud
```

The jobs come from what the bot booked, so the list takes a minute to assemble. Ten working days.

| Measure                      | Read as                                                                                                                                     |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Replies on **≥7 of 10 days** | Green. Build the owner channel.                                                                                                             |
| Replies on 4–6 days          | Amber. The message is wrong, not the idea — try morning-after instead of end-of-day, or shorter. Re-run once.                               |
| Replies on **≤3 days**       | Red. Stop. State has to come from somewhere else, and the build order changes (calendar inference + one-tap confirm, or integration-first). |

Also record: how long until they reply, whether the reply is parseable without a follow-up question, and what they volunteer beyond the answer. The last one is free product research.

This costs ~5 minutes a day, needs nothing built, doubles as a relationship with the pilot, and produces case-study material either way. **It is the first thing to do and it does not wait for anything.**

---

## 2. The three clocks someone else controls

These are the only date-driven items. All three are waiting-time rather than work-time, so start them early and let them run in the background.

### a. Production WhatsApp sender — critical path for every outbound module

Currently on the **Twilio sandbox** (`ai-receptionist/docs/CHANNELS.md`). The sandbox cannot send approved templates to real customers, so it cannot run a single outbound module. Going live needs a Twilio WhatsApp sender: a business number approved by Meta, which means Meta Business verification with the KvK details.

The code does not change — only Twilio config. But verification has lead time measured in days-to-weeks and can bounce for paperwork reasons. **Start this as soon as the KvK/BTW numbers exist** (already an open box in `TODO.md` §D). It blocks Phase 2 entirely, so it must not be discovered late.

### b. Template approval queue

Five generic Dutch **utility** templates with variable slots, submitted once and reused across every client — never per-client, or every onboarding waits on Meta. Writing them is an hour; approval is the queue. Can only be submitted once (a) exists.

Draft: quote follow-up ×2 (different tone), appointment reminder, review request, invoice reminder. Every one written as a transaction status, never an offer — that is what keeps them in the €0.03 utility band instead of the €0.16 marketing band, and clear of the Forbidden list.

### c. Meta's 1 October 2026 billing change — model it by mid-September

From 1 Oct 2026 Meta charges per business message **including service replies inside the 24-hour window**. This hits the €299 core product, not the modules: an active client sends on the order of 1,600 service messages a month. The ~97% gross margin in `07-finance/` is stated on today's rules and will be wrong.

Deadline: re-model `07-finance/` by **mid-September**, once Meta publishes the service rate. Do not guess it now. If the number is bad, the answer is probably a fair-use ceiling in the contract rather than a price rise — decide then, with the real figure.

---

## 3. The phases

### P0 — Sell the depth, build nothing

**Entry:** now. **Exit:** 3 paying clients.

The receptionist has no paying client yet (`TODO.md` item E). Building the office layer before the front desk has proof produces two unproven products and no revenue.

What happens in P0:

- **Reposition the story.** Site and deck move from "de AI-telefoniste" to **"het kantoor dat meedraait"**, with the office work shown honestly as roadmap, not as shipped features. Costs nothing, defends against the €99 floor, and reframes the €299 as an entry point rather than a ceiling.
- **Make every discovery call demand research.** One question, asked the same way every time: _"Als er één ding op kantoor vanzelf zou gaan — wat zou dat zijn?"_ Log the answer verbatim against the prospect in `app/pipeline.py` notes. Twenty answers pick module 1 better than any analysis in this repo.
- **Run the closeout test** (§1) with pilot #1.
- **Start clock (a)** and, once it lands, (b).

**Founder cost:** the closeout test (~1 h total) plus one extra question per call. Everything else is selling he is doing anyway.

**Exit gate:** 3 paying clients, a tally of what they asked for, and a green closeout test.

**Kill criterion:** if the receptionist alone cannot get to 3 paying clients, workflow depth is not the problem and this plan is not the fix. Go back to the wedge.

---

### P1 — Ship the owner channel

**Entry:** 3 paying clients + green closeout test. **Exit:** one client replying to the automated closeout for 2 consecutive weeks.

Build stages 0, 0b from `WORKFLOW-MOAT.md`: `job_store.py`, `messaging.py`, the role split, `TOOLS_OWNER`, and the daily closeout in the worker.

The reason this is P1 and not plumbing buried in P2: **the owner channel is itself the first visible piece of the office layer.** The client gets a daily summary of their own jobs and answers in one line. It is the smallest thing that makes "het kantoor dat meedraait" true, it is what every later module triggers on, and it starts the daily contact that makes cancelling awkward.

It also starts the data asset. Every job gets an outcome labeled by the person who did it, with no data entry.

**Founder cost:** low. Mostly reviewing the closeout copy and watching one client use it.

**Exit gate:** two weeks of a real client replying to a message no human sent.

**Kill criterion:** they replied to the founder but not to the bot. That is a signal about who they think they are talking to, and it means the closeout needs the founder's name on it, or it needs to be a nudge that a human follows up on.

---

### P2 — The money module

**Entry:** P1 exit + production WhatsApp sender live + templates approved. **Exit:** a number.

Build the module the P0 tally chose. Default, absent a clear signal, is **offerte-opvolging** — it sells on revenue won rather than time saved, needs no accounting integration, and is the stage with the most money sitting in it.

Give it **free to the first three clients** in exchange for permission to publish the numbers. This is the same trade as the founding-member offer: they are buying proof nobody else in the Dutch market has, and per `competitor-landscape-2026-07.md` not one rival proves with a real trade business.

**The exit gate is a measured number, not a shipped feature.** Specifically: quotes that converted after a nudge, against that client's own baseline from before. If it cannot be stated as _"€X in klussen die anders waren blijven liggen"_, it is not done, because that sentence is the entire €599 sales argument.

**Founder cost:** medium — three clients to brief and a baseline to establish with each.

**Kill criterion:** module works, nudges send, nothing converts. Then quote follow-up is not the money and the tally's #2 gets the same treatment. Do not build #3 on faith.

---

### P3 — Package and price

**Entry:** P2 produced a number. **Exit:** first client paying €599.

- Launch **Kantoor €599** (Chat + offerte-opvolging + reminders + reviews), per `research/automation-expansion-2026-07.md` §4.
- **Upsell existing clients first.** They have the before/after, and the conversation lands in months 2–3 — the documented churn window, which is exactly when a client needs to see something new arrive.
- New-client acquisition stays at €299. The ladder does the selling; the entry price does not move.
- Update `01-strategy/offer-and-pricing.md`, `/prijzen`, and the calculator in one pass.

**Founder cost:** the upsell calls. This is the phase where the plan pays him back.

---

### P4 — Deepen

**Entry:** ~10 clients. **Exit:** none — this is the normal-operations state.

Module 2 (onderhoudsherinneringen — the one that creates recurring revenue _for the client_, so it is the hardest to cancel), then the Moneybird connector, then invoice chasing.

By this point real demand will have re-ranked everything and this document will be a year stale. **Trust the tally over this plan.**

---

## 4. The rules that keep it a product

Carried from `research/automation-expansion-2026-07.md`, restated because this is where they get broken:

1. **A module ships only if it works for every client from a config field.** Client-specific Python means it is a project, and the answer is no.
2. **Build module N+1 only when three paying clients have asked for it.** The tally decides, not the roadmap.
3. **Standalone by default.** Every module must work with zero integrations. The smallest trades have no system at all, and for them the automation _is_ the system.
4. **Two accounting integrations, maximum, in year one** — Moneybird first (much better API), e-Boekhouden second. A new connector needs three clients or one who pays for it knowing it becomes a product.
5. **Never integrate to become a feature of an FSM platform.** Read from Gripp/Robaws/Bouw7 if a client asks; never depend on one.
6. **Outbound is transactional only.** Every template reports a status. Never an offer, never a discount, always an opt-out.

---

## 5. What would make this plan wrong

Worth writing down now, while it is cheap to admit.

| Signal                                  | What it means                               | Response                                                                                                                                              |
| --------------------------------------- | ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| Closeout test comes back red            | Owners will not feed the bot state          | Whole build order changes — calendar inference + one-tap confirm, or integration-first. Re-plan before building.                                      |
| Module 1 ships and converts nothing     | The value story is wrong, not the execution | Try tally #2 once. If that also fails, the office layer is not worth €300/mo and €299 is the product.                                                 |
| A Dutch FSM platform ships this bundled | The wedge is closing faster than expected   | The counter is the no-migration position — Klantkraan works on WhatsApp for trades that will never adopt an ERP. Defend there, do not chase features. |
| Meta's October rate is punitive         | Core margin, not module margin              | Fair-use ceiling in the contract before a price rise.                                                                                                 |
| 3 paying clients never arrive           | Nothing in this document is the problem     | Stop. The wedge is the issue.                                                                                                                         |

---

## 6. Immediate next actions

In order. Only the first is urgent.

1. **Start the closeout test with pilot #1** the day they go live. No code, no dependencies.
2. **Get KvK/BTW numbers** (`TODO.md` §D) → start Meta Business verification for the WhatsApp sender. Long lead time, blocks P2.
3. **Ask the office question on every discovery call.** Log verbatim.
4. **Draft the five Dutch utility templates** so they are ready to submit the moment the sender exists.
5. **Mid-September: re-model `07-finance/`** against Meta's published service rate.

Nothing else starts until there are 3 paying clients.
