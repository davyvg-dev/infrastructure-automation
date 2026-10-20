# Repo Architecture

> pnpm workspaces + Turborepo. Three apps, shared packages, a single `apps/api` Cloudflare Worker for low-latency edge endpoints. n8n workflows live in `infra/n8n/` as exported JSON for version control.

## Top-level layout

```
klantkraan/
├── README.md
├── TODO.md
├── docs/                       # this whole tree
├── apps/
│   ├── marketing-site/         # Astro 5 + Tailwind, deployed to Cloudflare Pages
│   ├── api/                    # Cloudflare Worker (form intake, dashboard fetch, webhooks)
│   └── ops/                    # internal Astro app (founder/VA dashboard, restricted by Cloudflare Access)
├── packages/
│   ├── ui/                     # shared Astro components (buttons, cards, layouts)
│   ├── content/                # MDX cornerstones + blog + case-study templates
│   ├── telephony/              # CM.com adapter (Twilio fallback hidden behind interface)
│   ├── prompts/                # Synthflow Dutch system prompts (versioned) + RAG snippets
│   ├── db/                     # Drizzle schema + migrations for Neon
│   ├── attio/                  # typed client for Attio API
│   ├── billing/                # Mollie + Moneybird client
│   ├── messaging/              # SMS + email templates (Resend + CM.com SMS)
│   ├── domain/                 # types: Client, Call, Booking, Review, Suppression
│   └── config/                 # shared eslint, tsconfig, prettier, env schema (zod)
├── infra/
│   ├── n8n/                    # workflows-as-JSON (exported via n8n CLI)
│   ├── caddy/                  # Caddyfile
│   ├── docker/                 # docker-compose.yml + per-service Dockerfiles
│   ├── terraform/              # Cloudflare DNS, Hetzner volume, Neon project (optional)
│   └── scripts/                # deploy.sh, backup.sh, restore.sh
├── .github/
│   └── workflows/              # CI: typecheck, lint, build, deploy
├── turbo.json
├── pnpm-workspace.yaml
├── package.json
└── .env.example
```

## `apps/marketing-site`

Astro 5 (current as of 2026-05). Cloudflare Pages adapter. Tailwind 4. MDX content.

Routes:

- `/` — hero, value-prop, demo CTA
- `/loodgieters` — vertical LP with loodgieter-specific copy + audio demo
- `/dakdekkers` — vertical LP
- `/prijzen` — three tiers, FAQ, comparison vs. Cowcierge/Gold Lemon
- `/rekentool` — ROI calculator (3 fields → annual loss + how Klantkraan recovers it)
- `/demo` — embedded audio + the public 085 number
- `/over` — founder bio + KvK + DPA download
- `/blog/[...slug].astro` — MDX from `packages/content/blog/`
- `/case/[slug].astro` — case studies
- `/legal/voorwaarden`, `/legal/dpa`, `/legal/sla`, `/legal/privacy`, `/legal/ai-disclosure`, `/legal/subprocessors`
- `/r/[slug].astro` — per-client dashboard (see `03-delivery/dashboard-spec.md`)
- `/unsubscribe` — handles email + SMS opt-out via signed token

## `apps/api`

Cloudflare Worker, single file with route handlers. Endpoints:

| Route                             | Method   | Purpose                                     |
| --------------------------------- | -------- | ------------------------------------------- |
| `/api/intake-form`                | POST     | Tally webhook → validate → Attio + Neon     |
| `/api/lead`                       | POST     | Site form submissions → Attio               |
| `/api/dashboard/:slug`            | GET      | Dashboard data (cached in KV 5 min)         |
| `/api/webhook/cm/call`            | POST     | CM.com missed-call event → n8n forward      |
| `/api/webhook/cm/sms`             | POST     | Incoming SMS → STOP handler + reply routing |
| `/api/webhook/synthflow/call-end` | POST     | Call summary → Neon `calls` + Attio         |
| `/api/webhook/calcom/booking`     | POST     | Cal.com bookings → Neon + SMS confirmation  |
| `/api/webhook/mollie/payment`     | POST     | Mollie subscription events → Moneybird      |
| `/api/webhook/signwell/signed`    | POST     | Contract signed → trigger onboarding flow   |
| `/api/unsubscribe`                | GET/POST | Signed-token opt-out                        |
| `/api/health`                     | GET      | Health-check (used by Uptime Kuma)          |

## `apps/ops`

Restricted Astro app for founder + VA. Cloudflare Access (Zero Trust) for auth. Routes:

- `/ops` — overview: active clients, today's calls, today's bookings
- `/ops/clients` — list + drill-down
- `/ops/calls` — call review queue (founder QAs transcripts)
- `/ops/onboarding/[client]` — onboarding stepper for VA
- `/ops/sops` — internal SOP wiki (MDX from `packages/content/sops/`)

## `packages/telephony`

Adapter pattern. One interface, two implementations.

```ts
export interface TelephonyAdapter {
  provisionNumber(opts: { country: 'NL' | 'UK'; type: 'local' }): Promise<{ e164: string }>
  sendSms(opts: {
    to: string
    from: string
    body: string
    clientId: string
  }): Promise<{ id: string }>
  configureCallForwarding(opts: { number: string; targetAgentId: string }): Promise<void>
  onCallMissed(handler: (e: MissedCallEvent) => Promise<void>): void
  onSmsInbound(handler: (e: InboundSmsEvent) => Promise<void>): void
}

// implementations:
// packages/telephony/src/cm.ts        (primary)
// packages/telephony/src/twilio.ts    (fallback)
```

Day-to-day code uses the interface; vendor swap is config-change + adapter selection only.

## `packages/db`

Drizzle ORM + Neon Postgres. One schema, multi-tenant via `client_id` on every row. RLS-style guards in code (Drizzle middleware) rather than Postgres RLS — keeps Neon free tier viable.

Migration policy: every schema change in `packages/db/migrations/`, applied via `drizzle-kit push` in CI on `main` only after manual approval.

## `packages/prompts`

Synthflow system prompts versioned per language + vertical:

- `nl/loodgieter.v1.md` — base
- `nl/dakdekker.v1.md`
- `nl/loodgieter-faq.{client}.md` — per-client FAQ overlay (generated by n8n from intake)

Prompt hash (SHA-256) stored alongside every call recording for compliance audit (`04-legal/ai-act-disclosure.md`).

## `infra/n8n`

Workflows are exported as JSON via `n8n export:workflow --backup --output=./infra/n8n/` after every change. CI rejects PRs touching workflows without a corresponding `.json` file change. Diffable, reviewable, restorable.

Core workflows:

- `client-onboarding.json` — orchestrates day-by-day onboarding
- `missed-call-back.json` — CM.com webhook → suppression check → SMS via CM.com
- `review-request.json` — job-done trigger → SMS T+2h → email T+7
- `call-summary-router.json` — Synthflow webhook → Neon + Attio + escalation SMS
- `daily-stats-sms.json` — cron → Postgres aggregate → CM.com SMS
- `weekly-stats-email.json` — cron Monday 08:00 → screenshot dashboard → Resend
- `contract-signed.json` — SignWell webhook → trigger onboarding
- `mrr-snapshot.json` — daily MRR + churn snapshot to Notion

## `packages/config`

- Shared TypeScript config (strict + paths)
- Shared ESLint config (security plugin)
- Zod env schema (parsed at app boot — fail-fast on missing vars)
- Prettier config

## Branch + commit policy

- One branch per feature/fix.
- PR-required for changes to `main`.
- Conventional commits (`feat:`, `fix:`, `chore:`, `docs:`).
- Squash-merge to keep `main` linear.
- Tag releases at meaningful milestones (`v0.1-pilot`, `v1.0-launch`).

## CI workflow (`.github/workflows/ci.yml`)

Jobs (parallel where possible):

1. `lint` — eslint + prettier-check
2. `typecheck` — tsc --noEmit across the workspace
3. `test` — vitest (when tests exist)
4. `build:marketing` — astro build
5. `build:api` — wrangler build (Cloudflare Worker)
6. `n8n-snapshot-check` — fails if n8n workflow JSON drift exists
7. `deploy:marketing` (main only) — wrangler pages deploy
8. `deploy:api` (main only) — wrangler deploy

## Source

- pnpm workspaces: https://pnpm.io/workspaces
- Turborepo: https://turbo.build/repo/docs
- Drizzle + Neon: https://orm.drizzle.team/learn/tutorials/drizzle-with-neon
- n8n CLI export: https://docs.n8n.io/hosting/cli-commands/
- Cloudflare Workers + Pages: https://developers.cloudflare.com/
