import { z } from "zod";
import {
  ConfigureForwardingInput,
  E164,
  ForwardCallInput,
  ProvisionNumberInput,
  SendSmsInput,
  TelephonyError,
} from "./types.js";
import type {
  InboundSmsHandler,
  MissedCallHandler,
  NumberLookup,
  TelephonyAdapter,
} from "./types.js";

/**
 * Twilio adapter — fallback provider (see docs/08-tech/stack-decisions.md).
 * Source: context7 /websites/twilio (fetched 2026-05-20).
 *
 * Endpoints used:
 *   POST /2010-04-01/Accounts/{Sid}/Messages.json     -> sendSms
 *   POST /2010-04-01/Accounts/{Sid}/Calls.json        -> forwardCall
 *   POST /2010-04-01/Accounts/{Sid}/IncomingPhoneNumbers.json -> provisionNumber
 *   GET  https://lookups.twilio.com/v2/PhoneNumbers/{e164}?Fields=line_type_intelligence
 *
 * Auth: HTTP Basic with (AccountSid : AuthToken).
 * Webhook signature: HMAC-SHA1 over (URL + sorted-concat of POST params),
 * base64-encoded, sent in `x-twilio-signature`. For application/json bodies
 * Twilio signs URL + raw JSON body string (see Webhook docs).
 */

export interface TwilioAdapterOptions {
  accountSid: string;
  authToken: string;
  /** Public webhook URL the Worker is mounted at — required for signature
   * verification because Twilio signs URL+params, not the body alone. */
  webhookUrl?: string;
  baseUrl?: string;
  fetchImpl?: typeof fetch;
}

const TwilioApiBase = "https://api.twilio.com";
const TwilioLookupsBase = "https://lookups.twilio.com";

const encoder = new TextEncoder();

function basicAuth(sid: string, token: string): string {
  return `Basic ${btoa(`${sid}:${token}`)}`;
}

function toBase64(buf: ArrayBuffer): string {
  let bin = "";
  const bytes = new Uint8Array(buf);
  for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]!);
  return btoa(bin);
}

function constantTimeEqualBytes(a: Uint8Array, b: Uint8Array): boolean {
  if (a.length !== b.length) return false;
  let r = 0;
  for (let i = 0; i < a.length; i++) r |= a[i]! ^ b[i]!;
  return r === 0;
}

export class TwilioAdapter implements TelephonyAdapter {
  private readonly sid: string;
  private readonly token: string;
  private readonly webhookUrl: string | undefined;
  private readonly base: string;
  private readonly fetchImpl: typeof fetch;
  private missedCallHandlers: MissedCallHandler[] = [];
  private smsInboundHandlers: InboundSmsHandler[] = [];

  constructor(opts: TwilioAdapterOptions) {
    if (!opts.accountSid || !opts.authToken) {
      throw new TelephonyError("auth", "Twilio sid/token missing", {
        provider: "twilio",
      });
    }
    this.sid = opts.accountSid;
    this.token = opts.authToken;
    this.webhookUrl = opts.webhookUrl;
    this.base = opts.baseUrl ?? TwilioApiBase;
    this.fetchImpl = opts.fetchImpl ?? fetch;
  }

  private async form(url: string, params: Record<string, string>): Promise<unknown> {
    const body = new URLSearchParams(params).toString();
    let res: Response;
    try {
      res = await this.fetchImpl(url, {
        method: "POST",
        headers: {
          authorization: basicAuth(this.sid, this.token),
          "content-type": "application/x-www-form-urlencoded",
        },
        body,
      });
    } catch (err) {
      throw new TelephonyError("unknown", `network: ${(err as Error).message}`, {
        provider: "twilio",
      });
    }
    return parseTwilioResponse(res);
  }

  private async get(url: string): Promise<unknown> {
    let res: Response;
    try {
      res = await this.fetchImpl(url, {
        method: "GET",
        headers: { authorization: basicAuth(this.sid, this.token) },
      });
    } catch (err) {
      throw new TelephonyError("unknown", `network: ${(err as Error).message}`, {
        provider: "twilio",
      });
    }
    return parseTwilioResponse(res);
  }

  async provisionNumber(opts: ProvisionNumberInput): Promise<{ e164: string }> {
    const parsed = z
      .object({ country: z.enum(["NL", "UK"]), type: z.literal("local") })
      .parse(opts);
    const json = (await this.form(
      `${this.base}/2010-04-01/Accounts/${this.sid}/IncomingPhoneNumbers.json`,
      { AreaCode: "", IsoCountry: parsed.country },
    )) as { phone_number?: string };
    if (!json.phone_number) {
      throw new TelephonyError("provider_error", "Twilio provision missing phone_number", {
        provider: "twilio",
      });
    }
    return { e164: json.phone_number };
  }

  async sendSms(opts: SendSmsInput): Promise<{ messageId: string }> {
    const parsed = SendSmsInput.parse(opts);
    const json = (await this.form(
      `${this.base}/2010-04-01/Accounts/${this.sid}/Messages.json`,
      { To: parsed.to, From: parsed.from, Body: parsed.body },
    )) as { sid?: string };
    if (!json.sid) {
      throw new TelephonyError("provider_error", "Twilio message response missing sid", {
        provider: "twilio",
      });
    }
    return { messageId: json.sid };
  }

  async configureCallForwarding(opts: ConfigureForwardingInput): Promise<void> {
    const parsed = ConfigureForwardingInput.parse(opts);
    // Twilio routes forwarding via TwiML at the IncomingPhoneNumber's VoiceUrl.
    // `targetAgentId` is treated as a TwiML Bin / Studio Flow URL.
    await this.form(
      `${this.base}/2010-04-01/Accounts/${this.sid}/IncomingPhoneNumbers.json`,
      { PhoneNumber: parsed.number, VoiceUrl: parsed.targetAgentId },
    );
  }

  async forwardCall(opts: ForwardCallInput): Promise<{ callId: string }> {
    const parsed = ForwardCallInput.parse(opts);
    // Initiate a forwarded outbound leg. `Twiml` inline keeps it Worker-friendly
    // (no need for a hosted TwiML doc). Recordings opt-in per call.
    const twiml = `<Response><Dial${parsed.recordingsEnabled ? ' record="record-from-answer"' : ""}>${escapeXml(parsed.to)}</Dial></Response>`;
    const json = (await this.form(
      `${this.base}/2010-04-01/Accounts/${this.sid}/Calls.json`,
      { To: parsed.to, From: parsed.from, Twiml: twiml },
    )) as { sid?: string };
    if (!json.sid) {
      throw new TelephonyError("provider_error", "Twilio call response missing sid", {
        provider: "twilio",
      });
    }
    return { callId: json.sid };
  }

  async lookupNumber(e164: string): Promise<NumberLookup> {
    const parsed = E164.parse(e164);
    const url = `${TwilioLookupsBase}/v2/PhoneNumbers/${encodeURIComponent(parsed)}?Fields=line_type_intelligence`;
    const json = (await this.get(url)) as {
      valid?: boolean;
      country_code?: string;
      line_type_intelligence?: { type?: string };
    };
    const t = (json.line_type_intelligence?.type ?? "").toLowerCase();
    const type: NumberLookup["type"] =
      t === "mobile" || t === "landline" || t === "fixedLine".toLowerCase()
        ? t === "fixedline"
          ? "landline"
          : (t as "mobile" | "landline")
        : t === "voip" || t === "nonfixedvoip" || t === "fixedvoip"
          ? "voip"
          : "unknown";
    return {
      valid: json.valid ?? false,
      country: json.country_code ?? "",
      type,
    };
  }

  /**
   * Twilio webhook signature: HMAC-SHA1(authToken) over
   *   URL + sortedParams.flatMap(k => k + value).join("")
   * for x-www-form-urlencoded payloads, or URL + rawBody for JSON.
   * Result is base64. Header is `x-twilio-signature`.
   *
   * `rawBody` here is the raw request body. For JSON webhooks we sign
   * URL+rawBody; for form-encoded we reconstruct the sorted-concat. We
   * detect by sniffing the leading character (`{` -> JSON, else form).
   */
  async verifyWebhookSignature(
    rawBody: string,
    signatureHeader: string,
    secret: string,
  ): Promise<boolean> {
    if (!signatureHeader || !this.webhookUrl) return false;
    const isJson = rawBody.trimStart().startsWith("{");
    let signingString: string;
    if (isJson) {
      signingString = this.webhookUrl + rawBody;
    } else {
      const params = new URLSearchParams(rawBody);
      const sorted = [...params.entries()].sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0));
      signingString =
        this.webhookUrl + sorted.map(([k, v]) => k + v).join("");
    }
    const key = await crypto.subtle.importKey(
      "raw",
      encoder.encode(secret),
      { name: "HMAC", hash: "SHA-1" },
      false,
      ["sign"],
    );
    const sig = await crypto.subtle.sign("HMAC", key, encoder.encode(signingString));
    const expected = toBase64(sig);
    return constantTimeEqualBytes(
      encoder.encode(signatureHeader.trim()),
      encoder.encode(expected),
    );
  }

  onCallMissed(handler: MissedCallHandler): void {
    this.missedCallHandlers.push(handler);
  }

  onSmsInbound(handler: InboundSmsHandler): void {
    this.smsInboundHandlers.push(handler);
  }
}

function escapeXml(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

async function parseTwilioResponse(res: Response): Promise<unknown> {
  const text = await res.text();
  let json: unknown = null;
  try {
    json = text ? JSON.parse(text) : null;
  } catch {
    // non-JSON body
  }
  if (res.ok) return json;
  if (res.status === 401 || res.status === 403) {
    throw new TelephonyError("auth", `Twilio auth failed (${res.status})`, {
      provider: "twilio",
      status: res.status,
    });
  }
  if (res.status === 429) {
    throw new TelephonyError("rate_limited", "Twilio rate limit", {
      provider: "twilio",
      status: 429,
    });
  }
  // Twilio puts error codes in body.code; 21211 = invalid To, 21614 = not mobile, etc.
  const code = (json as { code?: number } | null)?.code;
  if (code === 21211 || code === 21614 || code === 21610) {
    throw new TelephonyError(
      "invalid_number",
      `Twilio invalid number (${code})`,
      { provider: "twilio", status: res.status },
    );
  }
  throw new TelephonyError(
    "provider_error",
    `Twilio error ${res.status}: ${text.slice(0, 200)}`,
    { provider: "twilio", status: res.status },
  );
}
