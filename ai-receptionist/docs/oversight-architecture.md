# Maintainability & oversight architecture

Design round, 2026-07-22. Question: as clients come in (target ~10-50 chatbots), how does this stay maintainable, how do we deploy client pages with minimal work, and how do we get per-client oversight so we can send clients reports? Grounded in the actual repo, not generic advice. **No building yet — this is the design + decision list.**

> Companion: `client-intelligence.md` takes the oversight goal further — mining the actual conversations for maintenance, improvement, client insights, upsell signals, and hard ROI ("perfect oversight"). This doc is the infra/tenancy substrate it builds on.

---

## Verdict up front
The architecture is **already right**. Do NOT re-architect tenancy. `ai-receptionist` serves every client from **one shared FastAPI process**, routing per-request by slug (`?client=` / `X-Client-Slug` / `<slug>.klantkraan.nl` Host) via a `ContextVar` in `app/settings.py`. A new client is a **YAML file, not a process** — the equivalent of the "pooled / shared-schema" model that is the standard recommendation for a solo B2B SaaS at this scale. Config-per-client YAML in git (versioned, diffable, no infra) is fine well past 50 clients.

The real gap is not tenancy — it's that **almost nothing per-client is persisted or observable**. That is what to build, and it does not require changing the tenancy model.

You outgrow "YAML + one process" on three specific triggers, none of which is client count:
1. **You need per-client metrics/reports** → add a `client_slug`-tagged events store. *(This is the actual pain. Do it first.)*
2. **Config must be editable by non-devs / self-serve** → move config from YAML-in-git to DB rows. Not needed while you're the only editor.
3. **One heavy/regulated client needs isolation** → silo *that one* into its own process (systemd template unit — you already run this pattern for `growth-engine@fitness`). Don't split everyone because one is special.

---

## What exists today (ground truth)
- **Client = one YAML.** `config/clients/<slug>.yaml` is live/auto-routed (production, gitignored for PII, ~25 real files). Fields: business/persona/scope/services/hours/booking/faq/greeting/model/locale/calendar. Loaded with `@lru_cache` in `settings.py` → **editing a client needs a server restart**.
- **Slug is the identity through-line**: same slug names the demo config, `config/clients/<slug>.yaml`, `data/bookings-<slug>.json`, and `data/pipeline/<slug>.yaml`.
- **One process, per-request tenancy**: `server.py:_activate` → `resolve_slug(host, override)` → `use_slug()` sets `ContextVar`; every `settings.business()` reads the active tenant ambiently. In-memory session store (`sessions.py` `_STORE`) forces **a single uvicorn worker** — the hard scaling ceiling and a shared blast radius (one crash drops all tenants).
- **Onboarding is already a state machine**: `app/pipeline.py` (`lead → qualified → staged → demo → signed → onboarding → live`), one `data/pipeline/<slug>.yaml` per prospect, with the AVG suppression + NL-BV gate on `qualify` and the scaffold seam on `stage` (`scaffold.build_config`, language-keyed template registry). Go-live = move the YAML into `config/clients/` + DNS A-record + optional Google Calendar. No new process, no code redeploy.
- **Demo pages** = `?client=<slug>` query param on one shared backend (the ec01a38 fix made `index.html` forward the param); per-vertical marketing pages point their iframe at a different `?client=`.
- **growth-engine is the multi-instance precedent**: `growth-engine@<vertical>` systemd template, one `.env.<vertical>` each. This is the model *if* per-client process isolation is ever wanted — but `ai-receptionist` deliberately multiplexes in-process instead.

### The oversight gaps (concrete)
1. **No durable transcripts** — `_STORE` is in-memory, lost on restart. Can't audit what the bot said.
2. **Lead capture is global** — `take_message` writes all clients into one `data/messages.json` with no client field (`notify.py`).
3. **Single-recipient alerting** — one `OWNER_TELEGRAM_CHAT_ID` for everyone; clients can't get their own leads.
4. **No metrics** — no counts of conversations, bookings, messages, tokens/cost per client.
5. **No report/dashboard** for the live Python app.
6. **Logs are stdout only, un-namespaced by tenant** — correlating an incident to a client means guessing.
7. **Watchdog is single-tenant** — probes only the default demo; a specific client's broken bot is invisible.
8. **Two divergent client models** — the Python app keys off a filesystem slug; the `klantkraan/` monorepo defines a Postgres `clients` tenant table (`packages/db/src/schema.ts`) with `calls`/`bookings`/`events`/`mrr_snapshots` and a per-client `dashboard.ts` route — but **the write paths are commented-out stubs and it's not deployed**. No shared source of truth links a `config/clients/<slug>` to a `clients` row.

---

## Recommended stack (pragmatic, bootstrapped, one VPS)
- **Tenancy** — keep YAML-per-client + single shared process, routed by slug. Tag every stored event with `client_slug`. No change.
- **Deploy** — keep the single systemd unit + `ops/hetzner/deploy.sh`. Adding a client stays "drop a YAML + DNS." (Add a `.socket` unit later for zero-downtime restarts. No PaaS yet — the €6-7 Hetzner box wins until well past 50 clients. If juggling services by hand ever gets fiddly, **Coolify** gives a UI without a managed-PaaS bill.)
- **Data** — one **Postgres on the Hetzner box** (or Neon free tier), schema: `conversations` + `events`/`bookings`, tagged by `client_slug` + timestamp. SQLite+Litestream is a legit simpler start, but Postgres gives concurrent writers (channel adapters + report job) and easy per-client SQL. *Avoid Supabase free tier — it pauses after ~1 week idle, bad for quiet client bots.* Keeps EU data on infra you control.
- **Observability** — **PostHog Cloud free (100k LLM events/mo, EU region)** *or* **Langfuse Cloud Hobby free (50k units/mo)** wrapped around the Anthropic client for prompt/tool-use tracing + token/cost + per-session view; **Sentry free (5k errors/mo)** for code errors. Both PostHog and Langfuse are native-Anthropic and zero-infra. **Do NOT self-host Langfuse at this scale** — it wants ClickHouse+Postgres+Redis+MinIO (~4 CPU/16 GB), won't sit next to the bot on a cx23. PostHog edges it because the same free account also gives product analytics + session replay.
- **Reporting** — monthly `cron`/systemd timer → SQL per client → **Jinja2** HTML → **WeasyPrint** PDF → email via your existing Resend/SMTP. One Dutch template, per-client data injected (same config-over-code discipline). Metrics that move an SMB owner: **conversations handled (+ % after-hours)**, **leads/bookings captured**, **questions answered/deflected**, **after-hours capture count**, **estimated hours saved / € ROI vs subscription**. The ROI line is the retention hook that justifies the invoice.
- **GDPR/AVG** — set a retention window (30-90 days) with an auto-purge job *now* (cheap early, painful to retrofit); redact obvious PII (phone/email) before logging to any observability tool; prefer EU-region cloud or self-host so conversation content stays out of US-transfer/DPA complexity. You already do the EU AI Act art. 50 disclosure — you're ahead of the Aug 2026 deadline.

---

## The fastest insertion points (where these hooks land in the code)
The repo already has clean seams for all of this:
- **Persist transcripts + per-turn events** at `sessions.respond` / the `receptionist.run_turn` tool loop, namespaced by `active_client()`. (`sessions.py` explicitly documents `_STORE` as the Redis/Postgres swap seam.)
- **Per-client counters** at the single tool-execute choke point (`tools.execute` + the existing `log.info("tool ...")` line).
- **Tenant-aware notifications** — make `notify.owner` / `notify.take_message` read a `notify:` block per client YAML; write leads to `data/messages-<slug>.json` (or the DB) instead of one global file. Fixes gaps 2 + 3 together.
- **Client registry** — `data/pipeline/<slug>.yaml` is already the closest thing to a client registry; either keep it file-based (add `data/metrics/<slug>.json` rollups) or converge onto the `klantkraan/` Postgres `clients` table.

---

## Decisions to make (these are yours)
1. **File-based vs Postgres for events.** Recommendation: **Postgres on the VPS** — SQL per-client is what makes reporting and the oversight view trivial. (SQLite+Litestream if you want the absolute-minimum start.)
2. **Converge the two client models, or not?** The `klantkraan/` monorepo already has the ideal schema (`clients`/`calls`/`bookings`/`events`) + a stubbed per-client `dashboard.ts`. Option A: wire the Python app's events into that Postgres and unify on `clients.slug` (more upfront, one source of truth, gets you the dashboard route). Option B: keep it lightweight in the Python app (`data/metrics/<slug>.json` or a small Postgres table) and treat the monorepo as future voice-only. Recommendation: **B now, A when the voice product actually ships** — don't converge onto an undeployed stack prematurely.
3. **PostHog vs Langfuse** for LLM tracing — both free, both native-Anthropic. Recommendation: **PostHog** (analytics + replay in the same free account).

---

## Phased roadmap (mapped to the real seams)
**Do now (1-5 clients) — ~a weekend, essentially free**
- Add a `conversations`/`events` table (SQLite or on-VPS Postgres); log every turn at `sessions.respond` with `client_slug`, timestamp, after-hours flag, whether a booking/lead resulted, tokens/cost.
- Make `notify` tenant-aware (per-client recipient + per-client `data/messages-<slug>.json`). Fixes the global-lead defect.
- Wire **PostHog/Langfuse Cloud (free)** around the Anthropic client + **Sentry** for errors.
- Add the retention + auto-delete job.

**At ~10 clients — the reporting/oversight build**
- If on SQLite, move events to Postgres.
- Build the **monthly PDF report** cron (conversations, after-hours capture, leads/bookings, hours-saved/ROI, in Dutch).
- Stand up a tiny **internal oversight view** — PostHog dashboards or a single `/admin` page querying the DB per client. This is what lets you see every bot at a glance.
- Make the **watchdog per-client** (probe each `config/clients/<slug>` bot, not just the demo).

**At ~50 clients — only if pain appears**
- If LLM volume outgrows the free tier or EU residency forces it, pay Langfuse Core ($29/mo) or self-host it *on its own box*.
- **Silo any VIP/regulated client** into its own systemd template process + DB; keep the rest pooled.
- Add **Coolify** if managing services by hand gets fiddly; add Prometheus+Grafana if the VPS itself needs health monitoring; consider a second VPS before this becomes a second job.

**Bottom line:** don't touch tenancy. Add one `client_slug`-tagged events store + free-tier LLM observability now, a Jinja2→WeasyPrint monthly report at ~10 clients, and fix the tenant-aware `notify` defect along the way. Everything is free-tier or on-VPS until past 50 clients, keeps EU data on infra you control, and adds almost no ops burden.
