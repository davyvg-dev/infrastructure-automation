---
description: Morning status — deal pipeline board + outreach sequence board, summarized
allowed-tools: Bash(cd "$(git rev-parse --show-toplevel)/ai-receptionist" && ./.venv/bin/python -m app.pipeline:*), Bash(cd "$(git rev-parse --show-toplevel)/ai-receptionist" && ./.venv/bin/python -m scripts.sequence:*)
---

## Deal pipeline

!`cd "$(git rev-parse --show-toplevel)/ai-receptionist" && ./.venv/bin/python -m app.pipeline board`

## Outreach sequence (authoritative for touches due)

!`cd "$(git rev-parse --show-toplevel)/ai-receptionist" && ./.venv/bin/python -m scripts.sequence board`

## Task

From the two boards above, give a short morning status:

1. Deals by stage (counts + names), calling out anything that moved or is stuck.
2. Touches due TODAY from the sequence board (respect the 6/day cap noted in the outreach workflow).
3. Replies, bounces, or DSNs needing action. Reminders: halt a bounced prospect with `--bounced`, never `--opt-out` (that flag is the legal consent record); check DSNs after every send batch.
4. One suggested next action, nothing more.

Read-only: do not send mail, advance deals, or log touches from this command.
