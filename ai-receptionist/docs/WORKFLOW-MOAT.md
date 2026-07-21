# Workflow moat — build order

Turning the receptionist (the *wedge*) into the operations layer (the *moat*). Strategy context:
the durable defensibility is **workflow depth + proprietary data + distribution**, not the model
and not compliance. This doc is the concrete build sequence: which `tools.py` tools and which
integration seams to add, in what order, and what each needs.

Guiding rule (from CLAUDE.md): **one module, one job**; every external integration is a seam with
a **fixed signature** and a config-selected provider, exactly like `calendar_store.py`
(`provider: sim | google`). `sim` = a local per-config JSON file for demos; the real provider is
swapped in per client without changing signatures or the receptionist.

Each stage below maps to the customer journey:
**intake/triage → offerte → schedule → invoice → review/repeat.** Build order is NOT journey order
— it's leverage ÷ cost (foundation first, the money stage early, deepest lock-in last).

---

## The spine: one job record (build this first)

Today state lives in two flat files — `bookings-<stem>.json` and `messages.json` — with no thread
between "someone asked" and "someone paid." The moat and the data asset both need a single record
that follows a customer through the whole journey.

**`job_store.py`** — internal system-of-record (the proprietary-data asset). Mirror `calendar_store`'s
sim provider: per-config file `data/jobs-<stem>.json`, atomic `.tmp`→`replace`, one lock.

```
create_job(customer_name, contact, channel, **fields) -> job_id
update_job(job_id, **fields) -> job            # appends to status_history on status change
get_job(job_id) -> job | None
find_jobs(status=None, older_than_days=None) -> list[job]   # powers the chase + reminders
```

Record shape (the data you'll later mine for benchmarks):
`id, customer_name, contact, channel, job_type, urgency, postcode, in_area, est_size, photos[],`
`status, status_history[], appointment_slot, quote_ref, invoice_ref, notes, created_at, updated_at`.

Status lifecycle: `lead → quoted → scheduled → completed → invoiced → reviewed` (+ `lost`).

- [ ] `job_store.py` with the four functions + sim JSON backing, namespaced per config.
- [ ] Fix latent multi-tenant bug: `notify.py` writes `messages.json` **un-namespaced** — clients
      share it. Namespace it `messages-<stem>.json` (mirror `_bookings_path`).
- [ ] `python -m app.selftest jobstore` (offline): create → update status → find_jobs filters.

**`messaging.py`** — the OUTBOUND seam (needed by stages 2, 3, 5; build before any outbound).
```
send(contact, text, *, channel="whatsapp", template=None) -> {ok, sent, error}
```
Provider-selected (`messaging.provider: dev | twilio | email`); `dev` prints to stdout like
`notify.owner`'s fallback. **Constraint that shapes everything outbound:** an inbound WhatsApp reply
is free (TwiML), but a *business-initiated* WhatsApp message (the chase, a reminder) requires the
**Twilio REST API + a pre-approved WhatsApp template** and respects the 24-hour session window.
Design `send()` so `template=` is mandatory for WhatsApp outside the window; SMS/email have no
template gate. Never let this become marketing — outbound is transactional only (see Compliance).

- [ ] `messaging.py` with `dev` + `twilio` providers; template-required guard for WhatsApp outbound.
- [ ] Add `MESSAGING_PROVIDER`, Twilio REST creds to `.env.example`.

---

## Build order (the answer)

| # | Stage | Add | Kind | Effort | Moat |
|---|-------|-----|------|--------|------|
| 0 | Spine | `job_store.py`, `messaging.py` | foundation | M | data asset + every integration |
| 1 | Intake & triage | `record_lead` tool + triage prompt; WhatsApp media | conversational | S–M | fills the data asset |
| 2 | Review & repeat | `request_review` action; recurring reminders | event + background | S | cheap, visible ROI (grows their leads) |
| 3 | Offerte record | `quote_store.py` + `create_quote_request` tool | conversational | M | starts the money stage |
| 4 | Offerte **chase** | `followup.py` worker (systemd timer) | background + outbound | M–H | **highest — the money** |
| 5 | Schedule | reminders (reuse worker) + `reschedule_appointment` | background + conv. | S–M | fewer no-shows |
| 6 | Invoice & pay | `invoice_store.py` → boekhouding API | external + event | H | **deepest lock-in** |

Rationale: **#2 before #3–4** because a Google review link is a config URL (near-zero integration)
with the most visible ROI — it demos as "we grew your leads" and validates the outbound path
cheaply. **#4 is the real moat** but rides on the spine, `messaging.py`, and the worker, so it comes
after them. **#6 last** — deepest lock-in, but it needs the client to run invoicing through you, so
build it only once a client is committed.

---

## Per-stage detail

### 1 — Intake & triage → persist
- **Tool** `record_lead(job_type, urgency, postcode, in_area, est_size, summary)` → `job_store.create_job(status="lead")`. Triage itself is prompt work (classify spoed/offerte/onderhoud; check postcode vs. `booking.service_area`; ask job size); the tool **persists** the structured result.
- **Channel** `channels/whatsapp.py`: read `NumMedia` + `MediaUrl0..N` + `MediaContentType0`, pass media URLs through `sessions.respond` onto the job (`photos[]`). Twilio media URLs need auth to fetch — store the URL, fetch server-side when needed. (Web-widget upload = later.)
- **Test** `selftest scope`-style: a triage turn creates a `lead` job with the right fields.

### 2 — Review & repeat
- **Action** `request_review(job_id)` — fired when a job hits `completed`; `messaging.send()` the Google review link (`reviews.google_url` in config) at the right moment. Recurring inspection/maintenance reminders via the worker (#4/#5).
- **Needs** only a config URL + `messaging.py`. No external API.

### 3 — Offerte record
- **Tool** `create_quote_request(job_id, roof_type, m2, access, notes)` → `quote_store.create(...)` (status `quoted`), then reuse `book_appointment` for the opmeting. Never quote a price (guardrail) — book the measurement.
- **Seam** `quote_store.py` (`create`, `list_open`, `update_status`) — `sim` now; later the client's quoting tool (e.g. Offorte) or their template pipeline.

### 4 — Offerte chase (the moat)
- **Worker** `followup.py` run by a **systemd timer** (copy `ops/hetzner/ai-receptionist-watchdog.{service,timer}`). Each run: `job_store.find_jobs(status="quoted", older_than_days=N)` → `messaging.send(template=...)` a nudge → record the attempt on the job → after M attempts with no reply, `notify.owner`. Idempotent; safe to run every few hours.
- **Needs** the spine + `messaging.py` + an **approved WhatsApp template** (or fall back to SMS/email).
- **Test** offline: seed a stale `quoted` job, run one worker pass with the `dev` messaging provider, assert one attempt recorded + escalation after M.

### 5 — Schedule & dispatch
- Reuse the worker for **appointment reminders** + "monteur is onderweg" (jobs with `appointment_slot` tomorrow → reminder). **Tool** `reschedule_appointment(job_id, new_slot)` — extend `calendar_store` with a reschedule (free old slot, book new). Weather-aware planning / crew routing = **deferred** (advanced, low near-term ROI).

### 6 — Invoice & get paid
- **Seam** `invoice_store.py` (`create_invoice(job)`, `list_unpaid()`, `mark_paid()`) → boekhouding API. **Moneybird** has the friendliest API; e-Boekhouden / Exact are alternatives per client. Trigger on `completed` (internal/event, not a customer turn); chase unpaid via the worker.
- Heaviest lift, deepest lock-in. Do it with a committed, paying client — not speculatively.

---

## Cross-cutting

- **The worker is one process, many jobs.** `followup.py` does the chase (#4), reminders (#5), and
  review sends (#2) in one systemd-timed pass — don't spawn three workers.
- **Config over code.** Every new capability is config-selected per client: `messaging.provider`,
  `quote.provider`, `invoice.provider`, `reviews.google_url`, chase thresholds (`followup.after_days`,
  `followup.max_attempts`). A rebrand stays zero-code. New secret → also add to `.env.example`.
- **Testing.** Keep each seam offline-testable with a `sim`/`dev` provider (like `calendar`): add
  `selftest` layers `jobstore`, `quotes`, `followup` (dev provider), so the whole moat runs with no
  network and no spend.
- **Compliance (unchanged, non-negotiable).** Art. 50 disclosure stays in every greeting. Outbound
  (chase/reminders/reviews) is **transactional only** — the customer initiated by requesting a quote
  or booking; this is not the "automated replies/DMs/cold outreach" the Forbidden list bans. Honor
  WhatsApp's template + 24h rules; give every outbound an opt-out; never repurpose the chase as
  marketing.

## First concrete task when resuming
Build **the spine** (`job_store.py` + namespacing fix + `selftest jobstore`), commit, then #1
(`record_lead`). Everything else hangs off those. Ralph loop: small step → build → selftest →
eyeball → commit.
