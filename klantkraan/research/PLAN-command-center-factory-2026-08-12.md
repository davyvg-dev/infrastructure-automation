# Build plan: command center + automated marketing + website factory

Date: 2026-08-12. Synthesis of four research tracks (full reports in this folder):
`command-center-audit-2026-08-12.md` · `agentic-marketing-research-2026-08-12.md` · `website-factory-research-2026-08-12.md` · `website-market-pricing-2026-08-12.md`

## Decisions taken (founder, 2026-08-12)

- Website factory = **trades add-on to Klantkraan** (same ICP, bundle with receptionist), not a standalone venture.
- Command center = **hybrid: CLI (`kk`) for actions + one read-only static status page** for glances. Approvals stay in Telegram.
- Pricing: **€1.000 ex BTW + €39/mo hosting & onderhoud** standalone; **€749 bundled** with a receptionist plan. Never free.
- Public delivery promise: **"binnen een week online na complete intake"** — never "in één uur" (the hour is founder-attention, not wall-clock).

## Operating frame (from research + Nate Herk service ladder)

- Three buckets: every build maps to *get more customers / make each customer worth more / cut costs*. Four blanks before any client build: bucket, KPI, baseline, 60-day target.
- Service ladder fit: website = rung-2 project (€1.000), receptionist = rung-3 retainer (€299–499/mo). The site's tel:/wa.me buttons feed the receptionist → churn insurance both ways.
- Honest automation ceiling: **~15–30 min/day founder approvals**. Nobody credible runs marketing unsupervised. Agents produce; founder curates.
- Constraints unchanged: no auto-replies/DMs, no cold-call automation, BV-only cold email (calculator opt-in legally opens eenmanszaak/VOF), no avatars, Dutch customer-facing.

## Phase 1 — Command center (build first; everything plugs into it)

Principle: ~300-line dispatcher + one HTML generator. Zero new services, zero new databases, no n8n/Temporal. Full design in `command-center-audit-2026-08-12.md` §C.

Steps (each independently shippable, Ralph loop):
1. `scripts/kk` dispatcher wrapping verbs that already work: `board`, `deal`, `outreach`, `evals`, `billing`, `health`, `deploy`, `logs`. Kills the cwd problem; enforces 6/day outreach cap in code.
2. Ledger fixes + new readers: `created_at` in growth-engine `generate.py`; tag dry-run records (`dry_run: true`, stop fake `status="posted"`); durable failure records for Buffer/TikTok pushes; fix `sequence.py` cwd-relative path. Then `kk content` (~80-line queue.json reader) + `kk leads` (~60-line merger over the 4 lead stores).
3. Alerting: `kk-alert@.service` template unit → `app.notify.owner` Telegram, added as `OnFailure=` to all systemd units. Closes every silent-failure hole.
4. Status page: `ops/status/generate.py` on Hetzner, 15-min timer, one static index.html (no JS, phone-glance order: RAG header → today's numbers → deals due → outreach → content queue → billing → timer matrix), Caddy basic-auth vhost. Stale-warning header.
5. Merge Mac launchd briefing (IMAP replies/DSNs) into the 07:30 server digest → one morning Telegram message; delete launchd job.

Pre-existing defects list (8 items) in audit §C5 — fix during steps 1–3, not after.

## Phase 2 — Automated marketing loops (ranked; feed the Phase-1 approval queue)

1. **Gemiste-omzet calculator → e-mailcursus.** Calculator on Astro site (62% of calls unanswered, ~€208 Werkspot-fee per won job as inputs); opt-in → automated Dutch 4-part course over Resend; completions scored into pipeline. Opt-in consent opens the eenmanszaak/VOF market.
2. **Vertical pSEO + GEO factory.** ~40–80 Dutch pages, trade × problem × comparison ("AI-receptionist voor loodgieters", "antwoordservice vs AI-receptionist", "Werkspot-leads sneller opvolgen") — each with a real data layer + FAQ/schema. NOT city × service pages (doorway penalty). Nightly agent drafts → Telegram approval per page → wrangler deploy.
3. **Evidence-driven content loop.** Weekly agent pulls anonymized receptionist stats → posts + monthly Dutch benchmark via existing growth-engine approval → Buffer/X.
4. **AI-visibility monitor.** One-time schema/FAQ/llms.txt + directory submissions; monthly agent queries ChatGPT/Perplexity/AI Mode with buyer questions, logs citations, digests.
5. (Later) **Demo-video factory** — rendered chat-replays + Dutch VO, Remotion/Creatomate templating. No avatars ever.

Skip list: paid ads until ~30 conversions/mo, n8n, city pages, faceless-video channels, automated review responses, "AI marketing employee" platforms. Human-only: vakbladen (Gawalo, Installatiejournaal), Techniek Nederland, VSK-beurs, sales calls.

## Phase 3 — Website factory (pilot first, then automate)

Narrow-pilot rule applies: **run ONE pilot site for a warm prospect through the manual pipeline, timing each stage, before automating anything.** Full architecture + time budget in `website-factory-research-2026-08-12.md`.

- Architecture: single Astro codebase in the existing monorepo (`apps/client-sites` + shared packages), per-client YAML (same config feeds receptionist + site), one CF Pages project per client. No repo forks, no Duda/Webflow.
- .nl registration via **TransIP API/tipctl** (Cloudflare Registrar has no .nl); domain in the client's name; CF zone + Pages domain via REST API; Email Routing (client clicks one verification mail).
- Process gates (the whole game): clock starts at complete intake; AI writes all copy (Tally pick-from-menu intake, one human NL pass); exactly one consolidated revision round via form; 10 real phone photos required (WhatsApp shot list) with a photo-free fallback design — never stock people or AI job photos.
- QA gates: squirrelscan + lychee + pa11y-ci + Lighthouse budgets + Playwright screenshots + intake-fact assertion (phone/KvK/plaatsen/tel:/wa.me/no placeholders).
- Legal template: KvK + btw-id footer, privacyverklaring naming the receptionist processor, **no cookie banner** (functional-only + cookieless analytics; approved embed list guards this), IP transfer in writing on final payment.
- Sales assets: "Stop met huren van je klanten" (Werkspot math), the complete missed-call funnel as one outcome, "binnen een week online, vaste prijs, en het is van ú".
- Factory verb lands as `kk factory <slug>` in Phase 1's CLI; each live site auto-registers into status-page monitoring (HTTP + cert expiry).

## Build order rationale

Command center first because it is smallest, de-risks everything else (silent failures currently invisible), and both the marketing loops and the factory need its approval queue, alerting, and CLI as substrate. Marketing loops second because they compound with time. Factory third because the pilot needs a real buyer (sell it into an existing deal — DRS, Cool Global, or the riool vertical sprint) and the pilot is a sales motion, not a build.
