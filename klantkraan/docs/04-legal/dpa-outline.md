# DPA / Verwerkersovereenkomst — Outline (planning only)

> **The signable NL template is `04-legal/verwerkersovereenkomst-template.md`.** Use that with
> clients. This file is the older planning skeleton and its Annexen describe the **retired
> voice stack** (Synthflow/ElevenLabs/CM.com, audio recordings, Neon/Mollie/Attio) — do not
> hand its sub-processor list to a client. Kept for the art. 28 rationale.

> AVG (GDPR) art. 28 requires a signed processing agreement before any personal data flows. Klantkraan is **processor (verwerker)**; the client (loodgieter/dakdekker) is **controller (verwerkingsverantwoordelijke)**. This DPA flows down to all our sub-processors.

## Why this matters

If we don't have a DPA signed _before_ go-live, every call recording, every caller phone number, every transcript is an unlawful processing under art. 28(3) AVG. AP can impose corrective measures + fines up to €20M / 4% turnover (art. 83 AVG).

## Sections (outline)

### 1. Definities

- Verwerkingsverantwoordelijke, Verwerker, Persoonsgegevens, Subverwerker — refer to AVG art. 4
- Diensten (verwijst naar MSA)

### 2. Onderwerp, duur, aard & doel van de verwerking

- Onderwerp: het uitvoeren van Klantkraan-diensten zoals beschreven in de Service Description
- Duur: voor de looptijd van de hoofdovereenkomst + 60 dagen retentie-window
- Aard: ontvangen, opslaan, transcriberen, analyseren, en doorsturen van persoonsgegevens
- Doel: het beantwoorden van inkomende communicatie namens verwerkingsverantwoordelijke
- Annex I: categorieën van betrokkenen + persoonsgegevens

### 3. Instructies

- Verwerker handelt uitsluitend op gedocumenteerde instructies van verwerkingsverantwoordelijke
- Verwerker meldt onverwijld indien een instructie inbreuk maakt op AVG of andere wetgeving

### 4. Vertrouwelijkheid van personeel

- art. 28(3)(b) AVG
- Verwerker bindt alle personen die persoonsgegevens verwerken aan geheimhouding
- Geldt ook voor freelancers, VAs, dev-partners

### 5. Beveiligingsmaatregelen (TOMs)

- art. 32 AVG
- Annex II: concrete maatregelen
  - EU-only data residency (Hetzner Frankfurt, Neon EU, Cloudflare EU Workers)
  - At-rest encryption (Postgres TDE), in-transit TLS 1.3
  - Role-based access (Bitwarden Business + audit log)
  - Per-client `client_id` isolation in alle queries
  - Automatische back-ups dagelijks, encrypted, off-site
  - Logging via Sentry + audit-trail in Postgres
  - Incident response playbook (zie §8)

### 6. Sub-processor regime

- Algemene toestemming voor de sub-processors op de gepubliceerde lijst (klantkraan.nl/legal/subprocessors)
- 30 dagen voorafgaande kennisgeving bij wijzigingen
- Bezwaar binnen die 30 dagen leidt tot opzeggingsrecht voor verwerkingsverantwoordelijke
- Verwerker legt aan elke sub-processor dezelfde verplichtingen op (flow-down)
- Annex III: huidige sub-processor lijst

### 7. Assistentie bij rechten van betrokkenen

- art. 12–22 AVG
- Verwerker biedt redelijke assistentie binnen 14 dagen
- Kosten voor verzoeken: eerste 2 per kwartaal gratis, daarna €75/uur

### 8. Inbreuk-melding

- art. 33–34 AVG
- Binnen **48 uur** aan verwerkingsverantwoordelijke (strikter dan de 72 uur naar AP)
- Inhoud melding: aard inbreuk, betrokken categorieën, geschatte aantallen, contactpersoon, maatregelen

### 9. DPIA / voorafgaande raadpleging

- art. 35–36 AVG
- Verwerker levert redelijke informatie voor de DPIA van klant
- Verwerker heeft eigen DPIA per service-tier uitgevoerd (zie `04-legal/dpia-template.md`)

### 10. Verwijdering / teruggave bij einde

- Export beschikbaar in JSON/CSV binnen 30 dagen na einde
- Wissing binnen 60 dagen na einde (30 dagen retentie-window)
- Schriftelijke bevestiging van wissing op verzoek

### 11. Audit-rechten

- 1× per jaar + bij gerede vermoedens van non-compliance
- Klant draagt kosten, tenzij non-compliance wordt geconstateerd
- 30 dagen schriftelijke aankondiging
- Audit uitgevoerd door onafhankelijke derde onder NDA
- Geen verstoring van dagelijkse bedrijfsvoering

### 12. Internationale doorgiften

- Geen doorgiften buiten EER zonder geldige doorgifte-mechanisme
- Indien doorgifte: EU Standard Contractual Clauses 2021/914 module 3 + TIA (Transfer Impact Assessment)
- Anthropic (US): SCC + supplementary measures gedocumenteerd
- Cloudflare (US): SCC + EU data-only configuratie

### 13. Aansprakelijkheid

- Wederzijdse cap = 12 maanden vergoedingen, max €25.000
- Uitzondering: bewuste roekeloosheid niet uitsluitbaar

### 14. Toepasselijk recht & forum

- Nederlands recht
- Exclusief Rechtbank Den Haag

## Annexen

### Annex I — Categorieën van persoonsgegevens

| Categorie             | Voorbeelden                                                            | Bron                       |
| --------------------- | ---------------------------------------------------------------------- | -------------------------- |
| Identificatiegegevens | Naam, telefoonnummer                                                   | Inbound calls              |
| Adresgegevens         | Adres, postcode                                                        | Caller dictation           |
| Communicatiegegevens  | Audio-opnames, transcripten                                            | Synthflow + CM.com         |
| Klantgeschiedenis     | Eerdere klussen, voorkeuren                                            | Attio (na koppeling)       |
| Locatiegegevens       | Service-postcode                                                       | Booking flow               |
| Financiële gegevens   | Voorrijkosten geaccordeerd, kostenraming                               | Soms gevraagd in gesprek   |
| Bijzondere gegevens   | In principe geen — bellers kunnen onbedoeld gezondheidsgegevens noemen | Audit + redactie-procedure |

Geen verwerking van strafrechtelijke gegevens, BSN, of andere bijzondere categorieën als doel.

### Annex II — Technische en organisatorische maatregelen

- EU-only hosting
- Encryption at-rest + in-transit
- Per-client tenant isolation
- Role-based access + audit log
- Daily encrypted backups
- Incident response playbook
- Annual penetration test (vanaf jaar 2)

### Annex III — Sub-processor list

| Sub-processor | Doel                    | Locatie data            | DPA-link                                                 |
| ------------- | ----------------------- | ----------------------- | -------------------------------------------------------- |
| Anthropic     | LLM inference (Claude)  | US, SCC + supplementary | https://www.anthropic.com/legal/data-processing-addendum |
| Synthflow     | Voice agent runtime     | EU + US (config'd EU)   | https://docs.synthflow.ai/privacy-policy                 |
| ElevenLabs    | TTS via Synthflow       | US, SCC                 | https://elevenlabs.io/legal                              |
| CM.com        | SMS / telephony         | EU (NL)                 | https://www.cm.com/nl-nl/app/legal/                      |
| Attio         | CRM                     | EU/US                   | https://attio.com/legal/terms-and-conditions             |
| Hetzner       | Hosting (VPS, Postgres) | EU (DE/FI)              | https://www.hetzner.com/AV/DPA_en.pdf                    |
| Cloudflare    | CDN, edge workers       | Global (EU-pinned)      | https://www.cloudflare.com/cloudflare-customer-dpa/      |
| Neon          | Postgres                | EU                      | https://neon.com/dpa                                     |
| Resend        | Transactional email     | US, SCC                 | https://resend.com/legal/dpa                             |
| Mollie        | Payments                | EU (NL)                 | https://www.mollie.com/legal/data-processing-agreement   |
| Moneybird     | Invoicing               | EU (NL)                 | https://www.moneybird.com/legal/verwerkersovereenkomst   |

## Where to publish

- Full text on `klantkraan.nl/legal/dpa`
- Sub-processor list at `klantkraan.nl/legal/subprocessors` (canonical, updated with each change)
- Klant tekent DPA digitaal naast MSA bij contractondertekening

## Source

- AVG art. 28 (Nederlandse tekst): https://www.privacy-regulation.eu/nl/artikel-28-verwerker-EU-AVG.htm
- AP verwerkersovereenkomst guide: https://www.autoriteitpersoonsgegevens.nl/en/themes/basic-gdpr/gdpr-basics/processing-agreement
- EU SCCs 2021/914: https://eur-lex.europa.eu/eli/dec_impl/2021/914
