# Text-First Onboarding Playbook

> The delivery bible for the pivoted product: a Claude web-chat widget on the client's own
> site that qualifies leads and books into the client's own Google Calendar, hosted on our
> server. No voice, no call-forwarding, no CM.com for v1.
>
> **Target:** signed → live in ~5 days, **≤ ~2h founder time** (~112 min to go-live).
> **"Done" = first real lead handled by the receptionist — not "widget installed."**
>
> Supersedes the voice-era `onboarding-30-day.md` (deleted). Also makes stale, pending cleanup:
> `intake-form.md` (32-field Tally form — replaced by §3 below), `sms-templates.md` and
> `synthflow-system-prompt.md` (voice legacy). `churn-prevention.md` stays but read its
> metric/channel swaps against §7/§9 here.

---

## 0. Operating model — white-glove feel, self-serve back end

A €299–€499/mo ACV cannot afford human white-glove labour by the textbook. The resolution the
research lands on: **the client's experience is white-glove; the work is self-serve for us** —
templated, config-driven, near-zero marginal labour. The `config/<business>.yaml`-per-client
architecture *is* that economic trick; protect it. Every onboarding step that isn't "edit one
YAML + connect one calendar + place one snippet" is scope creep against the 2h budget.

The client never sees a config, a form builder, or a dashboard — they get a finished thing, not
a control panel. Reserve scarce live founder time for exactly **two moments**: the kickoff
(set the goal + connect the calendar) and the go-live aha (watch it book a real lead).
Everything else goes async.

---

## 1. The sequence, signed → live

"Auto" = script/webhook. "Founder" = hands-on. "Client" = client action. The single biggest
lever is **pre-building the receptionist before the client lifts a finger** — their first
experience is a finished demo of *their own* receptionist, not a blank setup.

| Step | What | Owner | Founder min | Auto? |
|---|---|---|---|---|
| Sign | Contract signed (SignWell/PandaDoc webhook) → create client record, generate `slug`, fire Mollie SEPA mandate, send welcome e-mail + re-recorded 90s Loom | System | 0 | AUTO |
| Pre-build | Scrape site + Google Maps → Claude drafts cited config (prices left as `PRIJS?`) → `scaffold --from-json` → stage a branded demo (§3) | Founder | 15 | semi-AUTO |
| Day 0–1 | Client **confirms the draft** by chatting with their own demo + a plain-Dutch one-pager, and supplies the only 4 human inputs: prices, spoed policy, where leads go, optional persona name (§3) | Client | 0 | — |
| Day 1 | Founder pastes prices/spoed/lead-destination into the YAML, fills any gaps via WhatsApp; verify greeting keeps the AI-Act disclosure | Founder | 25 | FOUNDER |
| Day 2 | **Kickoff (15 min, live or async):** set the one goal, **connect Google Calendar right there** (§4 — never homework), show their receptionist book a test lead | Founder | 15 | FOUNDER |
| Day 2–3 | Founder sets `calendar.provider: google` + calendar id in config; deploy the client config to the server (route by slug) | Founder | 10 | AUTO once built |
| Day 3 | **5 test chats** (spoed / nieuw_werk / spam / leverancier / bestaande_klant); confirm a booking lands in the real Google Calendar and the owner gets the lead notification | Founder | 20 | FOUNDER |
| Day 3–4 | **Widget install (§5):** default = we paste the snippet using access the client gave / a 2-min screen-share; fallback = per-CMS guide or hosted `<client>.klantkraan.nl` link | Founder | 15 | partial |
| Day 4 | Client does **3 test chats** on their own live surface; go/no-go via WhatsApp | Client | 0 | — |
| Day 4–5 | Any YAML tweaks from the transcripts | Founder | 7 | FOUNDER |
| Day 5 | **Go-live confirm (§10):** snippet/link live, calendar connected, disclosure present, one booking round-trip verified | Founder | 5 | AUTO msg |
| Day 5–19 | Light **weekly** summary (chats handled / after-hours leads / bookings) via WhatsApp or e-mail | System | 0 | AUTO |
| Day 14 | Check-in (5 min) | Founder | 5 | FOUNDER |
| Day 30 | Month-1 review + case-study capture (top chats / bookings won; anonymised case) | Founder | 45 | FOUNDER |

**Founder total to go-live (~day 5): ~112 min.** Full 30-day incl. review: ~157 min. The two
soft numbers are widget install (15m, can balloon on an awkward CMS) and the calendar connection
(assumes §4 built + a real service account). Timeline compresses from 30→~5 days because
number-porting/forwarding lead time is gone.

---

## 2. Intake — scrape-first, confirm-in-chat

**Do-it-for-them beats any form.** Confirming a pre-filled draft is an order of magnitude less
friction than filling a blank one — and a busy loodgieter will abandon a 32-field form.

**The Minimum Viable Intake = one confirmation + four questions.** Everything else is scraped or
a safe Dutch-trade default:

1. **Confirm the draft** — "Klopt dit?" over auto-filled name / phone / region / hours / services (tap-level).
2. **Prices** — starttarief per service + voorrijkosten (or "gratis offerte"). *The single unavoidable input.*
3. **Spoed policy** — do you take emergencies? surcharge / after-hours? (yes/no + optional number).
4. **Where do leads/afspraken go?** — WhatsApp number / e-mail, and which agenda to book into.
5. *(optional)* **Persona name** — keep "Fleur" or pick another.

If the client answers nothing, the scraped draft + defaults still produce a working, *safe* demo
(it just quotes no prices — the guardrail already defers those to the monteur).

**How the draft is built (report: intake §3):**
- Auto-fill from **Google Maps Place Details** (name, phone, `regularOpeningHours`, `primaryType`,
  `pureServiceAreaBusiness` → region) + site text (`/diensten`, `/tarieven`, `/contact`).
- Claude emits a **cited extraction JSON** — every field carries value + source + confidence +
  verbatim snippet. Rules baked in: **never invent a price** (emit literal `PRIJS?`);
  citation-or-blank for services/hours; classify services against a controlled Dutch-trade
  vocabulary (spoedservice, cv-ketel onderhoud, lekkage-reparatie, inspectie/offerte,
  dakinspectie…); leave spoed policy / booking rules / lead-destination blank.
- Merge cited values over `scaffold.py`'s template; `greeting`, `persona.guardrails`, and the
  AI-Act disclosure stay template-owned (locked, never touched by extraction).

**Confirm in chat, never in YAML.** Boot the draft config, send the client their branded demo
link + one WhatsApp line: *"Ik heb alvast een digitale receptionist voor [bedrijf] gebouwd —
praat er even mee. Klopt alles? Wat mag anders?"* Attach a plain-Dutch one-pager (name, hours
grid, service+price table with `PRIJS?` rows highlighted, region, spoed line) so they can correct
in one message. The founder pastes prices + spoed + lead-destination, redeploys, done.

**Fallback:** a **3-field** Tally form (prices / spoed / lead-destination) for prospects with no
website or thin Maps data. Never the 32-field form.

**Dutch-trade defaults (so we don't ask):** hours ma–vr 08:00–18:00 / za 09:00–13:00; tz
`Europe/Amsterdam`; region "`<Stad>` en omgeving"; 60-min jobs (30 for offerte/inspectie); 60-min
slots, 14-day horizon; persona "Fleur", rustig/vriendelijk. Price-shape hints shown next to
`PRIJS?` (spoed ~€90–130, voorrijkosten ~€20–40, cv-onderhoud ~€120–150, offerte gratis) prime
the client to answer fast — they still supply the real number.

---

## 3. Calendar connection — service account + client shares their calendar

The lowest-friction path on both sides. We create **one** Google Cloud service account, ever.
For each client, a ~60-second in-Calendar share — no Google Cloud login, no OAuth consent screen,
no token refresh, no verification gauntlet.

**Works for consumer @gmail.com with NO domain-wide delegation** — a consumer account has no
domain, DWD isn't available or needed; the service account is just another writer on the
calendar's ACL. The one gotcha (adding guests → `forbiddenForServiceAccounts`) we sidestep:
`book()` **never sets `attendees`** — the customer's name/phone/service go in the event
title/description; they already got their confirmation in the chat thread.

**What the client does (send verbatim, Dutch; desktop-only — the share UI isn't on mobile):**
1. Open **calendar.google.com** op je computer, log in met je normale Google-account.
2. Onder "Mijn agenda's" → hover over je agenda → drie puntjes (⋮) → **"Instellingen en delen"**.
3. Scroll naar **"Delen met specifieke personen of groepen"** → **"Personen en groepen toevoegen"**.
4. Plak dit e-mailadres exact: *(onze service-account e-mail)*.
5. Kies bij rechten **"Wijzigingen aan afspraken aanbrengen"** — **niet** "alleen vrij/bezet", **niet** "alle afspraakgegevens". *(The #1 client mistake — bold it.)*
6. Klik **"Verzenden"**. Klaar — niets te installeren, geen wachtwoord te delen.

Access is live the instant they click Send (a service account can't "accept an invite"). The
calendar id = their Gmail address (primary calendar); we paste it into their config.

**In code (`calendar_store.py`, signatures unchanged):** `availability()` → `freebusy().query()`
minus config-generated opening-hours slots; `book()` → `events().insert()` with
`start/end.timeZone = Europe/Amsterdam`, **no `attendees`**. Add a per-client startup health check
(cheap `events.list`) that alerts us via `notify.owner` if a client downgrades/removes the share
before a customer hits it.

**Status:** the Google provider is **built** (commit a980e30, `calendar.provider: sim|google`),
verified offline only. Gate: founder creates the service account
(`ai-receptionist/docs/GOOGLE-CALENDAR.md`) → real `selftest calendar-google` → redeploy.

---

## 4. Widget install — keep the chat on our origin

The widget talks to our API with **relative URLs**, so served from our origin it has **zero CORS
problem and no exposed API key**. That decides the architecture: the chat always runs on our
origin, fronted to the client's visitors as an iframe or a hosted page. Never let widget JS run
on the client's own page calling `/chat` cross-origin (that forces CORS + a page-visible key).

- **Default:** a one-line `<script>` that injects a floating bubble → opens an `<iframe>` to the
  client's hosted widget URL. Paste into the platform's header/footer: **WPCode footer**
  (WordPress), **Custom Code → all pages** (Wix, needs Premium), **Code Injection footer**
  (Squarespace). **Google Sites** sandboxes scripts → use **Insert → Embed** with an iframe or the
  plain URL instead.
- **Universal fallback (client can't edit the site):** we host `https://<client>.klantkraan.nl`
  (our `index.html` + their config). They link/button to it from Google Business Profile,
  Instagram/Facebook bio, WhatsApp greeting, e-mail signature, or a QR code on the van. **Fully
  functional, not a degraded mode** — just no floating bubble on their domain. Many trades get
  more traffic from their Google Business Profile than their own site anyway.

**Do it for them.** Getting a `<script>` onto a non-technical owner's site is the #1 unbudgeted
friction and the #1 place trades ghost. Default to "stuur ons de toegang / de contactgegevens van
wie je site beheert en wij plaatsen het," with the per-CMS guide as fallback. Server note: don't
send `X-Frame-Options: DENY` on the widget route; if you set CSP, allow the client's domain via
`frame-ancestors`.

**Status:** the embeddable widget is **not built yet** — today only a standalone full-page
`web/index.html` exists. This is roadmap step 2 (see §12).

---

## 5. Welcome & expectations — async-first, on WhatsApp

Trades live on WhatsApp; the product already has a WhatsApp channel. A short human welcome within
24–48h makes non-technical clients feel supported and is one of the strongest early-churn levers.
Keep synchronous time for goal-alignment only; push info to async video, reused across clients.

1. **Kickoff (live, ~15 min, or async if they prefer):** one goal ("meer afspraken uit je website,
   ook 's avonds"), do the calendar share *right there*, show *their* receptionist book a test lead.
2. **Welcome Loom (async, ≤2 min, reusable):** "dit is je digitale receptioniste, zo werkt het, zo
   pas je iets aan, zo bereik je mij." Record once; optional 30-sec personalised top.
3. **Go-live confirmation (async):** "Je bent live. De eerste keer dat een klant 's avonds boekt,
   krijg je een seintje." Primes the aha so they notice it.

**Set 3 expectations explicitly (confusion = churn):** (a) it's a digital assistant that discloses
itself (EU AI Act art. 50 — already mandated in the greeting; tell them so they're not surprised);
(b) what it does/doesn't — books & qualifies, hands genuine edge cases to them, never invents
prices or times; (c) how to reach a human — you, WhatsApp, same-day.

---

## 6. Anti-stall / anti-ghost

The two Klantkraan-specific stalls, and how to remove the client's technical burden entirely:

- **Won't connect the calendar** → do the share live on the kickoff, never leave it as homework.
- **Won't install the widget** → we paste the snippet for them (§4).
- **Ghosts the test feedback** → **default to go-live**: *"we gaan maandag live tenzij je iets wilt
  aanpassen."* Silence becomes consent-to-launch, not a blocker.
- **Instrument the ghost signal:** if a client hasn't opened the kickoff link / connected the
  calendar within 48h, fire a warm WhatsApp nudge — don't wait for revenue to dip. Track a simple
  per-client CLI status: `staged → calendar-connected → live → first-lead-handled`.
- **Be the "who to call."** One named human on WhatsApp answering same-day *is* the trades adoption
  strategy — make that promise explicit in the welcome.

---

## 7. Metrics that matter (dashboard-free — per client, CLI/CSV)

Don't over-instrument as a solo founder; go concierge. Track exactly these:

| Metric | Klantkraan definition | Target |
|---|---|---|
| Time-to-first-value | Signup → first real customer conversation handled | **Same day** |
| Activation | First real appointment booked into the client's calendar by the AI | **Within 7 days** — *the* number |
| Onboarding completion | Calendar connected + widget/link live + test lead booked | **Within 48–72h of kickoff** |
| Retention proxy | Still live + ≥1 lead handled in the last 7 days (D7/D30) | Watch D30 as the churn tripwire |
| Founder-time-per-client | Actual hours signup → go-live | **≤2h** (the DFY math breaks if it creeps) |

**Leading indicator unique to us: the first "'s avonds/weekend afspraak."** The after-hours
booking is emotional proof the client couldn't have captured that lead themselves — flag it and
celebrate it back ("Je receptioniste boekte gisteren om 21:40 een afspraak"). For client #1, read
the actual transcripts: every fumble is a config-tuning item *and* a better default for every
future client.

---

## 8. Churn prevention (text-first swaps)

`churn-prevention.md` stays for the channel-agnostic parts (signals table, off-boarding, win-back,
saved-churn math). Apply these swaps:

- Daily stats **SMS** → **weekly** value summary via **WhatsApp/e-mail** (chats handled /
  after-hours leads / bookings won). Consider weekly-only until volume justifies more.
- "Top-3 **recovered calls**" Loom → "top chats handled / after-hours leads captured / bookings
  won." Still the highest-leverage retention artefact.
- "Powered by Klantkraan" badge KEEP — even more natural next to a chat widget on the site.
- Day-45 case-study capture KEEP (binds the client emotionally + feeds marketing).

---

## 9. Go-live checklist

- [ ] Snippet or hosted link live on the client's surface
- [ ] Calendar connected + **one booking round-trip verified** in the real Google Calendar
- [ ] AI Act art. 50 disclosure visible in the greeting
- [ ] Owner lead-notification tested (both a booking and a `take_message` lead)
- [ ] Weekly summary scheduled
- [ ] Tracking the real "done": first real lead handled

---

## 10. What can go wrong

| Risk | Recovery |
|---|---|
| Widget won't install on an awkward CMS | Hand out the hosted `<client>.klantkraan.nl` link + GBP/socials/QR — fully functional |
| Calendar share set to wrong permission | Bold rule: must be **"Wijzigingen aan afspraken aanbrengen"** (writer); "vrij/bezet" or "reader" → booking 403s |
| Workspace admin blocks external full-share | Admin allows our SA email, or client shares a dedicated calendar they own |
| Widget says the wrong thing | Edit the YAML, redeploy — no voice agent to re-clone |
| Client doesn't return test feedback | Default to go-live on conservative settings; WhatsApp nudge first |
| Mollie mandate fails | Manual Moneybird invoice with iDEAL link; flag for risk-review |
| Client wants to disable the AI-Act disclosure | Refuse in writing; non-waivable (`04-legal/ai-act-disclosure.md`) |

---

## 11. Engineering prerequisites & status

The gap between "signed" and "live on the client's site booking into their calendar":

1. **Google Calendar provider** — **DONE** (a980e30); pending founder's real service account + `selftest calendar-google`.
2. **Embeddable widget** (`<script>` bubble → iframe to hosted URL, per-client, CSP-safe) — **not built** (roadmap step 2).
3. **Multi-client routing** (serve >1 client from one box by slug/subdomain; today `BUSINESS_CONFIG` = one config per process) — **not built** (roadmap step 3).
4. **Client-facing lead/booking notification** — `notify.owner()` targets the founder's Telegram only; needs a per-client destination (WhatsApp/e-mail).
5. **Scrape→draft pipeline** (`app/extract.py` + `scaffold.py --from-json` + a `selftest intake` that asserts no price is ever written without human input) — **not built**.

---

## Sources

Synthesised from the 2026-07-13 onboarding deep-dive (internal audit · best-practices · technical
integration · intake minimisation). Google Calendar sharing/ACL:
https://developers.google.com/workspace/calendar/api/concepts/sharing · Places Data Fields:
https://developers.google.com/maps/documentation/places/web-service/data-fields · TTV / activation
benchmarks (Chameleon, Userpilot, Message Valley) and white-glove-vs-self-serve economics
(PulseRevOps, Command AI) as cited in the research reports.
