# Outreach batch 3 — 23 cold emails on the founding-member offer (2026-07-29)

> **In flux, do not treat the bodies below as final.** Two changes landed after this was
> written, both on the founder's call:
> 1. **Price: first *month* at €149, not the first six.** The plain-text bodies below still
>    say six months.
> 2. **The mails are now generated**, branded, from `ai-receptionist/scripts/outreach_mail.py`
>    (same `mail_layout` blocks as the welcome mail), not hand-written plain text. That script
>    is the source of what actually gets sent; this file is its human-readable twin.
>
> Also parked: the "maandelijks opzegbaar" line is **removed** from the generated mails until
> the cancellation term is decided.
>
> **Resolved 2026-07-31 on the founder's call:** the founding offer is **eerste maand €149**,
> plus an optional prepay reward — 6 months upfront at the founding rate, **€894 excl. BTW**
> (offered after a verbal yes, on the phone or in the mail P.S., never as the opener).
> `founding-member-offer.md` now matches, the six-month taper is retired, and the generated
> mails carry the prepay line. Doc, mails and phone script agree; this batch is clear to send.

**This supersedes batches 1 and 2. Do not send those.** Both pitch the free 14-day pilot at
€299/mnd, which `founding-member-offer.md` retired on 2026-07-24. Same 23 prospects, same
branded demos, new offer: **€149/mnd de eerste 6 maanden, geen opstartkosten, 30 dagen
geld-terug.**

Every prospect here is a confirmed **BV** from `prospects/prospects-randstad-2026-06-08.csv`
with a findable, unflagged e-mail. That is the complete cold-email-cleared set: the other 22
Randstad rows are blocked, each for a reason listed at the bottom.

All 23 branded demos verified live on 2026-07-29 (`GET /config?client=<slug>` → 200 on
demo.klantkraan.nl), each greeting disclosing it is a digital assistant (EU AI Act art. 50).

---

## Send order and pacing

The list is ordered by hook strength, not by city. Numbers 1–13 lead with a **bereikbaarheids-gat**
(a beller who gets nothing back, which is direct lost revenue). Numbers 14–23 lead with a
**review-gat**, which is real but a softer sell. If you only get through half the list, you got
through the right half.

**Pacing:** 5 to 8 per day from `davy@klantkraan.nl`, spread across the morning, plain text, no
tracking pixels, no attachments. The domain is young and its reputation is worth more than speed.
The whole batch takes about four working days. Reply to any interest within the hour, that is the
single biggest lever on close rate.

**A/B on the subject line:** the default below is `Een AI-receptionist voor {bedrijf}, al
klaargezet`. Run the first ten with that, and if opens disappoint, switch the second half to
`{bedrijf}: wie neemt op als jij op een dak staat?` and compare.

**Send with `python -m scripts.outreach_send --send --limit 6`** from `ai-receptionist/`, over
Gmail SMTP as `davy@klantkraan.nl`. Dry run is the default; `--send` is the only thing that opens
a socket, already-sent prospects are skipped from `build/outreach/sent.json`, and `--dump` writes
`.eml` files to eyeball first. Needs `GMAIL_USER` + `GMAIL_APP_PASSWORD` in `.env`.

> **Do not stage this batch as Gmail drafts.** The 23 drafts created on 2026-07-29 are stale and
> should be deleted: they carry the retired six-month offer, and every link in them is wrapped in
> `https://www.google.com/url?q=…&source=gmail&ust=…`, which in a cold mail reads as phishing.
>
> An earlier note here claimed an explicit HTML anchor fixed that. It does not. The wrapper is
> applied by Gmail *after* our HTML is handed over, to the `href` itself, and there is no flag to
> turn it off — supplying an anchor only changes what the link *says*, not where it points. Proof
> it is Gmail and not our renderer: a Resend mail read back through the same API keeps its hrefs
> intact, and `scripts/outreach_mail.py` emits `href="https://demo.klantkraan.nl/?client=<slug>"`
> clean every time.
>
> It also matters beyond looks. The wrapper percent-encodes the `=` in `?client%3D<slug>`, the one
> parameter that selects the branded demo, and a mangled `?client=` silently loads the *default*
> business — a bug this project has already shipped once (fixed in ec01a38).
>
> The rule for any future batch: render the MIME, send it over SMTP, never compose in Gmail.

---

## The 23 at a glance

| # | Bedrijf | Stad | Vak | E-mail | Demo link |
|---|---------|------|-----|--------|-----------|
| 1 | Dak Garantie Amsterdam B.V. | Amsterdam | dakdekker | info@dakgarantieamsterdam.nl | https://demo.klantkraan.nl/?client=dak-garantie-amsterdam |
| 2 | MD Dak & Klusbedrijf B.V. | Utrecht | dakdekker | info@dakdekkerutrechtbv.nl | https://demo.klantkraan.nl/?client=md-dak |
| 3 | Duckdekker B.V. | Den Haag | dakdekker | info@duckdekker.nl | https://demo.klantkraan.nl/?client=duckdekker |
| 4 | AJ Dakwerken B.V. | Hilversum | dakdekker | info@ajdakwerken.nl | https://demo.klantkraan.nl/?client=aj-dakwerken |
| 5 | Smits Installaties B.V. | Amsterdam | loodgieter | info@smits-installaties.nl | https://demo.klantkraan.nl/?client=smits-installaties |
| 6 | Derwort Loodgieters B.V. | Delft | loodgieter | info@derwort.nu | https://demo.klantkraan.nl/?client=derwort |
| 7 | Andries Valkenburg B.V. | Delft | loodgieter | info@valkenburgloodgieters.nl | https://demo.klantkraan.nl/?client=valkenburg |
| 8 | P.H. Frauenfelder B.V. | Den Haag | loodgieter | info@phfrauenfelder.nl | https://demo.klantkraan.nl/?client=frauenfelder |
| 9 | Technisch Bureau W. Janssen B.V. | Den Haag | loodgieter | info@wjanssen.nl | https://demo.klantkraan.nl/?client=w-janssen |
| 10 | Visser & Van der Hell B.V. | Rotterdam | loodgieter | info@visservanderhell.nl | https://demo.klantkraan.nl/?client=visser-van-der-hell |
| 11 | Loodgieter Utrecht B.V. | Utrecht | loodgieter | info@loodgieterutrechtbv.nl | https://demo.klantkraan.nl/?client=loodgieter-utrecht-bv |
| 12 | VDP Dakbedekking B.V. | Rotterdam | dakdekker | info@vdpdakbedekking.nl | https://demo.klantkraan.nl/?client=vdp-dakbedekking |
| 13 | Buddingh Dakdekkersbedrijf B.V. | Amsterdam | dakdekker | info@buddingh-dak.nl | https://demo.klantkraan.nl/?client=buddingh |
| 14 | Lohmann Groep B.V. | Rotterdam | loodgieter | info@lohmannbv.nl | https://demo.klantkraan.nl/?client=lohmann |
| 15 | DV Dakdekkers B.V. | Amsterdam | dakdekker | info@dvdakdekkers.nl | https://demo.klantkraan.nl/?client=dv-dakdekkers |
| 16 | Dekker Installatietechniek B.V. | Gouda | loodgieter | info@dekkerinstallatietechniek.eu | https://demo.klantkraan.nl/?client=dekker |
| 17 | Warmtetechnisch Bureau Joop Buiteman B.V. | Leiden | loodgieter | info@buiteman.nl | https://demo.klantkraan.nl/?client=buiteman |
| 18 | Loodgietersbedrijf Meijer B.V. | Rotterdam | loodgieter | info@loodgietermeijer.nl | https://demo.klantkraan.nl/?client=meijer |
| 19 | Herfst B.V. | Amsterdam | loodgieter | info@herfstbv.nl | https://demo.klantkraan.nl/?client=herfst |
| 20 | W.J. van der Herp B.V. | Den Haag | loodgieter | info@vanderherp.nl | https://demo.klantkraan.nl/?client=van-der-herp |
| 21 | A. Barendse & Zn. B.V. | Leiden | loodgieter | info@barendseleiden.nl | https://demo.klantkraan.nl/?client=barendse |
| 22 | T.I.B. Verkuylen bv | Leiden | loodgieter | info@tib-verkuylen.nl | https://demo.klantkraan.nl/?client=verkuylen |
| 23 | L van der Wiel b.v. | Den Haag | loodgieter | info@lvanderwielbv.nl | https://demo.klantkraan.nl/?client=van-der-wiel |

Replace `[jouw naam]` with your own signature before sending.

---

## Cold emails — ready to paste and send

### 1 — Dak Garantie Amsterdam (Amsterdam, dakdekker) · info@dakgarantieamsterdam.nl

**Onderwerp:** Een AI-receptionist voor Dak Garantie Amsterdam, al klaargezet

```
Beste team van Dak Garantie Amsterdam,

Drie vestigingen, één telefoonnummer. Zodra die lijn bezet is, lopen aanvragen
uit meerdere stadsdelen tegelijk mis, zonder dat iemand het merkt.

Daarvoor is Klantkraan gebouwd: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt en meteen een afspraak of
offerte inplant.

Ik heb er alvast een voor Dak Garantie Amsterdam klaargezet, met jullie diensten
erin. Stel 'm gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=dak-garantie-amsterdam

We nemen een klein aantal oprichtersklanten aan. Die betalen de eerste zes
maanden €149 per maand (excl. btw) in plaats van €299, zonder opstartkosten, en
krijgen binnen 30 dagen alles terug als het niet bevalt. Maandelijks opzegbaar.
In ruil vragen we een kort verhaal zodra hij zich bewezen heeft.

Zal ik 'm voor jullie live zetten? Binnen 48 uur staat hij op je site.

Met vriendelijke groet,
[jouw naam]
Klantkraan

--
Klantkraan is een handelsnaam van T4 Software Consulting BV · KvK 90232135
klantkraan.nl · Geen interesse? Antwoord met "stop" en je hoort niets meer.
```

### 2 — MD Dak & Klusbedrijf (Utrecht, dakdekker) · info@dakdekkerutrechtbv.nl

**Onderwerp:** Een AI-receptionist voor MD Dak & Klusbedrijf, al klaargezet

```
Beste team van MD Dak & Klusbedrijf,

Op jullie site staat dag-en-nacht bereikbaarheid, maar zelf een 24/7-lijn
bemannen is duur en zwaar. In de praktijk valt een nachtelijke stormmelding dan
alsnog buiten de boot.

Daarvoor is Klantkraan gebouwd: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt en meteen een afspraak of
offerte inplant.

Ik heb er alvast een voor MD Dak klaargezet, met jullie diensten erin. Stel 'm
gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=md-dak

We nemen een klein aantal oprichtersklanten aan. Die betalen de eerste zes
maanden €149 per maand (excl. btw) in plaats van €299, zonder opstartkosten, en
krijgen binnen 30 dagen alles terug als het niet bevalt. Maandelijks opzegbaar.
In ruil vragen we een kort verhaal zodra hij zich bewezen heeft.

Zal ik 'm voor jullie live zetten? Binnen 48 uur staat hij op je site.

Met vriendelijke groet,
[jouw naam]
Klantkraan

--
Klantkraan is een handelsnaam van T4 Software Consulting BV · KvK 90232135
klantkraan.nl · Geen interesse? Antwoord met "stop" en je hoort niets meer.
```

### 3 — Duckdekker (Den Haag, dakdekker) · info@duckdekker.nl

**Onderwerp:** Een AI-receptionist voor Duckdekker, al klaargezet

```
Beste team van Duckdekker,

Jullie sluiten om 17:00, maar stormschade en daklekkages melden zich ook 's
avonds en in het weekend. Zonder opvang gaat die spoedklus naar een dakdekker
die wel opneemt, of je draait er zelf een dure nachtdienst voor.

Daarvoor is Klantkraan gebouwd: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt en meteen een afspraak of
offerte inplant.

Ik heb er alvast een voor Duckdekker klaargezet, met jullie diensten erin. Stel
'm gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=duckdekker

We nemen een klein aantal oprichtersklanten aan. Die betalen de eerste zes
maanden €149 per maand (excl. btw) in plaats van €299, zonder opstartkosten, en
krijgen binnen 30 dagen alles terug als het niet bevalt. Maandelijks opzegbaar.
In ruil vragen we een kort verhaal zodra hij zich bewezen heeft.

Zal ik 'm voor jullie live zetten? Binnen 48 uur staat hij op je site.

Met vriendelijke groet,
[jouw naam]
Klantkraan

--
Klantkraan is een handelsnaam van T4 Software Consulting BV · KvK 90232135
klantkraan.nl · Geen interesse? Antwoord met "stop" en je hoort niets meer.
```

### 4 — AJ Dakwerken (Hilversum, dakdekker) · info@ajdakwerken.nl

**Onderwerp:** Een AI-receptionist voor AJ Dakwerken, al klaargezet

```
Beste team van AJ Dakwerken,

Met 108 beoordelingen en een eigen showroom hebben jullie flink in acquisitie
geïnvesteerd. Des te zonde als een beller buiten kantooruren geen gehoor krijgt
en alsnog bij de concurrent uitkomt.

Daarvoor is Klantkraan gebouwd: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt en meteen een afspraak of
offerte inplant.

Ik heb er alvast een voor AJ Dakwerken klaargezet, met jullie diensten erin.
Stel 'm gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=aj-dakwerken

We nemen een klein aantal oprichtersklanten aan. Die betalen de eerste zes
maanden €149 per maand (excl. btw) in plaats van €299, zonder opstartkosten, en
krijgen binnen 30 dagen alles terug als het niet bevalt. Maandelijks opzegbaar.
In ruil vragen we een kort verhaal zodra hij zich bewezen heeft.

Zal ik 'm voor jullie live zetten? Binnen 48 uur staat hij op je site.

Met vriendelijke groet,
[jouw naam]
Klantkraan

--
Klantkraan is een handelsnaam van T4 Software Consulting BV · KvK 90232135
klantkraan.nl · Geen interesse? Antwoord met "stop" en je hoort niets meer.
```

### 5 — Smits Installaties (Amsterdam, loodgieter) · info@smits-installaties.nl

**Onderwerp:** Een AI-receptionist voor Smits Installaties, al klaargezet

```
Beste team van Smits Installaties,

Klanten die buiten kantooruren bellen moeten bij jullie een apart 088-nummer
onthouden. In de praktijk pakt lang niet iedereen dat, en die beller belt gewoon
de volgende loodgieter.

Daarvoor is Klantkraan gebouwd: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt en meteen een afspraak
inplant.

Ik heb er alvast een voor Smits klaargezet, met jullie diensten erin. Stel 'm
gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=smits-installaties

We nemen een klein aantal oprichtersklanten aan. Die betalen de eerste zes
maanden €149 per maand (excl. btw) in plaats van €299, zonder opstartkosten, en
krijgen binnen 30 dagen alles terug als het niet bevalt. Maandelijks opzegbaar.
In ruil vragen we een kort verhaal zodra hij zich bewezen heeft.

Zal ik 'm voor jullie live zetten? Binnen 48 uur staat hij op je site.

Met vriendelijke groet,
[jouw naam]
Klantkraan

--
Klantkraan is een handelsnaam van T4 Software Consulting BV · KvK 90232135
klantkraan.nl · Geen interesse? Antwoord met "stop" en je hoort niets meer.
```

### 6 — Derwort Loodgieters (Delft, loodgieter) · info@derwort.nu

**Onderwerp:** Een AI-receptionist voor Derwort, al klaargezet

```
Beste team van Derwort,

Jullie staan sterk op Google, maar voor spoed na 16:30 is er geen zichtbare
opvang. Een gemiste oproep op vrijdagmiddag is een klant die maandag bij iemand
anders zit.

Daarvoor is Klantkraan gebouwd: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt en meteen een afspraak
inplant.

Ik heb er alvast een voor Derwort klaargezet, met jullie diensten erin. Stel 'm
gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=derwort

We nemen een klein aantal oprichtersklanten aan. Die betalen de eerste zes
maanden €149 per maand (excl. btw) in plaats van €299, zonder opstartkosten, en
krijgen binnen 30 dagen alles terug als het niet bevalt. Maandelijks opzegbaar.
In ruil vragen we een kort verhaal zodra hij zich bewezen heeft.

Zal ik 'm voor jullie live zetten? Binnen 48 uur staat hij op je site.

Met vriendelijke groet,
[jouw naam]
Klantkraan

--
Klantkraan is een handelsnaam van T4 Software Consulting BV · KvK 90232135
klantkraan.nl · Geen interesse? Antwoord met "stop" en je hoort niets meer.
```

### 7 — Andries Valkenburg (Delft, loodgieter) · info@valkenburgloodgieters.nl

**Onderwerp:** Een AI-receptionist voor Valkenburg, al klaargezet

```
Beste team van Valkenburg,

Jullie zijn 's ochtends bereikbaar van negen tot half één. Tussen de middag en
na sluitingstijd loopt een beller vast, en iemand met een lekkage wacht niet tot
morgen.

Daarvoor is Klantkraan gebouwd: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt en meteen een afspraak
inplant.

Ik heb er alvast een voor Valkenburg klaargezet, met jullie diensten erin. Stel
'm gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=valkenburg

We nemen een klein aantal oprichtersklanten aan. Die betalen de eerste zes
maanden €149 per maand (excl. btw) in plaats van €299, zonder opstartkosten, en
krijgen binnen 30 dagen alles terug als het niet bevalt. Maandelijks opzegbaar.
In ruil vragen we een kort verhaal zodra hij zich bewezen heeft.

Zal ik 'm voor jullie live zetten? Binnen 48 uur staat hij op je site.

Met vriendelijke groet,
[jouw naam]
Klantkraan

--
Klantkraan is een handelsnaam van T4 Software Consulting BV · KvK 90232135
klantkraan.nl · Geen interesse? Antwoord met "stop" en je hoort niets meer.
```

### 8 — P.H. Frauenfelder (Den Haag, loodgieter) · info@phfrauenfelder.nl

**Onderwerp:** Een AI-receptionist voor Frauenfelder, al klaargezet

```
Beste team van Frauenfelder,

Jullie bestaan sinds 1944 en werken voor particulier en zakelijk. Maar wie na
kantoortijd belt, bereikt niemand, en een lekkage wacht niet tot de volgende
ochtend.

Daarvoor is Klantkraan gebouwd: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt en meteen een afspraak
inplant.

Ik heb er alvast een voor Frauenfelder klaargezet, met jullie diensten erin.
Stel 'm gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=frauenfelder

We nemen een klein aantal oprichtersklanten aan. Die betalen de eerste zes
maanden €149 per maand (excl. btw) in plaats van €299, zonder opstartkosten, en
krijgen binnen 30 dagen alles terug als het niet bevalt. Maandelijks opzegbaar.
In ruil vragen we een kort verhaal zodra hij zich bewezen heeft.

Zal ik 'm voor jullie live zetten? Binnen 48 uur staat hij op je site.

Met vriendelijke groet,
[jouw naam]
Klantkraan

--
Klantkraan is een handelsnaam van T4 Software Consulting BV · KvK 90232135
klantkraan.nl · Geen interesse? Antwoord met "stop" en je hoort niets meer.
```

### 9 — Technisch Bureau W. Janssen (Den Haag, loodgieter) · info@wjanssen.nl

**Onderwerp:** Een AI-receptionist voor W. Janssen, al klaargezet

```
Beste team van W. Janssen,

Bijna 90 jaar loodgieterswerk in Den Haag, en toch krijgt wie na vijven belt
geen gehoor. Op jullie site staat wel een WhatsApp-nummer, maar zonder iemand
die erop reageert blijft dat een dichte deur.

Daarvoor is Klantkraan gebouwd: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt en meteen een afspraak
inplant.

Ik heb er alvast een voor W. Janssen klaargezet, met jullie diensten erin. Stel
'm gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=w-janssen

We nemen een klein aantal oprichtersklanten aan. Die betalen de eerste zes
maanden €149 per maand (excl. btw) in plaats van €299, zonder opstartkosten, en
krijgen binnen 30 dagen alles terug als het niet bevalt. Maandelijks opzegbaar.
In ruil vragen we een kort verhaal zodra hij zich bewezen heeft.

Zal ik 'm voor jullie live zetten? Binnen 48 uur staat hij op je site.

Met vriendelijke groet,
[jouw naam]
Klantkraan

--
Klantkraan is een handelsnaam van T4 Software Consulting BV · KvK 90232135
klantkraan.nl · Geen interesse? Antwoord met "stop" en je hoort niets meer.
```

### 10 — Visser & Van der Hell (Rotterdam, loodgieter) · info@visservanderhell.nl

**Onderwerp:** Een AI-receptionist voor Visser & Van der Hell, al klaargezet

```
Beste team van Visser & Van der Hell,

Een klant die om half zes belt en geen gehoor krijgt, zoekt online verder en
belt de volgende loodgieter. Juist buiten kantooruren, als een lekkage niet kan
wachten, gaat er zo omzet langs je heen.

Daarvoor is Klantkraan gebouwd: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen over je diensten beantwoordt en
meteen een afspraak inplant.

Ik heb er alvast een voor Visser & Van der Hell klaargezet, met jullie diensten
erin. Stel 'm gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=visser-van-der-hell

We nemen een klein aantal oprichtersklanten aan. Die betalen de eerste zes
maanden €149 per maand (excl. btw) in plaats van €299, zonder opstartkosten, en
krijgen binnen 30 dagen alles terug als het niet bevalt. Maandelijks opzegbaar.
In ruil vragen we een kort verhaal zodra hij zich bewezen heeft.

Zal ik 'm voor jullie live zetten? Binnen 48 uur staat hij op je site.

Met vriendelijke groet,
[jouw naam]
Klantkraan

--
Klantkraan is een handelsnaam van T4 Software Consulting BV · KvK 90232135
klantkraan.nl · Geen interesse? Antwoord met "stop" en je hoort niets meer.
```

### 11 — Loodgieter Utrecht B.V. (Utrecht, loodgieter) · info@loodgieterutrechtbv.nl

**Onderwerp:** Een AI-receptionist voor Loodgieter Utrecht, al klaargezet

```
Beste team van Loodgieter Utrecht,

Je belooft klanten dat je direct terugbelt, maar zonder automatische opvolging
valt er op een drukke dag altijd wel een oproep tussen wal en schip. Eén gemiste
beller is zo een misgelopen klus.

Daarvoor is Klantkraan gebouwd: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt en meteen een afspraak
inplant.

Ik heb er alvast een voor Loodgieter Utrecht klaargezet, met jullie diensten
erin. Stel 'm gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=loodgieter-utrecht-bv

We nemen een klein aantal oprichtersklanten aan. Die betalen de eerste zes
maanden €149 per maand (excl. btw) in plaats van €299, zonder opstartkosten, en
krijgen binnen 30 dagen alles terug als het niet bevalt. Maandelijks opzegbaar.
In ruil vragen we een kort verhaal zodra hij zich bewezen heeft.

Zal ik 'm voor jullie live zetten? Binnen 48 uur staat hij op je site.

Met vriendelijke groet,
[jouw naam]
Klantkraan

--
Klantkraan is een handelsnaam van T4 Software Consulting BV · KvK 90232135
klantkraan.nl · Geen interesse? Antwoord met "stop" en je hoort niets meer.
```

### 12 — VDP Dakbedekking (Rotterdam, dakdekker) · info@vdpdakbedekking.nl

**Onderwerp:** Een AI-receptionist voor VDP Dakbedekking, al klaargezet

```
Beste team van VDP Dakbedekking,

Op jullie site staat dat je telefonisch geen offertes opneemt. Maar wie 's
avonds belt na een daklekkage wil juist meteen geholpen worden. Die beller
krijgt nu niets terug en gaat verder zoeken.

Daarvoor is Klantkraan gebouwd: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt en meteen een afspraak of
offerte inplant.

Ik heb er alvast een voor VDP Dakbedekking klaargezet, met jullie diensten erin.
Stel 'm gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=vdp-dakbedekking

We nemen een klein aantal oprichtersklanten aan. Die betalen de eerste zes
maanden €149 per maand (excl. btw) in plaats van €299, zonder opstartkosten, en
krijgen binnen 30 dagen alles terug als het niet bevalt. Maandelijks opzegbaar.
In ruil vragen we een kort verhaal zodra hij zich bewezen heeft.

Zal ik 'm voor jullie live zetten? Binnen 48 uur staat hij op je site.

Met vriendelijke groet,
[jouw naam]
Klantkraan

--
Klantkraan is een handelsnaam van T4 Software Consulting BV · KvK 90232135
klantkraan.nl · Geen interesse? Antwoord met "stop" en je hoort niets meer.
```

### 13 — Buddingh Dakdekkersbedrijf (Amsterdam, dakdekker) · info@buddingh-dak.nl

**Onderwerp:** Een AI-receptionist voor Buddingh, al klaargezet

```
Beste team van Buddingh,

Veertig jaar dakwerk in Amsterdam, en online staat er alleen een telefoonnummer.
Geen formulier, geen WhatsApp. Wie 's avonds belt en niemand treft, is een
aanvraag die je nooit gezien hebt.

Daarvoor is Klantkraan gebouwd: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt en meteen een afspraak of
offerte inplant, en na de klus netjes om een Google-review vraagt.

Ik heb er alvast een voor Buddingh klaargezet, met jullie diensten erin. Stel 'm
gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=buddingh

We nemen een klein aantal oprichtersklanten aan. Die betalen de eerste zes
maanden €149 per maand (excl. btw) in plaats van €299, zonder opstartkosten, en
krijgen binnen 30 dagen alles terug als het niet bevalt. Maandelijks opzegbaar.
In ruil vragen we een kort verhaal zodra hij zich bewezen heeft.

Zal ik 'm voor jullie live zetten? Binnen 48 uur staat hij op je site.

Met vriendelijke groet,
[jouw naam]
Klantkraan

--
Klantkraan is een handelsnaam van T4 Software Consulting BV · KvK 90232135
klantkraan.nl · Geen interesse? Antwoord met "stop" en je hoort niets meer.
```

### 14 — Lohmann Groep (Rotterdam, loodgieter) · info@lohmannbv.nl

**Onderwerp:** Een AI-receptionist voor Lohmann, al klaargezet

```
Beste team van Lohmann Groep,

Jullie zijn 24/7 bereikbaar, maar zonder automatische bevestiging weet je nooit
hoeveel bellers alsnog afhaken. En na een klus blijft de Google-review vaak
liggen, terwijl juist die je de volgende klant oplevert.

Daarvoor is Klantkraan gebouwd: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt, meteen een afspraak
inplant en na de klus netjes om een review vraagt.

Ik heb er alvast een voor Lohmann klaargezet, met jullie diensten erin. Stel 'm
gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=lohmann

We nemen een klein aantal oprichtersklanten aan. Die betalen de eerste zes
maanden €149 per maand (excl. btw) in plaats van €299, zonder opstartkosten, en
krijgen binnen 30 dagen alles terug als het niet bevalt. Maandelijks opzegbaar.
In ruil vragen we een kort verhaal zodra hij zich bewezen heeft.

Zal ik 'm voor jullie live zetten? Binnen 48 uur staat hij op je site.

Met vriendelijke groet,
[jouw naam]
Klantkraan

--
Klantkraan is een handelsnaam van T4 Software Consulting BV · KvK 90232135
klantkraan.nl · Geen interesse? Antwoord met "stop" en je hoort niets meer.
```

### 15 — DV Dakdekkers (Amsterdam, dakdekker) · info@dvdakdekkers.nl

**Onderwerp:** Een AI-receptionist voor DV Dakdekkers, al klaargezet

```
Beste team van DV Dakdekkers,

Een perfecte 5.0 op meer dan vijftig beoordelingen, daar loop je op voor. Toch
draait er een kortingsactie, en die trekt vooral prijskopers. Sneller reageren op
serieuze aanvragen laat je op kwaliteit concurreren in plaats van op prijs.

Daarvoor is Klantkraan gebouwd: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt en meteen een afspraak of
offerte inplant.

Ik heb er alvast een voor DV Dakdekkers klaargezet, met jullie diensten erin.
Stel 'm gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=dv-dakdekkers

We nemen een klein aantal oprichtersklanten aan. Die betalen de eerste zes
maanden €149 per maand (excl. btw) in plaats van €299, zonder opstartkosten, en
krijgen binnen 30 dagen alles terug als het niet bevalt. Maandelijks opzegbaar.
In ruil vragen we een kort verhaal zodra hij zich bewezen heeft.

Zal ik 'm voor jullie live zetten? Binnen 48 uur staat hij op je site.

Met vriendelijke groet,
[jouw naam]
Klantkraan

--
Klantkraan is een handelsnaam van T4 Software Consulting BV · KvK 90232135
klantkraan.nl · Geen interesse? Antwoord met "stop" en je hoort niets meer.
```

### 16 — Dekker Installatietechniek (Gouda, loodgieter) · info@dekkerinstallatietechniek.eu

**Onderwerp:** Een AI-receptionist voor Dekker Installatietechniek, al klaargezet

```
Beste team van Dekker Installatietechniek,

Jullie storingsdienst draait 24/7, maar online is Dekker nauwelijks zichtbaar:
geen WhatsApp, geen online afspraak, weinig beoordelingen. Nieuwe klanten die
vergelijken haken daar stilletjes op af.

Daarvoor is Klantkraan gebouwd: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt, meteen een afspraak
inplant en na de klus netjes om een Google-review vraagt.

Ik heb er alvast een voor Dekker klaargezet, met jullie diensten erin. Stel 'm
gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=dekker

We nemen een klein aantal oprichtersklanten aan. Die betalen de eerste zes
maanden €149 per maand (excl. btw) in plaats van €299, zonder opstartkosten, en
krijgen binnen 30 dagen alles terug als het niet bevalt. Maandelijks opzegbaar.
In ruil vragen we een kort verhaal zodra hij zich bewezen heeft.

Zal ik 'm voor jullie live zetten? Binnen 48 uur staat hij op je site.

Met vriendelijke groet,
[jouw naam]
Klantkraan

--
Klantkraan is een handelsnaam van T4 Software Consulting BV · KvK 90232135
klantkraan.nl · Geen interesse? Antwoord met "stop" en je hoort niets meer.
```

### 17 — Warmtetechnisch Bureau Joop Buiteman (Leiden, loodgieter) · info@buiteman.nl

**Onderwerp:** Een AI-receptionist voor Buiteman, al klaargezet

```
Beste team van Buiteman,

Met 36 monteurs op de weg ronden jullie elke dag flink wat klussen af. Zonder een
vast opvolgmoment blijft de Google-review daarna liggen, en dat is precies wat
een nieuwe klant als eerste checkt.

Daarvoor is Klantkraan gebouwd: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt, meteen een afspraak
inplant en na de klus netjes om een review vraagt.

Ik heb er alvast een voor Buiteman klaargezet, met jullie diensten erin. Stel 'm
gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=buiteman

We nemen een klein aantal oprichtersklanten aan. Die betalen de eerste zes
maanden €149 per maand (excl. btw) in plaats van €299, zonder opstartkosten, en
krijgen binnen 30 dagen alles terug als het niet bevalt. Maandelijks opzegbaar.
In ruil vragen we een kort verhaal zodra hij zich bewezen heeft.

Zal ik 'm voor jullie live zetten? Binnen 48 uur staat hij op je site.

Met vriendelijke groet,
[jouw naam]
Klantkraan

--
Klantkraan is een handelsnaam van T4 Software Consulting BV · KvK 90232135
klantkraan.nl · Geen interesse? Antwoord met "stop" en je hoort niets meer.
```

### 18 — Loodgietersbedrijf Meijer (Rotterdam, loodgieter) · info@loodgietermeijer.nl

**Onderwerp:** Een AI-receptionist voor Loodgietersbedrijf Meijer, al klaargezet

```
Beste team van Loodgietersbedrijf Meijer,

120 jaar vakmanschap en tien monteurs op de weg, en toch staan er maar 23
beoordelingen op Google. Dat is niet wat jullie waard zijn, en juist die eerste
indruk is waar een nieuwe klant op afgaat.

Daarvoor is Klantkraan gebouwd: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt, meteen een afspraak
inplant en na de klus netjes om een Google-review vraagt.

Ik heb er alvast een voor Meijer klaargezet, met jullie diensten erin. Stel 'm
gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=meijer

We nemen een klein aantal oprichtersklanten aan. Die betalen de eerste zes
maanden €149 per maand (excl. btw) in plaats van €299, zonder opstartkosten, en
krijgen binnen 30 dagen alles terug als het niet bevalt. Maandelijks opzegbaar.
In ruil vragen we een kort verhaal zodra hij zich bewezen heeft.

Zal ik 'm voor jullie live zetten? Binnen 48 uur staat hij op je site.

Met vriendelijke groet,
[jouw naam]
Klantkraan

--
Klantkraan is een handelsnaam van T4 Software Consulting BV · KvK 90232135
klantkraan.nl · Geen interesse? Antwoord met "stop" en je hoort niets meer.
```

### 19 — Herfst B.V. (Amsterdam, loodgieter) · info@herfstbv.nl

**Onderwerp:** Een AI-receptionist voor Herfst, al klaargezet

```
Beste team van Herfst,

Met veertien man en meer dan vijftig jaar vakwerk hoort daar een sterkere online
reputatie bij dan er nu te zien is. Elke tevreden klant die geen beoordeling
achterlaat, is een gemiste kans om de volgende binnen te halen.

Daarvoor is Klantkraan gebouwd: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt, meteen een afspraak
inplant en na de klus netjes om een review vraagt.

Ik heb er alvast een voor Herfst klaargezet, met jullie diensten erin. Stel 'm
gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=herfst

We nemen een klein aantal oprichtersklanten aan. Die betalen de eerste zes
maanden €149 per maand (excl. btw) in plaats van €299, zonder opstartkosten, en
krijgen binnen 30 dagen alles terug als het niet bevalt. Maandelijks opzegbaar.
In ruil vragen we een kort verhaal zodra hij zich bewezen heeft.

Zal ik 'm voor jullie live zetten? Binnen 48 uur staat hij op je site.

Met vriendelijke groet,
[jouw naam]
Klantkraan

--
Klantkraan is een handelsnaam van T4 Software Consulting BV · KvK 90232135
klantkraan.nl · Geen interesse? Antwoord met "stop" en je hoort niets meer.
```

### 20 — W.J. van der Herp (Den Haag, loodgieter) · info@vanderherp.nl

**Onderwerp:** Een AI-receptionist voor Van der Herp, al klaargezet

```
Beste team van Van der Herp,

Ruim 75 jaar vakmanschap sinds 1946, en online staan er 24 beoordelingen. Dat
doet jullie staat van dienst tekort. En wie na kantoortijd belt krijgt geen
gehoor, terwijl de spoedklus dan juist binnenkomt.

Daarvoor is Klantkraan gebouwd: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt, meteen een afspraak
inplant en na de klus netjes om een review vraagt.

Ik heb er alvast een voor Van der Herp klaargezet, met jullie diensten erin.
Stel 'm gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=van-der-herp

We nemen een klein aantal oprichtersklanten aan. Die betalen de eerste zes
maanden €149 per maand (excl. btw) in plaats van €299, zonder opstartkosten, en
krijgen binnen 30 dagen alles terug als het niet bevalt. Maandelijks opzegbaar.
In ruil vragen we een kort verhaal zodra hij zich bewezen heeft.

Zal ik 'm voor jullie live zetten? Binnen 48 uur staat hij op je site.

Met vriendelijke groet,
[jouw naam]
Klantkraan

--
Klantkraan is een handelsnaam van T4 Software Consulting BV · KvK 90232135
klantkraan.nl · Geen interesse? Antwoord met "stop" en je hoort niets meer.
```

### 21 — A. Barendse & Zn. (Leiden, loodgieter) · info@barendseleiden.nl

**Onderwerp:** Een AI-receptionist voor Barendse, al klaargezet

```
Beste team van Barendse,

Op Google staan er 11 beoordelingen op jullie naam, terwijl Barendse al 65 jaar
tevreden klanten heeft. Al die stille tevreden klanten leveren nu geen nieuwe op.

Daarvoor is Klantkraan gebouwd: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt, meteen een afspraak
inplant en na de klus netjes om een Google-review vraagt.

Ik heb er alvast een voor Barendse klaargezet, met jullie diensten erin. Stel 'm
gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=barendse

We nemen een klein aantal oprichtersklanten aan. Die betalen de eerste zes
maanden €149 per maand (excl. btw) in plaats van €299, zonder opstartkosten, en
krijgen binnen 30 dagen alles terug als het niet bevalt. Maandelijks opzegbaar.
In ruil vragen we een kort verhaal zodra hij zich bewezen heeft.

Zal ik 'm voor jullie live zetten? Binnen 48 uur staat hij op je site.

Met vriendelijke groet,
[jouw naam]
Klantkraan

--
Klantkraan is een handelsnaam van T4 Software Consulting BV · KvK 90232135
klantkraan.nl · Geen interesse? Antwoord met "stop" en je hoort niets meer.
```

### 22 — T.I.B. Verkuylen (Leiden, loodgieter) · info@tib-verkuylen.nl

**Onderwerp:** Een AI-receptionist voor Verkuylen, al klaargezet

```
Beste team van Verkuylen,

Al meer dan 55 jaar actief in Leiden, en online staan er negen beoordelingen.
Dat weerspiegelt jullie vakmanschap niet. En wie na half vijf belt, krijgt geen
gehoor.

Daarvoor is Klantkraan gebouwd: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt, meteen een afspraak
inplant en na de klus netjes om een review vraagt.

Ik heb er alvast een voor Verkuylen klaargezet, met jullie diensten erin. Stel
'm gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=verkuylen

We nemen een klein aantal oprichtersklanten aan. Die betalen de eerste zes
maanden €149 per maand (excl. btw) in plaats van €299, zonder opstartkosten, en
krijgen binnen 30 dagen alles terug als het niet bevalt. Maandelijks opzegbaar.
In ruil vragen we een kort verhaal zodra hij zich bewezen heeft.

Zal ik 'm voor jullie live zetten? Binnen 48 uur staat hij op je site.

Met vriendelijke groet,
[jouw naam]
Klantkraan

--
Klantkraan is een handelsnaam van T4 Software Consulting BV · KvK 90232135
klantkraan.nl · Geen interesse? Antwoord met "stop" en je hoort niets meer.
```

### 23 — L van der Wiel (Den Haag, loodgieter) · info@lvanderwielbv.nl

**Onderwerp:** Een AI-receptionist voor Van der Wiel, al klaargezet

```
Beste team van Van der Wiel,

Meer dan 60 jaar loodgieterswerk in Den Haag, en toch staan er online maar een
handvol beoordelingen. Dat doet je vakmanschap tekort, want juist die reviews
leveren de volgende klant op.

Daarvoor is Klantkraan gebouwd: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt, meteen een afspraak
inplant en na de klus netjes om een Google-review vraagt.

Ik heb er alvast een voor Van der Wiel klaargezet, met jullie diensten erin.
Stel 'm gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=van-der-wiel

We nemen een klein aantal oprichtersklanten aan. Die betalen de eerste zes
maanden €149 per maand (excl. btw) in plaats van €299, zonder opstartkosten, en
krijgen binnen 30 dagen alles terug als het niet bevalt. Maandelijks opzegbaar.
In ruil vragen we een kort verhaal zodra hij zich bewezen heeft.

Zal ik 'm voor jullie live zetten? Binnen 48 uur staat hij op je site.

Met vriendelijke groet,
[jouw naam]
Klantkraan

--
Klantkraan is een handelsnaam van T4 Software Consulting BV · KvK 90232135
klantkraan.nl · Geen interesse? Antwoord met "stop" en je hoort niets meer.
```

---

## Opvolging — twee keer, dan stoppen

Most replies to cold B2B mail arrive on the follow-up, not the first send. Two touches, then
leave them alone. Reply in the same thread so the original mail sits underneath.

**Opvolging 1 (4 werkdagen na de eerste mail):**

```
Beste team van {bedrijf},

Korte vraag nog: heb je 'm al even geprobeerd? De link staat er nog:
{demo-link}

Je hoeft niets in te vullen, hij praat gewoon terug. Ben vooral benieuwd of hij
jullie werk goed genoeg kent.

Met vriendelijke groet,
[jouw naam]
```

**Opvolging 2, afsluitend (10 werkdagen na de eerste mail):**

```
Beste team van {bedrijf},

Ik laat het hierbij, geen zorgen. Mocht het later toch spelen dat aanvragen
buiten kantooruren blijven liggen, dan weet je me te vinden. De demo blijft
staan.

Met vriendelijke groet,
[jouw naam]
```

---

## Compliance recap

- All 23 are confirmed **BV**, so cold e-mail falls under the opt-out regime. Every mail carries
  the KvK number and a working "stop" opt-out, satisfying Telecommunicatiewet art. 11.7 without
  using the founder's name.
- Every demo **discloses that it is a digital assistant** in its greeting (EU AI Act art. 50,
  binding from 2 August 2026), baked into each config.
- No invented prices in any demo. The bot books, and says the monteur confirms the tarief on
  locatie.
- Anyone who replies "stop" goes on the suppression list immediately and gets no follow-up.

## The other 22 Randstad rows, and what unblocks them

**No findable e-mail (6)** — Folstra, Loodgieter Rotterdam B.V., Osterhoff, Vak Loodgieter,
Dakreparatie Nederland, JHF Bouw. Unblock: a contact form submission or a LinkedIn approach
instead of e-mail.

**Confirmed BV but flagged (3)** — W.A. Kuijpers (address derived from a spam-protected page, may
bounce), Vermeulen B.V. and Bol B.V. (share one website and ownership in Gouda; mailing both
`opdrachten@` and `planning@bol-vermeulen.nl` would read as spam). Unblock: verify Kuijpers'
address, and treat Vermeulen/Bol as **one** prospect with one demo config and one mail.

**Not confirmed BV (13)** — ISA Loodgieters (KvK 65267079), Hennink, Loodgieter Rotterdam 24
(94149860), Van Gelder Utrecht, Direct Loodgietersbedrijf, Loodgieter Utrecht (.com),
Loodgietersbedrijf Utrecht (96496290), Van der Wijck Daktechniek (81212755), B&G Onderhoud
(93469896), Kewodak (27330935), Haagsche Dakwerken, Dakdekkersbedrijf Leiden, Dakdekker
Amsterdam. Cold e-mail to an eenmanszaak or VOF without opt-in is forbidden (CLAUDE.md), so these
stay untouched until a KvK check confirms the rechtsvorm. LinkedIn is fine for all 13 today.

*Sources: `prospects/prospects-randstad-2026-06-08.csv`, offer from `founding-member-offer.md`
(2026-07-24), demo configs in `ai-receptionist/config/clients/`.*
