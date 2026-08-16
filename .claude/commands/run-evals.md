---
description: Run the ai-receptionist chat goldens and summarize any failures
allowed-tools: Bash(cd "$(git rev-parse --show-toplevel)/ai-receptionist" && ./.venv/bin/python -m app.evals:*)
---

## Eval run (live — LLM customer + judge over the real receptionist)

- Result: !`cd "$(git rev-parse --show-toplevel)/ai-receptionist" && ./.venv/bin/python -m app.evals run all`

## Task

Summarize the run above: scenarios passed/failed, and for each failed criterion quote the judge's verdict and the transcript turns that caused it.

Rules:
- The module MUST run as `-m app.evals` from `ai-receptionist/` (relative imports; `python app/evals.py` breaks).
- Exit 1 means at least one golden failed. If ANY golden fails: do NOT proceed to any deploy (site, API, or demo config). Fix the root cause first, re-run `/run-evals`, and only continue on a clean pass.
- Never "fix" a failure by weakening the criterion; propose a prompt/tool/config fix and re-run.
