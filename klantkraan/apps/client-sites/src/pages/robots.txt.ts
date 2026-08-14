// robots.txt is generated (not a public/ asset) because the sitemap URL is
// per-client: it points at the client's own domain from client.yaml.
import type { APIRoute } from 'astro'
import { loadClient } from '../lib/client'

export const GET: APIRoute = () => {
  const { siteUrl } = loadClient()
  const body = `User-agent: *\nAllow: /\n\nSitemap: ${siteUrl}/sitemap-index.xml\n`
  return new Response(body, {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  })
}
