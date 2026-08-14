// Fact gate for a built client site: does dist/ say what client.yaml says?
//
//   CLIENT=<slug> pnpm build && CLIENT=<slug> pnpm check
//
// The Zod schema proves the config is well formed and squirrelscan proves the HTML is sane.
// Neither can catch the failure that actually costs a client money: a right-looking site
// carrying the wrong phone number, a leftover placeholder, a price, or a city page for a town
// the client does not serve. This script re-reads the yaml itself (deliberately not through
// src/lib/client.ts, so a bug in the loader cannot hide behind its own output) and asserts the
// rendered pages against it.
//
// Exit 0 = every check passed. Exit 1 = at least one failure, listed. Exit 2 = usage error.
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { parse } from 'yaml'

const APP_ROOT = fileURLToPath(new URL('..', import.meta.url))
const DIST = path.join(APP_ROOT, 'dist')

// Text that must never survive into a published page. Kept literal on purpose: a marker list
// with clever regexes is a list nobody trusts. "voorbeeld" is absent by design, the tracked
// fixtures are full of it.
const PLACEHOLDERS = [
  'PRIJS?',
  'TODO',
  'FIXME',
  'AANVULLEN',
  'INVULLEN',
  'XXXX',
  'Lorem ipsum',
  'undefined',
  'NaN',
  '[object Object]',
]

// Prices are never published on a client site (pilot rule). Catches "€ 95", "95 euro", "EUR 95".
const PRICE_RE = /(€\s*\d|(\d[\d.,]*)\s*(euro\b|EUR\b))/i

const failures = []
const notes = []
const fail = (msg) => failures.push(msg)

function plaatsSlug(plaats) {
  // Mirror of src/lib/format.ts plaatsSlug.
  return plaats
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
}

function htmlFiles(dir) {
  return fs
    .readdirSync(dir, { withFileTypes: true })
    .flatMap((e) =>
      e.isDirectory()
        ? htmlFiles(path.join(dir, e.name))
        : e.name.endsWith('.html')
          ? [path.join(dir, e.name)]
          : [],
    )
}

const slug = process.env.CLIENT
if (!slug) {
  console.error('[verify-site] CLIENT is not set. Usage: CLIENT=<slug> pnpm check')
  process.exit(2)
}
const yamlPath = path.join(APP_ROOT, 'clients', slug, 'client.yaml')
if (!fs.existsSync(yamlPath) || !fs.existsSync(DIST)) {
  console.error(`[verify-site] need both ${yamlPath} and a dist/ build. Run pnpm build first.`)
  process.exit(2)
}

const cfg = parse(fs.readFileSync(yamlPath, 'utf8'))
const { bedrijf } = cfg
const isPreview = cfg.modus === 'preview'
const pages = htmlFiles(DIST).map((file) => ({
  file: path.relative(DIST, file),
  html: fs.readFileSync(file, 'utf8'),
}))
if (pages.length === 0) fail('dist/ contains no HTML pages')

// Guard against checking one client's config against another client's build.
if (!pages.some((p) => p.html.includes(bedrijf.naam))) {
  console.error(
    `[verify-site] dist/ never mentions "${bedrijf.naam}": it was built for a different client. ` +
      `Run: CLIENT=${slug} pnpm build`,
  )
  process.exit(2)
}

const everyPage = (label, predicate) => {
  const bad = pages.filter((p) => !predicate(p.html)).map((p) => p.file)
  if (bad.length) fail(`${label}, missing on: ${bad.join(', ')}`)
}
const noPage = (label, predicate) => {
  const bad = pages.filter((p) => predicate(p.html)).map((p) => p.file)
  if (bad.length) fail(`${label}, found on: ${bad.join(', ')}`)
}
const collect = (re) => {
  const found = new Set()
  for (const p of pages) for (const m of p.html.matchAll(re)) found.add(m[1])
  return found
}
const sameSet = (label, actual, expected) => {
  const extra = [...actual].filter((v) => !expected.includes(v))
  const missing = expected.filter((v) => !actual.has(v))
  if (extra.length) fail(`${label}, unexpected: ${extra.join(', ')}`)
  if (missing.length) fail(`${label}, never rendered: ${missing.join(', ')}`)
}

// 1. The business facts, exactly as configured.
const telHref = `tel:${bedrijf.telefoon.replace(/ /g, '')}`
everyPage(`phone number "${bedrijf.telefoon}" on every page`, (h) => h.includes(bedrijf.telefoon))
sameSet('tel: links', collect(/href="(tel:[^"]*)"/g), [telHref])
sameSet(
  'mailto: links',
  collect(/href="(mailto:[^"]*)"/g),
  bedrijf.email ? [`mailto:${bedrijf.email}`] : [],
)
sameSet(
  'wa.me links',
  collect(/href="(https:\/\/wa\.me\/[^"?]*)/g),
  bedrijf.whatsapp ? [`https://wa.me/${bedrijf.whatsapp}`] : [],
)
everyPage(`business name "${bedrijf.naam}" on every page`, (h) => h.includes(bedrijf.naam))
for (const dienst of cfg.diensten) {
  if (!pages.some((p) => p.html.includes(dienst.naam))) fail(`dienst "${dienst.naam}" never rendered`)
}

// 2. City pages: exactly the configured werkgebied, no more.
const builtCities = fs.existsSync(path.join(DIST, 'werkgebied'))
  ? fs
      .readdirSync(path.join(DIST, 'werkgebied'), { withFileTypes: true })
      .filter((e) => e.isDirectory())
      .map((e) => e.name)
      .sort()
  : []
const wantedCities = bedrijf.werkgebied.map(plaatsSlug).sort()
if (builtCities.join(',') !== wantedCities.join(',')) {
  fail(`werkgebied pages [${builtCities}] do not match the config [${wantedCities}]`)
}

// 3. Legal identifiers: present on a live site, absent from a proposal.
for (const [label, value] of [
  ['KvK', bedrijf.kvk],
  ['btw-id', bedrijf.btw_id],
]) {
  if (isPreview) {
    if (value) fail(`${label} is set on a modus: preview config; a proposal must not carry one`)
  } else if (!value) {
    fail(`${label} missing from the config of a live site`)
  } else {
    everyPage(`${label} ${value} in the footer of every page`, (h) => h.includes(value))
  }
}

// 4. Never published, in either mode.
for (const marker of PLACEHOLDERS) {
  noPage(`placeholder "${marker}"`, (h) => h.includes(marker))
}
noPage('a price', (h) => PRICE_RE.test(h.replace(/<[^>]+>/g, ' ')))
noPage('review/aggregateRating structured data', (h) => /aggregateRating|"@type"\s*:\s*"Review"/.test(h))

// 5. Zero external requests: what keeps the site cookie-banner-free. A proposal additionally
// links to klantkraan.nl from its banner (a link is not a request, and it names the sender).
const allowedHosts = [...(cfg.domein ? [cfg.domein] : []), 'wa.me', ...(isPreview ? ['klantkraan.nl'] : [])]
const externals = new Set()
for (const p of pages) {
  for (const m of p.html.matchAll(/(?:href|src)="(https?:\/\/[^"]+)"/g)) {
    const host = new URL(m[1]).hostname.replace(/^www\./, '')
    if (!allowedHosts.includes(host) && !host.endsWith('.pages.dev')) externals.add(host)
  }
}
if (externals.size) fail(`external hosts (breaks the no-cookie-banner guarantee): ${[...externals].join(', ')}`)
noPage('executable JavaScript', (h) => /<script(?![^>]*type="application\/ld\+json")/.test(h))

// 6. Mode-specific publishing posture.
const robots = fs.existsSync(path.join(DIST, 'robots.txt'))
  ? fs.readFileSync(path.join(DIST, 'robots.txt'), 'utf8')
  : ''
const headers = fs.existsSync(path.join(DIST, '_headers'))
  ? fs.readFileSync(path.join(DIST, '_headers'), 'utf8')
  : ''
if (isPreview) {
  everyPage('noindex meta on every page', (h) => /name="robots" content="noindex/.test(h))
  everyPage('preview banner on every page', (h) => h.includes('Voorbeeld, nog niet online.'))
  noPage('LocalBusiness JSON-LD (must not appear on a proposal)', (h) => h.includes('ld+json'))
  if (!/Disallow:\s*\//.test(robots)) fail('robots.txt does not disallow crawling of a proposal')
  if (!/X-Robots-Tag:\s*noindex/.test(headers)) fail('_headers has no X-Robots-Tag: noindex')
  if (fs.existsSync(path.join(DIST, 'sitemap-index.xml'))) fail('a proposal must not ship a sitemap')
} else {
  noPage('noindex meta on a live site', (h) => /name="robots" content="noindex/.test(h))
  everyPage('LocalBusiness JSON-LD', (h) => h.includes('ld+json'))
  if (!fs.existsSync(path.join(DIST, 'sitemap-index.xml'))) fail('live site has no sitemap')
  if (!robots.includes(`https://${cfg.domein}/sitemap-index.xml`)) {
    fail(`robots.txt does not point at https://${cfg.domein}/sitemap-index.xml`)
  }
  everyPage(`canonical on https://${cfg.domein}`, (h) =>
    h.includes(`rel="canonical" href="https://${cfg.domein}`),
  )
}

// 7. Structural hygiene (the QA.md greps, so the whole battery is one command).
everyPage('exactly one <h1>', (h) => (h.match(/<h1[\s>]/g) || []).length === 1)
everyPage('a <title>', (h) => /<title>[^<]+<\/title>/.test(h))
everyPage('a meta description', (h) => /name="description" content="[^"]+"/.test(h))
everyPage('a viewport meta', (h) => h.includes('name="viewport"'))
for (const p of pages) {
  const m = p.html.match(/<script type="application\/ld\+json">(.*?)<\/script>/s)
  if (m) {
    try {
      JSON.parse(m[1])
    } catch (err) {
      fail(`${p.file}: JSON-LD does not parse (${err.message})`)
    }
  }
}

// 8. Things a human still has to look at, printed rather than asserted.
if (!bedrijf.email) notes.push('no e-mail address configured: the contact page is phone-only')
if (!fs.existsSync(path.join(APP_ROOT, 'clients', slug, 'fotos'))) {
  notes.push('no fotos/ dir: the site runs on the colour-block fallback')
}
if (!isPreview) notes.push('/voorwaarden/ is a generic placeholder: adapt it before go-live')

const mode = isPreview ? 'VOORSTEL (preview)' : 'LIVE'
if (failures.length) {
  console.error(`\n[verify-site] ${slug} (${mode}): ${failures.length} FAILURE(S) over ${pages.length} pages:\n`)
  for (const f of failures) console.error(`  ✗ ${f}`)
  console.error('')
  process.exit(1)
}
console.log(`[verify-site] ${slug} (${mode}): all checks passed over ${pages.length} pages.`)
for (const n of notes) console.log(`  · ${n}`)
