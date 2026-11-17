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
      'De oude panden langs de Oudegracht hebben gemetselde topgevels met loden goten die elke twintig jaar herzien moeten worden; in de naoorlogse wijken Kanaleneiland en Overvecht overheersen vlakke bitumendaken die elke tien jaar onderhoud vragen. Veel dakdekkers in Utrecht werken volgens vaste schema’s voor VvE-besturen en de corporaties Mitros en Bo-Ex, naast losse particuliere opdrachten in Lombok en Wittevrouwen. In Leidsche Rijn liggen relatief jonge daken, maar de eerste vervangingsronde komt rond 2030 in zicht.',
    cityFaqs: [
      {
        q: 'Hoe snel kan een dakdekker in Utrecht ter plaatse zijn bij een lekkage?',
        a: 'Dat bepaalt u zelf. Bij een lekkage vraagt de receptionist meteen naar adres en schade en meldt die direct aan u. U beslist of u nog dezelfde dag iemand stuurt. Klantkraan herkent een lekkage in het gesprek en plant de inspectie in uw agenda, zodat u niet eerst hoeft terug te bellen.',
      },
      {
        q: 'Wat zijn gangbare tarieven voor dakdekkers in Utrecht?',
        a: 'In Utrecht ligt het uurtarief voor dakdekkers doorgaans tussen € 55 en € 75 excl. btw, met voorrijkosten van € 65 tot € 95. Materiaal en specialistisch werk (loodwerk, dakkapelafdichting, zinkwerk in het beschermd stadsgezicht) komen daar bovenop. Klantkraan noemt alleen tarieven die u zelf heeft ingesteld en verzint geen bedragen.',
      },
    ],
  },
  // ---- Priority 2
  {
    city: 'den-haag',
    niche: 'schilder',
    nicheNote:
      'Het Statenkwartier, de Archipelbuurt en de Vogelwijk hebben veel monumentale gevels die elke zeven tot tien jaar geschilderd moeten worden, vaak met door welstand voorgeschreven kleurstellingen en glansgraden. In Scheveningen en Duindorp zorgt zoutdamp voor corrosie, wat extra schuurwerk en grondering vraagt aan kozijnen en hekwerk. Veel Haagse schildersbedrijven splitsen het seizoen: buitenwerk van april tot september, binnen- en lakwerk van oktober tot maart, met spuitwerk in een vaste werkplaats.',
    cityFaqs: [
      {
        q: 'Hoe lang van tevoren moet ik een schilder in Den Haag boeken voor buitenwerk?',
        a: 'Voor buitenwerk in het hoogseizoen (april tot september) zijn de meeste Haagse schilders zes tot acht weken vooruit volgeboekt; voor het Statenkwartier en de Archipelbuurt vaak nog langer. Klantkraan zet offerteaanvragen direct als terugbelafspraak in uw agenda, zodat ze niet drie dagen blijven liggen voordat u kunt reageren.',
      },
      {
        q: 'Hoeveel kost binnenschilderwerk in Den Haag gemiddeld?',
        a: 'In Den Haag rekenen schilders voor binnenwerk doorgaans € 30 tot € 45 per m², inclusief sausen en aflakken; voor monumentale panden in het Statenkwartier of de Archipelbuurt loopt dat hoger door specifiek kleuradvies en stucwerkvoorbereiding. Klantkraan kan een eerste m²-indicatie geven aan de hand van uw eigen tarieven en de opgegeven oppervlakte.',
      },
    ],
  },
  // ---- Priority 3
  {
    city: 'utrecht',
    niche: 'loodgieter',
    nicheNote:
      'De grachtenpanden in Wijk C hebben dunne lood- en koperleidingen die bij vorst snel scheuren; in Leidsche Rijn werken loodgieters vaak in nieuwbouwclusters met collectieve cv-stations en stadsverwarming van Eneco. Door de vele studenten en expats rond De Uithof wisselen huurders vaak, waardoor reactieve klussen (lekkende kranen, verstopte afvoeren, defecte boilers) een groot deel van de orderportefeuille van veel Utrechtse loodgieters vullen. Spoedwerk concentreert zich rond vorstweekenden in januari en februari.',
    cityFaqs: [
      {
        q: 'Is een loodgieter in Utrecht ook in het weekend bereikbaar?',
        a: 'Met Klantkraan wel. De AI-receptionist neemt dag en nacht op, herkent spoed (vorstschade, een overstromend riool, gaslucht) en stuurt direct een sms met een planningslink naar de dienstdoende loodgieter. Zonder Klantkraan blijft veel vraag op zaterdag in de voicemail hangen.',
      },
      {
        q: 'Wat kost een spoed-loodgieter in Utrecht?',
        a: 'In Utrecht ligt de spoedtoeslag voor loodgieters doorgaans tussen € 45 en € 85 boven het gewone uurtarief (€ 55 tot € 75 excl. btw), en er wordt minimaal een uur gerekend. Klantkraan noemt de spoedtoeslag in het gesprek alleen als u die zelf heeft ingesteld, zodat uw klant niet voor verrassingen staat.',
      },
    ],
  },
  // ---- Priority 4
  {
    city: 'utrecht',
    niche: 'schilder',
    nicheNote:
      'De gevelschilder in Utrecht heeft te maken met strikte welstandsregels langs de Oudegracht en in Wittevrouwen, waar kleurkeuze en glansgraad zijn vastgelegd in beeldkwaliteitsplannen. Veel particuliere opdrachten zijn binnenwerk: studentenkamers in Lombok en Tuinwijk, en eengezinswoningen in Tuindorp en Oog in Al. De lentepiek loopt van eind maart tot juni; in oktober volgt nog een korte piek voor binnenschilderwerk vóór de winter.',
    cityFaqs: [
      {
        q: 'Welke kleuren mag ik voor een gevel in Utrecht kiezen?',
        a: 'In het beschermd stadsgezicht (Binnenstad, Wittevrouwen, deel van Wijk C) gelden beeldkwaliteitsplannen die kleur en glansgraad voorschrijven; u vraagt een omgevingsvergunning aan bij de gemeente Utrecht voordat u start. Veel Utrechtse schilders zetten vooraf een proefvlak op de gevel; Klantkraan zet die afspraak in uw agenda.',
      },
      {
        q: 'Hoeveel kost gevelschilderwerk in Utrecht?',
        a: 'Voor een gemiddelde tussenwoning in Utrecht ligt het tarief voor al het schilderwerk aan de gevel (kozijnen, deuren, dakranden) rond € 1.800 tot € 3.500, afhankelijk van houtsoort en welstandsregels. Voor monumentale panden langs de Oudegracht is dat hoger. Klantkraan noemt alleen tarieven die u zelf heeft ingesteld.',
      },
    ],
  },
  // ---- Priority 5
  {
    city: 'amsterdam',
    niche: 'schilder',
    nicheNote:
      'In de Amsterdamse grachtengordel zijn schilders gebonden aan welstandseisen voor zichtbare gevels en kozijn-, deur- en hekwerkkleuren; veel opdrachten lopen via VvE’s en monumentenrestaurateurs. In Oud-Zuid en De Pijp domineert hoogwaardig binnenwerk voor particulieren met budget; in Noord en Nieuw-West is er veel projectmatig spuitwerk voor de woningcorporaties Ymere en Stadgenoot. De winterpiek voor binnenwerk is in Amsterdam vrijwel even groot als de zomerpiek voor buitenwerk, wat binnen de G4 uniek is.',
    cityFaqs: [
      {
        q: 'Welke kleuren zijn toegestaan voor een gevel in Amsterdam-Centrum?',
        a: 'In het beschermde stadsgezicht (grachtengordel, Jordaan, Plantagebuurt) is de kleurkeuze gebonden aan de welstandsnota Amsterdam. Veel schilders werken met een vaste kleurenwaaier per buurt en stemmen vooraf af met de monumentencommissie. Klantkraan zet het VvE-overleg of de afspraak met welstand in uw agenda.',
      },
      {
        q: 'Wat is een gangbaar tarief voor binnenschilderwerk in Amsterdam?',
        a: 'In Amsterdam liggen tarieven voor binnenschilderwerk doorgaans tussen € 35 en € 55 per m², inclusief sausen en aflakken; in Oud-Zuid en de grachtengordel hoger door specifieke kleurkeuze, stucwerkvoorbereiding en parkeerlasten. Klantkraan noemt alleen tarieven die u zelf heeft ingesteld.',
      },
    ],
  },
  // ---- Priority 6
  {
    city: 'rotterdam',
    niche: 'schilder',
    nicheNote:
      'Rotterdamse schilders splitsen hun werk tussen herhalingsopdrachten voor VvE’s van galerijflats in Zuidwijk en Pendrecht, en particuliere binnenklussen in Kralingen en Hillegersberg. Het Schiekadeblok en de Wilhelminapier vragen industriële verfsystemen met certificering. De zoutbelasting in de havenwijken (Charlois, Pernis) versnelt corrosie op kozijnen, wat kortere intervallen tussen schilderbeurten betekent dan elders in de Randstad.',
    cityFaqs: [
      {
        q: 'Hoe vaak moet ik kozijnen in Rotterdam laten schilderen?',
        a: 'In het Rotterdamse havengebied (Charlois, Pernis, Heijplaat) moeten houten kozijnen door corrosie van zoutdamp elke 5 tot 7 jaar geschilderd worden; in Kralingen of Hillegersberg is dat doorgaans elke 7 tot 10 jaar. Klantkraan kan herhaalafspraken in uw agenda zetten op basis van uw eigen onderhoudscyclus.',
      },
      {
        q: 'Wat kost gevelschilderwerk in Rotterdam?',
        a: 'Voor een tussenwoning in Rotterdam-Zuid rekent een schilder doorgaans € 1.500 tot € 3.000 voor al het schilderwerk aan de gevel; in Hillegersberg en Kralingen hoger door grotere geveloppervlakten. Industriële opdrachten op de Wilhelminapier zijn aparte calculaties met certificeringseis. Klantkraan noemt alleen tarieven die u zelf heeft ingesteld.',
      },
    ],
  },
  // ---- Priority 7
  {
    city: 'amsterdam',
    niche: 'loodgieter',
    nicheNote:
      'Amsterdamse loodgieters werken vaak met krappe leidingschachten in 17e-eeuwse panden en strenge VvE-regels rond standleidingen in galerijflats in Zuidoost. Spoedwerk concentreert zich rond vorstperiodes en de horeca rond het Rembrandtplein en het Leidseplein. De combinatie van VvE-administratie, oude woningvoorraad en hoge concentratie expat-huurders maakt nazorg en reviews zwaarder wegen dan in de meeste andere Nederlandse steden.',
    cityFaqs: [
      {
        q: 'Welke spoedloodgieter is in Amsterdam-Centrum 24/7 bereikbaar?',
        a: 'Veel Amsterdamse loodgieters werken dag en nacht tegen spoedtoeslag, maar oproepen na 22:00 en vóór 07:00 belanden zonder Klantkraan vaak in de voicemail. Met Klantkraan neemt de AI-receptionist dag en nacht op, herkent spoed (lekkage, gaslucht, een overstromend riool) en stuurt direct een sms naar de dienstdoende loodgieter.',
      },
      {
        q: 'Wat kost een loodgieter in Amsterdam gemiddeld per uur?',
        a: 'In Amsterdam ligt het uurtarief voor loodgieters doorgaans tussen € 65 en € 90 excl. btw, met voorrijkosten van € 85 tot € 120. Dat is hoger dan in de meeste Nederlandse steden, door parkeerdruk en de bereikbaarheid binnen de Ring A10. Klantkraan noemt alleen tarieven die u zelf heeft ingesteld.',
      },
    ],
  },
  // ---- Priority 8
  {
    city: 'rotterdam',
    niche: 'loodgieter',
    nicheNote:
      'Naast particulier werk in Kralingen en Hillegersberg vinden Rotterdamse loodgieters een groot deel van de orderportefeuille in industrieel onderhoud (scheepswerven, raffinaderijen in Botlek) en in collectieve installaties van VvE’s. Veel galerijflats in Zuid hebben standleidingen uit de jaren zestig en zeventig die nu op grote schaal aan vervanging toe zijn. Die stroom opdrachten groeit de komende vijftien jaar.',
    cityFaqs: [
      {
        q: 'Welke loodgieters in Rotterdam doen ook industriële opdrachten?',
        a: 'In Rotterdam werken meerdere loodgieters in Botlek, Pernis en op de Wilhelminapier met certificering voor procesinstallaties; de marktverdeling is geconcentreerd bij een handvol bedrijven. Klantkraan onderscheidt particuliere en industriële aanvragen in het intakegesprek, zodat u die wachtrijen gescheiden kunt houden.',
      },
      {
        q: 'Wat zijn gangbare tarieven voor loodgieters in Rotterdam?',
        a: 'In Rotterdam ligt het uurtarief voor loodgieters doorgaans tussen € 55 en € 80 excl. btw, met voorrijkosten van € 65 tot € 95. Industriële opdrachten in Botlek en op de Wilhelminapier worden vaak per project geoffreerd, met certificeringseisen. Klantkraan noemt alleen tarieven die u zelf heeft ingesteld.',
      },
    ],
  },
  // ---- Priority 9
  {
    city: 'amsterdam',
    niche: 'dakdekker',
    nicheNote:
      'Amsterdamse dakdekkers verdelen hun werk over monumentaal pannenwerk in de Jordaan en Oud-Zuid, en grote vlakke daken in Nieuw-West en Zuidoost. De combinatie van strenge welstandseisen en steeds vaker hagel- en stormschade vergroot de vraag naar inspectierapporten met foto’s, wat een hoge administratielast oplevert. Spoedklussen tijdens stormwaarschuwingen (oktober tot februari) moeten binnen 24 uur ingepland worden.',
    cityFaqs: [
      {
        q: 'Hoe snel reageert een dakdekker in Amsterdam op stormschade?',
        a: 'Klantkraan herkent een melding van stormschade zodra de beller "lekkage", "tegels eraf" of "noodreparatie" zegt, en markeert die direct als spoed. De dakdekker krijgt binnen 60 seconden een sms met een planningslink. U kunt daar uw eigen noodprotocol aan koppelen, bijvoorbeeld tijdelijke afdichting binnen 24 uur en definitieve reparatie binnen 5 werkdagen.',
      },
      {
        q: 'Wat kost een dakinspectie in Amsterdam?',
        a: 'In Amsterdam rekent een dakdekker doorgaans € 120 tot € 250 voor een visuele dakinspectie met fotorapport; voor monumentale panden in de grachtengordel meer, door bereikbaarheid en welstandsadvies. Klantkraan plant inspecties in uw agenda en noemt alleen tarieven die u zelf heeft ingesteld.',
      },
    ],
  },
  // ---- Priority 10
  {
    city: 'rotterdam',
    niche: 'dakdekker',
    nicheNote:
      'De combinatie van platte daken in de naoorlogse wijken en zoutbelasting vanuit de haven betekent dat bitumendaken in Rotterdam doorgaans 15 tot 20% sneller verouderen dan elders in Nederland. Veel Rotterdamse dakdekkers werken met meerjarige onderhoudscontracten voor de woningcorporaties Vestia, Havensteder en Woonstad. Spoedklussen bij stormschade vragen om inspectie binnen 24 uur, een belangrijk verschil met dakdekkers in Brabant of het oosten.',
    cityFaqs: [
      {
        q: 'Hoe lang gaat een bitumendak in Rotterdam mee?',
        a: 'Door zoutbelasting vanuit de haven gaan bitumendaken in Rotterdam-Zuid en de havenwijken doorgaans 15 tot 20 jaar mee, in plaats van de gebruikelijke 20 tot 25 jaar in het binnenland. Een tussentijdse inspectie elke vijf jaar is daarom verstandig. Klantkraan kan een herhaalinspectie inplannen op basis van uw eigen onderhoudscyclus.',
      },
      {
        q: 'Wat zijn gangbare tarieven voor dakdekkers in Rotterdam?',
        a: 'In Rotterdam ligt het uurtarief voor dakdekkers doorgaans tussen € 50 en € 70 excl. btw, met voorrijkosten van € 55 tot € 85. Meerjarige onderhoudscontracten met VvE’s en corporaties hebben lagere uurtarieven dan losse spoedklussen. Klantkraan noemt alleen tarieven die u zelf heeft ingesteld.',
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
