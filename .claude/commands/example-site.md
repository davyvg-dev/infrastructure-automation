---
description: Build an example client site for any vak, with stock photos curated on demand
argument-hint: [vak] [plaats] [optional: 1-3 reference URLs you like the look of]
---

Build an example site for: $ARGUMENTS

A throwaway demo of the website factory: a fictional business, built locally, never deployed.
`example-site barber rotterdam` is a complete instruction. Do not come back with questions the
steps below already answer; the only thing worth stopping for is a genuine conflict in the request.

Ralph rule: verify every step before the next; any failure stops the line.

## a) Read the request

Pull from $ARGUMENTS: the **vak**, the **plaats** (default Amersfoort), and **0-3 reference URLs**.
More than 3 references: use the first 3 and say which you dropped.

Then settle three things yourself and report what you chose:

- **The vak as a Dutch noun.** "barber" is `kapper`, "plumber" is `loodgieter`. This string is the
  key for everything downstream: the stock set lives at `stock/<vak>/` and the copy says "Uw
  <vak> in ...". Pick the noun a Dutch customer would search for, and stay with it.
- **`bedrijfstype`.** Does the business drive to the customer or does the customer come to it?
  `mobiel` for dakdekker, loodgieter, installateur, hovenier, schilder. `locatie` for kapper,
  tandarts, hondentrimmer, garage, restaurant. When it is genuinely both (a fietsenmaker with a
  shop that also does pickups) pick the one their money comes from and say so in the report. Under
  `locatie` the `werkgebied` becomes the **neighbourhoods customers travel from**, not towns
  travelled to, so list wijken.
- **A company name** that reads as obviously fictional (`Voorbeeld <vak>`, `Testbedrijf <vak>`),
  does not collide with a real firm, and stays **under 34 characters** or the `groot` scale is
  withdrawn (`sitestyle.py:142`).

## b) Stock photos

`ls klantkraan/apps/client-sites/stock/sets/` shows which vakken are covered. If yours is missing,
build it -- it is free and takes one pass:

```sh
growth-engine/.venv/bin/python klantkraan/apps/client-sites/scripts/stock-photos.py zoek <vak> \
  --query "<term>" --query "<term>" --query "<term>" --query "<term>"
```

Aim the queries at **hands, tools, materials and interiors**, never at the vak alone: a bare
"kapper" or "roofer" search returns faces and the wrong continent, which is the whole reason the
picking rule exists. Then **Read `stock/kandidaten/<vak>/contactblad.webp`** and apply that rule
(it is in the script's docstring, read it): no recognisable faces, northern European subject
matter, a hero showing someone at work, varied distance. Read the individual `NN.webp` files for
any candidate you are unsure about -- a face is easy to miss at thumbnail size, and so is a logo
that places the photo on another continent.

Write the seven picks to `stock/sets/<vak>.json` with Dutch alt text per photo (describe the
frame, never who did the work) and your reasoning in `notitie`. Copy the ids **from
`kandidaten.json`, not from the contact sheet by eye** -- transposing a number silently ships a
photo you rejected. Tile order must be TALL WIDE WIDE TALL TALL WIDE; the renderer refuses
anything else. Prefer portrait sources for the tall slots and landscape for the wide, so no crop
fights its own frame. Then:

```sh
growth-engine/.venv/bin/python .../stock-photos.py render --vak <vak>
```

Look at what came out before moving on. Two tiles of the same subject on the same surface read as
filler; that is worth one more `zoek` round, not a shrug.

## c) Write the config

Write `klantkraan/apps/client-sites/clients/<slug>/client.yaml`, slug kebab-case prefixed
`voorbeeld-`. If the dir exists, ask before overwriting. Model it on the tracked fixtures:
`clients/voorbeeld-kapper-rotterdam/client.yaml` for locatie, `clients/voorbeeld-dakdekker/` for
mobiel. Non-negotiable:

- `modus: preview` and `receptionist: false`. Preview mode is what makes the missing KvK, btw-id,
  e-mail, adres and domein legal. Do not invent them to satisfy the schema.
- **No reviews.** A fictional business with testimonials is a fabricated testimonial.
- **No prices** anywhere. The template refuses to render them.
- Phone stays `'+31 6 12 34 56 78'` with the trailing `# voorbeeldnummer (copy-lint-ok)` comment.
- `kleur_primair` must clear 5.25:1 against white or the Zod schema rejects it.
- Dutch copy, u-register, 3-8 diensten, 2-4 usps, 1-5 werkgebied plaatsen.
- `spoed.beschikbaar: false` for most `locatie` vakken. A barber has no emergencies.

## d) Skin

**With reference URLs** -- measure first, it is free:

```sh
cd ai-receptionist
.venv/bin/python -m app.sitestyle --voorbeeld <url> [--voorbeeld <url> ...] --feiten
```

Report per site whether `lettertypes` is non-empty and whether `kop1_px`/`tekst_px` are null. A site
that measures nothing contributes nothing, and that is worth knowing before the call. Then the real
call, adding `--vak <vak> --naam "<Naam>"`.

**Without references** the factory composes one:

```sh
.venv/bin/python -m app.sitestyle --vak <vak> --naam "<Naam>" --kleur <hex> --accent <hex>
```

Paste the emitted block into the yaml at top level. On the reference path, sanity-check it against
the merge rule (`sitestyle.py:751`): shared traits win, and on disagreement the **first** URL wins.
A skin that clearly follows the third reference contradicts the rule -- flag it rather than shipping.

## e) Build, gate, serve

```sh
./scripts/kk site build <slug>     # build + fact gate
./scripts/kk site open <slug>      # the same, then serves it
```

The gate must print `all checks passed`. Notes about a missing e-mail, a stock fallback, or the
voorwaarden placeholder are expected on a preview build, not failures.

`kk site open` blocks -- it is a server. Run it in the background, read the port from the output
(do not assume 4321), and give the user the URL.

## f) Look at it

Open the served page and actually look, at the hero and at the photo band. Lazy-loaded tiles are
blank for a moment, so a blank band means wait and screenshot again, not a bug. On a `locatie`
build also grep the built HTML for the mobiel register, because it is valid Dutch and nothing else
will catch it:

```sh
grep -rl "en omgeving\|wij komen langs\|uw klus\|vrijblijvende offerte" dist/*.html dist/*/
```

Only `dist/voorwaarden/` may match: those terms are trades-shaped and rewriting them is the
founder's call.

## g) Report

Report the slug, the vak and bedrijfstype you chose and why, where the photos came from (curated
now, or an existing set), the resolved `stijl:` block with one line per axis, the gate output, and
the URL. Then STOP.

Never deploy this: `kk site deploy` puts a site on `klant-preview.pages.dev`, which is for real
prospects, not fixtures. Do not commit until the founder has eyeballed it. To revert, delete the
`stijl:` block for the default skin, or `rm -rf` the client dir for all of it. A stock set you
curated is worth keeping either way -- it is the reusable part.
