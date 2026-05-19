# Risk Register

> Single source of truth for every known risk that could materially harm Klantkraan: compliance, commercial, product, operational, financial, security, brand. Reviewed quarterly (Q-end Friday) plus on any incident or contract change. Owner until M6: founder. From M6: founder + VA share register hygiene; founder retains sign-off. Cross-referenced by `00-MASTER-PLAN.md § 6`, `04-legal/*`, `06-outbound/gdpr-compliance.md`, `08-tech/observability.md`, and every incident postmortem.

## How to read this register

- **Likelihood (L)**: L = <10% in any rolling 12 months, M = 10–40%, H = >40%.
- **Impact (I)**: L = <€2k or <1 week recovery, M = €2–20k or 1–4 weeks, H = >€20k, regulatory, or existential.
- **Score**: L×I bucketed. LL/LM = Low, ML/MM = Mid, MH/HM = High, HH = Critical.
- **Owner**: founder until M6 VA hire (see `07-finance/mrr-projections.md` trigger thresholds). After M6: name in cell.
- **Review cadence**: quarterly default. High/Critical re-scored monthly. On-trigger review fires on any incident touching the row.
- **Status**: open / mitigated / accepted / closed. "Accepted" entries also live in § 4 with rationale.

## ID conventions

IDs are stable across the register lifetime. They are referenced from MSA, DPA, onboarding checklists, observability dashboards, and incident postmortems.

| Prefix | Category | Numbering |
|---|---|---|
| R-COMP | Compliance & legal | R-COMP-01 onwards |
| R-COM | Commercial / go-to-market | R-COM-01 onwards |
| R-DEL | Product / delivery | R-DEL-01 onwards |
| R-OPS | Operational | R-OPS-01 onwards |
| R-FIN | Financial | R-FIN-01 onwards |
| R-SEC | Information security | R-SEC-01 onwards |
| R-BRA | Reputational / brand | R-BRA-01 onwards |

A retired risk keeps its ID. The status column flips to `closed` and a closure note is added in the mitigation cell. New risks never reuse a retired ID.

## Heatmap snapshot (current quarter)

Top of mind. Re-rendered each quarterly review.

| Score | Count | Examples |
|---|---|---|
| Critical (HH) | 0 | — |
| High | 11 | R-COMP-01, R-COMP-02, R-COM-01, R-COM-05, R-DEL-01, R-DEL-03, R-OPS-01, R-OPS-03, R-FIN-01, R-SEC-04, R-SEC-06 |
| Mid | 41 | majority of register |
| Low | 2 | R-COM-09, R-BRA-04 |

Trend rule: any row that climbs a band between quarters is auto-flagged for a postmortem-style root-cause note even if no incident has fired yet.

## First 90 days — concentrated focus

The master plan (`00-MASTER-PLAN.md § 4`) makes M1–M3 the highest-leverage period. The register risks that matter most during this window:

| Phase | Top risks to watch | Why now |
|---|---|---|
| M1 — Foundation | R-COMP-01, R-COMP-04, R-DEL-01, R-FIN-01, R-BRA-03 | Compliance baselines must be in place before invoice #1; Synthflow voice quality decides product viability; cash bridge buffers the slowest revenue month |
| M2 — Proof + outbound on | R-COM-01, R-COMP-02, R-COM-05, R-DEL-03 | Cold-email starts at scale; pilot reputational risk peaks; emergency-call logic gets first real-world load |
| M3 — Compound | R-OPS-01, R-COM-06, R-DEL-07, R-FIN-04 | Founder throughput strain begins; paid-ads test runs; onboarding pace must stay under control |

The weekly KPI review (`10-ops/weekly-kpi-review.md`) is the operational forum where these phase-specific risks are watched.

## Cross-doc references

| Risk family | Linked doc | What it provides |
|---|---|---|
| R-COMP | `04-legal/ai-act-disclosure.md`, `04-legal/compliance-checklists.md`, `04-legal/insurance.md`, `06-outbound/gdpr-compliance.md` | Regulatory baseline, audit cadence, MSA clauses |
| R-COM | `01-strategy/offer-and-pricing.md`, `02-sales/funnel-benchmarks.md`, `05-content/30-day-calendar.md`, `06-outbound/deliverability-stack.md` | Channel mix, deliverability stack, funnel KPIs |
| R-DEL | `03-delivery/onboarding-playbook.md`, `08-tech/stack-decisions.md`, `08-tech/observability.md` | Provider swaps, alerting, SLA backstops |
| R-OPS | `08-tech/infra-setup.md`, `08-tech/observability.md`, Notion runbooks | Restore procedures, on-call signals |
| R-FIN | `07-finance/unit-economics.md`, `07-finance/mrr-projections.md` | Bear-case modelling, trigger thresholds |
| R-SEC | `08-tech/infra-setup.md`, `08-tech/observability.md`, `04-legal/insurance.md` | Hardening, alerting, cyber cover |
| R-BRA | `09-brand/visual-identity-brief.md`, `05-content/*`, founder LinkedIn audit | Voice, response templates, content counter-channel |

---

## 1. Compliance & legal (R-COMP)

Regulatory exposure is the single highest-impact category. NL is a strict-enforcement jurisdiction (AP + ACM both active), and the AI Act adds a second regulator on top of AVG.
Sole-founder structure means a single AP-melding can swallow a quarter of bandwidth, so every row here has a documented mitigation and a recurring audit hook.

| ID | Risk | L | I | Score | Mitigation | Early warning | Owner | Review |
|---|---|---|---|---|---|---|---|---|
| R-COMP-01 | EU AI Act Art. 50 disclosure missing or weakened on a live call | L | H | High | Disclosure baked into Synthflow first-turn prompt per `04-legal/ai-act-disclosure.md`; SHA-256 prompt hash logged per call; non-waivable MSA clause; monthly 10-call audit per `04-legal/compliance-checklists.md` periodic routines | Audit finds a call without disclosure in first 8 sec; client requests "disable AI line"; Synthflow voice or model version changes without prompt re-verification | Founder | Monthly |
| R-COMP-02 | AP enforcement on cold outbound to eenmanszaak/VOF | M | H | High | Hard BV-only filter on KvK API `rechtsvorm` field; LIA per campaign in Notion; suppression list checked pre-send; sender-ID + one-click opt-out per Tw 11.7; see `06-outbound/gdpr-compliance.md` | AP klacht received; ACM letter; bounce of a misclassified eenmanszaak; spike in "STOP" replies | Founder | Quarterly |
| R-COMP-03 | AVG sub-processor breach (Synthflow / CM.com / Hetzner / Anthropic) | L | H | Mid | DPA signed per sub-processor (`04-legal/compliance-checklists.md` item 4); SCCs in Annex III; sub-processor change notice 30 days; breach playbook drafted (48h client notify, 72h AP-melding) | Sub-processor breach notification email; sub-processor status page incident; sub-processor SCC version bump | Founder | Quarterly |
| R-COMP-04 | DPA missing on a paid client at sign | L | M | Mid | DPA template auto-attached to SignWell envelope; SignWell template enforces required signature blocks; check on invoice #1 of each client; Attio field `dpa_signed_at` blocks go-live without value | Client signs MSA but DPA shows "missing" in compliance audit; SignWell envelope status mismatch | Founder | Quarterly + on signup |
| R-COMP-05 | DPIA missing for a Pro/Max client | M | M | Mid | DPIA per service tier (`04-legal/compliance-checklists.md` item 6); auto-generated at onboarding from template; stored in Notion + client folder; onboarding-checklist item 7 blocks go-live | Onboarding checklist item 7 unchecked at go-live; Pro/Max client with no DPIA file in client folder | Founder | Per onboarding |
| R-COMP-06 | Voice-call recording without valid consent | L | H | Mid | First-turn disclosure includes recording; consent confirmed by call-continuation; opt-out path ("zeg medewerker") routes to human and stops recording; retention auto-deleted after contract + 6 months | Caller complaint; AP klacht; recording flagged in monthly audit; opt-out path failure in Sentry | Founder | Monthly |
| R-COMP-07 | Art. 30 RoPA out of date when AP asks | L | H | Mid | RoPA in Notion + Postgres `ropa_entries`; reviewed quarterly; auto-update reminder on sub-processor change; move to Vanta / ICTRecht tool at >20 sub-processors | Sub-processor added without RoPA edit; RoPA last-modified > 90 days; quarterly review checkbox skipped | Founder | Quarterly |
| R-COMP-08 | Reverse-charge BTW applied wrong on EU invoice | M | M | Mid | Moneybird native EU reverse-charge module; VIES validation on every EU invoice; quarterly ICP-opgave; accountant retainer from 10th client onwards | Moneybird flags missing BTW-id; Belastingdienst correction letter; ICP-opgave mismatch | Founder | Quarterly |
| R-COMP-09 | UBO / KvK handelsnaam filing lapses (post-BV conversion) | L | M | Mid | UBO registered at notary appointment per `04-legal/compliance-checklists.md` § DO BEFORE 10TH; annual KvK statement reminder in Cal.com | UBO reminder email; KvK warning letter | Founder | Annually |
| R-COMP-10 | Reclamecode violation on landing page or testimonial | L | M | Mid | No fake/AI-generated testimonials (see `04-legal/ai-act-disclosure.md` deepfake policy); claims grounded in client data; ROI calculator labelled "indicatief"; review by founder before publish | SRC complaint; competitor flagging on social | Founder | Quarterly |

## 2. Commercial / go-to-market (R-COM)

This category is where the bear case actually originates. Distribution and pricing — not product — are the constraint.
Every commercial risk has a documented fallback channel so no single failure stalls the funnel.

| ID | Risk | L | I | Score | Mitigation | Early warning | Owner | Review |
|---|---|---|---|---|---|---|---|---|
| R-COM-01 | Cold-email deliverability collapse (Google/MS tenant suspension) | M | H | High | 9-inbox rotation across 3 secondary `.nl` domains, 25/day cap, 3-week warmup, DMARC `p=reject` after week 4, brand domain never used for cold (see `06-outbound/deliverability-stack.md` § 9-inbox rotation); MS 365 fallback inboxes pre-provisioned; domains treated as consumables | Smartlead inbox-placement <80%; Postmaster reputation drops to "low"; single suspension email; bounce-rate >3% on any inbox | Founder | Monthly |
| R-COM-02 | Pricing too high vs NL voice-only tools (€149 Voicelabs / Agentfabriek) | M | M | Mid | Tier anchor at €999 Max; bundle (SMS + voice + reviews) outpriced individually vs equivalent stack; killer Dutch demo destroys feature-for-feature comparison; ROI calculator on site quantifies recovered missed-call value | Win-rate <20% on discovery calls; "te duur" objection in >40% of lost deals; competitor lands a named client we lost | Founder | Quarterly |
| R-COM-03 | Founder content engine stalls before flywheel ignites (M2-M3) | M | M | Mid | 5 LI + 1 blog + 1 newsletter/wk hard cadence; Buffer scheduled 2 weeks ahead; cornerstones pre-drafted in batches; Anthropic Claude drafts to cut time; backup batch of 10 evergreen posts on file | LinkedIn impressions trend flat for 3 consecutive weeks; newsletter open rate drops <30%; founder logs <3 publishing hours/wk | Founder | Monthly |
| R-COM-04 | Werkspot / Werkbon / Bouwhulp push competitive pricing down | L | M | Mid | We sell receptionist + recovery, they sell lead-gen — different category; ICP messaging hammers difference; never compete on per-lead price; partnership lane available if marketplaces ever pivot | Prospect cites Werkspot price in discovery; loss-reason field tagged "marketplace alt"; marketplace launches own receptionist | Founder | Quarterly |
| R-COM-05 | Bad-fit pilot publishes a negative public review | L | H | High | ICP filter on pilot selection (BV, 2-8 staff, owner-operator); 30-day mutual-out clause in pilot agreement; weekly check-ins in pilot phase; satisfaction signal before any review request; legal review of public statements via Hiscox PI | Pilot ignores 2 consecutive check-ins; NPS <6 in week 2 survey; pilot reduces forwarded calls below baseline | Founder | Per pilot |
| R-COM-06 | Google Ads payback worse than projected (CPC inflation, low CVR) | M | M | Mid | Cap test at €400/mo until 2 conversions verified; pause if CAC > €450 after 30 days; switch budget to LinkedIn/content if test fails; long-tail "AI telefoniste loodgieter [stad]" keywords only | CPC > €5 for 14 days; CVR <3% over 100 clicks; Quality Score <5 on core ads | Founder | Monthly during test |
| R-COM-07 | Trademark / brand opposition delays content compounding | L | M | Mid | BOIP search class 35+42 before launch (pre-launch item 4); fallback names (Vakflow, Afspraakmotor) pre-vetted; BOIP watch service from M3 | BOIP opposition letter; conflicting NL handelsnaam appears in KvK; cease-and-desist | Founder | Quarterly |
| R-COM-08 | LinkedIn outbound platform restriction (HeyReach account ban) | M | M | Mid | HeyReach within platform limits (<100 invites/wk per seat); native LinkedIn behavior simulation; no auto-DMs to non-connections; secondary seat ready as standby | LinkedIn warning email; seat restriction; connection-acceptance <25% | Founder | Monthly |
| R-COM-09 | Sales Navigator pricing change or feature lock-down | L | L | Low | Annual contract locks pricing; no operational dependency on a single SN feature (we use core search + saved leads); Apollo/Surfe as cold-data backups | SN price-hike email; feature deprecation notice | Founder | Annually |

## 3. Product / delivery (R-DEL)

These risks tie directly to the AI receptionist promise. A single bad emergency-call episode (spoed loodgieter) is the worst-case story for the press and for trust.
Every product risk has a fallback documented in the `packages/telephony` adapter or in an n8n alt-path workflow.

| ID | Risk | L | I | Score | Mitigation | Early warning | Owner | Review |
|---|---|---|---|---|---|---|---|---|
| R-DEL-01 | Synthflow Dutch voice quality insufficient | M | H | High | Verified in trial pre-pricing (pre-launch item 8); adapter pattern in `packages/telephony` allows swap to VAPI + ElevenLabs v3 Dutch; trigger documented in `08-tech/stack-decisions.md` re-evaluation table; CSAT survey post-call samples voice quality | Client reports robotic voice >2 calls/wk; CSAT survey <7/10 on voice quality; Synthflow voice ID changes silently | Founder | Monthly |
| R-DEL-02 | CM.com Dutch landline reservation blocked or revoked | L | H | Mid | Twilio Voice NL fallback documented in adapter; second number reserved for staging; KYC docs filed and refreshed annually; number-portability rights asserted in CM.com contract | CM.com KYC re-verification email; number-port rejection; CM.com regulatory letter | Founder | Quarterly |
| R-DEL-03 | AI escalation logic fails on a loodgieter spoed call | M | H | High | Hard rule in system prompt: any keyword in {spoed, lekkage, gasreuk, geen water, brand} forces immediate SMS + WhatsApp to owner within 30 sec; recording flag set; tested in onboarding red-team script; Healthchecks.io heartbeat on escalation webhook (`08-tech/observability.md`) | Healthchecks miss on escalation webhook; client SMS not received on a flagged call; spoed call duration >2 min without escalation | Founder | Monthly |
| R-DEL-04 | Review-automation crosses Google anti-incentive policy | L | H | Mid | Never offer reward for review; SMS text reviewed against Google policy; no review-gating (must offer 1- and 5-star paths equally); rate-limit ≤3 review requests per client per week | Google business profile flagged "suspicious activity"; review removed by Google; sudden positive-review velocity drop | Founder | Quarterly |
| R-DEL-05 | Synthflow >€0.18/min Dutch pricing change kills Pro margin | L | M | Mid | Adapter swap to VAPI + ElevenLabs direct; bear-case re-prices Pro at €699; documented trigger in `08-tech/stack-decisions.md`; per-call COGS logged to Postgres `cogs_daily` for alerting | Synthflow pricing email; per-min cost in Postgres `cogs_daily` > €0.15 rolling 7-day avg | Founder | Quarterly |
| R-DEL-06 | n8n workflow corruption / silent data loss between Attio and Postgres | L | H | Mid | Borgbase daily encrypted backups; n8n exports versioned to git per `08-tech/repo-architecture.md`; Healthchecks.io heartbeat per critical flow; idempotency keys on all writes; weekly diff of Attio vs Postgres counts | Healthcheck miss on critical flow; Attio webhook 500 spike in Sentry; row-count drift Attio↔Postgres >0.5% | Founder | Monthly |
| R-DEL-07 | Onboarding overruns the 2h 10m budget at scale | M | M | Mid | Productized onboarding checklist; pre-recorded Loom walkthroughs; client-side form intake via Tally; VA hire trigger at 12 active clients per master plan; SOPs in Notion | 3 consecutive onboardings >3h; founder weekly time-tracker drift; onboarding-NPS <8 | Founder | Monthly |
| R-DEL-08 | AI receptionist mis-routes after-hours emergency to voicemail | L | H | Mid | Per-client opening hours block in n8n; out-of-hours flow routes to owner WhatsApp + retry SMS; tested per-client at go-live; client confirms via signed-off "go-live test" | Out-of-hours escalation Healthcheck miss; client reports missed after-hours emergency | Founder | Per onboarding + quarterly |
| R-DEL-09 | Synthflow ASR mis-hears Dutch dialect (Limburgs, Fries, Brabants) | M | M | Mid | Dialect samples reviewed in trial; system prompt includes "vraag om herhaling bij twijfel"; transcript-confidence threshold logs low-confidence calls for review; ElevenLabs/VAPI fallback if persistent | Transcript-confidence <0.7 in >5% of calls; client complaints "begreep me niet" | Founder | Quarterly |

## 4. Operational (R-OPS)

Sole-founder reality. M1-M5 is the most fragile period: no redundancy, no backup human.
Every operational row either has a runbook in Notion or is explicitly accepted in § 4.

| ID | Risk | L | I | Score | Mitigation | Early warning | Owner | Review |
|---|---|---|---|---|---|---|---|---|
| R-OPS-01 | Founder delivery wall at ~30 active clients | H | M | High | Productized onboarding <2h; VA hire trigger pulled forward to M6 (was M8) per `07-finance/mrr-projections.md`; SOPs in Notion before VA arrives; client-facing async-first comms reduce sync time | Weekly founder hours >55 for 3 consecutive weeks; client response SLA breach; onboarding-queue depth >3 | Founder | Monthly |
| R-OPS-02 | Critical sub-processor outage >4h (Synthflow, CM.com, Hetzner) | L | M | Mid | 99% SLA promised (not 99.9%); telephony adapter allows provider swap; status page proxies sub-processor incidents (`08-tech/observability.md`); pre-drafted client comms template | Sub-processor status page open incident; Uptime Kuma red >15 min; Healthchecks miss on sub-processor probe | Founder | Per incident |
| R-OPS-03 | Founder bus factor: illness, family emergency, accident | M | H | High | Documented runbooks per critical flow in Notion; 1Password emergency vault shared with spouse; AOV insurance evaluated (`04-legal/insurance.md`); pause-mode template for client comms drafted; weekly KPI review doc up-to-date so any successor can orient | n/a (event-driven) | Founder | Quarterly |
| R-OPS-04 | First VA hire fails background check or quits in week 2 | M | M | Mid | Two-candidate parallel trial week (paid, scoped); reference check before contract; 30-day notice in VA contract; SOPs reduce cold-start cost of replacement; recruitment shortlist kept warm for 60 days post-hire | Trial-week deliverables missed; references decline second call; VA logs <20h/wk in trial | Founder | At hire |
| R-OPS-05 | Mollie payments rail freezes account | L | H | Mid | Stripe + iDEAL secondary processor account pre-registered (dormant); Moneybird supports both; SEPA direct-debit mandates portable; KYC docs refreshed annually with Mollie | Mollie KYC re-verification request; chargeback rate >0.5%; payout delay >2 business days | Founder | Quarterly |
| R-OPS-06 | Single-VPS n8n outage with no hot failover | M | M | Mid | Daily Borgbase backups; documented 30-min restore runbook; Hetzner FI hot standby is the documented upgrade at M9+ per `08-tech/stack-decisions.md`; image tags pinned; restore tested twice a year | Hetzner status incident in Falkenstein; Uptime Kuma VPS check red; CPU pegged >90% for >10 min | Founder | Quarterly |
| R-OPS-07 | Client onboarding queue >5 deep blocks new sign-ups | M | M | Mid | Onboarding-week calendar capped at 3 slots/wk in Cal.com; auto-defer with personal email if full; VA absorbs in M6+; reschedule policy in MSA | Cal.com week shows zero open slots 2 weeks out; sales-pipeline → onboarded conversion drops | Founder | Monthly |
| R-OPS-08 | Founder timezone constraint blocks critical sub-processor incident response | L | M | Mid | Healthchecks + Sentry route alerts to mobile; SMS escalation after 15 min; spouse aware of critical-alert routing; Hetzner support is 24/7 EU | After-hours Healthcheck miss not ack'd within 30 min | Founder | Quarterly |
| R-OPS-09 | Knowledge concentration in founder's head (no documented SOP for X) | M | M | Mid | Quarterly SOP audit (list every recurring task, flag undocumented); Notion knowledge base; VA shadow week before any owner change | New incident missing a runbook; VA blocked on "ask founder" >3x in week | Founder | Quarterly |

## 5. Financial (R-FIN)

Bear-case modelling per `07-finance/mrr-projections.md` assumes some of these fire. The header risk is personal-cash bridge, since founder draws nothing M1-M4.
Cash dashboards refresh weekly so any drift fires before it becomes existential.

| ID | Risk | L | I | Score | Mitigation | Early warning | Owner | Review |
|---|---|---|---|---|---|---|---|---|
| R-FIN-01 | Personal cash bridge (€5-6k) insufficient | M | H | High | Bear-case dip is -€3.8k per `07-finance/mrr-projections.md`; €5-6k injection includes €1.5k buffer; founder draw deferred until €4.7k MRR; ad-budget gated on M3 cash position | Cumulative cash <€2k at M2 end; founder personal account dips below buffer; ad-spend trigger missed | Founder | Monthly |
| R-FIN-02 | FX shifts vs USD subscriptions (Anthropic, Synthflow, Sentry, Smartlead) | M | L | Mid | USD spend ~€80/mo at M1, ~€250/mo at M6; <5% of revenue; EUR pricing power on revenue side absorbs 20% FX swing; annual EUR-pricing options on Anthropic/Sentry checked yearly | EUR/USD <0.85 sustained; sub-processor invoices climb >15% MoM | Founder | Quarterly |
| R-FIN-03 | BTW reverse-charge applied wrong → Belastingdienst claw-back | L | M | Mid | Moneybird native handling; VIES validation per invoice; accountant engaged before 10th client (`04-legal/compliance-checklists.md` § DO BEFORE 10TH); ICP-opgave quarterly | Belastingdienst correction letter; ICP-opgave mismatch; Moneybird VIES warning | Founder | Quarterly |
| R-FIN-04 | CAC inflation kills payback at scale | M | M | Mid | Payback <1 month at €200 CAC; pause Google Ads at CAC >€450; channel mix diversified (5 channels per `07-finance/unit-economics.md`); content + partnership channels are CAC floors | Blended CAC >€350 over rolling 60 days; channel-mix concentration >50% on one channel | Founder | Monthly |
| R-FIN-05 | One large client (>20% MRR) churns | M | M | Mid | Max tier capped at 15% of mix; concentration metric tracked in KPI dashboard; quarterly QBR with top-3 accounts; multi-stakeholder relationship on Max accounts | Single client >18% of MRR for 2 consecutive months; QBR cancelled by client; usage drop >30% MoM | Founder | Monthly |
| R-FIN-06 | Annual prepay refund obligation hits at scale | L | M | Mid | Refund-on-cancel = pro rata, documented in MSA; deferred-revenue tracking in Moneybird from invoice #1; prepay funds segregated mentally (not spent ahead) | Prepay-cancel request; deferred-rev balance > 2 months of operating burn | Founder | Quarterly |
| R-FIN-07 | Failed SEPA direct-debit chain drives involuntary churn | M | M | Mid | Mollie dunning configured: retry +3d, +7d, +14d; email + SMS reminder; manual call from founder before suspend; Moneybird flag on bounce | Bounce-rate >2% of debits; dunning queue depth >5 | Founder | Monthly |
| R-FIN-08 | Belastingdienst loon-DGA / Vpb adjustment after BV conversion | L | M | Mid | Accountant retained pre-conversion (`04-legal/compliance-checklists.md` § DO BEFORE 10TH item 3); DGA-loon €58k baseline; managementovereenkomst at arm's length | Belastingdienst correction; accountant flag during annual closing | Founder | Annually |

## 6. Information security (R-SEC)

Cyber cover (`04-legal/insurance.md`) absorbs the worst-case financial impact but does not absorb reputational damage. Containment beats remediation.
Every infosec row is paired with a Healthchecks/Sentry signal so detection is automatic, not heroic.

| ID | Risk | L | I | Score | Mitigation | Early warning | Owner | Review |
|---|---|---|---|---|---|---|---|---|
| R-SEC-01 | Hetzner VPS compromised (root, lateral, supply-chain) | L | H | Mid | UFW default-deny; Caddy reverse-proxy only; SSH key-only + Tailscale admin plane; Wazuh/Sentry for anomaly alerts; daily Borgbase off-site backup; image-pull tags pinned in Docker Compose | Wazuh alert; SSH auth-fail spike; Sentry anomaly on n8n; unexpected outbound from VPS | Founder | Quarterly |
| R-SEC-02 | Credentials leak via founder laptop loss / theft | L | H | Mid | FileVault on; 1Password vault with biometric; Bitwarden Business; remote-wipe enrolled (Apple Find My + MDM); no plaintext .env on disk (loaded via 1Password CLI); critical accounts behind YubiKey | Laptop lost/stolen report; 1Password "unusual sign-in" alert | Founder | Quarterly |
| R-SEC-03 | Synthflow webhook secret leaked | L | M | Mid | HMAC signing on all webhook traffic; secret rotated quarterly; n8n endpoint behind Cloudflare WAF; secret never in git (pre-commit gitleaks scan); replay protection via nonce | Anomalous webhook source IP in Sentry; failed-signature spike in `08-tech/observability.md` dashboards | Founder | Quarterly |
| R-SEC-04 | n8n unauthenticated public endpoint exposed | L | H | High | All inbound through Caddy with basic-auth or HMAC; n8n editor on Tailscale only; pre-deploy lint checks for exposed webhooks; quarterly nmap from external; auth header required on every workflow trigger | Open-port scan finds n8n editor exposed; unexpected 200 on `/rest/*`; new workflow webhook without `requireAuth` flag | Founder | Quarterly |
| R-SEC-05 | Client phone-call transcripts exposed via misconfigured Postgres backup | L | H | Mid | Neon EU + role-based access; Borgbase backups encrypted client-side (key in 1Password); R2 bucket private + signed URL only; quarterly access audit; backup restore tested twice a year | R2 access log shows unexpected GET; Neon role table modified outside change window; backup-restore test failure | Founder | Quarterly |
| R-SEC-06 | Phishing of founder credentials (Google Workspace / Mollie / Hetzner) | M | H | High | Hardware key (YubiKey) on all critical accounts; Google Advanced Protection enrolled; Mollie + Hetzner 2FA on; quarterly phishing-awareness self-test; password-manager auto-fill blocks lookalike domains | Google security alert; failed 2FA attempts on Mollie; suspicious-login email | Founder | Quarterly |
| R-SEC-07 | n8n / Postgres dependency CVE exploited before patch | M | M | Mid | Renovate bot opens PRs on CVE; n8n pinned to LTS image; Postgres on Neon managed (auto-patched); Wazuh signature feed; quarterly dependency review | Renovate PR sits >7 days; Neon maintenance announcement; CVE in Sentry monitor | Founder | Monthly |
| R-SEC-08 | Misconfigured Cloudflare Worker leaks Attio API key | L | H | Mid | Worker secrets via Cloudflare bindings only; never in code; pre-deploy `wrangler` lint; quarterly key rotation; Attio API key scoped to read/write minimum | Attio audit log shows unexpected key use; Cloudflare deploy with secret in git diff | Founder | Quarterly |

## 7. Reputational / brand (R-BRA)

A faceless brand selling AI to skeptical trades has a thin reputational margin. A single viral negative anecdote can compress months of content work.
Every brand row is paired with either a content counter-channel or a legal counter-response so the brand never goes silent under pressure.

| ID | Risk | L | I | Score | Mitigation | Early warning | Owner | Review |
|---|---|---|---|---|---|---|---|---|
| R-BRA-01 | AI hallucinates a price on a call → invoiced dispute | M | M | Mid | System prompt forbids quoting prices; hard rule "altijd doorzetten naar {{owner_naam}} voor prijs"; tested in onboarding red-team script; recording + transcript evidence retained per Art. 50(5); MSA limit-of-liability clause | Client invoice-dispute ticket; caller complaint citing "AI zei €X"; transcript audit finds a price token | Founder | Monthly |
| R-BRA-02 | Faceless brand framed as "just an AI agency" by competitor | M | M | Mid | Founder personal LinkedIn rebrand pre-launch (pre-launch open question § 7.3); face-on-camera content from M1; case studies with named clients; founder-led webinar series M3+ | Competitor LinkedIn post tagging Klantkraan; review mentioning "wie zit erachter"; sales objection "is dit een eenmansbedrijf?" | Founder | Quarterly |
| R-BRA-03 | Klantkraan trademark opposition filed late by a third party | L | M | Mid | BOIP search class 35+42 pre-launch (pre-launch item 4); register handelsnaam within first week; defensive `.com` registration; fallback names vetted; BOIP watch service from M3 | BOIP watch service alert; opposition letter; conflicting EUIPO filing | Founder | Quarterly |
| R-BRA-04 | Founder's personal LinkedIn audit reveals off-brand prior content | L | L | Low | Audit + purge of off-brand posts pre-launch; pin Klantkraan pivot post; archive historic posts >2 years; LinkedIn "About" copy aligned with Klantkraan positioning | Prospect references old LI post in discovery | Founder | One-off (pre-launch) |
| R-BRA-05 | Dutch trade press writes a critical piece on AI receptionists | L | M | Mid | EU residency + Art. 50 + Dutch-native + AVG-clean positioning is the press counter-narrative; pre-drafted press response in Notion; opt-in interview offers to Cobouw / Installatie.nl / Stedendriehoek trade press | Journalist outreach; trade-association statement on AI receptionists; tweet/LI thread by sector influencer | Founder | Quarterly |
| R-BRA-06 | Negative Google review on Klantkraan business profile | M | M | Mid | Active monitoring; reply within 24h; escalate factually-wrong reviews via Google flagging; positive-review velocity counterbalance; founder personal review-response policy in Notion | Google alert; new ≤3-star review; review-velocity drop >50% MoM | Founder | Weekly |
| R-BRA-07 | Personal social-media misstep (founder LinkedIn / X post) damages brand | L | M | Mid | Documented personal posting guidelines; 30-second-rule on hot-takes about competitors / clients / regulators; no political content on Klantkraan-tagged posts | DMs flagging a post; comment storm; one-off engagement spike on a sensitive topic | Founder | Quarterly |

---

## 4. Accepted risks (we knowingly carry these)

Four risks where mitigation cost > expected loss. Documented here so the next quarterly review challenges them honestly.
Acceptance is not "ignore" — each row carries a re-score trigger and a sunset milestone.

| ID | Risk | Why we accept | Sunset trigger |
|---|---|---|---|
| R-OPS-03 (M1-M5 phase) | Sole-founder bus factor with no operational backup | Hiring a backup human at M1 costs €1.5–3k/mo and burns the personal bridge before MRR covers it. Bus-factor mitigation moves from "redundancy" to "documented runbooks + spouse-shared 1Password emergency vault" until M6 VA. | M6 VA hire complete + runbook handover signed off |
| R-OPS-02 / R-DEL-06 | 99% SLA, not 99.9% | A 99.9% target needs hot failover for n8n + Synthflow + CM.com. That's €200+/mo extra and dual-cloud complexity. At <60 clients, 99% (≈7h/mo allowance) is the right trade. | 50 active clients OR enterprise client requesting 99.9% in MSA |
| R-FIN-02 | USD FX exposure on Anthropic, Synthflow, Sentry, Smartlead | USD spend stays <5% of revenue through Y1. Hedging costs more than the swing. | USD spend share >10% of revenue for two consecutive months |
| R-OPS-06 | Single Hetzner VPS for n8n, daily backup but no hot failover | A 30-minute restore from Borgbase is acceptable for our SLA. Hot-standby in Hetzner FI is documented as the M9+ upgrade trigger (`08-tech/stack-decisions.md`). | First VPS-related SEV1 incident OR M9 |

### Risk-acceptance criteria

Before any new risk is moved to "accepted", three conditions must hold:

1. Mitigation cost (cash + founder time) is materially higher than expected loss × probability over the next 12 months
2. A sunset trigger is named (date or event) at which the acceptance is re-evaluated
3. The risk is visible — it cannot live in someone's head only; it must appear in this register with status `accepted`

---

## 5. Quarterly review checklist

Run on the last Friday of each quarter. Founder + VA (from M6) work the list together. Block 90 minutes.

- [ ] Re-score every High and Critical row against last quarter's data
- [ ] Close any row whose mitigation has been verified for two consecutive quarters
- [ ] Open new rows for any incident logged in Notion "Incidents" page this quarter
- [ ] Update owner column where VA has taken ownership
- [ ] Sync sub-processor list (`04-legal/dpa-outline.md` Annex III) and re-check R-COMP-03 status
- [ ] Insurance broker call (Hiscox) — confirm cover still matches exposure (`04-legal/insurance.md`)
- [ ] Re-read `04-legal/ai-act-disclosure.md` against any AP / EU AI Office guidance updates
- [ ] Verify the four accepted-risk rationales still hold; downgrade or upgrade as needed
- [ ] Backup runbook tabletop: pick one R-SEC or R-OPS row and walk the recovery steps in <30 min
- [ ] Commit the updated register with a `risk-register: Q[N] [YYYY]` message

---

## 6. Incident → register lifecycle

How a real event becomes (or doesn't become) a register row.

| Stage | Trigger | Action | Output |
|---|---|---|---|
| Incident | Healthchecks miss, Sentry alert, client report, AP letter | Open Notion incident page within 1h; declare severity (SEV1/2/3) | Incident page with timeline |
| Containment | SEV1: <2h; SEV2: <8h; SEV3: <24h | Apply runbook; communicate to affected clients per SLA | Customer comms + status-page entry |
| Postmortem | Within 5 working days for SEV1/2 | Blameless template in Notion; root cause + corrective actions | Postmortem doc + PR for code/runbook fix |
| Register update | At postmortem close | If recurrence likely, add or update register row; cite incident in mitigation column | New/updated row with ID and incident link |
| Playbook hook | If mitigation is procedural | Add to the relevant playbook in `03-delivery/` or `10-ops/` | Playbook PR merged + linked from register |
| Quarterly review | Next Q-end | Re-score; close if mitigated for two quarters | Updated register |

### Severity definitions

| Severity | Definition | Examples |
|---|---|---|
| SEV1 | Client-facing outage, data loss, or regulator contact | Synthflow down >30 min; Postgres backup corruption; AP letter |
| SEV2 | Partial degradation or single-client impact | n8n flow stuck for one client; SMS delivery failure for a campaign |
| SEV3 | Internal-only or near-miss | Sentry warning without user impact; Renovate PR sat too long |

### Client communication SLA

| Severity | First notice | Status updates | Postmortem shared |
|---|---|---|---|
| SEV1 | <30 min | Every 60 min until resolved | Within 5 working days |
| SEV2 | <2h | Daily | On request |
| SEV3 | n/a | n/a | Internal only |

### Where the register lives

| Artefact | Location | Update cadence |
|---|---|---|
| Canonical register | this file, version-controlled in git | per quarterly review + on-incident |
| Heatmap view | Notion mirror, generated from the markdown | quarterly |
| Status-page mapping | `status.klantkraan.nl` (Uptime Kuma) — incidents reference register IDs | per incident |
| Insurance evidence pack | `/legal/insurance/` + Hiscox annual renewal call notes | annually |
| Onboarding gate | client onboarding checklist references R-COMP-04, R-COMP-05, R-DEL-08 | per onboarding |

---

## 7. Sources

### Regulators and statute

- AP digital direct marketing guidance: https://www.autoriteitpersoonsgegevens.nl/en/themes/internet-and-smart-devices/advertising/digital-direct-marketing
- AP security incidents (breach notification): https://www.autoriteitpersoonsgegevens.nl/en/topics/security/security-incidents
- AP meldloket datalekken: https://www.autoriteitpersoonsgegevens.nl/meldloket-datalekken
- EU AI Act Article 50 (transparency): https://artificialintelligenceact.eu/article/50/
- EU AI Act Article 99 (penalties): https://artificialintelligenceact.eu/article/99/
- AVG Art. 30 RoPA: https://www.privacy-regulation.eu/nl/artikel-30-register-van-de-verwerkingsactiviteiten-EU-AVG.htm
- AVG Art. 33 + 34 (breach notification): https://www.privacy-regulation.eu/nl/artikel-33-melding-van-een-inbreuk-EU-AVG.htm
- AVG Art. 83 (fines): https://www.privacy-regulation.eu/nl/artikel-83-algemene-voorwaarden-voor-het-opleggen-van-administratieve-geldboetes-EU-AVG.htm
- ACM Wet ongewenste telemarketing (July 2026): https://www.acm.nl/nl/onderwerpen/telecommunicatie/telemarketing
- ICO PECR (UK reference for M6+ expansion): https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/

### Insurance and platform policies

- Hiscox PI ICT NL: https://www.hiscox.nl/beroepsaansprakelijkheidsverzekering-ICT
- Hiscox AVB ZZP: https://www.hiscox.nl/bedrijfsaansprakelijkheidsverzekering-zzp
- Gmail bulk sender requirements: https://support.google.com/mail/answer/81126
- Microsoft 365 anti-spam policies: https://learn.microsoft.com/en-us/defender-office-365/anti-spam-protection-about
- Google review policy (incentives): https://support.google.com/contributionpolicy/answer/7400114
- LinkedIn user agreement (automation restrictions): https://www.linkedin.com/legal/user-agreement

### Internal cross-references

- `00-MASTER-PLAN.md § 6` — top-7 risk snapshot
- `04-legal/ai-act-disclosure.md` — Art. 50 baseline
- `04-legal/compliance-checklists.md` — DO BEFORE FIRST CLIENT / DO BEFORE 10TH CLIENT
- `04-legal/insurance.md` — Hiscox PI + AVB + cyber stack
- `06-outbound/gdpr-compliance.md` — BV-filter, LIA, opt-out
- `06-outbound/deliverability-stack.md` — 9-inbox rotation, warm-up, DMARC
- `07-finance/unit-economics.md` — payback, CAC, LTV
- `07-finance/mrr-projections.md` — bear case, cash bridge, trigger thresholds
- `08-tech/stack-decisions.md` — provider swap triggers, EU residency
- `08-tech/observability.md` — Healthchecks + Sentry + Uptime Kuma layers
- `08-tech/infra-setup.md` — Hetzner + Caddy + Tailscale hardening
