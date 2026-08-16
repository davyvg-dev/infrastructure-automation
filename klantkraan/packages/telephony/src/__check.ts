/**
 * Compile-time shape check. `tsc --noEmit` will fail if either concrete
 * adapter drifts from the TelephonyAdapter interface or if the factory's
 * return type changes incompatibly. Not executed at runtime.
 */
import { CmComAdapter, TwilioAdapter, createTelephony, type TelephonyAdapter } from './index.js'

declare const _apiKey: string
declare const _sid: string
declare const _tok: string

const _cm: TelephonyAdapter = new CmComAdapter({ apiKey: _apiKey })
const _twilio: TelephonyAdapter = new TwilioAdapter({
  accountSid: _sid,
  authToken: _tok,
  webhookUrl: 'https://example.invalid/webhook',
})
const _viaFactoryCm: TelephonyAdapter = createTelephony({
  provider: 'cm',
  apiKey: _apiKey,
})
const _viaFactoryTwilio: TelephonyAdapter = createTelephony({
  provider: 'twilio',
  accountSid: _sid,
  authToken: _tok,
})

// Silence unused-var noise from the checker without runtime side-effects.
export const __check = { _cm, _twilio, _viaFactoryCm, _viaFactoryTwilio }
