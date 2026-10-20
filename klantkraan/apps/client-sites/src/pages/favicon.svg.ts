// Per-client favicon without any asset work: a rounded square in the brand
// color with the first letter of the bedrijfsnaam. Overridden the moment a
// client supplies a real icon (drop it in public/ as favicon.svg is generated,
// so instead change the <link rel="icon"> in Base.astro when that happens).
import type { APIRoute } from 'astro'
import { loadClient } from '../lib/client'

export const GET: APIRoute = () => {
  const { config } = loadClient()
  const letter = config.bedrijf.naam.charAt(0).toUpperCase()
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="14" fill="${config.branding.kleur_primair}"/>
  <text x="32" y="44" text-anchor="middle" font-family="system-ui, -apple-system, Arial, sans-serif" font-size="36" font-weight="700" fill="#ffffff">${letter}</text>
</svg>
`
  return new Response(svg, {
    headers: { 'Content-Type': 'image/svg+xml' },
  })
}
