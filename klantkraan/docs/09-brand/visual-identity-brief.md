# Visual Identity Brief

> A brief, not a system. Goal: hand this to one Fiverr designer (or v0 / Recraft / a junior on Upwork) for €100–300 and walk out with a logo + colour + type system good enough for M1–M6. Full identity refresh happens at month 9 when MRR justifies a €1,500 designer engagement. The brief is intentionally constraint-heavy so the deliverable is unambiguous.

## 1. Brand attributes (the only filter)

| Attribute | What it means visually | What it rules out |
|---|---|---|
| **Direct** | Clean geometry, no excess decoration | No retro-flourish, no calligraphy |
| **Vakman-trusted** | Tools-and-utility heritage, not Silicon-Valley-pastel | No fintech gradient, no AI-sparkle stars |
| **Modern, not trendy** | 2025-grade typography, but durable | No Y2K, no brutalist, no Web 2.0 glossy |
| **Dutch-functional** | Hard-edged confidence — Wim Crouwel grid heritage | No "playful curves", no kawaii |
| **Tap / valve metaphor** | Reads as a tap, a valve, or a flowing line | Not literally a sanitaire kraan (Hansgrohe collision) |
| **Approachable, not corporate** | Single-colour primary, generous whitespace | No navy-blue-consultancy palette |

## 2. The logo

### What we want

- **Wordmark first** — "klantkraan" set in a strong sans-serif, all lowercase.
- **Optional pictogram** — a stylised tap-valve or stylised K that doubles as a tap. Must work at 16×16 favicon size.
- **Single-colour version mandatory** — the logo must work in pure black, pure white, and one brand colour.
- **No tagline lock-up** — taglines change too often (see `01-strategy/positioning.md` H2 variations).

### Logo constraints

| Constraint | Requirement |
|---|---|
| Aspect ratios | 1:1 (avatar), 4:1 (header), 6:1 (email signature) |
| Sizes | Legible at 16px, 32px, 64px, 128px+ |
| File deliverables | SVG (vector master), 1024×1024 PNG, 64×64 favicon ICO, monochrome variant of each |
| Right of use | Full copyright transfer to T4 Software Consulting BV — no "designed by" credit required |
| Font | Must use a font we can self-host (SIL OFL or similar license) — see § 4 |

### What the pictogram should evoke

Pick one of these directions for the designer. Do not pick all three.

| Direction | Description | Risk |
|---|---|---|
| **A. The valve** | A circular tap valve, simplified to 4–6 lines | Could read as a Wi-Fi icon if oversimplified |
| **B. The K-tap** | A stylised lowercase `k` whose lower diagonal turns into a tap spout | Hardest to execute well |
| **C. The flow** | A short curved line emerging from a square base, drop at the end | Most generic — easy escape if A and B fail |

**Default brief:** ask the designer to attempt A and C, two versions of each, choose B only if their portfolio shows skill at type-glyph hybrids.

### What the logo must NEVER include

- ❌ A literal photo-realistic kraan
- ❌ A water drop with a face
- ❌ A circuit-board pattern (the "tech-ness" of the product is invisible)
- ❌ A speech bubble (this is not a chat app)
- ❌ A megaphone (this is not a marketing agency)
- ❌ Sparkles, stars, AI-sparkle iconography
- ❌ A gradient
- ❌ A drop shadow
- ❌ More than two colours
- ❌ A registered-trademark symbol until BOIP filing is registered (see `naming-and-domain.md` § 6)

## 3. Colour palette

Single primary + one accent + a neutral scale. Conservative on purpose — Dutch B2B tolerates dull, distrusts loud.

### Primary palette

| Token | Hex | Use | Why this colour |
|---|---|---|---|
| `--kraan-blue` | `#0F4C81` | Primary brand, CTAs, logo monochrome | Dutch deep-blue — Delftware, KLM, NL flag association. Trustworthy without being a fintech navy. |
| `--kraan-cream` | `#FAF6EE` | Page background | Warm off-white. Doesn't burn eyes at 22:00 when a loodgieter is browsing on a phone after a long day. |
| `--kraan-ink` | `#1A1A1A` | Body text | Not pure black — softer reading. |

### Secondary palette

| Token | Hex | Use |
|---|---|---|
| `--kraan-rust` | `#C75A2B` | Accent (single accent — error states, key highlights, hover) |
| `--kraan-leaf` | `#3F7F4A` | Success / confirmation only (booked afspraak, paid invoice) |
| `--kraan-stone-100` | `#F1ECDF` | Card background |
| `--kraan-stone-300` | `#D9D2C0` | Borders |
| `--kraan-stone-500` | `#8C8474` | Secondary text |
| `--kraan-stone-700` | `#4A463D` | Headings on cream |

### Colour rules

- The marketing site uses **only** cream + ink + blue + one accent block per page. That's it.
- Status colours (rust = warning, leaf = success) appear in the dashboard only.
- No purples, no teals, no pinks. Anything outside this palette requires an explicit decision logged here.
- Contrast ratio ≥ 4.5:1 for all body text on background — verified via WebAIM.

### Why we resisted bolder palettes

| Tempting palette | Why we said no |
|---|---|
| Black + neon orange (Hormozi-core) | Reads as US-import; Dutch tradesmen mistrust the aesthetic. |
| Pastel SaaS (lavender + mint) | Wrong audience signal. |
| Pure black + white | Too cold; cream signals approachability without being childish. |
| Dutch-flag tricolour | On-the-nose, cheap-souvenir energy. |

## 4. Typography

Self-hosted, free, OFL-licensed. No Google Fonts (avoid Privacy Shield mess + EU CDN concerns).

| Role | Font | Source | License |
|---|---|---|---|
| Display / H1–H2 | **Inter Tight** (bold 700, semibold 600) | https://rsms.me/inter/ | SIL OFL |
| Body | **Inter** (regular 400, medium 500) | Same | SIL OFL |
| Monospace (dashboard, code, numbers) | **JetBrains Mono** | https://www.jetbrains.com/lp/mono/ | SIL OFL |
| Brand wordmark | **Inter Tight** semibold, custom-spaced `-0.02em` | Same | SIL OFL |

### Type scale (rem-based, body = 1rem = 16px)

| Token | Size | Line height | Weight | Use |
|---|---|---|---|---|
| `--text-hero` | 3.5rem (56px) | 1.05 | 700 | Landing-page H1 |
| `--text-h1` | 2.25rem (36px) | 1.15 | 700 | Page H1 |
| `--text-h2` | 1.75rem (28px) | 1.2 | 600 | Section heading |
| `--text-h3` | 1.25rem (20px) | 1.3 | 600 | Sub-section |
| `--text-body` | 1rem (16px) | 1.55 | 400 | Default |
| `--text-small` | 0.875rem (14px) | 1.45 | 400 | Caption, meta |
| `--text-micro` | 0.75rem (12px) | 1.4 | 500 | Legal, fine print |

### Type rules

- Body line length max 70 characters.
- Headings allow tighter tracking (`-0.01em`), body never.
- No italic on the marketing site (Dutch B2B reads italics as "AI-generated").
- Numbers in body copy: tabular figures variant where supported.

## 5. Imagery and illustration

### Photography

- Real photos of installateurs / loodgieters / dakdekkers — earnt usage rights from pilot clients with case studies.
- Until pilots are live, **no stock photos** on the marketing site. Use illustrations instead (see § 5.2).
- When stock is unavoidable (blog headers): Unsplash-Plus → European photographers only → no grinning-thumbs-up tropes.

### Illustration

Hand-drawn, single-line, kraan-blue ink on cream. Constraints:

| Rule | Why |
|---|---|
| One illustration per page maximum | Doesn't compete with the message |
| Line weight `2px` consistent | Identifies as one set |
| No faces in illustrations | Faceless brand (founder's constraint, see `05-content/channel-strategy.md`) |
| Subject matter: tools, dashboards, calling, scheduling | Tied to product reality |

If the designer can't deliver a small illustration set in scope, defer and ship text-only — better empty than off-brand.

### Iconography

Use **Lucide Icons** (https://lucide.dev/) — SVG, MIT-licensed, consistent stroke. Stroke width 2, never filled. No exceptions.

## 6. Layout grid

- 12-column grid, 1280px max content width, 24px gutter.
- Mobile-first breakpoints: 640 / 768 / 1024 / 1280px.
- Vertical rhythm: 4px base unit. All spacing is multiples of 4 (4, 8, 12, 16, 24, 32, 48, 64, 96).
- Cards: 1px `--kraan-stone-300` border, 12px radius, no shadow.
- Buttons: 8px radius, no shadow, no gradient, single solid background.

## 7. Voice in visuals

The visual identity must echo the writing voice (see `voice-and-tone.md`). Translation:

| Voice rule | Visual translation |
|---|---|
| Concreet boven abstract | Specific iconography (a real tap, a real phone, a real Google review star) — not abstract dots |
| Doe-maar-gewoon | Single-weight strokes, no decorative flourish |
| Eén belofte per zin | One headline per fold. One CTA per page. |
| Cijfers > adjectieven | Numeric statistics get their own visual block — large weight, accent colour |

## 8. Deliverables checklist (designer brief)

Give this list to the designer verbatim.

```
Deliverables — Klantkraan v1 (M1–M6)

1. Logo
   - Wordmark in 3 variants: primary, mono-white, mono-black
   - Optional pictogram: 3 explorations (directions A and C, per brief)
   - SVG masters + PNG @1024 + ICO favicon

2. Colour
   - Confirm the supplied 8-token palette renders accessibly together
   - Provide tints/shades for blue + rust if any are missing for UI states

3. Typography
   - Pre-configured CSS variables file (`tokens.css`) for the type scale
   - WOFF2 + WOFF subsets for Inter, Inter Tight, JetBrains Mono — Latin-1 only

4. Buttons + form components
   - Primary, secondary, ghost — 3 states each (default, hover, disabled)
   - Input, textarea, select — 2 states (default, error)
   - All as a single Figma library + Tailwind config file

5. 4 social-share templates
   - 1200×630 LinkedIn / OG image base
   - 1080×1350 LinkedIn vertical post base
   - 1080×1080 square base
   - 1920×1080 YouTube end-card

6. Email signature
   - HTML + plaintext, with logo + name + role + KVK number + DPA link

Out of scope (v2, month 9):
- Custom illustration set
- Brand video / motion
- Print collateral

Budget: €100–300. Fixed-price.
Timeline: 5 working days.
License: full copyright transfer to T4 Software Consulting BV. No "designed by" credit required in deliverables.
```

## 9. Sourcing the designer

| Route | Cost | When to pick |
|---|---|---|
| Fiverr Pro (logo + brand pack) | €100–250 | Default. Look for Dutch / Nordic portfolios. |
| 99designs contest | €300–500 | If Fiverr round comes back weak. Slower (7 days). |
| Upwork (junior NL designer) | €150–300 | If we want Dutch sensibility built-in. |
| v0 + Recraft (AI-generated, founder iterates) | €0–20 | Day-zero placeholder only. Replace within month 3. |
| Senior designer engagement | €1,500–3,000 | **Defer to month 9**. Justified when MRR > €15k and brand becomes a real moat. |

## 10. Brand asset storage

| Asset | Where | Permission |
|---|---|---|
| SVG masters, source files | `apps/marketing-site/public/brand/` in repo | Founder + future hires (read) |
| Figma master | Figma workspace (free tier) | Founder, designer, future hires (read) |
| Press kit (PNG, PDF, written brand-do-don't) | `klantkraan.nl/pers` (M3+) | Public |
| Internal brand bible v1 (this doc) | This file | Internal |

## 11. When to refresh

| Trigger | Refresh scope |
|---|---|
| 10 paid clients live | Photography refresh (real installateur photos replace illustrations) |
| €15k MRR | Senior-designer engagement for v2 system: motion, illustration set, full brand book |
| UK launch (M6+) | Locale-agnostic logo audit; possibly secondary wordmark for UK if name differs |
| Investor / strategic conversation | Defer until that's a real thing |

## Sources

- Inter font: https://rsms.me/inter/
- Lucide icons: https://lucide.dev/
- WebAIM contrast checker: https://webaim.org/resources/contrastchecker/
- WCAG 2.2 contrast guidelines: https://www.w3.org/WAI/WCAG22/quickref/
- SIL OFL license: https://openfontlicense.org/
- Cross-references: `01-strategy/positioning.md`, `09-brand/voice-and-tone.md`, `09-brand/naming-and-domain.md`, `05-content/channel-strategy.md`
