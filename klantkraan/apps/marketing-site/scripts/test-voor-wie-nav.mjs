// Test the "Voor wie?" navigation flow — desktop dropdown + mobile nested
// menu — against the built dist served by `astro preview`.
//
// Usage:  node scripts/test-voor-wie-nav.mjs [base-url]
// Default base URL: http://localhost:4321 (astro preview default).

import { chromium } from 'playwright'

const BASE = process.argv[2] ?? 'http://localhost:4321'

const EXPECTED_BRANCHES = [
  { label: 'Loodgieters', href: '/loodgieters' },
  { label: 'Dakdekkers', href: '/dakdekkers' },
  { label: 'Schilders', href: '/schilder' },
  { label: 'Installateurs', href: '/installateur' },
  { label: 'Elektriciens', href: '/elektricien' },
  { label: 'Aannemers', href: '/aannemer' },
]

const browser = await chromium.launch({ headless: true })

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

// ============================================================
// 1. Desktop: viewport 1280×800, dropdown behaviour
// ============================================================
console.log(`\n=== Desktop dropdown @ ${BASE} ===`)
{
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } })
  const page = await ctx.newPage()
  const errors = []
  page.on('pageerror', (e) => errors.push(e.message))
  page.on('requestfailed', (r) => errors.push(`req-failed: ${r.url()}`))

  await page.goto(BASE + '/', { waitUntil: 'networkidle' })

  const dropdown = page.locator('[data-branches-dropdown="desktop"]')
  const summary = dropdown.locator('summary').first()
  const ul = dropdown.locator('ul').first()

  check('desktop dropdown element exists', (await dropdown.count()) === 1)

  // Closed by default
  const startOpen = await dropdown.evaluate((el) => el.open)
  check('dropdown closed by default', startOpen === false)

  // Items not in viewport rect when closed (details hides them)
  const closedItemsVisible = await ul.first().isVisible({ timeout: 500 }).catch(() => false)
  check('niche items hidden when closed', closedItemsVisible === false)

  // Click summary -> opens
  await summary.click()
  await page.waitForTimeout(150)
  const afterOpen = await dropdown.evaluate((el) => el.open)
  check('dropdown opens on summary click', afterOpen === true)

  const openItemsVisible = await ul.first().isVisible()
  check('niche items visible when open', openItemsVisible === true)

  // All 6 niche links present + correct href
  for (const b of EXPECTED_BRANCHES) {
    const link = ul.locator(`a[href="${b.href}"]`)
    const text = (await link.textContent())?.trim()
    check(`link to ${b.href} present`, (await link.count()) > 0, `text="${text}"`)
    check(`link label is "${b.label}"`, text === b.label, `got "${text}"`)
  }

  // "Alle branches →" link present
  const alleLink = ul.locator('a[href="/voor-wie"]')
  check('"Alle branches →" link present', (await alleLink.count()) === 1)

  // Escape closes
  await page.keyboard.press('Escape')
  await page.waitForTimeout(150)
  const afterEsc = await dropdown.evaluate((el) => el.open)
  check('Escape closes dropdown', afterEsc === false)

  // Open again, click outside -> closes
  await summary.click()
  await page.waitForTimeout(100)
  await page.locator('main, body').first().click({ position: { x: 600, y: 500 } })
  await page.waitForTimeout(150)
  const afterOutside = await dropdown.evaluate((el) => el.open)
  check('outside click closes dropdown', afterOutside === false)

  // Navigation: click loodgieters from open dropdown lands on /loodgieters
  await summary.click()
  await page.waitForTimeout(100)
  await ul.locator('a[href="/loodgieters"]').first().click()
  // ClientRouter does SPA pushState — waitForURL polls instead of relying on
  // networkidle / waitForNavigation which assume a full document load.
  await page.waitForURL(/\/loodgieters\/?$/, { timeout: 5000 }).catch(() => {})
  check(
    'clicking Loodgieters navigates to /loodgieters',
    page.url().endsWith('/loodgieters') || page.url().endsWith('/loodgieters/'),
    `url=${page.url()}`,
  )

  check('no console / page errors on desktop run', errors.length === 0, errors.join('; '))

  await ctx.close()
}

// ============================================================
// 2. Mobile: viewport 375×812, hamburger + nested details
// ============================================================
console.log(`\n=== Mobile menu @ ${BASE} ===`)
{
  const ctx = await browser.newContext({
    viewport: { width: 375, height: 812 },
    userAgent:
      'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    isMobile: true,
    hasTouch: true,
  })
  const page = await ctx.newPage()
  const errors = []
  page.on('pageerror', (e) => errors.push(e.message))
  page.on('requestfailed', (r) => errors.push(`req-failed: ${r.url()}`))

  await page.goto(BASE + '/', { waitUntil: 'networkidle' })

  // Hamburger opens
  const toggle = page.locator('#mobile-menu-toggle')
  check('hamburger toggle visible', await toggle.isVisible())
  await toggle.click()
  await page.waitForTimeout(150)

  const mobileMenu = page.locator('#mobile-menu')
  check('mobile menu visible after click', await mobileMenu.isVisible())

  // Voor wie? nested details
  const mobileDropdown = page.locator('[data-branches-dropdown="mobile"]')
  check('mobile Voor-wie? dropdown present', (await mobileDropdown.count()) === 1)

  const mobileStartOpen = await mobileDropdown.evaluate((el) => el.open)
  check('mobile dropdown closed by default', mobileStartOpen === false)

  await mobileDropdown.locator('summary').first().click()
  await page.waitForTimeout(150)
  const mobileAfterOpen = await mobileDropdown.evaluate((el) => el.open)
  check('mobile dropdown opens on tap', mobileAfterOpen === true)

  // All 6 niche links present in mobile dropdown
  for (const b of EXPECTED_BRANCHES) {
    const link = mobileDropdown.locator(`a[href="${b.href}"]`)
    check(`mobile link to ${b.href} present`, (await link.count()) > 0)
  }

  const mobileAlleLink = mobileDropdown.locator('a[href="/voor-wie"]')
  check('mobile "Alle branches →" link present', (await mobileAlleLink.count()) === 1)

  // Tap Loodgieters -> navigates AND hamburger closes (existing behaviour).
  // ClientRouter does SPA pushState; waitForURL is needed.
  await mobileDropdown.locator('a[href="/loodgieters"]').first().click()
  await page.waitForURL(/\/loodgieters\/?$/, { timeout: 5000 }).catch(() => {})
  check(
    'mobile tap navigates to /loodgieters',
    page.url().endsWith('/loodgieters') || page.url().endsWith('/loodgieters/'),
  )

  check('no console / page errors on mobile run', errors.length === 0, errors.join('; '))

  await ctx.close()
}

// ============================================================
// 3. Hub page
// ============================================================
console.log(`\n=== Hub page @ ${BASE}/voor-wie ===`)
{
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } })
  const page = await ctx.newPage()
  const errors = []
  page.on('pageerror', (e) => errors.push(e.message))

  await page.goto(BASE + '/voor-wie', { waitUntil: 'networkidle' })

  const h1 = await page.locator('h1').textContent()
  check('hub H1 reads "Voor welk vak werkt u?"', h1?.includes('Voor welk vak werkt u'))

  // 6 niche cards each linking to its cornerstone
  for (const b of EXPECTED_BRANCHES) {
    const card = page.locator(`main a[href="${b.href}"]`)
    check(`hub card for ${b.href} present`, (await card.count()) >= 1)
  }

  check('no console / page errors on hub run', errors.length === 0, errors.join('; '))

  await ctx.close()
}

// ============================================================
// 4. Footer alignment
// ============================================================
console.log(`\n=== Footer Branches alignment @ ${BASE} ===`)
{
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } })
  const page = await ctx.newPage()
  await page.goto(BASE + '/', { waitUntil: 'networkidle' })

  for (const b of EXPECTED_BRANCHES) {
    const footerLink = page.locator(`footer a[href="${b.href}"]`)
    check(`footer link to ${b.href}`, (await footerLink.count()) >= 1)
  }

  await ctx.close()
}

await browser.close()

console.log(`\n=== ${passes} passed · ${fails} failed ===`)
process.exit(fails === 0 ? 0 : 1)
