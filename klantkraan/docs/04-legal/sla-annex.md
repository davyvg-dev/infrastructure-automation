# Service Level Agreement — Annex 1 to the MSA

> 99,0% maandelijkse uptime (not 99,9% — be honest as a solo founder). Service credits capped at 10% van maandfee.

## Definities

| Term                           | Betekenis                                                                                                                                                                                              |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Beschikbaarheid**            | Het percentage van de tijd binnen een kalendermaand dat de Dienst beschikbaar is voor normale operatie, gemeten van buitenaf via Uptime Kuma checks.                                                   |
| **Geplande Downtime**          | Aangekondigd onderhoud, min. 7 dagen vooraf, max. 1× per maand, in onderhoudsvenster zondagavond 22:00–02:00 CET.                                                                                      |
| **Niet-toerekenbare Downtime** | Uitval die niet aan Klantkraan toe te rekenen is: sub-processor outage (Synthflow, CM.com, Anthropic, Cloudflare), internet-storing, overmacht, AVG-toezichthouder besluit, klant-veroorzaakte issues. |
| **Service Credit**             | Een terug-betaling op de volgende maandfactuur, uitgedrukt als percentage van de maandfee.                                                                                                             |

## Beschikbaarheidsdoel

| Niveau                                  | Doel              |
| --------------------------------------- | ----------------- |
| **Maand-uptime**                        | **99,0%**         |
| Toegestane downtime per maand bij 99,0% | ~7 uur 18 minuten |

Niet inbegrepen in de berekening:

- Geplande Downtime
- Niet-toerekenbare Downtime

## Service Credits

Indien de maand-uptime onder het doel zakt:

| Uptime in maand X | Service Credit op factuur maand X+1                |
| ----------------- | -------------------------------------------------- |
| 98,0% – 98,99%    | 5% van maandfee                                    |
| 95,0% – 97,99%    | 10% van maandfee                                   |
| < 95,0%           | 10% van maandfee + recht om kosteloos op te zeggen |

**Maximum credit per maand: 10% van maandfee.** Geen verdere remedie (incl. schadevergoeding) buiten deze credits, met uitzondering van opzet of bewuste roekeloosheid.

## Onderhoudsvensters

- Zondagavond 22:00 CET tot 02:00 CET maandagochtend.
- Maximum 1× per maand.
- Aankondiging minimaal 7 dagen vooraf via e-mail naar het primaire contact van de klant.
- Onderhoud tijdens dit venster telt NIET als downtime.

## Incident response

| Severity          | Definitie                                                       | Eerste reactie    | Resolution target |
| ----------------- | --------------------------------------------------------------- | ----------------- | ----------------- |
| **S1 — Critical** | Volledige dienst-uitval, geen calls worden afgehandeld          | ≤30 min           | ≤4 uur            |
| **S2 — High**     | Significant deel van de dienst uitgevallen (bv. SMS werkt niet) | ≤2 uur            | ≤8 uur (werkuren) |
| **S3 — Medium**   | Beperkte impact (bv. dashboard niet bereikbaar)                 | ≤8 uur (werkuren) | ≤2 werkdagen      |
| **S4 — Low**      | Cosmetisch of niet-blokkerend                                   | ≤2 werkdagen      | ≤10 werkdagen     |

Werkuren = ma t/m vr 09:00–18:00 CET.

S1 incidents trigger automatisch:

- Sentry alert → WhatsApp ping naar founder
- Healthchecks.io alert (separate, mis-ping geeft ook escalatie)
- Status page update binnen 30 min

## Status page

`status.klantkraan.nl` — operated via self-hosted Uptime Kuma op de Hetzner VPS. Toont per dienst-component:

- Astro marketing site
- n8n automation engine
- API (automation-api)
- Synthflow voice (via API health-check)
- CM.com SMS (via API health-check)
- Database (Neon)

## Beperkingen

- Klant moet incident melden via `support@klantkraan.nl` of WhatsApp om credit-recht in te roepen.
- Credit-aanvraag binnen 30 dagen na incident.
- Geen credits voor downtime tijdens trial/eerste maand 50% korting.

## Wat de SLA NIET dekt

- Synthflow-fouten in AI-gespreksinhoud (geen prijs voor klant) → tuning, geen credit
- Klant-veroorzaakte forwarding-problemen
- Carrier-storingen (KPN, Vodafone, Odido) buiten de macht van Klantkraan
- DNS-veranderingen door klant zonder coördinatie

## Realistische verwachting voor de founder

99,0% maandelijks is een **eerlijk doel** voor een solo founder met een Hetzner CX22 + n8n self-hosted. Een sub-processor outage van 1 uur consumeert al ~14% van de toegestane downtime in een 99,9%-belofte, maar slechts 1,4% in een 99,0%-belofte. **Niet over-beloven.**

Wanneer de bezetting groeit naar 30+ clients, overweeg dan upgrade naar 99,5% met:

- Multi-region failover (Hetzner FI + DE)
- Hot standby Postgres replica
- Multi-channel sub-processor adapter (Twilio fallback voor CM.com)

## Source

- Hetzner SLA: https://www.hetzner.com/SLA/
- Cloudflare Pages SLA: https://www.cloudflare.com/business-sla/
- Industry SaaS SLA benchmarks: https://www.atlassian.com/incident-management/kpis/sla-vs-slo-vs-sli
