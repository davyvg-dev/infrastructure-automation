// The design vocabulary: the bounded set of looks this factory can build.
//
// The template used to have exactly one appearance, and the only thing a client
// could change about it were two hex colours. Two voorstellen sent in the same
// week were recognisably the same site, which is the one thing an unsolicited
// proposal cannot afford to be.
//
// So the skin is parameterised and the silhouette is not. Every axis below is a
// closed set of named values that resolve to CSS custom properties, injected on
// <html> by Base.astro next to --brand-primary. Section order, markup and the
// components themselves are identical for every client: what varies is type,
// colour, rhythm, radius and how photographs are set.
//
// Why a closed vocabulary rather than generated CSS: every value here has been
// looked at once, on a real build, and can be trusted forever after. A model
// choosing among them cannot produce an inaccessible contrast, a broken mobile
// reflow, or a layout the fact gate cannot assert. It can only choose a look.
//
// Grounded in the twelve award-level trade/architecture sites read for TODO Q9
// (Koto, Leidner, Adriaans, Zecc, Van Wijnen, Hobbs, Land Morphology): what
// separates those from a template is the type scale, the amount of air, and
// whether photographs are framed or allowed to bleed. Not the section order --
// they all say the same things in the same sequence.

export const LETTERONTWERPEN = ['systeem', 'grotesk', 'industrieel', 'redactioneel'] as const
export const SCHALEN = ['compact', 'normaal', 'groot'] as const
export const VORMEN = ['scherp', 'zacht', 'rond'] as const
export const RITMES = ['dicht', 'normaal', 'ruim'] as const
export const PALETTEN = ['warm', 'koel', 'neutraal', 'zand'] as const
export const KLEURINGEN = ['spaarzaam', 'royaal'] as const
export const FOTOZETTINGEN = ['ingekaderd', 'randloos'] as const

export type Letterontwerp = (typeof LETTERONTWERPEN)[number]
export type Schaal = (typeof SCHALEN)[number]
export type Vorm = (typeof VORMEN)[number]
export type Ritme = (typeof RITMES)[number]
export type Palet = (typeof PALETTEN)[number]
export type Kleuring = (typeof KLEURINGEN)[number]
export type Fotozetting = (typeof FOTOZETTINGEN)[number]

export interface Stijl {
  letterontwerp: Letterontwerp
  schaal: Schaal
  vorm: Vorm
  ritme: Ritme
  palet: Palet
  kleuring: Kleuring
  foto: Fotozetting
}

/**
 * The look every client site had before the vocabulary existed. Kept as the
 * default so an existing client.yaml with no `stijl:` block builds the same
 * bytes it did yesterday, and so there is one known-good reference to diff a
 * new combination against.
 */
export const STANDAARD_STIJL: Stijl = {
  letterontwerp: 'systeem',
  schaal: 'normaal',
  vorm: 'zacht',
  ritme: 'normaal',
  palet: 'warm',
  kleuring: 'spaarzaam',
  foto: 'ingekaderd',
}

type Tokens = Record<string, string>

// --- typefaces --------------------------------------------------------------------------
//
// The single biggest tell that a site came out of a template is that it is set in
// system-ui: it is what a page looks like when nobody chose anything. So the vocabulary
// gets real faces, self-hosted (see scripts/fonts.mjs) rather than linked, because a
// client site making zero external requests is what lets it ship without a cookie banner.
//
// Which files each pairing needs lives in fonts/manifest.json, read here and by
// astro.config.mjs, so the stack the CSS names and the bytes the build copies cannot
// drift apart. A stack naming a family that was never copied does not fail anything --
// it silently falls back to Arial on a client's live site, which is exactly the class of
// bug a shared manifest removes.
import manifest from '../../fonts/manifest.json'

// Trailing fallbacks. The webfont is prepended; on the systeem pairing this stack is all
// there is. Kept identical to what the template shipped before webfonts existed, so
// `letterontwerp: systeem` really is the old look and not an approximation of it.
const SYSTEEM_STACK =
  "system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
const SERIF_FALLBACK = "Georgia, 'Times New Roman', serif"

interface Pairing {
  dirs: string[]
  display: string | null
  body: string | null
}

/**
 * Per-pairing display treatment: the weight and tracking of h1/h2.
 *
 * Sizes come from `schaal`, but weight and tracking belong to the face -- the same
 * numbers do not suit a 400-weight serif and an 800-weight grotesk, and a display serif
 * forced to 800 with -0.015em tracking looks like a rendering fault rather than a choice.
 *
 * h3 is deliberately not here. It is a card and panel title at ~1.15rem, and at that size
 * a display face is either invisible (a high-contrast serif loses its thin strokes) or
 * shouty (a wide grotesk). Every pairing sets h3 in the body face, which is the ordinary
 * convention: display for the two headings that carry the page, text face for the rest.
 */
const LETTER_TOKENS: Record<Letterontwerp, Tokens> = {
  systeem: {
    '--text-h1--font-weight': '800',
    '--text-h2--font-weight': '700',
    '--display-tracking': '-0.015em',
  },
  // Figtree carries its own weight at 700; 800 is heavier than the face wants.
  grotesk: {
    '--text-h1--font-weight': '700',
    '--text-h2--font-weight': '700',
    '--display-tracking': '-0.02em',
  },
  // Archivo is wide and sturdy, which is why it suits construction, and it needs tighter
  // tracking at display sizes or a Dutch company name sprawls across three lines.
  industrieel: {
    '--text-h1--font-weight': '700',
    '--text-h2--font-weight': '700',
    '--display-tracking': '-0.03em',
  },
  // Instrument Serif ships one weight and is high contrast: let the size do the work.
  // Negative tracking collides its thin strokes, so this is the one pairing at 0.
  redactioneel: {
    '--text-h1--font-weight': '400',
    '--text-h2--font-weight': '400',
    '--display-tracking': '0em',
  },
}

const PAIRINGEN = manifest as unknown as Record<string, Pairing>

/** Font-family stacks for a pairing: the webfont first, then the system fallbacks. */
function fontTokens(naam: Letterontwerp): Tokens {
  const pairing = PAIRINGEN[naam]
  const isSerif = naam === 'redactioneel'
  return {
    '--font-sans': pairing.body ? `'${pairing.body}', ${SYSTEEM_STACK}` : SYSTEEM_STACK,
    '--font-display': pairing.display
      ? `'${pairing.display}', ${isSerif ? SERIF_FALLBACK : SYSTEEM_STACK}`
      : SYSTEEM_STACK,
    ...LETTER_TOKENS[naam],
  }
}

/** Font directories a client on this pairing has to ship. Used by astro.config.mjs. */
export function fontDirs(naam: Letterontwerp): string[] {
  return PAIRINGEN[naam]?.dirs ?? []
}

// --- type scale -----------------------------------------------------------------------
//
// Sizes only. Weight and tracking belong to the typeface, not to the scale, and are set
// by the letterontwerp axis. Every step is a clamp() so the scale is fluid rather than
// stepped: a trade site is read on a phone in a van as often as on a desktop.
const SCHAAL_TOKENS: Record<Schaal, Tokens> = {
  // Dense and businesslike. Suits a client with many diensten, where the page is long
  // and a huge H1 would push the first real information below the fold.
  compact: {
    '--text-h1': 'clamp(1.65rem, 3.6vw, 2.35rem)',
    '--text-h2': 'clamp(1.3rem, 2.4vw, 1.65rem)',
    '--text-h3': '1.05rem',
    '--text-body': '1rem',
    '--text-small': '0.8125rem',
  },
  normaal: {
    '--text-h1': 'clamp(1.9rem, 4.5vw, 3rem)',
    '--text-h2': 'clamp(1.45rem, 3vw, 2rem)',
    '--text-h3': '1.15rem',
    '--text-body': '1.0625rem',
    '--text-small': '0.875rem',
  },
  // The editorial end: a headline big enough to carry the first screen on its own.
  //
  // Capped at 3.5rem rather than the 4.25rem this started at. The H1 is
  // "<bedrijf.naam>: vakwerk waar u op kunt rekenen." in a half-width hero column, and
  // Dutch trade names are long ("Voorbeeld Loodgietersbedrijf" is 28 characters): at
  // 68px that ran to five lines and pushed the call button off a 1000px screen. A trade
  // site that hides its phone number below the fold has lost the only conversion it has.
  groot: {
    '--text-h1': 'clamp(2.1rem, 5vw, 3.5rem)',
    '--text-h2': 'clamp(1.7rem, 3.8vw, 2.6rem)',
    '--text-h3': '1.25rem',
    '--text-body': '1.125rem',
    '--text-small': '0.9375rem',
  },
}

// --- radius ---------------------------------------------------------------------------
//
// One axis drives cards, buttons and the hero photo together: a site with sharp cards
// and pill buttons reads as two designs stapled together, which is precisely the tell
// this vocabulary exists to remove.
const VORM_TOKENS: Record<Vorm, Tokens> = {
  scherp: {
    '--radius-card': '0px',
    '--radius-button': '0px',
    '--radius-foto': '0px',
  },
  zacht: {
    '--radius-card': '0.75rem',
    '--radius-button': '0.625rem',
    '--radius-foto': '1.25rem',
  },
  rond: {
    '--radius-card': '1.25rem',
    '--radius-button': '9999px',
    '--radius-foto': '1.5rem',
  },
}

// --- vertical rhythm ------------------------------------------------------------------
//
// Two pairs: the ordinary text sections, and the photo band, which has always carried
// more air than the rest and has to keep that relationship at every density.
const RITME_TOKENS: Record<Ritme, Tokens> = {
  dicht: {
    '--ritme-y': '1.75rem',
    '--ritme-y-md': '2.25rem',
    '--ritme-band-y': '2.5rem',
    '--ritme-band-y-md': '3.5rem',
  },
  normaal: {
    '--ritme-y': '2.25rem',
    '--ritme-y-md': '3rem',
    '--ritme-band-y': '3.5rem',
    '--ritme-band-y-md': '5rem',
  },
  // Gallery air. The single cheapest way to stop a page reading as a brochure, and the
  // one thing every site in the Q9 reference set had in common.
  ruim: {
    '--ritme-y': '3.25rem',
    '--ritme-y-md': '5rem',
    '--ritme-band-y': '4.5rem',
    '--ritme-band-y-md': '7rem',
  },
}

// --- surfaces -------------------------------------------------------------------------
//
// Paper, card, ink, muted text and hairline. Brand colour is deliberately NOT here: it
// comes from client.yaml and has to survive on top of any of these. Every ink/paper pair
// below clears WCAG AA for body text, and every mist/paper pair clears 4.5:1 as well --
// muted text is still text.
const PALET_TOKENS: Record<Palet, Tokens> = {
  warm: {
    '--color-paper': '#faf9f7',
    '--color-card': '#ffffff',
    '--color-ink': '#20262c',
    '--color-mist': '#5a646e',
    '--color-line': '#e5e1da',
  },
  koel: {
    '--color-paper': '#f6f7f9',
    '--color-card': '#ffffff',
    '--color-ink': '#1b2027',
    '--color-mist': '#565f6a',
    '--color-line': '#dfe3e8',
  },
  neutraal: {
    '--color-paper': '#f7f7f7',
    '--color-card': '#ffffff',
    '--color-ink': '#1f1f1f',
    '--color-mist': '#5b5b5b',
    '--color-line': '#e2e2e2',
  },
  // The editorial warm-grey the reference set kept reaching for: paper with a little
  // yellow in it, card slightly warmer than white, hairlines the colour of card stock.
  zand: {
    '--color-paper': '#f5f1ea',
    '--color-card': '#fffdf9',
    '--color-ink': '#23201c',
    '--color-mist': '#5f584e',
    '--color-line': '#e0d8ca',
  },
}

// --- how much brand colour the page carries -------------------------------------------
//
// The alternating bands (Usps, Werk, Werkgebied) read --band-* rather than --color-card
// directly, so this axis moves them without touching the components' structure. The
// tinted variant is mixed from the client's own primary, so it cannot clash with it, and
// stays at a low enough percentage that --color-ink keeps its contrast on top.
const KLEURING_TOKENS: Record<Kleuring, Tokens> = {
  spaarzaam: {
    '--band-bg': 'var(--color-card)',
    '--band-line': 'var(--color-line)',
    '--band-foto-bg': 'color-mix(in oklab, var(--brand-primary) 5%, var(--color-paper))',
  },
  royaal: {
    '--band-bg': 'color-mix(in oklab, var(--brand-primary) 6%, var(--color-card))',
    '--band-line': 'color-mix(in oklab, var(--brand-primary) 18%, var(--color-line))',
    '--band-foto-bg': 'color-mix(in oklab, var(--brand-primary) 13%, var(--color-paper))',
  },
}

// --- photography ----------------------------------------------------------------------
//
// Framed keeps every photograph inside the max-w-5xl column with a radius on it. Bleeding
// lets the work band run to both edges of the viewport with square corners, which is what
// the reference sites do and what makes a stock set look like a portfolio rather than a
// contact sheet. The radius token is what the framed variant spends and the bleeding one
// zeroes, so `vorm` and `foto` cannot disagree about the corner of the same photo.
const FOTO_TOKENS: Record<Fotozetting, Tokens> = {
  // The photo grid sits in its own wrapper, and these two set how wide that wrapper is
  // allowed to be. Framed keeps it in the 72rem text column with the page gutter; bleeding
  // lets it fill the section and keeps only a hairline gutter so the outer photographs
  // reach the edge of the screen without touching it.
  // Two radii, not one: the hero photograph is a single large plate and carries a bigger
  // corner than the work tiles, which sit next to the dienst cards and match them. Folding
  // them into one value looks tidier in this file and visibly re-rounds the tiles on every
  // existing site, so they stay separate and only `randloos` squares both at once.
  ingekaderd: {
    '--foto-kolom': '72rem',
    '--foto-gutter': '1.5rem',
    '--foto-radius': 'var(--radius-foto)',
    '--foto-tegel-radius': 'var(--radius-card)',
  },
  randloos: {
    '--foto-kolom': '100%',
    '--foto-gutter': '0.5rem',
    '--foto-radius': '0px',
    '--foto-tegel-radius': '0px',
  },
}

/**
 * Resolve a stijl into the CSS custom properties Base.astro writes onto <html>.
 *
 * Only properties that differ from the stylesheet's own @theme defaults would strictly
 * need emitting, but all of them are written unconditionally: a partial override is the
 * kind of thing that works until someone edits global.css, and the bytes are noise next
 * to one photograph.
 */
export function resolveStijl(stijl: Stijl): Tokens {
  return {
    ...fontTokens(stijl.letterontwerp),
    ...SCHAAL_TOKENS[stijl.schaal],
    ...VORM_TOKENS[stijl.vorm],
    ...RITME_TOKENS[stijl.ritme],
    ...PALET_TOKENS[stijl.palet],
    ...KLEURING_TOKENS[stijl.kleuring],
    ...FOTO_TOKENS[stijl.foto],
  }
}

/** The resolved stijl as an inline `style` attribute value. */
export function stijlStyle(stijl: Stijl, extra: Tokens = {}): string {
  return Object.entries({ ...extra, ...resolveStijl(stijl) })
    .map(([prop, value]) => `${prop}: ${value}`)
    .join('; ')
}
