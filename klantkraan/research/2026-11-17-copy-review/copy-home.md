# Copy review: homepage and shared chrome (copy-home, 17 Nov 2026)

Scope: `src/pages/index.astro`, `src/components/home/*` (mine), `Base`, `Header`, `Footer`, `StickyMobileCta`, `OfferCta`, `RiskReversal`, `MiniOfferCard`, `MiniOfferLine`, `VerderLezen`, `PhotoBand`, `Stat`, `JsonLd`, `ui/*`, `public/js/header-menu.js`, `src/data/{services,magnets,company,contact,i18n,jsonld,brevo}.ts`.
Read first: http://127.0.0.1:4399/ as innerText at 1440 and 393 wide, top to bottom.

Main problem on `/`: the same three claims ran four times before the first service band (hero sub, proof strip, Diensten heading, Diensten sub), and every band sub repeated its own bullet points. Most cuts below remove those repeats.

No changes (reviewed, nothing worth changing): `Honest`, `HowItWorks`, `CostReceipt`, `DemoSection`, `FinalCta`, `ServiceCards`, `ServiceBand` (all copy comes in through props or data), `Base`, `StickyMobileCta`, `OfferCta`, `MiniOfferCard`, `MiniOfferLine`, `VerderLezen`, `PhotoBand`, `Stat`, `JsonLd`, `ui/*`, `header-menu.js`, `company.ts` (see flags), `contact.ts`, `i18n.ts`, `jsonld.ts`, `brevo.ts`.

## src/pages/index.astro

| old | new | why |
|---|---|---|
| Diensten sub: "Elke dienst heeft een vaste prijs vooraf en een gratis eerste stap. Begin met wat nu het meest knelt." | "Begin met wat nu het meest knelt." | cut: the proof strip right above says the first sentence already, and every card shows its price and its free first step |
| demo sub: "Dit is een voorbeeldbedrijf, een installateur. Typ een vraag of plan een afspraak. U heeft er geen account voor nodig." | "Dit is een voorbeeldbedrijf, een installateur. U kunt ook een afspraak plannen. Een account is niet nodig." | cut: the h2 already says to ask a question; shorter |
| "Stel bijvoorbeeld:" | "Vraag bijvoorbeeld:" | grammar: "stel" without "een vraag" reads as "suppose" |
| iframe title "Live chat met de digitale receptionist van Klantkraan" | "Live demo: chat met de AI-receptionist van een voorbeeldbedrijf" | clarity: it is the demo of a voorbeeldbedrijf; same service name as everywhere else |
| mobile hint "Chat als een klant. Stel een vraag of plan een afspraak. Opent op volledig scherm." | "Chat als een klant. De demo opent op het hele scherm." | cut: repeats the sub; "volledig scherm" is a calque of "full screen" |
| flow step 1 "Met uw diensten, tarieven en werkgebied. Geen verzonnen prijzen, alleen wat u heeft ingesteld." | "Met uw diensten, tarieven en werkgebied. Hij verzint geen prijzen." | AI tell ("Geen X, alleen Y"); "ingesteld" was already in the line under the chat |
| "Alles over de receptionist" | "Meer over de receptionist" | consistency: the card links to the same page with "Meer over" |
| websites band h2 "Een website die snel, veilig en bijgewerkt blijft." | "Wij houden uw WordPress-site bij." | cut: same sentence as the card above ("Uw WordPress-site blijft snel, veilig en bijgewerkt."); verb first |
| websites sub "Wij houden uw WordPress-site bij, zodat u er zelf niet naar hoeft te kijken. Begin met de gratis check: in 1 minuut ziet u wat er nu aandacht vraagt." | "U hoeft er zelf niet naar te kijken. Met de gratis check ziet u in 1 minuut wat er nu aandacht vraagt." | first half moved to the h2; colon reveal removed |
| automations h2 "Offertes en herinneringen die vanzelf de deur uit gaan." | "Offertes en facturen die zichzelf opvolgen." | clarity: offertes do not go out by themselves, the follow-ups do |
| automations sub "Een offerte die niemand opvolgt, een factuur die blijft openstaan: dat werk kan zichzelf doen. We beginnen met een gratis scan van waar u nu tijd verliest. Daarna krijgt u een vaste prijs vooraf." | "Eerst zoeken we gratis uit waar u nu tijd verliest. Daarna krijgt u een vaste prijs vooraf." | cut: first sentence is now the h2; the last two were point 3 word for word (point 3 changed instead, see services.ts) |
| ads sub "Een video die goed liep, zakt weg zodra mensen de eerste seconden kennen. Van uw bestaande beeld maken we zestien versies, elk met een andere opening, zodat u ziet welke het beste werkt." | "Een video die goed liep, zakt weg zodra mensen de eerste seconden kennen." | cut: the second sentence is points 1 and 2 directly below |
| final sub "Zie in 1 minuut wat uw website mist, laat uitzoeken waar uw bedrijf tijd verliest, reken uit wat gemiste aanvragen kosten of krijg 3 gratis openingen voor uw advertentievideo. Liever meteen iets geregeld? Begin klein, met een vaste prijs." | "Voor een gratis eerste stap en voor een klus met een vaste prijs is geen gesprek nodig." | cut: the four free steps repeat the four cards; "krijg" is an anglicism; the new line answers the objection a vakman has at this point (do I have to talk to a salesman?). The claim already stands on /gratis/ and /klein-beginnen/ ("Een gesprek is niet nodig.") |

## src/data/services.ts (points show only in the bands on /)

| old | new | why |
|---|---|---|
| "Elke dag een back-up, en bewaking of de site online en veilig is" | "Elke dag een back-up, plus bewaking of de site online en veilig is" | grammar: "en ... en ... en" in one line |
| "Offertes die zichzelf opvolgen als de klant niet reageert" | "Een herinnering als de klant niet op uw offerte reageert" | cut: the band h2 now says "zichzelf opvolgen" |
| "Herinneringen voor afspraken en facturen, reviewverzoeken na de klus" | "Herinneringen voor afspraken en facturen" | one promise per line (reviews get their own) |
| "Eerst een gratis scan, daarna een vaste prijs vooraf" | "Reviewverzoeken na de klus" | the scan line is now the band sub; same three facts, no repeat |
| "Zestien versies van één bestaande video" | "16 versies van één bestaande video" | numbers: matches the drawing ("16 versies") beside it |
| "Eerst drie openingen gratis, om te zien of het werkt" | "Eerst 3 openingen gratis, om te zien of het werkt" | numbers: matches "3 nieuwe openingen" in the card and footer |

## src/data/magnets.ts (shows on /, /gratis/, the footer of every Dutch page, OfferCta, /klein-beginnen/, /automatiseringen/)

| old | new | why |
|---|---|---|
| websites short "Wat mist uw website? In 1 minuut" | "Zie in 1 minuut wat uw website mist" | AI tell: three of the four list items were questions; named by result, verb first |
| automations name "Waar verliest uw bedrijf elke week tijd? Antwoord binnen 1 werkdag" | "Laat uitzoeken waar uw bedrijf elke week tijd verliest" | question plus fragment; named by result; "binnen 1 werkdag" stays in `next`, which shows directly under it |
| automations short "Waar verliest u tijd? Antwoord in 1 werkdag" | "Hoor binnen 1 werkdag waar u tijd verliest" | same; keeps the 1 werkdag |
| receptionist name "Reken uit wat onbeantwoorde aanvragen u per maand kosten" | "Reken uit wat gemiste aanvragen u per maand kosten" | same term for the same thing ("gemiste aanvragen" everywhere else on /) |
| receptionist short "Wat kosten gemiste aanvragen u?" | "Reken uit wat gemiste aanvragen kosten" | rhetorical question; same label as the receptionist link under the flow diagram |
| receptionist reason "Het rekent met uw eigen cijfers en kost u één minuut." | "Het rekent met uw eigen cijfers en kost u 1 minuut." | numbers: "1 minuut" everywhere else |
| ads short "3 gratis openingen voor uw advertentie" | "Vraag 3 nieuwe openingen aan voor uw advertentie" | cut: it always sits under a "Gratis" label; parallel with the other three imperatives |
| Offerte-opvolger delivers "... een nette herinnering. Die stopt zodra de klant antwoordt." | "... een nette herinnering. De herinneringen stoppen zodra de klant antwoordt." | grammar: "Die" pointed at one reminder; there are two |

## src/components/Footer.astro (NL only)

| old | new | why |
|---|---|---|
| trust aria "Vertrouwens-signalen" | "Vertrouwenssignalen" | spelling: no hyphen in this compound |
| badge sub "Disclosure niet uitschakelbaar" | "AI-melding staat altijd aan" | anglicism; "melding" is the word / uses for the art. 50 sentence |

## src/components/Header.astro (NL only)

| old | new | why |
|---|---|---|
| summary aria-label "Voor welke branches" | "Voor wie? Kies uw branche" | accessibility: the accessible name must contain the visible "Voor wie?" (WCAG 2.5.3); aria-label overrode it |

## src/components/RiskReversal.astro (NL only; shows on the 7 trade pages)

| old | new | why |
|---|---|---|
| "Klantkraan Chat vanaf €149,50 in maand 1. Werkt het niet voor u, zegt u op zonder uitleg." | "Klantkraan Chat vanaf € 149,50 in de eerste maand, excl. btw. Werkt het niet voor u, dan zegt u op zonder uitleg." | number format (€ 149,50); added the "excl. btw" the site shows with every price (/aanmelden/ says "eerste maand €149,50 ... excl. btw"); "dan" reads better |
| "Maandelijks opzegbaar" | "Per maand opzegbaar" | same term as the footer badge and the voice guide |
| "Geen jaarcontract, geen verborgen verlenging. Eén e-mail naar hallo@klantkraan.nl en het stopt aan het einde van de betaalde maand. Geen opzegtermijn." | "Eén mail naar hallo@klantkraan.nl en het stopt aan het eind van de betaalde maand. Geen jaarcontract en geen opzegtermijn." | AI tell ("Geen X, geen Y ... Geen Z" staccato); "geen verborgen verlenging" adds nothing to "geen jaarcontract"; "mail" as in the footer |
| "Live zonder gedoe" | "Wij installeren het" | AI tell ("zonder gedoe") |
| "Eén klein scriptje op uw website en de receptionist draait. Wij installeren het. U hoeft niets te doen." | "Eén scriptje op uw website en de receptionist draait. U hoeft er zelf niets voor te doen." | "klein scriptje" says small twice; "Wij installeren het" is now the title |
| section aria "Risico-reductie" | "Zekerheden" | spelling ("risicoreductie") and jargon |

## Flagged, not changed

- `/` shows the calculator four times: card, the link under the flow diagram, and the OfferCta block (Base default `offerArea='receptionist'`) right after the final close. That puts a second "Gratis" close straight under "Begin klein, of begin gratis." Proposal: `offerArea={false}` on index.astro. That's a prop change, so I left it for the main session.
- `company.ts` legalName "T4 Software Consulting BV": it is an eenmanszaak (review fix #1, needs Davy's go). The footer and JSON-LD render it on every page.
- Footer trust band on every page: "EU-gehost" while Cloudflare (a US company with a global edge) is listed first; "Per maand opzegbaar · Eén mail, geen opzegtermijn" while the € 45 website care has no confirmed term (services.ts note) and the automations beheer term is not stated; "AVG-conform" and "EU AI Act art. 50" hold for the receptionist only (review fix #5).
- Footer tagline "De Klantenmotor voor Nederlandse ondernemers.": Klantenmotor is retired and it competes with "Het licht blijft aan."; the voice guide prefers "vakman" over "ondernemer". Davy's decision (see terminology).
- Website care points "Elke dag een back-up, plus bewaking ...": which tools do this today is still open (wiki review, open decisions).
- Open decisions from the review, not touched: ads as a fourth equal band on /, the hero primary button, Diensten position in the nav.
- `/rekentool/` counts "gemiste oproepen" (calls, € 450 per klus, 28%) while the receptionist answers chat and WhatsApp and / says "gemiste aanvragen". The tool's model may not match the service it sells. Decision for Davy and copy-content.
- `scripts/test-integration.mjs` risk-reversal block (lines 59-67) expects RiskReversal on "/" and the strings "Opzegbaar per direct" and "Geen wurgcontract, geen setup". Neither the component nor those strings were on "/" before my edits, so that block was already stale.

## Terminology proposals (not applied)

- "Per maand opzegbaar" everywhere. Footer and RiskReversal already use it; it still says "Maandelijks opzegbaar" in `prijzen.astro:125`, `aanmelden.astro:262` and the `legal/voorwaarden.astro:9` description.
- "AI-disclosure" and "Sub-processors": footer legal links and the h1s of `legal/ai-disclosure.astro` and `legal/subprocessors.astro` should become "AI-melding" and "Subverwerkers". Change the footer labels and the page titles together, so they keep matching.
- "digitale receptionist" should become "AI-receptionist" (the service name), except in the art. 50 sentence "U chat met een digitale assistent.", which stays word for word. See FlowDiagram below.
- Footer tagline: "Het licht blijft aan." in place of "De Klantenmotor voor Nederlandse ondernemers.", or no tagline.

## For other owners

| file (owner) | exact old | exact new | why |
|---|---|---|---|
| home/ServicesHero.astro `t.sub` (anim-hero) | "Klantkraan houdt de techniek achter uw bedrijf aan de gang. Een receptionist die klanten antwoordt op site en WhatsApp, een website die snel en bijgewerkt blijft, automatiseringen die het nawerk doen en advertentievideo's die blijven werken. Eén aanspreekpunt, vaste prijzen vooraf." | "Klantkraan houdt de techniek achter uw bedrijf draaiende: een receptionist die klanten antwoord geeft op uw website en in WhatsApp, een website die snel en bijgewerkt blijft, automatiseringen die het nawerk doen en advertentievideo's die blijven werken." | "draaiende houden" is the idiom for systems; "klanten antwoordt op site" is missing an article and reads stiff; the last sentence is the proof strip directly below |
| home/ServicesHero.astro `t.proof[1]` | "Elke dienst heeft een gratis eerste stap" | "Gratis eerste stap bij elke dienst" | parallel with the two noun phrases beside it |
| home/ServicesHero.astro `aria` | "Schema van een meterkast: Klantkraan voedt vier groepen, elk met een schakelaar en een lamp, en alle vier lampen branden: " | "Schema van een meterkast waarin Klantkraan vier groepen voedt. Alle vier lampen branden: " | two colons in one sentence; the switch-and-lamp detail tells a screen-reader user nothing |
| diagrams/FlowDiagram.astro `nl.nodeSub` (anim-flow) | "digitale receptionist" | "AI-receptionist" | same name as the service everywhere else |
| diagrams/CareDiagram.astro `aria` (anim-bands) | "Schema: uw website voedt vier taken die alle vier aan staan: updates van WordPress en plugins, een dagelijkse back-up, bewaking of de site online en veilig is, en een snelheidscheck per maand." | "Schema: vier taken op uw website, alle vier aan: updates van WordPress en plugins, een dagelijkse back-up, bewaking of de site online en veilig is, en een snelheidscheck per maand." | "voedt" belongs to the meterkast in the hero, not to a website; "die alle vier aan staan" is wordy |
| pages/scan/index.astro title and h1 (owner of /scan/) | "Waar verliest uw bedrijf elke week tijd? Antwoord binnen 1 werkdag" | h1: "Laat uitzoeken waar uw bedrijf elke week tijd verliest"; title can keep the question | the h1 mirrored the magnet name in magnets.ts, which changed |
| pages/automatiseringen.astro (copy-services) | the Offerte-opvolger `delivers` text shows twice on the page (in "Zo werkt de Offerte-opvolger" and in the MiniOfferCard below it) | keep one | said twice on one page |

FollowUpDiagram and VariantsDiagram: labels and aria read well; no proposals.

## Test strings

I ran `grep -n -F "<old fragment>" scripts/test-*.mjs` for each changed string ("Elke dienst heeft een vaste prijs vooraf", "Typ een vraag of plan een afspraak", "geen account voor nodig", "Stel bijvoorbeeld", "Live chat met de digitale receptionist", "Opent op volledig scherm", "Geen verzonnen prijzen", "Alles over de receptionist", "Een website die snel, veilig en bijgewerkt blijft", "zodat u er zelf niet naar hoeft te kijken", "Offertes en herinneringen die vanzelf", "dat werk kan zichzelf doen", "We beginnen met een gratis scan", "Van uw bestaande beeld maken we zestien versies", "Zie in 1 minuut wat uw website mist, laat uitzoeken", "Liever meteen iets geregeld", "Elke dag een back-up, en bewaking", "Offertes die zichzelf opvolgen", "reviewverzoeken na de klus", "Eerst een gratis scan, daarna", "Zestien versies van één bestaande video", "Eerst drie openingen gratis", "Wat mist uw website? In 1 minuut", "Waar verliest uw bedrijf elke week tijd", "Waar verliest u tijd? Antwoord in 1 werkdag", "onbeantwoorde aanvragen", "Wat kosten gemiste aanvragen u", "3 gratis openingen voor uw advertentie", "Die stopt zodra de klant antwoordt", "kost u één minuut", "Disclosure niet uitschakelbaar", "Vertrouwens-signalen", "Voor welke branches", "€149,50 in maand 1", "Maandelijks opzegbaar", "Geen jaarcontract, geen verborgen verlenging", "Live zonder gedoe", "Eén klein scriptje", "Risico-reductie").

Hits: none. Unchanged strings that tests check are still there: "U chat met een digitale assistent.", "Eerste maand 50% korting", "Alle branches →", "Bestel per mail", € 299 in the line under the flow diagram, and "excl. btw" in every card and band.

## Verification

- curl 200: /, /gratis/, /klein-beginnen/, /loodgieters/, /automatiseringen/, /prijzen/.
- Playwright innerText of / at 1440 and 393 (and /gratis/, /loodgieters/, /automatiseringen/): new text present; no em or en dashes and no " - " in the rendered text; every changed sentence reread in context.
- The dev log shows no errors from these edits; its only warning is a 404 probe for /bestaat-niet-xyz/.
- In my files, — and – appear in code comments only.
