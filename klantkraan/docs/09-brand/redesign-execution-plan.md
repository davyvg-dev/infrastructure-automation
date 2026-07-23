# Site-wide redesign — execution plan ("Het licht blijft aan")

**Status:** planning approved 2026-07-23. Not yet started building.
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
- [ ] 1.3 Screenshot (desktop + 320px) for the founder. **Founder approval gate** — this is
      the template; do not fan out until approved. **← PAUSED HERE. Screenshots produced +
      shown to the founder; awaiting the go before 1.4/1.5.**
- [ ] 1.4 Build `/en/index.astro` + `/es/index.astro` twins (copy already exists).
- [ ] 1.5 First **preview deploy**; record alias URL in the log; send to founder.
- **■ Checkpoint 1** — commit "home NL/EN/ES + preview live", clear context.

### Phase 2 — Page groups (parallel draft → serial verify)
Design each page *type* once (NL), audit, commit; then replicate locale twins.

- [ ] **G1 Trade landings** — redesign the shared `components/dakdekkers/*` set once (Hero,
      Features, Faq, PainStats, SocialProof, FinalCta, StormScenario, RoiSnippet, CityLinks);
      all trade pages inherit. Pages: dakdekkers, loodgieters, elektricien, installateur,
      schilder, aannemer, sportscholen, en/air-conditioning (+ EN twins).
- [ ] **G2 Conversion pages** — prijzen, rekentool, demo, voor-wie, over (+ EN/ES twins).
      `/demo` keeps the live embedded chatbot; restyle its container only.
- [ ] **G3 `[stad]/[vak]` template** — one file, the whole programmatic long tail.
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
  hidden) — acceptable because the panel is decorative. **PAUSED at 1.3 (founder approval gate).**
  Next session (after founder go): 1.4 EN/ES twins from `/en/index.astro` + `/es/index.astro` copy,
  1.5 first preview deploy → `redesign` alias, record the alias URL here.
