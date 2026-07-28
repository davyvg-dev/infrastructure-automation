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

## Who sets the status — the owner channel (build this second)

The spine above has a hole: **nothing sets most of the statuses.** The bot can set `lead`
(`record_lead`) and `scheduled` (`book_appointment`). It has no way to know a quote went out, a
job got finished, an invoice was sent, or money arrived. Every module downstream of `scheduled`
triggers on state the bot cannot observe. Solve this before building any of them.

Three possible sources of truth, cheapest first:

| Source | Covers | Cost to the client | Verdict |
|---|---|---|---|
| Infer from the calendar | `completed` (slot has passed) | zero | Too unreliable to act on — a cancelled visit becomes "hoe ging het?". Use it to *ask*, never to assert. |
| **The owner tells the bot** | everything | one WhatsApp reply a day | **Primary.** |
| Boekhouding API (Moneybird) | `invoiced`, `paid` | integration | Upgrade, per client, stage #6. |

**The design: the owner talks to the same bot, from their own number.**

The client already has WhatsApp open all day. Give them no dashboard, no app, no login — just the
same thread, in the other direction. Each afternoon the worker sends the owner today's jobs and
takes plain-language replies:

```
17:30  Klantkraan → owner
       2 klussen vandaag. Klaar?
       1. Van Ostadestraat 44 — lekkage keuken
       2. Bilderdijkkade 12 — cv-onderhoud

17:52  owner → Klantkraan
       1 klaar, factuur 340. 2 niet gelukt, klant was niet thuis

17:52  Klantkraan → owner
       Genoteerd. Van Ostadestraat op factuur €340, reviewverzoek gaat morgen.
       Bilderdijkkade terug op de planning — zal ik een nieuwe tijd voorstellen?
```

Why this is the right shape:

- **Zero adoption cost.** No new tool for someone who does not want new tools. The channel is the
  one they already answer.
- **It reuses the whole stack.** `sessions.respond()` unchanged, `whatsapp.py` unchanged apart from
  a role check, tenant routing unchanged.
- **It fills the data asset for free.** Every job gets an outcome labeled by the person who did it,
  in one sentence, with no data entry. That is the proprietary-data moat writing itself.
- **It is the retention surface.** The client hears from Klantkraan every working day, doing office
  work. That is a very different cancellation decision than a bot they never see.

Shape:

```yaml
# config/clients/<slug>.yaml
owner:
  whatsapp: "+3161..."          # inbound from this number = owner role
  daily_closeout: "17:30"       # when the worker asks; omit to disable
```

- `channels/whatsapp.py` — after resolving the tenant from `To`, if `From` matches `owner.whatsapp`,
  call `sessions.respond("whatsapp-owner", ...)`. One branch.
- `receptionist.py` — `build_system_prompt(role="customer" | "owner")`. The owner prompt is short
  and terse: no art. 50 pitch, no sales tone, no booking flow.
- `tools.py` — split into `TOOLS_CUSTOMER` and `TOOLS_OWNER` (`list_jobs`, `update_job_status`,
  `pause_followups`, `reschedule_appointment`). **The owner tool list must be selected by role, not
  requested by the prompt** — a customer session must be structurally unable to reach
  `update_job_status`, not merely told not to. Enforce at the tool-list level.
- Session keys already namespace by channel, so `whatsapp-owner` gets its own history for free.

- [ ] `owner:` block in config + `settings` accessor; role resolution in `whatsapp.py`.
- [ ] `TOOLS_OWNER` + role-parameterised system prompt; assert in a test that a customer role
      cannot see owner tools.
- [ ] Daily closeout in the worker; `selftest owner` offline (seed jobs → run closeout with the
      `dev` provider → assert the prompt lists exactly today's jobs).

---

## One job, end to end

What stages 0–4 look like in the client's actual life. Tuesday.

| When | Who | What happens | State |
|---|---|---|---|
| 07:12 | customer → WhatsApp | "Goedemorgen, ik heb een lekkage onder de gootsteen" | `record_lead` → `lead` |
| 07:12 | bot | triages as spoed, checks the postcode against `service_area`, offers 11:00 | |
| 07:14 | bot | books it, notifies the owner on Telegram as today | `scheduled` |
| 11:40 | owner → bot | (at closeout) "klaar, offerte voor nieuwe kraan 285" | `completed` + quote opened |
| 12:00 | worker | sends the review request | `reviewed` |
| Thu | worker | quote is 2 days old, no answer: one utility template nudge | attempt 1 |
| Sun | worker | 5 days: second nudge | attempt 2 |
| next Wed | worker | no reply after 3 attempts — stops, tells the owner to call | escalated |
| next Wed | owner | calls, wins the job | `scheduled` again |

The receptionist alone delivers row 1–3 — the front desk. Rows 4–9 are the office. **That gap is
the entire €299 → €599 argument**, and it is the part no €99 answering bot reaches, because it
requires a job record and a relationship with the owner, not a better voice.

---

## Build order (the answer)

| # | Stage | Add | Kind | Effort | Moat |
|---|-------|-----|------|--------|------|
| 0 | Spine | `job_store.py`, `messaging.py` | foundation | M | data asset + every integration |
| 0b | Owner channel | role split + `TOOLS_OWNER` + daily closeout | foundation | M | **sets the state everything else triggers on**; daily client contact |
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

## Outbound economics — what WhatsApp charges (checked 2026-07-28)

Business-initiated messages are metered, and the meter shapes the copy. Meta moved to per-message
pricing on 1 July 2025: every delivered template is billed by **category** and **recipient country**.

| Category | NL rate | Applies to |
|---|---|---|
| Utility | typically **under $0.03** (DE, the top of the band, is $0.055) | transaction follow-up: quote nudge, appointment reminder, invoice chase |
| Marketing | **~$0.16–0.18** — among the highest in the world | anything with promotional intent |
| Service (free-form, inside the 24h window) | free today, **charged from 1 Oct 2026** | the receptionist's own replies |

Three consequences, in order of how much they matter:

1. **Every follow-up must qualify as utility, and the Dutch copy decides that.** Meta draws the
   line at promotional intent. *"Zullen we de offerte doorzetten?"* is utility — it concerns an
   existing transaction. Add *"deze week 10% korting"* and the same message becomes marketing at
   roughly five times the price, in a country where marketing is the most expensive rate on earth.
   Write every template as a transaction status, never as an offer. This is also what keeps
   outbound on the right side of the Forbidden list.
2. **Module cost per client is negligible — say so when pricing.** A trade doing ~40 jobs/month
   sends roughly 45 quote nudges + 40 reminders + 40 review requests ≈ 125 utility messages ≈
   **€3–5/month**. The €599 tier is not exposed to messaging cost. *(Correction 2026-07-29: the 40
   review requests should not be assumed utility. Asking a customer for a review is persuasive
   intent by Meta's published criteria, so expect that template to bill as marketing — about €5/mo
   more per client. Still negligible; the number above is the floor, not the ceiling. See
   `whatsapp-templates.md` §2.4.)*
3. **From 1 Oct 2026 Meta charges per business message including service replies inside the 24-hour
   window.** This hits the **core €299 product**, not the modules. At ~200 conversations × ~8
   replies a client sends ~1,600 service messages a month; the gross-margin claim of ~97% needs
   re-modelling once the service rate is published. **Do not guess it — check the rate and redo
   `07-finance/` before 1 October.**

**Get templates approved once, generically.** Templates are submitted to Meta for approval and
approval is not instant. Do not create per-client templates or every onboarding is gated on Meta.
Approve ~5 generic Dutch utility templates with variable slots (`{{1}}` business name, `{{2}}` job,
`{{3}}` amount) and reuse them across the whole client base. Twilio's surface is the Content API:
`client.messages.create(from_=..., to=..., content_sid=..., content_variables=json.dumps({...}))`
— `content_sid` is the approved template, so `messaging.send(template=...)` maps to it directly.
*(Twilio Content API + WhatsApp quickstart via context7 `/llmstxt/twilio_llms_txt`, 2026-07-28.)*

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
Build **the spine** (`job_store.py` + namespacing fix + `selftest jobstore`), commit, then **0b the
owner channel** — without it stages 2–6 have no trigger — then #1 (`record_lead`). Ralph loop:
small step → build → selftest → eyeball → commit.

**Gate:** none of this starts before the receptionist has paying clients (`klantkraan/TODO.md`
item E is still open). Build order is settled; build *timing* is ~5 paying clients, and module N+1
waits for three clients to ask. Rationale in `klantkraan/research/automation-expansion-2026-07.md`.
