# Stack Decisions

> Every external service has been picked deliberately. Each line below is a small bet — if the bet goes wrong, the swap-out cost is bounded by the architecture (telephony adapter, sub-processor list, environment-driven config).

## Decisions table

| Layer                         | Pick                                                       | Why                                                                                 | Cost (M1)                         | Swap difficulty                                                                        |
| ----------------------------- | ---------------------------------------------------------- | ----------------------------------------------------------------------------------- | --------------------------------- | -------------------------------------------------------------------------------------- |
| **Repo**                      | pnpm + Turborepo monorepo                                  | `apps/marketing-site` + `apps/automation-api` + `packages/*` share types, single CI | €0                                | Low                                                                                    |
| **Marketing site**            | Astro 5 + Tailwind on Cloudflare Pages                     | Edge-rendered, fast, free hosting, NL CDN PoPs                                      | €0                                | Medium (Next migration possible)                                                       |
| **Forms**                     | Astro Actions → Cloudflare Worker → Attio API              | Edge-native, no server                                                              | €0                                | Low                                                                                    |
| **CRM**                       | Attio Free                                                 | Modern API, generous free tier, GDPR-friendly                                       | €0 → €34/mo at 10 clients         | Medium (migration to HubSpot if needed)                                                |
| **CRM dashboard for clients** | Astro page `/r/{slug}` on Cloudflare Pages                 | Public unguessable URL, no auth, mobile-first                                       | €0                                | Low                                                                                    |
| **Automation engine**         | n8n self-hosted on Hetzner CX22                            | €5/mo vs €25 cloud, full control, EU residency                                      | €3.79/mo (Hetzner)                | Medium                                                                                 |
| **VPS**                       | Hetzner CX22 (4 GB / 40 GB / Falkenstein DE)               | Cheapest EU-only Tier 1                                                             | €3.79/mo                          | Low                                                                                    |
| **Reverse proxy**             | Caddy 2                                                    | Auto-HTTPS, simple config                                                           | €0                                | Low                                                                                    |
| **Containers**                | Docker Compose                                             | One file, no Kubernetes overhead                                                    | €0                                | Low until ~50 services                                                                 |
| **Database**                  | Neon Postgres EU (Frankfurt)                               | Branching for ops + migrations, generous free tier                                  | €0 → €19/mo at scale              | Low (managed PG)                                                                       |
| **Object storage**            | Cloudflare R2                                              | Zero egress fees, S3-compatible                                                     | €0 → €0.30/mo per Compleet client | Low                                                                                    |
| **Telephony**                 | CM.com Voice / SMS                                         | NL native, AVG-clean, real Dutch landlines                                          | €0 setup + per-msg/min usage      | **Critical to abstract** via `packages/telephony` adapter — Twilio fallback documented |
| **AI receptionist**           | Synthflow + ElevenLabs Dutch                               | Best Dutch voice quality + tool-use combo as of 2026-05                             | per-min ~€0.12                    | High — but adapter abstracts it                                                        |
| **LLM**                       | Anthropic Claude (Sonnet for drafts, Opus for cornerstone) | Best Dutch quality + safety + caching                                               | usage-based                       | Low (provider swap behind a wrapper)                                                   |
| **eSign**                     | SignWell (priority 1) / PandaDoc (priority 2)              | eIDAS SES is enough for SaaS <€10k/jr                                               | €8 / €19                          | Low                                                                                    |
| **Payments**                  | Mollie                                                     | NL-native iDEAL + SEPA, Moneybird native integration                                | €0 setup, 1.8% + €0.25            | Medium                                                                                 |
| **Invoicing**                 | Moneybird                                                  | NL standard, BTW + reverse-charge + ICP built-in                                    | €12/mo                            | Medium                                                                                 |
| **Email (transactional)**     | Resend                                                     | Best DX, EU region available, React Email templates                                 | $20/mo when needed                | Low                                                                                    |
| **Email (outbound cold)**     | Smartlead + Google Workspace × 9 inboxes                   | See deliverability-stack                                                            | €98 + €36                         | Low (Instantly equivalent)                                                             |
| **LinkedIn outreach**         | HeyReach + Sales Navigator                                 | Multi-seat-ready when SDR added                                                     | €70 + €82                         | Medium                                                                                 |
| **Calendar**                  | Cal.com                                                    | Open-source, integrations galore                                                    | €0 → €12/mo per team seat         | Low                                                                                    |
| **Form intake**               | Tally                                                      | Mobile-fast, logic-jumps, free for our volume                                       | €0                                | Low                                                                                    |
| **Analytics**                 | Plausible                                                  | EU-hosted, AVG-clean, simple                                                        | €9/mo                             | Low                                                                                    |
| **Errors**                    | Sentry                                                     | Industry standard, generous free tier                                               | €0 → €26/mo                       | Low                                                                                    |
| **Uptime**                    | Healthchecks.io + Uptime Kuma self-hosted                  | Two layers (push + pull) for evidence                                               | €0                                | Low                                                                                    |
| **Logging**                   | Sentry + Postgres `events` table                           | Avoid Datadog premium-cost trap                                                     | €0                                | Low                                                                                    |
| **DNS**                       | Cloudflare (free)                                          | Fast, DDoS-protected, EU PoPs                                                       | €0                                | Low                                                                                    |
| **Code hosting**              | GitHub                                                     | Standard                                                                            | €0                                | Low                                                                                    |
| **CI**                        | GitHub Actions                                             | Standard, free for our usage                                                        | €0                                | Low                                                                                    |
| **Project mgmt**              | Linear free                                                | Sole + 1 VA fits free tier                                                          | €0 → €8/seat                      | Low                                                                                    |
| **Knowledge base / SOPs**     | Notion                                                     | Free for our scale                                                                  | €0                                | Low                                                                                    |
| **Secrets**                   | Bitwarden Business + 1Password vault                       | Bitwarden default; 1Password for client-handoff packages                            | €4/mo                             | Low                                                                                    |
| **Backups**                   | Borgbase (encrypted, EU)                                   | €2/mo for 100 GB plenty                                                             | €2/mo                             | Low                                                                                    |

## Anti-patterns (decisions taken NOT to take)

| Tempting choice       | Why we said no                                                                                                                                                |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Next.js + Vercel      | Vercel SSR pricing climbs, Astro is faster for content sites, Cloudflare Pages is cheaper. Revisit if we need React Server Components at heavy interactivity. |
| Supabase              | More functionality than we need; Neon's branching wins; Cloudflare Workers handle auth gaps.                                                                  |
| AWS / GCP for hosting | Egress + complexity. Hetzner + Cloudflare gives us 95% of what we need at 5% of the price.                                                                    |
| Twilio direct         | NL deliverability worse than CM.com; no native Dutch landlines on demand. Twilio stays as the fallback adapter.                                               |
| HubSpot CRM           | Free tier is honey-trap; paid tier is $50+/seat. Attio is cleaner.                                                                                            |
| Salesforce            | Comically overscoped for a 60-client business.                                                                                                                |
| Zapier                | n8n self-hosted is 10x cheaper at our volume.                                                                                                                 |
| Datadog               | $30+/host/mo. Sentry + Healthchecks + Uptime Kuma cover it.                                                                                                   |

## EU residency story (for sales + legal)

A pillar of the Klantkraan positioning. Concrete proof points:

| Service       | Data location                                                        |
| ------------- | -------------------------------------------------------------------- |
| Hetzner       | Falkenstein DE / Helsinki FI                                         |
| Neon Postgres | EU (Frankfurt)                                                       |
| Cloudflare    | Global, but data pinned to EU PoPs with Workers + R2 EU jurisdiction |
| Mollie        | NL                                                                   |
| Moneybird     | NL                                                                   |
| Attio         | EU/US (config'd EU)                                                  |
| CM.com        | NL                                                                   |
| Resend        | US (transactional only — caveat documented in DPA)                   |
| Synthflow     | US — config'd EU regions only + SCCs                                 |
| Anthropic     | US — SCCs + supplementary measures                                   |
| ElevenLabs    | US — SCCs                                                            |

All US-located sub-processors documented in `04-legal/dpa-outline.md` Annex III with SCCs.

## When we'll re-evaluate

| Trigger                                  | Re-evaluate                                    |
| ---------------------------------------- | ---------------------------------------------- |
| Synthflow >€0.18/min in Dutch            | Switch to VAPI + ElevenLabs direct via adapter |
| Hetzner outage > 4h                      | Add Hetzner FI hot standby                     |
| Cloudflare Pages bandwidth cost > €50/mo | Investigate (shouldn't happen on free tier)    |
| Attio paid tier > €50/seat               | Revisit HubSpot, Pipedrive                     |
| Synthflow Dutch quality slips            | VAPI + ElevenLabs Eleven v3 direct             |

## Source

- Astro hosting: https://astro.build/
- Cloudflare Pages: https://pages.cloudflare.com/
- Hetzner Cloud pricing: https://www.hetzner.com/cloud
- n8n self-host vs cloud: https://docs.n8n.io/hosting/
- Synthflow pricing: https://synthflow.ai/pricing
- CM.com NL telephony: https://www.cm.com/voice/
- Attio API: https://docs.attio.com/
- Neon Postgres: https://neon.tech/
