# Internal audit — text-first onboarding redesign

Scope: take the delivery playbook (written for the voice/call-forwarding product) and
re-cut it for the pivoted product = a Claude web-chat widget on the client's own website,
booking into the client's own Google Calendar, hosted on our live server. No voice, no
WhatsApp, no CM.com for v1.

## 0. What the software actually does today (ground truth)

Read from `ai-receptionist/app/*`. This bounds what onboarding can promise.

- **Rebrand = one YAML.** `scaffold.py` writes `config/<slug>.yaml` (Dutch trades template);
  `sessions.respond()` → `receptionist.run_turn()` drives Claude tool-use. Greeting carries
  the EU AI Act art. 50 disclosure by construction (`_greeting()`), and the scaffolder bakes
  "digitale assistent" into every persona. This part is real and works.
- **The widget is NOT embeddable yet.** `server.py` serves `web/index.html` as a full-page
  app at `/`. There is no `<script>` bubble, no iframe embed, no per-client routing. Embedding
  it on a client's own site (the whole v1 promise) does not exist yet.
- **Google Calendar is NOT integrated yet.** `calendar_store.py` reads/writes a local JSON
  file (`data/bookings-<config>.json`) and generates slots from the YAML `hours`. The module
  is explicitly the "swap the bodies, keep the signatures" seam for Google Calendar / Cal.com,
  but that swap is unwritten. `availability()` / `book()` do not touch any real calendar.
- **Owner handoff is Telegram + a local JSON log** (`notify.py`), not SMS/CM.com. Bookings and
  `take_message` leads ping `OWNER_TELEGRAM_CHAT_ID` and persist to `data/messages.json`.
- **One process = one client.** `BUSINESS_CONFIG` selects a single config per process; sessions
  are in-memory, single-worker. Fine for client #1; multi-client needs a routing/hosting layer.

Net: the config-driven brain is ready; the two things standing between "signed" and "live on
the client's website booking into their calendar" — an **embeddable widget** and a **real
Google Calendar hookup** — are both unbuilt. Everything voice in the playbook is dead weight.

---

## 1. Gap analysis — `onboarding-30-day.md`, row by row

Legend: KEEP = applies to text-first as-is · ADAPT = keep the intent, rewrite for chat/calendar
· DROP = voice-legacy, delete.

### Day-by-day table

| Day | Step | Verdict | Why / what it becomes |
|---|---|---|---|
| 0 | Contract → Tally intake via SMS + e-mail | ADAPT | Keep intake; drop the SMS (CM.com) channel — send the link by e-mail/WhatsApp. Intake content must be trimmed (see §4). |
| 0 | Welkomstvideo Loom (90s) | ADAPT | Keep the artefact; re-record — current script promises forwarding instructions on day 4. |
| 1 | Intake → n8n validates 32 fields | ADAPT | 32 fields are voice-heavy. For client #1 this is manual; the fields that matter shrink to ~12 (see §4). n8n validation is over-engineering at 1 client. |
| 1 | Founder reviews intake, fills gaps via WhatsApp | KEEP | Still the right move. |
| 2 | Kickoff call 15 min (Cal.com) | ADAPT | Keep the call; its agenda changes — this is where you collect **website/CMS access** and **Google Calendar share**, not forwarding prep. |
| 2 | CM.com Dutch landline provisioned | **DROP** | Voice. No phone number in v1. |
| 2 | Attio workspace + pipeline | ADAPT | Optional/light. Not on the delivery critical path; keep only if already using Attio for pipeline. |
| 3 | Synthflow agent cloned + variables | **DROP** → replace | Replaced by `python -m app.scaffold` + editing the YAML. Synthflow is voice. |
| 3 | Founder fine-tunes prompt (regio/FAQ/tone) | ADAPT | Becomes: edit the client's YAML — `services`+prices, `hours`, `faq`, `persona`, region. This is the core config step and stays. |
| 4 | Cal.com event-types + Google-calendar koppeling | ADAPT | Drop the Cal.com layer (context = client's **own** Google Calendar). Becomes: connect the client's Google Calendar to the receptionist. **Blocked on unbuilt calendar integration.** |
| 4 | n8n flows (missed-call, review) deployed | **DROP** | Missed-call recovery is a voice concept; SMS review-request is CM.com. Revisit review-requests later as a chat/e-mail touch, not v1. |
| 4 | Carrier-specific forwarding Loom (KPN/Odido/Vodafone) | **DROP** | Pure voice/GSM. |
| 5 | Founder does 5 test calls (spoed/nieuw_werk/…) | ADAPT | Becomes 5 test **chats** in the widget across the same intents. Same value, different channel. |
| 5 | Cloudflare-Pages dashboard live `/r/{slug}` | ADAPT (or DROP for #1) | Dashboard is call-centric (AI calls, recovered calls, audio snippets). Metrics must change to chats/leads/bookings. For client #1, a weekly summary message is enough; defer the page. |
| 6 | Client does 3 test calls, go/no-go via WhatsApp | ADAPT | Client sends 3 test chats to the live widget on their own site; go/no-go via WhatsApp. |
| 7 | Prompt adjustments | ADAPT | YAML tweaks based on test-chat transcripts. |
| 8 | Go-live: forwarding activated, go-live SMS + dashboard link | ADAPT | Go-live = the **embed snippet is live on the client's site** and the calendar is connected — not forwarding. Confirmation via WhatsApp/e-mail; SMS optional. |
| 8–13 | Daily stats SMS | ADAPT (or DROP for #1) | Metrics change; channel changes (CM.com → WhatsApp/e-mail/Telegram). Consider weekly-only until volume justifies daily. |
| 14 | Check-in call 5 min | KEEP | Channel-agnostic. |
| 15–29 | Weekly Monday mail + dashboard PNG | ADAPT | Keep the ritual; swap call metrics for chat/booking metrics. |
| 30 | Month-1 review + case-study Loom (top-3 recovered calls, €-est.) | ADAPT | Keep the ritual (highest retention lever). "Recovered calls" → "top chats handled / after-hours leads captured / bookings won." |

### Surrounding sections

- **Pre-day-0 (webhook actions):** KEEP contract webhook + Mollie SEPA mandate. ADAPT slug
  generation (now the config filename / subdomain, still useful). ADAPT intake delivery (drop
  SMS). KEEP the Loom + kickoff scheduling. Attio record = optional/light.
- **The kickoff call:** KEEP the format; ADAPT the script — replace "dag 4 forwarding-instructies"
  with "we zetten de chat op je website en koppelen je Google Agenda." Add: collect website
  platform (WordPress/Wix/etc.) + who can edit the site + calendar-share.
- **Carrier-specific forwarding Loom library (KPN/Odido/GSM codes):** **DROP entirely.**
- **Why conditional forwarding (not porting):** **DROP entirely.**
- **Day 30 review call:** ADAPT metrics (as above); ritual KEEP.
- **Churn-prevention touchpoints:** ADAPT — daily stats SMS → text-first channel + text-first
  metrics; monthly Loom of "recovered calls" → recovered chats/after-hours leads. "Powered by
  Klantkraan" badge KEEP (even more natural — it lives next to a chat widget on the site).
- **What can go wrong table:** DROP the carrier-refuses-forwarding and tracking-number rows.
  DROP/ADAPT the Synthflow row → "widget says wrong thing → edit YAML, no redeploy of a voice
  agent." KEEP client-no-response, Mollie-fail, and (critically) the AI-Act-disclosure-refusal
  row unchanged — the disclosure is non-waivable and already enforced in the greeting.

**Also in the folder:** `synthflow-system-prompt.md` — voice legacy, out of scope for v1
(archive, don't maintain).

---

## 2. Friction map

### Top founder-time sinks (in the *current* playbook)
1. **Prompt fine-tune (30m) + 5 test calls (20m)** — survives as YAML edit + 5 test chats;
   roughly the same, still the biggest hands-on block.
2. **Day-30 Loom (45m)** — survives (retention gold), but pulling call stats becomes pulling
   chat stats; no audio to review, so likely *faster*.
3. **Kickoff (15m) + intake gap-fill (15m)** — survive.

### Hidden time sinks the current playbook does NOT budget for (new in text-first)
- **Getting the embed snippet onto a non-technical client's website.** The playbook assumed
  the client dials GSM codes themselves in 3 min. Pasting a `<script>` into WordPress/Wix/
  Squarespace (or emailing the client's web person) is the new equivalent friction — and the
  widget isn't even embeddable yet. This is the #1 unbudgeted risk to the ~2h target.
- **Connecting the client's Google Calendar.** OAuth consent / sharing a calendar with a
  service account is unfamiliar to trades owners and the integration is unbuilt.

### Top client-effort points
- **Current (to drop):** 32-field intake on a phone (10–14 min); dialing carrier forwarding
  codes; test calls.
- **Text-first (real):** (a) **installing the widget snippet on their own site** — the single
  biggest client-effort point, and the one most likely to stall go-live; (b) **sharing their
  Google Calendar**; (c) a shorter intake. Everything hinges on lowering (a): offer "stuur ons
  je inloggegevens / de contactgegevens van wie je site beheert en wij plaatsen het" as the
  default, with a self-serve guide as the fallback.

---

## 3. Proposed text-first onboarding sequence (signed → live)

Target unchanged: ≤ ~2h founder time. "Auto" = can be automated (n8n/webhook/script);
"Founder" = hands-on; "Client" = client action.

| Step | What | Owner | Founder min | Auto? |
|---|---|---|---|---|
| Sign | Contract signed (SignWell/PandaDoc webhook) → create client record, generate `slug`, fire Mollie SEPA mandate, send welcome e-mail + trimmed intake link + re-recorded 90s Loom | System | 0 | AUTO |
| Day 0–1 | Client fills **trimmed intake** (~12 fields, ~5 min): business + services/prices, hours, region, FAQ top-10, what-you-don't-do, spoed-definition, owner contact for lead handoff, website platform, Google account for calendar | Client | 0 | — |
| Day 1 | Founder reviews intake, fills gaps via WhatsApp | Founder | 15 | FOUNDER |
| Day 1 | `python -m app.scaffold "<Bedrijf>"` → generates `config/<slug>.yaml` | Founder | 2 | semi-AUTO |
| Day 1–2 | Founder edits the YAML: services+prices, hours, region, FAQ, spoed-rules, persona; verify greeting keeps the AI-Act disclosure | Founder | 25 | FOUNDER |
| Day 2 | **Kickoff call (15 min):** confirm intake, explain the 3 remaining steps (calendar share, widget install, test), set WhatsApp as support line | Founder | 15 | FOUNDER |
| Day 2 | **Client shares Google Calendar** with our service account (guided by a 1-page how-to) | Client | 0 | — |
| Day 2–3 | Founder connects that calendar to the receptionist (fill calendar id / creds; the `calendar_store.py` Google integration must exist first) | Founder | 10 | AUTO once built |
| Day 3 | Deploy the client's config to the live server (one config per client / route by slug) | Founder | 5 | AUTO |
| Day 3 | Founder runs **5 test chats** (spoed / nieuw_werk / spam / leverancier / bestaande_klant); confirm a booking lands in the real Google Calendar and the owner gets the lead notification | Founder | 20 | FOUNDER |
| Day 3–4 | **Widget install:** default = founder/we paste the embed snippet using access the client gave; fallback = client (or their web person) follows the per-CMS install guide | Founder | 15 | partial |
| Day 4 | **Client does 3 test chats** on their own live site; go/no-go via WhatsApp | Client | 0 | — |
| Day 4–5 | Any YAML tweaks from the transcripts | Founder | 10 | FOUNDER |
| Day 5 | **Go-live confirm:** snippet live, calendar connected, disclosure present, one booking round-trip verified. Go-live message to owner | Founder | 5 | AUTO msg |
| Day 5–19 | Light weekly summary (chats handled / after-hours leads / bookings) via WhatsApp or e-mail | System | 0 | AUTO |
| Day 14 | Check-in (5 min) | Founder | 5 | FOUNDER |
| Day 30 | Month-1 review + case-study capture (top chats / bookings won; anonymised case) | Founder | 45 | FOUNDER |

**Founder total to go-live (≈ day 5): ~112 min.** Full 30-day incl. review: ~177 min. The two
soft numbers are widget install (15m, could balloon on an awkward CMS) and the calendar
connection (10m, assumes the integration is built). Both are the items to de-risk first.

Timeline compresses from 30→~5 days to live because number-porting/forwarding lead time is gone.

---

## 4. Missing deliverables / artefacts to build

**Engineering (blockers — nothing goes live without these):**
1. **Embeddable widget** — a `<script>` snippet or iframe that drops a floating chat bubble on
   the client's site and points at our hosted `/chat` for their slug. Today only a standalone
   full-page `index.html` exists. Must be per-client (carry the client's config/slug) and
   CSP/cross-origin-safe.
2. **Google Calendar integration in `calendar_store.py`** — implement `availability()` and
   `book()` against the client's real Google Calendar (service account + shared calendar, or
   OAuth), keeping the existing signatures. This is the "swap the bodies" seam, still a stub.
3. **Multi-client hosting/routing** — a way to serve >1 client from the live server (route by
   slug/subdomain to the right config), since today `BUSINESS_CONFIG` = one config per process.
4. **Client-facing lead/booking notification** — route bookings + `take_message` leads to the
   *client* (their e-mail/WhatsApp), not just the founder's Telegram. `notify.owner()` currently
   targets one owner (the founder).

**Guides / content (non-technical clients, Dutch):**
5. **Widget-install guide** — per platform (WordPress, Wix, Squarespace, "email your webdev"),
   with the exact snippet and screenshots. This is the #1 friction point.
6. **Google-Calendar-share guide** — 1-page "deel je Google Agenda met ons" (or the OAuth
   consent flow), Dutch, screenshotted.
7. **Trimmed text-first intake form** (~12 fields). Drop from the current 32: current phone
   number, provider, line type (Q7–9), voice preference/AI name (Q32), and the CM.com/forwarding
   fields. Keep: business+KvK+address, services+prices, hours, region, spoed-definition, FAQ
   top-10, what-you-don't-do, may-quote-prices, owner contact for handoff. Add: **website
   platform** + **who can edit the site** + **Google account for calendar**.
8. **Re-recorded welcome sequence** — welcome e-mail + 90s Loom that describe the text-first
   path (calendar share → widget install → test → live), replacing the forwarding narrative in
   `sms-templates.md §8` and the day-0 Loom.
9. **Text-first go-live checklist** — snippet live on site, calendar connected + one booking
   round-trip verified, AI-Act disclosure visible in the greeting, owner lead-notification
   tested.

**Adapt, don't rebuild:**
10. **Dashboard/weekly summary** — re-spec `dashboard-spec.md` metrics from calls/recovered-calls/
    audio to chats/after-hours-leads/bookings; drop the audio-snippet + call-transcript UI. For
    client #1 a weekly WhatsApp/e-mail summary can stand in for the page.

**Keep as-is (already correct for text-first):** the config-driven scaffolder, the AI-Act
disclosure in the greeting, the Mollie/SEPA billing step, the kickoff + day-14 + day-30 rituals,
the "Powered by Klantkraan" badge, and the STOP/opt-out handling pattern (relevant if any
outbound messaging is kept).
