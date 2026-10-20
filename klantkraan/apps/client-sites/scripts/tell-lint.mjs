#!/usr/bin/env node
// tell-lint.mjs -- the tells a site gives off on its own, without a sibling to compare to.
//
//   CLIENT=<slug> node scripts/tell-lint.mjs
//
// Sibling of scripts/copy-lint.sh, and node rather than bash for one reason: these rules
// count things (how many headings are three words, how many cards are in the last row, how
// many sections carry the same eyebrow) and grep cannot count siblings. copy-lint.sh keeps
// the source-level copy rules it already owns; this owns the rendered page.
//
// The rule set comes from the AI-tell taxonomy read for the 2026-08-16 plan -- designer
// primary sources, not SEO listicles -- filtered down to the tells THIS factory can actually
// produce. It deliberately does not carry rules for gradients, glassmorphism, purple, fake
// statistics, motion or <script>: the template cannot emit any of them and a lint rule that
// can never fire is noise that makes the ones that do fire easier to ignore.
//
// Per-page opt-out: none. If a rule is wrong, fix the rule -- a page-level escape hatch on a
// gate this small is how the gate stops meaning anything.

import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { parse } from 'yaml'

const APP_ROOT = fileURLToPath(new URL('..', import.meta.url))
const DIST = path.join(APP_ROOT, 'dist')

const slug = process.env.CLIENT ?? '(onbekend)'

const yamlPad = path.join(APP_ROOT, 'clients', slug, 'client.yaml')
const cfg = fs.existsSync(yamlPad) ? (parse(fs.readFileSync(yamlPad, 'utf8')) ?? {}) : {}
const bedrijf = cfg.bedrijf ?? {}

// The company name, so a heading is not accused of Title Case for containing it. "Waarom
// Voorbeeld Barbier" is sentence case around a proper noun, which is correct Dutch.
const naam = bedrijf.naam ?? ''
const naamWoorden = new Set(
  naam
    .split(/\s+/)
    .filter(Boolean)
    .map((w) => w.toLowerCase()),
)

// The second rule family needs three facts about the business, not just its name. A locatie
// business (kapper, tandarts, garage) is held to openingstijden and an address; a mobiel one
// is not, and applying the locatie rules to a loodgieter would be a gate that lies.
const bedrijfstype = bedrijf.bedrijfstype ?? 'mobiel'
const vak = (bedrijf.vak ?? '').toLowerCase()
const plaats = (bedrijf.adres?.plaats ?? '').toLowerCase()

function pagesOf(dir) {
  const out = []
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name)
    if (e.isDirectory()) out.push(...pagesOf(p))
    else if (e.name.endsWith('.html')) out.push(p)
  }
  return out
}

if (!fs.existsSync(DIST)) {
  console.error(`[tell-lint] no dist/. Run: CLIENT=${slug} pnpm build`)
  process.exit(2)
}
const pages = pagesOf(DIST).map((f) => ({
  file: path.relative(DIST, f),
  html: fs.readFileSync(f, 'utf8'),
}))

const bevindingen = []
const meld = (regel, file, wat) => bevindingen.push({ regel, file, wat })

const ontdoe = (s) =>
  s
    .replace(/<[^>]+>/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&#39;/g, "'")
    .replace(/&quot;/g, '"')
    .replace(/&nbsp;/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()

const hoofdVan = (html) => html.match(/<main[^>]*>([\s\S]*?)<\/main>/i)?.[1] ?? ''
const voetVan = (html) => html.match(/<footer[^>]*>([\s\S]*?)<\/footer>/i)?.[1] ?? ''
const koppenVan = (frag, tag) =>
  [...frag.matchAll(new RegExp(`<${tag}[^>]*>([\\s\\S]*?)</${tag}>`, 'gi'))]
    .map((m) => ontdoe(m[1]))
    .filter(Boolean)

for (const { file, html } of pages) {
  const main = hoofdVan(html)
  const tekst = ontdoe(main)
  const h2 = koppenVan(main, 'h2')
  const h3 = koppenVan(main, 'h3')

  // 1. drieslag -- the rule of three, the copy tell every detector regexes for. "Van A en B
  //    tot C" is a hardcoded tricolon in lib/toon.ts, and it also breaks as soon as a dienst
  //    name contains "en": "Van lekkage opsporen en verhelpen en ontstoppen tot ...".
  for (const m of tekst.matchAll(
    /\bvan\s+[^.:;]{3,45}\s+en\s+[^.:;]{3,45}\s+tot\s+[^.:;]{3,45}/gi,
  )) {
    meld('drieslag', file, m[0].slice(0, 90))
  }

  // 2. parallelle-koppen -- every section heading a short noun phrase of the same shape
  //    ("Onze diensten", "Werkgebied", "Waarom X"). Human pages mix a statement, a question
  //    and a label; a page where every heading is two words was filled in, not written.
  //    Homepage only: on /diensten/ the h2s ARE the dienst names and on /voorwaarden/ they
  //    are clause titles, both legitimately short nouns.
  const kort = h2.filter((k) => k.split(/\s+/).length <= 3)
  if (file === 'index.html' && h2.length >= 4 && kort.length / h2.length >= 0.75) {
    meld(
      'parallelle-koppen',
      file,
      `${kort.length} van ${h2.length} h2 zijn <=3 woorden: ${kort.slice(0, 4).join(' / ')}`,
    )
  }

  // 3. titelkast -- Title Case in a Dutch heading. Dutch uses sentence case; capitalising
  //    every word is an English habit that arrives with generated copy and reads instantly
  //    wrong to a Dutch reader.
  for (const k of [...h2, ...h3]) {
    const woorden = k
      .split(/\s+/)
      .filter((w) => /^[a-zA-Z]/.test(w) && !naamWoorden.has(w.toLowerCase()))
    if (woorden.length < 3) continue
    const hoofd = woorden.filter((w) => /^[A-Z]/.test(w))
    if (hoofd.length === woorden.length) meld('titelkast', file, k)
  }

  // 4. wenkbrauw -- the tracked uppercase label above a heading. One is a house gesture;
  //    on every section it is the badge-above-the-headline pattern the taxonomy scores
  //    highest, and here it is immune to all seven skin axes, so it never varies at all.
  const wenkbrauwen = [...main.matchAll(/tracking-\[0\.18em\]/g)].length
  if (wenkbrauwen > 1) {
    meld('wenkbrauw', file, `${wenkbrauwen} secties dragen dezelfde uppercase eyebrow`)
  }

  // 5. weesrij -- a three-column card grid with one card alone on the last row. A designer
  //    either fills the row or changes the column count; a generator ships whatever the
  //    array length was.
  if (/lg:grid-cols-3/.test(main) && h3.length >= 4 && h3.length % 3 === 1) {
    meld('weesrij', file, `${h3.length} kaarten in een 3-koloms raster laat er een alleen achter`)
  }

  // 6. vulwoorden -- claims that sound like evidence and are not. Every one of these was
  //    found on the lead-gen end of the real-site survey and on none of the good sites.
  const VUL = [
    /jarenlange ervaring/i,
    /kwaliteit staat voorop/i,
    /de beste van de (regio|omgeving)/i,
    /op maat gemaakte oplossing/i,
    /hoogwaardige kwaliteit/i,
    /uw betrouwbare partner/i,
    /wij ontzorgen u/i,
    // Added by T8, all observed on the lead-gen end of the 60-site survey and on none of the
    // good sites.
    /de klant staat bij ons centraal/i,
    /met oog voor detail/i,
    /scherpe prijzen/i,
    /snel en vakkundig/i,
    /vakmanschap sinds jaar en dag/i,
    /professioneel en betrouwbaar/i,
    /passie voor het vak/i,
    /denken graag met u mee/i,
  ]
  for (const re of VUL) {
    const m = tekst.match(re)
    if (m) meld('vulwoorden', file, m[0])
  }

  // Two of the survey's filler phrases are only filler when unbacked, so they are conditional
  // rather than banned: "24/7 bereikbaar" is a real claim if the page says when, and "geen
  // verrassingen achteraf" is a real claim if the page states a price.
  if (
    /24\/7 bereikbaar/i.test(tekst) &&
    !/\b\d{1,2}[:.]\d{2}\b|\b(avond|weekend|nacht|zondag)/i.test(tekst)
  ) {
    meld('vulwoorden', file, '"24/7 bereikbaar" zonder één tijdsaanduiding op de pagina')
  }
  if (/geen verrassingen achteraf/i.test(tekst) && !/€\s?\d|\d+\s?euro/i.test(tekst)) {
    meld('vulwoorden', file, '"geen verrassingen achteraf" zonder een prijs op de pagina')
  }

  // 7. offerte-dichtheid -- "vrijblijvende offerte" is the correct Dutch phrase and the
  //    template says it in the hero, the meta description and the slot. Said three times on
  //    one page it stops being an offer and becomes a template seam.
  const offertes = [...tekst.matchAll(/vrijblijvende? offerte/gi)].length
  if (offertes > 1) meld('offerte-dichtheid', file, `${offertes}x "vrijblijvende offerte"`)

  // 8. gedachtestreepje -- banned in customer copy (CLAUDE.md); copy-lint.sh catches it in
  //    source, this catches it after the drafter's text has been through the template.
  for (const m of tekst.matchAll(/[^\s]\s[—–]\s[^\s]/g)) {
    meld('gedachtestreepje', file, m[0])
  }

  // --- second rule family (T8) -----------------------------------------------------------
  //
  // Rules 1-8 ask "was this written by a machine". These ask "does this page do the job a
  // trade site is for", and the thresholds are measured rather than chosen: 60 trade sites in
  // research/trade-site-craft-2026-08-16.md (36 mechanically) against 16 award sites in
  // research/award-craft-2026-08-16.md. Where a number appears below, that file has the
  // population it came from.

  const h1 = koppenVan(main, 'h1')
  const voet = voetVan(html)
  const telLinks = [...html.matchAll(/<a[^>]+href="tel:[^"]*"[^>]*>([\s\S]*?)<\/a>/gi)]

  // 9. telefoon-ontbreekt -- no tel: link at all. 29% of the AWARD tier fails this, which is
  //    the study's most useful embarrassment: a beautiful site that hides the phone number is
  //    still a broken trade site. The template always renders one, so this is a regression
  //    guard against `indeling.weglaten` removing the section that carries it.
  if (!telLinks.length) meld('telefoon-ontbreekt', file, 'geen enkele tel:-link op de pagina')

  // 10. telefoon-te-laat -- the first tel: appears after the </h1>. The craft tier averages
  //     63% into the document before the number shows up; a trade customer with a leak reads
  //     the first screen and nothing else (NN/g: ~80% of viewing time above the fold).
  const eersteTel = html.search(/href="tel:/i)
  const eindeH1 = html.search(/<\/h1>/i)
  if (file === 'index.html' && eersteTel > -1 && eindeH1 > -1 && eersteTel > eindeH1) {
    const pct = Math.round((eersteTel / html.length) * 100)
    meld('telefoon-te-laat', file, `eerste tel: staat na de </h1>, op ${pct}% van het document`)
  }

  // 11. telefoon-onzichtbaar -- the page shows no phone number in readable text anywhere. The
  //     classic "designer replaced the number with an icon" defect: it still works on a phone
  //     and is invisible to everyone reading on a laptop, which is where a BV owner decides
  //     who to call. Judged over the page and not per link: a "Bel nu" button is a fine CTA as
  //     long as the number itself is legible somewhere, which is how the good sites do it.
  if (telLinks.length && !telLinks.some((m) => /\d/.test(ontdoe(m[1])))) {
    meld(
      'telefoon-onzichtbaar',
      file,
      `${telLinks.length} tel:-links en geen enkele toont het nummer: "${ontdoe(telLinks[0][1])}"`,
    )
  }

  // 12. telefoon-spam -- more than 12 tel: links on one page. mrloodgieteramsterdam.nl ships
  //     62. Past a dozen the number stops being a way to reach someone and becomes the page.
  if (telLinks.length > 12)
    meld('telefoon-spam', file, `${telLinks.length} tel:-links op één pagina`)

  // 13. telefoon-opmaak -- the visible number is unspaced (+31202102601). Observed on 4 NL
  //     sites. Dutch readers parse their own national grouping and stumble over a digit wall.
  for (const m of telLinks) {
    const zichtbaar = ontdoe(m[1])
    if (/(\+31|0)\d{8,}/.test(zichtbaar)) {
      meld('telefoon-opmaak', file, `nummer zonder groepering: "${zichtbaar}"`)
    }
  }

  // 14. kanaal-eenzaam -- a phone number and no second way in. 12 of 15 NL sites in the survey
  //     offer the phone alone; the good ones pair it with WhatsApp, an agenda or a form,
  //     because a share of customers will not call a stranger.
  const tweedeKanaal = /href="https:\/\/wa\.me|href="mailto:|<form|\/afspraak|\/contact/i.test(main)
  if (file === 'index.html' && telLinks.length && !tweedeKanaal) {
    meld('kanaal-eenzaam', file, 'telefoon zonder tweede kanaal (WhatsApp, afspraak of formulier)')
  }

  // 15. geen-h1 -- measured on 5 corpus sites. Nothing else on a page can stand in for it.
  if (!h1.length) meld('geen-h1', file, 'pagina zonder <h1>')

  // 16. h1-nietszeggend -- the H1 is <=2 words, or the company name and nothing else, or a
  //     word describing the page rather than the business ("Home", "Welkom"). The first two
  //     limbs are homepage-only: "Contact" is the correct H1 for /contact/ and
  //     "Privacyverklaring" for the privacy page, and a rule that calls those defects would
  //     train the founder to ignore the gate. "Home" is never right anywhere.
  for (const k of h1) {
    const woorden = k.split(/\s+/).filter(Boolean)
    if (/^(home|welkom|landing ?page)$/i.test(k.trim())) {
      meld('h1-nietszeggend', file, `h1 beschrijft de pagina, niet het bedrijf: "${k}"`)
    } else if (file !== 'index.html') {
      // subpage titles are allowed to be short nouns
    } else if (woorden.length <= 2) {
      meld('h1-nietszeggend', file, `h1 van ${woorden.length} woord(en): "${k}"`)
    } else if (naam && k.toLowerCase().trim() === naam.toLowerCase().trim()) {
      meld('h1-nietszeggend', file, `h1 is alleen de bedrijfsnaam: "${k}"`)
    }
    // 17. h1-te-lang -- over 12 words (reinert-bau.de ships 15). A headline nobody finishes.
    if (woorden.length > 12) meld('h1-te-lang', file, `h1 van ${woorden.length} woorden: "${k}"`)

    // 18. h1-plaatsnaam-stapel -- a bare "<vak> <plaats>" with no promise in it. The SEO-farm
    //     signature: 4 of 7 NL lead-gen sites, against the best headline in the whole corpus
    //     ("Lekkage? Vandaag nog opgelost."), which names neither vak nor plaats. Homepage
    //     only, because the population it was measured on is homepages: on /werkgebied/breda/
    //     the vak and the plaats ARE the subject of the page, and firing there would flag every
    //     city page of every site forever.
    //     "en omgeving" is stripped before counting: it names a service radius, not a promise,
    //     and leaving it in gave the rule a hole the factory's own default drove straight
    //     through ("Dakdekker in Nieuwegein en omgeving" was 5 words and passed).
    if (file === 'index.html' && vak && plaats) {
      const kern = k.toLowerCase().replace(/\s+en omgeving\b/, '')
      const kernWoorden = kern.split(/\s+/).filter(Boolean)
      if (kernWoorden.length <= 4 && kern.includes(vak) && kern.includes(plaats)) {
        meld('h1-plaatsnaam-stapel', file, `h1 is vak + plaats zonder belofte: "${k}"`)
      }
    }
  }

  // 19. openingstijden-alleen-footer -- locatie only. For a kapper or een garage the opening
  //     hours are the fact the visitor came for, and the factory renders them in the footer
  //     and nowhere else. A mobiel loodgieter is exempt: his availability is "spoed, ook 's
  //     avonds", not a table.
  if (bedrijfstype === 'locatie' && file === 'index.html') {
    const inVoet = /openingstijden|geopend|ma\s*[-–]\s*(vr|za)/i.test(ontdoe(voet))
    const inHoofd = /openingstijden|geopend|ma\s*[-–]\s*(vr|za)/i.test(tekst)
    if (inVoet && !inHoofd) {
      meld(
        'openingstijden-alleen-footer',
        file,
        'locatiebedrijf: openingstijden staan alleen in de voet',
      )
    }
  }

  // 20. adres-ontbreekt -- locatie only. A business someone has to walk into and no street on
  //     the page.
  if (bedrijfstype === 'locatie' && file === 'index.html') {
    const straat = bedrijf.adres?.straat
    if (straat && !ontdoe(html).toLowerCase().includes(straat.toLowerCase())) {
      meld('adres-ontbreekt', file, `locatiebedrijf: "${straat}" staat nergens op de pagina`)
    }
  }

  // 21. review-schema -- aggregateRating or Review in the JSON-LD. Already house policy (we
  //     ship curated quotes and link the live Google profile), and 5 of 7 NL lead-gen sites
  //     violate it. Now it is enforced rather than remembered.
  if (/"@type"\s*:\s*"(AggregateRating|Review)"|"aggregateRating"/i.test(html)) {
    meld('review-schema', file, 'aggregateRating of Review in de schema-markup')
  }

  // 22. stockfoto-cdn -- a hotlinked stock URL. Zero good sites in the survey had one, and the
  //     factory cuts its own renditions, so this only fires if someone pasted a URL into the
  //     yaml.
  for (const m of html.matchAll(
    /(unsplash|pexels|shutterstock|istockphoto|gettyimages|adobestock|freepik)\.com/gi,
  )) {
    meld('stockfoto-cdn', file, m[0])
  }

  // 23. alt-ontbreekt -- an <img> with no alt attribute (puetzconstruction.com ships 11). T5
  //     made Dutch alt text required in the manifest, so this guards that door from the
  //     template side.
  for (const m of html.matchAll(/<img\b(?![^>]*\balt=)[^>]*>/gi)) {
    meld('alt-ontbreekt', file, m[0].slice(0, 80))
  }

  // 24. derde-partij -- a request to a consent-triggering third party. The generated sites
  //     need no cookie banner, which is a real advantage over every measured competitor, and
  //     exactly one embed takes it away.
  for (const m of html.matchAll(
    /(googletagmanager|google-analytics|connect\.facebook\.net|trustindex|elfsight|youtube\.com\/embed|google\.com\/maps\/embed)/gi,
  )) {
    meld('derde-partij', file, m[0])
  }

  // 25. keurmerk-verlopen -- Sterkin, KvINL and UNETO-VNI have all merged or been renamed.
  //     Citing one dates the copy and, worse, names a scheme the client cannot be in.
  for (const m of tekst.matchAll(/\b(Sterkin|KvINL|UNETO-VNI)\b/gi)) {
    meld('keurmerk-verlopen', file, m[0])
  }

  // 26. erkend-onbepaald -- "erkend" with no named scheme behind it (5 of 7 NL lead-gen
  //     sites). Either say which register, or say something true instead.
  for (const m of tekst.matchAll(/\berkend\w*\s+(\w+)/gi)) {
    const volgend = m[1].toLowerCase()
    const SCHEMAS = [
      'sterkin',
      'kvinl',
      'vca',
      'bovag',
      'rdw',
      'kiwa',
      'komo',
      'techniek',
      'inscert',
    ]
    if (!SCHEMAS.includes(volgend)) meld('erkend-onbepaald', file, m[0])
  }

  // 27. paginagewicht -- homepage HTML over 150KB. The best site measured
  //     (luecke-dachfassade.de) ships 39KB; fixedtoday.com.au ships 555KB.
  if (file === 'index.html' && html.length > 150_000) {
    meld('paginagewicht', file, `${Math.round(html.length / 1024)}KB HTML op de homepage`)
  }

  // 28. register-gemengd -- "u" and "je" both over 15% of the address forms on one page.
  //     cvloodgieter.nl sits at 55/45 and reads like two people wrote it. The register is a
  //     decision per client (`teksten:`), so it has to hold across the whole page.
  const uVormen = [...tekst.matchAll(/\b(u|uw)\b/gi)].length
  const jeVormen = [...tekst.matchAll(/\b(je|jij|jouw|jullie)\b/gi)].length
  const totaal = uVormen + jeVormen
  if (totaal >= 10) {
    const min = Math.min(uVormen, jeVormen) / totaal
    if (min > 0.15) meld('register-gemengd', file, `${uVormen}x u-vorm tegen ${jeVormen}x je-vorm`)
  }

  // 29. plaatsnaam-dichtheid -- one plaatsnaam more than 8 times on a page, or a homepage over
  //     2,500 words. Catches the 6,226-word city-permutation wall the SEO end of the survey
  //     ships. The city pages are exempt on the count: naming the city is their job.
  if (plaats && !/^[a-z-]+\/index\.html$/.test(file)) {
    const n = [...tekst.matchAll(new RegExp(`\\b${plaats}\\b`, 'gi'))].length
    if (n > 8) meld('plaatsnaam-dichtheid', file, `"${plaats}" ${n}x op één pagina`)
  }
  const woordenTotaal = tekst.split(/\s+/).filter(Boolean).length
  if (file === 'index.html' && woordenTotaal > 2500) {
    meld('plaatsnaam-dichtheid', file, `${woordenTotaal} woorden op de homepage`)
  }
}

// --- the CSS side (T8) --------------------------------------------------------------------
//
// Three tells that live in the stylesheet rather than the markup, all from the 16-award /
// 11-trade measurement in research/award-craft-2026-08-16.md. They are counted once over the
// built CSS, not per page: one stylesheet serves the whole site.

const cssBestanden = fs.existsSync(path.join(DIST, '_astro'))
  ? fs
      .readdirSync(path.join(DIST, '_astro'))
      .filter((f) => f.endsWith('.css'))
      .map((f) => ({
        file: path.join('_astro', f),
        css: fs.readFileSync(path.join(DIST, '_astro', f), 'utf8'),
      }))
  : []

for (const { file, css } of cssBestanden) {
  // 30. themabreedte -- a main container of exactly 1140, 1170, 1200 or 1320px. The single
  //     most reliable tell in the whole study: 11 of 11 trade sites, 3 of 16 award sites, and
  //     every one of those four numbers is a Bootstrap, Elementor or Divi default. A site
  //     whose measure is one of them was installed, not laid out.
  for (const m of css.matchAll(/max-width:\s*(1140|1170|1200|1320)px/g)) {
    meld('themabreedte', file, `${m[0]} is een Bootstrap/Elementor-default`)
  }

  // 31. kleurenspreiding -- distinct hex values. The award sites that read most expensive ship
  //     4 to 15; the median award site 30.5, the median trade site 108. Gate at the study's
  //     own numbers: over 60 is a warning, over 100 fails. Counted normalised, so #FFF and
  //     #ffffff are one colour.
  const hexen = new Set(
    [...css.matchAll(/#([0-9a-f]{3}|[0-9a-f]{6})\b/gi)].map((m) => {
      const h = m[1].toLowerCase()
      return h.length === 3
        ? h
            .split('')
            .map((c) => c + c)
            .join('')
        : h
    }),
  )
  if (hexen.size > 60) {
    meld(
      'kleurenspreiding',
      file,
      `${hexen.size} unieke hex-kleuren (award-mediaan 30,5; >60 waarschuwing, >100 fout)`,
    )
  }

  // 32. tracking-positief -- positive letter-spacing on display type. Award display type is
  //     optically tightened (-0.012em to -0.03em, median 2 declarations); theme headings track
  //     it out (reliablepaving.com: 0.1em on the H1, median 0 negative declarations). The
  //     uppercase eyebrow is the one legitimate positive tracking on the page and rule 4
  //     already owns it, so this only looks at rules that also set a size of 32px or more.
  for (const m of css.matchAll(/\{[^{}]*\}/g)) {
    const regel = m[0]
    const spacing = regel.match(/letter-spacing:\s*(-?[\d.]+)(px|em|rem)/)
    if (!spacing || Number(spacing[1]) <= 0) continue
    const grootte = regel.match(/font-size:\s*(?:clamp\([^)]*?,\s*)?([\d.]+)(px|rem)/)
    if (!grootte) continue
    const px = grootte[2] === 'rem' ? Number(grootte[1]) * 16 : Number(grootte[1])
    if (px >= 32)
      meld('tracking-positief', file, `letter-spacing ${spacing[0]} op ${Math.round(px)}px`)
  }
}

// --- report ------------------------------------------------------------------------------

const perRegel = new Map()
for (const b of bevindingen) perRegel.set(b.regel, [...(perRegel.get(b.regel) ?? []), b])

console.log(`[tell-lint] ${slug}: ${pages.length} pagina's, ${bevindingen.length} bevindingen.`)
for (const [regel, lijst] of [...perRegel].sort((a, b) => b[1].length - a[1].length)) {
  const paginas = new Set(lijst.map((b) => b.file))
  console.log(`  X ${regel} (${lijst.length}x op ${paginas.size} pagina's)`)
  for (const b of lijst.slice(0, 3)) console.log(`      ${b.file}: ${b.wat}`)
  if (lijst.length > 3) console.log(`      ... en ${lijst.length - 3} meer`)
}

if (bevindingen.length) process.exit(1)
console.log('[tell-lint] schoon.')
