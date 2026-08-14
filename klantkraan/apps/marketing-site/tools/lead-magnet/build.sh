#!/usr/bin/env bash
# Render the telefoon-checklist to the committed PDF. Rerun after editing the HTML.
set -euo pipefail
cd "$(dirname "$0")"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT="../../public/downloads/nooit-meer-een-klus-missen.pdf"
mkdir -p "$(dirname "$OUT")"
"$CHROME" --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="$OUT" telefoon-checklist.html
echo "wrote $OUT"
