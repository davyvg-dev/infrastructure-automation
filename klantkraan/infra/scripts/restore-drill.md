# Restore drill — monthly tabletop

> Cadence: first Monday of each month, 30-minute slot on the founder's calendar.
> Target time-to-restore (TTR) SLA: **< 2 hours** from "go" to verified-green production replacement.
> Outcome: tick the month off in the log table below, file any deviations as issues.

## Scope

What we prove every month:

1. The latest Borg archive can be listed, extracted, and decrypted with the passphrase in Bitwarden.
2. A `pg_dump` from the archive restores cleanly into a Neon `dev` branch.
3. The n8n volume tarball restores into a fresh Docker compose stack that starts, authenticates, and reads/writes against the restored Neon `dev` branch.
4. The Caddyfile + DNS swap path is documented and unambiguous.

Do **not** touch production during the drill. The drill runs against a throwaway sandbox VM (Hetzner CX22 ad-hoc, destroyed at the end) and a Neon `dev` branch.

## Pre-flight

1. Provision a sandbox host: `hcloud server create --name kk-restore-drill --type cx22 --image ubuntu-24.04 --location fsn1 --ssh-key kk-ops`. Note its public IP.
2. Pull secrets from Bitwarden vault `klantkraan-infra` into a local `.env.drill`: `BORG_REPO`, `BORG_PASSPHRASE`, `BORG_RSH` key, and the Neon connection string for a fresh `dev` branch (create one via `neonctl branches create --name drill-$(date +%Y%m)`).
3. Confirm wall-clock start time. Start a stopwatch.

## Steps

1. **List archives.** `borg list "${BORG_REPO}"`. Confirm there is an archive named `kk-<ts>` from within the last 24 hours. Record archive name.
2. **Extract to sandbox.** On the sandbox VM, `mkdir -p /mnt/data/restore && cd /mnt/data/restore && borg extract --progress "${BORG_REPO}::<archive>"`. Time this step.
3. **Verify checksums.** `gzip -t db-*.sql.gz && tar -tzf n8n-*.tar.gz >/dev/null`. Any failure aborts the drill.
4. **Restore Postgres dump.** `gunzip -c db-*.sql.gz | psql "${NEON_DEV_URL}"`. Watch for errors; non-zero exit aborts.
5. **Spot-check Postgres data.** Run a smoke query: `psql "${NEON_DEV_URL}" -c "select count(*) from execution_entity;"` (or equivalent n8n table). Compare against the production count (within tolerance — production keeps writing).
6. **Restore n8n volume.** `mkdir -p /mnt/data/n8n && tar -xzf n8n-*.tar.gz -C /mnt/data/`. Verify `/mnt/data/n8n/config` exists.
7. **Bring up sandbox stack.** Copy `infra/docker/docker-compose.yml`, `infra/docker/.env` (drill copy with Neon `dev` URL) and `infra/caddy/Caddyfile` to `/mnt/data/`. Run `docker compose --env-file .env up -d`.
8. **Wait for healthy.** `docker compose ps` — caddy + n8n + uptime-kuma all `healthy` within 3 min. Record the time-to-healthy.
9. **Authenticate to n8n.** Browse `http://<sandbox-ip>:5678` (skip Caddy on drill; basic-auth credentials from `.env`). Confirm previously stored workflows are listed and credentials decrypt (the `N8N_ENCRYPTION_KEY` from prod must match — verify it does).
10. **Execute a read-only workflow.** Pick a daily cron workflow, trigger manually, confirm it completes green and writes the expected row into the Neon `dev` branch.
11. **Document time-to-restore.** Stop the stopwatch. Log total elapsed time and any step that exceeded its budget.
12. **Tear down.** `hcloud server delete kk-restore-drill`. `neonctl branches delete drill-$(date +%Y%m)`. Shred `.env.drill`.
13. **Update the log table below.** If TTR exceeded 2 h, open an issue tagged `incident-prep` with the slowest step and a remediation proposal.

## Drill log

| Month | Date | TTR | Slowest step | Notes |
|---|---|---|---|---|
| YYYY-MM |  |  |  |  |

## What this drill does NOT cover (separate procedures)

- DNS cutover from `n8n.klantkraan.nl` to the restored host — requires a Cloudflare DNS edit; documented in `klantkraan/docs/08-tech/infra-setup.md` and rehearsed quarterly.
- Marketing site rollback — Cloudflare Pages keeps last 20 deployments; one-click rollback in the dashboard.
- Cloudflare Worker rollback — `wrangler rollback`; covered in the API runbook.
- Sentry data — not backed up, retained 90 d in Sentry SaaS.

## Failure mode lookup

| Symptom | First check |
|---|---|
| `borg list` hangs | `BORG_RSH` SSH key — is the agent loaded? Borgbase IP allowlist still includes this host? |
| Postgres restore errors on extensions | Neon `dev` branch missing extensions — install `pgcrypto`, `uuid-ossp` before re-running step 4 |
| n8n container restart-loops on boot | `N8N_ENCRYPTION_KEY` mismatch — credentials can't be decrypted. Confirm Bitwarden value matches. |
| Healthchecks not green after restore | Sandbox cron not configured — expected during drill; ignore |
