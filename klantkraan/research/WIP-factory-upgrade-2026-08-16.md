# WIP — website factory upgrade (award craft + editability), 2026-08-16

Founder ask, verbatim: award-level design as the factory default, reachable by running
`/example-site`; and **every delivered site must be editable by the founder and the client
without breaking existing functionality** ("that last point is crucial").

Live state so this survives a context clear. Delete when §T lands in TODO.md.

## Baseline, measured

Built `voorbeeld-kapper-rotterdam` and looked at it at 1440x900. The paint is good; the
bones are timid. What the screenshots showed:

1. **A right-hand void on every text section.** Intro/Diensten/Werkgebied set an H2 and a
   paragraph at `max-w-2xl`/`3xl` inside a centred `max-w-5xl` column, so the right ~40% of
   a 1440 screen is empty on section after section. This is the single loudest composition
   flaw and no skin axis could reach it.
2. **The H1 wraps to four lines** in the 46% hero column (`text-wrap: balance` splits it
   evenly), pushing the call button to ~745px — above the fold only just, and only because
   the preview banner is 70px.
3. **The two hero buttons stack** instead of sitting side by side: the column is too narrow.
4. **No editorial detailing anywhere** — one eyebrow on one section, no rules, no numerals,
   no captions, no asymmetry. Nine sections of heading-paragraph-grid.
5. The photo band (mixed 2:3 / 3:2 masonry, bleeding) is the best thing on the page and
   should be the model for the rest.

## Done

- **`stijl.maat` — the measure axis.** `max-w-5xl` appeared as a literal 19 times and no
  axis could move it. Added `--maat-kolom` / `--maat-band` / `--maat-kop` / `--maat-tekst` /
  `--maat-gutter`, three values (`smal` / `normaal` / `breed`), and replaced every literal
  in components, pages and layouts. `normaal` is exactly the old 64/72/42/48rem + 1.5rem
  gutter, so an existing client.yaml builds the same bytes. `--foto-kolom` now spends
  `var(--maat-band)` instead of a pinned 72rem, so the framed photo band cannot end up
  narrower than the column it interrupts at `maat: breed`.
  Files: `src/lib/stijl.ts`, `src/lib/client.ts`, `src/styles/global.css`, `src/lib/stijl.test.ts`,
  all of `src/components/`, `src/pages/`.
  Tests: 42 pass, sweeping all 5184 combinations (was 1728).
  A test caught a real design error mid-write: the first values grew the prose measure as
  fast as the container (40→50rem), which is how a "roomier" site becomes a harder one to
  read. `--maat-tekst` now stops at 48rem (~90 characters) and the extra width goes to the
  margins and the photographs instead.

## Next, in order

1. **The CSS floor** (concrete, researched, not yet applied) — see the findings below.
2. **Client photo pipeline + named roles** (task #2). The biggest editability hole.
3. **Composition vocabulary** (task #3): hero + diensten variants, `volgorde`, `nadruk`.
4. **Craft pass** (task #4) — blocked, the two design-research agents died on the session
   limit and must be re-run.
5. **Editing story** (task #5) — research is in, decision below.
6. **Rewrite `/example-site`** (task #6) and run it end to end.

## Research landed (agents completed)

### The CSS floor — three defects worth fixing regardless of anything else

- `text-wrap: balance` **silently switches itself off past six wrapped lines in Chromium**
  (ten in Firefox). It is inert on exactly the headlines that have a problem, and it never
  prevented a pixel of overflow — Chrome's docs: balancing "won't change the inline-size of
  the element". So it is polish, not a floor.
- `global.css` gives `h1,h2,h3` **`text-wrap: balance` and nothing else**. No
  `overflow-wrap`, no `hyphens: auto`, despite `<html lang="nl">` being set in Base.astro,
  which means hyphenation would work today for free. A 40-character kop containing
  `rioolontstoppingsservice` (24 unbreakable characters) overflows at 360px right now, and
  the 70-character schema gate cannot see it — the thing that breaks a Dutch hero is one
  compound, not the total length. The marketing site already does `break-words
  hyphens-auto`; it never made it into the factory.
- `--text-h1: clamp(1.9rem, 4.5vw, 3rem)` is a **bare `vw` in the preferred term**, which is
  the WCAG 1.4.4 resize-text failure. Needs a `rem` in the middle: `clamp(1.9rem, 1.2rem +
  3.2vw, 3rem)`. Every step of every schaal has the same shape.
- The hero's text column needs `min-width: 0` and its grid `minmax(0, 1fr)`, or
  `overflow-wrap` cannot help — a flex/grid item defaults to `min-width: auto` and refuses
  to shrink below its longest word. The marketing site does this; the client-site Hero does not.

Division of labour, which is the useful framing: **CSS answers "will the page still
function"; a length limit answers "will the page still be good".** Neither substitutes for
the other. The repo already does the second part well (`teksten.kop` gated at 70/90 chars,
measured in-browser rather than guessed) and is missing the first.

### Editing story

Every option was researched against "a 52-year-old loodgieter must change his opening hours
and swap a photo, and must not be able to break the site".

- **Sveltia CMS** — much the better software (976 commits in 6 months vs Decap's 76 human
  ones, in-browser WebP conversion + resize on upload, `max_file_size`, PWA phone editing).
  **Disqualified on auth**: GitHub/GitLab/Gitea account required, git-gateway explicitly
  unsupported, custom backends closed "not planned", no email or magic link. A tradesman
  will not create a GitHub account. Its Cloudflare Worker is only an OAuth relay, not an
  identity provider.
- **Decap + DecapBridge** ($9/mo, free for 3 sites) — the only combination with email-invite
  and password login. But **no image resize at all**: a 12MB phone photo lands in the repo
  at 12MB.
- **Pages CMS** — email OTP invites genuinely work (verified in its source: the collaborator
  never gets a GitHub account, writes go through the App installation token). But: no image
  optimization, an open unfixed 413 on normal phone photos on the hosted app, needs
  Node + Postgres to self-host, **no preview and no PR flow at all**, bus factor 1, and an
  unanswered GDPR DPA question on the hosted instance.
- **Both Decap and Sveltia destroy YAML comments.** Proven at source level — both rebuild
  the file from a plain JS object rather than round-tripping a Document. Measured against
  `voorbeeld-kapper-rotterdam/client.yaml`: **47 comment lines and 12 blank lines out of
  122 (39%)** would be deleted on the client's first save, including the header explaining
  why preview mode legally omits KvK/btw. Decap can regenerate comments from a `comment:`
  property in its own config; Sveltia cannot.

**Where I have landed, to be built rather than bought:** generate the form from the Zod
schema we already have. `zodToJsonSchema(ClientSchema)` was verified to produce a clean
4,954-byte draft-07 schema covering all 13 top-level fields including the `openingstijden`
tuple. That keeps **one source of truth**, writes the YAML with our own serializer (so the
comments survive), and lets the same schema that gates the build gate the form. The schema
uses `.describe()` zero times today — adding descriptions is the cheapest possible upgrade
to how self-explanatory that form is.

### Deploy / hosting facts that constrain the above

- Cloudflare Pages is **not** deprecated (the "maintenance mode" claim is a community
  paraphrase of one April-2025 blog sentence). Cap is 100 projects/account; Workers is 500.
- **GitHub Actions is free at this scale** — 150 builds/month is ~450 of 2000 free minutes;
  it stays free to roughly 220 client sites.
- **A push written with a GitHub App installation token does trigger `on: push`** — no
  `repository_dispatch` needed. Watch the secondary limit (80 content-generating requests
  per minute), not the hourly one.
- **`/cdn-cgi/image/` does not work on `*.pages.dev`** — image transformations need a real
  custom domain on a Cloudflare zone. Relevant to any client-upload resize plan.
- **Pages cannot promote a preview to production without re-uploading**; there is no promote
  endpoint and rollback only targets prior production deployments. Workers can
  (`versions upload` → stable preview URL → `versions deploy`). If "client approves before
  it goes live" matters, that is the one real argument for Workers Static Assets — against
  it, Workers cannot serve custom domains outside Cloudflare zones, which tradesmen keeping
  their domain at their own registrar will need.
- Cloudflare Access + one-time PIN is €0 up to 50 users, but seats never auto-free.

### Still missing — MUST RE-RUN

Both design-research agents died on the session limit:

- **award craft** (Awwwards/FWA/CSSDA/Godly winners, measured: H1 px, body px, measure in
  ch, section padding, colour count, font pairings, cheap CSS motion, template tells).
  Intended output `research/award-craft-2026-08-16.md` — never written.
- **trade-site craft** (best-in-class loodgieter/dakdekker/kapper sites, NL specifics,
  above-the-fold structure, the beautiful-vs-converting tension). It wrote
  `research/trade-site-craft-2026-08-16.md` before dying — **check whether it is complete**
  before re-running.

## Housekeeping

- `clients/zz-breaktest/` is a research agent's schema stress fixture (contains an emoji
  dienst name on purpose). Gitignored. Delete or keep deliberately.
- `dist/` was overwritten by that agent's build, so any "compare against baseline" must
  rebuild first. Baseline copy of the kapper build:
  `<scratchpad>/baseline-kapper`, served on :8934.
