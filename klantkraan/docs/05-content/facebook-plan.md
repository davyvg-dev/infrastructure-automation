# Facebook — plan, copy bank & assets

Getting Klantkraan moving on Facebook. Audience is the **buyer**: owners of Dutch trade
businesses (loodgieters, dakdekkers, elektriciens, installateurs, schilders) — vakmensen,
not tech people. Everything below matches the repo rules: **no auto-posting, no automated
replies/comments/DMs** on any platform. Drafting original posts is the automation ceiling.

---

## 1. The verdict on paid ads: not yet

Short answer to "is paid ads a good idea to get traffic flowing?" — **hold off for now, go
organic first.** Reasons:

- **Pre-validation.** The site does ~2 visits/day and no demo has converted to a paying
  client yet. Paid traffic to an unproven funnel just buys expensive proof that the funnel
  isn't ready. Fix conversion with warm traffic first, then pour paid on top.
- **Meta is weak for micro-niche B2B.** "Owner of a 1–5 person Dutch plumbing/roofing firm"
  is a tiny, hard-to-target audience on Facebook. You'll pay to show ads to lots of
  non-buyers. LinkedIn + groups + direct outreach reach this buyer far more precisely.
- **You already have a warmer lever:** the 45-prospect Randstad list (docs/02-sales/prospects)
  and the LinkedIn cadence. Prove the demo closes there first.

**When to switch paid ON** (trigger, not a date): once **≥1 paying client + a testimonial**
exist and the demo page converts warm visitors. Then run a small test — see §5.

**Do now, cheap:** stand up the Facebook Page + install the **Meta Pixel** on klantkraan.nl
so retargeting data accrues from day one. Retargeting site visitors will be the highest-ROI
paid play later, and it needs weeks of pixel data before it's useful. (I can wire the Pixel
into the Astro site the moment there's a Pixel ID.)

---

## 2. Where to post

**A. A Klantkraan Facebook Page** — the brand home + the thing Meta requires before you can
ever run an ad. Founder creates it (I can't create accounts). Set: name *Klantkraan*, category
*Software / Local service*, profile = the blue "k" mark, cover = the benefit image below,
"Send WhatsApp" button → the business number, website → klantkraan.nl.

**B. Groups — post from the founder's *personal* profile, not the Page.** Groups distrust
brand accounts and many block Page posting. Find them by searching Facebook for:

- `ZZP <regio>`, `Ondernemers <stad/regio>`, `MKB <regio>` (Randstad first — matches the
  prospect list)
- `Loodgieters` / `Installateurs` / `Dakdekkers` / `Elektriciens` / `Klusbedrijven Nederland`
- `Bouw ZZP`, `Vakmensen`, regional `<stad> ondernemers` / bedrijvennetwerk groups

Vet each before posting: is it active (posts this week), does it allow any self-promo, and does
it contain *owners* (not just consumers looking for a klusser)? Join 5–8 good ones. **Read the
rules; most ban overt ads.** So in groups you lead with value (§3A), never a sales pitch. A
"promo/zaterdag" thread, if the group has one, is the one place a direct post is welcome.

**C. Marktplaats-style / local buy-sell groups** are consumer-side — skip them, wrong audience.

---

## 3. What to post — copy bank (Dutch)

Voice = direct, concrete, a little opinionated, short sentences, no hype, no emoji spam.

### 3A. Group-safe (value-first, soft or no CTA) — for dropping into ZZP/vakman groups

**Post 1 — the missed-call problem (no link, pure value):**
> Iets wat ik veel zie bij eenmanszaken in de bouw en installatie:
> de meeste gemiste omzet zit niet in te weinig klanten, maar in klanten die bellen terwijl je
> op een dak of onder een gootsteen zit. Ze spreken geen voicemail in — ze bellen de volgende
> in Google.
>
> Drie dingen die helpen, zonder dure software:
> 1. Automatische WhatsApp-reactie op je zakelijke nummer: "Ik zit op een klus — app je vraag +
>    postcode, ik reageer vanavond."
> 2. Laat je voicemail een concrete belofte doen ("ik bel voor 18:00 terug"), geen standaardtekst.
> 3. Blok elke dag een vast kwartier om terug te bellen.
>
> Wat werkt bij jullie tegen gemiste telefoontjes?

**Post 2 — pilot recruit (soft, only in groups that allow it):**
> Ik bouw een digitale receptionist speciaal voor vakbedrijven — een assistent die via de chat
> op je site en via WhatsApp opneemt als jij niet kan, de vraag uitvraagt (inclusief adres en
> postcode) en de afspraak meteen in je agenda zet.
>
> Ik zoek een paar loodgieters/installateurs in de Randstad die 'm gratis willen testen op hun
> eigen diensten en eerlijk zeggen of het klopt. Interesse? Laat een reactie of stuur een DM.

### 3B. Direct (Page posts + ad copy) — these may sell

**Ad 1 — problem → solution:**
> Hoeveel klussen loop je mis omdat je de telefoon niet kon opnemen?
>
> Klantkraan is een digitale receptionist voor vakmensen. Hij neemt 24/7 op via de chat op je
> site én via WhatsApp, beantwoordt vragen over je diensten en werkgebied, en zet de afspraak
> meteen in je agenda — met adres en al.
>
> Geen gemiste oproep is nog een gemiste klus.
> Probeer de live demo → klantkraan.nl

**Ad 2 — benefit-led:**
> Je beste monteur kan niet én op het dak staan én de telefoon opnemen.
>
> Klantkraan doet dat tweede: 24/7 antwoord op elke klant, afspraken direct ingepland, elke
> lead meteen op je telefoon. Voor loodgieters, dakdekkers, elektriciens en installateurs.
>
> Bekijk de live demo op klantkraan.nl

**Ad 3 — one-liner (image caption / short ad):**
> Elke gemiste oproep is een klus voor de concurrent. Klantkraan neemt op — 24/7, ook via
> WhatsApp. klantkraan.nl

### 3C. Captions for the two images (§4)

- **Problem image:** use Ad 1 or Ad 3.
- **Benefit image:** use Ad 2.

---

## 4. Images

Two on-brand square (1080×1080) posts in `facebook/assets/`, built from the brand palette
(kraan-blue #0F4C81, cream #FAF6EE, rust #C75A2B), flat/no-gradient per the logo brief:

- `fb-post-problem.png` — cream, "Elke gemiste oproep is een klus voor de concurrent."
- `fb-post-benefit.png` — blue, "Nooit meer een klus mislopen door een gemiste oproep."

Source SVGs + `build_images.py` (regenerate: `python3 build_images.py`, needs macOS
`qlmanage` + Pillow) sit alongside. To change wording, edit the SVG text or the builder.
These use Helvetica Neue as an Inter Tight stand-in; swap to Inter Tight once the real font
is embedded, and to the final wordmark once the logo designer delivers (see 09-brand).

---

## 5. Paid ads — the first campaign, when the trigger is met

Only after §1's trigger. Keep it small and boring:

- **Platform:** Meta (FB + Instagram), Advantage+ or a simple Traffic/Leads campaign.
- **Budget:** €5–10/day for 2–3 weeks. Treat it as tuition, not scale.
- **Geo:** Netherlands (start Randstad). **Language:** Dutch.
- **Audience:** interests around small-business ownership + the trades (ondernemer, ZZP,
  loodgieter/installateur/bouw). Expect imprecision — this is Meta's weak spot for B2B.
- **Best play:** **retargeting** klantkraan.nl visitors (needs the Pixel live now) + a
  lookalike off any client/lead list later.
- **Creative:** the two images above + Ad 1/Ad 2 copy. **Destination:** the demo page
  (klantkraan.nl/demo) — let the live demo do the selling.
- **One metric that matters:** cost per demo-chat-started (or per WhatsApp lead), not clicks.

---

## 6. Compliance guardrails (non-negotiable, from CLAUDE.md)

- No auto-posting to Facebook or groups. **Manual only.** (FB-groups auto-post was ruled out.)
- No automated replies, comments, or DMs — ever. Human writes every reply.
- Respect each group's rules; value-first, not spam.
- Dutch in all customer-facing copy. Never the founder's name — "de oprichter" / "Klantkraan".
- The growth-engine could later draft Facebook posts as a **paste-ready** channel (like
  LinkedIn/Reddit today). That's a future build; it stays assisted, never auto.

---

## 7. Next actions

**Founder:**
1. Create the Klantkraan Facebook Page (§2A).
2. Join 5–8 vetted groups from your personal profile; read each group's rules (§2B).
3. Post value-first (§3A) 1–2×/week; save the direct copy (§3B) for the Page.
4. If/when you set up Meta Business + get a Pixel ID, send it over.

**Claude (ready when you are):**
- Wire the Meta Pixel into the Astro site once there's a Pixel ID.
- Draft more group-safe posts / more image variants on request.
- Add Facebook as a paste-ready channel in the growth-engine (assisted, never auto).
