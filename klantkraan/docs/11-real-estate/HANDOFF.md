# Real Estate MVP — session handoff

> Rewrite this file at every ⏸ CHECKPOINT in `TASKS.md`, then commit.
> A fresh session starts here: read this, then `TASKS.md`, then `00-PLAN.md`.

## State (2026-08-09)

- Plan committed (`00-PLAN.md`, a65376f). Ledger created (`TASKS.md`).
- Build not started — next task: **0.1 lead schema v1**.
- Existing assets: `ai-receptionist/app/listings_store.py` (sim|resales seam),
  Solvista demo live at `demo.klantkraan.nl/?client=solvista-demo`, config in
  `ai-receptionist/config/listings/solvista-demo.json`, selftest
  `python -m app.selftest listings`.

## Decisions in force

- ElevenLabs for voice (LiveKit later), Costa del Sol market, full MVP before
  outreach, no live voice transfer, propose-only after-hours booking,
  art. 50 disclosure non-negotiable.

## Open / blocked

- Resales provider untested (needs a real agency key — founder item).
- ElevenLabs headroom for a second agent (founder item, blocks Phase 2).

## Gotchas for the next session

- Vertical = config pack on the shared engine, NOT a fork.
- Config tracked via gitignore exception (fictional client, like fitness).
- Run python via `./.venv/bin/python` in ai-receptionist.
- Growth/receptionist deploys: see ops/hetzner/deploy.sh; site deploys are
  manual wrangler with `--branch=production`.
