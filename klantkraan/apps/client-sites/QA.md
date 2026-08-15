# QA battery for a client-site build

Run everything from `klantkraan/apps/client-sites/`. Three commands, all must be green before a
site is sent to anyone:

```sh
CLIENT=<slug> pnpm build      # Zod schema: config is well formed
pnpm typecheck                # astro check
pnpm test                     # design vocabulary: what a skin resolves to (no CLIENT needed)
CLIENT=<slug> pnpm check      # fact gate: dist/ says what client.yaml says
```

## 1. Build + typecheck

The build fails loudly on: missing `CLIENT`, unknown slug (lists known clients), invalid YAML,
schema violations with per-field Dutch messages (including the WCAG contrast check on
`kleur_primair`), a missing `modus`, a `modus: live` config without KvK/btw-id/e-mail/adres/
domein, and a `modus: preview` config that claims the receptionist or carries reviews.

## 1b. `pnpm test`: the design vocabulary (`src/lib/stijl.test.ts`)

Per-client checks all run against one skin -- the one that client got. These run against all
1728 the vocabulary can express, which is what makes editing an axis or adding a value to one
safe. `node --test` on the TypeScript directly; no framework, no CLIENT, about half a second.

Every combination resolves the same token set, nothing empty, and the seven axes write disjoint
properties (two axes on one property means the founder moves a knob and nothing happens). Then
what the values have to mean: the type scale runs downhill and the schalen are ordered at both
ends of every clamp, no h1 grows past the 3.5rem cap, the photo band keeps more air than the
text at every density, `scherp` zeroes all three radii and `randloos` squares a photo whatever
`vorm` says, every palet clears AA for ink AND mist on its own surfaces, `royaal`'s tint stays
under 20%, the skin outranks a caller's override, and every `var()` the inline style references
is set in the same declaration. Fonts: the leading family of each stack matches
`fonts/manifest.json` and has a woff2 really on disk, and only the serif pairing falls back to
a serif.

Believed because they were made to fail first: 17 mutations of `stijl.ts` (drop a token, collide
two axes, put `groot`'s h1 back to 4.25rem, invert a step, lighten the mist, pill a sharp button,
ask for an uncopied family, let a caller outrank the skin), each caught by the test that should
catch it and no other. Runs in CI on every push.

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
  (the banner's sender link; a link is not a request). Stylesheets are swept too: a remote
  `@import` or a `url()` on a CDN costs the guarantee just as dearly as a `<script>`
- **the skin, as the browser will paint it**: the gate reads the custom properties off `<html>`
  and resolves what they actually resolve to -- `var()` chains and `color-mix(in oklab, …)`
  included -- rather than trusting the vocabulary. 14 text/surface pairs against the 4.5:1 AA
  floor, including white and white-at-85% over the client's own `kleur_primair`, which the
  schema only ever checked against white. Hairlines are exempt on purpose (WCAG 1.4.11). Every
  page must carry the same skin, and a page with none was not built on `Base.astro`
- **fonts**: every `@font-face` names a family the page's stacks name and loads a root-relative
  file really in `dist/`; every leading family has a rule; no shipped woff2 goes unreferenced;
  and the pairing `stijl.letterontwerp` asked for is the one each stack LEADS with. That last
  one is per stack, not a count: a `redactioneel` site that lost its serif still leads
  `--font-sans` with Figtree, so a count sees nothing wrong while the half a reader notices
  is gone
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

The skin half (2026-08-15) got nine of its own: a missing woff2, a CDN `src`, a rule for a
family the page does not name, a stack fallen back to the system one, a merkkleur too light for
its band, a page with no skin, an off-host `url()`, an orphan font file, and two pages
disagreeing about the skin. Each was made to fail before the check was believed.

## 3. Squirrelscan against a local preview

```sh
CLIENT=<slug> pnpm preview --port 4331 &
squirrel audit http://localhost:4331 --format llm
```

Audit through `astro preview`, not a plain static server. `python -m http.server` sends no gzip
and ignores `public/_headers`, which fails `perf/compression` and `perf/cache-headers` for reasons
that have nothing to do with the site; scores across the two are not comparable.

Ran on 2026-08-14 (squirrel v0.0.85, voorbeeld-dakdekker): 9 pages, 78/C, 953 passed, 50 warnings,
10 failed, with Images and Accessibility both at 100. Up from 76/C, 914 passed, 59 warnings after
the photo rework: the share card closed `social/og-image`, per-photo Dutch alt text closed
`images/alt-text`, and width/height plus a hero preload closed `images/dimensions`,
`perf/cls-hints` and `perf/lcp-hints`. Known local-preview artifacts, NOT template bugs (re-check
on the deployed Pages URL instead):

- `security/https`, `perf/http2`: localhost is plain HTTP.
- `security/csp`, `security/x-frame-options`, `perf/bad-caching`: served by `public/_headers`
  on Cloudflare Pages, which `astro preview` ignores.
- `crawl/sitemap-coverage`: the sitemap carries the client's real domain, the crawl ran on
  localhost.
- `links/broken-links`, `links/orphan-pages`, `eeat/privacy-policy` were on this list under
  v0.0.80 (trailing-slash handling) and no longer fire under v0.0.85.

Real, accepted findings: no About page (the homepage intro covers it), an a11y underline hint on
the werkgebied chips (they are bordered button-style cards), `images/optimized` (info: "consider
an image CDN", which a static Pages deploy does not have), and `perf/lazy-above-fold` on the first
two work-section tiles. That section is the fourth on the homepage, well below any real fold, so
`loading="lazy"` stays; the rule appears to flag the first grid row by position in the DOM rather
than on screen. The hero photo above it is `fetchpriority="high"` with a `<link rel="preload">`,
which is the image that actually matters for LCP.

Stock photo budget: every rendition stays under the 200 KB that `images/image-file-size` flags
(largest is the dakdekker hero at 179 KB). The aerial tile first came in at 291 KB, which is what
sized the wide rendition down to 900px -- it is drawn in a 357px box, so the rest was never going
to be seen. Re-check this after adding any vak: detail-dense frames (roof tiles, brickwork,
foliage) compress far worse than studio close-ups.

Also accepted, and worth a decision before a real client ships: `content/word-count` on
`/contact/` (201), `/diensten/` (216) and the city pages (~261) against a 300 minimum, and
`core/meta-description` outside 120-160 on four pages. `content/keyword-stuffing` flags "het" and
"een": squirrel has no Dutch stopword list, so that part is noise.

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
