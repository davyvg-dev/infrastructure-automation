/**
 * HMAC-SHA256 verification helper for vendor webhooks.
 * Constant-time compare via Web Crypto. Required on every webhook
 * (see CLAUDE.md and 06-outbound/gdpr-compliance.md).
 */

const encoder = new TextEncoder()

async function importHmacKey(secret: string): Promise<CryptoKey> {
  return crypto.subtle.importKey(
    'raw',
    encoder.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign', 'verify'],
  )
}

/**
 * Returns the hex-encoded HMAC-SHA256 of `payload` with `secret`.
 */
export async function hmacSha256Hex(secret: string, payload: string): Promise<string> {
  const key = await importHmacKey(secret)
  const sig = await crypto.subtle.sign('HMAC', key, encoder.encode(payload))
  return [...new Uint8Array(sig)].map((b) => b.toString(16).padStart(2, '0')).join('')
}

/**
 * Constant-time comparison of two hex strings of equal length.
 * Returns false on length mismatch (also constant-time relative to declared length).
 */
export function constantTimeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) return false
  let result = 0
  for (let i = 0; i < a.length; i++) {
    result |= a.charCodeAt(i) ^ b.charCodeAt(i)
  }
  return result === 0
}

/**
 * Verify an inbound webhook signature. `provided` is expected hex or `sha256=...`.
 */
export async function verifyHmac(
  secret: string,
  payload: string,
  provided: string | null | undefined,
): Promise<boolean> {
  if (!provided) return false
  const clean = provided.startsWith('sha256=') ? provided.slice(7) : provided
  const expected = await hmacSha256Hex(secret, payload)
  return constantTimeEqual(clean.toLowerCase(), expected.toLowerCase())
}
