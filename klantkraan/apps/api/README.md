# `@kk/api` — Klantkraan edge Worker

Cloudflare Worker that fronts every webhook + form submission for Klantkraan. Single bundle, Hono router, Zod-validated bodies, HMAC-checked webhooks. Routed at `api.klantkraan.nl/*`.

Architecture context: [`klantkraan/docs/08-tech/repo-architecture.md`](../../docs/08-tech/repo-architecture.md) §`apps/api`.

## Routes

| Route | Method | Purpose | Compliance notes |
|---|---|---|---|
| `/api/intake-form` | POST | Tally intake → Attio + Neon | AVG: suppression check before any auto-reply (06-outbound/gdpr-compliance.md) |
| `/api/lead` | POST | Site lead form → Attio | AVG: suppression check |
| `/api/dashboard/:slug` | GET | Per-client aggregate, KV-cached 5 min | Public unguessable URL, no PII beyond client's own data |
| `/api/webhook/cm/call` | POST | CM.com missed call → n8n | HMAC `x-cm-signature`; downstream SMS gated by suppression |
| `/api/webhook/cm/sms` | POST | CM.com inbound SMS → n8n | HMAC; `STOP` adds to suppression_list in n8n |
| `/api/webhook/synthflow/call-end` | POST | Synthflow call summary → Neon + Attio | HMAC; **rejects 422 if `ai_disclosure_played != true`** (04-legal/ai-act-disclosure.md, AI Act art. 50) |
| `/api/webhook/calcom/booking` | POST | Cal.com booking → Neon + SMS confirmation | HMAC `x-cal-signature-256`; SMS gated by suppression |
| `/api/webhook/mollie/payment` | POST | Mollie payment → Moneybird + Neon | HMAC; form-encoded `id` only, payment fetched via API |
| `/api/webhook/signwell/signed` | POST | Contract signed → trigger n8n `client-onboarding` | HMAC `x-signwell-signature` |
| `/api/unsubscribe` | GET/POST | Signed-token opt-out, inserts into suppression_list | AVG: writes to suppression_list; Dutch confirmation page |
| `/api/health` | GET | Liveness for Uptime Kuma | Public, no PII |

The 10-route spec in `repo-architecture.md` is honoured exactly; `/api/health` is the 11th item and was already on the spec list.

## Dev

```bash
pnpm install
pnpm --filter @kk/api dev    # wrangler dev on http://127.0.0.1:8787
```

`.dev.vars` (gitignored) supplies local secrets. Format mirrors `wrangler.toml`:

```
ATTIO_API_KEY=...
CM_API_KEY=...
SYNTHFLOW_API_KEY=...
MOLLIE_API_KEY=...
CM_WEBHOOK_SECRET=...
SYNTHFLOW_WEBHOOK_SECRET=...
CALCOM_WEBHOOK_SECRET=...
MOLLIE_WEBHOOK_SECRET=...
SIGNWELL_WEBHOOK_SECRET=...
UNSUBSCRIBE_TOKEN_SECRET=...
NEON_DATABASE_URL=postgres://...
WEBHOOK_N8N_URL=https://n8n.klantkraan.nl
SENTRY_DSN=
```

## Test (curl)

```bash
# health
curl -i http://127.0.0.1:8787/api/health

# intake
curl -i -X POST http://127.0.0.1:8787/api/intake-form \
  -H 'content-type: application/json' \
  -d '{"name":"Jan de Vries","email":"jan@plumber-bv.nl","phone":"+31612345678",
       "kvk_number":"12345678","vertical":"loodgieter","tier_interest":"groei",
       "source":"google"}'

# site lead
curl -i -X POST http://127.0.0.1:8787/api/lead \
  -H 'content-type: application/json' \
  -d '{"name":"Piet","email":"piet@example.nl","message":"interesse in demo"}'

# dashboard (slug must match ^[a-z0-9-]{2,80}$)
curl -i http://127.0.0.1:8787/api/dashboard/demo-loodgieter

# CM.com call webhook (HMAC required)
BODY='{"call_id":"c1","from":"+31600000000","missed":true}'
SIG=$(printf "%s" "$BODY" | openssl dgst -sha256 -hmac "$CM_WEBHOOK_SECRET" | awk '{print $2}')
curl -i -X POST http://127.0.0.1:8787/api/webhook/cm/call \
  -H "content-type: application/json" -H "x-cm-signature: $SIG" -d "$BODY"

# Synthflow call-end (rejects 422 if ai_disclosure_played=false)
BODY='{"call_id":"sf1","agent_id":"a1","caller_e164":"+31600000000",
       "started_at":"2026-05-20T10:00:00Z","ended_at":"2026-05-20T10:02:00Z",
       "duration_s":120,"transcript":"...","summary":"...",
       "model_version":"sf-v3","voice_id":"el-nl-1",
       "prompt_sha256":"'"$(printf %0.s0 {1..64})"'",
       "ai_disclosure_played":true,"client_id":"demo-loodgieter"}'
SIG=$(printf "%s" "$BODY" | openssl dgst -sha256 -hmac "$SYNTHFLOW_WEBHOOK_SECRET" | awk '{print $2}')
curl -i -X POST http://127.0.0.1:8787/api/webhook/synthflow/call-end \
  -H "content-type: application/json" -H "x-synthflow-signature: $SIG" -d "$BODY"

# Unsubscribe (token built by the email/SMS templates in packages/messaging)
curl -i "http://127.0.0.1:8787/api/unsubscribe?t=PAYLOAD.SIG"
```

## Typecheck + lint

```bash
pnpm --filter @kk/api typecheck
pnpm --filter @kk/api lint
```

## Deploy

```bash
pnpm wrangler login            # one-time, opens browser
pnpm --filter @kk/api deploy   # wrangler deploy
```

Verify route binding in Cloudflare dashboard → Workers → `klantkraan-api` → Triggers → `api.klantkraan.nl/*`.

## Env vars / secrets

| Name | Where used | Type |
|---|---|---|
| `ATTIO_API_KEY` | intake, lead, webhook-synthflow | secret |
| `CM_API_KEY` | webhook-calcom (SMS confirmations) | secret |
| `SYNTHFLOW_API_KEY` | webhook-synthflow (future direct calls) | secret |
| `MOLLIE_API_KEY` | webhook-mollie (payment fetch) | secret |
| `MONEYBIRD_API_KEY` | webhook-mollie (invoice creation) | secret (optional) |
| `MONEYBIRD_ADMIN_ID` | webhook-mollie | secret (optional) |
| `CM_WEBHOOK_SECRET` | webhook-cm | secret |
| `SYNTHFLOW_WEBHOOK_SECRET` | webhook-synthflow | secret |
| `CALCOM_WEBHOOK_SECRET` | webhook-calcom | secret |
| `MOLLIE_WEBHOOK_SECRET` | webhook-mollie | secret |
| `SIGNWELL_WEBHOOK_SECRET` | webhook-signwell | secret |
| `UNSUBSCRIBE_TOKEN_SECRET` | unsubscribe | secret |
| `NEON_DATABASE_URL` | all persisting routes | secret |
| `WEBHOOK_N8N_URL` | webhook-cm, webhook-signwell | plain var |
| `SENTRY_DSN` | global error handler | secret (optional) |
| `KV_DASHBOARD` | dashboard cache | KV namespace binding |

Set secrets:

```bash
pnpm wrangler secret put ATTIO_API_KEY
pnpm wrangler secret put CM_WEBHOOK_SECRET
# ...repeat per row above
```

KV:

```bash
pnpm wrangler kv namespace create KV_DASHBOARD
# paste returned id into wrangler.toml under [[kv_namespaces]]
pnpm --filter @kk/api deploy
```

## Where secrets live

- **Cloudflare dashboard** → Workers → `klantkraan-api` → Settings → Variables — the source of truth at runtime.
- **Bitwarden vault** `klantkraan-infra` — encrypted master copies. Keep in sync after every rotation; rotation cadence defined in `04-legal/dpa-outline.md`.

## Per-route AVG / AI Act notes (summary)

- **Suppression check is mandatory** on any route that triggers an outbound message (intake, lead, calcom booking SMS, missed-call SMS via n8n). Source: `06-outbound/gdpr-compliance.md`.
- **AI Act art. 50 disclosure** is enforced at `/api/webhook/synthflow/call-end` — payloads with `ai_disclosure_played=false` are rejected with HTTP 422. The disclosure itself is delivered inside the Synthflow first turn (see `04-legal/ai-act-disclosure.md`).
- **HMAC verification** is mandatory on every vendor webhook; rejection is HTTP 401 with `{error: "invalid_signature"}`.
- **No cold-call automation** — there is no route here that initiates an outbound call. Founder constraint, also law (Wet ongewenste telemarketing from 2026-07-01).
- **Suppression writes**: only `/api/unsubscribe` writes directly here; CM.com `STOP` is written by n8n's `missed-call-back` workflow.

## Stubs that need real implementations

| File | What's stubbed | Lands in |
|---|---|---|
| `src/lib/neon.ts` | `sql` tag throws at runtime | `packages/db` (Drizzle + `@neondatabase/serverless`) |
| `src/lib/suppression.ts` | `isSuppressed` always returns `false` | `packages/db` (`suppression_list` table) |
| `src/lib/attio.ts` | typed Attio v2 calls — real HTTP but small surface | `packages/attio` (extended client) |
| `src/routes/webhook-mollie.ts` | `createMoneybirdInvoice` returns `{id:"stub"}` | `packages/billing` (Moneybird client) |
| `src/routes/webhook-calcom.ts` | `sendSmsViaCm` returns `{id:"stub"}` | `packages/telephony` (CM.com adapter) |
| `src/index.ts` | Sentry `captureException` is a `console.error` | Add `@sentry/cloudflare`, init in `fetch` handler |

## Source

- Hono on Cloudflare Workers: https://hono.dev/docs/getting-started/cloudflare-workers
- Wrangler config: https://developers.cloudflare.com/workers/wrangler/configuration/
- KV from Workers: https://developers.cloudflare.com/kv/api/
- Mollie webhook signature: https://docs.mollie.com/reference/webhooks
- Cal.com webhooks: https://cal.com/docs/core-features/webhooks
- Synthflow webhooks: https://docs.synthflow.ai/
- SignWell webhooks: https://developers.signwell.com/reference/webhooks
- CM.com Voice + SMS webhooks: https://developers.cm.com/
