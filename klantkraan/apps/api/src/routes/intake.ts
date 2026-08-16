import { Hono } from 'hono'
import { zValidator } from '@hono/zod-validator'
import { z } from 'zod'
import type { Bindings } from '../env.js'
import { createPerson, addActivity } from '../lib/attio.js'
import { getSql } from '../lib/neon.js'
import { isSuppressed } from '../lib/suppression.js'

export const intakeRouter = new Hono<{ Bindings: Bindings }>()

const IntakeSchema = z.object({
  name: z.string().min(2).max(200),
  email: z.string().email(),
  phone: z
    .string()
    .min(8)
    .max(20)
    .regex(/^\+?[0-9 ()-]+$/),
  kvk_number: z.string().regex(/^\d{8}$/, 'kvk_number must be 8 digits'),
  vertical: z.enum(['loodgieter', 'dakdekker']),
  tier_interest: z.enum(['start', 'groei', 'schaal']),
  source: z.string().max(200).optional(),
})

intakeRouter.post('/intake-form', zValidator('json', IntakeSchema), async (c) => {
  const data = c.req.valid('json')

  // Suppression check — AVG-required even on inbound (we may auto-reply).
  // See 06-outbound/gdpr-compliance.md.
  const supp = await isSuppressed(c.env.NEON_DATABASE_URL, {
    email: data.email,
    phone: data.phone,
  })
  if (supp.suppressed) {
    return c.json({ error: 'suppressed', reason: supp.reason }, 409)
  }

  // Attio — upsert Person + add an intake Note (stub: lands in packages/attio).
  const person = await createPerson(c.env.ATTIO_API_KEY, {
    name: data.name,
    email_addresses: [data.email],
    phone_numbers: [data.phone],
    kvk_number: data.kvk_number,
  })
  await addActivity(c.env.ATTIO_API_KEY, {
    recordId: person.id,
    type: 'note',
    content: `Intake — vertical=${data.vertical}, tier=${data.tier_interest}, source=${data.source ?? 'unknown'}`,
  })

  // Neon — persist to `intakes` table. stub: real query in packages/db.
  const _sql = getSql(c.env.NEON_DATABASE_URL)
  // await _sql`INSERT INTO intakes (...) VALUES (...)`;

  return c.json({ id: person.id }, 201)
})
