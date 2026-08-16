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

// The company name, so a heading is not accused of Title Case for containing it. "Waarom
// Voorbeeld Barbier" is sentence case around a proper noun, which is correct Dutch.
const yamlPad = path.join(APP_ROOT, 'clients', slug, 'client.yaml')
const naamWoorden = new Set(
  fs.existsSync(yamlPad)
    ? (parse(fs.readFileSync(yamlPad, 'utf8'))?.bedrijf?.naam ?? '')
        .split(/\s+/)
        .filter(Boolean)
        .map((w) => w.toLowerCase())
    : [],
)

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
  for (const m of tekst.matchAll(/\bvan\s+[^.:;]{3,45}\s+en\s+[^.:;]{3,45}\s+tot\s+[^.:;]{3,45}/gi)) {
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
  ]
  for (const re of VUL) {
    const m = tekst.match(re)
    if (m) meld('vulwoorden', file, m[0])
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
