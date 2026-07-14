# Pilot → paid conversion + case-study template

> Sprint asset #4 (`02-sales/28-day-sprint.md`). Two jobs: (1) turn a day-14 free pilot into a
> paying Chat customer, led by the pilot's OWN numbers, and (2) turn that same pilot into a
> proof asset the growth engine can post. Dutch is customer-facing; internal notes are English.
> Only claim metrics the receptionist actually captures: gesprekken gevoerd, afspraken
> ingepland, terugbelverzoeken/leads vastgelegd, aandeel buiten kantooruren.

---

## Part 1 — De conversie

**The whole close is the weekly report.** You are not selling features on day 14 — you are
showing them what they nearly missed. Instrument every pilot from hour one so the numbers exist.

### Timing ladder

| Dag | Touch | Doel |
|---|---|---|
| 3 | Check-in | "Staat alles goed? Iets bijstellen?" — geen verkoop, alleen zorgen dat 't goed draait |
| 10 | Preview | Stuur de tussenstand mét cijfers. Warmt de close op, geen vraag nog |
| 14 | De vraag | Results-led, assumptief. Houden of niet |
| 16 | Follow-up | Als dag 14 stil bleef: één herinnering, dan stoppen |

### Dag 10 — preview (cijfers, nog geen vraag)
```
Hoi {{voornaam}}, kleine tussenstand van je AI-receptionist deze eerste
anderhalve week:

- {{X}} gesprekken gevoerd
- {{Y}} afspraken ingepland
- {{Z}} terugbelverzoeken vastgelegd
- {{P}}% daarvan buiten kantooruren — precies de klussen die anders
  langs je neus voorbij waren gegaan

Nog vier dagen te gaan. Iets wat je anders wilt hebben? Zeg 't gerust.
```

### Dag 14 — de conversie (results-led, assumptief)
```
Hoi {{voornaam}}, je pilot loopt vandaag af. De eindstand:

- {{X}} gesprekken, {{Y}} afspraken ingepland, {{Z}} leads vastgelegd
- {{P}}% buiten kantooruren

Dat zijn {{Y}} afspraken die je er anders naast had kunnen grijpen. Bij een
gemiddelde klus van €{{klusbedrag}} verdient hij zichzelf ruim terug — hij
kost €299 per maand.

Zal ik 'm gewoon voor je laten staan? Dan loopt-ie door, maandelijks
opzegbaar, en stuur ik je de opdrachtbevestiging (SEPA, zo geregeld).

Wil je 'm niet houden? Ook prima — dan zet ik 'm netjes uit, geen kosten.
```

### Als ze "ja" zeggen
1. Stuur de 1-page offerte (`02-sales/offerte-template.md`) — setup €0 (pilot), €299/mnd, maandelijks opzegbaar, 30-dagen geld-terug.
2. SEPA-machtiging via het ondertekenmoment (PandaDoc/SignWell).
3. Bevestig: hij blijft gewoon draaien, geen onderbreking, geen nieuwe inrichting.
4. Vraag het testimonial (Part 2) nu het enthousiasme vers is.

### Als ze twijfelen
- Echte bezwaren → `02-sales/objection-handling.md`. De meest voorkomende bij dag 14:
  - *"Ik moet het nog even zien"* → "Snap ik. Zal ik 'm 7 dagen laten doorlopen? Dan heb je een vollere maand aan cijfers." (verlengen is goedkoop, het bewijs stapelt zich op)
  - *"Te duur"* → reken terug naar één gemiste klus. Eén afspraak per maand betaalt 'm al.
  - *"Geen tijd om te wisselen"* → er is niets te wisselen; hij draait al. Doorgaan = niets doen.

### Als ze "nee" zeggen
```
Helemaal goed, dank dat je 'm een kans gaf. Twee korte vragen, puur zodat
ik 'm beter maak: wat had 'm voor jou wél de moeite waard gemaakt, en klopte
er iets niet aan de cijfers?

Mocht het later toch spelen — je pilot staat binnen een dag weer live.
```
- Werkte hij goed maar was de timing verkeerd? Vraag alsnog om een testimonial en zet een
  herinnering over 3 maanden.
- Log de reden. Terugkerende "nee"-redenen sturen de volgende sprintronde.

### Optionele hefboom: "founding 10" prijsvast
Voor de eerste 10 klanten van de julironde: **€299 vast voor 12 maanden** ("jij bent een van de
eersten, jouw prijs beweegt niet mee"). Een prijsgarantie sluit beter dan korting — het verlaagt
de prijs niet en dus ook niet de waarde. Alleen inzetten als iemand op het randje twijfelt.

---

## Part 2 — Case-study template

A live pilot with real numbers is your single most persuasive marketing asset. This turns one
into raw material for the growth engine (`growth-engine/` → Telegram approval → posts). Fill one
per pilot that produced results.

### Toestemming eerst (niet-onderhandelbaar)
- [ ] Klant akkoord dat we hun **bedrijfsnaam** noemen? Zo nee → geanonimiseerde variant.
- [ ] Klant akkoord met het **citaat** zoals hieronder genoteerd?
- [ ] Cijfers komen uit het echte weekoverzicht (geen afronding naar boven, geen verzinsels).

Geen toestemming voor de naam = prima, gebruik de geanonimiseerde variant. Nooit een klant
citeren of noemen zonder expliciet "ja".

### De template (vul in)
```
Bedrijf:            {{bedrijf}} — {{stad}}, {{branche}}
Situatie vooraf:    {{de pijn in 1 zin, bv. "miste geregeld klussen omdat
                    de telefoon tijdens het werk naar voicemail ging"}}
Pilotperiode:       {{14 dagen, DD-MM t/m DD-MM}}
Resultaat:
  - {{X}} gesprekken gevoerd
  - {{Y}} afspraken ingepland
  - {{Z}} leads / terugbelverzoeken vastgelegd
  - {{P}}% buiten kantooruren afgevangen
Citaat klant:       "{{echte quote, in hun eigen woorden}}"
                    — {{voornaam of "de eigenaar"}}, {{bedrijf}}
Toestemming naam:   ja / nee (bij nee → geanonimiseerd)
```

### Geanonimiseerde variant (bij geen naam-toestemming)
> "Een installatiebedrijf uit {{regio}} ving in twee weken {{Y}} afspraken af die anders
> waren blijven liggen — {{P}}% daarvan buiten kantooruren."

### Doorgeven aan de growth-engine
- Lever dit als één ingevuld blok aan; de growth-engine giet het per platform in de juiste vorm
  (X / LinkedIn / Reddit / Facebook) met eigen goedkeuring via Telegram.
- Config blijft leidend: het past onder de bestaande pijler over gemiste oproepen / bereikbaarheid
  in `config/content_strategy.yaml`. Voeg geen nieuwe claim toe die niet in het weekoverzicht staat.
- Geen bedragen (omzet/klusprijs) publiceren tenzij de klant daar apart akkoord op geeft —
  aantallen en percentages zijn genoeg en veiliger.

### Toon
- Nuchter, cijfermatig, Nederlands. Geen superlatieven, geen emoji.
- Het bewijs zit in de aantallen, niet in bijvoeglijke naamwoorden.
