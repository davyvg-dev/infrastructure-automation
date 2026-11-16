// Saves ?bron= (the channel tag on ad, mail and LinkedIn links) for this visit, so
// a visitor who lands on /gratis/?bron=linkedin and clicks through to a form still
// signs up with that tag (read back in bron.js). Session storage only; blocked
// storage simply means no tag. Loaded on every page by Base.astro.

function keepBron() {
  const tag = new URLSearchParams(window.location.search).get('bron')
  if (!tag) return
  try {
    window.sessionStorage.setItem('kk-bron', tag.toLowerCase().replace(/[^a-z0-9_-]/g, '').slice(0, 40))
  } catch {
    /* private mode or storage off */
  }
}

keepBron()
document.addEventListener('astro:page-load', keepBron)
