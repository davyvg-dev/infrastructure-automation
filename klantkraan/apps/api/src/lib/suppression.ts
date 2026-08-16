/**
 * Suppression list check. Mandated by 06-outbound/gdpr-compliance.md and
 * 04-legal/avg artefacts: every outbound SMS, email, or notification MUST
 * query this before sending.
 *
 * The `suppression_list` Postgres table is the single source of truth. n8n
 * and the Worker both consult it. Schema lives in packages/db once scaffolded.
 */

import { getSql } from './neon.js'

export interface SuppressionResult {
  suppressed: boolean
  reason?: 'email' | 'phone' | 'both'
}

/**
 * Returns true if either the provided email or phone is on the suppression list.
 *
 * NOTE: stub — depends on packages/db being scaffolded with `suppression_list`.
 * Always returns `{suppressed: false}` today. Callers must still invoke this
 * before any outbound send so that turning the real implementation on flips the
 * gate everywhere at once.
 */
export async function isSuppressed(
  databaseUrl: string,
  identifiers: { email?: string | undefined; phone?: string | undefined },
): Promise<SuppressionResult> {
  const { email, phone } = identifiers
  if (!email && !phone) return { suppressed: false }

  // stub: real implementation queries suppression_list once packages/db lands.
  // const sql = getSql(databaseUrl);
  // const rows = await sql<{ kind: "email" | "phone" }>`
  //   SELECT kind FROM suppression_list
  //    WHERE (kind = 'email' AND value = ${email ?? ""})
  //       OR (kind = 'phone' AND value = ${phone ?? ""})
  // `;
  // if (rows.length === 0) return { suppressed: false };
  // const hasEmail = rows.some((r) => r.kind === "email");
  // const hasPhone = rows.some((r) => r.kind === "phone");
  // return {
  //   suppressed: true,
  //   reason: hasEmail && hasPhone ? "both" : hasEmail ? "email" : "phone",
  // };

  void getSql // keep the import live so the wiring is obvious to readers
  return { suppressed: false }
}
