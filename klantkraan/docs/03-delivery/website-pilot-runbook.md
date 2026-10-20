# Website pilot: go-live runbook

Stage-by-stage, for the founder, one manual pilot site at a time. Targets per stage in the
timing log (`website-pilot-timing-log.md`); fill it in as you go, that is the pilot's whole
point. The promise is "binnen een week online na complete intake", never faster promises.

Selling one in the first place, by building a prospect their site before they buy, is a
separate playbook: `website-voorstel-playbook.md`. A voorstel that turns into a client joins
this runbook at stage 3.

## Stage 0: sale closed

- Send the client Deel 1 of `website-intake-checklist.md` (photos + five questions).
- Price is locked: €1.000 ex btw (€749 bundled with a receptionist plan) + €39/mo
  onderhoud per `website-maintenance-scope.md`. No discounts on the receptionist side.
- BLOCKER until fixed: seller BTW-id/address placeholders in the billing config make
  invoices legally invalid (see TODO §P8). Resolve before invoicing the pilot.

## Stage 1: intake completeness check (10 min)

Per the checklist's completeness gate: complete → confirm and start the clock; incomplete →
one reject-with-checklist reply naming exactly what is missing. Nothing else.

## Stage 2: build (pilot = by hand)

1. Scrape-first: `kk site new "<Naam>" --url <site> --near <plaats>` (see checklist Part 2)
   writes `klantkraan/apps/client-sites/clients/<slug>/client.yaml`; top it up with what the
   scrape cannot know (KvK, btw-id, adres, e-mail, domein, reviews) and set `modus: live`.
   Photos into `clients/<slug>/fotos/`. Client dirs are gitignored (PII). A prospect who
   already has a voorstel-site keeps that config: promote it per the voorstel-playbook.
2. `kk site build <slug>`; the schema fails loudly on anything invalid, including a brand
   color that cannot carry white text and a live config still missing its legal fields.
3. Copy pass on the generated pages with the client's own words from the intake. No
   statistics, no prices, u-register.

## Stage 3: QA battery (~15 min, all must pass)

`kk site build <slug>` is the battery: it builds and then runs the fact gate, which asserts the
rendered pages against `client.yaml` (phone number and every tel:/mailto:/wa.me link, business
name, diensten, city pages, KvK+btw in the footer, no placeholders, no prices, no review
schema, zero external requests, no executable JavaScript, sitemap and canonicals on the
client's own domain, one h1 and a title/description/viewport per page). A live-mode build also
refuses to run at all until KvK, btw-id, adres, e-mail and domein are filled in.

The full list, including what the gate deliberately does not judge, lives in
`klantkraan/apps/client-sites/QA.md`. Additionally, from repo root against a local preview:
the `audit-website` skill (squirrelscan; ignore trailing-slash and header findings that
only exist on `astro preview`, Cloudflare Pages serves both). Lighthouse/pa11y/lychee are
not installed locally; run Lighthouse from Chrome devtools on the preview URL until the
pilot decides whether they earn a place in the battery.

## Stage 4: founder review (25 min)

Dutch copy out loud, photos in the right spots (or the fallback looks intentional), mobile
at 320px, click-to-call works, WhatsApp link opens with the right number, spoed panel
matches what the client actually promises.

## Stage 5: client review, ONE revision round (15 min founder)

Send the `*.pages.dev` preview link. Ask for ALL feedback in one reply (form or one mail).
Apply, rebuild, confirm. A second round is meerwerk; say so kindly and log it.

## Stage 6: go-live (5 min founder, 1-2 h wall clock)

1. **Domain** (client's name, always): register via TransIP with the client as holder.
   NS to Cloudflare per `docs/08-tech/dns-ns-troubleshooting.md`, including its known
   failure mode: the TransIP UI can confirm an NS change that never persists; verify with
   `dig NS <domein> +short` after ~15 min, not with the UI.
2. **Cloudflare**: add the zone, create a Pages project `client-<slug>`, upload the build:
   `pnpm dlx wrangler@4 pages deploy ./dist --project-name=client-<slug> --branch=production`.
3. **Custom domain**: attach via the Pages REST API, not wrangler (workers-sdk#11772):
   `curl -X POST "https://api.cloudflare.com/client/v4/accounts/<account_id>/pages/projects/client-<slug>/domains" -H "Authorization: Bearer $CF_API_TOKEN" -H "Content-Type: application/json" --data '{"name":"<domein>"}'`
   plus the apex/www CNAME records in the zone.
4. **E-mail routing**: Cloudflare Email Routing forward to the client's existing mailbox;
   the client clicks one verification mail; warn them it is coming.
5. **Smoke**: https loads on apex + www, `?v=1` cache-bust (Pages new-asset cache poison:
   verify via the deploy alias first), tel: link on a phone, sitemap.xml reachable.

## Stage 7: handover (5 min)

- WhatsApp to the client: live URL, what is in onderhoud (link/attach the scope doc's
  Dutch section), how to request a change.
- **IP-transfer**: on final payment, send the written akte line: auteursrecht op de site
  wordt overgedragen aan <bedrijf> per <datum>, bevestigd per e-mail. Without the written
  akte the copyright legally stays with the builder; this is not optional.
- Register the live URL in the status-page monitoring (manual note for now; automation is
  a post-pilot decision).
- Fill the timing log the same day, while the friction is fresh.
