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

function filesWithExt(dir, ext) {
  return fs
    .readdirSync(dir, { withFileTypes: true })
    .flatMap((e) =>
      e.isDirectory()
        ? filesWithExt(path.join(dir, e.name), ext)
        : e.name.endsWith(ext)
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
const pages = filesWithExt(DIST, '.html').map((file) => ({
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

// 2. City pages: exactly the configured werkgebied, no more. Counted from the built HTML rather
// than from directory names, because a werkgebied/<plaats>/ that lost its index.html still looks
// like a city page to readdir while every link to it 404s.
const builtCities = pages
  .map((p) => p.file.split(path.sep))
  .filter((parts) => parts.length === 3 && parts[0] === 'werkgebied' && parts[2] === 'index.html')
  .map((parts) => parts[1])
  .sort()
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

// 8. The skin (stijl): a typeface that is really there, and text that stays readable.
//
// src/lib/stijl.ts guarantees each named value on its own -- every ink/paper pair in it was
// looked at once and can be trusted forever. What it cannot guarantee is the combination,
// because two axes are mixed with a colour that comes from client.yaml: `kleuring` tints the
// bands out of --brand-primary, and the schema only ever checked that colour against white.
// A dark-enough-for-white-buttons green can still put muted text on a tinted band below AA.
//
// So this resolves what the browser will actually paint -- var() chains and color-mix()
// included -- out of the built page, rather than trusting the vocabulary's own promises.

// The skin travels as one inline style on <html> (Base.astro). A page without one was not
// built on that layout and is carrying the stylesheet defaults instead of this client's look.
const rootStyles = pages.map((p) => ({
  file: p.file,
  style: p.html.match(/<html[^>]*\sstyle="([^"]*)"/)?.[1] ?? null,
}))
const skinless = rootStyles.filter((s) => !s.style).map((s) => s.file)
if (skinless.length) fail(`no skin on <html> (page not built on Base.astro?): ${skinless.join(', ')}`)
const skins = new Set(rootStyles.filter((s) => s.style).map((s) => s.style))
if (skins.size > 1) fail(`pages disagree about the skin: ${skins.size} different <html> style values`)

/** Custom properties as written on <html>, unresolved. */
const vars = {}
for (const decl of ([...skins][0] ?? '').split(';')) {
  const i = decl.indexOf(':')
  if (i > 0) vars[decl.slice(0, i).trim()] = decl.slice(i + 1).trim()
}

// --- colour --------------------------------------------------------------------------
//
// OKLab, because that is the space the tokens mix in. The matrices are Ottosson's, checked
// against his published vectors (white -> L=1, red -> 0.62796/0.22486/0.12585) to within
// 1.2e-5; CSS Color 4 routes the same conversion through XYZ and lands in the same place,
// far inside what a 4.5:1 threshold can tell apart.
const srgbToLinear = (c) => (c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4)
const linearToSrgb = (c) => (c <= 0.0031308 ? c * 12.92 : 1.055 * c ** (1 / 2.4) - 0.055)
const hexToRgb = (hex) => {
  const n = parseInt(hex.slice(1), 16)
  return [((n >> 16) & 255) / 255, ((n >> 8) & 255) / 255, (n & 255) / 255]
}
const toHex = (rgb) =>
  '#' + rgb.map((c) => Math.round(c * 255).toString(16).padStart(2, '0')).join('')

function rgbToOklab([r, g, b]) {
  const [R, G, B] = [r, g, b].map(srgbToLinear)
  const l = Math.cbrt(0.4122214708 * R + 0.5363325363 * G + 0.0514459929 * B)
  const m = Math.cbrt(0.2119034982 * R + 0.6806995451 * G + 0.1073969566 * B)
  const s = Math.cbrt(0.0883024619 * R + 0.2817188376 * G + 0.6299787005 * B)
  return [
    0.2104542553 * l + 0.793617785 * m - 0.0040720468 * s,
    1.9779984951 * l - 2.428592205 * m + 0.4505937099 * s,
    0.0259040371 * l + 0.7827717662 * m - 0.808675766 * s,
  ]
}
function oklabToRgb([L, A, B]) {
  const l = (L + 0.3963377774 * A + 0.2158037573 * B) ** 3
  const m = (L - 0.1055613458 * A - 0.0638541728 * B) ** 3
  const s = (L - 0.0894841775 * A - 1.291485548 * B) ** 3
  // Clamped into sRGB the way a screen does: a mix of two in-gamut colours can leave the
  // gamut by a hair, and the pixel the visitor sees is the clamped one.
  const clamp = (v) => Math.min(1, Math.max(0, linearToSrgb(v)))
  return [
    clamp(4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s),
    clamp(-1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s),
    clamp(-0.0041960863 * l - 0.7034186147 * m + 1.707614701 * s),
  ]
}

/** A token value down to one #rrggbb: follows var() chains and evaluates color-mix(in oklab). */
function resolveColor(value, depth = 0) {
  if (value === undefined) throw new Error('token is not set on <html>')
  if (depth > 8) throw new Error(`var() chain does not terminate at "${value}"`)
  const v = value.trim()
  if (/^#[0-9a-f]{6}$/i.test(v)) return v.toLowerCase()
  if (/^white$/i.test(v)) return '#ffffff'
  const ref = v.match(/^var\(\s*(--[\w-]+)\s*\)$/)
  if (ref) return resolveColor(vars[ref[1]], depth + 1)
  // Only the one form the vocabulary emits: `color-mix(in oklab, <a> <p>%, <b>)`.
  const mix = v.match(/^color-mix\(\s*in oklab\s*,\s*(.+?)\s+([\d.]+)%\s*,\s*(.+)\)$/i)
  if (mix) {
    const a = rgbToOklab(hexToRgb(resolveColor(mix[1], depth + 1)))
    const b = rgbToOklab(hexToRgb(resolveColor(mix[3], depth + 1)))
    const p = Number(mix[2]) / 100
    return toHex(oklabToRgb(a.map((x, i) => x * p + b[i] * (1 - p))))
  }
  throw new Error(`cannot resolve "${v}" to a colour`)
}

const luminance = (hex) => {
  const [r, g, b] = hexToRgb(hex).map(srgbToLinear)
  return 0.2126 * r + 0.7152 * g + 0.0722 * b
}
const contrast = (a, b) => {
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x)
  return (hi + 0.05) / (lo + 0.05)
}
/** An alpha foreground flattened onto its background, the way the compositor does it. */
const over = (hex, alpha, bg) => {
  const onder = hexToRgb(bg)
  return toHex(hexToRgb(hex).map((c, i) => c * alpha + onder[i] * (1 - alpha)))
}

// Every text colour the components use, against every surface they sit on. The full matrix
// rather than the observed pairs: which component lands on which band is a layout decision
// that changes, and all four surfaces are near-white variants of each other, so a
// combination that has no failure mode costs nothing to assert. AA for body text is 4.5:1
// and everything here is body-sized -- the vocabulary has no large-text exemption to spend.
//
// Hairlines (--color-line, --band-line) are deliberately absent: a divider carries no
// information a visitor could lose, which is exactly the case WCAG 1.4.11 exempts.
const AA = 4.5
const VOORGROND = ['--color-ink', '--color-mist', '--brand-primary']
const ACHTERGROND = ['--color-paper', '--color-card', '--band-bg', '--band-foto-bg']
const contrastPairs = [
  ...VOORGROND.flatMap((fg) => ACHTERGROND.map((bg) => ({ fg, bg }))),
  // White on the brand colour: every call button, the sticky bar and the closing panel.
  // The schema checks this one too; re-asserting it here is what catches a build that
  // shipped before the config it claims to be built from.
  { fg: 'white', bg: '--brand-primary' },
  // ...and the panel's body line, which is white at 85% (FinalCta.astro).
  { fg: 'white', alpha: 0.85, bg: '--brand-primary' },
]
for (const { fg, bg, alpha } of contrastPairs) {
  let fgHex, bgHex
  try {
    bgHex = resolveColor(bg.startsWith('--') ? vars[bg] : bg)
    fgHex = resolveColor(fg.startsWith('--') ? vars[fg] : fg)
    if (alpha !== undefined) fgHex = over(fgHex, alpha, bgHex)
  } catch (err) {
    fail(`skin colour ${fg} on ${bg}: ${err.message}`)
    continue
  }
  const ratio = contrast(fgHex, bgHex)
  if (ratio < AA) {
    const label = alpha === undefined ? fg : `${fg} at ${alpha * 100}%`
    // Which knob actually moves this pair. Naming all three every time would send the
    // founder to kleuring for a pair that is not tinted, and a gate that misdirects once
    // is a gate that gets argued with.
    const advies =
      bg === '--brand-primary'
        ? 'kies een donkerdere branding.kleur_primair'
        : bg === '--band-bg' || bg === '--band-foto-bg'
          ? 'kies een donkerdere branding.kleur_primair, een lichter stijl.palet, of stijl.kleuring: spaarzaam'
          : 'kies een donkerdere branding.kleur_primair of een lichter stijl.palet'
    fail(
      `${label} (${fgHex}) on ${bg} (${bgHex}) is ${ratio.toFixed(2)}:1, below the ${AA}:1 WCAG AA ` +
        `floor for body text -- ${advies}.`,
    )
  }
}

// --- typefaces -----------------------------------------------------------------------
//
// The failure this exists for is silent: a font stack naming a family whose bytes were not
// copied does not break anything visibly, it just serves the client the system stack -- the
// look the vocabulary exists to get away from -- on their live site.
const styleSheets = [
  ...filesWithExt(DIST, '.css').map((f) => ({
    file: path.relative(DIST, f),
    css: fs.readFileSync(f, 'utf8'),
  })),
  // Astro inlines a small enough stylesheet into <style>, so both are searched.
  ...pages.flatMap((p) =>
    [...p.html.matchAll(/<style[^>]*>([\s\S]*?)<\/style>/g)].map((m) => ({ file: p.file, css: m[1] })),
  ),
]
const unquote = (s) => s.trim().replace(/^['"]|['"]$/g, '')
const faces = styleSheets.flatMap((sheet) =>
  [...sheet.css.matchAll(/@font-face\s*\{[^}]*\}/g)].map((m) => ({
    sheet: sheet.file,
    family: unquote(m[0].match(/font-family:\s*([^;}]+)/)?.[1] ?? ''),
    urls: [...m[0].matchAll(/url\(\s*['"]?([^'")]+)['"]?\s*\)/g)].map((u) => u[1]),
  })),
)

// Generic families and the system keywords: legitimate stack members that no build ever
// ships bytes for.
const SYSTEEMFAMILIES = new Set([
  'system-ui',
  '-apple-system',
  'sans-serif',
  'serif',
  'ui-sans-serif',
  'ui-serif',
])
const stacks = ['--font-sans', '--font-display'].map((k) => vars[k] ?? '')
// Every family the page names anywhere, and the ones it names FIRST. Only the first entry
// of a stack is a face this build is responsible for; the rest ('Segoe UI', Georgia) are
// the fallbacks behind it and belong to the visitor's machine.
const genoemd = new Set(stacks.flatMap((s) => s.split(',').map(unquote)))
const webfonts = [...new Set(stacks.map((s) => unquote(s.split(',')[0])))].filter(
  (f) => f && !SYSTEEMFAMILIES.has(f),
)

for (const face of faces) {
  if (!genoemd.has(face.family)) {
    fail(`${face.sheet}: @font-face for "${face.family}", which no font stack on the page names`)
  }
  for (const url of face.urls) {
    if (/^(https?:)?\/\//.test(url)) {
      fail(`@font-face "${face.family}" loads ${url} from another host (breaks the no-cookie-banner guarantee)`)
    } else if (!url.startsWith('/')) {
      fail(`@font-face "${face.family}" loads "${url}", which is not a root-relative path`)
    } else if (!fs.existsSync(path.join(DIST, url.slice(1)))) {
      fail(`@font-face "${face.family}" points at ${url}, which this build did not copy`)
    }
  }
}
for (const family of webfonts) {
  if (!faces.some((f) => f.family === family)) {
    fail(`the page is set in "${family}" but no @font-face declares it: it will render in Arial`)
  }
}
// The other direction: bytes in the deploy that nothing asks for.
const fontsDir = path.join(DIST, 'fonts')
if (fs.existsSync(fontsDir)) {
  const referenced = new Set(faces.flatMap((f) => f.urls.map((u) => path.basename(u))))
  for (const file of fs.readdirSync(fontsDir).filter((f) => f.endsWith('.woff2'))) {
    if (!referenced.has(file)) fail(`dist/fonts/${file} is shipped but no @font-face names it`)
  }
}
// And the end-to-end one: the yaml asked for a pairing, so the page has to be set in that
// pairing and not merely in some webfont. Named per stack rather than counted, because the
// display face is the half a reader notices and a fallback there is invisible to a count:
// a redactioneel site that lost its serif still leads --font-sans with Figtree.
//
// fonts/manifest.json is the same file the build and src/lib/stijl.ts read. Consulting it
// here is the client.yaml move, not the loader move: shared data, independent assertion.
const letterontwerp = cfg.stijl?.letterontwerp ?? 'systeem'
const pairing = JSON.parse(fs.readFileSync(path.join(APP_ROOT, 'fonts', 'manifest.json'), 'utf8'))[
  letterontwerp
]
if (!pairing) {
  fail(`stijl.letterontwerp "${letterontwerp}" has no entry in fonts/manifest.json`)
} else {
  for (const [token, family] of [
    ['--font-display', pairing.display],
    ['--font-sans', pairing.body],
  ]) {
    const lead = unquote((vars[token] ?? '').split(',')[0])
    if (family && lead !== family) {
      fail(`stijl.letterontwerp "${letterontwerp}" means ${family} for ${token}, but the page leads with "${lead}"`)
    }
    if (!family && !SYSTEEMFAMILIES.has(lead)) {
      fail(`stijl.letterontwerp "${letterontwerp}" is the system stack, but ${token} leads with "${lead}"`)
    }
  }
}

// --- everything else the stylesheet loads ----------------------------------------------
//
// Section 5 covers the HTML; a stylesheet can reach off-host too, and an @import or a
// background-image on a CDN would cost the cookie-banner-free guarantee just as dearly.
for (const sheet of styleSheets) {
  for (const [, url] of sheet.css.matchAll(/url\(\s*['"]?([^'")]+)['"]?\s*\)/g)) {
    if (/^(https?:)?\/\//.test(url)) fail(`${sheet.file}: url(${url}) loads from another host`)
  }
  if (/@import\s+(url\(\s*)?['"]?(https?:)?\/\//i.test(sheet.css)) {
    fail(`${sheet.file}: @import of a remote stylesheet`)
  }
}

// 9. Things a human still has to look at, printed rather than asserted.
if (!bedrijf.email) notes.push('no e-mail address configured: the contact page is phone-only')
if (!fs.existsSync(path.join(APP_ROOT, 'clients', slug, 'fotos'))) {
  // Which fallback actually rendered depends on whether a stock set exists for the vak.
  // Worth naming: stock is generic by definition, so it is the founder's call whether it
  // is good enough to send, and real client photos always beat it.
  const hasStock = fs.existsSync(path.join(APP_ROOT, 'stock', bedrijf.vak))
  notes.push(
    hasStock
      ? `no fotos/ dir: the band runs on the ${bedrijf.vak} stock set, not this client's own work`
      : `no fotos/ dir and no stock set for "${bedrijf.vak}": the site runs on the colour-block fallback`,
  )
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
