#!/usr/bin/env bash
# Deploy/redeploy the Klantkraan apps to the Hetzner server.
# Usage: ops/hetzner/deploy.sh <server-ip>
# Idempotent: rsyncs the repo (NOT .env files — server .env is the source of truth
# for secrets; edit it on the box), rebuilds venvs only when requirements change,
# (re)installs systemd units + Caddyfile, restarts services.
set -euo pipefail

IP="${1:?usage: deploy.sh <server-ip>}"
HOST="root@$IP"
DEST=/opt/klantkraan
DEMO_HOST="demo-${IP//./-}.sslip.io"
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

echo "==> rsync repo to $HOST:$DEST"
rsync -az --delete \
  --exclude .venv --exclude node_modules --exclude .wrangler \
  --exclude .DS_Store --exclude __pycache__ \
  --exclude '.env' --exclude '.env.*' \
  --exclude growth-engine/data --exclude ai-receptionist/data \
  "$REPO_ROOT"/ "$HOST:$DEST/"

echo "==> build venvs + install units"
ssh "$HOST" DEMO_HOST="$DEMO_HOST" 'bash -s' <<'REMOTE'
set -euo pipefail
# growth-engine reels (src/media.py build_reel) shell out to ffmpeg/ffprobe.
command -v ffmpeg >/dev/null || DEBIAN_FRONTEND=noninteractive apt-get install -y -qq ffmpeg
for app in growth-engine ai-receptionist; do
  cd /opt/klantkraan/$app
  [ -d .venv ] || python3 -m venv .venv
  ./.venv/bin/pip install -q -r requirements.txt
  mkdir -p data
done
chown -R klantkraan:klantkraan /opt/klantkraan

cp /opt/klantkraan/ops/hetzner/growth-engine.service /etc/systemd/system/
# Template for extra verticals (not auto-enabled: each instance needs its own
# .env.<vertical> with its own bot token first — see the unit's header comment).
cp "/opt/klantkraan/ops/hetzner/growth-engine@.service" /etc/systemd/system/
cp /opt/klantkraan/ops/hetzner/ai-receptionist.service /etc/systemd/system/
# Watchdog: liveness self-heal + deep /chat probe -> Telegram alert on transitions.
cp /opt/klantkraan/ops/hetzner/ai-receptionist-watchdog.service /etc/systemd/system/
cp /opt/klantkraan/ops/hetzner/ai-receptionist-watchdog.timer /etc/systemd/system/
# Retention: daily AVG purge of raw transcript text past the window (rollups kept).
cp /opt/klantkraan/ops/hetzner/ai-receptionist-retention.service /etc/systemd/system/
cp /opt/klantkraan/ops/hetzner/ai-receptionist-retention.timer /etc/systemd/system/
sed "s/__DEMO_HOST__/$DEMO_HOST/" /opt/klantkraan/ops/hetzner/Caddyfile.template > /etc/caddy/Caddyfile

systemctl daemon-reload
systemctl enable --now growth-engine ai-receptionist caddy \
  ai-receptionist-watchdog.timer ai-receptionist-retention.timer
systemctl restart growth-engine ai-receptionist
systemctl reload caddy
sleep 3
systemctl --no-pager --quiet is-active growth-engine ai-receptionist caddy \
  && echo "services: all active"
REMOTE

echo "==> health check"
sleep 5
curl -sf "https://$DEMO_HOST/config" >/dev/null && echo "demo up: https://$DEMO_HOST"
