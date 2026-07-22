// context7: Astro 5 (/llmstxt/astro_build_llms-full_txt, 2026-05-20)
//           @astrojs/sitemap (/withastro/docs, 2026-05-20)
//           Tailwind v4 via @tailwindcss/vite (/tailwindlabs/tailwindcss.com)
import { defineConfig } from 'astro/config'
import cloudflare from '@astrojs/cloudflare'
import sitemap from '@astrojs/sitemap'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  site: 'https://klantkraan.nl',
  output: 'static',
  // Cloudflare Pages serves /path/ (directory build format); trailing-slash
  // internal URLs avoid a 308 redirect hop on every link.
  trailingSlash: 'always',
  adapter: cloudflare({
    platformProxy: {
      enabled: true,
    },
  }),
  integrations: [
    sitemap({
      // /r/* are private per-client dashboards — keep them out of the sitemap.
      filter: (page) => !page.includes('/r/'),
      // Stamp every entry with the build date so crawlers see fresh lastmod
      // values on each deploy.
      serialize: (item) => ({ ...item, lastmod: new Date().toISOString() }),
    }),
  ],
  vite: {
    plugins: [tailwindcss()],
    server: {
      allowedHosts: ['.trycloudflare.com'],
    },
  },
  i18n: {
    locales: ['nl', 'en', 'es'],
    defaultLocale: 'nl',
    routing: {
      // Dutch stays at the root (/prijzen/); English lives under /en/ (/en/prijzen/),
      // Spanish under /es/ (/es/prijzen/) — both keep the Dutch route names.
      prefixDefaultLocale: false,
    },
  },
})
