# Website factory — the tells that survived section R

**Prepared:** 2026-08-16
**Scope:** why sites out of `apps/client-sites/` still read as machine-made, and the smallest
architecture that fixes it. Successor to TODO §R.
**Evidence:** three parallel research passes (AI-tell taxonomy from designer primary sources;
16 real Dutch trade sites across 9 vakken; a full sameness audit of the factory), plus two
fixtures built and looked at in a browser at 1440x900.

---

## 1. What R actually solved, and what it did not

R was right about its own problem. The factory had one look and two hex values; it now has
1728 skins, name-seeded so two prospects in one week cannot collide, self-hosted faces, and a
resolver test over every combination. On the *cosmetic* half of the AI-tell taxonomy the
factory is already clean, and that is worth stating plainly: zero gradients, zero
glassmorphism, zero purple, zero fake statistics, zero motion, zero `<script>`, semantic
markup, real photography, correct contrast. Most generated sites fail on exactly those.

The tells that remain are not paint. They are **bones** and **words**, and the factory has
exactly one set of each.

### Three measurements

**Copy.** Rendered text of `voorbeeld-schilder` against `kk-skintest` (different vak,
different plaats, different skin, same `mobiel` register):

```
6-gram overlap (Jaccard):   26.0%
of A's 6-grams also in B:   41.7%
longest identical run:      35 words
```

Two unrelated prospects receive documents that share 42% of their phrasing, including a
35-word identical passage. For a paying client this is duplicate content across the fleet;
for a voorstel it is what happens when two prospects compare notes.

**Bones.** Every homepage is `Hero → Intro → Diensten → Werk → Werkgebied → Usps → Reviews →
SpoedPanel → FinalCta`, hardcoded as a component list at `src/pages/index.astro:20-28`. No
axis, no vak, no client field reorders it, and preview mode forbids reviews, so **every
voorstel is the identical 8-section scroll.** Real Dutch trade sites run 6-13 sections,
median ~10, in orders that differ by vak.

**Skin is not enough to hide it.** `voorbeeld-kapper-rotterdam` and `kk-skintest` differ on
five of seven axes (grotesk/industrieel, zacht/rond, ruim/normaal, zand/warm,
randloos/ingekaderd). Screenshotted side by side, the two heroes are visibly the same page:
same tracked uppercase eyebrow, same H1 wrapping to four lines, same subline, same button
pair, same photo bleeding right at 46%. The tell moved from "same colours" to "same bones".

### The single loudest line

`src/components/Hero.astro:58` — `{bedrijf.naam}: vakwerk waar u op kunt rekenen.`

The largest text on the first screen is the same sentence for a barber and a dakdekker. It
is also *wrong against the market*: nearly every real Dutch trade site puts vak + plaats in
the H1 ("Timmerman in Waalwijk en omgeving"), which this factory demotes to the eyebrow.

### Where else it is hardcoded

`Duidelijke afspraken, nette afwerking` (Intro.astro:12) · `Onze diensten` · `Waarom {naam}` ·
`Wat klanten zeggen` · `Deze website gebruikt geen cookies en geen trackers.` (Footer.astro:98)
· the entire `/voorwaarden/` and `/privacyverklaring/` documents · and in `lib/toon.ts`, ~15
sentences per register that every site of that register says verbatim, in the same order.

`toon.ts:114` is worth its own line: `Van {d1} en {d2} tot {d3}: …` is a hardcoded rule of
three — the copy tell every detector regexes for — and it produces broken Dutch as soon as a
dienst name contains "en":

> "Van lekkage opsporen **en** verhelpen **en** ontstoppen tot sanitair vervangen"

---

## 2. What real Dutch trade sites do (16 sites, 9 vakken)

The survey killed an assumption the template is built on: that one silhouette fits every vak.

| | bouw/installatie (loodgieter, dakdekker, elektricien, schilder, timmerman, hovenier) | afspraak (kapper, trimsalon, garage, tandarts) |
|---|---|---|
| primary CTA | bel / offerte / gratis inspectie | **afspraak maken** |
| prices | never (at most one indicative m²-prijs) | **prijslijst is a nav item** |
| openingstijden | absent or footer | **on the homepage, as a table** |
| spoed | everywhere, often a second number | only tandarts |
| werkgebied | 8-28 town list, internally linked | **irrelevant** — one address + parkeren/bereikbaarheid |
| photos | the work, before/after, **the bus** | the salon, **the owner's face** |
| keurmerken | VCA, Techniek NL, KOMO, VHG | BOVAG/RDW, KNMT, opleiding |

The factory builds `werkgebied/<wijk>/` pages for a kapper. No real appointment-trade site
in the sample had a werkgebied section at all.

**And the finding that inverts the brief:** *too polished and too complete is itself the
tell.* Every real site is missing something obvious — five of seventeen have no reviews,
FAQs run to two questions, a "projecten" heading sits above no projects, the copyright says
2022. One legitimate twenty-year schildersbedrijf ships a six-section, 50 KB homepage. A
factory that always emits every section, filled and symmetric, is identifiable *because*
nothing is missing.

The other durable human signal is **published friction**: "wij nemen geen plukhonden meer
aan", avondtoeslag 25%, bouwvak-sluiting, om-de-week zaterdag, "bel eerst, wij zijn soms
ambulant". Generated copy is frictionless. Real businesses publish their friction.

---

## 3. The proposal

R already discovered the mechanism that makes variety safe:

> a closed vocabulary of named values → each looked at once on a real build → resolved into
> tokens → asserted by a test over every combination.

It was applied to paint. **Apply it twice more — to bones and to words — and add the one
gate a vocabulary cannot give you: distance from siblings.**

This is deliberately *not* the thing the founder ruled out on 2026-08-15 ("free-form markup
per client cannot be fact-gated, cannot be checked for reflow"). Nothing below generates
markup. Every arrangement is a named value that has been built and looked at once, exactly
like `ritme: ruim`.

### 3.1 `indeling` — the composition vocabulary (bones)

A second block in `client.yaml`, resolved like `stijl:`.

| axis | values | notes |
|---|---|---|
| `volgorde` | `standaard`, `bewijs-eerst`, `spoed-eerst`, `plaats-eerst`, `afspraak-eerst` | pre-verified section permutations, each a named editorial logic |
| `weglaten` | subset of `{intro, werkgebied, usps, werk}` | the counter-intuitive axis: which sections this site does **not** have |
| `hero` | `gesplitst-rechts` (today), `gesplitst-links`, `plaat`, `typografisch`, `gestapeld` | `typografisch` = no photo, USP bullets — a third of real sites |
| `diensten` | `kaarten` (today), `lijst`, `index`, `met-foto` | the 3-card grid is the single most-flagged AI component |
| `nadruk` | `slot`, `spoed`, `werk`, `geen` | which one section gets the big colour moment |

Cost is low because the seams already exist: `index.astro` is pure composition, no component
takes layout props, `Werk` and `Reviews` already drop out when empty, and `resolveStijl` is a
spread of per-axis records that `Base.astro` writes onto `<html>` unread. A `secties:` list
is a ~15-line change to `index.astro` alone.

**`indeling` is chosen from `vak` + `bedrijfstype` first, seed second.** Structure should
follow the business (that is the whole finding of §2); the seed only picks among the
arrangements that are plausible for that vak. A per-vak profile table (`bouw` / `afspraak` /
`portfolio`) is the input, and it replaces `bedrijfstype` as the thing that drives more than
copy.

### 3.2 `stem` — the copy vocabulary (words)

Three levels, in order of value:

1. **Frames, not sentences.** The H1 slot gets a closed set of named frames — `vak-plaats`
   (what real sites do), `belofte`, `naam-vak`, `vraag` ("Dak lek?"). The frame is the
   vocabulary; the words come from the copy call. Same for the intro heading and slotkop.
2. **Extend the sitedraft schema** with `kop`, `introkop`, `slotkop`, and — where the sources
   support it — one `huisregel`, the operational friction that reads human.
3. **Keep today's strings as one named value** (`stem: standaard`), so the `mobiel` register
   stays byte-identical for the live clients whose test pins it (`toon.test.ts:120-133`).
   Exactly the `STANDAARD_STIJL` trick.

And delete the tricolon at `toon.ts:114`/`:81`.

### 3.3 `bewijs` — turning the honesty constraint into the differentiator

A voorstel may invent no KvK, no keurmerk, no year, no review, no price. That is
non-negotiable and it is why a generated voorstel will always be thinner than a real site.

So make the missing things **designed, labelled slots** rather than absences: in preview mode
a `bewijs` block renders "hier komen uw keurmerken / uw KvK / uw eigen foto's" as an
intentional part of the layout — which is simultaneously the sales pitch — and in live mode
it fills from `client.yaml`. The one thing a competitor's generated voorstel cannot copy is
an honest empty slot that says what goes in it.

### 3.4 The new gate: `kk site check --vloot`

Vocabularies create variety. Only a gate keeps it. On every build, against every other
client:

- **copy distance** — 6-gram Jaccard over rendered text; fail below threshold
- **silhouette signature** — `volgorde` + `weglaten` + `hero` + `diensten`; fail on an exact
  match with any sibling in the same vak
- **skin distance** — Hamming over the 7 axes + OKLab hue distance on the primary

Print the nearest sibling and the number, every time. Today that number is 42% and nobody
knew, because nothing measures it. Variety that is not measured decays back to the default
within a month.

### 3.5 `scripts/tell-lint.sh`

A `copy-lint.sh` sibling, same shape (grep-only, `# tell-lint-ok` opt-out), over `dist/`:

`tricolon` (Van X en Y tot Z, adjective triads, `<ul>` with exactly 3 `<li>`) ·
`parallel-koppen` (all H2s are 1-3-word noun phrases) · `eyebrow` (the tracked uppercase
label on more than one section) · `wees-kaarten` (orphan row: 5 cards in a 3-column grid) ·
`vulwoorden` (Dutch buzzword list) · `offerte-dichtheid` ("vrijblijvende offerte" more than
once) · `vloot-kop` (an H2 set identical to another client's).

### 3.6 Free fixes, worth doing regardless

- **`--brand-accent` is dead.** Schema-required, contrast-gated, fed to the composer, written
  onto `<html>` — and read by no component. A whole differentiation channel evaporates
  silently. Either spend it or drop it from the schema.
- **The eyebrow** (`tracking-[0.18em] uppercase`) is duplicated verbatim in `Hero.astro:54`
  and `Werk.astro:79`, is immune to all seven axes, and sits above the tracking threshold
  detectors flag. It is the most distinctive micro-typographic gesture on the page and it is
  a constant.
- **`max-w-5xl` appears as a literal 19 times.** Measure width is the thing reference sites
  differ on most and it has no token.
- **Cream paper is now on the detector lists** (`zand` #f5f1ea, `warm` #faf9f7 — weight 7/8 on
  slop-detect, because it is the model's learned move when told "not purple"). Not a panic;
  the counter-move is a neutral tinted with a few percent of the client's own hue, which the
  factory can compute and a detector cannot pattern-match.

---

## 4. The skill (`/example-site`) — rewritten around decisions

The current command is a good runbook: it tells the agent which commands to run and what to
look at. It cannot deliver a non-templated site, because the templating is in the factory,
not in the prompt. Once §3 lands, the skill changes shape — from steps to **decisions,
declared before the build and checked after it**:

1. Choose the **vak profile** (`bouw` / `afspraak` / `portfolio`) and say why. This now drives
   structure, not only copy register.
2. **Declare the omissions up front.** "This site will have no werkgebied section and no
   reviews, because a kapper's customers do not travel and real kapper sites do not have
   them." A build that ships every section must justify it.
3. Build, then run `kk site check --vloot` and **report the three distance numbers**, with a
   hard stop when a sibling is too close.
4. Run `tell-lint`.
5. Look at the page against a **named list of the tells the factory can still produce** —
   not "actually look", which is unfalsifiable.
6. Close with one judgement, in words: *would a Dutch trade owner believe a person made
   this?* — and the reason.

---

## 5. Order of work

Each step is independently shippable and independently verifiable, Ralph-style.

| # | step | why first |
|---|---|---|
| 1 | `--vloot` distance check + `tell-lint` | measures the problem before changing anything; the 42% becomes a regression test |
| 2 | H1 frames + kill the tricolon (`stem`, minimal) | biggest visible win, smallest diff, no layout risk |
| 3 | vak profiles + `weglaten` | omission is cheaper than new layout and buys more credibility |
| 4 | `hero` + `diensten` variants | the two components a viewer reads first |
| 5 | `volgorde` + `nadruk` | needs 1-4 in place to be judgeable |
| 6 | `bewijs` slots | sales value as much as design value |
| 7 | rewrite `/example-site` around the above | the skill can only gate what exists |

Steps 1 and 2 together already move the copy number below 15% and remove the two loudest
tells. Everything after that is compounding, not corrective.

---

## 6. What must not break

From the audit, all still binding: the fact gate's exact link sets, zero external hosts and
zero executable `<script>`, one `<h1>` per page, the skin travelling as one inline style on
`<html>` identical across pages, 13 contrast pairs at AA, tints mixed over `--color-card`
never `--color-paper` (R6b), `kleur_primair` ≥ 5.25:1 mirrored in `sitedraft.py:223`, diensten
3-8, usps 2-4, werkgebied ≤ 5, reviews forbidden in preview, the verbatim preview banner,
`NAAM_MAX_GROOT = 34`, tile order TALL WIDE WIDE TALL TALL WIDE, and the `mobiel` register
pinned verbatim because it is live on paying clients.

The 1728-combination sweep in `stijl.test.ts` is the template for how `indeling` gets tested:
every axis must move something, no two axes may write the same property, and every
combination must keep the call button above the fold at 1000px.

---

## 7. The one decision that needs the founder

§3.1 revisits the 2026-08-15 ruling that the reference drives the skin only and layout stays
fixed. The reasons given then were: free-form markup cannot be fact-gated, cannot be checked
for reflow, and grows the by-eye stage.

A closed composition vocabulary answers all three — it is gated by the same
`verify-site.mjs`, swept by the same test pattern, and *shrinks* the by-eye stage because
`--vloot` replaces "does this look like the last one?" with a number. It is the argument that
justified the skin vocabulary, applied one level up.

The founder's call is how far: omission and copy frames only (steps 1-3, low risk, most of
the win), or the full composition vocabulary (steps 1-6).
