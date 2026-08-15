# Track 2 — Website Factory for Klantkraan — Research Report (2026-08-12)

**Goal tested:** €1000 fixed-price Dutch trades website, <1 hour founder time, as receptionist add-on.
**Verdict:** achievable in _founder-time_ (~60 min) but not wall-clock (realistically 1–3 days elapsed), and only if three process gates are enforced ruthlessly: clock-starts-on-complete-intake, AI-writes-all-copy, and exactly one consolidated revision round. Comparable human services spend 8–16 hours of labor; automation absorbs that, but nothing absorbs client-chasing except process design.

## 1. Factory architecture: one codebase, per-client config wins

**Recommended: single Astro codebase + per-client YAML config + content collections, one Cloudflare project per client.** Mirrors what already works in `ai-receptionist/config/prospects/*.yaml` — ideally the _same_ client YAML feeds both receptionist and site.

- Astro multi-tenant template + 2025 Content Layer API (typed collections, Zod schemas in shared packages) built for exactly this (astro.build/blog/year-in-review-2025).
- Practitioner pattern for 15+ client sites: monorepo, each client site a thin app importing shared `packages/`; packages never import from apps (Wumty). Repo is already a pnpm/turbo monorepo — factory is an `apps/client-sites` addition, not a new stack.
- **Reject per-client repo forks:** template fixes must be cherry-picked into N repos — maintenance death at ~10 clients. Config-driven: one fix + `for client in configs: build && deploy`.
- **Reject site builders (Duda/Webflow):** Duda = $19/mo per extra site on top of $149–199/mo plans — the entire €25–49/mo maintenance margin gone to a vendor, plus lock-in, plus losing the cookie-banner-free static story and squirrelscan/Claude leverage. Duda's existence validates the market; owning the pipeline beats renting it past ~5 clients.

**AI site builders don't threaten this.** 2025–2026 verdicts: Lovable best design but buggy; v0 for React devs; Durable 30-second sites but generic/limited; Mixo/Carrd validation-grade (usemotion.com 14-builder test, TechRadar, DesignRevision). Recurring complaint: "generic templates lightly customized with your text." None give: consistent Dutch trades brand system, NL legal footer/privacy templates, no-cookie-banner guarantee, schema correctness, QA gates.

## 2. Hosting & infra: automatable end-to-end (verified against current docs)

| Step                                   | Automatable?                     | How                                                                                                                                                                  |
| -------------------------------------- | -------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Deploy site                            | Yes, fully                       | `wrangler pages deploy` (existing flow)                                                                                                                              |
| Pages projects at scale                | Yes, to a point                  | **100 projects/account soft cap** (raisable via support); 100 custom domains/project free (CF Pages limits)                                                          |
| Attach custom domain to Pages          | Yes — REST API, **not** wrangler | `POST /accounts/{id}/pages/projects/{name}/domains` + PATCH retry validation; wrangler has no domain command (workers-sdk#11772)                                     |
| Register .nl domain                    | Yes — but **not via Cloudflare** | CF Registrar API (beta Apr 2026) does NOT support .nl. Use **TransIP REST API / `tipctl` CLI**: register .nl (~€10/yr), set NS, manage DNS — fully scriptable        |
| DNS zone + records                     | Yes, fully                       | TransIP NS → Cloudflare → CF API `POST /zones` (free plan) → records via API. SSL on Pages automatic                                                                 |
| Email forwarding (info@klantdomein.nl) | Mostly                           | CF Email Routing rules/addresses API-driven, **but each new destination address requires the client to click a verification email** — one client action, unavoidable |

**Domain ownership policy:** register in the _client's_ name (Klantkraan as technical contact) — "u blijft eigenaar van uw domein" is a trust point vs WaaS competitors and de-risks offboarding.

**Platform note:** Cloudflare now recommends Workers-with-static-assets over Pages for new projects; Pages stays supported. Don't migrate now; isolate the factory's deploy step in one script so a later Pages→Workers swap touches one file.

## 3. What goes ON the site (conversion + NL legal)

Conversion, evidence-ranked:

1. **Click-to-call**: phone leads convert 10–15x the revenue of form fills for home services; sticky mobile call button + `tel:` header link (Rocket Media 2026). Above-fold CTAs outperform ~304%.
2. **WhatsApp button**: plain `https://wa.me/316...?text=...` — zero setup. Strategic: feeds the receptionist's WhatsApp surface — **the website is a lead-intake funnel for the €299–499/mo product**.
3. **Speed**: conversion ~3.05% at 1s load vs ~1.08% at 5s — Astro static is a measurable selling point.
4. **Reviews**: 5+ visible reviews lift conversion up to 270%. Google Places API: only 5 reviews, no caching, attribution required; widgets (Elfsight/Trustindex) add third-party JS breaking the no-cookie-banner story. **Do: manually curated quotes + "Bekijk al onze reviews op Google" link. Do NOT add review/aggregateRating schema** — self-serving review markup is ignored and can trigger a manual action.
5. **Service-area pages**: still core local SEO, but templated city pages = doorway abuse (March 2024 wiped ~80%). **Cap at 3–5 city pages with real local substance**, never 30 templated ones.
6. **Schema**: `Plumber`/LocalBusiness + Service JSON-LD, NAP matching GBP exactly.
7. **Photos**: real phone photos out-convert stock by up to 35% in trades A/B tests; AI "work photos" damage trust and violate GBP reality guidance. **Policy: 10 phone photos = hard intake requirement (WhatsApp shot list: bus, werk, voor/na). Fallback = photo-free design (color blocks, werkgebied map, review cards) — never stock people, never AI job photos.**

NL legal (template once, reuse forever):

- **Footer**: statutaire naam + handelsnaam, bezoekadres, e-mail, telefoon, **KvK-nummer én btw-id** (art. 27 Hrw 2007 + art. 3:15d BW). btw-id, never the old BSN-based number.
- **Privacyverklaring**: required with any contact form; must name processors incl. the receptionist backend.
- **Cookie banner: NOT needed** on a static site with only functional cookies + cookieless analytics (Plausible / CF Web Analytics) — Telecommunicatiewet 11.7a lid 3 exception. Re-triggers: YouTube embeds, Google Maps, review widgets, pixels. **"Geen cookiebanner nodig" is a verifiable sales feature** (ACM fines to €900k; Eneco €750k in 2024).
- **EAA/accessibility**: brochure trades sites not covered + micro-enterprise exemption — build to reasonable WCAG AA, don't sell as legal obligation.
- **Algemene voorwaarden**: optional; publishing on site satisfies art. 6:230c BW information duty.

## 4. The <1 hour workflow (what "website in a day" services actually do)

Honest finding: **"one day" services hide labor outside the window** — homepage designed days before with prior contracts/copy docs (Inkpot); VIP-day designers require all copy/photos upfront and cap at 3–5 pages. Time is lost to intake chasing and feedback loops ("projects reach 80% then stall"), not building.

Three load-bearing mechanisms:

1. **Clock starts at approved-complete intake, not payment** — incomplete submissions rejected with checklist; client delays contractually excluded (48HourWebsites). No discovery calls: pricing page → Tally form → build (Perier).
2. **AI writes all copy; client is never a copy dependency.** Tally intake with conditional logic + pick-from-menu answers (USPs, tone, diensten per vertical preset) feeding Claude prompts. Dutch output needs one human NL pass — fits the no-AI-tells rule.
3. **Exactly one consolidated revision round**, via form (not email threads), 5-working-day response window or it ships as-is; post-launch edits live in the maintenance subscription (market norm: 1 round at €399-tier).

**Minimal intake form (Tally):** bedrijfsnaam + KvK-nr + btw-id, diensten (checkboxes per vertical preset), werkgebied (3–5 plaatsen), openingstijden + spoed ja/nee, USPs from menu, telefoon/WhatsApp, logo (optional), **10 werkfoto's (required, shot list)**, 2–3 review quotes of GBP link, certificeringen, domeinnaam-wens.

## 5. Recommended pipeline + founder time budget

| Stage                                                                                                                                                                                                                                                      | Automation           | Founder time | Wall clock                                         |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------- | ------------ | -------------------------------------------------- |
| 0. Sale: pricing page → Mollie → Tally intake link auto-sent (Resend)                                                                                                                                                                                      | Full                 | 0 min        | —                                                  |
| 1. Intake completeness check; reject-with-checklist                                                                                                                                                                                                        | Claude pre-screens   | **10 min**   | 0–7 days (client-dependent, excluded from promise) |
| 2. Generate: intake YAML → client config → Astro build → Dutch copy via Claude → preview to `*.pages.dev`                                                                                                                                                  | Full (one command)   | 0 min        | ~30–60 min compute                                 |
| 3. Automated QA: squirrelscan + lychee + pa11y-ci WCAG2AA + Lighthouse gates (perf ≥0.9, LCP ≤2.5s, CLS ≤0.1) + Playwright 3-viewport screenshots vs baseline + **intake-fact assertion script** (phone, KvK, plaatsen, tel:/wa.me links, no placeholders) | Full                 | 0 min        | ~15 min                                            |
| 4. Founder review: Dutch copy pass, photo placement, mobile eyeball                                                                                                                                                                                        | —                    | **25 min**   | —                                                  |
| 5. Client review via preview link, one consolidated revision form, deadline                                                                                                                                                                                | Claude applies edits | **15 min**   | 1–5 days                                           |
| 6. Go-live: TransIP .nl + NS → CF zone API → Pages domain REST → Email Routing (client clicks verify) → deploy → smoke re-audit                                                                                                                            | Full script          | **5 min**    | ~1–2 h incl. DNS                                   |
| 7. Handover: WhatsApp with live URL, GBP-link instructie, review-vraag                                                                                                                                                                                     | Templated            | **5 min**    | —                                                  |
| **Total**                                                                                                                                                                                                                                                  |                      | **~60 min**  | **2–8 days elapsed**                               |

Holds **per site, in founder attention, at steady state** — after template, intake form, QA harness, and go-live script exist (one-time build ~2–4 focused days, mostly assembling existing assets). Breaks the moment the founder takes a call, answers an email thread, or grants a second revision round.

Note: no CLI exists for Google's Rich Results Test — validate emitted JSON-LD with own assertion script. The intake-fact check guards the most embarrassing failure (wrong phone number on a lead-gen site).

## 6. Pricing & recurring attach

- €1000 sits comfortably: comparables Webexperts €495 + €25/mo, Froseo €69/mo WaaS, Web&Wij €39/mo. Upfront pricing self-selects committed clients vs €0-down WaaS.
- **Attach €29–39/mo "onderhoud & hosting"** (market €25–50/mo entry) — near-pure margin on static. Discount **only when bundled with a receptionist plan** (≤10–15%, on the cheap-to-serve site side). One invoice.
- Strategic frame: the site's wa.me/click-to-call buttons route into the receptionist — the website is receptionist-attach and **churn insurance** (cancelling the receptionist orphans the site's lead channels).

## 7. Top risks (skeptical view)

1. **Client-side latency destroys the promise perception.** Sell "live binnen X werkdagen na complete intake," never "in één uur."
2. **Revision creep.** One "vriendendienst" extra round turns 1 hour into 4. Included/swap/paid-change taxonomy in the offerte.
3. **Photo bottleneck.** The one asset that can't be AI'd. Mitigate: shot list via WhatsApp at payment, photo-free fallback design pre-built.
4. **Wrong business facts shipped.** Squirrelscan won't catch a wrong phone number — intake-fact assertion gate is mandatory.
5. **Infra caps & gaps:** 100 Pages projects soft cap (request raise early); .nl not on CF Registrar (TransIP dependency); email-routing needs one client click; Pages→Workers drift (isolate deploy in one script).
6. **SEO landmines:** self-serving review schema (manual action risk) and templated city pages (doorway penalty) — tempting "value adds" the factory must deliberately NOT do.
7. **Maintenance expectations vs €29–39/mo:** define "kleine wijzigingen" (e.g. 2 tekst/foto-edits per month) in writing.
8. **Cookie-free claim is fragile:** one YouTube embed or review widget reintroduces the banner — keep an approved embed list (lite-youtube/nocookie, static maps image).

**Recommended first step:** don't build the full factory — run one pilot site for an existing warm prospect through a manual version of the pipeline, timing each stage, before automating what measurement proves expensive. Matches the narrow-pilot principle.
