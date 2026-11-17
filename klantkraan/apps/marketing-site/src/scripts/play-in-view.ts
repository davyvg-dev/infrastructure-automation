// The wire-and-lamp drawings that play a sequence (ServicesHero, CareDiagram,
// FollowUpDiagram, VariantsDiagram) mark their root with data-kk-play. Their CSS
// runs the sequence by itself, so a page whose scripts fail still ends with every
// lamp on. This script makes it play when the visitor actually sees it:
//
// - Until then the sequence is held at its start (lamps off, switches open).
// - "Seen" means every lamp of the drawing (whatever lights up, LAMPS below) sits
//   in the part of the screen that nothing covers: the sticky header and the
//   phone's bottom action bar are measured and cut off. So a drawing that rests
//   half under the bar waits, and one whose lamps are all on screen plays even if
//   its bottom edge is cut off. When its lamps cannot all fit in that part at once
//   (a landscape phone), it starts once the drawing fills most of it. A drawing
//   without lamps starts once nearly all of it is there.
// - Once started it plays to the end; it only pauses while fully off screen.
//
// It binds as soon as this module runs (module scripts run once the page is
// parsed). The first astro:page-load waits for the window load event, and on a
// slow phone the CSS had played the whole hero under the bar by then. A drawing
// that is not in view when bound is restarted from zero: an animation that has
// already finished is gone from getAnimations() and cannot be rewound.
//
// The CSS has no animation under reduced motion or without scripting, so then
// there is nothing to hold and the drawing is simply finished.
// Also bound on astro:page-load, so it runs after a ClientRouter navigation.

type Item = {
  el: HTMLElement
  anims: Animation[]
  started: boolean
  done: boolean
  /** whenSeen(): called once instead of playing animations. */
  go?: () => void
}

// What lights up: the lamps (hero, care, follow-up, the flow's appointment lamp),
// the hero's node lamp and the sixteen openings of the variants drawing.
const LAMPS = '[data-lamp], .main-lamp, .fan .op'
const START_RATIO = 0.9 // no lamps: this much of the drawing in view
const START_SHARE = 0.8 // lamps too far apart to fit: the drawing fills this much of the view
const THRESHOLDS = Array.from({ length: 21 }, (_, i) => i / 20)
// One style pass with every CSS animation in a drawing switched off makes them start over.
const RESET =
  '[data-kk-reset],[data-kk-reset]::before,[data-kk-reset]::after,[data-kk-reset] *,' +
  '[data-kk-reset] *::before,[data-kk-reset] *::after{animation:none!important}'

let items: Item[] = []
const byTarget = new Map<Element, Item>()
let io: IntersectionObserver | undefined
let insetKey = ''

/** Height of what covers the top and bottom edge: sticky or fixed full-width bars. */
function insets(): [number, number] {
  let top = 0
  let bottom = 0
  const vh = window.innerHeight
  for (const n of Array.from(document.body.children)) {
    const cs = getComputedStyle(n)
    if ((cs.position !== 'fixed' && cs.position !== 'sticky') || cs.display === 'none' || cs.visibility === 'hidden') continue
    const r = n.getBoundingClientRect()
    if (r.height === 0 || r.width < window.innerWidth * 0.6 || r.height > vh * 0.4) continue
    if (r.top <= 1) top = Math.max(top, r.bottom)
    else if (r.bottom >= vh - 1) bottom = Math.max(bottom, vh - r.top)
  }
  return [Math.round(top), Math.round(bottom)]
}

/** Is the drawing seen in the band from top to bottom (viewport px)? See the rules above. */
function ready(el: HTMLElement, top: number, bottom: number) {
  const area = bottom - top
  if (area <= 0) return false
  const r = el.getBoundingClientRect()
  const visible = Math.max(0, Math.min(r.bottom, bottom) - Math.max(r.top, top))
  const lamps = Array.from(el.querySelectorAll(LAMPS), (l) => l.getBoundingClientRect()).filter((b) => b.width || b.height)
  if (!lamps.length) return (r.height > 0 && visible / r.height >= START_RATIO) || visible >= area * START_SHARE
  const first = Math.min(...lamps.map((b) => b.top))
  const last = Math.max(...lamps.map((b) => b.bottom))
  if (last - first > area) return visible >= area * START_SHARE
  return first >= top && last <= bottom
}

/** Start every CSS animation in the drawing over, including ones that already ended. */
function restart(el: HTMLElement): Animation[] {
  const s = document.createElement('style')
  s.textContent = RESET
  el.setAttribute('data-kk-reset', '')
  document.head.append(s)
  el.getAnimations({ subtree: true }) // style pass without them: the old ones are cancelled
  s.remove()
  el.removeAttribute('data-kk-reset')
  return el.getAnimations({ subtree: true }) // and with them: new ones, at zero
}

function hold(anims: Animation[], on: boolean) {
  for (const a of anims) {
    if (on && a.playState === 'running') a.pause()
    // Only resume what we paused: play() on a finished animation restarts it.
    else if (!on && a.playState === 'paused') a.play()
  }
}

function start(it: Item) {
  it.started = true
  hold(it.anims, false)
  if (it.go) {
    it.done = true
    it.go()
  }
}

// The drawings and their lamps are observed: a lamp crossing an edge of the band is
// often the moment the rule above turns true, between two steps of the drawing's own.
function onEntries(entries: IntersectionObserverEntry[]) {
  const check = new Set<Item>()
  for (const e of entries) {
    const it = byTarget.get(e.target)
    if (!it || it.done) continue
    if (!it.started) check.add(it)
    else if (e.target === it.el) hold(it.anims, !e.isIntersecting)
  }
  if (!check.size) return
  // The band the observer was built with. Not e.rootBounds: for a target without a
  // box (the flow's hidden drawing) Chromium reports it as an empty rect.
  const [top, bottom] = insetKey.split(',').map(Number)
  for (const it of check) if (ready(it.el, top, window.innerHeight - bottom)) start(it)
}

function observeAll(force = false) {
  const [top, bottom] = insets()
  const key = `${top},${bottom}`
  if (io && !force && key === insetKey) return
  io?.disconnect()
  insetKey = key
  io = new IntersectionObserver(onEntries, {
    rootMargin: `-${top}px 0px -${bottom}px 0px`,
    threshold: THRESHOLDS,
  })
  byTarget.clear()
  for (const it of items) if (!it.done) watch(it)
}

function watch(it: Item) {
  for (const t of [it.el, ...Array.from(it.el.querySelectorAll(LAMPS))]) {
    byTarget.set(t, it)
    io?.observe(t)
  }
}

function bind() {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
  if (!('IntersectionObserver' in window) || !('getAnimations' in Element.prototype)) return
  items = items.filter((i) => i.el.isConnected)
  const fresh = Array.from(document.querySelectorAll<HTMLElement>('[data-kk-play]')).filter((el) => !el.dataset.kkBound)
  const [top, bottom] = insets()
  for (const el of fresh) {
    el.dataset.kkBound = '1'
    // Already seen: let it run on. Otherwise start it over and hold it at zero.
    const started = ready(el, top, window.innerHeight - bottom)
    const anims = started ? el.getAnimations({ subtree: true }) : restart(el)
    if (!anims.length) continue
    if (!started) hold(anims, true)
    const it: Item = { el, anims, started, done: false }
    items.push(it)
    const done = () => {
      it.done = true
      for (const [t, of] of byTarget) if (of === it) io?.unobserve(t)
    }
    Promise.all(anims.map((a) => a.finished)).then(done, done)
  }
  if (items.length) observeAll(fresh.length > 0)
  else {
    io?.disconnect()
    io = undefined
  }
}

/**
 * For a drawing that starts itself (FlowDiagram adds a class): calls go() once, when
 * it is seen by the same rule as above (its lamps carry data-lamp).
 */
export function whenSeen(el: HTMLElement, go: () => void) {
  if (!('IntersectionObserver' in window)) return go()
  const it: Item = { el, anims: [], started: false, done: false, go }
  items.push(it)
  if (io) watch(it)
  else observeAll(true)
}

let resizeTimer: number | undefined
window.addEventListener('resize', () => {
  window.clearTimeout(resizeTimer)
  resizeTimer = window.setTimeout(() => items.length && observeAll(), 200)
})
document.addEventListener('astro:page-load', bind)
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', bind, { once: true })
else bind()
