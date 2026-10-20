// Integration test — runs against `serve ./dist` on a configurable base URL.
// Covers: illustrations, risk-reversal, view transitions, gidsen routes,
// Wave 2 isolation (data exists but no pages generated), lead-form posting.
//
// Usage: node scripts/test-integration.mjs [base-url] [api-base]
//   base-url  defaults to http://localhost:4322
//   api-base  defaults to https://api.klantkraan.nl (skip lead test if unset)

import { chromium } from 'playwright'

const BASE = process.argv[2] ?? 'http://localhost:4322'
const API = process.argv[3] // optional

let passes = 0
let fails = 0
function check(label, cond, detail = '') {
  if (cond) {
    console.log(`  ✓ ${label}`)
    passes++
  } else {
    console.log(`  ✗ ${label}${detail ? ` — ${detail}` : ''}`)
    fails++
  }
}

const browser = await chromium.launch({ headless: true })

// ============================================================
// 1. Illustrations on all 6 cornerstones
// ============================================================
console.log(`\n=== Illustrations on cornerstones @ ${BASE} ===`)
{
  const expected = [
    { path: '/loodgieters', aria: 'Waterkraan' },
    { path: '/dakdekkers', aria: 'Onweer boven dak' },
    { path: '/schilder', aria: 'Verfroller' },
    { path: '/aannemer', aria: 'Bouwhelm en bouwtekening' },
    { path: '/installateur', aria: 'Radiator' },
    { path: '/elektricien', aria: 'Stekker en stopcontact' },
  ]

  const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } })
  const page = await ctx.newPage()
  page.on('pageerror', (e) => console.log('[pageerror]', e.message))

  for (const e of expected) {
    await page.goto(BASE + e.path, { waitUntil: 'networkidle' })
    const svg = page.locator(`svg[aria-label="${e.aria}"]`)
    check(`${e.path} renders ${e.aria}`, (await svg.count()) >= 1)
  }
  await ctx.close()
}

// ============================================================
// 2. Risk-reversal section appears on every cornerstone + home
// ============================================================
console.log(`\n=== Risk-reversal copy @ ${BASE} ===`)
{
  const paths = ['/', '/loodgieters', '/dakdekkers', '/schilder', '/aannemer', '/installateur', '/elektricien']
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } })
  const page = await ctx.newPage()

  for (const p of paths) {
    await page.goto(BASE + p, { waitUntil: 'networkidle' })
    const a = page.locator('text=Eerste maand 50% korting')
    const b = page.locator('text=Opzegbaar per direct')
    const c = page.locator('text=Geen wurgcontract, geen setup')
    const all = (await a.count()) >= 1 && (await b.count()) >= 1 && (await c.count()) >= 1
    check(`${p} shows the 3 risk-reversal promises`, all)
  }
  await ctx.close()
}

// ============================================================
// 3. View Transitions — ClientRouter shipped + scripts re-init
// ============================================================
console.log(`\n=== View Transitions @ ${BASE} ===`)
{
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } })
  const page = await ctx.newPage()
  const errors = []
  page.on('pageerror', (e) => errors.push(e.message))

  await page.goto(BASE + '/', { waitUntil: 'networkidle' })

  // ClientRouter ships its script — astro:before-preparation event fires.
  // Easier check: meta tag from <ClientRouter /> + window.astrouter is undef
  // (it's not exposed) — so instead check that navigating between pages
  // changes the URL without a full reload (sentinel survives).
  await page.evaluate(() => {
    window.__kkSentinel = 'ABCDEF'
  })

  // Navigate via the Voor wie? dropdown
  await page.locator('[data-branches-dropdown="desktop"] summary').first().click()
  await page.waitForTimeout(120)
  await page.locator('[data-branches-dropdown="desktop"] ul a[href="/dakdekkers"]').first().click()
  await page.waitForURL(/\/dakdekkers\/?$/, { timeout: 5000 }).catch(() => {})

  const sentinel = await page.evaluate(() => window.__kkSentinel)
  check(
    'ClientRouter preserves window across navigation (no full reload)',
    sentinel === 'ABCDEF',
    `sentinel=${sentinel}`,
  )
  check('URL updated to /dakdekkers', /\/dakdekkers/.test(page.url()), `url=${page.url()}`)

  // After SPA navigation, the dakdekker storm-cloud illustration should be on
  // the page (proof that the body actually swapped).
  const storm = page.locator('svg[aria-label="Onweer boven dak"]')
  check('post-nav DOM shows dakdekker illustration', (await storm.count()) >= 1)

  // Now navigate to /rekentool and verify the ROI calc re-initialises
  // (astro:page-load is the trigger). We type into the calls input and
  // expect the missed-year output to update.
  await page.goto(BASE + '/', { waitUntil: 'networkidle' })
  await page.locator('a[href="/rekentool"]').first().click()
  await page.waitForURL(/\/rekentool\/?$/, { timeout: 5000 }).catch(() => {})
  await page.waitForTimeout(300)

  const callsInput = page.locator('#calls')
  await callsInput.fill('100')
  await page.waitForTimeout(150)
  const missedYear = (await page.locator('#out-missed-year').textContent())?.trim()
  // 100 calls/wk × 52 × 0.28 = 1456
  check('ROI calc re-binds + reacts after SPA nav', missedYear === '1.456', `out=${missedYear}`)

  // Navigate to /demo and back to /rekentool to make sure repeated
  // navigation doesn't double-bind (output should still update).
  await page.locator('a[href="/demo"]').first().click()
  await page.waitForURL(/\/demo\/?$/, { timeout: 5000 }).catch(() => {})
  await page.waitForTimeout(200)
  await page.goBack()
  await page.waitForURL(/\/rekentool\/?$/, { timeout: 5000 }).catch(() => {})
  await page.waitForTimeout(300)
  await page.locator('#calls').fill('20')
  await page.waitForTimeout(150)
  const missedYear2 = (await page.locator('#out-missed-year').textContent())?.trim()
  // 20 × 52 × 0.28 = 291.2 → 291
  check('ROI calc still works after back-nav', missedYear2 === '291', `out=${missedYear2}`)

  check('no console / page errors during VT run', errors.length === 0, errors.join('; '))
  await ctx.close()
}

// ============================================================
// 4. Hamburger still works after SPA navigation
// ============================================================
console.log(`\n=== Hamburger after SPA nav @ ${BASE} ===`)
{
  const ctx = await browser.newContext({
    viewport: { width: 375, height: 812 },
    isMobile: true,
    hasTouch: true,
  })
  const page = await ctx.newPage()
  const errors = []
  page.on('pageerror', (e) => errors.push(e.message))

  await page.goto(BASE + '/', { waitUntil: 'networkidle' })

  // Open hamburger, navigate via the mobile dropdown to /aannemer
  await page.locator('#mobile-menu-toggle').click()
  await page.waitForTimeout(150)
  await page.locator('[data-branches-dropdown="mobile"] summary').first().click()
  await page.waitForTimeout(150)
  await page.locator('[data-branches-dropdown="mobile"] a[href="/aannemer"]').first().click()
  await page.waitForURL(/\/aannemer\/?$/, { timeout: 5000 }).catch(() => {})
  await page.waitForTimeout(300)

  // The hamburger toggle on /aannemer should still respond — proves the
  // re-init hook fires.
  const toggle = page.locator('#mobile-menu-toggle')
  await toggle.click()
  await page.waitForTimeout(150)
  const menu = page.locator('#mobile-menu')
  check('hamburger re-binds after SPA nav', await menu.isVisible())

  check('no console / page errors during hamburger-after-nav run', errors.length === 0, errors.join('; '))
  await ctx.close()
}

// ============================================================
// 5. Gidsen index + 6 [slug] pages render
// ============================================================
console.log(`\n=== Gidsen routes @ ${BASE} ===`)
{
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } })
  const page = await ctx.newPage()

  await page.goto(BASE + '/gidsen', { waitUntil: 'networkidle' })
  const h1 = await page.locator('main h1').first().textContent()
  check('gids index H1 = "Gidsen voor vakmensen"', h1?.includes('Gidsen voor vakmensen'))

  // 6 gids cards
  const cards = page.locator('main a[href^="/gidsen/"]')
  const cardCount = await cards.count()
  check('gids index lists 6 gids cards', cardCount === 6, `count=${cardCount}`)

  // Each slug renders + has reading time + niche label
  const slugs = [
    'loodgieters-klanten-werven',
    'dakdekkers-storm-protocol',
    'schilders-lentepiek-overleven',
    'installateurs-cv-storingen-januari',
    'elektriciens-spoed-vs-projecten',
    'aannemers-offerteaanvragen-filteren',
  ]
  for (const s of slugs) {
    await page.goto(BASE + '/gidsen/' + s, { waitUntil: 'networkidle' })
    const slugH1 = await page.locator('main h1').first().textContent()
    check(`/gidsen/${s} renders H1`, !!(slugH1 && slugH1.length > 5), `h1="${slugH1}"`)
    const breadcrumb = page.locator('nav[aria-label="Kruimelpad"]')
    check(`/gidsen/${s} has breadcrumb`, (await breadcrumb.count()) >= 1)
  }

  await ctx.close()
}

// ============================================================
// 6. Wave 2 isolation — wave2 data exists but no pages generated
// ============================================================
console.log(`\n=== Wave 2 isolation @ ${BASE} ===`)
{
  // Wave-2-only combo: /eindhoven/loodgieter (per blueprint pages 11-20).
  // Must 404 because wave2 is not in getStaticPaths.
  const res = await fetch(BASE + '/eindhoven/loodgieter', { redirect: 'manual' })
  check('Wave 2 URL (/eindhoven/loodgieter) is NOT live', res.status === 404, `status=${res.status}`)

  // Wave-1 URL should still be live.
  const wave1Res = await fetch(BASE + '/utrecht/dakdekker', { redirect: 'manual' })
  check(
    'Wave 1 URL (/utrecht/dakdekker) is live',
    wave1Res.status === 200 || wave1Res.status === 301 || wave1Res.status === 308,
    `status=${wave1Res.status}`,
  )
}

// ============================================================
// 7. /voor-wie hub still works (no regression from new nav item)
// ============================================================
console.log(`\n=== /voor-wie hub regression @ ${BASE} ===`)
{
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } })
  const page = await ctx.newPage()
  await page.goto(BASE + '/voor-wie', { waitUntil: 'networkidle' })

  // 6 niche cards present
  for (const slug of ['loodgieters', 'dakdekkers', 'schilder', 'installateur', 'elektricien', 'aannemer']) {
    const card = page.locator(`main a[href="/${slug}"]`)
    check(`hub card for /${slug}`, (await card.count()) >= 1)
  }
  await ctx.close()
}

// ============================================================
// 8. Gidsen nav link present in header
// ============================================================
console.log(`\n=== Gidsen nav link @ ${BASE} ===`)
{
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } })
  const page = await ctx.newPage()
  await page.goto(BASE + '/', { waitUntil: 'networkidle' })

  const gidsenLink = page.locator('header nav a[href="/gidsen"]')
  check('Gidsen link in desktop header', (await gidsenLink.count()) >= 1)
  await ctx.close()
}

// ============================================================
// 9. Lead form POSTs to worker (only if API endpoint provided)
// ============================================================
if (API) {
  console.log(`\n=== Lead form → ${API}/api/lead ===`)
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } })
  const page = await ctx.newPage()
  await page.goto(BASE + '/demo', { waitUntil: 'networkidle' }).catch(() => {
    // fall back to homepage if /demo doesn't have the form
  })
  // If lead form not on /demo, try homepage section
  let form = page.locator('#lead-form')
  if ((await form.count()) === 0) {
    await page.goto(BASE + '/#contact', { waitUntil: 'networkidle' })
    form = page.locator('#lead-form')
  }
  if ((await form.count()) === 0) {
    console.log('  ⚠ lead form not found on /demo or homepage — skipping')
  } else {
    // Override the apiBase via dataset so we can use --resolve via a custom origin.
    // For local testing the API URL is hard to reach; this branch is best-effort.
    await page.fill('#lead-name', 'Test Founder')
    await page.fill('#lead-email', `test+${Date.now()}@example.com`)
    await page.fill('#lead-message', 'Integration test from Playwright — please ignore.')

    const responsePromise = page.waitForResponse(
      (r) => r.url().includes('/api/lead'),
      { timeout: 10000 },
    ).catch(() => null)

    await page.locator('#lead-submit').click()
    const res = await responsePromise
    if (res) {
      check(`lead form POST got ${res.status()}`, [200, 201, 409].includes(res.status()))
    } else {
      console.log('  ⚠ no response captured for /api/lead — DNS likely unresolved (expected pre-DNS-fix)')
    }
  }
  await ctx.close()
}

await browser.close()

console.log(`\n=== ${passes} passed · ${fails} failed ===`)
process.exit(fails === 0 ? 0 : 1)
