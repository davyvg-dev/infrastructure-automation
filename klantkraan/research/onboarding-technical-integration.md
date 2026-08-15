# Onboarding research — smoothest technical path for the two client integrations

Scope: (A) let Klantkraan read availability from and write bookings to the CLIENT'S OWN Google
Calendar, and (B) get the chat widget onto the client's existing site. Optimised for LEAST client
effort and LEAST founder time, for a non-technical tradesperson (plumber/roofer/installer), solo-founder DFY.

Our stack (verified in repo):

- `ai-receptionist/app/calendar_store.py` — the integration seam. Two functions, `availability(on_date, days)`
  and `book(customer_name, contact, service, slot)`. CLAUDE.md rule: _swap the bodies, keep the signatures._
  Timezone already sourced from config (`business.timezone`, default `Europe/Amsterdam`). This is exactly
  where a Google Calendar client plugs in.
- `ai-receptionist/app/server.py` — FastAPI. `POST /chat` (optional `CHAT_API_KEY` via `x-api-key` header,
  per-IP sliding-window rate limit, default 20/min). **No CORS middleware is installed.** `GET /config`
  feeds the widget its business name + greeting.
- `ai-receptionist/web/index.html` — the widget today is a **full-page, same-origin** app: it does
  `fetch('/config')` and `fetch('/chat')` with **relative** URLs. Served from our origin it needs zero CORS.

---

## PART A — Google Calendar access for a non-technical client

### Recommendation (least friction): Service account + client shares their calendar with it

We create ONE Google Cloud service account (once, ever). For each client, the client does a ~60-second,
in-app calendar share: "Settings and sharing" → add the service account's email → "Make changes to events".
No Google Cloud login for the client, no OAuth consent screen, no billing, no token refresh to maintain,
no Google verification/review process. This is the lowest-friction path on both sides.

### The three approaches compared

|                                                  | (i) Service account + client shares calendar **[RECOMMENDED]**                                                                             | (ii) OAuth 2.0 click-through consent                                                                                                               | (iii) Client makes a new dedicated calendar for us                                                                             |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| Client effort                                    | Share one calendar, pick "Make changes to events". ~1 min, all inside Google Calendar they already use.                                    | Click a Google consent screen; must trust our app; sees scary "unverified app" warning until we pass Google's OAuth verification.                  | Same share step as (i) **plus** first create a new calendar. More steps, more confusion.                                       |
| Founder effort                                   | One-time: create project, enable API, make service account, download JSON key. Then per client: paste their calendar ID into their config. | One-time: build OAuth flow, consent screen, **submit for Google verification** (weeks, sensitive scope review), store + refresh per-client tokens. | Same as (i).                                                                                                                   |
| Ongoing maintenance                              | None. Service-account key doesn't expire.                                                                                                  | Refresh tokens can be revoked (password change, 6-month inactivity, security events) → re-consent.                                                 | None.                                                                                                                          |
| Works for personal @gmail.com?                   | **Yes** (see authoritative answer below).                                                                                                  | Yes.                                                                                                                                               | Yes.                                                                                                                           |
| Reads/writes the client's real working calendar? | Yes — their existing calendar, no data migration.                                                                                          | Yes.                                                                                                                                               | No — a _separate_ calendar; if the client keeps booking jobs into their normal calendar, we can't see it. Defeats the purpose. |
| Verdict                                          | **Winner.** Least effort, no verification gauntlet, no token upkeep.                                                                       | Overkill; verification + token refresh is a lot of founder time for a solo DFY.                                                                    | Only as a privacy option (see below), not the default.                                                                         |

**When (iii) is still useful:** as a _variant_ of (i), not a replacement. If a client is squeamish about us
seeing personal appointments, have them create one calendar named e.g. "Klantkraan afspraken", keep their
jobs there, and share _that_ one with the service account. Same service-account mechanism, narrower data
exposure. Only recommend if the client raises privacy — otherwise it adds a step and risks the "invisible
second calendar" failure mode.

### Authoritative answer: does simple sharing with a service account (NO domain-wide delegation) work for a consumer Gmail user?

**Yes — for reading availability and creating/editing events on the shared calendar, simple ACL sharing is
sufficient and domain-wide delegation (DWD) is NOT required.** DWD only exists to impersonate users inside a
Google Workspace _domain_; a consumer @gmail.com account has no domain and no admin console, so DWD is not
even available to it — and it isn't needed. The service account is just another grantee on the calendar's
access-control list (ACL). Grant it the **writer** role ("Make changes to events") and it can list, insert,
update and delete events on that calendar via the API. This is confirmed by Google's own Calendar API
sharing concepts (writer = "read and write events on the calendar") and consistently by Google Calendar
Community answers ("share the actual user calendar with the service account… then provide the calendar ID in
the call to list/update/delete/insert events").

Sources:

- Google — Calendar sharing / ACL roles: https://developers.google.com/workspace/calendar/api/concepts/sharing
- Google Calendar Community — sharing a calendar with a service-account email to insert/update events:
  https://groups.google.com/g/google-calendar-api/c/MySzyAXq12Q
- Google Calendar Help — "Choose what others can do with your calendar" (the four permission levels):
  https://support.google.com/calendar/answer/15716974

### The ONE real gotcha: adding guests/attendees needs DWD (we sidestep it)

A service account **cannot add attendees / send guest invitations** on a consumer calendar without DWD — the
API returns **`forbiddenForServiceAccounts`**. This is the single most-reported service-account calendar
error.

**Why it does not affect us:** our booking doesn't need to invite the _customer_ as a Google Calendar guest.
We create the event ON THE PLUMBER'S calendar with the customer's name/phone/service in the event **title and
description** (e.g. summary "Klantkraan: Lekkage — Jan de Vries 06-12345678"). No `attendees[]` array → no
invitation logic → no `forbiddenForServiceAccounts`. The customer already got their confirmation through the
chat/WhatsApp thread; the plumber gets the job in their calendar. Rule for our `book()` implementation:
**never populate the `attendees` field** unless/until we move a client to Workspace + DWD.

Sources:

- Google issue tracker — service accounts can't invite attendees without DWD: https://issuetracker.google.com/issues/408598694
- Community write-up of `forbiddenForServiceAccounts` + DWD fix: https://www.technetexperts.com/service-account-dwd-calendar-attendees/

### Exact steps — what WE do ONCE (founder, ~15 min, one time ever)

Do this in the Google Cloud Console. Prefer the gcloud CLI where noted (per memory: founder prefers CLI over
dashboards), but the API-enable + service-account steps are simplest in the console the first time.

1. Create (or reuse) a Google Cloud project — e.g. "klantkraan-calendar". No billing account is required for
   Calendar API usage within the free quota.
2. **Enable the Google Calendar API** for that project: APIs & Services → Library → search "Google Calendar
   API" → Enable. (CLI: `gcloud services enable calendar-json.googleapis.com --project=klantkraan-calendar`.)
3. **Create a service account**: IAM & Admin → Service Accounts → Create. Name e.g. "klantkraan-agenda".
   No project IAM roles needed (calendar access comes from the per-calendar share, not IAM).
   (CLI: `gcloud iam service-accounts create klantkraan-agenda --project=klantkraan-calendar`.)
4. **Create a JSON key** for it: the service account → Keys → Add key → Create new key → JSON → download.
   Store it as a secret on our VPS (never in git; add path to `.env`, e.g. `GOOGLE_CALENDAR_KEY_FILE=...`).
5. **Copy the service account's email** — it looks like
   `klantkraan-agenda@klantkraan-calendar.iam.gserviceaccount.com`. This is the address every client shares
   their calendar with. Keep it handy; it goes in the client onboarding message.
6. Do **NOT** configure domain-wide delegation. Not needed, and not possible for consumer Gmail clients.

One service account serves ALL clients — each client just shares their own calendar with the same email.

### Exact steps — what the CLIENT does (plain-language, plumber-proof)

Send this verbatim (Dutch in production; English here). It's all inside the Google Calendar they already use
on a computer — the share UI is desktop-only, so tell them "op de computer, niet de telefoon".

1. Open Google Agenda on your computer: go to calendar.google.com and log in with your normal Google/Gmail
   account.
2. On the left, under "Mijn agenda's" ("My calendars"), hover over your own name/calendar. Click the three
   dots (⋮) that appear → **"Instellingen en delen"** ("Settings and sharing").
3. Scroll to **"Delen met specifieke personen of groepen"** ("Share with specific people or groups").
   Click **"Personen en groepen toevoegen"** ("Add people and groups").
4. Paste this email exactly: `klantkraan-agenda@klantkraan-calendar.iam.gserviceaccount.com`
   (we send them the real address).
5. In the permission dropdown, choose **"Wijzigingen aan afspraken aanbrengen"**
   ("Make changes to events"). Not "See only free/busy", not "See all event details".
6. Click **"Verzenden"** ("Send"). Done — nothing else to install, no password to give us.

Then the client sends us nothing except a confirmation they did it — **their calendar ID is simply their
Gmail address** (a primary calendar's ID = the account email). We already know it, or ask once. For a
dedicated/secondary calendar the ID is shown on that same Settings page under "Agenda-id integreren"
("Integrate calendar" → Calendar ID). We paste that ID into their `config/<business>.yaml`.

Note: because the grantee is a service account (not a human), there's no "click the link in the invite email"
step — the service account can't read email. Access is live the moment they click Send. (A human grantee
would need to accept; a service account does not.)

### How it lands in our code

In `calendar_store.py`, keep `availability()` and `book()` signatures; swap the bodies:

- `availability()` → call `service.freebusy().query()` (scope `calendar.readonly` or `calendar`) or
  `events().list(timeMin,timeMax,singleEvents=True,orderBy='startTime')` on the client's calendar ID, then
  subtract busy blocks from the config-generated opening-hours slots (logic we already have).
- `book()` → `events().insert(calendarId=<client id>, body={summary, description, start, end})`. Set
  `start.timeZone` / `end.timeZone` to `Europe/Amsterdam` (from config) and send RFC3339 datetimes. **Do not
  set `attendees`.** Keep the local JSON write as a mirror/audit if wanted.
- Auth: `google.oauth2.service_account.Credentials.from_service_account_file(key, scopes=['.../auth/calendar'])`.
  The `calendar` scope covers both read and event write on shared calendars. (Fetch exact client-library
  syntax via context7 at implementation time per CLAUDE.md.)

### Failure modes to watch

- **Personal @gmail.com vs Google Workspace:** Both work with simple sharing. Workspace admins can _restrict_
  external sharing to free/busy-only at the domain level — if a Workspace client's share silently downgrades
  to free/busy, we can read availability but `insert` will 403. Fix: their admin allows full sharing, or use
  a dedicated calendar they own. Consumer Gmail has no such restriction.
- **Wrong permission level:** "See only free/busy" → we can't read event details or write (booking fails).
  "See all event details" (reader) → we can read availability but **cannot** create bookings (insert 403).
  Must be **writer / "Make changes to events"**. This is the #1 client mistake — put it in bold in the guide.
- **Attendees:** `forbiddenForServiceAccounts` if we ever add guests without DWD. Our `book()` must not set
  `attendees`. (Covered above.)
- **free/busy vs full read:** `freebusy.query` returns only busy intervals (fast, privacy-friendly) — good
  for `availability()`. It does NOT return event details or let you write. Writing still needs the `events`
  endpoint + writer role. Use freebusy for reads, events.insert for writes.
- **Timezone:** always send `timeZone: "Europe/Amsterdam"` on event start/end and on freebusy queries; never
  rely on UTC defaulting. DST shifts (CET/CEST) are handled by Google if you pass the named zone, not a fixed
  offset. Our config already carries `Europe/Amsterdam`.
- **CalendarList quirk:** sharing no longer auto-adds the calendar to the grantee's CalendarList — irrelevant
  to us because we address the calendar by ID via the API, not through a UI list.
- **Rate limits / quota:** default Calendar API quota is ~1,000,000 queries/day per project and a per-minute
  per-user cap; a `403 User Rate Limit Exceeded` means back off. At our scale (a handful of clients, a few
  reads/writes per booking) we're nowhere near it. Best practice: exponential backoff on 403/429, and pass a
  distinct `quotaUser` per client so one busy client can't starve others. This only matters at scale.
- **Client revokes/changes the share:** if they remove the service account or downgrade permission, calls
  start 403-ing. Add a startup/health check that does a cheap `events.list` per client and alerts us
  (Telegram via `notify.owner`) so we catch a broken share before a customer does.

---

## PART B — Getting the chat widget onto the client's site

### Key insight from our own code

The widget (`web/index.html`) is a **full-page app that talks to our API with relative URLs**. Served from
our own origin, it has **zero CORS problem and no exposed cross-origin API key**. That single fact decides
the architecture: keep the chat running ON OUR ORIGIN and put it in front of the client's visitors either as
(a) an iframe injected by a one-line script, or (b) a plain hosted page they link to. Both keep `/chat`
same-origin. We should **avoid** the option where widget JS runs on the client's own page and calls our
`/chat` cross-origin — that would force us to add CORS middleware and ship an API key that's visible in the
client's page source.

### Embedding options compared

| Option                                                                                          | UX                                                                                     | CORS?                                                                                                                                          | Effort to install                                 | Best for                                                                                       |
| ----------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| **One-line `<script>` that injects a floating bubble → opens an `<iframe>` to our hosted page** | Floating "Chat" bubble bottom-right, expands to our widget in an iframe. Feels native. | **None** — iframe content is served from _our_ origin, so its `fetch('/chat')` is same-origin. Embedding an iframe cross-domain needs no CORS. | Paste one line into a "custom code / header" box. | **Recommended default** for sites the client (or we) can edit.                                 |
| **Raw `<iframe>` embed** (client pastes an `<iframe src>`)                                      | Inline box wherever they place it; no floating bubble unless they style it.            | None (same as above).                                                                                                                          | Paste an iframe tag; may need sizing tweaks.      | Page-builders whose "embed" only accepts an iframe/HTML block (Google Sites, some Wix blocks). |
| **Full-page hosted link** (`chat.klantkraan.nl/<client>` or `<client>.klantkraan.nl`)           | Separate page/tab; a button/menu link "Plan een afspraak" points to it.                | None.                                                                                                                                          | Add one hyperlink/button. Lowest possible skill.  | **Universal fallback** — works even when the client can't add ANY code, and on mobile.         |

Recommendation: **ship the one-line script (iframe-injection floating bubble) as the primary**, and **always
also give them the full-page hosted link** as the no-code fallback. The script tag is a thin loader we host
(e.g. `https://cdn.klantkraan.nl/widget.js`) that creates a bubble button + an iframe pointing at the client's
hosted widget URL. Because everything network-facing lives on our origin, we change zero server config.

### Per-platform install steps (common cases)

The script goes in the site's global header/footer so the bubble shows on every page. Menu names below are
current as of 2026.

- **WordPress**
  - Easiest, no plugin: Appearance → Editor (or Customize) may not expose head. Reliable path: install the
    free **WPCode** plugin → Code Snippets → Header & Footer → paste our line into **Footer** → Save. Shows
    site-wide.
  - Classic alternative: Appearance → Widgets → add a **Custom HTML** block to the Footer.
- **Wix**
  - Requires a **Premium plan** for custom code. Settings → **Custom Code** (under "Advanced" / "Developer
    Tools") → **+ Add Custom Code** → paste our line → set "Add Code to Pages: All pages" → place in **Body -
    end** (or Head) → Apply.
- **Squarespace**
  - **Settings → Advanced → Code Injection** → paste our line into the **Footer** box → Save. (Business plan
    or higher for Code Injection.) Site-wide automatically.
- **Google Sites (new)**
  - Google Sites does **not** run arbitrary site-wide script tags — it sandboxes embeds in an iframe. Use the
    **Insert → Embed** panel: choose **"Embed code"** and paste an **`<iframe>`** pointing at the client's
    hosted widget URL, OR choose **"By URL"** and paste the full-page hosted link. The floating-bubble script
    won't behave here; give Google Sites clients the **iframe or the link**. Place it on the contact/home
    section.
- **A site built by someone else / "I can't edit it"** → see fallback below.

### Fallback when the client CANNOT edit their site

This is the common tradesperson case (site built years ago by a nephew/agency, no login). Do **not** chase
their web host. Instead:

1. **Host a standalone booking page on a subdomain WE control** — e.g. `https://<clientnaam>.klantkraan.nl`
   or `https://chat.klantkraan.nl/<client>`. It's literally our existing `web/index.html` served with that
   client's config. Zero client effort, zero CORS, we own the whole stack.
2. Give the client a **link + button** to place wherever they _can_ reach: their Google Business Profile
   ("Afspraak maken"/website link), Instagram/Facebook bio, WhatsApp Business greeting, email signature,
   footer of quotes/invoices, a QR code on the van or a flyer. Many trades get more traffic from Google
   Business Profile than their own site anyway — the link works everywhere.
3. If they later get someone to touch the site, upgrade them to the one-line script for the floating bubble.

Because the hosted page is same-origin to our API, this fallback is not a degraded mode — it's fully
functional, just without the floating bubble on their domain.

### CORS, cross-origin, API key, rate limits — concrete notes

- **CORS:** With the recommended iframe/hosted-page architecture, the browser's request to `/chat` originates
  from our own domain → **same-origin → no CORS headers needed**, and our current `server.py` (which has no
  `CORSMiddleware`) works as-is. Only if we ever let widget JS run on the _client's_ domain and call `/chat`
  directly would we need CORS — and then we must set `Access-Control-Allow-Origin` to a **specific allowlist
  of client domains** (never `*` if we also send credentials/the API key). Avoid that path; the iframe keeps
  it simple and more secure.
- **API key:** `server.py` supports an optional `CHAT_API_KEY` via the `x-api-key` header. In any
  browser-delivered widget the key is visible in page/iframe source, so treat it as a **coarse gate, not a
  secret** — it stops trivial scripted hits, not a determined actor. The real abuse control is the built-in
  **per-IP rate limit** (`CHAT_RATE_LIMIT_PER_MINUTE`, default 20/min; every `/chat` call is a paid Claude
  request, so this is the token-cost guard). Keep the server behind Caddy/nginx so the real client IP arrives
  via `X-Forwarded-For` (the code already reads it) — bare-exposed, the IP is spoofable and the limit is weak.
- **Per-tenant isolation:** serve each client from a distinct hosted URL/subdomain (which already selects
  their `BUSINESS_CONFIG`). That gives per-client identification for rate-limiting, logging, and killing a
  single client's widget without touching others — no code change, just routing/config.
- **Framing headers:** for the iframe to load on the client's page, do **not** send `X-Frame-Options: DENY`
  on the widget page. If you set a `Content-Security-Policy`, use `frame-ancestors` to allow the client's
  domain(s) (or leave it permissive for the widget route). This is the one server-side thing to verify before
  handing out the script.

---

## Least-friction recommended path (the answer)

**Part A — Calendar:** One shared Google Cloud **service account**. We create it once (enable Calendar API,
make the service account, download the JSON key, note its email). Each client does a ~1-minute, in-Calendar
share: Settings and sharing → add our service-account email → **"Make changes to events"** → Send. We paste
their calendar ID (= their Gmail address) into their config and swap the bodies of `availability()`/`book()`
to call the Calendar API — **without** an `attendees` field. Simple sharing works for consumer @gmail.com with
**no domain-wide delegation**; DWD is only needed to invite guests, which we don't do.

**Part B — Widget:** Keep the chat on OUR origin. **Default:** a one-line `<script>` that injects a floating
bubble opening an **iframe to the client's hosted widget URL** — same-origin API, so **no CORS and no exposed
key**. Paste it into the platform's header/footer code box (WPCode footer on WordPress, Custom Code on Wix,
Code Injection footer on Squarespace). **Google Sites:** paste an iframe/URL embed instead. **Universal
fallback (can't edit the site):** we host `https://<client>.klantkraan.nl` and they just link/button to it
from Google Business Profile, socials, WhatsApp, email signature, or a QR code — fully functional, no client
code at all.

## Fallback decision trees

**Calendar (A):**

1. Consumer @gmail.com? → Service account + share "Make changes to events". Done. (Default, ~all trades.)
2. Google Workspace + admin blocks external full-share? → their admin allows full sharing for our SA email,
   OR client makes a dedicated calendar they own and shares that.
3. Client privacy-wary about us seeing personal appointments? → dedicated "Klantkraan afspraken" calendar,
   same service-account share.
4. Later need to send the customer a Google invite (attendees)? → only then move that client to Workspace +
   domain-wide delegation. Not needed for the standard booking flow.

**Widget (B):**

1. Client can edit their site AND platform allows script? (WordPress/Wix/Squarespace) → one-line script,
   floating bubble.
2. Platform is script-restricted/iframe-only? (Google Sites, some builders) → iframe or full-page URL embed.
3. Client can't edit the site at all? → we host `<client>.klantkraan.nl`; they add a link/button/QR from
   Google Business Profile, socials, WhatsApp, email signature.
4. No website at all? → same hosted page is their booking page; link from Google Business Profile + socials.

## Sources

- Google — Calendar API sharing / ACL roles: https://developers.google.com/workspace/calendar/api/concepts/sharing
- Google — freeBusy.query reference: https://developers.google.com/workspace/calendar/api/v3/reference/freebusy/query
- Google — Calendar API errors (403 rate limit, quotaUser, backoff): https://developers.google.com/workspace/calendar/api/guides/errors
- Google Calendar Help — Share your calendar (UI steps): https://support.google.com/calendar/answer/37082
- Google Calendar Help — Permission levels: https://support.google.com/calendar/answer/15716974
- Google Calendar Community — share calendar with service-account email to insert/update events: https://groups.google.com/g/google-calendar-api/c/MySzyAXq12Q
- Google issue tracker — service accounts can't invite attendees without DWD: https://issuetracker.google.com/issues/408598694
- forbiddenForServiceAccounts + DWD explainer: https://www.technetexperts.com/service-account-dwd-calendar-attendees/
- Google Sites — embed HTML/JS is iframe-sandboxed: https://sites.google.com/view/how-to-with-new-sites/embeds/embed-with-htmljavascript
- CORS API-security best practice (never `*` with credentials; rate-limit regardless): https://www.wisp.blog/blog/cors-api-security-guide
