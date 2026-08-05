import { z } from "zod";

/**
 * Worker env schema. Every secret consumed by any route lives here, even if the
 * route is stubbed. Parsed at request boundary via `parseEnv` so that a missing
 * binding fails fast with a typed error instead of a silent undefined at fetch.
 */
export const EnvSchema = z.object({
  ENV: z.enum(["development", "preview", "production"]).default("development"),

  // Vendor APIs
  ATTIO_API_KEY: z.string().min(1),
  CM_API_KEY: z.string().min(1),
  SYNTHFLOW_API_KEY: z.string().min(1),
  MOLLIE_API_KEY: z.string().min(1),
  MONEYBIRD_API_KEY: z.string().min(1).optional(),
  MONEYBIRD_ADMIN_ID: z.string().min(1).optional(),
  ELEVENLABS_API_KEY: z.string().min(1).optional(),

  // Webhook signing secrets (HMAC SHA-256)
  CM_WEBHOOK_SECRET: z.string().min(16),
  SYNTHFLOW_WEBHOOK_SECRET: z.string().min(16),
  CALCOM_WEBHOOK_SECRET: z.string().min(16),
  MOLLIE_WEBHOOK_SECRET: z.string().min(16),
  SIGNWELL_WEBHOOK_SECRET: z.string().min(16),
  UNSUBSCRIBE_TOKEN_SECRET: z.string().min(16),

  // Datastores + outbound
  NEON_DATABASE_URL: z.string().url(),
  WEBHOOK_N8N_URL: z.string().url(),

  // Observability
  SENTRY_DSN: z.string().url().optional(),
});

export type Env = z.infer<typeof EnvSchema> & {
  KV_DASHBOARD: KVNamespace;
};

/**
 * Validate the Worker runtime env. Throws a ZodError on missing/invalid bindings.
 * Call once per request inside route handlers (cheap, ~µs) or once at boot.
 */
export function parseEnv(env: unknown): Env {
  const parsed = EnvSchema.parse(env);
  const kv = (env as { KV_DASHBOARD?: KVNamespace }).KV_DASHBOARD;
  if (!kv) {
    throw new Error("KV_DASHBOARD binding missing on Worker env");
  }
  return { ...parsed, KV_DASHBOARD: kv };
}

/**
 * Hono Bindings type. Cloudflare exposes secrets + KV namespaces on `c.env`,
 * so the same shape that `parseEnv` validates is what `c.env` is typed as.
 */
export type Bindings = Env;
