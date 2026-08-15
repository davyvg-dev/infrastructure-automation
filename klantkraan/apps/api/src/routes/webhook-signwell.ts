import { Hono } from 'hono'
import { z } from 'zod'
import type { Bindings } from '../env.js'
import { verifyHmac } from '../lib/signing.js'

export const webhookSignwellRouter = new Hono<{ Bindings: Bindings }>()

const SignedSchema = z.object({
  event: z.object({
    type: z.string(),
    related_signature_request: z
      .object({
        id: z.string(),
      })
      .optional(),
  }),
  data: z
    .object({
      object: z
        .object({
          id: z.string().optional(),
          status: z.string().optional(),
          metadata: z.record(z.unknown()).optional(),
        })
        .optional(),
    })
    .optional(),
})

webhookSignwellRouter.post('/webhook/signwell/signed', async (c) => {
  const body = await c.req.text()
  const ok = await verifyHmac(
    c.env.SIGNWELL_WEBHOOK_SECRET,
    body,
    c.req.header('x-signwell-signature'),
  )
  if (!ok) return c.json({ error: 'invalid_signature' }, 401)

  let raw: unknown
  try {
    raw = JSON.parse(body)
  } catch {
    return c.json({ error: 'invalid_json' }, 400)
  }
  const parsed = SignedSchema.safeParse(raw)
  if (!parsed.success) {
    return c.json({ error: 'invalid_payload', details: parsed.error.flatten() }, 400)
  }

  // Fire `client-onboarding.json` n8n workflow.
  const url = `${c.env.WEBHOOK_N8N_URL.replace(/\/$/, '')}/webhook/client-onboarding`
  await fetch(url, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(parsed.data),
  })

  return c.json({ ok: true })
})
