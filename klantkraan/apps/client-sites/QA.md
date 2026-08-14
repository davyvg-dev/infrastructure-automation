# QA battery for a client-site build

Exact commands run against the fixture (`voorbeeld-dakdekker`) on 2026-08-14; these feed
the P6 pilot runbook. Run everything from `klantkraan/apps/client-sites/` unless noted.
Replace the slug and the domain grep with the client's own.

## 1. Build + typecheck (must both be green)

```sh
CLIENT=voorbeeld-dakdekker pnpm build
pnpm typecheck
```

The build fails loudly on: missing `CLIENT`, unknown slug (lists known clients), invalid
YAML, and schema violations (per-field Dutch messages, including the WCAG contrast check
on `kleur_primair`). All four verified.

## 2. Zero external requests (the no-cookie-banner guarantee)

```sh
grep -rhoE '(href|src)="https?://[^"]*"' dist --include='*.html' \
  | grep -vE 'voorbeeld-dakwerken\.nl|wa\.me' | sort -u
# expected: empty. Only tel:/mailto:/wa.me and the client's own domain may occur.

grep -rhoE '<script[^>]*>' dist --include='*.html' | sort -u
# expected: only <script type="application/ld+json"> (zero executable JS site-wide)
```

## 3. Exactly one h1 per page

```sh
for f in $(find dist -name '*.html'); do echo "$(grep -o '<h1' $f | wc -l | tr -d ' ')  $f"; done
# expected: every line starts with 1
```

## 4. LocalBusiness JSON-LD parses, no review schema

```sh
node -e 'const fs=require("fs");const m=fs.readFileSync("dist/index.html","utf8").match(/<script type="application\/ld\+json">(.*?)<\/script>/s);const d=JSON.parse(m[1]);console.log(d["@type"],d.name,d.telephone)'
grep -ri aggregateRating dist || echo none   # expected: none
```

## 5. Title, description, viewport on every page

```sh
for f in $(find dist -name '*.html'); do echo "title=$(grep -c '<title>' $f) desc=$(grep -c 'name=\"description\"' $f) viewport=$(grep -c 'name=\"viewport\"' $f)  $f"; done
# expected: title=1 desc=1 viewport=1 everywhere
```

## 6. Copy lint (repo-root script)

```sh
# from the repo root
bash scripts/copy-lint.sh klantkraan/apps/client-sites
```

Clean on 2026-08-14. Note: a real client's phone number in `client.yaml` trips the
`stale-phone` rule by design; keep the ` # copy-lint-ok` marker on the telefoon/whatsapp
lines of client configs (the rule exists for Klantkraan's own copy, not client data).

## 7. Squirrelscan against a local preview

```sh
CLIENT=voorbeeld-dakdekker pnpm preview --port 4331 &
squirrel audit http://localhost:4331 --format llm
```

Ran on 2026-08-14 (squirrel v0.0.80): 9 pages, 131 rules passed. Known local-preview
artifacts, NOT template bugs (re-check on the deployed Pages URL instead):

- `links/broken-links`, `links/orphan-pages`, `eeat/privacy-policy`: squirrel strips the
  trailing slash and `astro preview` does not redirect `/contact` to `/contact/`;
  Cloudflare Pages 308-redirects, so these clear in production.
- `security/https`, `perf/http2`: localhost is plain HTTP.
- `security/csp`, `security/x-frame-options`, `perf/bad-caching`: served by
  `public/_headers` on Cloudflare Pages, which `astro preview` ignores.
- `crawl/sitemap-coverage`: the sitemap carries the client's real domain, the crawl ran
  on localhost.

Real, accepted findings: no og:image (client sites ship no share image yet; candidate:
first client photo), no About page (the homepage intro covers it), a11y underline hint on
the werkgebied chips (they are bordered button-style cards).

## Not available locally on 2026-08-14

lychee, pa11y and Lighthouse CLIs are not installed (and installing global tools is out
of scope here). The founder runbook (P6) carries the full battery against the deployed
URL: rerun `squirrel audit https://<domein>` there, which also covers link checking and
the header/HTTPS rules for real.
