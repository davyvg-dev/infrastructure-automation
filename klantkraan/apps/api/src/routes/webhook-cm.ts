import { Hono } from "hono";
import type { Bindings } from "../env.js";
import { verifyHmac } from "../lib/signing.js";

export const webhookCmRouter = new Hono<{ Bindings: Bindings }>();

/**
 * CM.com webhooks: missed call + inbound SMS.
 *
 * HMAC verification against CM_WEBHOOK_SECRET on the raw request body.
 * Forwarding is delegated to n8n (`WEBHOOK_N8N_URL`) so business logic stays
 * out of the edge Worker. ACK 200 fast; n8n handles retries internally.
 */

async function forwardToN8n(env: Bindings, kind: "call" | "sms", payload: unknown) {
  const url = `${env.WEBHOOK_N8N_URL.replace(/\/$/, "")}/webhook/cm-${kind}`;
  // best-effort; the Worker should not block on n8n latency
  await fetch(url, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(payload),
  });
}

webhookCmRouter.post("/webhook/cm/call", async (c) => {
  const body = await c.req.text();
  const ok = await verifyHmac(
    c.env.CM_WEBHOOK_SECRET,
    body,
    c.req.header("x-cm-signature"),
  );
  if (!ok) return c.json({ error: "invalid_signature" }, 401);

  let payload: unknown;
  try {
    payload = JSON.parse(body);
  } catch {
    return c.json({ error: "invalid_json" }, 400);
  }

  // Note: any outbound SMS triggered by this missed-call event MUST first call
  // isSuppressed() — that gate lives in the n8n `missed-call-back` workflow.
  await forwardToN8n(c.env, "call", payload);
  return c.json({ ok: true });
});

webhookCmRouter.post("/webhook/cm/sms", async (c) => {
  const body = await c.req.text();
  const ok = await verifyHmac(
    c.env.CM_WEBHOOK_SECRET,
    body,
    c.req.header("x-cm-signature"),
  );
  if (!ok) return c.json({ error: "invalid_signature" }, 401);

  let payload: unknown;
  try {
    payload = JSON.parse(body);
  } catch {
    return c.json({ error: "invalid_json" }, 400);
  }

  // Inbound "STOP" handling: the n8n workflow inserts into suppression_list.
  await forwardToN8n(c.env, "sms", payload);
  return c.json({ ok: true });
});
