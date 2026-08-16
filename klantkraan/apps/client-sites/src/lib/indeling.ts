// The composition vocabulary: the bounded set of arrangements this factory can build.
//
// `stijl.ts` parameterised the paint and the sameness moved rather than left. Every site
// still had one silhouette: a split hero, then a three-column grid of bordered cards, nine
// times over, and no axis could reach either. A visitor reads the silhouette before they
// read a word, so that is the layer a template is recognised at.
//
// Same mechanism as the skin, deliberately: a closed set of named values, each built and
// looked at once, resolving to markup the components already know how to render. Nothing
// here generates layout. A model choosing among these cannot invent a grid that reflows
// wrong on a phone or a hero the fact gate cannot assert -- it can only choose an
// arrangement that has been seen working.
//
// Grounded in the 60-site trade survey in research/trade-site-craft-2026-08-16.md. Two of
// its findings drive what is on offer:
//   - award-tier sites average 0.9 tel: links per homepage and 29% have none at all, so
//     no arrangement here is allowed to move, hide or de-text the phone number. Contact
//     mechanics are invariant; only the composition around them varies.
//   - the three-card dienst grid is the single most-flagged generated-site component, and
//     the good trade sites overwhelmingly run a numbered list or an index instead.

export const HEROS = ['gesplitst', 'gestapeld', 'typografisch'] as const
export const DIENSTVORMEN = ['kaarten', 'lijst', 'index'] as const

export type Hero = (typeof HEROS)[number]
export type Dienstvorm = (typeof DIENSTVORMEN)[number]

/** Homepage sections a site may do without. See `indeling.weglaten` for why these four. */
export const WEGLAATBAAR = ['intro', 'werk', 'werkgebied', 'usps'] as const
export type Weglaatbaar = (typeof WEGLAATBAAR)[number]

export interface Indeling {
  weglaten: Weglaatbaar[]
  hero: Hero
  diensten: Dienstvorm
}

/**
 * The composition every client site had before this vocabulary existed.
 *
 * Same contract as STANDAARD_STIJL: a client.yaml with no `indeling:` block, or with only
 * the `weglaten` key it used to have, builds the bytes it built yesterday.
 */
export const STANDAARD_INDELING: Indeling = {
  weglaten: [],
  hero: 'gesplitst',
  diensten: 'kaarten',
}

/**
 * How much of the hero row the copy column takes, and whether there is a second column.
 *
 * `gesplitst` is the arrangement the template shipped with and it stays the default, but
 * measuring it found the reason the other two exist: at `schaal: groot` and `maat: normaal`
 * the headline gets a 460px column, which is about eight characters a line at 56px. The
 * kapper fixture's H1 came back hyphenated across three lines on a 1440px screen. A
 * headline is the largest thing on the page and the one element that most wants room; two
 * of the three arrangements here give it the full measure.
 */
export const HERO_VORM: Record<Hero, { kolommen: boolean; fotoBreed: boolean }> = {
  // Copy on paper, photograph bleeding off the right edge. The photo is beside the words,
  // so the words get half the column.
  gesplitst: { kolommen: true, fotoBreed: false },
  // Headline and copy across the full measure, photograph full width underneath. The
  // headline gets every pixel the page has, and the photograph gets to be a photograph
  // rather than a tall crop -- which is what the reference sites do with a good one.
  gestapeld: { kolommen: false, fotoBreed: true },
  // No photograph at all: headline, promise, contact row. A third of the real Dutch trade
  // sites surveyed open this way, and it is the honest arrangement for a vak whose stock
  // set has no hero frame worth the first screen. Costs nothing and loads instantly.
  typografisch: { kolommen: false, fotoBreed: false },
}

/** Does this hero draw a photograph at all? */
export function heroToontFoto(hero: Hero): boolean {
  return hero !== 'typografisch'
}
