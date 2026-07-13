# Klantkraan SEO Strategy — organic growth, short & long term

**Date:** 2026-07-13 | **Method:** 5-agent research pass (technical audit of built site, SERP/keyword refresh, content-strategy research, off-page/authority research, repo-decision synthesis) on top of the May research (`serp-audit.md`, `programmatic-seo-blueprint.md`).
**Product truth this strategy serves:** Chat €299/mo (websitechat + WhatsApp) sellable today; Compleet €499/mo includes voice, never promised before voice is live. All customer-facing content Dutch, founder anonymous ("de oprichter"), KvK 90232135.

---

## Executive summary

1. **klantkraan.nl has a distribution problem, not a conversion problem.** ~2 human visits/day; the domain is invisible even for near-branded queries. Everything below is about earning discovery.
2. **The competitive whitespace is closing.** In May the "AI receptionist for Dutch trades" SERP barely existed; today ≥5 Dutch players occupy it by name (Voicelabs €99–299, installatietelefoniste.nl, vakmanai.nl €197–697, loodgieterai.nl, MIKE365 €15). But **none has real social proof** (loodgieterai's testimonials are labeled AI-generated), most are voice-only, and none owns the text-first WhatsApp+chat angle. The defensible position is *done-for-you + trades-specific + real proof*, not price. First real case study wins the category.
3. **Keyword pivot.** The May plan targeted "[vak] klanten werven" / "leads voor [vak]" — those SERPs are still a broker oligopoly (ETEB, LeadsMaster) and the intent mismatches a receptionist product. The realistic surface is the **bereikbaarheid cluster**: "ai telefoniste [vak]", "gemiste oproepen", "telefoonservice [vak]", "antwoordservice kosten", "whatsapp receptionist" — SERPs that are weeks old, thin, and exactly our intent. Keep the cornerstones for conversion; stop expecting them to rank on broker terms.
4. **AI search is the fresh-domain shortcut.** Dutch AI Overviews live since Oct 2025; citation-overlap with organic top-10 has fallen to 17–54%, meaning **a low-authority site can be cited without ranking**. Levers: answer-first structure, FAQPage/Organization schema, original data, earned third-party mentions. (llms.txt: near-worthless per current evidence — 10-minute lottery ticket, fine, expect nothing.)
5. **Original data is our only outsized lever.** A fresh anonymous-founder domain can't out-authority anyone, but it can be the *primary Dutch source* for missed-call/bereikbaarheid numbers (competitors quote US stats). The rekentool + a "Bereikbaarheid van Nederlandse vakbedrijven" study + a Tarievenindex built from wave1.ts data are the linkable assets.
6. **Respect the founder's validation-first gate.** 2026-05-31 stance: no more site polish until pilot #1. This strategy sequences accordingly — the short-term list is (a) one-time technical debt paydown, (b) assets that *help close pilots* (comparison/price content arms sales conversations), (c) zero-cost founder registrations. The content flywheel scales after pilot #1.

---

## Blocking dependency: Google Search Console (founder, ~15 min)

Every programmatic wave-gate in `programmatic-seo-blueprint.md` §6 is defined against GSC evidence (impressions, "Crawled not indexed" <20%). GSC has never been set up, so **Wave 2 is formally blocked** even though calendar-time (T+6wk = ~2026-07-02) has passed. Verify the domain via DNS TXT (Cloudflare CLI-friendly), submit sitemap-index.xml, manually inspect the 10 Wave-1 URLs. Until then we fly blind on indexation, queries, and rankings — and it's the only free rank/query data source we're allowed (no paid tools until €5k MRR).

---

## Short term (0–3 months)

### S1. Technical debt paydown (Claude-executable, one pass) — from the dist/ audit

Baseline is healthy (unique titles, 1 h1/page, FAQPage schema on niche+city pages, 85 KB pages, no webfonts, strong headers). Ranked fixes:

1. **Trailing-slash internal links site-wide** (HIGH): all ~43 internal hrefs per page hit a 308 redirect (Pages serves `/loodgieters/`, links say `/loodgieters`). Fix Header/Footer/all pages; consider `trailingSlash: 'always'` in astro.config.
2. **City-page canonical/og:url/JSON-LD use the redirecting slash-less URL** (`[stad]/[vak].astro:53,88,111`) while the sitemap says slash — canonical/sitemap disagreement risks Google choosing its own canonical.
3. **Organization + WebSite JSON-LD in Base.astro** (KvK as `identifier`, `sameAs` to socials); Service/Offer schema on /prijzen (two tiers are pure text today).
4. **Home title targets zero demand** ("De Klantenmotor…" — invented branding). Retarget to "AI-receptionist voor vakmensen — websitechat & WhatsApp | Klantkraan". Body: add a niche-teaser section with in-content links to the 6 cornerstones (currently nav/footer-only).
5. **Meta lengths**: 6 niche descriptions 185–256 chars (truncate at ≤155), titles up to 101 chars (≤60).
6. **Blog/gidsen are near-orphans** (1 inbound link each; posts never link niche pages in body). Add: contextual body links, related-posts block, "Verder lezen" block on niche pages (gids + same-vertical posts), both-direction niche↔gids links. Bug: `blog/[slug].astro` `verticalLabel` misses `installateur` → renders `undefined` breadcrumb.
7. **BlogPosting + FAQPage schema in blog layout** (2 posts have FAQ HTML), author = Organization "Klantkraan".
8. Housekeeping: `<lastmod>` via sitemap `serialize`, Cache-Control for `/js/*`, richer titles on /prijzen /rekentool /blog, verify 404 status post-deploy, per-niche OG images (later, CTR only).

### S2. Content — arm the sale first, flywheel second

**Step 0 (before net-new posts):** deepen the 6 cornerstones from ~700 to 1,500–2,000 words (serp-audit's #1 unfinished action — competitors rank with 1,500–3,500) with the §S3 answer-first structure, "Hoe het werkt" deep-dive, sub-niche paragraphs (warmtepomp/laadpaal on installateur; renovatie/aanbouw on aannemer), certification awareness (KOMO/Dakmerk on dakdekkers).

**Cluster build order (D → A → B → C), 2 posts/month, founder-approved via a Telegram gate mirroring growth-engine:**

- **Cluster D — "De digitale receptionist" (buying intent, build FIRST).** Pillar: *AI-receptionist voor vakmensen: de complete gids 2026* (~3,000 w). Money spokes: *AI-telefoniste vs. antwoordservice vs. telefoonaanname uitbesteden: kosten 2026*; *Wat kost een AI-receptionist in 2026? Eerlijke prijzen, ook van concurrenten* (name Voicelabs/MIKE365/VakmanAI with real prices — the honest-comparison page is also the #1 GEO play: nobody owns "ai receptionist vergelijken nederland", and AI assistants cite comparison content when asked "beste ai telefoniste voor loodgieters"); *De Europese AI-wet voor mkb'ers uitgelegd*; *Websitechat, WhatsApp of telefoon: waar uw klanten écht contact zoeken*.
- **Cluster A — "Gemiste oproepen & bereikbaarheid" (core pain).** Pillar anchored on the rekentool. Spokes per the content agent's map; the existing cv-storing post and 2 gidsen slot in.
- **Cluster B — "Klanten werven zonder platformen".** Keeps the serp-audit discovery keywords; Werkspot-as-foil content from `lead-source-platforams.md` data; hosts the **Tarievenindex** (see L2).
- **Cluster C — "Slim plannen & no-shows".** Existing no-show post becomes the pillar. Build last.

**Quality gates (anti scaled-content-abuse; Google penalizes value-less volume, not AI tools):** every post carries ≥1 unfakeable element (real number, real transcript, original calculation, founder-verified tariff); human approval always; ≤10 non-programmatic pages/month; never same-day near-identical vertical variants.

**E-E-A-T with an anonymous founder** (QRG requires *accountability*, not a name): Organization-as-author in schema + byline; KvK in footer + schema; first-person experience content ("we analyzed X chat conversations" — the ai-receptionist app generates proprietary data); named *customers* once pilots exist; live outbound citations; `/over` as accountability hub (story as "de oprichter", KvK, contact, product photos not face).

### S3. Answer-first retrofit (GEO)

On every content page: open each H2 section with a 1–3 sentence direct answer; literal Q&A FAQ blocks; visible "laatst bijgewerkt" dates; quotable standalone stats. Don't block GPTBot/ClaudeBot/PerplexityBot (robots.txt currently allows all — keep). Add llms.txt (10 min, zero maintenance, zero expectations).

### S4. Rekentool → linkable asset (Claude-executable)

Own indexable landing copy (headline number + methodology), per-branche presets deep-linkable by trade media, "embed deze rekentool" snippet with attribution link (website builders for vakmensen + accountants are realistic embedders), linked from every ROI snippet and Cluster-A post.

### S5. Off-page quick wins (founder ~2h total, Claude preps everything)

One sitting: **Gartner Digital Markets** (free listing propagates Capterra/GetApp/Software Advice incl. .nl), **Appwiki.nl**, **VIDM** (journalist-request platform; attribution as "oprichter van Klantkraan" — check profile-visibility first), **ANP Expert Support**. Claude pre-writes the full directory kit (NL/EN descriptions in 3 lengths, category mapping, screenshots list) and expert profiles/talking points. Skip: Google Bedrijfsprofiel (pure-online SaaS is ineligible per Google's rules; suspension risk), generic bedrijvengidsen (nofollow noise), paid advertorials before a news asset exists.

### S6. Distribution loop (infrastructure exists)

Every published post → growth-engine drafts: X auto-post + LinkedIn paste-ready (LinkedIn is the actual buyer channel; X is builder-crowd distribution). Hard ceiling stands: drafting only, no automated replies/DMs, LinkedIn/Reddit manual forever. Repurpose post sections into the 17 existing LinkedIn drafts pipeline.

### S7. Wave 2 programmatic: **NO-GO until GSC evidence**

wave2.ts is written and deliberately unwired. Ship only when GSC shows Wave-1 impressions AND "Crawled not indexed" <20% (blueprint §6). Before wiring: re-angle wave1/wave2 copy from voice-era mechanics ("herkent lekkage in het gesprek") to chat/WhatsApp truth — same fix the cornerstones just got.

---

## Long term (3–12 months)

### L1. The data study (the authority engine)

"Bereikbaarheid van Nederlandse vakbedrijven" — the citable Dutch primary source that doesn't exist (competitors quote US stats; Voicelabs already proved the angle works with a complaints piece). Two methods: (a) desk-based aggregation of public complaint/review data ("niet bereikbaar"/"belt niet terug" mentions per trade per city) — Claude does ~all of it; (b) manual mystery-call study (200 calls, 10 cities; lawful with genuine research purpose, aggregate publishing, no automated dialing ever). Distribute via persbericht to Eisma (installatie.nl — has Expertartikel/Partner-content routes), VMN (gawalo.nl, Cobouw /opinie), Louwers (installatieenbouw.nl bedrijvenindex), InstallatieTotaal Marktnieuws, SchildersVakkrant + the VIDM/ANP channels. ANP Pers Support paid distribution only if organic pickup stalls.

### L2. Tarievenindex (annual linkable asset)

"Voorrijkosten en uurtarieven [vak] 2026, per stad" — the city-level tariff data already sitting in wave1.ts FAQ fragments, aggregated per niche, framed for the trade ("wat rekenen uw concurrenten?"). Earns links from both trade and consumer "kosten" roundups without writing consumer content; internally strengthens every city page sharing the numbers. Refresh yearly (title year becomes a liability every January — quarterly refresh pass from month 6).

### L3. Programmatic waves per blueprint

Wave 2 (10 pages) on GSC evidence → Wave 3 at +6 weeks if indexation holds → batches of 10–20 every 3–4 weeks → 150 pages by ~T+40 weeks. Blueprint's thin-content firewall and internal-linking rules stand. Installateur-G4 suppression rule stands. Add `/amsterdam/`-style city hubs only after ≥3 niches live per city.

### L4. Case studies & proof (the category-winning move)

After pilot #1: a real, named (with permission), KvK-verifiable case study with €-numbers — the single asset no Dutch competitor has. Then: Klantenvertellen/Google reviews widget at ≥5 reviews, per-vertical case pages, "echte gesprekken" transcript content.

### L5. Partnership link engine (ongoing weekly drip)

Website builders for vakmensen (Installizi, Heijtec, Prosperbiz, Vrijdag Online, EigenWebsite.nl…): white-label/referral (15% first-year MRR per partner-channels.md) + rekentool embed → natural dofollow links from tens of trade-adjacent domains. Boekhouders (telt, Doomen & Quist): co-branded guest articles. Brancheverenigingen: trust badges and distribution, not efficient link buys (Techniek Nederland partner-directory link unverified; OnderhoudNL partner page lists nothing) — rank below directories and data-PR.

### L6. Measurement maturity

Month 0: GSC + weekly query/indexation check (CLI: `gsc`-API script fits founder's CLI preference). Month 1+: Cloudflare Web Analytics goals for demo/WhatsApp clicks; growth-engine post → traffic correlation. Month 6: quarterly content refresh pass keyed on GSC query data; Ahrefs Webmaster Tools (free) for backlink monitoring. No paid tools until €5k MRR (standing rule).

---

## Founder actions (Claude cannot do these)

| # | Action | Time | Unblocks |
|---|--------|------|----------|
| 1 | GSC domain verification (DNS TXT) + submit sitemap | 15 min | Wave 2, all rank/query data, wave gates |
| 2 | Deploy the committed truth-audit + upcoming SEO fixes (`wrangler pages deploy`) | 5 min | everything — live site still serves stale claims |
| 3 | Gartner DM + Appwiki + VIDM + ANP registrations (Claude preps all copy) | ~2 h | first real backlinks + press channel |
| 4 | Approve content cadence (2 posts/month) + each post via Telegram gate | 15 min/post | content flywheel |
| 5 | Decide data-study method (desk-based vs mystery-call) | decision | L1 |
| 6 | Send persbericht/partner emails from company mailbox (Claude drafts) | drip | L1, L5 |

## Standing constraints honored

Dutch customer-facing; "de oprichter" never a name; no fake proof ever; no cold-call automation; no eenmanszaak cold email; drafting-only social ceiling (X auto, LinkedIn/Reddit manual); no third-party scripts (CSP self); manual wrangler deploys; no paid SEO tools <€5k MRR; no paid ads at €299 tier; validation-first — content that arms pilot sales ships first, scale ships after pilot #1.

## Stale docs flagged (do not propagate)

serp-audit action #7 pricing ("€299 Lite · €599 Pro"), positioning.md voice-era lead + "no setup fee", seo-keywords.md audio-demo angles, channel-strategy's GBP-posts assumption (GBP ineligible), memory `project_pricing_tiers` (€349/€599/€849 superseded by Chat €299 / Compleet €499).

## Sources

Full agent reports (SERP refresh with competitor table + URLs; GEO/AI-search evidence incl. llms.txt studies; topic-cluster/E-E-A-T/cadence sources — Backlinko, Grow and Convert, Animalz, Google QRG Sept 2025, Google gen-AI content guidance; off-page channel research with all outlet/directory URLs) are preserved in the session transcript of 2026-07-13; key standing references: `research/serp-audit.md`, `research/programmatic-seo-blueprint.md`, `research/partner-channels.md`, `research/email-nurture-teardown.md`, `docs/05-content/seo-keywords.md`, Search Engine Land GEO guide 2026, developers.google.com/search AI-optimization guide, otterly.ai + seranking.com llms.txt studies.
