import { Hono } from 'hono'
import type { Bindings } from '../env.js'

export const healthRouter = new Hono<{ Bindings: Bindings }>()

healthRouter.get('/health', (c) => c.json({ ok: true, ts: new Date().toISOString() }))
