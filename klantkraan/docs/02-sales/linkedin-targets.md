# LinkedIn Prospecting Target List

Internal working doc for the founder's **manual** LinkedIn outreach. This is not a list of people or
companies — inventing 150 real-looking businesses would create fake records we might actually try to
contact. Instead each row is a **search segment** (niche x region) you paste into LinkedIn or Sales
Navigator to surface real owners, then work by hand.

Positioning is any business / any language / international. The first paying client is an English/German
airco company on Mallorca, so the international angle is proven, not theoretical.

## How to use — the manual co-pilot loop

1. **Run the search.** Pick a row. Paste its query into the LinkedIn keyword box (or Sales Navigator
   Keywords field), set the region and the title filter from the row's columns.
   - *Sales Navigator:* Keywords = the query string, **Geography** = the Region, **Title** = the row's
     job titles, Company headcount 1-20, Seniority = Owner/Partner.
   - *Free LinkedIn:* paste the query, append the title terms with `AND (...)`, set the city under the
     **Locations** filter.
2. **Open the profile.** Confirm it is an owner-run service business that actually takes inbound calls /
   WhatsApp / web leads and has no dedicated front desk. Skip franchises, chains, and anyone with a
   staffed reception.
3. **Send a PERSONALIZED connection note.** Reference something real from their profile or company (a
   recent post, their service area, an obvious after-hours gap). Never a template blast. The pitch is the
   lost after-hours / overflow lead — the AI receptionist answers 24/7, qualifies, and books.
4. **Log the prospect** as a pipeline record (run from `ai-receptionist/`):
   ```
   python -m app.pipeline add "Business Name" \
     --country ES --lang en --type airco \
     --source linkedin-manual \
     --note "connected 22-07, personalized note re 24/7 guest emergencies"
   ```
   Use `--country NL --lang nl` for Dutch rows. Advance with `python -m app.pipeline advance <slug> ...`.

## Golden rules

- **Manual only.** No automation, scrapers, or auto-connect tools. LinkedIn ToS forbids it and it is a
  hard founder rule. Every action is a human click. (This supersedes the old HeyReach-based
  `linkedin-cadence.md`.)
- **Personalize every note.** One relevant, specific sentence beats a clever template.
- **One connect batch per day, ~15-20 requests max.** Stay well under LinkedIn's daily ceiling; bursts
  get the account flagged.
- **Log everything.** Every connect becomes a pipeline record so nothing leaks and follow-ups are tracked.
- **Owner is the decision-maker.** Filter for eigenaar / oprichter / directeur (NL) and owner / founder /
  managing director (international). Skip employees.

Any row below can be converted into an actual list of named prospects via a Google Maps pull (business
name + owner lookup) if you want named targets instead of a live LinkedIn search — ask and it gets built.

---

## Section A — Netherlands

All NL rows: profiles and keywords are Dutch; title filter defaults to **Eigenaar / Oprichter /
Directeur / Directeur-eigenaar**. Region = the city set as the Geography / Locations filter. Language: NL.

### A1. Trades (plumber, roofer, electrician, airco, locksmith, glazier)

| # | Niche | Region | Search query (paste) |
|---|---|---|---|
| 1 | Plumber | Amsterdam | `("loodgieter" OR "loodgietersbedrijf" OR "installatiebedrijf")` |
| 2 | Plumber | Rotterdam | `("loodgieter" OR "loodgietersbedrijf" OR "installatiebedrijf")` |
| 3 | Plumber | Den Haag | `("loodgieter" OR "loodgietersbedrijf" OR "installatiebedrijf")` |
| 4 | Plumber | Utrecht | `("loodgieter" OR "loodgietersbedrijf" OR "installatiebedrijf")` |
| 5 | Plumber | Eindhoven | `("loodgieter" OR "loodgietersbedrijf" OR "installatiebedrijf")` |
| 6 | Roofer | Amsterdam | `("dakdekker" OR "dakdekkersbedrijf" OR "dakspecialist")` |
| 7 | Roofer | Rotterdam | `("dakdekker" OR "dakdekkersbedrijf" OR "dakspecialist")` |
| 8 | Roofer | Breda / Tilburg | `("dakdekker" OR "dakdekkersbedrijf" OR "dakspecialist")` |
| 9 | Roofer | Arnhem / Nijmegen | `("dakdekker" OR "dakdekkersbedrijf" OR "dakspecialist")` |
| 10 | Roofer | Groningen | `("dakdekker" OR "dakdekkersbedrijf" OR "dakspecialist")` |
| 11 | Electrician | Amsterdam | `("elektricien" OR "elektrotechnisch installateur" OR "installatiebedrijf elektra")` |
| 12 | Electrician | Utrecht | `("elektricien" OR "elektrotechnisch installateur" OR "installatiebedrijf elektra")` |
| 13 | Electrician | Eindhoven | `("elektricien" OR "elektrotechnisch installateur" OR "installatiebedrijf elektra")` |
| 14 | Electrician | Zwolle | `("elektricien" OR "elektrotechnisch installateur" OR "installatiebedrijf elektra")` |
| 15 | Electrician | Haarlem | `("elektricien" OR "elektrotechnisch installateur" OR "installatiebedrijf elektra")` |
| 16 | Airco / HVAC | Amsterdam | `("airco" OR "airconditioning" OR "klimaatbeheersing" OR "koeltechniek")` |
| 17 | Airco / HVAC | Rotterdam | `("airco" OR "airconditioning" OR "klimaatbeheersing" OR "koeltechniek")` |
| 18 | Airco / HVAC | Eindhoven | `("airco" OR "airconditioning" OR "klimaatbeheersing" OR "koeltechniek")` |
| 19 | Airco / HVAC | Amersfoort | `("airco" OR "airconditioning" OR "klimaatbeheersing" OR "koeltechniek")` |
| 20 | Airco / HVAC | Den Haag | `("airco" OR "airconditioning" OR "klimaatbeheersing" OR "koeltechniek")` |
| 21 | Locksmith | Amsterdam | `("slotenmaker" OR "sleutelservice")` |
| 22 | Locksmith | Rotterdam | `("slotenmaker" OR "sleutelservice")` |
| 23 | Locksmith | Utrecht | `("slotenmaker" OR "sleutelservice")` |
| 24 | Locksmith | Den Haag | `("slotenmaker" OR "sleutelservice")` |
| 25 | Glazier | Amsterdam | `("glaszetter" OR "glasservice" OR "glasherstel")` |
| 26 | Glazier | Rotterdam | `("glaszetter" OR "glasservice" OR "glasherstel")` |
| 27 | Glazier | Eindhoven | `("glaszetter" OR "glasservice" OR "glasherstel")` |

Count: 27.

### A2. Home services (cleaning, pest control, garden, movers, security)

| # | Niche | Region | Search query (paste) |
|---|---|---|---|
| 28 | Cleaning | Amsterdam | `("schoonmaakbedrijf" OR "schoonmaakservice")` |
| 29 | Cleaning | Rotterdam | `("schoonmaakbedrijf" OR "schoonmaakservice")` |
| 30 | Cleaning | Utrecht | `("schoonmaakbedrijf" OR "schoonmaakservice")` |
| 31 | Cleaning | Den Haag | `("schoonmaakbedrijf" OR "schoonmaakservice")` |
| 32 | Pest control | Amsterdam | `("ongediertebestrijding" OR "plaagdierbeheersing")` |
| 33 | Pest control | Rotterdam | `("ongediertebestrijding" OR "plaagdierbeheersing")` |
| 34 | Pest control | Breda / Tilburg | `("ongediertebestrijding" OR "plaagdierbeheersing")` |
| 35 | Garden / landscaping | Utrecht | `("hovenier" OR "hoveniersbedrijf" OR "tuinaanleg")` |
| 36 | Garden / landscaping | Amersfoort | `("hovenier" OR "hoveniersbedrijf" OR "tuinaanleg")` |
| 37 | Garden / landscaping | Haarlem | `("hovenier" OR "hoveniersbedrijf" OR "tuinaanleg")` |
| 38 | Garden / landscaping | Arnhem / Nijmegen | `("hovenier" OR "hoveniersbedrijf" OR "tuinaanleg")` |
| 39 | Movers | Amsterdam | `("verhuisbedrijf" OR "verhuizer")` |
| 40 | Movers | Rotterdam | `("verhuisbedrijf" OR "verhuizer")` |
| 41 | Movers | Eindhoven | `("verhuisbedrijf" OR "verhuizer")` |
| 42 | Security / alarm | Amsterdam | `("beveiligingsbedrijf" OR "alarminstallatie" OR "camerabeveiliging")` |
| 43 | Security / alarm | Rotterdam | `("beveiligingsbedrijf" OR "alarminstallatie" OR "camerabeveiliging")` |
| 44 | Security / alarm | Eindhoven | `("beveiligingsbedrijf" OR "alarminstallatie" OR "camerabeveiliging")` |

Count: 17.

### A3. Health & beauty (dental, physio, skin/aesthetic, salon, vet)

| # | Niche | Region | Search query (paste) |
|---|---|---|---|
| 45 | Dental | Amsterdam | `("tandarts" OR "tandartspraktijk")` |
| 46 | Dental | Utrecht | `("tandarts" OR "tandartspraktijk")` |
| 47 | Dental | Rotterdam | `("tandarts" OR "tandartspraktijk")` |
| 48 | Dental | Groningen | `("tandarts" OR "tandartspraktijk")` |
| 49 | Physio | Amsterdam | `("fysiotherapie" OR "fysiotherapeut" OR "fysiopraktijk")` |
| 50 | Physio | Den Haag | `("fysiotherapie" OR "fysiotherapeut" OR "fysiopraktijk")` |
| 51 | Physio | Eindhoven | `("fysiotherapie" OR "fysiotherapeut" OR "fysiopraktijk")` |
| 52 | Physio | Zwolle | `("fysiotherapie" OR "fysiotherapeut" OR "fysiopraktijk")` |
| 53 | Skin / aesthetic clinic | Amsterdam | `("huidkliniek" OR "huidtherapie" OR "esthetische kliniek")` |
| 54 | Skin / aesthetic clinic | Rotterdam | `("huidkliniek" OR "huidtherapie" OR "esthetische kliniek")` |
| 55 | Skin / aesthetic clinic | Den Haag | `("huidkliniek" OR "huidtherapie" OR "esthetische kliniek")` |
| 56 | Hair / beauty salon | Amsterdam | `("kapsalon" OR "schoonheidssalon" OR "beautysalon")` |
| 57 | Hair / beauty salon | Utrecht | `("kapsalon" OR "schoonheidssalon" OR "beautysalon")` |
| 58 | Hair / beauty salon | Eindhoven | `("kapsalon" OR "schoonheidssalon" OR "beautysalon")` |
| 59 | Veterinary | Amsterdam | `("dierenarts" OR "dierenkliniek")` |
| 60 | Veterinary | Rotterdam | `("dierenarts" OR "dierenkliniek")` |
| 61 | Veterinary | Amersfoort | `("dierenarts" OR "dierenkliniek")` |

Count: 17.

### A4. Auto (garages, tyre, body repair)

| # | Niche | Region | Search query (paste) |
|---|---|---|---|
| 62 | Garage | Amsterdam | `("autobedrijf" OR "garagebedrijf")` |
| 63 | Garage | Rotterdam | `("autobedrijf" OR "garagebedrijf")` |
| 64 | Garage | Eindhoven | `("autobedrijf" OR "garagebedrijf")` |
| 65 | Garage | Utrecht | `("autobedrijf" OR "garagebedrijf")` |
| 66 | Tyre shop | Amsterdam | `("bandenspecialist" OR "bandenservice")` |
| 67 | Tyre shop | Breda / Tilburg | `("bandenspecialist" OR "bandenservice")` |
| 68 | Body / repair | Rotterdam | `("schadeherstel" OR "autoschade" OR "plaatwerk")` |
| 69 | Body / repair | Amsterdam | `("schadeherstel" OR "autoschade" OR "plaatwerk")` |
| 70 | Body / repair | Arnhem / Nijmegen | `("schadeherstel" OR "autoschade" OR "plaatwerk")` |

Count: 9.

### A5. Property & hospitality (property/VvE mgmt, holiday rental, estate agents)

| # | Niche | Region | Search query (paste) |
|---|---|---|---|
| 71 | Property / VvE mgmt | Amsterdam | `("vastgoedbeheer" OR "VvE-beheer" OR "vastgoedbeheerder")` |
| 72 | Property / VvE mgmt | Rotterdam | `("vastgoedbeheer" OR "VvE-beheer" OR "vastgoedbeheerder")` |
| 73 | Property / VvE mgmt | Den Haag | `("vastgoedbeheer" OR "VvE-beheer" OR "vastgoedbeheerder")` |
| 74 | Holiday-rental mgmt | Amsterdam | `("vakantieverhuur" OR "verhuurbeheer" OR "Airbnb beheer")` |
| 75 | Holiday-rental mgmt | Zeeland coast | `("vakantieverhuur" OR "verhuurbeheer" OR "recreatieverhuur")` |
| 76 | Holiday-rental mgmt | Veluwe | `("vakantieverhuur" OR "verhuurbeheer" OR "recreatieverhuur")` |
| 77 | Estate agent | Amsterdam | `("makelaar" OR "makelaarskantoor")` |
| 78 | Estate agent | Utrecht | `("makelaar" OR "makelaarskantoor")` |
| 79 | Estate agent | Eindhoven | `("makelaar" OR "makelaarskantoor")` |

Count: 9.

### A6. Professional services (accountants, law firms, insurance brokers)

| # | Niche | Region | Search query (paste) |
|---|---|---|---|
| 80 | Accountant / boekhouder | Amsterdam | `("boekhouder" OR "administratiekantoor" OR "accountantskantoor")` |
| 81 | Accountant / boekhouder | Rotterdam | `("boekhouder" OR "administratiekantoor" OR "accountantskantoor")` |
| 82 | Accountant / boekhouder | Utrecht | `("boekhouder" OR "administratiekantoor" OR "accountantskantoor")` |
| 83 | Accountant / boekhouder | Eindhoven | `("boekhouder" OR "administratiekantoor" OR "accountantskantoor")` |
| 84 | Small law firm | Amsterdam | `("advocaat" OR "advocatenkantoor")` |
| 85 | Small law firm | Den Haag | `("advocaat" OR "advocatenkantoor")` |
| 86 | Small law firm | Rotterdam | `("advocaat" OR "advocatenkantoor")` |
| 87 | Insurance broker | Amsterdam | `("assurantie" OR "verzekeringsadviseur" OR "financieel adviseur")` |
| 88 | Insurance broker | Utrecht | `("assurantie" OR "verzekeringsadviseur" OR "financieel adviseur")` |
| 89 | Insurance broker | Zwolle | `("assurantie" OR "verzekeringsadviseur" OR "financieel adviseur")` |

Count: 10.

**Section A (Netherlands) subtotal: 89.**

---

## Section B — International (expat hubs)

Title filter defaults to **Owner / Founder / Managing Director / General Manager** (add **Inhaber /
Geschaftsfuhrer** where the Lang note includes DE). Region = the Geography / Locations filter. The Lang
column is which languages the business likely serves — match your connection note to it. Airco and
holiday-rental management on Mallorca / Costa del Sol are the proven, highest-value angles.

### B1. Trades & technical (airco, pool, plumber, electrician)

| # | Niche | Region | Title filter | Search query (paste) | Lang |
|---|---|---|---|---|---|
| 90 | Airco / HVAC | Mallorca (Palma) | Owner / MD | `("air conditioning" OR "HVAC" OR "climate control" OR "aire acondicionado" OR "Klimaanlage")` | EN / DE / ES |
| 91 | Airco / HVAC | Costa del Sol / Marbella | Owner / MD | `("air conditioning" OR "HVAC" OR "climate control" OR "aire acondicionado" OR "Klimaanlage")` | EN / DE |
| 92 | Airco / HVAC | Alicante / Costa Blanca | Owner / MD | `("air conditioning" OR "HVAC" OR "climate control" OR "aire acondicionado")` | EN / DE |
| 93 | Airco / HVAC | Barcelona | Owner / MD | `("air conditioning" OR "HVAC" OR "aire acondicionado")` | EN / ES |
| 94 | Airco / HVAC | Algarve | Owner / MD | `("air conditioning" OR "HVAC" OR "climate control" OR "ar condicionado")` | EN / PT |
| 95 | Airco / HVAC | Dubai | Owner / MD | `("air conditioning" OR "HVAC" OR "AC maintenance" OR "chiller")` | EN |
| 96 | Pool maintenance | Mallorca | Owner / MD | `("pool maintenance" OR "pool service" OR "piscinas" OR "Poolservice")` | EN / DE / ES |
| 97 | Pool maintenance | Costa del Sol / Marbella | Owner / MD | `("pool maintenance" OR "pool service" OR "piscinas")` | EN / DE |
| 98 | Pool maintenance | Costa Blanca | Owner / MD | `("pool maintenance" OR "pool service" OR "piscinas")` | EN / DE |
| 99 | Pool maintenance | Algarve | Owner / MD | `("pool maintenance" OR "pool service" OR "piscinas")` | EN / PT |
| 100 | Plumber | Mallorca | Owner / MD | `("plumber" OR "plumbing" OR "fontanero")` | EN / DE / ES |
| 101 | Plumber | Costa del Sol / Marbella | Owner / MD | `("plumber" OR "plumbing" OR "fontanero")` | EN / DE |
| 102 | Plumber | Costa Blanca | Owner / MD | `("plumber" OR "plumbing" OR "fontanero")` | EN / DE |
| 103 | Electrician | Mallorca | Owner / MD | `("electrician" OR "electrical" OR "electricista")` | EN / DE / ES |
| 104 | Electrician | Costa del Sol / Marbella | Owner / MD | `("electrician" OR "electrical" OR "electricista")` | EN / DE |
| 105 | Electrician | Dubai | Owner / MD | `("electrician" OR "electrical services" OR "MEP")` | EN |

Count: 16.

### B2. Home services (cleaning, garden, pest, security)

| # | Niche | Region | Title filter | Search query (paste) | Lang |
|---|---|---|---|---|---|
| 106 | Villa cleaning | Mallorca | Owner / MD | `("villa cleaning" OR "cleaning company" OR "limpieza")` | EN / DE / ES |
| 107 | Villa cleaning | Costa del Sol / Marbella | Owner / MD | `("villa cleaning" OR "cleaning company" OR "limpieza")` | EN / DE |
| 108 | Villa cleaning | Costa Blanca | Owner / MD | `("villa cleaning" OR "cleaning company" OR "limpieza")` | EN / DE |
| 109 | Cleaning company | Dubai | Owner / MD | `("cleaning company" OR "cleaning services" OR "facility cleaning")` | EN |
| 110 | Garden / landscaping | Mallorca | Owner / MD | `("gardening" OR "landscaping" OR "jardineria")` | EN / DE / ES |
| 111 | Garden / landscaping | Costa del Sol / Marbella | Owner / MD | `("gardening" OR "landscaping" OR "jardineria")` | EN / DE |
| 112 | Pest control | Costa Blanca | Owner / MD | `("pest control" OR "control de plagas")` | EN / DE |
| 113 | Pest control | Algarve | Owner / MD | `("pest control" OR "controlo de pragas")` | EN / PT |
| 114 | Security / alarm | Costa del Sol / Marbella | Owner / MD | `("security systems" OR "alarm" OR "seguridad")` | EN / DE |
| 115 | Security / alarm | Mallorca | Owner / MD | `("security systems" OR "alarm" OR "seguridad")` | EN / DE / ES |

Count: 10.

### B3. Property & hospitality (villa / holiday-rental mgmt, property mgmt, estate agents)

| # | Niche | Region | Title filter | Search query (paste) | Lang |
|---|---|---|---|---|---|
| 116 | Villa / holiday-rental mgmt | Mallorca | Owner / MD | `("holiday rental" OR "villa management" OR "vacation rental" OR "short-let")` | EN / DE / ES |
| 117 | Villa / holiday-rental mgmt | Ibiza | Owner / MD | `("holiday rental" OR "villa management" OR "vacation rental")` | EN / DE / ES |
| 118 | Villa / holiday-rental mgmt | Costa del Sol / Marbella | Owner / MD | `("holiday rental" OR "villa management" OR "vacation rental" OR "short-let")` | EN / DE |
| 119 | Villa / holiday-rental mgmt | Costa Blanca | Owner / MD | `("holiday rental" OR "villa management" OR "vacation rental")` | EN / DE |
| 120 | Villa / holiday-rental mgmt | Algarve | Owner / MD | `("holiday rental" OR "villa management" OR "vacation rental")` | EN / PT |
| 121 | Villa / holiday-rental mgmt | Lisbon | Owner / MD | `("holiday rental" OR "short-let" OR "alojamento local")` | EN / PT |
| 122 | Villa / holiday-rental mgmt | Tenerife / Canaries | Owner / MD | `("holiday rental" OR "villa management" OR "vacation rental")` | EN / DE / ES |
| 123 | Short-let / vacation rental mgmt | Dubai | Owner / MD | `("holiday homes" OR "short-term rental" OR "vacation rental management")` | EN |
| 124 | Property management | Mallorca | Owner / MD | `("property management" OR "property manager")` | EN / DE / ES |
| 125 | Property management | Costa del Sol / Marbella | Owner / MD | `("property management" OR "property manager")` | EN / DE |
| 126 | Property management | Dubai | Owner / MD | `("property management" OR "owners association" OR "facility management")` | EN |
| 127 | Estate agent | Mallorca | Owner / MD | `("real estate" OR "estate agent" OR "inmobiliaria" OR "Immobilien")` | EN / DE / ES |
| 128 | Estate agent | Costa del Sol / Marbella | Owner / MD | `("real estate" OR "estate agent" OR "inmobiliaria" OR "Immobilien")` | EN / DE |
| 129 | Estate agent | Costa Blanca | Owner / MD | `("real estate" OR "estate agent" OR "inmobiliaria" OR "Immobilien")` | EN / DE |
| 130 | Estate agent | Barcelona | Owner / MD | `("real estate" OR "estate agent" OR "inmobiliaria")` | EN / ES |
| 131 | Estate agent | Algarve | Owner / MD | `("real estate" OR "estate agent" OR "imobiliaria")` | EN / PT |
| 132 | Estate agent | Lisbon | Owner / MD | `("real estate" OR "estate agent" OR "imobiliaria")` | EN / PT |
| 133 | Estate agent | Dubai | Owner / MD | `("real estate" OR "property broker" OR "real estate agency")` | EN |

Count: 18.

### B4. Health & beauty (aesthetic, dental, physio, salon)

| # | Niche | Region | Title filter | Search query (paste) | Lang |
|---|---|---|---|---|---|
| 134 | Aesthetic / skin clinic | Marbella | Owner / MD | `("aesthetic clinic" OR "skin clinic" OR "cosmetic clinic" OR "medical aesthetics")` | EN / DE / ES |
| 135 | Aesthetic / skin clinic | Mallorca | Owner / MD | `("aesthetic clinic" OR "skin clinic" OR "cosmetic clinic")` | EN / DE / ES |
| 136 | Aesthetic / skin clinic | Barcelona | Owner / MD | `("aesthetic clinic" OR "medical aesthetics" OR "clinica estetica")` | EN / ES |
| 137 | Aesthetic / skin clinic | Dubai | Owner / MD | `("aesthetic clinic" OR "medical aesthetics" OR "cosmetic clinic")` | EN |
| 138 | Dental clinic | Costa del Sol / Marbella | Owner / MD | `("dental clinic" OR "dentist" OR "dental practice")` | EN / DE |
| 139 | Dental clinic | Costa Blanca / Alicante | Owner / MD | `("dental clinic" OR "dentist" OR "clinica dental")` | EN / DE |
| 140 | Dental clinic | Algarve | Owner / MD | `("dental clinic" OR "dentist" OR "clinica dentaria")` | EN / PT |
| 141 | Dental clinic | Barcelona | Owner / MD | `("dental clinic" OR "dentist" OR "clinica dental")` | EN / ES |
| 142 | Physio / rehab | Marbella | Owner / MD | `("physiotherapy" OR "physio" OR "rehabilitation" OR "fisioterapia")` | EN / DE |
| 143 | Physio / rehab | Mallorca | Owner / MD | `("physiotherapy" OR "physio" OR "rehabilitation" OR "fisioterapia")` | EN / DE / ES |
| 144 | Hair / beauty salon | Marbella | Owner / MD | `("beauty salon" OR "hair salon" OR "spa")` | EN / DE |
| 145 | Hair / beauty salon | Dubai | Owner / MD | `("beauty salon" OR "hair salon" OR "spa")` | EN |

Count: 12.

### B5. Professional services (expat-facing)

| # | Niche | Region | Title filter | Search query (paste) | Lang |
|---|---|---|---|---|---|
| 146 | Accountant / gestoria | Costa del Sol | Owner / Partner | `("gestoria" OR "accountant" OR "tax advisor")` | EN / ES |
| 147 | Lawyer (expat) | Mallorca | Owner / Partner | `("abogado" OR "lawyer" OR "legal services")` | EN / DE / ES |
| 148 | Lawyer (expat) | Costa Blanca | Owner / Partner | `("abogado" OR "lawyer" OR "legal services")` | EN / DE |
| 149 | Insurance broker (expat) | Costa del Sol | Owner / MD | `("insurance broker" OR "seguros" OR "insurance advisor")` | EN / ES |
| 150 | Property / conveyancing lawyer | Dubai | Owner / Partner | `("legal consultant" OR "conveyancing" OR "property lawyer")` | EN |

Count: 5.

**Section B (International) subtotal: 61.**

---

## Totals

| Section | Rows |
|---|---|
| A. Netherlands | 89 |
| B. International | 61 |
| **Grand total** | **150** |

By vertical family (both sections combined):

| Vertical family | NL | Intl | Total |
|---|---|---|---|
| Trades & technical | 27 | 16 | 43 |
| Home services | 17 | 10 | 27 |
| Health & beauty | 17 | 12 | 29 |
| Auto | 9 | 0 | 9 |
| Property & hospitality | 9 | 18 | 27 |
| Professional services | 10 | 5 | 15 |
| **Total** | **89** | **61** | **150** |

---

## First 2 weeks — starter plan

Ten working days, one batch of ~15-20 personalized connects per day. Start where pain and
willingness-to-pay are highest and where we already have proof. Hit roughly these ~24 segments first.

**Proven international (highest WTP, first client already here) — days 1-4:**

- Airco Mallorca / Costa del Sol (rows 90, 91) — the exact profile of the first paying client; the pitch
  writes itself: missed after-hours guest and installation-quote calls.
- Pool maintenance Mallorca (row 96) — same seasonal, villa-driven, after-hours emergency pattern.
- Villa / holiday-rental management Mallorca, Ibiza, Marbella (rows 116, 117, 118) and property
  management Mallorca (row 124) — guests message 24/7 in multiple languages; this is the strongest
  overflow / after-hours story and high monthly value per client.
- Aesthetic clinic Marbella (row 134) + dental Marbella (row 138) — cash-pay expat clinics, high booking
  value per lead, clear "no front desk after 6pm" gap.

**High after-hours-emergency NL trades — days 5-8:**

- Airco Amsterdam / Rotterdam (rows 16, 17) — same seasonal spike as Mallorca, easy demo parallel.
- Locksmith Amsterdam / Rotterdam (rows 21, 22) — lockouts are pure after-hours emergency demand.
- Plumber Amsterdam / Rotterdam (rows 1, 2) — burst pipes and leaks call at night.
- Roofer Amsterdam (row 6) — storm-damage overflow.

**High-WTP NL services — days 9-10:**

- Dental Amsterdam (row 45) + skin/aesthetic Amsterdam (row 53) — high value per booking, staffed only
  in office hours.
- Property / VvE management Amsterdam (row 71) — constant tenant and owner inbound, no front desk.
- Security / alarm Amsterdam (row 42) — alarm-response inquiries are inherently 24/7.
- Garage Amsterdam (row 62) — steady inbound, one owner juggling the phone and the workshop.

Why this order: international first because it is proven and the note is easy to make specific; then the
NL trades whose demand is genuinely after-hours (airco, locksmith, plumber, roofer) where the 24/7
argument lands hardest; then the high-ticket clinics and property managers where a single captured lead
covers the subscription many times over. Rotate verticals across days so no single niche gets a burst of
requests from one account.

After two weeks, review which segments accepted and replied best in the pipeline board
(`python -m app.pipeline board`) and double down on the winners.
