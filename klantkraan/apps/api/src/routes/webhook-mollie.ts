import { Hono } from "hono";
import { z } from "zod";
import type { Bindings } from "../env.js";
import { getSql } from "../lib/neon.js";
import { verifyHmac } from "../lib/signing.js";

export const webhookMollieRouter = new Hono<{ Bindings: Bindings }>();

/**
 * Mollie payment webhook.
 *
 * Mollie pushes only the payment `id`; we then GET it from Mollie's API for
 * the actual state. On success we create a Moneybird invoice (stub) and
 * update the `subscriptions` row in Neon.
 */

const MollieFormSchema = z.object({
  id: z.string().regex(/^tr_[A-Za-z0-9]+$/),
});

interface MolliePayment {
  id: string;
  status: "open" | "canceled" | "pending" | "authorized" | "expired" | "failed" | "paid";
  amount: { currency: string; value: string };
  description: string;
  customerId?: string;
  subscriptionId?: string;
  metadata?: Record<string, unknown>;
}

async function fetchMolliePayment(apiKey: string, id: string): Promise<MolliePayment> {
  const res = await fetch(`https://api.mollie.com/v2/payments/${id}`, {
    headers: { Authorization: `Bearer ${apiKey}` },
  });
  if (!res.ok) {
    throw new Error(`mollie GET payment ${id} failed ${res.status}`);
  }
  return (await res.json()) as MolliePayment;
}

async function createMoneybirdInvoice(
  _env: Bindings,
  _payment: MolliePayment,
): Promise<{ id: string }> {
  // stub: real implementation in packages/billing once Moneybird client lands
  return { id: "stub" };
}

webhookMollieRouter.post("/webhook/mollie/payment", async (c) => {
  const body = await c.req.text();
  const ok = await verifyHmac(
    c.env.MOLLIE_WEBHOOK_SECRET,
    body,
    c.req.header("x-mollie-signature"),
  );
  if (!ok) return c.json({ error: "invalid_signature" }, 401);

  // Mollie posts application/x-www-form-urlencoded with `id=tr_...`
  const params = new URLSearchParams(body);
  const parsed = MollieFormSchema.safeParse({ id: params.get("id") ?? "" });
  if (!parsed.success) {
    return c.json({ error: "invalid_payload", details: parsed.error.flatten() }, 400);
  }

  const payment = await fetchMolliePayment(c.env.MOLLIE_API_KEY, parsed.data.id);

  if (payment.status === "paid") {
    await createMoneybirdInvoice(c.env, payment);
  }

  // Update subscription state. stub: real query in packages/db.
  const _sql = getSql(c.env.NEON_DATABASE_URL);
  // await _sql`UPDATE subscriptions SET status=${payment.status} WHERE mollie_id=${payment.id}`;

  return c.json({ ok: true, payment_id: payment.id, status: payment.status });
});
