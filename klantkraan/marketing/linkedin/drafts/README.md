# LinkedIn personal-profile post drafts

Dutch drafts for the Klantkraan founder to publish manually from the
founder's personal LinkedIn profile. No auto-posting — copy-paste only.

## Files

| File | Week | Topic | Status |
|---|---|---|---|
| `001-launch-story.md` | 1 | Intro: "Vandaag launch ik Klantkraan" — wat ik bouw en waarom | draft |
| `002-stat-hook.md` | 1 | Probleem-statement: loodgieters missen 28% van inkomende calls | draft |
| `003-contrarian-take.md` | 1 | Listicle/carousel: 5 redenen dat installateurs offertes verliezen | draft |
| `004-customer-pain.md` | 2 | Teardown: hoe een loodgieter 12 calls/week beantwoordt zonder receptionist | draft |
| `005-call-transcript.md` | 2 | Demo-transcript: wat een AI-call écht klinkt (90s gesprek) | draft |
| `006-no-aaa-agency.md` | 2 | Contrarian: waarom je geen AAA-agency moet inhuren | draft |
| `007-poll-missed-calls.md` | 2 | Native LI-poll: welk % van calls mis je echt? | draft |
| `008-case-study-1.md` | 3 | Case study #1 reveal (loodgieter-pilot, geanonimiseerd) | **holdback** |
| `009-lessons-pilot-1.md` | 3 | 3 lessons learned uit pilot #1 — wat fout ging | **holdback** |
| `010-ten-questions-ai.md` | 3 | Listicle: 10 vragen die je AI-receptionist moet beantwoorden | draft |
| `011-myth-ai-replace.md` | 3 | Hot take: AI vervangt geen vakmensen, wel receptionisten | draft |
| `012-may-pilots-dm.md` | 3 | Soft CTA: 3 loodgieter-pilot-plekken open voor mei | draft |
| `013-emergency-call-voiceover.md` | 4 | Voice-over clip: spoed-call afgehandeld door AI (22:47) | **holdback** |
| `014-dashboard-before-after.md` | 4 | Dashboard screenshot: before/after pilot #1, 30 dagen data | **holdback** |
| `015-dakdekker-pilot.md` | 4 | Case study #2: dakdekker-pilot — andere flow dan loodgieter | **holdback** |
| `016-month-1-lessons.md` | 4 | Build-in-public: 5 lessons learned uit maand 1 | **holdback** |
| `017-dakdekkers-pilot-cta.md` | 4 | Soft CTA: 2 dakdekker-pilot-plekken open voor juni | draft |

Topics follow `klantkraan/docs/05-content/first-30-days-calendar.md`
(LinkedIn posts 1–17, weeks 1–4). The filename suffixes track the actual
post content/topic, not the original template names.

**Status legend:**
- `draft` — ship-ready, founder reviews + publishes
- `holdback` — skeleton with `[PLACEHOLDER]` slots; do not publish until
  the pilot data referenced in the frontmatter `holdback_reason` exists.
  Faking pilot numbers on LinkedIn = brand suicide. Always wait.

## Each draft file contains

1. **Frontmatter** — post number, publish week, post type, status,
   manually counted character count of the post body (incl. hashtags,
   excl. the first-comment block).
2. **Voice notes for the founder** — hook test, cadence checks, what to
   personalise before publishing.
3. **Post body** — the exact Dutch text to copy-paste into LinkedIn.
   Each is ≤1300 characters so the full post renders without "see more"
   getting in the way of the CTA.
4. **First comment** — the link / extra CTA to drop as the first reply
   to your own post. LinkedIn suppresses reach on posts that contain
   external links in the body, so the link always lives in comment #1.

## Publish cadence

- Full 30-day batch covered (17 posts, weeks 1–4).
- Cadence target per `docs/05-content/first-30-days-calendar.md`:
  3 posts/week in week 1, 5/week in weeks 2–4.
- Best Dutch B2B publish windows: Tuesday or Thursday, 07:30–09:00
  or 17:00–18:30. Owner-operators check LinkedIn on commute or post-work.
- Holdback posts (008, 009, 013, 014, 015, 016) ship only after the
  pilot data referenced in their `holdback_reason` frontmatter exists.
  If pilot timing slips, push these posts later in the calendar — do
  not backfill with fake numbers.

## Style rules (enforced — see `docs/09-brand/voice-and-tone.md`)

- Dutch only in the post body (these go to a Dutch audience).
- First-person "ik" — founder posts under own name.
- No emojis. No "revolutionair / AI-gedreven / next-gen / disruptief".
- One concrete number per post (28%, €450, 12 calls, 60% loss).
- One CTA at the end — a question, a DM ask, or a tag-someone ask.
- 2–3 lowercase hashtags at the bottom: `#loodgieter #dakdekker #ondernemen`.
- ≤1300 characters in the post body.
- Link in first comment, never in the post body (LinkedIn reach penalty).

## Pre-publish checklist (founder)

- [ ] Read the post out loud — does the first line earn the click on "see more"?
- [ ] Personalise any "een loodgieter in Utrecht…" placeholder to a real moment from this week if possible.
- [ ] Verify the character count in frontmatter matches reality if you edited.
- [ ] Confirm the first-comment text is ready to paste immediately after publishing.
- [ ] Check no banned words slipped in (`revolutionair`, `next-gen`, "Powered by GPT", etc.).
- [ ] Tag the company page `@Klantkraan` once it exists (Week 2+).

## Not in this folder

- Carousel image files (Canva): live in `klantkraan/marketing/canva/`
  once produced. Post 003 will pair with an 8-slide carousel.
- Company-page reposts: handled in `klantkraan/marketing/linkedin/company/`
  (folder TBD).
- DMs / outbound sequences: see `klantkraan/docs/02-sales/`.
