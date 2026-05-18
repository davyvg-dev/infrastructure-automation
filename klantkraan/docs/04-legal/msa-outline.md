# MSA / Algemene Voorwaarden — Outline

> Not a contract — an outline for a Dutch lawyer to render into a final document. Hire ICTRecht, Considerati or a comparable B2B SaaS firm for a one-pass review (~€1,500–2,500).

## Why these clauses, and why now

NL B2B has specific quirks: `art. 6:233(a) BW` on *onredelijk bezwarend*, the Hoge Raad case-law on `aansprakelijkheidsbeperking`, the soft opt-in regime changing on 1 July 2026 — these all affect how a stock SaaS MSA from a US template translates. The outline below is rendered against those constraints.

## Sections (Dutch B2B SaaS MSA)

### 1. Definities
- Klantkraan / Opdrachtnemer
- Klant / Opdrachtgever
- Dienst (refer to current Service Description on klantkraan.nl/dienst)
- Persoonsgegevens (verwijst naar AVG art. 4)
- Verwerkersovereenkomst (incorporated by reference)
- Overmacht (zie §13)
- SLA (zie Bijlage 1)

### 2. Dienstomschrijving
- Verwijzing naar de Service Description URL (versiebeheer via Wayback / hash)
- Tier (Lite / Pro / Max) zoals vastgelegd in de offerte
- Wijzigingen aan de Dienst worden vooraf gecommuniceerd met 30 dagen voorafgaande kennisgeving

### 3. Looptijd & opzegging
- Default: maandelijks, opzegtermijn 30 dagen, per e-mail aan `support@klantkraan.nl`
- 6-mo prepay variant: looptijd 6 maanden, daarna maandelijks opzegbaar
- 12-mo prepay variant: looptijd 12 maanden, daarna maandelijks opzegbaar
- Geen automatische verlenging > 1 maand zonder schriftelijke instemming klant

### 4. Prijzen & BTW
- 21% NL BTW standaard (art. 9 lid 1 Wet OB 1968)
- Reverse-charge naar EU-bedrijven (zonder NL-vestiging) — BTW-nummer vermelden
- B2B services naar UK (post-Brexit): outside scope NL BTW
- Jaarlijkse indexering op CBS-CPI (consumentenprijsindex), bekendgemaakt 30 dagen voor verandering

### 5. Betaling
- Mollie SEPA-incasso, eerste maand via iDEAL met mandaatregistratie
- Betalingstermijn: incasso vindt plaats op 1e werkdag van de maand
- Wettelijke handelsrente (art. 6:119a BW) bij niet-betaling
- Incassokosten 15% van de hoofdsom, minimaal €40 (conform Wet Incassokosten)
- Opschorting na 2 mislukte incasso-pogingen + 14 dagen herinneringstermijn

### 6. SLA (zie Bijlage 1)
- Uptime 99,0% maandgemiddeld (excl. onderhoud, sub-processor failures, force majeure)
- Service credit max 10% van maandfee — geen verdere remedie
- Onderhoudsvensters: zondagavond 22:00–02:00 CET, max 1x per maand, 7 dagen vooraankondiging

### 7. Aansprakelijkheid
- Alleen *directe schade*
- Cap = 12 maanden vergoedingen voorafgaand aan event
- **Absolute cap: €25.000 per geval, €50.000 per kalenderjaar**
- Uitsluiting *indirecte schade*: gederfde winst, omzet, goodwill, dataverlies, gemiste klantopdrachten
- Uitzonderingen niet uitsluitbaar: opzet of bewuste roekeloosheid (analogie art. 7:951 BW)
- *Onredelijk bezwarend* (art. 6:233 sub a BW) toets: bij Lite-tier (€299) kan een 12-mo cap acceptabel zijn omdat klant ook eenvoudig kan opzeggen. Op Max wordt een hogere cap overlegd.

### 8. Intellectueel eigendom
- Klantkraan houdt IE op platform, prompts, modellen, dashboards, code
- Klant houdt IE op klantdata + uploads
- Klant verleent Klantkraan een niet-exclusieve licentie om data te verwerken *uitsluitend* voor de Dienst
- Geen training van algemene modellen op klantdata zonder schriftelijke toestemming

### 9. Klantdata & teruggave
- Klantdata blijft eigendom van klant
- Export beschikbaar in JSON/CSV binnen 30 dagen na einde overeenkomst
- Verwijdering binnen 60 dagen na einde overeenkomst (30 dagen export + 30 dagen retentie-window)

### 10. Geheimhouding
- Wederzijds
- 3 jaar na einde overeenkomst
- Uitzonderingen: wet, publiek beschikbare informatie, eigen-ontwikkelde informatie

### 11. Verwerkersovereenkomst
- Incorporated by reference (klantkraan.nl/legal/dpa)
- Klant warrants dat zij verwerkingsverantwoordelijke is voor alle persoonsgegevens van bellers/klanten
- Sub-processor flow-down clausule

### 12. Compliance (AI Act art. 50)
- **Niet-uitsluitbare clausule**: "Klant erkent dat de AI-disclosure verplicht is op grond van art. 50 AI Act en niet kan worden uitgeschakeld."
- Klantkraan biedt het script standaard met disclosure; uitschakelen is contractueel niet toegestaan
- Klant vrijwaart Klantkraan voor boetes voortvloeiend uit klant-veroorzaakte non-compliance

### 13. Overmacht (art. 6:75 BW)
- Inclusief: uitval Anthropic/Synthflow/CM.com, internetstoringen, DDoS-aanvallen, AVG-toezichthouder-besluiten met opschortend effect, oorlog, pandemie
- Indien overmacht > 30 dagen, mag elke partij beëindigen zonder schadevergoeding
- Eerder betaalde maandfees worden naar rato terugbetaald

### 14. Wijzigingen voorwaarden
- 30 dagen vooraf, schriftelijk
- Klant mag binnen 30 dagen kosteloos opzeggen
- Wijzigingen die uitsluitend in voordeel van klant zijn: direct van kracht

### 15. Overdraagbaarheid
- Klantkraan mag overdragen aan rechtsopvolger zonder consent
- Klant mag enkel met schriftelijke toestemming Klantkraan, niet onredelijk te weigeren

### 16. Toepasselijk recht & forum
- Nederlands recht
- Exclusief Rechtbank Den Haag
- Weens Koopverdrag (CISG) uitdrukkelijk uitgesloten
- Mediationclausule: partijen proberen eerst mediation via Nederlands Arbitrage Instituut

### 17. Slotbepalingen
- Volledige overeenkomst (geen mondelinge afspraken bindend)
- Severability (partial nullity laat rest in stand)
- Originele Nederlandse versie prevaleert boven vertalingen

## Bijlages

1. **SLA** — zie `04-legal/sla-annex.md`
2. **Service Description per tier** — link naar URL met versiebeheer
3. **Sub-processor list** — link naar `klantkraan.nl/legal/subprocessors`

## Where to publish

- Full text on `klantkraan.nl/legal/voorwaarden`
- Linked from every offerte, every invoice, every email footer
- Versioned with date stamp + git commit hash

## Source

- art. 6:233 BW (algemene voorwaarden): https://wetten.overheid.nl/BWBR0005289/2024-01-01/0/Boek6/Titel5/Afdeling3/Artikel233/
- art. 6:119a BW (handelsrente): https://wetten.overheid.nl/BWBR0005289/2024-01-01/0/Boek6/Titel1/Afdeling11/Artikel119a/
- Wet Incassokosten: https://wetten.overheid.nl/BWBR0031432/
- Dirkzwager op exoneratiebeding B2B: https://www.dirkzwager.nl/kennis/artikelen/totale-uitsluiting-van-aansprakelijkheid-bij-wanprestatie-in-algemene-voorwaarden-mag-dat
- EU AI Act art. 50: https://artificialintelligenceact.eu/article/50/
