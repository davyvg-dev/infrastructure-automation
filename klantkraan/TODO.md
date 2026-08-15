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

### L. Marketing loop 1 — gemiste-omzet calculator + e-mailcursus (Phase 2.1 of research/PLAN-command-center-factory-2026-08-12.md)
- [x] Step 1: `app/cursus.py` — subscriber ledger (data/cursus/), 4 Dutch lessons over Resend (day 0/2/5/9, one lesson per run max, List-Unsubscribe + HMAC afmeldlink, Idempotency-Keys), completion scored onto the pipeline board as inbound opt-in lead; mailer.py headers passthrough; CLI board/send/preview/add/stop/link; 18 offline tests, suite 268 green (f191538)
- [x] Step 2: FastAPI opt-in — `POST /api/cursus` (JSON + no-JS 303 path, honeypot, rate limit, founder ping, fires les 1 via `send_due(only=...)`, failed send never fails the opt-in) + `GET /cursus/uitschrijven` confirm page (prefetch-safe) with `POST` doing the stop, incl. RFC 8058 one-click header; 13 endpoint tests, suite 281 green
- [x] Step 3: `klantkraan-cursus.timer` (daily 09:15, Persistent) + `klantkraan-cursus.service` (oneshot `app.cursus send`, OnFailure=kk-alert@) + deploy.sh copies both and enables the timer + `kk cursus` passthrough verb (default board) + `cursus` LOG_UNITS alias; 4 new planner tests (49 total in scripts/tests), ruff clean. Ships on next `kk deploy server`.
- [x] Step 4: site — rekentool grows the Werkspot-math panel (leads €3–75, ±€208/gewonnen klus per Adaptoo, "van ú" close) + e-mailcursus opt-in form (native POST → /api/cursus with ?cursus=ok|fout fallback, rekentool.js fetch() enhancement toggling per-locale markup, honeypot, CSP already allowed both paths), NL/EN/ES; calculator stays e-mail-free. Typecheck 0 errors, build green, form/action/scoped-hp verified in dist. NOT DEPLOYED: founder runs `kk deploy server` FIRST (ships /api/cursus + timer + Phase 1 steps 3–5, prints status-page password ONCE), THEN `kk deploy site` — site first would ship a form that 404s

### M. Marketing loop 2 — vertical pSEO + GEO factory (Phase 2.2 of research/PLAN-command-center-factory-2026-08-12.md)
~40–60 Dutch pages, vertical × problem × comparison. NEVER city×service: `wave2.ts` stays
unwired and seo-strategy §S7's NO-GO stands. Data-product rules (agentic-marketing research §3
+ seo-strategy quality gates): boilerplate <60% per page, every page ≥1 unfakeable element,
answer-first H2 openers, visible "laatst bijgewerkt", Organization-as-author. Stats policy
(first-client research §1) is law: banned folklore list (62%/85%/voicemail/3-nummers), only
sourced stats + the euro-math formula framing ("X gemiste calls × €Y per klus"). Pipeline
reality (recon 2026-08-13): growth-engine drafts are social-post-shaped (2000-token schema,
4096-char Telegram preview) so pages get their own draft kind delivered as a .md document; the
server has no Node and Pages has no git integration, so approval never auto-deploys — approved
pages land in the rsync-durable data dir, founder pulls and ships with `kk deploy site`.
- [x] Step 1: site foundation — `pseo` content collection (schema: title ≤60, description ≤155,
      vertical over all 7 branches, type `probleem|vergelijking|hub`, targetKeyword, faq[],
      stats-used incl. bron, laatstBijgewerkt, related slugs) + shared `JsonLd.astro` component
      (factor the FAQPage builder out for new pages; retrofitting the 13 inline copies is a
      later cleanup) + one top-level dynamic route rendering the collection (answer-first
      sections, `<details>` FAQ, BreadcrumbList + FAQPage + Article JSON-LD, VerderLezen +
      hub-and-spoke link block, NL-only per the i18n pattern) + 2 hand-written seed pages
      proving template + boilerplate ratio (1 probleem, 1 vergelijking); copy-lint clean,
      typecheck + build + eyeball
- [ ] Step 2: data layer + inventory — `src/data/pseo.ts` (approved-stats registry with
      bron+datum, per-vertical euro-math table, competitor/pricing table from
      competitor-pricing.md + website-market-pricing incl. STUDIOLEE/LoodgieterAI) +
      `pseo-inventory.json`: ~40–60 planned slugs (7 verticals × problems, ~12 comparisons,
      2–3 hubs) with target keyword + angle + data-block refs; JSON so Astro imports it for
      link blocks AND the server-side drafter reads the rsynced copy. FOUNDER gate: approve the
      inventory before drafting starts
      — code DONE 2026-08-13 (44 pages: 23 probleem / 18 vergelijking / 3 hubs; extra
      vertical 'vakmensen' for cross-vertical cluster-D pages; elektricien/installateur/
      sportscholen have NO published job value → formula-only, herkomst 'geen');
      GATE PENDING: founder approves the inventory, then step 3 may start
- [ ] Step 3: drafter — growth-engine page module: nightly in-process JobQueue job in the bot
      (one page/night ≈ 30/mo, no cross-process queue.json writes), own draft schema with
      page-sized max_tokens, prompt carries the stats registry + banned list + boilerplate
      rule, page-specific verify criteria (invented stats, u-register, em-dashes, founder
      name), body stored under durable `data/<vertical>/pages/`, Telegram delivery = summary +
      .md document + approve/rewrite/skip buttons, approve only marks approved (no publisher
      fanout), GROWTH_ENGINE_DRY_RUN honored; offline tests in growth-engine/tests
- [ ] Step 4: ship path + GEO — `kk pages` verb (board: inventory vs drafted vs approved vs
      live; `kk pages pull` rsyncs approved .md into `src/content/pseo/`), llms.txt section
      refreshed from the collection at build time, close the gidsen JSON-LD gap, deploy stays
      founder-run `kk deploy site` after eyeballing pulled pages; verify sitemap pickup +
      schema validity + copy-lint on pulled content

### N. Command center dashboard — client-grade branded status page (planned 2026-08-14)
Presentation-layer upgrade of `ops/status/generate.py` over the same collected data: static,
no-JS, behind the existing basic auth, branded in the site's night/sodium system so it doubles
as a sales asset ("dit is de cockpit die u krijgt"). `render_ansi`/`_section_lines` untouched
(`kk status` terminal output unchanged); new HTML renderer reads `data["sections"]` directly.
RAG colors: confirm green / sodium amber / dashboard-local ember red (inline CSS only — the
site palette gets no red). Dutch labels, u-register, no em-dashes, no founder name. Fonts
copied next to the output by a `_write_assets` helper (repo woff2; system-font fallback).
- [x] N1-N4 (one commit): render_html() replaced by per-section renderers over
      `data["sections"]` (render_ansi/_section_lines untouched); brand tokens inline, page-
      local ember red #e0654f (global.css untouched), RAG pill = dot + GREEN/AMBER/RED +
      Dutch gloss, 7 Space Mono KPI tiles, Vandaag/Deals (due-callback chip)/Outreach/
      Facturatie/Content/Systeem panels, faults as sodium-bordered panels, timers as mono
      ledger; `_write_assets` copies 5 woff2 subsets next to the output (skip-if-present,
      no-op on missing source); Dutch labels, all-escaped, noindex + refresh 900 kept;
      scripts/tests 56 green, ruff clean, eyeballed real-data desktop + red fixture at 320px
- [ ] N5: FOUNDER ships `kk deploy server`; verify fonts + page at the basic-auth status URL

### O. Email list — opt-in everywhere, lead magnet, nieuwsbrief (planned 2026-08-14)
Builds on the §L cursus machinery. Compliance fixes first (live gaps), then site coverage,
then the broadcast layer. Opt-in stays NL-only (course is Dutch); nieuwsbrief sends are
founder-triggered, never a timer.
- [x] O1: afmelding now writes `data/suppression.txt` — helper extracted to
      `app/suppression.py` (call-time DATA_DIR, shared by `sequence.py --opt-out` and
      `cursus.stop()`); bounce deliberately NOT suppressed (a dead mailbox says nothing
      about consent, mirroring sequence.py's rule); 2 new tests, suite 283 green
- [x] O2: `POST /api/resend/webhook` — svix-signature-verified (stdlib hmac against
      `RESEND_WEBHOOK_SECRET`, 5-min replay tolerance, constant-time compare); Permanent
      bounce → halt only, complaint → halt + suppress (also for non-subscribers, e.g. the
      welcome mail); unconfigured secret → 503 so svix retries and no event is lost; 7
      tests, suite 290 green. FOUNDER: set `RESEND_WEBHOOK_SECRET` in the server .env and
      add the webhook (events: email.bounced + email.complained) in the Resend dashboard,
      endpoint https://demo.klantkraan.nl/api/resend/webhook
- [x] O3: `cursus.digest_lines()` in both build_digest paths (aanmeldingen/actief/
      afgerond/afgemeld/bounced/due; empty ledger = no section; unreadable ledger = warning
      line, digest still goes out); 3 tests, suite 293 green, live `--dry --today` eyeballed
      → ready for `kk deploy server`
- [x] O4: `CursusForm.astro` (lang prop with full per-locale strings, recessed/embedded
      variants, scoped honeypot) + `public/js/cursus-form.js`; rekentool ×3 swapped;
      typecheck 0, build green, dist eyeballed (586d6c2)
- [x] O5: opt-in band on the 7 NL trade landings + homepage (after the honesty section) +
      /voor-wie; EN/ES untouched (bdca6eb)
- [x] O6: gidsen/[slug] (recessed), blog/[slug] (embedded), [pseo].astro — templates, so
      all future pSEO pages inherit it (6730e64)
- [x] O7: lead magnet — one-A4 telefoonchecklist "Nooit meer een klus missen"
      (tools/lead-magnet/telefoon-checklist.html + build.sh via headless Chrome →
      public/downloads/nooit-meer-een-klus-missen.pdf); fully qualitative, no stats;
      copy-lint clean, PDF eyeballed, dist carries it
- [x] O8: les 1 links the checklist ("Voor bij de telefoon" block + button to
      klantkraan.nl/downloads/nooit-meer-een-klus-missen.pdf, URL pinned as
      `cursus.CHECKLIST_URL`); deploy order: site (O7 PDF) before the next les-1 send;
      1 test, suite 301 green, preview eyeballed
- [x] O9: `app/nieuwsbrief.py` — broadcast layer on the SAME subscriber ledger (one
      afmelding stops cursus + nieuwsbrief), resumable broadcasts.json written per send,
      .md front-matter input → mail_layout blocks, `nb-<id>-<email>` Idempotency-Keys,
      List-Unsubscribe + RFC 8058 one-click, `--dry`, 1/sec pacing, corrupt ledger exits
      loudly; CLI board/send/preview; suppression.entries() reader added; 7 tests, suite
      300 green, preview eyeballed
- [x] O10: growth-engine drafter — `src/newsletter.py` draft kind (max_tokens 4000,
      structured output), monthly JobQueue job (1st, 09:30 Amsterdam, dedupes per month) +
      `/nieuwsbrief` manual trigger, Telegram delivery = .md document + summary +
      approve/rewrite/skip, verify pass = Haiku judge + deterministic checks (u-register,
      dashes, founder name, numbers outside 299/499/24-7, subject/preheader budgets,
      150-350 words, ≤1 button to /demo|/rekentool), approve writes
      `data/trades/newsletters/editie-YYYY-MM.md` and marks approved only; kk verb
      re-pointed at the vertical-scoped path; growth-engine tests 17→42 green, ruff clean
- [x] O11: `kk nieuwsbrief send [--dry] [--file <naam.md>]` + `board` — server-side over
      ssh (ledger lives there), runuser as klantkraan, newest .md from rsync-durable
      `growth-engine/data/newsletters/` unless --file names one (bare .md names only);
      3 planner tests, scripts/tests 52 green
- [ ] O12: FOUNDER first edition: draft → approve → `--dry` → send (`kk deploy server` first)

### P. Website factory — pilot kit (planned 2026-08-14; Phase 3 of the factory plan)
Narrow-pilot principle holds: build the kit, do the first site BY HAND for a warm prospect,
measure founder-minutes per stage. NOT built now: `kk factory` verb, TransIP API, generator
CLI. Template rules baked in: click-to-call primary CTA, no review/aggregateRating schema,
max 3–5 city pages, photo-free fallback, no external embeds (cookie-banner-free stays a
verifiable sales feature), KvK+btw footer, privacyverklaring names the receptionist processor.
- [x] P1-P4 (one commit, 65dc94f): `apps/client-sites/` — Zod client.yaml (8-digit KvK,
      +31 phone, ≤5 plaatsen, WCAG contrast check on brand color, NO price fields),
      CLIENT=<slug> selection failing loudly, 9-page template (click-to-call primary, no
      contact form, no aggregateRating, color-block photo fallback, zero external
      requests = cookie-banner-free verifiable, KvK/btw footer, verwerker-naming privacy
      page), fixture voorbeeld-dakdekker, QA battery run (squirrelscan 131 rules + greps)
      and recorded in QA.md; copy-lint clean; real client dirs gitignored (PII); build +
      typecheck green, homepage eyeballed over http
- [x] P5: `docs/03-delivery/website-intake-checklist.md` — Dutch client part (10-foto shot
      list + 5 top-up questions, prijzen bewust niet) + internal scrape-first procedure
      (extract/scaffold, completeness gate starts the week-promise clock, client dirs stay
      out of git); copy-lint clean
- [x] P6: `docs/03-delivery/website-pilot-runbook.md` — stages 0-7 incl. completeness gate,
      QA.md battery reference, TransIP NS with the UI-lies failure mode (dig verify),
      Pages deploy + custom-domain REST curl (wrangler can't), Email Routing client click,
      Pages cache-poison smoke, IP-akte on final payment, domain in client's name;
      copy-lint clean
- [x] P7: `website-maintenance-scope.md` (2 tekst/foto-edits per maand in writing, meerwerk
      list, opzeggen = site + domein mee, internal margin notes) +
      `website-pilot-timing-log.md` (stage table vs research targets + automation decision
      rule); copy-lint clean
- [x] P8: kit complete; the two FOUNDER blockers before a pilot can invoice:
  - [ ] FOUNDER: fix seller BTW-id/address placeholders (invoices not legally valid yet —
        also blocks §D and the BTW memory item)
  - [ ] FOUNDER: the pilot needs a real buyer — sell the website into an existing deal
        (DRS reply spotted 2026-08-14 / Cool Global t/m 24-08 / riool sprint wk 24 aug)

### Q. Website factory — voorstel-sites as the opening move (built 2026-08-14)
The kit could only build a site for someone who had already bought, so it could not help with
the one blocker that was actually open (no buyer). Q turns the factory into outreach ammunition:
a real, working, noindexed proposal site per prospect, built from public sources in ~10 founder
minutes. Deliberately NOT built: TransIP automation, per-dienst pages, client-site monitoring,
a public /website sales page. (An og:image pipeline was on this list until Q9 — the photo rework
gave the page a photograph worth cutting a share card from, which is why it was cheap.)
- [x] Q1 (d07ed30): `modus: preview | live` required in the schema (no default: a forgotten
      mode must fail, never silently publish a proposal or silently noindex a paying client).
      Live keeps every legal field mandatory; preview allows KvK/btw-id/e-mail/adres/domein to
      be absent and answers with noindex + X-Robots-Tag + robots Disallow, no sitemap, no
      LocalBusiness JSON-LD, no reviews, receptionist false, a non-dismissable banner naming
      Klantkraan, and canonicals on `<slug>.klant-preview.pages.dev`. Second fixture added.
- [x] Q2 (d3f39c8): `app.sitedraft` bridges `app.extract` into a client.yaml — telefoon and
      openingstijden mapped in code from the cited extraction, the Dutch copy from one
      schema-constrained Claude call that must paraphrase and may not invent claims or prices;
      `--from-json` reuses one scrape for both the receptionist config and the site. 12 tests.
- [x] Q3 (844b617): `CLIENT=<slug> pnpm check` — the fact gate research §7 risk 4 asked for.
      Re-reads the yaml itself and asserts dist/ against it (phone, every tel:/mailto:/wa.me,
      diensten, city pages, KvK+btw, no placeholders, no prices, no review schema, zero
      external hosts, per-mode publishing posture, structural greps). Proven by sabotage: all
      seven mutated builds exit 1.
- [x] Q4 (55c6394): `kk site new|build|check|open|deploy` — one command instead of seven, with
      two refusals in the planner (a voorstel cannot go live; a paying client cannot land on
      the shared preview host). scripts/tests 73.
- [x] Q5 (a22bc6b): `docs/03-delivery/website-voorstel-playbook.md` — the sales motion and the
      rules it does not relax (BV filter, no cold e-mail to eenmanszaak/VOF, 6/day, no cold
      calling, public sources only, take it down on request), the by-eye check, the Dutch
      first touch, and how a voorstel is promoted to a live client. Runbook + intake checklist
      re-pointed at `kk site`.
- [ ] Q6 FOUNDER: first real voorstel end to end. Pick a prospect already in the sequence,
      run `kk site new` → `build` → `open` → `deploy`, time it, and send it as the opener.
      Needs a Cloudflare Pages project named `klant-preview` to exist first (one-off).
- [ ] Q7: after 3 voorstellen, decide from the timing log whether the copy pass or the by-eye
      check is the expensive stage, and automate only that one.
- [x] Q8: factory tested end to end (scrape → yaml → build → gate → serve). Three defects found
      and fixed, all in code that had never been run: (a) `kk site new` could not work at all —
      `_SCHEMA` used `maxItems`/`minItems: 3`, which structured outputs reject with a 400, and
      the one stage that calls the API was the one stage the tests skipped; counts moved to the
      prompt + build_config (truncate at the ceiling, refuse under the floor); (b) a prospect
      without opening hours burned the Opus copy call before failing, and the error told the
      founder to fix it "after generating" when nothing had been written — now checked first
      (11.1s → 1.1s) with an honest message; (c) the fact gate counted city pages by directory
      name, so a `werkgebied/<plaats>/` that lost its index.html passed while every link to it
      404s — now counted from built HTML. 8-way sabotage battery otherwise clean; both fixtures
      build + gate in ~4s; all `kk site` refusals hold. 16 sitedraft tests (+4), 73 kk tests.
- [x] Q9 (6b40573, 503a253, 6f231e2): the photography. The site's only imagery was six equal
      squares in one flat row, and the hero had no photo at all — a contact sheet between two
      blocks of text. Twelve award-level trade/construction sites (Koto, Leidner, Adriaans,
      Zecc, Van Wijnen, Hobbs, Land Morphology) use no square content photos anywhere, so the
      fix was the crop, not the CSS: stock-photos.py now cuts per role (3:2 hero, 2:3 tall and
      3:2 wide tiles, 1200x630 share card) in WebP, the crop follows the subject, and the tile
      order is TALL WIDE WIDE TALL TALL WIDE so the three-column fill ends level while the
      seams stay ragged. The hero is split rather than text-over-photo (these frames are bright
      at the top; a scrim heavy enough for white copy would muddy the photo). Each vak gained a
      seventh photo to fill the gap in its own coverage — a Dutch aerial establishing shot for
      dakdekker, a cv-verdeler for loodgieter. Every stock photo carries its own Dutch alt from
      a generated `stock/<vak>/alt.json`, describing the frame and never who did the work; a
      missing description fails the build. NOT done: no captions — the strongest pattern found
      (service + city under each photo) would have a stock frame claim a job this client may
      never have done. squirrelscan 76/C → 78/C, Images and Accessibility 100.
  - [ ] FOUNDER: the two fixture vakken are done; every new vak still needs its own pass
        against the picking rule (face-free, Northern European) and a 3-tall/3-wide split.

### R. Website factory — a design vocabulary, driven by reference sites (started 2026-08-15)
Q9 fixed the photography, but the factory still built ONE site: same silhouette, same type
scale, same corners, same air, and two hex values as the only thing a client could change.
Two voorstellen sent in the same week were recognisably the same document. R makes the skin
a parameter, and lets the founder point at example websites he likes instead of describing
them. Decided up front (founder, 2026-08-15): the reference drives the SKIN ONLY — layout
and section order stay fixed, because free-form markup per client cannot be fact-gated,
cannot be checked for reflow, and grows the by-eye stage that Q7 wants to shrink. With no
reference given, the factory composes a look itself rather than falling back to a preset.
- [x] R1 (0d740f2): the vocabulary. Six axes (`schaal`, `vorm`, `ritme`, `palet`,
      `kleuring`, `foto`) in `src/lib/stijl.ts`, each a closed set of named values that
      resolve to CSS custom properties injected on `<html>` beside `--brand-primary`.
      Tailwind v4 compiles utilities to `var()` references rather than inlining them, so
      overriding a theme property re-skins every utility that reads it; components spend
      tokens instead of literal `py-9`/`rounded-*` steps. Closed rather than generated so
      every value is one that has been looked at once on a real build. Absent `stijl:` =
      the old look, proven by diffing a default build against the previous one — including
      the two photo radii (tiles 12px, hero 20px) that one `--foto-radius` silently
      unified. Two defects found by looking: the `randloos` bleed used `calc(50% - 50vw)`,
      and 50vw counts the scrollbar the layout width does not, so `overflow-x: clip` shaved
      a slice off the outer photographs (now a tokenised max-width, no viewport
      arithmetic); and `groot` at 4.25rem pushed the call button off a 1000px screen with a
      real Dutch company name in the H1 (capped at 3.5rem).
- [x] R2 (c915929): `letterontwerp` — systeem (unchanged), grotesk (Figtree), industrieel
      (Archivo + Figtree), redactioneel (Instrument Serif + Figtree). Self-hosted woff2 via
      `scripts/fonts.mjs`, never a CDN stylesheet: zero external requests is what lets these
      sites ship with no cookie banner, and that is about where the bytes come from, not
      whether there are any. All three families OFL 1.1, notice ships with them. Only the
      selected family lands in a client's dist/ (the stock-photo rule); `fonts/manifest.json`
      is the single source for both the CSS stacks and the copied files, because if those
      drift the failure is a live site silently falling back to Arial. Weight and tracking
      travel with the face, not the scale; h3 stays in the body face at every pairing.
- [ ] R3: `app.sitestyle` — the reference-site analyser. Fetch each `--voorbeeld` URL,
      extract MEASURABLE facts (font stacks, weights, sizes, colours, radii, section
      padding, image ratios) in code, then one schema-constrained Claude call maps those
      onto the vocabulary. The model picks among named values; it never emits CSS. Extract
      design parameters only — never a reference's copy, images or logo.
- [x] R3 (aee01f0): `app.sitestyle`, built as above. `--feiten` prints the measurements
      alone, so the extractor can be judged without paying for a call. The vocabulary is
      parsed out of `stijl.ts` instead of restated in Python: a value only sitestyle knew
      about would clear the API schema and then fail Zod at build time, on the founder's
      machine, after the voorstel was written. The no-copy rule is a property of the parser
      rather than an instruction — it is blind to text outside `<style>`, so no sentence of
      the reference is ever in memory to leak, and a test pins that. Three defects found by
      running it against real sites instead of fixtures: taking the largest length in a
      value reported sizes browsers never render (`clamp()` is now resolved at an assumed
      1440x900 viewport, which also taught it viewport units it could not read at all);
      selector-based heading detection found nothing on compiled stylesheets, where rules
      are named `.styles_heading__x7f2` rather than `h1`, so the type scale came back null
      on exactly the modern sites the founder admires (added a size histogram — highest
      count is the body text, top of the range is the display size); and Next.js
      `<Family> Fallback` faces plus emoji/mono stack members were read as chosen
      typefaces. Verified end to end: zecc.nl → industrieel/groot/scherp/neutraal,
      vanwijnen.nl → industrieel/groot/zacht/koel. NOTE: a fully client-rendered reference
      has no measurable CSS and is refused with a clear error rather than guessed at.
- [ ] R4: the no-reference path. Same call with no facts, told to compose from the vak and
      the client's own brand colours. Must avoid `groot` when `bedrijf.naam` is long (see
      R1) — encode that as a rule in the prompt, not as a hope.
- [x] R4 (4ca0edf): `--vak --naam --kleur --accent` with no `--voorbeeld` composes instead
      of refusing. Same call, measurements swapped for what a prospect always has; both
      paths now share one schema, one validator and one yaml writer. Two things went into
      the enum rather than the prompt, because a prompt line is advice and the run that
      ignores it ships a real voorstel. First, `groot` is withdrawn above 34 characters of
      `bedrijf.naam` — measured in the browser on a real build at 1440x800, where the H1
      (`<naam>: vakwerk waar u op kunt rekenen.` in a column that stops growing at ~480px)
      sets in four lines at 33 characters and five at 35. R1 capped `groot` at 3.5rem to
      keep the call button on screen; this is the other half of the same defect, the
      headline that is legal but unreadable. It applies to the reference path too: it is a
      fact about the client, not about the mode. Second, the composer gets a two-value
      shortlist per axis rotated by a blake2b seed over the name, not the whole vocabulary
      — sitedraft gives every prospect the same DEFAULT_PRIMARY until the founder overrides
      it, so six dakdekkers drafted in one week would arrive with identical inputs and leave
      with an identical skin, which is R's own defect one layer up. The cost is deliberate:
      a shortlist sometimes withholds the best value (`ritme: ruim` above all), and handed
      the full range the model keeps reaching for that same best answer, which is one site
      with a longer prompt. blake2b and not `hash()` (salted per process) so fixing a typo
      in the yaml does not redesign the page. `systeem` is never offered to the composer —
      it is what a page looks like when nobody chose a typeface; measuring a reference
      really set in Arial still maps to it, which is a reading rather than a decision.
      Verified on two real calls: "Dakwerken Bos" → industrieel/scherp/warm/royaal/randloos,
      "Installatietechniek Van der Veldenhuizen" (40 chars) → grotesk/zacht/ruim/koel, no
      `groot`; built the long one and both call buttons sit above the fold. 60 tests.
- [ ] R5: wire it in — `kk site new --voorbeeld <url>` (repeatable) through to sitedraft, so
      the stijl block is written with the rest of the yaml.
- [x] R5 (783cdc7): wired as above, and composing when there is no `--voorbeeld` rather than
      leaving the block out — a factory that composes only when asked gets asked on the first
      prospect and never again. The ordering carries two decisions. Both free gates moved
      ahead of the copy call (references measured, brand colours checked), following the
      openingstijden rule: a mistyped URL or a too-light `--kleur` costs a second, not an Opus
      request, and the colour would otherwise come back twice — once as a warning from the
      composer, which is handed it, and again as build_config's error. A skin that fails
      AFTER that call does not sink the run: the voorstel is written in the default look with
      the `app.sitestyle` command to fix it printed underneath, because a proposal in last
      month's look beats a paid call thrown away. The yaml is dumped one top-level key at a
      time so `stijl:` can carry each choice's reason as a comment above it (yaml.dump cannot,
      and the founder judges the analyser by those lines before he sends the site); output is
      byte-identical without a block, pinned by a test. Verified end to end on a real build:
      industrieel/groot/scherp/ruim/warm/royaal/randloos → Archivo+Figtree, 0px radii,
      full-bleed photos, only the two chosen families in dist/, `pnpm check` green over 8
      pages. One defect found by building rather than testing: a hand-made fixture put a
      kleuring value (`royaal`) on the ritme axis and rode the round trip all the way to a Zod
      refusal, so fixtures are now checked against the vocabulary too. 28 tests.
- [ ] R6: extend `CLIENT=<slug> pnpm check` for the skin: fonts resolve locally, the
      resolved palette still clears WCAG AA, no external hosts, no @font-face pointing at a
      family this build did not copy.
- [x] R6 (this commit): the gate now reads the skin off the built page — the inline custom
      properties on `<html>` — and resolves what the browser will actually paint, `var()`
      chains and `color-mix(in oklab, …)` included, rather than trusting the vocabulary's
      own promises. 14 contrast pairs (ink/mist/merkkleur over paper/card/band/fotoband,
      white and white-at-85% over the merkkleur) against the 4.5:1 AA floor; hairlines are
      out on purpose (1.4.11 exempts a divider). The OKLab matrices are Ottosson's, checked
      against his published vectors to 1.2e-5, because a WCAG gate computing the wrong
      colour is worse than no gate. Fonts: every `@font-face` must name a family the page's
      stacks name, load a root-relative file that is really in `dist/`, and no shipped
      woff2 may go unreferenced — plus the end-to-end one, `stijl.letterontwerp` against
      the family each stack LEADS with, per stack. That last one started as "does the page
      carry any webfont at all" and a negative test killed it: a `redactioneel` site that
      loses its serif still leads `--font-sans` with Figtree, so a count sees nothing wrong
      while the half a reader notices is gone. Stylesheets are also swept for off-host
      `url()`/`@import`, which section 5 never covered — it reads the HTML only.
      One build change fell out of writing it: `src/styles/fonts.css` declares all three
      families (a stylesheet cannot be imported conditionally), so every build shipped
      `@font-face` rules for files it had not copied — dead today, a 404 the day anything
      names them. `astro.config.mjs` now prunes the rules of families this client did not
      get, which is what makes "every rule resolves" assertable at all. Verified on all
      four pairings: systeem 0 rules/no fonts dir, grotesk 6/6, industrieel 10/10,
      redactioneel 8/8; CSS 19982 → 18766 bytes on the preview fixture. Nine negative tests
      (missing woff2, CDN src, dead rule, fallen-back stack, too-light merkkleur, page
      without a skin, off-host `url()`, orphan file, pages disagreeing) each fail the gate
      on their own before it was believed.
- [ ] R6b: the gate rejects skins the factory can compose. Swept the whole vocabulary
      against the 3262 merkkleuren the Zod schema accepts: 3.6% of palet × kleuring ×
      kleur_primair combinations fall under AA somewhere. Two root causes, both older than
      R. First, `contrastWithWhite >= 4.5` guards a colour that is then used as TEXT on
      paper/card/band — all darker than white — so the schema's own floor is systematically
      too low for 11 of its usages (worst case 3.42:1). Second, `text-white/85` in
      FinalCta.astro: 17% of accepted merkkleuren fail that line, and no alpha short of 1.0
      is safe for a colour sitting exactly at the schema's 4.5 (#ed0c0c → 3.50). Not fixed
      here because both fixes are the founder's call, not a check's: either raise the floor
      in the schema AND the sitedraft pre-flight together (R5 put the colour gate ahead of
      the Opus call on purpose — letting the two disagree is how a voorstel costs a paid
      call twice), or drop the /85 and carry the hierarchy on size. Nothing ships broken
      meanwhile: `pnpm check` runs before a voorstel goes out, so a bad combination stops
      the send instead of reaching a prospect.
- [ ] R7: tests (the vocabulary resolver — sitestyle's own 41 landed with R3) and a docs
      pass — the voorstel-playbook and intake checklist both describe the look as fixed.
- NOTE (pre-existing, not from R): `.prettierrc.json` lists `prettier-plugin-astro` but the
  plugin is not installed, so `pnpm format:check` fails repo-wide before any of this.

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
