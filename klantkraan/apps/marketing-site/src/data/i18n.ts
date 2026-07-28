// Single source of truth for the page pairs across NL / EN / ES. Consumed by:
//   - Base.astro   -> emits <link rel="alternate" hreflang> + x-default
//   - Header.astro -> the language-switcher targets
//
// A page is "translated" into a locale iff that locale's URL appears in its
// row. Dutch (nl) is always present; en/es are optional so a partially
// translated page is representable (ES currently covers only the 6 core
// conversion pages; trade cornerstones stay nl+en).
//
// Anything not listed at all (Dutch-only city pages under /[stad]/[vak],
// gidsen, blog; the English-only /en/air-conditioning) gets no hreflang
// alternate, and the switcher falls back to that locale's home (/, /en/, /es/)
// so it never points at a 404.
//
// All paths carry a trailing slash to match astro.config `trailingSlash: 'always'`.

export interface LocalePair {
  nl: string
  en?: string
  es?: string
}

export const localePairs: LocalePair[] = [
  { nl: '/', en: '/en/', es: '/es/' },
  { nl: '/prijzen/', en: '/en/prijzen/', es: '/es/prijzen/' },
  { nl: '/aanmelden/', en: '/en/aanmelden/', es: '/es/aanmelden/' },
  { nl: '/demo/', en: '/en/demo/', es: '/es/demo/' },
  { nl: '/over/', en: '/en/over/', es: '/es/over/' },
  { nl: '/voor-wie/', en: '/en/voor-wie/', es: '/es/voor-wie/' },
  { nl: '/rekentool/', en: '/en/rekentool/', es: '/es/rekentool/' },
  { nl: '/loodgieters/', en: '/en/loodgieters/' },
  { nl: '/dakdekkers/', en: '/en/dakdekkers/' },
  { nl: '/installateur/', en: '/en/installateur/' },
  { nl: '/elektricien/', en: '/en/elektricien/' },
  { nl: '/aannemer/', en: '/en/aannemer/' },
  { nl: '/schilder/', en: '/en/schilder/' },
  { nl: '/sportscholen/', en: '/en/sportscholen/' },
]

/** Home URL per locale — the switcher's fallback when a page has no twin. */
export const localeHome = { nl: '/', en: '/en/', es: '/es/' } as const

/** The pair a path belongs to, or null when the path has no translation. */
export function pairForPath(path: string): LocalePair | null {
  return (
    localePairs.find((p) => p.nl === path || p.en === path || p.es === path) ?? null
  )
}

/**
 * Every locale's URL for the page at `path`. When a locale has no twin for
 * this page it falls back to that locale's home, so the switcher never 404s.
 */
export function localeUrls(path: string): { nl: string; en: string; es: string } {
  const pair = pairForPath(path)
  return {
    nl: pair?.nl ?? localeHome.nl,
    en: pair?.en ?? localeHome.en,
    es: pair?.es ?? localeHome.es,
  }
}
