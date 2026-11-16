// The two small Brevo forms added for the lead magnets: "Stuur mij deze
// berekening" on /rekentool/ and the free openings request on
// /advertentievideos/. Same fetch upgrade as scan-form.js (Brevo answers JSON with
// ?isAjax=1), plus the source tag and a honeypot check. Each form carries
//   data-magnet-form="<source>"   and a done card with id "<form id>-done".
// Optional data-klus-prefix is put in front of SCAN_KLUS.
// Externalised so it loads under CSP `script-src 'self'`.
//
// astro:page-load aware so ClientRouter SPA transitions re-bind the forms.

import { tagSource } from '/js/bron.js'

function initMagnetForms() {
  for (const form of document.querySelectorAll('form[data-magnet-form]')) {
    if (form.dataset.kkInit) continue
    form.dataset.kkInit = '1'

    const source = form.dataset.magnetForm
    const done = document.getElementById(`${form.id}-done`)
    const errorEl = form.querySelector('[data-form-error]')
    const btn = form.querySelector('button[type="submit"]')
    const trap = form.querySelector('input[name="email_address_check"]')

    form.addEventListener('submit', (event) => {
      // The browser has already checked the required fields and the e-mail shape.
      event.preventDefault()
      if (trap && trap.value) return
      if (errorEl) errorEl.hidden = true
      if (btn) btn.disabled = true

      const fd = tagSource(new FormData(form), source)
      const prefix = form.dataset.klusPrefix
      if (prefix) fd.set('SCAN_KLUS', `${prefix}${fd.get('SCAN_KLUS') || ''}`.slice(0, 500))

      void fetch(`${form.action}?isAjax=1`, { method: 'POST', body: fd })
        .then((res) => res.json())
        .then((body) => {
          if (!body || !body.success) throw new Error('brevo')
          form.hidden = true
          if (done) {
            done.hidden = false
            done.focus({ preventScroll: true })
            done.scrollIntoView({ behavior: 'smooth', block: 'center' })
          }
        })
        .catch(() => {
          if (errorEl) errorEl.hidden = false
          if (btn) btn.disabled = false
        })
    })
  }
}

initMagnetForms()
document.addEventListener('astro:page-load', initMagnetForms)
