// Lead form — validate, POST /api/lead, render success/error state.
// Externalised so it loads under CSP `script-src 'self'` (no inline allowed).
// 409 'suppressed' is rendered as success to avoid leaking suppression-list
// membership (Worker contract: apps/api/src/routes/lead.ts).
//
// astro:page-load aware so ClientRouter SPA transitions re-bind the form.

// Mirror the Worker zod regex exactly.
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
const PHONE_RE = /^\+?[0-9 ()-]+$/

function show(el) {
  if (el) el.classList.remove('hidden')
}
function hide(el) {
  if (el) el.classList.add('hidden')
}

function initLeadForm() {
  const form = document.getElementById('lead-form')
  const submitBtn = document.getElementById('lead-submit')
  if (!form || !submitBtn || form.dataset.kkInit) return
  form.dataset.kkInit = '1'

  const formError = document.getElementById('lead-form-error')
  const successCard = document.getElementById('lead-success')
  const nameEl = document.getElementById('lead-name')
  const emailEl = document.getElementById('lead-email')
  const phoneEl = document.getElementById('lead-phone')
  const messageEl = document.getElementById('lead-message')
  const nameErr = document.getElementById('lead-name-error')
  const emailErr = document.getElementById('lead-email-error')
  const phoneErr = document.getElementById('lead-phone-error')
  const messageErr = document.getElementById('lead-message-error')

  function validate() {
    let ok = true
    const name = nameEl?.value.trim() ?? ''
    const email = emailEl?.value.trim() ?? ''
    const phone = phoneEl?.value.trim() ?? ''
    const message = messageEl?.value.trim() ?? ''

    if (name.length < 2) { show(nameErr); ok = false } else { hide(nameErr) }
    if (!EMAIL_RE.test(email)) { show(emailErr); ok = false } else { hide(emailErr) }

    if (phone.length > 0) {
      const validLen = phone.length >= 8 && phone.length <= 20
      if (!validLen || !PHONE_RE.test(phone)) { show(phoneErr); ok = false } else { hide(phoneErr) }
    } else { hide(phoneErr) }

    if (message.length < 1) { show(messageErr); ok = false } else { hide(messageErr) }

    return ok
  }

  // Labels come from the rendered button so the form works in any locale:
  // the idle label is whatever the server rendered; the busy label is a data attr.
  const idleLabel = submitBtn.textContent.trim()
  const submittingLabel = submitBtn.dataset.submitting ?? idleLabel

  function setSubmitting(submitting) {
    submitBtn.disabled = submitting
    submitBtn.textContent = submitting ? submittingLabel : idleLabel
  }

  function renderSuccess() {
    hide(form)
    show(successCard)
  }

  function renderError() {
    show(formError)
    setSubmitting(false)
  }

  const apiBase = form.dataset.apiBase ?? 'https://api.klantkraan.nl'

  form.addEventListener('submit', (event) => {
    event.preventDefault()
    hide(formError)
    if (!validate()) return

    const name = nameEl?.value.trim() ?? ''
    const email = emailEl?.value.trim() ?? ''
    const phone = phoneEl?.value.trim() ?? ''
    const message = messageEl?.value.trim() ?? ''

    const payload = phone.length > 0
      ? { name, email, message, phone }
      : { name, email, message }

    setSubmitting(true)

    void fetch(`${apiBase}/api/lead`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
      .then((res) => {
        if (res.status === 201 || res.status === 200 || res.status === 409) {
          renderSuccess()
          return
        }
        renderError()
      })
      .catch(() => {
        renderError()
      })
  })
}

initLeadForm()
document.addEventListener('astro:page-load', initLeadForm)
