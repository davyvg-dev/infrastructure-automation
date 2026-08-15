# How the best AI agents operate — verified research, August 2026

Four parallel research agents, primary sources only (vendor engineering blogs, official
docs, peer-reviewed/arXiv papers — every claim traced to a fetched page, dates noted).
Full source tables at the end of each section.

---

## 1. Architecture & workflow design

**The canonical taxonomy** (Anthropic, "Building Effective Agents", Dec 2024):
_workflows_ = LLMs orchestrated through predefined code paths; _agents_ = LLMs that
dynamically direct their own process based on tool feedback. Five workflow patterns:
prompt chaining, routing, parallelization (sectioning/voting), orchestrator-workers,
evaluator-optimizer. The agent pattern is a loop grounded in environmental feedback with
human checkpoints at blockers.

**What everyone converged on, 2024-2026:**

1. **Simplicity first, universally.** Anthropic: "The most successful implementations
   weren't using complex frameworks... they were building with simple, composable
   patterns." OpenAI: "maximize a single agent's capabilities first"; a deterministic
   solution may suffice. Escalation ladder: single LLM call + retrieval → workflow →
   single agent loop → multi-agent, stepping up only when evals prove the previous rung
   fails.
2. **The dominant production architecture is the single-agent tool loop**: model + tools
   - instructions in a while-loop until an exit condition (final answer, no tool calls,
     error, max turns), wrapped in layered guardrails, with human escalation on failure
     thresholds and high-risk actions.
3. **Multi-agent is a context-window strategy, not an org chart.** Anthropic's research
   system (orchestrator + parallel subagents) beat single-agent Opus by **90.2%** on
   breadth-first research — but at **~15x** the tokens of chat ("multi-agent systems work
   mainly because they help spend enough tokens"). Cognition's counter ("Don't Build
   Multi-Agents", Jun 2025): parallel workers make conflicting implicit decisions —
   fatal for write-heavy interdependent work like coding. Reconciliation: parallel
   subagents for read-heavy parallelizable exploration returning summaries; single
   thread + context compression for write-heavy work.
4. **Split a single agent only on two triggers** (OpenAI): if-then-else prompt sprawl, or
   tool overload — and overlap matters more than count: "some implementations
   successfully manage more than 15 well-defined, distinct tools while others struggle
   with fewer than 10 overlapping tools."
5. **Context engineering displaced prompt engineering** (Anthropic, Sep 2025): attention
   is a finite budget that degrades as the window fills. Standard toolkit: compaction
   (summarize + reinitialize), structured note-taking/external memory, fresh-context
   subagents returning 1-2k-token summaries, just-in-time retrieval via lightweight
   identifiers instead of pre-stuffed context.
6. **Tools are load-bearing architecture** (Anthropic, Sep 2025): fewer, consolidated,
   workflow-shaped tools; namespaced names; semantic identifiers instead of UUIDs
   ("significantly improves precision... by reducing hallucinations"); token-efficient
   responses; descriptions written like onboarding docs — "even small refinements to
   tool descriptions can yield dramatic improvements."
7. **Verification closes the loop**: runnable checks (tests/builds/screenshots),
   fresh-context adversarial review, trajectory-level evals (judge the full decision
   sequence, not just the output — Google), LLM-judge with rubric starting at ~20 test
   cases (early changes move success rates 30%→80%, so small samples suffice).

| Source                                                                    | Date            |
| ------------------------------------------------------------------------- | --------------- |
| anthropic.com/engineering/building-effective-agents                       | 2024-12-19      |
| anthropic.com/engineering/multi-agent-research-system                     | 2025-06-13      |
| anthropic.com/engineering/writing-tools-for-agents                        | 2025-09-11      |
| anthropic.com/engineering/effective-context-engineering-for-ai-agents     | 2025-09-29      |
| code.claude.com/docs/en/best-practices                                    | fetched 2026-08 |
| cdn.openai.com — A Practical Guide to Building Agents (PDF, read in full) | 2025            |
| openai.github.io/openai-agents-python                                     | fetched 2026-08 |
| cognition.com/blog/dont-build-multi-agents                                | 2025-06-12      |
| cloud.google.com blog — production-ready AI agents (5 whitepapers)        | 2026-02-26      |

---

## 2. Hallucination prevention (ranked by evidence strength)

**Tier 1 — published numbers:**

1. **Grounding + enforced citations.** Anthropic Citations API: recall accuracy +15%
   internal; production customer Endex: source hallucinations **10% → 0%** with 20% more
   references per response. Foundational: Shuster et al. 2021 — retrieval augmentation
   "substantially reduces" knowledge hallucination in dialogue.
2. **Chain-of-Verification** (Meta, 2023): draft → generate verification questions →
   answer them _without seeing the draft_ → revise. Hallucinated entities **−77%**
   (2.95 → 0.68 per answer); longform FactScore +28%. Two negative findings: plain
   chain-of-thought did NOT reduce hallucination, and chat-tuned models hallucinated
   _more_ than few-shot base models. The verifier must be independent or it copies the
   error.
3. **Fix the incentive** (OpenAI, "Why Language Models Hallucinate", Sep 2025):
   hallucination is statistically inevitable under binary-scored training — a guessing
   model always beats an honest abstainer. Singleton bound: facts appearing once in
   pretraining are hallucinated at least at their singleton rate. Consequences: rare
   business facts (a client's price list) must come from tools, never recall; and your
   own evals must score "I don't know" as neutral-or-positive.
4. **Self-consistency / best-of-N**: majority vote across samples (+11-18% on reasoning
   benchmarks); inconsistency across samples is itself a hallucination signal.
5. **Structured outputs / JSON schema**: eliminates _format_ hallucinations (invented
   fields, malformed tool calls) entirely; does nothing for factual ones.

**Tier 2 — production vendor patterns:**

- **Anthropic's documented prompt techniques**: explicit permission to say "I don't
  know" ("can drastically reduce false information"); quote-first grounding for long
  docs; cite-then-retract ("if it can't find a quote, it must retract the claim");
  restrict to provided documents only.
- **Runtime groundedness checking** (Azure AI Content Safety): checks output against
  sources at runtime and can auto-rewrite ungrounded spans. English-optimized — limited
  for Dutch.
- **Layered guardrails** (OpenAI): small-model relevance/safety classifiers + moderation
  - regex/blocklists + tool risk ratings + human escalation, run concurrently with
    optimistic execution. "A single one is unlikely to provide sufficient protection."
- **Reality check**: even frontier models hallucinate on >3-13% of _grounded_
  summarization tasks (Vectara HHEM leaderboard, Nov 2025). The layers exist because no
  model is clean.

**Consensus stack**: retrieve/tool-call never recall → constrain in the prompt (only
tool results, "I don't know" allowed) → enforce schemas → independent second-pass
verification → layered guardrails → claim-level faithfulness evals that never penalize
abstention.

Key sources: platform.claude.com (reduce-hallucinations, citations), arXiv:2509.04664,
arXiv:2309.11495, arXiv:2104.07567, arXiv:2203.11171, learn.microsoft.com groundedness,
OpenAI agents guide PDF, vectara.com HHEM leaderboard (2025-11-19), docs.ragas.io.

---

## 3. Error handling & reliability

1. **A failed tool call is model input, not an exception.** Return errors as
   `tool_result` with `is_error: true` and _instructive_ text ("Rate limit exceeded.
   Retry after 60 seconds" — not "failed"); the model self-corrects, retrying 2-3 times.
   Anthropic production: "letting the agent know when a tool is failing and letting it
   adapt works surprisingly well" — but only combined with deterministic retries and
   checkpoints. Errors also steer behavior (truncation messages teach pagination).
2. **Prevent errors structurally** ("poka-yoke"): strict tool schemas, argument designs
   that make mistakes impossible (absolute paths eliminated a whole error class),
   detailed descriptions, paginated/truncated responses. Bounded loops everywhere:
   max-iteration caps, timeouts, exponential backoff honoring retry-after.
3. **Contain the blast radius**: sandbox filesystem AND network (both, always —
   Anthropic's sandboxing cut permission prompts **84%** while blocking exfiltration);
   rate every tool low/medium/high on write-access, **reversibility**, financial impact;
   gate high-risk calls behind approval implemented as serializable, resumable state;
   treat tool results as untrusted content (prompt-injection surface).
4. **Degrade gracefully** (Microsoft): timeouts + retries, surface errors instead of
   hiding them, validate outputs before they cascade, circuit-break sick dependencies.
   Human handoff is a designed path with two canonical triggers (OpenAI): exceeding
   retry/failure thresholds, and high-risk irreversible actions.
5. **Persist everything**: checkpoint per step (LangGraph) or record/replay event
   history (Temporal) so crashes resume instead of restart; external memory for context
   limits; rainbow deployments so code pushes don't kill in-flight agents.
6. **Trace everything**: every LLM call and tool call with prompt, response, tokens,
   cost, latency (OTel GenAI conventions, Langfuse-style); async export; replay for
   debugging. Anthropic: "full production tracing let us diagnose why agents failed and
   fix issues systematically."
7. **The cautionary tale**: Project Vend (Anthropic) — an agent running a real shop lost
   money via hallucinated payment details, below-cost pricing, and social-engineered
   discounts. Verdict: reliability is largely a systems-engineering problem _around_ the
   model (better tools, memory, structured reflection), not a model problem.

Key sources: platform.claude.com (handle-tool-calls, errors), anthropic.com/engineering
(multi-agent, writing-tools, sandboxing 2025-10-20), anthropic.com/research/project-vend-1,
OpenAI agents guide PDF + developers.openai.com guardrails-approvals, temporal.io blog
2025-07-10, learn.microsoft.com AI agent design patterns 2026-02, docs.langchain.com
persistence, langfuse.com, github.com/open-telemetry/semantic-conventions-genai.

---

## 4. Latency — with voice-agent depth

**Budgets (the numbers that matter for phone agents):**

- Human turn gap: modal **0-200 ms**, median +100 ms; 70-82% of human transitions happen
  within 500 ms (Stivers et al. PNAS 2009; Levinson & Torreira 2015). Humans achieve
  this by planning their reply _while the other person still talks_ — the biological
  justification for speculative generation and predictive endpointing.
- Industry consensus: **<500 ms feels responsive; 500-1000 ms noticeable (users repeat
  themselves); >1000 ms users abandon** (ElevenLabs). Production targets: ≤700 ms
  time-to-first-audio (ElevenLabs), p50 <500 / p95 <800 ms (Vapi); ~465 ms demonstrated
  as an optimized floor (AssemblyAI on Vapi).
- Budget template that reaches it: STT 90-150 + endpoint decision 200-400 + LLM TTFT
  200-400 + TTS 75-135 + network ~100 ms.

**The two biggest levers:**

1. **Endpointing/turn detection** — default silence-timeout misconfiguration can add
   **1.5 s** of dead air, "completely negating all your other optimizations"
   (AssemblyAI). Semantic/STT-native turn detection (Deepgram Flux, ElevenLabs
   speculative turn-taking, LiveKit turn-detector model) saves 200-600 ms vs plain VAD.
   ElevenLabs' own docs: use **Patient** turn-mode when collecting phone numbers,
   addresses, emails; Eager for quick loops; disable interruption during legal
   disclaimers (⇒ our art. 50 line).
2. **LLM TTFT — the largest and most variable stage.** Stability matters as much as the
   median: an erratic 0.5-13 s pool is worse than a stable 400 ms one (exactly our
   Gemini-pool finding on the DRS agent, independently confirmed). Reasoning/thinking
   counts inside TTFT (Artificial Analysis methodology) — voice LLMs run thinking OFF.
   Cap max tokens (150-200): shorter generates faster and is better phone UX anyway.

**Supporting techniques**: stream every stage (saves 100-300 ms at the LLM boundary
alone); filler-phrase soft timeout (~3 s) masks tool-call tail latency; prompt caching
(Anthropic: cached reads 0.1x price, better TTFT — keep system prompt + tools
byte-stable, variation at the end); co-locate STT/LLM/TTS in-region; single codec path
(transcoding hops cost 100-300 ms); async writes — never block the speech path on a CRM
call; timestamp every stage boundary because you can't fix what you don't measure.

**Speech-to-speech vs cascaded**: S2S (OpenAI Realtime, Gemini Live) wins raw latency
and naturalness; cascaded remains the production norm when stages must be visible and
replaceable (specific Dutch STT, tool calls, compliance transcripts). Choose the audio
architecture first, then design the agent (OpenAI).

Key sources: PNAS 2009 (PMC2705608), Frontiers in Psychology 2015, docs.livekit.io
turns, developers.deepgram.com, elevenlabs.io latency blog (2025-03, upd. 2026-07) +
conversation-flow docs, vapi.ai/blog/speech-latency (2025-06), assemblyai.com blog
(2025-07), retellai.com, developers.openai.com voice-agents + realtime, cartesia.ai
sonic, platform.claude.com prompt-caching, artificialanalysis.ai/methodology.

---

## What this validates or changes for Klantkraan

Already aligned with best practice (independently confirmed):

- Bounded manual tool loop + config-over-code (single-agent tool loop is the norm).
- "Only offer slots check_availability returned" = tool-result grounding, the single
  strongest anti-hallucination measure in the literature.
- Thinking OFF on voice LLMs; the Gemini-pool TTFB variance diagnosis; filler soft
  timeout; in-call lookups only with writes on the call-end webhook; static disclosure
  first message.
- Telegram error surfacing + watchdog = "surface errors, human handoff as designed path."

Worth adopting next (highest leverage first):

1. **Patient turn-mode during address/phone capture** on the ElevenLabs agent — vendor-
   documented fix for exactly our postcode-capture failure class; keep Eager/Normal
   elsewhere. Also confirm interruption stays off during the art. 50 disclosure.
2. **"I don't know" affordance + cite-then-retract** lines in receptionist prompts —
   documented "drastic" reduction, one prompt edit.
3. **Per-stage latency timestamps** on voice calls (we already pull
   conversation_turn_metrics — make the four-stage breakdown a standard post-call
   check).
4. **20-case eval set + LLM-judge rubric** for the receptionist (disclosure spoken,
   booking attempted, no invented prices, lead captured) — small samples are enough to
   steer; never score abstention as failure.
5. **Instructive tool-error text** in every webhook tool ("PDOK returned 0 results —
   ask for street + city instead"), not bare failures.
