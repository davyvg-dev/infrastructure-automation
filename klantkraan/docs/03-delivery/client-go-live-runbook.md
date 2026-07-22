# Client go-live runbook — the hands-on steps

The keystroke-level technical how-to for taking a signed client from a config file to a live
receptionist: the website embed, WhatsApp, the phone-number decision, and calendar. The
business sequence and timings (signed → live in ~5 days, ~2h founder time) live in
`onboarding-playbook.md`; **this document is the "exactly what I do" detail behind its
Deploy / Embed / WhatsApp / Calendar steps.**

Everything here rests on one architectural fact: **a client is a YAML file, not a new server.**
One shared process hosts every client and routes each request to the right config — by Host
subdomain for the web, and by WhatsApp number for WhatsApp. Adding a client is "drop a YAML +
DNS," never a redeploy of code.

---

## The two delivery surfaces

| Surface | Who gets it | How the client is identified |
|---|---|---|
| **Web widget** (default, every client) | Everyone | Host subdomain `<slug>.klantkraan.nl` → `config/clients/<slug>.yaml` |
| **WhatsApp** (optional upsell) | Clients who want their WhatsApp answered | The business's own WhatsApp number (the `To` on Twilio's webhook) → the client whose config declares it |

Both run off the same FastAPI server (`app.server`), share one conversation brain
(`app/receptionist.py`), and feed the same per-client oversight (daily digest + analyst).

---

## Prerequisites

**One-time (already set up, reused for every client):**

- The ops server is live (Hetzner, `ops/hetzner/`; deploy with `ops/hetzner/deploy.sh <ip>`).
- A Google service account for calendars (`docs/GOOGLE-CALENDAR.md`, "one-time").
- A Twilio account (only if selling WhatsApp).
- Cloudflare DNS access for `klantkraan.nl`.
- The receptionist's **own** Telegram bot token in the server `.env` (`TELEGRAM_BOT_TOKEN`) so
  lead alerts can fire — never the growth-engine approval bot.

**Per client, before you start:** a `slug` (a DNS label — lowercase, digits, hyphens), a drafted
config (`python -m app.scaffold "<Business Name>"`), and the real prices filled in (the scaffold
leaves them as `PRIJS?` — the bot never invents a price).

---

## 1. Deploy the client to a routable subdomain

**1.1 — Create the config.** Save it as `config/clients/<slug>.yaml`. These files carry client
PII, so they are **gitignored** (`config/clients/*.yaml`) — they live in your local working copy,
which is the source of truth `deploy.sh` pushes to the server. Fill in:

- Real `services` prices (no `PRIJS?` left), `hours`, `scope`, `greeting` (the greeting **must**
  keep the "digital assistant" disclosure — EU AI Act art. 50).
- `locale: en` if the client is English/other (defaults to Dutch).
- `notify:` → `telegram_chat_id: "..."` so *their* leads reach *them* (per-client recipient).
- `whatsapp:` → `number: "+<E.164>"` only if selling WhatsApp (see §3).
- `calendar:` block only once real bookings are wired (see §5); until then the demo `sim`
  provider generates slots.

**1.2 — DNS.** Cloudflare → `klantkraan.nl` → add an **A record**: name `<slug>`, value = the
server IP, **Proxy status: DNS only (grey cloud)**. Grey-cloud matters: it lets Caddy provision
its own Let's Encrypt certificate over HTTP. (Orange-cloud proxying breaks the ACME challenge.)

**1.3 — Caddy vhost.** Add a block to `ops/hetzner/Caddyfile.template`:

```
<slug>.klantkraan.nl {
    reverse_proxy 127.0.0.1:8000
}
```

**1.4 — Push + restart.** `ops/hetzner/deploy.sh <server-ip>` rsyncs the repo (including the new
client YAML), rewrites `/etc/caddy/Caddyfile`, reloads Caddy, and restarts the receptionist so
it loads the new config. (Config is cached per file at load — a restart is required after any
YAML edit.)

**1.5 — Verify.**

```
curl https://<slug>.klantkraan.nl/health
# -> {"status":"ok","business":"<Client name>"}
```

Then open `https://<slug>.klantkraan.nl` and have a real conversation — book a test appointment.
If `/health` returns the *default* business name instead of the client's, the config or DNS
didn't take (check the subdomain resolves and the YAML is on the box).

---

## 2. Website embed — the bot on the client's own site

**2.1 — The one line** the client (or you, on their behalf) pastes:

```html
<script src="https://<slug>.klantkraan.nl/widget.js" defer
        data-label="Chat met ons" data-color="#0d7d5a" data-position="right"></script>
```

Replace `<slug>` and set `data-color` to their brand and `data-label` to a friendly Dutch label.
The script only touches the DOM: it injects a floating bubble that opens an `<iframe>` back to
our origin, so the chat's `/chat` and `/config` calls stay same-origin — **no CORS, no API key in
their page source.** It lives in a shadow root, so their site's CSS can't break it.

**2.2 — Where it goes (default: you paste it, with access they grant).** Getting a `<script>`
onto a non-technical owner's site is the #1 place trades stall.

- **WordPress** — free **WPCode** plugin → Code Snippets → Header & Footer → paste into **Footer**.
- **Wix** (Premium) — Settings → **Custom Code** → **+ Add Custom Code** → All pages → **Body - end**.
- **Squarespace** (Business+) — Settings → Advanced → **Code Injection** → **Footer**.
- **Google Sites** — sandboxes scripts, so the bubble won't run: use **Insert → Embed** with an
  `<iframe src="https://<slug>.klantkraan.nl/?embed=1">`, or just give them the hosted link.

**2.3 — Can't edit the site?** Not a degraded mode — hand them the hosted full-page link
`https://<slug>.klantkraan.nl` and place it where they *can* reach: Google Business Profile
website/booking link, Instagram/Facebook bio, WhatsApp Business greeting, e-mail signature, a QR
code on the van and on quotes.

**2.4 — Verify.** Load their live page, open the bubble, send a message, book a test lead.

---

## 3. WhatsApp — their WhatsApp answered by the bot (optional)

Same brain, an adapter. WhatsApp is now **multi-tenant**: the inbound Twilio webhook has no Host
to route on, so the server routes by the *business's own* WhatsApp number (the `To` field). One
webhook URL serves every client safely because the number picks the tenant.

**Decide the number first — see §4.** Then:

**3.1 — Register the number as a Twilio WhatsApp sender.** Twilio Console → **Messaging →
Senders → WhatsApp senders** → add the number → verify by the SMS/voice code Meta sends. (For a
free trial without Meta approval, use the **WhatsApp sandbox** under Messaging → Try it out.)

**3.2 — Point the sender's inbound webhook** ("When a message comes in") at the ops server's
stable HTTPS host, method **POST**:

```
https://<ops-host>/whatsapp
```

Use the server's own host (e.g. `demo.klantkraan.nl`, which reverse-proxies to the app; or add a
dedicated `api.klantkraan.nl` vhost pointing at `127.0.0.1:8000` for cleanliness). **The same URL
is used for every WhatsApp client** — routing by the `To` number is what makes that safe.

**3.3 — Declare the number in the client config** so their WhatsApp reaches their bot:

```yaml
whatsapp:
  number: "+31 6 1234 5678"   # the client's WhatsApp sender number, E.164 (format-insensitive)
notify:
  telegram_chat_id: "..."      # their lead alerts
```

Then `deploy.sh` to push + restart. An inbound message to a number **no** client declares falls
back to the default config, so single-tenant setups are unchanged.

**3.4 — Lock the webhook.** Set `TWILIO_AUTH_TOKEN` in the server `.env` — signature validation
is fail-closed (unsigned requests are rejected unless `WHATSAPP_ALLOW_UNSIGNED=1`, dev only).

**3.5 — Test.** Message the number, get a booked lead, and confirm the reply reflects *that*
client (not the default) — that proves routing. A quick sanity check without a live Twilio round
trip: `resolve_whatsapp_slug("whatsapp:+<number>")` should return the slug (covered by the
`routing` selftest).

---

## 4. Phone-number strategy — the core decision

**The rule that drives everything (verified against Twilio/Meta docs, not memory):** a phone
number can be active on **only one WhatsApp surface at a time** — the personal **WhatsApp app**,
*or* the **WhatsApp Business app**, *or* the **WhatsApp Business Platform** (the API, which is
what Twilio uses). They are mutually exclusive. Registering a number as a Twilio WhatsApp sender
**requires that the number is not registered on a WhatsApp app first** — Twilio's guidance is to
"ensure the number is not registered elsewhere, delete existing WhatsApp accounts associated with
the number." Migrating a number *to* the API therefore *removes* it from the WhatsApp Business app.

| Option | What it costs | When to choose |
|---|---|---|
| **A. New dedicated number** *(recommended default)* | Buy a cheap new number (Twilio, or a local prepaid SIM / VoIP DID). Customers must learn a new number. | Almost always. Nothing to migrate; the client's existing WhatsApp stays untouched; the bot line is cleanly "the business line." The website widget is the primary capture channel anyway, so a fresh WA number costs little reach. Mitigate the "new number" friction by putting it on the site, Google Business Profile, and signatures. |
| **B. Migrate their existing business number** | That number **leaves the WhatsApp Business app** — they can no longer use the manual WA Business inbox on it; **all** messages now flow through the bot (and your alerts to them). | Only if brand continuity (the number customers already know) matters more than keeping the WhatsApp Business app, **and** they're willing to run their WhatsApp entirely through us. Migration = remove the number from the app → register it as the Twilio sender → verify. |
| **C. Their personal number** | Removes WhatsApp from their personal phone; mixes personal and business; unprofessional. | **Never.** Rule it out up front. |

**Recommendation:** default to **A (new dedicated number)** for almost every trade. Reach for
**B** only when a client insists on keeping a well-known number and accepts losing the WhatsApp
Business app on it. Never **C**.

---

## 5. Calendar — real bookings (optional upgrade from the sim)

The demo books into a built-in simulator. For real bookings, connect the client's own Google
Calendar (full steps in `docs/GOOGLE-CALENDAR.md`). In short:

- **Client (≈1 min):** Google Calendar → their calendar → **Settings and sharing** → share with
  the service-account email → permission **Make changes to events** (writer, not read-only).
- **You:** add the calendar block to their config, and ensure `GOOGLE_CALENDAR_SA_JSON` points at
  the service-account key on the server:

```yaml
calendar:
  provider: google
  calendar_id: "client@gmail.com"
```

- **Smoke test (read-only, books nothing):**
  `BUSINESS_CONFIG=config/clients/<slug>.yaml python -m app.selftest calendar-google` → expect
  `connected to Google Calendar; N open day(s)`.

Availability = the config's opening hours **minus** the calendar's busy blocks; the client blocks
time off simply by putting anything on their own calendar.

---

## 6. Go-live checklist

- [ ] `config/clients/<slug>.yaml`: real prices (no `PRIJS?`), hours, scope, greeting with the
      art. 50 disclosure, `locale`, `notify.telegram_chat_id`.
- [ ] DNS A-record (grey cloud) + Caddy vhost + `deploy.sh`; `/health` returns the **client's** name.
- [ ] Widget embedded on their site (or hosted link placed) **and** a real test lead handled.
- [ ] *(WhatsApp)* sender registered, `whatsapp.number` in config, webhook → `/whatsapp` set,
      `TWILIO_AUTH_TOKEN` in `.env`, test message routed to the **right** client.
- [ ] *(Real bookings)* calendar shared + `calendar:` block + `calendar-google` smoke test green.
- [ ] Lead alert reaches the client on their `telegram_chat_id` (send a test message that triggers
      a take-message).
- [ ] Oversight: the client appears in the daily digest once they have traffic (no action needed).

---

## Appendix — where each thing lives

| Thing | File |
|---|---|
| Client config (gitignored) | `ai-receptionist/config/clients/<slug>.yaml` |
| Multi-tenant routing rules | `ai-receptionist/config/clients/README.md` |
| Widget loader (served at `/widget.js`) | `ai-receptionist/web/widget.js` · `docs/WIDGET.md` |
| WhatsApp handler + number routing | `app/channels/whatsapp.py` · `app/settings.py` (`resolve_whatsapp_slug`) |
| Caddy vhosts / deploy | `ops/hetzner/Caddyfile.template` · `ops/hetzner/deploy.sh` |
| Calendar integration | `docs/GOOGLE-CALENDAR.md` · `app/calendar_store.py` · `app/calendar_google.py` |
| Channels overview | `ai-receptionist/docs/CHANNELS.md` |
