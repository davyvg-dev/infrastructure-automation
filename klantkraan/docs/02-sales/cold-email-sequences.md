# Cold Email Sequences

> 3 sequences, 4 touches each, Dutch, ≤100 words/email, single CTA, plain text. Signed with real name + 06 + KvK.

## Rules of the road

- **Audience**: BV-registered loodgieters + dakdekkers only (eenmanszaak / VOF require opt-in — see `06-outbound/gdpr-compliance.md`).
- **Send window**: 08:00–18:00 CET, weekdays only.
- **Volume**: 25 sends/inbox/day, 9 inboxes = ~225/day = ~4,500/month.
- **Personalisation tokens**: `{{voornaam}} {{bedrijf}} {{stad}} {{concurrent}}` minimum. Without `{{voornaam}}`, do not send.
- **Subject lines**: lowercase, ≤45 chars, no `RE:` faking.
- **Signature**: real name + 06-nummer + KvK 12345678 + `klantkraan.nl`.

## Sequence A — "Gemiste oproepen = gemist geld"

**Target**: ICP that values quantified ROI. Most loodgieters.

### Touch 1 — Day 0

```
Onderwerp: hoeveel gemiste oproepen had {{bedrijf}} deze week?

Hoi {{voornaam}},

Ik zag dat {{bedrijf}} actief is in {{stad}}. Loodgieters missen
gemiddeld 28% van inkomende oproepen — 2 tot 3 klussen per week
die naar de buurman gaan.

Ik bouwde een rekentool (3 velden, 30 seconden) die laat zien
wat dat u kost per jaar. Wilt u de link?

Groet,
[Voornaam Achternaam]
06-XXXXXXXX · KvK 12345678
klantkraan.nl
```

### Touch 2 — Day 3

```
Onderwerp: re: gemiste oproepen

Direct de link: klantkraan.nl/rekentool

Gemiddelde uitkomst voor een eenmansloodgieter met 2 monteurs:
€34.000 misgelopen omzet per jaar.

{{Voornaam}}
```

### Touch 3 — Day 7

```
Onderwerp: 1 vraag, geen pitch

{{voornaam}}, wie neemt bij u op als u op een dak staat en de
telefoon gaat?

Als het antwoord "niemand" of "voicemail" is, kost dit u geld.

15 min Zoom volgende week dinsdag of donderdag 16:00?

[Voornaam]
```

### Touch 4 — Day 12 (breakup)

```
Onderwerp: laatste mail

Ik stop hier met mailen. Geen probleem.

Mocht het ooit relevant worden: bel onze AI-receptionist live op
085-XXX XX XX. Stel hem een lastige vraag, hoor of het bevalt.

Succes met de zaak,
[Voornaam]
```

## Sequence B — "Uw concurrent heeft net X"

**Target**: ICP that's competitive / status-driven. Often dakdekkers or larger loodgieters (5+ staff).

### Touch 1 — Day 0

```
Onderwerp: {{concurrent}} pakt nu 24/7 op

Hoi {{voornaam}},

{{concurrent}} in {{regio}} heeft sinds kort een AI-receptionist
die buiten kantooruren opneemt, afspraken inplant en spoed doorzet.
Klanten merken het verschil niet.

Bij u kan dat binnen 7 dagen live staan.
Bel zelf onze demo: 085-XXX XX XX.

Groet,
[Voornaam] · 06-XXXXXXXX
KvK 12345678 · klantkraan.nl
```

### Touch 2 — Day 3

```
Onderwerp: demo gehoord?

Heeft u de demo gebeld?

Veel loodgieters bellen 2x — eerst sceptisch, dan met een lastige
vraag erin. Beide keren wint de AI. Probeer maar.

085-XXX XX XX

[Voornaam]
```

### Touch 3 — Day 7

```
Onderwerp: 15 min volgende week?

Korte Zoom dinsdag of donderdag 16:00?

Ik laat in 6 min zien hoe het bij {{bedrijf}} eruit ziet.
Geen verkooppraat.

cal.com/klantkraan/15min

[Voornaam]
```

### Touch 4 — Day 12 (breakup)

```
Onderwerp: sluit dossier

Ik laat het hierbij.

Mocht u ooit willen zien wat het oplevert: rekentool op
klantkraan.nl/rekentool.

Succes met de zaak,
[Voornaam]
```

## Sequence C — Value-first (geen pitch)

**Target**: ICP that's distrustful of sales. Default for second-attempt audiences (warm-up after A or B failed).

### Touch 1 — Day 0

```
Onderwerp: tip voor uw voicemail-tekst

Hoi {{voornaam}},

Korte tip: vervang uw voicemail-tekst door:
"Spreek uw postcode en spoed ja/nee in."

Dat verdubbelt de kans dat de klant inspreekt in plaats van
doorbelt naar de concurrent.

Geen pitch, gewoon iets dat werkt.

[Voornaam]
06-XXXXXXXX · KvK 12345678
```

### Touch 2 — Day 4

```
Onderwerp: nog een tip

Tweede tip: bel inkomende voicemails binnen 8 minuten terug —
daarna is de klant al verder.

Klinkt logisch, maar 70% van loodgieters doet het niet.

[Voornaam]
```

### Touch 3 — Day 9

```
Onderwerp: mag ik iets laten horen?

Ik bouw AI-receptionisten voor loodgieters.
Wil niets verkopen — wil alleen dat u onze demo belt en mij
eerlijk zegt of het natuurlijk klinkt:

085-XXX XX XX

2 minuten van uw tijd.

[Voornaam]
```

### Touch 4 — Day 14 (breakup)

```
Onderwerp: laatste

Geen reactie = geen probleem.

Mocht het ooit spelen: klantkraan.nl.

Succes,
[Voornaam]
```

## Reply-handling routing

| Reply category | Action |
|---|---|
| Positive ("interesse", "vertel meer") | n8n flags in Attio → Slack ping → founder personal reply within 15 min, propose Zoom + Cal.com link. |
| Information request | Personal reply with answer + Cal.com link as soft CTA. |
| "Niet nu, later" | Polite reply, snooze in Attio 90 days, drop into newsletter list. |
| "Stop" / "niet meer mailen" | Immediate unsubscribe, Postgres `suppressions` table, all sequences. |
| Negative / hostile | Personal reply ("dank voor de duidelijkheid"), suppress. |
| Out-of-office | Wait 14 days, resume sequence. |

## A/B testing schedule

- Subject lines: rotate 3 per sequence, measure open rate at week 2.
- Opening line: rotate 2 per sequence, measure reply rate at week 3.
- CTA: demo number vs Cal.com link vs rekentool — test at week 4.
- Whole sequence: A vs B vs C side-by-side at month 2.

## Inbox/domain rotation

| Domain | Inboxes | Mailbox naming |
|---|---|---|
| getklantkraan.nl | 3 | `jan@`, `pieter@`, `info@` — all role-based-safe |
| klantenmotor.nl | 3 | `jan@`, `pieter@`, `info@` |
| klantkraanpro.nl | 3 | `jan@`, `pieter@`, `info@` |

Never send from the brand domain `klantkraan.nl` to protect deliverability of legitimate transactional mail.

## Compliance footer (on every email)

```
[Voornaam Achternaam] — Klantkraan
T4 Software Consulting BV · KvK 12345678 · BTW NL000000000B01
[Adres]
klantkraan.nl/privacy
Liever geen mail meer ontvangen? Antwoord met "stop" en u staat
binnen 24u uit ons systeem.
```

## Source

- NL B2B cold email regulation: `06-outbound/gdpr-compliance.md`
- Reply benchmarks: `02-sales/funnel-benchmarks.md`
- Smartlead deliverability: https://www.smartlead.ai/blog/cold-email-open-rates
- Apollo reply-rate benchmarks 2026: https://www.apollo.io/insights/whats-the-expected-reply-rate-for-a-well-run-outbound-cold-email-campaign
