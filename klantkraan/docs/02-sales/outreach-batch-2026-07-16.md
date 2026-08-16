# Outreach batch — 10 branded demos, ready to send (2026-07-16)

> **SUPERSEDED — do not send.** These mails pitch the free 14-day pilot at €299/mnd, retired by
> `founding-member-offer.md` on 2026-07-24. The same 10 prospects are rewritten onto the
> founding-member offer in `outreach-batch-3-2026-07-29.md`. Kept for the demo links and the
> LinkedIn track below.

The first concrete outreach wave of the 28-day sprint. Ten confirmed-BV prospects from
`prospects/prospects-randstad-2026-06-08.csv`, each with:

1. a **branded, working demo** at `?client=<slug>` (config in `ai-receptionist/config/clients/`,
   verified loading via `selftest config`), and
2. a **ready-to-send cold email** below — personalised with that prospect's own pain, then the
   pilot offer from `pilot-offer.md`.

All ten are confirmed **BV** (opt-out regime → cold email is compliant; footer carries the KvK,
per art. 11.7 — no founder name needed). None are the `likely-BV`/`unknown` rows; those stay
untouched until KvK-verified (CLAUDE.md).

---

## Before you send — 3 steps to make every demo link live (~15 min, one-time)

The links below use `demo.klantkraan.nl`, which needs pointing at the ops server. A raw
`sslip.io` link in a cold email reads as a scam and kills conversion — don't skip this.

1. **DNS (founder, Cloudflare):** add an **A record** `demo` → `168.119.173.25`, set to
   **DNS only / grey cloud** (not proxied — Caddy provisions its own Let's Encrypt cert; the
   orange-cloud proxy would break that challenge).
2. **Caddy vhost:** already wired — `ops/hetzner/Caddyfile.template` now serves
   `demo.klantkraan.nl` alongside the sslip host (committed in this batch).
3. **Deploy:** `ops/hetzner/deploy.sh 168.119.173.25` — rsyncs the 10 new configs + the Caddyfile,
   restarts the service, Caddy fetches the cert. (Say the word and I'll run it.)

After that, every `https://demo.klantkraan.nl/?client=<slug>` link works. Bare
`demo.klantkraan.nl` shows the showcase; `?client=…` shows that prospect's own branded bot.

**Fallback that works today (before DNS):** `https://demo-168-119-173-25.sslip.io/?client=<slug>`
— fine to open yourself to sanity-check a demo, or to record a 30-sec screen clip to send
instead of a link (best for a cold first touch anyway).

---

## The 10 at a glance

| #   | Bedrijf                                       | Stad      | Vak        | E-mail                      | Demo link                                                |
| --- | --------------------------------------------- | --------- | ---------- | --------------------------- | -------------------------------------------------------- |
| 1   | Visser & Van der Hell Loodgietersbedrijf B.V. | Rotterdam | loodgieter | info@visservanderhell.nl    | https://demo.klantkraan.nl/?client=visser-van-der-hell   |
| 2   | Lohmann Groep B.V.                            | Rotterdam | loodgieter | info@lohmannbv.nl           | https://demo.klantkraan.nl/?client=lohmann               |
| 3   | Loodgieter Utrecht B.V.                       | Utrecht   | loodgieter | info@loodgieterutrechtbv.nl | https://demo.klantkraan.nl/?client=loodgieter-utrecht-bv |
| 4   | Herfst B.V.                                   | Amsterdam | loodgieter | info@herfstbv.nl            | https://demo.klantkraan.nl/?client=herfst                |
| 5   | W.J. van der Herp B.V.                        | Den Haag  | loodgieter | info@vanderherp.nl          | https://demo.klantkraan.nl/?client=van-der-herp          |
| 6   | Derwort Loodgieters B.V.                      | Delft     | loodgieter | info@derwort.nu             | https://demo.klantkraan.nl/?client=derwort               |
| 7   | T.I.B. Verkuylen B.V.                         | Leiden    | loodgieter | info@tib-verkuylen.nl       | https://demo.klantkraan.nl/?client=verkuylen             |
| 8   | Duckdekker B.V.                               | Den Haag  | dakdekker  | info@duckdekker.nl          | https://demo.klantkraan.nl/?client=duckdekker            |
| 9   | AJ Dakwerken B.V.                             | Hilversum | dakdekker  | info@ajdakwerken.nl         | https://demo.klantkraan.nl/?client=aj-dakwerken          |
| 10  | VDP Dakbedekking B.V.                         | Rotterdam | dakdekker  | info@vdpdakbedekking.nl     | https://demo.klantkraan.nl/?client=vdp-dakbedekking      |

**How to work it:** ~30 min/day. Send 3–4 cold emails, log replies, and run the LinkedIn track in
parallel for the same names. Replace `[jouw naam]` with your own signature. Reply to any interest
within the hour — speed is the single biggest lever on close rate.

---

## Cold emails — ready to paste and send

Each is complete. Subject + body + compliant footer. Register matches the sanctioned template in
`demo-outreach.md` (`je`/`jouw`, short, pain → demo → pilot → one ask).

### 1 — Visser & Van der Hell (Rotterdam, loodgieter) · info@visservanderhell.nl

**Onderwerp:** Een AI-receptionist voor Visser & Van der Hell — 14 dagen gratis

```
Beste team van Visser & Van der Hell,

Een klant die om half zes belt en geen gehoor krijgt, zoekt online verder en
belt de volgende loodgieter. Juist buiten kantooruren — als een lekkage niet
kan wachten — gaat er zo omzet langs je heen.

Daar bouwden we Klantkraan voor: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen over je diensten beantwoordt en
meteen een afspraak inplant.

Ik heb er alvast eentje voor Visser & Van der Hell klaargezet, met jullie
diensten erin. Stel 'm gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=visser-van-der-hell

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

### 2 — Lohmann Groep (Rotterdam, loodgieter) · info@lohmannbv.nl

**Onderwerp:** Een AI-receptionist voor Lohmann — 14 dagen gratis

```
Beste team van Lohmann Groep,

Jullie zijn 24/7 bereikbaar, maar zonder automatische bevestiging of opvolging
weet je nooit hoeveel bellers alsnog afhaken. En na een klus blijft de
Google-review vaak liggen — terwijl juist die je de volgende klant oplevert.

Daar bouwden we Klantkraan voor: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt en meteen een afspraak
inplant.

Ik heb er alvast eentje voor Lohmann klaargezet, met jullie diensten erin. Stel
'm gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=lohmann

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

### 3 — Loodgieter Utrecht B.V. (Utrecht, loodgieter) · info@loodgieterutrechtbv.nl

**Onderwerp:** Een AI-receptionist voor Loodgieter Utrecht — 14 dagen gratis

```
Beste team van Loodgieter Utrecht,

Je belooft klanten dat je direct terugbelt, maar zonder opvolging valt er altijd
wel een oproep tussen wal en schip. Eén gemiste beller op een drukke dag is zo
een misgelopen klus.

Daar bouwden we Klantkraan voor: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt en meteen een afspraak
inplant.

Ik heb er alvast eentje voor Loodgieter Utrecht klaargezet, met jullie diensten
erin. Stel 'm gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=loodgieter-utrecht-bv

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

### 4 — Herfst B.V. (Amsterdam, loodgieter) · info@herfstbv.nl

**Onderwerp:** Een AI-receptionist voor Herfst — 14 dagen gratis

```
Beste team van Herfst,

Met veertien man en meer dan vijftig jaar vakwerk hoort daar een sterkere online
reputatie bij dan nu te zien is. Elke tevreden klant die geen review achterlaat,
is een gemiste kans om de volgende binnen te halen.

Daar bouwden we Klantkraan voor: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt en meteen een afspraak
inplant — en na de klus netjes om een review kan vragen.

Ik heb er alvast eentje voor Herfst klaargezet, met jullie diensten erin. Stel
'm gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=herfst

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

### 5 — W.J. van der Herp B.V. (Den Haag, loodgieter) · info@vanderherp.nl

**Onderwerp:** Een AI-receptionist voor Van der Herp — 14 dagen gratis

```
Beste team van Van der Herp,

Ruim 75 jaar vakmanschap sinds 1946, maar online staan er maar een handvol
beoordelingen — dat doet jullie staat van dienst tekort. En wie na kantoortijd
belt, krijgt geen gehoor terwijl de klus dan wél binnenkomt.

Daar bouwden we Klantkraan voor: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt en meteen een afspraak
inplant.

Ik heb er alvast eentje voor Van der Herp klaargezet, met jullie diensten erin.
Stel 'm gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=van-der-herp

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

### 6 — Derwort Loodgieters B.V. (Delft, loodgieter) · info@derwort.nu

**Onderwerp:** Een AI-receptionist voor Derwort — 14 dagen gratis

```
Beste team van Derwort,

Jullie staan sterk op Google, maar voor spoed buiten kantoortijd (na 16:30) is er
geen zichtbare opvang. Een gemiste oproep op vrijdagmiddag is een klant die naar
de concurrent gaat.

Daar bouwden we Klantkraan voor: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt en meteen een afspraak
inplant.

Ik heb er alvast eentje voor Derwort klaargezet, met jullie diensten erin. Stel
'm gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=derwort

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

### 7 — T.I.B. Verkuylen B.V. (Leiden, loodgieter) · info@tib-verkuylen.nl

**Onderwerp:** Een AI-receptionist voor Verkuylen — 14 dagen gratis

```
Beste team van Verkuylen,

Al meer dan 55 jaar actief in Leiden, maar online staan er maar een paar
beoordelingen — dat weerspiegelt jullie vakmanschap niet. En wie na half vijf
belt, krijgt geen gehoor.

Daar bouwden we Klantkraan voor: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt en meteen een afspraak
inplant.

Ik heb er alvast eentje voor Verkuylen klaargezet, met jullie diensten erin.
Stel 'm gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=verkuylen

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

### 8 — Duckdekker B.V. (Den Haag, dakdekker) · info@duckdekker.nl

**Onderwerp:** Een AI-receptionist voor Duckdekker — 14 dagen gratis

```
Beste team van Duckdekker,

Jullie sluiten om 17:00, maar stormschade en daklekkages bellen ook 's avonds en
in het weekend. Zonder opvang gaat die spoedklus naar een dakdekker die wél
opneemt — of je draait er zelf een dure nachtdienst voor.

Daar bouwden we Klantkraan voor: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt en meteen een afspraak of
offerte inplant.

Ik heb er alvast eentje voor Duckdekker klaargezet, met jullie diensten erin.
Stel 'm gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=duckdekker

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

### 9 — AJ Dakwerken B.V. (Hilversum, dakdekker) · info@ajdakwerken.nl

**Onderwerp:** Een AI-receptionist voor AJ Dakwerken — 14 dagen gratis

```
Beste team van AJ Dakwerken,

Met 108 reviews en een eigen showroom hebben jullie flink in acquisitie
geïnvesteerd. Des te zonde als een beller buiten kantooruren geen gehoor krijgt
en alsnog naar de concurrent gaat.

Daar bouwden we Klantkraan voor: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt en meteen een afspraak of
offerte inplant.

Ik heb er alvast eentje voor AJ Dakwerken klaargezet, met jullie diensten erin.
Stel 'm gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=aj-dakwerken

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

### 10 — VDP Dakbedekking B.V. (Rotterdam, dakdekker) · info@vdpdakbedekking.nl

**Onderwerp:** Een AI-receptionist voor VDP Dakbedekking — 14 dagen gratis

```
Beste team van VDP Dakbedekking,

Op jullie site staat dat je telefonisch geen offertes opneemt — maar wie 's
avonds belt na een daklekkage wil juist meteen geholpen worden. Die beller
krijgt nu niets terug en gaat verder zoeken.

Daar bouwden we Klantkraan voor: een AI-receptionist die 24/7 in het Nederlands
je websitechat en WhatsApp opneemt, vragen beantwoordt en meteen een afspraak of
offerte inplant.

Ik heb er alvast eentje voor VDP Dakbedekking klaargezet, met jullie diensten
erin. Stel 'm gerust een lastige vraag, hij houdt stand:
https://demo.klantkraan.nl/?client=vdp-dakbedekking

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

## LinkedIn track (parallel, same 10 names)

Warmer than cold email, and compliant even for sole traders: connect + a genuine question first,
demo only on a reply. Full sequence in `demo-outreach.md §1`. Short version:

- **T1** — connection request, no note.
- **T2** (day 1 after accept, a question not a pitch): _"Dank voor de connectie. Korte vraag: nemen
  jullie zelf de telefoon op buiten kantooruren, of loopt dat via voicemail? Ik bouw
  AI-receptionisten voor installatie- en dakbedrijven en ben benieuwd hoe jij het oplost."_
- **T3** (only on any interested reply → send their demo): _"Ik heb er even eentje voor
  {bedrijf} klaargezet — met jullie diensten erin: {demo-link uit de tabel}. Bevalt het? Dan zet
  ik 'm 14 dagen gratis en volledig ingericht voor je live."_
- **T4** (day 12, no reply): one-line breakup, demo link stays up.

---

## Compliance recap

- All 10 are confirmed **BV** → cold email allowed under the opt-out regime; every email carries
  the KvK + a working "stop" opt-out (art. 11.7 satisfied without the founder's name).
- The demo **discloses it's a digital assistant** in its greeting (EU AI Act art. 50) — baked into
  every config.
- No invented prices anywhere — the bot books and says the monteur confirms the tarief on locatie.
- The `likely-BV`/`unknown` prospects in the CSV are **not** in this batch; KvK-verify them before
  any cold approach.

```

```
