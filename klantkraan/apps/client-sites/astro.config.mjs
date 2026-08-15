// Pilot-kit template app: one Astro codebase, one client site per build.
// CLIENT=<slug> selects clients/<slug>/client.yaml. Static output, no adapter:
// each client site deploys to its own Cloudflare Pages project (manual, pilot).
//
// The full Zod validation lives in src/lib/client.ts and runs during the page
// build (that is where a missing/invalid CLIENT fails loudly). This config only
// peeks at `domein` to set `site` for canonicals/sitemap, and stays tolerant so
// `astro check` (typecheck) works without CLIENT set.
import { defineConfig } from 'astro/config'
import sitemap from '@astrojs/sitemap'
import tailwindcss from '@tailwindcss/vite'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { parse } from 'yaml'

const appRoot = fileURLToPath(new URL('.', import.meta.url))
const slug = process.env.CLIENT
// Kept in sync with src/lib/client.ts (PREVIEW_HOST / previewUrl): this file
// cannot import the TS module, the yaml peek here runs before the build.
const PREVIEW_HOST = process.env.PREVIEW_HOST ?? 'klant-preview.pages.dev'
let site = 'https://client-not-set.invalid'
let fotosDir = null
let stockDir = null
let fontDirs = []
let isPreview = false

// Which woff2 directories this client's typeface pairing needs. The mapping lives in
// fonts/manifest.json rather than here because src/lib/stijl.ts builds its font-family
// stacks from the same file: if the stack and the copied bytes could drift apart, the
// failure is a client's live site silently falling back to Arial. This config cannot
// import the TS module (the yaml peek runs before the build), but it can read the JSON
// they share.
const fontManifest = JSON.parse(
  fs.readFileSync(path.join(appRoot, 'fonts', 'manifest.json'), 'utf8'),
)

if (slug) {
  const clientDir = path.join(appRoot, 'clients', slug)
  const yamlPath = path.join(clientDir, 'client.yaml')
  if (fs.existsSync(yamlPath)) {
    const raw = parse(fs.readFileSync(yamlPath, 'utf8'))
    isPreview = raw?.modus === 'preview'
    if (isPreview) {
      // A proposal never canonicalises to the prospect's own domain.
      site = `https://${slug}.${PREVIEW_HOST}`
    } else if (raw && typeof raw.domein === 'string' && raw.domein.length > 0) {
      site = `https://${raw.domein}`
    }
    fotosDir = path.join(clientDir, 'fotos')
    // Only this client's own vak, so a dakdekker's site never ships a loodgieter's
    // stock photos (nor lets a visitor browse the other trades we build for).
    const vak = typeof raw?.bedrijf?.vak === 'string' ? raw.bedrijf.vak : null
    if (vak) stockDir = path.join(appRoot, 'stock', vak)
    // Same reasoning as the stock set: ship this client's typeface and nothing else, so
    // a site is not carrying 250KB of faces it never names. Unknown/absent falls through
    // to `systeem`, whose entry has no directories -- the pure system stack, no files.
    const pairing = fontManifest[raw?.stijl?.letterontwerp ?? 'systeem'] ?? fontManifest.systeem
    fontDirs = pairing?.dirs ?? []
  }
}

// Client photos live outside src/ (clients/<slug>/fotos/). Serve them at /fotos/
// in dev and copy them into dist/fotos/ on build. No image pipeline on purpose:
// the intake checklist asks for web-ready photos, and the pilot stays simple.
const MIME = {
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.png': 'image/png',
  '.webp': 'image/webp',
  '.avif': 'image/avif',
  '.svg': 'image/svg+xml',
}

// Both client photos and the per-vak stock set live outside src/ and are mounted the
// same way: served from disk in dev, copied into dist/<mount>/ on build.
const mountDir = (name, getDir, mount) => ({
  name,
  hooks: {
    'astro:server:setup': ({ server }) => {
      const dir = getDir()
      if (!dir || !fs.existsSync(dir)) return
      server.middlewares.use(`/${mount}`, (req, res, next) => {
        const file = path.join(dir, path.basename(decodeURIComponent((req.url ?? '/').split('?')[0])))
        const type = MIME[path.extname(file).toLowerCase()]
        if (!type || !fs.existsSync(file)) return next()
        res.setHeader('Content-Type', type)
        fs.createReadStream(file).pipe(res)
      })
    },
    'astro:build:done': ({ dir }) => {
      const src = getDir()
      if (!src || !fs.existsSync(src)) return
      fs.cpSync(src, path.join(fileURLToPath(dir), mount), { recursive: true })
    },
  },
})

const clientFotos = mountDir('client-fotos', () => fotosDir, 'fotos')
const clientStock = mountDir('client-stock', () => stockDir, 'stock')

// Fonts differ from the other two mounts: several source directories flatten into one
// /fonts/ mount, because src/styles/fonts.css addresses every face as /fonts/<file>.woff2
// regardless of which family it belongs to. The OFL notice travels with them -- these
// files are redistributed into a client's deploy, which is exactly the case the licence
// asks to be accompanied.
const clientFonts = {
  name: 'client-fonts',
  hooks: {
    'astro:server:setup': ({ server }) => {
      server.middlewares.use('/fonts', (req, res, next) => {
        const wanted = path.basename(decodeURIComponent((req.url ?? '/').split('?')[0]))
        for (const dir of fontDirs) {
          const file = path.join(appRoot, 'fonts', dir, wanted)
          if (!fs.existsSync(file)) continue
          res.setHeader('Content-Type', 'font/woff2')
          return fs.createReadStream(file).pipe(res)
        }
        next()
      })
    },
    'astro:build:done': ({ dir }) => {
      if (fontDirs.length === 0) return
      const out = path.join(fileURLToPath(dir), 'fonts')
      fs.mkdirSync(out, { recursive: true })
      for (const family of fontDirs) {
        const src = path.join(appRoot, 'fonts', family)
        if (!fs.existsSync(src)) throw new Error(`[client-fonts] fonts/${family}/ does not exist`)
        for (const file of fs.readdirSync(src)) {
          fs.copyFileSync(path.join(src, file), path.join(out, file))
        }
      }
      fs.copyFileSync(path.join(appRoot, 'fonts', 'OFL-NOTICE.txt'), path.join(out, 'OFL-NOTICE.txt'))
    },
  },
}

// A proposal build gets X-Robots-Tag on top of the per-page meta: the meta tag
// alone does not cover non-HTML responses, and a preview URL that gets indexed
// is the one failure mode of this whole motion.
const previewNoindex = {
  name: 'preview-noindex',
  hooks: {
    'astro:build:done': ({ dir }) => {
      if (!isPreview) return
      const headers = path.join(fileURLToPath(dir), '_headers')
      const block = '\n/*\n  X-Robots-Tag: noindex, nofollow\n'
      fs.appendFileSync(headers, block)
    },
  },
}

export default defineConfig({
  site,
  output: 'static',
  // Cloudflare Pages serves /path/ (directory build format); trailing-slash
  // internal URLs avoid a 308 redirect hop on every link (same as marketing-site).
  trailingSlash: 'always',
  integrations: [
    // No sitemap on a proposal build: nothing about it should invite a crawler.
    ...(isPreview
      ? []
      : [
          sitemap({
            // Stamp entries with the build date so crawlers see fresh lastmod values.
            serialize: (item) => ({ ...item, lastmod: new Date().toISOString() }),
          }),
        ]),
    clientFotos,
    clientStock,
    clientFonts,
    previewNoindex,
  ],
  vite: {
    plugins: [tailwindcss()],
  },
})
