// Source tag for every Brevo form (/scan, /websitecheck, /rekentool,
// /advertentievideos). There is no analytics script (CSP and choice), so each form
// writes where it came from into SCAN_PROGRAMMAS:
//   "<source> | bron=<tag> | <what the visitor typed>"
// <tag> is ?bron= from the page URL (ads, mails and LinkedIn links set it), or the
// one bron-keep.js saved earlier in this visit; kept to [a-z0-9_-]. Both the tag
// and the typed part are left out when empty.

export function bron() {
  let raw = new URLSearchParams(window.location.search).get('bron') || ''
  if (!raw) {
    try {
      raw = window.sessionStorage.getItem('kk-bron') || ''
    } catch {
      /* storage blocked: no tag */
    }
  }
  return raw.toLowerCase().replace(/[^a-z0-9_-]/g, '').slice(0, 40)
}

/** Rewrites SCAN_PROGRAMMAS in a FormData built from one of the Brevo forms. */
export function tagSource(fd, source) {
  const tag = bron()
  const own = String(fd.get('SCAN_PROGRAMMAS') || '').trim()
  const parts = [source, tag && `bron=${tag}`, own && own !== source ? own : '']
  fd.set('SCAN_PROGRAMMAS', parts.filter(Boolean).join(' | ').slice(0, 200))
  return fd
}
