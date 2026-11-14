/**
 * GET /api/websitecheck/?url=voorbeeld.nl
 *
 * The only server-rendered route on the site: it reads the homepage someone
 * typed into /websitecheck/ and answers with the points from
 * src/lib/websitecheck.ts. It returns verdicts only, never the page it read,
 * so it cannot be used as a proxy. Called from the page's own script; requests
 * that a browser marks as coming from another site are refused.
 */
import type { APIRoute } from 'astro'
import { normaliseHost, runCheck } from '../../lib/websitecheck'

export const prerender = false

// Per worker instance, so a rough brake and not a guarantee.
const hits = new Map<string, number[]>()
const WINDOW_MS = 60_000
const MAX_PER_WINDOW = 8

function tooMany(ip: string): boolean {
  const now = Date.now()
  const recent = (hits.get(ip) ?? []).filter((t) => now - t < WINDOW_MS)
  recent.push(now)
  hits.set(ip, recent)
  if (hits.size > 5000) hits.clear()
  return recent.length > MAX_PER_WINDOW
}

const json = (body: unknown, status = 200, cache = 'no-store') =>
  new Response(JSON.stringify(body), {
    status,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Cache-Control': cache,
      'X-Robots-Tag': 'noindex',
    },
  })

export const GET: APIRoute = async ({ request, url, clientAddress }) => {
  const site = request.headers.get('sec-fetch-site')
  if (site && site !== 'same-origin') return json({ ok: false, reden: 'geweigerd' }, 403)

  const host = normaliseHost(url.searchParams.get('url') ?? '')
  if (!host) return json({ ok: false, reden: 'adres' }, 400)

  let ip = 'onbekend'
  try {
    ip = clientAddress
  } catch {
    /* not available in every runtime */
  }
  if (tooMany(ip)) return json({ ok: false, reden: 'druk' }, 429)

  // The same domain within half an hour is answered from Cloudflare's cache.
  const cache = (globalThis as { caches?: { default?: Cache } }).caches?.default
  const key = new Request(new URL(`/api/websitecheck/?url=${host}`, url.origin).href)
  try {
    const hit = await cache?.match(key)
    if (hit) return hit
  } catch {
    /* no cache in local dev */
  }

  const result = await runCheck(host)
  const res = json(result, 200, result.ok ? 'public, max-age=1800' : 'no-store')
  if (result.ok && cache) {
    try {
      await cache.put(key, res.clone())
    } catch {
      /* ignore */
    }
  }
  return res
}
