# Klantkraan — TODO

> Living checklist. Tick boxes as we go. Ralph Higgums loop: small step → test → next.

## ACTIVE — Productize sprint (from 2026-07-12 birds-eye audit)

Text-first pivot is the product: `ai-receptionist/` is what we sell — plug-and-play per client config, done-for-you setup. Voice = upsell later. Work top-to-bottom; each box = one small verified commit.

### A. Lock the offer (blocks all sales artefacts)
- [x] Pricing LOCKED (2026-07-14): **"Klantkraan Chat" €299/mo** (webchat + WhatsApp receptionist, booking, done-for-you setup) + **"Klantkraan Compleet" €499/mo** (adds voice line, later); €249 one-time setup, waived for pilots. Market anchors (2026-07): Klusio €199 (bundles chat+WhatsApp+voice), Voicelabs €199–399, VoxFlow €99, secretaresse.ai €397 flat, InstallatieTelefoniste €0.25/min no-subscription, human telefoonservice €25–150.
- [x] Propagate the locked price everywhere — site (prijzen/rekentool) + all sales/finance/legal docs + LinkedIn post 006 now read €299/€499/€249; dead Pro/Max tier names and stale 599/999/849/699 figures retired
- [x] Rewrite offer docs voice-first → text-first (offer-and-pricing, discovery-script demo flow, master-plan product section). NOTE: `00-MASTER-PLAN.md` §4/§5 still frames the Synthflow voice trial as the core pre-launch promise — founder decision, left intact (CLAUDE.md pins §5)

### B. Product hardening (`ai-receptionist/` — make it sellable plug-and-play)
- [x] Commit the pending WhatsApp-first site pass (committed 2026-07-13, f169ac7)
- [x] Art. 50 disclosure into `config/business.yaml` + `config/home-services-example.yaml` (0f82e7e)
- [x] WhatsApp webhook signature validation fail-closed; `WHATSAPP_ALLOW_UNSIGNED=1` for local dev (5941efc)
- [x] `take_message`: persists to `data/messages.json`; tool result reports saved/notified honestly (e3435cc)
- [x] `/chat`: per-IP rate limit (default 20/min) + optional `CHAT_API_KEY` + 2000-char cap + caught 503 (36c77c0)
- [x] Logging `basicConfig` at startup; `/health` endpoint; `HOST`/`PORT`/`LOG_LEVEL` from env (1db1745)
- [x] Calendar: future-only slots, tz-aware via business config, per-business `bookings-<config>.json` (e5057df)
- [x] Session store: per-conversation locks; single-worker constraint documented (e7ff1e2)
- [x] Prospect/client configs with real names/phones — DECIDED: gitignored dir. `config/prospects/*.yaml` + `config/clients/*.yaml` untracked (kept on disk, still rsync to server); tracked READMEs document it (68b68de). NOTE: the 6 scaffolds remain in past git history — say the word for a history scrub.
- [x] Privacy page: Cloudflare Web Analytics named instead of Plausible (9022f04)
- [x] `/over`: KvK-uittreksel is on-request via mail until the PDF exists (3999034)

### C. Repo hygiene
- [x] Fix root `.gitignore` — .DS_Store/.wrangler now ignored; Python-era `downloads/` pattern removed (d9ef618)
- [x] Delete legacy `Python/`; root `README.md` now describes Klantkraan (0d2db3f)
- [x] `apps/voice-agent/` marked dormant — voice upsell, resume when a client wants it (9f67dcf)
- [x] growth-engine: TASK.md step 6 ticked, `anthropic>=0.116,<1`, dead `paste_block` removed, `buildlog` in CLAUDE.md (0279d5f)

### D. Founder real-world batch (Claude preps, founder executes)
- [ ] KvK + BTW numbers → new `src/data/company.ts` → renders on `/over`, legal pages, offerte template (founder supplies 2 numbers; one file edit fixes every placeholder)
- [ ] Upload real KvK-uittreksel PDF → `public/downloads/`
- [x] Attach `klantkraan.nl` custom domain — NS propagation completed; apex + www both serve the site over Cloudflare (verified 2026-07-13, HTTP 200)
- [ ] Moneybird trial + Mollie account (walkthrough prepped; needed before first invoice)
- [ ] Liability insurance — get the Hiscox beroepsaansprakelijkheidsverzekering ICT quote (€500k cover, ~€40–80/mo, master plan § 5 item 7) and ask for bedrijfsaansprakelijkheid (AVB) in the same bundle; in place before the first paying client goes live
- [ ] Point `/demo` at the live text demo (web chat) instead of the TODO phone number — text demo works today, no CM.com dependency

### E. First pilot (the gate everything else waits behind)
- [x] Finish ONE prospect config fully — **Loodgietersbedrijf Meijer B.V.** (`config/clients/meijer.yaml`): real services/hours/FAQ from their site, persona "Sanne", art. 50 disclosure, guardrails; `selftest config` passes
- [x] Deploy the demo publicly at a stable URL — Hetzner ops redeployed 2026-07-14: `widget.js` now live (was 404), showcase at https://demo-168-119-173-25.sslip.io/ and Meijer's own bot at https://demo-168-119-173-25.sslip.io/?client=meijer (verified end-to-end: offers a real slot, collects details, books)
- [ ] Walk one warm prospect through it; offer pilot terms (free/€99 for 30 days in exchange for case-study data) — FOUNDER: Meijer demo is ready to show

### F. Onboarding + maintenance process — research + harden (added 2026-07-21)
Goal: make onboarding frictionless for BOTH sides, so the product works smoothly from day one and stays that way. Not a from-scratch build — audit/harden the existing `docs/03-delivery/onboarding-playbook.md` + `churn-prevention.md` against the text-first + Synthflow reality and the first real client (Mallorca airco).
- [x] Research/benchmark how comparable done-for-you providers onboard trades with minimal client effort (intake → build → go-live → handover) — 2026-07-29, cited in playbook Sources. Load-bearing findings: <$5k-ARR band expects TTV in *minutes* (we are €3.6k/yr); B2B services has the **lowest** activation of any category (~29%), so assume 2 in 3 self-serve payers never activate alone; activation:churn couples ~1:2; pay → auto-welcome → intake → queue with no manual gap is the standard productized shape.
- [x] Map the end-to-end flow: close → one-time intake → build config → deploy/route → client test & sign-off → go-live → maintenance — founder-led path already existed (playbook §1). **Added the path that was missing entirely: §1b, the self-serve payer.** Since Mollie went live a stranger can subscribe at 03:00 and the playbook had no answer past the founder's Telegram ping.
- [x] Define the minimal client-side intake collected ONCE — playbook §2 (scrape-first, one confirmation + four questions) held up; §1b adds the self-serve variant and the "ask one question, don't guess" rule when the scrape has no site to work from.
- [x] Define the post-go-live upkeep loop (monitoring, monthly tune, change requests, who owns what) — `churn-prevention.md` rewritten: §1 cadence table (~35 min/client/month steady state) against the 4 deployed timers, §2 monthly tune, §3 change-request rule, §4 ownership split. Voice-era leftovers (daily stats SMS, "recovered calls", Attio) removed.
- [x] Output: one smooth, repeatable playbook the founder runs per client — playbook + churn doc now meet at go-live with no gap. Also added playbook §1c, the written scope boundary (inbegrepen vs meerwerk), which did not exist.
- [x] **Follow-ups this opened (see playbook §11 items 6–9) — all five closed 2026-07-29:**
  - [x] **Terms + DPA acceptance at checkout** — required checkbox + persisted `akkoord_versie`/`akkoord_op` (4ce359d).
  - [x] **Paid-webhook welcome message** — the buyer now gets a Dutch welcome the moment the first payment lands, via `app/mailer.py` (Resend). Promises one working day, skips the website question when the form supplied it, idempotent against webhook replays; if it cannot send, the founder ping says so and names the fallback command (d5f7984).
  - [x] **Website URL field on the signup form** — optional `site` field on `/aanmelden` NL/EN/ES; normalised server-side, never rejected, so a typo cannot fail a €299 checkout (4bc60e8).
  - [x] **`billing.cancel` / `billing.refund` CLI** — `subs` / `cancel` / `refund` / `offboard`; the decline path is one command and the Mollie dashboard is out of the loop (8c262aa).
  - [x] **Digest delivering nowhere** — no longer gated on `OWNER_TELEGRAM_CHAT_ID`: the daily digest falls back to `OWNER_EMAIL` over Resend, and exits 1 (visible failed unit) when neither channel is configured instead of quietly writing to the journal. `python -m app.notify chatid` now prints the chat id, so wiring Telegram is one command whenever the founder wants the upgrade.
  - [ ] **FOUNDER: set `RESEND_API_KEY` + `OWNER_EMAIL` in the prod `.env`.** Both the welcome mail and the digest fallback are dark without it — the code is deployed-ready, the key is the only thing missing.
  - [ ] **LATER (not now, founder request 2026-07-31): richer dagrapport** — the daily digest (`ai-receptionist/app/oversight.py`) should carry more detail than the current counts + top-5 signal lists. Candidates when picked up: per-conversation one-liners (intent → outcome), booking details, est. job value totals, sentiment split, quality flags — the Layer-2 insight fields are already extracted, the digest just doesn't surface most of them. Scope it with the founder before building.

### G. Website copy — de-AI / professional-copywriter pass (added 2026-07-21)
Goal: the site copy reads like a professional copywriter wrote it, not like AI. Founder specifically flagged em-dashes and AI-tell writing. Cut them; keep dashes/punctuation only when genuinely relevant.
- [x] `/en/` pages done (home, prijzen, over, demo, air-conditioning): decorative em-dashes + AI-tells removed, facts/prices/AI Act art. 50 disclosure kept, natural professional voice; build passes. (2026-07-21)
- [x] Also dropped the "call you back / book a demo" lead-form block (section 4) from both home pages; capture now runs via the hero WhatsApp + demo CTAs. (2026-07-21)
- [x] Dutch pass done (2026-07-21): home, over, demo, demo/sportscholen, voor-wie, sportscholen, rekentool, all 6 trade landings, the `[stad]/[vak]` template, gidsen/blog titles, and the RiskReversal + DashboardMock + dakdekkers/* components; art. 50 FAQ harmonised across the 6 trade/gym pages. Visible marketing prose is em-dash-free; build passes.
- [x] Deferred de-AI items done in Phase 3 of the redesign (commit beb42c8): legal-page `<title>` "— Klantkraan" → "| Klantkraan" (also fixes an inconsistency — marketing pages already used the pipe); DPA "Annex I/II/III —" headings → colon; `/r/[slug]` dashboard description + dynamic title → colon (kept the empty-state "—" no-value glyphs); LeadForm success copy → period. Curly quotes DEFERRED (documented in the redesign runbook — a partial pass looks worse than none; not founder-flagged).
- [x] Re-deployed (Phase 3, preview alias `redesign.klantkraan-marketing.pages.dev`, deployment `7f8d95f0`) + verified 200 + dark theme across page types. Production cutover is Phase 4.

### H. Site-wide visual redesign — "Het licht blijft aan" (STARTED planning 2026-07-23)
Founder wants the whole site rebuilt in the clean-sheet hero concept. Full runbook (source of
truth, survives context clears): **`docs/09-brand/redesign-execution-plan.md`**. Visual reference:
`docs/09-brand/redesign-concept-2026-07-23-light-stays-on.html`.
Approach approved 2026-07-23: preview alias + atomic cutover (apex stays live on the old design
throughout); every page incl. reading variant for legal/blog/gidsen; foundation + home serial,
then parallel-draft / serial-verify. Checkboxes below mirror the runbook phases.
- [x] **Phase 0 — Foundation** (serial, DONE 2026-07-23, commits 9eb015b + 91bc019): self-hosted 3 fonts (18 woff2 subsets) → palette/type flipped in `global.css` `@theme` (old kraan-* kept, deprecated) → Header/Footer/StickyCta/Base rebuilt + screenshot-verified → universal .btn/.eyebrow primitives. Home-specific signatures deferred to Phase 1. Build green, astro check 0 errors.
- [x] **Phase 1 — Home** (serial, DONE 2026-07-23): 1.1 NL `index.astro` rebuilt (faf1e29) + 1.2 web-design-guidelines fixes (cd83615) + 1.3 **founder APPROVED** + 1.4 EN/ES twins (4b9b33f) + 1.5 first preview deploy. **Preview alias LIVE: `https://redesign.klantkraan-marketing.pages.dev`** (apex still old design). All 3 home locales verified 200 + art. 50 + dispatch panel. **NEXT = Phase 2 G1 trade landings.** ■
- [ ] **Phase 2 — Groups** (parallel draft / serial verify): ■ per group
  - [x] **G1 trade landings** — DONE 2026-07-23 (ccf2ba3 + 332cacf). 26 files: shared `dakdekkers/*` set (9) + primitives Stat/RiskReversal/VerderLezen + 6 self-contained NL + 8 self-contained EN. NB "shared set, all inherit" was wrong — only `dakdekkers.astro` uses the set; every other trade page is self-contained. Locked token/pattern map in runbook §8 (reuse for G2-G4). 0 kraan- left in all 15 trade pages; build green, audit clean. Site-wide kraan- burn-down ~1998 → 1009.
  - [x] **G2 conversion** — DONE 2026-07-23 (055b242 + 42609b9). prijzen/rekentool/demo/voor-wie/over NL+EN+ES (15) + `demo/sportscholen` NL folded in (16 files). Same G1 deterministic transform + locked map. `/demo` + `/demo/sportscholen` keep the live chatbot + overlay (shell restyled only). Audit fix: rekentool inputs got inputmode+autocomplete. Build green, astro check 0/0, eyeballed desktop+320px+ES. Site-wide kraan- burn-down 1009 → 424 across 18 files.
  - [x] **G3** `[stad]/[vak]` template (+ `r/[slug]` dashboard) — DONE 2026-07-23 (7f3255a). Both used only tokens/patterns in the locked G1/G2 rule table -> same deterministic transform, RULES copied verbatim, zero new rules, zero residuals (65 + 40 kraan- -> 0). Dashboard's `<script>` innerHTML classes migrated by the same substring pass; error alert -> sodium-bordered panel (no red in the palette). Build green, astro check 0/0, eyeballed `/amsterdam/loodgieter/` desktop+320px + `/r/example`. Site-wide kraan- burn-down 424 -> measured 269 (266 real tokens; 3 are `Klantkraan-` brand-copy false positives). Remaining = G4 (~189) + non-page components DashboardMock/LeadForm/RingingPhone (64) + global.css `@theme` tokens (13).
  - [x] **G4** reading variant (blog/gidsen/legal/404) — DONE 2026-07-23 (a072182). 11 files: blog index+[slug], gidsen index+[slug], 404, 6 legal. Already calm document layouts, so a straight token migration; 3 structural specials (alt stone-100 sections -> recessed band; bg-white/cream cards -> panel; inline buttons -> `.btn` primitives, night-on-sodium avoids the white-on-amber trap). Reading-variant restraint: dim kickers left muted, not upgraded to sodium eyebrows. 0 kraan-/bg-white/text-white in all 11; build green, astro check 0/0, eyeballed all 6 page types desktop+320px. **Phase 2 DONE — all groups migrated.** Site-wide `--color-kraan` burn-down 266 -> 73 (all non-page: global.css @theme tokens 11 + DashboardMock 31 + LeadForm 30 + RingingPhone 1). ■
- [x] **Phase 3 — Audit + polish** — DONE 2026-07-23 (commits da182ca components + beb42c8 audit). Migrated the last 3 non-page components + deleted the 11 deprecated `@theme` kraan tokens → `grep -r -- '--color-kraan' src` empty (only `Klantkraan-` brand copy remains). NB DashboardMock + LeadForm were dead code (unimported) — migrated for consistency, founder may prefer to delete. Whole-site web-design-guidelines pass: structural rules already satisfied per-group; fixed `text-wrap:balance` global rule, 2 critical-font preloads, ellipsis labels, deferred-de-AI em-dashes (legal titles→pipe, DPA annex→colon, LeadForm→period, `/r`→colon). Curly quotes deferred (documented). Verified a11y (sodium `:focus-visible`), view-transition continuity (html bg = night everywhere), reduced-motion (resting stamp), `/demo` widget (iframe + art. 50), 320px, all 3 locales, €299/€499 parity, no AI-tells. Build green, astro check 0/0. **Preview alias REDEPLOYED with the full site** (`7f8d95f0`, `https://redesign.klantkraan-marketing.pages.dev`; apex still old design). ■
- [x] **Phase 4 — Cutover — SHIPPED 2026-07-23.** Founder gave the go; fresh rebuild from HEAD (d119833) → `pnpm dlx wrangler@4 pages deploy ./dist --branch=production --project-name=klantkraan-marketing` → deployment `22c89e15`. **`klantkraan.nl` is LIVE on the new design.** Verified: all page types + locales 200 + dark `theme-color #0f1c1e`; home renders correctly (fonts, dispatch panel, calc teaser, art. 50) via live screenshot. **Redesign project complete.** Optional non-blocking cleanups left: delete 2 dead components (DashboardMock/LeadForm), curly-quotes pass.

### I. Workflow depth — P0 only (added 2026-07-28)
Plan: **`docs/01-strategy/workflow-depth-plan.md`** (gates + phases + kill criteria). Why:
`research/automation-expansion-2026-07.md`. What to build: `ai-receptionist/docs/WORKFLOW-MOAT.md`.
**Nothing gets built until 3 paying clients.** Only the boxes below are live — they are either
zero-cost research or blocked on someone else's clock.
- [ ] **Closeout test** — from pilot #1's go-live, founder sends the end-of-day "klaar?" message BY HAND on WhatsApp for 10 working days (~5 min/day, no code). Log reply rate, latency, whether the reply is parseable. Green ≥7/10 → build the owner channel; ≤3/10 → the build order changes. Tests the assumption everything past a booking depends on.
- [ ] **Meta Business verification → production WhatsApp sender** — we are on the Twilio *sandbox*, which cannot send approved templates, so it blocks every outbound module. Needs the KvK/BTW numbers from §D first. Long lead time; start early, it is waiting-time not work-time.
- [ ] **Ask the office question on every discovery call** — *"Als er één ding op kantoor vanzelf zou gaan — wat zou dat zijn?"* Log verbatim against the prospect in `app/pipeline.py` notes. The tally picks module 1, not the roadmap.
- [x] **Draft 5 Dutch utility templates** — DONE 2026-07-29, `ai-receptionist/docs/whatsapp-templates.md`. All five written as transaction status with `{{n}}` slots (positional, matching Twilio's Content API), plus the category rules verified via context7, a submission checklist, and the `correct_category=MARKETING` audit query so a silent re-categorization surfaces instead of showing up in a bill. **Correction to the moat doc:** the reviewverzoek should not be assumed utility — asking for a review is persuasive intent by Meta's criteria, so it is drafted in a conservative variant A (submit this) and a direct variant B, and the cheaper path is sending it inside the 24h window with no template at all. NOT SUBMITTED — blocked on the production sender below.
- [ ] **Mid-September: re-model `07-finance/`** — from 1 Oct 2026 Meta bills service replies inside the 24h window, hitting the €299 core product (~1,600 msg/client/mo). The ~97% margin is stated on today's rules. Do not guess the rate; wait for Meta to publish it. Likely answer is a fair-use ceiling in the contract, not a price rise.
- [ ] Reposition site + deck: "de AI-telefoniste" → **"het kantoor dat meedraait"**, office work shown as roadmap not as shipped. (Copy pass, no product change.)
  - [x] **Site half done 2026-07-29** — new `components/home/Roadmap.astro` on all three homepages, between the honesty section and the how-to-start steps: what it does today vs what we are building. Honesty is structural, not a disclaimer (solid panel + sodium edge + checks for live; no fill, dashed border, dim clock icons for roadmap, and "nog niet beschikbaar, u betaalt er nu niet voor" *above* the list). The four roadmap items are exactly the five WhatsApp templates' jobs, so the story and the build queue are one list. Hero left alone on purpose: "Het licht blijft aan" is founder-approved and already says the place keeps running.
  - [ ] **Deck half NOT done** — no pitch deck was touched.

### J. Workflow adoption — verification gates + ops tooling (added 2026-08-10)
From `research/claude-code-workflow-videos-2026-08-10.md` (7 Agentic Lab videos + prompt survey).
Through-line: catch failures with deterministic gates, don't prevent with prompt rules. Small
items only — never displaces dials.
- [x] `scripts/copy-lint.sh` — built + negative-tested (68d544e). Sweep of docs/02-sales: 849 findings — 2 banned-phrase (voltwerk call-review quotes), 13 founder-name (offerte-coolglobal sender lines, playbook, call sheets), 674 dash (mostly internal docs), 160 stale-phone (all prospects' own numbers — no old Klantkraan number found anywhere). FOUNDER decides what to clean; findings list in the session scratchpad
- [x] `scripts/compliance-check.sh` + CI job — art. 50 in all 41 business configs OK; outreach CSVs BV-only-ungated OK; wired as 4th CI job (68d544e)
- [x] Hallucination eval pack in `ai-receptionist/app/evals.py` — 6 goldens (`run hallucination`), baseline 3/6 → 6/6 after 5 never-invent prompt bullets; full suite 14/14, 236 tests + ruff green (82bf27a). NOT deployed — founder retest gates deploy. NB: CI's ruff-format job was already red on this branch (pre-existing drift in 9 files)
- [x] Mirror the voice hallucination cases as Cekura scenarios (agent 21227) — 6 scenarios in folder "Hallucination" (317129–317134: out-of-scope glass, €200 price-cap trap, unknown staff "Kees", guaranteed-arrival demand, Koningsdag hours, vague request), own test profiles, nl, same 11 metrics as First Run. Also softened the John/regio clauses in 316615/316617/316622 + agent description per the founder's parked decision (regional locksmith name + 5-15 min callback window OK; guaranteed arrival time never). NOT run yet — each run = real calls, founder triggers
- [x] `.claude/commands/`: `/deploy-site`, `/run-evals`, `/board`, `/log-regression`, `/new-client-demo` — all invocations verified against source (5b8624c)
- [x] Stop-hook dispatcher in `.claude/settings.json` — git-diff-scoped: copy-lint on touched artefacts, pinned ruff on touched .py, non-blocking evals reminder on receptionist prompt/config change; fail-open, loop-guarded, exit 2 feeds findings back (54911d8). NB: open `/hooks` once or restart Claude Code to activate in running sessions
- [x] Daily ops briefing agent (`ops/briefing/`) — built + dry-run verified on real data (bd280c6). FOUNDER (4 steps in ops/briefing/README.md): bot chat id via `app.notify chatid`, Gmail app password, `~/.klantkraan-briefing.env`, load the launchd plist
- [x] Growth-engine verify pass — Haiku judge, 6 criteria, one auto-revise then deliver-flagged; toggle `GROWTH_ENGINE_VERIFY` (default on); 10 offline tests + ruff green (e5424a5). Needs a redeploy of growth-engine to go live on the server
- [ ] Prompt refinements after eval pack: few-shot golden snippets (postcode, kenteken), Chain-of-Draft conciseness rule, restate-before-booking; TTFB check + Cekura rerun after
- [x] Policy lines in CLAUDE.md: prompt-rule-needs-failing-golden; no wholesale rewrites of CLAUDE.md/MEMORY.md; markdown-folder memory only (no vector DBs/plugins) (2026-08-10)
- [ ] Habits (no build): rewind-after-debug, recon-then-trim

### K. Command center (Phase 1 of research/PLAN-command-center-factory-2026-08-12.md)
- [x] Step 1: `scripts/kk` dispatcher — cwd-proof CLI over existing tools (board/deal/outreach/evals/billing/health/logs/deploy); 6/day outreach cap enforced in code, server deploy gated on evals; 21 offline tests + ruff green (22b39d4)
- [x] Step 2: ledger fixes (`created_at`, `dry_run` tagging, durable push-failure records, sequence.py path anchor) + `kk content` + `kk leads` readers; 26 kk tests + 3 approve-ledger tests, all suites green
- [x] Step 3: `kk-alert@.service` OnFailure= → founder alert on all systemd units (`app.notify alert <unit>` sends redacted journal tail, Telegram → e-mail fallback; growth-engine units get StartLimit so crash loops fail loudly; caddy drop-in via deploy.sh; `kk health` now lists failed units + flags unconfigured alert delivery). Ships on next `kk deploy server`.
- [x] Step 4: status page — `ops/status/generate.py` (RAG header, today's numbers, deals, outreach, content, billing, timer matrix; fault-isolated collectors, no JS) + `klantkraan-status.timer` every 15 min + Caddy basic-auth vhost at status.<demo-host> (password generated once by deploy.sh, shown once); `kk status` (terminal) / `kk status open` (HTML) / `kk status push` (deal+outreach snapshot → server, since that data lives on the Mac). 17 new offline tests (45 total in scripts/tests), ruff clean. Ships on next `kk deploy server`.
- [x] Step 5: briefing merged into the 07:30 digest — `app/mail_signals.py` (read-only IMAP: last-24h replies + DSN/bounces with failed-recipient extraction, MAIL_WATCH_SENDERS pins live deals) appended by the digest CLI/timer path only; `ops/briefing/` deleted (plist was never installed). Server needs GMAIL_USER+GMAIL_APP_PASSWORD in ai-receptionist/.env or the digest says "MAIL: skipped". 10 new offline tests, live --dry verified against the real inbox.
- [x] §C5 defects 6–8 closed: 6 = `docs/regressions.md` created (two-line header, /log-regression appends); 7 = false alarm, `BUFFER_CHANNEL_LINKEDIN` is live config via `channel_for()`'s dynamic `BUFFER_CHANNEL_<PLATFORM>` lookup (publish_buffer.py, shipped 2026-07-30 — the audit grep missed the f-string); 8 = rewrite/recording waits moved from chat_data to a durable `awaiting` field on the draft record + `_post_init` resurfaces delivered-but-undecided drafts (buttons only, no media re-upload); 4 new offline tests in growth-engine/tests/test_awaiting_restart.py. Defect 5 closed with step 3; the founder still owes OWNER_TELEGRAM_CHAT_ID or OWNER_EMAIL+RESEND_API_KEY in the server's ai-receptionist/.env (`kk health` shows which)

## Phase 0 — Planning docs

### `00-MASTER-PLAN.md` + `README.md`
- [x] `klantkraan/README.md`
- [x] `klantkraan/docs/00-MASTER-PLAN.md`

### 01-strategy
- [x] `icp.md`
- [x] `offer-and-pricing.md`
- [x] `positioning.md`
- [x] `90-day-roadmap.md`

### 02-sales
- [x] `cold-email-sequences.md`
- [x] `linkedin-cadence.md`
- [x] `discovery-script.md`
- [x] `objection-handling.md`
- [x] `offerte-template.md`
- [x] `funnel-benchmarks.md`

### 03-delivery
- [x] `onboarding-playbook.md` (text-first; supersedes voice-era `onboarding-30-day.md`, now deleted)
- [x] `churn-prevention.md` (read metric/channel swaps against the playbook §7/§8)
- [x] removed voice-legacy docs `intake-form.md`, `sms-templates.md`, `synthflow-system-prompt.md`, `dashboard-spec.md` — playbook owns intake §2 / channel §5 / metrics §7 / churn §8 (172ccaf)

### 04-legal
- [x] `msa-outline.md`
- [x] `dpa-outline.md`
- [x] `sla-annex.md`
- [x] `ai-act-disclosure.md`
- [x] `insurance.md`
- [x] `compliance-checklists.md`

### 05-content
- [x] `channel-strategy.md`
- [x] `first-30-days-calendar.md`
- [x] `seo-keywords.md`
- [x] `content-stack.md`

### 06-outbound
- [x] `gdpr-compliance.md`
- [x] `data-sources.md`
- [x] `deliverability-stack.md`
- [x] `compliance-kill-list.md`

### 07-finance
- [x] `unit-economics.md`
- [x] `mrr-projections.md`
- [x] `cogs-per-tier.md`
- [x] `first-hire-triggers.md`

### 08-tech
- [x] `stack-decisions.md`
- [x] `repo-architecture.md`
- [x] `infra-setup.md`
- [x] `observability.md`

### 09-brand
- [x] `naming-and-domain.md`
- [x] `voice-and-tone.md`
- [x] `visual-identity-brief.md`
- [x] `logo-designer-brief.md` (Fiverr Pro brief + v0/Recraft prompts)

### 10-ops
- [x] `weekly-kpi-review.md`
- [x] `risk-register.md`
- [x] `founder-tooling.md`

## Phase 0.5 — Founder real-world actions (BLOCKING)

See `docs/00-MASTER-PLAN.md § 5`.

- [x] Verify `klantkraan.nl` available — https://www.sidn.nl/en/whois (verified 2026-05-20)
- [x] Verify `klantkraan.com` available — https://lookup.icann.org/en/lookup (verified 2026-05-20)
- [x] KvK handelsnaam search "Klantkraan" — https://www.kvk.nl/zoeken/ (no conflict, 2026-05-20)
- [x] BOIP trademark search class 35 + 42 — https://www.boip.int/en/trademarks-register (no conflict, 2026-05-20)
- [x] Register `klantkraan.nl` (TransIP, 2026-05-20)
- [x] Register `klantkraan.com` (TransIP, 2026-05-20)
- [x] File `handelsnaamwijziging` "Klantkraan" under T4 at KvK (2026-05-20)
- [ ] Hiscox PI quote ICT — https://www.hiscox.nl/beroepsaansprakelijkheidsverzekering-ICT
- [ ] Synthflow trial: test 30 min Dutch voice quality
- [ ] CM.com signup + reserve 1 Dutch landline
- [ ] Moneybird trial open + 21% / reverse-charge / ICP configured
- [ ] Confirm €5–6k personal cash bridge available
- [ ] LinkedIn profile audit (real-name, faceless avatar OK)

## Phase 1 — Scaffolding (after Phase 0 complete)

### Tooling baseline
- [ ] Enable `context7` MCP server (using `ctx7` CLI for now — equivalent)
- [x] Repo monorepo: pnpm + Turborepo skeleton

### Marketing site (Astro on Cloudflare Pages)
- [x] `apps/marketing-site` scaffold (Astro 5 + Tailwind 4 + Cloudflare adapter + brand tokens)
- [x] Home + `/loodgieters` + `/dakdekkers` (home complete; /loodgieters + /dakdekkers stubs to expand)
- [x] `/prijzen`, `/rekentool` (ROI calc), `/demo`, `/over`
- [x] `/legal/{voorwaarden,dpa,sla,privacy,ai-disclosure,subprocessors}`
- [x] Lead form → Cloudflare Worker → Attio API (UI on / posts to /api/lead; CORS allow-list set)
- [x] Deploy to Cloudflare Pages (live at `https://klantkraan-marketing.pages.dev`, 17+ routes 200, 2026-05-20)
- [x] Mobile optimization pass (9 commits, 2026-05-20): typography scale, hamburger + disclosure menu, 44px touch targets, responsive padding, prijzen cards on mobile, skip-to-main link, blank-button + hamburger-click iOS fixes
- [x] Aesthetic pass per brand brief (6 commits, 2026-05-20): Lucide icons site-wide, rust hero accents, full-bleed cream/stone-100 alt-bg sections, Stat component with rust marker, mono section kickers, hairline-divided feature rows, link underline reveal
- [x] Competitor-research polish (5 commits, 2026-05-20): three-icon trust badge strip (AVG + EU + Dutch voice), Article 50 transparency callout, day-price framing on /prijzen
- [x] `/elektricien`, `/installateur`, `/aannemer` profession landings (template clone, trade-specific copy)
- [x] Attach `klantkraan.nl` + `www.klantkraan.nl` custom domains (NS propagation completed; both live over Cloudflare, verified 2026-07-13)

### Automation infra
- [x] Hetzner CX22 + Caddy + docker-compose (compose + Caddyfile + deploy.sh + borg-backup.sh ready; not yet provisioned — founder action)
- [ ] n8n self-hosted, Postgres on Neon (workflow JSONs versioned; awaits VPS provisioning)
- [ ] Healthchecks.io + Sentry + Uptime Kuma (Uptime Kuma in compose; HC + Sentry env wired in code, accounts pending)

### Per-client product
- [x] Synthflow Dutch agent template (`packages/prompts/nl/{loodgieter,dakdekker}.v1.md` + agent JSON)
- [x] Missed-call-back n8n workflow (CM.com webhook → SMS) — `infra/n8n/missed-call-back.json`
- [x] Review automation n8n workflow — `infra/n8n/review-request.json`
- [ ] Cal.com event-types template
- [x] Client dashboard page `/r/[slug]`

### Content (wave 3)
- [x] `/blog` Astro Content Collection + 2 Dutch SEO cornerstone posts
- [x] First 17 LinkedIn personal-profile post drafts (`marketing/linkedin/drafts/`, weeks 1–4; 11 ship-ready, 6 holdback awaiting pilot data)
- [x] Programmatic SEO Wave 1 (10 G4 city×niche pages live, /[stad]/[vak] route, src/data/{cities,niches,wave1}.ts — 2026-05-21)
- [ ] Programmatic SEO Wave 2 (next 10 pages: Eindhoven niches + Den Haag/Utrecht loodgieter + Amsterdam/Rotterdam aannemer — wait T+6 wk for Wave 1 indexation per blueprint §6)

### Tooling integrations
- [ ] Attio workspace + pipeline + automation hooks
- [ ] PandaDoc / SignWell templates
- [ ] Mollie + Moneybird invoicing
- [ ] Tally intake form

### Demo assets
- [ ] Chat header X button is dead on the /demo pages: it posts the widget
      close message (`web/index.html` ~l.134) but the demo iframes have no
      listener — only `widget.js` on client sites does. Fix: replace it with
      a restart control (↺, clears session + log, fresh greeting) on demo
      pages, keep X-as-close only for the real widget embed.
- [ ] Public AI demo number (+31 ...) live
- [x] ROI calculator live (page built; goes live with Pages deploy)
- [x] Founder bio page with KVK + DPA download (added to `/over`: founder section + 3-column downloads block; KvK PDF path placeholder until founder uploads)

## Phase 2 — Pilots + outbound (after Phase 1)

- [ ] 2 pilot clients onboarded
- [ ] First case study published
- [ ] Smartlead inbox warm-up complete (3 weeks)
- [ ] Cold email Sequence A live
- [ ] LinkedIn cadence via HeyReach live
- [ ] First 4 LinkedIn posts published
- [ ] First 2 SEO cornerstones published

## Test gates (Ralph loop)

Before ticking a Phase 1 task as done:
- Build passes
- Lint passes
- Run-locally smoke check
- Eyeball the rendered output
- Commit with the *why* in the message

Before ticking a Phase 2 task as done:
- The pilot client has confirmed the artefact (call, dashboard, SMS, review)
- The artefact appears as expected in Attio + Postgres + the Cloudflare dashboard
