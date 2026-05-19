/**
 * Neon HTTP driver factory.
 *
 * Cloudflare Workers run in the V8 isolate runtime — no TCP, no `ws`. The
 * Neon HTTP driver issues a single fetch() per query, which is the only
 * supported path on Workers. Do NOT swap this for `drizzle-orm/neon-serverless`
 * (WebSocket): it requires a Node `ws` shim and breaks the Workers build.
 *
 * Usage:
 *   import { createDb } from "@kk/db";
 *   const db = createDb(env.NEON_DATABASE_URL);
 *   const rows = await db.select().from(clients).where(...);
 */

import { neon } from "@neondatabase/serverless";
import { drizzle, type NeonHttpDatabase } from "drizzle-orm/neon-http";
import * as schema from "./schema.js";

export type Db = NeonHttpDatabase<typeof schema>;

export function createDb(databaseUrl: string): Db {
  if (!databaseUrl) {
    throw new Error("NEON_DATABASE_URL is required");
  }
  const sql = neon(databaseUrl);
  return drizzle({ client: sql, schema });
}
