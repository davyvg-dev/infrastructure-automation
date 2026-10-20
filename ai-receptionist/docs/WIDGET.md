# Embeddable chat widget

The receptionist ships two front-ends off the same server:

1. **Full-page chat** at `/` — the hosted-link fallback (`https://<client>.klantkraan.nl`).
2. **Floating bubble** via `/widget.js` — a one-line `<script>` the client pastes on their own
   site. It injects a bubble that opens an `<iframe>` back to `/?embed=1` on our origin.

Because the chat always runs inside an iframe on **our** origin, its `fetch('/chat')` and
`fetch('/config')` stay same-origin: **no CORS, no API key in the client's page source.** The
whole bubble lives in a shadow root, so the host site's CSS can't leak in and break it.

## The snippet the client pastes

```html
<script src="https://CLIENT.klantkraan.nl/widget.js" defer
        data-label="Chat met ons" data-color="#0d7d5a" data-position="right"></script>
```

Replace `CLIENT.klantkraan.nl` with the client's hosted origin (the subdomain that serves their
`BUSINESS_CONFIG`). Optional `data-*` attributes:

| Attribute | Default | Notes |
|---|---|---|
| `data-label` | `Chat` | Bubble aria-label + iframe title (Dutch, client-facing). |
| `data-color` | `#2f6df6` | Bubble background; match the client's brand. |
| `data-position` | `right` | `right` or `left`. |

The chat's own UI language (placeholder, send button, subtitle) follows the config's `locale`
(`/config`), defaulting to Dutch — set `locale: en` at the top of a config to opt out.

## Per-platform install (default = we do it for them)

Getting a `<script>` onto a non-technical owner's site is the #1 place trades stall — default to
pasting it yourself with access the client gives you. Menu names current as of 2026.

- **WordPress** — install the free **WPCode** plugin → Code Snippets → Header & Footer → paste the
  line into **Footer** → Save. (Classic alt: Appearance → Widgets → Custom HTML block in the footer.)
- **Wix** (Premium plan) — Settings → **Custom Code** → **+ Add Custom Code** → paste → "Add Code to
  Pages: All pages" → place in **Body - end** → Apply.
- **Squarespace** (Business plan+) — Settings → Advanced → **Code Injection** → **Footer** → paste → Save.
- **Google Sites** — sandboxes scripts, so the bubble won't run. Use **Insert → Embed** with an
  `<iframe src="https://CLIENT.klantkraan.nl/?embed=1">` or paste the plain full-page URL instead.

## Fallback — client can't edit the site

Not a degraded mode; fully functional, just no bubble on their domain. Hand them the hosted
full-page link `https://CLIENT.klantkraan.nl` and place it wherever they *can* reach:

- Google Business Profile "Afspraak maken" / website link (often more traffic than their own site)
- Instagram / Facebook bio, WhatsApp Business greeting, e-mail signature
- A QR code on the van, flyers, or quotes/invoices

## Hosting / server notes

- The widget page is **frameable by default** — the server never sends `X-Frame-Options`. If a
  reverse proxy (Caddy/nginx) sits in front, make sure it doesn't add one. If you set a CSP, allow
  the client's domain(s) via `frame-ancestors`.
- Each client is served from a **distinct origin/subdomain** (`<slug>.klantkraan.nl`) that the
  server maps to `config/clients/<slug>.yaml` — one process hosts many clients. Unknown hosts fall
  back to the `BUSINESS_CONFIG` default. See `config/clients/README.md`. Per-tenant session state
  and (sim) bookings are namespaced by slug, so clients never share conversations or slots.
- `/chat` keeps its optional `CHAT_API_KEY` (a coarse gate, visible in any browser widget — the real
  guard is the per-IP `CHAT_RATE_LIMIT_PER_MINUTE`, default 20/min, since every call is a paid
  Claude request). Keep the server behind a proxy so `X-Forwarded-For` carries the real IP.
