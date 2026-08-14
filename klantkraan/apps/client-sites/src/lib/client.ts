// Per-client configuration: Zod schema + loader.
//
// One client site = one clients/<slug>/client.yaml (+ optional fotos/ dir).
// CLIENT=<slug> selects the client at build time; the build fails loudly here
// when CLIENT is unset or the yaml is invalid. Field vocabulary mirrors the
// ai-receptionist configs (business/services/hours) where sensible, translated
// to Dutch keys because the founder fills these in per client.
//
// Deliberately absent: prices. Prices are never scraped and never published on
// client sites (pilot rule).
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { parse } from 'yaml'
import { z } from 'zod'

export const DAGEN = [
  'maandag',
  'dinsdag',
  'woensdag',
  'donderdag',
  'vrijdag',
  'zaterdag',
  'zondag',
] as const
export type Dag = (typeof DAGEN)[number]

const hex = z.string().regex(/^#[0-9a-fA-F]{6}$/, 'kleur moet een #rrggbb hex-waarde zijn')
const tijd = z.string().regex(/^\d{2}:\d{2}$/, 'tijd moet HH:MM zijn, bv. "08:00"')
const dagdeel = z.tuple([tijd, tijd])

// WCAG relative luminance; primary must carry white button/header text.
function contrastWithWhite(hexColor: string): number {
  const channel = (c: number) => {
    const s = c / 255
    return s <= 0.03928 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4
  }
  const n = parseInt(hexColor.slice(1), 16)
  const lum =
    0.2126 * channel((n >> 16) & 0xff) + 0.7152 * channel((n >> 8) & 0xff) + 0.0722 * channel(n & 0xff)
  return 1.05 / (lum + 0.05)
}

export const ClientSchema = z.object({
  bedrijf: z.object({
    naam: z.string().min(2),
    // The trade, lowercase singular noun: "dakdekker", "loodgieter", "installateur".
    // Used in template copy ("Uw dakdekker in ...").
    vak: z.string().min(2),
    kvk: z.string().regex(/^\d{8}$/, 'kvk moet 8 cijfers zijn'),
    btw_id: z.string().regex(/^NL\d{9}B\d{2}$/, 'btw_id moet NL#########B## zijn'),
    telefoon: z.string().regex(/^\+31[\d ]{9,14}$/, 'telefoon moet +31... zijn'),
    // Digits only, international format without +, for wa.me links: "31612345678".
    whatsapp: z
      .string()
      .regex(/^31\d{9}$/, 'whatsapp moet 31########## zijn (alleen cijfers)')
      .optional(),
    email: z.string().email(),
    adres: z.object({
      straat: z.string().min(2),
      postcode: z.string().regex(/^\d{4} ?[A-Z]{2}$/, 'postcode moet 1234 AB zijn'),
      plaats: z.string().min(2),
    }),
    // Max 5: the city-page template renders one page per plaats and Google's
    // doorway-page rules cap how many near-identical local pages are safe.
    werkgebied: z.array(z.string().min(2)).min(1).max(5),
  }),
  branding: z.object({
    kleur_primair: hex.refine((c) => contrastWithWhite(c) >= 4.5, {
      message:
        'kleur_primair moet donker genoeg zijn voor witte tekst (WCAG contrast >= 4.5:1); kies een donkere variant van de merkkleur',
    }),
    kleur_accent: hex,
    // Filename inside fotos/ (e.g. "logo.svg"); shown in the header when set.
    logo: z.string().optional(),
  }),
  diensten: z
    .array(
      z.object({
        naam: z.string().min(2),
        omschrijving: z.string().min(10),
      }),
    )
    .min(3)
    .max(8),
  // Per weekday [open, dicht]; omit a day to mark it closed (same convention as
  // the ai-receptionist hours block).
  openingstijden: z.object({
    maandag: dagdeel.optional(),
    dinsdag: dagdeel.optional(),
    woensdag: dagdeel.optional(),
    donderdag: dagdeel.optional(),
    vrijdag: dagdeel.optional(),
    zaterdag: dagdeel.optional(),
    zondag: dagdeel.optional(),
  }),
  spoed: z.object({
    beschikbaar: z.boolean(),
    // Short client-voice line about how spoed works, shown next to the hours.
    tekst: z.string().optional(),
  }),
  usps: z.array(z.string().min(3)).min(2).max(4),
  // Real client quotes only, max 3, plain text on the page. Never rendered as
  // review/aggregateRating structured data (manual-action risk).
  reviews: z
    .array(
      z.object({
        tekst: z.string().min(10),
        naam: z.string().min(2),
        plaats: z.string().min(2),
      }),
    )
    .max(3)
    .default([]),
  // Desired/registered domain, bare: "voorbeeld-dakwerken.nl".
  domein: z.string().regex(/^[a-z0-9][a-z0-9.-]+\.[a-z]{2,}$/, 'domein zonder https:// of www.'),
  // True when the client also has the Klantkraan receptionist: the privacy
  // page then names Klantkraan as verwerker and the site mentions 24/7
  // bereikbaarheid on phone/chat.
  receptionist: z.boolean(),
})

export type ClientConfig = z.infer<typeof ClientSchema>

export interface LoadedClient {
  slug: string
  config: ClientConfig
  /** Public URL paths of the client's photos (/fotos/...), excluding the logo. */
  fotos: string[]
  /** Public URL path of the logo, when configured and present. */
  logoUrl: string | null
  siteUrl: string
}

const FOTO_EXT = /\.(jpe?g|png|webp|avif)$/i

function fail(message: string): never {
  throw new Error(
    `\n[client-sites] BUILD STOPPED: ${message}\n` +
      `Usage: CLIENT=<slug> pnpm build (configs live in clients/<slug>/client.yaml)\n`,
  )
}

let cached: LoadedClient | null = null

export function loadClient(): LoadedClient {
  if (cached) return cached

  const slug = process.env.CLIENT
  if (!slug) {
    fail('the CLIENT environment variable is not set, so there is no client to build.')
  }

  const clientsRoot = fileURLToPath(new URL('../../clients/', import.meta.url))
  const clientDir = path.join(clientsRoot, slug)
  const yamlPath = path.join(clientDir, 'client.yaml')
  if (!fs.existsSync(yamlPath)) {
    const known = fs.existsSync(clientsRoot)
      ? fs
          .readdirSync(clientsRoot, { withFileTypes: true })
          .filter((d) => d.isDirectory())
          .map((d) => d.name)
          .join(', ')
      : '(none)'
    fail(`no config at clients/${slug}/client.yaml. Known clients: ${known}`)
  }

  let raw: unknown
  try {
    raw = parse(fs.readFileSync(yamlPath, 'utf8'))
  } catch (err) {
    fail(`clients/${slug}/client.yaml is not valid YAML: ${(err as Error).message}`)
  }

  const parsed = ClientSchema.safeParse(raw)
  if (!parsed.success) {
    const issues = parsed.error.issues
      .map((i) => `  - ${i.path.join('.') || '(root)'}: ${i.message}`)
      .join('\n')
    fail(`clients/${slug}/client.yaml failed validation:\n${issues}`)
  }
  const config = parsed.data

  const fotosDir = path.join(clientDir, 'fotos')
  const logoFile = config.branding.logo ?? null
  let fotos: string[] = []
  let logoUrl: string | null = null
  if (fs.existsSync(fotosDir)) {
    const files = fs.readdirSync(fotosDir).sort()
    fotos = files.filter((f) => FOTO_EXT.test(f) && f !== logoFile).map((f) => `/fotos/${f}`)
    if (logoFile && files.includes(logoFile)) logoUrl = `/fotos/${logoFile}`
  }
  if (logoFile && !logoUrl) {
    fail(`branding.logo is set to "${logoFile}" but clients/${slug}/fotos/${logoFile} does not exist.`)
  }

  cached = { slug, config, fotos, logoUrl, siteUrl: `https://${config.domein}` }
  return cached
}
