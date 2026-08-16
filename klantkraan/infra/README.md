# `infra/` — operator guide

> Authoritative spec: [`klantkraan/docs/08-tech/infra-setup.md`](../docs/08-tech/infra-setup.md).
> This file is the day-2 cheatsheet. Read the spec once, keep this page open.

## Layout

| Path                        | Purpose                                                                      |
| --------------------------- | ---------------------------------------------------------------------------- |
| `docker/docker-compose.yml` | Caddy + n8n + Uptime Kuma stack                                              |
| `docker/.env.example`       | Env-var template; real values from Bitwarden                                 |
| `caddy/Caddyfile`           | Reverse proxy + security headers                                             |
| `scripts/deploy.sh`         | rsync + remote `docker compose up -d` + healthcheck wait + Healthchecks ping |
| `scripts/borg-backup.sh`    | Nightly Postgres + n8n-volume backup to Borgbase                             |
| `scripts/restore-drill.md`  | Monthly tabletop restore checklist                                           |
| `n8n/`                      | Workflow JSON exports (managed by `n8n export:workflow`)                     |
| `terraform/`                | Optional IaC for Cloudflare + Hetzner (not in scope for v0.1)                |

## Pre-requisites

1. Hetzner CX22 provisioned per spec Step 2 (Ubuntu 24.04, `klantkraan` user, ufw, fail2ban, `/mnt/data` mounted).
2. SSH key `~/.ssh/id_ed25519_klantkraan` authorised on the host as `klantkraan`.
3. Bitwarden vault `klantkraan-infra` populated; required entries:
   - `n8n basic auth` (user + password)
   - `n8n encryption key` (32-byte hex)
   - `neon klantkraan_n8n` (host, db, user, password)
   - `borgbase repo` (URL + passphrase + SSH key)
   - `healthchecks` (per-cron UUID URLs)
4. `.env` written to the host at `/mnt/data/docker/.env`, `chmod 600`, owned by `klantkraan`. Never committed.
5. Local tools: `rsync`, `ssh`, `docker compose` (only for `compose config` dry-runs), `curl`.

## Deploy

```bash
# from repo root
export KK_HOST=klantkraan@kk-prod-1.klantkraan.nl
export KK_SSH_KEY=~/.ssh/id_ed25519_klantkraan
export HC_DEPLOY_URL=https://hc-ping.com/<deploy-uuid>
./klantkraan/infra/scripts/deploy.sh
```

What the script does, in order:

1. rsyncs `infra/docker/` and `infra/caddy/` to `/mnt/data/`.
2. rsyncs `borg-backup.sh` to `/mnt/data/scripts/`.
3. SSH's in and runs `docker compose pull && docker compose up -d --remove-orphans`.
4. Polls `docker compose ps` until all services report `healthy` (timeout 180 s, override via `HEALTH_TIMEOUT`).
5. Pings `${HC_DEPLOY_URL}` on success.

`.env` itself is never rsynced — it lives on the host only. Edit it in place via `ssh` when secrets rotate.

## Verify after deploy

| Check                 | Command                                                                                             | Expected                        |
| --------------------- | --------------------------------------------------------------------------------------------------- | ------------------------------- |
| Containers up         | `ssh $KK_HOST 'docker compose -f /mnt/data/docker/docker-compose.yml ps'`                           | All `running` + `healthy`       |
| n8n reachable         | `curl -fsS https://n8n.klantkraan.nl/healthz`                                                       | `{"status":"ok"}`               |
| Status page reachable | `curl -fsSI https://status.klantkraan.nl/`                                                          | `200 OK`                        |
| Certs minted          | `ssh $KK_HOST 'ls /mnt/data/caddy/data/caddy/certificates/acme-v02.api.letsencrypt.org-directory/'` | two domain directories          |
| n8n DB connection     | n8n editor → Settings → check no banner about DB connectivity                                       | green                           |
| Smoke workflow        | Trigger `daily-stats-sms` manually in n8n                                                           | Green run + Healthchecks beacon |

## Roll back

n8n is pinned; rolling back is `docker compose pull` of the previous tag.

1. Identify the previous good tag. Last successful deploys are logged in Healthchecks (and Git log of `docker-compose.yml`).
2. Edit `infra/docker/docker-compose.yml` locally — change `image: docker.n8n.io/n8nio/n8n:1.111.0` to the prior tag.
3. Re-run `deploy.sh`.
4. If the rollback is for a DB-schema-incompatible change, **also** restore the latest `db-*.sql.gz` from Borg into the same Neon branch (see `scripts/restore-drill.md` steps 4–5). n8n migrations are forward-only.

Cloudflare Pages (marketing site) and Workers (API) roll back separately via `wrangler rollback` and the Pages dashboard.

## Where secrets live

| Secret                         | Location                                                               |
| ------------------------------ | ---------------------------------------------------------------------- |
| n8n basic-auth, encryption key | Bitwarden vault `klantkraan-infra` → item `n8n`                        |
| Neon Postgres credentials      | Bitwarden → item `neon-klantkraan_n8n`                                 |
| Borgbase repo + passphrase     | Bitwarden → item `borgbase`                                            |
| Healthchecks ping URLs         | Bitwarden → item `healthchecks` (one note, multiple URLs)              |
| Cloudflare API token           | Bitwarden → item `cloudflare-api` (used by `wrangler` and `terraform`) |
| Hetzner API token              | Bitwarden → item `hetzner-api` (used by `hcloud` CLI)                  |
| SSH keys                       | `~/.ssh/`, never in vault; rotate via `ssh-keygen` + Hetzner console   |

`.env` on the production host is the only deployed copy of the n8n + Neon + Borg secrets. Treat the host like a vault: ssh-key-only, no password auth, fail2ban watching.

## Backups

- Schedule: `/etc/cron.d/kk-borg-backup` — `0 3 * * * klantkraan /mnt/data/scripts/borg-backup.sh`
- Retention: 7 daily / 4 weekly / 12 monthly (in `borg-backup.sh`)
- Monitor: Healthchecks UUID `$HC_BORG_BACKUP_URL`; alerts to founder WhatsApp if missed.
- Drill: monthly per [`scripts/restore-drill.md`](./scripts/restore-drill.md).

## Updating n8n

1. Pick the target tag from <https://hub.docker.com/r/n8nio/n8n/tags> — pin to a specific release, never `:latest`.
2. Read the n8n release notes for breaking changes (especially around runners and `N8N_ENCRYPTION_KEY` handling).
3. Take a manual backup: `ssh $KK_HOST /mnt/data/scripts/borg-backup.sh`.
4. Edit `image:` in `docker-compose.yml`. Commit with the ctx7-fetched changelog summary in the message.
5. Run `deploy.sh`. Verify the post-deploy checks above.
6. If anything regresses, follow **Roll back**.

## Adding a new service

1. Append the service block in `docker-compose.yml` (place it on the `kk-prod` network; add resource limits within the CX22 budget — see `docs/08-tech/infra-setup.md`).
2. Add a vhost block in `caddy/Caddyfile` using `import security_headers`.
3. Add a Cloudflare DNS A record pointing the subdomain at the Hetzner public IP, DNS-only (not proxied) so Caddy can mint the cert.
4. `deploy.sh`. Confirm `caddy` reloads cleanly (it does so via the compose restart).
5. Add a corresponding Uptime Kuma monitor.

## Why some things look the way they do

- `DB_POSTGRESDB_SSL_REJECT_UNAUTHORIZED=false`: Neon's TLS chain isn't always in n8n's distroless trust bundle. The connection is still TLS-encrypted; only chain verification is relaxed. See spec § Step 4 for the trade-off.
- `version:` key missing from compose: Compose v2 ignores it; keeping the schema lean.
- Caddy and Uptime Kuma run on the same host as n8n — single-VM design, see `docs/08-tech/infra-setup.md § Costs at this scale`. When we outgrow CX22, the status page moves to its own host.
- Borgmatic block commented out: host-cron is the simpler default on a one-VM stack. Switch to the in-container path only if the host is doing something exotic with cron.
