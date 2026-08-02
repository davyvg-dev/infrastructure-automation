# Cold-call playbook

> The canonical doc for founder-led cold calling. Built 2026-08-02 from four research passes:
> Gong/Cognism call-data (90K–300M calls), NL telemarketing law + culture, AI-receptionist
> objection research, and the voltwerk call review. Spoken lines are Dutch; keep them
> AI-tell-free. Supersedes the script blocks in `call-sheet-2026-07-31.md`;
> `discovery-script.md` and `objection-handling.md` remain for booked Zoom calls but their
> pricing sections are stale — the offer below is canonical.

## 0. May I even call? — the resolved position

Manual cold calling **confirmed BV's on their kantoornummer** is legal (Tw 11.7 protects
natural persons only) and allowed by the founder. What stays forbidden:

- eenmanszaak / VOF / maatschap / CV / zzp — opt-in territory since **2021**. KvK rechtsvorm
  check before every dial (`pipeline qualify` holds until `--entity bv`).
- A monteur's 06 — call the kantoornummer, ask for the eigenaar.
- Cold WhatsApp, ever. WhatsApp only after they say yes to "mag ik u de link appen?" — that
  spoken yes is the opt-in.
- Any automation of the calling itself.
- Anonymous caller ID. Show +31 6 44 58 83 21.
- Calling after "bel me niet meer": log `pipeline call <slug> rejected --opt-out` on the spot —
  that writes the phone into the suppression list. This is a legal duty (recht van verzet),
  not politeness.

Older docs saying "don't cold call, period" (`compliance-kill-list.md` #6,
`gdpr-compliance.md`, `28-day-sprint.md`) predate the 2026-07-31 decision and carry a
superseded-note pointing here.

## 1. When to call

- **Windows, in order of expected connect:** 07:30–08:45 (in de bus, voor de eerste klus) and
  16:00–17:30 (terugrijden, offertes). Lunch 12:00–12:30 is the experiment window — log two
  weeks of outcomes per window and let `pipeline calls` decide. Your 50 local dials beat any
  US study.
- **Days:** Tuesday–Thursday. Monday morning and Friday afternoon never (vrijmibo; bouw
  crews often don't work Friday).
- **Right now it's bouwvak** — Midden (the Randstad list) is out 3–21 Aug. Voicemail-heavy
  weeks; a logged callback date is a win, not a failure. The real sprint starts the week of
  **24 August** — first week back, when the missed-calls-while-away pain is freshest. Use it:
  *"U bent net terug van de bouwvak — hoeveel voicemails stonden er?"*
- Call blocks are only calls. Admin in the dead midday hours.

## 2. The call — 90 seconds to 3 minutes

The data that shapes this structure: on cold calls the *seller* talks 55:45; winning calls
carry one unbroken ~35-second problem monologue, ~175 words/min, calm and low — not pumped.
"Send me some info" is a loss state; the only two wins are a demo agreed or a callback at a
named time.

### 2.1 Opener (10 sec)

Never *"bel ik gelegen?"* / *"belt het even gelegen?"* — the single worst opener ever measured
(0.9% vs 1.5% baseline; it hands them the exit). The bounded permission ask scores 7x better
(~11%). Always say *"de reden dat ik bel"* — 2.1x lift, the most replicated finding there is.

**Koud (Blok D/F/G1):**

> "Goedemiddag, Davy van Klantkraan. Ik overval u — mag ik 30 seconden, dan zegt u daarna
> zelf of het wat is? [ja] De reden dat ik bel: ik help [loodgieters/dakdekkers] in [regio]
> om gemiste telefoontjes en avond-aanvragen op te vangen. [pijn-hook van de belsheet-rij]."

**Gemaild (Blok B/E, mail 1–2 dagen oud — beste belmoment dat er bestaat):**

> "Goedemiddag, u spreekt met Davy van Klantkraan. Ik stuurde u [eergisteren] een mail — ik
> had voor [bedrijf] alvast een receptionist klaargezet die uw websitechat en WhatsApp
> opneemt. De reden dat ik bel: [de 'mail zei'-kolom als brug]. Mag ik er 30 seconden over
> vertellen?"

**Warm / via een contact:** name the mutual contact in the first sentence, rest as koud.

First-10-seconds job: sound like the opposite of a bedrijvengids/Google-vermelding scammer —
real name, real visible number, plainly what it is. No "ik heb maar heel even nodig"-tricks,
no superlatives.

### 2.2 Probleem-monoloog (30–40 sec, één adem, niet opknippen)

Paint the scene, one euro number, no AI-story. Sell the outcome; AI is the how, mentioned
once.

> "Wat wij zien bij [vak]: u staat op een klus, telefoon gaat, u kunt niet opnemen. Minder
> dan drie op de honderd bellers spreekt een voicemail in — twee van de drie bellen gewoon de
> volgende [loodgieter] in de rij. Dat is per gemiste klus €150 tot €400 weg. Wij zetten een
> digitale receptionist op uw websitechat en WhatsApp die dat opvangt: vragen beantwoorden,
> agenda inkijken, afspraak inplannen. En mist u een oproep, dan krijgt die beller meteen een
> WhatsApp — dus elke lead komt bij u binnen, u mist er geen één meer."

(That last line landed clean on the voltwerk call — keep it.)

### 2.3 Discovery (2–3 vragen, dan stil)

> "Hoe gaat dat nu bij u — als er 's avonds iemand belt of een appje stuurt?"

If they claim no pain, **dig, don't argue** (voltwerk mistake 2 — never "dit hoor ik
vaker..."):

> "Wat kost dat u — de klus stilleggen voor elk telefoontje?"
> "En als u op vakantie bent, of 's nachts?"
> "Hoeveel van die belletjes zijn kleine vragen die uw tijd niet waard zijn?"

Genuinely no pain after that → qualify out politely, log `rejected`, next. A Dutch no is a
no.

The decision question, before any close (voltwerk mistake 3 was skipping it):

> "Beslist u daar zelf over, of overlegt u met iemand?"

### 2.4 De demo-in-het-gesprek (the move no voice competitor can copy)

The cold call's goal is the demo, not the subscription (demos convert 35–50%; in-call closes
5–10%). And a demo *during* the call has zero delay and zero no-show:

> "Mag ik u 'm nu appen, terwijl we bellen? Stel 'm gerust een lastige vraag — vindt u er
> een gat in, dan houd ik op."

Their yes = the WhatsApp opt-in. Demo tabs open before the block starts
(`demo.klantkraan.nl/?client=<slug>`); Blok D without a branded demo shows `klantkraan.nl/demo`
plus *"morgen staat er een met uw naam en diensten op"*.

### 2.5 De vraag (alleen deze aanbieding — niets anders aanbieden, ooit)

> "We nemen tien oprichtersklanten aan, tot 30 september. Eerste maand €149 in plaats van
> €299, geen opstartkosten, 30 dagen geld-terug, binnen 48 uur live. Prijzen exclusief btw.
> Zal ik 'm voor u aanzetten?"

- Both cap numbers, every conversation, hold both. The cap is why it converts.
- **Prepay only after a verbal yes, never as opener:** "U kunt maandelijks betalen, of de
  eerste zes maanden in één keer — dan houdt u het oprichterstarief vast: €894 in plaats van
  €1.644. Ik stuur u nu een betaallinkje."
- Guarantee direction: *geld terug als het niks is* — never "als u tevreden bent" inverted
  (voltwerk mistake 1b).
- Ja gehoord → betaallink binnen het uur (`billing.py checkout`).
- Voice bestaat niet — verkoop alleen Chat; eerlijk zeggen als ernaar gevraagd wordt (dat
  werkte op de voltwerk-call).

### 2.6 Elke exit heeft een datum (voltwerk mistake 3)

"Ik stuur de link en we houden contact" is not an outcome. The two acceptable soft exits:

> "Ik app 'm nu meteen — mag ik u donderdag even terugbellen, eind van de middag of begin
> van de avond?"

> [genuinely on a roof] "Dan houd ik het kort — vanmiddag 16:30 als u in de bus zit, of
> morgen 7:45?"

Named time agreed → `pipeline call <slug> callback --next <datum>`. "Bel maar eens" without a
date converts like a voicemail.

## 3. Voicemail + cadence

Voicemail's measured job is not the callback (2–5%) — it doubles the reply rate of the email
you send right after (2.7% → 5.9%). Hard cap **2 voicemails per prospect**; a third drops you
below the no-voicemail baseline. No VM on attempt 1 (keep one unknown-number connect chance).
Under 20 seconds, no pitch:

> "Goedemiddag, Davy van Klantkraan. Ik heb voor [bedrijf] een digitale receptionist
> klaargezet die uw gemiste telefoontjes opvangt. Ik stuur u zo een mailtje met de link, dan
> ziet u het in één minuut. Ik probeer het [dinsdag] nog eens. Fijne dag."

**Cadence per prospect — 6 touches over ~15 working days, halt on any reply:**

| Dag | Touch |
|---|---|
| 1 | Dial (window A). No answer → nothing left |
| 3 | Dial (window B) + VM 1 + mail binnen het uur die de VM noemt |
| 4 | (mailed prospects: this is the existing 4-touch ledger doing its work) |
| 8 | Dial (other window) + VM 2 + mail |
| 14 | Laatste dial + breakup-mail ("ik laat u met rust; de demo blijft staan") |

Never twice in one day, always a different day/window than last attempt. Email is the
between-channel — WhatsApp only exists after their spoken yes.

## 4. Objecties — één zin, dan opnieuw afsluiten of loslaten

Half of all objections (49.5% measured) are reflexes, not positions. The pattern: **meegaan,
reden, één vraag** — never fight the reflex, never "ik begrijp je twijfel" / "veel van mijn
klanten zeggen hetzelfde" (patronising to Dutch ears), no anglicisms.

**Reflex-breker (geen tijd / geen interesse, seconde 5):**

> "Helemaal terecht — ik val u rauw op het dak. Eén vraag en dan laat ik u gaan: wie neemt er
> op als u onder een ketel ligt?"

| Objectie | Antwoord |
|---|---|
| Te duur | "Wat kost één gemiste klus? Eén geredde klus per week is €600–€1.600 per maand — dit kost €299, en de eerste maand €149 met geld-terug. Het risico ligt bij ons." Nooit de maandprijs verlagen; bij aarzelen → prepay. |
| Mijn klanten willen een mens | "De beller die uw voicemail krijgt, spreekt ook geen mens — die belt de volgende. Zeven op de tien Nederlanders appen liever dan bellen. En hij zegt er eerlijk bij dat hij digitaal is." |
| AI zegt straks iets doms / verkeerde prijs | "Kan niet — hij kent alleen uw prijslijst en alleen agendaslots die echt bestaan. Alles daarbuiten gaat naar u. Test 'm nu: vindt u een gat, dan geen deal." |
| Mijn vrouw / kantoor doet de telefoon | "Houden zo — dit is de aanvulling: 7 uur 's ochtends, lunch, na vijven, haar vakantie. Zij houdt het persoonlijke werk, wij de overloop." |
| Ik bel iedereen terug | "Tegen die tijd heeft twee derde al een ander. Een spoedbeller belt drie nummers in vijf minuten — wie het eerst reageert, heeft de klus. En het kost u uw avonden." |
| Ik heb werk genoeg | "Dan is dit geen leadmachine maar een filter: hij boekt de goede klussen en houdt de rest beleefd af. Vol is prima — onbereikbaar levert slechte reviews op." |
| Ik mis er niet zoveel | "Dat denkt iedereen — gemeten is het bij mkb 1 op de 4. Zullen we het gewoon een maand meten? Dan telt u wat hij opvangt." |
| Zo'n antwoordservice was niks | "Die krabbelt een briefje. Hier staat elk gesprek zwart-op-wit in WhatsApp, met een geboekte afspraak in uw agenda — er kan niks kwijtraken." |
| Klanten zijn oud, die appen niet | "Uw telefoonlijn blijft gewoon bestaan — dit vangt alleen wat er nu doorheen valt. En ook senioren appen liever: vier op de tien tegen twee op de tien die liever bellen." |
| Is dat wel legaal, AI? | "Sinds 2 augustus moet elke chatbot zich als AI bekendmaken — stond op NOS. Die van ons doet dat vanaf dag één. U bent hiermee juist meteen compliant." |
| Geen tijd voor gedoe / niet technisch | "Eén telefoongesprek van 20 minuten, ik doe de rest. Binnen 48 uur staat hij aan." |
| Eerst overleggen / over nadenken | "Natuurlijk. Ik app u de demo en de voorwaarden nu, dan heeft u iets om te laten zien — mag ik u donderdag terugbellen, eind van de middag?" |
| Stuur maar een mailtje | "Die heeft u al — ik zet 'm nu bovenaan uw inbox, met de demolink. Wanneer kan ik u terugbellen?" |
| Bouwvak / vakantie | "Juist dan mist u telefoontjes — hij vangt ze op terwijl u weg bent. Wanneer kan ik beter terugbellen?" (datum loggen) |
| Watermelon is €99 | Not at €99 — the comparable setup is €224 and still no agenda. Webshop of supportteam? Zeg eerlijk dat Watermelon dan beter past en loop weg. |
| Geen abonnement, wel eenmalig | Interest noteren, niets beloven — losse verkoop is geen product. |

One counter per objection, maximum. Second resistance → date or `rejected`, next dial.

## 5. Tracking — log every dial, no exceptions

The funnel is only as honest as the worst-logged no-answer. Everything lives in
`ai-receptionist/` (`./.venv/bin/python -m app.pipeline ...`):

**Before the block (10 min):** demo tabs open for the first three names; checkout CLI ready
(betaallink binnen het uur na een ja); belsheet hooks bij de hand; `pipeline calls` for due
callbacks — those dial first.

**Per dial (≤60 sec, direct na ophangen, nooit batchen):**

```
pipeline call <slug> <outcome> --note "..." [--next YYYY-MM-DD] [--opt-out]
```

Outcomes: `no-answer` `voicemail` `gatekeeper` `bad-number` | `callback` `talked` `demo`
`close` `rejected` (last five = reached). In the note, capture **their verbatim words** —
that's the callback opener ("u zei vorige week dat...") — plus anything promised. Objection
heard → tag it `obj:te-duur`, `obj:mens`, `obj:vrouw-doet-telefoon`, `obj:genoeg-werk`,
`obj:overleggen`, ... so trends are grep-able.

**After the block:** demo agreed → advance when it happens; ja → `pipeline sign` + betaallink
binnen het uur; reply per mail → binnen het uur antwoorden (grootste hefboom op close rate).

**Friday review (5 min):**

```
pipeline calls                      # funnel + due/planned callbacks
pipeline calls --since 2026-08-24   # this sprint only
grep -h "obj:" data/pipeline/*.yaml | grep -o "obj:[a-z-]*" | sort | uniq -c | sort -rn
```

Watch: connect rate per window (pick the winning window after 2 weeks), reach→demo, the
top objection of the week (feed its counter back into §4), and callback-date adherence.

## 6. What good looks like (so 30 dials of silence doesn't read as failure)

| Metric | Expect (avg skill) | Top decile |
|---|---|---|
| Connect (kantoornummers/mobiel) | 18–22% | — |
| Demo per conversation | ~5% | 11–17% |
| Dial → demo | 2–3% | 5%+ |
| 50 dials/week | 10–15 gesprekken, 1–2 demo's | 3–4 demo's |

Below 4% reply-equivalent after 100 dials → the hook is wrong, not the market: swap the
pijn-hook family (bereikbaarheids-gat before review-gat) before swapping the list.

## 7. Founder rules, restated

- Niets anders aanbieden. The voltwerk deviating terms (1e maand gratis, €150, dan €300) are
  honored for voltwerk alone, in writing, and never repeated.
- Every exit gets a named day/time.
- BV bevestigd vóór de dial; twijfel = `hold`, eerst KvK.
- "Stop" → `--opt-out`, alle kanalen, voorgoed.
- Log the dial before the next dial.
