/**
 * Lead magnets and mini offers: the one source for every call to action on the
 * site. OfferCta (the block above the footer), /gratis/, /klein-beginnen/ and the
 * lines before, inside and after each magnet all read from here, so a name, price
 * or reason changed here changes everywhere.
 *
 * Rules (plan 2026-11-15-lead-magnets-and-mini-offers):
 * - A magnet is named by its result, never "scan", "check" or "cursus" alone.
 * - `reason` is a real limit only. No invented deadlines.
 * - Copy is Dutch, "u" voice on the dark site. Mini-offer texts avoid "u" and "je"
 *   because they also show on the light /scan and /websitecheck pages, which say "je".
 * - No founder name anywhere in customer copy.
 * - Prices are excl. btw, as on /prijzen/. \u00a0 keeps "€ 295" on one line.
 *
 * payUrl: the Mollie payment link for that offer (reusable, no expiry, created by the
 * founder in the Mollie dashboard; amounts there are incl. 21% btw, see payAmount).
 * Empty means the button becomes a mail link to order.
 */
import { contact } from './contact'

export type Area = 'websites' | 'automations' | 'receptionist' | 'ads'

/** Real weekly limits that the reason lines quote. Change the number here only. */
export const SCANS_PER_WEEK = 5
export const FREE_OPENINGS_PER_WEEK = 10

export interface Magnet {
  area: Area
  /** Headline: the result the visitor gets. */
  name: string
  /** Short label for lists (footer, /gratis/). */
  short: string
  href: string
  /** Element id of the tool or form on the magnet's own page. */
  anchor: string
  button: string
  /** Exactly what happens after the click. */
  next: string
  /** The true reason to do it now. */
  reason: string
}

export interface MiniOffer {
  area: Area
  slug: string
  name: string
  problem: string
  delivers: string
  /** Shown as is, e.g. "€ 295". */
  price: string
  priceNote: string
  days: string
  /** One line used before the magnet and inside its result. */
  hook: string
  /** What the buyer mails after paying (a payment link does not tell us). */
  send: string
  /** /websitecheck/ point ids this offer fixes; the result shows the offer next to them. */
  fixes?: string[]
  payUrl: string
  /** What the Mollie link charges, incl. btw, shown on the button. Must match Mollie. */
  payAmount: string
}

export const magnets: Record<Area, Magnet> = {
  websites: {
    area: 'websites',
    name: 'Zie in 1 minuut wat een klant op uw website mist',
    short: 'Zie in 1 minuut wat uw website mist',
    href: '/websitecheck/',
    anchor: 'wc-form',
    button: 'Check mijn website',
    next: 'U typt uw webadres en ziet meteen per punt wat goed staat en wat aandacht vraagt.',
    reason: 'Voor de uitslag hoeft u geen e-mailadres in te vullen.',
  },
  automations: {
    area: 'automations',
    name: 'Laat uitzoeken waar uw bedrijf elke week tijd verliest',
    short: 'Hoor binnen 1 werkdag waar u tijd verliest',
    href: '/scan/',
    anchor: 'scan-form',
    button: 'Vraag de gratis scan aan',
    next: 'U beantwoordt drie korte vragen. Binnen 1 werkdag staat het antwoord in uw mail.',
    reason: `We doen er ${SCANS_PER_WEEK} per week, zodat we elke aanvraag zelf lezen.`,
  },
  receptionist: {
    area: 'receptionist',
    name: 'Reken uit wat gemiste aanvragen u per maand kosten',
    short: 'Reken uit wat gemiste aanvragen kosten',
    href: '/rekentool/',
    anchor: 'roi-form',
    button: 'Reken het uit',
    next: 'U vult drie getallen in en ziet direct wat u per maand en per jaar misloopt.',
    reason: 'Het rekent met uw eigen cijfers en kost u 1 minuut.',
  },
  ads: {
    area: 'ads',
    name: '3 nieuwe openingen voor uw advertentievideo, gratis',
    short: 'Vraag 3 nieuwe openingen aan voor uw advertentie',
    href: '/advertentievideos/',
    anchor: 'aanvragen',
    button: 'Stuur uw video',
    next: 'U stuurt de link naar de advertentie die nu draait. Binnen 5 werkdagen krijgt u drie nieuwe openingen terug.',
    reason: `We maken er ${FREE_OPENINGS_PER_WEEK} per week, op volgorde van aanmelding.`,
  },
}

export const miniOffers: Record<Area, MiniOffer> = {
  websites: {
    area: 'websites',
    slug: 'wordpress-op-slot',
    name: 'WordPress op slot',
    problem: 'De WordPress-site loopt achter met updates, en elke oude plugin is een open deur.',
    delivers:
      'Alles bijgewerkt, oude accounts eruit, back-ups aan, plus één pagina met wat er is gedaan.',
    price: '€\u00a0295',
    priceNote: 'eenmalig, excl. btw',
    days: 'Klaar binnen 3 werkdagen',
    hook: 'Liever meteen laten regelen?',
    send: 'het webadres',
    fixes: ['wordpress', 'php', 'https'],
    payUrl: 'https://payment-links.mollie.com/payment/hYch6bxuV7xcTBMnKLHAw',
    payAmount: '€\u00a0356,95',
  },
  ads: {
    area: 'ads',
    // 2026-11-16: replaces "Drie nieuwe openingen" (95 euro), which sold the same three
    // openings the free magnet gives away. Price from research/pricing-2026-11-15 (middle
    // band 650 to 950 euro). No Mollie link yet, so the button orders by mail.
    slug: 'zestien-versies',
    name: 'Zestien versies van één video',
    problem: 'De advertentievideo draait al een tijd en wordt steeds minder bekeken.',
    delivers:
      'Van het bestaande beeld zestien versies, elk met een andere opening, klaar om naast elkaar te testen. Filmen is niet nodig.',
    price: '€\u00a0795',
    priceNote: 'eenmalig, excl. btw',
    days: 'Klaar binnen 5 werkdagen',
    hook: 'Liever meteen het hele pakket?',
    send: 'de link naar de video',
    payUrl: '',
    payAmount: '',
  },
  automations: {
    area: 'automations',
    slug: 'offerte-opvolger',
    name: 'Offerte-opvolger',
    problem: 'Offertes gaan de deur uit en niemand belt erachteraan.',
    delivers:
      'Na 3 en na 7 dagen krijgt de klant een nette herinnering. De herinneringen stoppen zodra de klant antwoordt.',
    price: '€\u00a0195',
    priceNote: '+ €\u00a019 per maand, excl. btw',
    days: 'Draait binnen 5 werkdagen',
    hook: 'Blijven offertes liggen?',
    send: 'een korte beschrijving van hoe offertes nu verstuurd worden',
    payUrl: 'https://payment-links.mollie.com/payment/uqy7L9F44iULvsx8sBqKc',
    payAmount: '€\u00a0235,95',
  },
  receptionist: {
    area: 'receptionist',
    slug: 'vakantiewacht',
    name: 'Vakantiewacht',
    problem: 'Tijdens de vakantie neemt niemand de aanvragen aan.',
    delivers:
      'De receptionist op website en WhatsApp, tot 4 weken lang, en bij terugkomst één lijst met alle aanvragen.',
    price: '€\u00a0149',
    priceNote: 'eenmalig, excl. btw',
    days: 'Staat binnen 3 werkdagen aan',
    hook: 'Binnenkort met vakantie?',
    send: 'het webadres en de vakantiedata',
    payUrl: 'https://payment-links.mollie.com/payment/6LyT8hKSATZZG4oTfkxpe',
    payAmount: '€\u00a0180,29',
  },
}

/** Display order on /gratis/, /klein-beginnen/ and the footer: the service order (services.ts). */
export const AREAS: Area[] = ['receptionist', 'automations', 'websites', 'ads']

export const KLEIN_BEGINNEN = '/klein-beginnen/'

export function offerHref(offer: MiniOffer): string {
  return `${KLEIN_BEGINNEN}#${offer.slug}`
}

/** Pay link when set; otherwise a mail link that orders the offer. */
export function payHref(offer: MiniOffer): string {
  if (offer.payUrl) return offer.payUrl
  const subject = `Bestelling: ${offer.name}`
  return `mailto:${contact.email}?subject=${encodeURIComponent(subject)}`
}

export function payLabel(offer: MiniOffer): string {
  return offer.payUrl ? `Betaal ${offer.payAmount} incl. btw` : 'Bestel per mail'
}
