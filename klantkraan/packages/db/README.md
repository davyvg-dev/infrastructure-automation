# @kk/db

Drizzle schema + Neon HTTP client for Klantkraan. Mirrors `@kk/domain` 1:1 —
field names, enums, and nullability match the TypeScript interfaces, so the
domain layer remains the canonical source of truth.

## Tables

`clients`, `calls`, `bookings`, `reviews`, `suppression_list`, `mrr_snapshots`,
`events`. See `src/schema.ts` for column-by-column definitions and the inferred
`*Row` / `*Insert` types.

## Runtime: Workers must use the HTTP driver

Cloudflare Workers cannot open TCP or WebSocket connections, so this package
exports a Drizzle client bound to `@neondatabase/serverless`'s `neon()` (HTTP
only):

```ts
import { createDb } from "@kk/db";
const db = createDb(env.NEON_DATABASE_URL);
```

Do not import `drizzle-orm/neon-serverless` here — it requires a `ws` shim
that breaks the Workers build.

## Migrations against a Neon branch

1. Create a Neon branch (`main` or a feature branch) and copy its connection string.
2. From the repo root, generate a migration after editing the schema:

   ```sh
   NEON_DATABASE_URL="postgres://..." pnpm --filter @kk/db generate
   ```

   Drizzle Kit writes SQL into `src/migrations/`. Commit those files.

3. Apply pending migrations:

   ```sh
   NEON_DATABASE_URL="postgres://..." pnpm --filter @kk/db migrate
   ```

The migrator (`src/migrate.ts`) uses `drizzle-orm/neon-http/migrator`, which
issues each statement over HTTP — same driver as runtime, so behaviour is
identical between CI and production.

## Versions

- `drizzle-orm` ^0.36.4 (`/drizzle-team/drizzle-orm-docs`, fetched 2026-05-20)
- `drizzle-kit` ^0.31.5
- `@neondatabase/serverless` ^0.10.4
