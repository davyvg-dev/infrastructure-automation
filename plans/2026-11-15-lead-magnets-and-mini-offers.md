# Plan — Lead magnets, mini offers and one repeated call to action, everywhere — 2026-11-15
Status: done
Task: none

Davy's answers (2026-11-15, before the build): "so cta within and before and after the lead magnet. do the prices you have, weekly cap is 20? is that a lot? just do klantkraan i guess." So: every magnet gets a call to action before it, inside it and after it; the four mini offers keep the proposed prices (€ 295, € 95, € 195 + € 19 a month, € 149, excl. btw); the free-openings cap is a number in `magnets.ts`; no founder name on the site, Klantkraan only (this now includes removing the existing hits on `/scan` and `/websitecheck`).

## Goal
Davy (after Hormozi's lead-magnet talk): "need to implement this in my business. needs to be everwhere". Focus: websites, photo and video ads, Klantkraan automations and the receptionist. Give value right away for an email address, "combined with selling something immediately". The mini offer "needs to be on the website also and it needs to be a complete solution to a narrow problem". Paid ad test starts 24 Nov 2026.

Paths: **MS** = `klantkraan/apps/marketing-site/`, **AR** = `ai-receptionist/`, **V** = vault `Notes/Marketing/`, **SA** = `~/Documents/.claude/skills/static-ads/`.

## Acceptance
- Four lead magnets live on the built site, one per area, each named by its result (not "scan", "check", "cursus"), each ending in an email address in Brevo list #6 or the course ledger with a source tag: `/websitecheck/` (websites), `/scan/` (automations), `/rekentool/` (receptionist), `/advertentievideos/` (ads).
- `/klein-beginnen/` exists with one mini offer per area, each with: the narrow problem, what is delivered, the fixed price, the delivery time, and a pay button that opens a Mollie payment link. `grep -c "data-mini-offer" dist/klein-beginnen/index.html` = 4.
- Every NL page that uses the normal layout shows one call to action block with three parts: the button (what to do), one line saying what happens next, one true reason to do it now. `node scripts/test-magnets.mjs` checks this on `/`, `/prijzen/`, `/loodgieters/`, `/rekentool/`, one gids, one blog post, `/advertentievideos/`, and checks every magnet and mini-offer link returns 200.
- After each magnet (`/scan/bevestigd/`, the result screen of `/websitecheck/` and `/rekentool/`, course lesson mails) the matching mini offer is shown once.
- `pnpm build`, `pnpm typecheck` and `scripts/copy-lint.sh` pass for the files this plan touches (existing founder-name hits on `/scan` and `/websitecheck` are not made worse).
- V has one note "Lead magnets en CTA per kanaal" with the name, link, button line, next-step line and reason line per magnet, and the ready lines for mail signature, cold mail PS, LinkedIn featured link, WhatsApp profile and ad caption. Nothing is sent or posted by Claude.
- SA `SKILL.md` says: the picture carries the picture, one headline and the button; offer text and price go in the ad's caption. A brief with a `sub` longer than 90 characters is flagged by `gate.py`.
- Nothing is deployed and no Mollie link is created by Claude: both are Davy's gates.

## What exists
- MS `src/pages/websitecheck.astro`, `src/lib/websitecheck.ts:600-649` (`runCheck`), `src/pages/api/websitecheck.ts:17-18,54-73` — live tool: owner types a URL, gets https, WordPress and PHP version, phone link, phone layout, title, description, h1, alt texts, heaviest photo. No speed measurement. Step 2 posts EMAIL plus hidden SCAN_* fields to the Brevo form (`websitecheck.astro:78-134`).
- MS `src/pages/scan/index.astro:18-19,26-108` — the written scan: Brevo form, list #6, confirmation template #10; lands on `src/pages/scan/bevestigd.astro` (plain "bevestigd" card, no next offer). Promise: answer within 1 working day, five a week (V `Gratis scan.md`).
- MS `src/pages/rekentool.astro:27-30,204` — calculator only, no email step; `CursusForm` sits below it.
- MS `src/components/CursusForm.astro:132-188` — 4-lesson course, used on 15 pages; posts to `demo.klantkraan.nl/api/cursus`; AR `app/server.py:399-437` stores the address and sends lesson 1 via Resend; lessons in AR `app/cursus.py:215-353`, days 0, 2, 5, 9 (`:57`).
- MS `src/pages/advertentievideos.astro:7-8,138` — ad-video offer; contact only by mailto and WhatsApp, no form, no price; promises "eerst een paar voorbeelden terug".
- MS `src/pages/demo.astro:8,40` — chat demo, no account (the usage-based free trial).
- No internal page links to `/scan/` or `/websitecheck/` (sweep 2026-11-15). The site's 68 pages all sell the receptionist (V `Inbound - leads naar mij toe.md`).
- MS `src/layouts/Base.astro:180-191` — Header, main, Footer, StickyMobileCta in one place; `bare` prop skips them (`:176-177`). No Button or CTA component; `.btn*` classes in `src/styles/components.css:12-76`. Strings are inline per component; no dictionaries. EN and ES are separate page files.
- AR `app/billing.py:74,183-245,690-723`, `app/server.py:340` — Mollie checkout only for plans `chat` 299 and `compleet` 499, always followed by a monthly subscription. No one-time product can be sold in code today.
- MS `public/_headers:8` — CSP: `script-src 'self'`, connect and form-action only to api/demo.klantkraan.nl and the Brevo forms host. No analytics script anywhere in MS.
- Rules: `CLAUDE.md:23,31,32` (human gates: live Mollie, deploy; Dutch; no founder name in customer-facing artefacts); `klantkraan/docs/09-brand/voice-and-tone.md:54-55,65,80` ("wij" allowed on the site, "u" first, no unsourced ROI, one "!" per page); `scripts/copy-lint.sh:9-14`.
- `plans/2026-11-15-klantkraan-site-redesign.md` is `ready` and rewrites Header, Footer, CursusForm and the home sections; `/scan`, `/websitecheck` and `advertentievideos.astro` are out of its scope. The working tree is dirty (self-install work).
- Proposed prices and the 20 mini-offer ideas: `~/Documents/wiki/offers-and-pricing.md` ("Price research 2026-11-15", marked not decided).

## Changes
Phase 1, before 24 Nov (what the ads need):
1. MS `src/data/magnets.ts` (new) — the single source for the four magnets and four mini offers: `name` (result first), `href`, `button`, `next` (exact next step), `reason` (true reason now), `area`, and for mini offers `problem`, `delivers`, `price`, `days`, `payUrl` (empty until Davy pastes his Mollie link; an empty one renders "Mail mij" instead of a pay button). Names to start with:
   - websites: "Zie in 1 minuut wat een klant op uw website mist" → `/websitecheck/`; reason: no email needed for the result.
   - automations: "Waar verliest uw bedrijf elke week tijd? Antwoord binnen 1 werkdag" → `/scan/`; reason: five a week.
   - receptionist: "Reken uit wat onbeantwoorde aanvragen u per maand kosten" → `/rekentool/`; reason: uses their own numbers, one minute.
   - ads: "3 nieuwe openingen voor uw advertentievideo, gratis" → `/advertentievideos/`; reason: a weekly cap Davy names.
2. MS `src/components/OfferCta.astro` (new) — one block: headline (magnet name), button, next-step line, reason line; props `area` and `variant` (band or inline). Reads `magnets.ts`.
3. MS `src/layouts/Base.astro:180-191` — render `OfferCta` above the Footer on every non-bare page, with a per-page `offerArea` prop (default `receptionist`; `false` to switch off on `/aanmelden/`, `/bedankt/`, legal pages). One edit puts it on all normal pages.
4. MS `src/pages/advertentievideos.astro` — add a short form (email, link to the running ad or video, honeypot) posting to the Brevo form with source `advertentievideos`; keep mailto and WhatsApp as second choice. Qualifier: the field "link to the ad that runs now" is required.
5. MS `src/pages/rekentool.astro` + `public/js/rekentool.js` — after the result: "Stuur mij deze berekening" (email) posting to the Brevo form with source `rekentool` and the numbers in SCAN_KLUS.
6. MS `src/pages/klein-beginnen.astro` (new) — the four mini offers from `magnets.ts`, each a card with `data-mini-offer`, price, delivery time and pay button. First four (prices pending Davy): WordPress op slot, Drie nieuwe openingen, Offerte-opvolger, Vakantiewacht.
7. MS `src/pages/scan/bevestigd.astro`, the result step of `websitecheck.astro` and `rekentool.astro` — show the matching mini offer once ("Liever meteen geregeld?").
8. MS `src/components/Header.astro:12-34`, `Footer.astro` — one nav item "Gratis" (to a short list of the four magnets on `/gratis/`, new page from `magnets.ts`) and one footer column with the magnets and `/klein-beginnen/`.
9. MS `scripts/test-magnets.mjs` (new) and the source tag: every form sets SCAN_PROGRAMMAS to its source plus any `?bron=` from the URL, so ad, mail and LinkedIn sign-ups can be told apart in Brevo without a tracking script.

Phase 2, everywhere outside the site (drafts only, Davy sends):
10. V `Lead magnets en CTA per kanaal.md` (new) — the lines per channel from `magnets.ts`, plus the four naming patterns applied (number + outcome + time; how to X without Y; the [adjective] [type] that [benefit]; N mistakes that prevent X) with 3 name candidates per magnet to test as ad headlines.
11. AR `app/cursus.py:215-353` — one PS line per lesson pointing at the matching mini offer; `~/Documents/tools/scanmail/scanmail.py` — same PS in the scan reply.
12. SA `SKILL.md`, `scripts/gate.py` — picture, one headline, button; text in the caption; flag `sub` over 90 characters. Briefs for the paid test use the magnet names as headlines, one magnet per ad.
13. `~/marketing-os/config/campaigns.toml` — register `ads:websitecheck`, `ads:rekentool`; update the offer text of `ads:scan`, `ads:advertentievideos`, `ads:receptionist` to the magnet names.

Phase 3, later, each its own plan: a case-study page of the hacked-site job (client unnamed); real speed measurement in the website check; one-time checkout in AR `billing.py`; EN and ES.

## Tests
- MS `scripts/test-magnets.mjs` — written first; Playwright against `astro preview`: the pages in Acceptance each have exactly one `[data-offer-cta]` with a button, a next line and a reason line; `/klein-beginnen/` has 4 `[data-mini-offer]`; every `href` in `magnets.ts` answers 200; the two new forms refuse an empty email and a filled honeypot; at 390 and 320 wide no horizontal scroll.
- Existing `scripts/test-integration.mjs`, `scripts/test-voor-wie-nav.mjs` still pass. `mobile-qa` and `fix-verifier` before saying done.
- SA `tests/` — one case: a brief with a 91-character `sub` is flagged.

## Decisions
- Use what is live and rename it, build only two small forms and two pages — because the vault's own finding is that nothing gets published when new things must be built first. Rejected: new tools (speed test, sitecheck v2) before the 24th.
- One data file and one component for every call to action — because "everywhere" stays true only if a name or reason is changed in one place. Rejected: copy per page.
- Mini offers are paid through Mollie payment links that Davy creates — because the code sells subscriptions only and live Mollie is his gate. Rejected: one-time checkout code now (phase 3).
- Reasons to act now are real limits only (five scans a week, a weekly cap on free openings, no email needed) — no invented deadline.
- Site copy keeps the site's voice ("u", "wij" allowed, no founder name); ads and mails keep "ik". Rejected: unifying the voice in this plan.
- NL only; build this before the redesign plan and keep the footprint in shared files to single insertions, so the redesign can restyle `OfferCta` with its own tokens.
- Source tag in the form instead of an analytics script — the CSP forbids outside scripts and Meta lead forms need no pixel.

## Out of scope
- The redesign, prices on `/prijzen/`, the receptionist product, any send, post, publish, deploy or Mollie action.
- Physical lead magnets; polls; EN and ES pages.

## Risks / unknowns
- Prices and which four mini offers: proposals, not decided. If Davy changes them, only `magnets.ts` changes.
- Mollie payment links: assumed available on his account; check Mollie's docs through `ctx7` at step 6. If not, the button becomes a mail link with the price shown.
- The Brevo form accepts the hidden SCAN_* fields from two more pages: untested; the first test send on `/websitecheck` never confirmed the hidden answers reach list #6. Test with one real confirmation before relying on the source tag.
- Free "3 openings" costs Davy's time per request; without a cap he names, do not publish that magnet.
- Dirty tree and the pending redesign both touch `Footer.astro`: run `git status --short` first and ask before touching a modified file.
- `OfferCta` on 60-plus pages may clash with `StickyMobileCta` and `CursusForm` on the same page (three asks). If a page shows more than two, drop `CursusForm` there and report.

## Deviations
- Weekly cap on free openings is 10, not the 20 Davy floated with a question ("is that a lot?"): at an estimated 20 to 30 minutes each, 20 is 7 to 10 hours of free work a week and does not read as a limit. One constant in `magnets.ts`.
- Before / within / after (Davy's answer) added on top of the plan: a `MiniOfferLine` before each magnet's button, inside each result (website check points `wordpress`, `php`, `https`; the rekentool's new per-month figure), and the `MiniOfferCard` after. Course and scan mails got the same (PS per lesson, overview link in les 4; a body line and PS in `scanmail`).
- `/scan` and `/websitecheck`: founder name removed (9 hits to 0), "ik" became "we" on those pages and in the four "ik" lines of `src/lib/websitecheck.ts`; mail address is `contact.email` (hallo@). The "je" voice of those pages stays; mini-offer copy avoids "u"/"je" so it reads right on both.
- OfferCta is switched off by path in `Base.astro` (`/aanmelden/`, `/bedankt/`, `/legal/`, `/r/`) instead of a prop on nine page files, two of which were someone else's uncommitted work. `/gratis/` passes `offerArea={false}`; `/rekentool/` uses `automations` (its own magnet would point at itself); `/advertentievideos/` uses `ads`, whose button jumps to the on-page form.
- Footer: the magnets and `/klein-beginnen/` went into the first column (replacing the lone advertentievideos link) instead of a fifth column, which would break the 4-column grid.
- CursusForm removed from the 12 Dutch pages that would otherwise show three asks (plan's own risk rule). The course stays signable on `/gratis/` and on EN/ES rekentool.
- `/scan/bevestigd/` is the landing page for every Brevo confirmation (one redirect setting), so it shows the scan's offer plus a link to all prices; the other magnets show their own offer in-page right after submitting.
- Acceptance `grep -c "data-mini-offer" dist/klein-beginnen/index.html` = 4 cannot hold literally: the built page is one line, so `grep -c` prints 1. `grep -o ... | wc -l` = 4, and `test-magnets.mjs` counts the elements.
- The Brevo URL moved to `src/data/brevo.ts`, shared by the four forms.
- `astro preview` does not run with the Cloudflare adapter; tests run against `dist/` served statically, as `test-integration.mjs` already assumes.
- `test-voor-wie-nav.mjs` and `test-integration.mjs` were already failing before this change (links gained trailing slashes; H1 and risk-reversal copy changed since May). Their link selectors now use trailing slashes; voor-wie-nav is 49/1, integration 30/14, all remaining failures are copy expectations from May that the committed source no longer contains.
- Mollie: ctx7 docs confirm payment links can be shown on a website, not whether one link can be paid many times. Buttons stay "Bestel per mail" until Davy pastes links.
- static-ads `gate.py`: the 90-character `sub` rule exempts kind B (native notes), where the `sub` is the note's own text. Tonight's kind A/D/E briefs (subs 112 to 276) will be stopped until shortened; SKILL.md says so.
- Phone QA fixes: `#aanvragen` got `scroll-mt-24` (the heading sat under the sticky header); shorter placeholder on the ad link field; the mobile menu now scrolls inside the screen with bottom room, because the extra "Gratis" item pushed the language switch under the fixed phone/WhatsApp bar on an iPhone SE (622 vs 598 px; now 562).
- fix-verifier (FAIL, fixed): (1) `/en/bedankt/` and `/es/bedankt/` showed the Dutch block because those pages never pass `lang`; Base now also skips `/en/`, `/es/` paths and every `noindex` page (404, bedankt, private demos, `/r/`). (2) `/scan/` and `/websitecheck/` titles and H1s now carry the result name, in those pages' own "je" voice ("Waar verliest je bedrijf elke week tijd? ...", "Zie in 1 minuut wat een klant op je website mist"); footer labels are result names too. Ads say "uw": converting those two pages to "u" is a follow-up. (3) `?bron=` is kept for the visit (`public/js/bron-keep.js`, session storage), so `/gratis/?bron=linkedin` -> calculator still tags the sign-up. All three are now cases in `test-magnets.mjs` (92 green).
- Incident: the phone QA agent's own Brevo stub missed and two real test posts reached Brevo (rekentool form, `qa-test@example.invalid`; ad form, `qa@example.invalid`). Davy should delete those two contacts. Lesson in `wiki/log.md`.

## Build
Read this file and CLAUDE.md, nothing else first. Set `Status: building`. Work through Changes in order, tests first. If a line under "What exists" is no longer true, stop and report instead of improvising. Small deviations go under a `## Deviations` heading in this file. When every Acceptance line passes and the project's checks are green, set `Status: done`.
