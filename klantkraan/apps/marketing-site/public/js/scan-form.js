// Gratis scan (/scan): progressive enhancement over the native form post in
// src/pages/scan.astro. The form posts to Brevo's own form endpoint; this
// script sends the same fields with fetch() (Brevo answers JSON when asked
// with ?isAjax=1, exactly as its own embed script does) and swaps the form
// for the pre-rendered "Bijna klaar" card. All copy lives in the page markup.
// Externalised so it loads under CSP `script-src 'self'` (no inline allowed).
//
// astro:page-load aware so ClientRouter SPA transitions re-bind the form.

function initScanForm() {
  const form = document.getElementById('scan-form')
  if (!form || form.dataset.kkInit) return
  form.dataset.kkInit = '1'

  const doneEl = document.getElementById('scan-done')
  const errorEl = document.getElementById('scan-error')
  const submitBtn = document.getElementById('scan-submit')

  function showDone() {
    form.hidden = true
    if (!doneEl) return
    doneEl.hidden = false
    doneEl.focus({ preventScroll: true })
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
  function showError() {
    if (errorEl) errorEl.hidden = false
    if (submitBtn) submitBtn.disabled = false
  }

  form.addEventListener('submit', (event) => {
    // The browser has already checked the required fields and the e-mail shape.
    event.preventDefault()
    if (errorEl) errorEl.hidden = true
    if (submitBtn) submitBtn.disabled = true

    void fetch(`${form.action}?isAjax=1`, { method: 'POST', body: new FormData(form) })
      .then((res) => res.json())
      .then((body) => (body && body.success ? showDone() : showError()))
      .catch(showError)
  })
}

initScanForm()
document.addEventListener('astro:page-load', initScanForm)
