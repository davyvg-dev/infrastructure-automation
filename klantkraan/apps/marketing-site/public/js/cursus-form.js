// E-mailcursus opt-in: progressive enhancement over the native form post in
// CursusForm.astro. All user-facing copy lives in the component markup (per
// locale); this script only toggles the pre-rendered success/error elements.
// Externalised so it loads under CSP `script-src 'self'` (no inline allowed).
//
// astro:page-load aware so ClientRouter SPA transitions re-bind the form.

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

initCursusForm()
document.addEventListener('astro:page-load', initCursusForm)
