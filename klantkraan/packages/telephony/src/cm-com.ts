import { z } from "zod";
import {
  ConfigureForwardingInput,
  E164,
  ForwardCallInput,
  ProvisionNumberInput,
  SendSmsInput,
  TelephonyError,
  constantTimeEqualHex,
} from "./types.js";
import type {
  InboundSmsHandler,
  MissedCallHandler,
  NumberLookup,
  TelephonyAdapter,
} from "./types.js";

/**
 * CM.com adapter — primary provider for NL telephony (see
 * docs/08-tech/stack-decisions.md). CM.com is not indexed in context7 as of
 * 2026-05-20; endpoint shapes below come from CM's public OpenAPI surface
 * (Business Messaging v1.0 + Voice API v2) and the existing webhook signature
 * scheme in apps/api/src/lib/signing.ts.
 *
 * Auth: bearer token (CM_API_KEY) on every request.
 * Webhook signature: HMAC-SHA256(secret, rawBody) hex, sent in
 * `x-cm-signature`, optionally prefixed with `sha256=`.
 */

export interface CmComAdapterOptions {
  apiKey: string;
  /** Optional override (testing). Defaults to CM's prod gateway. */
  baseUrl?: string;
  /** Override the global fetch (testing). */
  fetchImpl?: typeof fetch;
}

const CmBusinessMessagingBase = "https://gw.messaging.cm.com";
const CmVoiceBase = "https://api.cm.com/voice/v2";
const CmLookupBase = "https://api.cm.com/numberverify/v1";

const encoder = new TextEncoder();

async function importHmacKey(secret: string): Promise<CryptoKey> {
  return crypto.subtle.importKey(
    "raw",
    encoder.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign", "verify"],
  );
}

function toHex(buf: ArrayBuffer): string {
  return [...new Uint8Array(buf)]
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

export class CmComAdapter implements TelephonyAdapter {
  private readonly apiKey: string;
  private readonly baseMessaging: string;
  private readonly baseVoice: string;
  private readonly baseLookup: string;
  private readonly fetchImpl: typeof fetch;
  private missedCallHandlers: MissedCallHandler[] = [];
  private smsInboundHandlers: InboundSmsHandler[] = [];

  constructor(opts: CmComAdapterOptions) {
    if (!opts.apiKey) {
      throw new TelephonyError("auth", "CM_API_KEY missing", { provider: "cm" });
    }
    this.apiKey = opts.apiKey;
    this.baseMessaging = opts.baseUrl ?? CmBusinessMessagingBase;
    this.baseVoice = CmVoiceBase;
    this.baseLookup = CmLookupBase;
    this.fetchImpl = opts.fetchImpl ?? fetch;
  }

  private async post(url: string, body: unknown): Promise<unknown> {
    let res: Response;
    try {
      res = await this.fetchImpl(url, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          "x-cm-productapikey": this.apiKey,
        },
        body: JSON.stringify(body),
      });
    } catch (err) {
      throw new TelephonyError("unknown", `network error: ${(err as Error).message}`, {
        provider: "cm",
      });
    }
    return parseCmResponse(res);
  }

  private async get(url: string): Promise<unknown> {
    let res: Response;
    try {
      res = await this.fetchImpl(url, {
        method: "GET",
        headers: { "x-cm-productapikey": this.apiKey },
      });
    } catch (err) {
      throw new TelephonyError("unknown", `network error: ${(err as Error).message}`, {
        provider: "cm",
      });
    }
    return parseCmResponse(res);
  }

  async provisionNumber(opts: ProvisionNumberInput): Promise<{ e164: string }> {
    const parsed = z
      .object({ country: z.enum(["NL", "UK"]), type: z.literal("local") })
      .parse(opts);
    const json = (await this.post(`${this.baseVoice}/numbers`, {
      country: parsed.country,
      type: parsed.type,
    })) as { number?: string; e164?: string };
    const e164 = json.e164 ?? json.number;
    if (!e164) {
      throw new TelephonyError("provider_error", "CM number response missing e164", {
        provider: "cm",
      });
    }
    return { e164 };
  }

  async sendSms(opts: SendSmsInput): Promise<{ messageId: string }> {
    const parsed = SendSmsInput.parse(opts);
    // CM Business Messaging v1.0 "send" envelope.
    const payload = {
      messages: {
        authentication: { producttoken: this.apiKey },
        msg: [
          {
            from: parsed.from,
            to: [{ number: parsed.to }],
            body: { type: "auto", content: parsed.body },
            reference: parsed.clientId,
            allowedChannels: ["SMS"],
          },
        ],
      },
    };
    const json = (await this.post(`${this.baseMessaging}/v1.0/message`, payload)) as {
      messages?: Array<{ reference?: string; messageDetails?: string; id?: string }>;
    };
    const id = json.messages?.[0]?.id ?? json.messages?.[0]?.reference;
    if (!id) {
      throw new TelephonyError("provider_error", "CM SMS response missing id", {
        provider: "cm",
      });
    }
    return { messageId: id };
  }

  async configureCallForwarding(opts: ConfigureForwardingInput): Promise<void> {
    const parsed = ConfigureForwardingInput.parse(opts);
    await this.post(`${this.baseVoice}/numbers/${encodeURIComponent(parsed.number)}/routing`, {
      destination: { type: "agent", id: parsed.targetAgentId },
    });
  }

  async forwardCall(opts: ForwardCallInput): Promise<{ callId: string }> {
    const parsed = ForwardCallInput.parse(opts);
    const json = (await this.post(`${this.baseVoice}/calls/forward`, {
      from: parsed.from,
      to: parsed.to,
      record: parsed.recordingsEnabled,
    })) as { callId?: string; id?: string };
    const callId = json.callId ?? json.id;
    if (!callId) {
      throw new TelephonyError("provider_error", "CM forward response missing callId", {
        provider: "cm",
      });
    }
    return { callId };
  }

  async lookupNumber(e164: string): Promise<NumberLookup> {
    const parsed = E164.parse(e164);
    const json = (await this.get(
      `${this.baseLookup}/lookup/${encodeURIComponent(parsed)}`,
    )) as {
      valid?: boolean;
      countryCode?: string;
      country?: string;
      lineType?: string;
    };
    const lineType = (json.lineType ?? "").toLowerCase();
    const type: NumberLookup["type"] =
      lineType === "mobile" || lineType === "landline" || lineType === "voip"
        ? lineType
        : "unknown";
    return {
      valid: json.valid ?? false,
      country: json.countryCode ?? json.country ?? "",
      type,
    };
  }

  /**
   * CM.com signs the raw request body with HMAC-SHA256 keyed by the
   * webhook secret. Header may be bare hex or `sha256=<hex>`.
   */
  async verifyWebhookSignature(
    rawBody: string,
    signatureHeader: string,
    secret: string,
  ): Promise<boolean> {
    if (!signatureHeader) return false;
    const clean = signatureHeader.startsWith("sha256=")
      ? signatureHeader.slice(7)
      : signatureHeader;
    const key = await importHmacKey(secret);
    const sig = await crypto.subtle.sign("HMAC", key, encoder.encode(rawBody));
    const expected = toHex(sig);
    return constantTimeEqualHex(clean.toLowerCase(), expected.toLowerCase());
  }

  onCallMissed(handler: MissedCallHandler): void {
    this.missedCallHandlers.push(handler);
  }

  onSmsInbound(handler: InboundSmsHandler): void {
    this.smsInboundHandlers.push(handler);
  }
}

async function parseCmResponse(res: Response): Promise<unknown> {
  const text = await res.text();
  let json: unknown = null;
  try {
    json = text ? JSON.parse(text) : null;
  } catch {
    // CM occasionally returns plain text on 4xx
  }
  if (res.ok) return json;
  if (res.status === 401 || res.status === 403) {
    throw new TelephonyError("auth", `CM auth failed (${res.status})`, {
      provider: "cm",
      status: res.status,
    });
  }
  if (res.status === 429) {
    throw new TelephonyError("rate_limited", "CM rate limit", {
      provider: "cm",
      status: 429,
    });
  }
  if (res.status === 400 && /number|msisdn/i.test(text)) {
    throw new TelephonyError("invalid_number", "CM rejected number", {
      provider: "cm",
      status: 400,
    });
  }
  throw new TelephonyError(
    "provider_error",
    `CM error ${res.status}: ${text.slice(0, 200)}`,
    { provider: "cm", status: res.status },
  );
}
