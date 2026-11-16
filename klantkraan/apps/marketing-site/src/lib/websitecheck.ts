/**
 * Website check: what a homepage publicly says about itself, read the way any
 * visitor's browser reads it. One GET of the homepage, at most one GET of
 * /feed/, one request to the http address, and HEAD requests for the photos.
 * Nothing is logged into and nothing is probed.
 *
 * Every point follows the rule from the vault note "Website check - wat is
 * goed": seen on the page itself, and the owner can check it in ten seconds.
 * The texts never say anything about visitors, search position or safety
 * verdicts; they say what was found and where to look.
 *
 * The pure part (analyse) takes strings so it can be tested without a network.
 */

export type Status = 'goed' | 'let-op' | 'onbekend'

export interface Punt {
  id: string
  status: Status
  titel: string
  uitleg: string
  /** How the owner checks it himself. */
  zelf?: string
}

export interface Extra {
  /** true: http forwards to https. false: http opens as it is. null: not known. */
  httpForwards: boolean | null
  /** WordPress version from the feed, when the page itself does not show it. */
  feedVersion?: string | null
  /** Latest release per branch ("6.2" -> "6.2.15") and the newest release overall. */
  wpLatest?: { newest: string; perBranch: Record<string, string> } | null
  /** Largest image found on the homepage. */
  largestImage?: { bytes: number; url: string } | null
  year: number
}

const UA = 'klantkraan-websitecheck/1.0 (+https://klantkraan.nl/websitecheck/)'
const TIMEOUT_MS = 10_000
const MAX_BODY = 600_000
const MAX_HOPS = 5
const MAX_IMAGES = 12

/** Latest release per branch, read from api.wordpress.org on 2026-11-14. Used only if the live read fails. */
const WP_FALLBACK = {
  newest: '7.1.4',
  perBranch: {
    '7.1': '7.1.4',
    '7.0': '7.0.8',
    '6.9': '6.9.11',
    '6.8': '6.8.12',
    '6.7': '6.7.11',
    '6.6': '6.6.11',
    '6.5': '6.5.14',
    '6.4': '6.4.14',
    '6.3': '6.3.14',
    '6.2': '6.2.15',
    '6.1': '6.1.16',
    '6.0': '6.0.18',
    '5.9': '5.9.20',
    '5.8': '5.8.19',
    '5.7': '5.7.21',
    '5.6': '5.6.23',
    '5.5': '5.5.24',
    '5.4': '5.4.25',
    '5.3': '5.3.27',
    '5.2': '5.2.30',
    '5.1': '5.1.28',
    '5.0': '5.0.31',
    '4.9': '4.9.35',
    '4.8': '4.8.34',
    '4.7': '4.7.39',
  } as Record<string, string>,
}

/** Month in which security updates stopped (php.net). */
const PHP_EOL: Record<string, string> = {
  '5.': 'voor 2019',
  '7.0': 'januari 2019',
  '7.1': 'december 2019',
  '7.2': 'november 2020',
  '7.3': 'december 2021',
  '7.4': 'november 2022',
  '8.0': 'november 2023',
  '8.1': 'december 2025',
}

/* ---------- input ---------- */

const HOST_RE = /^(?=.{4,253}$)([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,24}$/

/** "https://www.Voorbeeld.nl/contact" -> "www.voorbeeld.nl"; null when it is not a public domain name. */
export function normaliseHost(input: string): string | null {
  let s = String(input ?? '')
    .trim()
    .toLowerCase()
  if (!s || s.length > 300) return null
  s = s.replace(/^[a-z][a-z0-9+.-]*:\/\//, '')
  s = s.split(/[/?#]/)[0] ?? ''
  if (s.includes('@') || s.includes(':')) return null
  s = s.replace(/\.$/, '')
  if (!HOST_RE.test(s)) return null
  if (/(^|\.)(localhost|local|internal|lan|home|test|invalid|example)$/.test(s)) return null
  return s
}

function safeUrl(raw: string, base?: string): URL | null {
  try {
    const u = new URL(raw, base)
    if (u.protocol !== 'https:' && u.protocol !== 'http:') return null
    if (u.port || u.username || u.password) return null
    if (!normaliseHost(u.hostname)) return null
    return u
  } catch {
    return null
  }
}

/* ---------- reading the page ---------- */

const strip = (s: string) =>
  s
    .replace(/<[^>]*>/g, ' ')
    .replace(/&nbsp;/gi, ' ')
    .replace(/&amp;/gi, '&')
    .replace(/&#0?39;|&apos;|&rsquo;/gi, "'")
    .replace(/&quot;/gi, '"')
    .replace(/&#(x[0-9a-f]+|[0-9]+);/gi, (_, n: string) => {
      const code = n[0] === 'x' || n[0] === 'X' ? parseInt(n.slice(1), 16) : parseInt(n, 10)
      return code > 31 && code < 0x10ffff ? String.fromCodePoint(code) : ' '
    })
    .replace(/&(ndash|mdash);/gi, '-')
    .replace(/&[a-z0-9]+;/gi, ' ')
    .replace(/\s+/g, ' ')
    .trim()

function attr(tag: string, name: string): string | null {
  const m = tag.match(new RegExp(`\\s${name}\\s*=\\s*("([^"]*)"|'([^']*)'|([^\\s>]+))`, 'i'))
  return m ? (m[2] ?? m[3] ?? m[4] ?? '') : null
}

function metaContent(html: string, name: string): string | null {
  for (const tag of html.match(/<meta\b[^>]*>/gi) ?? []) {
    if ((attr(tag, 'name') ?? '').toLowerCase() === name) return attr(tag, 'content')
  }
  return null
}

const kb = (bytes: number) =>
  bytes >= 1_000_000
    ? `${(bytes / 1_000_000).toFixed(1).replace('.', ',')} MB`
    : `${Math.round(bytes / 1000)} kB`

const branchOf = (v: string) => v.split('.').slice(0, 2).join('.')

/** true when version a is older than version b ("6.2.1" < "6.10"). */
export function older(a: string, b: string): boolean {
  const x = a.split('.').map(Number)
  const y = b.split('.').map(Number)
  for (let i = 0; i < 3; i++) {
    if ((x[i] ?? 0) !== (y[i] ?? 0)) return (x[i] ?? 0) < (y[i] ?? 0)
  }
  return false
}

export function wpVersionFromHtml(html: string): string | null {
  const g = metaContent(html, 'generator')
  const m = g?.match(/^WordPress ([0-9]+(?:\.[0-9]+){1,2})/i)
  return m ? m[1]! : null
}

export function isWordPress(html: string): boolean {
  return /\/wp-(content|includes)\//.test(html)
}

export function imageUrls(html: string, base: string): string[] {
  const out: string[] = []
  for (const tag of html.match(/<img\b[^>]*>/gi) ?? []) {
    const src = attr(tag, 'src') ?? attr(tag, 'data-src')
    if (!src || src.startsWith('data:')) continue
    const u = safeUrl(src, base)
    if (u && !out.includes(u.href)) out.push(u.href)
    if (out.length >= MAX_IMAGES) break
  }
  return out
}

/* ---------- the verdicts (pure) ---------- */

export function analyse(
  html: string,
  headers: Record<string, string>,
  finalUrl: string,
  extra: Extra,
): Punt[] {
  const punten: Punt[] = []
  const body = html.replace(/<script\b[\s\S]*?<\/script>/gi, ' ').replace(/<style\b[\s\S]*?<\/style>/gi, ' ')
  const text = strip(body.replace(/<head\b[\s\S]*?<\/head>/i, ' '))

  // 1. https
  const isHttps = finalUrl.startsWith('https://')
  if (!isHttps) {
    punten.push({
      id: 'https',
      status: 'let-op',
      titel: 'Je site opent zonder slotje',
      uitleg:
        'Je homepage opent op een http-adres. Browsers zetten daar "Niet beveiligd" bij in de adresbalk.',
      zelf: 'Open je site en kijk links van het adres of er een slotje staat.',
    })
  } else if (extra.httpForwards === false) {
    punten.push({
      id: 'https',
      status: 'let-op',
      titel: 'Het oude http-adres stuurt niet door',
      uitleg:
        'Je site heeft een slotje, maar wie het adres met http:// intypt of een oude link volgt, blijft op de versie zonder slotje.',
      zelf: `Typ http://${new URL(finalUrl).hostname} in je browser en kijk of het adres vanzelf https wordt.`,
    })
  } else {
    punten.push({
      id: 'https',
      status: 'goed',
      titel: 'Slotje in orde',
      uitleg: 'Je site opent op https.',
    })
  }

  // 2. WordPress
  if (isWordPress(html)) {
    const v = wpVersionFromHtml(html) ?? extra.feedVersion ?? null
    const latest = extra.wpLatest ?? WP_FALLBACK
    if (!v) {
      punten.push({
        id: 'wordpress',
        status: 'onbekend',
        titel: 'WordPress, versie niet zichtbaar',
        uitleg:
          'Je site draait op WordPress. Het versienummer staat niet openbaar, dus van buitenaf zien we niet of hij bij is.',
        zelf: `Log in en kijk onder Dashboard, Updates. De nieuwste versie is ${latest.newest}.`,
      })
    } else if (!older(v, latest.newest)) {
      punten.push({
        id: 'wordpress',
        status: 'goed',
        titel: `WordPress ${v} is bij`,
        uitleg: 'Plugins en thema zien we van buitenaf niet; die staan in je dashboard onder Updates.',
      })
    } else {
      const br = branchOf(v)
      const brLatest = latest.perBranch[br]
      let uitleg = `Je site meldt zelf WordPress ${v}. De nieuwste versie is ${latest.newest}.`
      if (brLatest && brLatest !== v) {
        uitleg += ` Ook binnen ${br} loopt hij achter: de laatste beveiligingsupdate daarvan is ${brLatest}.`
      } else if (!brLatest) {
        uitleg += ` Voor ${br} verschijnen geen beveiligingsupdates meer.`
      }
      uitleg += ' Updates dichten lekken die inmiddels bekend zijn.'
      punten.push({
        id: 'wordpress',
        status: 'let-op',
        titel: `WordPress ${v} loopt achter`,
        uitleg,
        zelf: 'Log in en kijk onder Dashboard, Updates. Maak eerst een back-up.',
      })
    }
  }

  // 3. PHP (only when the server says so itself)
  const pm = (headers['x-powered-by'] ?? '').match(/PHP\/([0-9]+\.[0-9]+)(\.[0-9]+)?/)
  if (pm) {
    const key = pm[1]!.startsWith('5.') ? '5.' : pm[1]!
    const eol = PHP_EOL[key]
    if (eol) {
      punten.push({
        id: 'php',
        status: 'let-op',
        titel: `PHP ${pm[1]} krijgt geen updates meer`,
        uitleg: `Je server meldt PHP ${pm[1]}${pm[2] ?? ''}. Daarvoor zijn de beveiligingsupdates gestopt in ${eol}. Sommige hosters repareren het zelf nog; vraag het na.`,
        zelf: 'Vraag je hoster welke PHP-versie je site gebruikt en of hij naar een nieuwere kan.',
      })
    }
  }

  // 4. phone
  const hasTel = /href\s*=\s*["']?tel:/i.test(body)
  const number = text.match(/(?:\+31[\s(]*0?\)?|\b0)[1-9](?:[\s.-]?\d){8}\b/)
  if (hasTel) {
    punten.push({
      id: 'telefoon',
      status: 'goed',
      titel: 'Telefoonnummer is aantikbaar',
      uitleg: 'Wie op een telefoon op je nummer tikt, belt meteen.',
    })
  } else if (number) {
    punten.push({
      id: 'telefoon',
      status: 'let-op',
      titel: 'Telefoonnummer is geen link',
      uitleg: `Je nummer (${number[0].trim()}) staat als gewone tekst op de pagina. Een iPhone maakt er vaak zelf een link van, maar daar kun je niet op rekenen.`,
      zelf: 'Open je site op een telefoon en tik op het nummer. Belt hij meteen?',
    })
  } else {
    punten.push({
      id: 'telefoon',
      status: 'let-op',
      titel: 'Geen telefoonnummer gevonden',
      uitleg:
        'Op je homepage vonden we geen telefoonnummer in de tekst. Staat het in een afbeelding, dan kan niemand erop tikken en leest Google het niet.',
      zelf: 'Open je homepage op een telefoon. Zie je je nummer zonder te zoeken?',
    })
  }

  // 5. phone screen
  const viewport = metaContent(html, 'viewport')
  if (viewport === null) {
    punten.push({
      id: 'mobiel',
      status: 'let-op',
      titel: 'Niet ingesteld voor telefoons',
      uitleg:
        'De regel die een pagina op telefoonbreedte zet ontbreekt. Meestal verschijnt de site dan piepklein, als een verkleinde computerpagina.',
      zelf: 'Open je site op een telefoon. Moet je inzoomen om de tekst te lezen?',
    })
  } else if (/user-scalable\s*=\s*(no|0)|maximum-scale\s*=\s*1(\.0)?\b/i.test(viewport)) {
    punten.push({
      id: 'mobiel',
      status: 'let-op',
      titel: 'Inzoomen staat uit',
      uitleg:
        'Je site past op een telefoon, maar bezoekers kunnen de tekst niet groter maken. Lastig voor wie minder goed ziet.',
      zelf: 'Open je site op een telefoon en probeer met twee vingers in te zoomen.',
    })
  } else {
    punten.push({
      id: 'mobiel',
      status: 'goed',
      titel: 'Ingesteld voor telefoons',
      uitleg: 'De pagina past zich aan de schermbreedte aan en inzoomen kan.',
    })
  }

  // 6. title
  const tm = html.match(/<title[^>]*>([\s\S]*?)<\/title>/i)
  const title = tm ? strip(tm[1]!) : ''
  if (!title) {
    punten.push({
      id: 'titel',
      status: 'let-op',
      titel: 'Geen paginatitel',
      uitleg:
        'De titel is de blauwe regel waarmee je in Google staat. Die ontbreekt, dus Google bedenkt er zelf een.',
      zelf: 'Kijk wat er op het tabblad van je browser staat.',
    })
  } else if (/^(home|welkom|homepage|start|index)(\s*[-|–:·]|$)/i.test(title) || title.length < 15) {
    punten.push({
      id: 'titel',
      status: 'let-op',
      titel: 'Paginatitel zegt weinig',
      uitleg: `Je titel is "${title}". Dat is de blauwe regel in Google. Een titel die zegt wat je doet en waar, vertelt een zoeker meteen of hij goed zit.`,
      zelf: 'Kijk wat er op het tabblad van je browser staat.',
    })
  } else {
    punten.push({
      id: 'titel',
      status: 'goed',
      titel: 'Paginatitel aanwezig',
      uitleg: `"${title.length > 90 ? title.slice(0, 88) + '…' : title}"`,
    })
  }

  // 7. description
  const desc = (metaContent(html, 'description') ?? '').trim()
  if (!desc) {
    punten.push({
      id: 'omschrijving',
      status: 'let-op',
      titel: 'Geen omschrijving voor Google',
      uitleg:
        'Onder de blauwe titel toont Google twee regels tekst. Je hebt ze niet zelf geschreven, dus Google pakt een willekeurig stuk van je pagina.',
      zelf: 'Zoek je bedrijfsnaam in Google en lees de twee regels onder je titel.',
    })
  } else {
    punten.push({
      id: 'omschrijving',
      status: 'goed',
      titel: 'Omschrijving voor Google aanwezig',
      uitleg: `"${desc.length > 120 ? desc.slice(0, 118) + '…' : desc}"`,
    })
  }

  // 8. main heading
  const h1s = (body.match(/<h1\b[\s\S]*?<\/h1>/gi) ?? []).map(strip)
  if (h1s.length === 0) {
    punten.push({
      id: 'kop',
      status: 'let-op',
      titel: 'Geen hoofdkop',
      uitleg:
        'De pagina heeft geen hoofdkop (H1). Dat is de kop waaraan een bezoeker en Google zien waar de pagina over gaat.',
    })
  } else if (h1s.length > 1) {
    punten.push({
      id: 'kop',
      status: 'let-op',
      titel: `${h1s.length} hoofdkoppen`,
      uitleg: 'Een pagina hoort één hoofdkop (H1) te hebben. Met meer is niet duidelijk waar hij over gaat.',
    })
  } else if (!h1s[0] || /^(home|welkom|homepage)[\s!.]*$/i.test(h1s[0])) {
    punten.push({
      id: 'kop',
      status: 'let-op',
      titel: 'Hoofdkop zegt weinig',
      uitleg: `Je hoofdkop is "${h1s[0] || '(leeg)'}". Zet daar wat je doet en voor wie.`,
    })
  } else {
    punten.push({
      id: 'kop',
      status: 'goed',
      titel: 'Eén duidelijke hoofdkop',
      uitleg: `"${h1s[0].length > 90 ? h1s[0].slice(0, 88) + '…' : h1s[0]}"`,
    })
  }

  // 9. image descriptions
  const imgs = body.match(/<img\b[^>]*>/gi) ?? []
  const without = imgs.filter((t) => !(attr(t, 'alt') ?? '').trim()).length
  if (imgs.length >= 4 && without / imgs.length > 0.5) {
    punten.push({
      id: 'alt',
      status: 'let-op',
      titel: `${without} van de ${imgs.length} afbeeldingen zonder beschrijving`,
      uitleg:
        'Een korte beschrijving bij een foto (alt-tekst) wordt voorgelezen aan wie slecht ziet, en Google gebruikt hem om te snappen wat erop staat.',
    })
  } else if (imgs.length >= 4) {
    punten.push({
      id: 'alt',
      status: 'goed',
      titel: 'Afbeeldingen hebben een beschrijving',
      uitleg: `${imgs.length - without} van de ${imgs.length} afbeeldingen hebben een alt-tekst.`,
    })
  }

  // 10. heaviest photo
  const big = extra.largestImage
  if (big && big.bytes > 500_000) {
    const name = decodeURIComponent(new URL(big.url).pathname.split('/').pop() ?? '').slice(0, 60)
    punten.push({
      id: 'foto',
      status: 'let-op',
      titel: `Eén foto weegt ${kb(big.bytes)}`,
      uitleg: `De zwaarste foto op je homepage${/\.(jpe?g|png|webp|gif|avif)$/i.test(name) ? ` (${name})` : ''} is ${kb(big.bytes)}. Voor een foto op een website is zo'n 300 kB meestal genoeg; de rest haalt een telefoon voor niets op.`,
      zelf: 'Open je site op een telefoon zonder wifi en kijk hoe lang de foto\'s op zich laten wachten.',
    })
  } else if (big) {
    punten.push({
      id: 'foto',
      status: 'goed',
      titel: "Foto's zijn licht genoeg",
      uitleg: `De zwaarste foto die we op je homepage vonden is ${kb(big.bytes)}.`,
    })
  }

  // 11. footer year
  const years = [...body.matchAll(/(?:&copy;|©|copyright)\s*(?:\d{4}\s*[-–]\s*)?(20[0-9]{2})/gi)]
    .map((m) => Number(m[1]))
    .filter((y) => y <= extra.year)
  if (years.length) {
    const y = Math.max(...years)
    if (y < extra.year) {
      punten.push({
        id: 'jaartal',
        status: 'let-op',
        titel: `Onderaan staat nog ${y}`,
        uitleg: `Bij het copyright onderaan je pagina staat ${y}. Een bezoeker vraagt zich dan af of de rest nog klopt.`,
        zelf: 'Scrol naar de onderkant van je homepage.',
      })
    }
  }

  return punten
}

/* ---------- network ---------- */

interface Page {
  finalUrl: string
  status: number
  headers: Record<string, string>
  body: string
}

async function readCapped(res: Response, max: number): Promise<string> {
  if (!res.body) return ''
  const reader = res.body.getReader()
  const chunks: Uint8Array[] = []
  let size = 0
  while (size < max) {
    const { done, value } = await reader.read()
    if (done) break
    chunks.push(value)
    size += value.byteLength
  }
  void reader.cancel().catch(() => {})
  const all = new Uint8Array(Math.min(size, max))
  let at = 0
  for (const c of chunks) {
    const part = c.subarray(0, Math.min(c.byteLength, all.byteLength - at))
    all.set(part, at)
    at += part.byteLength
    if (at >= all.byteLength) break
  }
  return new TextDecoder('utf-8', { fatal: false }).decode(all)
}

/** GET with every redirect hop checked: public domain names only, http(s) only, default ports only. */
async function get(start: string, max = MAX_BODY): Promise<Page> {
  let url = safeUrl(start)
  for (let hop = 0; url && hop <= MAX_HOPS; hop++) {
    const res = await fetch(url.href, {
      redirect: 'manual',
      headers: { 'User-Agent': UA, Accept: 'text/html,application/xhtml+xml,*/*;q=0.8', 'Accept-Language': 'nl' },
      signal: AbortSignal.timeout(TIMEOUT_MS),
    })
    const loc = res.headers.get('location')
    if (res.status >= 300 && res.status < 400 && loc) {
      void res.body?.cancel().catch(() => {})
      url = safeUrl(loc, url.href)
      continue
    }
    const headers: Record<string, string> = {}
    res.headers.forEach((v, k) => (headers[k.toLowerCase()] = v))
    return { finalUrl: url.href, status: res.status, headers, body: await readCapped(res, max) }
  }
  throw new Error('redirect')
}

async function httpForwards(host: string): Promise<boolean | null> {
  try {
    const res = await fetch(`http://${host}/`, {
      redirect: 'manual',
      headers: { 'User-Agent': UA },
      signal: AbortSignal.timeout(TIMEOUT_MS),
    })
    void res.body?.cancel().catch(() => {})
    const loc = res.headers.get('location') ?? ''
    if (res.status >= 300 && res.status < 400) return loc.startsWith('https://')
    return res.status < 400 ? false : null
  } catch {
    return null
  }
}

async function wpLatest(): Promise<Extra['wpLatest']> {
  try {
    const res = await fetch('https://api.wordpress.org/core/version-check/1.7/', {
      headers: { 'User-Agent': UA },
      signal: AbortSignal.timeout(5000),
    })
    const data = (await res.json()) as { offers?: { version?: string; response?: string }[] }
    const perBranch: Record<string, string> = {}
    let newest = ''
    for (const o of data.offers ?? []) {
      if (!o.version || !/^\d+\.\d+(\.\d+)?$/.test(o.version)) continue
      if (o.response === 'upgrade' && !newest) newest = o.version
      perBranch[branchOf(o.version)] ??= o.version
    }
    return newest ? { newest, perBranch } : null
  } catch {
    return null
  }
}

async function largestImage(urls: string[]): Promise<Extra['largestImage']> {
  const sizes = await Promise.all(
    urls.map(async (url) => {
      try {
        const res = await fetch(url, {
          method: 'HEAD',
          redirect: 'manual',
          headers: { 'User-Agent': UA },
          signal: AbortSignal.timeout(5000),
        })
        const type = res.headers.get('content-type') ?? ''
        const bytes = Number(res.headers.get('content-length'))
        return res.ok && type.startsWith('image/') && bytes > 0 ? { bytes, url } : null
      } catch {
        return null
      }
    }),
  )
  return sizes.reduce<Extra['largestImage']>((a, b) => (b && (!a || b.bytes > a.bytes) ? b : a), null)
}

export type Result =
  | { ok: true; domein: string; punten: Punt[]; letOp: number }
  | { ok: false; domein?: string; reden: 'adres' | 'onbereikbaar' | 'geweigerd' | 'leeg' }

export async function runCheck(input: string): Promise<Result> {
  const host = normaliseHost(input)
  if (!host || host === 'klantkraan.nl' || host.endsWith('.klantkraan.nl')) {
    return { ok: false, reden: 'adres' }
  }
  let page: Page | null = null
  for (const scheme of ['https://', 'http://']) {
    try {
      page = await get(`${scheme}${host}/`)
      break
    } catch {
      /* try the next scheme */
    }
  }
  if (!page) return { ok: false, domein: host, reden: 'onbereikbaar' }
  if (page.status === 401 || page.status === 403 || page.status === 429 || page.status === 503) {
    return { ok: false, domein: host, reden: 'geweigerd' }
  }
  if (page.status >= 400) return { ok: false, domein: host, reden: 'onbereikbaar' }
  if (!/<(html|body|head|title)\b/i.test(page.body)) return { ok: false, domein: host, reden: 'leeg' }

  const wp = isWordPress(page.body)
  const needFeed = wp && !wpVersionFromHtml(page.body)
  const [forwards, latest, feedVersion, big] = await Promise.all([
    page.finalUrl.startsWith('https://') ? httpForwards(host) : Promise.resolve(null),
    wp ? wpLatest() : Promise.resolve(null),
    needFeed
      ? get(new URL('/feed/', page.finalUrl).href, 20_000)
          .then((f) => f.body.match(/<generator>https?:\/\/wordpress\.org\/\?v=([0-9.]+)<\/generator>/)?.[1] ?? null)
          .catch(() => null)
      : Promise.resolve(null),
    largestImage(imageUrls(page.body, page.finalUrl)),
  ])

  const punten = analyse(page.body, page.headers, page.finalUrl, {
    httpForwards: forwards,
    feedVersion,
    wpLatest: latest,
    largestImage: big,
    year: new Date().getFullYear(),
  })
  const order: Record<Status, number> = { 'let-op': 0, onbekend: 1, goed: 2 }
  punten.sort((a, b) => order[a.status] - order[b.status])
  return {
    ok: true,
    domein: host.replace(/^www\./, ''),
    punten,
    letOp: punten.filter((p) => p.status === 'let-op').length,
  }
}
