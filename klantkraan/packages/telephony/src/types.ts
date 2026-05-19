import { z } from "zod";

/**
 * E.164 phone number — `+` followed by 8–15 digits. Tight on purpose: every
 * adapter rejects non-E.164 input at the boundary so vendor APIs never see
 * malformed numbers (CM.com silently no-ops on some shapes, Twilio 400s).
 */
export const E164 = z
  .string()
  .regex(/^\+[1-9]\d{7,14}$/, "must be E.164 (e.g. +31612345678)");

export const SendSmsInput = z.object({
  to: E164,
  from: z.string().min(1), // sender id (alphanum) or E.164 — vendor-validated
  body: z.string().min(1).max(1530), // 10 SMS-segment safety cap
  clientId: z.string().min(1),
});
export type SendSmsInput = z.infer<typeof SendSmsInput>;

export const ForwardCallInput = z.object({
  from: E164,
  to: E164,
  recordingsEnabled: z.boolean(),
});
export type ForwardCallInput = z.infer<typeof ForwardCallInput>;

export const ProvisionNumberInput = z.object({
  country: z.enum(["NL", "UK"]),
  type: z.literal("local"),
});
export type ProvisionNumberInput = z.infer<typeof ProvisionNumberInput>;

export const ConfigureForwardingInput = z.object({
  number: E164,
  targetAgentId: z.string().min(1),
});
export type ConfigureForwardingInput = z.infer<typeof ConfigureForwardingInput>;

export type NumberType = "mobile" | "landline" | "voip" | "unknown";

export interface NumberLookup {
  valid: boolean;
  country: string; // ISO 3166-1 alpha-2 (e.g. "NL")
  type: NumberType;
}

export interface MissedCallEvent {
  callId: string;
  fromE164: string;
  toE164: string;
  occurredAt: string; // ISO-8601
  raw: unknown;
}

export interface InboundSmsEvent {
  messageId: string;
  fromE164: string;
  toE164: string;
  body: string;
  occurredAt: string; // ISO-8601
  raw: unknown;
}

export type MissedCallHandler = (e: MissedCallEvent) => Promise<void>;
export type InboundSmsHandler = (e: InboundSmsEvent) => Promise<void>;

/**
 * Adapter contract for SMS + voice operations. Day-to-day code uses this
 * interface; vendor swap is config-change only (see master plan §6 risk:
 * sub-processor outage).
 */
export interface TelephonyAdapter {
  /** One-off number provisioning for a new client. */
  provisionNumber(opts: ProvisionNumberInput): Promise<{ e164: string }>;

  /** Outbound SMS. Returns the provider message id for audit + suppression. */
  sendSms(opts: SendSmsInput): Promise<{ messageId: string }>;

  /** Persistent call-forwarding setup (CM.com Voice routing rule). */
  configureCallForwarding(opts: ConfigureForwardingInput): Promise<void>;

  /** Per-call conditional forward (e.g. emergency escalation mid-conversation). */
  forwardCall(opts: ForwardCallInput): Promise<{ callId: string }>;

  /** Number intelligence (line type, country) for triage + outbound gating. */
  lookupNumber(e164: string): Promise<NumberLookup>;

  /**
   * Verify inbound webhook signature. The signature transport differs per
   * provider — CM.com uses HMAC-SHA256(hex) over the raw body in
   * `x-cm-signature`; Twilio uses HMAC-SHA1(base64) over URL + sorted POST
   * params in `x-twilio-signature`. Adapters encapsulate that detail; the
   * Worker just passes through the raw body + header value(s).
   */
  verifyWebhookSignature(
    rawBody: string,
    signatureHeader: string,
    secret: string,
  ): Promise<boolean>;

  /** Subscribe to missed-call events. n8n is the actual transport; this is
   * the Worker-side router that forwards parsed events. */
  onCallMissed(handler: MissedCallHandler): void;

  /** Subscribe to inbound SMS events (STOP keyword + reply routing). */
  onSmsInbound(handler: InboundSmsHandler): void;
}

export type TelephonyErrorCode =
  | "rate_limited"
  | "invalid_number"
  | "auth"
  | "provider_error"
  | "unknown";

/**
 * Typed error surfaced from every adapter call. `status` is the upstream HTTP
 * code when applicable. Call sites pattern-match on `code`, never on message.
 */
export class TelephonyError extends Error {
  readonly code: TelephonyErrorCode;
  readonly status: number | undefined;
  readonly provider: string;

  constructor(
    code: TelephonyErrorCode,
    message: string,
    opts: { provider: string; status?: number | undefined } = { provider: "unknown" },
  ) {
    super(message);
    this.name = "TelephonyError";
    this.code = code;
    this.status = opts.status;
    this.provider = opts.provider;
  }
}

/**
 * Constant-time hex-string compare. Length mismatch returns false (still
 * constant-time relative to the declared length). Lifted from the original
 * apps/api/lib/signing.ts so the adapter is self-contained.
 */
export function constantTimeEqualHex(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let result = 0;
  for (let i = 0; i < a.length; i++) {
    result |= a.charCodeAt(i) ^ b.charCodeAt(i);
  }
  return result === 0;
}
