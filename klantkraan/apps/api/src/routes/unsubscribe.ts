import { Hono, type Context } from "hono";
import { z } from "zod";
import type { Bindings } from "../env.js";
import { getSql } from "../lib/neon.js";
import { constantTimeEqual, hmacSha256Hex } from "../lib/signing.js";

export const unsubscribeRouter = new Hono<{ Bindings: Bindings }>();

/**
 * Signed-token opt-out endpoint.
 *
 * Token layout (base64url): `${payload}.${sig}` where
 *   payload = base64url(JSON.stringify({email, phone, ts}))
 *   sig     = hex(HMAC-SHA256(UNSUBSCRIBE_TOKEN_SECRET, payload))
 *
 * Tokens are valid for 30 days. Both fields are optional in the JSON payload,
 * but at least one of email or phone must be present.
 */

const MAX_AGE_MS = 30 * 24 * 60 * 60 * 1000;

const PayloadSchema = z
  .object({
    email: z.string().email().optional(),
    phone: z.string().min(8).max(20).optional(),
    ts: z.number().int(),
  })
  .refine((v) => v.email || v.phone, { message: "email or phone required" });

function b64urlDecode(s: string): string {
  const padded = s.replace(/-/g, "+").replace(/_/g, "/");
  // atob exists in Workers runtime
  return atob(padded + "===".slice((padded.length + 3) % 4));
}

async function verifyToken(
  secret: string,
  token: string,
): Promise<z.infer<typeof PayloadSchema> | null> {
  const dot = token.indexOf(".");
  if (dot <= 0) return null;
  const payloadB64 = token.slice(0, dot);
  const providedSig = token.slice(dot + 1);
  const expectedSig = await hmacSha256Hex(secret, payloadB64);
  if (!constantTimeEqual(providedSig.toLowerCase(), expectedSig.toLowerCase())) return null;

  let payload: unknown;
  try {
    payload = JSON.parse(b64urlDecode(payloadB64));
  } catch {
    return null;
  }
  const parsed = PayloadSchema.safeParse(payload);
  if (!parsed.success) return null;
  if (Date.now() - parsed.data.ts > MAX_AGE_MS) return null;
  return parsed.data;
}

function confirmationPage(opts: { email?: string | undefined; phone?: string | undefined }): string {
  const identifier = opts.email ?? opts.phone ?? "";
  return `<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<title>Uitgeschreven — Klantkraan</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  body{font-family:system-ui,sans-serif;max-width:36rem;margin:4rem auto;padding:0 1rem;color:#0f172a;line-height:1.55}
  h1{font-size:1.5rem;margin-bottom:1rem}
  .id{font-family:ui-monospace,monospace;background:#f1f5f9;padding:.15rem .4rem;border-radius:.25rem}
  .note{color:#475569;font-size:.95rem;margin-top:2rem}
</style>
</head>
<body>
  <h1>U bent uitgeschreven</h1>
  <p>We hebben <span class="id">${identifier.replace(/[<&>]/g, "")}</span> toegevoegd aan onze onderdrukkingslijst.</p>
  <p>Het kan tot 24 uur duren voordat alle systemen zijn bijgewerkt.</p>
  <p class="note">Vragen? Mail naar <a href="mailto:privacy@klantkraan.nl">privacy@klantkraan.nl</a>.</p>
</body>
</html>`;
}

async function persistSuppression(
  env: Bindings,
  identifiers: { email?: string | undefined; phone?: string | undefined },
): Promise<void> {
  const _sql = getSql(env.NEON_DATABASE_URL);
  // stub: real query in packages/db
  // if (identifiers.email)
  //   await _sql`INSERT INTO suppression_list (kind, value, source, created_at)
  //              VALUES ('email', ${identifiers.email}, 'unsubscribe-link', now())
  //              ON CONFLICT (kind, value) DO NOTHING`;
  // if (identifiers.phone)
  //   await _sql`INSERT INTO suppression_list (kind, value, source, created_at)
  //              VALUES ('phone', ${identifiers.phone}, 'unsubscribe-link', now())
  //              ON CONFLICT (kind, value) DO NOTHING`;
  void identifiers;
}

async function handle(c: Context<{ Bindings: Bindings }>) {
  const token = c.req.query("t") ?? "";
  if (!token) return c.text("ontbrekend token", 400);
  const payload = await verifyToken(c.env.UNSUBSCRIBE_TOKEN_SECRET, token);
  if (!payload) return c.text("ongeldig of verlopen token", 400);

  await persistSuppression(c.env, { email: payload.email, phone: payload.phone });

  return c.html(confirmationPage({ email: payload.email, phone: payload.phone }));
}

unsubscribeRouter.get("/unsubscribe", handle);
unsubscribeRouter.post("/unsubscribe", handle);
