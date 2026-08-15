# Claude Code workflow research — 7 Agentic Lab videos + prompt-engineering survey

Date: 2026-08-10. Sources: 7 YouTube videos (all from one channel, "Agentic Lab" / Roman) analyzed
from full transcripts by parallel subagents, plus `Naturallanguage.pdf` (arXiv:2402.07927v2,
"A Systematic Survey of Prompt Engineering in LLMs", Sahoo et al., rev. March 2025).

All seven videos are top-of-funnel content for the creator's Skool community. The marketing
claims ("90% of users...", "mathematically proven") are unsupported; the underlying patterns are
mostly sound and several validate what this repo already does. Value is prioritization, not new
capability.

---

## Per-source findings (condensed)

### 1. "The Claude Code Workflow That Runs My Business Without Me" (10:08)

Core: automations fail because people rely on rules-in-prompt instead of deterministic
verification gates. Verification hierarchy (use the highest tier possible):
script/test > LLM-judge with explicit criteria > open LLM-judge > prompt rules > human review.
Pattern: generation agent finishes → hook runs a deterministic check → on failure, spawn a
healing agent with the violation. His demo: a 50-line bash "slide linter" as a Stop hook
("50 lines of bash outperformed an entire LLM reviewer"). Claims CLAUDE.md rules get ignored —
overstated; the real lesson is don't let CLAUDE.md be the _only_ enforcement.

**Adopt:** copy-lint script for customer-facing text; hooks that run existing verifiers
automatically; compliance greps as gates. **Skip:** "no rules in CLAUDE.md" literalism (the
Forbidden list stays); unbounded healing loops (cap retries).

### 2. "Why Coding Agents Hallucinate" (7:08)

Two failure modes from the OpenAI hallucination paper: the **knowledge gap** (model interpolates
plausibly on repo-specific facts — fixable with context: a traversable "map, not a novel") and
the **confidence trap** (model rewarded to sound confident when uncertain — NOT fixable with
context, only with verification that catches bluffs). "Catch, don't prevent." Deterministic
verifiers first (tests, linters, type checkers), then LLM verification in a _separate context
window_ from generation.

**Adopt:** hallucination eval pack for the receptionist (the confidence trap is our production
risk — the Cekura "John + 5-15 min callback" incident is exactly this class); fresh-context
review subagent as a Ralph gate; convert mistake-born prose rules into tests/evals where
possible. **Skip:** nothing structural — repo already follows the "map" pattern via
`.claude/rules/`.

### 3. "The Six Levels of Slash Commands" (7:08)

Ladder: saved prompt → argument/bash injection → multi-step workflow with stop gates →
subagent orchestrator → app-replacement pipeline → autonomous architect. Sharp point: skills
trigger fuzzily; slash commands are the deterministic trigger for them. Gap found by the agent:
**this monorepo has zero slash commands** (`.claude/` has only `rules/` and skills) while the
business runs on exactly the repeatable CLI workflows commands are for (pipeline board, evals,
wrangler deploy with the `--branch=production` footgun, sequence board, demo spin-up).

**Adopt:** `.claude/commands/` with the 4–5 weekly workflows: `/deploy-site`, `/run-evals`,
`/board`, `/log-regression`, `/new-client-demo` (the demo spin-up has been done manually 6+
times). **Skip:** Level-6 autonomy — collides with repo law (human gates on everything
customer-facing stay).

### 4. "I Replaced OpenClaw with Claude Code" (8:54)

Headless `claude -p` as the skeleton for personal ops agents; "four zones": trigger (cron /
Telegram), context (`--append-system-prompt`), tools (restricted allowlist), output/state
(`--resume`, `/reset`). "Proactive bot magic is literally just a cron job." Runs on the Max
subscription → zero marginal cost for _internal founder tooling_ (never for the resold product
backend — that stays on the API).

**Adopt:** daily ops briefing agent (cron → claude -p reads sequence board + DSNs/replies via
read-only IMAP + calls log → one Telegram message) — closes the deferred oversight-Telegram
item and the DSN-check chore; a reply-watcher for the three offers in flight (DRS, Cool Global,
Anas). **Skip:** any send/reply/label capability (no-automated-replies rule; ledger has legal
semantics); verify current `claude -p` flags via ctx7 before building.

### 5. "Why your coding agent keeps getting DUMBER" (11:47)

Context rot from ever-growing CLAUDE.md; LLM-driven compaction risks **catastrophic rewrite**
(model nukes the file); poisoned context performs below the no-context baseline. Stanford ACE
paper (generator/reflector/curator over a voted bullet DB) explained but even the presenter
hasn't really used it. Takeaway: CLAUDE.md = permanent invariants only; episodic/deal state
lives elsewhere.

**Adopt:** prune MEMORY.md index (closed/superseded entries out, target ~30 live lines);
line-level edits only, never full-file rewrites of CLAUDE.md/MEMORY.md; prompt-rule gate =
only add a receptionist prompt rule when a failing golden motivates it (evals are the "votes").
**Skip:** building ACE (vector DB + 3-agent loop = weeks of plumbing for a problem we don't
have; bottleneck is dials, not assets).

### 6. "The 3 Levels of Context Engineering" (5:41)

Treat sessions as non-linear: `/rewind` (double-Esc) to keep context lean. Patterns:
**rewind-after-debug** (fix the bug, rewind to before the noisy detour, replace it with one
line: "you introduced X, fixed by Y, committed") and **recon-then-trim** (explore on a branch,
rewind, re-prompt with only the conclusion). Since the Ralph loop commits every verified step,
the repo is the durable state — aggressive conversation trimming is safe here.

**Adopt:** both habits — zero cost, directly useful in prompt-tuning/eval sessions. Caution:
after a rewind, tell the model what changed on disk; conversation rewinds don't rewind the
filesystem. **Skip:** over-branching on routine tasks.

### 7. "RAG is dead. Here's the better method." (6:18)

Four memory levels: markdown folder ("most people should stop here", works to 250+ files) →
metadata tags → embeddings → wiki-links/Obsidian. Rules: smallest system that fits; human
decides when the agent queries it (auto-injection bleeds irrelevant context); don't install
memory plugins. Our dev memory (MEMORY.md + topic files) and per-client configs already sit at
the recommended level.

**Adopt:** the decision rule as standing policy — no memory plugins/vector DBs below ~250
files per corpus; for future clients with big doc sets: markdown KB folder + a `search_kb`
tool in the receptionist's tool-use loop, embeddings only if that demonstrably fails.
**Skip:** Obsidian (founder is dashboard-averse; no agent-side benefit), Levels 3–4.

### 8. Naturallanguage.pdf — prompt-engineering survey (41 techniques)

Academic catalogue; benchmarks are on 2022–24 models, treat numbers as historical. Relevant
handful: **ReAct** (validates the tool-use architecture — no change), **Chain-of-Draft**
(concise reasoning, up to ~80% fewer output tokens / ~76% latency cut — matches the
max_tokens=200 voice discipline, make it an explicit prompt rule), **few-shot** (embed 2–3
golden-transcript snippets for the historically failing flows: postcode capture, kenteken),
**Chain-of-Verification** (a checklist verify pass in growth-engine before Telegram — offline,
latency-free), **RaR-lite** (restate ambiguous requests before booking), **Chain-of-Note's
"unknown means unknown"** (never invent hours/prices/availability — take a message; also a
trust/sales point).

**Skip:** the whole multi-sample family (Self-Consistency, Tree/Graph-of-Thoughts, OPRO
automation) — built for benchmark accuracy, ruinous for sub-second TTFB at ~50% margin;
EmotionPrompt (gimmick); all math/table/code-specific clusters.

---

## Consolidated adoption plan (deduped, prioritized)

Build-side items — remember the sprint plan's verdict: the bottleneck is dials, not assets.
Everything below is small; nothing here should displace sales time.

**A. Zero-cost habits (start immediately)**

1. Rewind-after-debug + recon-then-trim in every Claude Code session.
2. Prompt-rule gate: new receptionist prompt rules require a failing golden first; rerun
   `evals.py run all` after.
3. Policy: smallest memory system that fits; no memory plugins/vector DBs; line-level edits
   only on CLAUDE.md/MEMORY.md.

**B. ~30–60 min each (this week, between calls)** 4. Prune MEMORY.md index to live threads. 5. `scripts/copy-lint.sh`: grep gate over customer-facing text — em/en-dashes, founder name,
English tells in .nl artefacts, banned pricing phrases, old phone number. Run it once over
docs/02-sales templates (memory says the old number may linger there). 6. Hallucination eval pack in `app/evals.py`, applied per client config: service-not-offered,
price-not-in-config, invented staff name, invented callback window, ambiguous-request
restatement, unknown-means-unknown. Mirror the voice cases as Cekura scenarios (agent 21227). 7. `.claude/commands/`: `/deploy-site`, `/run-evals`, `/board` first; `/log-regression` and
`/new-client-demo` next.

**C. One evening each (next 1–2 weeks)** 8. Stop-hook dispatcher in `.claude/settings.json` (use the update-config skill; scope by
`git diff --name-only`): copy-lint for touched artefacts, eval subset when receptionist
prompts/config change, exit 2 to feed failures back. Cap healing retries at 1–2; scope eval
runs to avoid API burn. 9. `scripts/compliance-check.sh` as a CI job: art. 50 disclosure string present in every agent
prompt/config; outreach CSVs BV-only. 10. Daily ops briefing agent (`ops/briefing/`: SPEC.md, agent.sh, read-only fetch_signals.py →
Telegram, single allowed chat ID) + reply-watcher for DRS / Cool Global / Anas. Fetch
current `claude -p` flag docs via ctx7 first. 11. Growth-engine verify pass (CoVe-style, one Haiku call, AI-tells + stats-policy checklist)
before the Telegram approval message; dry-run semantics untouched. 12. Few-shot + CoD + RaR + unknown-rule prompt edits, one commit each, goldens between commits;
check TTFB via `calls.py latency` and rerun the Cekura smoke suite after.

**Global cautions**

- Human gates on anything outbound are a legal/positioning choice, not inefficiency — no
  video's autonomy advice overrides Telegram approval, dry-run, or the no-automated-replies rule.
- CLAUDE.md's Forbidden section stays as prose _and_ gains script enforcement where possible —
  never prose-only for compliance, never script-only either.
- Max-plan `claude -p` is for internal founder tooling only; product stays on the API.
- Don't cite any of the videos' numbers anywhere (stats policy).
