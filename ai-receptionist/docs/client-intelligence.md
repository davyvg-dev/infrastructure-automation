# Perfect oversight — the client intelligence layer

Design round, 2026-07-22. Goal: one operator with complete oversight of every client's chatbot — enough to **maintain** them, **improve** them, **give the client insights**, **spot upsells**, and **prove ROI** — all mined from the actual conversations. Companion to `oversight-architecture.md` (that doc covers tenancy/deploy/infra; this one covers the data + intelligence + surfacing).

The honest framing: "perfect" oversight = you never have to read a raw transcript to know how every bot is doing, what's broken, what to improve, and where the money is. You get that by capturing everything cheaply, then letting Claude turn transcripts into structured intelligence you can query and push to your pocket.

---

## The two data layers

**Layer 1 — raw capture (deterministic, cheap, at the code seams).** Every conversation, turn, tool call, and token, persisted to Postgres, tagged `client_slug`. This is ground truth. It already all flows through one function.

- **Hook: `sessions.respond(channel, user_id, text)`** (`sessions.py:49`) — every channel (web/WhatsApp/Telegram) passes through here, and `active_client()` gives the slug. Wrap it: open/append a `session` row, store each user+assistant turn, stamp `after_hours` (compare to the client's `hours` in config), close the session on inactivity.
- **Hook: the tool loop in `run_turn`** (`receptionist.py:154-167`) — already funnels every `check_availability` / `book_appointment` / `take_message` through one `tools.execute` + `log.info`. Capture tool name, input, output here → that's how you know a booking or a lead happened, deterministically, without guessing.
- **Hook: `response.usage`** (`receptionist.py:143`) — `input_tokens`/`output_tokens` are on every `messages.create` and currently thrown away. Sum them per session → **exact per-client cost and margin** (you already know your price and your token rate).
- **Fix while here:** make `notify.take_message` tenant-aware (write the lead with its `client_slug`, route the alert to that client's recipient). Today all clients' leads pile into one global `data/messages.json` — that defect blocks per-client lead counts.

**Layer 2 — derived intelligence (an async Claude "analyst" over each finished conversation).** This is the gold. A cheap, batched pass (nightly, Haiku 4.5, forced JSON schema) reads each completed transcript and extracts structured insight. The same model that runs the bot mines its own conversations. It runs *out of band* — never in the customer's turn, so it never adds latency or risk.

What the analyst extracts per conversation (`insights` row):

| Field | Use |
|---|---|
| `intent`, `topics[]` | What customers actually want → client insight, FAQ/scope tuning |
| `resolved` (bool) | Did the bot handle it? → quality/maintenance |
| `escalated` (bool) + `escalation_reason` | Where the bot gave up → improvement backlog |
| `unanswered_questions[]` | Exact questions the bot couldn't answer → **FAQ gaps to fix** |
| `out_of_scope_requests[]` | Adjacent services asked for → **new-service upsell for the client** |
| `sentiment` (pos/neu/neg) | CSAT proxy → attention feed |
| `language` | Customer's language vs the bot's config language → **multilingual upsell** |
| `customer_type` (new/existing/vendor/spam) | Lead quality |
| `lead_captured`, `booking_made` (bool) | ROI (corroborates Layer-1 tool events) |
| `est_job_value_eur` | ROI € figure (from service prices in config + intent) |
| `upsell_signals[]` | Structured tags (see catalog below) |
| `quality_flags[]` | **Bot mistakes to review** (see catalog below) |

Retention split (AVG): purge **raw transcripts** at 30-90 days; keep the **`insights` + rollups** longer — they're aggregated, lower-PII, and they're your ROI history and trend line. Redact obvious PII (phone/email) before the analyst pass and before any external observability tool.

---

## The intelligence that comes out

### Upsell radar (per client, auto-tagged)
- `after_hours_share_high` → **voice/callback tier upsell** ("38% of your chats came in after hours").
- `out_of_scope:<service>` recurring → **new service line** ("customers asked 12× for airco maintenance you don't list").
- `language_mismatch:<lang>` → **multilingual upsell** ("8 customers wrote in German this month").
- `booking_intent_no_calendar` (booking asked, provider still `sim`) → **calendar integration upsell**.
- `volume_growth` → **higher tier**.
- `unsupported_request:<feature>` (photos, quotes-with-attachments, payment) → **feature upsell**.

### Improvement / maintenance backlog (per client, auto-generated)
- Repeated `unanswered_questions` clustering on the same topic → **"add these 5 FAQ entries."**
- `quality_flags`: `refused_in_scope_job` (the exact class fixed in commit 16dff39), `quoted_price_it_shouldnt`, `invented_slot`, `hallucinated_fact` → **transcripts to review + config/prompt fix.**
- Turn-cap hits (already alert via `notify.owner`), rising escalation rate, negative-sentiment clusters → **the bot is degrading, act.**
- Bot health: error rate, last-seen, API/credit failures (extend the existing watchdog to probe *each* `config/clients/<slug>` bot, not just the demo).

### Client ROI report (the retention + upsell weapon)
Monthly Dutch PDF (Jinja2 → WeasyPrint → Resend), per client:
- **Conversations handled** and **% after-hours** (the headline — the gap you sell against).
- **Leads captured + bookings made** → **estimated € value** (leads × their avg job value) and **hours saved** (conversations × avg handle time), framed against the subscription: "€X captured vs €Y/mo."
- **Top questions your customers asked** — insight they cannot get anywhere else; this is what makes the report feel worth paying for.
- **What we improved this month** — one line, shows you're actively managing their bot.
- A soft upsell line seeded from the radar ("we noticed 38% after-hours — voice could catch those calls too").

---

## Delivery — oversight without a dashboard to babysit

You dislike babysitting vendor dashboards, so sequence it that way:

1. **Daily Telegram oversight digest (v1 — the fastest "perfect oversight").** One message each morning via the existing `notify.owner` seam: a one-liner per client (conversations · leads · cost · red flags) + a **"NEEDS ATTENTION"** block (a bot erroring, an escalation spike, a quality flag, a cost overrun). This is complete oversight of everybody, in your pocket, zero web UI. Reuses infra you already run.
2. **Read-only `/admin` page (v2).** A single Basic-Auth HTML page querying Postgres: all-clients table with sparklines + drill-down into a client's insights, backlog, upsell radar, and (within retention) transcripts. Or just point PostHog dashboards at the same events — no custom UI at all.
3. **Monthly client PDF (v3).** The ROI report above, sent to each client.

---

## Data model (Postgres on the Hetzner box; all tagged `client_slug`)
- `sessions` — id, client_slug, channel, user_ref (hashed), started_at, ended_at, turns, after_hours, outcome (booked|message|answered|dropped), input_tokens, output_tokens, cost_eur, model.
- `turns` — id, session_id, role, text, tools (jsonb), ts. *(30-90d retention, then purge text.)*
- `insights` — session_id, client_slug, + all Layer-2 fields above (jsonb/arrays), analyzed_at, analyst_model. *(kept beyond transcript purge.)*
- `daily_client_stats` — client_slug, date, conversations, after_hours, leads, bookings, est_value_eur, tokens, cost_eur, unanswered_count, escalations, avg_sentiment. *(cheap rollup powering the digest, console, and report.)*

`data/pipeline/<slug>.yaml` stays the client registry; these tables join to it on `slug`. (Convergence onto the `klantkraan/` monorepo `clients`/`calls`/`events` Postgres schema is optional and better deferred until the voice product ships — see `oversight-architecture.md` decisions.)

---

## Cost & trust
- **Analyst cost is small:** one **Haiku 4.5** call per finished conversation, batched nightly. Pennies per client per month; keep the bot itself on `claude-opus-4-8` from config. Model choice lives in config, per repo convention.
- **The analyst is probabilistic:** treat `quality_flags` and `upsell_signals` as *leads to review*, not ground truth. The deterministic Layer-1 events (a booking happened, a lead was saved, tokens spent) are the hard numbers for the client-facing ROI report; the LLM-derived layer drives *your* attention and improvement work.

---

## Phased build (mapped to the real seams)
**Slice 1 — capture (do first, ~a weekend).** Postgres `sessions`+`turns`; write at `sessions.respond` + the `run_turn` tool loop; capture `response.usage`; make `notify` tenant-aware (fixes the global-lead defect). Now every conversation is durable and per-client. Add the retention/purge job.

**Slice 2 — the analyst + digest.** Nightly Haiku job → `insights` + `daily_client_stats`; ship the **daily Telegram oversight digest**. This is the moment you have real oversight of everybody.

**Slice 3 — surfacing.** The read-only `/admin` page (or PostHog dashboards) for drill-down; the auto-generated improvement backlog + upsell radar views.

**Slice 4 — client ROI PDF.** Monthly Jinja2 → WeasyPrint → Resend report with the insight + upsell hooks.

**Bottom line:** capture everything at the one function every channel already flows through, let a cheap nightly Claude pass turn transcripts into structured intelligence (upsell signals, FAQ gaps, quality flags, ROI €), and push a daily digest to your Telegram. That is perfect oversight — maintenance, improvement, client insight, upsell, and ROI proof — with almost no ops and no dashboard to babysit.
