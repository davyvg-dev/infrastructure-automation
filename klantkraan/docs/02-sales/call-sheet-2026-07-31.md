# Belsheet — 31 juli 2026

Eén vel naast de telefoon. Alle prospects uit alle bronnen (Randstad-CSV, batch 3, Apollo,
warm), in belvolgorde, met per rij de pijn-hook en wat ze al van ons zagen. Aanbod en script
staan bovenaan; de rest is de lijst.

**Het aanbod (besloten 2026-07-31, niets anders aanbieden):**

1. **Eerste maand €149** i.p.v. €299 (excl. btw), geen opstartkosten, 30 dagen geld-terug,
   binnen 48 uur live. Daarna €299/mnd.
2. **Pas ná een mondelinge ja:** 6 maanden vooruit in één iDEAL-betaling = **€894 excl. btw**
   i.p.v. €1.644 — oprichterstarief het hele halfjaar. Geld-terug dekt ook de vooruitbetaling.

Cap: **tien oprichtersklanten of 30 september**, wat het eerst komt. Noem beide, houd beide.

**Vandaag geldt óók:** vanaf **zondag 2 augustus** is de AI-verordening (art. 50) afdwingbaar —
elke chatbot moet zich als AI bekendmaken. Onze demo's doen dat al. Eén zin, geen juridisch
advies: _"vanaf zondag verplicht; die van ons doet het al netjes."_

---

## Voordat je belt (10 min)

- [ ] Mollie dashboard → uitbetaling op **dagelijks** (staat standaard op wekelijks-woensdag).
- [ ] Checkout-CLI open: binnen een uur na een ja moet de betaallink de deur uit.
- [ ] Demo-tabs open voor de eerste drie namen (`demo.klantkraan.nl/?client=<slug>`).
- [ ] Log na elk gesprek: `./.venv/bin/python -m app.pipeline note <slug> "..."` (vanuit
      `ai-receptionist/`).
- [ ] Beltijden bouw: **07:30–09:00** en **16:00–17:00** vangen de eigenaar; 12:00–13:00 mijden.
- [ ] Bouwvak loopt t/m ~7–14 aug: veel voicemail is normaal. **Een ingeplande terugbelafspraak
      is winst, geen mislukking.**

## Scriptkaart

**Opener (gemaild):** "Goedemiddag, u spreekt met Davy van Klantkraan. Ik heb u [eergisteren]
een mail gestuurd — ik had voor [bedrijf] alvast een AI-receptionist klaargezet die uw
websitechat en WhatsApp opneemt. Belt het even gelegen, twee minuten?"

**Opener (koud, niet gemaild):** "Goedemiddag, Davy van Klantkraan. Ik help
[loodgieters/dakdekkers] in [regio] om gemiste telefoontjes en avond-aanvragen automatisch op
te vangen. [Pijn-hook uit de rij hieronder]. Ik heb zoiets werkend staan — mag ik u de link
appen, kost u één minuut?"

**De vraag:** "We nemen tien oprichtersklanten aan, tot 30 september. Eerste maand €149 in
plaats van €299, geen opstartkosten, 30 dagen geld-terug, binnen 48 uur live. Zal ik 'm voor u
aanzetten?"

**Prepay (alleen ná de ja):** "U kunt maandelijks betalen, of de eerste zes maanden in één
keer — dan houdt u het oprichterstarief het hele halfjaar vast: €894 in plaats van €1.644. Ik
stuur u nu een betaallinkje."

**Voicemail:** "Goedemiddag, Davy van Klantkraan. Ik heb voor [bedrijf] een AI-receptionist
klaargezet — de link staat in mijn mail. Ik probeer het morgen nog eens. Fijne dag."

**Bezwaren, één tegenzet en dan loslaten:**

- _Bouwvak/vakantie_ → "Juist dan mist u telefoontjes — hij vangt ze op terwijl u weg bent.
  Wanneer kan ik beter terugbellen?" (datum loggen)
- _Te duur / geen interesse_ → "Wat kost één gemiste klus? Eerste maand €149 en geld terug als
  het niks is. Het risico ligt bij ons."
- _Geen abonnement_ → interesse noteren, niets beloven; eenmalige koopversie is nog niet
  geproductiseerd. Terugkoppelen aan de oprichter.
- _Stuur maar een mailtje_ → "Die heeft u al — ik zet 'm nu bovenaan uw inbox, met de demolink.
  Wanneer kan ik u terugbellen?"

---

## Blok A — Warm, eerst doen (2)

| #   | Wie                                      | Kanaal           | Contact                                        | Situatie & actie                                                                                                                                                                                                        |
| --- | ---------------------------------------- | ---------------- | ---------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A1  | **Cool Global Mallorca** (airco, ES)     | WhatsApp, Engels | +34 656 86 03 98 · info@coolglobalmallorca.com | Close pack verstuurd 22 juli, sindsdien stil — opvolging is 9 dagen te laat. Demo: `?client=airco-mallorca`. Hook: 24/7 guest-emergencies buiten kantooruren. Actie: korte Engelse WhatsApp, vraag om 10 min deze week. |
| A2  | **Comfortec** (installateur, BE, Vlaams) | WhatsApp/mail    | eigen thread (config is placeholder)           | Demo live: `?client=comfortec`. Wacht op discovery-call; echte bedrijfsgegevens pas na dat gesprek in de config. Actie: opvolgbericht, discovery-call plannen.                                                          |

## Blok B — Gemaild 29–30 juli, **vandaag bellen** (11)

Mail is 1–2 dagen oud: het beste belmoment dat er bestaat. Openen met de gemaild-opener; de
kolom "mail zei" is je bruggetje. Demo per rij: `demo.klantkraan.nl/?client=<slug>`.

| #   | Bedrijf                                                | Plaats    | Tel           | Mail zei (angle)                        | Pijn-hook voor het gesprek                                                                             |
| --- | ------------------------------------------------------ | --------- | ------------- | --------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| B1  | Derwort Loodgieters B.V. (`derwort`)                   | Delft     | 015-212 50 46 | spoed na 16:30 onbemand                 | Sterk op Google (4.4/134), maar wie vrijdagavond belt krijgt niets — die klus is weg.                  |
| B2  | Smits Installaties B.V. (`smits-installaties`)         | Amsterdam | 020-694 95 50 | apart 088-storingsnummer                | Klant moet buiten kantooruren een tweede nummer onthouden; de meesten doen dat niet.                   |
| B3  | Wtb. Joop Buiteman B.V. (`buiteman`)                   | Leiden    | 071-579 40 50 | 36 monteurs, geen opvolgmoment          | Ze betálen al voor een 24/7-telefooncentrum — wij vangen ook WhatsApp en web, en bevestigen elke lead. |
| B4  | Dekker Installatietechniek B.V. (`dekker`)             | Gouda     | 0182-68 63 00 | 24/7-storingsdienst, online onzichtbaar | Storingsdienst draait, maar geen WhatsApp/online afspraak — avondleads lekken naar de buurman.         |
| B5  | P.H. Frauenfelder (`frauenfelder`)                     | Den Haag  | 070-325 44 40 | sinds 1944, na kantoortijd niemand      | Tachtig jaar naam, nul avondopvang.                                                                    |
| B6  | Duckdekker B.V. (`duckdekker`)                         | Den Haag  | 070-204 22 10 | dicht om 17:00                          | Stormschade meldt zich 's avonds en in het weekend.                                                    |
| B7  | Dak Garantie Amsterdam B.V. (`dak-garantie-amsterdam`) | Amsterdam | 020-244 39 78 | 3 vestigingen, 1 lijn                   | Lijn bezet = aanvragen uit meerdere stadsdelen tegelijk kwijt.                                         |
| B8  | MD Dak & Klusbedrijf B.V. (`md-dak`)                   | Utrecht   | 085-760 07 23 | 24/7-claim, niemand die 'm waarmaakt    | Dag-en-nacht beloven is duur om zelf te bemannen — precies wat wij overnemen.                          |
| B9  | Buddingh Dakdekkersbedrijf B.V. (`buddingh`)           | Amsterdam | 020-611 34 46 | alleen een telefoonnummer online        | Veertig jaar dakwerk, geen formulier, geen WhatsApp, geen reviews.                                     |
| B10 | AJ Dakwerken B.V. (`aj-dakwerken`)                     | Hilversum | 035-772 04 10 | review-angle: 108 reviews + showroom    | Ze investeren zichtbaar in acquisitie — zonde als een avondlead alsnog wegloopt.                       |
| B11 | A. Barendse & Zn. B.V. (`barendse`)                    | Leiden    | 071-523 32 39 | review-angle: 11 reviews in 65 jaar     | Stille tevreden klanten leveren nu geen nieuwe op; de bot vraagt na de klus om de review.              |

## Blok C — Gebounced, koud bellen (1)

| #   | Bedrijf                              | Plaats    | Tel           | Let op                                                                                                                                                                                                        |
| --- | ------------------------------------ | --------- | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| C1  | DV Dakdekkers B.V. (`dv-dakdekkers`) | Amsterdam | 085-060 93 55 | Mail is **nooit aangekomen** (hard bounce) — koude opener, niet naar de mail verwijzen. Demo staat wel live. Hook: 5.0 op 50+ reviews en een kortingsactie — ze willen groeien, maar 24u-claim zonder opvang. |

## Blok D — Nooit gemaild: BV's met alléén telefoon (8) — **koud bellen is hier het kanaal**

Deze staan niet in batch 3 omdat er **geen e-mailadres vindbaar** is (of de mail geflagd is).
Bellen mag: allemaal bevestigd BV. Geen branded demo — laat `klantkraan.nl/demo` zien en zeg
"morgen staat er een met uw naam en diensten op" (config is nul code).

| #   | Bedrijf                                                | Plaats         | Tel                           | Pijn-hook                                                                                                                     |
| --- | ------------------------------------------------------ | -------------- | ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| D1  | Folstra B.V.                                           | Rotterdam      | 010-600 11 57                 | Telefonisch bereikbaar, maar geen terugbelservice of online afspraak — en geen e-mail: elke gemiste beller is definitief weg. |
| D2  | Loodgieter Rotterdam B.V.                              | Rotterdam      | 06-261 44 204                 | Alleen een 06 — elke gemiste oproep is weg; geen WhatsApp, reviews onzichtbaar.                                               |
| D3  | Dakreparatie Nederland B.V.                            | Rotterdam      | 010-600 12 10                 | "24/7 spoedservice" op de site, geen e-mail zichtbaar — wie maakt die claim 's nachts waar?                                   |
| D4  | Vak Loodgieter B.V.                                    | Amsterdam      | 020-213 61 51                 | Geen e-mail vindbaar, geen reviews zichtbaar; sluit vroeg.                                                                    |
| D5  | Loodg.bedrijf Osterhoff B.V.                           | Utrecht        | 030-200 35 62                 | Geen e-mail, geen reviews; vermeldt vakantiesluiting — precies dán vangt de bot op.                                           |
| D6  | JHF Bouw B.V.                                          | Amsterdam      | 020-213 60 06                 | 24/7 spoedservice geclaimd, geen e-mail, geen WhatsApp.                                                                       |
| D7  | W.A. Kuijpers B.V.                                     | Delft/Rijswijk | 015-257 02 90                 | Sinds 1935, opvallend weinig reviews; (mail stond geflagd — bellen omzeilt dat).                                              |
| D8  | Vermeulen B.V. + Bol B.V. — **één prospect, één deal** | Gouda          | 0182-52 22 76 / 0182-54 10 41 | Gedeelde site en eigendom; 50-jarig jubileum, afspraakformulier maar geen directe opvang. Eén demo, één gesprek.              |

## Blok E — Batch 3, nog niet gemaild (11) — mail eerst, bel 24 u later

Demo's staan al live per slug. Cadans: vandaag 6 mailen (`python -m scripts.outreach_send
--send --limit 6`), morgen die 6 bellen; overmorgen de laatste 5 + bellen. (Koud bellen mag
ook — allemaal BV — maar mail-dan-bellen geeft het bruggetje.) De mails dragen sinds vandaag
ook de prepay-regel.

| #   | Bedrijf                                            | Plaats                | Tel           | Angle in de klaarstaande mail                                 |
| --- | -------------------------------------------------- | --------------------- | ------------- | ------------------------------------------------------------- |
| E1  | Visser & Van der Hell B.V. (`visser-van-der-hell`) | Rotterdam             | 010-413 58 63 | half-zes-beller krijgt geen gehoor                            |
| E2  | Lohmann Groep B.V. (`lohmann`)                     | Rotterdam             | 010-466 75 55 | 24/7 bereikbaar, maar geen bevestiging — afhakers onzichtbaar |
| E3  | Loodg.bedrijf Meijer B.V. (`meijer`)               | Rotterdam             | 010-412 57 00 | review-angle: 23 reviews in 120 jaar                          |
| E4  | Loodgieter Utrecht B.V. (`loodgieter-utrecht-bv`)  | Utrecht               | 030-760 11 65 | belooft direct terugbellen, geen automatische opvolging       |
| E5  | Herfst B.V. (`herfst`)                             | Amsterdam             | 020-624 21 39 | 14 man, 50+ jaar, reputatie online onzichtbaar                |
| E6  | W.J. van der Herp (`van-der-herp`)                 | Den Haag              | 070-345 25 00 | review-angle: 24 reviews sinds 1946                           |
| E7  | L. van der Wiel b.v. (`van-der-wiel`)              | Den Haag              | 070-391 46 64 | review-angle: handvol reviews in 60 jaar                      |
| E8  | Tech. Bureau W. Janssen B.V. (`w-janssen`)         | Den Haag              | 070-346 12 80 | bijna 90 jaar, na vijven geen gehoor                          |
| E9  | Valkenburg Loodgieters (`valkenburg`)              | Delft                 | 015-364 61 70 | open 9:00–12:30/13:30–17:00 — drie gaten per dag              |
| E10 | T.I.B. Verkuylen bv (`verkuylen`)                  | Leiden                | 071-522 37 67 | review-angle: 9 reviews in 55 jaar                            |
| E11 | VDP Dakbedekking B.V. (`vdp-dakbedekking`)         | Rotterdam (Hoogvliet) | 010-766 00 28 | telefoon "alleen voor informatie, geen offertes"              |

## Blok F — Eerst KvK-check (5 min p/st), dán pas bellen

Cold bellen naar een eenmanszaak/VOF valt sinds 2021 onder het opt-in-regime
(Telecommunicatiewet) — zelfde logica als onze e-mailregel. **Rechtsvorm eerst bevestigen.**

**Waarschijnlijk BV (check en bel):** ISA Loodgieters A'dam (KvK 65267079, 020-688 56 29 —
322×4.8 reviews, geen online afspraak) · Hennink Den Haag (0900-0105 — score 6.8, onder
branchemaat) · Van der Wijck Daktechniek Utrecht (KvK 81212755, 085-401 31 67 — 24/7-claim) ·
B&G Onderhoud Utrecht (KvK 93469896, 06-81 61 28 70) · Kewodak Alphen a/d Rijn (KvK 27330935,
0172-43 83 32 — 40+ jaar, geen e-mail op site).

**Onbekend, mogelijk eenmanszaak — NIET koud bellen tot KvK anders zegt (LinkedIn mag wel):**
Loodgieter Rotterdam 24 (KvK 94149860) · Van Gelder Utrecht · Direct Loodgietersbedrijf ·
Loodgieter Utrecht (.com) · Loodgietersbedrijf Utrecht (KvK 96496290) · Haagsche Dakwerken ·
Dakdekkersbedrijf Leiden · Dakdekker Amsterdam.

## Blok G — Apollo-export (113 contacten) — zo werk je 'm

Persoonsniveau, rechtsvorm grotendeels onbevestigd, veel ZZP → **standaard LinkedIn-manual**
(wave 1: 36 connects verstuurd 27 juli; volgende wave niet vóór 3 aug). Drie uitzonderingen:

**G1 — Kantoornummers van B.V.'s: koud bellen mag.** Bel de zaak, vraag naar de eigenaar — de
genoemde persoon is vaak een monteur; **nooit** het 06 van een monteur koud bellen.

| Bedrijf                           | Tel (kantoor)   | Let op                  |
| --------------------------------- | --------------- | ----------------------- |
| Installatiebedrijf ter Beek B.V.  | +31 33 298 0145 |                         |
| Knol Installatie Techniek B.V.    | +31 18 046 2798 |                         |
| L. Root B.V. (Amsterdam)          | +31 20 613 4652 |                         |
| LKS Installatietechniek BV        | +31 49 344 0144 |                         |
| JJansen BV                        | +31 16 145 6880 |                         |
| Installatie Mij. H.Ek. B.V.       | +31 73 649 6400 |                         |
| Technisch Totaal Beheer Plus B.V. | +31 85 049 7600 |                         |
| Installatiebedrijf Gijsbertsen    | 0341-35138      | rechtsvorm even checken |

**G2 — Eigenaren met e-mail: mail/LinkedIn, geen koude call nodig.** Silvain Maliepaard (DGA,
Maliepaard Loodgieters B.V., silvain@maliepaard.nl) · Marco (directeur, Installatiebedrijf
Bek, marco@bekbv.nl). Entity eerst bevestigen vóór cold e-mail (BV-filter), of gewoon via de
bestaande LinkedIn-connect.

**G3 — Overslaan (verkeerd ICP):** grote installatiegroepen — Giesbers, Lomans, Equans,
ToekomstGroep, Van der Velden, Hanab, Modderkolk, Bokhorst, DUTECO. Die hebben kantoorpersoneel;
onze pitch is voor de eigenaar die zelf op het dak staat. De rest van tier A/B (ZZP'ers,
monteurs zonder kanaal): LinkedIn-wave van 3 aug.

---

## Na elk gesprek

1. Loggen: `note <slug> "..."` + bij afspraak een datum.
2. **Ja gehoord? Betaallink binnen het uur.** €149-link, of €894-link bij prepay-ja
   (excl. btw; Mollie brut eert de btw-opslag automatisch).
3. Reply of interesse per mail → binnen het uur antwoorden (grootste hefboom op close rate).
4. "Stop" of boos → suppressielijst, klaar, volgende.

_Bronnen: `prospects/prospects-randstad-2026-06-08.csv` · `outreach-batch-3-2026-07-29.md` ·
`linkedin-prospects.md` (Apollo) · `ai-receptionist/build/outreach/sent.json` (ledger) ·
`data/pipeline/_.yaml`· aanbod:`founding-member-offer.md` (2026-07-31).\*
