// Hamburger menu + Voor-wie? dropdown — vanilla JS, ES module.
// Externalised so it loads under CSP `script-src 'self'` (no inline allowed).
// See klantkraan/apps/marketing-site/public/_headers for the policy.

const toggle = document.getElementById('mobile-menu-toggle')
const menu = document.getElementById('mobile-menu')

if (toggle && menu) {
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

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
      setOpen(false)
      toggle.focus()
    }
  })

  menu.addEventListener('click', (e) => {
    if (e.target.tagName === 'A') setOpen(false)
  })
}

// Voor-wie? dropdown polish — close the desktop <details> when the user
// clicks outside or presses Escape. The dropdown still works without this
// JS (native <details> handles open/close on summary click) but the polish
// matches user expectations for a header dropdown.
const desktopDropdown = document.querySelector('[data-branches-dropdown="desktop"]')

if (desktopDropdown) {
  document.addEventListener('click', (e) => {
    if (!desktopDropdown.open) return
    if (!desktopDropdown.contains(e.target)) {
      desktopDropdown.open = false
    }
  })

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && desktopDropdown.open) {
      desktopDropdown.open = false
      const summary = desktopDropdown.querySelector('summary')
      if (summary) summary.focus()
    }
  })
}
