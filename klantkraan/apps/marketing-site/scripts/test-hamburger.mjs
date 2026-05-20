// One-shot debug script: load the live klantkraan-marketing.pages.dev home page
// at mobile viewport, click the hamburger, inspect what happens. Captures
// console errors, network failures, and the menu's computed visibility before
// and after click. Not part of the test suite — diagnostic only.

import { chromium } from 'playwright'

const URL = process.argv[2] ?? 'https://klantkraan-marketing.pages.dev/'

const browser = await chromium.launch({ headless: true })
const ctx = await browser.newContext({
  viewport: { width: 375, height: 812 }, // iPhone X-ish
  userAgent:
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
  isMobile: true,
  hasTouch: true,
})
const page = await ctx.newPage()

const consoleEvents = []
const pageErrors = []
const requestFailures = []
page.on('console', (msg) => consoleEvents.push(`[${msg.type()}] ${msg.text()}`))
page.on('pageerror', (err) => pageErrors.push(err.message))
page.on('requestfailed', (req) =>
  requestFailures.push(`${req.method()} ${req.url()} :: ${req.failure()?.errorText}`)
)

await page.goto(URL, { waitUntil: 'networkidle' })

const toggle = page.locator('#mobile-menu-toggle')
const menu = page.locator('#mobile-menu')

const before = await page.evaluate(() => {
  const t = document.getElementById('mobile-menu-toggle')
  const m = document.getElementById('mobile-menu')
  return {
    toggleFound: !!t,
    menuFound: !!m,
    toggleVisible: t ? getComputedStyle(t).display !== 'none' : null,
    menuVisible: m ? getComputedStyle(m).display !== 'none' : null,
    menuHidden: m ? m.hidden : null,
    menuHasHiddenClass: m ? m.classList.contains('hidden') : null,
    ariaExpanded: t ? t.getAttribute('aria-expanded') : null,
    listenerKey:
      typeof window !== 'undefined' && window.__hamburgerListenerAttached
        ? true
        : 'not flagged (test-only flag missing)',
  }
})

console.log('\n=== BEFORE CLICK ===')
console.log(JSON.stringify(before, null, 2))

// Click via real tap
try {
  await toggle.click({ timeout: 3000 })
} catch (err) {
  console.log('CLICK FAILED:', err.message)
}

// Brief wait for any async UI changes
await page.waitForTimeout(300)

const after = await page.evaluate(() => {
  const t = document.getElementById('mobile-menu-toggle')
  const m = document.getElementById('mobile-menu')
  return {
    menuVisible: m ? getComputedStyle(m).display !== 'none' : null,
    menuHidden: m ? m.hidden : null,
    menuHasHiddenClass: m ? m.classList.contains('hidden') : null,
    ariaExpanded: t ? t.getAttribute('aria-expanded') : null,
    menuRect: m ? m.getBoundingClientRect() : null,
  }
})

console.log('\n=== AFTER CLICK ===')
console.log(JSON.stringify(after, null, 2))

console.log('\n=== CONSOLE EVENTS ===')
console.log(consoleEvents.length ? consoleEvents.join('\n') : '(none)')

console.log('\n=== PAGE ERRORS ===')
console.log(pageErrors.length ? pageErrors.join('\n') : '(none)')

console.log('\n=== REQUEST FAILURES ===')
console.log(requestFailures.length ? requestFailures.join('\n') : '(none)')

await browser.close()
