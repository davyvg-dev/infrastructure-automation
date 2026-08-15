# Track 4 — Klantkraan Command Center — Audit + Research + Design

## A. Inventory: what exists today

### A1. Runnable commands (all `python -m`, cwd-sensitive)

| Command                                                                                                                                                        | Lives in                            | Purpose                                                                                          | State it owns                                                                                           |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- | ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `app.pipeline board / add / qualify / advance / stage / sign / call / calls / note / show`                                                                     | `ai-receptionist/app/pipeline.py`   | Deal-flow state machine, text kanban with `NEXT_ACTION` per stage                                | `ai-receptionist/data/pipeline/<slug>.yaml` (25 records; 23 stuck at `staged`) + `data/suppression.txt` |
| `scripts.sequence board / stop <slug> --replied                                                                                                                | --opt-out                           | --bounced`                                                                                       | `ai-receptionist/scripts/sequence.py`                                                                   | 4-touch outreach ledger (day 0/3/7/14)                           | `ai-receptionist/build/outreach/sent.json` — **relative path, breaks unless cwd is `ai-receptionist/`** |
| `scripts.outreach_send [--dump                                                                                                                                 | --send --limit 6 --touch N]`        | `ai-receptionist/scripts/`                                                                       | Gmail SMTP sender; dry-run default; 6/day cap is convention, not code                                   | writes touches into `sent.json`                                  |
| `scripts.sourcing discover / qualify / export`, `scripts.enrich`                                                                                               | `ai-receptionist/scripts/`          | KvK list-building + enrichment                                                                   | `data/sourcing/profiles/`, CSVs; prospect roster **hardcoded** in `outreach_mail.py`                    |
| `app.billing checkout / status / welcome / subs / cancel / refund / offboard`                                                                                  | `ai-receptionist/app/billing.py`    | Mollie subscriptions CLI                                                                         | `data/billing.jsonl` (1 event: €1 test); `data/invoices.json` + `data/invoices/` **don't exist yet**    |
| `app.evals [run <name                                                                                                                                          | pack                                | all>]`                                                                                           | `ai-receptionist/app/evals.py`                                                                          | 14 goldens, LLM customer + judge, exit 1 on fail; plaintext only | none (sandboxed tmp DATA_DIR)                                                                           |
| `app.selftest <14 layers                                                                                                                                       | all>`                               | `ai-receptionist/app/`                                                                           | Offline config/routing/calendar checks                                                                  | reads `data/`                                                    |
| `app.oversight digest [--dry --today] / analyze / insights <slug>`                                                                                             | `ai-receptionist/app/`              | Founder digest + nightly Claude analyst                                                          | `data/analytics.db` (SQLite)                                                                            |
| `app.watchdog [--check                                                                                                                                         | --deep]`                            | `ai-receptionist/app/`                                                                           | Liveness + deep `/chat` probe, self-heal, Telegram transitions                                          | `data/watchdog_state.json`                                       |
| `app.extract` → `app.scaffold`                                                                                                                                 | `ai-receptionist/app/`              | Website → cited client config YAML                                                               | `config/{clients,prospects}/<slug>.yaml` (31 configs)                                                   |
| `python -m src.run`                                                                                                                                            | `growth-engine/`                    | Content pipeline: Telegram approval bot + scheduler                                              | `data/<vertical>/queue.json` (append-only), `state.json`, `media/`                                      |
| `src.seo report [--send]`, `src.push`, `src.selftest`, `src.publish_buffer [--test-draft]`, `src.publish_meta`, `src.publish_tiktok`, `src.pagekit`, `src.sfx` | `growth-engine/src/`                | SEO report, draft push, self-tests, publishers                                                   | tokens in `data/<v>/`                                                                                   |
| `calls.py list / show / latency`                                                                                                                               | `klantkraan/apps/voice-agent/demo/` | ElevenLabs call-log reader                                                                       | none (API)                                                                                              |
| `ops/hetzner/deploy.sh <ip>`                                                                                                                                   | repo root                           | THE deploy: rsync monorepo → `/opt/klantkraan` on 168.119.173.25, venvs, 10 systemd units, Caddy | server `.env` + `data/` are source of truth                                                             |
| `ops/briefing/agent.sh [--dry-run]`                                                                                                                            | repo root                           | 08:30 briefing: IMAP + DSNs + boards + call log → `claude -p` → Telegram                         | **launchd plist not installed yet**                                                                     |
| `scripts/copy-lint.sh`, `scripts/compliance-check.sh`                                                                                                          | repo root                           | Copy + art. 50/BV-gate CI gates                                                                  | none                                                                                                    |
| Slash commands `/board /run-evals /deploy-site /new-client-demo /log-regression`                                                                               | `.claude/commands/`                 | Wrappers; `/board` = pipeline + sequence boards                                                  | —                                                                                                       |
| Site deploy                                                                                                                                                    | `klantkraan/apps/marketing-site`    | `astro check` → `build` → `wrangler pages deploy ./dist --branch=production`                     | CF Pages `klantkraan-marketing`; API = Hono Worker `klantkraan-api`                                     |

### A2. Schedulers (the fleet as it actually runs)

| Unit                              | Where                          | Schedule    | Runs                        | Alerts on failure?      |
| --------------------------------- | ------------------------------ | ----------- | --------------------------- | ----------------------- |
| `ai-receptionist.service`         | Hetzner systemd                | always-on   | FastAPI server              | via watchdog only       |
| `growth-engine.service`           | Hetzner                        | always-on   | `src.run` Telegram bot      | **no**                  |
| `ai-receptionist-watchdog.timer`  | Hetzner                        | every 2 min | self-heal + Telegram        | is the alerter          |
| `ai-receptionist-retention.timer` | Hetzner                        | daily       | `app.analytics purge` (AVG) | **no**                  |
| `ai-receptionist-analyst.timer`   | Hetzner                        | 03:00       | `app.oversight analyze`     | **no**                  |
| `ai-receptionist-digest.timer`    | Hetzner                        | 07:30       | digest → Telegram           | exits 1, nobody watches |
| `growth-engine-seo.timer`         | copied, **not enabled**        | Mon 08:00   | `src.seo report --send`     | —                       |
| `growth-engine@.service`          | template, **not enabled**      | —           | fitness/founder verticals   | —                       |
| `com.klantkraan.briefing`         | Mac launchd, **not installed** | 08:30       | briefing agent              | —                       |
| (dormant) `infra/` docker stack   | different host design          | —           | Caddy+n8n+Uptime Kuma+Borg  | superseded              |

### A3. The N-places problem

| Question                             | Places today                                                                                                                                                                                               |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Content posted/queued/failed?        | Telegram scroll-back, SSH+jq queue.json, journalctl, Buffer UI, platforms, TikTok inbox — **6+ places, no read-back command**; `queue.json` has **no `created_at`**; dry-run writes fake `status="posted"` |
| Pipeline / outreach?                 | `/board` (2 commands, cwd-sensitive) — decent                                                                                                                                                              |
| Receptionist health / failed convos? | Telegram + digest + systemctl/journalctl + raw sqlite3; **no transcript CLI**                                                                                                                              |
| New leads?                           | **4 separate stores** (`messages-<slug>.json`, `leads.jsonl`, `listing-leads-<slug>.jsonl`, `bookings-<slug>.json`)                                                                                        |
| Billing / invoices?                  | `app.billing status` + Mollie dashboard; invoice ledger absent                                                                                                                                             |
| Site deploy status?                  | wrangler stdout + curl + CF dashboard                                                                                                                                                                      |
| Did timers run?                      | `systemctl list-timers` over SSH — nothing pushes on failure                                                                                                                                               |

## B. Research findings (2025–2026)

1. **Headless agent fleets:** consensus = headless `claude -p`/Python jobs on cron/systemd + chat-app HITL gate. Pitfalls: quiet failures run for weeks; subprocesses outliving cron shells (setsid + timeouts); parallel jobs multiplying spend; every autonomous run needs a machine-checkable exit signal. Claude Code has first-party scheduled tasks/Routines. (hidekazu-konishi.com, ranjankumar.in, code.claude.com/docs/scheduled-tasks, duet.so)
2. **Telegram-as-approval-gate** is a named recommended pattern; async review beats sync blocking. growth-engine's bot already is this — the gap is read-back, not the gate. (nnode.ai, buildmvpfast, Medium HITL example)
3. **Status page:** lowest-maintenance pattern = script regenerates **one static index.html** on a timer; no JS, no DB, no interaction. (raymii.org bash dashboard, tinystatus, pludoni/status-page). Push twin = morning Telegram digest. Klantkraan has both halves — not merged, not reliably installed.
4. **Orchestration:** Temporal = overkill; n8n = second place for logic + a service to babysit (dormant infra/ stack proves it). **Stay on systemd timers + Python + existing ledgers.** systemd gives Persistent=true catch-up + OnFailure= hooks cron lacks. (dev.to comparison, arcbjorn, xtom, dchost)
5. **Alerting:** (a) `OnFailure=` on every unit → existing `app.notify.owner` Telegram; (b) dead-man's-switch (healthchecks.io model) optional later. Client-site monitoring: uptime, SSL expiry, DNS/domain expiry, heartbeats. Page only on actionable state _transitions_ (watchdog already correct). (pingalert.io, uptimerobot)

## C. Recommended design: `kk` + one static page

**Principle: ~300-line dispatcher + one report generator. Zero new services, zero new databases. Every verb delegates to a CLI that already exists and owns its state.**

### C1. The `kk` CLI (`scripts/kk`, symlinked into PATH; also on VPS)

Thin dispatcher killing the cwd problem; resolves repo root once, cds per verb, picks the right venv.

| Verb                             | Delegates to                                             | Notes                                                                                |
| -------------------------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------ | ----------------------------------- | ----------------------------------------- |
| `kk board`                       | pipeline board + sequence board + calls                  | today's /board + due callbacks                                                       |
| `kk deal <sub>`                  | `app.pipeline …`                                         | passthrough                                                                          |
| `kk outreach [send               | stop                                                     | board]`                                                                              | outreach_send / sequence            | wrapper enforces `--limit 6` in code      |
| `kk content`                     | **new ~80-line reader** over queue.json                  | the missing read-back; needs upstream fixes: write `created_at`, tag `dry_run: true` |
| `kk leads [--today]`             | **new ~60-line reader** merging 4 lead stores + bookings | read-only                                                                            |
| `kk clients [<slug>]`            | configs + oversight insights + /config curl              | roster, health, analyst backlog                                                      |
| `kk billing`                     | `app.billing status`                                     |                                                                                      |
| `kk evals [pack]`                | `app.evals run all`                                      |                                                                                      |
| `kk health`                      | watchdog --check --deep + ssh list-timers + curl /health | fleet snapshot                                                                       |
| `kk logs <unit                   | slug>`                                                   | ssh journalctl / sqlite3 transcript query                                            | closes "no transcript CLI" gap      |
| `kk deploy [site                 | server                                                   | api]`                                                                                | /deploy-site / deploy.sh / wrangler | evals gate mandatory before server deploy |
| `kk factory <name> --url <site>` | extract → scaffold → selftest → evals → deploy → verify  | the factory verb; later grows cert/uptime registration                               |
| `kk status [--open]`             | same generator as status page                            | two renderers (ANSI + HTML)                                                          |

Keep `.claude/commands/*` wrappers calling `kk` — one surface for Claude sessions and terminal.

### C2. The single status page

- **Generator:** `ops/status/generate.py` on VPS, 5th timer (`klantkraan-status.timer`, every 15 min, Persistent=true). Reads only local server state; writes one static index.html (inline CSS, no JS, phone-friendly). Caddy serves at basic-auth'd `status.<demo-host>` vhost. "Generated at HH:MM" header + stale-warning color.
- **Content (phone-glance order):** ① red/amber/green header (watchdog, failed units, digest/analyst last-run age); ② today: conversations/leads/bookings/est. cost; ③ deal board one-liners + next actions due; ④ outreach: touches due, DSN count; ⑤ content: pending approvals, posted/queued, failures; ⑥ billing: subs/MRR/last webhook; ⑦ timer matrix; ⑧ (post-factory) per client site: HTTP status + cert days-left (curl + openssl loop, no vendor <20 sites).
- **Push stays Telegram:** merge Mac briefing's unique inputs (IMAP replies/DSNs) into the server digest → one morning message from one machine; delete launchd job.

### C3. Data flow

```
timers/services (systemd, Hetzner) ──write──> existing ledgers
        │ OnFailure=kk-alert@%n.service ──> app.notify.owner ──> Telegram (event alerts)
        └── klantkraan-status.timer ──> ops/status/generate.py ──> /var/www/status/index.html ── Caddy
founder: Telegram (push) · status page (glance) · `kk` (act)
```

New alerting piece: template unit `kk-alert@.service` firing `app.notify.owner("unit %i failed")` as `OnFailure=` on all units — ~10 lines, closes the silent-failure holes.

### C4. What NOT to build

- No n8n / Temporal / Windmill; treat dormant `infra/` docker stack as superseded.
- No database unification — ledgers each have one owning writer; `kk` adds readers only.
- No interactive web dashboard, no admin panel, no charts; approval stays in Telegram, never on the page.
- No vendor monitoring SaaS below ~20 client sites.
- No always-on `kk` daemon.

### C5. Pre-existing defects surfaced (fix before/while building `kk`)

1. `growth-engine/src/generate.py` never writes `created_at` (docstring promises it).
2. `GROWTH_ENGINE_DRY_RUN=1` approvals write `status="posted"` + fake URL into queue.json — ledger pollution.
3. TikTok/Buffer push failures leave no durable record — only Telegram scroll-back.
4. `scripts/sequence.py` ledger path is cwd-relative.
5. Digest exits 1 when Telegram/Resend unconfigured — invisible; prod .env lacks RESEND_API_KEY/OWNER_EMAIL.
6. `com.klantkraan.briefing.plist` not installed; `klantkraan/docs/regressions.md` referenced by /log-regression doesn't exist.
7. `BUFFER_CHANNEL_LINKEDIN` in .env.example is dead config.
8. Delivered-but-unanswered drafts never re-surfaced after bot restart; in-memory `awaiting_note` drops rewrites across restarts.

**Build order (each independently shippable):** ① `kk` dispatcher wrapping working verbs (board, deal, evals, billing, health, deploy) → ② ledger fixes + `kk content` + `kk leads` → ③ OnFailure wiring → ④ status generator + timer + Caddy stanza → ⑤ merge briefing into digest → ⑥ `kk factory` grows cert/uptime checks when factory lands.
