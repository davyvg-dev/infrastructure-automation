// Full-screen demo launcher for /demo on mobile.
// Externalised so it loads under CSP `script-src 'self'` (no inline allowed).
// See klantkraan/apps/marketing-site/public/_headers for the policy.
//
// Robust model (why it's built this way):
//  - The overlay is a FULL-SCREEN solid backdrop (position:fixed; inset:0). It is
//    NEVER resized, so the marketing page can never peek out behind the chat — not
//    mid keyboard-animation, not when visualViewport math is imperfect on old iOS.
//    (The previous version sized the backdrop itself to the visual viewport, so it
//    shrank when the keyboard opened and the page bled through underneath.)
//  - The body is scroll-locked with the position:fixed technique so iOS can't
//    rubber-band the page into view around the overlay.
//  - Only the IFRAME is sized to the visual viewport, so the chat's input row sits
//    just above the on-screen keyboard. If those numbers are ever off, the user
//    sees the backdrop, never the page.
//
// astro:page-load aware: Astro 5 ClientRouter swaps the document body on
// client-side navigation, so element lookups happen at call time and the
// document-level listeners attach once for the page lifetime.

// Default demo (trades). A vertical demo page (e.g. /demo/sportscholen/) points the
// overlay elsewhere via a data-demo-src attribute on #demo-overlay; the allowed
// message origin is derived from whichever src is active.
const DEFAULT_DEMO_SRC = 'https://demo-168-119-173-25.sslip.io/?embed=1'
const vv = window.visualViewport

function overlay() {
  return document.getElementById('demo-overlay')
}

function demoSrc() {
  const el = overlay()
  return (el && el.dataset.demoSrc) || DEFAULT_DEMO_SRC
}

function demoOrigin() {
  return new URL(demoSrc()).origin
}

function frame() {
  const el = overlay()
  return el && el.querySelector('iframe')
}

let savedScrollY = 0

// Lock the background page so it can't scroll or rubber-band into view behind the
// overlay. position:fixed is the only reliable lock on iOS; overflow:hidden alone
// is ignored once the keyboard is open.
function lockBody() {
  savedScrollY = window.scrollY || window.pageYOffset || 0
  const b = document.body
  b.style.position = 'fixed'
  b.style.top = -savedScrollY + 'px'
  b.style.left = '0'
  b.style.right = '0'
  b.style.width = '100%'
  document.documentElement.style.overflow = 'hidden'
}

function unlockBody() {
  const b = document.body
  b.style.position = ''
  b.style.top = ''
  b.style.left = ''
  b.style.right = ''
  b.style.width = ''
  document.documentElement.style.overflow = ''
  window.scrollTo(0, savedScrollY)
}

// Size ONLY the iframe to the visible viewport (keyboard-aware). The backdrop stays
// full-screen, so this only places the chat — it can never uncover the page.
function sizeFrame() {
  const el = overlay()
  if (!el || el.classList.contains('hidden')) return
  const f = frame()
  if (!f) return
  const w = vv ? vv.width : window.innerWidth
  const h = vv ? vv.height : window.innerHeight
  const top = vv ? vv.offsetTop : 0
  const left = vv ? vv.offsetLeft : 0
  f.style.width = w + 'px'
  f.style.height = h + 'px'
  f.style.top = top + 'px'
  f.style.left = left + 'px'
}

// The keyboard open/close animation settles over a few hundred ms, and older iOS
// fires a single, sometimes-early resize. Re-measure a few times so the input ends
// up right above the keyboard rather than behind it or with a gap under it.
let settleTimer = null
function sizeFrameSettling() {
  sizeFrame()
  if (settleTimer) clearInterval(settleTimer)
  let n = 0
  settleTimer = setInterval(() => {
    sizeFrame()
    if (++n >= 6) { clearInterval(settleTimer); settleTimer = null }
  }, 100)
}

function openDemo() {
  const el = overlay()
  if (!el) return
  if (!frame()) {
    const f = document.createElement('iframe')
    f.src = demoSrc()
    f.title = 'Live chat met de digitale receptionist van Klantkraan'
    // Absolutely positioned inside the fixed backdrop; sizeFrame sets w/h/top/left.
    f.setAttribute('style', 'position:absolute;top:0;left:0;border:0;display:block;')
    el.appendChild(f)
  }
  el.classList.remove('hidden')
  el.setAttribute('aria-hidden', 'false')
  lockBody()
  sizeFrameSettling()
}

function closeDemo() {
  const el = overlay()
  if (!el) return
  el.classList.add('hidden')
  el.setAttribute('aria-hidden', 'true')
  // Drop the iframe so the session resets on next open (and stops any polling).
  const f = frame()
  if (f) f.remove()
  unlockBody()
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
    if (e.origin !== demoOrigin()) return
    const d = e.data
    if (d && d.type === 'klantkraan-widget' && d.action === 'close') closeDemo()
  })

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeDemo()
  })

  if (vv) {
    vv.addEventListener('resize', sizeFrameSettling)
    vv.addEventListener('scroll', sizeFrame)
  }
  window.addEventListener('orientationchange', sizeFrameSettling)
}

// If a prior /demo visit left the scroll lock on, clear it once we land on a
// page without the overlay.
document.addEventListener('astro:page-load', () => {
  if (!overlay()) unlockBody()
})
