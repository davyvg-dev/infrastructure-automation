/**
 * One-shot migration runner.
 *
 * Runs all pending `src/migrations/*` files against the Neon database pointed
 * to by NEON_DATABASE_URL. Intended for CI + local dev (Node 22), NOT for the
 * Worker. Uses the same HTTP driver as the runtime client so behaviour stays
 * identical.
 *
 * Invoke with:
 *   NEON_DATABASE_URL=... pnpm --filter @kk/db migrate
 */

import { neon } from "@neondatabase/serverless";
import { drizzle } from "drizzle-orm/neon-http";
import { migrate } from "drizzle-orm/neon-http/migrator";

async function main(): Promise<void> {
  const url = process.env["NEON_DATABASE_URL"];
  if (!url) {
    throw new Error("NEON_DATABASE_URL must be set to run migrations");
  }
  const sql = neon(url);
  const db = drizzle({ client: sql });
  await migrate(db, { migrationsFolder: "./src/migrations" });
  console.log("migrations applied");
}

main().catch((err: unknown) => {
  console.error(err);
  process.exit(1);
});
