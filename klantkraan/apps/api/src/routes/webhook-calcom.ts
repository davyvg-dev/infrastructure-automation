import { Hono } from 'hono'
import { z } from 'zod'
import type { Bindings } from '../env.js'
import { getSql } from '../lib/neon.js'
import { verifyHmac } from '../lib/signing.js'
import { isSuppressed } from '../lib/suppression.js'

export const webhookCalcomRouter = new Hono<{ Bindings: Bindings }>()

const BookingSchema = z.object({
  triggerEvent: z.string(),
  payload: z.object({
    bookingId: z.union([z.string(), z.number()]),
    startTime: z.string(),
    endTime: z.string(),
    title: z.string(),
    attendees: z.array(
      z.object({
        name: z.string(),
        email: z.string().email(),
        phoneNumber: z.string().optional(),
      }),
    ),
    metadata: z.record(z.unknown()).optional(),
  }),
})

/**
 * CM.com SMS adapter (stub).
 * Real implementation lives in packages/telephony/src/cm.ts.
 */
async function sendSmsViaCm(args: {
  apiKey: string
  to: string
  body: string
}): Promise<{ id: string }> {
  // stub: replace with cm-adapter call once packages/telephony is scaffolded
  void args
  return { id: 'stub' }
}

webhookCalcomRouter.post('/webhook/calcom/booking', async (c) => {
  const body = await c.req.text()
  const ok = await verifyHmac(
    c.env.CALCOM_WEBHOOK_SECRET,
    body,
    c.req.header('x-cal-signature-256'),
  )
  if (!ok) return c.json({ error: 'invalid_signature' }, 401)

  let raw: unknown
  try {
    raw = JSON.parse(body)
  } catch {
    return c.json({ error: 'invalid_json' }, 400)
  }
  const parsed = BookingSchema.safeParse(raw)
  if (!parsed.success) {
    return c.json({ error: 'invalid_payload', details: parsed.error.flatten() }, 400)
  }
  const { payload } = parsed.data

  // Persist booking. stub: real query in packages/db.
  const _sql = getSql(c.env.NEON_DATABASE_URL)
  // await _sql`INSERT INTO bookings (...) VALUES (...)`;

  // Confirmation SMS — only to attendees with a phone, and only if NOT suppressed.
  for (const att of payload.attendees) {
    if (!att.phoneNumber) continue
    const supp = await isSuppressed(c.env.NEON_DATABASE_URL, {
      email: att.email,
      phone: att.phoneNumber,
    })
    if (supp.suppressed) continue
    await sendSmsViaCm({
      apiKey: c.env.CM_API_KEY,
      to: att.phoneNumber,
      body: `Bevestigd: ${payload.title} op ${new Date(payload.startTime).toLocaleString('nl-NL')}.`,
    })
  }

  return c.json({ ok: true, booking_id: String(payload.bookingId) })
})
