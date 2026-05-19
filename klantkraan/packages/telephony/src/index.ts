export type {
  TelephonyAdapter,
  TelephonyErrorCode,
  NumberLookup,
  NumberType,
  MissedCallEvent,
  InboundSmsEvent,
  MissedCallHandler,
  InboundSmsHandler,
  SendSmsInput,
  ForwardCallInput,
  ProvisionNumberInput,
  ConfigureForwardingInput,
} from "./types.js";
export { TelephonyError, E164 } from "./types.js";

export { CmComAdapter } from "./cm-com.js";
export type { CmComAdapterOptions } from "./cm-com.js";

export { TwilioAdapter } from "./twilio.js";
export type { TwilioAdapterOptions } from "./twilio.js";

import { CmComAdapter, type CmComAdapterOptions } from "./cm-com.js";
import { TwilioAdapter, type TwilioAdapterOptions } from "./twilio.js";
import type { TelephonyAdapter } from "./types.js";

export type CreateTelephonyOptions =
  | ({ provider: "cm" } & CmComAdapterOptions)
  | ({ provider: "twilio" } & TwilioAdapterOptions);

/**
 * Build a telephony adapter for the requested provider. Call sites depend on
 * the returned `TelephonyAdapter` interface only — vendor swap is a config
 * change (see master plan §6 sub-processor-outage risk).
 */
export function createTelephony(opts: CreateTelephonyOptions): TelephonyAdapter {
  switch (opts.provider) {
    case "cm": {
      const { provider: _p, ...rest } = opts;
      return new CmComAdapter(rest);
    }
    case "twilio": {
      const { provider: _p, ...rest } = opts;
      return new TwilioAdapter(rest);
    }
  }
}
