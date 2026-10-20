# client-sites

One reusable Astro template that builds a complete website for a Dutch trades client from a single `clients/<slug>/client.yaml` (plus an optional `clients/<slug>/fotos/` dir with the client's own work photos and logo). This is the kit for the EUR 1.000 website product: no hosting automation yet. The founder fills in the yaml (by hand from the intake checklist, or scraped, see below), builds with `CLIENT=<slug>`, runs the fact gate, eyeballs the result, and deploys `dist/` to Cloudflare Pages (see `docs/03-delivery/website-pilot-runbook.md`).

## Two modes

`modus` is required in every config, because neither default is safe to assume:

- **`live`**: a paying client's real site. Every legal field is mandatory (KvK, btw-id, e-mail, adres, eigen domein) or the build stops.
- **`preview`**: an unsolicited proposal built from public sources for a prospect who has not bought anything. Legal identifiers may be absent and are never invented. The site is noindex + `Disallow: /`, ships no sitemap and no LocalBusiness JSON-LD, carries no reviews, cannot claim the receptionist, and shows a banner naming Klantkraan as the sender. It is served from `https://<slug>.klant-preview.pages.dev` (one Pages project, one branch per prospect, so proposals never eat the 100-projects-per-account cap) and never from the prospect's own domain.

## Commands

```sh
# from klantkraan/apps/client-sites/
CLIENT=voorbeeld-dakdekker pnpm dev        # local dev server
CLIENT=voorbeeld-dakdekker pnpm build      # static build -> dist/
CLIENT=voorbeeld-dakdekker pnpm check      # fact gate: dist/ vs client.yaml
CLIENT=voorbeeld-dakdekker pnpm preview    # serve the built dist/
CLIENT=voorbeeld-dakdekker pnpm vloot      # distance from every other site we have built
CLIENT=voorbeeld-dakdekker pnpm tell-lint  # the AI-tells this page gives off on its own
pnpm typecheck                             # astro check (no CLIENT needed)
pnpm test                                  # design vocabulary tests (no CLIENT needed)
```

The build fails loudly when `CLIENT` is unset or the yaml does not pass the Zod schema (`src/lib/client.ts`). `pnpm check` (`scripts/verify-site.mjs`) then asserts the built pages against the config: phone number, links, city pages, no placeholders, no prices, no external requests, the right publishing posture per mode. The full battery lives in `QA.md`.

## The design vocabulary (`src/lib/stijl.ts`)

The template used to have exactly one appearance, and the only thing a client could change about
it were two hex colours: two voorstellen sent in the same week were recognisably the same
document, which is the one thing an unsolicited proposal cannot afford to be. So the skin is a
parameter and the silhouette is not.

Seven axes, each a closed set of named values that resolve to CSS custom properties written onto
`<html>`: `letterontwerp` (systeem/grotesk/industrieel/redactioneel), `schaal`, `vorm`, `ritme`,
`palet`, `kleuring`, `foto`. Section order, markup and the components are identical for every
client -- what varies is type, colour, rhythm, radius and how photographs are set. A closed
vocabulary rather than generated CSS because every value in it has been looked at once on a real
build: a chooser can produce a look, not an inaccessible contrast or a layout the fact gate
cannot assert. No `stijl:` block in a config means the look every client site had before the
vocabulary existed, so an older client.yaml builds the same bytes it did.

The one place the vocabulary meets the client's own colour is `kleuring`, which tints the bands
with `branding.kleur_primair`. Those tints are mixed over `--color-card`, the lightest surface a
palet owns, never over `--color-paper`: the tint comes out of the brand colour, so a darker
client colour makes a darker band, and over paper the two compound into combinations that no
contrast floor can rescue -- raising the floor makes that band darker still. Over card, every
colour the schema accepts clears AA on all 1728 skins, which is what lets `kleur_primair` be
gated by a single number (5.25:1 against white) instead of a per-skin check.

Chosen by `app.sitestyle` (in `ai-receptionist/`): off `--voorbeeld` reference sites when the
founder has one, otherwise composed from the vak and the company name. Measuring a reference is
code; choosing among the vocabulary is one schema-constrained Claude call. Nothing is lifted off
a reference -- it is measured and thrown away.

Typefaces are self-hosted (`fonts/`, `scripts/fonts.mjs`), never linked: zero external requests
is what ships these sites without a cookie banner, and a Google Fonts `<link>` would cost that.
`fonts/manifest.json` is read by BOTH `stijl.ts` (to build the stacks) and `astro.config.mjs`
(to copy only the woff2 a client needs, and to prune the `@font-face` rules of families this
build did not get), so what the CSS asks for and what the deploy contains cannot drift.

## Scraping a proposal config

`python -m app.sitedraft "<Bedrijfsnaam>" --url https://... --near <plaats>` (in `ai-receptionist/`) turns a prospect's public website plus Google Places into `clients/<slug>/client.yaml` with `modus: preview`. Phone and opening hours are mapped in code from the cited extraction; the Dutch copy comes from one schema-constrained Claude call that must paraphrase and may not invent claims or prices. Always check the phone number, plaats and diensten by eye before sending anything: `pnpm check` proves the site matches the config, not that the config matches reality.

## Stock photos per vak

`stock/<vak>/` holds a fetched Pexels set (`scripts/stock-photos.py`, pinned ids, run with the
growth-engine venv for Pillow). The photo band uses it only when the client supplied no photos of
their own, which is always true on a voorstel because we do not take a prospect's images. Only the
client's own vak is copied into `dist/` (the `clientStock` integration in `astro.config.mjs`), so a
dakdekker's site never ships a loodgieter's photos.

Covered today: `dakdekker`, `loodgieter`. Any other vak falls back to the color block until someone
adds a folder. Adding one is a manual pass, not a script run: plain "roofer"/"plumber" queries return
Mediterranean barrel tile and US asphalt shingle almost exclusively, so the dakdekker set had to come
from querying gutters, scaffolding and brick facades. Pick by eye from a contact sheet, no
recognisable faces (a stock person implying they work for a named client is a model-release problem),
Northern European subject matter.

Stock is a backdrop, not a claim: only the client's own photos get the `Werk van <naam>` alt text;
stock is described as `Werk van een <vak>` and the band is labelled `Sfeerbeeld`. `pnpm check` prints
which fallback actually rendered. Real client photos beat stock every time: the intake checklist
still asks for ten, and `research/website-aesthetics.md` puts real photos at +35% over the best stock.

## Template rules (baked in, do not undo)

- Click-to-call is the primary CTA everywhere; sticky call bar on mobile. No contact form.
- Zero external requests: self-hosted fonts, inline icons, no CDN, no embeds. That is what keeps the site cookie-banner-free, and it is a sales feature.
- No prices anywhere. No statistics or numeric claims in template copy. Dutch u-register.
- Reviews are plain text, max 3, only when the client supplied real ones. Never review/aggregateRating JSON-LD (LocalBusiness JSON-LD is emitted).
- Max 5 city pages, generated only for the configured `werkgebied` plaatsen.
- Photo band prefers the client's own work photos, falls back to the per-vak stock set
  (`stock/<vak>/`, see below), and only then to a color block. Never AI images.
- `/voorwaarden/` is a generic placeholder: adapt per client before go-live.
- The skin is deliberately not on this list: everything above holds at every point in the design
  vocabulary, which is what makes varying the look safe. Markup and section ORDER are still not
  negotiable per client -- free-form markup cannot be fact-gated. What a site may do since
  2026-08-16 is leave a section out (below).

## What makes two sites two sites

The design vocabulary gave the factory 1728 skins and the sameness moved rather than left: the
silhouette was one design and the copy was ~85% fixed strings with noun slots. Measured before
anything changed, two voorstellen for different vakken in different towns shared 42% of their
phrasing and a 35-word passage. Diagnosis, evidence and plan:
`research/PLAN-site-factory-anti-template-2026-08-16.md`.

Three things carry it now, and the first two are optional blocks in `client.yaml`:

- **`teksten:`** -- eight slots (`kop`, `belofte`, `intro_kop`, `werkwijze`, `bereik`,
  `diensten_tekst`, `slot_kop`, `slot_tekst`), each merged over the register default in
  `src/lib/toon.ts` one key at a time. `kop` is the H1. Written by `app.sitedraft` from the
  prospect's own sources; an absent key falls back to the register, which is the honest outcome
  for a thin prospect. This block is what moved a fixture from 23.8% to 5.8%.
- **`indeling.weglaten:`** -- up to two of `intro`, `werk`, `werkgebied`, `usps`. Real Dutch
  trade sites run 6-13 sections and every one is missing something obvious; shipping all nine,
  filled and symmetric, is identifiable because nothing is missing. Hero, diensten, the closing
  CTA, the hours panel and the footer are not omittable: a site without one of those is not
  sparse, it is broken.
- **The two gates**, `pnpm vloot` and `pnpm tell-lint`, both also reachable as
  `kk site check <slug> --vloot --tells`. Neither is in `pnpm check` yet, because every fixture
  without a `teksten:` block still fails the copy threshold. Wire them into the build gate once
  the fleet passes them.
