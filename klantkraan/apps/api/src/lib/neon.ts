/**
 * Worker-side Neon entrypoint.
 *
 * Thin re-export over `@kk/db`. The real Drizzle schema + factory live in
 * `packages/db`; this file exists so routes can keep importing from a stable
 * local path (`../lib/neon.js`) without reaching into the workspace package
 * directly. The transitional `getSql` tagged-template stub is preserved as an
 * alias so existing route stubs typecheck until they are rewritten to use the
 * Drizzle query builder.
 */

import { createDb, type Db } from "@kk/db";

export { createDb };
export type { Db };

export type SqlRow = Record<string, unknown>;

export interface SqlTag {
  <T extends SqlRow = SqlRow>(strings: TemplateStringsArray, ...values: unknown[]): Promise<T[]>;
}

/**
 * Transitional shim. Returns a tagged-template `sql` that throws if invoked —
 * the route stubs that import it never actually call it yet. Once each route
 * is rewritten to use `createDb(...)` + Drizzle, remove the corresponding
 * `getSql` import and eventually delete this function.
 */
export function getSql(databaseUrl: string): SqlTag {
  if (!databaseUrl) {
    throw new Error("NEON_DATABASE_URL is required");
  }
  const tag: SqlTag = async (_strings, ..._values) => {
    throw new Error(
      "getSql is a transitional stub; migrate to `createDb(env.NEON_DATABASE_URL)` from @kk/db",
    );
  };
  return tag;
}
