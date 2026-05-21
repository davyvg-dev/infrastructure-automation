// Hamburger menu + Voor-wie? dropdown — vanilla JS, ES module.
// Externalised so it loads under CSP `script-src 'self'` (no inline allowed).
// See klantkraan/apps/marketing-site/public/_headers for the policy.
//
// astro:page-load aware: Astro 5 ClientRouter swaps the document body on
// client-side navigation, so init must run on every page transition, not
// just once at DOMContentLoaded.

function initHeaderMenu() {
  const toggle = document.getElementById('mobile-menu-toggle')
  const menu = document.getElementById('mobile-menu')

  if (toggle && menu && !toggle.dataset.kkInit) {
    toggle.dataset.kkInit = '1'

    const openIcons = toggle.querySelectorAll('[data-icon-open]')
    const closeIcons = toggle.querySelectorAll('[data-icon-close]')

    function setOpen(open) {
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false')
      toggle.setAttribute('aria-label', open ? 'Menu sluiten' : 'Menu openen')
      menu.hidden = !open
      menu.classList.toggle('hidden', !open)
      openIcons.forEach((el) => el.classList.toggle('hidden', open))
      closeIcons.forEach((el) => el.classList.toggle('hidden', !open))
    }

    toggle.addEventListener('click', () => {
      const isOpen = toggle.getAttribute('aria-expanded') === 'true'
      setOpen(!isOpen)
    })

    menu.addEventListener('click', (e) => {
      if (e.target.tagName === 'A') setOpen(false)
    })
  }

  // Desktop dropdown: outside-click + Escape close. Idempotent — guarded by
  // the dropdown's own dataset flag so it doesn't double-listen.
  const desktopDropdown = document.querySelector('[data-branches-dropdown="desktop"]')
  if (desktopDropdown && !desktopDropdown.dataset.kkInit) {
    desktopDropdown.dataset.kkInit = '1'

    document.addEventListener('click', (e) => {
      if (!desktopDropdown.open) return
      if (!desktopDropdown.contains(e.target)) {
        desktopDropdown.open = false
      }
    })
  }
}

// Document-level Escape handler — attaches once for the page lifetime even
// across view transitions (because the document object survives).
if (!window.__kkEscapeAttached) {
  window.__kkEscapeAttached = true
  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape') return

    const toggle = document.getElementById('mobile-menu-toggle')
    if (toggle && toggle.getAttribute('aria-expanded') === 'true') {
      toggle.click()
      toggle.focus()
      return
    }

    const dd = document.querySelector('[data-branches-dropdown="desktop"]')
    if (dd && dd.open) {
      dd.open = false
      dd.querySelector('summary')?.focus()
    }
  })
}

initHeaderMenu()
document.addEventListener('astro:page-load', initHeaderMenu)
