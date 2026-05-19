# Klantkraan — TODO

> Living checklist. Tick boxes as we go. Ralph Higgums loop: small step → test → next.

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
- [x] `onboarding-30-day.md`
- [x] `intake-form.md`
- [x] `synthflow-system-prompt.md`
- [x] `sms-templates.md`
- [x] `dashboard-spec.md`
- [x] `churn-prevention.md`

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

### 10-ops
- [ ] `weekly-kpi-review.md`
- [ ] `risk-register.md`
- [ ] `founder-tooling.md`

## Phase 0.5 — Founder real-world actions (BLOCKING)

See `docs/00-MASTER-PLAN.md § 5`.

- [x] Verify `klantkraan.nl` available — https://www.sidn.nl/en/whois (verified 2026-05-20)
- [x] Verify `klantkraan.com` available — https://lookup.icann.org/en/lookup (verified 2026-05-20)
- [x] KvK handelsnaam search "Klantkraan" — https://www.kvk.nl/zoeken/ (no conflict, 2026-05-20)
- [x] BOIP trademark search class 35 + 42 — https://www.boip.int/en/trademarks-register (no conflict, 2026-05-20)
- [ ] Register `klantkraan.nl` + `klantkraan.com` (TransIP / Namecheap)
- [ ] File `handelsnaamwijziging` "Klantkraan" under T4 at KvK
- [ ] Hiscox PI quote ICT — https://www.hiscox.nl/beroepsaansprakelijkheidsverzekering-ICT
- [ ] Synthflow trial: test 30 min Dutch voice quality
- [ ] CM.com signup + reserve 1 Dutch landline
- [ ] Moneybird trial open + 21% / reverse-charge / ICP configured
- [ ] Confirm €5–6k personal cash bridge available
- [ ] LinkedIn profile audit (real-name, faceless avatar OK)

## Phase 1 — Scaffolding (after Phase 0 complete)

### Tooling baseline
- [ ] Enable `context7` MCP server (required by CLAUDE.md)
- [ ] Repo monorepo: pnpm + Turborepo skeleton

### Marketing site (Astro on Cloudflare Pages)
- [ ] `apps/marketing-site` scaffold
- [ ] Home + `/loodgieters` + `/dakdekkers`
- [ ] `/prijzen`, `/rekentool` (ROI calc), `/demo`, `/over`
- [ ] `/legal/{voorwaarden,dpa,sla,privacy,ai-disclosure,subprocessors}`
- [ ] Lead form → Cloudflare Worker → Attio API

### Automation infra
- [ ] Hetzner CX22 + Caddy + docker-compose
- [ ] n8n self-hosted, Postgres on Neon
- [ ] Healthchecks.io + Sentry + Uptime Kuma

### Per-client product
- [ ] Synthflow Dutch agent template (`docs/03-delivery/synthflow-system-prompt.md`)
- [ ] Missed-call-back n8n workflow (CM.com webhook → SMS)
- [ ] Review automation n8n workflow
- [ ] Cal.com event-types template
- [ ] Client dashboard page `/r/[slug]`

### Tooling integrations
- [ ] Attio workspace + pipeline + automation hooks
- [ ] PandaDoc / SignWell templates
- [ ] Mollie + Moneybird invoicing
- [ ] Tally intake form

### Demo assets
- [ ] Public AI demo number (+31 ...) live
- [ ] ROI calculator live
- [ ] Founder bio page with KVK + DPA download

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
