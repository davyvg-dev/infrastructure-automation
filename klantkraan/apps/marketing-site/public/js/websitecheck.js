// Websitecheck (/websitecheck): asks /api/websitecheck/ for the points and
// writes them into the page; then, if the visitor wants it, posts the request
// into the same Brevo form as /scan (see src/pages/websitecheck.astro).
// Everything is written with textContent: the texts contain words taken from
// the checked site (its title, its heading) and must never run as markup.
// Externalised so it loads under CSP `script-src 'self'` (no inline allowed).
//
// astro:page-load aware so ClientRouter SPA transitions re-bind the form.

import { tagSource } from '/js/bron.js'

const REDENEN = {
  adres: 'Dat adres herkennen we niet. Typ het zoals het op uw visitekaartje staat, bijvoorbeeld uwbedrijf.nl.',
  onbereikbaar: 'We kregen uw site niet te zien. Klopt het adres? Dan is de site nu van buitenaf niet bereikbaar.',
  geweigerd: 'Uw site laat geautomatiseerde bezoekers niet toe, dus deze check kan hem niet lezen. Vul hieronder uw e-mailadres in, dan kijken we er zelf naar.',
  leeg: 'Op dat adres staat geen gewone webpagina die we kunnen lezen.',
  druk: 'Dat waren veel checks achter elkaar. Wacht een minuut en probeer het dan opnieuw.',
}
const MARK = { goed: '✓', 'let-op': '!', onbekend: '?' }

function el(tag, className, text) {
  const node = document.createElement(tag)
  if (className) node.className = className
  if (text) node.textContent = text
  return node
}

function initWebsitecheck() {
  const form = document.getElementById('wc-form')
  if (!form || form.dataset.kkInit) return
  form.dataset.kkInit = '1'

  const input = document.getElementById('wc-url')
  const errorEl = document.getElementById('wc-error')
  const submitBtn = document.getElementById('wc-submit')
  const result = document.getElementById('wc-result')
  const head = document.getElementById('wc-head')
  const sum = document.getElementById('wc-sum')
  const list = document.getElementById('wc-list')
  const again = document.getElementById('wc-again')
  const lead = document.getElementById('wc-lead')
  const leadError = document.getElementById('wc-lead-error')
  const leadBtn = document.getElementById('wc-lead-submit')
  const done = document.getElementById('wc-done')
  // The matching mini offer: a line inside each point it fixes, the card after the result.
  const fix = document.getElementById('wc-fix')
  const fixes = new Set((fix?.dataset.fixes || '').split(',').filter(Boolean))
  const offer = document.getElementById('wc-offer')
  const klus = document.getElementById('SCAN_KLUS')
  const bedrijf = document.getElementById('SCAN_BEDRIJF')
  const label = submitBtn.textContent

  function fail(reden, domein) {
    errorEl.textContent = REDENEN[reden] || REDENEN.onbereikbaar
    errorEl.hidden = false
    // A site that refuses the check can still be looked at by hand.
    if (reden === 'geweigerd' && domein) {
      bedrijf.value = domein
      klus.value = `Websitecheck ${domein}: de site liet de automatische check niet toe.`
      lead.hidden = false
    }
  }

  function show(data) {
    const n = data.letOp
    head.textContent = data.domein
    sum.textContent =
      n === 0
        ? 'Op deze punten staat uw homepage er goed voor.'
        : n === 1
          ? 'Eén punt vraagt aandacht. De rest staat goed.'
          : `${n} punten vragen aandacht. Die staan bovenaan.`
    list.replaceChildren(
      ...data.punten.map((p) => {
        const li = el('li', 'wc-item')
        li.dataset.status = p.status
        const mark = el('span', 'wc-mark', MARK[p.status] || '?')
        mark.setAttribute('aria-hidden', 'true')
        const title = el('h3', '', p.titel)
        const sr = el('span', 'wc-sr', p.status === 'goed' ? 'Goed: ' : p.status === 'let-op' ? 'Let op: ' : 'Onbekend: ')
        title.prepend(sr)
        li.append(mark, title, el('p', '', p.uitleg))
        if (p.zelf) {
          const zelf = el('p', 'wc-zelf')
          zelf.append(el('b', '', 'Zelf nakijken: '), p.zelf)
          li.append(zelf)
        }
        if (fix && p.status === 'let-op' && fixes.has(p.id)) li.append(fix.content.cloneNode(true))
        return li
      }),
    )
    const punten = data.punten.filter((p) => p.status === 'let-op').map((p) => p.titel)
    bedrijf.value = data.domein
    klus.value = `Websitecheck ${data.domein}: ${punten.length ? punten.join('; ') : 'geen punten gevonden'}`.slice(0, 490)

    form.hidden = true
    result.hidden = false
    lead.hidden = false
    if (offer) offer.hidden = false
    result.focus({ preventScroll: true })
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  form.addEventListener('submit', (event) => {
    event.preventDefault()
    errorEl.hidden = true
    lead.hidden = true
    const value = input.value.trim()
    if (!value) {
      fail('adres')
      return
    }
    submitBtn.disabled = true
    submitBtn.textContent = 'We lezen uw homepage…'
    void fetch(`/api/websitecheck/?url=${encodeURIComponent(value)}`, { headers: { Accept: 'application/json' } })
      .then((res) => res.json())
      .then((data) => (data && data.ok ? show(data) : fail(data && data.reden, data && data.domein)))
      .catch(() => fail('onbereikbaar'))
      .finally(() => {
        submitBtn.disabled = false
        submitBtn.textContent = label
      })
  })

  again.addEventListener('click', () => {
    result.hidden = true
    lead.hidden = true
    if (offer) offer.hidden = true
    form.hidden = false
    input.value = ''
    input.focus()
  })

  lead.addEventListener('submit', (event) => {
    // The browser has already checked the e-mail shape.
    event.preventDefault()
    leadError.hidden = true
    leadBtn.disabled = true
    void fetch(`${lead.action}?isAjax=1`, { method: 'POST', body: tagSource(new FormData(lead), 'websitecheck') })
      .then((res) => res.json())
      .then((body) => {
        if (!body || !body.success) throw new Error('brevo')
        form.hidden = true
        result.hidden = true
        lead.hidden = true
        done.hidden = false
        done.focus({ preventScroll: true })
        window.scrollTo({ top: 0, behavior: 'smooth' })
      })
      .catch(() => {
        leadError.hidden = false
        leadBtn.disabled = false
      })
  })
}

initWebsitecheck()
document.addEventListener('astro:page-load', initWebsitecheck)
