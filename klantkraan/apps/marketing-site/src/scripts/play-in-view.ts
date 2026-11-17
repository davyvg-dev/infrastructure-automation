// The wire-and-lamp drawings that play a sequence (ServicesHero, CareDiagram,
// FollowUpDiagram, VariantsDiagram) mark their root with data-kk-play. Their CSS
// runs the sequence by itself, so a page whose scripts fail still ends with every
// lamp on. This script makes it play when the visitor actually sees it:
//
// - Until then the whole drawing is held at its start (lamps off, switches open).
// - "Seen" means every lamp of the drawing (whatever lights up, LAMPS below) sits
//   in the part of the screen that nothing covers: the sticky header and the
//   phone's bottom action bar are measured and cut off. So a drawing that rests
//   half under the bar waits, and one whose lamps are all on screen plays even if
//   its bottom edge is cut off. It also starts once its top and its bottom lamp
//   have each been in that part, one after the other (scrolled past without a
//   stop, where the lamps only just fit). When its lamps cannot all fit in that
//   part at once (a landscape phone), it starts once the drawing fills most of it. A drawing
//   without lamps starts once nearly all of it is there.
// - Once started, it pauses while it is fully out of that part and resumes where
//   it was when it comes back. A drawing whose animations all end is let go once
//   they have ended. A drawing with an endless animation (an idle cycle after the
//   build-up: animation-iteration-count: infinite) stays watched as long as it is
//   on the page, so the cycle only runs while it can be seen.
// - All CSS animations of a drawing (everything inside the data-kk-play element,
//   pseudo-elements too) run on one clock: their delays count from the same start,
//   and pausing and resuming moves them together. A resize can make the browser
//   swap in new animations that would start over at zero: a media query renames
//   one (the hero's wires run x on a wide screen and y on a phone) or shows a part
//   it hid. Those are put on the drawing's clock at once, before they paint, so a
//   rotated phone does not replay the build-up and an idle cycle stays in step.
//   Only animations created by that resize are moved; one a drawing starts itself
//   later (a class it adds) is left alone.
//
// It binds as soon as this module runs (module scripts run once the page is
// parsed). The first astro:page-load waits for the window load event, and on a
// slow phone the CSS had played the whole hero under the bar by then. A drawing
// that is not in view when bound is restarted from zero: an animation that has
// already finished is gone from getAnimations() and cannot be rewound.
//
// The CSS has no animation under reduced motion or without scripting, so then
// there is nothing to hold and the drawing is simply finished.
// Also bound on astro:page-load, so it runs after a ClientRouter navigation; the
// drawings of the page that was left are dropped and no longer observed.
//
// whenSeen(el, go) is for a drawing that starts itself (FlowDiagram): go() is
// called once, when el is seen by the rule above; nothing is held or paused.

type Item = {
  el: HTMLElement
  started: boolean
  /** Nothing left to do: its animations have ended, or whenSeen() has called go(). */
  done: boolean
  /** Held at the start (not yet seen) or paused (off screen). */
  held: boolean
  /** The drawing's own time while held, and the timeline time of its zero while running. */
  at: number
  base: number
  /** The animations it had last time we looked, to tell the ones a resize swaps in. */
  known: Set<Animation>
  /** The ones this script paused, the only ones it resumes. */
  paused: Set<Animation>
  /** whenSeen(): called once instead of playing animations. */
  go?: () => void
  /** Seen in the band so far, while held: 1 its top lamp, 2 its bottom lamp. */
  swept?: number
}

// What lights up: the lamps (hero, care, follow-up, the flow's three lamps), the
// hero's node lamp, the sixteen openings of the variants drawing, the bars of the
// cost ledger and, in home/Hero.astro's window, the customer's message and the
// booked badge.
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
function ready(el: HTMLElement, top: number, bottom: number, it?: Item) {
  const area = bottom - top
  if (area <= 0) return false
  const r = el.getBoundingClientRect()
  const visible = Math.max(0, Math.min(r.bottom, bottom) - Math.max(r.top, top))
  const lamps = Array.from(el.querySelectorAll(LAMPS), (l) => l.getBoundingClientRect()).filter((b) => b.width || b.height)
  if (!lamps.length) return (r.height > 0 && visible / r.height >= START_RATIO) || visible >= area * START_SHARE
  const first = Math.min(...lamps.map((b) => b.top))
  const last = Math.max(...lamps.map((b) => b.bottom))
  if (last - first > area) return visible >= area * START_SHARE
  if (first >= top && last <= bottom) return true
  // Swept: the top lamp and the bottom lamp have each been in the band, just not at
  // the same moment. On a landscape phone the lamps only just fit, so a visitor who
  // scrolls past without stopping in that narrow window has still seen them all.
  if (!it) return false
  if (first >= top && first <= bottom) it.swept = (it.swept ?? 0) | 1
  if (last >= top && last <= bottom) it.swept = (it.swept ?? 0) | 2
  return it.swept === 3
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

const isCss = (a: Animation) => 'animationName' in a
const endless = (a: Animation) => a.effect?.getTiming().iterations === Infinity
const now = () => Number(document.timeline.currentTime ?? performance.now())

/** The drawing's own time in ms: read from one of its animations, else from our own count. */
function clock(it: Item) {
  for (const a of it.known) {
    if (isCss(a) && a.playState !== 'finished' && a.playState !== 'idle' && a.currentTime !== null) return Number(a.currentTime)
  }
  return it.held ? it.at : now() - it.base
}

/**
 * After a resize: the CSS animations the browser has just created for the drawing
 * (still pending) were swapped in by a media query; put them on its clock, held
 * if it is held. A drawing that has ended ends them as well.
 */
function resync(it: Item) {
  const list = it.el.getAnimations({ subtree: true })
  const fresh = list.filter((a) => !it.known.has(a) && isCss(a) && a.pending)
  if (fresh.length) {
    const t = it.done ? undefined : clock(it)
    // Running: share the start time of one that runs, so they stay on the same frame.
    const run = it.held ? undefined : [...it.known].find((a) => isCss(a) && a.playState === 'running' && a.startTime !== null)
    for (const a of fresh) {
      if (t === undefined) {
        if (!endless(a)) a.finish()
      } else if (run) a.startTime = run.startTime
      else {
        a.currentTime = t
        if (it.held) {
          a.pause()
          it.paused.add(a)
        }
      }
    }
  }
  it.known = new Set(list)
}

/** Hold the drawing (on) or let it run again (off). */
function hold(it: Item, on: boolean) {
  if (it.go) return
  const t = clock(it)
  const list = it.el.getAnimations({ subtree: true })
  it.known = new Set(list)
  it.held = on
  if (on) it.at = t
  else it.base = now() - t
  for (const a of list) {
    if (on && a.playState === 'running') {
      a.pause()
      it.paused.add(a)
    }
    // Only resume what we paused: play() on a finished animation restarts it.
    else if (!on && it.paused.has(a) && a.playState === 'paused') a.play()
  }
  if (!on) it.paused.clear()
}

function start(it: Item) {
  it.started = true
  if (it.go) {
    finish(it)
    it.go()
    return
  }
  hold(it, false)
  // The lamps only told us when to start; from now on the drawing itself says
  // whether it is in view.
  for (const l of Array.from(it.el.querySelectorAll(LAMPS))) unwatch(l)
  settle(it)
}

/** Let a drawing go once all its animations have ended. One with an endless one never does. */
function settle(it: Item) {
  const list = it.el.getAnimations({ subtree: true })
  if (list.some(endless)) return
  // A cancelled one (swapped by a media query, or the drawing left the page) rejects: look again.
  Promise.all(list.map((a) => a.finished)).then(
    () => (it.el.getAnimations({ subtree: true }).some((a) => a.playState !== 'finished') ? settle(it) : finish(it)),
    () => (it.el.isConnected ? settle(it) : finish(it)),
  )
}

function finish(it: Item) {
  it.done = true
  for (const [t, of] of byTarget) if (of === it) unwatch(t)
}

function unwatch(t: Element) {
  byTarget.delete(t)
  io?.unobserve(t)
}

// The drawings and their lamps are observed: a lamp crossing an edge of the band is
// often the moment the rule above turns true, between two steps of the drawing's own.
function onEntries(entries: IntersectionObserverEntry[]) {
  const check = new Set<Item>()
  for (const e of entries) {
    const it = byTarget.get(e.target)
    if (!it || it.done) continue
    if (!it.started) check.add(it)
    else if (e.target === it.el && it.held === e.isIntersecting) hold(it, !e.isIntersecting)
  }
  if (!check.size) return
  // The band the observer was built with. Not e.rootBounds: for a target without a
  // box (the flow's hidden drawing) Chromium reports it as an empty rect.
  const [top, bottom] = insetKey.split(',').map(Number)
  for (const it of check) if (ready(it.el, top, window.innerHeight - bottom, it)) start(it)
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

/** Not started: the drawing and its lamps. Started: the drawing only (pause and resume). */
function watch(it: Item) {
  const targets = it.started ? [it.el] : [it.el, ...Array.from(it.el.querySelectorAll(LAMPS))]
  for (const t of targets) {
    byTarget.set(t, it)
    io?.observe(t)
  }
}

function item(el: HTMLElement, go?: () => void): Item {
  return { el, started: false, done: false, held: false, at: 0, base: now(), known: new Set(), paused: new Set(), go }
}

function bind() {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
  if (!('IntersectionObserver' in window) || !('getAnimations' in Element.prototype)) return
  // Drawings of a page we left: stop observing them.
  const left = items.filter((i) => !i.el.isConnected)
  for (const it of left) finish(it)
  items = items.filter((i) => i.el.isConnected)
  const fresh = Array.from(document.querySelectorAll<HTMLElement>('[data-kk-play]')).filter((el) => !el.dataset.kkBound)
  const [top, bottom] = insets()
  for (const el of fresh) {
    el.dataset.kkBound = '1'
    // Already seen: let it run on. Otherwise start it over and hold it at zero.
    const started = ready(el, top, window.innerHeight - bottom)
    const anims = started ? el.getAnimations({ subtree: true }) : restart(el)
    if (!anims.length) continue
    const it = item(el)
    it.known = new Set(anims)
    it.started = started
    if (started) {
      it.base = now() - Math.max(0, ...anims.map((a) => Number(a.currentTime ?? 0)))
      settle(it)
    } else hold(it, true)
    items.push(it)
  }
  if (items.length) observeAll(fresh.length > 0 || left.length > 0)
  else {
    io?.disconnect()
    io = undefined
    byTarget.clear()
  }
}

/**
 * For a drawing that starts itself (FlowDiagram adds a class): calls go() once, when
 * it is seen by the same rule as above (its lamps carry data-lamp).
 */
export function whenSeen(el: HTMLElement, go: () => void) {
  if (!('IntersectionObserver' in window)) return go()
  items.push(item(el, go))
  if (io) watch(items[items.length - 1])
  else observeAll(true)
}

let resizeTimer: number | undefined
window.addEventListener('resize', () => {
  // Right away, before the next frame paints: a media query may just have swapped
  // animations in, and they must not show a frame from zero.
  for (const it of items) if (it.el.isConnected && !it.go) resync(it)
  window.clearTimeout(resizeTimer)
  resizeTimer = window.setTimeout(() => items.length && observeAll(), 200)
})
document.addEventListener('astro:page-load', bind)
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', bind, { once: true })
else bind()
