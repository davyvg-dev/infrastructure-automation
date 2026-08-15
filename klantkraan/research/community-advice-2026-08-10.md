# Community advice — 2026-08-10

Three pieces of outside advice the founder collected, with relevance to Klantkraan.

## 1. Voice-agent latency and crash debugging (Vapi-flavored, applies to our stack)

Advice: check the call logs; latency usually comes from the LLM step — a faster model drops
lag noticeably. Crashes usually trace to a tool call or webhook timing out.

Relevance:

- We already lived the latency half on ElevenLabs: the Gemini-pool glitches and erratic TTFB
  (0.5s-13.7s) drove the switch to claude-haiku-4-5, and `calls.py latency` now measures it
  (median ~400ms). The advice validates the playbook: metrics first, then model choice.
- The crash half is the actionable part: the briefing dry-run flagged 3 FAILED calls and one
  anomalous 4-second call in the recent log. Before blaming the model, check the tool-call
  path — PDOK address lookup and RDW kenteken lookup are external HTTP calls inside the
  conversation loop. Action: when investigating failed calls, pull the call trace first and
  look for tool/webhook timeouts; consider explicit timeouts + graceful fallback wording on
  PDOK/RDW so a slow upstream degrades to "ik noteer het adres even handmatig" instead of a
  dead call.
- Also relevant to the still-open Vapi A/B (parked): same diagnostic lens applies there.

## 2. Market read 2026: competition proves demand; differentiate on the full front desk

Advice: AI receptionist that just answers calls is becoming a commodity; the value is in
qualifying leads, following up, booking, updating the CRM, improving the whole journey —
"solve the entire front-desk problem."

Relevance:

- Confirms the existing strategy stack: workflow-depth moat (docs/01-strategy/
  workflow-depth-plan.md, "het kantoor dat meedraait" repositioning, WORKFLOW-MOAT.md) and
  the first-client research conclusion that the plain-receptionist niche got crowded in 2026.
- We already do qualify + book; follow-up and CRM-update are exactly the gated §I roadmap
  (WhatsApp templates, owner channel) — gated on 3 paying clients, which stays right.
- Sales-copy angle available now at zero build cost: pitch the system, show the roadmap
  honestly (the Roadmap.astro section already does this on the site; the deck still doesn't —
  §I deck half open).

## 3. Intake-to-decision prep is the AI task businesses actually want

Advice: the highest-leverage automation is the messy front end of decisions — gather context,
check what's missing, summarize facts, flag risks, tee up a clean recommendation; the human
keeps the final 10%.

Relevance:

- This is a sharper articulation of what the receptionist already is: it does intake and
  preps the owner's callback decision. Worth stealing the framing for sales copy: "wij
  bereiden de beslissing voor, u beslist" — fits the honesty positioning and art. 50 story.
- Maps 1:1 to the real-estate track MVP gaps: branched qualification + lead temperature IS
  intake-to-decision prep for an agent choosing which lead to call first. Use this framing in
  the real-estate sales docs when that track gets its own materials.
- The just-built ops briefing agent (ops/briefing/) is the same pattern applied to the founder
  personally: signals gathered, risks flagged, no decisions taken.
- Guardrail it implies (keep): the agent never makes judgment calls — no improvised pricing,
  no invented commitments; that boundary is now also enforced by the hallucination eval pack.
