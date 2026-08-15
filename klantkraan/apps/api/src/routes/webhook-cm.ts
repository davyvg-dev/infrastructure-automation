import { Hono } from 'hono'
import { CmComAdapter } from '@kk/telephony'
import type { Bindings } from '../env.js'

export const webhookCmRouter = new Hono<{ Bindings: Bindings }>()

/**
 * CM.com webhooks: missed call + inbound SMS.
 *
 * Signature verification is delegated to @kk/telephony's CmComAdapter so the
 * HMAC scheme stays co-located with the rest of the CM integration. Other
 * vendor webhooks (Synthflow/Mollie/etc.) keep using ../lib/signing.ts until
 * they get their own adapters.
 *
 * Forwarding is delegated to n8n (`WEBHOOK_N8N_URL`) so business logic stays
 * out of the edge Worker. ACK 200 fast; n8n handles retries internally.
 */

async function forwardToN8n(env: Bindings, kind: 'call' | 'sms', payload: unknown) {
  const url = `${env.WEBHOOK_N8N_URL.replace(/\/$/, '')}/webhook/cm-${kind}`
  // best-effort; the Worker should not block on n8n latency
  await fetch(url, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

function cmAdapter(env: Bindings): CmComAdapter {
  return new CmComAdapter({ apiKey: env.CM_API_KEY })
}

webhookCmRouter.post('/webhook/cm/call', async (c) => {
  const body = await c.req.text()
  const sigHeader = c.req.header('x-cm-signature') ?? ''
  const ok = await cmAdapter(c.env).verifyWebhookSignature(body, sigHeader, c.env.CM_WEBHOOK_SECRET)
  if (!ok) return c.json({ error: 'invalid_signature' }, 401)

  let payload: unknown
  try {
    payload = JSON.parse(body)
  } catch {
    return c.json({ error: 'invalid_json' }, 400)
  }

  // Note: any outbound SMS triggered by this missed-call event MUST first call
  // isSuppressed() — that gate lives in the n8n `missed-call-back` workflow.
  await forwardToN8n(c.env, 'call', payload)
  return c.json({ ok: true })
})

webhookCmRouter.post('/webhook/cm/sms', async (c) => {
  const body = await c.req.text()
  const sigHeader = c.req.header('x-cm-signature') ?? ''
  const ok = await cmAdapter(c.env).verifyWebhookSignature(body, sigHeader, c.env.CM_WEBHOOK_SECRET)
  if (!ok) return c.json({ error: 'invalid_signature' }, 401)

  let payload: unknown
  try {
    payload = JSON.parse(body)
  } catch {
    return c.json({ error: 'invalid_json' }, 400)
  }

  // Inbound "STOP" handling: the n8n workflow inserts into suppression_list.
  await forwardToN8n(c.env, 'sms', payload)
  return c.json({ ok: true })
})
