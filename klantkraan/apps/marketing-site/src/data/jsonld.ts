// Shared JSON-LD builders for content routes. New pages (pseo, gidsen) build
// their schemas here and render them via components/JsonLd.astro.
// [stad]/[vak].astro and the 13 older inline copies are a later retrofit
// (TODO §M step 1 note); do not let this file drift from their output shape.

export interface FaqItem {
  q: string
  a: string
}

export interface Crumb {
  name: string
  /** Absolute URL. */
  item: string
}

const ORG = (siteRoot: string) => ({
  '@type': 'Organization',
  name: 'Klantkraan',
  url: siteRoot,
})

export function faqPageSchema(faqs: FaqItem[]) {
  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: faqs.map((faq) => ({
      '@type': 'Question',
      name: faq.q,
      acceptedAnswer: {
        '@type': 'Answer',
        text: faq.a.replace(/<[^>]+>/g, ''),
      },
    })),
  }
}

export function breadcrumbSchema(crumbs: Crumb[]) {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: crumbs.map((crumb, i) => ({
      '@type': 'ListItem',
      position: i + 1,
      name: crumb.name,
      item: crumb.item,
    })),
  }
}

export function articleSchema(input: {
  headline: string
  description: string
  /** Canonical absolute URL of the article. */
  url: string
  /** Site root absolute URL. Organization is always the author (no personal bylines). */
  siteRoot: string
  datePublished: Date
  dateModified: Date
}) {
  return {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: input.headline,
    description: input.description,
    mainEntityOfPage: { '@type': 'WebPage', '@id': input.url },
    author: ORG(input.siteRoot),
    publisher: ORG(input.siteRoot),
    datePublished: input.datePublished.toISOString().slice(0, 10),
    dateModified: input.dateModified.toISOString().slice(0, 10),
    inLanguage: 'nl-NL',
  }
}
