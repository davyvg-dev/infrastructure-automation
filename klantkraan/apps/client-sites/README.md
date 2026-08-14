# client-sites

One reusable Astro template that builds a complete website for a Dutch trades client from a single `clients/<slug>/client.yaml` (plus an optional `clients/<slug>/fotos/` dir with the client's own work photos and logo). This is the pilot kit for the EUR 1.000 website product: no generator CLI and no hosting automation yet. The founder copies the fixture dir, fills in the yaml from the intake checklist, builds with `CLIENT=<slug>`, eyeballs the preview, and deploys `dist/` to a dedicated Cloudflare Pages project per client (see `docs/03-delivery/website-pilot-runbook.md`).

## Commands

```sh
# from klantkraan/apps/client-sites/
CLIENT=voorbeeld-dakdekker pnpm dev        # local dev server
CLIENT=voorbeeld-dakdekker pnpm build      # static build -> dist/
CLIENT=voorbeeld-dakdekker pnpm preview    # serve the built dist/
pnpm typecheck                             # astro check (no CLIENT needed)
```

The build fails loudly when `CLIENT` is unset or the yaml does not pass the Zod schema (`src/lib/client.ts`). QA commands for a finished build live in `QA.md`.

## Template rules (baked in, do not undo)

- Click-to-call is the primary CTA everywhere; sticky call bar on mobile. No contact form.
- Zero external requests: system fonts, inline icons, no CDN, no embeds. That is what keeps the site cookie-banner-free, and it is a sales feature.
- No prices anywhere. No statistics or numeric claims in template copy. Dutch u-register.
- Reviews are plain text, max 3, only when the client supplied real ones. Never review/aggregateRating JSON-LD (LocalBusiness JSON-LD is emitted).
- Max 5 city pages, generated only for the configured `werkgebied` plaatsen.
- Photo band uses client photos or a color-block fallback. No stock photos, no AI images.
- `/voorwaarden/` is a generic placeholder: adapt per client before go-live.
