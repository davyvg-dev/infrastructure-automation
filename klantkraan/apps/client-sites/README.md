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
pnpm typecheck                             # astro check (no CLIENT needed)
```

The build fails loudly when `CLIENT` is unset or the yaml does not pass the Zod schema (`src/lib/client.ts`). `pnpm check` (`scripts/verify-site.mjs`) then asserts the built pages against the config: phone number, links, city pages, no placeholders, no prices, no external requests, the right publishing posture per mode. The full battery lives in `QA.md`.

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
- Zero external requests: system fonts, inline icons, no CDN, no embeds. That is what keeps the site cookie-banner-free, and it is a sales feature.
- No prices anywhere. No statistics or numeric claims in template copy. Dutch u-register.
- Reviews are plain text, max 3, only when the client supplied real ones. Never review/aggregateRating JSON-LD (LocalBusiness JSON-LD is emitted).
- Max 5 city pages, generated only for the configured `werkgebied` plaatsen.
- Photo band prefers the client's own work photos, falls back to the per-vak stock set
  (`stock/<vak>/`, see below), and only then to a color block. Never AI images.
- `/voorwaarden/` is a generic placeholder: adapt per client before go-live.
