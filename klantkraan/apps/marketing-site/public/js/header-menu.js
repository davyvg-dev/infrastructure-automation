// Hamburger menu disclosure — vanilla JS, ES module.
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
