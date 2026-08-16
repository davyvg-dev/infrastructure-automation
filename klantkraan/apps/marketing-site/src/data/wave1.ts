// Wave 1 — the 10 city×niche combos that ship in the first programmatic-SEO
// batch (research/programmatic-seo-blueprint.md §4, launch order pages 1-10).
// Each combo carries the niche-in-city paragraph (≈60 words, the second
// "city-unique" content block per page) and 2 city-named FAQs (mandatory
// per blueprint §6 thin-content prevention rule 2).

import type { CitySlug } from './cities'
import type { Faq, NicheSlug } from './niches'

export interface Combo {
  city: CitySlug
  niche: NicheSlug
  // Niche-in-city paragraph rendered between the city intro and the
  // neighbourhood block. ≥50 words, ≥1 hyper-specific local detail.
  nicheNote: string
  // ≥2 FAQs whose question contains the city name (thin-content firewall).
  cityFaqs: Faq[]
}

export const wave1: Combo[] = [
  // ---- Priority 1
  {
    city: 'utrecht',
    niche: 'dakdekker',
    nicheNote:
      'De oude panden langs de Oudegracht hebben gemetselde topgevels met loden goten die elke twintig jaar herzien moeten worden; in de naoorlogse wijken Kanaleneiland en Overvecht overheersen vlakke bitumendaken die elke tien jaar onderhoud vragen. Veel dakdekkers in Utrecht werken in vaste roosters met VvE-besturen en de corporaties Mitros en Bo-Ex, naast losse particuliere opdrachten in Lombok en Wittevrouwen. In Leidsche Rijn liggen relatief jonge daken, maar de eerste vervangingsronde komt rond 2030 in zicht.',
    cityFaqs: [
      {
        q: 'Hoe snel kan een dakdekker in Utrecht ter plaatse zijn bij een lekkage?',
        a: 'Bij spoedmeldingen die vóór 16:00 binnenkomen sturen aangesloten dakdekkers in Utrecht doorgaans nog dezelfde dag iemand voor een tijdelijke afdichting; bij meldingen na 16:00 is dat de volgende ochtend tussen 8:00 en 10:00. Klantkraan herkent een lekkage automatisch in het gesprek en plant de inspectie in Cal.com — u hoeft niet eerst terug te bellen om in te plannen.',
      },
      {
        q: 'Wat zijn gangbare tarieven voor dakdekkers in Utrecht?',
        a: 'In Utrecht ligt het uurtarief voor dakdekkers doorgaans tussen €55–75 ex BTW, met voorrijkosten van €65–95. Materiaal en specialistische werkzaamheden (loodwerk, dakkapelafdichting, zinkwerk in het beschermd stadsgezicht) komen daar bovenop. Klantkraan noemt alleen tarieven die u zelf in uw systeem heeft gezet — onbekende bedragen worden niet verzonnen.',
      },
    ],
  },
  // ---- Priority 2
  {
    city: 'den-haag',
    niche: 'schilder',
    nicheNote:
      'Het Statenkwartier, de Archipelbuurt en de Vogelwijk hebben veel monumentale gevels die elke zeven tot tien jaar geschilderd moeten worden, vaak met door welstand voorgeschreven kleurstellingen en glansgraden. In Scheveningen en Duindorp speelt zoutdamp-corrosie, wat extra schuurwerk en grondering vraagt aan kozijnen en hekwerk. Veel Haagse schildersbedrijven splitsen het seizoen: buitenwerk april tot september, binnenwerk en lakwerk oktober tot maart, met spuitwerk in een vaste werkplaats.',
    cityFaqs: [
      {
        q: 'Hoe lang van tevoren moet ik een schilder in Den Haag boeken voor buitenwerk?',
        a: 'Voor buitenwerk in het hoogseizoen (april–september) zijn de meeste Haagse schilders zes tot acht weken vooruit volgeboekt; voor het Statenkwartier en de Archipelbuurt vaak nog langer. Klantkraan boekt offerteaanvragen direct in als terugbel-afspraak, zodat aanvragen niet drie dagen blijven liggen voordat u kunt reageren.',
      },
      {
        q: 'Hoeveel kost binnenschilderwerk in Den Haag gemiddeld?',
        a: 'In Den Haag rekenen schilders voor binnenwerk doorgaans €30–45 per m² inclusief sausen en aflakken; voor monumentale panden in het Statenkwartier of de Archipelbuurt loopt dat hoger door specifiek kleuradvies en stucwerkvoorbereiding. Klantkraan kan een eerste m²-indicatie geven aan de hand van uw eigen tarieven en de opgegeven oppervlakte.',
      },
    ],
  },
  // ---- Priority 3
  {
    city: 'utrecht',
    niche: 'loodgieter',
    nicheNote:
      'De grachtenpanden in Wijk C hebben dunne lood- en koperleidingen die bij vorst snel scheuren; in Leidsche Rijn werken loodgieters vaak in nieuwbouwclusters met collectieve cv-stations en stadsverwarming Eneco. De student- en expatpopulatie rond De Uithof zorgt voor hoge tenant-turnover, waardoor reactieve klussen — lekkende kranen, verstopte afvoeren, defecte boilers — een groot deel van de orderportefeuille van veel Utrechtse loodgieters vullen. Spoedwerk concentreert zich rond vorstweekenden in januari en februari.',
    cityFaqs: [
      {
        q: 'Is een loodgieter in Utrecht ook in het weekend bereikbaar?',
        a: 'Met Klantkraan wel — de AI-receptionist neemt 24/7 op, herkent spoed (vorstschade, riool-overstroming, gasluchten) en stuurt direct een sms naar de dienstdoende loodgieter met een Cal.com-link voor inplanning. Zonder Klantkraan blijft veel Utrechtse zaterdagvraag bij voicemail steken — een typische missed-call gap die wij dichten.',
      },
      {
        q: 'Wat kost een spoed-loodgieter in Utrecht?',
        a: 'In Utrecht ligt de spoedtoeslag voor loodgieters doorgaans tussen €45–85 boven het reguliere uurtarief (€55–75 ex BTW), met een minimum-belasting van een uur. Klantkraan benoemt de spoedtoeslag in het gesprek alleen wanneer u die zelf heeft ingesteld — geen verrassingen voor uw klant.',
      },
    ],
  },
  // ---- Priority 4
  {
    city: 'utrecht',
    niche: 'schilder',
    nicheNote:
      'De gevelschilder in Utrecht heeft te maken met strikte welstandsregels langs de Oudegracht en in Wittevrouwen, waar kleurkeuze en glansgraad zijn vastgelegd in beeldkwaliteitsplannen. Veel particuliere opdrachten zijn binnenwerk: studentenkamers in Lombok en Tuinwijk, en eengezinswoningen in Tuindorp en Oog in Al. De lente-piek loopt van eind maart tot juni; in oktober volgt nog een korte piek voor binnenschilderwerk vóór de winter.',
    cityFaqs: [
      {
        q: 'Welke kleuren mag ik voor een gevel in Utrecht kiezen?',
        a: 'In het beschermd stadsgezicht (Binnenstad, Wittevrouwen, deel van Wijk C) gelden beeldkwaliteitsplannen die kleur en glansgraad voorschrijven; u vraagt een omgevingsvergunning aan bij de gemeente Utrecht voordat u start. Veel Utrechtse schilders bieden vooraf een proefvlak op gevel — Klantkraan registreert die proefafspraak automatisch in uw agenda.',
      },
      {
        q: 'Hoeveel kost gevelschilderwerk in Utrecht?',
        a: 'Voor een typische tussenwoning in Utrecht ligt het tarief voor volledig gevelschilderwerk (kozijnen, deuren, dakranden) rond €1.800–3.500, afhankelijk van houtsoort en welstandsregels. Voor monumentale panden langs de Oudegracht is dat hoger. Klantkraan geeft alleen tarieven door die u zelf heeft ingesteld.',
      },
    ],
  },
  // ---- Priority 5
  {
    city: 'amsterdam',
    niche: 'schilder',
    nicheNote:
      'In de Amsterdamse grachtengordel zijn schilders gebonden aan welstandseisen voor zichtbare gevels en kozijn-, deur- en hekwerkkleuren; veel opdrachten lopen via VvE’s en monumentenrestaurateurs. In Oud-Zuid en De Pijp domineert hoogwaardig binnenwerk voor particulieren met budget; in Noord en Nieuw-West veel projectmatig spuitwerk voor woningcorporaties Ymere en Stadgenoot. De winterpiek voor binnenwerk is in Amsterdam vrijwel gelijk aan de zomerpiek voor buitenwerk — een unicum binnen de G4.',
    cityFaqs: [
      {
        q: 'Welke kleuren zijn toegestaan voor een gevel in Amsterdam-Centrum?',
        a: 'In het beschermde stadsgezicht (grachtengordel, Jordaan, Plantagebuurt) is de kleurkeuze gebonden aan de welstandsnota Amsterdam. Veel schilders werken met een vaste kleurenwaaier per buurt en stemmen vooraf af met de monumentencommissie. Klantkraan registreert het VvE-overleg of de welstandsafspraak automatisch in uw Cal.com-agenda.',
      },
      {
        q: 'Wat is een gangbaar tarief voor binnenschilderwerk in Amsterdam?',
        a: 'In Amsterdam liggen tarieven voor binnenschilderwerk doorgaans tussen €35–55 per m² inclusief sausen en aflakken; in Oud-Zuid en de grachtengordel hoger door specifieke kleurkeuze, stucwerkvoorbereiding en parkeerlasten. Klantkraan geeft alleen tarieven door die u zelf heeft ingesteld.',
      },
    ],
  },
  // ---- Priority 6
  {
    city: 'rotterdam',
    niche: 'schilder',
    nicheNote:
      'Rotterdamse schilders splitsen hun werk tussen herhalingsopdrachten voor VvE’s van galerijflats in Zuidwijk en Pendrecht, en particuliere binnenklussen in Kralingen en Hillegersberg. Het Schiekadeblok en de Wilhelminapier vragen industriële verfsystemen met certificering. De zoutbelasting in de havenwijken (Charlois, Pernis) versnelt corrosie op kozijnen, wat dunnere intervallen tussen schilderbeurten betekent dan elders in de Randstad.',
    cityFaqs: [
      {
        q: 'Hoe vaak moet ik kozijnen in Rotterdam laten schilderen?',
        a: 'In Rotterdam-havengebied (Charlois, Pernis, Heijplaat) versnelt zoutdamp-corrosie de schilderintervallen tot 5–7 jaar voor houten kozijnen; in Kralingen of Hillegersberg is dat doorgaans 7–10 jaar. Klantkraan kan herhaalafspraken automatisch in uw Cal.com agenda zetten op basis van uw eigen onderhoudscyclus.',
      },
      {
        q: 'Wat kost gevelschilderwerk in Rotterdam?',
        a: 'Voor een tussenwoning in Rotterdam-Zuid rekent een schilder doorgaans €1.500–3.000 voor volledig gevelschilderwerk; in Hillegersberg en Kralingen hoger door grotere geveloppervlakten. Industriële opdrachten op de Wilhelminapier zijn aparte calculaties met certificeringseis. Klantkraan benoemt alleen door uzelf opgegeven tarieven.',
      },
    ],
  },
  // ---- Priority 7
  {
    city: 'amsterdam',
    niche: 'loodgieter',
    nicheNote:
      'Amsterdamse loodgieters werken vaak met krappe leidingschachten in 17e-eeuwse panden en strenge VvE-regels rond standleidingen in galerijflats in Zuidoost. Spoedwerk concentreert zich rond vorstperiodes en de horeca-as Rembrandtplein–Leidseplein. De combinatie van VvE-administratie, oude woningvoorraad en hoge concentratie expat-huurders maakt nazorg en reviews zwaarder wegen dan in de meeste andere Nederlandse steden.',
    cityFaqs: [
      {
        q: 'Welke spoed-loodgieter is in Amsterdam-Centrum 24/7 bereikbaar?',
        a: 'Veel Amsterdamse loodgieters bieden 24/7 dienst tegen spoedtoeslag, maar mistroostige uren (na 22:00, vóór 7:00) raken zonder Klantkraan vaak verloren in voicemail. Met Klantkraan neemt de AI-receptionist 24/7 op, herkent spoed (lekkage, gaslucht, riool-overstroming) en stuurt direct een sms naar de dienstdoende loodgieter.',
      },
      {
        q: 'Wat kost een loodgieter in Amsterdam gemiddeld per uur?',
        a: 'In Amsterdam ligt het uurtarief voor loodgieters doorgaans tussen €65–90 ex BTW, met voorrijkosten van €85–120 — hoger dan de meeste Nederlandse steden door parkeerdruk en bereikbaarheid binnen de Ring A10. Klantkraan noemt alleen tarieven die u zelf in uw systeem heeft gezet.',
      },
    ],
  },
  // ---- Priority 8
  {
    city: 'rotterdam',
    niche: 'loodgieter',
    nicheNote:
      'Naast particulier werk in Kralingen en Hillegersberg vinden Rotterdamse loodgieters een groot deel van de orderportefeuille in industrieel onderhoud (scheepswerven, raffinaderijen in Botlek) en in collectieve installaties van VvE’s. Veel galerijflats in Zuid hebben standleidingen uit de jaren ’60–’70 die nu massaal aan vervanging toe zijn — een opdrachtenstroom die de komende vijftien jaar groeit.',
    cityFaqs: [
      {
        q: 'Welke loodgieters in Rotterdam doen ook industriële opdrachten?',
        a: 'In Rotterdam werken meerdere loodgieters in Botlek, Pernis en op de Wilhelminapier met certificering voor procesinstallaties; de marktverdeling is geconcentreerd bij een handvol bedrijven. Klantkraan onderscheidt particuliere en industriële aanvragen in het intake-gesprek, zodat u die wachtrijen gescheiden kunt houden.',
      },
      {
        q: 'Wat zijn gangbare tarieven voor loodgieters in Rotterdam?',
        a: 'In Rotterdam ligt het uurtarief voor loodgieters doorgaans tussen €55–80 ex BTW, met voorrijkosten van €65–95. Industriële opdrachten in Botlek en op de Wilhelminapier worden vaak per project geoffreerd met certificeringseisen. Klantkraan noemt alleen tarieven die u zelf in uw systeem heeft gezet.',
      },
    ],
  },
  // ---- Priority 9
  {
    city: 'amsterdam',
    niche: 'dakdekker',
    nicheNote:
      'Amsterdamse dakdekkers verdelen hun werk over monumentaal pannenwerk in de Jordaan en Oud-Zuid, en grote vlakke daken in Nieuw-West en Zuidoost. De combinatie van strenge welstandseisen en steeds vaker hagel- en stormschade vergroot de vraag naar inspectie-rapporten met fotomateriaal, wat een hoge administratielast oplevert. Spoedklussen tijdens stormwaarschuwingen (oktober–februari) vragen om snelle inplanning binnen 24 uur.',
    cityFaqs: [
      {
        q: 'Hoe snel reageert een dakdekker in Amsterdam op stormschade?',
        a: 'Met Klantkraan wordt een stormschade-melding herkend zodra de beller "lekkage", "tegels eraf" of "noodreparatie" zegt — en direct als spoed gemarkeerd. De dakdekker krijgt binnen 60 seconden een sms met een Cal.com-link. Aangesloten Amsterdamse dakdekkers koppelen daar een 24-uurs noodprotocol aan: tijdelijke afdichting binnen 24 uur, definitieve reparatie binnen 5 werkdagen.',
      },
      {
        q: 'Wat kost een dakinspectie in Amsterdam?',
        a: 'In Amsterdam rekent een dakdekker doorgaans €120–250 voor een visuele dakinspectie met fotorapport; voor monumentale panden in de grachtengordel hoger door bereikbaarheid en welstandsadvies. Klantkraan plant inspecties automatisch in uw Cal.com-agenda en noemt alleen tarieven die u zelf heeft ingesteld.',
      },
    ],
  },
  // ---- Priority 10
  {
    city: 'rotterdam',
    niche: 'dakdekker',
    nicheNote:
      'De combinatie van platte daken in de naoorlogse wijken en zoutbelasting vanuit de haven betekent dat bitumendaken in Rotterdam doorgaans 15–20% sneller verouderen dan elders in Nederland. Veel Rotterdamse dakdekkers werken met meerjarige onderhoudscontracten voor woningcorporaties Vestia, Havensteder en Woonstad. Spoedklussen rond stormschade vragen om een 24-uurs inspectieprotocol — een belangrijk verschil met dakdekkers in Brabant of het oosten.',
    cityFaqs: [
      {
        q: 'Hoe lang gaat een bitumendak in Rotterdam mee?',
        a: 'Door zoutbelasting vanuit de haven gaan bitumendaken in Rotterdam-Zuid en de havenwijken doorgaans 15–20 jaar mee in plaats van de gebruikelijke 20–25 jaar in het binnenland. Aangesloten dakdekkers in Rotterdam adviseren tussentijdse inspectie elke vijf jaar. Klantkraan kan herhaalinspectie automatisch inplannen op basis van uw eigen onderhoudscyclus.',
      },
      {
        q: 'Wat zijn gangbare tarieven voor dakdekkers in Rotterdam?',
        a: 'In Rotterdam ligt het uurtarief voor dakdekkers doorgaans tussen €50–70 ex BTW, met voorrijkosten van €55–85. Meerjarige onderhoudscontracten met VvE’s en corporaties hebben lagere uurtarieven dan losse spoedklussen. Klantkraan noemt alleen tarieven die u zelf in uw systeem heeft gezet.',
      },
    ],
  },
]

// Helper: which Wave-1 niches exist for a given city — used by the page
// template to render cross-niche links in the same stad.
export function nichesForCity(citySlug: string): NicheSlug[] {
  return wave1.filter((c) => c.city === citySlug).map((c) => c.niche)
}

// Helper: which Wave-1 cities exist for a given niche — used for lateral
// SEO link blocks at the bottom of each page.
export function citiesForNiche(nicheSlug: NicheSlug): CitySlug[] {
  return wave1.filter((c) => c.niche === nicheSlug).map((c) => c.city)
}
