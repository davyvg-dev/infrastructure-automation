---
description: Build an example client site for any vak, with stock photos curated on demand
argument-hint: [vak] [plaats] [optional: 1-3 reference URLs you like the look of]
---

Build an example site for: $ARGUMENTS

A throwaway demo of the website factory: a fictional business, built locally, never deployed.
`example-site barber rotterdam` is a complete instruction. Do not come back with questions the
steps below already answer; the only thing worth stopping for is a genuine conflict in the request.

Ralph rule: verify every step before the next; any failure stops the line.

**What this command is for.** Not "a site that builds". A site a Dutch trade owner would believe
a person made. The factory now measures that in two numbers (§f) and they are the acceptance
criteria, not decoration: a build that passes the fact gate and fails those is a failed build.

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
  does not collide with a real firm, and stays **under 34 characters**.

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

## c) Decide what this site is NOT

Do this before writing a line of yaml, and put the answer in the report.

Sixteen real Dutch trade sites were read for `research/PLAN-site-factory-anti-template-2026-08-16.md`.
They run 6-13 sections and **every one of them is missing something obvious**. A site that ships
every section, filled and symmetric, is identifiable precisely because nothing is missing. So
choose up to two of `intro`, `werk`, `werkgebied`, `usps` to leave out, and justify each from the
business rather than from variety:

- **`locatie` vakken should usually drop `werkgebied`.** No kapper, trimsalon or tandarts in that
  survey had one; those businesses publish an address and how to reach it. The wijk pages and the
  footer column stay either way.
- Drop `usps` when the same three claims are already in the running copy. Saying it twice is how
  a template fills a page.
- Drop `intro` when the vak sells by showing rather than explaining (hovenier, timmerman).
- Keep `werk` unless the stock set is thin. It is the section that does the most work.

Two is the cap; the schema enforces it. Dropping nothing is a legitimate answer for a
`mobiel` bedrijf with a lot to say -- but say that you chose it.

## d) Write the config

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

### The `teksten:` block is the whole job

Eight optional slots -- `kop`, `belofte`, `intro_kop`, `werkwijze`, `bereik`, `diensten_tekst`,
`slot_kop`, `slot_tekst` -- each falling back to a register default in `src/lib/toon.ts`. Leaving
them out is legal and it is also how two sites end up sharing forty words. Write all eight.

`kop` is the H1, the largest text on the screen: 70 characters at `schaal: groot`, 90 below it
(the schema will tell you). Name the vak and where they are, or something concrete this business
does. Never the company name -- it is already in the header two centimetres above.

The rest is one rule: **write the sentence only this business could have written.** A dak is not
judged from the pavement. A verstopping sits two metres from where you think. A barber's customer
does not want to stand holding a coat. That kind of line cannot be lifted onto another site,
which is exactly the property being bought.

And do not write, ever:

- a rule of three (`Van X en Y tot Z`, three adjectives in a row, three parallel bullets)
- headings that are all two-word noun phrases -- mix a statement, a question and a label
- Title Case in a Dutch heading
- "jarenlange ervaring", "kwaliteit staat voorop", "op maat", "uw betrouwbare partner"
- em-dashes
- anything not derivable from the diensten, openingstijden and werkgebied you just wrote: no
  years, no keurmerken, no guarantees, no company history. A fictional business has no history.

## e) Skin

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

## f) Build, gate, measure

```sh
./scripts/kk site build <slug>                    # build + fact gate
./scripts/kk site check <slug> --vloot --tells    # distance from the fleet + the tell linter
```

The fact gate must print `all checks passed`. Notes about a missing e-mail, a stock fallback, or
the voorwaarden placeholder are expected on a preview build, not failures.

Then the two that decide whether this was worth building:

- **`--vloot`** prints the copy overlap, skin distance and silhouette signature against every other
  site the factory has made. **Over 15% copy against any sibling is a failed build.** Do not
  lower the threshold; go back to §d and write sentences instead. The number moves a long way for
  a small amount of honest writing -- a fixture went 23.8% to 5.8% on eight slots.
- **`--tells`** must come back `schoon`. Each rule names the tell it caught; fix the copy, not
  the rule.

`--vloot` runs first and stops the line if it fails, so run `--tells` on its own when that happens.

## g) Look at it

```sh
./scripts/kk site open <slug>
```

It blocks -- it is a server. Run it in the background, read the port from the output (do not assume
4321; the marketing site often holds it), and give the user the URL.

Open the page and actually look. Lazy-loaded tiles and the hero are blank for a moment, so a blank
band means wait and screenshot again, not a bug. Then check these by eye, because no gate can:

1. Is the call button above the fold at 1440x900? A four-line H1 is the usual cause.
2. Does the photo band show two tiles of the same subject on the same surface?
3. Does the dienst grid leave one card alone on the last row?
4. Read the H1 and the first paragraph aloud. Could they sit on a competitor's site unchanged?

On a `locatie` build also grep the built HTML for the mobiel register, because it is valid Dutch
and nothing else will catch it:

```sh
grep -rl "en omgeving\|wij komen langs\|uw klus\|vrijblijvende offerte" dist/*.html dist/*/
```

Only `dist/voorwaarden/` may match: those terms are trades-shaped and rewriting them is the
founder's call.

## h) Report

Report the slug, the vak and bedrijfstype and why, **which sections you left out and why**, where
the photos came from (curated now, or an existing set), the resolved `stijl:` block with one line
per axis, the gate output, **the three `--vloot` numbers and the nearest sibling**, the `--tells`
result, and the URL.

Close with one judgement in your own words: **would a Dutch trade owner believe a person made
this?** Give the reason. If the answer is no, say what is wrong with it rather than shipping it
with a caveat. Then STOP.

Never deploy this: `kk site deploy` puts a site on `klant-preview.pages.dev`, which is for real
prospects, not fixtures. Do not commit until the founder has eyeballed it. To revert, delete the
`stijl:` block for the default skin, or `rm -rf` the client dir for all of it. A stock set you
curated is worth keeping either way -- it is the reusable part.
