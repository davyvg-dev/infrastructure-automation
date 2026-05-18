# SMS Templates (CM.com, Dutch)

> All SMS sent via CM.com Business Messaging API. Alphanumeric sender ID = `bedrijfsnaam` (max 11 chars, alphanumeric, no spaces). GSM-7 encoding (155 chars/message before split). Send window 08:00–21:00 CET (n8n cron gate; out-of-window messages queue until 08:00 next day).

## 1. Missed-call-back

**Trigger**: CM.com webhook `call.missed` → n8n waits 45s (gives Synthflow time to answer on Pro/Max; Lite skips wait) → Postgres lookup (did this caller speak to Synthflow in last 30 min?) → if not, send.

```
Hoi, u belde net met {{bedrijfsnaam}}. We konden niet opnemen.
Plan direct online: {{calcom_short_url}}
Of bel terug. STOP = afmelden.
```

**Compliance**:
- Alphanumeric sender ID (bedrijfsnaam)
- STOP-opt-out in body (required by Tw 11.7)
- Send window 08:00–21:00 CET (queued otherwise)
- Logged in Postgres `sms_sent` table with delivery confirmation from CM.com

## 2. Review request — initial (SMS, +2h after job complete)

**Trigger**: client marks job "afgerond" via Werkbon webhook / Snelstart webhook / n8n form-link / Attio button.

```
Bedankt dat u koos voor {{bedrijfsnaam}}, {{voornaam}}!
Een korte review op Google helpt ons enorm: {{google_review_short}}
Duurt 20 sec. STOP = afmelden.
```

## 3. Review reminder (email, day 7 if no review)

**Trigger**: n8n cron checks Postgres for review_status `pending` at D+7. If still pending, send email (not SMS — softer touch).

```
Onderwerp: Heeft u nog een momentje, {{voornaam}}?

Beste {{voornaam}},

Vorige week hebben we {{kort_klus_omschrijving}} bij u uitgevoerd.
We hopen dat alles naar wens is.

Mocht u tevreden zijn, dan zouden we het waarderen als u een
korte review achterlaat:

Google: {{google_link}}
Trustpilot: {{trustpilot_link}}

Heeft u opmerkingen of klachten? Antwoord dan gerust op deze
mail — die komen rechtstreeks bij {{owner_voornaam}} terecht.

Met vriendelijke groet,
{{bedrijfsnaam}}
```

## 4. Cal.com booking confirmation (SMS)

**Trigger**: Cal.com webhook `booking.created` (booked via AI receptionist or web form).

```
{{voornaam}}, uw afspraak is bevestigd bij {{bedrijfsnaam}}.
Datum: {{datum}} om {{tijd}}.
Adres: {{adres}}.
Wijzigen: {{calcom_reschedule_link}}
```

## 5. Cal.com booking reminder (SMS, T-24h)

```
Morgen om {{tijd}}: afspraak bij {{bedrijfsnaam}}.
Adres: {{adres}}. Annuleren? {{calcom_cancel_link}}
```

## 6. Owner daily stats (SMS, first 14 days only)

**Trigger**: n8n cron 18:00 every weekday, first 14 days post-go-live.

```
{{owner_voornaam}}, vandaag bij {{bedrijfsnaam}}:
{{calls_taken}} calls door AI, {{missed_recovered}} gemist
teruggewonnen, {{bookings}} boekingen, {{reviews}} reviews.
Dashboard: {{slug_url}}
```

## 7. Owner weekly stats (email, Mondays 08:00)

**Trigger**: n8n cron Monday 08:00 from D15 onwards.

```
Onderwerp: {{bedrijfsnaam}} — week {{weeknr}}

Hoi {{owner_voornaam}},

Vorige week op een rij:

📞 {{calls_taken}} calls beantwoord door AI
🚨 {{missed_recovered}} gemiste klanten teruggewonnen
📅 {{bookings}} nieuwe boekingen
⭐ {{reviews}} nieuwe Google-reviews ({{avg_rating}}/5)

Top 3 calls van de week:
1. {{call_1_summary}}
2. {{call_2_summary}}
3. {{call_3_summary}}

Volledig dashboard: {{slug_url}}

Vragen? App me op {{founder_whatsapp}}.

— {{founder_voornaam}}
```

## 8. Onboarding day-0 welcome (SMS + e-mail)

**Trigger**: contract signed in PandaDoc/SignWell.

SMS:
```
Welkom {{owner_voornaam}}! Klantkraan is begonnen. 
Vul deze intake (12 min, vanaf je telefoon): {{tally_short_url}}
Vragen? App {{founder_whatsapp}}
```

E-mail (richer):
```
Onderwerp: Welkom bij Klantkraan — eerste stap

Hoi {{owner_voornaam}},

Welkom! De komende 8 dagen ben ik vooral op de achtergrond bezig.
Wat we van jou nodig hebben:

1. Vul de intake in (12 minuten): {{tally_link}}
2. Bekijk dit korte filmpje (90 sec) over wat er deze week gebeurt:
   {{loom_link}}
3. Donderdag dag 4 stuur ik je de doorschakel-instructies voor
   {{provider}}.

Vragen tussendoor? App me direct op {{founder_whatsapp}}.

Tot zo,
{{founder_voornaam}}
```

## 9. Go-live SMS (day 8)

```
{{owner_voornaam}}, Klantkraan is LIVE bij {{bedrijfsnaam}}!
Alle gemiste calls worden vanaf nu opgepakt door {{agent_naam}}.
Dashboard: {{slug_url}}
Dag-stats volgen elke avond.
```

## 10. STOP / opt-out handling

**Trigger**: incoming SMS body matches `(?i)^stop$|^afmelden$|^uitschrijven$`.

n8n actions:
1. Insert into Postgres `suppressions` table with phone-number hash.
2. Reply with confirmation:
   ```
   U bent afgemeld voor SMS van {{bedrijfsnaam}}. 
   Vragen? Bel {{owner_phone}}.
   ```
3. No further SMS sent to this number from any client of Klantkraan.

## Variable convention

All variables come from one of:
- `clients` table (intake-form derived)
- `calls` table (call event)
- `bookings` table (Cal.com)
- `reviews` table (Google/Trustpilot API)
- `weekly_snapshots` table (computed cron)

## Length budget

GSM-7 is 160 chars/message. Templates above kept ≤ 155 chars to leave room for variable substitution. Anything that splits to 2+ messages is flagged in n8n with a warning (cost doubles).

## Cost model

| Item | Cost |
|---|---|
| CM.com SMS to NL | €0.08 |
| CM.com SMS to BE | €0.08 |
| CM.com SMS to international | €0.10–0.15 (Pro/Max only, rare) |
| Avg SMS / client / month | ~50 (across all categories) |
| Avg cost / client / month | ~€4 |

## Source

- CM.com SMS pricing: https://www.cm.com/pricing/sms/
- CM.com GDPR opt-in guide: https://www.cm.com/knowledge-center/739a4b2c-641b-4ca2-9d95-9cfeffa6c62d/
- Telecommunicatiewet Art. 11.7 (opt-out + sender-ID requirements): https://wetten.overheid.nl/BWBR0009950/
- CM.com international SMS rules: https://www.cm.com/blog/sending-international-sms-country-specific-rules-regulations-and-habits/
