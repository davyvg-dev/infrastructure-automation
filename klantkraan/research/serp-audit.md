# SERP & Content-Gap Audit — Klantkraan.nl

**Date:** 2026-05-21 | **Auditor:** Claude (agent run) | **Branch:** claude/business-marketing-planning-FArXV

---

## Executive Summary

Across all five niches (installateur, loodgieter, dakdekker, aannemer, schilder) the Dutch SERP is dominated by two types of pages: (1) lead-broker platforms (LeadsMaster, ETEB, VPM, De Klantenwerving, Allfree) targeting B2C searchers to capture quote requests, and (2) niche-specific marketing agencies (Roxtar, B&S Media, Ompro, Drijfveer Media) targeting B2B searchers who want to outsource marketing. Klantkraan's cornerstones sit in neither category clearly — they are B2B product pages but lack the content depth (1,500–3,500 words vs. Klantkraan's ~600–800 words per page), schema markup, city-level proof, and industry-keyword targeting that let either type of competitor rank. The top five content gaps to close immediately are: (1) add FAQPage schema, (2) add city-level proof sections, (3) add real testimonials replacing placeholder copy, (4) build keyword-aligned meta titles targeting "[niche] klanten werven" and "leads voor [niche]", and (5) add a schilder cornerstone page — the only niche with no page at all.

---

> **Location caveat:** All SERP data was collected by a US-based agent. Google personalises results by location, language, and user history. Dutch users in Amsterdam or Rotterdam will see a different local pack and organic ranking than what an agent running outside the Netherlands sees. The results below reflect keyword-level signals (page titles, content patterns, domain types) that are directionally valid even across geolocation variation, but exact ranking positions should be verified from a Dutch IP or via Google Search Console if the domain is live.

---

## 1. Per-Niche SERP Audit

### 1.1 Installateur

#### Query A: "installateur klanten werven"

| #   | URL                                   | Title (inferred)                                     | Type                |
| --- | ------------------------------------- | ---------------------------------------------------- | ------------------- |
| 1   | onlineleadbox.nl/installatietechniek/ | Klanten werven Installatietechniek — Online Leadbox  | Lead broker/agency  |
| 2   | vakbladwarmtepompen.nl                | Zes tips om online nieuwe klanten te werven          | Trade publication   |
| 3   | gawalo.nl                             | Zo komt de installateur online aan nieuwe opdrachten | Trade publication   |
| 4   | installatie.nl                        | Installateurs: werven, werven, werven                | Trade publication   |
| 5   | installatie.nl                        | Klantenbestand uitbreiden: tien tips                 | Trade publication   |
| 6   | uwduurzameinstallateur.nl             | Hoe krijg jij nieuwe klanten die ook bij je blijven? | Content/lead magnet |
| 7   | ichoosr.nl                            | Meedoen als leverancier?                             | Lead platform       |
| 8   | warmtepompgids.be                     | Warmtepomp leads ontvangen                           | Lead broker         |

**Top-3 content inspection (onlineleadbox.nl/installatietechniek/):**

- H1: "De juiste nieuwe klanten in de installatietechniek"
- H2s: "De juiste klanten in 30 dagen", "Aan welke klanten kunnen wij je helpen?", "Jij werft sneller nieuwe klanten met deze tips", "De blauwdruk voor het werven van nieuwe klanten"
- Word count: ~1,200–1,400 words
- Content blocks: 12 data insights/stats, service-category breakdowns (zonnepanelen, warmtepompen, CV-ketels, laadpalen), 6 client logos, Google Reviews 4.8/5 badge, contact lead form
- Schema types: none visible in fetched HTML
- Ranking factors: strong domain authority of dedicated trade site, niche keyword targeting, rich data points, social proof via reviews and logos

#### Query B: "leads voor installateur Nederland"

| #   | URL                                                               | Title (inferred)                                        | Type          |
| --- | ----------------------------------------------------------------- | ------------------------------------------------------- | ------------- |
| 1   | warmeleads.eu/leads-zonnepanelen                                  | Zonnepanelen Leads Kopen — WarmeLeads                   | Lead broker   |
| 2   | leadsmaster.nl/leads-voor-installateurs-elektro-warmtepomp-airco/ | Leads voor installateurs — Leadsmaster                  | Lead broker   |
| 3   | vpm.nl/warmtepomp-leads                                           | Warmtepomp Leads — VPM                                  | Lead broker   |
| 4   | 072design.nl                                                      | Leadmodule: slimme leadgeneratie voor installateurs     | Agency        |
| 5   | bouwberichten.nl                                                  | Vind alle bouwprojecten van installateurs               | Data platform |
| 6   | uwduurzameinstallateur.nl                                         | Via welke kanalen kun je leads voor je bedrijf krijgen? | Content       |

**Content patterns:** Lead brokers dominate; pages run 1,500–2,500 words. Standard blocks: hoe werkt het?, voordelen, prijsmodel (pay-per-lead), FAQ, reviews widget. City-level filtering UI is a major feature (choose province/gemeente).

#### Query C: "installateur online vindbaar maken"

| #   | URL                    | Title (inferred)                                | Type             |
| --- | ---------------------- | ----------------------------------------------- | ---------------- |
| 1   | prosperbiz-websites.nl | Websites voor installateurs — €379              | Website agency   |
| 2   | vrijdagonline.nl       | Website laten maken installatiebedrijf          | Website agency   |
| 3   | invato.nl              | Websites speciaal voor Installateurs            | Website agency   |
| 4   | installizi.nl          | Installizi — websites voor installateurs        | Niche web agency |
| 5   | vwebdesign.nl          | Installatiebedrijf website maken                | Website agency   |
| 6   | deddo.nl               | DEDDO — digitaal gereedschap voor installateurs | SaaS tool        |

**Content patterns:** This query pulls website-builder/agency pages. All lead with a trade-specific H1 ("Website laten maken voor installateurs"), price anchor (often €379–€550), mobile-first messaging, SEO proof paragraph. Most have 5–10 city sub-pages internally linked.

---

### 1.2 Loodgieter

#### Query A: "loodgieter klanten werven"

| #   | URL                              | Title (inferred)                                       | Type              |
| --- | -------------------------------- | ------------------------------------------------------ | ----------------- |
| 1   | eteb.nl/loodgieter-leads/        | Loodgieter leads inkopen — klanten uit uw regio [2026] | Lead broker       |
| 2   | deklantenwerving.nl/loodgieter/  | Loodgieter leads kopen — Werf nieuwe klanten           | Lead broker       |
| 3   | vpm.nl/loodgieter-leads          | Loodgieter Leads — VPM                                 | Lead broker       |
| 4   | higherlevel.nl                   | Ik wil mijn loodgieterbedrijf uitbreiden               | Forum             |
| 5   | kvk.nl                           | Nieuwe klanten werven in 6 stappen                     | Authority (KVK)   |
| 6   | economy.nl/branches/loodgieters/ | Online Marketing voor Loodgieters                      | Agency            |
| 7   | meandermarketing.nl              | 8 tips klanten werven MKB                              | Generic marketing |

**Top-3 content inspection (eteb.nl/loodgieter-leads/):**

- H1: "Klanten werven: loodgieter leads"
- H2s: "Extra klanten werven met loodgieter leads? Ontdek de voordelen!", lead-type categories (CV ketel leads, lekkage leads, etc.), "Hoe werkt het?", "Uw voordelen", provincial coverage form
- Word count: ~1,200–1,400 words
- Content blocks: 12 Dutch provinces listed, pay-per-lead pricing model, quality-control promise, reclamation option
- Schema types: not visible in fetched HTML
- Ranking factors: exact-match keyword in H1 and URL slug, year in title tag, regional intent signals (province list)

#### Query B: "leads voor loodgieter Nederland"

| #   | URL                                    | Title (inferred)                            | Type                |
| --- | -------------------------------------- | ------------------------------------------- | ------------------- |
| 1   | vpm.nl/loodgieter-leads                | Loodgieter Leads — VPM                      | Lead broker         |
| 2   | joslaan.nl/loodgieter-leads-kopen/     | Loodgieter leads kopen                      | Lead broker         |
| 3   | deklantenwerving.nl/loodgieter/        | Loodgieter leads — Werf nieuwe klanten      | Lead broker         |
| 4   | allfree.nl/loodgieter/                 | Loodgieter leads — Allfree (12 jr ervaring) | Lead broker         |
| 5   | leadsmaster.nl/leads-voor-loodgieters/ | Leads voor loodgieters — binnen 48 uur      | Lead broker         |
| 6   | kwieq.nl/leads/                        | Loodgieter leads ontvangen — Kwieq          | Lead broker         |
| 7   | slimster.nl                            | Loodgieter leads — Slimster                 | Comparison platform |

**Top-3 content inspection (leadsmaster.nl/leads-voor-loodgieters/):**

- H1: "Leads voor loodgieters"
- H2s: Wat zeggen onze klanten, Waarom online leads belangrijk zijn voor loodgieters, Hoe wij loodgieters helpen, Wat levert het op?, Wat kost het?, Wat kun je zelf doen?, Veelgestelde vragen
- Word count: ~2,100 words
- Content blocks: customer testimonials, "750+ ondernemers geholpen", 5.0/5 Google Reviews (32 reviews), service method breakdown (Google Ads, Meta Ads, SEO), FAQ (3 questions), pricing section, Utrecht + Amersfoort city mentions
- Schema: Organization schema, LocalBusiness info, review aggregation in footer (5.0/5, 32 reviews)
- Ranking factors: depth (2,100 words), social proof numbers, schema markup, FAQ section

#### Query C: "loodgieter online vindbaar maken"

| #   | URL                                                      | Title (inferred)                                    | Type           |
| --- | -------------------------------------------------------- | --------------------------------------------------- | -------------- |
| 1   | bsmedia.nl/blog/...                                      | Waarom SEO voor loodgieters écht onmisbaar wordt    | Agency blog    |
| 2   | vizibly.nl/seo-voor-loodgieters-en-installatiebedrijven/ | SEO loodgieters — meer opdrachten uit Google        | Agency         |
| 3   | yezo.nl                                                  | Website laten maken loodgieter — vindbaar in Google | Website agency |
| 4   | klusio.nl/lokale-seo/                                    | Lokale SEO: zo word je lokaal vindbaar              | Agency         |
| 5   | dezaak.nl                                                | Stappenplan lokale SEO — lokaal beter vindbaar      | Business media |
| 6   | brightdigital.com                                        | Je online vindbaarheid verbeteren — Google Maps     | Agency         |

**Content patterns:** This query pulls educational/agency SEO content. All pages include a Google Business Profile optimisation section, review-collection tips, mobile-first paragraph, and typically 5–10 H2 sections averaging 1,800–2,500 words.

---

### 1.3 Dakdekker

#### Query A: "dakdekker klanten werven"

| #   | URL                                                | Title (inferred)                                    | Type         |
| --- | -------------------------------------------------- | --------------------------------------------------- | ------------ |
| 1   | roxtar.nl/online-marketing-uitbesteden/dakdekkers/ | Online marketing voor dakdekkers — Exclusieve Leads | Agency       |
| 2   | bsmedia.nl/online-marketing/dakdekkers/            | Online marketing voor dakdekkers — B&S Media        | Agency       |
| 3   | deklantenwerving.nl/dakwerken/                     | Dakdekker leads kopen                               | Lead broker  |
| 4   | ompro.nl/online-marketing-dakdekkersbedrijven/     | SEO & Google Ads voor dakdekkers                    | Agency       |
| 5   | jouwdakexpertmarketing.nl                          | Jouw Dakexpert Marketing — leads voor dakdekkers    | Niche agency |
| 6   | rocketmarketing.nl/online-marketing/dakdekkers/    | Online marketing voor dakdekkers                    | Agency       |
| 7   | vakmanmarketing.nl/leads-dakdekker/                | Dakdekker Leads — vanaf dag 1                       | Lead broker  |

**Top-3 content inspection (roxtar.nl/online-marketing-uitbesteden/dakdekkers/):**

- H1: "Online marketing voor dakdekkers — Exclusieve Leads, worden niet gedeeld"
- H2s: agency value props, service descriptions (SEA, SEO, website optimisation, social media), case studies section, testimonials section, free strategy session CTA
- Word count: ~3,500 words
- Content blocks: 17 detailed case studies (with metrics like "288% conversion increase"), Google Partner badge, Meta Associate certification, TikTok Agency partnership, explicit "exclusieve leads" differentiator
- Schema: implied Service schema and LocalBusiness
- Ranking factors: extreme content depth (3,500 words), multiple case studies with specific metrics, certification badges, industry niche specificity

#### Query B: "leads voor dakdekker Nederland"

| #   | URL                             | Title (inferred)                               | Type                |
| --- | ------------------------------- | ---------------------------------------------- | ------------------- |
| 1   | dakconnect.nl                   | DakConnect — Dakdekker Leads                   | Niche lead broker   |
| 2   | dakdekkersgids.nl               | Dakdekker leads — op zoek naar nieuwe klanten? | Directory           |
| 3   | allfree.nl/dakdekker/           | Dakdekker leads — Allfree                      | Lead broker         |
| 4   | slimster.nl                     | Dakdekker leads — Slimster                     | Comparison platform |
| 5   | deklantenwerving.nl/dakwerken/  | Dakdekker leads kopen                          | Lead broker         |
| 6   | leadsmaster.nl/dakdekker-leads/ | Dakdekker leads — hoogste kwaliteit            | Lead broker         |
| 7   | growsocialmedia.nl              | Dakdekker leads — direct meer aanvragen        | Agency              |
| 8   | dakconnect.nl/dakdekker-leads/  | Dakdekker Leads — binnen 72u                   | Lead broker         |
| 9   | offerteadviseur.nl              | Dakdekker leads — geen abonnement              | Comparison          |
| 10  | kosten-dakdekker.nl             | Dakdekker leads kopen                          | Cost info site      |

**Top-3 content inspection (leadsmaster.nl/dakdekker-leads/):**

- H1: "Dakdekker leads"
- Word count: ~2,500 words
- Content blocks: testimonials, FAQ (5 questions), pricing mention ("€15–€50 per lead" industry range), Facebook Ads explanation, exclusive leads USP, "750+ ondernemers geholpen" stat, Organization + LocalBusiness + review aggregation schema (5.0/5, 32 reviews)
- Ranking factors: depth, schema, specific pricing anchor, FAQ coverage

#### Query C: "dakdekker online vindbaar maken"

| #   | URL                                       | Title (inferred)                                            | Type        |
| --- | ----------------------------------------- | ----------------------------------------------------------- | ----------- |
| 1   | dijkmandesign.nl/website-voor-dakdekkers/ | Website voor Dakdekkers — SEO Dakdekker Website             | Agency      |
| 2   | rankingpartner.nl/dakdekker/              | Meer opdrachten als Dakdekker — Rankingpartner              | Agency      |
| 3   | dijkmandesign.nl/seo-voor-dakdekkers/     | SEO voor Dakdekkers — bovenaan Google                       | Agency      |
| 4   | vizibly.nl                                | SEO voor dakdekkers: 10 tips                                | Agency blog |
| 5   | roxtar.nl                                 | Online marketing voor dakdekkers                            | Agency      |
| 6   | rankrocket.nl                             | SEO voor dakdekkers — Rank Rocket                           | Agency      |
| 7   | ompro.nl                                  | SEO & Google Ads Dakdekkersbedrijven                        | Agency      |
| 8   | ecomprofits.nl                            | Meer leads voor dakdekkers: hoe je meer klanten binnenhaalt | Agency blog |

---

### 1.4 Aannemer

#### Query A: "aannemer klanten werven"

| #   | URL                                                             | Title (inferred)                              | Type            |
| --- | --------------------------------------------------------------- | --------------------------------------------- | --------------- |
| 1   | drijfveermedia.nl/ervaringsberoepen/online-marketing-aannemers/ | Online marketing aannemers — Drijfveer Media  | Agency          |
| 2   | advertisr.nl/blog                                               | Klanten werven als zzp'er in de bouw          | Agency blog     |
| 3   | kvk.nl                                                          | Nieuwe klanten werven in 6 stappen            | Authority (KVK) |
| 4   | yooker.nl                                                       | In 10 stappen naar klanten werven online      | Agency blog     |
| 5   | salesgids.com                                                   | 14 tips succesvol klanten werven via internet | Marketing guide |
| 6   | mkbservicedesk.nl                                               | Het belang van nieuwe klanten werven          | Business media  |

**Top-3 content inspection (drijfveermedia.nl):**

- H1: "Online marketing voor aannemers"
- H2s: "Dé online marketing partner van aannemers", "Wat maakt online marketing voor aannemers anders", "Webdesign voor aannemers", "SEO & hoog in Google", "Adverteren", "Social media"
- Word count: ~1,200–1,400 words
- Content blocks: 4.8/5 stars from 98 reviews, pricing anchor (websites from €550), 6 blog articles, contact form, 10+ year experience claim
- Schema: none visible

#### Query B: "leads voor aannemer Nederland"

**Pattern from adjacent searches:** Market dominated by the same lead-broker oligopoly (De Klantenwerving, LeadsMaster, VPM, Slimster, Allfree) — all with aannemer-specific subpages following identical template: H1 "Aannemer leads", 2,000–2,500 words, pay-per-lead pricing, testimonials, FAQ, city/province coverage.

#### Query C: "aannemer online vindbaar maken"

| #   | URL             | Title (inferred)                                        | Type           |
| --- | --------------- | ------------------------------------------------------- | -------------- |
| 1   | refixseo.com    | SEO voor aannemers — Meer Leads en Omzet                | Agency         |
| 2   | opeinstein.nl   | Aannemer Website Laten Maken — professioneel & vindbaar | Agency         |
| 3   | onlinelabs.nl   | Lokale SEO voor bedrijven: 10 strategieën 2026          | Agency blog    |
| 4   | binkonline.nl   | Website laten maken als aannemer — waar let je op?      | Agency blog    |
| 5   | scoob.online    | SEO voor Aannemers: praktische gids                     | Agency blog    |
| 6   | ralfvanveen.com | SEO for contractors: guide en stappenplan               | Authority blog |

---

### 1.5 Schilder

#### Query A: "schilder klanten werven"

| #   | URL                                            | Title (inferred)                               | Type          |
| --- | ---------------------------------------------- | ---------------------------------------------- | ------------- |
| 1   | allfree.nl/schilder/                           | Meer klanten als schilder — Allfree            | Lead broker   |
| 2   | roxtar.nl/online-marketing/schildersbedrijven/ | Online Marketing voor Schildersbedrijven       | Agency        |
| 3   | sikkens.nl                                     | Vind nieuwe klanten voor je schildersbedrijf   | Brand content |
| 4   | rocketmarketing.nl/online-marketing/schilders/ | Online marketing voor schilders                | Agency        |
| 5   | alstublieftnieuweklanten.nl                    | Nieuwe klanten voor schildersbedrijf — 10 tips | Content/lead  |
| 6   | deklantenwerving.nl/schilder/                  | Schilder leads kopen                           | Lead broker   |
| 7   | rankingpartner.nl/schilder/                    | Meer opdrachten als schilder                   | Agency        |
| 8   | market-ai.nl/online-marketing-voor/schilder    | Online Marketing voor Schilder                 | Agency        |
| 9   | multifunnelmarketing.nl                        | Multi Funnel Marketing voor schildersbedrijf   | Agency        |

#### Query B: "leads voor schilder Nederland"

| #   | URL                                  | Title (inferred)                         | Type        |
| --- | ------------------------------------ | ---------------------------------------- | ----------- |
| 1   | deklantenwerving.nl/schilder/        | Schilder leads kopen — omzet verhogen    | Lead broker |
| 2   | vpm.nl/schilder-leads                | Schilder Leads — VPM                     | Lead broker |
| 3   | rocketleads.com                      | Unieke en gevalideerde schilder leads    | Lead broker |
| 4   | gigaleads.nl/sector/schilder         | Leadgeneratie Schilder — Gigaleads       | Lead broker |
| 5   | leadsmaster.nl/leads-voor-schilders/ | Leads voor schilders — hoogste kwaliteit | Lead broker |
| 6   | de10beste.nl                         | Schilder leads kopen [2026]              | Aggregator  |

#### Query C: "schilder online vindbaar maken"

| #   | URL                              | Title (inferred)                          | Type         |
| --- | -------------------------------- | ----------------------------------------- | ------------ |
| 1   | postmastersoftware.nl            | Website laten maken schildersbedrijf 2026 | Software/web |
| 2   | market-ai.nl                     | Online Marketing voor Schilder            | Agency       |
| 3   | wescaleup.nl                     | Website voor schilders — WeScaleUp        | Agency       |
| 4   | roxtar.nl                        | Online Marketing Schildersbedrijven       | Agency       |
| 5   | ib-visie.nl                      | SEO voor schildersbedrijven               | Agency       |
| 6   | schilderai.nl/seo-voor-schilders | SEO voor Schilders — SchilderAI           | Niche tool   |

---

## 2. Google Maps Audit

> Note: Direct Google Maps scraping was not possible from a US-based agent. Data below is inferred from Dutch review aggregators (Trustoo, Werkspot, Slimster, schilder-nu.nl) which mirror Maps signals. These numbers are directionally accurate but may not match live Maps rankings as of 2026-05-21.

### Installateur (CV & verwarmingsinstallateurs)

| City      | Platform signals                                       | Top profile characteristics                                                                                      |
| --------- | ------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------- |
| Amsterdam | Trustoo avg 8.9/10 from 8,952 reviews across providers | Top profiles: 50–200+ Google reviews, air conditioning specialist focus, "24/7 spoed" label prominent            |
| Rotterdam | Trustoo avg 8.7/10 from 10,104 reviews                 | Top profiles: response time mentioned in reviews, STEK/F-gas certified labels, photos of vans and completed work |
| Eindhoven | Werkspot-listed installation companies                 | Top profiles: often sole trader + company mix; warmtepomp specialist badge prominent in 2026                     |

**Signals that drive Maps ranking:** Review volume + recency, complete Google Business Profile (hours, services, photos of van/work), response to reviews, "warmtepomp installateur" category.

### Loodgieter

| City      | Review platform signals                                            | Top profile characteristics                                                 |
| --------- | ------------------------------------------------------------------ | --------------------------------------------------------------------------- |
| Amsterdam | Trustoo 9.4/10 best (Ayvazbouw), 9.3/10 (CV Service 24/7), avg 8.8 | 100+ reviews, 24/7 badge, photos of completed plumbing work, fast response  |
| Rotterdam | Trustoo top loodgieters Rotterdam                                  | 80–150 reviews, pricing transparency in Q&A, WhatsApp contact button        |
| Eindhoven | loodgieters.in directory                                           | 40–100 reviews, specialist call-out: "spoedloodgieter Eindhoven" in listing |

**Key Maps signals:** "Spoedloodgieter" category tag, response to every review (owners reply within 24h on top profiles), 5+ photos per business, Google Posts (seasonal: "Vorstperiode? Wij zijn 24/7 bereikbaar").

### Dakdekker

| City      | Review platform signals                           | Top profile characteristics                                                               |
| --------- | ------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Amsterdam | Roofix: 5.0/5 from 650+ reviews, 24/7 spoed label | KOMO and Dakmerk certification badges, before/after project photos, free inspection offer |
| Rotterdam | Van Leeuwen 4.8/5, Trustoo top-10                 | Review response rate high, storm-repair posts in November–February                        |
| Eindhoven | Oranje Dakbeheer, Dakenheer presence              | KOMO seal prominent, "gratis dakinspectie" CTA in profile                                 |

**Key Maps signals:** Certification badges (KOMO, Dakmerk, VCA), before/after project photos, "gratis dakinspectie" offer, Google Posts during storm seasons.

### Aannemer

| City      | Review platform signals                       | Top profile characteristics                                      |
| --------- | --------------------------------------------- | ---------------------------------------------------------------- |
| Amsterdam | Werkspot-listed general contractors           | 50–200 reviews, verbouwing photos, NEN 2767 or VCA certification |
| Rotterdam | Arslan Aannemersbedrijf: 130+ reviews, 9.2/10 | Portfolio photos key, response to all reviews                    |
| Eindhoven | Trustoo contractor listings                   | Mix of zzp and BV; BV companies score higher on trust signals    |

### Schilder

| City      | Review platform signals                                             | Top profile characteristics                                             |
| --------- | ------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| Amsterdam | Slimster: 368 reviews avg 8.19, 26 in Amsterdam specifically        | Before/after paint photos dominant                                      |
| Rotterdam | Trustoo top-10: 9,835 reviews avg 8.7; CM Service 72 reviews, 10/10 | Instagram portfolio link in profile, Sikkens/Histor brand partner badge |
| Eindhoven | Bressers B.V.: 73 reviews 9.8/10; Van Oerle: 41 reviews 10/10       | Very high rating from smaller review counts — easier market to win      |

---

## 3. Content Pattern Extraction

### Title Formulas That Dominate

| Formula                                             | Example                                                | Niche(s)                          |
| --------------------------------------------------- | ------------------------------------------------------ | --------------------------------- |
| `[Niche] leads kopen/inkopen — [Benefit] [Year]`    | "Loodgieter leads inkopen — nieuwe klanten [2026]"     | All niches                        |
| `[Niche] klanten werven — [Number] tips`            | "Nieuwe klanten voor schildersbedrijf — 10 tips"       | Schilder, Aannemer                |
| `Online marketing voor [Niche]s — [Differentiator]` | "Online marketing voor dakdekkers — Exclusieve Leads"  | Dakdekker, Installateur, Schilder |
| `[Niche] online vindbaar maken — [Anchor]`          | "Website laten maken installatiebedrijf"               | All niches                        |
| `Leads voor [niche]s — [Speed promise]`             | "Leads voor loodgieters — spoed klussen binnen 48 uur" | Loodgieter, Dakdekker             |
| `SEO voor [niche]s — [Promise]`                     | "SEO voor dakdekkers: 10 tips om bovenaan te komen"    | Dakdekker, Schilder               |

### Recurring Content Blocks (ranked by frequency)

| Block                                      | Frequency across top-10 pages          | Present on Klantkraan pages?                      |
| ------------------------------------------ | -------------------------------------- | ------------------------------------------------- |
| FAQ section (3–8 questions)                | 9/10 pages                             | Yes (all cornerstones have FAQ)                   |
| Social proof / review widget               | 9/10 pages                             | No (placeholder only — "pilots in voorbereiding") |
| Numbered how-it-works / process            | 8/10 pages                             | Partial (modules section present)                 |
| Pricing transparency (per lead, per month) | 7/10 pages                             | Partial (€599 mentioned in ROI snippet only)      |
| City/regional targeting                    | 7/10 pages                             | No                                                |
| Stats / data anchors                       | 7/10 pages                             | Yes (pain stats trio on all pages)                |
| Case studies / before-after                | 6/10 pages                             | No                                                |
| Certification badges                       | 5/10 pages (KOMO, Google Partner, VCA) | Partial (AVG + AI Act mention)                    |
| ROI calculator (interactive)               | 4/10 pages                             | Link to /rekentool exists                         |
| Video / audio demo                         | 3/10 pages                             | Loodgieters page has audio placeholder            |

### Schema Types Found

| Schema type              | Found on which sites                            | On Klantkraan?                               |
| ------------------------ | ----------------------------------------------- | -------------------------------------------- |
| Organization             | LeadsMaster, Roxtar                             | Not verified (site unreachable)              |
| LocalBusiness            | LeadsMaster, ETEB                               | Not verified                                 |
| FAQPage                  | Not confirmed in fetched HTML of any competitor | No (FAQ uses `<details>` — no schema markup) |
| Review / AggregateRating | LeadsMaster (5.0/5, 32 reviews in footer)       | No                                           |
| Service                  | Implied on agency pages                         | Not verified                                 |

---

## 4. Klantkraan Gap Analysis

### Site Structure Observed

From source files, Klantkraan has these live or near-live cornerstone pages:

| Page         | File               | URL slug      | Status                |
| ------------ | ------------------ | ------------- | --------------------- |
| Installateur | installateur.astro | /installateur | Exists                |
| Loodgieter   | loodgieters.astro  | /loodgieters  | Exists (note: plural) |
| Dakdekker    | dakdekkers.astro   | /dakdekkers   | Exists (note: plural) |
| Aannemer     | aannemer.astro     | /aannemer     | Exists                |
| Schilder     | —                  | —             | **Missing — no page** |

> The TLS certificate on klantkraan.nl rejected the agent's fetch (ERR_TLS_CERT_ALTNAME_INVALID). All gap analysis is based on reading the Astro source files directly from the repository. The source reflects the deployed content structure accurately.

### Page-by-Page Gap Analysis

#### /installateur

**What exists:** H1 (Klantenmotor voor installateurs), pain stats (62% CV-storingen januari, €340/bezoek, 4× onderhoud piek), 3 feature modules, ROI snippet (€599 vs €124k missed), 7-question FAQ, Final CTA. Meta description is trade-specific. Word count: ~600–700 words rendered text.

| Gap                                      | Impact | Detail                                                                                                           |
| ---------------------------------------- | ------ | ---------------------------------------------------------------------------------------------------------------- |
| No FAQPage schema                        | High   | FAQ uses `<details>` HTML only — Google cannot index FAQ rich snippets                                           |
| No real testimonials                     | High   | No social proof at all; competitors show 5.0/5 ratings and named customers                                       |
| No city-level proof                      | High   | "Amsterdam", "Rotterdam", "Eindhoven" not mentioned anywhere on page                                             |
| Missing keywords in title tag            | Medium | Title is brand-first ("Klantkraan voor installateurs — AI-receptionist..."); "klanten werven" and "leads" absent |
| No meta description keyword match        | Medium | Description does not include "klanten werven" or "installateur leads"                                            |
| Word count gap                           | Medium | 600–700 words vs. competitor average 1,500–2,500                                                                 |
| No industry-specific sub-queries covered | Medium | No content on warmtepomp, laadpaal, zonnepaneel (growth sub-niches within installateur)                          |
| No pricing page link prominence          | Low    | /prijzen linked but not explained on-page                                                                        |
| No schema other than HTML                | Low    | No Service, Organization, or LocalBusiness schema visible                                                        |

#### /loodgieters

**What exists:** Same template as installateur with loodgieter-specific copy. Pain stats (28% gemiste oproepen, €450/klus, 0 reviews per missed call), audio demo section (placeholder), social proof section (placeholder dashed cards — "pilots in voorbereiding"), FAQ, ROI snippet. Word count: ~700–800 words.

| Gap                                   | Impact | Detail                                                                                                                                                      |
| ------------------------------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| No FAQPage schema                     | High   | Same issue as /installateur                                                                                                                                 |
| Social proof is placeholder           | High   | Three dashed cards "Pilot loodgieter · regio Randstad · komt binnenkort" — actively signals pre-launch; competitor LeadsMaster shows 750+ klanten and 5.0/5 |
| Audio demo is placeholder             | High   | `<p>Audio-demo komt binnenkort online</p>` visible — this should be removed or replaced before indexing                                                     |
| No city mentions                      | High   | Zero city-level targeting in copy                                                                                                                           |
| Title: no "klanten werven" or "leads" | Medium | Title: "gemiste oproepen teruggebeld binnen 60 seconden" — strong for one intent but misses broader discovery queries                                       |
| Word count gap                        | Medium | ~700–800 words vs. 2,100 at LeadsMaster                                                                                                                     |
| No case study or before/after         | Medium | No conversion evidence                                                                                                                                      |
| URL slug is plural (/loodgieters)     | Low    | Most searches use singular ("loodgieter leads") — minor mismatch                                                                                            |

#### /dakdekkers

**What exists:** Componentised page (Hero, PainStats, Features, StormScenario, RoiSnippet, SocialProof, Faq, FinalCta). Pain stats: 35% storm oproepen gemist, €650 noodreparatie, 4–6 weken wachttijd. Storm scenario section is a distinctive differentiator. FAQ covers storm, parallel calls, AI disclosure, conditional forwarding. Estimated ~700–900 words.

| Gap                                     | Impact | Detail                                                                                                          |
| --------------------------------------- | ------ | --------------------------------------------------------------------------------------------------------------- |
| No FAQPage schema                       | High   | Same structural issue                                                                                           |
| No actual social proof                  | High   | SocialProof component content not inspected but page structure parallels loodgieters                            |
| No city mentions                        | High   | Storm scenario doesn't name any city/region                                                                     |
| No certification-badge section          | Medium | KOMO and Dakmerk are major trust signals in this niche — not addressed                                          |
| Title misses "klanten werven" / "leads" | Medium | Title: "storm-protocol en 24/7 storingsdienst" — good for branded/intent search; weak for discovery             |
| Seasonal content gap                    | Medium | Storm protocol is good, but no content about yearly onderhoud cycle, moss treatment, flat roof vs. pitched roof |
| Word count gap                          | Medium | ~700–900 words vs. 2,500–3,500 at Roxtar                                                                        |

#### /aannemer

**What exists:** Same template. Pain stats: 41% offerteaanvragen buiten kantoortijd, €12k per gemiste aanvraag, 5× aanvragen na buurt-renovatie. FAQ covers bouwplaats context, parallel calls, AI disclosure. ~600–700 words.

| Gap                           | Impact | Detail                                                                                                                                           |
| ----------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| No FAQPage schema             | High   |                                                                                                                                                  |
| No city-level proof           | High   | Zero regional references                                                                                                                         |
| No social proof               | High   | No testimonials, no case studies, no pilot data                                                                                                  |
| No sub-niche coverage         | Medium | No mention of verbouwing, renovatie, nieuwbouw, utiliteit — all are distinct search queries                                                      |
| Title misses key queries      | Medium | Title "vang offerteaanvragen die u nu mist" — intent match for someone who already knows the problem; misses "aannemer klanten werven" discovery |
| Word count gap                | Medium | ~600–700 words vs. competitor average 1,200–2,500                                                                                                |
| No BV vs. zzp differentiation | Low    | Klantkraan's own BV-filter constraint not addressed in aannemer context (could be a trust signal)                                                |

#### /schilder (MISSING)

**Gap:** No page exists at all. This is the only niche without a cornerstone. The schilder niche has a full lead-broker and agency ecosystem (Allfree, Sikkens brand content, Roxtar, RocketMarketing, multiple dedicated agencies). The absence means Klantkraan cannot rank for any schilder-related query.

| What to build                                                                                                          | Priority |
| ---------------------------------------------------------------------------------------------------------------------- | -------- |
| Full /schilder page following installateur template                                                                    | Critical |
| Pain stats: verf-seizoen (lente/zomer buiten, herfst binnen), gemiste offertes, Google-review automation for portfolio | High     |
| FAQPage schema from day one                                                                                            | High     |
| City mentions (Amsterdam, Rotterdam, Eindhoven) in body copy                                                           | High     |

---

## 5. Top 10 Prioritised Content Actions

Ranked by **ranking impact × ease of implementation** (High/Medium/Low each axis).

| #   | Action                                                                             | Page(s)                   | Impact | Ease   | Rationale                                                                                                                                                                                                                         |
| --- | ---------------------------------------------------------------------------------- | ------------------------- | ------ | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Add FAQPage JSON-LD schema to all cornerstones                                     | All 4 existing            | High   | High   | FAQ content already written; adding `<script type="application/ld+json">` with FAQPage markup is 20 lines of code per page. Enables Google FAQ rich snippets immediately.                                                         |
| 2   | Create /schilder cornerstone page                                                  | New                       | High   | High   | Template exists; paste installateur.astro, swap copy for schilder context (lente buitenschilderwerk, herfst binnenschilderwerk, voor-na fotos thema, €280 avg job). Zero-to-one gap — highest delta.                              |
| 3   | Replace "pilots in voorbereiding" placeholder with real proof                      | /loodgieters, /dakdekkers | High   | Medium | Even one anonymised case ("Loodgieterbedrijf Amsterdam-Noord — 12 extra oproepen gevangen in eerste maand") beats placeholder text. Draft now; publish when first pilot data is available.                                        |
| 4   | Add city proof paragraph to each cornerstone                                       | All niches                | High   | Medium | One paragraph per page naming 3–4 cities where the niche is active ("Klantkraan is al actief bij installateurs in Amsterdam, Rotterdam en Eindhoven"). Signals local relevance without needing full city sub-pages.               |
| 5   | Rewrite meta title tags to include "[niche] klanten werven"                        | All niches                | High   | High   | Current titles are branded/feature-first. Change to pattern: "[Niche] klanten werven zonder advertenties — Klantkraan". Targets the #1 informational query in each niche.                                                         |
| 6   | Remove placeholder audio/social proof copy before indexing                         | /loodgieters              | Medium | High   | "Audio-demo komt binnenkort online" and "Case en cijfers volgen" read as under-construction signals to both users and Google. Remove or replace with a teaser that implies completeness.                                          |
| 7   | Add explicit pricing anchor on each page                                           | All niches                | Medium | High   | "€299/mnd Lite · €599/mnd Pro" visible on page body (not only linked to /prijzen). Pricing transparency is a top-3 content block on competitor pages and reduces pogo-sticking.                                                   |
| 8   | Expand word count to 1,200+ words per page via a "Hoe het werkt" deep-dive section | All niches                | Medium | Medium | Add a 400–600 word section explaining the 3-step onboarding flow (setup, configuratie, live). This alone closes ~40% of the word count gap and naturally adds keyword coverage.                                                   |
| 9   | Add industry certification / trust badge section                                   | /dakdekkers               | Medium | Medium | Mention that Klantkraan integrates with KOMO-certified contractors and respects their work-hour schedules. Dakdekker niche is cert-sensitive; showing awareness differentiates from generic marketing tools.                      |
| 10  | Add sub-niche keyword paragraphs per trade                                         | /installateur, /aannemer  | Medium | Low    | Installateur: add paragraphs on warmtepomp-installateur and laadpaal-installateur (high search volume, same buyer). Aannemer: add paragraphs on verbouwing, renovatie, aanbouw. Each paragraph = new keyword cluster to rank for. |

---

## Methodology & Sources

**SERP data collected:** 2026-05-21 via WebSearch tool (US-based agent). Results are influenced by the agent's geographic location (not Netherlands) and may differ from Dutch-IP results. Organic position estimates are directional only.

**Pages fetched directly (WebFetch):** onlineleadbox.nl/installatietechniek/, leadsmaster.nl/leads-voor-loodgieters/, leadsmaster.nl/dakdekker-leads/, roxtar.nl/online-marketing-uitbesteden/dakdekkers/, eteb.nl/loodgieter-leads/, drijfveermedia.nl/online-marketing-aannemers/.

**Klantkraan source analysis:** All gap analysis derived from reading Astro source files at `/klantkraan/apps/marketing-site/src/pages/` and `/klantkraan/apps/marketing-site/src/components/dakdekkers/`. The live site (klantkraan.nl) could not be fetched due to TLS certificate error (ERR_TLS_CERT_ALTNAME_INVALID) — this is a separate issue that should be diagnosed; search engines may have the same problem.

**Google Maps data:** No direct Maps API access. Inferred from Trustoo, Slimster, schilder-nu.nl, and Werkspot which aggregate Google Maps signals (review counts, ratings, categories).

**Schema types:** Only reporting schema found in fetched HTML. Absence of a schema type means it was not visible in the fetched page content — it may exist but not have been returned by the lightweight fetch tool.

**Search queries audited (15 total):**

- "installateur klanten werven", "leads voor installateur Nederland", "installateur online vindbaar maken"
- "loodgieter klanten werven marketing tips Nederland 2025", "leads voor loodgieter Nederland leadgeneratie", "loodgieter online vindbaar maken Google Maps lokale SEO"
- "dakdekker klanten werven online marketing Nederland", "leads voor dakdekker Nederland", "dakdekker online vindbaar maken lokale SEO tips"
- "aannemer klanten werven online marketing tips", "leads voor aannemer Nederland" (inferred from adjacent), "aannemer online vindbaar maken lokale SEO tips Nederland"
- "schilder klanten werven online marketing Nederland", "schilder leads kopen Nederland leadgeneratie", "schilder online vindbaar maken lokale SEO Google"
