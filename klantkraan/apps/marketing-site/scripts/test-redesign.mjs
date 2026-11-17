// The precise, diagram-led redesign (plan 2026-11-15-klantkraan-site-redesign),
// against the built site served by `astro preview`.
//
// Checks: no horizontal overflow and no text past the screen edge at 1440, 390
// and 320 on the main pages; one h1; the art. 50 line on /; the flow diagram and
// cost ledger exist with an accessible name; NL homepage section order; no glow,
// no radial gradient and no pill badge on the main pages; with reduced motion the hero thread
// and both diagrams show their finished state; h1 is set in Inter; body::before
// paints nothing; the old fonts are never requested.
// Since plan 2026-11-16-homepage-four-services: / shows four services (hero with
// four lamps, cards, bands), /ai-receptionist/ keeps the old homepage, prices agree
// with src/data/services.ts on every page that shows them, and the header carries
// a Diensten menu on one row at 1024, 1280 and 1440.
//
// Usage: node scripts/test-redesign.mjs [base-url]   (default http://localhost:4321)

import { chromium } from 'playwright'

const BASE = (process.argv[2] ?? 'http://localhost:4321').replace(/\/$/, '')

let passes = 0
let fails = 0
function check(label, cond, detail = '') {
  if (cond) {
    console.log(`  ✓ ${label}`)
    passes++
  } else {
    console.log(`  ✗ ${label}${detail ? ` (${detail})` : ''}`)
    fails++
  }
}

const browser = await chromium.launch({ headless: true })

// The demo chat and form endpoints are third-party; nothing is sent from a test.
async function newPage(opts = {}) {
  const ctx = await browser.newContext(opts)
  await ctx.route(/sslip\.io|sibforms\.com|brevo|mollie/, (r) => r.fulfill({ status: 204, body: '' }))
  const page = await ctx.newPage()
  return { ctx, page }
}

const findOffenders = (page) =>
  page.evaluate(() => {
    const out = []
    for (const el of document.querySelectorAll('main *')) {
      const cs = getComputedStyle(el)
      const r = el.getBoundingClientRect()
      if (r.width === 0 || r.height === 0) continue
      if (/radial-gradient/.test(cs.backgroundImage)) out.push(`radial-gradient on ${el.className}`)
      // A glow: a shadow with a wide blur in a warm or coloured tone.
      for (const m of cs.boxShadow.matchAll(/rgba?\(([^)]+)\)[^,]*?(\d+(?:\.\d+)?)px (\d+(?:\.\d+)?)px (\d+(?:\.\d+)?)px/g)) {
        const [rr, gg, bb] = m[1].split(',').map((x) => parseFloat(x))
        const blur = parseFloat(m[4])
        const coloured = Math.max(rr, gg, bb) - Math.min(rr, gg, bb) > 40
        if (coloured && blur >= 12) out.push(`glow on ${el.className}`)
      }
      if (cs.textShadow !== 'none') out.push(`text-shadow on ${el.className}`)
      // A pill: fully rounded, much wider than tall, carrying text.
      const radius = parseFloat(cs.borderTopLeftRadius)
      const text = (el.textContent ?? '').trim()
      if (text && r.width > r.height * 2 && radius >= r.height / 2 - 1 && r.height < 48) out.push(`pill: "${text.slice(0, 30)}"`)
    }
    return [...new Set(out)].slice(0, 6)
  })

const PAGES = [
  '/',
  '/ai-receptionist/',
  '/website-onderhoud/',
  '/automatiseringen/',
  '/loodgieters/',
  '/prijzen/',
  '/demo/',
  '/en/',
  '/es/',
]
const WIDTHS = [1440, 768, 390, 320]

// ------------------------------------------------------------------ layout
console.log(`\n=== Layout @ ${BASE} ===`)
const oldFonts = []
for (const width of WIDTHS) {
  const { ctx, page } = await newPage({ viewport: { width, height: 900 } })
  page.on('request', (req) => {
    if (/bricolage|hanken|spacemono/i.test(req.url())) oldFonts.push(req.url())
  })
  for (const path of PAGES) {
    await page.goto(`${BASE}${path}`, { waitUntil: 'load' })
    const over = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth)
    check(`${path} @${width}: no horizontal overflow`, over <= 0, `${over}px over`)

    // Text that runs past the screen edge, outside any element that clips it on purpose.
    const clipped = await page.evaluate(() => {
      const vw = window.innerWidth
      const out = []
      const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT)
      while (walker.nextNode()) {
        const node = walker.currentNode
        if (!node.textContent.trim()) continue
        const el = node.parentElement
        if (!el || el.closest('[hidden], [aria-hidden="true"], .sr-only, script, style, noscript')) continue
        const cs = getComputedStyle(el)
        if (cs.visibility === 'hidden' || cs.display === 'none') continue
        const range = document.createRange()
        range.selectNodeContents(node)
        for (const r of range.getClientRects()) {
          if (r.width === 0 || r.height === 0) continue
          if (r.right > vw + 1 || r.left < -1) {
            // Allowed when an ancestor clips it inside the viewport (a scroller).
            let a = el
            let clippedByScroller = false
            while (a && a !== document.body) {
              const s = getComputedStyle(a)
              if (/(auto|scroll|hidden|clip)/.test(s.overflowX)) {
                const ar = a.getBoundingClientRect()
                if (ar.right <= vw + 1 && ar.left >= -1) {
                  clippedByScroller = true
                  break
                }
              }
              a = a.parentElement
            }
            if (!clippedByScroller) out.push(`${el.tagName.toLowerCase()}: "${node.textContent.trim().slice(0, 40)}"`)
            break
          }
        }
      }
      return out.slice(0, 5)
    })
    check(`${path} @${width}: no text past the screen edge`, clipped.length === 0, clipped.join('; '))

    if (width === 1440) {
      const h1s = await page.locator('h1').count()
      check(`${path}: exactly one h1`, h1s === 1, `found ${h1s}`)
      const h1Font = await page.locator('h1').first().evaluate((el) => getComputedStyle(el).fontFamily)
      check(`${path}: h1 is set in Inter`, /^"?Inter/.test(h1Font), h1Font)
      const before = await page.evaluate(() => {
        const s = getComputedStyle(document.body, '::before')
        return { bg: s.backgroundImage, content: s.content }
      })
      check(`${path}: body::before paints no background`, before.bg === 'none', before.bg)
      const offenders = await findOffenders(page)
      check(`${path}: no glow, radial gradient, text shadow or pill badge`, offenders.length === 0, offenders.join('; '))
    }
  }
  await ctx.close()
}
check('old fonts (Bricolage, Hanken, Space Mono) never requested', oldFonts.length === 0, oldFonts[0])

// ------------------------------------------------------------------ stat line
// A figure must never squeeze its caption into a narrow column (round 3 of the
// independent check: "4–6 weken" left its caption 67px wide at 768).
console.log('\n=== Stat line captions ===')
for (const width of [1440, 1024, 768, 390, 320]) {
  const { ctx, page } = await newPage({ viewport: { width, height: 900 } })
  for (const path of ['/loodgieters/', '/dakdekkers/', '/sportscholen/', '/en/dakdekkers/', '/en/sportscholen/']) {
    await page.goto(`${BASE}${path}`, { waitUntil: 'load' })
    const narrow = await page.evaluate(() =>
      [...document.querySelectorAll('[data-stat-caption]')]
        .map((el) => ({ w: Math.round(el.getBoundingClientRect().width), t: el.textContent.trim().slice(0, 30) }))
        .filter((c) => c.w < 160),
    )
    check(`${path} @${width}: every stat caption is at least 160px wide`, narrow.length === 0, JSON.stringify(narrow))
  }
  await ctx.close()
}

// ------------------------------------------------------------------ NL homepage + /ai-receptionist/
// Plan 2026-11-16-homepage-four-services: / shows the four services, the old
// receptionist homepage lives on at /ai-receptionist/ unchanged.
const sectionOrder = (page) =>
  page.evaluate(() => [...document.querySelectorAll('main [data-section]')].map((s) => s.getAttribute('data-section')))

async function checkDiagrams(page, path, names) {
  for (const name of names) {
    const d = page.locator(`[data-diagram="${name}"]`)
    const n = await d.count()
    check(`${path}: ${name} diagram present once`, n === 1, `found ${n}`)
    if (n !== 1) continue
    const acc = await d.evaluate((el) => {
      const label = el.getAttribute('aria-label') ?? ''
      const by = el.getAttribute('aria-labelledby')
      const byText = by ? (document.getElementById(by)?.textContent ?? '') : ''
      return { role: el.getAttribute('role') ?? el.tagName.toLowerCase(), name: (label || byText).trim() }
    })
    // The cost ledger is a <figure> with a table inside; every drawing is role="img".
    const roleOk = name === 'ledger' || acc.role === 'img'
    check(`${path}: ${name} diagram has an accessible name`, roleOk && acc.name.length > 10, JSON.stringify(acc))
  }
}

// Visible text of <main>, for price checks ("€ 45" with a normal or no-break space).
const mainText = (page) => page.evaluate(() => document.querySelector('main')?.innerText ?? '')

console.log('\n=== NL homepage: four services ===')
{
  const { ctx, page } = await newPage({ viewport: { width: 1440, height: 900 } })
  await page.goto(`${BASE}/`, { waitUntil: 'load' })

  const art50 = await page.getByText('U chat met een digitale assistent.').count()
  check('art. 50 line "U chat met een digitale assistent." is on /', art50 > 0)

  const order = await sectionOrder(page)
  const want = ['hero', 'services', 'demo', 'flow', 'websites', 'automations', 'ads', 'final']
  check('/ section order: ' + want.join(', '), JSON.stringify(order) === JSON.stringify(want), order.join(', '))

  await checkDiagrams(page, '/', ['services', 'flow', 'care', 'followup', 'variants'])

  // The hero list under the drawing: four links, each to a band that exists here.
  const circuits = await page.locator('[data-section="hero"] [data-hero-circuits] a').evaluateAll((as) =>
    as.map((a) => {
      const href = a.getAttribute('href') ?? ''
      return { href, ok: href.startsWith('#') && !!document.getElementById(href.slice(1)) }
    }),
  )
  check('hero lists 4 circuit links', circuits.length === 4, JSON.stringify(circuits))
  check('every hero circuit link points to an id on /', circuits.length > 0 && circuits.every((c) => c.ok), JSON.stringify(circuits))

  // Four service cards: each with a € price, excl. btw, and links that answer 200.
  const cards = page.locator('[data-section="services"] [data-service]')
  const nCards = await cards.count()
  check('4 [data-service] cards', nCards === 4, `found ${nCards}`)
  const areas = []
  for (let i = 0; i < nCards; i++) {
    const c = cards.nth(i)
    const area = await c.getAttribute('data-service')
    areas.push(area)
    const text = await c.evaluate((el) => el.innerText)
    check(`card ${area}: a € price and "excl. btw"`, /€\s?\d/.test(text) && /excl\.\sbtw/.test(text), text.slice(0, 120))
    check(`card ${area}: a drawing`, (await c.locator('svg[aria-hidden="true"]').count()) >= 1)
    const hrefs = await c.locator('a[href^="/"]').evaluateAll((as) => as.map((a) => a.getAttribute('href')))
    check(`card ${area}: links to its own page`, hrefs.length >= 1, JSON.stringify(hrefs))
    for (const h of hrefs) {
      const res = await page.request.get(`${BASE}${h.split('#')[0]}`)
      check(`card ${area}: ${h} answers 200`, res.status() === 200, `status ${res.status()}`)
    }
  }
  check('cards in order receptionist, websites, automations, ads',
    JSON.stringify(areas) === JSON.stringify(['receptionist', 'websites', 'automations', 'ads']), areas.join(', '))

  // Each band on / names its price excl. btw.
  for (const band of ['websites', 'automations', 'ads']) {
    const text = await page.locator(`[data-section="${band}"]`).evaluate((el) => el.innerText).catch(() => '')
    check(`band ${band}: a € price and "excl. btw"`, /€\s?\d/.test(text) && /excl\.\sbtw/.test(text), text.slice(0, 120))
  }

  // The receptionist keeps its price line and the way to the old homepage and the calculator.
  const recLine = await page.locator('[data-receptionist-line]').evaluate((el) => ({
    text: el.innerText,
    hrefs: [...el.querySelectorAll('a')].map((a) => a.getAttribute('href')),
  })).catch(() => ({ text: '', hrefs: [] }))
  check('receptionist line under the flow diagram: price, /ai-receptionist/ and /rekentool/',
    /€\s?299/.test(recLine.text) && recLine.hrefs.includes('/ai-receptionist/') && recLine.hrefs.includes('/rekentool/'),
    JSON.stringify(recLine))

  await ctx.close()
}

console.log('\n=== /ai-receptionist/: the old homepage ===')
{
  const { ctx, page } = await newPage({ viewport: { width: 1440, height: 900 } })
  await page.goto(`${BASE}/ai-receptionist/`, { waitUntil: 'load' })

  const art50 = await page.getByText('U chat met een digitale assistent.').count()
  check('art. 50 line is on /ai-receptionist/', art50 > 0)

  const order = await sectionOrder(page)
  const want = ['hero', 'demo', 'flow', 'ledger', 'honest', 'start', 'final']
  check('/ai-receptionist/ section order: ' + want.join(', '), JSON.stringify(order) === JSON.stringify(want), order.join(', '))

  await checkDiagrams(page, '/ai-receptionist/', ['flow', 'ledger'])

  const windowLink = await page.locator('[data-hero-window] a[href="#demo"]').count()
  check('/ai-receptionist/ hero window links straight to the live demo', windowLink > 0)

  const title = await page.title()
  check('/ai-receptionist/ keeps the old homepage title', title === 'AI-receptionist voor uw bedrijf: websitechat & WhatsApp | Klantkraan', title)

  // The roadmap no longer calls follow-ups unavailable while /automatiseringen/ sells them.
  const html = await page.content()
  check('/ai-receptionist/ roadmap drops "Nog niet beschikbaar"', html.includes('Wat we bouwen') && !html.includes('Nog niet beschikbaar'))

  await ctx.close()
}

// ------------------------------------------------------------------ prices
// services.ts is the one source; these pages must agree with it.
console.log('\n=== Price parity ===')
{
  const { ctx, page } = await newPage({ viewport: { width: 1440, height: 900 } })
  const want = [
    ['/', [/€\s?45\b/, /€\s?795\b/, /€\s?299\b/, /€\s?1\.250\b/]],
    ['/website-onderhoud/', [/€\s?45 per maand/, /€\s?295\b/]],
    ['/automatiseringen/', [/vanaf €\s?1\.250/, /vanaf €\s?350 per maand/, /€\s?195\b/, /€\s?19 per maand/]],
    ['/advertentievideos/', [/€\s?795\b/]],
    ['/prijzen/', [/€\s?299\b/, /€\s?45\b/, /€\s?1\.250\b/, /€\s?795\b/]],
  ]
  for (const [path, res] of want) {
    await page.goto(`${BASE}${path}`, { waitUntil: 'load' })
    const text = await mainText(page)
    for (const re of res) check(`${path} shows ${re.source.replace(/\\s\?/g, ' ').replace(/\\b|\\/g, '')}`, re.test(text))
  }
  // Every price on the two new pages says excl. btw: no € amount without it in the same block.
  for (const path of ['/website-onderhoud/', '/automatiseringen/']) {
    await page.goto(`${BASE}${path}`, { waitUntil: 'load' })
    const bare = await page.evaluate(() => {
      const out = []
      for (const el of document.querySelectorAll('main p, main li, main td, main dd')) {
        if (el.querySelector('p, li')) continue
        const t = el.innerText
        if (!/€\s?\d/.test(t)) continue
        // The price and its note may sit in sibling elements of one block.
        const block = el.closest('[data-price], li, article, section') ?? el
        if (!/excl\.\sbtw/.test(block.innerText) && !/incl\. btw/.test(t)) out.push(t.slice(0, 60))
      }
      return out
    })
    check(`${path}: every € amount says excl. btw`, bare.length === 0, bare.join(' | '))
  }
  // /prijzen/ keeps its tiers and gains one block with the other three services.
  await page.goto(`${BASE}/prijzen/`, { waitUntil: 'load' })
  const others = await page.locator('[data-other-services] [data-service]').evaluateAll((ls) =>
    ls.map((l) => ({ area: l.getAttribute('data-service'), text: l.innerText, href: l.querySelector('a')?.getAttribute('href') })),
  )
  check('/prijzen/ "Andere diensten" lists 3 services with a price, excl. btw and a link',
    others.length === 3 && others.every((o) => /€\s?\d/.test(o.text) && /excl\.\sbtw/.test(o.text) && o.href?.startsWith('/')),
    JSON.stringify(others))
  await ctx.close()
}

// ------------------------------------------------------------------ header
console.log('\n=== Header: Diensten menu, one row from 900 ===')
{
  const { ctx, page } = await newPage({ viewport: { width: 1280, height: 900 } })
  await page.goto(`${BASE}/`, { waitUntil: 'load' })
  const links = await page.locator('header [data-services-dropdown="desktop"] a').evaluateAll((as) => as.map((a) => a.getAttribute('href')))
  const wantLinks = ['/ai-receptionist/', '/website-onderhoud/', '/automatiseringen/', '/advertentievideos/', '/#diensten']
  check('desktop Diensten menu: four services and "Alle diensten"', JSON.stringify(links) === JSON.stringify(wantLinks), JSON.stringify(links))
  const mobile = await page.locator('#mobile-menu [data-services-dropdown="mobile"] a').count()
  check('mobile Diensten menu has 5 links', mobile === 5, `found ${mobile}`)
  await page.goto(`${BASE}/en/`, { waitUntil: 'load' })
  check('/en/ header has no Diensten menu', (await page.locator('header [data-services-dropdown]').count()) === 0)
  await ctx.close()

  for (const width of [900, 1024, 1280, 1440]) {
    const { ctx: c2, page: p2 } = await newPage({ viewport: { width, height: 900 } })
    await p2.goto(`${BASE}/`, { waitUntil: 'load' })
    // The flex row never wraps; crowding shows as a label that breaks over two
    // lines, a row taller than one item, or the nav running into the logo.
    const h = await p2.evaluate(() => {
      const nav = document.querySelector('header nav')
      const ul = nav?.querySelector(':scope > ul')
      const logo = document.querySelector('header a[href="/"]')
      const tallest = Math.max(...[...(ul?.children ?? [])].map((li) => li.getBoundingClientRect().height))
      const broken = [...(ul?.querySelectorAll(':scope > li > a, :scope > li > details > summary') ?? [])]
        .filter((el) => {
          const tops = new Set()
          const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT)
          while (w.nextNode()) {
            if (!w.currentNode.textContent.trim()) continue
            const r = document.createRange()
            r.selectNodeContents(w.currentNode)
            for (const x of r.getClientRects()) tops.add(Math.round(x.top))
          }
          return tops.size > 1
        })
        .map((el) => el.textContent.trim())
      return {
        tallest: Math.round(tallest),
        broken,
        gap: Math.round((nav?.getBoundingClientRect().left ?? 0) - (logo?.getBoundingClientRect().right ?? 0)),
        right: Math.round(nav?.getBoundingClientRect().right ?? 0) <= window.innerWidth,
      }
    })
    check(`header @${width}: nav on one row`, h.tallest <= 36 && h.broken.length === 0 && h.gap >= 16 && h.right, JSON.stringify(h))
    await c2.close()
  }
}

// ------------------------------------------------------------------ reduced motion
console.log('\n=== Reduced motion: finished state ===')
for (const [path, width] of [['/', 1440], ['/', 390], ['/ai-receptionist/', 1440], ['/ai-receptionist/', 390]]) {
  const { ctx, page } = await newPage({ viewport: { width, height: 900 }, reducedMotion: 'reduce' })
  await page.goto(`${BASE}${path}`, { waitUntil: 'load' })
  await page.waitForTimeout(250)
  const state = await page.evaluate(() => {
    // A lamp is on when its circle is actually filled with the accent, not
    // because the markup says so. Only the drawing on screen counts (wide or tall).
    const accent = getComputedStyle(document.documentElement).getPropertyValue('--color-sodium').trim()
    const probe = document.createElement('i')
    probe.style.color = accent
    document.body.append(probe)
    const want = getComputedStyle(probe).color
    probe.remove()
    const shown = (el) => el.getBoundingClientRect().width > 0
    const lampsLit = (sel) => {
      const lamps = [...document.querySelectorAll(sel)].filter(shown)
      const lit = lamps.filter((l) => {
        const cs = [...(l.matches('circle') ? [l] : l.querySelectorAll('circle'))].filter(shown)
        return cs.length > 0 && cs.every((c) => getComputedStyle(c).fill === want)
      })
      return { shown: lamps.length, lit: lit.length }
    }
    const vis = (el) => {
      if (!el) return false
      if (el.closest('[hidden]')) return false
      const cs = getComputedStyle(el)
      return cs.display !== 'none' && cs.visibility !== 'hidden' && parseFloat(cs.opacity) > 0.99
    }
    const reveal = [...document.querySelectorAll('[data-hero-window] [data-reveal], [data-diagram] [data-reveal]')]
    const flow = lampsLit('[data-diagram="flow"] [data-lamp]')
    return {
      reply: vis(document.getElementById('kk-reply')),
      stamp: vis(document.getElementById('kk-stamp')),
      typingGone: !vis(document.getElementById('kk-typing')),
      revealTotal: reveal.length,
      revealHidden: reveal.filter((el) => !vis(el)).length,
      flowLampOn: flow.shown > 0 && flow.lit === flow.shown,
      hero: lampsLit('[data-diagram="services"] [data-lamp]'),
      running: document
        .getAnimations()
        .filter((a) => a.playState === 'running' && a.effect?.getComputedTiming().iterations === Infinity).length,
    }
  })
  const at = `${path} @${width}`
  if (path === '/ai-receptionist/') {
    check(`${at}: hero reply and booking slip shown, typing dots gone`, state.reply && state.stamp && state.typingGone, JSON.stringify(state))
    check(`${at}: every [data-reveal] in the hero and diagrams is fully visible`, state.revealTotal > 0 && state.revealHidden === 0, `${state.revealHidden} of ${state.revealTotal} hidden`)
  } else {
    check(`${at}: all 4 hero lamps are lit`, state.hero.shown === 4 && state.hero.lit === 4, JSON.stringify(state.hero))
    check(`${at}: every [data-reveal] in the diagrams is fully visible`, state.revealHidden === 0, `${state.revealHidden} of ${state.revealTotal} hidden`)
  }
  check(`${at}: the flow diagram's lamp is on`, state.flowLampOn)
  check(`${at}: no endless animation runs`, state.running === 0, `${state.running} running`)
  await ctx.close()
}

await browser.close()
console.log(`\n${passes} passed, ${fails} failed`)
process.exit(fails ? 1 : 0)
