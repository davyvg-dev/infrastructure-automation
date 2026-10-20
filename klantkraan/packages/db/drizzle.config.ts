import { defineConfig } from 'drizzle-kit'

/**
 * Drizzle Kit config. Targets Postgres (Neon) over the HTTP driver at runtime;
 * Kit itself uses the plain connection string to introspect / push / generate.
 *
 * NEON_DATABASE_URL is sourced from the environment at the time `drizzle-kit`
 * is invoked. Migrations are version-controlled at src/migrations/ so a Neon
 * branch can be rebuilt from scratch.
 */
export default defineConfig({
  dialect: 'postgresql',
  schema: './src/schema.ts',
  out: './src/migrations',
  dbCredentials: {
    url: process.env.NEON_DATABASE_URL ?? '',
  },
  strict: true,
  verbose: true,
})
