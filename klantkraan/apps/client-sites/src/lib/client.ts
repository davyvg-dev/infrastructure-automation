// Per-client configuration: Zod schema + loader.
//
// One client site = one clients/<slug>/client.yaml (+ optional fotos/ dir).
// CLIENT=<slug> selects the client at build time; the build fails loudly here
// when CLIENT is unset or the yaml is invalid. Field vocabulary mirrors the
// ai-receptionist configs (business/services/hours) where sensible, translated
// to Dutch keys because the founder fills these in per client.
//
// Two modes, and `modus` is required so neither can happen by accident:
//   live    = a paying client's real site. Every legal field must be present
//             (KvK, btw-id, adres, e-mail, eigen domein) or the build stops.
//   preview = an unsolicited proposal built from public sources for a prospect
//             we have not sold yet. Legal identifiers are unknown and are NOT
//             invented: the schema allows them to be absent, the pages omit
//             them, the site is noindex + Disallow, carries no LocalBusiness
//             JSON-LD (no entity confusion with the real business) and shows a
//             banner naming Klantkraan as the sender. It lives on a
//             *.pages.dev preview host, never on the prospect's own domain.
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
  // Required on purpose: a forgotten mode must fail the build, never silently
  // publish a proposal or silently noindex a paying client's site.
  modus: z.enum(['preview', 'live'], {
    errorMap: () => ({ message: 'modus moet "preview" (voorstel) of "live" (echte klant) zijn' }),
  }),
  bedrijf: z.object({
    naam: z.string().min(2),
    // The trade, lowercase singular noun: "dakdekker", "loodgieter", "installateur".
    // Used in template copy ("Uw dakdekker in ...").
    vak: z.string().min(2),
    // Legal identifiers: required for live, absent (never invented) for preview.
    kvk: z.string().regex(/^\d{8}$/, 'kvk moet 8 cijfers zijn').optional(),
    btw_id: z.string().regex(/^NL\d{9}B\d{2}$/, 'btw_id moet NL#########B## zijn').optional(),
    telefoon: z.string().regex(/^\+31[\d ]{9,14}$/, 'telefoon moet +31... zijn'),
    // Digits only, international format without +, for wa.me links: "31612345678".
    whatsapp: z
      .string()
      .regex(/^31\d{9}$/, 'whatsapp moet 31########## zijn (alleen cijfers)')
      .optional(),
    email: z.string().email().optional(),
    adres: z.object({
      straat: z.string().min(2).optional(),
      postcode: z
        .string()
        .regex(/^\d{4} ?[A-Z]{2}$/, 'postcode moet 1234 AB zijn')
        .optional(),
      // Always required: the trade, the title and every page's copy are built
      // around "in <plaats> en omgeving", and public sources always yield it.
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
  // Registered domain, bare: "voorbeeld-dakwerken.nl". Live only: a preview is
  // never served from the prospect's own domain, so canonicals and the sitemap
  // point at the *.pages.dev preview host instead.
  domein: z
    .string()
    .regex(/^[a-z0-9][a-z0-9.-]+\.[a-z]{2,}$/, 'domein zonder https:// of www.')
    .optional(),
  // True when the client also has the Klantkraan receptionist: the privacy
  // page then names Klantkraan as verwerker and the site mentions 24/7
  // bereikbaarheid on phone/chat. A preview never claims this.
  receptionist: z.boolean(),
})

// Everything a live site legally needs. A preview may omit these because they
// are not public; inventing them is what this list exists to prevent.
const LIVE_VEREIST: Array<{ path: (string | number)[]; label: string }> = [
  { path: ['bedrijf', 'kvk'], label: 'KvK-nummer (footer, art. 27 Hrw)' },
  { path: ['bedrijf', 'btw_id'], label: 'btw-id (footer, art. 3:15d BW)' },
  { path: ['bedrijf', 'email'], label: 'e-mailadres' },
  { path: ['bedrijf', 'adres', 'straat'], label: 'straat' },
  { path: ['bedrijf', 'adres', 'postcode'], label: 'postcode' },
  { path: ['domein'], label: 'eigen domein' },
]

function op(root: unknown, path: (string | number)[]): unknown {
  return path.reduce<unknown>(
    (acc, key) => (acc && typeof acc === 'object' ? (acc as Record<string, unknown>)[key] : undefined),
    root,
  )
}

export const ClientSchemaChecked = ClientSchema.superRefine((cfg, ctx) => {
  if (cfg.modus === 'live') {
    for (const { path, label } of LIVE_VEREIST) {
      if (op(cfg, path) === undefined) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          path,
          message: `verplicht bij modus: live (${label}). Zet modus: preview zolang u dit nog niet heeft.`,
        })
      }
    }
  }
  if (cfg.modus === 'preview' && cfg.receptionist) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      path: ['receptionist'],
      message: 'een voorstel kan geen receptionist claimen; zet receptionist: false bij modus: preview',
    })
  }
  if (cfg.modus === 'preview' && cfg.reviews.length > 0) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      path: ['reviews'],
      message: 'geen reviews op een voorstel: die zijn niet van ons om over te nemen',
    })
  }
})

export type ClientConfig = z.infer<typeof ClientSchema>

/**
 * Host that serves proposal builds. One Cloudflare Pages project holds them all,
 * one branch per prospect slug, so speculative sites never eat into the 100
 * projects-per-account cap that real client sites need.
 */
export const PREVIEW_HOST = process.env.PREVIEW_HOST ?? 'klant-preview.pages.dev'

/** Preview URL for a prospect slug: https://<slug>.<preview host>. */
export function previewUrl(slug: string): string {
  return `https://${slug}.${PREVIEW_HOST}`
}

export interface LoadedClient {
  slug: string
  config: ClientConfig
  /** Public URL paths of the client's photos (/fotos/...), excluding the logo. */
  fotos: string[]
  /** Public URL path of the logo, when configured and present. */
  logoUrl: string | null
  siteUrl: string
  /** True for an unsolicited proposal build (noindex, banner, no JSON-LD). */
  isPreview: boolean
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

  const parsed = ClientSchemaChecked.safeParse(raw)
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

  const isPreview = config.modus === 'preview'
  cached = {
    slug,
    config,
    fotos,
    logoUrl,
    // A proposal is always served from the preview host, even when we already
    // know the prospect's domain: canonicals must never point at their own site.
    siteUrl: isPreview ? previewUrl(slug) : `https://${config.domein}`,
    isPreview,
  }
  return cached
}
