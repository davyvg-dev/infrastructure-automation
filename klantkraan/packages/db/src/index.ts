/**
 * Public surface of @kk/db.
 *
 * Re-exports the full Drizzle schema (tables + enums + inferred row types) and
 * the `createDb` factory bound to the Neon HTTP driver. Consumers (the Worker,
 * n8n function nodes, future Node scripts) only ever import from here.
 */

export * from "./schema.js";
export { createDb, type Db } from "./client.js";
