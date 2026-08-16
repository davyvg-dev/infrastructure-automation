// Data layer for the vertical pSEO pages (TODO §M step 2).
// Stats policy is law: research/first-client-market-research-2026-08-10.md §1.
// Every stat here is approved for customer copy; anything not in this file
// (and everything in bannedClaims) stays out of pages and drafter prompts.
// Pricing peildata: competitor-pricing.md = mei 2026,
// website-market-pricing-2026-08-12.md = 2026-08-12.

export interface ApprovedStat {
  id: string
  /** Exact Dutch wording cleared for customer copy. */
  claim: string
  bron: string
  bronUrl?: string
  /** As-of date of the underlying data, when known. */
  datum?: string
  /** Usage restriction the page MUST respect (e.g. "als internationaal labelen"). */
  voorbehoud?: string
}

export const approvedStats: Record<string, ApprovedStat> = {
  'eerste-reageerder-78': {
    id: 'eerste-reageerder-78',
    claim: '78% van de klanten koopt bij het bedrijf dat als eerste reageert.',
    bron: 'MIT/InsideSales, via Harvard Business Review',
    bronUrl: 'https://hbr.org/2011/03/the-short-life-of-online-sales-leads',
    datum: '2011',
  },
  'kcm-terugbelbeloftes': {
    id: 'kcm-terugbelbeloftes',
    claim: 'Bijna de helft van de terugbelbeloftes wordt nooit nagekomen.',
    bron: 'KCM Group, mystery-call onderzoek onder 10.000 gesprekken, via DIRECT Klantcontact',
  },
  'kcm-geen-contact': {
    id: 'kcm-geen-contact',
    claim: '1 op de 12 bellers krijgt helemaal geen contact met het bedrijf dat hij belt.',
    bron: 'KCM Group, mystery-call onderzoek onder 10.000 gesprekken, via DIRECT Klantcontact',
    voorbehoud: 'Gemiddelde over alle branches; niet presenteren als vakmensen-cijfer.',
  },
  'invoca-gemiste-calls-27': {
    id: 'invoca-gemiste-calls-27',
    claim:
      'Ongeveer 27% van de inkomende telefoontjes naar klusbedrijven wordt gemist (Amerikaanse data).',
    bron: 'Invoca, analyse van 60 miljoen gesprekken in de VS',
    voorbehoud: 'Altijd expliciet als internationaal/VS-cijfer labelen.',
  },
  'google-ads-ban': {
    id: 'google-ads-ban',
    claim:
      'Google verbiedt in Nederland zoekadvertenties voor slotenmakers (sinds 2021) en voor loodgieters- en ontstoppingsdiensten (sinds 22 februari 2024).',
    bron: 'Google Ads-beleid voor lokale dienstverleners',
    datum: '2024-02-22',
  },
  'techniek-nl-personeelstekort': {
    id: 'techniek-nl-personeelstekort',
    claim: '67 tot 68% van de technische bedrijven meldt een personeelstekort.',
    bron: 'Techniek Nederland',
  },
  'techniek-nl-vacatures': {
    id: 'techniek-nl-vacatures',
    claim: 'Eind 2024 stonden er 75.600 technische vacatures open.',
    bron: 'Techniek Nederland',
    datum: '2024',
  },
  'techniek-nl-vakmensen-nodig': {
    id: 'techniek-nl-vakmensen-nodig',
    claim: 'Nederland heeft de komende 5 jaar 121.000 extra vakmensen nodig.',
    bron: 'Techniek Nederland',
  },
  'werkspot-leadprijs': {
    id: 'werkspot-leadprijs',
    claim: 'Via Werkspot betaalt u €3 tot €75 per lead, afhankelijk van de klusgrootte.',
    bron: 'Werkspot-tarieven, geverifieerd mei 2026',
    datum: '2026-05',
  },
  'werkspot-per-gewonnen-klus': {
    id: 'werkspot-per-gewonnen-klus',
    claim: 'Gemiddeld kost een via Werkspot gewonnen klus zo’n €208 aan leadkosten.',
    bron: 'Adaptoo, analyse van Werkspot-kosten',
    bronUrl: 'https://adaptoo.nl/blog/werkspot-kosten',
    voorbehoud:
      'Schatting van Adaptoo, geen door Werkspot gepubliceerd cijfer; altijd attribueren.',
  },
  'leadplatform-gedeelde-leads': {
    id: 'leadplatform-gedeelde-leads',
    claim: 'Leadplatforms sturen dezelfde klusaanvraag door naar 3 tot 6 concurrenten tegelijk.',
    bron: 'Klantkraan-analyse van 9 NL klusplatforms, mei 2026',
    datum: '2026-05',
  },
  'ai-transparantie-plicht': {
    id: 'ai-transparantie-plicht',
    claim:
      'Sinds 2 augustus 2026 is AI-transparantie verplicht: een klant moet horen dat hij met een digitale assistent praat (art. 50 AI-verordening).',
    bron: 'EU AI-verordening, artikel 50',
    datum: '2026-08-02',
  },
}

// Vendor folklore that every concurrent doorvertelt en die hier nooit in copy
// mag: onbewezen of stokoud. De drafter-prompt (§M step 3) en de verify-pass
// controleren hierop; de patterns zijn substring-matchers over gegenereerde copy.
export const bannedClaims: { omschrijving: string; patterns: string[] }[] = [
  {
    omschrijving: '"62% van de oproepen onbeantwoord" (2016, n=85)',
    patterns: ['62%', '62 procent'],
  },
  {
    omschrijving: '"85% belt nooit terug" / "85% spreekt geen voicemail in"',
    patterns: ['85%', '85 procent'],
  },
  {
    omschrijving: '"20% spreekt voicemail in"',
    patterns: ['20% spreekt', 'spreekt voicemail in'],
  },
  {
    omschrijving: '"belt 3 nummers in 5 minuten"',
    patterns: ['3 nummers', 'drie nummers'],
  },
]

// Euro-math per vertical. Framing rule (research §1): noem de formule
// ("X gemiste oproepen × €Y per klus") en laat de lezer X invullen; nooit een
// verzonnen verliespercentage. herkomst 'onderzoek' = NL-sourced job values uit
// het marktonderzoek §1; 'site-aanname' = het gemiddelde dat de cornerstones en
// [stad]-pagina's al publiek gebruiken (src/data/niches.ts jobValueEur).
// Verticals ZONDER jobValueEur (elektricien, installateur, sportscholen) hebben
// geen gepubliceerde of onderzochte kluswaarde: copy gebruikt daar de formule
// zonder ingevuld voorbeeldbedrag, of laat de lezer zelf invullen.
export interface VerticalMath {
  vertical: string
  /** Gemiddelde kluswaarde in euro's die copy als voorbeeld mag noemen. */
  jobValueEur?: number
  /** Bandbreedte in woorden, voor genuanceerde copy. */
  bandbreedte?: string
  herkomst: 'onderzoek' | 'site-aanname' | 'geen'
  toelichting?: string
}

export const euroMath: Record<string, VerticalMath> = {
  loodgieters: {
    vertical: 'loodgieters',
    jobValueEur: 250,
    bandbreedte:
      'spoedklussen €150 tot €400; rioolontstopping €90 tot €250, met camera €270 tot €480, spoedtoeslag +60 tot 100%',
    herkomst: 'onderzoek',
    toelichting:
      'NL-sourced job values, research §1: één gemiste klus per week = €600 tot €1.600 per maand. NB: de cornerstone gebruikt €450 als gemiddelde kluswaarde (niches.ts); niet mengen op één pagina.',
  },
  dakdekkers: {
    vertical: 'dakdekkers',
    jobValueEur: 600,
    bandbreedte: 'inspectie- en lekkage-spoedklussen',
    herkomst: 'site-aanname',
  },
  aannemer: {
    vertical: 'aannemer',
    jobValueEur: 5000,
    bandbreedte: 'verbouwings- en dakkapelklussen; één gemiste aanvraag is al groot',
    herkomst: 'site-aanname',
  },
  schilder: {
    vertical: 'schilder',
    jobValueEur: 2500,
    bandbreedte: 'binnen-schilderklus huis',
    herkomst: 'site-aanname',
  },
  elektricien: { vertical: 'elektricien', herkomst: 'geen' },
  installateur: { vertical: 'installateur', herkomst: 'geen' },
  sportscholen: {
    vertical: 'sportscholen',
    herkomst: 'geen',
    toelichting: 'Reken in lidmaatschapswaarde per jaar; laat de lezer het eigen tarief invullen.',
  },
}

// Concurrenten- en marktprijzen voor vergelijkingspagina's. Alleen publiek
// geverifieerde cijfers; "prijs op aanvraag" blijft "niet gepubliceerd" en
// wordt nooit ingevuld. peildatum = wanneer geverifieerd.
export interface CompetitorRow {
  naam: string
  categorie:
    | 'ai-telefonist'
    | 'website-bundel'
    | 'leadplatform'
    | 'marketingbureau'
    | 'websitebouwer'
    | 'antwoordservice'
  product: string
  prijs: string
  doelgroep?: string
  opmerking?: string
  peildatum: string
}

export const marktprijzen: CompetitorRow[] = [
  {
    naam: 'STUDIOLEE',
    categorie: 'website-bundel',
    product: 'Vakmensen-website (abonnement) + AI-telefonist',
    prijs: 'website vanaf €79/mnd, AI-telefonist vanaf €79/mnd plus €0,25 tot €0,80 per minuut',
    doelgroep: 'loodgieters',
    opmerking: 'oplevering 7 tot 14 dagen; "vanaf"-prijs, hogere staffels niet geadverteerd',
    peildatum: '2026-08-12',
  },
  {
    naam: 'LoodgieterAI',
    categorie: 'website-bundel',
    product: 'Alles-in-één: website, voice-AI, chatbot, reviews',
    prijs: 'staffels €79, €297 en €497/mnd',
    doelgroep: 'loodgieters',
    peildatum: '2026-08-12',
  },
  {
    naam: 'Voicelabs (Robin)',
    categorie: 'ai-telefonist',
    product: 'Nederlandstalige AI-telefonist',
    prijs: 'vanaf €299/mnd voor 1.000 minuten',
    doelgroep: 'zorg, vastgoed, mkb',
    peildatum: '2026-05',
  },
  {
    naam: 'InstallatieTelefoniste.nl',
    categorie: 'ai-telefonist',
    product: 'AI-telefoonservice voor installateurs',
    prijs: '€0,25 per minuut, setup vanaf €250',
    doelgroep: 'installateurs',
    peildatum: '2026-05',
  },
  {
    naam: 'Klusio',
    categorie: 'marketingbureau',
    product: 'SEO + content + AI-chatbot + voice-telefonist',
    prijs: '€199, €399 of €699/mnd, maandelijks opzegbaar', // copy-lint-ok: concurrentprijs, niet ons tarief
    doelgroep: 'zzp-vakmensen',
    peildatum: '2026-05',
  },
  {
    naam: 'LeadLead',
    categorie: 'marketingbureau',
    product: 'Website + hosting + SEO + Google Ads + CRM',
    prijs: 'vanaf €699/mnd', // copy-lint-ok: concurrentprijs, niet ons tarief
    doelgroep: 'loodgieters, installateurs, aannemers',
    peildatum: '2026-05',
  },
  {
    naam: 'Marketingbureaus voor vakmensen (bandbreedte)',
    categorie: 'marketingbureau',
    product: 'SEO/ads-trajecten',
    prijs: '€699 tot €3.500+/mnd, meestal zonder leadgarantie', // copy-lint-ok: marktprijs, niet ons tarief
    peildatum: '2026-05',
  },
  {
    naam: 'Werkspot',
    categorie: 'leadplatform',
    product: 'Gedeelde klusaanvragen',
    prijs: '€3 tot €75 per lead; abonnement €29,95 of €49,95/mnd',
    opmerking:
      'zelfde lead naar meerdere bedrijven; ±€208 leadkosten per gewonnen klus (schatting Adaptoo)',
    peildatum: '2026-05',
  },
  {
    naam: 'Homedeal',
    categorie: 'leadplatform',
    product: 'Gedeelde klusaanvragen',
    prijs:
      '€40 tot €80 per lead, gedeeld met 3 tot 5 concurrenten, plus verplicht abonnement (prijs niet gepubliceerd)',
    peildatum: '2026-05',
  },
  {
    naam: 'Slimster',
    categorie: 'leadplatform',
    product: 'Klusaanvragen zonder abonnement',
    prijs: '€15 tot €40 per lead',
    doelgroep: 'duurzaam/warmtepomp',
    peildatum: '2026-05',
  },
  {
    naam: 'Webdesignbureau (mkb-site, gemiddeld)',
    categorie: 'websitebouwer',
    product: 'Maatwerksite 5 tot 8 pagina’s',
    prijs: '€1.500 tot €7.500 eenmalig, plus €30 tot €100/mnd onderhoud, oplevering 4 tot 8 weken',
    peildatum: '2026-08-12',
  },
  {
    naam: 'Vaste-prijs websitebouwers',
    categorie: 'websitebouwer',
    product: 'Standaardsite binnen een week',
    prijs: '€175 tot €749 eenmalig, onderhoud €20 tot €35/mnd (o.a. Goedgestart, Tijdvooreensite)',
    peildatum: '2026-08-12',
  },
  {
    naam: 'Doe-het-zelf sitebouwers',
    categorie: 'websitebouwer',
    product: 'JouwWeb, Webador, Wix',
    prijs: 'vanaf €6 tot €20/mnd, eigen werk',
    opmerking: 'het echte prijsanker in het hoofd van een vakman',
    peildatum: '2026-08-12',
  },
]

// Eigen prijzen, zodat vergelijkingspagina's nooit een verouderd bedrag
// hardcoden. Bron: project_pricing_tiers + website-market-pricing §8.
export const eigenPrijzen = {
  chatPerMaand: 299,
  compleetPerMaand: 499,
  websiteEenmalig: 1000,
  websiteOnderhoudPerMaand: 39,
  websiteBundelEenmalig: 749,
} as const

// De pagina-inventaris (welke ~45 pagina's er komen) leeft in
// pseo-inventory.json: JSON zodat Astro hem importeert voor linkblokken EN de
// server-side drafter (growth-engine, §M step 3) de gersyncte kopie leest.
// dataBlocks-refs: "stat:<id>" → approvedStats, "euromath:<vertical>" →
// euroMath, "markt:<categorie>" → marktprijzen-rijen, "prijzen:eigen".
export interface InventoryPage {
  slug: string
  vertical: string
  type: 'probleem' | 'vergelijking' | 'hub'
  targetKeyword: string
  /** Geschat NL-zoekvolume per maand, alleen waar seo-keywords.md het geeft. */
  zoekvolume?: string
  /** Contentcluster uit research/seo-strategy.md: D → A → B → C is de bouwvolgorde. */
  cluster: 'D' | 'A' | 'B' | 'C'
  angle: string
  dataBlocks: string[]
}

export interface Inventory {
  version: number
  bijgewerkt: string
  verboden: string
  pages: InventoryPage[]
}

import inventoryJson from './pseo-inventory.json'
export const inventory: Inventory = inventoryJson as Inventory
