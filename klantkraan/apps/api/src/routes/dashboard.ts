import { Hono } from 'hono'
import type { Bindings } from '../env.js'
import { getSql } from '../lib/neon.js'

export const dashboardRouter = new Hono<{ Bindings: Bindings }>()

const CACHE_TTL_SECONDS = 60 * 5 // 5 minutes per spec

interface DashboardPayload {
  client_id: string
  slug: string
  generated_at: string
  recent_calls: Array<{ id: string; started_at: string; duration_s: number; outcome: string }>
  bookings: Array<{ id: string; when: string; service: string }>
  reviews: Array<{ id: string; rating: number; text: string; created_at: string }>
  missed_call_recoveries: { last_30d: number }
}

dashboardRouter.get('/dashboard/:slug', async (c) => {
  const slug = c.req.param('slug')
  if (!/^[a-z0-9-]{2,80}$/.test(slug)) {
    return c.json({ error: 'invalid_slug' }, 400)
  }

  const cacheKey = `dashboard:${slug}`
  const cached = await c.env.KV_DASHBOARD.get(cacheKey, 'json')
  if (cached) {
    c.res.headers.set('x-cache', 'HIT')
    return c.json(cached as DashboardPayload)
  }

  // stub: lands in packages/db. Aggregate across calls + bookings + reviews.
  const _sql = getSql(c.env.NEON_DATABASE_URL)
  const payload: DashboardPayload = {
    client_id: slug,
    slug,
    generated_at: new Date().toISOString(),
    recent_calls: [],
    bookings: [],
    reviews: [],
    missed_call_recoveries: { last_30d: 0 },
  }

  await c.env.KV_DASHBOARD.put(cacheKey, JSON.stringify(payload), {
    expirationTtl: CACHE_TTL_SECONDS,
  })
  c.res.headers.set('x-cache', 'MISS')
  return c.json(payload)
})
