# Real Estate pilot — session handoff

> Rewrite this file at every ⏸ CHECKPOINT in `TASKS.md`, then commit.
> A fresh session starts here: read this, then `TASKS.md`, then `00-PLAN.md`.

## State (2026-08-10, Checkpoint B — Week 1 build COMPLETE)

All of Phase 0 and Week 1 (1.1–1.5) are done and committed. The build half of
the narrow pilot is finished; what remains is owner conversations (2.1–2.4),
which are founder-led with session support.

- 1.1 Branched qualification lives in `persona.goals` of
  `config/clients/solvista-demo.yaml` (buyer/seller/renter/existing, per-type
  required fields, structured tool fields named explicitly). Verified with
  four live chats.
- 1.2 Temperature leads the agent ping: "[Business] 🔥 HOT buyer lead for
  Maria: …" (`listings_store.py`), asserted in selftest + pytest.
- 1.3 `voice_missed.py` is multi-tenant (routes on the called number via
  `resolve_whatsapp_slug`) and localized nl/en/es via config `locale:`. NB the
  follow-up thread re-activates the tenant explicitly — contextvars don't
  cross threads.
- 1.4 Before/after demo page LIVE: klantkraan.nl/demo/solvista (noindex,
  share by link). 21:04-enquiry-goes-cold timeline vs real transcript + real
  HOT ping, live chat CTA, per-flow try-this list. Source:
  `klantkraan/apps/marketing-site/src/pages/demo/solvista.astro`. Deploy =
  `npm run build` then `pnpm dlx wrangler@4 pages deploy ./dist
  --branch=production --project-name=klantkraan-marketing`.
- 1.5 Chat evals: `ai-receptionist/app/evals.py` — LLM customer simulator +
  LLM judge (claude-opus-5, structured outputs) over the real receptionist.
  `python -m app.evals run all` = 4 scenarios, 14 criteria, all green. Online
  (needs ANTHROPIC_API_KEY); leads land in a temp DATA_DIR. Rerun after any
  Solvista prompt/config change.
- Verification state: 229 pytest green, `app.selftest all` green, ruff clean.

## Next: Weeks 2–4 — owner conversations (TASKS.md 2.1–2.4)

- 2.1 Prospect list: Costa del Sol agencies on Resales-Online, source per
  row; phone/manual only until the LSSI-CE check clears email (founder item).
- 2.2 Discovery script EN/ES around the /demo/solvista before/after,
  including the Resales API-key ask (agency dashboard: Properties → Feed Out
  → API Keys, IP-locked — see the WebAPI notes in the project memory).
- 2.3 Pricing proposal — founder sign-off required, never improvise.
- 2.4 Track conversations in the pipeline CLI (`app/pipeline.py` via
  ./.venv/bin/python), demo sent same-day.

## Decisions in force

Narrow 30-day pilot (one problem: after-hours enquiries go cold; one result:
answered <1 min, qualified, hot flagged same-hour; one demo:
/demo/solvista). Costa del Sol / Resales-Online; EN primary ES/DE secondary;
text-first, voice = upsell; no live transfer ever in this vertical; art. 50
disclosure non-negotiable; config pack on the shared engine, NOT a fork.

## Open / blocked (founder)

Pricing sign-off (blocks 2.3); LSSI-CE check before any cold email; Resales
WebAPI test key (sim provider is the demo fallback).

## Gotchas

- Run python via `./.venv/bin/python` inside ai-receptionist; pytest = `-q`.
- Solvista config tracked via gitignore exception (fictional client).
- Pages deploys are manual wrangler; verify via the deploy alias first
  (edge-cache poison memory), then prod.
- Narrow-pilot principle is a standing memory
  (feedback_narrow_pilot_principle_2026_08_09) — challenge build-creep.
- Side note captured in klantkraan/TODO.md: the demo-page chat X button is
  dead (posts a widget close message nothing listens for); proposed fix is a
  restart (↺) control on demo pages. Founder hasn't picked a direction yet.
