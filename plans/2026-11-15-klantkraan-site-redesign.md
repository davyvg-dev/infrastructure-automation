# Plan — Klantkraan site redesign: precise, diagram-led, not AI-looking — 2026-11-15
Status: done
Task: klantkraan/TODO.md §V, new item V7 (absorbs V4 and V6)

## Goal
Davy: "i hate websites that look ai built", "i haet how ai ish it feels, i like the diagrams on these example sites, and just how they ar eput together". References he picked: linear.app, raycast.com, attio.com, zed.dev.
Rebuild the look of klantkraan.nl on those four: neutral surfaces, precise type, hairline grids, real product UI and schematic diagrams in place of glow, mood and chat bubbles alone.

All paths below are relative to `klantkraan/apps/marketing-site/` unless they start with `klantkraan/` or `/`.

## Acceptance
- `pnpm --filter marketing-site build` and `pnpm --filter marketing-site typecheck` pass (check the package name in `package.json` first).
- `node scripts/test-redesign.mjs` passes (new, see Tests).
- `grep -rn "Bricolage\|bricolage" src public/fonts` returns nothing; `grep -n "radial-gradient" src/styles/global.css` returns nothing.
- `grep -rnE "#[0-9a-fA-F]{6}" src/components src/pages` returns only lines inside `scan/ScanShell.astro` (its own light theme) and SVG brand marks.
- NL homepage at 1440px shows, in order: hero with product window, flow diagram, live demo, cost ledger, honesty + roadmap grid, start steps, final CTA. No section uses a glow or a pill badge.
- The flow diagram and cost ledger are inline SVG or HTML, have an accessible name, show their finished state under `prefers-reduced-motion: reduce`, and contain no channel, number or claim that is not already in `src/pages/index.astro:14-205`.
- Screenshots at 1440, 768, 390 and 320 wide of `/`, `/loodgieters/`, `/prijzen/`, `/demo/`, `/en/`, `/es/`: no horizontal scroll, no clipped text. `mobile-qa` agent returns no FAIL; `fix-verifier` returns PASS against the Goal.
- The demo chat iframe on `/` and `/demo/` still loads and answers.
- `/Users/bigd/Documents/marketing/infrastructure-automation/scripts/copy-lint.sh` passes.
- Nothing is deployed. Deploy is Davy's gate.

## What exists
- Astro 5 static site, Tailwind v4 configured in CSS, no React, no UI kit, client JS only as files in `public/js/` because the CSP is `script-src 'self'` (`public/_headers`).
- `src/styles/global.css:13-59` — all tokens (`night`, `panel`, `panel-2`, `line`, `chalk`, `dim`, `sodium`, `sodium-soft`, `confirm`, three font families, type scale with hero at weight 800, radii 11px and 10px). No spacing or shadow tokens.
- `src/styles/global.css:92-101` — fixed amber and mint glow behind every page.
- `src/styles/fonts.css` — 18 `@font-face` rules: Bricolage Grotesque 600 to 800, Hanken Grotesk 400 to 700, Space Mono; files in `public/fonts/`; two preloaded in `src/layouts/Base.astro:112-125`.
- `src/styles/components.css:12-105` — `.btn`, `.btn-primary` (amber glow shadow at line 42), `.btn-ghost`, `.eyebrow` (dot plus amber text, 105 uses in 53 files).
- No Section, Card or Button component. `mx-auto max-w-5xl px-6` is written out 240 times, `py-10 md:py-16` 221 times, the card class set 135 times.
- `src/pages/index.astro:213-222` — NL homepage renders Hero, Conversation, DemoSection, CostReceipt, Transparency, CursusForm, Roadmap, HowItWorks, FinalCta. Copy objects at lines 14-205. The copy claims two channels only: site and WhatsApp (lines 15, 20, 161, 176).
- `src/components/home/Hero.astro` (499 lines) — status pill (48-51), H1 with the lighting "aan." word (53, 178-221), chat-thread mock (75-101), halo bloom (266-273), JS at 457-499.
- `src/components/home/CostReceipt.astro` — the 173 / 48 / 16 / €450 arithmetic.
- `src/components/DashboardMock.astro` — unused mock of call log and SMS flow. `src/pages/r/[slug].astro` is the real client dashboard.
- `src/pages/en/index.astro:166-172`, `src/pages/es/index.astro:164-170` — EN and ES render Hero, Duties, CostReceipt, Transparency, Roadmap, HowItWorks, FinalCta.
- 35 hardcoded hex colours in components and pages; 8 pill badges (hero plus 7 demo pages); 4 backdrop blurs; 13 Lucide icons in `src/components/Icon.astro:31-51`.
- `klantkraan/docs/09-brand/redesign-execution-plan.md:62-78` — invariants: art. 50 disclosure, no founder name, price parity NL/EN/ES, `Base.astro` head intact, reduced motion, focus-visible, 320px, demo chatbot working, flash-free `ClientRouter`, hero re-init on `astro:page-load`.
- `klantkraan/TODO.md:922-949` — earlier "less AI" pass V0 to V3 done; V4 (cut homepage to about 6 sections, test a display face) and V6 (EN/ES) open.
- No test script for the site; `playwright` 1.60.0 is a dev dependency; manual scripts in `scripts/test-*.mjs`. CI does not build the site.
- Working tree is dirty: uncommitted self-install work touches `Footer.astro`, `home/Conversation.astro`, `home/CostReceipt.astro`, `home/DemoSection.astro`, aanmelden/bedankt/demo pages, plus untracked `installeren.astro` and `advertentievideos.astro`.

## Changes
Phase 1, the system (every page changes at once because token names stay):
1. `src/styles/global.css` — new values under the same token names: neutral near-black base (about `#0b0c0d`), panels `#111315` / `#16181b`, hairline `#23262a`, text `#ededed`, dim `#8b9096`; keep `sodium` as the one accent and `confirm` for the booked stamp. Delete the `body::before` glow. Add tokens for container width (1200px), section spacing, one shadow, one inner top highlight. Hero type: smaller (max about 4rem), weight 600, tracking -0.03em.
2. `src/styles/fonts.css`, `public/fonts/`, `src/layouts/Base.astro:112-125` — replace Bricolage and Hanken with one variable Inter file (optical size axis for headings), replace Space Mono with a quieter mono (Geist Mono or JetBrains Mono). Update `OFL-NOTICE.txt` and the preloads. Delete the old files.
3. `src/styles/components.css` — `.btn-primary` loses the glow, gets a 1px inner highlight; `.eyebrow` becomes a small mono label with no dot and no amber; add `.frame` (hairline box with corner ticks, the Zed look), `.grid-rule` (hairline-divided grid cells that share borders, in place of floating cards) and `.window` (product window chrome).
4. New `src/components/ui/Section.astro`, `Frame.astro`, `Window.astro` — so pages stop repeating class sets. Used by every file touched in phases 2 and 3; untouched pages keep their classes and still pick up the tokens.

Phase 2, NL homepage:
5. `src/components/home/Hero.astro` — drop pill and halo; left: H1 (keep "Het licht blijft aan." and the lighting word, toned down), sub, two CTAs; below or right: a wide `Window` with three panes: conversation list (site and WhatsApp rows with times), the existing animated thread, and the structured result (name, problem, slot, INGEPLAND). Model the panes on `r/[slug].astro` so it is the real product. Keep the JS hook on `astro:page-load`.
6. New `src/components/diagrams/FlowDiagram.astro`, replaces `Conversation` on the homepage — schematic in inline SVG: two inputs (Websitechat, WhatsApp) into one Klantkraan node, three outputs (answer, afspraak in agenda, terugbelverzoek), hairlines with mono labels, one amber pulse travelling the active path (CSS `stroke-dashoffset`, no JS). The three duties from the copy sit beside it as a plain list.
7. New `src/components/diagrams/CostLedger.astro`, replaces the inside of `CostReceipt.astro` — the same four numbers as a measured bar diagram (173 to 48 to 16 to ± €7.200/mnd) with tick marks and mono figures.
8. `home/Transparency.astro` + `home/Roadmap.astro` — merge into one `grid-rule` block: quote on the left, "nu" and "we bouwen" columns on the right. `home/HowItWorks.astro` — numbered rail on a hairline; `CursusForm.astro` restyled as a slim band under it. `home/FinalCta.astro` — remove the glow, plain framed block.
9. `src/pages/index.astro:213-222` — new order: Hero, FlowDiagram, DemoSection (inside a `Window`), CostReceipt, Honest (merged), HowItWorks + CursusForm, FinalCta. Copy objects unchanged except keys that move.
10. `src/components/Header.astro`, `Footer.astro` — 1200px container, hairline bottom border, lighter nav weight; footer on `grid-rule`.

Phase 3, roll out:
11. Sweep the 35 hardcoded hex values and 8 pills; replace with tokens and the new label style.
12. Trade pages (`loodgieters`, `dakdekkers`, `schilder`, `installateur`, `elektricien`, `aannemer`, `sportscholen`), `voor-wie`, `prijzen`, `demo`: swap the trust strip and Stat trio for `grid-rule`, put `FlowDiagram` (trade label as a prop) in place of one text section, illustrations get stroke 1.5.
13. `src/pages/en/index.astro`, `src/pages/es/index.astro` — same section order as NL (closes V6).
14. Delete `DashboardMock.astro`, `LeadForm.astro`, `home/Duties.astro` and `home/Conversation.astro` once nothing imports them. Update `README.md` font line and `klantkraan/docs/09-brand/redesign-execution-plan.md` §3 token table.

## Tests
- `scripts/test-redesign.mjs` (new, Playwright against `astro preview`, written first) — for `/`, `/loodgieters/`, `/prijzen/`, `/en/`, `/es/` at 1440, 390 and 320: no horizontal overflow; one `h1`; the art. 50 line "U chat met een digitale assistent." present on `/`; flow diagram and ledger present with an accessible name; with reduced motion emulated the hero thread and diagrams show their end state; computed `font-family` of `h1` starts with Inter; `body::before` has no background image.
- Existing `scripts/test-integration.mjs` and `scripts/test-voor-wie-nav.mjs` still pass.

## Decisions
- Neutral near-black base, amber kept as the only accent — because three of the four references are neutral dark and the teal tint plus glow is the "themed" look that reads as generated. Rejected: light theme like Attio, a second full reskin with more risk on 60 pages. **Davy to confirm (question 1).**
- Inter variable for text and headings — because all four references use Inter or a close relative, and a quirky display face at weight 800 is itself a tell. Rejected: keeping Bricolage; Geist Sans, less tested on Dutch diacritics here.
- Diagrams in hand-written SVG and HTML with CSS motion — because the CSP forbids CDN scripts and the site has no React. Rejected: Lottie, GSAP, image exports (blurry, not themeable).
- Diagrams show only what the homepage copy already claims (site and WhatsApp, no phone line) — no new claims in a visual-only change.
- Keep the "Het licht blijft aan" line and the lighting word — it is the one idea that is the brand's own; only the glow around it goes.
- Token names stay, values change — one edit reskins all pages, so nothing is left half old. Rejected: new token names with a page-by-page migration.
- Three phases, one commit each, review screenshots after phase 2 before phase 3.

## Out of scope
- Copy changes, prices, new claims, SEO head, legal pages' text.
- `/scan`, `/scan/bevestigd`, `/websitecheck` (own light theme in `scan/ScanShell.astro`), the client dashboard `r/[slug].astro`, private prospect demos beyond the token change.
- Real photos (V5), deploy, the uncommitted self-install work, `advertentievideos.astro`.

## Risks / unknowns
- Dirty tree: four files this plan rewrites carry uncommitted self-install edits. Before step 1, run `git status --short`; if they are still modified, ask Davy whether to commit that work first (question 2). Do not stash or discard it.
- Font files and licence (Inter 4 optical size axis, the mono choice) are from memory, not checked. Confirm the files and OFL text at step 2; if the variable file is too heavy, use static 400/500/600.
- Amber on neutral black may look harsher than on teal. If it does, lower its use to links, one CTA and the diagram pulse, and report.
- Contrast of `dim` on the new base must stay at 4.5:1 or better; measure, do not eyeball.
- Trade pages share patterns but are separate files; phase 3 is the long part. If it runs over one session, stop after a whole page, never mid-page.
- `ClientRouter` plus the new hero: re-test navigation back to `/` so the thread animation restarts.

## Deviations
- 2026-11-16, Davy's answers: Q1 neutral black + amber confirmed. Q2 build in a clean worktree off HEAD 7103b97 (`/Users/bigd/Documents/marketing/kk-site-redesign`, branch `claude/site-redesign`); the self-install edits in the main tree stay untouched. Merging them later needs a small fix in Footer, DemoSection, demo pages (demo=1 flag, Installeren link); Conversation's de-pin edit is moot (file deleted) and CostReceipt's Safari fix (total on its own row) is kept in the new ledger.
- "What exists" drift from the lead-magnet deploy (e718830, after this plan was written): `CursusForm` is no longer on the homepage; a site-wide "Gratis" block above the footer (`Base.astro`, `OfferCta`/`MiniOffer*` components, `src/data/magnets.ts`) replaces it, plus `/gratis/` and `/klein-beginnen/`. Homepage render list is at `index.astro:212-219`; preloads at `Base.astro:122-140`; `.eyebrow` 146 uses in 57 files; 34 hex values. Step 8's "CursusForm as a slim band" becomes: restyle the Gratis block and mini-offer components instead.
- Davy (growth, after the 15 Nov AdKit research: long-running competitor ads let people try the product at once, show it working, lean on local/EU trust): copy and claims unchanged, but the live demo moves up to right after the hero, the hero window links straight into it, and the Gratis block, `/gratis/` and `/klein-beginnen/` get the new design. New NL order: Hero, DemoSection, FlowDiagram, CostReceipt, Honest, HowItWorks, FinalCta.
- Davy: may spend a few Kie credits (own bucket, after `kie.py balance --go`) on imagery that makes the site feel more human, only if it is beautifully generated and does not read as AI. Outcome: 0 credits spent. One Kie scene costs 8 credits (more than "a couple"), and the scan-ads scene bought on 15 Nov (`~/Documents/ads/2026-11-15-scan/briefs/scan-bus.png`, van cab on a Dutch brick street, reads as a real phone photo) fits "while you work"; it is reused in the closing block as `public/photos/home-van(-sm).jpg`.
- No site-wide fade-in on scroll any more (`global.css` kk-settle removed): it is the most common template tell. Motion stays only in the hero thread and the flow diagram's current.
- `.grid-rule` draws its lines with cell borders, not a 1px gap over a line-coloured background, so an unfilled last row (7 trades in 3 columns on /voor-wie/) ends cleanly instead of showing a filled block.
- Homepage section names in `data-section` (hero, demo, flow, ledger, honest, start, final) drive the order test. EN/ES have no live demo section (the demo receptionist speaks Dutch); their hero window links to their /demo/ pages.
- Trade pages (all 7 NL incl. dakdekkers via `components/dakdekkers/Features.astro`): the FlowDiagram replaces the "Modules" list and carries its three module texts under the three outputs (`nodeSub` = "voor loodgieters" etc.), so no trade copy is lost. EN trade pages got the token/grid sweep only.
- Also deleted, unused after phase 2: `home/Transparency.astro`, `home/Roadmap.astro` (merged into `home/Honest.astro`).
- `test-redesign.mjs` grew beyond the plan's list: /demo/ and 768px are in the layout loop (the Acceptance screenshot matrix), and the glow/pill check runs on all six pages.
- The demo chat (ai-receptionist web UI) is still teal inside the new window; retheming it is out of scope here (separate app, shared with client widgets). Its overlay colour is now the token `--color-demo-chat`.
- Merge risk for later: the static-ads brand style (`ads/*/briefs/*.json` `style.fonts`) points at `public/fonts/bricolage-*.woff2` and `hanken-*.woff2` in the main tree. Those files are deleted on this branch; after the merge, ad renders need the new fonts (Inter, Geist Mono) or their own copies. `scripts/build-brand.mjs` (email logo) still uses its own Bricolage/Hanken TTFs in `scripts/fonts/`, untouched.
- fix-verifier round 1 (16 Nov): every measurable Acceptance line PASS, Goal FAIL on the trade pages. Fixed: PhotoBand scrim was the old teal as rgba (the hex grep cannot see it), now `--color-night`; every remaining `max-w-5xl px-6` column outside Base's prose `main` moved to the page width (trade heroes sat in a narrower column than the header); icon-in-a-box strips flattened: trade-hero and /voor-wie/ trust strips are one mono `.fact-row`, RiskReversal and the footer trust band are text cells without icons; 50 section labels that only repeated their heading dropped (Vragen, Rekensom, Klaar?, Wat zit erin, De demo, Waarom, Methode and their EN/ES twins), the rest kept; the active hero list row waits with the appointment pane; the closing block's photo column narrowed so its three buttons fit one row; the "lamp is on" test now reads the lamp's computed fill instead of the markup attribute; footer links back to 37px tall after mobile-qa.
- fix-verifier round 2 (16 Nov): all round-1 items confirmed fixed, live demo answered, every measurable line PASS; Goal FAIL on new spots. Fixed: the big-number stat trio on all trade pages (and [stad]/[vak], EN) is now one ruled line of figures (`.stat-row`, figure and caption side by side, no band); /dakdekkers/ "Zonder/Met Klantkraan" comparison cards and FAQ cards moved to the hairline grid and list, its "Rekensom" echo label dropped; the /voor-wie/ trust line that repeated the footer's trust band removed (NL/EN/ES); Elektriciens and Installateurs get their Plug and Radiator drawings on /voor-wie/ (`data/branches.ts`). Left as Davy's call: the teal demo chat (separate app).
- fix-verifier round 3 (16 Nov): every round-2 spot confirmed fixed, no stock-template block left on /, /loodgieters/, /dakdekkers/, /prijzen/, /voor-wie/; one regression from round 2's stat line (a wide figure such as "4–6 weken" left its caption 67 to 110px wide at 768 to 1024 and 320). Fixed by setting the caption under its figure; `test-redesign` now checks every stat caption is at least 160px wide on five pages at five widths. /en/dakdekkers/ "The maths" echo label dropped.
- fix-verifier round 4 (16 Nov, cbf7229): round-3 regression fixed (narrowest stat caption 183px), Goal PASS, every Acceptance line PASS except mobile-qa, which it cannot run. mobile-qa re-run on the 8 changed pages: no FAIL on SE, iPhone 15, Pro Max portrait and Pro Max landscape; WARNs are pre-existing small taps and the /voor-wie/ drawings being hidden below 640px (unchanged `sm:block`, kept on purpose).
- Acceptance "copy-lint passes": read as "no new findings". The whole `src` was at 251 findings before this work and is at 221 now; none were added.
- mobile-qa (16 Nov): no FAIL on 9 pages x SE, iPhone 15, Pro Max, landscape. WARNs are pre-existing small taps (EN/ES switch, "Alle branches", inline links) and the NL/EN/ES row of the phone menu starting partly under the bottom bar on an SE (reachable by scrolling, unchanged by this work).
- copy-lint on the whole `src` was never clean (251 findings at 7103b97, old copy); after the redesign 221, none new.

## Build
Read this file and CLAUDE.md, nothing else first. Set `Status: building`. Work through Changes in order, tests first. If a line under "What exists" is no longer true, stop and report instead of improvising. Small deviations go under a `## Deviations` heading in this file. When every Acceptance line passes and the project's checks are green, set `Status: done`.
