#!/usr/bin/env bash
# Daily ops briefing: fetch signals -> claude -p summarizes -> post to Telegram.
#
#   ./agent.sh            post the briefing to TELEGRAM_CHAT_ID
#   ./agent.sh --dry-run  print the briefing instead of posting (no creds needed)
#
# Env comes from ~/.klantkraan-briefing.env (see README.md). Strictly read-only:
# the model runs with all tools disabled and the only outbound action is the
# single curl to the Telegram Bot API below.

set -u -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

ENV_FILE="${KLANTKRAAN_BRIEFING_ENV:-$HOME/.klantkraan-briefing.env}"
if [ -f "$ENV_FILE" ]; then
    set -a
    # shellcheck disable=SC1090
    . "$ENV_FILE"
    set +a
fi

DRY_RUN=0
if [ "${1:-}" = "--dry-run" ]; then
    DRY_RUN=1
fi

# Gate: never run for real without a single, explicit chat id.
if [ "$DRY_RUN" -eq 0 ]; then
    if [ -z "${TELEGRAM_CHAT_ID:-}" ]; then
        echo "TELEGRAM_CHAT_ID is niet gezet — weiger te draaien. Test met --dry-run." >&2
        exit 2
    fi
    if [ -z "${TELEGRAM_BOT_TOKEN:-}" ]; then
        echo "TELEGRAM_BOT_TOKEN is niet gezet — weiger te draaien. Test met --dry-run." >&2
        exit 2
    fi
fi

# 1. Collect signals (read-only). A FAILED collector exits nonzero but still
#    emits the dump — we brief anyway and fail loudly at the end.
SIGNALS="$(python3 "$SCRIPT_DIR/fetch_signals.py" 2>&1)"
FETCH_EXIT=$?
if [ -z "$SIGNALS" ]; then
    echo "fetch_signals.py gaf geen output — stop." >&2
    exit 3
fi

# 2. Summarize with headless claude. Flags verified against `claude --help`:
#    -p/--print, --model, --tools "" (disables ALL built-in tools),
#    --append-system-prompt, --no-session-persistence.
BRIEFING="$(printf '%s\n' "$SIGNALS" | claude -p \
    --model sonnet \
    --tools "" \
    --no-session-persistence \
    --append-system-prompt "$(cat "$SCRIPT_DIR/briefing_prompt.md")")"
CLAUDE_EXIT=$?
if [ "$CLAUDE_EXIT" -ne 0 ] || [ -z "$BRIEFING" ]; then
    echo "claude -p faalde (exit $CLAUDE_EXIT) — geen briefing gepost." >&2
    exit 3
fi

if [ "$FETCH_EXIT" -ne 0 ]; then
    BRIEFING="[LET OP: een signaalbron is kapot — zie COLLECTOR STATUS] ${BRIEFING}"
fi

# Telegram sendMessage weigert > 4096 tekens; ruim afkappen.
BRIEFING="${BRIEFING:0:4000}"

# 3. Deliver.
if [ "$DRY_RUN" -eq 1 ]; then
    echo "--- DRY RUN: briefing (niet gepost) ---"
    printf '%s\n' "$BRIEFING"
else
    curl -fsS -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
        --data-urlencode "chat_id=${TELEGRAM_CHAT_ID}" \
        --data-urlencode "text=${BRIEFING}" >/dev/null || {
        echo "Telegram sendMessage faalde." >&2
        exit 4
    }
    echo "briefing gepost naar chat ${TELEGRAM_CHAT_ID}"
fi

# Fail loudly if a signal source was broken, even after a successful post.
exit "$FETCH_EXIT"
