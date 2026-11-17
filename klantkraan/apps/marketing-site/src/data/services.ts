/**
 * The four services: the one source for their names, prices and links, the way
 * magnets.ts is for the free first steps and the mini offers (plan
 * 2026-11-16-homepage-four-services). The homepage hero, the service cards, the
 * bands on /, the header's Diensten menu and /prijzen/ all read from here.
 *
 * Rules:
 * - Prices are excl. btw and shown as is. \u00a0 keeps "€ 45" on one line.
 * - Only claims the founder confirmed: no "small fixes" in website care, no term
 *   (monthly, cancellable) for the € 45 until it is confirmed.
 * - The free step and the small step are the records in magnets.ts, not copies.
 */
import { magnets, miniOffers, type Area, type Magnet, type MiniOffer } from './magnets'

/** Receptionist tier prices per month, excl. btw. /prijzen/ reads these. */
export const RECEPTIONIST_PRICES = { chat: 299, compleet: 499 } as const

/** Website care per month, excl. btw (decided 16 Nov 2026). */
export const WEBSITE_CARE_PER_MONTH = 45

/** Automations: one-time build from, and management per month from, excl. btw (16 Nov 2026). */
export const AUTOMATION_BUILD_FROM = 1250
export const AUTOMATION_BEHEER_FROM = 350

export type Service = {
  area: Area
  /** Short name, the mono label on a card and the menu entry. */
  label: string
  /** The hero lamp label: what stays on. */
  circuit: string
  /** The card heading: the result for the client. */
  promise: string
  points: [string, string, string]
  /** Shown as is. */
  price: string
  /** Always names excl. btw. */
  priceNote: string
  /** The service's own page. */
  href: string
  /** The id of its band on /. */
  anchor: string
  /** The free first step (lead magnet). */
  free: Magnet
  /** The small paid start (mini offer). */
  small: MiniOffer
}

/** "€ 1.250": Dutch thousands dot, no decimals, a no-break space after the sign. */
export const eur = (n: number) => `€\u00a0${String(n).replace(/\B(?=(\d{3})+(?!\d))/g, '.')}`

export const services: Service[] = [
  {
    area: 'receptionist',
    label: 'AI-receptionist',
    circuit: 'Klanten krijgen antwoord',
    promise: 'Elke klant krijgt antwoord, ook als u op een dak staat.',
    points: [
      'Beantwoordt vragen op uw site en WhatsApp, dag en nacht',
      'Plant afspraken in uw eigen agenda',
      'Meldt zich in elk gesprek als digitale assistent',
    ],
    price: `vanaf ${eur(RECEPTIONIST_PRICES.chat)} per maand`,
    priceNote: 'excl. btw',
    href: '/ai-receptionist/',
    anchor: 'demo',
    free: magnets.receptionist,
    small: miniOffers.receptionist,
  },
  {
    area: 'automations',
    label: 'Automatiseringen',
    circuit: 'Nawerk loopt vanzelf',
    promise: 'Het werk na de klus loopt vanzelf.',
    points: [
      'Een herinnering als de klant niet op uw offerte reageert',
      'Herinneringen voor afspraken en facturen',
      'Reviewverzoeken na de klus',
    ],
    price: `vanaf ${eur(AUTOMATION_BUILD_FROM)} eenmalig`,
    priceNote: `plus beheer vanaf ${eur(AUTOMATION_BEHEER_FROM)} per maand, excl.\u00a0btw`,
    href: '/automatiseringen/',
    anchor: 'automatiseringen',
    free: magnets.automations,
    small: miniOffers.automations,
  },
  {
    area: 'websites',
    label: 'Website-onderhoud',
    circuit: 'Website snel en bijgewerkt',
    promise: 'Uw WordPress-site blijft snel, veilig en bijgewerkt.',
    points: [
      'Updates van WordPress, thema en plugins',
      'Elke dag een back-up, plus bewaking of de site online en veilig is',
      'Elke maand een snelheidscheck, met de uitslag in uw mail',
    ],
    price: `${eur(WEBSITE_CARE_PER_MONTH)} per maand`,
    priceNote: 'excl. btw',
    href: '/website-onderhoud/',
    anchor: 'website-onderhoud',
    free: magnets.websites,
    small: miniOffers.websites,
  },
  {
    area: 'ads',
    label: "Advertentievideo's",
    circuit: 'Advertenties blijven werken',
    promise: 'Uw advertentievideo krijgt nieuwe openingen, zonder opnieuw te filmen.',
    points: [
      '16 versies van één bestaande video',
      'Elke versie met een andere opening, klaar om naast elkaar te testen',
      'Eerst 3 openingen gratis, om te zien of het werkt',
    ],
    price: `${miniOffers.ads.price} per pakket`,
    priceNote: miniOffers.ads.priceNote,
    href: '/advertentievideos/',
    anchor: 'advertentievideos',
    free: magnets.ads,
    small: miniOffers.ads,
  },
]

export const serviceByArea = Object.fromEntries(services.map((s) => [s.area, s])) as Record<Area, Service>
