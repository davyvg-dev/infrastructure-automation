import { z } from 'zod'

export const sharedEnvSchema = z.object({
  NODE_ENV: z.enum(['development', 'preview', 'production']).default('development'),
  PUBLIC_API_BASE: z.string().url().default('http://localhost:8787'),
  SENTRY_DSN: z.string().url().optional(),
})

export type SharedEnv = z.infer<typeof sharedEnvSchema>

export function parseSharedEnv(input: unknown): SharedEnv {
  return sharedEnvSchema.parse(input)
}
