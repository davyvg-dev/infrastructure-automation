# n8n Workflows — Operator Guide

Workflows-as-code for Klantkraan. Every n8n flow that runs in production exists here as a JSON file. CI rejects PRs touching `/klantkraan/infra/n8n/**` without a matching JSON change (see `n8n-snapshot-check` job in `.github/workflows/ci.yml`).

## Why JSON-in-Git, not n8n's internal store as source of truth

- Diffable on PRs — reviewer can see exactly which node, parameter, or expression changed.
- Restorable — `n8n import:workflow` rebuilds production from this directory in <60s.
- Auditable — every prompt/template change in `call-summary-router` or onboarding is git-blamed.
- Forks safe — preview/dev n8n instances import the same JSON; no drift.

## How exports are produced

On the n8n host (Hetzner CX22, `kk-prod-1`), after any edit in the n8n UI:

```bash
# inside the n8n container
docker exec -it $(docker ps -qf name=n8n) n8n export:workflow \
  --backup \
  --output=/home/node/.n8n/exports/

# copy out
docker cp $(docker ps -qf name=n8n):/home/node/.n8n/exports/ ./infra/n8n/
```

Then commit the changed JSON files. Convention: **one file per workflow, file name = `meta.name` in kebab-case**. The eight core workflows are:

| File                       | Trigger                                          | Purpose                                            |
| -------------------------- | ------------------------------------------------ | -------------------------------------------------- |
| `missed-call-back.json`    | Webhook `POST /webhook/cm/missed-call`           | CM.com missed-call → suppression check → SMS       |
| `review-request.json`      | Webhook `POST /webhook/job-done`                 | Job done → +2h SMS, +7d email fallback             |
| `call-summary-router.json` | Webhook `POST /webhook/synthflow/call-end`       | Synthflow call end → Neon + Attio + escalation     |
| `client-onboarding.json`   | Webhook `POST /webhook/signwell/signed`          | Day 0/7/14/21/30 onboarding cadence                |
| `daily-stats-sms.json`     | Cron 18:00 CET                                   | Per-client daily-stats SMS (D1–D14 post-go-live)   |
| `weekly-stats-email.json`  | Cron Monday 08:00 CET                            | Per-client weekly email + dashboard screenshot     |
| `contract-signed.json`     | Webhook `POST /webhook/signwell/contract-signed` | SignWell signed → DB + Slack + chain to onboarding |
| `mrr-snapshot.json`        | Cron daily 23:50 CET                             | Mollie active subs → Neon `mrr_snapshots` + Notion |

## Diffable JSON convention

- Pretty-printed (2-space indent). Re-format on commit if n8n exported minified.
- Field order: `name`, `nodes`, `connections`, `settings`, `staticData`, `meta` — matches n8n's public REST OpenAPI shape (see ctx7 `/n8n-io/n8n-docs`).
- `staticData: null` unless a workflow explicitly uses per-execution static state.
- `settings.executionOrder: "v1"` everywhere (v0 is deprecated).
- `settings.timezone: "Europe/Amsterdam"` — overrides container default if drift ever happens.
- Credentials are referenced **by name only**, never by ID, never embedded. ID is the placeholder `"PLACEHOLDER"`. The first import on a fresh n8n instance will prompt to re-bind credentials by name.
- `id` per node uses a stable uuid placeholder — n8n re-issues these on import; this avoids spurious diffs.

## `meta.version`

Bump `meta.version` when **any of**:

- A node's `parameters` shape changes (added/removed field, expression rewrite).
- Suppression-check semantics change (e.g., new opt-out source table).
- An outbound template body changes (SMS or email).
- A credential's **name** is renamed.
- A webhook path changes.

Do not bump for cosmetic re-layouts (`position` only) or for `meta.notes` clarifications.

Versioning is `vN` (`v1`, `v2`, ...). Tag a release in git when **all** workflows are at the same version: `git tag n8n-v2`.

## EU AI Act audit chain (Art. 50, `04-legal/ai-act-disclosure.md`)

Every Synthflow call ends with a webhook to `call-summary-router.json`. That workflow:

1. **Validates `ai_disclosure_played === true`** in the Code node "Parse + Validate AI Act Flag". If false, the workflow **throws** — no DB insert, no Attio push, no escalation. The error surfaces in n8n's executions list and triggers the failure alert.
2. **Logs the prompt hash** (`prompt_hash` SHA-256 of the Synthflow system prompt at call time) into the `calls` table on every row.
3. **Logs model_version + voice_id** alongside.
4. **Includes prompt_hash in the Attio Activity** so the founder/auditor sees it on the contact's timeline.

Operator implication: never delete a `calls` row. Retention is "contract duration + 6 months" per AI Act art. 50(5). The `mrr-snapshot.json` workflow never touches `calls`.

If you find a call without `ai_disclosure_played: true`, **do not** edit the JSON to bypass — the disclosure is non-waivable per MSA. Investigate why Synthflow didn't set the flag (prompt regression? voice agent override?) and fix upstream.

## Importing on a fresh n8n instance

Bootstrap order matters — `contract-signed` chains to `client-onboarding`, so the latter must exist first.

```bash
# from a clean n8n container with Postgres backend already configured
cd /klantkraan/infra/n8n

for f in client-onboarding.json missed-call-back.json review-request.json \
         call-summary-router.json daily-stats-sms.json weekly-stats-email.json \
         contract-signed.json mrr-snapshot.json; do
  docker exec -i $(docker ps -qf name=n8n) n8n import:workflow --input=- < "$f"
done
```

After import:

1. Re-bind credentials. Each workflow references a credential by **name** (e.g., `Neon - klantkraan_app`, `CM.com - producttoken`, `Resend - API Key`, `Attio - API Key`, `Synthflow - API Key`, `Cal.com - API Key`, `Mollie - API Key`, `Notion - Integration Token`). Create these in n8n UI (Settings → Credentials) before activating workflows.
2. Set env vars on the n8n container (already in `infra/docker/docker-compose.yml` template):
   - `HC_PING_MISSED_CALL_BACK` — Healthchecks.io UUID for that workflow
   - `HC_PING_REVIEW_REQUEST`
   - `HC_PING_CALL_SUMMARY_ROUTER`
   - `HC_PING_CLIENT_ONBOARDING`
   - `HC_PING_DAILY_STATS_SMS`
   - `HC_PING_WEEKLY_STATS_EMAIL`
   - `HC_PING_CONTRACT_SIGNED`
   - `HC_PING_MRR_SNAPSHOT`
   - `BROWSERLESS_TOKEN`
   - `SLACK_WEBHOOK_FOUNDER_PATH`
   - `NOTION_MRR_DB_ID`
3. Activate each workflow. Smoke-test by hitting the webhook with a synthetic payload (see per-workflow test fixtures under `infra/n8n/fixtures/` — TODO).
4. Confirm a Healthchecks ping arrives within 60s on each cron / first webhook hit.

## Who can edit which workflows

| Workflow                   | Editor                                            | Reviewer |
| -------------------------- | ------------------------------------------------- | -------- |
| `missed-call-back.json`    | Founder + VA                                      | Founder  |
| `review-request.json`      | Founder + VA                                      | Founder  |
| `call-summary-router.json` | **Founder only** (touches AI Act compliance path) | Founder  |
| `client-onboarding.json`   | Founder + VA                                      | Founder  |
| `daily-stats-sms.json`     | Founder + VA                                      | Founder  |
| `weekly-stats-email.json`  | Founder + VA                                      | Founder  |
| `contract-signed.json`     | **Founder only** (DB writes + Slack secret)       | Founder  |
| `mrr-snapshot.json`        | **Founder only** (finance data)                   | Founder  |

The VA never edits a `Code` node containing AI Act validation logic — that's a deliberate guard against accidental compliance regression.

## Best-effort flags (operator must verify in n8n UI)

A few constructs in this set may require small UI tweaks because n8n's wire-format for `Wait`, `If`, and `respondToWebhook` varies subtly between minor versions:

- **`client-onboarding.json`** — long-running Wait chain. After the first import, open the workflow in the n8n UI and verify each `Wait` node renders with the expected unit (days/hours). If it shows raw seconds, click "Save" to normalise.
- **`review-request.json`** — multi-branch If after the fallback email. Verify both branches converge into `Healthchecks Ping`.
- **`weekly-stats-email.json`** — Browserless screenshot returns binary; the Resend node references `$binary.data` for the attachment. If your Resend credential uses a different attachment-encoding convention, swap to a `Move Binary Data` node before Resend.
- **`mrr-snapshot.json`** — Mollie listing assumes a single page (≤250 subs). At >250 active subs, add a pagination loop with `$next` link.

These are documented inline in each file's `meta.notes`.

## Source

- n8n CLI export/import: https://docs.n8n.io/hosting/cli-commands/
- n8n public REST API v1 workflow schema: https://github.com/n8n-io/n8n-docs/blob/main/n8n-docs/docs/api/v1/openapi.yml
- n8n node types reference: https://docs.n8n.io/integrations/builtin/node-types/
- CM.com Business Messaging API: https://developers.cm.com/messaging/docs
- Synthflow webhooks: https://docs.synthflow.ai/
- Mollie subscriptions: https://docs.mollie.com/reference/v2/subscriptions-api/list-subscriptions
- Notion pages API: https://developers.notion.com/reference/post-page
- Healthchecks.io: https://healthchecks.io/docs/
