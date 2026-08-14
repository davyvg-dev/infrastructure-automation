# QA battery for a client-site build

Run everything from `klantkraan/apps/client-sites/`. Three commands, all must be green before a
site is sent to anyone:

```sh
CLIENT=<slug> pnpm build      # Zod schema: config is well formed
pnpm typecheck                # astro check
CLIENT=<slug> pnpm check      # fact gate: dist/ says what client.yaml says
```

## 1. Build + typecheck

The build fails loudly on: missing `CLIENT`, unknown slug (lists known clients), invalid YAML,
schema violations with per-field Dutch messages (including the WCAG contrast check on
`kleur_primair`), a missing `modus`, a `modus: live` config without KvK/btw-id/e-mail/adres/
domein, and a `modus: preview` config that claims the receptionist or carries reviews.

## 2. `pnpm check`: the fact gate (`scripts/verify-site.mjs`)

The schema proves the config is well formed; squirrelscan proves the HTML is sane. Neither
catches the failure that actually costs a client money: a right-looking site with the wrong
phone number on it. This script re-reads `client.yaml` itself (not through `src/lib/client.ts`,
so a loader bug cannot hide behind its own output) and asserts the rendered pages against it:

- **facts**: the configured phone number on every page; the set of `tel:`, `mailto:` and
  `wa.me` links is exactly what the config specifies and nothing else; the business name on
  every page; every configured dienst rendered somewhere
- **werkgebied**: the built city pages are exactly the configured plaatsen, no extras
- **legal**: KvK and btw-id in the footer of every page on a live site; absent from a proposal
- **never published**: placeholder markers (`TODO`, `PRIJS?`, `AANVULLEN`, `undefined`, …),
  any price (`€ 95`, `95 euro`), review/aggregateRating structured data
- **zero external requests**: the no-cookie-banner guarantee, plus no executable JavaScript.
  Allowed: the client's own domain, `wa.me`, `*.pages.dev`, and on a proposal `klantkraan.nl`
  (the banner's sender link; a link is not a request)
- **publishing posture**: live: sitemap, robots pointing at it, canonicals on the client's
  domain, LocalBusiness JSON-LD, no noindex. Preview: noindex meta on every page, the banner on
  every page, `X-Robots-Tag` in `_headers`, `Disallow: /` in robots.txt, no sitemap, no JSON-LD
- **structure**: exactly one `<h1>`, a title, a description and a viewport per page; JSON-LD
  parses

It also refuses to run against a `dist/` built for a different client, and prints the things a
human still has to judge (missing photos, phone-only contact page, the generic `/voorwaarden/`).

Verified 2026-08-14 against both fixtures, and against seven deliberately sabotaged builds:
a swapped phone number, an injected price, a leftover `TODO`, an external `<script>`, review
schema, a stripped preview banner, and a `dist/` from another client. All seven exit 1.

## 3. Squirrelscan against a local preview

```sh
CLIENT=<slug> pnpm preview --port 4331 &
squirrel audit http://localhost:4331 --format llm
```

Ran on 2026-08-14 (squirrel v0.0.80): 9 pages, 131 rules passed. Known local-preview artifacts,
NOT template bugs (re-check on the deployed Pages URL instead):

- `links/broken-links`, `links/orphan-pages`, `eeat/privacy-policy`: squirrel strips the
  trailing slash and `astro preview` does not redirect `/contact` to `/contact/`;
  Cloudflare Pages 308-redirects, so these clear in production.
- `security/https`, `perf/http2`: localhost is plain HTTP.
- `security/csp`, `security/x-frame-options`, `perf/bad-caching`: served by `public/_headers`
  on Cloudflare Pages, which `astro preview` ignores.
- `crawl/sitemap-coverage`: the sitemap carries the client's real domain, the crawl ran on
  localhost.

Real, accepted findings: no og:image (client sites ship no share image yet; candidate: first
client photo), no About page (the homepage intro covers it), an a11y underline hint on the
werkgebied chips (they are bordered button-style cards).

## 4. Copy lint (repo root)

```sh
bash scripts/copy-lint.sh klantkraan/apps/client-sites
```

Clean on 2026-08-14. Note: a real client's phone number in `client.yaml` trips the
`stale-phone` rule by design; keep the ` # copy-lint-ok` marker on the telefoon/whatsapp lines
of client configs (the rule exists for Klantkraan's own copy, not client data).

## Not available locally on 2026-08-14

lychee, pa11y and Lighthouse CLIs are not installed (and installing global tools is out of
scope here). The founder runbook (`docs/03-delivery/website-pilot-runbook.md`) carries the full
battery against the deployed URL: rerun `squirrel audit https://<domein>` there, which also
covers link checking and the header/HTTPS rules for real.
