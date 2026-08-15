import { Hono } from 'hono'
import { z } from 'zod'
import type { Bindings } from '../env.js'
import { addActivity, findByEmail } from '../lib/attio.js'
import { getSql } from '../lib/neon.js'
import { verifyHmac } from '../lib/signing.js'

export const webhookSynthflowRouter = new Hono<{ Bindings: Bindings }>()

/**
 * Synthflow `call-end` webhook.
 *
 * AI Act Article 50 enforcement (see 04-legal/ai-act-disclosure.md):
 * `ai_disclosure_played` MUST be `true`. We reject with HTTP 422 otherwise
 * so the violation is surfaced loudly — silent acceptance would compound the
 * compliance failure and contaminate downstream records.
 */

const CallEndSchema = z.object({
  call_id: z.string().min(1),
  agent_id: z.string().min(1),
  caller_e164: z.string().min(5),
  started_at: z.string(),
  ended_at: z.string(),
  duration_s: z.number().int().nonnegative(),
  transcript: z.string(),
  summary: z.string(),
  recording_url: z.string().url().optional(),
  model_version: z.string(),
  voice_id: z.string(),
  prompt_sha256: z.string().regex(/^[a-f0-9]{64}$/, 'prompt_sha256 must be SHA-256 hex'),
  ai_disclosure_played: z.boolean(),
  client_id: z.string().min(1),
  client_email: z.string().email().optional(),
})

webhookSynthflowRouter.post('/webhook/synthflow/call-end', async (c) => {
  const body = await c.req.text()
  const ok = await verifyHmac(
    c.env.SYNTHFLOW_WEBHOOK_SECRET,
    body,
    c.req.header('x-synthflow-signature'),
  )
  if (!ok) return c.json({ error: 'invalid_signature' }, 401)

  let raw: unknown
  try {
    raw = JSON.parse(body)
  } catch {
    return c.json({ error: 'invalid_json' }, 400)
  }
  const parsed = CallEndSchema.safeParse(raw)
  if (!parsed.success) {
    return c.json({ error: 'invalid_payload', details: parsed.error.flatten() }, 400)
  }
  const data = parsed.data

  // --- Article 50 hard gate ------------------------------------------------
  if (!data.ai_disclosure_played) {
    return c.json(
      {
        error: 'ai_disclosure_required',
        reference: 'klantkraan/docs/04-legal/ai-act-disclosure.md',
        call_id: data.call_id,
      },
      422,
    )
  }

  // --- Persist to Neon (calls table). stub: real query in packages/db ------
  const _sql = getSql(c.env.NEON_DATABASE_URL)
  // await _sql`INSERT INTO calls (...) VALUES (...)`;

  // --- Attio activity ------------------------------------------------------
  if (data.client_email) {
    const person = await findByEmail(c.env.ATTIO_API_KEY, data.client_email)
    if (person) {
      await addActivity(c.env.ATTIO_API_KEY, {
        recordId: person.id,
        type: 'call',
        content: data.summary,
        metadata: {
          call_id: data.call_id,
          duration_s: data.duration_s,
          recording_url: data.recording_url,
          model_version: data.model_version,
          voice_id: data.voice_id,
          prompt_sha256: data.prompt_sha256,
        },
      })
    }
  }

  return c.json({ ok: true, call_id: data.call_id })
})
