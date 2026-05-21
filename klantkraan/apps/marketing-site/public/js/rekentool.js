// ROI calculator — reactive on every input, no framework.
// Externalised so it loads under CSP `script-src 'self'` (no inline allowed).
// Pricing tiers and conversion assumption mirror rekentool.astro's "Hoe wij rekenen" section.
//
// astro:page-load aware so ClientRouter SPA transitions re-bind the inputs.

const TIERS = { lite: 349, pro: 599, max: 849 }
const CONVERSION = 0.33

const eurFmt = new Intl.NumberFormat('nl-NL', {
  style: 'currency',
  currency: 'EUR',
  maximumFractionDigits: 0,
})
const numFmt = new Intl.NumberFormat('nl-NL', { maximumFractionDigits: 0 })

function readNumber(el, fallback) {
  if (!el) return fallback
  const n = Number(el.value)
  return Number.isFinite(n) && n >= 0 ? n : fallback
}

function formatPayback(monthly, lostRevenuePerYear) {
  if (lostRevenuePerYear <= 0) return 'n.v.t.'
  const lostPerMonth = lostRevenuePerYear / 12
  if (lostPerMonth <= 0) return 'n.v.t.'
  const months = monthly / lostPerMonth
  if (months < 1) return '< 1 maand'
  if (months > 60) return '> 5 jaar'
  return `${months.toFixed(1)} maand`
}

function initRekentool() {
  const callsEl = document.getElementById('calls')
  const missedEl = document.getElementById('missed')
  const valueEl = document.getElementById('value')
  if (!callsEl || callsEl.dataset.kkInit) return
  callsEl.dataset.kkInit = '1'

  const outMissed = document.getElementById('out-missed-year')
  const outLost = document.getElementById('out-lost-revenue')
  const outPaybackLite = document.getElementById('out-payback-lite')
  const outPaybackPro = document.getElementById('out-payback-pro')
  const outPaybackMax = document.getElementById('out-payback-max')

  function recompute() {
    const calls = readNumber(callsEl, 0)
    const missedPct = Math.min(100, readNumber(missedEl, 0))
    const value = readNumber(valueEl, 0)

    const missedPerYear = Math.round(calls * 52 * (missedPct / 100))
    const lostRevenue = Math.round(missedPerYear * value * CONVERSION)

    if (outMissed) outMissed.textContent = numFmt.format(missedPerYear)
    if (outLost) outLost.textContent = eurFmt.format(lostRevenue)
    if (outPaybackLite) outPaybackLite.textContent = formatPayback(TIERS.lite, lostRevenue)
    if (outPaybackPro) outPaybackPro.textContent = formatPayback(TIERS.pro, lostRevenue)
    if (outPaybackMax) outPaybackMax.textContent = formatPayback(TIERS.max, lostRevenue)
  }

  for (const el of [callsEl, missedEl, valueEl]) {
    if (el) el.addEventListener('input', recompute)
  }
  recompute()
}

initRekentool()
document.addEventListener('astro:page-load', initRekentool)
