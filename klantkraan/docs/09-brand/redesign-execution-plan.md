# Site-wide redesign — execution plan ("Het licht blijft aan")

**Status:** Phase 0 + Phase 1 (home) + Phase 2 **G1 (trade landings)** + **G2 (conversion pages)** + **G3 (`[stad]/[vak]` + `r/[slug]`)** complete 2026-07-23.
Preview alias LIVE: `https://redesign.klantkraan-marketing.pages.dev` (apex still old design).
Next = Phase 2 **G4 (reading variant)** — blog/gidsen/legal/404 in the calm document layout.
**Visual reference (north star):** `redesign-concept-2026-07-23-light-stays-on.html` (this folder — open in a browser for the real fonts).
**Progress mirror:** `klantkraan/TODO.md` § H (checkboxes there track the same phases).

This document is the single source of truth for the redesign. It is written to survive
context clears: any fresh session resumes from the **Resume preamble** below, works exactly
one phase, appends to the **Migration log**, and stops at the next checkpoint.

---

## 0. Resume preamble (read this first, every new session)

1. Read this file top-to-bottom, plus `TODO.md` § H.
2. Open the visual reference `redesign-concept-2026-07-23-light-stays-on.html`.
3. Read the tail of the **Migration log** (§ 8) — it says what's done and what bit us last time.
4. Do the **next unchecked phase only**. Respect the Ralph gates. Stop at the checkpoint.
5. Before stopping: append a Migration-log entry, tick the boxes here + in TODO § H, commit.

Founder-approved decisions (2026-07-23):
- **Rollout:** build on the branch, deploy to a Cloudflare Pages *preview* alias, keep the
  apex `klantkraan.nl` on the current design the entire time, one **atomic cutover** at the end.
- **Scope:** every page (all 47 + the `[stad]/[vak]` template), all three locales. Marketing
  pages get full energy; legal + blog/gidsen get a calm **reading variant** (same palette, no
  animated hero).
- **Rhythm:** foundation + home built **serially** in the main loop first. After that, page
  groups may be **drafted by parallel subagents**, but the main loop always verifies
  (build → typecheck → eyeball) and commits each page serially through the Ralph gates.

---

## 1. Rollout mechanic — how the site stays online

Cloudflare Pages has no git integration here; the live site changes **only** when we run
wrangler. So the branch work is invisible to the public until we choose to cut over.

- **Preview deploy** (safe, use throughout): a non-production branch name produces a preview
  deployment with its own alias URL, leaving the apex untouched:
  ```
  cd klantkraan/apps/marketing-site
  pnpm build
  pnpm dlx wrangler@4 pages deploy ./dist --branch=redesign --project-name=klantkraan-marketing
  ```
  First run: capture the alias URL wrangler prints (expected `redesign.klantkraan-marketing.pages.dev`)
  and record it in the Migration log. Give that URL to the founder for review.
- **Production cutover** (Phase 4 only, after founder go): swap `--branch=redesign` for
  `--branch=production`. That is the single command that flips `klantkraan.nl`.
- **Cache note:** a fresh asset path can edge-cache the SPA HTML fallback mid-propagation.
  Verify new assets via the deploy alias, not the plain prod URL; bust with `?v=` (token has
  no cache_purge). See memory `project_pages_new_asset_cache_poison`.

---

## 2. Invariants — never break these during the reskin

The redesign is **visual only**. Every rebuilt page must still:

- Open with the **art. 50 disclosure** ("U chat met een digitale assistent." / locale copy).
- Contain **no founder name** — "de oprichter" / "Klantkraan".
- Keep **price parity** across NL / EN / ES.
- Keep everything in `Base.astro`'s `<head>`: canonical, hreflang, Organization + WebSite
  schema, OG/Twitter, skip-link, sitemap. Only `theme-color` changes (`#0F4C81` → `#0f1c1e`).
- Introduce **no AI-tells** in copy (no decorative em-dashes, no "unlock/elevate/seamless").
  The de-AI pass is already done and deployed — do not regress it.
- Preserve: `prefers-reduced-motion` (animations off → static), visible `:focus-visible`,
  keyboard nav, mobile down to 320px, the `/demo` embedded chatbot working.
- Keep `ClientRouter` view-transitions flash-free (no light→dark flash on navigation) and
  re-init the hero animation after client-side navigation (`astro:page-load`, not `DOMContentLoaded`).

---

## 3. Token map — old (light) → new (dispatch dark)

Do **not** repoint the old `kraan-*` values in place (a token named `ink` pointing at chalk is
a landmine). Introduce the new semantic tokens in `@theme`, migrate each component's classes to
them during rebuild (so every component gets eyes), and delete the `kraan-*` tokens once
`grep -r kraan- src` is empty.

| Old token | New token | Value | Role |
|---|---|---|---|
| `kraan-cream` | `night` | `#0f1c1e` | page base bg |
| — | `panel` / `panel-2` | `#16292b` / `#1c3335` | raised surfaces |
| `kraan-stone-300` | `line` | `#26403f` | borders / dividers |
| `kraan-ink` | `chalk` | `#f4efe6` | primary text |
| `kraan-stone-500/700` | `dim` | `#93a6a2` | muted text |
| `kraan-blue` (+700/300) | `sodium` / `sodium-soft` | `#ffb84d` / `#ffd089` | the single accent, links, CTAs |
| `kraan-rust` | `sodium-soft` | `#ffd089` | hover accent |
| `kraan-leaf` | `confirm` | `#63d3ab` | rationed — "booked" stamp only |

Type: `--font-display` Inter Tight → **Bricolage Grotesque**; `--font-sans` Inter → **Hanken
Grotesk**; `--font-mono` JetBrains Mono → **Space Mono**. Radii align to the concept
(`--r: 11px` cards, 10–12px buttons).

**Styling approach:** keep Tailwind v4 as the utility engine (redefine `@theme` values only).
The concept's signature pieces — dispatch panel/log, clock-time ledger, receipt tally — go in a
scoped `@layer components` block (reused) or the owning component's `<style>` (one-offs like the
hero). Watch selector specificity on section padding/margins (frontend-design skill warning).

---

## 4. Phase plan + checkpoints

`■` = context-clear checkpoint (commit, update log, then a fresh session may resume).
Ralph gate for every page: **build → `astro check` → eyeball (Playwright screenshot) → commit.**

### Phase 0 — Foundation (serial, main loop) — no page looks right until this is done
- [x] 0.1 Self-host the three fonts. 18 latin + latin-ext woff2 subsets from Google Fonts CSS2
      (Bricolage 600/700/800, Hanken 400/500/600/700, Space Mono 400/700) in `public/fonts/`,
      `font-display:swap`, unicode-range preserved; `src/styles/fonts.css` + OFL notice. Regen
      with `scratchpad/fetch_fonts.py`. (commit 9eb015b)
- [x] 0.2 Palette + type + base ported into `global.css` `@theme` (§ 3 map). Dark `html`/`body`,
      `::selection`, sodium focus ring, reduced-motion block, ambient glow via `body::before`.
      Old `kraan-*` tokens kept (deprecated) so un-migrated pages still build. (commit 9eb015b)
- [x] 0.3 Chrome rebuilt: `Header` (sticky blurred, lamp, dim nav, sodium switcher), `Footer`
      (trust band + calm dim links), `StickyMobileCta` (sodium primary), `Base` (theme-color +
      skip-link). Head machinery intact. Verified via Playwright screenshot. (commit 91bc019)
- [x] 0.4 UNIVERSAL primitives only: `.btn/.btn-primary/.btn-ghost/.btn-lg` + `.eyebrow` in
      `src/styles/components.css` (`@layer components`). **Home-specific signatures (dispatch
      log, ledger, receipt, duty cards) deferred to Phase 1** — built + verified in context there,
      then reused. (commit 91bc019)
- **■ Checkpoint 0 — DONE 2026-07-23.** Foundation committed, build green, chrome eyeballed.
  Safe to clear context. Next session: Phase 1 (home).

### Phase 1 — Reference page: HOME (serial, main loop) — proves the whole system
- [x] 1.1 Rebuild `index.astro` (NL) to near-parity with the concept, on the foundation.
      frontend-design skill used for the hero fidelity. (commit faf1e29)
- [x] 1.2 Audit with **web-design-guidelines** skill; fix findings. (commit cd83615)
- [x] 1.3 Screenshot (desktop + 320px) for the founder. **Founder approval gate — APPROVED
      2026-07-23** ("That's all good"). The template is locked; safe to fan out.
- [x] 1.4 Build `/en/index.astro` + `/es/index.astro` twins (reskin of the locked NL template).
      (commit 4b9b33f)
- [x] 1.5 First **preview deploy** — alias `https://redesign.klantkraan-marketing.pages.dev`.
- **■ Checkpoint 1 — DONE 2026-07-23.** Home NL/EN/ES rebuilt + preview live. Safe to clear
  context. Next session: Phase 2 (page groups) — start with **G1 trade landings**.

### Phase 2 — Page groups (parallel draft → serial verify)
Design each page *type* once (NL), audit, commit; then replicate locale twins.

- [x] **G1 Trade landings** — DONE 2026-07-23 (commits ccf2ba3 gold ref + 332cacf twins).
      Reskinned the shared `components/dakdekkers/*` set (only `dakdekkers.astro` uses it) +
      shared primitives (Stat, RiskReversal, VerderLezen) + all self-contained pages. **NB the
      "all trade pages inherit" assumption was wrong:** only `dakdekkers.astro` composes the
      shared set; the other 6 NL pages + all 8 EN pages are self-contained 14 KB files that
      each duplicate the section markup inline. So G1 = 9 shared components + 3 primitives + 6
      self-contained NL + 8 self-contained EN = 26 files (no ES trade pages — cornerstones stay
      nl+en). All clean of kraan-. Build green, audit clean, eyeballed.
- [x] **G2 Conversion pages** — DONE 2026-07-23 (commits 055b242 + 42609b9). prijzen,
      rekentool, demo, voor-wie, over (NL + EN + ES = 15 files) + the linked
      `demo/sportscholen` (NL, folded in so the demo click-through isn't half-migrated) =
      16 files. Same deterministic transform as G1 (`scratchpad/reskin_conversion.py`),
      locked token/pattern map. `/demo` + `/demo/sportscholen` keep the live embedded
      chatbot + mobile overlay (restyled the shell only, iframe/overlay untouched).
- [x] **G3 `[stad]/[vak]` template** — DONE 2026-07-23 (commit 7f3255a). The programmatic
      city×trade template (drives the whole `/[stad]/[vak]` long tail, 10 pages today) + the
      noindex per-client `r/[slug]` KPI dashboard. Both used only tokens/patterns already in the
      locked G1/G2 rule table -> same deterministic transform, RULES copied verbatim, zero new
      rules, zero residuals. Dashboard's `<script>` innerHTML classes migrated by the same
      substring pass. 65 + 40 kraan- -> 0. Build green, astro check 0/0, eyeballed.
- [ ] **G4 Reading variant** — blog/[slug], blog/index, gidsen/[slug], gidsen/index, and the
      6 legal pages (privacy, dpa, sla, voorwaarden, subprocessors, ai-disclosure) + 404.
      Calm document layout in the dark palette, no animated hero.
- **■ Checkpoint after each group** — commit, update log, clear context between groups.

### Phase 3 — Cross-cutting audit + polish (serial)
- [ ] Run **web-design-guidelines** across the whole rebuilt site; fix findings.
- [ ] Verify: view-transition theme continuity, reduced-motion, keyboard nav, `/demo` widget,
      320px mobile, all three locales, art. 50 present everywhere, price parity, no AI-tells,
      `grep -r kraan- src` empty. Full local build green.
- **■ Checkpoint 3** — commit "audit + polish", clear context before cutover.

### Phase 4 — Cutover (fresh session)
- [ ] Founder final review on the preview alias.
- [ ] Production deploy (`--branch=production`).
- [ ] Re-verify live: curl 200s across locales, spot-check, optional squirrelscan re-audit.
- [ ] Update memory + close TODO § H.

---

## 5. Skill routing

- **frontend-design** (anthropics) — the creative pass. Used in Phase 1 (hero fidelity) and at
  the front of each Phase 2 group to *extend* the concept's language to page types it never
  designed (pricing, rekentool, legal, `[stad]/[vak]`). Brief is mostly fixed (design approved),
  so its job is faithful translation + solving the gaps + the Chanel "remove one accessory" pass.
- **web-design-guidelines** (vercel) — the audit gate. Run per page/group before commit and once
  wholesale in Phase 3. Fetches the live Web Interface Guidelines and reports `file:line` findings.

---

## 6. Context-hygiene rules

- One phase per session. Don't chain Phase 0 → 1 → 2 in a single context; clear between.
- State lives in files (this doc + TODO § H + Migration log), never only in chat.
- Eyeball = a Playwright screenshot saved to the scratchpad, not a guess.
- Parallel subagents draft; the main loop verifies + commits. Commits stay serialized.

---

## 7. Open risks / watch-list

- Font subsetting must cover NL + ES accents, or Spanish pages show tofu.
- View-transition flash on the dark theme (guard with a matching `<html>` bg + `theme-color`).
- Hero animation must bind to `astro:page-load` so it survives client-side nav.
- `/demo` iframe/embed styling — restyle the shell, don't touch the functional widget.
- 1,998 `kraan-*` references — the migration isn't done until grep is clean.

---

## 8. Migration log (append-only)

- **2026-07-23** — Plan approved. Baseline build green (~8s, `astro build`). Toolchain:
  Astro 5, Tailwind v4, pnpm monorepo, Playwright + sharp available. No code changed yet.
- **2026-07-23 — Phase 0 complete (commits 9eb015b, 91bc019).** Fonts self-hosted (18 woff2,
  564 KB on disk but only ~118 KB latin loads on first paint), palette flipped, chrome rebuilt +
  screenshot-verified, universal button/eyebrow primitives in place. Build green, `astro check`
  0 errors. **Gotchas learned:** (1) old `kraan-*` tokens kept in `@theme` so un-migrated pages
  still build — un-migrated content now shows chalk-inheriting body text (readable) + a few
  broken explicit-color elements on dark; that's expected until each page's phase. (2) Playwright
  screenshot scripts must run FROM the marketing-site dir (ESM can't resolve `playwright` from
  the scratchpad); serve the built `dist/` with `python3 -m http.server` on a spare port. (3) All
  NL/ES accents live in the `latin` subset (U+0000–00FF), so latin-ext is belt-and-suspenders.
  Next: Phase 1 — rebuild `index.astro` with the frontend-design skill, build the signature
  dispatch-log hero + ledger + receipt here, founder approval gate, then EN/ES twins + first
  preview deploy.
- **2026-07-23 — Phase 1.1 + 1.2 done (commits faf1e29, cd83615).** NL `index.astro` rebuilt on
  the foundation: live dispatch-log hero (klant → typing → reply → INGEPLAND stamp), ledger strip,
  duty cards, cost receipt, art. 50 transparency panel, final CTA. Signatures in a scoped `<style>`
  (kk-* classes, `--color-*`/`--font-*` tokens); universal chrome/buttons/eyebrow reused from
  Phase 0. Copy de-AI'd on the way in (em-dashes → punctuation). Panel is decorative (role=img +
  summary label); animation binds to `astro:page-load` (view-transition safe) and honours
  reduced-motion (verified: jumps to resting state). web-design-guidelines audit fixes: scroll-mt
  on jump-target sections, text-wrap:balance on headings, nbsp on "artikel 50", `color-scheme:dark`
  on html (global.css), touch-action+tap-highlight on `.btn` (components.css). Build green, astro
  check 0 errors, eyeballed desktop + 320px + reduced-motion. **Gotchas:** (1) Astro scopes `<style>`
  by raising specificity via a `[data-astro-cid]` attribute — a scoped `.kk-stamp{display:flex}`
  beats the UA `[hidden]{display:none}`, so I hide with `.kk-msg[hidden],.kk-stamp[hidden]{display:none}`
  (higher specificity than the base rule). (2) No-JS state = concept's (typing shown, reply/stamp
  hidden) — acceptable because the panel is decorative. (3) SendUserFile rejects a full-page 320px
  screenshot (668×12838, ~1:19 aspect) with a 400 — send a viewport-height crop instead.
- **2026-07-23 — 1.3 founder approval gate PASSED.** Founder reviewed the desktop + mobile
  screenshots and approved ("That's all good"). The home template is locked. **NEXT = 1.4:** build
  `/en/index.astro` + `/es/index.astro` twins (EN/ES home copy already exists in those files — reskin
  them to match the NL rebuild), then 1.5 first preview deploy (`pnpm build` →
  `pnpm dlx wrangler@4 pages deploy ./dist --branch=redesign --project-name=klantkraan-marketing`),
  capture the alias URL wrangler prints and record it here, send to the founder. Apex stays on the
  old design (preview alias only).
- **2026-07-23 — Phase 1.4 + 1.5 done → Checkpoint 1 (commit 4b9b33f + this).** EN + ES home twins
  built by reskinning the locked NL `index.astro`: same section structure, scoped `<style>` and the
  `astro:page-load` dispatch script carried **verbatim** (language-neutral kk-* classes + tokens);
  only copy, `<Base>` lang/title/description, and locale hrefs (`/en/demo/`, `/es/demo/`) differ.
  Section ids kept identical to NL (`nachtdienst`/`kosten`/`eerlijk`) — only the hero "how it works"
  link uses `#nachtdienst`, and nothing outside the home references the others, so translating the ids
  bought no safety and risked breakage. Invariants verified by grep + screenshot: art. 50 opens each
  dispatch panel and transparency block (`digital assistant` / `asistente digital`), no founder name,
  price parity €450 across NL/EN/ES, `article/artículo 50` with nbsp, no decorative em-dashes in copy
  (the 3 em-dashes per file are in HTML comments copied from the NL template, not rendered), no
  `kraan-*` left in either file. Build green (~1.7s), astro check 0/0. Eyeballed desktop + 320px for
  both locales via Playwright against the built `dist/` — dispatch animation resolves to the
  BOOKED/AGENDADA stamp, ES accents render (no tofu), no 320px horizontal overflow, sticky WhatsApp
  CTA present. **First preview deploy** landed the alias `https://redesign.klantkraan-marketing.pages.dev`
  (deployment `a15d0b3d`); all 3 home locales return 200 with the dispatch signature + art. 50 on the
  alias; apex `klantkraan.nl` untouched (still old design). **Gotchas:** (1) wrangler is authenticated
  on this machine via OAuth (`wrangler login`, davyvg98@gmail.com, `pages (write)`) — no CF token in
  env or `.env`; a fresh session can deploy directly. (2) The preview is intentionally **half-migrated**:
  home is redesigned, every other page is still the old light design (deprecated `kraan-*` tokens now
  render broken on the dark base, as Phase 0 warned). Tell the founder to review the **home only** on
  the alias; the rest lands in Phase 2. **NEXT = Phase 2, G1 trade landings** (redesign the shared
  `components/dakdekkers/*` set once; all trade pages inherit).
- **2026-07-23 — Phase 2 G1 complete (commits ccf2ba3 gold ref, 332cacf twins).** All trade
  landings reskinned to the dispatch-dark language. **Structural reality that bit the runbook's
  plan:** only `dakdekkers.astro` composes the shared `components/dakdekkers/*` set; the other 6
  NL trade pages + all 8 EN pages are self-contained ~14 KB files that inline-duplicate the same
  section markup. So "redesign the shared set once, all inherit" only covered 1 of 15 pages. G1
  actually = 9 shared components + 3 shared primitives (Stat/RiskReversal/VerderLezen, used by
  ~15 pages incl. all trades) + 6 self-contained NL + 8 self-contained EN = 26 files. No ES trade
  pages (cornerstones stay nl+en). **Locked token/pattern map (reuse for G2-G4):** kraan-ink->chalk,
  kraan-stone-700/500/100->dim, kraan-rust & kraan-blue->sodium, kraan-leaf->confirm, stone-300->line;
  white cards->`bg-(--color-panel)`; alt "stone-100" sections + full-blue CTA bands->recessed
  `border-y border-(--color-line) bg-[rgba(0,0,0,0.14)]`; inline blue/white button anchors->shared
  `.btn btn-primary/btn-ghost btn-lg`; section kickers->`.eyebrow`; hero illustration wrapper->
  text-sodium (reads as a warm neon sign — illustrations use currentColor, only the wrapper
  changes); with/without compare card->"with" highlighted `border-sodium/40`+confirm label, "without"
  dim label. **Method:** hand-built loodgieters + the shared set as gold references (frontend-design
  fidelity + web-design-guidelines audit — contrast AA verified: dim 7.2:1/6.8:1, confirm 9.6:1;
  Icon.astro auto-sets aria-hidden on decorative icons; global :focus-visible ring intact), then
  applied ONE deterministic Python substring transform to the other 13 self-contained pages
  (`scratchpad/reskin_trades.py`) — 5 uniform button strings + a fixed token table meant zero drift,
  faster + more consistent than 13 subagents. Verified: 0 kraan-/bg-white/text-white/inline-btn left
  in all 15 trade pages; build green (84 files, ~1.7s), astro check 0/0; eyeballed loodgieters,
  dakdekkers, schilder, sportscholen, en/dakdekkers (desktop + 320px). **Gotchas:** (1) `grep`/`cd`
  quirks — `grep` is aliased to `ugrep` which errors on an unquoted multi-file arg list; and a `cd`
  as the first token of a compound Bash command sometimes doesn't stick (cwd reverts to repo root) —
  prefer `cd X && cmd` or absolute paths, and use Python for multi-file scans. (2) Site-wide kraan-
  burn-down: ~1998 -> **1009 refs across 34 files**. Remaining is G2 (en/es/base conversion pages),
  G3 (`[stad]`, `/r`), G4 (6 legal + gidsen + blog + 404), plus deprecated `@theme` kraan tokens in
  global.css + DashboardMock/LeadForm/RingingPhone-comment (later groups). **NEXT = G2 conversion
  pages** (prijzen, rekentool, demo, voor-wie, over — NL + EN + ES; `/demo` keeps the live embedded
  chatbot, restyle its container only). Preview alias NOT redeployed this session (still shows home-
  only migration); redeploy at G2 end or when the founder wants to review trade pages.
- **2026-07-23 — Phase 2 G2 complete (commits 055b242 conversion set, 42609b9 sportschool demo).**
  All conversion pages reskinned to dispatch-dark: prijzen, rekentool, demo, voor-wie, over in
  NL/EN/ES (15 files) + `demo/sportscholen` (NL, folded in — `/demo` links to it, so leaving it
  light would break the click-through). **Method = G1's exact deterministic transform**
  (`scratchpad/reskin_conversion.py`): compound/structural rules first (buttons->`.btn`
  primitives, full-blue + stone-100 sections->recessed `border-y border-(--color-line)
  bg-[rgba(0,0,0,0.14)]`, eyebrows, signature panels, form inputs, badges), generic token
  catch-alls last (ink->chalk, stone->dim, blue/rust->sodium, stone-300->line, white->panel).
  Confirmed the 5 page types are structurally analogous to trades; twins share identical
  language-neutral class strings, so one rule table migrated all three locales at once (verified:
  82 distinct kraan class strings, each appearing in 3s/6s/9s/12s/15s across locales). **Page-type
  gaps the concept never designed, solved once each:** (1) rekentool form inputs -> dark inset
  (`bg-[rgba(0,0,0,0.25)]` + explicit `text-(--color-chalk)` — native inputs don't inherit body
  color); results aside keeps its highlight via `border-(--color-sodium)`; calculator JS untouched,
  live results verified (582 / EUR86.427 / payback <1 mnd). (2) prijzen "aanrader" badge + over "K"
  avatar -> `bg-(--color-sodium)` with `text-(--color-night)` (chalk-on-sodium ~1.3:1 fails; night-
  on-sodium passes). (3) demo art.50 disclosure card -> the home `.kk-trans` signature (panel + 1px
  line + 3px sodium left rail + mono dashed `sodium-soft` quote); live chat iframe + full-screen
  mobile overlay (functional widget) left alone, only the shell restyled. web-design-guidelines
  audit: global `:focus-visible` (sodium ring) + `color-scheme:dark` already cover the new form
  surface; one fix applied = rekentool number inputs gained `inputmode="numeric"` +
  `autocomplete="off"` (all 3 locales). `text-wrap:balance` on headings + curly quotes in body copy
  are site-wide gaps -> deferred to Phase 3's wholesale pass (do them as single global rules, not
  16-file churn). Invariants verified: art.50 disclosure intact (demo + sportschool, all locales),
  price parity EUR299/EUR499 across NL/EN/ES, no founder name, no rendered em-dashes (transform is
  class-only, copy untouched), zero kraan-/bg-white/text-white in all 16 files. Build green (84
  files), astro check 0/0, eyeballed prijzen/rekentool/demo/sport-demo desktop + prijzen 320px +
  es/prijzen (ES accents render, no tofu, no horizontal overflow). **Gotchas:** (1) RULE ORDERING
  BIT ONCE — the CTA-inner `font-display text-h1 text-white`->chalk rule is a substring of the over
  avatar's class string, so run first it turned the avatar chalk-on-sodium (contrast bug). Fix: the
  badge/avatar rules (which need night text) MUST precede any `text-white` catch-all. Lesson for
  G3/G4: order specific-with-shared-suffix rules before their generic suffix. (2) zsh does NOT
  word-split unquoted `$VAR` (bash does) — passing a built-up file list via `$TWINS` sent the whole
  string as one arg; list files explicitly or use `${=VAR}`. (3) Playwright scripts must live in the
  marketing-site dir (ESM resolves `playwright` from local node_modules, not `/tmp`); serve `dist/`
  with `python3 -m http.server`. **Site-wide kraan- burn-down: ~1009 -> 424 refs across 18 files.**
  Remaining = G3 (`[stad]/[vak]` 65, `r/[slug]` 40), G4 (6 legal ~110, blog/[slug] 24 + index 10,
  gidsen/[slug] 22 + index 9, 404 10), plus non-page components (DashboardMock 31, LeadForm 30,
  RingingPhone 2) + deprecated `@theme` kraan tokens in global.css (13) — clean those with their
  owning group / at final sweep. **NEXT = G3 `[stad]/[vak]` template** (one file drives the whole
  programmatic city×trade long tail; also `r/[slug]`). Preview alias NOT redeployed this session
  (still home-only) — redeploy at a group boundary when the founder wants to review.
- **2026-07-23 — Phase 2 G3 complete (commit 7f3255a).** The last two page types on the light
  palette migrated: `src/pages/[stad]/[vak].astro` (the programmatic city×trade template — one
  file driving the whole `/[stad]/[vak]` long tail, 10 built pages today) + `src/pages/r/[slug].astro`
  (the noindex per-client `/r/:slug` KPI dashboard). **This was the cleanest group yet:** both files
  used ONLY tokens/patterns already in the locked G1/G2 rule table (verified up front — 65 + 40
  kraan- refs, every `--color-kraan-*` token + all 6 button strings + all sections already covered),
  so I copied the `reskin_conversion.py` RULES table **verbatim** into `scratchpad/reskin_g3.py` and
  applied it — **zero new specific rules, zero residuals** (0 kraan-/bg-white/text-white/inline-btn
  in both). The `[stad]/[vak]` page decomposes exactly like a trade landing (hero + sodium city span
  -> recessed pijn-stat band -> modules w/ sodium icons -> panel ROI card -> FAQ -> internal-link
  block -> recessed final CTA), so its output matches the `loodgieters.astro` gold reference class-
  for-class. **New wrinkle handled by the generic catch-alls, no code needed:** `r/[slug]` holds
  kraan- classes both in static markup AND inside the `<script>` innerHTML template strings
  (calls/bookings/reviews/error rows) — a plain substring replace hits markup + JS alike, so all of
  them migrated in one pass (KPI values -> sodium, cards -> panel/line, review stars -> sodium/amber
  which actually reads *better* than the old rust, error alert -> sodium-bordered panel). **Design
  note on the dashboard error box:** there is no red/danger colour in the dispatch-dark palette, so
  rust->sodium (per the locked map) turns the alert into a warm amber-bordered panel; `role="alert"`
  carries the semantics, so this is fine and consistent with every other rust->sodium migration.
  Copy untouched (class-only; git shows insertions==deletions 92/92). Invariants: 0 kraan- both
  files, EUR299 parity in the city page, no founder name, no art.50 chat surface on either page
  type (so no disclosure to preserve). Build green (84 files, ~2s), astro check 0/0, eyeballed
  `/amsterdam/loodgieter/` desktop + 320px (no horizontal overflow, sticky WhatsApp CTA present) +
  `/r/example` (dark KPI shell + offline error state render correctly). **web-design-guidelines:**
  not re-run for G3 — both page types are deterministic reskins of primitives already audited in
  G1 (`[stad]/[vak]` == trade-landing structure) / reused card+list patterns; the wholesale audit
  is Phase 3's job (§4). **Site-wide kraan- burn-down: measured 269 raw `kraan-` matches across 17
  files** (down from ~424). **3 of those are false positives** — `Klantkraan-abonnement`/
  `Klantkraan-klant` brand copy (`rekentool.astro:16`, `blog/cv-storing-januari-installateur.md`
  x2) where the word "Klantkraan" is followed by a hyphen; those are NOT tokens, leave them. So
  **266 real `--color-kraan-*` token refs remain**, all in G4 + non-page components:
  G4 pages = legal voorwaarden 25 / dpa 25 / sla 20 / privacy 17 / ai-disclosure 17 / subprocessors
  10 (=114) + blog/[slug] 24 + blog/index 10 + gidsen/[slug] 22 + gidsen/index 9 + 404 10 (≈189);
  non-page components = DashboardMock 32 + LeadForm 30 + RingingPhone 2 (=64); deprecated `@theme`
  kraan tokens in global.css = 13. **Final-sweep plan:** do G4, then migrate the 3 non-page
  components + delete the 13 `@theme` tokens so `grep -r -- '--color-kraan' src` is empty (the 3
  brand-copy hits stay — filter them by grepping `--color-kraan` not bare `kraan-`). **NEXT = G4
  reading variant** (calm document
  layout, no animated hero — blog/gidsen indexes + [slug] pages + 6 legal pages + 404). Preview
  alias NOT redeployed this session (still home-only) — redeploy at a group boundary when the
  founder wants to review the fuller migration.
