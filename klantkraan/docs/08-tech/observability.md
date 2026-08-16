# Observability

> Three layers: errors (Sentry), uptime (Healthchecks + Uptime Kuma), business KPIs (Postgres → Notion + weekly review). No Datadog, no premium-cost trap.

## Layer 1 — Errors (Sentry)

| What                         | Where                                      | SDK                       |
| ---------------------------- | ------------------------------------------ | ------------------------- |
| Marketing site client errors | Astro pages + Cloudflare Pages             | `@sentry/astro`           |
| API Worker errors            | Cloudflare Worker                          | `@sentry/cloudflare`      |
| n8n workflow errors          | n8n built-in Error workflow                | Webhook → Sentry HTTP API |
| Postgres slow queries        | Neon dashboard + Drizzle slow-query logger | manual instrumentation    |

Alert rules:

- Any `error` level in `apps/api` → Slack #alerts + WhatsApp to founder
- Any `warning` rate > 10/min → Slack only
- Workflow error in n8n with severity HIGH → WhatsApp escalation
- Quotas: free tier 5k events/mo; upgrade to Team €26/mo when consistently breached

## Layer 2 — Uptime

### Push-style — Healthchecks.io

Every n8n cron writes a heartbeat to a unique Healthchecks URL on success:

```
HEAD https://hc-ping.com/<uuid>
```

If the heartbeat is missed (cron expected every 15 min didn't fire for 30 min), Healthchecks alerts via WhatsApp.

Covers:

- `daily-stats-sms` (every weekday 18:00)
- `weekly-stats-email` (Mondays 08:00)
- `mrr-snapshot` (every day 23:55)
- `borg-backup` (every day 03:00)
- `suppression-sync` (every 6h)

### Pull-style — Uptime Kuma (self-hosted)

Runs on the same Hetzner CX22 at `status.klantkraan.nl`. Checks:

| Monitor                        | Method                        | Interval | Alert                    |
| ------------------------------ | ----------------------------- | -------- | ------------------------ |
| `klantkraan.nl/`               | HTTP 200                      | 60s      | After 2 fails → WhatsApp |
| `api.klantkraan.nl/api/health` | HTTP 200                      | 60s      | After 2 fails → WhatsApp |
| `n8n.klantkraan.nl/healthz`    | HTTP 200                      | 60s      | After 3 fails → WhatsApp |
| `status.klantkraan.nl/`        | HTTP 200                      | 5 min    | Slack only (self-ref)    |
| DNS check `klantkraan.nl`      | DNS                           | 5 min    | After 1 fail → WhatsApp  |
| Synthflow API status           | HTTP via Synthflow status URL | 5 min    | After 2 fails → Slack    |
| CM.com API status              | HTTP via CM.com status URL    | 5 min    | After 2 fails → Slack    |
| Neon Postgres TCP              | TCP 5432                      | 5 min    | After 2 fails → WhatsApp |

Public status page at `status.klantkraan.nl` — referenced from the SLA (`04-legal/sla-annex.md`). Evidence-of-uptime for service-credit disputes.

### Why two layers

- Pull-only would miss "service responds 200 but business workflows are broken"
- Push-only would miss "n8n process crashed entirely and no cron fires"
- Two layers catch both failure modes

## Layer 3 — Business KPIs

Most important for the founder. Postgres views generated nightly by n8n cron, posted to Notion as a structured page.

### Daily snapshot (Notion page generated every day 23:55)

```
KPI                       Today    7-day avg    Last week
-------------------------+--------+------------+------------
New leads (form)              7        5.4          4.2
Cold emails sent            225      221         219
Cold email replies            16       14.1        12.8
Positive replies               3        2.7         2.4
Demos booked                   2        1.8         1.6
Demos shown                    2        1.5         1.4
Demos won                      1        0.6         0.5
Active clients               18       18.0        17.4
MRR (€)                    8,640    8,500       8,200
Calls handled by AI           42       38.6        35.2
Missed-call recoveries        14       12.3        11.0
Review requests sent          22       20.5        19.0
Reviews received               7        6.3         5.8
S1 incidents                   0        0          0
```

### Weekly review (Friday 16:00)

See `10-ops/weekly-kpi-review.md`. The Notion page is the agenda.

### What we DON'T track (yet)

| Thing                               | Why defer                                                                                            |
| ----------------------------------- | ---------------------------------------------------------------------------------------------------- |
| Full-funnel attribution per channel | Heuristic attribution in Attio is enough at <100 clients; switch to Dreamdata or similar at €20k MRR |
| Cohort retention plots              | At <60 clients, every churn is a one-on-one conversation                                             |
| LTV calculation per cohort          | Aggregate LTV is fine until M9                                                                       |
| Custom Datadog dashboards           | Overkill at this scale                                                                               |
| OpenTelemetry traces                | Sentry + Cloudflare Workers traces cover us                                                          |

## Audit log (compliance evidence)

Separate from observability but related. Postgres `audit_log` table:

```sql
CREATE TABLE audit_log (
  id          UUID PRIMARY KEY,
  ts          TIMESTAMPTZ DEFAULT now(),
  actor       TEXT,          -- 'founder' | 'va:<name>' | 'system' | 'api'
  action      TEXT,          -- 'client.created' | 'prompt.updated' | 'sms.sent' | ...
  entity_type TEXT,
  entity_id   UUID,
  metadata    JSONB,
  ip          INET
);
```

Written by:

- `apps/api` middleware (every write endpoint)
- n8n via Postgres node (every workflow that mutates client data)
- `apps/ops` (every founder/VA action)

Retention: 24 months. Evidence for AP audits, AI Act disclosure proof, DPA audit rights.

## Log shipping

Cloudflare Workers logs → Logpush to R2 (free, EU-only). Searchable via SQL queries on the R2 bucket.

n8n logs → on-VPS file rotation (logrotate, 14 days). Critical events also written to `audit_log`.

## When to add what

| Trigger                           | Add                                                                                     |
| --------------------------------- | --------------------------------------------------------------------------------------- |
| First S1 incident postmortem      | Document in `infra/postmortems/` + add a Sentry alert that would have caught it earlier |
| First data-subject access request | Build a `/ops/dsr/<email>` page that pulls all data for that subject                    |
| First sub-processor change        | Add automated diff notification to all active clients (30-day notice)                   |
| First disputed bill               | Add per-client usage drill-down in `apps/ops`                                           |
| First serious AP question         | Add SOAR / formal incident response playbook                                            |

## Cost

| Item                      | Monthly                  |
| ------------------------- | ------------------------ |
| Sentry free tier          | €0                       |
| Healthchecks free tier    | €0                       |
| Uptime Kuma (self-hosted) | €0                       |
| Cloudflare Logpush to R2  | €0 (free for our volume) |
| Notion free tier          | €0                       |
| **Total**                 | **€0**                   |

Scaling: Sentry Team €26/mo at >5k events/mo; everything else stays free until ~80 active clients.

## Source

- Sentry SaaS pricing: https://sentry.io/pricing/
- Healthchecks.io: https://healthchecks.io/pricing/
- Uptime Kuma: https://github.com/louislam/uptime-kuma
- Cloudflare Logpush: https://developers.cloudflare.com/logs/logpush/
- Atlassian SLA vs SLO vs SLI: https://www.atlassian.com/incident-management/kpis/sla-vs-slo-vs-sli
