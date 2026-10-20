#!/usr/bin/env bash
# Claude Code Stop-hook verification dispatcher — "catch, don't prevent".
# Runs the repo's deterministic gates against changed files when a session
# ends its turn. Failures exit 2 with findings on stderr so Claude
# self-corrects. Fast (<5s), no network, fail-open on script bugs.
#
# Hook schema verified against code.claude.com/docs/en/hooks via context7
# (/llmstxt/code_claude_llms_txt, fetched 2026-08-10):
#   - stdin JSON carries stop_hook_active; exit 0 when true to avoid loops
#   - exit 2 + stderr = feedback fed back to Claude; exit 0 = allow stop

# ---- fail-open guard: a broken hook must never wedge sessions ------------
# Any exit that we did not deliberately request is converted to 0.
DELIBERATE_EXIT=0
trap '_c=$?; if [ "$_c" -ne 0 ] && [ "$DELIBERATE_EXIT" != "1" ]; then exit 0; fi' EXIT

die_block() { # concise findings on stderr, then the deliberate exit 2
  printf '%s\n' "$1" >&2
  DELIBERATE_EXIT=1
  exit 2
}

ok_exit() {
  DELIBERATE_EXIT=1
  exit 0
}

# ---- read hook JSON from stdin; bail out of stop-hook loops --------------
INPUT=$(cat 2>/dev/null || true)
if command -v jq >/dev/null 2>&1; then
  [ "$(printf '%s' "$INPUT" | jq -r '.stop_hook_active // false' 2>/dev/null)" = "true" ] && ok_exit
else
  printf '%s' "$INPUT" | grep -q '"stop_hook_active"[[:space:]]*:[[:space:]]*true' && ok_exit
fi

# ---- repo root -----------------------------------------------------------
ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null)}"
[ -n "$ROOT" ] && [ -d "$ROOT" ] || ok_exit
cd "$ROOT" || ok_exit
git rev-parse --git-dir >/dev/null 2>&1 || ok_exit

# ---- changed files: unstaged + staged + untracked, deduped ---------------
CHANGED=$(
  {
    git diff --name-only HEAD 2>/dev/null
    git diff --name-only --cached 2>/dev/null
    git ls-files --others --exclude-standard 2>/dev/null
  } | sort -u
)
[ -n "$CHANGED" ] || ok_exit

# ---- route ---------------------------------------------------------------
copy_files=()
prompt_files=()
recep_py=()
growth_py=()

while IFS= read -r f; do
  [ -n "$f" ] || continue
  [ -e "$f" ] || continue # deleted files: nothing to lint
  case "$f" in
    # (a) customer-facing text -> copy-lint
    klantkraan/docs/02-sales/*)
      copy_files+=("$f") ;;
    growth-engine/data/*|growth-engine/src/prompts.py)
      copy_files+=("$f") ;;
    klantkraan/apps/marketing-site/src/*)
      case "$f" in
        *.astro|*.md|*.mdx|*.txt|*.html|*.json) copy_files+=("$f") ;;
      esac ;;
  esac
  case "$f" in
    # (b) receptionist prompt/config surfaces -> eval reminder
    ai-receptionist/app/*prompt*|ai-receptionist/app/receptionist.py|ai-receptionist/config/*.yaml|ai-receptionist/config/*/*.yaml)
      prompt_files+=("$f") ;;
  esac
  case "$f" in
    # (c) python -> per-app pinned ruff
    ai-receptionist/*.py) recep_py+=("$f") ;;
    growth-engine/*.py)   growth_py+=("$f") ;;
  esac
done <<< "$CHANGED"

FINDINGS=""
append_finding() { FINDINGS="${FINDINGS:+$FINDINGS
}$1"; }

# (a) copy lint — only if the gate script exists (built in parallel)
if [ ${#copy_files[@]} -gt 0 ] && [ -x "scripts/copy-lint.sh" ]; then
  out=$(scripts/copy-lint.sh "${copy_files[@]}" 2>&1)
  rc=$?
  if [ $rc -ne 0 ]; then
    append_finding "copy-lint failed on customer-facing text:
$out"
  fi
elif [ ${#copy_files[@]} -gt 0 ] && [ -f "scripts/copy-lint.sh" ]; then
  out=$(bash scripts/copy-lint.sh "${copy_files[@]}" 2>&1)
  rc=$?
  if [ $rc -ne 0 ]; then
    append_finding "copy-lint failed on customer-facing text:
$out"
  fi
fi

# (c) ruff on just the changed .py files, using each app's pinned ruff
run_ruff() { # $1 = app dir, remaining = files (repo-root relative)
  local app="$1"; shift
  local ruff="$app/.venv/bin/ruff"
  [ -x "$ruff" ] || return 0 # no venv -> skip silently (fail-open)
  local out rc
  out=$("$ruff" check --no-cache "$@" 2>&1)
  rc=$?
  if [ $rc -ne 0 ]; then
    append_finding "ruff check ($app) failed:
$out"
  fi
}
[ ${#recep_py[@]} -gt 0 ] && run_ruff "ai-receptionist" "${recep_py[@]}"
[ ${#growth_py[@]} -gt 0 ] && run_ruff "growth-engine" "${growth_py[@]}"

# ---- verdict -------------------------------------------------------------
if [ -n "$FINDINGS" ]; then
  # fold the eval reminder into the blocking feedback when we block anyway
  if [ ${#prompt_files[@]} -gt 0 ]; then
    append_finding "REMINDER: prompt/config surfaces changed (${prompt_files[*]}) — run 'app/evals.py run all' in ai-receptionist before deploy."
  fi
  die_block "Stop-hook gates failed — fix before finishing:
$FINDINGS"
fi

# (b) reminder only: cannot verify whether evals ran, so warn without blocking
if [ ${#prompt_files[@]} -gt 0 ]; then
  echo "REMINDER: prompt/config surfaces changed (${prompt_files[*]}) — run 'app/evals.py run all' in ai-receptionist before deploy." >&2
fi

ok_exit
