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
- [ ] Point `/demo` at the live text demo (web chat) instead of the TODO phone number — text demo works today, no CM.com dependency

### E. First pilot (the gate everything else waits behind)
- [x] Finish ONE prospect config fully — **Loodgietersbedrijf Meijer B.V.** (`config/clients/meijer.yaml`): real services/hours/FAQ from their site, persona "Sanne", art. 50 disclosure, guardrails; `selftest config` passes
- [x] Deploy the demo publicly at a stable URL — Hetzner ops redeployed 2026-07-14: `widget.js` now live (was 404), showcase at https://demo-168-119-173-25.sslip.io/ and Meijer's own bot at https://demo-168-119-173-25.sslip.io/?client=meijer (verified end-to-end: offers a real slot, collects details, books)
- [ ] Walk one warm prospect through it; offer pilot terms (free/€99 for 30 days in exchange for case-study data) — FOUNDER: Meijer demo is ready to show

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
