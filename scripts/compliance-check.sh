#!/usr/bin/env bash
# compliance-check.sh -- deterministic compliance gate. Exit 1 on any violation.
#
# Check 1: every tracked receptionist business config (ai-receptionist/config/**/*.yaml
#          that defines a business/agent, i.e. has a top-level `business:` or `greeting:`
#          key) must carry the EU AI Act art. 50 disclosure. Convention in this repo:
#          the "EU AI Act art. 50" marker comment plus a "digital assistant"/"digitale
#          assistent" phrase in the greeting/persona. Disabling it is forbidden (CLAUDE.md).
#
# Check 2: outreach prospect CSVs under klantkraan/docs/02-sales/ may only mark BV-form
#          companies for cold email. Hard rule: no cold email to eenmanszaak/VOF without
#          opt-in. Limitation: the CSV has no explicit "cold-email planned" flag, so we
#          treat a row as cold-emailable when it has a usable e-mail address and an EMPTY
#          verify_before_cold gate; such a row must have rechtsvorm/entity_type "BV".
#          Explicit eenmanszaak/VOF/ZZP rows with an e-mail address are flagged even when
#          gated, because a gate note is not a recorded opt-in.

set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail=0

# ---- Check 1: art. 50 disclosure ------------------------------------------------
while IFS= read -r rel; do
  f="$ROOT/$rel"
  [ -f "$f" ] || continue
  # Business/agent configs only; sourcing.yaml etc. have no business/greeting key.
  grep -qE '^(business|greeting):' "$f" || continue
  if ! grep -qiE 'art\.? ?50' "$f" || ! grep -qiE 'digitale? assist|asistente digital' "$f"; then
    echo "VIOLATION (art. 50): $rel lacks the EU AI Act art. 50 disclosure (marker comment + digital-assistant phrase)"
    fail=1
  fi
done < <(git -C "$ROOT" ls-files -- 'ai-receptionist/config' | grep -E '\.ya?ml$')

# ---- Check 2: BV-only cold-email lists ------------------------------------------
while IFS= read -r csv; do
  out=$(python3 - "$csv" <<'PY'
import csv, sys

path = sys.argv[1]
bad = 0
with open(path, newline="", encoding="utf-8") as fh:
    reader = csv.DictReader(fh)
    cols = [c.strip().lower() for c in reader.fieldnames or []]
    def col(*names):
        for n in names:
            if n in cols:
                return (reader.fieldnames or [])[cols.index(n)]
        return None
    form_col = col("rechtsvorm", "entity_type", "legal_form")
    email_col = col("email", "e-mail")
    gate_col = col("verify_before_cold")
    if form_col is None:
        # No rechtsvorm column at all: cannot prove BV, so the whole list is suspect.
        print(f"VIOLATION (BV-only): {path}: no rechtsvorm/entity_type column; cannot verify BV-only rule")
        sys.exit(1)
    for i, row in enumerate(reader, start=2):
        form = (row.get(form_col) or "").strip().lower().replace(".", "")
        email = (row.get(email_col) or "").strip() if email_col else ""
        gate = (row.get(gate_col) or "").strip() if gate_col else ""
        usable_email = "@" in email
        if form in ("eenmanszaak", "vof", "zzp") and usable_email:
            print(f"VIOLATION (BV-only): {path}:{i}: {row.get('company_name','?')} is {form} with an e-mail address -- no cold email without opt-in")
            bad = 1
        elif form != "bv" and usable_email and not gate:
            print(f"VIOLATION (BV-only): {path}:{i}: {row.get('company_name','?')} rechtsvorm '{form or 'empty'}' is not confirmed BV and row is not gated (verify_before_cold empty)")
            bad = 1
sys.exit(bad)
PY
  ) || fail=1
  [ -n "$out" ] && printf '%s\n' "$out"
done < <(find "$ROOT/klantkraan/docs/02-sales" -name '*.csv' 2>/dev/null)

if [ "$fail" -eq 0 ]; then
  echo "compliance-check: OK (art. 50 disclosures present; outreach CSVs BV-only for cold email)"
fi
exit "$fail"
