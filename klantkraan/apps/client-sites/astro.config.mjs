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
let isPreview = false

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

const clientFotos = {
  name: 'client-fotos',
  hooks: {
    'astro:server:setup': ({ server }) => {
      if (!fotosDir || !fs.existsSync(fotosDir)) return
      server.middlewares.use('/fotos', (req, res, next) => {
        const name = path.basename(decodeURIComponent((req.url ?? '/').split('?')[0]))
        const file = path.join(fotosDir, name)
        const type = MIME[path.extname(name).toLowerCase()]
        if (!type || !fs.existsSync(file)) return next()
        res.setHeader('Content-Type', type)
        fs.createReadStream(file).pipe(res)
      })
    },
    'astro:build:done': ({ dir }) => {
      if (!fotosDir || !fs.existsSync(fotosDir)) return
      fs.cpSync(fotosDir, path.join(fileURLToPath(dir), 'fotos'), { recursive: true })
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
    previewNoindex,
  ],
  vite: {
    plugins: [tailwindcss()],
  },
})
