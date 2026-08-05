import { Hono } from "hono";
import { cors } from "hono/cors";
import type { Bindings } from "./env.js";
import { intakeRouter } from "./routes/intake.js";
import { leadRouter } from "./routes/lead.js";
import { dashboardRouter } from "./routes/dashboard.js";
import { webhookCmRouter } from "./routes/webhook-cm.js";
import { webhookSynthflowRouter } from "./routes/webhook-synthflow.js";
import { webhookCalcomRouter } from "./routes/webhook-calcom.js";
import { webhookMollieRouter } from "./routes/webhook-mollie.js";
import { webhookSignwellRouter } from "./routes/webhook-signwell.js";
import { unsubscribeRouter } from "./routes/unsubscribe.js";
import { voiceDemoRouter } from "./routes/voice-demo.js";
import { healthRouter } from "./routes/health.js";

// TODO: import { initSentry, captureException } from "@sentry/cloudflare";
//       wire once SENTRY_DSN env exists; until then use the local stub below.
function captureException(err: unknown, ctx: Record<string, unknown>): void {
  // stub — replace with Sentry SDK call once dependency lands
  console.error(JSON.stringify({ level: "error", ts: new Date().toISOString(), err: String(err), ...ctx }));
}

type Variables = {
  request_id: string;
  client_id?: string;
  started_at: number;
};

const app = new Hono<{ Bindings: Bindings; Variables: Variables }>();

// ---------------------------------------------------------------------------
// CORS — production zone + Cloudflare Pages previews. Adjust patterns when
// staging domains are added.
// ---------------------------------------------------------------------------
app.use(
  "*",
  cors({
    origin: (origin) => {
      if (!origin) return null;
      if (origin === "https://klantkraan.nl") return origin;
      if (origin === "https://www.klantkraan.nl") return origin;
      if (origin.endsWith(".klantkraan-marketing.pages.dev")) return origin;
      if (origin.endsWith(".pages.dev") && origin.includes("klantkraan")) return origin;
      return null;
    },
    allowMethods: ["GET", "POST", "OPTIONS"],
    allowHeaders: ["content-type", "authorization", "x-request-id"],
    maxAge: 600,
  }),
);

// ---------------------------------------------------------------------------
// Structured logging middleware. One JSON line per request:
// {level, ts, route, method, status, duration_ms, client_id?, request_id}
// ---------------------------------------------------------------------------
app.use("*", async (c, next) => {
  const request_id =
    c.req.header("x-request-id") ?? crypto.randomUUID();
  const started_at = Date.now();
  c.set("request_id", request_id);
  c.set("started_at", started_at);

  // best-effort client_id extraction (slug param or body field); routes can
  // overwrite via c.set("client_id", ...) when they know better.
  const slugFromPath = c.req.path.match(/\/api\/dashboard\/([^/]+)/)?.[1];
  if (slugFromPath) c.set("client_id", slugFromPath);

  await next();

  const duration_ms = Date.now() - started_at;
  const line = {
    level: c.res.status >= 500 ? "error" : c.res.status >= 400 ? "warn" : "info",
    ts: new Date().toISOString(),
    route: c.req.routePath,
    method: c.req.method,
    path: c.req.path,
    status: c.res.status,
    duration_ms,
    client_id: c.get("client_id"),
    request_id,
  };
  console.log(JSON.stringify(line));
  c.res.headers.set("x-request-id", request_id);
});

// ---------------------------------------------------------------------------
// Global error handler. Never leak vendor errors to the client; surface a
// stable request_id so support can correlate.
// ---------------------------------------------------------------------------
app.onError((err, c) => {
  const request_id = c.get("request_id") ?? "unknown";
  captureException(err, {
    request_id,
    route: c.req.routePath,
    path: c.req.path,
    method: c.req.method,
  });
  const status = (err as { status?: number }).status ?? 500;
  return c.json(
    { error: status >= 500 ? "internal_error" : err.message, request_id },
    status as 400 | 401 | 403 | 404 | 422 | 500,
  );
});

app.notFound((c) =>
  c.json({ error: "not_found", request_id: c.get("request_id") }, 404),
);

// ---------------------------------------------------------------------------
// Root + route mounts. Order doesn't matter for Hono dispatch but keep
// alphabetical-ish for readability.
// ---------------------------------------------------------------------------
app.get("/", (c) => c.text("klantkraan-api"));

app.route("/api", healthRouter);
app.route("/api", intakeRouter);
app.route("/api", leadRouter);
app.route("/api", dashboardRouter);
app.route("/api", unsubscribeRouter);
app.route("/api", voiceDemoRouter);
app.route("/api", webhookCmRouter);
app.route("/api", webhookSynthflowRouter);
app.route("/api", webhookCalcomRouter);
app.route("/api", webhookMollieRouter);
app.route("/api", webhookSignwellRouter);

export default app;
