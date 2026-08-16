import { Hono } from 'hono'
import { zValidator } from '@hono/zod-validator'
import { z } from 'zod'
import type { Bindings } from '../env.js'

/**
 * Call-me-back for voice-agent demos: the visitor enters their number on a
 * demo page and the ElevenLabs agent calls them from our 970 number.
 * The number stays assigned to one agent for inbound; outbound picks the
 * agent per call, so every demo shares the same number.
 */
export const voiceDemoRouter = new Hono<{ Bindings: Bindings }>()

// One entry per demo slug; a new voice demo = one line here.
const DEMOS: Record<string, { agentId: string; languages: string[] }> = {
  'cool-global': {
    agentId: 'agent_9201kz8j953jesms7g9h5er53ykg',
    languages: ['en', 'de', 'es'],
  },
  dhz: {
    agentId: 'agent_2501kz8ntph6fa6amhhtb92ve5ht',
    languages: ['nl'],
  },
}

const AGENT_PHONE_NUMBER_ID = 'phnum_5901kz73jk4kef7awz3x80kxtzq9' // +31 970 0653 0002

// EU prefixes the demo may call. Keeps the endpoint useless for toll fraud
// against far-away premium ranges; the agent's daily_limit caps volume.
const ALLOWED_PREFIXES = ['+34', '+31', '+49', '+43', '+41', '+32', '+44']

const CallSchema = z.object({
  demo: z.string().refine((s) => s in DEMOS, 'unknown demo'),
  phone: z
    .string()
    .min(8)
    .max(24)
    .regex(/^[+0-9 ()-]+$/),
  language: z.string().length(2).optional(),
})

// Best-effort in-memory throttle (per isolate — resets on eviction). The hard
// cap is the agent's daily_limit on the ElevenLabs side.
const recentByIp = new Map<string, number[]>()
const WINDOW_MS = 15 * 60 * 1000
const MAX_PER_WINDOW = 3

voiceDemoRouter.post('/voice-demo/call', zValidator('json', CallSchema), async (c) => {
  const { demo, phone, language } = c.req.valid('json')
  const cfg = DEMOS[demo]
  if (!cfg) return c.json({ error: 'unknown_demo' }, 404)

  if (!c.env.ELEVENLABS_API_KEY) {
    return c.json({ error: 'not_configured' }, 503)
  }

  // Normalize: strip separators, fold 00-prefix into +.
  let to = phone.replace(/[ ()-]/g, '')
  if (to.startsWith('00')) to = `+${to.slice(2)}`
  if (!/^\+[0-9]{8,15}$/.test(to)) {
    return c.json({ error: 'invalid_phone' }, 422)
  }
  if (!ALLOWED_PREFIXES.some((p) => to.startsWith(p))) {
    return c.json({ error: 'country_not_supported' }, 422)
  }

  const ip = c.req.header('cf-connecting-ip') ?? 'unknown'
  const now = Date.now()
  const recent = (recentByIp.get(ip) ?? []).filter((t) => now - t < WINDOW_MS)
  if (recent.length >= MAX_PER_WINDOW) {
    return c.json({ error: 'rate_limited' }, 429)
  }
  recent.push(now)
  recentByIp.set(ip, recent)

  const lang = language && cfg.languages.includes(language) ? language : undefined
  const res = await fetch('https://api.elevenlabs.io/v1/convai/twilio/outbound-call', {
    method: 'POST',
    headers: {
      'xi-api-key': c.env.ELEVENLABS_API_KEY,
      'content-type': 'application/json',
    },
    body: JSON.stringify({
      agent_id: cfg.agentId,
      agent_phone_number_id: AGENT_PHONE_NUMBER_ID,
      to_number: to,
      conversation_initiation_client_data: {
        dynamic_variables: { customer_number: to },
        ...(lang ? { conversation_config_override: { agent: { language: lang } } } : {}),
      },
    }),
  })

  if (!res.ok) {
    console.log(
      JSON.stringify({
        level: 'warn',
        evt: 'voice_demo.call_failed',
        demo,
        status: res.status,
        detail: (await res.text()).slice(0, 500),
      }),
    )
    return c.json({ error: 'call_failed' }, 502)
  }

  console.log(JSON.stringify({ level: 'info', evt: 'voice_demo.call_placed', demo, lang }))
  return c.json({ ok: true })
})
