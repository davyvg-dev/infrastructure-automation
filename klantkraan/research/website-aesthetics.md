# Klantkraan website aesthetics — audit + 2025-26 research + recommendations

**Prepared:** 2026-05-21
**Scope:** Diagnose why klantkraan.nl reads as "boring", benchmark against B2B SaaS gold standards and direct competitors, propose concrete visual upgrades that respect the brand brief and the `script-src 'self'` CSP.

---

## Executive summary

The site is **on-brand but visually under-utilised**. The brand brief at `klantkraan/docs/09-brand/visual-identity-brief.md` already permits single-line illustrations, larger stat treatments, and richer hero compositions — the live site uses none of them. Every cornerstone page follows the same hero → stats → features → ROI → FAQ pattern. Zero imagery, zero motion, zero product visualisation. Lucide icons are used as bullet points rather than as a designed visual language. The result is plain by omission, not by rule.

Three moves close most of the gap, in this order:

1. **A custom single-line illustration per cornerstone** (tap valve / ringing phone / storm cloud / paint roller / hard hat). The brief explicitly authorises this, and it removes the dominant "wall of text" feeling instantly.
2. **A real product screenshot in the hero or right after the hero** (the dashboard, the call-log, or an SMS preview). B2B SaaS golds (Linear, Mercury, Vercel, Stripe) all anchor a UI artefact above the fold. Klantkraan has nothing to anchor on.
3. **A founder photo + KvK number + AVG/AI Act badges in the footer**. Trust signals that fit when there are zero customers yet. Costs nothing visually but shifts perceived credibility hard.

Everything else (motion, palette warming, typography refinement, social proof restructuring) is incremental and can ship over the next two passes.

---

## 1. Current site state (verified 2026-05-21)

### Design system — what's actually in place

- **Colors** (CSS custom properties in `src/styles/global.css`): `--color-kraan-blue: #0F4C81` (Delftware primary), `--color-kraan-cream: #FAF6EE` (warm off-white background), `--color-kraan-ink: #1A1A1A`, `--color-kraan-rust: #C75A2B` (single accent per page), `--color-kraan-leaf: #3F7F4A` (success), stone-100–700 neutrals.
- **Typography**: Inter Tight (700/600) for display, Inter (400/500) for body, JetBrains Mono for numbers. Self-hosted, OFL — no Google CDN, CSP-clean.
- **Type scale**: hero 3.5rem → micro 0.75rem, responsive at 640px breakpoint. Line-height 1.55 on body, 70-char max line length.
- **Spacing + components**: 4px base rhythm, 12-column max-w-5xl container, 24px gutter. Cards: `--radius-card: 0.75rem`, 1px border, **no shadow**. Buttons: `--radius-button: 0.5rem`, solid single-color, no gradient.
- **Iconography**: Lucide only — 12 icons vendored as inline SVG (phone-call, shield-check, message-square, star, calendar-check, mail, check, zap, clock, wrench, chevron-down, phone). Stroke 2, never filled.

### What visual elements exist today

Every cornerstone (loodgieters, dakdekkers, schilder, installateur, aannemer, elektricien) plus index uses the same skeleton:

1. Hero — large H1 with one-word rust `<span>` accent, H3 subhead in stone-700, two CTA buttons, small icon+text trust signals.
2. Pain-stat band — stone-100 background, 3-column grid, value (H1 blue) + 10px rust bar above + label (stone-700).
3. Features list — icon + title + body, divide-y rows, max 3.
4. ROI snippet — white card on cream, rust accent on the hero number, dual CTA.
5. FAQ — `<details>/<summary>` disclosure, chevron rotates on open, FAQPage JSON-LD.
6. Final CTA band — full-bleed blue, white text, white button.

`/rekentool` adds an interactive ROI form (now working post-deploy). `/loodgieters` has an `<audio>` element pointing at a file that doesn't exist (`/audio/demo-loodgieter.mp3` → 404). `/dakdekkers` uses a per-page component split (Hero, PainStats, Features, StormScenario, RoiSnippet, Faq, CityLinks, FinalCta) but visually it lands on the same skeleton.

### Imagery inventory

- Present: `favicon.svg`, `og-default.png` (placeholder), three `public/js/*.js` scripts. That's it.
- **Absent**: zero photos, zero custom illustrations, zero product screenshots, zero dashboard mocks, zero call-log previews, zero SMS-preview images, no founder photo, no customer logos (none exist yet — acceptable), no social-share template variations, no branded assets in `public/brand/`, no `audio/demo-loodgieter.mp3` despite being referenced.

The site is **entirely text-based**.

### Where it reads as plain (the brutal version)

- Every page is structurally identical, so a visitor reading two cornerstones in a row sees the same shape twice. No visual variety = no memorability.
- Lucide icons at 24–28px next to two-line copy blocks read as bullet points, not as visual elements. They never lead the eye; they're decorative noise.
- The 10px rust bar above each stat is meant to be the "single accent block per page" but is so subtle it dies on the page. Compare to Mercury's universal-search illustration or Stripe's stripe motif — there is no equivalent anchor on klantkraan.
- The hero has zero supporting visual. The user's first impression is "a paragraph of Dutch text and two buttons." B2B SaaS golds in 2026 all anchor the hero on at least one of: screenshot, illustration, animated graphic.
- The audio demo (when the file exists) uses the unstyled browser `<audio controls>` element — instantly identifiable as un-designed.
- Lead form is a plain white card. No urgency, no testimonial beside it, no founder face.
- Footer has KvK/BTW marked TODO and no trust badges (AVG, AI Act, EU hosting). All the credibility levers are unpulled.

---

## 2. Competitor landscape (live audit, 2026-05-21)

Live fetches succeeded for the B2B SaaS golds; werkspot.nl is behind Cloudflare bot challenge; trustoo.nl is a consumer directory (less directly relevant).

### B2B SaaS gold standards

| Site        | Hero                                                                                   | Palette                                                 | Standout visual element                                               | Imagery strategy                                                                         |
| ----------- | -------------------------------------------------------------------------------------- | ------------------------------------------------------- | --------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| **Linear**  | Text + interactive screenshots demoing the issue tracker                               | Near-black, cyan accent                                 | Animated "Codex agent" terminal output (live status, real product UI) | UI screenshots throughout; zero stock photos                                             |
| **Vercel**  | Animated graphic — "nodes on the globe sending pulses" + tagline                       | Dark navy/charcoal + electric blue accent               | The pulsing globe = "global CDN" made visible                         | Animations + diagrams; UI shots for product sections                                     |
| **Stripe**  | Text + wave-pattern animated background                                                | White/off-white + deep navy text + electric blue accent | Recurring parallelogram/stripe motif framing real customer photos     | Real customer scenes (street, storefront) framed by brand-shaped geometry; minimal stock |
| **Mercury** | Text + animated UI frames                                                              | White + teal/cyan accent                                | "Universal search bar" illustration mid-page as "one command center"  | Illustrations over photos; alternating text/illustration layout                          |
| **Attio**   | (Fetch returned text-only; brand known: white + navy, video product loops in hero)     | Light + navy                                            | Looping UI video showing the product in action                        | Product video in hero, minimal photography                                               |
| **Resend**  | (Fetch returned text-only; brand known: pure black + orange accent, dense screenshots) | Black + orange                                          | Layered API-response screenshots stacked on the hero                  | UI screenshots are the entire visual identity                                            |

**Patterns common across all six**: a product artefact anchors the hero or appears within one scroll. None use stock photos of "the customer". None use decorative illustrations of office workers. Motion is restrained — animated UI states, not parallax circus.

### Direct competitors (AI receptionist / Dutch trades)

| Site              | Hero                                                                                         | Imagery                                                                       | Social proof                                                                   | Notable                                                                                                                             |
| ----------------- | -------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| **Smith.ai**      | Text + generic AVIF illustration                                                             | Illustrations only, no real photos                                            | None above the fold                                                            | Dual-form lead capture (AI-first vs Human-first preference) is a clear positioning move; trust-band is weak                         |
| **Goodcall**      | Text + emoji illustration ("AI phone calls made easy")                                       | AI-generated Gemini illustrations + partner logos (Google, Microsoft, Twilio) | "Born at Google" + metrics ("306 area codes, 50,000 agents, 60M interactions") | The big-number strip is the only thing that lands; "Championed by Industry Leaders" logo bar leans entirely on borrowed credibility |
| **Trustoo (NL)**  | Dark hero with white headline ("Leg uit wat je nodig hebt"), text-shadow, large display font | Consumer-directory tiles, reviews carousel, Dutch trade categories            | Customer-side reviews                                                          | Consumer marketplace, not direct B2B SaaS; Tailwind-based, dark hero is the one design move worth noting                            |
| **Werkspot (NL)** | (Cloudflare bot challenge — could not audit)                                                 | —                                                                             | —                                                                              | —                                                                                                                                   |

**What Dutch competitors do that the B2B golds reject**: dark hero with shadowed text (Trustoo), AI-generated graphics that read fake (Goodcall), no social proof at all (Smith.ai). None of these are templates Klantkraan should clone.

**What Goodcall got right that Klantkraan can steal**: the big-number metric strip ("306 area codes · 50,000+ agents · 60M+ interactions"). Klantkraan has the pieces — "28% gemiste oproepen", "€450 per klus", "AI antwoordt in 4 sec" — but presents them small.

---

## 3. B2B SaaS visual design principles (2025-26)

Sourced research, summarised tight.

### Imagery strategy

- **Screenshots > illustrations > stock photos.** Real product UI satisfies cautious B2B buyers' "show, don't tell" instinct. ([SaaS Hero](https://www.saashero.net/design/best-saas-visuals-b2b-ads/), [Marketing Mix](https://www.themarketingmix.agency/post/product-visuals-for-saas-startups-photos-screenshots-or-illustrations))
- **Stock photos of "the customer" actively hurt trust.** 71% of users recognise stock instantly; 65% say it damages credibility. A real-photo test lifted signups +35% vs. the best stock photo. ([CXL](https://cxl.com/blog/stock-photography-vs-real-photos-cant-use/)) For a Dutch roofer audience this would be a hard "no" — generic American smiling-handyman stock is unmissable.
- **No-imagery / typography-as-hero is a legitimate 2026 pattern** (Linear, Vercel, Mercury). "Confidence in typography signals confidence in the product." ([Framiq](https://framiq.app/blog/best-saas-landing-pages-2026), [LogRocket on Linear](https://blog.logrocket.com/ux-design/linear-design/))

### Hero patterns that convert

- **Single-stat / single-claim hero**: +18% lift in 2026 panel tests of 2,000 pages. One big number beats everything else. ([Digital Applied](https://www.digitalapplied.com/blog/landing-page-conversion-study-2000-pages-tested-2026))
- **Video heroes**: −7% in the same test. Skip.
- **Asymmetric-with-product-shot**: still strong, but reflow on mobile becomes the design problem.
- **Centred-text-only**: lowest-risk, fastest LCP, best mobile parity — but typography has to carry the page.
- **H1 constraint**: under 8 words / 44 chars. Must answer _what, who, why_ in 5 seconds.

### Colour and typography

- **"Blue is invisible in 2026."** Every fintech/SaaS uses the same indigo. Differentiation comes from warm neutrals (cream, sand, putty) instead of cool zinc/slate. ([Tentackles](https://tentackles.com/blog/b2b-saas-color-palettes-2026-that-stand-out)) — Klantkraan's `#FAF6EE` cream + `#0F4C81` blue is closer to right than wrong, but the rust accent is too sparse to register.
- **One family, two weights** is the pattern at 41% of high-converting B2B sites. ([FullStop](https://fullstop360.com/blog/insights/branding/saas-typography-playbook-what-leading-companies-use)) Klantkraan currently uses two: Inter Tight (display) + Inter (body) — borderline. Could simplify to one family at the cost of some display character.

### Social proof when you have zero customers

Ranked by credibility for pre-launch:

1. **Compliance + certification badges** — KvK number, BTW-id, AVG/GDPR statement, EU AI Act art. 50 disclosure compliant, ISO badges. Already partially in scope; not yet on the site.
2. **Quantified non-customer metrics** — "AI antwoordt binnen 4 sec", "24/7 bereikbaar", "Eerste maand gratis." Replace the "X customers trust us" pattern wholesale until pilots ship. ([LaunchWall](https://launchwall.online/blog/social-proof-for-saas-landing-pages))
3. **Vendor/tech-stack logos** — "Draait op Synthflow, n8n, Mollie, EU-gehost op Hetzner." Borrows credibility from upstream brands.
4. **Founder face + story + KvK link** — the "handmade designs as trust signal" pattern NN/G documents. ([NN/G](https://www.nngroup.com/articles/handmade-designs/))
5. **Risk-reversal guarantee** — "Eerste maand gratis, opzegbaar per direct, geen wurgcontract." Converts higher than a missing testimonial wall. ([Crazy Egg](https://www.crazyegg.com/blog/trust-signals/))

### Motion + micro-interactions

- **2026 bar**: subtle scroll reveals via `IntersectionObserver`, CSS-only hover lifts on cards, View Transitions for page-to-page fades. ([WebPeak](https://webpeak.org/blog/css-js-animation-trends/))
- **Astro 5 View Transitions** are stable and run **without** violating `script-src 'self'`. Page fades come free.
- **Lottie**: only with self-hosted JSON + self-hosted player (CSP-safe), budget < 30KB, max two per page.
- **Avoid**: GSAP/Framer Motion (extra JS), autoplay video, mobile parallax.

### Mobile-first reality check

- 60-68% of B2B research is mobile, closer to 90% for tradespeople reading during a break.
- Mobile-fragile patterns: asymmetric heroes, horizontal logo bars, 3-column tables.
- Mobile-robust: centred-text hero, single-column FAQs, **sticky-bottom CTA (+11% lift)**.

### Accessibility + performance ceiling on Klantkraan's stack

- Astro 5 + Tailwind 4 static on Cloudflare Pages can hit perfect LCP/INP with zero JS shipped.
- `script-src 'self'` rules out Calendly/Cal.com embeds, Lottie CDN, YouTube iframes that load extra script, Hotjar, Intercom widgets. All animation must be CSS, View Transitions, or self-hosted JS.
- Realistic ceiling: heavy AVIF/WebP hero image under 150KB, one SVG/Lottie illustration, CSS animations, View Transitions. Anything more is vanity, not conversion.

---

## 4. Recommendations — ranked by impact-per-effort

Each entry: what it is, why it lifts the page, effort (S/M/L), and which file(s) it touches.

### Tier A — biggest visual lift, ship first

**A1. Custom single-line illustrations, one per cornerstone.** Brief § 5.2 explicitly authorises "hand-drawn, single-line, kraan-blue ink on cream — tap valve, ringing phone, storm cloud, scheduling, calling." Five SVGs at ~5KB each. Place in the hero (right column on desktop, above the H1 on mobile). Effort: **M** (need a designer or careful Figma export; the brief says one per page max, so 5–6 SVGs total). Files: `public/brand/illustrations/*.svg`, plus an `<img>` per cornerstone hero.

**A2. Product screenshot above the fold.** Even a single dashboard mock (call log → SMS preview → review request) anchors the product. If a real dashboard isn't ready, ship a Figma-exported PNG mock of the call-log view + missed-call SMS. Place after the hero, full-bleed on stone-100 background. Effort: **M**. Files: new `public/brand/screenshots/dashboard-call-log.png`, one section per cornerstone.

**A3. Footer trust band — KvK + AVG + AI Act + Founder.** Replace the TODO placeholders with: KvK number, BTW-id, "AVG/GDPR-conform", "EU AI Act art. 50 disclosure", "EU-gehost (Hetzner Frankfurt + Neon EU + Cloudflare EU)", founder name + photo + 1-line bio. Effort: **S**. File: `src/components/Footer.astro` + `public/brand/founder.jpg`.

**A4. Big-number quantified-stat strip on the homepage.** Three numbers across (`4 sec. AI-responstijd · 24/7 bereikbaar · Eerste maand gratis`), big-type (text-hero), warm cream background, no chrome. Replaces the missing "customer-logo bar" slot under the hero. Effort: **S**. File: `src/pages/index.astro` + a new `src/components/QuantStripe.astro`.

### Tier B — second pass

**B1. Astro 5 View Transitions for page-to-page fades.** Drop `<ViewTransitions />` into `Base.astro`. Zero JS shipped, page transitions become subtle fades. Effort: **S**. File: `src/layouts/Base.astro`.

**B2. Scroll-reveal fade-in on cornerstone sections.** Self-hosted ~1KB `IntersectionObserver` script under `public/js/reveal.js`; add `data-reveal` to top-of-section blocks; CSS transitions opacity + transform. Effort: **S**. Files: new `public/js/reveal.js`, `src/styles/global.css` (small additions), per-page data attrs.

**B3. Audio demo — actually create the file + style the player.** Generate `/audio/demo-loodgieter.mp3` (a 30–45-sec Synthflow recording handling a spoed call) and style the `<audio>` element with custom controls. Effort: **M** (audio work, plus custom controls = some JS in `public/js/audio-player.js`). Files: `public/audio/*.mp3`, `public/js/audio-player.js`, audio-related sections.

**B4. Sticky-bottom mobile CTA bar.** On viewports < 768px, fix a thin bar at the bottom of the viewport with "Probeer demo" + phone icon. +11% lift per Digital Applied. Effort: **S**. File: `src/components/StickyMobileCta.astro` + import in `Base.astro`.

### Tier C — third pass / brand-vanity-but-nice

**C1. Hover-lift micro-interactions on cards** (CSS only, `transition`, `transform: translateY(-2px)`, light shadow appears on hover). Effort: **S**. Brief currently says no shadows — would need a one-line brief amendment to allow hover-only shadow.

**C2. Logo polish in the Header.** The header currently shows "klantkraan" as text (font-display, text-h3, blue). Could replace with a small SVG logomark. Brief specifies blue ink on cream, single-line. Effort: **M**.

**C3. Per-niche accent illustration in the FAQ section.** A second illustration deep in the page to break up the divide-y rows. Stretches the "one illustration per page max" rule — would need a brief amendment. Effort: **M**. Risk: breaks the brief's restraint principle.

### What NOT to do (anti-patterns the brief locks down)

- ❌ Stock photos of tradespeople in overalls. (Brief § 5.1 + CXL data.)
- ❌ Emojis anywhere. (Brief + CLAUDE.md.)
- ❌ HeyGen/Synthesia avatars. (Founder constraint in CLAUDE.md.)
- ❌ Disabling the EU AI Act art. 50 disclosure on the Synthflow agent — ever. (CLAUDE.md.)
- ❌ Multi-color gradient buttons. (Brief § 6.)
- ❌ Dark mode default. (Brief mandates cream background.)
- ❌ Italic on the marketing site. (Voice-and-tone.md — reads as AI-generated to Dutch B2B.)
- ❌ Decorative parallax / 3D / Framer Motion. (CSP + perf ceiling.)
- ❌ Customer-logo bar with fake logos. (No customers yet.)

---

## 5. Sources

| Source                                                                                                                                                                  | Purpose                                                               |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| [SaaS Hero — Best SaaS Visuals B2B Ads](https://www.saashero.net/design/best-saas-visuals-b2b-ads/)                                                                     | Screenshots vs illustrations vs stock photos in B2B                   |
| [SaaS Hero — High-converting landing pages](https://www.saashero.net/design/high-converting-landing-page-examples/)                                                     | Hero patterns + H1 length                                             |
| [SaaS Hero — Mobile-first B2B SaaS ads](https://www.saashero.net/design/mobile-first-saas-b2b-ads/)                                                                     | Mobile-first viewing share                                            |
| [Marketing Mix — Photos vs screenshots vs illustrations](https://www.themarketingmix.agency/post/product-visuals-for-saas-startups-photos-screenshots-or-illustrations) | Imagery strategy                                                      |
| [CXL — Stock vs real photos](https://cxl.com/blog/stock-photography-vs-real-photos-cant-use/)                                                                           | +35% real-photo lift, 71% stock recognition                           |
| [Design Web Local — Local vs stock](https://designweblocal.com/local-vs-stock-photography-the-data-behind-authentic-visual-content/)                                    | Stock photo damage in B2B trust                                       |
| [Digital Applied — 2026 landing page study (2000 pages)](https://www.digitalapplied.com/blog/landing-page-conversion-study-2000-pages-tested-2026)                      | Hero patterns; +18% single-stat hero; +11% sticky CTA; −7% video hero |
| [Framiq — Best SaaS landing pages 2026](https://framiq.app/blog/best-saas-landing-pages-2026)                                                                           | Centred-text hero pattern (Linear)                                    |
| [LogRocket — Linear-style design](https://blog.logrocket.com/ux-design/linear-design/)                                                                                  | Typography confidence pattern                                         |
| [Tentackles — B2B SaaS palettes 2026](https://tentackles.com/blog/b2b-saas-color-palettes-2026-that-stand-out)                                                          | Warm neutral palettes                                                 |
| [Recursion — UI color trends 2026](https://recursion.software/blog/ui-color-trends-2026)                                                                                | 2026 colour direction                                                 |
| [Pravin Kumar — Inter / Geist / Plus Jakarta](https://www.pravinkumar.co/blog/inter-geist-plus-jakarta-sans-webflow-b2b-2026)                                           | Mainstream B2B typography                                             |
| [FullStop — SaaS typography playbook](https://fullstop360.com/blog/insights/branding/saas-typography-playbook-what-leading-companies-use)                               | One-family-two-weights pattern                                        |
| [GTM Works — Social proof checklist](https://www.gtmworks.ai/blog/how-to-build-social-proof-for-saas-social-proof-checklist)                                            | Pre-launch trust signals                                              |
| [LaunchWall — Social proof 2026 guide](https://launchwall.online/blog/social-proof-for-saas-landing-pages)                                                              | Quantified non-customer metrics                                       |
| [TrustSignals — Trust signals chapter 5](https://www.trustsignals.com/blog/chapter-5-website-trust-signals-making-visitors-feel-at-home)                                | Footer + cert badges                                                  |
| [Crazy Egg — Trust signals](https://www.crazyegg.com/blog/trust-signals/)                                                                                               | Risk-reversal vs testimonial                                          |
| [NN/G — Handmade designs as trust](https://www.nngroup.com/articles/handmade-designs/)                                                                                  | Founder photo pattern                                                 |
| [NN/G — Photos as web content](https://www.nngroup.com/articles/photos-as-web-content/)                                                                                 | Real-people photography                                               |
| [WebPeak — CSS/JS animation trends 2026](https://webpeak.org/blog/css-js-animation-trends/)                                                                             | Motion restraint                                                      |
| [Techqware — Motion design 2026](https://www.techqware.com/blog/motion-design-micro-interactions-what-users-expect)                                                     | Micro-interaction expectations                                        |
| [PixelFree — Motion + performance](https://blog.pixelfreestudio.com/the-impact-of-motion-design-on-web-performance/)                                                    | Lottie budget guidance                                                |
| [Blend B2B — 15 best SaaS websites 2026](https://www.blendb2b.com/blog/the-15-best-saas-website-examples)                                                               | Asymmetric hero examples                                              |
| [Sitepins — Astro in 2026](https://sitepins.com/blog/astro-sitepins-2026)                                                                                               | View Transitions stable; perf ceiling                                 |
| [Educative — Astro + Core Web Vitals](https://www.educative.io/courses/building-static-pages-with-astro-for-perfect-core-web-vitals)                                    | Static-site perf ceiling                                              |
| Live audits (WebFetch, 2026-05-21)                                                                                                                                      | Linear, Vercel, Stripe, Mercury, Smith.ai, Goodcall homepages         |
| Live audits (curl + UA, 2026-05-21)                                                                                                                                     | Trustoo.nl (Werkspot.nl bot-challenged)                               |
| Klantkraan source (2026-05-21)                                                                                                                                          | `src/styles/global.css`, all cornerstones, `docs/09-brand/*`          |

---

_Demand-bucket caveats from `serp-audit.md` apply here too — competitor SERP screenshots, palettes and structures change frequently. This artifact captures the picture on 2026-05-21. Re-audit before any major redesign more than 6 months later._
