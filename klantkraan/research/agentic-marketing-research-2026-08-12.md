# Track 1 — Fully-Automated AI Marketing for Klantkraan — Research Report (Aug 2026)

Scope: agentic marketing state of the art, automatable vs. human functions, programmatic SEO post-2025, orchestration patterns, and channel fit for a Dutch trades ICP under Klantkraan's hard constraints (no auto-replies/DMs, no cold-call automation, BV-only cold email, Dutch content, CLI + approval-queue, no avatars).

## 1. State of the art: agentic marketing for solo founders (2025–2026)

**What demonstrably works is narrower than the hype.** The credible pattern is a *pipeline of specialized agents with human review at every meaningful boundary* — researcher → writer → critic → publisher. Architecturally identical to the growth-engine Klantkraan already runs. (Averi: https://www.averi.ai/how-to/ai-agent-marketing-how-autonomous-ai-is-changing-content-ops-in-2026, Naturaily: https://naturaily.com/blog/ai-agents-for-content-creation)

SaaStr "20 agents in 10 months" (https://www.saastr.com/stop-learning-ai-start-doing-ai-the-20-agents-running-saastr):
- **"Hero purchases" fail** — automating something already working sets an impossibly high bar. **"Layup roles" win** — automate work *nobody is doing at all* (for Klantkraan: SEO pages, nurture emails, GEO monitoring are layups).
- **Training beats tooling** — ~30 days setup, then **~1 hour/day of ongoing agent supervision**. Realistic target: 15–30 min/day approval-queue habit.
- Most "multi-agent marketing platforms" are single agents with branding; buy none.

Skepticism: viral solo-founder numbers ("$2M ARR in 8 months") come from vendor blogs, unverifiable. Verifiable solo successes (Levels, Marc Lou, HeadshotPro) won on product + distribution instincts, AI as production multiplier. Nobody credible reports fully-autonomous marketing producing customers unsupervised.

## 2. Automatable end-to-end vs. still-human

| Function | Verdict |
|---|---|
| Content drafting + repurposing | E2E automatable (with approval gate) |
| SEO page generation from structured data | E2E automatable (data-backed pages only) |
| Email nurture sequences | E2E automatable once written |
| Lead scoring/enrichment | E2E automatable (needs KvK API — known blocker) |
| Analytics/reporting | E2E automatable (cron agent → digest) |
| GBP posts, NAP audits, rank tracking | E2E automatable (GBP API since late-2025) |
| Ad creative generation | Automatable, but see next |
| **Ad buying (PMax / Advantage+)** | **NOT viable yet** — needs ~30 conversions/mo (PMax) or 50+ leads/wk; cold B2B Meta CPL $400–800. Algorithms starve at Klantkraan volume. (miniloop, optimumclick) |
| Review responses | Banned by constraint (automated reply) |
| Strategy, positioning, partnerships, sales | Human |

## 3. Programmatic SEO after 2025: alive, but only the data-product kind

**pSEO is not dead — cheap pSEO is.**
- Google March 2024 scaled-content-abuse action deindexed 1,400+ sites; failure pattern = ≥80–90% unedited AI content + velocity. Aug 2025 spam update flags city pages ~95% identical. (Rankability, digitalapplied, flashcrafter)
- What works: pages expressing a **data product** — boilerplate under ~60–75%, real data layer per page, hub-and-spoke linking, **20–60 pages per build**. (topicalmap.ai, aiappsapi)
- HN practitioner (5 yrs pSEO): durable templates = **use-case × industry × platform × country × "alternative/vs"** — maps to *trade-vertical pages*, not city pages. (HN 47551534)
- **AI Overviews NL**: live since May 2025; trigger on only ~5.2% of Dutch queries (informational long-tail, where pos-1 CTR drops ~58%). **Target commercial/transactional Dutch queries** ("telefoonservice loodgieter"). (youvia, yourfellow)
- **GEO**: schema + FAQ + citable stats = 30–40% higher AI-answer visibility; ~47% of brands have no GEO strategy. llms.txt unproven — ship it, expect nothing. (yotpo, postaimarketing, llmpulse)

**For Klantkraan:** city × service pages for Klantkraan itself = spam-shaped; sell nationally. Right surface = **vertical × problem × comparison**: "AI-receptionist voor loodgieters", "gemiste oproepen rioolbedrijf kosten", "antwoordservice vs. AI-receptionist", "Werkspot-leads sneller opvolgen". ~40–80 pages total with real data layers.

## 4. Orchestration patterns

Options: n8n HITL, custom Python + cron, **Claude Code scheduled/headless agents** (cron-triggered `claude -p` documented pattern for marketing reports/content pipelines — MindStudio, Koka Sexton, Orchestra).

n8n Telegram approval: no queue, no history, no diff — worse than the existing custom Telegram ledger. **Do not adopt n8n.**

Winning architecture (half-built already):
- systemd timers on Hetzner firing Claude Code headless jobs per marketing loop
- **one shared approval queue** — extend growth-engine Telegram approval to all artefact types (posts, SEO pages, emails, videos)
- **one CLI command center** — extend `board` to `marketing board`: pending approvals, pages live/indexed, GSC clicks, list growth, nurture stats, agent-run health
- watchdog + dead-man switch: heartbeats + daily digest ("ran / produced / awaiting approval / failed")

Reference (n8n version): operator time 20–30 h/wk → **4–6 h/wk with humans on approvals/escalations only** (nextgrowth.ai) — the ratio is the credible part.

## 5. Channel fit for Dutch trades ICP

- **Dutch pSEO + GEO** — best fit. See §3.
- **Lead magnets / interactive calculators** — strongest finding. Calculators outperform static downloads 2–3x; ROI calculators convert 22–38%; raw material: 62% of calls to small businesses unanswered, plumbing firms lose $18k–234k/yr, 85% of unanswered callers never call back, conversion drops ~80% after 5 min (calljolt, contractorincharge, hicira). "Gemiste-omzet calculator" writes itself. **Calculator opt-in = consent → legally opens email to eenmanszaak/VOF** — dissolves the BV-only ceiling.
- **Email/newsletter nurture** — ~$53 CPL vs $400+ paid social; Dutch 4-part e-mailcursus on Resend + sequencer, fully automatable.
- **Directories** — Werkspot = #1 platform, used by 43% of surveyed firms; content wedge: "Wat kost een trage reactie op je Werkspot-lead?" Also list Klantkraan in AI-tool/SaaS directories for GEO.
- **Vakbladen + beurs** — Gawalo, Installatiejournaal, E&W Installatietechniek, Techniek Nederland, VSK-beurs. Human-only; agents prep.
- **Video without avatars** — faceless-shorts tools = slop; but **rendered chat-replay demos** (real transcripts, Dutch ElevenLabs VO, Remotion/Creatomate templating) are legitimate. Semi-automatable.
- **GBP for Klantkraan itself** — low value (B2B SaaS); basic profile only. GBP automation more interesting as future client-facing product module.

## Works vs hype

**Works:** agent pipelines with approval gates; data-product pSEO; interactive calculators; trigger-based nurture; cron headless agents + CLI digests; GEO basics in an owned niche.

**Hype / not for you:** "AI marketing employee" platforms; AI ad buying at this volume; mass city × service pages; faceless-video farms; llms.txt as silver bullet; n8n migration; unedited-AI content at velocity.

## Ranked top 5 fully-automatable marketing loops

1. **Vertical pSEO + GEO factory.** Nightly agent drafts Dutch pages from structured dataset (trade × problem × comparison, ~40–80 pages, real data + FAQ/schema), founder approves per page, wrangler deploys. Highest leverage per approval-minute.
2. **Gemiste-omzet calculator → opt-in e-mailcursus loop.** Calculator once on Astro site; automated Dutch 4-part course over Resend; agent scores completions into pipeline CLI. Best conversion economics; opt-in opens eenmanszaak/VOF market.
3. **Evidence-driven content loop (upgrade growth-engine).** Weekly agent pulls anonymized receptionist stats → posts + monthly Dutch benchmark snippet via existing Telegram approval → Buffer/X. Original data = E-E-A-T + GEO citations. Near-zero marginal cost.
4. **AI-visibility monitor + directory loop.** One-time schema/FAQ/llms.txt + directory submissions; monthly agent queries ChatGPT/Perplexity/AI Mode with buyer questions, logs citations, files digest. Trivial cost, fully unattended.
5. **Demo-video factory (no avatars).** Template rendered chat-replay + Dutch VO short once; agent generates variant per vertical from consented anonymized transcripts; founder approves; Buffer queues. Fifth because visual QA keeps human in render loop.

**Skip:** paid-ads automation, n8n, city × service pages, faceless channels, automated review responses, "AI marketing employee" platforms. **Human-only:** vakblad/VSK partnerships, Techniek Nederland relationships, sales calls.

**Orchestration verdict:** systemd timers on Hetzner running Claude Code headless jobs, one unified Telegram approval queue, one `marketing board` CLI extending `board`, heartbeat + daily digest. Realistic founder cost after ramp: ~15–30 min/day of approvals.
