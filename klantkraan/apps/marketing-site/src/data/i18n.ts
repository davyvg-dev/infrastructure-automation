// Single source of truth for the NL <-> EN page pairs. Consumed by:
//   - Base.astro   -> emits <link rel="alternate" hreflang> + x-default
//   - Header.astro -> the language-switcher target
//
// A page is "translated" iff its path appears here. Anything not listed
// (Dutch-only city pages under /[stad]/[vak], gidsen, blog; the English-only
// /en/air-conditioning) gets no hreflang alternate, and the switcher falls
// back to the other language's home so it never points at a 404.
//
// All paths carry a trailing slash to match astro.config `trailingSlash: 'always'`.

export interface LocalePair {
  nl: string
  en: string
}

export const localePairs: LocalePair[] = [
  { nl: '/', en: '/en/' },
  { nl: '/prijzen/', en: '/en/prijzen/' },
  { nl: '/demo/', en: '/en/demo/' },
  { nl: '/over/', en: '/en/over/' },
  { nl: '/voor-wie/', en: '/en/voor-wie/' },
  { nl: '/rekentool/', en: '/en/rekentool/' },
  { nl: '/loodgieters/', en: '/en/loodgieters/' },
  { nl: '/dakdekkers/', en: '/en/dakdekkers/' },
  { nl: '/installateur/', en: '/en/installateur/' },
  { nl: '/elektricien/', en: '/en/elektricien/' },
  { nl: '/aannemer/', en: '/en/aannemer/' },
  { nl: '/schilder/', en: '/en/schilder/' },
  { nl: '/sportscholen/', en: '/en/sportscholen/' },
]

/** The pair a path belongs to, or null when the path has no translation. */
export function pairForPath(path: string): LocalePair | null {
  return localePairs.find((p) => p.nl === path || p.en === path) ?? null
}

/** The other-language twin of `path`, or null when it has no translation. */
export function altPath(path: string): string | null {
  const pair = pairForPath(path)
  if (!pair) return null
  return pair.nl === path ? pair.en : pair.nl
}
