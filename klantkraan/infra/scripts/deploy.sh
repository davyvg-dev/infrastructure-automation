#!/usr/bin/env bash
# deploy.sh — push infra/ to the Hetzner host and bring the stack up.
# Usage: KK_HOST=klantkraan@host KK_SSH_KEY=~/.ssh/id_ed25519_klantkraan ./deploy.sh
#
# Expects to be invoked from the repo root or from infra/scripts/. Resolves paths relative to itself.

set -euo pipefail

: "${KK_HOST:?KK_HOST not set (e.g. klantkraan@kk-prod-1.klantkraan.nl)}"
KK_SSH_KEY="${KK_SSH_KEY:-$HOME/.ssh/id_ed25519_klantkraan}"
HC_DEPLOY_URL="${HC_DEPLOY_URL:-}"
HEALTH_TIMEOUT="${HEALTH_TIMEOUT:-180}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

SSH_OPTS=(-i "${KK_SSH_KEY}" -o StrictHostKeyChecking=accept-new -o ServerAliveInterval=30)
RSYNC_OPTS=(-az --delete --omit-dir-times --no-perms --chmod=Du=rwx,Dgo=rx,Fu=rw,Fgo=r
  --exclude '.env' --exclude '*.swp' --exclude '.DS_Store')

log() { printf '[deploy] %s\n' "$*" >&2; }

log "syncing infra/docker -> ${KK_HOST}:/mnt/data/docker"
rsync "${RSYNC_OPTS[@]}" -e "ssh ${SSH_OPTS[*]}" \
  "${INFRA_DIR}/docker/" "${KK_HOST}:/mnt/data/docker/"

log "syncing infra/caddy -> ${KK_HOST}:/mnt/data/caddy"
rsync "${RSYNC_OPTS[@]}" -e "ssh ${SSH_OPTS[*]}" \
  "${INFRA_DIR}/caddy/" "${KK_HOST}:/mnt/data/caddy/"

log "syncing borg-backup.sh -> ${KK_HOST}:/mnt/data/scripts"
rsync -az --chmod=Du=rwx,Dgo=rx,Fu=rwx,Fgo=rx -e "ssh ${SSH_OPTS[*]}" \
  "${INFRA_DIR}/scripts/borg-backup.sh" "${KK_HOST}:/mnt/data/scripts/borg-backup.sh"

log "pulling images + bringing stack up"
# shellcheck disable=SC2029 # remote-side expansion is intended
ssh "${SSH_OPTS[@]}" "${KK_HOST}" "bash -se" <<'REMOTE'
set -euo pipefail
cd /mnt/data/docker
docker compose --env-file .env pull
docker compose --env-file .env up -d --remove-orphans
docker image prune -f >/dev/null
REMOTE

log "waiting up to ${HEALTH_TIMEOUT}s for healthy containers"
deadline=$(( $(date +%s) + HEALTH_TIMEOUT ))
while :; do
  status=$(ssh "${SSH_OPTS[@]}" "${KK_HOST}" "cd /mnt/data/docker && docker compose ps --format '{{.Service}} {{.Health}}'" || true)
  unhealthy=$(printf '%s\n' "${status}" | awk 'NF && $2!="healthy" && $2!=""' || true)
  if [[ -z "${unhealthy}" && -n "${status}" ]]; then
    log "all services healthy"
    break
  fi
  if (( $(date +%s) >= deadline )); then
    log "healthcheck timeout. current status:"
    printf '%s\n' "${status}" >&2
    exit 1
  fi
  sleep 5
done

if [[ -n "${HC_DEPLOY_URL}" ]]; then
  log "pinging Healthchecks"
  curl -fsS --retry 3 --max-time 10 -o /dev/null "${HC_DEPLOY_URL}" || log "WARN: Healthchecks ping failed"
fi

log "deploy complete"
