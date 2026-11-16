// Lead magnets, mini offers and the one call to action, against the built site
// served by `astro preview` (plan 2026-11-15-lead-magnets-and-mini-offers).
//
// Checks: one [data-offer-cta] (button, next line, reason line) on the listed
// pages; 4 [data-mini-offer] on /klein-beginnen/; on every magnet a call to action
// before it, inside its result and after it (the matching mini offer, once);
// every magnet and mini-offer link answers 200; the two new forms refuse an empty
// email and a filled honeypot and send the source tag; no horizontal scroll at
// 390 and 320 wide; no founder name on the magnet pages.
// Brevo and /api/websitecheck/ are stubbed with page.route: nothing is sent.
//
// Usage: node scripts/test-magnets.mjs [base-url]   (default http://localhost:4321)

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
const context = await browser.newContext()
const page = await context.newPage()

async function open(path, p = page) {
  const res = await p.goto(`${BASE}${path}`, { waitUntil: 'load' })
  return res
}

// ------------------------------------------------------------------ CTA block
console.log(`\n=== One call to action block per page @ ${BASE} ===`)
const ctaPages = [
  '/',
  '/prijzen/',
  '/loodgieters/',
  '/rekentool/',
  '/gidsen/loodgieters-klanten-werven/',
  '/blog/ai-telefoniste-voor-loodgieters/',
  '/advertentievideos/',
  '/klein-beginnen/',
]
for (const path of ctaPages) {
  await open(path)
  const blocks = page.locator('[data-offer-cta]')
  const n = await blocks.count()
  check(`${path} has exactly one [data-offer-cta]`, n === 1, `found ${n}`)
  if (n !== 1) continue
  const b = blocks.first()
  const btn = b.locator('a.btn')
  const href = (await btn.count()) ? await btn.first().getAttribute('href') : null
  const next = (await b.locator('[data-next]').textContent())?.trim() ?? ''
  const reason = (await b.locator('[data-reason]').textContent())?.trim() ?? ''
  check(`${path} CTA has button, next line and reason line`, !!href && next.length > 10 && reason.length > 10, `href=${href}`)
}

for (const path of ['/aanmelden/', '/bedankt/', '/en/bedankt/', '/es/bedankt/', '/demo/dhz/', '/legal/privacy/', '/en/', '/gratis/']) {
  await open(path)
  const n = await page.locator('[data-offer-cta]').count()
  check(`${path} has no CTA block`, n === 0, `found ${n}`)
}

// ------------------------------------------------------------------ mini offers
console.log('\n=== /klein-beginnen/ ===')
await open('/klein-beginnen/')
{
  const cards = page.locator('[data-mini-offer]')
  const n = await cards.count()
  check('/klein-beginnen/ has 4 [data-mini-offer]', n === 4, `found ${n}`)
  for (let i = 0; i < n; i++) {
    const c = cards.nth(i)
    const text = (await c.textContent()) ?? ''
    const pay = await c.locator('[data-pay]').getAttribute('href')
    check(
      `card ${i + 1} has problem, delivery, price, days and a pay/mail button`,
      /€\s?\d+/.test(text) && /werkdag/.test(text) && !!pay && (pay.startsWith('https://') || pay.startsWith('mailto:')) &&
        (await c.locator('[data-problem]').count()) === 1 && (await c.locator('[data-delivers]').count()) === 1,
      `pay=${pay}`,
    )
  }
}

{
  const pays = await page.locator('[data-mini-offer] [data-pay]').evaluateAll((as) => as.map((a) => [a.getAttribute('href'), a.textContent.trim()]))
  check('every pay button opens a Mollie payment link and shows the amount incl. btw',
    pays.length === 4 && pays.every(([h, t]) => h.startsWith('https://payment-links.mollie.com/payment/') && /incl\. btw/.test(t)),
    JSON.stringify(pays))
  check('the four pay links are all different', new Set(pays.map(([h]) => h)).size === 4)
}

// ------------------------------------------------------------------ before / within / after
console.log('\n=== Call to action before, inside and after each magnet ===')
for (const path of ['/websitecheck/', '/scan/', '/rekentool/', '/advertentievideos/']) {
  await open(path)
  const before = await page.locator('[data-cta-line="before"]').count()
  check(`${path} has a line before the magnet`, before === 1, `found ${before}`)
  const after = await page.locator('[data-mini-offer]').count()
  check(`${path} has the matching mini offer once`, after === 1, `found ${after}`)
}
await open('/scan/bevestigd/')
{
  const n = await page.locator('[data-mini-offer]').count()
  check('/scan/bevestigd/ shows the mini offer once', n === 1, `found ${n}`)
}

// Website check: stub the API, check the offer sits inside a matching point.
{
  const p = await context.newPage()
  await p.route('**/api/websitecheck/**', (route) =>
    route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({
        ok: true,
        domein: 'voorbeeld.nl',
        letOp: 2,
        punten: [
          { id: 'wordpress', status: 'let-op', titel: 'WordPress 6.1 loopt achter', uitleg: 'x' },
          { id: 'telefoon', status: 'let-op', titel: 'Telefoonnummer is geen link', uitleg: 'x' },
          { id: 'titel', status: 'goed', titel: 'Paginatitel aanwezig', uitleg: 'x' },
        ],
      }),
    }),
  )
  await open('/websitecheck/', p)
  const offerBefore = await p.locator('[data-mini-offer]').isVisible()
  check('/websitecheck/ mini offer is hidden before the result', !offerBefore)
  await p.fill('#wc-url', 'voorbeeld.nl')
  await p.click('#wc-submit')
  await p.waitForSelector('#wc-result:not([hidden])')
  const inWp = await p.locator('.wc-item').nth(0).locator('[data-cta-line="within"]').count()
  const inTel = await p.locator('.wc-item').nth(1).locator('[data-cta-line="within"]').count()
  check('/websitecheck/ result shows the offer inside the WordPress point', inWp === 1)
  check('/websitecheck/ result leaves unrelated points alone', inTel === 0)
  check('/websitecheck/ mini offer shows after the result', await p.locator('[data-mini-offer]').isVisible())
  await p.close()
}

// Calculator: the per-month figure and the offer inside the result.
await open('/rekentool/')
{
  const month = (await page.locator('#out-lost-month').textContent())?.trim() ?? ''
  check('/rekentool/ shows the loss per month', /€\s?\d/.test(month), month)
  const within = await page.locator('aside [data-cta-line="within"]').count()
  check('/rekentool/ result has the offer inside it', within === 1, `found ${within}`)
}

// The landing pages carry the result name, not "scan" or "check".
for (const path of ['/scan/', '/websitecheck/']) {
  await open(path)
  const h1 = (await page.locator('h1').first().textContent())?.trim() ?? ''
  const title = await page.title()
  check(`${path} H1 and title name the result`, !/scan|check/i.test(h1) && !/^gratis (scan|websitecheck)/i.test(title), `${h1} / ${title}`)
}

// ------------------------------------------------------------------ links answer 200
console.log('\n=== Every magnet and mini-offer link answers 200 ===')
{
  const hrefs = new Set()
  for (const path of ['/gratis/', '/klein-beginnen/']) {
    await open(path)
    for (const h of await page.locator('main a[href^="/"]').evaluateAll((as) => as.map((a) => a.getAttribute('href')))) {
      hrefs.add(h.split('#')[0])
    }
  }
  hrefs.add('/gratis/')
  hrefs.add('/klein-beginnen/')
  for (const h of hrefs) {
    const res = await page.request.get(`${BASE}${h}`)
    check(`${h} answers 200`, res.status() === 200, `status ${res.status()}`)
  }
  await open('/')
  check('header links to /gratis/', (await page.locator('header a[href="/gratis/"]').count()) >= 1)
  const foot = await page.locator('footer').evaluate((f) => [...f.querySelectorAll('a')].map((a) => a.getAttribute('href')))
  for (const h of ['/websitecheck/', '/scan/', '/rekentool/', '/advertentievideos/', '/klein-beginnen/']) {
    check(`footer links to ${h}`, foot.includes(h))
  }
}

// ------------------------------------------------------------------ the two new forms
console.log('\n=== New forms: empty email, honeypot, source tag ===')
for (const f of [
  { path: '/rekentool/?bron=test', form: '#rekentool-mail', source: 'rekentool', fill: async () => {} },
  {
    path: '/advertentievideos/?bron=test',
    form: '#ad-form',
    source: 'advertentievideos',
    fill: async (p) => {
      await p.fill('#ad-link', 'https://www.facebook.com/ads/library/?id=123')
      await p.fill('#ad-shop', 'voorbeeldshop.nl')
    },
  },
]) {
  const p = await context.newPage()
  const posts = []
  await p.route('**/*sibforms.com/**', (route) => {
    posts.push(route.request().postData() ?? '')
    return route.fulfill({ contentType: 'application/json', body: '{"success":true}' })
  })
  await open(f.path, p)
  const form = p.locator(f.form)
  await f.fill(p)
  await form.locator('button[type="submit"]').click()
  await p.waitForTimeout(300)
  check(`${f.form} refuses an empty email`, posts.length === 0, `${posts.length} posts`)

  await form.locator('input[name="EMAIL"]').fill('test@voorbeeld.nl')
  await form.locator('input[name="email_address_check"]').evaluate((el) => (el.value = 'bot'))
  await form.locator('button[type="submit"]').click()
  await p.waitForTimeout(300)
  check(`${f.form} refuses a filled honeypot`, posts.length === 0, `${posts.length} posts`)

  await form.locator('input[name="email_address_check"]').evaluate((el) => (el.value = ''))
  await form.locator('button[type="submit"]').click()
  await p.waitForTimeout(500)
  const body = posts[0] ?? '' // multipart/form-data: values are plain text
  check(`${f.form} posts once to Brevo`, posts.length === 1, `${posts.length} posts`)
  check(`${f.form} sends source and bron in SCAN_PROGRAMMAS`, body.includes(`${f.source} | bron=test`), body.slice(0, 200))
  const done = p.locator(`${f.form}-done`)
  check(`${f.form} shows the done card`, await done.isVisible())
  await p.close()
}

// The channel tag survives a click-through: land on /gratis/?bron=linkedin, go to the
// calculator, sign up there.
{
  const p = await context.newPage()
  const posts = []
  await p.route('**/*sibforms.com/**', (route) => {
    posts.push(route.request().postData() ?? '')
    return route.fulfill({ contentType: 'application/json', body: '{"success":true}' })
  })
  await open('/gratis/?bron=linkedin', p)
  await p.click('[data-magnet="receptionist"] a')
  await p.waitForURL('**/rekentool/')
  await p.locator('#rekentool-mail input[name="EMAIL"]').fill('test@voorbeeld.nl')
  await p.locator('#rekentool-mail button[type="submit"]').click()
  await p.waitForTimeout(500)
  check('bron from the landing page reaches a form one click later', (posts[0] ?? '').includes('rekentool | bron=linkedin'), `${posts.length} posts`)
  await p.close()
}

// ------------------------------------------------------------------ phone widths
console.log('\n=== No horizontal scroll at 390 and 320 ===')
for (const width of [390, 320]) {
  const p = await browser.newPage({ viewport: { width, height: 800 } })
  for (const path of ['/', '/gratis/', '/klein-beginnen/', '/rekentool/', '/advertentievideos/', '/websitecheck/', '/scan/', '/scan/bevestigd/']) {
    await open(path, p)
    const over = await p.evaluate(() => document.documentElement.scrollWidth - window.innerWidth)
    check(`${path} @${width}: no horizontal scroll`, over <= 0, `${over}px over`)
  }
  await p.close()
}

// ------------------------------------------------------------------ Klantkraan, not the founder
console.log('\n=== No founder name on the magnet pages ===')
for (const path of ['/scan/', '/scan/bevestigd/', '/websitecheck/', '/rekentool/', '/advertentievideos/', '/gratis/', '/klein-beginnen/']) {
  await open(path)
  const html = await page.content()
  check(`${path} never says the founder's name`, !/davy/i.test(html)) // copy-lint-ok
}

await browser.close()
console.log(`\n${passes} passed, ${fails} failed`)
process.exit(fails ? 1 : 0)
