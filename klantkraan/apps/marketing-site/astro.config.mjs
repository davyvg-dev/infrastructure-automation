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
  adapter: cloudflare({
    platformProxy: {
      enabled: true,
    },
  }),
  integrations: [
    sitemap({
      // /r/* are private per-client dashboards — keep them out of the sitemap.
      filter: (page) => !page.includes('/r/'),
    }),
  ],
  vite: {
    plugins: [tailwindcss()],
    server: {
      allowedHosts: ['.trycloudflare.com'],
    },
  },
  i18n: {
    locales: ['nl'],
    defaultLocale: 'nl',
  },
})
