---
description: Spin up a branded prospect demo — config, checks, goldens, deploy, verified URL
argument-hint: [client name] [trade] [source URL or notes]
---

Spin up a branded demo for: $ARGUMENTS

All receptionist commands run from `ai-receptionist/` with `./.venv/bin/python`. Ralph rule: verify every step before the next; any failure stops the line.

## a) Config

1. Scrape → cited draft: `python -m app.extract "<Naam>" --url <site>` (prices are NEVER extracted — `PRIJS?` stays until the founder fills it in; citation-or-blank, no guessing).
2. Scaffold: `python -m app.scaffold "<Naam>" --from-json <extraction.json>` — writes `config/<slug>.yaml`.
3. Move it to the right gitignored dir (real names/phones allowed there, NEVER in git):
   - Shareable branded link (`?client=` routing) → `config/clients/<slug>.yaml`. This dir is immediately routable — treat as production.
   - Screen-share-only demo → `config/prospects/<slug>.yaml` (single-tenant via `BUSINESS_CONFIG=`, not routed).
4. Fill in services/hours/FAQ from their site, persona name, guardrails. The greeting MUST keep the "digitale receptionist/assistent" wording — that's the EU AI Act art. 50 disclosure; removing it is forbidden.
5. Selftest: `BUSINESS_CONFIG=config/clients/<slug>.yaml python -m app.selftest config` — must pass.

## b) Copy checks (Dutch-facing)

- Grep the config for the founder's first name — it must appear NOWHERE ("de oprichter" / "Klantkraan" only).
- Art. 50 disclosure present in the greeting.
- Customer-facing text in Dutch (unless the prospect is explicitly EN/ES), no AI-tells, no invented prices.

## c) Goldens

Add 2–3 scenarios for this client to `app/evals.py` (SCENARIOS: name, about, client=<slug>, Dutch persona, criteria incl. `ai_disclosure` — mirror the DHZ entries). Run them: `python -m app.evals run <name>` each, then `run all` to prove nothing else broke. Any failure → fix root cause before deploying.

## d) Deploy + verify

1. Deploy: `ops/hetzner/deploy.sh 168.119.173.25` (rsyncs configs incl. the gitignored client/prospect yamls, restarts the service). Server `.env` is the source of truth for secrets — never rsync .env.
2. VERIFY the branded URL end to end: open `https://demo.klantkraan.nl/?client=<slug>` and confirm `/config` returns THIS client's name and the chat greets as THIS business — not the default. (Bug ec01a38: index.html once dropped `?client=` on the `/config` + `/chat` calls, so every branded link showed the default business.) Curl check: `curl 'https://demo.klantkraan.nl/config?client=<slug>'` must show the client's name.
3. If a marketing-site page is wanted (like `/demo/dhz`), that's a separate `/deploy-site` run — site first, then API, if both change.

## e) Report

Report the demo URL, the goldens added + their results, and the selftest/verify output. Then STOP: founder confirmation gates any outreach mail — do not draft or send outreach from this command.
