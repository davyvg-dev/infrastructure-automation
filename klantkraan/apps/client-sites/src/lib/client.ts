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
// The extension is spelled out here, unlike the rest of this app's imports: the resolver
// tests run this module under plain Node, which does not resolve an extensionless specifier
// the way Vite does. Astro's tsconfig has allowImportingTsExtensions on, so both are happy.
import {
  FOTOZETTINGEN,
  KLEURINGEN,
  LETTERONTWERPEN,
  MATEN,
  PALETTEN,
  RITMES,
  SCHALEN,
  STANDAARD_STIJL,
  VORMEN,
  type Stijl,
} from './stijl.ts'
import {
  DIENSTVORMEN as DIENSTVORMEN_,
  HEROS as HEROS_,
  STANDAARD_INDELING as STANDAARD_INDELING_,
  WEGLAATBAAR as WEGLAATBAAR_,
  type Weglaatbaar as Weglaatbaar_,
} from './indeling.ts'

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

// Travels to the customer, or is travelled to. Declared here rather than in lib/toon.ts
// (which is what reads it) because toon.ts imports ClientConfig from this file, and a
// runtime constant going back the other way would close the cycle.
export const BEDRIJFSTYPEN = ['mobiel', 'locatie'] as const
export type Bedrijfstype = (typeof BEDRIJFSTYPEN)[number]

// The composition vocabulary lives in ./indeling.ts, next to the skin vocabulary in
// ./stijl.ts. Re-exported here because client.ts is what every component imports and
// `toont` (below) needs the same names.
export {
  DIENSTVORMEN,
  HEROS,
  HERO_VORM,
  STANDAARD_INDELING,
  WEGLAATBAAR,
  heroToontFoto,
  type Dienstvorm,
  type Hero,
  type Indeling,
  type Weglaatbaar,
} from './indeling.ts'

/**
 * Does this site have that section?
 *
 * One function rather than a check per component, because the answer is read in two places
 * that must agree: index.astro, which renders the section, and Header.astro, whose nav links
 * to `/#werkgebied`. A nav item pointing at an anchor the page does not contain is the kind
 * of defect that builds, passes every gate, and is only found by clicking it.
 */
export function toont(config: ClientConfig, sectie: Weglaatbaar_): boolean {
  return !config.indeling.weglaten.includes(sectie)
}

const hex = z.string().regex(/^#[0-9a-fA-F]{6}$/, 'kleur moet een #rrggbb hex-waarde zijn')
const tijd = z.string().regex(/^\d{2}:\d{2}$/, 'tijd moet HH:MM zijn, bv. "08:00"')
const dagdeel = z.tuple([tijd, tijd])

// WCAG relative luminance; primary must carry white button/header text.
//
// The floor is 5.25, not the 4.5 white-on-brand needs, because the brand colour is also
// TEXT -- links, the Hero and Werk eyebrows, .btn-outline -- on paper, card and the tinted
// bands, all of which are darker than white. 4.5:1 against white is systematically too
// generous for those 11 usages. 5.25 is the value that clears AA for every pair on every
// palet x kleuring, found by sweeping all 16.7M hex values; keep it in step with
// _MIN_CONTRAST in ai-receptionist/app/sitedraft.py, which gates the same colour before
// the paid draft call. See TODO R6b.
const MIN_CONTRAST_WITH_WHITE = 5.25

function contrastWithWhite(hexColor: string): number {
  const channel = (c: number) => {
    const s = c / 255
    return s <= 0.03928 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4
  }
  const n = parseInt(hexColor.slice(1), 16)
  const lum =
    0.2126 * channel((n >> 16) & 0xff) +
    0.7152 * channel((n >> 8) & 0xff) +
    0.0722 * channel(n & 0xff)
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
    // Does the business travel to the customer, or does the customer come to it?
    // `mobiel` is every trade the template was built for and stays the default, so a
    // client.yaml written before this field renders exactly what it always did.
    // `locatie` is the kapper, the tandarts, the hondentrimmer: one address, an agenda
    // instead of a call-out. It swaps the copy register (see lib/toon.ts) and turns the
    // werkgebied from towns travelled to into neighbourhoods travelled from.
    bedrijfstype: z.enum(BEDRIJFSTYPEN).default('mobiel'),
    // Legal identifiers: required for live, absent (never invented) for preview.
    kvk: z
      .string()
      .regex(/^\d{8}$/, 'kvk moet 8 cijfers zijn')
      .optional(),
    btw_id: z
      .string()
      .regex(/^NL\d{9}B\d{2}$/, 'btw_id moet NL#########B## zijn')
      .optional(),
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
    kleur_primair: hex.refine((c) => contrastWithWhite(c) >= MIN_CONTRAST_WITH_WHITE, {
      message:
        `kleur_primair moet donker genoeg zijn voor witte tekst EN om zelf als tekst op papier en ` +
        `getinte banden te staan (WCAG contrast met wit >= ${MIN_CONTRAST_WITH_WHITE}:1); ` +
        `kies een donkere variant van de merkkleur`,
    }),
    kleur_accent: hex,
    // Filename inside fotos/ (e.g. "logo.svg"); shown in the header when set.
    logo: z.string().optional(),
  }),
  // The skin: which of the vocabulary's looks this site is built in. Absent means
  // the look every client site had before the vocabulary existed, so an older
  // client.yaml keeps building the same bytes. Each axis defaults on its own, so a
  // partial block ("just make it roomier") is a valid config rather than an error.
  // Written by `app.sitestyle` from reference sites, or by hand.
  stijl: z
    .object({
      letterontwerp: z.enum(LETTERONTWERPEN).default(STANDAARD_STIJL.letterontwerp),
      schaal: z.enum(SCHALEN).default(STANDAARD_STIJL.schaal),
      vorm: z.enum(VORMEN).default(STANDAARD_STIJL.vorm),
      ritme: z.enum(RITMES).default(STANDAARD_STIJL.ritme),
      palet: z.enum(PALETTEN).default(STANDAARD_STIJL.palet),
      kleuring: z.enum(KLEURINGEN).default(STANDAARD_STIJL.kleuring),
      foto: z.enum(FOTOZETTINGEN).default(STANDAARD_STIJL.foto),
      maat: z.enum(MATEN).default(STANDAARD_STIJL.maat),
    })
    .default(STANDAARD_STIJL),
  // Which sections this site does NOT have.
  //
  // The counter-intuitive axis, and the one a 16-site survey of real Dutch trade sites
  // argued hardest for: those sites run 6-13 sections and every single one is missing
  // something obvious -- no reviews, a two-question FAQ, a "projecten" heading above no
  // projects. Shipping every section, filled and symmetric, is identifiable BECAUSE nothing
  // is missing. One concrete case from the same survey: no appointment-trade site (kapper,
  // trimsalon, tandarts) had a werkgebied section at all.
  //
  // Only these four are offered. Hero, diensten, the closing CTA, the hours panel and the
  // footer are how a visitor calls the business or learns when it is open, and a site that
  // drops one of those is not sparse, it is broken. Reviews already drop out on their own
  // when there are none, which in preview mode is always.
  //
  // `hero` and `diensten` are the other half of the block: not which sections exist, but
  // how the two that carry the page are arranged. See src/lib/indeling.ts for the values
  // and why each one is on offer. Both default to what the template always did, so a
  // client.yaml carrying only `weglaten` builds the same bytes it did before they existed.
  indeling: z
    .object({
      weglaten: z
        .array(z.enum(WEGLAATBAAR_))
        // At most two, so the page keeps at least six sections. Below that a trade site
        // stops reading as sparse and starts reading as unfinished, which costs the trust
        // the sparseness was buying.
        .max(2, 'hoogstens twee secties weglaten, anders oogt de pagina onaf')
        .default([]),
      hero: z.enum(HEROS_).default(STANDAARD_INDELING_.hero),
      diensten: z.enum(DIENSTVORMEN_).default(STANDAARD_INDELING_.diensten),
    })
    .default(STANDAARD_INDELING_),
  // The sentences that are this client's rather than this template's.
  //
  // Every one of these has a default in lib/toon.ts, one per bedrijfstype, and those
  // defaults are identical on every site of that register: measured 2026-08-16, two mobiel
  // voorstellen for different vakken in different towns shared a 40-word passage made of
  // exactly these slots. Filling them in is what makes two sites read as two businesses.
  // Written by `app.sitedraft` from the prospect's own sources, or by hand; every key is
  // optional and an absent one falls back to the register default.
  //
  // No `min()` on the strings and no list of allowed values: these are Dutch sentences a
  // human reads before the site ships, and a schema cannot tell a good one from a bad one.
  // What the schema CAN do is keep them out of the places copy must not go, which is why
  // the price ban and the placeholder ban live in the fact gate over the rendered page
  // rather than here.
  teksten: z
    .object({
      /** The H1. */
      kop: z.string().optional(),
      /** Hero subline, under the H1. */
      belofte: z.string().optional(),
      /** Intro heading. */
      intro_kop: z.string().optional(),
      /** Intro, first paragraph: how working with them goes. */
      werkwijze: z.string().optional(),
      /** Intro, second paragraph: where they are, or where they go. */
      bereik: z.string().optional(),
      /** The line under "Onze diensten". */
      diensten_tekst: z.string().optional(),
      /** Closing CTA heading and body. */
      slot_kop: z.string().optional(),
      slot_tekst: z.string().optional(),
    })
    .optional(),
  // The client's own photographs, in the order the page uses them: the first is the hero
  // and the share card, the rest are the work band, in the tall/wide rhythm the band's
  // multi-column fill needs.
  //
  // Named on purpose. `fotos/` used to be read with readdir().sort() and `fotos[0]` became
  // the hero, so which photograph led the site was decided by ALPHABETICAL ORDER -- adding
  // `afspraak.jpg` silently replaced the hero and renaming a file reshuffled the band. A
  // client cannot guess that rule and nothing reported it. Here the role is the position in
  // this list and nothing else moves it.
  //
  // The files named are the ORIGINALS in `foto-bron/`, at whatever size and format the
  // client sent (iPhone HEIC included). scripts/client-fotos.py cuts the renditions the
  // page actually loads. Absent means this site runs on the vak's stock set, which is
  // always the case on a voorstel.
  fotos: z
    .array(
      z.object({
        /** Filename inside clients/<slug>/foto-bron/, e.g. "dak-hoofdweg.jpg". */
        bestand: z.string().min(3),
        /** Dutch description of what is in the frame. Required: these are content photos. */
        alt: z.string().min(10),
      }),
    )
    .max(7, 'maximaal zeven: een hero plus zes tegels, anders loopt de fotoband scheef')
    .optional(),
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
    // Short client-voice line next to the hours. Read whether or not `beschikbaar` is true:
    // with a storingsdienst it says how spoed works, without one it says how to reach them
    // during opening hours. A business with neither has a default for both.
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
    (acc, key) =>
      acc && typeof acc === 'object' ? (acc as Record<string, unknown>)[key] : undefined,
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
      message:
        'een voorstel kan geen receptionist claimen; zet receptionist: false bij modus: preview',
    })
  }
  if (cfg.modus === 'preview' && cfg.reviews.length > 0) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      path: ['reviews'],
      message: 'geen reviews op een voorstel: die zijn niet van ons om over te nemen',
    })
  }
  // A headline long enough to push the call button off the first screen.
  //
  // R4 measured this in the browser at 1440x800 and encoded it as `NAAM_MAX_GROOT = 34` in
  // sitestyle.py, which withdrew `schaal: groot` above 34 characters of bedrijf.naam --
  // correct while the H1 was `<naam>: vakwerk waar u op kunt rekenen.`, and aimed at the
  // wrong string since the H1 became `teksten.kop` (S2). That rule now guards a name that is
  // no longer in the headline, so it is blind in exactly the direction that hurts: a drafted
  // kop of any length ships. The ceiling is the same one R4 found -- about seventy
  // characters of H1 at `groot` in a half-width column -- so it is applied to the headline
  // itself here, where the headline actually is.
  const kop = cfg.teksten?.kop
  const KOP_MAX: Record<string, number> = { royaal: 55, groot: 70 }
  const max = KOP_MAX[cfg.stijl.schaal] ?? 90
  if (kop && kop.length > max) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      path: ['teksten', 'kop'],
      message:
        `${kop.length} tekens is te lang voor de H1 bij schaal: ${cfg.stijl.schaal} ` +
        `(maximaal ${max}); de belknop zakt dan onder de vouw. Kort de kop in of ` +
        'zet schaal een stap kleiner.',
    })
  }
  // The one cross-axis rule in the whole vocabulary.
  //
  // `schaal: royaal` sets the H1 at 88px, which is what the award reference set does and
  // what this factory was furthest from. It only works when the headline has the whole
  // column: in the split hero the copy gets roughly half of it, and 88px in ~460px is about
  // five characters a line -- the exact failure R4 measured and capped `groot` at 3.5rem to
  // avoid. Rather than re-cap the type, refuse the combination, because the fix a founder
  // actually wants here is a different hero and not a smaller headline.
  if (cfg.stijl.schaal === 'royaal' && cfg.indeling.hero === 'gesplitst') {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      path: ['stijl', 'schaal'],
      message:
        'schaal: royaal zet de H1 op 88px en dat past niet in de halve kolom van ' +
        'hero: gesplitst -- de kop loopt dan over vijf regels en duwt de belknop onder de ' +
        'vouw. Kies indeling.hero: gestapeld of typografisch, of schaal: groot.',
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

/**
 * Rendition sizes, keyed by the filename suffix scripts/stock-photos.py writes.
 * Keep in sync with RENDITIONS there; the ratio is what the pages depend on, since the
 * CSS always draws these at width:100% and only needs the box reserved correctly.
 */
const SHAPES = {
  hero: { width: 1500, height: 1000 },
  og: { width: 1200, height: 630 },
  wide: { width: 900, height: 600 },
  tall: { width: 800, height: 1200 },
} as const

export interface StockPhoto {
  /** Public URL path, e.g. /stock/dakdekker-3-tall.webp */
  src: string
  /** Intrinsic size of the rendition, so the page can reserve the box before it loads. */
  width: number
  height: number
  /**
   * Dutch description of what is in the frame, from stock/<vak>/alt.json. Describes the
   * photograph, never who did the work: a stock frame must not testify to a job this
   * client may never have done.
   */
  alt: string
}

/**
 * The stock set for one vak, split by the role each file was cropped for.
 *
 * Roles exist because one aspect ratio cannot do every job: the hero crop, the tall tile
 * and the wide tile are three different crops of three different photos, and the page
 * has to ask for them by name. A flat file list cannot express that -- and would
 * silently mis-order, since "-hero" sorts before "-1" in a plain readdir.
 */
export interface StockSet {
  /** Work-section tiles in pinned order, alternating tall and wide. */
  tiles: StockPhoto[]
  /** 3:2 crop beside the hero copy, when the vak's set defines one. */
  hero: StockPhoto | null
  /** 1200x630 share card, cut from the same frame as the hero. */
  og: StockPhoto | null
}

/**
 * The photographs this site draws, and whose they are.
 *
 * One structure for both sources, because the page treats them identically in every way
 * except two: the client's own work gets the "Ons werk" heading and an alt that says whose
 * work it is, while a stock frame is only ever "zo ziet het werk van een dakdekker eruit".
 * That honesty rule is the whole reason `eigen` travels with the set rather than being
 * re-derived per component -- Hero and Werk got it right independently once and would not
 * keep doing so.
 */
export interface Beeld {
  set: StockSet
  /** True when these are the client's own photographs rather than the vak's stock set. */
  eigen: boolean
}

export interface LoadedClient {
  slug: string
  config: ClientConfig
  /** Resolved skin, defaults filled in. Same object as config.stijl, named for the layout. */
  stijl: Stijl
  /**
   * The photographs the page draws: the client's own when `client.yaml` names them and
   * scripts/client-fotos.py has cut them, otherwise the stock set for their vak -- which
   * is always the case on a voorstel, where we do not take a prospect's images. Both roles
   * are empty/null when neither exists; the page then falls back to photo-free layouts.
   */
  beeld: Beeld
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
  let logoUrl: string | null = null
  if (logoFile && fs.existsSync(path.join(fotosDir, logoFile))) logoUrl = `/fotos/${logoFile}`
  if (logoFile && !logoUrl) {
    fail(
      `branding.logo is set to "${logoFile}" but clients/${slug}/fotos/${logoFile} does not exist.`,
    )
  }

  // The client's own set, read from the manifest scripts/client-fotos.py writes -- never
  // from the directory listing. Reading the directory is what made the hero depend on
  // alphabetical order; the manifest carries the role, the rendition's real pixel size and
  // the Dutch alt for each file, which is everything the page needs to reserve the box and
  // describe the picture.
  //
  // A `fotos:` block with no manifest is a build failure rather than a silent fallback to
  // stock: the client sent photographs and paid for a site that shows them, and quietly
  // showing a stranger's stock instead is the worst of the available behaviours.
  const eigen: StockSet = { tiles: [], hero: null, og: null }
  if (config.fotos && config.fotos.length > 0) {
    const manifestPath = path.join(fotosDir, 'fotos.json')
    if (!fs.existsSync(manifestPath)) {
      fail(
        `clients/${slug}/client.yaml names ${config.fotos.length} photo(s) but ` +
          `clients/${slug}/fotos/fotos.json does not exist. Cut the renditions first:\n` +
          `  growth-engine/.venv/bin/python klantkraan/apps/client-sites/scripts/client-fotos.py ${slug}`,
      )
    }
    const entries: Array<{
      bestand: string
      rol: 'hero' | 'wide' | 'tall'
      breedte: number
      hoogte: number
      alt: string
    }> = JSON.parse(fs.readFileSync(manifestPath, 'utf8'))
    // Stale-manifest guard. The originals and the renditions are two directories that can
    // drift, and the failure is invisible: the page renders the photo the client replaced
    // last month because nobody re-ran the script.
    if (entries.length !== config.fotos.length) {
      fail(
        `clients/${slug}/fotos/fotos.json describes ${entries.length} photo(s) but ` +
          `client.yaml names ${config.fotos.length}. Re-run scripts/client-fotos.py ${slug}.`,
      )
    }
    for (const entry of entries) {
      const foto = {
        src: `/fotos/${entry.bestand}`,
        width: entry.breedte,
        height: entry.hoogte,
        alt: entry.alt,
      }
      if (entry.rol === 'hero') eigen.hero = foto
      else eigen.tiles.push(foto)
    }
    const og = path.join(fotosDir, 'og.webp')
    if (fs.existsSync(og)) eigen.og = { src: '/fotos/og.webp', ...SHAPES.og, alt: '' }
  }

  // Stock set for the vak: only consulted when the client supplied no photos, and only
  // the client's own vak is copied into dist/ (see clientStock in astro.config.mjs).
  // Roles are matched by filename rather than globbed, so a rendition that failed to
  // generate stays null (the section drops out) instead of arriving as a stray tile
  // with the wrong aspect ratio.
  const vak = config.bedrijf.vak
  const stockDir = fileURLToPath(new URL(`../../stock/${vak}/`, import.meta.url))
  const stock: StockSet = { tiles: [], hero: null, og: null }
  const heeftEigen = eigen.hero !== null || eigen.tiles.length > 0
  if (!heeftEigen && fs.existsSync(stockDir)) {
    const files = fs.readdirSync(stockDir).filter((f) => FOTO_EXT.test(f) && !f.includes('-sm.'))
    // Written by scripts/stock-photos.py alongside the images. A missing entry is a
    // build failure rather than a silent empty alt: an undescribed photo is exactly the
    // accessibility hole this file exists to close, and it can only happen when someone
    // adds a rendition without describing it.
    const altPath = path.join(stockDir, 'alt.json')
    const alts: Record<string, string> = fs.existsSync(altPath)
      ? JSON.parse(fs.readFileSync(altPath, 'utf8'))
      : {}
    const altFor = (file: string) => {
      const text = alts[file]
      if (!text) {
        fail(
          `stock/${vak}/alt.json has no description for "${file}". Add one in ` +
            `scripts/stock-photos.py and re-run it; every stock photo needs Dutch alt text.`,
        )
      }
      return text
    }
    // Tiles are "<vak>-<n>-<shape>.webp", numbered from 1, and must render in that order:
    // a plain .sort() is lexicographic, which is fine to 9 tiles and wrong at 10. The
    // shape suffix carries the crop, so the markup never has to guess an aspect ratio.
    const TILE = new RegExp(`^${vak}-(\\d+)-(wide|tall)\\.webp$`)
    stock.tiles = files
      .map((f) => ({ f, m: f.match(TILE) }))
      .filter((x): x is { f: string; m: RegExpMatchArray } => x.m !== null)
      .sort((a, b) => Number(a.m[1]) - Number(b.m[1]))
      .map(({ f, m }) => ({
        src: `/stock/${f}`,
        ...SHAPES[m[2] as 'wide' | 'tall'],
        alt: altFor(f),
      }))
    for (const role of ['hero', 'og'] as const) {
      const name = `${vak}-${role}.webp`
      if (!files.includes(name)) continue
      // The og card is never rendered in markup, so it carries no alt of its own.
      const alt = role === 'og' ? '' : altFor(name)
      stock[role] = { src: `/stock/${name}`, ...SHAPES[role], alt }
    }
  }

  const isPreview = config.modus === 'preview'
  cached = {
    slug,
    config,
    stijl: config.stijl,
    beeld: { set: heeftEigen ? eigen : stock, eigen: heeftEigen },
    logoUrl,
    // A proposal is always served from the preview host, even when we already
    // know the prospect's domain: canonicals must never point at their own site.
    siteUrl: isPreview ? previewUrl(slug) : `https://${config.domein}`,
    isPreview,
  }
  return cached
}
