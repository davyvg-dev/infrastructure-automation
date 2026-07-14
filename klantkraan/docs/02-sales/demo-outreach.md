# Per-prospect demo outreach messages (Dutch)

> The words that go with a scaffolded branded demo, one variant per compliant channel of the
> 28-day sprint (`02-sales/28-day-sprint.md`). Each pairs THEIR demo with the free-pilot ask
> (`02-sales/pilot-offer.md`). Dutch, direct, no soft-trick hooks (kill-list #13), no founder
> name in copy — `[jouw naam]` is where you sign your own profile/email.

## How to make the per-prospect demo link

```
python -m app.scaffold "Jansen Loodgieters" --address "Utrecht"
# writes config/prospects/jansen-loodgieters.yaml, pulls services/hours from their site
# → open it, fill every PRIJS?, sanity-check the scraped services
```

Two ways to hand it to them:

1. **Live link (best for hand-raisers)** — deploy the config to the ops server, then the link is
   `<demo-host>/?client=jansen-loodgieters`. The server already routes by `?client=<slug>`.
   Scaffold a batch, deploy once/day → every pending prospect link goes live together.
2. **Clip (best for cold-ish / top-of-funnel)** — run it locally
   (`BUSINESS_CONFIG=config/prospects/jansen-loodgieters.yaml python -m app.server`), record a
   30-sec booking clip, send the video. No deploy needed.

> **Founder action worth doing once:** point a clean subdomain (`demo.klantkraan.nl`) at the demo
> host. Sending `demo-168-119-173-25.sslip.io/?client=…` in outreach reads as a scam link and
> kills conversion. A pretty link is half the credibility.

Placeholders below: `{{bedrijf}}`, `{{voornaam}}` (prospect), `{{demo-link}}`, `[jouw naam]` (you).

---

## 1. LinkedIn — connect (no pitch), then demo on a hand-raise

Compliant path for sole traders: connect + a genuine *question* first (kill-list #1 carve-out).
The demo only goes out once they've replied — at that point you're answering interest, not
sending an unsolicited commercial DM. All manual, no HeyReach.

**T1 — connection request:** no note.

**T2 — day 1 after they accept (a question, not a pitch):**
```
Dank voor de connectie {{voornaam}}.

Korte vraag uit nieuwsgierigheid: nemen jullie zelf de telefoon op
buiten kantooruren, of loopt dat via voicemail? Ik bouw AI-receptionisten
voor installatie- en klusbedrijven en ben benieuwd hoe jij het oplost.
```

**T3 — only if they reply with any interest → send THEIR demo:**
```
Ik heb er even eentje voor {{bedrijf}} klaargezet — met jullie diensten erin.
Stel 'm gerust een lastige vraag, hij houdt stand: {{demo-link}}

Bevalt het? Dan zet ik 'm 14 dagen gratis en volledig ingericht voor je live.
Je betaalt pas als je 'm wilt houden.
```

**T4 — day 12, no reply (breakup):**
```
Laatste bericht, beloofd. Mocht het ooit spelen — de demo voor {{bedrijf}}
blijft staan: {{demo-link}}. Succes met de zaak.
```

---

## 2. Ad lead — follow-up within 15 minutes

They opted in via the lead form, so a direct pitch is fine. Speed is everything (2-4x close under
15 min). WhatsApp if they left a number, else email.
```
Hoi {{voornaam}}, je vroeg net een demo aan via Klantkraan.

Ik heb er meteen eentje voor {{bedrijf}} klaargezet — probeer 'm gerust:
{{demo-link}}

Zoals beloofd: bevalt het, dan zet ik 'm 14 dagen gratis en volledig
ingericht voor je live. Geen kosten tot je besluit 'm te houden.

Zal ik 'm even voor je in gang zetten? Dan heb je 'm binnen 48 uur live.
```

---

## 3. Cold email — confirmed BV only (the 32 in the CSV)

Opt-out regime applies because these are legal entities, not sole traders. Send from a real
identified sender (the BV + KvK in the footer satisfies art. 11.7 — no founder name needed),
accurate subject, real afmeld-link. Do NOT send this to eenmanszaak/VOF.

**Onderwerp:** `Een AI-receptionist voor {{bedrijf}} — 14 dagen gratis`
```
Beste {{voornaam}},

Elke gemiste oproep buiten kantooruren is voor een installatiebedrijf al
snel een gemiste klus. Daar bouwden we Klantkraan voor: een AI-receptionist
die 24/7 in het Nederlands de telefoon en de websitechat opneemt, vragen
beantwoordt en afspraken inplant.

Ik heb er alvast eentje voor {{bedrijf}} klaargezet, met jullie diensten erin.
Probeer 'm gerust: {{demo-link}}

Als het bevalt, zet ik 'm 14 dagen gratis en volledig ingericht voor je live.
Je betaalt pas als je 'm wilt houden — daarna €299 per maand, maandelijks
opzegbaar.

Zal ik 'm voor je in gang zetten?

Met vriendelijke groet,
[jouw naam]
Klantkraan

--
Klantkraan, handelsnaam van T4 Software Consulting BV · KvK 90232135
klantkraan.nl · Geen interesse? Antwoord met "stop" en je hoort niets meer.
```

---

## 4. In-person — opener + leave-behind

Not electronic, outside the telemarketing rules. Highest close rate; book the demo on the spot.

**Opener (question-led, same as LinkedIn):**
> "Even uit nieuwsgierigheid — als jullie op een klus zitten en de telefoon gaat, wie neemt 'm
> dan op?" → laat de pijn even landen → "Ik bouw iets dat dat opvangt. Mag ik je 'm laten zien?"

**Leave-behind (kaartje met QR):**
```
Mis nooit meer een klant.

Scan en praat met een AI-receptionist — 24/7, in het Nederlands.
[QR → een live demo]

14 dagen gratis uitproberen · klantkraan.nl
```

**Same-day follow-up (na een gesprek, met hun eigen demo):**
```
Leuk je te spreken vandaag. Ik heb 'm even op {{bedrijf}} gezet zoals beloofd:
{{demo-link}}. Zeg 't maar als ik 'm 14 dagen gratis voor je live mag zetten.
[jouw naam]
```

---

## 5. Referral / warm intro

The fastest pilots. Ask everyone in your network; make forwarding effortless.

**The ask (to a contact):**
```
Ken jij een loodgieter, installateur of dakdekker die vaak klanten misloopt
omdat-ie de telefoon niet kan opnemen tijdens een klus? Ik zet voor 10
bedrijven in juli gratis een AI-receptionist op en zoek de juiste namen.
Mag ik je vragen er één aan me voor te stellen?
```

**Message once introduced:**
```
Hoi {{voornaam}}, {{tussenpersoon}} bracht ons in contact. Ik heb alvast een
AI-receptionist voor {{bedrijf}} klaargezet — probeer 'm gerust: {{demo-link}}.
Bevalt het, dan zet ik 'm 14 dagen gratis en volledig ingericht voor je live.
```

---

## Tone rules (keep every message on-brand)

- Short. Trades read on a phone between jobs. Two questions max, one link, one ask.
- Lead with the pain (gemiste oproep = gemiste klus), then the demo, then the free pilot.
- Never fake urgency or pretend to know them. The scarcity (10 in juli) is real; keep it real.
- Always name it as an AI-assistant — never imply it's a person.
