# Infrastructure Setup

> Provisioning runbook for the Hetzner CX22 + Cloudflare + Neon trio. Goal: from zero to "production-ready n8n + Postgres + Caddy + healthchecks" in < 2 hours.

## Pre-requisites (founder)

- [ ] Hetzner Cloud account + project "klantkraan" + billing valid
- [ ] Cloudflare account + `klantkraan.nl` DNS delegated
- [ ] Neon account + EU project "klantkraan" + branch `main`
- [ ] GitHub repo created + SSH key registered
- [ ] Bitwarden vault "klantkraan-infra" for secrets
- [ ] Personal SSH keypair `~/.ssh/id_ed25519_klantkraan`

## Step 1 — Cloudflare DNS

Create records on `klantkraan.nl`:

| Type | Name | Value | Proxy |
|---|---|---|---|
| A | @ | (Cloudflare Pages auto) | Proxied |
| A | www | (Cloudflare Pages auto) | Proxied |
| A | n8n | <hetzner-public-ip> | DNS-only |
| A | status | <hetzner-public-ip> | DNS-only |
| A | api | (Workers route) | Proxied |
| TXT | @ | `v=spf1 -all` | n/a (no email from main domain) |
| TXT | _dmarc | `v=DMARC1; p=reject; rua=mailto:dmarc@klantkraan.nl` | n/a |
| MX | @ | (Resend inbound or Google Workspace if used) | n/a |

For cold-email secondary domains (`getklantkraan.nl`, `klantenmotor.nl`, `klantkraanpro.nl`), do the SPF/DKIM/DMARC setup per `06-outbound/deliverability-stack.md`.

## Step 2 — Hetzner CX22 provisioning

```bash
# via hcloud CLI
hcloud server create \
  --name kk-prod-1 \
  --type cx22 \
  --image ubuntu-24.04 \
  --location fsn1 \
  --ssh-key kk-ops \
  --label env=prod

hcloud volume create --name kk-data --size 40 --location fsn1
hcloud volume attach kk-data kk-prod-1
```

SSH in, harden:

```bash
ssh root@<ip>
# update + create non-root user
apt update && apt upgrade -y
adduser klantkraan
usermod -aG sudo,docker klantkraan
mkdir -p /home/klantkraan/.ssh
cp ~/.ssh/authorized_keys /home/klantkraan/.ssh/
chown -R klantkraan:klantkraan /home/klantkraan/.ssh
chmod 700 /home/klantkraan/.ssh
chmod 600 /home/klantkraan/.ssh/authorized_keys

# disable root login + password auth
sed -i 's/^#PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/^#PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl restart ssh

# basic firewall
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
fail2ban-client status
```

Mount the data volume:

```bash
mkfs.ext4 /dev/sdb
mkdir /mnt/data
echo '/dev/sdb /mnt/data ext4 defaults 0 2' >> /etc/fstab
mount -a
```

## Step 3 — Docker + Compose

```bash
apt install -y docker.io docker-compose-v2
systemctl enable --now docker
```

Layout on disk:

```
/mnt/data/
├── caddy/
│   ├── Caddyfile
│   └── data/
├── n8n/
│   └── .n8n/             # n8n persistent storage
├── uptime-kuma/
└── backups/
```

## Step 4 — `docker-compose.yml`

```yaml
version: "3.9"

services:
  caddy:
    image: caddy:2-alpine
    restart: unless-stopped
    ports: ["80:80", "443:443"]
    volumes:
      - /mnt/data/caddy/Caddyfile:/etc/caddy/Caddyfile
      - /mnt/data/caddy/data:/data
      - /mnt/data/caddy/config:/config

  n8n:
    image: n8nio/n8n:latest
    restart: unless-stopped
    environment:
      - N8N_HOST=n8n.klantkraan.nl
      - N8N_PROTOCOL=https
      - WEBHOOK_URL=https://n8n.klantkraan.nl/
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_USER}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=${PG_HOST}
      - DB_POSTGRESDB_DATABASE=${PG_DB}
      - DB_POSTGRESDB_USER=${PG_USER}
      - DB_POSTGRESDB_PASSWORD=${PG_PASS}
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_SSL_REJECT_UNAUTHORIZED=false
      - GENERIC_TIMEZONE=Europe/Amsterdam
      - N8N_DIAGNOSTICS_ENABLED=false
      - N8N_VERSION_NOTIFICATIONS_ENABLED=false
    volumes:
      - /mnt/data/n8n:/home/node/.n8n
    depends_on: [caddy]

  uptime-kuma:
    image: louislam/uptime-kuma:latest
    restart: unless-stopped
    volumes:
      - /mnt/data/uptime-kuma:/app/data
```

## Step 5 — Caddyfile

```caddy
n8n.klantkraan.nl {
  reverse_proxy n8n:5678
  encode gzip
}

status.klantkraan.nl {
  reverse_proxy uptime-kuma:3001
  encode gzip
}
```

Caddy auto-provisions Let's Encrypt certs.

## Step 6 — `.env` (Bitwarden-stored, deployed via deploy script)

```
N8N_USER=...
N8N_PASSWORD=...
PG_HOST=ep-xxx.eu-central-1.aws.neon.tech
PG_DB=klantkraan
PG_USER=klantkraan_n8n
PG_PASS=...
```

## Step 7 — Neon Postgres

Create project + branch + roles via Neon console:

```
Project: klantkraan
Region:  EU Central (Frankfurt)
Branches:
  - main  (production)
  - dev   (development, branched off main)
Roles:
  - klantkraan_app   (read/write app data)
  - klantkraan_n8n   (n8n internal storage, separate database)
```

Apply Drizzle migrations:

```bash
pnpm --filter @kk/db migrate
```

## Step 8 — Cloudflare Pages

- Connect GitHub repo `infrastructure-automation` (this repo)
- Project name: `klantkraan-marketing`
- Build command: `pnpm install && pnpm --filter @kk/marketing-site build`
- Output: `apps/marketing-site/dist`
- Env vars: `PUBLIC_API_BASE=https://api.klantkraan.nl`
- Production branch: `main` → goes to `klantkraan.nl`
- Preview branches: every PR gets a preview URL

## Step 9 — Cloudflare Workers (api)

```bash
cd apps/api
pnpm wrangler login
pnpm wrangler deploy
```

Route the Worker to `api.klantkraan.nl/*`.

## Step 10 — Healthchecks + Uptime Kuma

- Healthchecks.io (free) — push-style heartbeats from every n8n cron (`HEAD https://hc-ping.com/<uuid>` at the end of each workflow run)
- Uptime Kuma (self-hosted) — pull-style:
  - `https://klantkraan.nl/` (200 expected)
  - `https://api.klantkraan.nl/api/health` (200)
  - `https://n8n.klantkraan.nl/healthz` (200)
  - `https://status.klantkraan.nl/` (200)
  - DNS check for `klantkraan.nl`
  - Synthflow API health endpoint
  - CM.com API health endpoint

Alerts: WhatsApp via CM.com Business Messaging API → founder's number.

## Step 11 — Backups

Borgbase scheduled daily 03:00 CET:

```bash
# /etc/cron.d/borgbackup
0 3 * * * klantkraan /usr/local/bin/borg-backup.sh
```

`borg-backup.sh`:
1. `pg_dump` Neon `main` branch → `/mnt/data/backups/db-$(date).sql.gz`
2. Tar `/mnt/data/n8n/` → `/mnt/data/backups/n8n-$(date).tar.gz`
3. Borg push to Borgbase EU repo (encrypted, deduplicated)
4. Retention: 7 daily, 4 weekly, 12 monthly
5. Push ping to Healthchecks on success

Restore drill: monthly tabletop. Documented in `infra/scripts/restore-drill.md`.

## Step 12 — First deploy + smoke test

1. Push to `main`.
2. CI runs (lint, typecheck, build, deploy Pages + Workers).
3. Caddy + n8n + Uptime Kuma containers come up.
4. Hit `https://klantkraan.nl/` → 200 OK.
5. Hit `https://api.klantkraan.nl/api/health` → 200 OK.
6. Trigger a test n8n workflow → verify Postgres write + Healthchecks ping.
7. Tick off `infra-setup.md` complete in `TODO.md`.

## Costs at this scale

| Item | Monthly |
|---|---|
| Hetzner CX22 + 40 GB volume | €3.79 + €1.60 |
| Neon Postgres free tier | €0 |
| Cloudflare Pages + Workers + R2 | €0 (free tier) |
| Borgbase 100 GB | €2.20 |
| Healthchecks.io | €0 (free for our checks) |
| **Total infra** | **~€7.60/mo** |

## When this stack outgrows

| Trigger | Upgrade |
|---|---|
| n8n queue depth > 100 sustained | CX22 → CX32 (€7.49/mo, 8 GB / 80 GB) |
| Postgres > 500 MB or > 191k writes/mo | Neon Launch plan (€19/mo) |
| Workers requests > 100k/day | Cloudflare Workers Paid (€5/mo) |
| R2 storage > 10 GB | Add Pro (€5/mo) |
| Need HA / failover | Add second CX22 in Helsinki + Postgres read replica |

## Source

- Hetzner Cloud: https://www.hetzner.com/cloud
- Cloudflare Pages: https://pages.cloudflare.com/
- Cloudflare Workers: https://workers.cloudflare.com/
- Neon: https://neon.tech/docs/introduction
- n8n self-hosted: https://docs.n8n.io/hosting/installation/docker/
- Caddy: https://caddyserver.com/docs/
- Uptime Kuma: https://github.com/louislam/uptime-kuma
- Borgbase: https://www.borgbase.com/
