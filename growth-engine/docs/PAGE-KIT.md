# Page kit — IG / TikTok / FB profile setup (fitness vertical)

Generate the assets once:

    GROWTH_CONFIG=config/fitness.yaml python -m src.pagekit

Output in `data/fitness/pagekit/`: `avatar.png` (profile picture, all platforms — check
`avatar-preview.png` first: it must read at 40px), `fb-cover.png`, `highlight-*.png`
(4 IG highlight covers), `pinned-post.png` (4:5 intro card), `reel-cover.png` (demo of
the reel-cover template).

## Handle — OPEN FOUNDER DECISION

Pick ONE, use it identically on all three platforms (check availability everywhere
before committing; nothing in config or copy assumes any of these yet):

1. `klantkraan` — company-level; reusable when more verticals get pages.
2. `klantkraan.sport` (IG/TikTok) / `KlantkraanSport` (FB) — vertical-flavored, still the company.
3. `deledenassistent` — product-led, matches how the content talks about the product.

Until chosen: display name "Klantkraan", URL `klantkraan.nl/sportscholen` everywhere.

## Instagram

- [ ] Create the account, then switch to a **Creator** account (Instellingen > Account >
  Overstappen naar professioneel account > Creator). Not Business: business accounts get
  the limited royalty-free Sound Collection; Creator keeps insights AND the full music
  library — music choice is a reach lever for reels.
- [ ] Category: "Product/dienst" (shown under the name; can be hidden).
- [ ] Profile picture: `avatar.png`.
- [ ] Bio (118/150 chars, paste as 4 lines):

      AI-ledenassistent voor sportscholen
      Elk bericht direct beantwoord — 24/7
      Proefles meteen in de agenda
      Demo via de link

- [ ] Link: `https://klantkraan.nl/sportscholen`
- [ ] Pinned post: post `pinned-post.png` with the caption below, then ⋯ > "Vastzetten
  op profiel".

      Dit is de AI-ledenassistent voor sportclubs. Elk bericht direct
      beantwoord — ook om 23:00. Elke proefles meteen in de agenda.

      We bouwen hem in het openbaar: echte gesprekken, echte boekingen.
      Volg mee.

      Link in bio: klantkraan.nl/sportscholen

      #sportschool #fitnessondernemer #sportschooleigenaar

- [ ] Highlights (need a story first): post each `highlight-*.png` as a story, add it to
  a new highlight, set the image itself as the cover ("Omslag bewerken"), and name them
  exactly: **Demo**, **Resultaten**, **Uitleg**, **Over ons**. Fill them over time with
  reels/stories per theme; empty highlights are fine at launch.

## TikTok

- [ ] Stay on a **personal account** and set it to creator-style use — do NOT switch to
  a Business account for a cold start. Tradeoff: Business unlocks a website link at 0
  followers but loses the trending-sound library (Commercial Music only), and trending
  audio is TikTok's biggest organic lever under 10k followers. Revisit once the account
  has traction.
- [ ] Profile picture: `avatar.png`.
- [ ] Bio (73/80 chars):

      AI-ledenassistent voor sportscholen — 24/7 antwoord. Demo: zie Instagram.

- [ ] Link: personal accounts need 1.000 followers for a website link. Workaround until
  then: the bio points to Instagram (link allowed at 0 followers there), and every video
  shows `klantkraan.nl/sportscholen` on screen.
- [ ] Warm-up before the first post (docs/REELS.md §2): 7–14 days of following Dutch
  fitness/business accounts and watching niche videos to completion.

## Facebook

- [ ] Create a **Page** (not a profile — profiles can't run CTA buttons, insights, or
  later ads). Name: "Klantkraan", category "Softwarebedrijf" or "Bedrijfsdienst".
- [ ] Profile picture: `avatar.png`. Cover: `fb-cover.png` (critical content sits in the
  centered mobile-safe area; upload as-is, don't reposition).
- [ ] Description (paste):

      Klantkraan bouwt de AI-ledenassistent voor sportclubs: elk bericht van
      leden en leads direct beantwoord, 24/7, en de proefles meteen in de
      agenda. Volg hier echte demo's en resultaten. Meer weten?
      klantkraan.nl/sportscholen

- [ ] CTA button: "WhatsApp versturen" (matches the site's WhatsApp-first capture) —
  fallback "Meer informatie" → `https://klantkraan.nl/sportscholen`.
- [ ] First post: `pinned-post.png` with the Instagram caption above (drop the
  hashtags), then pin it to the top of the Page.
