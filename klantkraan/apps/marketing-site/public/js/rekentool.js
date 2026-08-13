// ROI calculator — reactive on every input, no framework.
// Externalised so it loads under CSP `script-src 'self'` (no inline allowed).
// Pricing tiers and conversion assumption mirror rekentool.astro's "Hoe wij rekenen" section.
//
// astro:page-load aware so ClientRouter SPA transitions re-bind the inputs.

const TIERS = { chat: 299, compleet: 499 }
const CONVERSION = 0.33

function readNumber(el, fallback) {
  if (!el) return fallback
  const n = Number(el.value)
  return Number.isFinite(n) && n >= 0 ? n : fallback
}

function initRekentool() {
  const callsEl = document.getElementById('calls')
  const missedEl = document.getElementById('missed')
  const valueEl = document.getElementById('value')
  if (!callsEl || callsEl.dataset.kkInit) return
  callsEl.dataset.kkInit = '1'

  // The same script serves /rekentool/, /en/rekentool/ and /es/rekentool/. Pick
  // locale + strings from <html lang>, which Base.astro stamps per page. Computed
  // inside init (not at module load) so an SPA switch between the pages picks the
  // right lang.
  const lang = (document.documentElement.lang || 'nl').toLowerCase().slice(0, 2)
  const locale = lang === 'en' ? 'en-GB' : lang === 'es' ? 'es-ES' : 'nl-NL'
  const eurFmt = new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: 'EUR',
    maximumFractionDigits: 0,
  })
  const numFmt = new Intl.NumberFormat(locale, { maximumFractionDigits: 0 })
  const stringsByLang = {
    nl: { na: 'n.v.t.', lt1: '< 1 maand', gt5: '> 5 jaar', unit: 'maand' },
    en: { na: 'n/a', lt1: '< 1 month', gt5: '> 5 years', unit: 'months' },
    es: { na: 'n/d', lt1: '< 1 mes', gt5: '> 5 años', unit: 'meses' },
  }
  const strings = stringsByLang[lang] || stringsByLang.nl

  function formatPayback(monthly, lostRevenuePerYear) {
    if (lostRevenuePerYear <= 0) return strings.na
    const lostPerMonth = lostRevenuePerYear / 12
    if (lostPerMonth <= 0) return strings.na
    const months = monthly / lostPerMonth
    if (months < 1) return strings.lt1
    if (months > 60) return strings.gt5
    return `${months.toFixed(1)} ${strings.unit}`
  }

  const outMissed = document.getElementById('out-missed-year')
  const outLost = document.getElementById('out-lost-revenue')
  const outPaybackChat = document.getElementById('out-payback-chat')
  const outPaybackCompleet = document.getElementById('out-payback-compleet')

  function recompute() {
    const calls = readNumber(callsEl, 0)
    const missedPct = Math.min(100, readNumber(missedEl, 0))
    const value = readNumber(valueEl, 0)

    const missedPerYear = Math.round(calls * 52 * (missedPct / 100))
    const lostRevenue = Math.round(missedPerYear * value * CONVERSION)

    if (outMissed) outMissed.textContent = numFmt.format(missedPerYear)
    if (outLost) outLost.textContent = eurFmt.format(lostRevenue)
    if (outPaybackChat) outPaybackChat.textContent = formatPayback(TIERS.chat, lostRevenue)
    if (outPaybackCompleet)
      outPaybackCompleet.textContent = formatPayback(TIERS.compleet, lostRevenue)
  }

  for (const el of [callsEl, missedEl, valueEl]) {
    if (el) el.addEventListener('input', recompute)
  }
  recompute()
}

// E-mailcursus opt-in — progressive enhancement over the native form post.
// All user-facing copy lives in the page markup (per locale); this script only
// toggles the pre-rendered success/error elements.

const CURSUS_API = 'https://demo.klantkraan.nl/api/cursus'

function initCursusForm() {
  const form = document.getElementById('cursus-form')
  if (!form || form.dataset.kkInit) return
  form.dataset.kkInit = '1'

  const successEl = document.getElementById('cursus-success')
  const errorEl = document.getElementById('cursus-error')
  const submitBtn = document.getElementById('cursus-submit')

  function showSuccess() {
    form.classList.add('hidden')
    if (successEl) successEl.classList.remove('hidden')
  }
  function showError() {
    if (errorEl) errorEl.classList.remove('hidden')
    if (submitBtn) submitBtn.disabled = false
  }

  // A native (no-JS) post 303s back to this page with ?cursus=ok|fout.
  const flag = new URLSearchParams(window.location.search).get('cursus')
  if (flag === 'ok') showSuccess()
  if (flag === 'fout') showError()

  form.addEventListener('submit', (event) => {
    event.preventDefault()
    if (errorEl) errorEl.classList.add('hidden')
    if (submitBtn) submitBtn.disabled = true

    const data = new FormData(form)
    const value = (name) => String(data.get(name) ?? '').trim()

    void fetch(CURSUS_API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: value('email'),
        naam: value('naam'),
        // Honeypot rides along: a bot that filled it gets the server's silent drop.
        website: value('website'),
      }),
    })
      .then((res) => (res.ok ? showSuccess() : showError()))
      .catch(showError)
  })
}

initRekentool()
initCursusForm()
document.addEventListener('astro:page-load', () => {
  initRekentool()
  initCursusForm()
})
