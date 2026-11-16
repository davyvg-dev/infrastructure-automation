// The precise, diagram-led redesign (plan 2026-11-15-klantkraan-site-redesign),
// against the built site served by `astro preview`.
//
// Checks: no horizontal overflow and no text past the screen edge at 1440, 390
// and 320 on the main pages; one h1; the art. 50 line on /; the flow diagram and
// cost ledger exist with an accessible name; NL homepage section order; no glow,
// no radial gradient and no pill badge on the main pages; with reduced motion the hero thread
// and both diagrams show their finished state; h1 is set in Inter; body::before
// paints nothing; the old fonts are never requested.
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

const PAGES = ['/', '/loodgieters/', '/prijzen/', '/demo/', '/en/', '/es/']
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

// ------------------------------------------------------------------ NL homepage
console.log('\n=== NL homepage ===')
{
  const { ctx, page } = await newPage({ viewport: { width: 1440, height: 900 } })
  await page.goto(`${BASE}/`, { waitUntil: 'load' })

  const art50 = await page.getByText('U chat met een digitale assistent.').count()
  check('art. 50 line "U chat met een digitale assistent." is on /', art50 > 0)

  const order = await page.evaluate(() =>
    [...document.querySelectorAll('main [data-section]')].map((s) => s.getAttribute('data-section')),
  )
  const want = ['hero', 'demo', 'flow', 'ledger', 'honest', 'start', 'final']
  check('section order: ' + want.join(', '), JSON.stringify(order) === JSON.stringify(want), order.join(', '))

  for (const name of ['flow', 'ledger']) {
    const d = page.locator(`[data-diagram="${name}"]`)
    const n = await d.count()
    check(`${name} diagram present once`, n === 1, `found ${n}`)
    if (n !== 1) continue
    const acc = await d.evaluate((el) => {
      const label = el.getAttribute('aria-label') ?? ''
      const by = el.getAttribute('aria-labelledby')
      const byText = by ? (document.getElementById(by)?.textContent ?? '') : ''
      return { role: el.getAttribute('role') ?? el.tagName.toLowerCase(), name: (label || byText).trim() }
    })
    check(`${name} diagram has an accessible name`, acc.name.length > 10, JSON.stringify(acc))
  }

  const windowLink = await page.locator('[data-hero-window] a[href="#demo"]').count()
  check('hero window links straight to the live demo', windowLink > 0)

  await ctx.close()
}

// ------------------------------------------------------------------ reduced motion
console.log('\n=== Reduced motion: finished state ===')
for (const width of [1440, 390]) {
  const { ctx, page } = await newPage({ viewport: { width, height: 900 }, reducedMotion: 'reduce' })
  await page.goto(`${BASE}/`, { waitUntil: 'load' })
  await page.waitForTimeout(250)
  const state = await page.evaluate(() => {
    const vis = (el) => {
      if (!el) return false
      if (el.closest('[hidden]')) return false
      const cs = getComputedStyle(el)
      return cs.display !== 'none' && cs.visibility !== 'hidden' && parseFloat(cs.opacity) > 0.99
    }
    const reveal = [...document.querySelectorAll('[data-hero-window] [data-reveal], [data-diagram] [data-reveal]')]
    return {
      reply: vis(document.getElementById('kk-reply')),
      stamp: vis(document.getElementById('kk-stamp')),
      typingGone: !vis(document.getElementById('kk-typing')),
      revealTotal: reveal.length,
      revealHidden: reveal.filter((el) => !vis(el)).length,
      lampOn: [...document.querySelectorAll('[data-diagram="flow"] [data-lamp]')].every(
        (el) => el.getAttribute('data-lamp') === 'on' || getComputedStyle(el).getPropertyValue('--lit').trim() === '1',
      ),
      running: document
        .getAnimations()
        .filter((a) => a.playState === 'running' && a.effect?.getComputedTiming().iterations === Infinity).length,
    }
  })
  check(`@${width}: hero reply and booking slip shown, typing dots gone`, state.reply && state.stamp && state.typingGone, JSON.stringify(state))
  check(`@${width}: every [data-reveal] in the hero and diagrams is fully visible`, state.revealTotal > 0 && state.revealHidden === 0, `${state.revealHidden} of ${state.revealTotal} hidden`)
  check(`@${width}: the flow diagram's lamp is on`, state.lampOn)
  check(`@${width}: no endless animation runs`, state.running === 0, `${state.running} running`)
  await ctx.close()
}

await browser.close()
console.log(`\n${passes} passed, ${fails} failed`)
process.exit(fails ? 1 : 0)
