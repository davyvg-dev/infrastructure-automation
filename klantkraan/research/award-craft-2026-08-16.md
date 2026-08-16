# Award-craft, measured — what actually makes a site look award-winning

Research date: 2026-08-16
Purpose: encode transferable craft into the Klantkraan static-site factory (Astro, near-zero JS, Dutch trade businesses).
Method: fetched the real HTML and every linked stylesheet of **16 award sites** (Awwwards SOTD / Honourable Mention / nominee, weighted toward architecture, construction, interiors and hospitality — the categories that transfer), resolved CSS custom properties transitively, and evaluated `clamp()` / `calc()` / `vw` **at a 1440px viewport**. Then ran the identical detector over a **control group of 11 real Dutch loodgieter and dakdekker sites** taken from this repo's own outreach lists, so every claim below is a measured gap between two populations rather than an assertion. Findings were then cross-checked against independent 2025–2026 studies (n=1,590 and n=47) and against Baseline/webstatus.dev platform data. No gallery blurbs were used as evidence.

Constraint that shapes every recommendation: **static Astro output, near-zero JS, fast on Dutch mobile, editable by a non-technical owner.** WebGL, Three.js, scroll-jacking, custom cursors and heavy motion are excluded by fiat. What follows is the craft that survives that exclusion.

---

## The 10 moves

Ranked by leverage. Every number is measured from the reference table below; every implementation line is CSS that ships in a static Astro build with no runtime JavaScript.

### 1. Fluid display type — big, tight, and negatively tracked
Display type at 1440 runs **96–192px** (median ≈ 130px; belgradearbor.rs hits 320px). Line-height goes **below 1**: ciaoenergy.com sets `0.8`, 2xa.studio `0.9`, schyns.de and smeulders-ig.nl `1.0`. Tracking is **negative** — `−0.012em` (tandjungsarihotel), `−0.015em` (2xa), `−0.024em` (era-residence), `−0.03em` (revelatio), up to `−3px` (purnatur). The single commonest amateur error is a 40px heading with `+0.1em` tracking, which is exactly what reliablepaving.com does.

> `h1{font-size:clamp(2.5rem,9vw,8.5rem);line-height:.95;letter-spacing:-.02em;text-wrap:balance}`

### 2. Cap the *line*, not the container — and cap it in `ch`
schyns.de is the only site in the set that authors this explicitly, and its ladder is the whole lesson: **12ch, 16ch, 18ch, 20ch, 25ch** for display and standfirst lines, **44ch and 48ch** for prose. Across the rest of the set, derived prose measure lands **48–64ch**. That is *narrower than the textbook 66–75ch*. Narrow measure is most of why editorial layouts feel considered — the ragged right edge becomes a shape rather than an accident.

> `.lede{max-width:22ch}  .prose{max-width:46ch}  h1{max-width:14ch}`

### 3. Warm paper and near-black ink — and no more than six authored colours
The dominant page ground on the strongest sites is never `#ffffff`: `#f5f4f0` (kellerstoeckl), `#f5f3ed`/`#eae7dd` (schyns), `#f3f0ed`/`#e6d8cc` (verostudio), `#f1ecde`/`#fffbf2` (tandjungsari), `#fff4d6`/`#fdfbef` (belgradearbor), `#f1eae1` (250broadway), `#f7f7f7` (purnatur). Ink is near-black, not black: `#141312`, `#111`, `#181615`, `#252f51`. Authored palette size at the top end is **4 colours** (as-associates.jp) to **15** (schyns, 250broadway). Against a trade-control median of **108**.

> `:root{--paper:#f4f1ec;--ink:#16150f;--accent:#b4471f}  body{background:var(--paper);color:var(--ink)}`

⚠️ **Caveat that changes how you apply this.** Warm paper is measurably right *and* has become the second-wave generated-design default. The AI-design field guide lists "**Cream and beige 'tasteful' palette** — warm cream page background, often with an amber accent" as an active, *rising* tell, explicitly "the second-wave default that appeared after purple gradients became a public joke", and its rule reads: "do not fall back to emerald or cream just because purple is off the table. Those are the second-wave defaults now." It also documents an **"emerald fallback"** — when a prompt bans purple, models cascade to `#10B981`, sometimes overriding explicit instructions ([signs-of-ai-design](https://github.com/febbhav/signs-of-ai-design), pattern #26 in the [impeccable.style catalog](https://impeccable.style/slop/)). So: warm neutral ground yes — **cream + amber, no**. The accent must be derived from the client's actual trade and material, which is what Strategy B below does.

### 4. Build the neutrals as one ink at alpha steps
as-associates.jp defines its entire grey ramp as a single black at five opacities — `--color-b5:#0000000d; --b20:#0003; --b40:#0006; --b60:#0009; --b100:#000`. This is why four colours are enough: every rule, caption, border and disabled state is the *same* ink, so the page cannot go out of tune. It also makes the ramp automatically correct on any ground colour you swap in — critical for a factory that reskins per client.

> `--ink-10:color-mix(in srgb,var(--ink) 10%,transparent)` — or literal `#16150f1a` for wider support.

### 5. A named spacing ladder of 7–8 fluid steps
ciaoenergy.com publishes the cleanest one measured, eight clamps resolving at 1440 to **24 / 32 / 48 / 64 / 80 / 96 / 112 / 160px**. Others: k95.it `60 / 80 / 160`, 2xa.studio `90 / 180 / 225`, for-living.it `8/16/24/32/40/48/64/80`, 250broadway `80 / 120`. Section padding at desktop clusters **80–160px**; editorial outliers run 225–360px. Ratio between adjacent steps is **1.25–2**, never uniform. Note schyns.de's variant: every utility is a *range*, named `mt-vw-40-to-60`, `gap-vw-6-to-8` — the value is fluid by construction.

> `--s5:clamp(3rem,3.5vw,5rem); --s7:clamp(4.5rem,6.5vw,10rem)`  then `section{padding-block:var(--s7)}`

### 6. A real 12-column grid, asymmetric spans, one deliberate bleed per page
`repeat(12,1fr)` is the house grid — cobloc.archi uses it 27 times, 2xa.studio 16 (plus `subgrid`, which appears **nowhere** in the control group). What makes it read expensive is that items get *explicit, unequal* spans: cobloc puts a section label at `grid-column:1/5` and its body at `6/-1`; era-residence places blocks at `grid-area:1/4/2/6` and `1/3/2/7`. Then exactly one element per page breaks the container: cobloc's gallery is `width:calc(100% + 2rem); margin-left:-1rem; margin-right:-1rem`.

> `.sec{display:grid;grid-template-columns:repeat(12,1fr);gap:var(--s2)} .sec>h2{grid-column:1/4} .sec>.body{grid-column:5/-1}`

### 7. The numbered sticky section header
The highest-value single pattern in the study, lifted verbatim from cobloc.archi. It delivers five "expensive" signals at once — numbering, mono numerals, a hairline rule, an asymmetric grid, and a sticky column header — in about eight lines of CSS and zero JavaScript.

```css
.sections { counter-reset: sec; }
.section  { display:grid; grid-template-columns:repeat(12,1fr); gap:.5rem;
            padding-block:3rem; border-top:1px solid rgb(0 0 0 / .08);
            counter-increment: sec; }
.section__title { grid-column:1/5; grid-row:1; align-self:start;
                  position:sticky; top:calc(var(--header-h,0px) + 1.5rem); }
.section__title::before { content:counter(sec, decimal-leading-zero);
                          display:block; margin-bottom:.75rem;
                          font-family:var(--font-mono); font-size:.75rem; }
.section__body  { grid-column:6/-1; }
```

### 8. Mono for every piece of metadata
The recurring type system is **grotesk + editorial serif + mono**, and the mono is not decoration — it is the metadata voice. 2xa.studio sets `a, button, .button { font-family: var(--font-mono) }`; cobloc sets its section numerals in DM Mono at `.75rem`; ciaoenergy and alethia.earth pair Geist with Geist Mono. This is where **positive** tracking is correct — small mono labels at 11–13px take `+0.02em` to `+0.06em`, the opposite of the display rule. For a trade site the mono carries: KvK number, opening hours, service-area list, phone number, section numbers, photo captions, form labels.

> `.meta{font-family:var(--font-mono);font-size:.75rem;letter-spacing:.04em;text-transform:uppercase}`

### 9. Photography: portrait and bespoke ratios, square corners, one grade
Reading the CSS in context settles this: `aspect-ratio:1` on award sites lands on icons, buttons, checkboxes and logos — **not on photos**. The photo ratios are portrait or bespoke: `3/4` (era-residence, cobloc), `2/3` (ciaoenergy's `.aspect-ratio-portrait`), `3/3.5` and `5/4` (schyns), `17/21` and `144/168` (era-residence), `640/275`, `350/406`, `580/677`. Bespoke denominators mean the ratio came from the *crop*, not a preset. And `border-radius` on a photo element: award median **0**, trade median **5**. Captions are real `<figcaption>`s set in the mono, offset to one side rather than centred under the image.

> `figure img{aspect-ratio:3/4;object-fit:cover;border-radius:0;filter:saturate(.92) contrast(1.04)}`

### 10. One easing, two durations — and a CSS-only scroll reveal
The award set converges on **expo/quint out**: `cubic-bezier(.16,1,.3,1)` (kellerstoeckl, tillbergdesign), `cubic-bezier(.19,1,.22,1)` (cobloc, verostudio `--ease-out-expo`), `cubic-bezier(.22,1,.36,1)` (schyns, k95), `cubic-bezier(.165,.84,.44,1)` (verostudio). tandjungsarihotel.com uses **one** easing site-wide, `cubic-bezier(.24,.43,.15,.97)`. Durations are bimodal: **150–300ms** for hover/micro, **600–800ms** for reveals, and kellerstoeckl runs 2400ms cross-fades.

Support, checked two ways on 2026-08-16 because **the two sources disagree and the disagreement matters**:

| Feature | caniuse | webstatus.dev / Baseline | Verdict |
|---|---|---|---|
| `@starting-style` | 90.65% | **Baseline newly available** since 2024-08-06; WPT 1.0 Chrome/Safari, 0.889 FF | **Safe to ship** |
| `transition-behavior: allow-discrete` | 90.7% | **Baseline newly available** 2024-08-06; **WPT 1.0 in every engine** | **Safe to ship** — cleanest interop in the set |
| `animation-timeline` (scroll-driven) | 85.43%, "Firefox 156" | **Baseline: LIMITED.** Firefox WPT stable **0.094** — implemented behind a flag, not shipped; Bugzilla [1324602](https://bugzilla.mozilla.org/show_bug.cgi?id=1324602) ("let it ride the trains to release") **REOPENED 2026-07-06**. Chrome 115, Safari 26. Used on **5.49%** of Chrome page loads | **Progressive enhancement only**, behind `@supports (animation-timeline: view())` |
| View Transitions, same-document | — | **Baseline newly available** 2025-10-14 (Firefox 144 landed last). ⚠️ Chrome-Android WPT only 0.253 | Usable; test on Android |
| View Transitions, cross-document (MPA) | — | **LIMITED** — Firefox WPT 0.054 | Degrades to a normal navigation, so harmless, but ~⅓ of EU visitors never see it |

Treat caniuse's Firefox figure as optimistic: it counts a version that has the flag, not the shipped default. Roughly **a third of Dutch traffic (Firefox + older Safari) must get the un-animated state**, which is why the reveal has to be additive rather than an opacity-0 default.

> `@media (prefers-reduced-motion:no-preference){.reveal{animation:rise linear both;animation-timeline:view();animation-range:entry 10% cover 35%}}`

### Two more that cost nothing
- **`mix-blend-mode: difference` on a sticky caption.** 2xa.studio pins `.subtitle` and `.footer` at `position:sticky; bottom:0; mix-blend-mode:difference` so the label inverts against whatever scrolls beneath it. One declaration, reads as a bespoke build. Present in the award group, **absent from all 11 control sites**.
- **A thin inset frame.** era-residence builds a decorative viewport frame from eight pieces (`frame_lt`, `frame_t-lr`, `frame_rt`, …). A single `outline`/`border` inset a few rem from the viewport edge gets 80% of it.

---

## Measured reference table

How these numbers were obtained: each site's HTML and every linked stylesheet were fetched, CSS custom properties were resolved transitively, and `clamp()` / `vw` / `calc()` were evaluated **at a 1440px viewport**. So "H1 px" is the real rendered size at 1440, not the token. Values marked ~ are derived (measure in ch ≈ `max-width` ÷ 0.5 × body-size, the standard grotesk approximation) rather than authored.

Award status verified against each site's Awwwards page (SOTD = Site of the Day, HM = Honourable Mention, NOM = Nominee).

| URL | What it is / award | H1 px @1440 | Body px | Measure | Section pad | Font pairing | Unique hex in CSS | Standout move |
|---|---|---|---|---|---|---|---|---|
| [kellerstoecklarchitektur.at](https://www.kellerstoecklarchitektur.at/) | Austrian architecture practice — Awwwards **HM** | — (no display h1; type maxes ~24px) | **11px** | ~60ch | 20–24px | Helvetica only, one weight (400) | **5** (`#111 #f5f4f0 #333 #dddbd7 #999`) | The whole site is 11px Helvetica on `#f5f4f0` warm paper with a `repeat(10, var(--tile))` modular grid. Restraint *is* the design. 2400ms fades, `cubic-bezier(0.16,1,0.3,1)`. |
| [cobloc.archi](https://www.cobloc.archi/) | French architecture studio — Awwwards **HM** | 96px, lh 1.3 | 20px, lh 1.6 | ~60ch (600px) | 120px | Ivory LL (serif) + Funnel Sans + **DM Mono** | 51 (but only ~6 authored: `#fff #000 #a6a6a5 #333 #fbd600`) | 12-column grid used 27 times — an actual grid, not a flex row. Single acid-yellow `#fbd600` accent against black/white. |
| [schyns.de](https://www.schyns.de) | German construction/interiors — Awwwards NOM | **172.8px** (`12vw`), lh 1.0, ls `.01em` | 14px (`--text-sm`) | **authored in ch: 12 / 16 / 18 / 20 / 25 / 30 / 44 / 48ch** | 16–227px | Aspekta Variable (`100 900`) + Helvetica Neue + AnotherPassion (script, accent only) | 15 | Text is capped in **`ch`, not px** — 12ch for display lines, 44–48ch for prose. Warm neutral system: `#f5f3ed` pearl, `#eae7dd` beige, text `#252f51` (blue-black, never `#000`). |
| [as-associates.jp](https://as-associates.jp) | Japanese architecture — Awwwards NOM | — | 16px, lh 1.5, ls `.02em` | 12-col `minmax(0,1fr)` | — | **Unica 77 LL only**, weights 300 + 400 | **4** (`#fff #1f2c9a #000 #424242`) | Four colours, one typeface, two weights. Neutrals built as alpha ramps off one ink: `--color-b5 #0000000d`, `b20 #0003`, `b40 #0006`, `b60 #0009`, `b100 #000`. |
| [tandjungsarihotel.com](https://www.tandjungsarihotel.com/) | Bali heritage hotel — Awwwards NOM | 40px, lh 1.15, ls `-.012em` | 15px, lh 1.556 | 640px ~53ch | — | **Adobe Caslon Pro** (serif) + Helvetica + Optima | 23 | One easing for the entire site: `cubic-bezier(.24,.43,.15,.97)`, dominant duration **800ms**. Palette is warm and material: `#93836c` clay, `#f1ecde` sand, `#544f45` bark, `#a62a23` lacquer red, `#fffbf2` paper. |
| [smeulders-ig.nl](https://smeulders-ig.nl/) | **Dutch** installation/engineering firm — Awwwards NOM | **96px** = `clamp(3rem, 12vw, 6rem)`, lh 1.0 | **18px**, lh 1.5 | 1038px container | 70–225px | **Syne** for everything (400/500/700) | 32 (WP presets); authored: `#fff #000 #313131` + alpha ramp | Complete type scale as clamps: `--h1-size: clamp(2rem, 2vw + 1rem, 5rem)`, h2 `clamp(1.5625rem, 2vw+1rem, 3.125rem)`, down to h6. Body 18px — bigger than the 16px default, which reads as confidence. |
| [2xa.studio](https://2xa.studio/) | Architecture studio — Awwwards **SOTD** | h2 display **144 / 216px**, lh 0.9, ls `-.015em` | 16px | 576 / 864 / 1184px (~54–74ch) | **90 / 180 / 225px** | Geist + GeistMono + a custom variable mono (2XAMONOVF) | 46 (cookie lib inflates; ~8 authored) | Named easing tokens, all expo: `--ease-out-expo: cubic-bezier(0,1,0,1)`. 12-col grid **plus `subgrid`** so nested items inherit the parent's columns. Section rhythm is a strict 90 → 180 doubling. |
| [verostudio.com](https://verostudio.com/) | Creative studio — Awwwards **SOTD** | — (fluid) | 16px | 290–450px sidebars, 1728px shell | 50 / 100 / 125px | **Louize Display** (serif) + Beausite Classic (grotesk) | **10** | A full easing library as tokens (`--ease-out-expo`, `-quart`, `-quint`, `-sine`) but a 10-colour palette: `#000 #fff #f8f8f8 #d9d9d9 #979696 #181615 #f3f0ed #e6d8cc #e97e00 #9d1414`. Backgrounds are **beige** (`--color-background-primary: #f3f0ed`), not white. |
| [ciaoenergy.com](https://www.ciaoenergy.com/) | Energy company — Awwwards **SOTD** (Webflow) | **108px** = `clamp(2.25rem, 7.5vw, 10rem)`, **lh 0.8** | 16px, lh 1.5 | 448px ~56ch | token scale **24/32/48/64/80/96/112/160px** | Franklin Gothic ATF + Geist + Geist Mono | 76 (Webflow default palette inflates) | The cleanest published spacing scale I measured — eight fluid steps, each a clamp: `clamp(1.25rem,1.1vw,1.5rem)` … `clamp(5rem,6.5vw,10rem)`. Page gutter is `4%`, not a px value. |
| [era-residence.com](https://www.era-residence.com/) | Residential development — Awwwards NOM (Webflow) | **192px**, ls `-.024em` | 14.4px | 1185 / 1382 / 1440px | 24/32/48/64px | Maison Neue **Extended** | 29 | Display type is an *extended* grotesk at 192px — width, not just size, does the work. Root font-size is 14.4px, so the whole UI scales down and the display type reads even larger by contrast. |
| [belgradearbor.rs](https://belgradearbor.rs/en) | Residential/landscape development — Awwwards NOM | `.huge` = **320px** (`20rem`), lh 1.0 | 16px | — | **328 / 344 / 360px** | Work Sans + **PP Editorial Old** | 44 | The most extreme numbers in the set: 320px type and ~350px section padding. Palette is entirely botanical: `#fff4d6` cream, `#ccbf99` straw, `#60735c` sage, `#2e3a26` forest. Zero pure black, zero pure white. |
| [250broadway.com](https://www.250broadway.com) | NYC commercial building — Awwwards NOM (Framer) | 56px | 12px (labels) | — | **80 / 120px** | Inter + **EB Garamond** + PP Neue York + PP Editorial New Ultralight | 15 | Four typefaces, but each does one job: Inter = UI, EB Garamond = pull-quotes, Neue York = numerals, Editorial New Ultralight = display. Palette `#001938` navy / `#f1eae1` cream / `#cc7760` terracotta. |
| [for-living.it](https://www.for-living.it/) | Italian property/interiors — Awwwards NOM (Webflow) | 72px (`4.5rem`), lh 1.1, ls `0` | 16px, lh 1.5 | 416 / 512px (~52–64ch) | **8/16/24/32/40/48/64/80px** | PP Fragment + Adobe Handwriting (signature accent) | 61 (Webflow defaults) | A textbook 8px-base spacing ladder actually adhered to, plus one handwritten typeface used *only* as a signature — a single human mark in an otherwise strict system. |
| [tillbergdesign.com](https://www.tillbergdesign.com/) | Interior design (ships/hotels) — Awwwards NOM | — (fluid) | 16px | 576 / 672 / 800px | **8/16/32/64/80px** | **Playfair** (serif) + Encode (grotesk) | 62 | Strict power-of-two vertical rhythm (8→16→32→64), 10/11/12-column grids switched per breakpoint rather than one grid reflowing. `cubic-bezier(.16,1,.3,1)`. |
| [purnatur.com](https://purnatur.com/) | Natural-materials brand — Awwwards NOM | 48–64px, ls **`-2px` to `-3px`** | 25.6px | 600–1250px | 15/20/25/30/40px | **T-Star Mono Round for the entire site** | 62; but two colours carry the page: `#141312` (1016 uses) + `#f7f7f7` (628 uses) | Proof that a monospace can be the *whole* type system, not just the label font. Near-black `#141312` and near-white `#f7f7f7` — neither is `#000`/`#fff`. |
| [pelizzari.com](https://www.pelizzari.com/) | Interior design studio — Awwwards NOM (**WordPress + Elementor + Bootstrap**) | 128–187px | 16px | 1140px (Bootstrap default) | 10/20/8/15px | Suisse Int'l + Suisse Works | **246** | Included as a **counter-example**: an award-nominated site that still ships the entire Bootstrap + WP-preset palette. 246 unique hex values, 50 script tags, `1140px` Bootstrap container. Good display type cannot hide template plumbing from a linter. |
| [reliablepaving.com](https://www.reliablepaving.com/) | US paving contractor — WP/Elementor, Awwwards **directory only** | 30–50px | 16px | — | 10/16/24px | **Tahoma** | 153 custom props, full WP preset palette | Included as the **trade-template control**: `Tahoma`, `letter-spacing: 0.1em` on headings, `line-height: 0.42`, WP preset colours untouched. This is exactly what our output must not resemble. |

### What the table says in one paragraph
Display type at 1440 sits between **96px and 320px** (median ≈ 130px) with line-height **0.8–1.1** and **negative** letter-spacing (−0.012em to −0.03em, or −2/−3px on the extremes). Body sits at **14–20px** — several award sites run 18px, and the two most restrained run 11px and 14.4px, so there is no single "correct" body size, only a deliberate one. Measure is **narrower than the textbook 66–75ch**: the only site authoring it explicitly (schyns.de) caps prose at **44–48ch** and display lines at **12–25ch**. Section padding at desktop clusters **80–160px**, with editorial outliers at 225–360px. And the colour count is brutal: the sites that read most expensive ship **4 to 15 unique colours**; the ones that read templated ship 60–250.

---

## Template tells

These are **differential**, not asserted. I ran one detector over two groups and compared distributions:

- **Award group (n=16)** — the sites in the table above.
- **Dutch trade control group (n=11)** — real Dutch loodgieter/dakdekker sites pulled from this repo's own outreach lists: [isa-loodgieters.nl](https://isa-loodgieters.nl), [dvdakdekkers.nl](https://dvdakdekkers.nl), [dakdekkersleiden.nl](https://www.dakdekkersleiden.nl), [loodgietermeijer.nl](https://www.loodgietermeijer.nl), [mulderloodgieterservice.nl](https://www.mulderloodgieterservice.nl), [vdwdakdekker.nl](https://www.vdwdakdekker.nl), [smits-installaties.nl](https://smits-installaties.nl), [vdpdakbedekking.nl](https://www.vdpdakbedekking.nl), [loodgieterrotterdam-bv.nl](https://loodgieterrotterdam-bv.nl), [dakdekkeramsterdam.nl](https://www.dakdekkeramsterdam.nl), [mrloodgieteramsterdam.nl](https://mrloodgieteramsterdam.nl).

Every row below is a **median-vs-median** gap that code can check. Numbers are counts of declarations across all of a page's CSS unless stated.

| # | Tell | Award median | Trade median | How to detect it in code |
|---|---|---|---|---|
| 1 | **Theme container width** — `1140` / `1170` / `1200` / `1320px` | 3 of 16 sites | **11 of 11 sites** | `grep -E 'max-width:\s*(1140\|1170\|1200\|1320)px'`. The single most reliable tell in the whole study: **100% of the trade control group, and it is always the Bootstrap/Elementor/Divi default.** Any site whose main container is one of those four numbers was not laid out, it was installed. |
| 2 | **Over-exposed Google font** — Poppins, Montserrat, Open Sans, Lato, Roboto, Nunito, Oswald, Raleway, Muli, Dosis, Source Sans, Merriweather | 1 of 16 | **10 of 11** | Match `font-family` first token against a blocklist. vdpdakbedekking.nl ships **fourteen** of them (Poppins + Montserrat + Lato + Muli + Oswald + Roboto + Source Sans Pro, several with `!important`). |
| 3 | **Unique hex colours in CSS** | **30.5** (min 4) | **108** (min 36, max 182) | Count distinct normalised hex. Award floor is 4 (as-associates.jp). Gate: **> 60 = warn, > 100 = fail.** |
| 4 | **Distinct authored `font-size` values** | **16** | **31** | Resolve every `font-size` to px and count the set. A designed scale has 6–10 steps; a theme has 30+. Gate: **> 24 = fail.** |
| 5 | **Pure `#ffffff` as the dominant page ground** | 6 of 16, and the best-scoring ones use warm paper instead (`#f5f4f0`, `#f1ecde`, `#fff4d6`, `#fdfbef`, `#f1eae1`, `#f7f7f7`, `#e5e3df`) or near-black (`#141312`, `#111111`) | **`#ffffff` is the top ground on 10 of 11** | Count `background(-color): #fff/#ffffff` declarations and check whether it is rank 1. Off-white paper is the cheapest single upgrade available. |
| 6 | **`text-align: center` declaration count** | **10** | **64** | Centred everything is the loudest visual tell. Gate: **centre declarations > 25% of all `text-align` = fail.** |
| 7 | **Icon-in-a-circle** — `border-radius: 50% / 9999px / 999px` | **3.5** | **10** | Count. Then cross-check: a circle whose child is an `<i class="fa-*">` or an inline `<svg>` inside a 3-up flex row is *the* trade-theme feature block. |
| 8 | **Font Awesome / icon font** | **0 of 16** | 7 of 11 | `grep -E 'font-awesome\|fa-solid\|fa-star\|class="fa '`. Zero award sites in the set use an icon font. Clean binary. |
| 9 | **`box-shadow` count** | **9** | **26** | Award sites separate with rules, ground colour and whitespace; templates separate with drop shadows on cards. |
| 10 | **Rounded photo corners** — `border-radius` on `img`/`figure`/`picture` | **0** (max 4 across all 16) | **5** (max 79) | Photography on award sites is square-cornered. Rounded photos read as "card component". Gate: **any `border-radius` on a photo element = warn.** |
| 11 | **Gradient count** | **8.5** | **23** | Especially `linear-gradient(...rgba(0,0,0,…))` laid over a hero photo so white centred text stays legible. That specific overlay-plus-centred-white-text hero is the definitive template hero. |
| 12 | **`!important` count** | **39.5** | **122** | Proxy for "a theme is being fought". Gate: **> 80 = fail.** |
| 13 | **Total CSS shipped** | **147 KB** | **338 KB** | 2.3× more CSS to say less. On Dutch mobile this is also the performance story. |
| 14 | **Empty `alt=""` on content images** | **0** | **9** | Bulk-uploaded stock/gallery images never get alt text. Doubles as an accessibility gate. |
| 15 | **Negative letter-spacing on display type** | median **2** declarations | median **0** | Award display type is optically tightened (`-0.012em` to `-0.03em`, or `-2px`/`-3px`). Theme headings use *positive* tracking (reliablepaving.com: `letter-spacing: 0.1em` on H1). Gate: **positive tracking on anything above 32px = fail.** |
| 16 | **`position: sticky`** | **1.5** | **0** | Sticky section labels / sticky image columns are an editorial move templates never make. |
| 17 | **`mix-blend-mode`** | **1** | **0** | Used for type-over-image and logo-on-photo. Absent from every template site. |
| 18 | **Modern viewport units `dvh`/`svh`** | **3** | **0** | `min-height: 100svh` on a hero vs `height: 100vh` (or a fixed `600px`) is a direct "authored after 2023" signal. |
| 19 | **`clamp()` for type** | present | **0 median** | Templates ship 3–4 fixed breakpoint sizes per heading; award sites ship one fluid clamp. |
| 20 | **Photography aspect ratios** | portrait + bespoke: `3/4`, `2/3`, `3/3.5`, `5/4`, `17/21`, `144/168`, `640/275`, `350/406`, `580/677` | `16/9` or **no `aspect-ratio` at all** | Verified by reading context: `aspect-ratio: 1` on award sites is almost always on icons, buttons, checkboxes and logos — **not on photos**. Photos are portrait or a bespoke ratio taken from the actual crop. A site where every photo is `16/9` or uncropped is a template. |
| 21 | **jQuery + a carousel library** (`swiper`/`slick`/`owl`/`glide`) | 3 of 16 | 6–7 of 11 | The "hero slider" is a trade-theme signature. |
| 22 | **WordPress preset palette shipped untouched** — `--wp--preset--color--vivid-red`, `--luminous-vivid-orange`, `--pale-cyan-blue` … | 3 of 16 (and those override it) | 7 of 11 | Exact-string grep. Its presence with default values means nobody opened the theme settings. |
| 23 | **Bolt-on trust widgets** — Trustindex/Elfsight review embeds, `★` glyph runs, floating WhatsApp bubble, animated count-up numbers | rare | 8 of 11 have at least one; one site has **27** star glyphs | `grep -E 'trustindex\|elfsight\|counterup\|odometer\|wa\.me'` plus a `★`/`⭐` count. |
| 24 | **Three equal columns as the only layout** — `repeat(3, 1fr)` / `1fr 1fr 1fr` | **0 median**, and `grid-column:` spans (asymmetric placement) median **2.5** | `repeat(3,1fr)` median **2**, `grid-column` spans median **1** | Ratio test: `grid-column` span declarations ÷ `repeat(3,1fr)` declarations. Award sites place items on a grid; templates repeat thirds. `subgrid` appears in the award group only (2xa.studio, 16 uses) and **never** in the control group. |
| 25 | **Uppercase + centred + tracked-out headings together** | — | common | Compound check: an element with `text-transform:uppercase` AND `text-align:center` AND positive `letter-spacing` is almost always a theme section title. |

### The composite gate
No single tell is fatal. A site that trips **five or more** of #1–#6 is mechanically a template. In the control group, 10 of 11 trip at least five; in the award group, **zero** do — the closest is purnatur.com (Bootstrap-era, 2 trips) and ciaoenergy.com (Webflow defaults, 2 trips).

---

## Hero anatomy, from the actual markup

I read the DOM of the heroes rather than looking at screenshots. Three patterns, none of them the centred stack.

**schyns.de** (construction/interiors). One full-bleed element at `min-h-svh` — note `svh`, not `vh`, so mobile browser chrome doesn't clip it. Inside: a background `<video>` at `absolute inset-0 object-cover`, the `<h1>` placed in a named `base-grid`, a **second, small** video thumbnail pinned asymmetrically (`lg:top-1/2 lg:-translate-y-full`), a left-aligned row of filter pills as the CTA layer, and — the detail that does the most work — **three award logos pinned bottom-right** (`if-design-award-winner.svg`, `designpreis-rp-2013.svg`, `innovationspreis-architecture+health.svg`). Every spacing value is a named fluid range: `px-container`, `mt-vw-40-to-60`, `gap-vw-6-to-8`.

**kellerstoecklarchitektur.at** (HM). **No hero image at all.** A nav reading `INDEX / DETAIL / EDITORIAL`, a centred `nav-title` + `nav-subtitle` pair ("KELLERSTÖCKL" / "EINE ARCHITEKTURTYPOLOGIE IM SÜDBURGENLAND"), and a slider whose label is the numeral `000`. The `<h1>` is **visually hidden and exists only for search engines** — the markup literally comments `Semantisch sichtbar für Suchmaschinen, visuell ausgeblendet`. The display type is the navigation.

**era-residence.com**. A decorative frame assembled from eight positioned pieces (`frame_lt`, `frame_t-lr`, `frame_rt`, `frame_r-tb`, …) inset from the viewport edge, plus paired `.link_label_text` / `.link_label_text.is-2` elements — the duplicated-label text-swap hover, which is `overflow:hidden` + two `translateY` transforms and needs no JS.

**What this means for a trade hero.** Headline sits bottom-left inside the grid, not centred; the media is one real photograph at `min-height:78–88svh` so a slice of the next section stays visible; the CTA is a left-aligned pair of links, not a centred pill; and the corner that award sites give to award logos is where a Dutch trade site puts its credibility marks — KvK number, VCA, Erkend Installateur, garantietermijn — set in the mono at 12px.

### Hero height, measured

I counted every viewport-unit height declaration across both groups. Two clean differentials:

- **Modern viewport units.** `100svh` appears on **7 of 14** award sites and `100dvh` on **8 of 14**. Across **10** trade sites, `svh`/`dvh` appears on exactly **one** — and that one is the only control site not built on WordPress. `height:100vh` on a mobile hero clips under the browser chrome; `100svh`/`100dvh` is the 2026 fix and is itself a dating signal.
- **Fixed pixel hero heights.** `min-height: 250px / 320px / 430px / 481px / 500px / 800px / 930px` appears on **7 of 10** trade sites. On award sites, fixed `min-height` values exist but are 100–150px — component sizes, never hero heights.

And the heroes are frequently **not** a full viewport. kellerstoeckl uses `70vh` and `80vh`; ciaoenergy, era-residence and for-living all use `84vh`, `86vh` and `96vh`; verostudio `90vh`; schyns `80vh`. Stopping short of 100 lets the top of the next section show, which tells the visitor the page continues — the opposite of the full-bleed centred hero that ends exactly at the fold.

---

## What we can't do

Being explicit about this so we stop wishing for it. Each of these is genuinely out of reach under static-Astro / near-zero-JS, and each has a listed substitute that is not a consolation prize.

| Technique | Why it's out | What we do instead |
|---|---|---|
| **WebGL / Three.js hero** (verostudio, k95, lamalama, ciaoenergy all ship it) | 150–600 KB of runtime, a canvas that can't be indexed, and a battery cost on Dutch mobile | One large photograph, cropped portrait or bespoke, with a `filter` grade. Move #9. |
| **Scroll-jacked / pinned scroll sequences** (GSAP ScrollTrigger + Lenis — present on era-residence, ciaoenergy, revelatio, normalisboring) | Needs GSAP + a smooth-scroll library; also breaks keyboard and reduced-motion users | `position:sticky` for the same "column holds while content passes" effect — one declaration, no JS, and it's what cobloc and 250broadway actually use for their sticky panels. |
| **Custom cursors / magnetic buttons** | Pointer-tracking JS on every frame; meaningless on touch, which is most Dutch trade traffic | Text-swap hover (`overflow:hidden` + two transforms) and a hairline underline that grows from the left. |
| **Page-transition overlays / preloaders** (era-residence's masked preloader; 2xa's loader) | Cross-document View Transitions are still effectively unshipped — `view-transition` appeared in **0 of 16** award sites' CSS | Nothing. A fast static page that just appears beats a 900ms loader, and the loader is largely there to hide JS boot time we don't have. |
| **Variable-font weight animation on scroll** | Needs a scroll driver plus a variable font with a weight axis | Static weight pairing. schyns.de ships Aspekta at `100 900` but only *uses* 300 and 600. |
| **Physics/drag galleries** (cobloc's `image-gallery-drag`) | Pointer physics library | CSS scroll-snap carousel — `scroll-snap-type:x mandatory` on the track, `scroll-snap-align:start` on items. Zero JS, works with a trackpad, keyboard and touch. |
| **True masonry** | `grid-template-rows:masonry` is not shipped | CSS multi-column (`columns:3; break-inside:avoid`) — already known in this repo: tile order is load-bearing because multicol fills sequentially. |
| **Counted-up statistics** (`counterup`/`odometer` on 2 control sites) | jQuery plugin — and it is a *template* tell, not an award one | Set the number large and static in the mono. Oversized static numerals read more confident than animated ones. |

One honest caveat: **the reveal-on-scroll animation that most award sites use is JavaScript** (GSAP + IntersectionObserver). The CSS-only replacement is `animation-timeline: view()`, at **85.43%** global support in Aug 2026 — so it must be written as progressive enhancement inside `@media (prefers-reduced-motion: no-preference)`, with the un-animated state as the default. The remaining ~15% simply see the content, which is the correct fallback anyway.

---

## Cheap wins ranked

Visual impact ÷ implementation cost. Everything here is CSS or a token change in the factory; nothing needs a runtime.

| # | Win | Cost | Impact | Note |
|---|---|---|---|---|
| 1 | **Swap `#fff` ground for warm paper, `#000` ink for near-black** | 2 tokens | Very high | The single biggest gap between the two groups. But **not cream + amber** — that pairing is now itself a generated-design default (see the caveat in move #3). Derive the ground and accent from the vak's material. |
| 2 | **Cap prose at `46ch` and headlines at `~14ch`** | 2 declarations | Very high | Turns a wall of text into a column. schyns.de authors 44–48ch. |
| 3 | **Display type to `clamp(2.5rem,9vw,8.5rem)`, `line-height:.95`, `letter-spacing:-.02em`** | 3 declarations | Very high | Also kill any positive tracking above 32px — that alone removes the strongest theme smell. |
| 4 | **Cut the palette to ≤6 authored colours + one alpha ramp** | Refactor tokens | Very high | Gate it: distinct hex > 60 = warn. Trade median is 108. |
| 5 | **Mono for all metadata** (labels, captions, phone, KvK, hours, section numbers) | 1 font + 1 class | High | The cheapest "designed" signal there is; recurs across the entire award set. |
| 6 | **The numbered sticky section header** (move #7) | ~8 lines CSS | High | Five expensive signals in one pattern, no JS. |
| 7 | **Square-corner photos at portrait/bespoke ratios with one grade** | CSS + crop config | High | Remove every `border-radius` from images; award median is 0, trade median 5. |
| 8 | **Real `<figcaption>`s in the mono, offset left rather than centred** | Template change | High | Captions are also where a trade site puts *proof* — location, date, job type. |
| 9 | **One easing token + two duration tokens, used everywhere** | 3 tokens | Medium-high | `--ease:cubic-bezier(.22,1,.36,1); --dur-micro:200ms; --dur-reveal:700ms`. |
| 10 | **12-column grid with unequal spans** for at least the section headers | Layout refactor | Medium-high | `1/4` + `5/-1` beats any three-equal-columns row. |
| 11 | **One deliberate full-bleed break per page** | 2 declarations | Medium | `width:calc(100% + 2*var(--pad)); margin-inline:calc(var(--pad)*-1)`. |
| 12 | **Hairline `1px solid rgb(0 0 0 /.08)` rules instead of card shadows** | Find/replace | Medium | Award box-shadow median 9 vs trade 26. |
| 13 | **`min-height:84svh` hero, headline bottom-left, CTA row left-aligned** | Template change | Medium | Replaces the centred stack; `svh` also fixes mobile clipping. |
| 14 | **`text-wrap:balance` on headings** | 1 declaration | Medium | Removes orphans and one-word last lines — a classic amateur tell, free to fix. `balance` is Baseline (since 2024-05-13); `pretty` is still **limited**, so treat it as optional sugar, not a dependency. |
| 15 | **`mix-blend-mode:difference` on one sticky caption** | 1 declaration | Medium | Absent from all 11 control sites; present in the award group. |
| 16 | **CSS scroll-snap gallery instead of a slider library** | ~5 lines | Medium | Also deletes swiper/slick — a template tell and ~40 KB. |
| 17 | **`animation-timeline:view()` reveals behind `@supports` + a reduced-motion guard** | ~6 lines | Medium | Not Baseline — Firefox has not shipped it to release. ~⅓ of Dutch traffic must get the static state, so the animation has to be additive, never an `opacity:0` default. |
| 18 | **A thin inset viewport frame** | 1 declaration | Low-medium | Cheap borrowed elegance from era-residence. |
| 19 | **Text-swap hover on links** (duplicate label + two transforms) | ~6 lines | Low-medium | The era-residence `.link_label_text.is-2` pattern. |
| 20 | **`font-variant-numeric: tabular-nums` on all numbers** | 1 declaration | Low | Prices, phone numbers and hours stop jittering; 250broadway sets it on counters. |

---

## Colour, measured: two valid strategies (and the accent is smaller than you think)

I classified every hex in each site's CSS by saturation and lightness and computed the share of colour declarations that are *chromatic* rather than neutral. The result splits the award set cleanly in two.

**Strategy A — neutral field, one accent, used sparingly.** cobloc.archi: a single acid yellow `#fbd600` accounting for **9.8%** of colour usage against pure black and white. purnatur.com: one red at **0.7%**. verostudio: `#e97e00` orange, **15.8%** including its beige grounds. And two sites run **0% chromatic** — kellerstoecklarchitektur.at and 2xa.studio are entirely achromatic. The accent is not a brand colour smeared over the page; it is a *punctuation mark*, typically **under 10%** of colour declarations, often on one CTA and one rule.

**Strategy B — no greys at all; every neutral is a desaturated colour.** belgradearbor.rs reads **39% chromatic** but has no accent in the usual sense: its whole system is botanical — `#fff4d6` cream, `#f4f0db`, `#ccbf99` straw, `#a68150` tan, `#60735c` sage, `#3e562e`/`#2e3a26` forest. tandjungsarihotel.com at **31%**: `#fffbf2`, `#f1ecde` sand, `#ded7c8`, `#93836c` clay, `#544f45` bark, `#a62a23` lacquer. houseofhoney.com at 39%: `#ffeacf`, `#edccbe`, `#331917`, `#d41203`. These sites contain **zero pure greys** — every "neutral" carries a hue.

For Dutch trade sites, **Strategy B is the stronger default**, because the desaturated palette can be derived from the trade's own material: zinc and lead greys for a loodgieter, bitumen/slate/terracotta for a dakdekker, sawn-oak warm neutrals for a timmerman, copper and cable-insulation tones for an elektricien, and warm skin/paper tones for a kapper. That gives each vak a genuinely different palette from the same generator rule, without inventing brand colours.

The trap to avoid is the third strategy, which is what the control group does: a saturated primary (`#0274be`, `#007cba`, `#428bca`, `#5bc0de`, `#e96656`) applied to buttons, icon circles, section headers and link states simultaneously, on top of a full framework palette.

---

## Type pairing: what actually recurs

Counting `@font-face` families across the measured set (icon fonts and framework artifacts like `swiper-icons` / `webflow-icons` / `fontello` excluded):

| Family | Sites | Role |
|---|---|---|
| **Geist** | 7 | Neutral grotesk workhorse |
| **Geist Mono** | 5 | Metadata voice |
| **Work Sans** | 5 | Grotesk |
| **Inter** | 4 | UI text (never display) |
| **Suisse Int'l / SuisseBPIntl** | 4 | Grotesk |
| **DM Mono** | 3 | Section numerals, labels |
| **Syne** | 3 | Display (the whole system on smeulders-ig.nl) |
| **PP Editorial New / Old** | 3 | Editorial serif, display only |
| **EB Garamond** | 2 | Pull-quotes |
| Unica 77 LL, Maison Neue Extended, Neue Haas Grotesk, Beausite Classic, Aspekta Variable, Encode, Ivory LL, Louize Display, Adobe Caslon Pro, Playfair, T-Star Mono Round | 1–2 each | — |

**The shape of the system is consistent even when the fonts differ: grotesk + editorial serif + mono.** Three roles, and one of them is always monospace. Weights actually used are few — as-associates.jp ships only 300 and 400; schyns.de loads a `100 900` variable font and uses 300 and 600; kellerstoeckl uses one weight, 400. Loading eight weights is itself a tell.

**Inter never appears as display type** in the set — it is UI text on 250broadway and alethia.earth, with a display face doing the headline work. Inter at 96px is a 2021 move.

### Three registers, and the trap in the middle one
Cross-checking my counts against two external datasets sharpens this considerably.

- **The template register.** [HTTP Archive Web Almanac 2025](https://almanac.httparchive.org/en/2025/fonts), measured across millions of sites: Roboto **10.0–10.7%** of pages, Poppins **5.8–6.0%**, Open Sans **5.0–5.6%**, Montserrat **3.3–3.9%**. These are the commodity web. Ten of my eleven Dutch trade sites use at least one; one uses fourteen.
- **The considered register.** [Typewolf's most-popular list](https://www.typewolf.com/) (curated, award-adjacent): Apercu, GT America, Futura, Founders Grotesk, Neue Haas Grotesk, Canela, Graphik, GT Walsheim, Maison Neue, Ogg. **Not one of Roboto, Poppins, Montserrat, Open Sans or Inter appears in that top 15.** That gap is the answer to "which fonts read as chosen".
- **The trap: the AI-default register.** Inter, **Geist**, Space Grotesk, Instrument Serif. This is a correction to my own measurement. Geist is the most recurrent family in my award set (7 sites) *and* it is v0's default — the field guide calls it "**the new Inter**". Space Grotesk is "the reach when the model tries to escape Inter, which made it a tell of its own"; Instrument Serif italic at hero size is named as the "tasteful AI startup" signature, status *rising* ([signs-of-ai-design](https://github.com/febbhav/signs-of-ai-design)).

So my earlier instinct — "Geist + Geist Mono is free, self-hostable and award-recurrent, use it" — is only half right. It is free and it does appear on award sites, but it is simultaneously the single most generated typeface of 2026. **For the factory the safer read is: keep the *shape* of the system (grotesk + editorial serif + mono) and vary the families per vak**, drawing from the less-saturated free options — Work Sans, Syne, Bricolage Grotesque, Instrument Sans, DM Mono, EB Garamond, Fraunces, Newsreader — rather than shipping Geist on every client site. A factory that emits the same typeface for every loodgieter in the Netherlands has recreated the template problem with better taste.

The operative quote, and the one worth pinning above the generator: "**the tell is not the font; it is the font unchosen, appearing beside twenty other unchosen defaults.**"

Blocklist, from the control-group evidence plus the Almanac: Poppins, Montserrat, Open Sans, Lato, Roboto, Roboto Slab, Nunito, Oswald, Raleway, Muli, Dosis, Source Sans Pro, Merriweather. Watchlist (allowed, but never as the default for every site): Inter, Geist, Space Grotesk, Instrument Serif.

---

## 2026 vs dated — answered from the measurements, not from trend posts

**The big centred hero is dated — but the useful precision is *which part*.** Not one site in the award set builds the stack of centred headline + centred subhead + centred pill button over a full-bleed stock photo with a dark gradient overlay. The measured components: `text-align:center` declarations run **10 (award) vs 64 (trade)**; dark `rgba(0,0,0,…)` gradient overlays have an award median of **0**. What replaced it is the grid-placed headline — bottom-left or in an explicit column — with the CTA as a left-aligned row and the credibility marks pinned to a corner. Also dated in the same gesture: `height:100vh` (award sites use `svh`/`dvh`, or deliberately stop at 84–96vh) and fixed pixel hero heights, which appear on **7 of 10** trade sites and no award site.

**Glassmorphism is not dead, and the common claim that it is, is wrong in a measurable way.** `backdrop-filter: blur()` has an award-group median of **4** declarations and a trade-group median of **0**. Frosted blur is alive — as sticky navigation bars, menu overlays and image-adjacent scrims. What died is the *decorative frosted card floating over a mesh gradient*. The technique survived; the composition did not.

**The three-icon-cards row is the most reliably templated block in the study.** Its two mechanical parts both split the groups: `border-radius:50%/9999px` (award median 3.5, trade 10) and icon fonts — Font Awesome appears on **7 of 11** trade sites and **0 of 16** award sites, a clean binary. And award sites place items on a grid (`grid-column` span median 2.5) where templates repeat thirds (`repeat(3,1fr)` median 2). Note the repo's existing `tell-lint.mjs` already catches the copy-side version of this (`lg:grid-cols-3` with an h3 count of 4, 7, 10 — a "rule of three" that ran out of content).

**Oversized display type, editorial/Swiss layout and warm-neutral grounds are the live idiom.** All three are load-bearing in the measurements above: 96–320px display, `ch`-capped measure, 12-column grids with unequal spans, and non-white paper on the strongest sites. **Mono-as-metadata** is the most consistent single signal across the set — Geist Mono, DM Mono, T-Star Mono Round, Geist Mono again.

**Over-exposed type is a real and detectable category.** Poppins, Montserrat, Open Sans, Lato, Roboto and friends appear on **10 of 11** Dutch trade sites and **1 of 16** award sites. Inter is different — it appears on 4 award sites but **never as display type**; it is UI text with a display face above it. Inter set at 96px is the 2021 look.

**What I could not confirm as live in production:** scroll-driven CSS animation (`animation-timeline`) and the View Transitions API appear in **0 of 16** award sites' CSS despite both now having usable support (85.43% and effectively unshipped for cross-document, respectively). `@starting-style` appears on at most a handful. The award sites still do their reveals with GSAP + Lenis, i.e. JavaScript we have ruled out. So `animation-timeline: view()` is not something we would be copying — it is a place where a static site can be *ahead* of the award set, at zero JS cost, provided it is written as progressive enhancement.

---

## Cross-check: the independent slop-detection literature

My numbers come from 27 sites I fetched myself. A parallel body of 2025–2026 work reaches the same conclusions from far larger samples, which is worth recording because it turns several of my findings from "measured on n=27" into "corroborated".

**Two quantitative studies.**
- **1,590 Show HN sites, Playwright-crawled** (April 2026): DOM + computed-style analysis, deterministic checks only, no LLM judgment, ~5–10% false positives on manual QA. **22%** matched 4+ generated-design patterns, **32%** matched 2–3. The 16 detected patterns include, by name: **centred heroes**, **badges above headlines**, **icon-topped feature grids**, low-contrast body text, coloured glows, numbered step sequences, stat rows, all-caps labels, glassmorphism. — [adriankrebs.ch/blog/design-slop](https://www.adriankrebs.ch/blog/design-slop/), live scanner at [slopcop.adriankrebs.ch](https://slopcop.adriankrebs.ch)
- **47 commercial sites torn down over 9 months** (Jul 2025 – Mar 2026): Tailwind blue `#3b82f6` on marketing sites went from ~10% in 2020 to **~78% in 2026**; the most reliable single fingerprint is "a gradient running between Tailwind's blue-600 and purple-500/pink-500"; em-dash density on AI-built landing copy runs **4–6×** archived 2019 comparables. — [sailop.com](https://www.sailop.com/blog/ai-slop-2026-state-of-the-ai-generated-web)

**The named critique of the three-icon-card row**, which I found mechanically but could not name:
> "**The three-card feature row** — exactly three equal cards below the hero, each with an icon on top, a short heading, and two lines of text. The single most consistently named tell across every source that documents this category. … Suspicion rises when the content visibly does not come in threes but was forced into three anyway."
> — [signs-of-ai-design](https://github.com/febbhav/signs-of-ai-design)

That last clause is precisely the rule `tell-lint.mjs` already implements on the copy side (`lg:grid-cols-3` with an h3 count of 4, 7 or 10). Related named sub-patterns: "**icon tile stacked above heading** — the universal AI feature-card template"; "**the Lucide five**" — *Sparkles*, *Zap*, *Shield*, *Check*, *BarChart3*, *ArrowRight* recurring across unrelated products. NN/g tested the sparkle icon with **n=107** and found **nobody** associated it with artificial intelligence ([nngroup.com](https://www.nngroup.com/articles/ai-sparkles-icon-problem/)).

**And the "cookie-cutter page order"**, which matters for a factory that assembles sections from a config: "hero, logo wall, three-card features, testimonial carousel, stats row, pricing table, FAQ, footer with a repeated call to action" — one 2026 analysis found about half of indie SaaS pricing pages following an identical nine-element template. This is the strongest argument for the `indeling.weglaten` capability already built into our factory: **a site that omits sections is structurally harder to fingerprint than one that always emits the full set.**

**Three corrections to the trend consensus, from this literature.**
1. **Bento grids are now a tell themselves** — "it spread as the safe alternative once three-card rows were called out, and is now a tell of its own", so replacing a 3-up row with a bento does not escape the problem.
2. **Glassmorphism is demoted, not dead** — which matches my measurement exactly (`backdrop-filter` award median 4, trade median 0). It survives on navigation and overlays where something genuinely layers; decorative frosted cards are the tell. Measured cost: **15–30% FPS drops** on real devices, so it stays off anything that scrolls.
3. **3D/WebGL underdelivered commercially** — "a single Spline scene in the hero loads 800 kB to 2 MB of JavaScript runtime". Our constraint turns out to be aligned with where the market went, not a compromise against it.

**The framing sentence worth pinning above the generator:**
> "No single item matters on its own. The AI look is the co-occurrence of many of these defaults at once **with no deliberate choice anywhere**. Ship a design where the important decisions were made on purpose, and it will not read as generated even if it happens to use a rounded card or a sans-serif font."

Reference artefacts worth keeping: [signs-of-ai-design](https://github.com/febbhav/signs-of-ai-design) (field guide + a `design-rules.md` written to be dropped in as `CLAUDE.md`), [impeccable.style/slop](https://impeccable.style/slop/) (46-pattern catalog with a CLI detector), [hallmark](https://github.com/Nutlope/hallmark) (57 slop-test gates), [vibecheck.fail](https://www.vibecheck.fail/).

**One honest gap.** There is *no* rigorous literature naming per-builder visual signatures — "the Squarespace look" is an established industry phrase but nobody has documented it the way the AI tells are documented. The defensible version is the composite I measured: over-exposed Google font + centred hero over stock with a dark overlay + three icon cards + `1140/1200px` container + Font Awesome + WP preset palette. Per-builder fingerprints beyond that are folklore. For context, WordPress is **64.3%** of CMS-driven sites, Wix ~5.2%, Squarespace ~3.0–3.3%, Webflow under 2% ([Web Almanac 2025](https://almanac.httparchive.org/en/2025/cms)) — which is why the trade control group is overwhelmingly WordPress and why the WP-specific greps in the gate table earn their place.

---

## Turning this into a gate

`apps/client-sites/scripts/tell-lint.mjs` currently owns **copy** tells (drieslag, two-word headings, eyebrow overuse, the 3-column/h3 count) and its header comment explicitly declines rules for gradients, glassmorphism and motion on the grounds that the template cannot emit them. That reasoning holds for those. But the template *can* emit every tell in the table above, because they are all properties of the generated CSS and markup — so these belong in a CSS-side sibling gate over `dist/`, not in the copy linter.

Proposed thresholds, all derived from the two measured distributions (award n=16, Dutch trade n=11):

| Check | Warn | Fail | Basis |
|---|---|---|---|
| Distinct resolved `font-size` values | > 14 | > 24 | award median 16, trade median 31 |
| Distinct hex colours in emitted CSS | > 40 | > 60 | award median 30.5, trade median 108 |
| Dominant `background` is `#fff`/`#ffffff` | — | fail | trade 10/11, best award sites never |
| `max-width` equal to 1140/1170/1200/1320px | — | fail | trade **11/11**, the single cleanest signal |
| Font family matches over-exposed blocklist | — | fail | trade 10/11, award 1/16 |
| `letter-spacing` > 0 on any `font-size` ≥ 32px | — | fail | award tracks display negative; themes track it positive |
| `border-radius` on `img`/`picture`/`figure` | > 0 | > 2 | award median 0, trade median 5 |
| `box-shadow` declarations | > 14 | > 26 | award median 9, trade median 26 |
| `text-align:center` share of all `text-align` | > 25% | > 40% | award median 10 decls, trade 64 |
| `border-radius: 50%/9999px` count | > 6 | > 10 | award median 3.5, trade 10 |
| Any `font-awesome` / `fa-` icon-font reference | — | fail | award **0/16**, trade 7/11 |
| `--wp--preset--color--*` present with defaults | — | fail | trade 7/11 |
| `!important` count | > 60 | > 120 | award median 39.5, trade median 122 |
| Emitted CSS size | > 200 KB | > 330 KB | award median 147 KB, trade median 338 KB |
| Content `<img>` with empty `alt` | > 0 | > 3 | award median 0, trade median 9 |
| `height:100vh` on the hero (rather than `svh`/`dvh`) | — | fail | award 7–8/14 use svh/dvh, trade 1/10 |
| Fixed px `min-height` ≥ 200px on a section | — | fail | trade 7/10 |
| `repeat(3,1fr)` count vs `grid-column` span count | span:third ratio < 1 | ratio < 0.5 | award places on a grid; templates repeat thirds |
| Tailwind default blue `#3b82f6` / indigo `#6366f1` / violet `#8b5cf6` / purple `#a855f7` / emerald `#10b981` present | — | fail | the generated-design palette; Tailwind blue went 10% → 78% of marketing sites 2020→2026 |
| Cream ground `#fdf8f0`-ish **with** an amber accent | warn | — | the documented second-wave generated default; warm ground is fine, this specific pair is not |
| Same typeface emitted across ≥3 client sites in the fleet | warn | — | a factory that ships one font to every loodgieter has rebuilt the template problem |
| Section sequence identical across ≥3 client sites | warn | fail | the "cookie-cutter page order"; this is what `indeling.weglaten` exists to break |

**Composite:** five or more failures = the site is mechanically a template. Against the measured sets this fires on 10 of 11 trade sites and **0 of 16** award sites, so it separates the two populations cleanly rather than just penalising cheapness.

The complement is a **positive** check — a site should *earn* marks, not merely avoid tells. Require at least four of: a `ch`-based measure cap; a CSS counter used for section numbering; `position:sticky` on a section label; at least one `grid-column` span that is not full-width; a monospace family bound to metadata; a non-`#fff` page ground; a portrait or bespoke photo aspect-ratio; one deliberate negative-margin bleed.

---

## Sources

Galleries and award listings: [Awwwards Sites of the Day](https://www.awwwards.com/websites/sites_of_the_day/), [Awwwards Architecture category](https://www.awwwards.com/websites/architecture/), [Godly](https://godly.website/websites), [SiteInspire](https://www.siteinspire.com/), [Land-book](https://land-book.com/), [FWA](https://thefwa.com/), [CSS Design Awards](https://www.cssdesignawards.com/), [Orpetron](https://orpetron.com/), [One Page Love](https://onepagelove.com/).

Award status per site verified at `awwwards.com/sites/<slug>` — e.g. [kellerstockl](https://www.awwwards.com/sites/kellerstockl), [cobloc](https://www.awwwards.com/sites/cobloc), [schyns](https://www.awwwards.com/sites/schyns), [smeulders](https://www.awwwards.com/sites/smeulders).

Browser-support figures (fetched 2026-08-16), cross-checked against Baseline data: caniuse for [`@starting-style`](https://caniuse.com/mdn-css_at-rules_starting-style), [`transition-behavior`](https://caniuse.com/mdn-css_properties_transition-behavior), [`animation-timeline`](https://caniuse.com/mdn-css_properties_animation-timeline); [webstatus.dev](https://webstatus.dev) for Baseline status and Chrome usage counters; [MDN `animation-timeline`](https://developer.mozilla.org/en-US/docs/Web/CSS/animation-timeline) for the limited-availability banner; [Bugzilla 1324602](https://bugzilla.mozilla.org/show_bug.cgi?id=1324602) for Firefox's shipping status. Where they disagree, the Baseline/Bugzilla reading is used.

Slop-detection and trend literature: [signs-of-ai-design](https://github.com/febbhav/signs-of-ai-design), [impeccable.style/slop](https://impeccable.style/slop/), [design-slop study, n=1590](https://www.adriankrebs.ch/blog/design-slop/), [Sailop teardown, n=47](https://www.sailop.com/blog/ai-slop-2026-state-of-the-ai-generated-web), [hallmark](https://github.com/Nutlope/hallmark), [vibecheck.fail](https://www.vibecheck.fail/), [925 Studios](https://www.925studios.co/blog/ai-slop-design-tells), [NN/g sparkle-icon study, n=107](https://www.nngroup.com/articles/ai-sparkles-icon-problem/), [StudioMeyer reality check](https://studiomeyer.io/en/blog/webdesign-trends-2026-reality-check), [Setproduct on glass](https://setproduct.com/blog/liquid-glass-vs-glassmorphism), [Lexington Themes on hero sections](https://lexingtonthemes.com/blog/stunning-hero-sections-2026), [Pixtar](https://pixtar.ae/blog/website-design-trends/).

Typography and platform data: [HTTP Archive Web Almanac 2025 — Fonts](https://almanac.httparchive.org/en/2025/fonts), [— CMS](https://almanac.httparchive.org/en/2025/cms), [Typewolf most-popular fonts](https://www.typewolf.com/).

Dutch trade control group sourced from this repo's own outreach lists; all 11 URLs listed in the Template tells section.

Measurement harness (not committed — scratchpad only): fetches HTML + all linked CSS, resolves CSS custom properties transitively, evaluates `clamp()`/`calc()`/`vw` at a 1440px viewport, and emits the token counts used throughout.
