# Voorstel-sites: de website als openingszet

A proposal site is a real, working website for a prospect who has not bought anything, built
from their public information and served noindex on a `*.pages.dev` URL under a banner that
says Klantkraan made it. It exists because the pilot is blocked on a buyer, not on a template:
a prospect who can click through their own new site is being sold something concrete instead of
a description.

This is a **sales** playbook. Delivery of a sold site stays in `website-pilot-runbook.md`.

## The rules this rides on (none of them are relaxed here)

- **The proposal is an asset inside the existing outreach, not a new channel.** Everything in
  `docs/02-sales/cold-email-sequences.md` still applies unchanged: BV filter, no cold e-mail to
  eenmanszaak or VOF without opt-in, 6 sends a day, one ledger. A proposal site does not make a
  prospect contactable who was not contactable before.
- **No cold calling.** Founder constraint, unchanged.
- **Only public sources.** `app.sitedraft` reads the prospect's own website and their Google
  Business listing. Nothing else, no personal data beyond the business contact details they
  publish themselves.
- **Their photos and reviews stay theirs.** A proposal runs on the colour-block fallback. The
  schema refuses reviews on a preview config for the same reason.
- **Never on their domain, never indexed.** The build emits noindex, `X-Robots-Tag`,
  `Disallow: /`, no sitemap and no LocalBusiness JSON-LD, and canonicals point at the preview
  host. A proposal that turns up in Google search results for their name is the one failure
  mode of this whole motion.
- **The banner is not decoration.** Every page says Klantkraan made this as a voorstel, on
  public information, and that we take it down on request. Do not remove it, do not shrink it,
  do not let the tab title lose its "voorbeeld van Klantkraan" suffix.
- **Take it down when asked, same day, no discussion.** `wrangler pages deployment delete`, or
  delete the branch. Log it in the sequence ledger as an opt-out.

## Making one (about 10 minutes of founder time)

```sh
# 1. Scrape the prospect into a voorstel-config (writes clients/<slug>/client.yaml)
kk site new "Jansen Loodgieters" --url https://jansen-loodgieters.nl --near Utrecht

# 2. Build it and let the fact gate check it against the config
kk site build jansen-loodgieters

# 3. Look at it yourself, at 375px and on a laptop
kk site open jansen-loodgieters

# 4. Ship it to <slug>.klant-preview.pages.dev
kk site deploy jansen-loodgieters
```

Step 1 maps telefoon and openingstijden in code from the cited extraction and drafts the Dutch
copy with one schema-constrained model call that must paraphrase and may not invent claims or
prices. Step 2 proves the site matches the config. **Neither proves the config matches
reality**, so step 3 is not optional:

- Is the phone number theirs, and is it the number they actually answer?
- Is the plaats right, and is every plaats in the werkgebied one they really serve?
- Do the diensten match what this business does, in their words rather than ours?
- Do the openingstijden match their site or their Google listing?
- Does any sentence claim something we cannot point at a source for?

Wrong facts are worse than no site: the whole pitch is that we pay attention.

## Sending it

Inside the normal sequence, as the opener for a prospect already in it. One link, no
attachment, no pressure, and the way out named in the same breath:

> Onderwerp: uw website, alvast gemaakt
>
> Goedemiddag,
>
> Wij bouwen websites voor installatie- en onderhoudsbedrijven en hebben er alvast een gemaakt
> voor [bedrijf], op basis van wat er openbaar over u te vinden is:
>
> [url]
>
> Hij staat niet online voor uw klanten en Google ziet hem niet. Kloppen de gegevens niet, dan
> pas ik ze aan. Wilt u hem niet, dan haal ik hem weg, dat kost u een regel terugmail.
>
> Zegt hij u wel wat, dan zet ik hem live op uw eigen domeinnaam, op uw naam, voor een vaste
> prijs.

Do not put the price in the first message. Do not send a second unsolicited message about the
same proposal; the sequence's own cadence governs follow-ups.

## When they say yes: promoting a voorstel to a live site

The config stays, the mode changes. Add what a proposal is not allowed to invent:

1. `kvk` (8 cijfers) and `btw_id` (`NL#########B##`), from the client, not from a register scrape.
2. `email`, and `adres.straat` + `adres.postcode`.
3. `domein`, bare, registered in the client's own name (see the runbook's stage 6).
4. `receptionist: true` only when they actually have one.
5. `reviews`, only real quotes, only with permission.
6. Photos into `clients/<slug>/fotos/`, from the intake checklist's shot list.
7. Flip `modus: live`.

`kk site build <slug>` then refuses until every one of those is present, which is the point.
From there the pilot runbook takes over at stage 3 (QA), and the timing log gets its row.

## What this does not change

The €1.000 price, the €39/mo onderhoud, the one-revision-round rule, and the promise of "binnen
een week online na complete intake" all stand as written. A proposal shortens the distance to
the conversation; it does not shorten delivery, and it is not a discount.
