# Copy review: service pages (copy-services, 2026-11-17)

Scope: `apps/marketing-site/src/pages/{ai-receptionist,website-onderhoud,automatiseringen,advertentievideos,prijzen,gratis,klein-beginnen}.astro`, including text passed as props. Read rendered at 1440 and 393 wide (Playwright innerText) before and after. Text only; no code, hrefs, ids, classes or markup changed. Euro amounts now use a no-break space (`€ 299`), as `eur()` in services.ts does.

House choices applied on these pages:
- Headings without a closing period (questions keep "?"). Exception: the lit-word brand device in the hero and final CTA ("aan.", "zelf.").
- "Per maand opzegbaar" (not "Maandelijks opzegbaar"), "aanvraag" (not "lead"), "inrichting" (not "setup"), "dag en nacht" (not "24/7"), "btw" lower case, "versies" (not "varianten") for the ad videos.

## ai-receptionist.astro (30 changes)

| old | new | why |
|---|---|---|
| U staat op een dak of u ligt al in bed, en net dan ... De digitale receptionist van Klantkraan beantwoordt hem ... | U staat op een dak of ligt al in bed, en net dan ... De AI-receptionist van Klantkraan beantwoordt hem ... | cut (double "u"); same term for the service |
| panelAria: ... de digitale receptionist plant een afspraak ... | ... de AI-receptionist plant een afspraak ... | same term |
| Wat de receptionist doet terwijl u aan het werk bent. | Wat de receptionist doet terwijl u aan het werk bent | heading period |
| Met uw diensten, tarieven en werkgebied. Geen verzonnen prijzen, alleen wat u heeft ingesteld. | Met uw diensten, tarieven en werkgebied. Hij noemt alleen prijzen die u heeft ingesteld. | AI tell ("Geen X, alleen Y") |
| Alleen op momenten die in uw agenda vrij zijn. U ziet het meteen. | Alleen op tijden die vrij zijn in uw agenda. U ziet de afspraak meteen staan. | clarity ("het" had no clear referent) |
| Stel hem een vraag zoals uw klant dat zou doen. | Stel hem een vraag zoals uw klant dat zou doen | heading period |
| ... Typ een vraag of plan een afspraak. U heeft er geen account voor nodig. | ... Typ een vraag of plan een afspraak. Een account is niet nodig. | cut |
| iframe title: Live chat met de digitale receptionist van Klantkraan | Live chat met de AI-receptionist van Klantkraan | same term |
| Chat als een klant. Stel een vraag of plan een afspraak. Opent op volledig scherm. | Chat zoals een klant dat doet. De demo opent op volledig scherm. | cut (repeated the sub right above) |
| Voorbeeldbedrijf · bij uw eigen receptionist staan uw diensten en tarieven ingesteld | Voorbeeldbedrijf · uw eigen receptionist kent uw diensten en tarieven | cut; "Voorbeeldbedrijf" kept |
| Wat gemiste oproepen u per maand kosten. | Wat gemiste oproepen u per maand kosten | heading period |
| Wie geen antwoord krijgt, belt de volgende in de lijst. Hieronder een voorbeeld met 40 oproepen per week. In de rekentool vult u uw eigen aantallen in. | Wie geen antwoord krijgt, belt de volgende in de lijst. | cut (the ledger caption says "40 oproepen per week", the button says "Reken met uw eigen cijfers") |
| €450 / ± €7.200/mnd | € 450 / ± € 7.200/mnd | number format |
| Uw klant weet altijd dat hij met een assistent praat. | Uw klant weet altijd dat hij met een assistent praat | heading period |
| ... Daar loopt u een boete mee op. Met Klantkraan niet. | ... Daarmee riskeert u een boete. | AI tell (staccato tag); "loopt op" stated the fine as certain, and "Met Klantkraan niet" implied a legal guarantee |
| Lees de volledige disclosure | Lees de AI-disclosure | clarity: matches the target page's H1; "volledige" was filler |
| Zo start u. Binnen een week staat hij live. | Binnen een week staat hij live | cut (the numbered steps show it is "how to start"); two sentences in a heading |
| Vijf minuten werk. U rekent direct af via Mollie: eerste maand €149,50, daarna €299 per maand, excl. btw. | Dat kost vijf minuten. U betaalt direct via Mollie: de eerste maand € 149,50, daarna € 299 per maand, excl. btw. | grammar (full sentence); number format |
| Binnen één werkdag bellen we om ... door te nemen. U hoeft niets te bouwen. | Binnen één werkdag bellen we om ... door te nemen. | cut (step title already says "Wij bouwen uw receptionist") |
| U test hem zelf en geeft akkoord. Vanaf dat moment neemt hij elke vraag aan, dag en nacht. | U test hem zelf en geeft akkoord. Daarna neemt hij elke vraag aan, dag en nacht. | cut |
| Per maand opzegbaar. Geen jaarcontract, geen verborgen verlenging; opzeggen per mail, geen opzegtermijn. | Per maand opzegbaar, zonder jaarcontract of verborgen verlenging. Opzeggen gaat per mail, zonder opzegtermijn. | AI tell ("Geen X, geen Y" staccato); all four terms kept |
| Wat hij nu doet, en wat er nog komt. | Wat hij nu doet en wat er nog komt | grammar (no comma before "en"); heading period |
| Nu vangt de receptionist alles op wat binnenkomt terwijl u werkt. Daarna willen we het papierwerk aanpakken dat u nu ’s avonds ... | Als volgende stap willen we het papierwerk aanpakken dat u nu 's avonds ... | cut (first sentence repeated the "now" list beside it); straight apostrophe as in the hero |
| nowLabel: Wat hij nu doet / laterLabel: Wat we bouwen / laterNote: Nog niet in het abonnement. U betaalt er nu niet voor. | Nu in het abonnement / Nog niet in het abonnement / U betaalt er nu niet voor. | cut (label repeated the heading); clearer pair |
| Vangt terugbelverzoeken met naam, nummer en klus / Meldt zichzelf als digitale assistent, in elk gesprek | Noteert terugbelverzoeken met naam, nummer en klus / Meldt zich in elk gesprek als digitale assistent | grammar ("vangt" needs "op"); same wording as services.ts and the flow step "Noteert" |
| Reviewverzoeken op het moment dat de klus net klaar is | Reviewverzoeken zodra de klus klaar is | cut |
| Wilt u een van deze nu al? Dan bouwen we het als losse automatisering, met een vaste prijs vooraf. | Wilt u er nu al een? Dan bouwen we die als losse automatisering, voor een vaste prijs vooraf. | grammar ("een van deze ... het": de-word needs "die") |
| Stel de receptionist in de demo een vraag alsof u een klant bent. Bevalt het? Meld u aan, dan bellen we binnen één werkdag om hem voor uw bedrijf in te richten. | Stel in de demo een vraag zoals een klant dat doet. Bevalt het, meld u dan aan. Binnen één werkdag bellen we om hem voor uw bedrijf in te richten. | AI tell (rhetorical question); cut |
| alt: Vanuit de cabine van een werkbus in een Nederlandse straat: werkbonnen, een rolmaat en werkhandschoenen op de stoel. | Werkbonnen, een rolmaat en werkhandschoenen op de stoel van een werkbus, in een Nederlandse straat. | colon reveal; object first |
| meta: ... plant afspraken en vangt leads, dag en nacht. Done-for-you setup. Per maand opzegbaar. | ... plant afspraken en noteert terugbelverzoeken, dag en nacht. Wij richten hem in. Per maand opzegbaar. | anglicisms |

Kept on purpose: "U chat met een digitale assistent." (word for word, twice); the customer lines "Werken jullie ook in Haarlem?" (the customer speaks, not the site); the title (a test pins it).

## website-onderhoud.astro (6 changes)

| old | new | why |
|---|---|---|
| Uw site in het midden, vier dingen die blijven lopen. | Vier dingen die blijven lopen | cut (described the drawing); heading period |
| Wat zit erin voor € 45 per maand | Dit krijgt u voor € 45 per maand | grammar (a question without "?") |
| Elke dag een kopie van de hele site, zodat ... | Een kopie van de hele site, zodat ... | cut (the item title is "Elke dag een back-up") |
| Bewaking: online en veilig | Bewaking of de site online en veilig is | clarity; same wording as services.ts and the drawing's aria |
| Website-onderhoud is er voor sites op WordPress. | Alleen voor sites op WordPress. | cut; same claim |
| eyebrow: Eerst opruimen? | Eerst opruimen | two questions in a row (eyebrow and heading) |

## automatiseringen.astro (11 changes)

| old | new | why |
|---|---|---|
| H1: Het werk na de klus, dat loopt vanzelf | Het werk na de klus loopt vanzelf | grammar; same as services.ts promise |
| Een offerte die niemand opvolgt, een herinnering die niemand stuurt, een factuur die blijft openstaan. Dat werk kan zichzelf doen. Wij bouwen het op maat, voor een vaste prijs vooraf. | De herinnering voor een offerte of een openstaande factuur gaat vanzelf de deur uit. Wij bouwen dat op maat, voor een vaste prijs vooraf. | AI tell (forced triad, vague "Dat werk kan zichzelf doen") |
| eyebrow: Zo werkt de Offerte-opvolger / h2: Zo volgt een offerte zichzelf op. | Offerte-opvolger / Zo volgt een offerte zichzelf op | cut ("Zo ... Zo"); heading period |
| Na een paar dagen een nette herinnering, die stopt zodra de klant antwoordt. | Een nette herinnering als de klant na een paar dagen niet reageert. | cut (the drawing section right above says when it stops) |
| Een verzoek om een review op het moment dat de klus net klaar is. | Een verzoek om een review, zodra de klus klaar is. | cut |
| Elk van deze bouwen we op maat, voor uw bedrijf. | Elk van deze bouwen we op maat. | cut |
| Eerst gratis kijken, dan een vaste prijs. | Eerst gratis kijken, dan een vaste prijs | heading period |
| Stap 1 title: Gratis scan | Scan | cut (the price line under it says "Gratis") |
| Stap 2: Vaste prijs vooraf / U weet wat het kost voordat we beginnen. Daarna bouwen we het op maat. | Bouw op maat / U krijgt vooraf een vaste prijs. Daarna bouwen we het. | cut (title and body said the same) |
| Eerst één ding laten lopen? | Begin met de offertes | AI tell (rhetorical question) |
| Begin met de offertes. Bevalt het, dan bouwen we daarna verder. | Bevalt het, dan bouwen we verder. | cut ("daarna" doubled "dan"; first sentence moved into the heading) |

## advertentievideos.astro (11 changes)

| old | new | why |
|---|---|---|
| title / meta / H1 / step title: zestien varianten | zestien versies | same term as services.ts, magnets.ts and the mini offer ("Zestien versies van één video") |
| Hetzelfde beeld met telkens een andere openingszin, andere muziek en een andere volgorde. Klaar voor Meta en TikTok, staand formaat. | Hetzelfde beeld, telkens met een andere openingszin, muziek en volgorde. In staand formaat, klaar voor Meta en TikTok. | cut |
| U zet de varianten naast elkaar ... De cijfers laten zien welke eerste seconden het beste werken. | U zet de versies naast elkaar ... De cijfers laten zien welke het beste werkt. | same term; cut |
| aria-label: Voorbeeldvariant met de opening ... | Voorbeeldversie met de opening ... | same term |
| eyebrow over the form: Gratis | Probeer het eerst | cut (the heading from magnets.ts already ends in "gratis") |
| placeholder: Link naar uw advertentie | https:// | the placeholder repeated the label |
| label: Uw webshop | Webadres van uw webshop | clarity (the field wants a web address) |
| Hier sturen we de openingen naartoe. Daarna sturen we u af en toe ... | ... Daarna mailen we u af en toe ... | double "sturen" |
| Dat ging niet goed. Probeer het nog een keer, of mail ... | Het versturen lukte niet. Probeer het opnieuw, of mail ... | clarity |
| Daarna maken we drie nieuwe openingen en heeft u ze binnen 5 werkdagen. | Daarna heeft u de drie openingen binnen 5 werkdagen. | cut |
| ... vangt de aanvragen op die binnenkomen. Met deze varianten haalt u meer uit de advertenties die die aanvragen opleveren. Wilt u zien hoe het er met uw eigen video uitziet? Stuur hem op, dan krijgt u eerst drie nieuwe openingen terug, gratis. Liever mailen of appen kan ook. | ... vangt de aanvragen op die binnenkomen; met deze versies haalt u meer uit de advertenties die ze opleveren. Liever mailen of appen dan het formulier invullen? Stuur uw video, dan krijgt u ook eerst drie nieuwe openingen gratis terug. | grammar ("die die", "Liever mailen of appen kan ook"); rhetorical question; the block's message and audience left as is (open decision) |

## prijzen.astro (27 changes)

| old | new | why |
|---|---|---|
| title: Chat €299 of Compleet €499 | Chat € 299 of Compleet € 499 | number format |
| meta: Chat €299 en Compleet €499 per maand. ... Wij richten hem volledig in ... Maandelijks opzegbaar. | Chat € 299 en Compleet € 499 per maand, excl. btw. ... Wij richten hem in ... Per maand opzegbaar. | added the btw qualifier; AI tell ("volledig"); same term |
| Maandelijks opzegbaar, eerste maand 50% korting. Eenmalige setup vanaf €249 (kwijtgescholden voor pilotklanten). Alle bedragen excl. 21% BTW. | Per maand opzegbaar, eerste maand 50% korting. Eenmalige inrichting vanaf € 249, gratis voor pilotklanten. Alle bedragen zijn excl. 21% btw. | same term; anglicism; spelling (btw); number format |
| €{price} /mnd, ≈ €{dayPrice} per dag | € {price} /mnd, ≈ € {dayPrice} per dag | number format |
| Chat: Plant afspraken direct in uw agenda en vangt elke lead op, via websitechat en WhatsApp, 24/7 in het Nederlands. Wij richten hem volledig voor u in. Onze aanrader. | Beantwoordt vragen via websitechat en WhatsApp, dag en nacht, in het Nederlands. Plant afspraken direct in uw agenda. Wij richten hem voor u in. | one promise per sentence; anglicism; "24/7"; AI tell ("volledig"); cut ("Onze aanrader" repeated the badge) |
| incl. 750 belminuten/mnd, daarna €0,40/min | incl. 750 belminuten per maand, daarna € 0,40 per minuut | number format, no abbreviations in running text |
| Compleet: ... een AI-telefonist die uw telefoon 24/7 opneemt op een eigen Nederlands nummer. | ... een AI-telefonist die dag en nacht uw telefoon opneemt, op een eigen Nederlands nummer. | "24/7" (voice guide) |
| Liever eerst proberen? Bekijk de demo | Of probeer eerst de demo | AI tell (rhetorical question) |
| Niets. Wij richten hem in. | Wij richten hem in, u kijkt mee | "Niets" was not true (the list says "U kijkt mee"; the start steps say "U test hem zelf"); punchline heading |
| Een chatbot kopen is één ding. Er een receptionist van maken die uw tarieven kent en uw agenda vult, is werk. Dat werk is van ons. | Een receptionist die uw tarieven kent en uw agenda vult, vraagt werk. Dat werk doen wij. | AI tell ("X is één ding"); the chatbot contrast stays once, at the end of the section |
| Zodat een afspraak er direct in staat, en niet als briefje in een inbox belandt. | Een afspraak komt direct in uw agenda, niet als briefje in een inbox. | grammar (sentence started with "Zodat") |
| De aanvraag bij Meta regelen wij. U hoeft daar niet doorheen. | De aanvraag bij Meta regelen wij. | cut |
| Nieuwe tarieven of een nieuwe dienst? Eén mailtje en wij passen hem aan. Blijvend. | Stuur een mail bij nieuwe tarieven of een nieuwe dienst, dan passen wij hem aan. | AI tell (staccato "Blijvend."); verb first |
| Goedkopere chatbots bestaan. Daar bent u zelf de bouwer, en de meeste plannen geen afspraak in. Dat is het verschil waar u voor betaalt. | Er zijn goedkopere chatbots. Die bouwt u zelf, en de meeste plannen geen afspraken in. | cut (closing explainer line) |
| Websitechat op uw eigen site (Nederlands, 24/7) | Websitechat op uw eigen site, in het Nederlands, dag en nacht | "24/7" |
| WhatsApp-kanaal | WhatsApp | cut (jargon) |
| Beantwoordt vragen over diensten, tarieven en werkgebied | Beantwoordt vragen over uw diensten, tarieven en werkgebied | clarity |
| Vangt leads en terugbelverzoeken op | Vangt aanvragen en terugbelverzoeken op | anglicism |
| table cells "–" (3x) | nee | the dash read as a pause character; "nee" pairs with "ja" and reads out loud |
| Inbegrepen belminuten per maand / 750, daarna €0,40/min | Belminuten inbegrepen / 750 per maand, daarna € 0,40 per minuut | clarity; number format |
| Gelijktijdige gesprekken / tot 5 tegelijk | Telefoongesprekken tegelijk / tot 5 | double "gelijk"; Chat has no phone |
| Alle abonnementen bevatten | Bij elk abonnement | terms are not "contents" |
| Volledige inrichting en onderhoud. U bouwt zelf niets. | Inrichting en onderhoud door ons. U bouwt zelf niets. | AI tell ("volledig") |
| Maandelijks opzegbaar; opzeggen per mail, geen opzegtermijn. | Per maand opzegbaar. Opzeggen gaat per mail, zonder opzegtermijn. | same term; semicolon |
| BTW-tarief 21% (verlegd voor klanten buiten Nederland). | Btw-tarief 21%, verlegd voor klanten buiten Nederland. | spelling |
| Klaar om te starten? | Aanmelden kost vijf minuten | AI tell; the fact comes from /ai-receptionist/ step 1 |
| Meld u aan en wij bellen binnen één werkdag om de setup in te plannen. Liever eerst zien hoe het werkt? Probeer de demo, direct in uw browser. | Binnen één werkdag bellen wij om de inrichting in te plannen. U kunt ook eerst de demo proberen, in uw browser. | anglicism; rhetorical question |

## gratis.astro (4 changes)

| old | new | why |
|---|---|---|
| title: Gratis: vier dingen die u vandaag weet | Gratis: vier eerste stappen, zonder gesprek | not true: the scan answers in 1 werkdag, the openings take 5 werkdagen |
| H1: Vier dingen die u vandaag weet | Vier eerste stappen | same; "gratis eerste stap" is the site's term (/prijzen/, home) |
| Geen gesprek en geen kosten. Kies wat nu speelt. | Een gesprek is niet nodig. Kies wat nu speelt. | staccato; "geen kosten" doubled the eyebrow "Gratis" |
| meta: ..., weet binnen 1 werkdag waar ... | ..., hoor binnen 1 werkdag waar ... | grammar ("weet" as an imperative) |

## klein-beginnen.astro (1 change)

| old | new | why |
|---|---|---|
| Alle bedragen zijn excl. 21% btw. Past geen van deze vier? Mail naar hallo@... wat er speelt. | Alle prijzen zijn excl. 21% btw. Past geen van deze vier? Mail wat er speelt naar hallo@.... | "Alle bedragen" was not true (the pay buttons show amounts incl. btw); word order |

Total: 90 rows of text changes across 7 files.

## Flagged, not changed

1. **/prijzen/ Compleet: "Gemiste oproepen bestaan niet meer."** Promises that no call is ever missed. The voice guide (§10) forbids promising 100% of calls answered, and the same page says "tot 5" calls at a time and 750 minutes. Proposal: cut the sentence.
2. **Compleet sells an AI-telefonist.** The repo's CLAUDE.md says the voice agent is "currently blocked on founder creds". Confirm it can be delivered today before it is sold at € 499.
3. **Setup fee conflict.** /prijzen/ says "Eenmalige inrichting vanaf € 249, gratis voor pilotklanten". /ai-receptionist/ step 1 says you pay € 149,50 and then € 299 per maand, with no setup fee. Is the pilot still running, and which of the two is true?
4. **/ai-receptionist/ cost example counts phone calls** ("Wat gemiste oproepen u per maand kosten", "Gemist (brancheschatting 28%)"), but the page sells website chat and WhatsApp, and Chat has no phone. The 28% has no source on the page. Davy should decide between "aanvragen" with a sourced number, and a note that the example is about calls.
5. **"AVG-proof, EU-gehost"** (hero proof chip on /ai-receptionist/). "proof" is an anglicism, and the phrase is a strong legal claim. Proposal: "AVG-conform, EU-gehost" if Davy stands behind it, otherwise only "EU-gehost".
6. **Same H1 on two pages.** / and /ai-receptionist/ both have "Het licht blijft aan." as their H1. That is the brand line, so I left it. Davy decides whether /ai-receptionist/ gets its own H1.
7. **/advertentievideos/ "Waarom Klantkraan dit doet"** still opens with the receptionist and talks to webshops (open decision #8 in the site review: webshops or trades). Only the grammar was tightened.
8. **"Btw-tarief 21%, verlegd voor klanten buiten Nederland."** Reverse charge applies to business customers in other EU countries. Outside the EU, Dutch btw usually does not apply at all. Check with the bookkeeper. The line also sits under "Korting bij vooruitbetaling", where it does not belong; moving it needs a markup change.
9. **/website-onderhoud/ gives no term** (monthly? cancellable?) and is ordered only by mail (open decision in the site review). Unchanged.
10. **/prijzen/ title and meta name only the receptionist**, while the page now also prices the other three services. This is an SEO decision.
11. **"Sinds 2 augustus 2026 is die melding verplicht onder artikel 50"**: check that the date still holds after the EU's 2026 simplification (omnibus) proposals.
12. **Hero scenario on /ai-receptionist/**: an appointment is booked and a callback is also set ("di 09:00 · terugbelverzoek klaar voor de eigenaar"). A reader may wonder why both happen. I left it, because the drawing's timing depends on it.

## Terminology proposals (not applied outside my pages)

- **versies, not varianten** for the ad videos: applied on /advertentievideos/; the rest of the site already says "versies".
- **AI-receptionist, not "digitale receptionist"**, for the service name in running text: applied on /ai-receptionist/. "digitale assistent" stays wherever the art. 50 sentence and the chat tag use it. The FlowDiagram node still says "digitale receptionist" (see below).
- **"check" → Dutch** ("websitecheck", "snelheidscheck", button "Check mijn website"): proposed "snelheidsmeting", "websitetest" / "Test mijn website". These are system-wide names in services.ts and magnets.ts, so I did not change them.
- **"AI-disclosure"** (the legal page name, and now the link label on /ai-receptionist/, which matches it): proposed "AI-melding" across the site. That needs copy-content's page, the footer and this link to change together.
- **Heading periods**: my pages now end headings without a period. The home page uses the same components (DemoSection, FlowDiagram) with "." headings, so the same component looks different on / and /ai-receptionist/. Proposal: copy-home drops them too, except the brand device "aan.".
- **€ format**: "€ 299" with a no-break space everywhere (services.ts `eur()` already does this).

## For other owners

| file (owner) | exact old | exact new |
|---|---|---|
| src/components/diagrams/FlowDiagram.astro (anim-flow) | `nodeSub: 'digitale receptionist',` | `nodeSub: 'AI-receptionist',` |
| src/pages/index.astro (copy-home) | `heading: 'Stel de receptionist een vraag zoals uw klant dat zou doen.',` | `heading: 'Stel de receptionist een vraag zoals uw klant dat zou doen',` (only if copy-home adopts the no-period headings) |
| src/pages/index.astro (copy-home) | `heading: 'Wat de receptionist doet terwijl u aan het werk bent.',` | `heading: 'Wat de receptionist doet terwijl u aan het werk bent',` (same condition) |

## Test strings

Each old fragment I changed was grepped in `scripts/test-*.mjs` with `grep -n -F`. Only one hit:

- `Wat we bouwen` → `scripts/test-redesign.mjs:282`: `check('/ai-receptionist/ roadmap drops "Nog niet beschikbaar"', html.includes('Wat we bouwen') && !html.includes('Nog niet beschikbaar'))`. The label is now "Nog niet in het abonnement". Proposed test: `html.includes('Nog niet in het abonnement') && !html.includes('Nog niet beschikbaar')`.

No hits for anything else, including "€299", "€450", "–", "zestien varianten", "Uw webshop", "Klaar om te starten?" or "Vier dingen die u vandaag weet". The price checks use `/€\s?299\b/`-style regexes, and `\s` matches the new no-break space, so they still pass. The title check at `test-redesign.mjs:278` still passes: the /ai-receptionist/ title is unchanged.

## Checks run

- No "—", "–" or " - " left in the 7 files. No je/jij (the only "jullie" is a customer's own question in the demo).
- curl: all 7 pages return 200 and serve the new text.
- Dev log: no errors after my edits.
- Rendered text at 1440 and 393 read top to bottom after the edits. The before and after copies are in the session scratchpad.
