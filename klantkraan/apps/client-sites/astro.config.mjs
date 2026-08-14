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
let site = 'https://client-not-set.invalid'
let fotosDir = null

if (slug) {
  const clientDir = path.join(appRoot, 'clients', slug)
  const yamlPath = path.join(clientDir, 'client.yaml')
  if (fs.existsSync(yamlPath)) {
    const raw = parse(fs.readFileSync(yamlPath, 'utf8'))
    if (raw && typeof raw.domein === 'string' && raw.domein.length > 0) {
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

export default defineConfig({
  site,
  output: 'static',
  // Cloudflare Pages serves /path/ (directory build format); trailing-slash
  // internal URLs avoid a 308 redirect hop on every link (same as marketing-site).
  trailingSlash: 'always',
  integrations: [
    sitemap({
      // Stamp entries with the build date so crawlers see fresh lastmod values.
      serialize: (item) => ({ ...item, lastmod: new Date().toISOString() }),
    }),
    clientFotos,
  ],
  vite: {
    plugins: [tailwindcss()],
  },
})
