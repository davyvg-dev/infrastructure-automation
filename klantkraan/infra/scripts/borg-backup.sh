#!/usr/bin/env bash
# borg-backup.sh — nightly backup. Invoked from host cron (or borgmatic container).
# Per infra-setup.md Step 11:
#   1. pg_dump Neon main -> /mnt/data/backups/db-<ts>.sql.gz
#   2. Tar /mnt/data/n8n -> /mnt/data/backups/n8n-<ts>.tar.gz
#   3. Borg create + push to Borgbase EU repo
#   4. Prune: 7 daily / 4 weekly / 12 monthly
#   5. Ping Healthchecks on success
#
# Required env (loaded from /mnt/data/docker/.env):
#   PG_HOST, PG_DB, PG_USER, PG_PASS
#   BORG_REPO, BORG_PASSPHRASE, BORG_RSH
#   HC_BORG_BACKUP_URL

set -euo pipefail

ENV_FILE="${ENV_FILE:-/mnt/data/docker/.env}"
BACKUP_DIR="${BACKUP_DIR:-/mnt/data/backups}"
N8N_DIR="${N8N_DIR:-/mnt/data/n8n}"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
LOCK_FILE="/var/lock/kk-borg-backup.lock"

log() { printf '[borg-backup %s] %s\n' "$(date -Iseconds)" "$*" >&2; }
ping_hc() { [[ -n "${HC_BORG_BACKUP_URL:-}" ]] && curl -fsS --retry 3 --max-time 10 -o /dev/null "${HC_BORG_BACKUP_URL}${1:-}" || true; }

trap 'rc=$?; if (( rc != 0 )); then log "FAILED rc=${rc}"; ping_hc "/fail"; fi' EXIT

# Prevent concurrent runs — non-blocking, fail fast.
exec 9>"${LOCK_FILE}"
flock -n 9 || { log "another backup is running, exiting"; exit 0; }

# shellcheck disable=SC1090
[[ -r "${ENV_FILE}" ]] && set -a && . "${ENV_FILE}" && set +a

: "${PG_HOST:?PG_HOST required}"
: "${PG_DB:?PG_DB required}"
: "${PG_USER:?PG_USER required}"
: "${PG_PASS:?PG_PASS required}"
: "${BORG_REPO:?BORG_REPO required}"
: "${BORG_PASSPHRASE:?BORG_PASSPHRASE required}"

export BORG_REPO BORG_PASSPHRASE
export BORG_RSH="${BORG_RSH:-ssh}"
export PGPASSWORD="${PG_PASS}"

mkdir -p "${BACKUP_DIR}"

log "step 1/5 pg_dump ${PG_DB}@${PG_HOST}"
DB_DUMP="${BACKUP_DIR}/db-${TS}.sql.gz"
pg_dump \
  --host="${PG_HOST}" --port=5432 --username="${PG_USER}" --dbname="${PG_DB}" \
  --no-owner --no-privileges --format=plain \
  | gzip -9 > "${DB_DUMP}.partial"
mv "${DB_DUMP}.partial" "${DB_DUMP}"

log "step 2/5 tar n8n volume"
N8N_TAR="${BACKUP_DIR}/n8n-${TS}.tar.gz"
tar --warning=no-file-changed -czf "${N8N_TAR}.partial" -C "$(dirname "${N8N_DIR}")" "$(basename "${N8N_DIR}")"
mv "${N8N_TAR}.partial" "${N8N_TAR}"

log "step 3/5 borg create"
borg create \
  --stats --compression zstd,6 \
  "::kk-${TS}" \
  "${DB_DUMP}" "${N8N_TAR}"

log "step 4/5 borg prune"
borg prune --list \
  --keep-daily 7 --keep-weekly 4 --keep-monthly 12 \
  --glob-archives 'kk-*'

borg compact

log "step 5/5 housekeeping local copies (keep 3 most recent)"
find "${BACKUP_DIR}" -maxdepth 1 -name 'db-*.sql.gz' -type f -printf '%T@ %p\n' \
  | sort -rn | awk 'NR>3{print $2}' | xargs -r rm -f
find "${BACKUP_DIR}" -maxdepth 1 -name 'n8n-*.tar.gz' -type f -printf '%T@ %p\n' \
  | sort -rn | awk 'NR>3{print $2}' | xargs -r rm -f

log "OK"
ping_hc ""
