// Voice-demo call-me-back form — POST /api/voice-demo/call on the Worker.
// Externalised so it loads under CSP `script-src 'self'` (no inline allowed).
// Reusable: the form carries data-demo="<slug>"; copy per future demo page.
//
// astro:page-load aware so ClientRouter SPA transitions re-bind the form.

const PHONE_RE = /^[+0-9 ()-]{8,24}$/

function initVoiceDemoForm() {
  const form = document.getElementById('voice-demo-form')
  const submitBtn = document.getElementById('voice-demo-submit')
  if (!form || !submitBtn || form.dataset.kkInit) return
  form.dataset.kkInit = '1'

  const phoneEl = document.getElementById('voice-demo-phone')
  const phoneErr = document.getElementById('voice-demo-phone-error')
  const formError = document.getElementById('voice-demo-error')
  const successCard = document.getElementById('voice-demo-success')

  const idleLabel = submitBtn.textContent.trim()
  const submittingLabel = submitBtn.dataset.submitting ?? idleLabel

  form.addEventListener('submit', async (e) => {
    e.preventDefault()
    formError?.classList.add('hidden')
    successCard?.classList.add('hidden')

    const phone = phoneEl?.value.trim() ?? ''
    if (!PHONE_RE.test(phone)) {
      phoneErr?.classList.remove('hidden')
      return
    }
    phoneErr?.classList.add('hidden')

    const language =
      form.querySelector('input[name="voice-demo-language"]:checked')?.value ?? 'en'

    submitBtn.disabled = true
    submitBtn.textContent = submittingLabel
    try {
      const res = await fetch('https://api.klantkraan.nl/api/voice-demo/call', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ demo: form.dataset.demo, phone, language }),
      })
      if (res.ok) {
        successCard?.classList.remove('hidden')
        form.classList.add('hidden')
        return
      }
      const body = await res.json().catch(() => ({}))
      if (formError) {
        formError.textContent =
          body.error === 'country_not_supported'
            ? formError.dataset.msgCountry
            : body.error === 'rate_limited'
              ? formError.dataset.msgRate
              : body.error === 'invalid_phone'
                ? formError.dataset.msgPhone
                : formError.dataset.msgGeneric
        formError.classList.remove('hidden')
      }
    } catch {
      if (formError) {
        formError.textContent = formError.dataset.msgGeneric
        formError.classList.remove('hidden')
      }
    } finally {
      submitBtn.disabled = false
      submitBtn.textContent = idleLabel
    }
  })
}

initVoiceDemoForm()
document.addEventListener('astro:page-load', initVoiceDemoForm)
