# Client Intake Form (Tally, 32 questions)

> Filled in by the owner-operator within minutes of signing the contract. Tally chosen over Typeform (free tier covers logic + webhooks, faster on mobile) and over a custom Astro form (overkill at <10 clients/mo).

## Form mechanics

- **Tool**: Tally Free tier
- **Auto-save**: enabled (van work-day completion friendly)
- **Logic jumps**: tier-conditional questions (e.g. integrations only shown if tier = Max)
- **Webhook**: `POST` to n8n endpoint that parses + validates + writes to Attio + Neon
- **Expected completion time**: 10–14 minutes on phone
- **Reminder cadence**: T+24h, T+72h via SMS if not submitted

## The 32 questions

### Bedrijf (1–6)

1. Bedrijfsnaam (zoals op factuur)
2. KvK-nummer
3. BTW-nummer
4. Vestigingsadres (straat, postcode, plaats)
5. Website-URL (laat leeg als geen website)
6. Logo upload (PNG/SVG, optioneel)

### Bereikbaarheid (7–13)

7. Huidig hoofd-telefoonnummer
8. Huidige provider (KPN / Vodafone / Odido / Youfone / Simyo / Anders)
9. Type lijn (mobiel GSM / VoIP / vast)
10. Kantooruren — per dag (ma t/m zo)
11. Lunchpauze? (ja + tijd / nee)
12. Beleid buiten kantooruren (alles via AI / alleen spoed / niets)
13. Wat is "spoed" voor uw bedrijf? (vrije tekst; voorbeelden: "lekkage waarbij water uit het plafond komt", "geen warm water in winter")

### Service-gebied (14–15)

14. Postcodegebied(en) waar u werkt (kommagescheiden, of "heel NL")
15. Bent u bereid buiten dat gebied te rijden? (ja / nee / op aanvraag)

### Tarieven (16–20)

16. Voorrijkosten (€, incl. of excl. BTW — specificeer)
17. Uurtarief excl. BTW (€)
18. Spoedtoeslag avond/weekend (% of vast €)
19. Materiaalopslag (%)
20. Mag de AI prijzen noemen? (ja, allemaal / alleen voorrijkosten / nee, altijd doorverwijzen)

### Diensten + FAQ (21–23)

21. Top-10 meest gestelde vragen (vrije tekst, één per regel) — feeds RAG context
22. Top-5 diensten die u aanbiedt
23. Wat doet u expliciet **niet**? (bv. asbest, gas-aansluitingen >0,5 MPa, dakwerk in winter)

### Integraties (24–28)

24. Google Business Profile e-mail (we vragen daarna "manager"-toegang)
25. Trustpilot-pagina-URL (indien aanwezig)
26. Huidige agenda (Google / Outlook / iCloud / papier / anders)
27. Boekhoudpakket (Snelstart / Moneybird / Exact / Werkbon / Skoon / Anders / geen)
28. Gebruikt u nu al een werkbon/CRM-tool? Welke? (Werkbon, Snelstart Pro, Mobielwerken, anders, geen)

### Escalatie + handoff (29–31)

29. Naam + 06-nummer van de eigenaar (voor handoff-SMS van AI naar mens)
30. Tweede contactpersoon (optioneel) — naam + 06
31. WhatsApp-nummer voor klant-communicatie met Klantkraan support

### Stem & toon (32)

32. Voorkeur AI-stem (mannelijk neutraal ABN / vrouwelijk neutraal ABN / geen voorkeur). Naam-suggestie voor de AI? (default: "Sanne" voor vrouw / "Daan" voor man)

## Conditional questions (Max tier only)

- Welke custom integratie heeft u nodig? (Werkbon, Snelstart, eigen ERP)
- API-toegang beschikbaar? (ja / nee / weet niet)
- Wie is de tech-contact aan uw kant? (naam, e-mail, telefoon)

## Validation rules (n8n side)

| Field | Rule | Action on fail |
|---|---|---|
| KvK-nummer | 8 digits | Re-query KvK API; if invalid, flag founder |
| BTW-nummer | NL + 9 digits + B + 2 digits | Re-query Belastingdienst VIES |
| Voorrijkosten | € 25–150 typical | Flag for verification if outside range |
| Uurtarief | € 40–120 typical | Flag for verification if outside range |
| Postcode pattern | 1234 AB or 1234AB | Auto-normalise |
| Owner 06-nummer | +31 6 + 8 digits | Reject if mobile prefix wrong |

## Output (n8n → Attio + Neon)

```sql
INSERT INTO clients (
  id, name, slug, tier, kvk, btw_number,
  primary_phone, hours, emergency_def,
  service_postcodes, willing_outside,
  voorrijkosten, uurtarief, spoedtoeslag_pct, materiaal_opslag_pct,
  may_quote_prices,
  faq, services_offered, services_not_offered,
  gbp_email, trustpilot_url, calendar_provider, accounting_pkg, crm_pkg,
  owner_name, owner_phone, secondary_contact,
  whatsapp_support, voice_pref, agent_name,
  -- Max-tier only:
  integration_request, api_available, tech_contact,
  created_at
) VALUES (...);
```

## Source

- Tally vs Typeform decision: cost + mobile UX research
- KvK API for validation: https://developers.kvk.nl/
- BTW VIES validation: https://ec.europa.eu/taxation_customs/vies/
