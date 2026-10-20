#!/usr/bin/env bash
# copy-lint.sh -- deterministic lint gate for customer-facing copy.
#
# Usage: scripts/copy-lint.sh <file-or-dir> [...]
# Prints "file:line: rule-name: matched text" per violation; exit 1 on any, 0 clean.
# Per-line opt-out: a line containing "copy-lint-ok" is never flagged.
#
# Rules (CLAUDE.md + founder feedback):
#   dash           em/en-dashes are banned in customer copy (no AI-tells)
#   founder-name   the founder's first name never appears in customer-facing artefacts
#   retired-price  599/999/849/699 are dead price points (current: 299/499/249/685)
#   banned-phrase  "eerste maand gratis" / "gratis maand" (improvised terms, never again)
#   stale-phone    any NL phone number that is not +31 6 44 58 83 21 (business) or
#                  +31 970 0653 0002 (live voice line)
#
# Plain bash 3.2+ and grep only. Here-strings instead of process substitution on
# purpose: nested process substitution SIGABRTs intermittently on macOS bash 3.2.

set -u
[ $# -ge 1 ] || { echo "usage: $0 <file-or-dir> [...]" >&2; exit 2; }

IGNORE_MARK='copy-lint-ok'
GREP_OPTS=(-rnIE --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=dist
           --exclude-dir=.astro --exclude-dir=.venv --exclude-dir=__pycache__
           --exclude=copy-lint.sh)
fail=0

# Print every match of $2 on each "file:line:content" line of $3, tagged $1.
report() { # $1=rule-name  $2=regex  $3=grep -rn output
  local rule="$1" re="$2" hits="$3" line file rest ln txt matches match
  [ -n "$hits" ] || return 0
  while IFS= read -r line; do
    [ -n "$line" ] || continue
    case "$line" in *"$IGNORE_MARK"*) continue ;; esac
    file=${line%%:*}; rest=${line#*:}; ln=${rest%%:*}; txt=${rest#*:}
    matches=$(printf '%s' "$txt" | grep -oE "$re")
    while IFS= read -r match; do
      [ -n "$match" ] || continue
      printf '%s:%s: %s: %s\n' "$file" "$ln" "$rule" "$match"
      fail=1
    done <<< "$matches"
  done <<< "$hits"
}

run_rule() { # $1=rule-name  $2=regex  $3...=paths
  local rule="$1" re="$2" hits; shift 2
  hits=$(grep "${GREP_OPTS[@]}" -e "$re" -- "$@" 2>/dev/null) || true
  report "$rule" "$re" "$hits"
}

run_rule dash '—|–' "$@"
run_rule founder-name '[Dd][Aa][Vv][Yy]' "$@"
# Left guard [^0-9.] keeps "1.999" (thousand separator) out; right guard allows "999,-".
run_rule retired-price '(^|[^0-9.])(599|999|849|699)([^0-9]|$)' "$@"
run_rule banned-phrase '[Ee]erste [Mm]aand [Gg]ratis|[Gg]ratis [Mm]aand' "$@"

# stale-phone: match NL numbers (+31/0031 international, or 0-prefixed 10-digit national),
# normalize to digits, and allow only the two current numbers in any formatting.
# Leading (^|[^0-9]) guard keeps matches from starting inside a longer number (IDs, KvK).
PHONE_RE='(^|[^0-9])((\+31|0031)([ .-]?\(0\))?([ .-]?[0-9]){9,11}|0[1-9]([ .-]?[0-9]){8})'
hits=$(grep "${GREP_OPTS[@]}" -e "$PHONE_RE" -- "$@" 2>/dev/null) || true
[ -n "$hits" ] && while IFS= read -r line; do
  [ -n "$line" ] || continue
  case "$line" in *"$IGNORE_MARK"*) continue ;; esac
  file=${line%%:*}; rest=${line#*:}; ln=${rest%%:*}; txt=${rest#*:}
  matches=$(printf '%s' "$txt" | grep -oE "$PHONE_RE")
  while IFS= read -r match; do
    [ -n "$match" ] || continue
    match=${match#"${match%%[0-9+]*}"}   # trim the guard char from the report
    digits=$(printf '%s' "$match" | tr -cd '0-9')
    digits=${digits#00}                                # 0031... -> 31...
    case "$digits" in 0*) digits="31${digits#0}" ;; esac  # 06... -> 316...
    case "$digits" in
      31644588321|3197006530002) ;;                    # current numbers, any formatting
      *) printf '%s:%s: %s: %s\n' "$file" "$ln" "stale-phone" "$match"; fail=1 ;;
    esac
  done <<< "$matches"
done <<< "$hits"

exit "$fail"
