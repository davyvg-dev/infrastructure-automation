# @kk/telephony

Adapter for SMS + voice operations. One interface (`TelephonyAdapter`), two
implementations:

- **`CmComAdapter`** — PRIMARY. CM.com Business Messaging + Voice. Chosen for
  NL deliverability and native Dutch landlines (see
  `docs/08-tech/stack-decisions.md`).
- **`TwilioAdapter`** — FALLBACK. Used if CM.com has an outage or NL pricing
  shifts. Same surface; call sites do not change.

## Why swap-ability matters

Master plan §6 lists "sub-processor outage" as a top operational risk for a
business whose product is "we pick up the phone when your customer calls."
The adapter pattern caps the cost of swapping providers to a config change —
no hunting through Workers and n8n nodes for hard-coded vendor URLs.

## Usage

```ts
import { createTelephony } from "@kk/telephony";

const tel = createTelephony({ provider: "cm", apiKey: env.CM_API_KEY });
await tel.sendSms({
  to: "+31612345678",
  from: "Klantkraan",
  body: "We bellen u zo terug.",
  clientId: "client_xxx",
});
```

## Webhook signature verification

Each adapter encapsulates the provider-specific scheme:

- CM.com: HMAC-SHA256 over the raw request body, hex-encoded, in
  `x-cm-signature` (optional `sha256=` prefix).
- Twilio: HMAC-SHA1 over `URL + sortedConcat(POST params)` (or `URL + rawBody`
  for JSON), base64-encoded, in `x-twilio-signature`.

Routes should call `tel.verifyWebhookSignature(rawBody, header, secret)` and
never reach for inline HMAC code.

## Adding a third provider

1. Implement `TelephonyAdapter` in `src/<vendor>.ts`.
2. Reuse `TelephonyError`, `E164`, and the zod input schemas from `types.ts`.
3. Add the discriminator to `CreateTelephonyOptions` and a `case` in
   `createTelephony`.
4. Add a line to `__check.ts` so `tsc --noEmit` enforces the shape.

## Runtime

Workers-compatible: uses the global `fetch` + Web Crypto. No Node-only deps.
