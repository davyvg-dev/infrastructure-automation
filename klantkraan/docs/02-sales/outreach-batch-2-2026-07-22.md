# Outreach batch 2 — 13 branded demos, ready to send (2026-07-22)

The second outreach wave. Thirteen more confirmed-**BV** Randstad prospects from
`prospects/prospects-randstad-2026-06-08.csv`, none overlapping batch 1, each with:

1. a **branded, working demo** at `?client=<slug>` (config in `ai-receptionist/config/clients/`,
   verified loading via `settings._load`), and
2. a **ready-to-send cold email** below — personalised with that prospect's own pain, then the
   pilot offer from `pilot-offer.md`.

All thirteen are confirmed **BV** (opt-out regime → cold email is compliant; footer carries the
KvK, per art. 11.7 — no founder name needed). The `likely-BV`/`unknown` rows and any prospect
without a findable e-mail or flagged `verify_before_cold` are **not** in this batch (CLAUDE.md).

---

## Before you send

The demo links use `demo.klantkraan.nl` — the same subdomain batch 1 already set up (A record
`demo` → `168.119.173.25`, DNS-only / grey cloud; Caddy vhost wired). These 13 new configs still
need to ship to the ops server: rerun `ops/hetzner/deploy.sh 168.119.173.25` so the new
`?client=<slug>` links resolve. (Say the word and I'll run it.)

**Fallback that works before deploy:** `https://demo-168-119-173-25.sslip.io/?client=<slug>`
— fine to open yourself to sanity-check a demo, or to record a 30-sec screen clip to send
instead of a link (best for a cold first touch anyway).

---

## The 13 at a glance

| # | Bedrijf | Stad | Vak | E-mail | Demo link |
|---|---------|------|-----|--------|-----------|
| 1 | Loodgietersbedrijf Meijer B.V. | Rotterdam | loodgieter | info@loodgietermeijer.nl | https://demo.klantkraan.nl/?client=meijer |
| 2 | Smits Installaties B.V. | Amsterdam | loodgieter | info@smits-installaties.nl | https://demo.klantkraan.nl/?client=smits-installaties |
| 3 | L van der Wiel B.V. | Den Haag | loodgieter | info@lvanderwielbv.nl | https://demo.klantkraan.nl/?client=van-der-wiel |
| 4 | P.H. Frauenfelder B.V. | Den Haag | loodgieter | info@phfrauenfelder.nl | https://demo.klantkraan.nl/?client=frauenfelder |
| 5 | Technisch Bureau W. Janssen B.V. | Den Haag | loodgieter | info@wjanssen.nl | https://demo.klantkraan.nl/?client=w-janssen |
| 6 | Andries Valkenburg Loodgieters & Verwarming B.V. | Delft | loodgieter | info@valkenburgloodgieters.nl | https://demo.klantkraan.nl/?client=valkenburg |
| 7 | A. Barendse & Zn. B.V. | Leiden | loodgieter | info@barendseleiden.nl | https://demo.klantkraan.nl/?client=barendse |
| 8 | Warmtetechnisch Bureau Joop Buiteman B.V. | Leiden | loodgieter | info@buiteman.nl | https://demo.klantkraan.nl/?client=buiteman |
| 9 | Dekker Installatietechniek B.V. | Gouda | loodgieter | info@dekkerinstallatietechniek.eu | https://demo.klantkraan.nl/?client=dekker |
| 10 | MD Dak & Klusbedrijf B.V. | Utrecht | dakdekker | info@dakdekkerutrechtbv.nl | https://demo.klantkraan.nl/?client=md-dak |
| 11 | Dak Garantie Amsterdam B.V. | Amsterdam | dakdekker | info@dakgarantieamsterdam.nl | https://demo.klantkraan.nl/?client=dak-garantie-amsterdam |
| 12 | Buddingh Dakdekkersbedrijf B.V. | Amsterdam | dakdekker | info@buddingh-dak.nl | https://demo.klantkraan.nl/?client=buddingh |
| 13 | DV Dakdekkers B.V. | Amsterdam | dakdekker | info@dvdakdekkers.nl | https://demo.klantkraan.nl/?client=dv-dakdekkers |

**How to work it:** ~30 min/day. Send 3–4 cold emails, log replies, and run the LinkedIn track in
parallel for the same names. Replace `[jouw naam]` with your own signature. Reply to any interest
within the hour — speed is the single biggest lever on close rate.

---

## Cold emails — ready to paste and send

Each is complete. Subject + body + compliant footer. Register matches batch 1 (`je`/`jouw`, short,
pain → demo → pilot → one ask).

### 1 — Loodgietersbedrijf Meijer (Rotterdam, loodgieter) · info@loodgietermeijer.nl

**Onderwerp:** Een AI-receptionist voor Loodgietersbedrijf Meijer — 14 dagen gratis

```
Beste team van Loodgietersbedrijf Meijer,

120 jaar vakmanschap en tien monteurs op de weg, en toch staan er maar 23
beoordelingen op Google. Dat is niet wat jullie waard zijn, en juist die eerste
indruk is waar een nieuwe klant op afgaat.

Daar bouwden we Klantkraan voor: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt en meteen een afspraak
inplant, en na de klus netjes om een Google-review vraagt.

Ik heb er alvast eentje voor Meijer klaargezet, met jullie diensten erin. Stel
'm gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=meijer

Bevalt het, dan zet ik 'm 14 dagen gratis en volledig ingericht voor je live.
Je betaalt pas als je 'm wilt houden — daarna €299 per maand, maandelijks
opzegbaar.

Zal ik 'm voor je in gang zetten?

Met vriendelijke groet,
[jouw naam]
Klantkraan

--
Klantkraan is een handelsnaam van T4 Software Consulting BV · KvK 90232135
klantkraan.nl · Geen interesse? Antwoord met "stop" en je hoort niets meer.
```

### 2 — Smits Installaties (Amsterdam, loodgieter) · info@smits-installaties.nl

**Onderwerp:** Een AI-receptionist voor Smits Installaties — 14 dagen gratis

```
Beste team van Smits Installaties,

Klanten die buiten kantooruren bellen, moeten bij jullie een apart storingsnummer
(088) onthouden. In de praktijk pakt lang niet iedereen dat, en die beller belt
gewoon de volgende loodgieter. Zonde van de aanvraag.

Daar bouwden we Klantkraan voor: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt en meteen een afspraak
inplant.

Ik heb er alvast eentje voor Smits klaargezet, met jullie diensten erin. Stel 'm
gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=smits-installaties

Bevalt het, dan zet ik 'm 14 dagen gratis en volledig ingericht voor je live.
Je betaalt pas als je 'm wilt houden — daarna €299 per maand, maandelijks
opzegbaar.

Zal ik 'm voor je in gang zetten?

Met vriendelijke groet,
[jouw naam]
Klantkraan

--
Klantkraan is een handelsnaam van T4 Software Consulting BV · KvK 90232135
klantkraan.nl · Geen interesse? Antwoord met "stop" en je hoort niets meer.
```

### 3 — L van der Wiel (Den Haag, loodgieter) · info@lvanderwielbv.nl

**Onderwerp:** Een AI-receptionist voor Van der Wiel — 14 dagen gratis

```
Beste team van Van der Wiel,

Meer dan 60 jaar loodgieterswerk in Den Haag, en toch staan er online maar een
handvol beoordelingen. Dat doet je vakmanschap tekort, want juist die reviews
leveren de volgende klant op.

Daar bouwden we Klantkraan voor: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt en meteen een afspraak
inplant, en na de klus netjes om een Google-review vraagt.

Ik heb er alvast eentje voor Van der Wiel klaargezet, met jullie diensten erin.
Stel 'm gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=van-der-wiel

Bevalt het, dan zet ik 'm 14 dagen gratis en volledig ingericht voor je live.
Je betaalt pas als je 'm wilt houden — daarna €299 per maand, maandelijks
opzegbaar.

Zal ik 'm voor je in gang zetten?

Met vriendelijke groet,
[jouw naam]
Klantkraan

--
Klantkraan is een handelsnaam van T4 Software Consulting BV · KvK 90232135
klantkraan.nl · Geen interesse? Antwoord met "stop" en je hoort niets meer.
```

### 4 — P.H. Frauenfelder (Den Haag, loodgieter) · info@phfrauenfelder.nl

**Onderwerp:** Een AI-receptionist voor Frauenfelder — 14 dagen gratis

```
Beste team van Frauenfelder,

Jullie bestaan al sinds 1944 en werken voor particulier en zakelijk. Maar wie na
kantoortijd belt, bereikt niemand, en een lekkage wacht niet tot de volgende
ochtend.

Daar bouwden we Klantkraan voor: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt en meteen een afspraak
inplant.

Ik heb er alvast eentje voor Frauenfelder klaargezet, met jullie diensten erin.
Stel 'm gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=frauenfelder

Bevalt het, dan zet ik 'm 14 dagen gratis en volledig ingericht voor je live.
Je betaalt pas als je 'm wilt houden — daarna €299 per maand, maandelijks
opzegbaar.

Zal ik 'm voor je in gang zetten?

Met vriendelijke groet,
[jouw naam]
Klantkraan

--
Klantkraan is een handelsnaam van T4 Software Consulting BV · KvK 90232135
klantkraan.nl · Geen interesse? Antwoord met "stop" en je hoort niets meer.
```

### 5 — Technisch Bureau W. Janssen (Den Haag, loodgieter) · info@wjanssen.nl

**Onderwerp:** Een AI-receptionist voor W. Janssen — 14 dagen gratis

```
Beste team van W. Janssen,

Bijna 90 jaar loodgieterswerk in Den Haag, en toch krijgt wie na vijven belt geen
gehoor. Precies op het moment dat een storing binnenkomt, staat de klant voor een
dichte deur.

Daar bouwden we Klantkraan voor: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt en meteen een afspraak
inplant.

Ik heb er alvast eentje voor W. Janssen klaargezet, met jullie diensten erin.
Stel 'm gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=w-janssen

Bevalt het, dan zet ik 'm 14 dagen gratis en volledig ingericht voor je live.
Je betaalt pas als je 'm wilt houden — daarna €299 per maand, maandelijks
opzegbaar.

Zal ik 'm voor je in gang zetten?

Met vriendelijke groet,
[jouw naam]
Klantkraan

--
Klantkraan is een handelsnaam van T4 Software Consulting BV · KvK 90232135
klantkraan.nl · Geen interesse? Antwoord met "stop" en je hoort niets meer.
```

### 6 — Andries Valkenburg (Delft, loodgieter) · info@valkenburgloodgieters.nl

**Onderwerp:** Een AI-receptionist voor Valkenburg — 14 dagen gratis

```
Beste team van Valkenburg,

Jullie zijn 's ochtends bereikbaar van negen tot half één, maar tussen de middag
en na sluitingstijd loopt een beller vast. Die klant met een lekkage wacht niet
en belt de volgende.

Daar bouwden we Klantkraan voor: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt en meteen een afspraak
inplant.

Ik heb er alvast eentje voor Valkenburg klaargezet, met jullie diensten erin.
Stel 'm gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=valkenburg

Bevalt het, dan zet ik 'm 14 dagen gratis en volledig ingericht voor je live.
Je betaalt pas als je 'm wilt houden — daarna €299 per maand, maandelijks
opzegbaar.

Zal ik 'm voor je in gang zetten?

Met vriendelijke groet,
[jouw naam]
Klantkraan

--
Klantkraan is een handelsnaam van T4 Software Consulting BV · KvK 90232135
klantkraan.nl · Geen interesse? Antwoord met "stop" en je hoort niets meer.
```

### 7 — A. Barendse & Zn. (Leiden, loodgieter) · info@barendseleiden.nl

**Onderwerp:** Een AI-receptionist voor Barendse — 14 dagen gratis

```
Beste team van Barendse,

Op Google staan er maar 11 beoordelingen op jullie naam, terwijl Barendse al 65
jaar tevreden klanten heeft. Al die stille tevreden klanten leveren nu geen
nieuwe op.

Daar bouwden we Klantkraan voor: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt en meteen een afspraak
inplant, en na de klus netjes om een Google-review vraagt.

Ik heb er alvast eentje voor Barendse klaargezet, met jullie diensten erin. Stel
'm gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=barendse

Bevalt het, dan zet ik 'm 14 dagen gratis en volledig ingericht voor je live.
Je betaalt pas als je 'm wilt houden — daarna €299 per maand, maandelijks
opzegbaar.

Zal ik 'm voor je in gang zetten?

Met vriendelijke groet,
[jouw naam]
Klantkraan

--
Klantkraan is een handelsnaam van T4 Software Consulting BV · KvK 90232135
klantkraan.nl · Geen interesse? Antwoord met "stop" en je hoort niets meer.
```

### 8 — Warmtetechnisch Bureau Joop Buiteman (Leiden, loodgieter) · info@buiteman.nl

**Onderwerp:** Een AI-receptionist voor Buiteman — 14 dagen gratis

```
Beste team van Buiteman,

Met 36 monteurs op de weg ronden jullie elke dag flink wat klussen af. Zonder een
vast opvolgmoment blijft de Google-review daarna liggen, en dat is precies wat een
nieuwe klant als eerste checkt.

Daar bouwden we Klantkraan voor: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt en meteen een afspraak
inplant, en na de klus netjes om een Google-review vraagt.

Ik heb er alvast eentje voor Buiteman klaargezet, met jullie diensten erin. Stel
'm gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=buiteman

Bevalt het, dan zet ik 'm 14 dagen gratis en volledig ingericht voor je live.
Je betaalt pas als je 'm wilt houden — daarna €299 per maand, maandelijks
opzegbaar.

Zal ik 'm voor je in gang zetten?

Met vriendelijke groet,
[jouw naam]
Klantkraan

--
Klantkraan is een handelsnaam van T4 Software Consulting BV · KvK 90232135
klantkraan.nl · Geen interesse? Antwoord met "stop" en je hoort niets meer.
```

### 9 — Dekker Installatietechniek (Gouda, loodgieter) · info@dekkerinstallatietechniek.eu

**Onderwerp:** Een AI-receptionist voor Dekker Installatietechniek — 14 dagen gratis

```
Beste team van Dekker Installatietechniek,

Jullie storingsdienst draait 24/7, maar online is Dekker nauwelijks zichtbaar:
geen WhatsApp, geen online afspraak, weinig reviews. Nieuwe klanten die je
vergelijken, haken daar stilletjes op af.

Daar bouwden we Klantkraan voor: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt en meteen een afspraak
inplant.

Ik heb er alvast eentje voor Dekker klaargezet, met jullie diensten erin. Stel 'm
gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=dekker

Bevalt het, dan zet ik 'm 14 dagen gratis en volledig ingericht voor je live.
Je betaalt pas als je 'm wilt houden — daarna €299 per maand, maandelijks
opzegbaar.

Zal ik 'm voor je in gang zetten?

Met vriendelijke groet,
[jouw naam]
Klantkraan

--
Klantkraan is een handelsnaam van T4 Software Consulting BV · KvK 90232135
klantkraan.nl · Geen interesse? Antwoord met "stop" en je hoort niets meer.
```

### 10 — MD Dak & Klusbedrijf (Utrecht, dakdekker) · info@dakdekkerutrechtbv.nl

**Onderwerp:** Een AI-receptionist voor MD Dak & Klusbedrijf — 14 dagen gratis

```
Beste team van MD Dak & Klusbedrijf,

Jullie zetten dag-en-nacht bereikbaarheid op de site, maar zelf een 24/7-lijn
bemannen is duur en zwaar. In de praktijk valt een nachtelijke stormmelding dan
alsnog buiten de boot.

Daar bouwden we Klantkraan voor: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt en meteen een afspraak of
offerte inplant.

Ik heb er alvast eentje voor MD Dak klaargezet, met jullie diensten erin. Stel 'm
gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=md-dak

Bevalt het, dan zet ik 'm 14 dagen gratis en volledig ingericht voor je live.
Je betaalt pas als je 'm wilt houden — daarna €299 per maand, maandelijks
opzegbaar.

Zal ik 'm voor je in gang zetten?

Met vriendelijke groet,
[jouw naam]
Klantkraan

--
Klantkraan is een handelsnaam van T4 Software Consulting BV · KvK 90232135
klantkraan.nl · Geen interesse? Antwoord met "stop" en je hoort niets meer.
```

### 11 — Dak Garantie Amsterdam (Amsterdam, dakdekker) · info@dakgarantieamsterdam.nl

**Onderwerp:** Een AI-receptionist voor Dak Garantie Amsterdam — 14 dagen gratis

```
Beste team van Dak Garantie Amsterdam,

Drie vestigingen, één telefoonnummer. Zodra die lijn bezet is, lopen aanvragen
uit meerdere stadsdelen tegelijk mis, zonder dat je het merkt.

Daar bouwden we Klantkraan voor: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt en meteen een afspraak of
offerte inplant.

Ik heb er alvast eentje voor Dak Garantie Amsterdam klaargezet, met jullie
diensten erin. Stel 'm gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=dak-garantie-amsterdam

Bevalt het, dan zet ik 'm 14 dagen gratis en volledig ingericht voor je live.
Je betaalt pas als je 'm wilt houden — daarna €299 per maand, maandelijks
opzegbaar.

Zal ik 'm voor je in gang zetten?

Met vriendelijke groet,
[jouw naam]
Klantkraan

--
Klantkraan is een handelsnaam van T4 Software Consulting BV · KvK 90232135
klantkraan.nl · Geen interesse? Antwoord met "stop" en je hoort niets meer.
```

### 12 — Buddingh Dakdekkersbedrijf (Amsterdam, dakdekker) · info@buddingh-dak.nl

**Onderwerp:** Een AI-receptionist voor Buddingh — 14 dagen gratis

```
Beste team van Buddingh,

Veertig jaar dakwerk in Amsterdam, en online is er alleen een telefoonnummer:
geen formulier, geen WhatsApp, geen reviews. Wie 's avonds belt en niemand treft,
is de aanvraag kwijt.

Daar bouwden we Klantkraan voor: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt en meteen een afspraak of
offerte inplant, en na de klus netjes om een Google-review vraagt.

Ik heb er alvast eentje voor Buddingh klaargezet, met jullie diensten erin. Stel
'm gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=buddingh

Bevalt het, dan zet ik 'm 14 dagen gratis en volledig ingericht voor je live.
Je betaalt pas als je 'm wilt houden — daarna €299 per maand, maandelijks
opzegbaar.

Zal ik 'm voor je in gang zetten?

Met vriendelijke groet,
[jouw naam]
Klantkraan

--
Klantkraan is een handelsnaam van T4 Software Consulting BV · KvK 90232135
klantkraan.nl · Geen interesse? Antwoord met "stop" en je hoort niets meer.
```

### 13 — DV Dakdekkers (Amsterdam, dakdekker) · info@dvdakdekkers.nl

**Onderwerp:** Een AI-receptionist voor DV Dakdekkers — 14 dagen gratis

```
Beste team van DV Dakdekkers,

Een perfecte 5.0 op meer dan 50 reviews: daar loop je op voor. Toch draait er een
kortingsactie, en dat trekt vooral prijskopers. Sneller reageren op serieuze
aanvragen laat je op kwaliteit concurreren in plaats van op prijs.

Daar bouwden we Klantkraan voor: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt en meteen een afspraak of
offerte inplant.

Ik heb er alvast eentje voor DV Dakdekkers klaargezet, met jullie diensten erin.
Stel 'm gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=dv-dakdekkers

Bevalt het, dan zet ik 'm 14 dagen gratis en volledig ingericht voor je live.
Je betaalt pas als je 'm wilt houden — daarna €299 per maand, maandelijks
opzegbaar.

Zal ik 'm voor je in gang zetten?

Met vriendelijke groet,
[jouw naam]
Klantkraan

--
Klantkraan is een handelsnaam van T4 Software Consulting BV · KvK 90232135
klantkraan.nl · Geen interesse? Antwoord met "stop" en je hoort niets meer.
```

---

## Compliance recap

- All 13 are confirmed **BV** → cold email allowed under the opt-out regime; every email carries
  the KvK + a working "stop" opt-out (art. 11.7 satisfied without the founder's name).
- The demo **discloses it's a digital assistant** in its greeting (EU AI Act art. 50) — baked into
  every config.
- No invented prices anywhere — the bot books and says the monteur confirms the tarief on locatie.
- Skipped and why: no findable e-mail — Folstra, Loodgieter Rotterdam B.V., Osterhoff, Vak
  Loodgieter, Dakreparatie Nederland, JHF Bouw. Flagged `verify_before_cold` — W.A. Kuijpers
  (spambeveiligd), Vermeulen & Bol (shared site/ownership). Not confirmed BV (`likely-BV` /
  `unknown`, KvK-verify first) — ISA Loodgieters, Hennink, Loodgieter Rotterdam 24, Van Gelder
  Utrecht, Direct Loodgietersbedrijf, Loodgieter Utrecht (.com), Loodgietersbedrijf Utrecht
  (.nl), Van der Wijck Daktechniek, B&G Onderhoud, Kewodak, Haagsche Dakwerken, Dakdekkersbedrijf
  Leiden, Dakdekker Amsterdam.
```
