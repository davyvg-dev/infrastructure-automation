// Full-screen demo launcher for /demo on mobile.
// Externalised so it loads under CSP `script-src 'self'` (no inline allowed).
// See klantkraan/apps/marketing-site/public/_headers for the policy.
//
// Why: on desktop the live receptionist sits inline in an iframe and behaves.
// On a phone an inline fixed-height iframe inside a scrolling page fights the
// on-screen keyboard — iOS scrolls the PAGE to reveal the focused input and the
// chat slides out of view ("the demo disappears"). Fix: on mobile we launch the
// chat into a fixed, full-viewport overlay that sits OUTSIDE the page scroll
// flow and is sized to window.visualViewport, so the keyboard shrinks the chat
// instead of hiding it.
//
// astro:page-load aware: Astro 5 ClientRouter swaps the document body on
// client-side navigation, so element lookups happen at call time and the
// document-level listeners attach once for the page lifetime.

const DEMO_SRC = 'https://demo-168-119-173-25.sslip.io/?embed=1'
const DEMO_ORIGIN = 'https://demo-168-119-173-25.sslip.io'
const vv = window.visualViewport

function overlay() {
  return document.getElementById('demo-overlay')
}

function unlockBody() {
  document.documentElement.style.overflow = ''
  document.body.style.overflow = ''
}

// Pin the overlay to the *visible* viewport in BOTH axes.
// Height matches the visual viewport so the on-screen keyboard shrinks the chat
// instead of hiding it. Width + left are pinned too: without them iOS sizes the
// position:fixed overlay to the (slightly wider) LAYOUT viewport, so the w-full
// iframe rendered a few px too wide and the chat's right edge was clipped on
// smaller iPhones. Position via top/left, not a transform — a transform on a
// position:fixed element is the classic iOS containing-block trap.
function sizeOverlay() {
  const el = overlay()
  if (!el || el.classList.contains('hidden')) return
  const de = document.documentElement
  const w = vv ? vv.width : de.clientWidth
  const h = vv ? vv.height : window.innerHeight
  const top = vv ? vv.offsetTop : 0
  const left = vv ? vv.offsetLeft : 0
  el.style.width = w + 'px'
  el.style.height = h + 'px'
  el.style.left = left + 'px'
  el.style.right = 'auto'
  el.style.top = top + 'px'
  el.style.transform = ''
}

function openDemo() {
  const el = overlay()
  if (!el) return
  if (!el.querySelector('iframe')) {
    const f = document.createElement('iframe')
    f.src = DEMO_SRC
    f.title = 'Live chat met de digitale receptionist van Klantkraan'
    f.className = 'block h-full w-full border-0'
    el.appendChild(f)
  }
  el.classList.remove('hidden')
  el.setAttribute('aria-hidden', 'false')
  document.documentElement.style.overflow = 'hidden'
  document.body.style.overflow = 'hidden'
  sizeOverlay()
}

function closeDemo() {
  unlockBody()
  const el = overlay()
  if (!el) return
  el.classList.add('hidden')
  el.setAttribute('aria-hidden', 'true')
  el.style.height = ''
  el.style.width = ''
  el.style.left = ''
  el.style.right = ''
  el.style.top = ''
  el.style.transform = ''
  // Drop the iframe so the session resets on next open (and stops any polling).
  const f = el.querySelector('iframe')
  if (f) f.remove()
}

if (!window.__kkDemoEmbed) {
  window.__kkDemoEmbed = true

  document.addEventListener('click', (e) => {
    const opener = e.target.closest && e.target.closest('[data-demo-open]')
    if (opener) {
      e.preventDefault()
      openDemo()
    }
  })

  // The embedded chat posts this when its own × (shown in embed mode) is tapped.
  window.addEventListener('message', (e) => {
    if (e.origin !== DEMO_ORIGIN) return
    const d = e.data
    if (d && d.type === 'klantkraan-widget' && d.action === 'close') closeDemo()
  })

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeDemo()
  })

  if (vv) {
    vv.addEventListener('resize', sizeOverlay)
    vv.addEventListener('scroll', sizeOverlay)
  }
}

// If a prior /demo visit left the scroll lock on, clear it once we land on a
// page without the overlay.
document.addEventListener('astro:page-load', () => {
  if (!overlay()) unlockBody()
})
