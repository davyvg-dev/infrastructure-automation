// context7: Lenis 1.3 (/darkroomengineering/lenis, 2026-10-20)
//
// Wheel scrolling with a little weight to it. Bundled by Astro into /_astro/,
// so it stays inside the CSP's script-src 'self'. Touch keeps native scrolling
// (syncTouch is off by default): phones already scroll smoothly, and faking it
// there feels worse, not better. Lenis honours prefers-reduced-motion itself.
//
// Rebuilt on every astro:page-load because ClientRouter swaps <html>'s
// attributes (dropping the classes Lenis sets) and resets the scroll position
// behind Lenis's back. Anchors stay native: ClientRouter already handles
// same-page hash links, and two owners of one click fight.
import Lenis from 'lenis'

let lenis: Lenis | undefined

document.addEventListener('astro:page-load', () => {
  lenis?.destroy()
  lenis = new Lenis({
    autoRaf: true,
    lerp: 0.12,
    allowNestedScroll: true,
    stopInertiaOnNavigate: true,
  })
})

document.addEventListener('astro:before-swap', () => {
  lenis?.destroy()
  lenis = undefined
})
