# Copy audit — klantkraan.nl

Date: 2026-05-21

> **Update 2026-07-13:** pricing has since been decided at €299 (Chat) / €499 (Compleet), text-first. Prices quoted below are the historical May snapshot — left intact.

## Executive summary

The Klantkraan copy is far above the Dutch trades-marketing baseline — it is concrete, u-form, uses real numbers, and avoids the worst AI cliches (no "ontgrendel", no "naadloos", no "transformeer", no "krachtige oplossing"). On the cornerstone pages it reads close to what a smart operator would actually write. The three problems that consistently undercut that voice: (1) **em-dash addiction** — 231 em-dashes across the copy, with several files using 8-15 each; this is the single loudest AI tell, (2) **structural twinning** — the six trade landing pages are near-clones of each other with the same hero formula, the same "Drie modules in één maandprijs" tricolon, the same "Vlot Nederlands, ook 's avonds en in het weekend" subhead, the same identical FAQ blocks; this reads CMS-generated even though it's not, and (3) **the homepage hero subhead is a textbook AI tricolon** ("AI-receptionist die uw vak spreekt, automatische reviews, geen setup, per maand opzegbaar"). The cleanest pages are `over.astro` and the gidsen — both read human. The two worst offenders are the blog post `cv-storing-januari-installateur.md` (15 em-dashes, scenario opener that sounds written for the page) and the homepage `index.astro` (every conversational pause is an em-dash).

## AI-tell severity heatmap

| Page / file                                             | Severity | Top 2 issues                                                                                                                                            |
| ------------------------------------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `pages/index.astro`                                     | moderate | (1) Hero subhead tricolon; (2) em-dash overuse (5) for a short page                                                                                     |
| `pages/voor-wie.astro`                                  | minor    | (1) "van voorrijkosten en spoedtoeslag tot m²-tarief en welstandseisen" rule-of-three (2) "of u nu X bent of Y" pattern in "Mijn vak staat er niet bij" |
| `pages/prijzen.astro`                                   | clean    | Only minor: "Geen verkooppraatje, wel een rekensom op uw cijfers" is borderline (works as voice)                                                        |
| `pages/over.astro`                                      | clean    | Cleanest page on the site — reads founder-written                                                                                                       |
| `pages/demo.astro`                                      | clean    | Plainspoken throughout. Disclosure block is necessarily formal                                                                                          |
| `pages/rekentool.astro`                                 | clean    | Tool copy is functional and concrete                                                                                                                    |
| `pages/loodgieters.astro`                               | moderate | (1) Twin-of-elektricien feature blocks (2) "Drie modules in één maandprijs" tricolon repeated across all trade pages                                    |
| `pages/elektricien.astro`                               | moderate | (1) Identical "AI-receptionist die uw vak spreekt" feature title as 4 other pages (2) Programmatic-feeling FAQ that mirrors loodgieters near-verbatim   |
| `pages/dakdekkers.astro`                                | minor    | Componentised, well-differentiated by storm-scenario angle. But still uses the "Drie modules" template language                                         |
| `pages/installateur.astro`                              | moderate | Same twin issue; "geen klant gaat naar de concurrent terwijl u op een andere klus zit" feels copy-pasted                                                |
| `pages/schilder.astro`                                  | moderate | 11 em-dashes; otherwise twin of installateur with surface-level swaps                                                                                   |
| `pages/aannemer.astro`                                  | moderate | 10 em-dashes; same template hero structure                                                                                                              |
| `pages/gidsen/index.astro`                              | clean    | "Geen sales-praatje, alleen werk dat u direct kunt toepassen" lands                                                                                     |
| `components/Header.astro`                               | clean    | Functional nav copy                                                                                                                                     |
| `components/Footer.astro`                               | clean    | "Gemaakt in Nederland" is fine                                                                                                                          |
| `components/LeadForm.astro`                             | clean    | Plain form copy                                                                                                                                         |
| `components/RiskReversal.astro`                         | minor    | "U bent vrij" is borderline marketing-y but recoverable                                                                                                 |
| `components/StickyMobileCta.astro`                      | clean    | One button label                                                                                                                                        |
| `components/DashboardMock.astro`                        | clean    | Functional UI text                                                                                                                                      |
| `components/Stat.astro`                                 | clean    | Pure component                                                                                                                                          |
| `components/dakdekkers/Hero.astro`                      | minor    | Tricolon hero subhead                                                                                                                                   |
| `components/dakdekkers/Features.astro`                  | minor    | Tricolon-heavy module bodies                                                                                                                            |
| `components/dakdekkers/PainStats.astro`                 | clean    | Three concrete stats                                                                                                                                    |
| `components/dakdekkers/SocialProof.astro`               | clean    | Placeholder content honestly labelled                                                                                                                   |
| `components/dakdekkers/StormScenario.astro`             | clean    | Strongest section on the site — concrete scenario, real numbers                                                                                         |
| `components/dakdekkers/RoiSnippet.astro`                | minor    | "die u in feite gratis draait" is fluffy phrasing                                                                                                       |
| `components/dakdekkers/Faq.astro`                       | clean    | FAQ has voice                                                                                                                                           |
| `components/dakdekkers/FinalCta.astro`                  | minor    | "Eén AI-receptionist, één storm-protocol, één review-flow" — anaphora tricolon                                                                          |
| `components/dakdekkers/CityLinks.astro`                 | clean    | Functional                                                                                                                                              |
| `content/gidsen/loodgieters-klanten-werven.md`          | clean    | Reads like an operator wrote it                                                                                                                         |
| `content/gidsen/dakdekkers-storm-protocol.md`           | clean    | Best longform on the site                                                                                                                               |
| `content/gidsen/elektriciens-spoed-vs-projecten.md`     | minor    | One "het verschil zit niet in X; het zit in Y" construction                                                                                             |
| `content/gidsen/installateurs-cv-storingen-januari.md`  | minor    | 6 em-dashes; otherwise solid                                                                                                                            |
| `content/gidsen/schilders-lentepiek-overleven.md`       | minor    | 10 em-dashes                                                                                                                                            |
| `content/gidsen/aannemers-offerteaanvragen-filteren.md` | minor    | 9 em-dashes; "Niet later 'even in de eindfactuur meenemen'" reads great though                                                                          |
| `content/blog/ai-telefoniste-voor-loodgieters.md`       | moderate | 13 em-dashes; "Geen verkooppraatje, wel cijfers" repeated                                                                                               |
| `content/blog/cv-storing-januari-installateur.md`       | moderate | 15 em-dashes; scenario opener feels overwritten                                                                                                         |
| `content/blog/no-show-afspraken-verminderen.md`         | minor    | 12 em-dashes; otherwise concrete                                                                                                                        |

## Per-file findings

### pages/index.astro:26-27

**Current copy:** "Elke gemiste oproep teruggebeld binnen 60 seconden. AI-receptionist die uw vak spreekt, automatische reviews, geen setup, per maand opzegbaar."
**Why it reads AI:** Category 3 (tricolon/list padding) + category 9 (buzzword density). The second sentence is a four-item AI-style benefit dump comma-separated. Real Dutch operators do not write subheadings as comma-separated feature lists.
**Suggested rewrite:** "Elke gemiste oproep krijgt binnen 60 seconden een terugbel-SMS. Een AI-receptionist die voorrijkosten en spoedtarief kent. Geen setup. Per maand opzegbaar."

### pages/index.astro:88

**Current copy:** "Elke gemiste oproep wordt een terugbel-afspraak — automatisch."
**Why it reads AI:** Category 4 (em-dash as conversational pause). The dangling "— automatisch" is the single most identifiable LLM voice tic.
**Suggested rewrite:** "Elke gemiste oproep wordt automatisch een terugbel-afspraak."

### pages/index.astro:117-120

**Current copy:** "Wettelijk verplicht onder de EU AI Act art. 50 — en op-brand voor een vakman die niet achter automation verstopt. Geen verwarring bij de klant, geen sancties bij de toezichthouder."
**Why it reads AI:** Category 4 (em-dash); category 8 (anglicism: "op-brand", "automation"); category 6 (assurance pairing). "Op-brand" is not Dutch tradesman vocabulary.
**Suggested rewrite:** "Wettelijk verplicht onder de EU AI Act artikel 50. Bovendien past het bij hoe een vakman werkt: openlijk, niets te verbergen. Geen verwarring bij de klant, geen boete van de toezichthouder."

### pages/index.astro:135-136

**Current copy:** "Vul het formulier in — wij nemen binnen 1 werkdag contact op om uw situatie door te nemen en een demo op uw eigen cijfers in te plannen."
**Why it reads AI:** Category 4 (em-dash); the sentence runs long and would naturally be two in spoken Dutch.
**Suggested rewrite:** "Vul het formulier in. Binnen 1 werkdag bellen wij u terug om uw situatie door te nemen en een demo op uw eigen cijfers te plannen."

### pages/voor-wie.astro:32-34

**Current copy:** "Klantkraan is gebouwd om de specifieke gesprekken van elk Nederlands vakgebied te begrijpen — van voorrijkosten en spoedtoeslag tot m²-tarief en welstandseisen."
**Why it reads AI:** Category 4 (em-dash); category 3 (four-item list as scope-padding).
**Suggested rewrite:** "Klantkraan kent de termen van uw vak. Voorrijkosten en spoedtoeslag voor de loodgieter. M²-tarief en kleurproef voor de schilder. Welstandseisen voor de aannemer."

### pages/voor-wie.astro:88-91

**Current copy:** "Klantkraan werkt voor elk Nederlands installatie-, onderhouds- of bouwvakbedrijf — ook voor timmermannen, hoveniers, glaszetters en stukadoors. De AI-receptionist leert uw eigen tarieven, woordenschat en spoedbeleid kennen tijdens een korte intake."
**Why it reads AI:** Category 4 (em-dash); category 3 (tricolon "uw eigen tarieven, woordenschat en spoedbeleid").
**Suggested rewrite:** "Klantkraan werkt voor elk Nederlands installatie-, onderhouds- of bouwvakbedrijf. Ook voor timmermannen, hoveniers, glaszetters of stukadoors. In een korte intake leggen we uw tarieven, vakjargon en spoedregels vast — daarna spreekt de AI-receptionist die uit zoals u dat zelf doet."

### pages/prijzen.astro:199-201

**Current copy:** "In een demo van 20 minuten laten wij precies zien hoe Klantkraan in uw situatie werkt. Geen verkooppraatje, wel een rekensom op uw cijfers."
**Why it reads AI:** Borderline — "Geen X, wel Y" is a controlled use of category 5 here and reads like a founder. Keep as-is. Noted only because the same phrase echoes in other files.

### pages/loodgieters.astro:33

**Current copy:** "Neemt op in vlot Nederlands, ook 's avonds en in het weekend. Kent uw voorrijkosten, spoedtoeslag en materiaalopslag — en noemt alleen tarieven die u zelf heeft ingesteld."
**Why it reads AI:** Category 4 (em-dash); category 3 (tricolon "voorrijkosten, spoedtoeslag en materiaalopslag"). Same construction repeats across `elektricien.astro:33`, `installateur.astro:33`, `schilder.astro:33`.
**Suggested rewrite:** "Neemt op in vlot Nederlands. Ook 's avonds en in het weekend. Kent uw voorrijkosten, spoedtoeslag en materiaalopslag — en noemt nooit een tarief dat u niet zelf heeft ingesteld." (Keeping one em-dash if it adds, but the second clause becomes the contrast — not decoration.)

### pages/loodgieters.astro:113-118

**Current copy:** "De Klantenmotor voor loodgieters. / Een AI-receptionist die voorrijkosten, spoedtoeslag en materiaalopslag kent. Neemt op in vlot Nederlands, ook 's avonds en in het weekend. Reviews en terugbel-afspraken erbij, in één pakket."
**Why it reads AI:** Category 10 (overly polished parallelism — six trade pages share this exact hero shape with only the niche-vocabulary swapped: loodgieter→elektricien→dakdekker→installateur→schilder→aannemer). The hero feels CMS-generated even though each page is written by hand.
**Suggested rewrite (loodgieter variant):** "Bent u onder een gootsteen bezig? Dan neemt onze AI-receptionist op. In het Nederlands, met uw voorrijkosten en spoedtarief paraat. 's Avonds, weekend, vakantie — hetzelfde verhaal."

### pages/loodgieters.astro:189-191 (and twins on every trade page)

**Current copy:** "Drie modules in één maandprijs — gebouwd voor loodgieters in heel Nederland, van Amsterdam en Rotterdam tot Eindhoven en daarbuiten."
**Why it reads AI:** Category 4 (em-dash); category 3 (tricolon "Amsterdam, Rotterdam, Eindhoven en daarbuiten"); category 10 — this exact sentence with just the niche-noun swapped appears in `elektricien.astro:190`, `installateur.astro:192`, `schilder.astro:192`, `aannemer.astro:192`, and the dakdekkers `Features.astro:33`. Five times the same sentence is the heaviest CMS-tell on the site.
**Suggested rewrite:** Vary per niche. For loodgieters: "Drie modules. Eén maandprijs. Gebouwd voor de loodgieter die meer onder een gootsteen ligt dan achter zijn telefoon." For dakdekkers: "Drie modules. Eén maandprijs. Geschreven na een avond meeluisteren met een dakdekker uit Utrecht." For elektricien: "Drie modules. Eén maandprijs. Niet voor de grote installatiebureaus — voor de elektricien met twee tot acht monteurs."

### pages/loodgieters.astro:243-244

**Current copy:** "Klantkraan Pro is €599 per maand. Terugverdiend zodra u één extra klus per maand herwint. De rest is winst."
**Why it reads AI:** Borderline — "De rest is winst" is a stock SaaS closing line that recurs on `elektricien.astro:220`, `installateur.astro:223`, `schilder.astro:223`, `aannemer.astro:223`. Category 10 (parallelism across pages).
**Suggested rewrite (vary per niche):** Loodgieter: "Eén extra spoedklus per maand en u staat quitte. De rest is uw marge." Elektricien: "Eén kortsluitings-spoed per maand betaalt het abonnement. Wat erna komt is omzet zonder concurrent." Aannemer: "Eén extra renovatie per jaar dekt twee jaar abonnement."

### pages/loodgieters.astro:333-335

**Current copy:** "Een demo van acht minuten op uw eigen nummer is de snelste manier om te horen wat Klantkraan voor uw bedrijf doet."
**Why it reads AI:** Same sentence appears verbatim on `elektricien.astro:287`, `installateur.astro:290`, `schilder.astro:315`, `aannemer.astro:290`. Five-fold copy-paste is the strongest signal of template generation.
**Suggested rewrite:** Pick per niche, varying the framing. Loodgieter: "Bel het demo-nummer. In acht minuten weet u of de stem klopt voor uw klanten." Aannemer: "Acht minuten demo. Daarna weet u of het past bij hoe uw klanten u willen bereiken."

### pages/elektricien.astro:32

**Current copy:** "Neemt op in vlot Nederlands, ook 's avonds en in het weekend. Kent uw voorrijkosten, uurtarief, kortsluitings-spoedtarief en eventueel weekend-toeslag — en noemt alleen tarieven die u zelf heeft ingesteld."
**Why it reads AI:** Same template body as loodgieters with niche-vocabulary swap. Category 10 (template parallelism); category 4 (em-dash).
**Suggested rewrite:** "Neemt op in vlot Nederlands, ook na 17:00 en in het weekend. Noemt alleen uw eigen kortsluitings-spoedtarief, uurtarief en weekendtoeslag. Geen prijs die u niet vooraf heeft ingesteld."

### pages/elektricien.astro:115-117

**Current copy:** "Een AI-receptionist die kortsluitings-spoed, EV-laadpaal-meerprijs en uurtarief kent. Neemt op in vlot Nederlands, ook 's avonds en in het weekend. Reviews en terugbel-afspraken erbij, in één pakket."
**Why it reads AI:** Category 3 (tricolon: kortsluitings-spoed, EV-laadpaal-meerprijs en uurtarief); category 10 (twin of loodgieter hero).
**Suggested rewrite:** "Een stem die uw klant uitlegt wat een kortsluitings-spoedtarief is. Of wat een EV-laadpaal-meerprijs is. Neemt op tot 22:00, 7 dagen per week. Reviews en terugbelafspraken erbij."

### pages/installateur.astro:118-121

**Current copy:** "Een AI-receptionist die CV-storingen, geiser-pannes en jaarlijks onderhoud uit elkaar houdt. Vangt januari-pieken en oktober-onderhoud — ook 's avonds en in het weekend."
**Why it reads AI:** Category 3 (tricolon "CV-storingen, geiser-pannes en jaarlijks onderhoud"); category 4 (em-dash).
**Suggested rewrite:** "Een stem die een CV-storing herkent en hem niet verwart met een planning-vraag voor de jaarbeurt. Vangt de januari-piek en het oktober-onderhoud op. Avonden en weekenden inbegrepen."

### pages/installateur.astro:222-224

**Current copy:** "Klantkraan Pro is €599 per maand. Terugverdiend zodra u één extra spoed-CV-storing per maand vangt. De rest is winst — en de klant valt niet in de kou."
**Why it reads AI:** Category 4 (em-dash); "valt niet in de kou" works as voice but the rest is template.
**Suggested rewrite:** "€599 per maand. Eén extra spoed-CV uit de januari-piek betaalt hem terug. De rest is omzet. En de klant valt niet in de kou."

### pages/schilder.astro:32

**Current copy:** "Neemt op in vlot Nederlands, ook 's avonds en in het weekend. Kent uw voorrijkosten, m²-tarief binnen en buiten, kleurproef-meerprijs en spuitwerk-toeslag — en noemt alleen tarieven die u zelf heeft ingesteld."
**Why it reads AI:** Category 3 (four-item list); category 4 (em-dash); category 10 (twin of loodgieter feature copy).
**Suggested rewrite:** "Neemt op in vlot Nederlands, ook na 17:00. Noemt alleen uw eigen m²-tarief, kleurproef-meerprijs en spuitwerk-toeslag. Niets verzonnen, niets benaderend."

### pages/schilder.astro:118-121

**Current copy:** "Een AI-receptionist die offerteaanvragen, planning-vragen en leveranciers uit elkaar houdt. Vangt lente-piek aanvragen en avond-bellers — ook 's avonds en in het weekend."
**Why it reads AI:** Category 3 (tricolon); category 4 (em-dash). Also "Vangt avond-bellers — ook 's avonds" is internally redundant.
**Suggested rewrite:** "Houdt offerteaanvragen, planning-vragen en leveranciers uit elkaar. Vangt de avond-bellers die u nu mist als u op de stelling staat. Vangt de lente-piek zonder dat u extra mensen aanneemt."

### pages/aannemer.astro:32

**Current copy:** "Neemt op in vlot Nederlands, ook 's avonds en in het weekend. Filtert offerteaanvragen, meerwerk-vragen, leveranciers en spoed apart — u krijgt elke ochtend een overzichtelijke samenvatting voordat u op de bouwplaats stapt."
**Why it reads AI:** Category 3 (four-item list); category 4 (em-dash); "overzichtelijke samenvatting" is corporate.
**Suggested rewrite:** "Neemt op in vlot Nederlands, ook 's avonds en in het weekend. Splitst offerteaanvragen, meerwerk, leveranciers en spoed apart. 's Ochtends krijgt u een lijstje in WhatsApp — voor u de bus instapt."

### pages/aannemer.astro:118-121

**Current copy:** "Een AI-receptionist die offerteaanvragen, meerwerk en leveranciers uit elkaar houdt. Vangt prospects terwijl u op de bouwplaats staat — ook 's avonds en in het weekend."
**Why it reads AI:** Category 3 (tricolon); category 11 (vague "vangt prospects" — what does that mean?); category 4 (em-dash).
**Suggested rewrite:** "Houdt offerteaanvragen, meerwerk en leveranciers apart. Belt iemand om 19:30 over een verbouwing? De AI-receptionist neemt op. Geen voicemail meer."

### components/dakdekkers/Features.astro:21

**Current copy:** "Klus klaar? De klant krijgt de volgende ochtend om 10:00 een SMS met een korte review-vraag, specifiek over de kwaliteit van het werk. Google-reviews stapelen zich op — uw lokale ranking voor 'dakdekker + plaats' stijgt vanzelf."
**Why it reads AI:** Category 4 (em-dash); "stijgt vanzelf" is the kind of throwaway promise an LLM produces. Also "specifiek over de kwaliteit van het werk" is filler.
**Suggested rewrite:** "Klus klaar? De volgende ochtend om 10:00 krijgt de klant een SMS met een review-vraag. Daarna gaan de Google-sterren werken voor uw vindbaarheid."

### components/dakdekkers/Features.astro:33

**Current copy:** "Drie modules in één maandprijs — gebouwd voor dakdekkers in heel Nederland, van Amsterdam en Rotterdam tot Eindhoven en daarbuiten."
**Why it reads AI:** Five-times-repeated template phrase (see notes under loodgieters.astro:189). Category 10.
**Suggested rewrite:** "Drie modules, één maandprijs. Bij elke storm één telefoonopname-systeem dat opschaalt zonder dat u extra personeel inhuurt."

### components/dakdekkers/RoiSnippet.astro:18-23

**Current copy:** "Stel: u mist 5 noodreparaties per stormseizoen. Gemiddeld €650 per reparatie = €3.250 aan omzet die naar de concurrent gaat. Klantkraan Lite kost €349 per maand. Dat zijn negen maanden Klantkraan die u in feite gratis draait — alleen al uit één gemiste-oproep-recovery."
**Why it reads AI:** Category 4 (em-dash); "in feite" is filler; "gemiste-oproep-recovery" is an anglicism (category 8); "die u in feite gratis draait" is a clumsy construction.
**Suggested rewrite:** "Stel: u mist 5 noodreparaties per stormseizoen. €650 per reparatie = €3.250 weggegooid aan de concurrent. Klantkraan Lite kost €349 per maand. Eén teruggewonnen noodreparatie en u draait negen maanden zonder netto kosten."

### components/dakdekkers/FinalCta.astro:10-13

**Current copy:** "Eén AI-receptionist, één storm-protocol, één review-flow. Geen jaarcontract, geen setup, eerste maand 50% korting."
**Why it reads AI:** Category 3 (rule-of-three anaphora "Eén X, één Y, één Z" — the most classic AI tricolon pattern in Dutch). Then a second tricolon right after.
**Suggested rewrite:** "Eén abonnement dat de storm-piek opvangt. Geen jaarcontract. Geen setup. Eerste maand halve prijs."

### components/RiskReversal.astro:21-33

**Current copy (three promises):** "Werkt het niet voor u, zegt u op zonder uitleg." / "Eén e-mail naar hallo@klantkraan.nl en u bent vrij." / "Wij koppelen Klantkraan aan uw bestaande nummer."
**Why it reads AI:** Mostly fine, but the three titles "Eerste maand 50% korting / Opzegbaar per direct / Geen wurgcontract, geen setup" plus the third body's "Geen setup-fee, geen migratiekosten" creates a quintuple "geen X, geen Y" stack — category 5 (the negation rhythm becomes its own AI tell).
**Suggested rewrite (third body):** "Wij hangen Klantkraan achter uw bestaande nummer. Niets om te porten, niets om te installeren."

### content/blog/ai-telefoniste-voor-loodgieters.md:23

**Current copy:** "Anders dan een antwoordapparaat **praat hij echt met de klant**. Anders dan een antwoordservice **werkt hij 24/7 zonder pauze** en kost hij geen €4 per gesprek."
**Why it reads AI:** Category 10 (anaphora — "Anders dan een X..., Anders dan een Y..."). LLMs love this construction.
**Suggested rewrite:** "Een antwoordapparaat zegt 'spreek uw bericht in'. Hij praat. Een antwoordservice kost €4 per gesprek en werkt alleen kantooruren. Hij niet."

### content/blog/ai-telefoniste-voor-loodgieters.md:43

**Current copy:** "Wie u een AI verkoopt die 'alles' kan, verkoopt lucht. Een goede AI doet drie of vier dingen heel goed en wijst de rest af zodat u kunt focussen op vakwerk."
**Why it reads AI:** "zodat u kunt focussen op vakwerk" — anglicism "focussen" plus the consultant-speak closing. A tradesman would say "zodat u uw werk kunt doen".
**Suggested rewrite:** "Wie u een AI verkoopt die 'alles' kan, verkoopt lucht. Een goede AI doet drie of vier dingen goed. De rest wijst hij netjes af, zodat u kunt werken."

### content/blog/ai-telefoniste-voor-loodgieters.md:73

**Current copy:** "U bent **fundamenteel tegen AI in de eerste lijn** met de klant. Onze ervaring: dat houdt twee maanden stand, daarna wint de praktijk."
**Why it reads AI:** "in de eerste lijn met de klant" is consultant-vocabulary; "daarna wint de praktijk" sounds neat but is hollow without specifics.
**Suggested rewrite:** "U wilt principieel geen AI tussen u en uw klant. Dat is een geldige keuze. Onze ervaring: de helft van de vakmensen die zo begint, belt na twee maanden terug omdat ze twee zaterdagen achter elkaar gemiste klussen telden."

### content/blog/cv-storing-januari-installateur.md:14-18

**Current copy:** "Een woensdagochtend in januari. Het heeft 's nachts gevroren. Drie klanten bellen u binnen veertig minuten met dezelfde melding: de CV doet niets meer, het is acht graden binnen, de kinderen moeten naar school. / U zit bij klant nummer één in de meterkast. Klant twee krijgt de bezetkleur. Klant drie krijgt voicemail en belt direct uw concurrent."
**Why it reads AI:** This is well-written but the structure — three-beat scenario opener with rule-of-three escalation — is a textbook LLM blog hook. A real installateur would write "Laatst belden in 40 minuten drie klanten met dezelfde storing. Dat is januari."
**Suggested rewrite:** "Laatst belden er in veertig minuten drie klanten met dezelfde melding: CV doet niets, acht graden binnen, kinderen die naar school moeten. Ik zat bij klant één onder de ketel. Klant twee hoorde de bezetkleur. Klant drie kreeg voicemail en belde mijn concurrent. Welkom in januari."

### content/blog/cv-storing-januari-installateur.md:31-32

**Current copy:** "Twee januari-weken kost u in dat scenario €3.400 — en dat is voordat u de reputatie-schade meeneemt: een klant die u niet bereikt op het moment dat hij u écht nodig heeft, vertelt zijn buren over uw concurrent."
**Why it reads AI:** Category 4 (em-dash plus colon in one sentence — over-punctuated). Category 6 ("op het moment dat hij u écht nodig heeft" — empty intensifier).
**Suggested rewrite:** "Twee januari-weken kost u €3.400. Plus de schade aan uw naam: een klant die u niet bereikt op een vorstochtend, vertelt zijn buren over de monteur die wel opnam."

### content/blog/no-show-afspraken-verminderen.md:73-84

**Current copy:** "Dit klinkt agressief, maar Nederlandse vakmensen die dit doorvoeren zien: / - **30% minder no-shows** binnen drie maanden. / - **Hogere conversie van offerte naar opdracht**, omdat de klant geen 'prijs-verrassing' meer ervaart. / - **Minder boze reviews** over onverwachte kosten — de meest voorkomende 1-ster Google-review in deze sector. / / Geen verrassingen = geen verongelijkte klant = geen no-show."
**Why it reads AI:** Category 3 (rule-of-three benefits list); category 10 (the equation-style closer "X = Y = Z" is a stock LLM device).
**Suggested rewrite:** "Dit klinkt agressief, maar Nederlandse vakmensen die hun voorrijkosten vooraf vermelden zien 30% minder no-shows binnen drie maanden, hogere offerte-acceptatie, en aanzienlijk minder 1-ster reviews over onverwachte kosten. Reden: een klant zonder prijs-verrassing is een klant zonder reden om niet thuis te zijn."

### content/gidsen/loodgieters-klanten-werven.md:60-62

**Current copy:** "Werkspot levert 8 tot 12 procent van de leads van een typische loodgieter, tegen een gemiddelde leadprijs van €3 tot €75 afhankelijk van de klusomvang. De lead is gedeeld met drie tot vijf concurrenten."
**Why it reads AI:** Clean. Noted to confirm the gidsen are the strongest writing on the site.

### content/gidsen/dakdekkers-storm-protocol.md:13-14

**Current copy:** "Tussen 20 oktober en 15 februari beslist een dakdekkersbedrijf zijn jaarcijfers. In die zestien weken komt meer dan 55 procent van alle stormschade-aanvragen binnen, geconcentreerd in de drie tot vijf dagen na een windkracht-8-of-hoger melding van het KNMI."
**Why it reads AI:** Clean. This is exactly the operator-voice the rest of the site should aim for.

## Competitor tone benchmark

- **vakman-online.nl is the closest tone reference and the cleanest** — "Hier gaat het meestal mis. En je merkt het vaak niet" / "Het zijn geen grote fouten. Het zijn vijf kleine gaten die samen flink wat werk kosten." Two-beat sentences, concrete metaphor, jij-form. Klantkraan can match this in the gidsen but loses it in the trade landing-page heroes. Vakman-online uses jij/je where Klantkraan uses u/uw — that is a deliberate Klantkraan choice (per voice-and-tone.md), not a tone problem.
- **klusio.nl is noticeably more AI-cliche heavy** — "groeimachine", "Automatisch. Meetbaar. Structureel." (three-word anaphora tricolon), "Word gevonden in Google. Genoemd in ChatGPT." Confident, but reads consultant-bro, not tradesman. Klantkraan is cleaner than this.
- **voicelabs.nl (Robin)** is similarly clean to Klantkraan's better pages — "Altijd bereikbaar met Robin" / "zet alleen door wanneer dat echt nodig is". Plainspoken. Voicelabs avoids em-dashes almost entirely; Klantkraan over-uses them.
- **Net-net:** Klantkraan is above the Dutch SaaS baseline and a bit above Voicelabs. It is below Vakman-online on the homepage and trade landing pages, but ahead of Vakman-online in the longform gidsen. The single biggest tone-debt is the em-dash density and the structural twinning across trade pages, both of which Vakman-online avoids.

## Top 10 fixes by impact

1. **Reduce em-dashes by ~70% site-wide.** 231 instances is the loudest AI tell. Rule of thumb: replace em-dash conversational pauses (`text — text`) with full stops or commas. Keep em-dashes only for genuine parenthetical insertions ( `Brand X — and only Brand X — does Y` ). Highest-impact files: `content/blog/cv-storing-januari-installateur.md` (15), `content/blog/ai-telefoniste-voor-loodgieters.md` (13), `content/blog/no-show-afspraken-verminderen.md` (12), `pages/schilder.astro` (11), `pages/installateur.astro` and `pages/aannemer.astro` (10 each).
2. **Rewrite the homepage hero subhead** at `pages/index.astro:26-27` — break the four-item comma list, lose the "AI-receptionist die uw vak spreekt, automatische reviews, geen setup, per maand opzegbaar" rhythm.
3. **Kill the five-fold "Drie modules in één maandprijs — gebouwd voor [niche] in heel Nederland, van Amsterdam en Rotterdam tot Eindhoven en daarbuiten" template** at `pages/loodgieters.astro:190`, `pages/elektricien.astro:190`, `pages/installateur.astro:192`, `pages/schilder.astro:192`, `pages/aannemer.astro:192`, `components/dakdekkers/Features.astro:33`. Five identical sentences with niche-noun swaps is the strongest CMS-tell on the site.
4. **Kill the five-fold "Een demo van acht minuten op uw eigen nummer is de snelste manier om te horen wat Klantkraan voor uw bedrijf doet"** at `pages/loodgieters.astro:333`, `pages/elektricien.astro:286`, `pages/installateur.astro:289`, `pages/schilder.astro:314`, `pages/aannemer.astro:289`. Vary per niche, with a real-world anchor for each trade.
5. **Vary the hero formula across trade pages.** Currently all six (including dakdekkers Hero.astro) follow exactly the same shape: `De Klantenmotor voor [niche].` + a 2-3-sentence subhead naming three of their tariffs + same dual CTA + same trust-line strip. One of them should open differently — e.g. dakdekker with a storm anecdote, aannemer with a meerwerk anecdote.
6. **Kill the "AI-receptionist die uw vak spreekt"** feature title that appears identically on loodgieters/elektricien/installateur/schilder feature blocks. Replace with niche-specific verbs ("Praat over kortsluiting in vakjargon", "Kent uw m²-tarief van buiten").
7. **Kill the "De rest is winst" closer** at the end of every trade-page ROI snippet (`loodgieters.astro:244`, `elektricien.astro:220`, `installateur.astro:223`, `schilder.astro:223`, `aannemer.astro:223`). Vary it.
8. **Drop "in feite" / "specifiek over X" / "fundamenteel" filler words.** Three small filler-adverbs concentrated in `RoiSnippet.astro`, `Features.astro` (dakdekkers), and the blog post `ai-telefoniste-voor-loodgieters.md`. Adverbs do not belong in tradesman copy.
9. **Rewrite the blog post `cv-storing-januari-installateur.md` opener** to first-person installateur perspective — "Laatst belden in veertig minuten drie klanten…" instead of the second-person scenario hook. Same for the loodgieter blog where possible.
10. **De-anglicise three specific phrases:** "op-brand" (`index.astro:118`), "gemiste-oproep-recovery" (`dakdekkers/RoiSnippet.astro:23`), "focussen op vakwerk" (`blog/ai-telefoniste-voor-loodgieters.md:43`). Each is a single-word fix that removes a tradesman-cringe trigger.

## Patterns to systematise

- **Template parallelism is the cross-cutting problem, not individual word choice.** The six trade pages (`loodgieters`, `elektricien`, `dakdekkers`, `installateur`, `schilder`, `aannemer`) share the same eight-section structure with identical sentence shapes at each section boundary. Even if every word in isolation is fine, the structural rhyme makes the site read AI-generated. The fix is not a global find-and-replace — it is a copy-edit pass per page where the writer breaks the shape on at least three of the eight sections.
- **Em-dash as conversational pause is the dominant punctuation tic.** This is independent of the trade-page issue and applies to longform too. Recommend a styleguide rule: em-dashes only for parenthetical insertions with content on both sides; for pauses use periods. Add to `voice-and-tone.md`.
- **Rule-of-three / tricolon scope-padding** ("voorrijkosten, spoedtoeslag en materiaalopslag", "kortsluitings-spoed, EV-laadpaal-meerprijs en uurtarief", "CV-storingen, geiser-pannes en jaarlijks onderhoud") shows up in every trade-page hero subhead and every feature body. A Dutch tradesman would say two items, not three. Cap lists at two items unless the list itself is the point.
- **"Geen X, geen Y" negation rhythm is overused.** "Geen setup, geen jaarcontract, geen verborgen verlenging" / "Geen verkooppraatje, wel een rekensom" / "Geen handmatig werk" / "Geen klant raakt verloren" — used sparingly this reads founder; used five times per page it reads LLM. Audit usage and reduce by half.
- **Stock SaaS closers** ("De rest is winst", "Geen handmatig werk", "stijgt vanzelf", "in één pakket") repeat across pages. Replace each with a niche-specific concrete line.
- **The longform `content/gidsen/` files are the model.** They read like an operator's notes: numbers, regional breakdowns, what-not-to-do warnings, no scope-padding. The cornerstone trade landing pages should be edited toward that voice — not the other way around.
