// Small presentation helpers shared by layout, components and JSON-LD.
import { DAGEN, type ClientConfig, type Dag } from './client'

/** tel: href for the client's phone number, with the spaces stripped. */
export function telHref(telefoon: string): string {
  return `tel:${telefoon.replace(/ /g, '')}`
}

/** wa.me href from the digits-only whatsapp field. */
export function waHref(whatsapp: string): string {
  return `https://wa.me/${whatsapp}`
}

/** URL slug for a plaats: "Alphen aan den Rijn" -> "alphen-aan-den-rijn". */
export function plaatsSlug(plaats: string): string {
  return plaats
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
}

export function capitalize(s: string): string {
  return s.charAt(0).toUpperCase() + s.slice(1)
}

export interface DagRegel {
  dag: string
  tijden: string
}

/** Ordered ma..zo rows for the hours tables; closed days say "Gesloten". */
export function openingstijdenRegels(openingstijden: ClientConfig['openingstijden']): DagRegel[] {
  return DAGEN.map((dag) => {
    const uren = openingstijden[dag]
    return {
      dag: capitalize(dag),
      tijden: uren ? `${uren[0]} tot ${uren[1]} uur` : 'Gesloten',
    }
  })
}

const SCHEMA_DAY: Record<Dag, string> = {
  maandag: 'Monday',
  dinsdag: 'Tuesday',
  woensdag: 'Wednesday',
  donderdag: 'Thursday',
  vrijdag: 'Friday',
  zaterdag: 'Saturday',
  zondag: 'Sunday',
}

/** schema.org OpeningHoursSpecification entries for LocalBusiness JSON-LD. */
export function openingHoursSpecification(openingstijden: ClientConfig['openingstijden']) {
  return DAGEN.filter((dag) => openingstijden[dag]).map((dag) => {
    const [opens, closes] = openingstijden[dag] as [string, string]
    return {
      '@type': 'OpeningHoursSpecification',
      dayOfWeek: SCHEMA_DAY[dag],
      opens,
      closes,
    }
  })
}

/** "Nieuwegein, Utrecht en IJsselstein" for running Dutch copy. */
export function somOp(items: string[]): string {
  if (items.length <= 1) return items[0] ?? ''
  return `${items.slice(0, -1).join(', ')} en ${items[items.length - 1]}`
}
