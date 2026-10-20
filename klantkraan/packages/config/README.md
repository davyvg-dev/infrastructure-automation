# @kk/config

Shared TypeScript + Prettier + ESLint baseline and the cross-app env schema.

- `tsconfig.base.json` — strict TypeScript baseline (every app extends this).
- `src/env.ts` — zod schema for env vars shared by every app (`NODE_ENV`, `PUBLIC_API_BASE`, optional `SENTRY_DSN`). Per-app schemas extend this one.

Apps add per-app schemas in their own `src/env.ts` and call `parseSharedEnv` first, then their own `.parse()`. Boot fails fast on missing vars.
