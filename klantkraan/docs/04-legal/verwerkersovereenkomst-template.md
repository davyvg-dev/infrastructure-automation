# Verwerkersovereenkomst (DPA) — invulbare template

> **Internal note (English) — not part of the signed text.**
> Canonical, signable NL processing agreement (AVG art. 28). Supersedes the planning skeleton in
> `dpa-outline.md`, which was built on the retired voice stack (Synthflow/ElevenLabs/CM.com,
> audio recordings). This template reflects the **text-first** reality: WhatsApp + website chat,
> Claude for the answers, Twilio for transport, Hetzner for hosting.
>
> **Sub-processor transfer bases verified 2026-07-24 (re-check annually against the DPF list):**
> Anthropic — EU-US Data Privacy Framework (active 2026-03) + SCCs fallback; direct API stores in
> the US, so message content is a lawful US transfer, NOT EU-resident. Twilio — EU-US DPF + BCRs +
> SCCs. Hetzner — EU (DE/FI), no transfer = the honest "EU hosting" claim applies to the
> storage/hosting layer only. Do not tell a client "niets verlaat de EER."
>
> **This is a template, not legal advice.** Have a Dutch jurist review it once before the first
> client signature; after that it is fill-in-the-blanks. Replace every `[...]` placeholder. Client
> signs this alongside the offer/MSA, *before* go-live — no signed DPA = unlawful processing under
> art. 28(3) and both parties are liable (AP guidance).

---

# Verwerkersovereenkomst

**De ondergetekenden:**

**1. [Naam klantbedrijf]**, gevestigd te [plaats], KvK-nummer [KvK], ten deze rechtsgeldig
vertegenwoordigd door [naam], hierna: **"Verwerkingsverantwoordelijke"**;

**en**

**2. T4 Software Consulting B.V.**, handelend onder de naam **Klantkraan**, gevestigd te
[plaats], KvK-nummer 90232135, hierna: **"Verwerker"**;

hierna gezamenlijk de "Partijen" en ieder afzonderlijk een "Partij";

**overwegende dat:**

- Verwerker voor Verwerkingsverantwoordelijke een digitale receptionist levert die inkomende
  berichten (websitechat, WhatsApp en verwante kanalen) namens Verwerkingsverantwoordelijke
  beantwoordt, afspraken vastlegt en leads doorgeeft (de "Diensten");
- Verwerker bij het uitvoeren van de Diensten persoonsgegevens verwerkt waarvoor
  Verwerkingsverantwoordelijke de verwerkingsverantwoordelijke is in de zin van de AVG;
- Partijen op grond van artikel 28 AVG hun afspraken over deze verwerking schriftelijk vastleggen
  in deze verwerkersovereenkomst (de "Overeenkomst");

**komen het volgende overeen:**

## Artikel 1 — Definities

De begrippen "persoonsgegevens", "verwerking", "betrokkene", "inbreuk in verband met
persoonsgegevens" (datalek), "subverwerker" en "toezichthoudende autoriteit" hebben de betekenis
uit artikel 4 AVG. "AVG" is Verordening (EU) 2016/679. "AP" is de Autoriteit Persoonsgegevens.

## Artikel 2 — Onderwerp, aard, doel en duur

1. Onderwerp, aard, doel, categorieën betrokkenen en soorten persoonsgegevens van de verwerking
   zijn beschreven in **Bijlage I**.
2. Verwerker verwerkt de persoonsgegevens uitsluitend voor de uitvoering van de Diensten en niet
   voor eigen doeleinden.
3. Deze Overeenkomst geldt zolang Verwerker persoonsgegevens verwerkt in het kader van de
   Diensten, en eindigt niet eerder dan nadat de verplichtingen uit artikel 11 (verwijdering) zijn
   nagekomen.

## Artikel 3 — Instructies (art. 28 lid 3 sub a)

1. Verwerker verwerkt de persoonsgegevens uitsluitend op basis van schriftelijke, gedocumenteerde
   instructies van Verwerkingsverantwoordelijke. Deze Overeenkomst, de configuratie van de
   receptionist en de reguliere aanwijzingen van Verwerkingsverantwoordelijke gelden als zulke
   instructies.
2. Verwerker stelt Verwerkingsverantwoordelijke onverwijld op de hoogte indien een instructie naar
   het oordeel van Verwerker in strijd is met de AVG of andere toepasselijke gegevensbescherming.
3. Verwerker geeft de digitale assistent de vaste instructie geen prijzen, afspraaktijden of advies
   te verzinnen; de assistent bevestigt uitsluitend informatie en tijdsloten die
   Verwerkingsverantwoordelijke zelf heeft ingesteld of die een gekoppelde agenda teruggeeft.

## Artikel 4 — Vertrouwelijkheid (art. 28 lid 3 sub b)

Verwerker verbindt alle personen die onder zijn gezag persoonsgegevens verwerken — werknemers en
ingeschakelde derden — tot geheimhouding, hetzij via een geheimhoudingsbeding, hetzij op grond van
een passende wettelijke geheimhoudingsplicht.

## Artikel 5 — Beveiliging (art. 28 lid 3 sub c, art. 32)

1. Verwerker treft passende technische en organisatorische maatregelen om een op het risico
   afgestemd beveiligingsniveau te waarborgen. De actuele maatregelen staan in **Bijlage II**.
2. Verwerker mag maatregelen actualiseren zolang het beveiligingsniveau daardoor niet daalt.

## Artikel 6 — Subverwerkers (art. 28 lid 2 en lid 4)

1. Verwerkingsverantwoordelijke verleent hierbij algemene toestemming voor het inschakelen van de
   subverwerkers in **Bijlage III**.
2. Verwerker informeert Verwerkingsverantwoordelijke ten minste **30 dagen** vooraf schriftelijk
   over de toevoeging of vervanging van een subverwerker. Verwerkingsverantwoordelijke kan binnen
   die termijn op redelijke gronden bezwaar maken; komen Partijen er niet uit, dan mag
   Verwerkingsverantwoordelijke de betreffende Dienst opzeggen.
3. Verwerker legt elke subverwerker bij overeenkomst dezelfde gegevensbeschermingsverplichtingen op
   als in deze Overeenkomst, en blijft jegens Verwerkingsverantwoordelijke volledig aansprakelijk
   voor het nakomen daarvan door de subverwerker.

## Artikel 7 — Doorgifte buiten de EER (Hoofdstuk V AVG)

1. Verwerker geeft persoonsgegevens uitsluitend buiten de Europese Economische Ruimte door indien
   daarvoor een geldig doorgiftemechanisme bestaat: een adequaatheidsbesluit (waaronder het
   EU-US Data Privacy Framework), standaardcontractbepalingen (SCC's) of bindende
   bedrijfsvoorschriften (BCR's).
2. Het doorgiftemechanisme per subverwerker staat in **Bijlage III**. De primaire opslag van
   conversatie- en leadgegevens vindt plaats binnen de EER (Hetzner, DE/FI). Berichtinhoud wordt
   voor het genereren van antwoorden verwerkt door Anthropic in de Verenigde Staten op grond van
   het EU-US Data Privacy Framework, aangevuld met SCC's.

## Artikel 8 — Bijstand bij rechten van betrokkenen (art. 28 lid 3 sub e)

1. Verwerker verleent Verwerkingsverantwoordelijke, rekening houdend met de aard van de verwerking,
   redelijke bijstand bij verzoeken van betrokkenen (art. 12–23 AVG: inzage, rectificatie, wissing,
   beperking, bezwaar, overdraagbaarheid).
2. Ontvangt Verwerker rechtstreeks een verzoek van een betrokkene, dan geeft Verwerker dit
   onverwijld door aan Verwerkingsverantwoordelijke en beantwoordt het niet zelf, tenzij daartoe
   wettelijk verplicht.
3. Bijstand binnen redelijke termijn; buitensporige of herhaalde verzoeken mag Verwerker tegen
   [uurtarief, bv. €75/uur] in rekening brengen.

## Artikel 9 — Datalekken (art. 28 lid 3 sub f, art. 33–34)

1. Verwerker meldt een inbreuk in verband met persoonsgegevens onverwijld en uiterlijk binnen
   **48 uur** na ontdekking schriftelijk aan Verwerkingsverantwoordelijke.
2. De melding bevat ten minste: de aard van de inbreuk, de betrokken categorieën en het geschatte
   aantal betrokkenen en records, de waarschijnlijke gevolgen, de getroffen en voorgestelde
   maatregelen, en een contactpunt.
3. Verwerker verleent redelijke bijstand bij de eventuele meldplicht van
   Verwerkingsverantwoordelijke aan de AP (72 uur) en aan betrokkenen. De beoordeling of gemeld
   moet worden aan de AP ligt bij Verwerkingsverantwoordelijke.

## Artikel 10 — DPIA en voorafgaande raadpleging (art. 35–36)

Verwerker verleent Verwerkingsverantwoordelijke redelijke bijstand en informatie voor een
eventuele gegevensbeschermingseffectbeoordeling (DPIA) en een voorafgaande raadpleging van de AP.

## Artikel 11 — Bewaring, teruggave en verwijdering (art. 28 lid 3 sub g)

1. Verwerker bewaart conversatie- en leadgegevens niet langer dan nodig, met een standaardtermijn
   van **[bewaartermijn, standaard 90 dagen]** na afronding van het betreffende gesprek of de
   afspraak, tenzij Partijen schriftelijk een kortere of langere termijn afspreken. Korter is beter
   voor dataminimalisatie.
2. Bij beëindiging van de Diensten verstrekt Verwerker op verzoek binnen **30 dagen** een export in
   een gangbaar formaat (JSON/CSV) en verwijdert daarna alle persoonsgegevens binnen **30 dagen**,
   inclusief bij subverwerkers, tenzij een wettelijke bewaarplicht anders vereist.
3. Verwerker bevestigt de verwijdering op verzoek schriftelijk.

## Artikel 12 — Audit en informatieplicht (art. 28 lid 3 sub h)

1. Verwerker stelt Verwerkingsverantwoordelijke alle informatie ter beschikking die nodig is om de
   naleving van artikel 28 aan te tonen.
2. Verwerkingsverantwoordelijke mag maximaal **1× per jaar** — en daarnaast bij een concreet
   vermoeden van niet-naleving — een audit (laten) uitvoeren, na **30 dagen** schriftelijke
   aankondiging, tijdens kantooruren, zonder verstoring van de bedrijfsvoering en onder
   geheimhouding. Kosten komen voor Verwerkingsverantwoordelijke, tenzij een wezenlijke
   niet-naleving wordt vastgesteld.

## Artikel 13 — Aansprakelijkheid

1. De aansprakelijkheid van Verwerker onder deze Overeenkomst is beperkt tot het totaal van de
   vergoedingen die Verwerkingsverantwoordelijke in de **12 maanden** voorafgaand aan de
   schadeveroorzakende gebeurtenis aan Verwerker heeft betaald.
2. De beperking geldt niet bij opzet of bewuste roekeloosheid van Verwerker, en laat de
   rechtstreekse aanspraken van betrokkenen op grond van artikel 82 AVG onverlet — die kunnen niet
   contractueel worden uitgesloten.

## Artikel 14 — Duur en beëindiging

Deze Overeenkomst treedt in werking bij ondertekening en eindigt gelijktijdig met de
hoofdovereenkomst voor de Diensten, met inachtneming van de verplichtingen uit artikel 11. Bepaling
die naar hun aard doorwerken (geheimhouding, aansprakelijkheid) blijven daarna gelden.

## Artikel 15 — Toepasselijk recht en forum

Op deze Overeenkomst is Nederlands recht van toepassing. Geschillen worden voorgelegd aan de
bevoegde rechter te [Rechtbank, bv. Den Haag].

**Aldus overeengekomen en in tweevoud ondertekend:**

| Verwerkingsverantwoordelijke | Verwerker (T4 Software Consulting B.V. / Klantkraan) |
|---|---|
| Naam: [ ] | Naam: [ ] |
| Functie: [ ] | Functie: [ ] |
| Datum: [ ] | Datum: [ ] |
| Handtekening: | Handtekening: |

---

## Bijlage I — Verwerkingsdetails

| | |
|---|---|
| **Onderwerp** | Het beantwoorden van inkomende berichten en het vastleggen van afspraken en leads namens Verwerkingsverantwoordelijke |
| **Aard van de verwerking** | Ontvangen, opslaan, verwerken met een taalmodel, en doorsturen van tekstberichten; vastleggen van afspraak- en leadgegevens |
| **Doel** | 24/7 bereikbaarheid: klantvragen beantwoorden, afspraken inplannen, terugbelverzoeken en leads doorgeven |
| **Duur** | Voor de looptijd van de Diensten + de bewaartermijn van artikel 11 |
| **Categorieën betrokkenen** | Klanten en prospects van Verwerkingsverantwoordelijke die contact opnemen |

**Soorten persoonsgegevens:**

| Categorie | Voorbeelden |
|---|---|
| Identificatiegegevens | Naam, telefoon-/WhatsApp-nummer, soms e-mail |
| Adres-/locatiegegevens | Adres of postcode van de klus (voor de afspraak) |
| Communicatiegegevens | Inhoud van de tekstberichten (de vraag/klus), afspraakgegevens |
| Overige door de klant genoemde gegevens | Wat de klant zelf in het gesprek deelt |

Geen doelverwerking van bijzondere categorieën, BSN of strafrechtelijke gegevens. Een klant kan
onbedoeld bijzondere gegevens (bv. over gezondheid) in vrije tekst noemen; deze worden niet actief
uitgevraagd en niet apart verwerkt. **Geen** audio-opnames of spraaktranscripties (tekst-first).

## Bijlage II — Technische en organisatorische maatregelen (art. 32)

- **EU-hosting** van applicatie en database (Hetzner, Duitsland/Finland).
- **Versleuteling** in transit (TLS 1.3) en at-rest.
- **Isolatie per klant** (aparte configuratie / `client_id`); geen vermenging van klantdata.
- **Toegangsbeheer**: minimale toegang op need-to-know, versleuteld wachtwoordbeheer, 2FA.
- **Back-ups**: dagelijks, versleuteld.
- **Logging en monitoring**, inclusief uitval-bewaking met terugval op leadopname ("we bellen je
  terug") in plaats van stilte of verzonnen antwoorden.
- **AI-specifiek**: prompts worden door Anthropic standaard uitgesloten van modeltraining
  (commerciële API-voorwaarden); de assistent verzint geen prijzen, tijden of advies (art. 3 lid 3);
  in elke begroeting wordt vermeld dat het om een digitale assistent gaat (EU AI Act art. 50).
- **Geheimhouding** van alle personen die gegevens verwerken.
- **Incident-responsprocedure** met melding binnen 48 uur (art. 9).

## Bijlage III — Subverwerkers

| Subverwerker | Rol | Verwerkte gegevens | Locatie | Doorgiftemechanisme | DPA |
|---|---|---|---|---|---|
| **Anthropic PBC** | Taalmodel (Claude) — genereert de antwoorden | Berichtinhoud + gesprekscontext | VS | EU-US Data Privacy Framework + SCC's | anthropic.com/legal/commercial-terms (incl. DPA) |
| **Twilio Inc.** | WhatsApp-/SMS-transport (BSP) | Telefoonnummer + berichtinhoud | VS + EER-regio's | EU-US DPF + BCR's + SCC's | twilio.com/en-us/legal/data-protection-addendum |
| **Hetzner Online GmbH** | Hosting van applicatie + database (primaire opslag) | Alle conversatie- en leadgegevens | EER (DE/FI) | Binnen EER — geen doorgifte | hetzner.com/AV/DPA_en.pdf |

**Per klant toe te voegen (indien van toepassing), vóór activering en met kennisgeving als in
artikel 6:**

- Een **agendaprovider** (bv. Google Calendar of Cal.com) zodra afsprakenkoppeling actief is —
  verwerkt naam en afspraakgegevens.
- **Telegram** (Telegram FZ-LLC) uitsluitend indien Verwerkingsverantwoordelijke kiest voor
  leadnotificaties via Telegram — verwerkt naam, nummer en de vraag.

De actuele subverwerkerslijst is deze Bijlage III; wijzigingen worden conform artikel 6 lid 2
30 dagen vooraf gemeld.

---

## Bronnen (voor onderhoud van deze template)

- AVG art. 28 (NL): https://www.privacy-regulation.eu/nl/artikel-28-verwerker-EU-AVG.htm
- AP — verwerkersovereenkomst: https://www.autoriteitpersoonsgegevens.nl/en/themes/basic-gdpr/gdpr-basics/processing-agreement
- EU-US Data Privacy Framework (certificatielijst): https://www.dataprivacyframework.gov/list
- Anthropic commerciële voorwaarden + DPA: https://www.anthropic.com/legal/commercial-terms
- Twilio DPA: https://www.twilio.com/en-us/legal/data-protection-addendum
- Hetzner AV/DPA: https://www.hetzner.com/AV/DPA_en.pdf
