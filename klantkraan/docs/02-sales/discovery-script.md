# Discovery Call Script — 20 min Zoom

> Goal: from cold-warm prospect to signed offerte within 14 days. ≤ 90 minutes founder time per closed deal.

## Pre-call (auto, 0 min founder time)

- Cal.com confirms with WhatsApp + email reminder.
- 2 hours before: auto-WhatsApp "Sta je nog klaar voor onze call om {{tijd}}? Zo niet, reply 'verzet'."
- Fathom records + transcribes (Dutch).
- n8n drops latest Attio data + their public-Google-profile review snapshot into founder's Zoom side-panel.

## Structure (20 min)

| Phase         | Time          | Purpose                                                         |
| ------------- | ------------- | --------------------------------------------------------------- |
| Rapport       | 0:00 – 2:00   | Set context, set length                                         |
| Qualification | 2:00 – 10:00  | Discover pain, qualify, build trust                             |
| Demo          | 10:00 – 16:00 | Live web-chat receptionist (websitechat + WhatsApp) + dashboard |
| Close         | 16:00 – 20:00 | Tier rec, objection handling, propose start date                |

## Phase 1: Rapport (2 min)

> "Hoi {{voornaam}}, dank voor je tijd. Ik hou het kort — 20 minuten, geen slides. Klopt dat?"

Wait for confirmation. Establish frame: kort, geen pitch.

> "Ik stel je een paar vragen, dan laat ik kort horen hoe het werkt, en dan kijken we of het past. Eerlijk, geen geneuzel."

## Phase 2: Qualification (8 min)

Ask these in order. Type answers into Attio open in another window.

1. **"Hoeveel inkomende telefoontjes krijg je per week, ruwe schatting?"**
   → looking for: 15–60. Below 10 = disqualify (no volume to recover).

2. **"Welk percentage pak je niet op — eerlijk?"**
   → looking for: 20–40%. They underestimate. Probe: "wat doe je als je op een dak staat?"

3. **"Wat doe je nu: voicemail, doorschakelen naar familie, antwoordservice?"**
   → most common: voicemail or partner. Antwoordservice gebruikers = mid-funnel competitor benchmark.

4. **"Wat kost een gemiddelde klus jou aan omzet?"**
   → loodgieter: €300–1,200; dakdekker: €4,500–30,000. Anchors ROI.

5. **"Wat is je grootste irritatie aan hoe het nu loopt?"**
   → listen for the _emotional_ answer. This is the language for the close.

6. **"Heb je eerder iets met software of AI geprobeerd? Wat ging er mis?"**
   → reveals trust hurdles + previous bad-vendor objections. Map to objection-handling table.

7. **"Wie beslist hierover — jij alleen, of overleg je met iemand?"**
   → if alleen → close today. If partner/accountant → schedule follow-up.

8. **"Als dit werkt, wat mag het per maand kosten — ruwe orde grootte?"**
   → never reveal price first. €200+ → Chat (€299) fits. If they push on missed _calls_ specifically → note as Compleet (voice) candidate for when the AI-telefonist is live; sell Chat today.

## Phase 3: Demo (6 min)

### Live chat demo (3 min including comment)

Screenshare the Klantkraan demo receptionist (web chat, `klantkraan-demo` config). Type a spoed-lek scenario as the customer: the AI asks the right questions, offers real agenda slots, books the appointment, captures the terugbelverzoek. Single comment:

> "Dat is letterlijk wat hij voor jou gaat doen — op je website én op WhatsApp, getuned op jouw diensten en tarieven."

### Dashboard screenshare (3 min)

Share screen. Show a test client's `/r/{slug}` Cloudflare Pages dashboard:

- Tile 1: AI-opgenomen calls deze week
- Tile 2: Gemiste klanten teruggewonnen
- Tile 3: Nieuwe Google reviews
- Tile 4: Geboekte afspraken
- Transcript list: laatste 5 calls met intent + audio-link

Comment: "Deze pagina komt elke maandag in je mailbox. Eén link, geen wachtwoord, geen app."

## Phase 4: Close (4 min)

### Tier recommendation

Based on Phase 2 answers, recommend one tier. Be confident:

> "Op basis van wat je vertelt past **Klantkraan Chat** bij je: €299 per maand, eerste maand 50% korting dus €149,50. Eenmalige setup €249 — die vervalt voor pilotklanten. Maandelijks opzegbaar, live binnen 7 werkdagen."

If they ask about phone calls: "De AI-telefonist op je eigen nummer is de volgende stap — Klantkraan Compleet, €499 per maand. Zodra die live is, sta jij bovenaan de lijst." Never promise a date.

### Two options close

> "Twee opties:
> **A.** Ik stuur nu de offerte per mail, jij tekent digitaal vandaag, we starten maandag.
> **B.** Ik stuur de offerte binnen 24 uur en jij laat me uiterlijk vrijdag weten.
> Welke?"

**Then SHUT UP.** First to speak loses. Silence is uncomfortable; let it work.

### If objection → handle (see `02-sales/objection-handling.md`)

After handling, re-close with same A/B structure.

### If still hesitant

> "Ik begrijp het. Wat zou je nu nog twijfel geven?"

Listen. Address the _real_ objection (usually #1 or #2 in the table). Re-close.

### If hard "no"

> "Helemaal goed. Mag ik je over 3 maanden nog een keer pollen?"

Note in Attio with reason code. Drop into newsletter list with consent.

## Post-call (5 min founder time)

- Attio: move to Discovery Done.
- Send WhatsApp recap within 10 min:
  > "Dank voor het gesprek {{voornaam}}. Zoals afgesproken: offerte komt binnen 24u in je mail. Vragen tussendoor? App me hier."
- Trigger n8n → PandaDoc offerte draft generated from template with auto-filled tier, prices, BTW.
- Founder reviews + sends.

## Discovery → close benchmarks

| Stage                     | Target | If below                                                    |
| ------------------------- | ------ | ----------------------------------------------------------- |
| Show rate                 | 80%    | Improve reminder cadence; WhatsApp T-2h is non-optional.    |
| Discovery → Proposal      | 80%    | Re-check qualification — are unfit leads making it through? |
| Proposal → Won            | 35%    | Review the close language; review pricing presentation.     |
| End-to-end (booked → won) | ~22%   | Review entire script.                                       |

## Founder time per closed deal

| Step                                              | Time       |
| ------------------------------------------------- | ---------- |
| Pre-call review                                   | 3 min      |
| Discovery call                                    | 20 min     |
| Recap + offerte send                              | 10 min     |
| 2 follow-ups average                              | 10 min     |
| Onboarding (separate, 130 min — see delivery doc) | —          |
| **Total sales time**                              | ~45 min    |
| **Buffer for negotiation / re-close**             | 25 min     |
| **Target ceiling**                                | **90 min** |

## Source

- Hofstede NL: https://www.hofstede-insights.com/country/the-netherlands/
- NL B2B SMB SaaS sales cycle benchmark (~7-21 days for <€1k/mo): https://optif.ai/learn/questions/sales-cycle-length-benchmark/
- Demo show-rate improvement via WhatsApp reminders: research summary in `02-sales/funnel-benchmarks.md`
