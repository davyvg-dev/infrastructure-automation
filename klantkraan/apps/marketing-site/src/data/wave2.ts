// Wave 2 — the next 10 city×niche combos in the programmatic-SEO rollout
// (research/programmatic-seo-blueprint.md §4, launch order pages 11-20).
// Same shape as wave1.ts: each combo carries the niche-in-city paragraph
// (≥50 words, ≥1 hyper-specific local detail) and 2 city-named FAQs
// (mandatory per blueprint §6 thin-content firewall).
//
// Not yet wired into getStaticPaths — Wave 2 ships T+6 weeks after Wave 1
// indexation per blueprint §6 staged-rollout cadence.

import type { CitySlug } from './cities'
import type { Faq, NicheSlug } from './niches'
import type { Combo } from './wave1'

export const wave2: Combo[] = [
  // ---- Priority 11
  {
    city: 'eindhoven',
    niche: 'loodgieter',
    nicheNote:
      'In Woensel-Noord en Woensel-Zuid staan grote naoorlogse galerijflats met collectieve standleidingen die nu massaal aan vervanging toe zijn; in Strijp-S en Strijp-T zijn voormalige Philips-fabriekspanden omgebouwd tot lofts met onorthodoxe leidingtracés. Veel Eindhovense loodgieters draaien daarnaast op het ASML-ecosysteem en de expat-instroom rond High Tech Campus en Brainport Industries Campus, met een hoge tenant-turnover die reactief werk — lekkende kranen, defecte boilers, verstopte afvoeren — domineert. Spoedwerk piekt rond vorstweekenden in januari en februari.',
    cityFaqs: [
      {
        q: 'Hoe snel kan een loodgieter in Eindhoven ter plaatse zijn bij een lekkage?',
        a: 'Bij spoedmeldingen die vóór 16:00 binnenkomen sturen aangesloten loodgieters in Eindhoven doorgaans nog dezelfde dag iemand voor een tijdelijke afdichting; bij meldingen na 16:00 is dat de volgende ochtend tussen 8:00 en 10:00. Klantkraan herkent spoed (vorstschade, gaslucht, riool-overstroming) automatisch en stuurt direct een sms naar de dienstdoende loodgieter met een Cal.com-link voor inplanning.',
      },
      {
        q: 'Wat zijn gangbare tarieven voor loodgieters in Eindhoven?',
        a: 'In Eindhoven ligt het uurtarief voor loodgieters doorgaans tussen €55–80 ex BTW, met voorrijkosten van €65–95. Spoedtoeslag bovenop het reguliere uurtarief is in Eindhoven gangbaar €45–80, met een minimum-belasting van een uur. Klantkraan noemt alleen tarieven die u zelf in uw systeem heeft gezet — geen verrassingen voor uw klant.',
      },
    ],
  },
  // ---- Priority 12
  {
    city: 'eindhoven',
    niche: 'dakdekker',
    nicheNote:
      'De vooroorlogse arbeiderswoningen in het Philipsdorp en Drents Dorp hebben pannendaken met loodslabben die elke twintig jaar herzien moeten worden; in Woensel en Achtse Barrier overheersen vlakke bitumendaken op rijwoningen uit de jaren ’60–’70. Veel Eindhovense dakdekkers werken in vaste roosters met VvE-besturen en de corporatie Woonbedrijf, naast losse particuliere opdrachten in Gestel en Tongelre. Industriële opdrachten rondom de High Tech Campus en Brainport Industries Campus vragen om certificering voor procesinstallaties.',
    cityFaqs: [
      {
        q: 'Hoe lang gaat een bitumendak in Eindhoven gemiddeld mee?',
        a: 'In Eindhoven gaan bitumendaken op naoorlogse rijwoningen in Woensel en Achtse Barrier doorgaans 20–25 jaar mee bij normaal onderhoud; tussentijdse inspectie elke vijf jaar voorkomt grote lekkages. Aangesloten dakdekkers in Eindhoven kunnen herhaalinspectie automatisch in uw Cal.com-agenda inplannen op basis van uw eigen onderhoudscyclus.',
      },
      {
        q: 'Wat kost een dakinspectie in Eindhoven?',
        a: 'In Eindhoven rekent een dakdekker doorgaans €100–200 voor een visuele dakinspectie met fotorapport; voor monumentale panden in het Philipsdorp of bij industriële opdrachten op de High Tech Campus loopt dat hoger door bereikbaarheid en certificeringseisen. Klantkraan plant inspecties automatisch in uw agenda en noemt alleen tarieven die u zelf heeft ingesteld.',
      },
    ],
  },
  // ---- Priority 13
  {
    city: 'den-haag',
    niche: 'loodgieter',
    nicheNote:
      'Haagse loodgieters verdelen hun werk tussen monumentale panden in het Statenkwartier en de Archipelbuurt — met krappe leidingschachten en strenge VvE-regels — en grote naoorlogse complexen in Moerwijk en Morgenstond, waar standleidingen uit de jaren ’50 nu aan vervanging toe zijn. Aan de Scheveningse kustlijn versnelt zoutdamp-corrosie op cv-installaties en buitenleidingen, met dunnere onderhoudsintervallen tot gevolg. Spoedwerk concentreert zich rond vorstperiodes en in de horeca-as Plein–Grote Markt.',
    cityFaqs: [
      {
        q: 'Is een loodgieter in Den Haag ook in het weekend bereikbaar?',
        a: 'Met Klantkraan wel — de AI-receptionist neemt 24/7 op, herkent spoed (vorstschade, riool-overstroming, gasluchten) en stuurt direct een sms naar de dienstdoende loodgieter met een Cal.com-link voor inplanning. Veel Haagse zaterdagvraag blijft zonder Klantkraan bij voicemail steken — een typische missed-call gap die wij dichten.',
      },
      {
        q: 'Wat kost een spoed-loodgieter in Den Haag?',
        a: 'In Den Haag ligt de spoedtoeslag voor loodgieters doorgaans tussen €55–95 boven het reguliere uurtarief (€65–85 ex BTW), met een minimum-belasting van een uur. In Scheveningen en Duindorp komt soms een extra zoutdamp-toeslag op buitenwerk. Klantkraan benoemt de spoedtoeslag in het gesprek alleen wanneer u die zelf heeft ingesteld.',
      },
    ],
  },
  // ---- Priority 14
  {
    city: 'den-haag',
    niche: 'dakdekker',
    nicheNote:
      'In het Statenkwartier, Bezuidenhout en de Archipelbuurt staan veel rijksmonumenten met gemetselde topgevels, loden goten en pannendaken die elke twintig jaar herzien moeten worden onder welstandstoezicht. In Scheveningen en Duindorp versnelt zoutdamp-corrosie het verouderen van dakranden en zinkwerk — gemiddeld 10–15% sneller dan elders in Den Haag. Veel Haagse dakdekkers werken met meerjarige onderhoudscontracten voor woningcorporaties Staedion en Haag Wonen, naast spoedinspecties bij stormwaarschuwingen langs de kustlijn.',
    cityFaqs: [
      {
        q: 'Hoe snel reageert een dakdekker in Den Haag op stormschade?',
        a: 'Met Klantkraan wordt een stormschade-melding herkend zodra de beller "lekkage", "tegels eraf" of "noodreparatie" zegt — en direct als spoed gemarkeerd. De dakdekker krijgt binnen 60 seconden een sms met een Cal.com-link. Aangesloten Haagse dakdekkers koppelen daar een 24-uurs noodprotocol aan: tijdelijke afdichting binnen 24 uur, definitieve reparatie binnen 5 werkdagen.',
      },
      {
        q: 'Wat kost een dakinspectie in Den Haag?',
        a: 'In Den Haag rekent een dakdekker doorgaans €130–250 voor een visuele dakinspectie met fotorapport; voor monumentale panden in het Statenkwartier of de Archipelbuurt loopt dat hoger door bereikbaarheid en welstandsadvies. Klantkraan plant inspecties automatisch in uw Cal.com-agenda en noemt alleen tarieven die u zelf heeft ingesteld.',
      },
    ],
  },
  // ---- Priority 15
  {
    city: 'amsterdam',
    niche: 'aannemer',
    nicheNote:
      'Amsterdamse aannemers werken tussen drie zeer verschillende werelden: kleinschalige renovaties in 17e-eeuwse grachtenpanden onder monumententoezicht, projectmatige badkamer- en keukenrenovaties via VvE’s in Oud-Zuid en De Pijp, en grootschalige nieuwbouwclusters in Noord, Zuidoost en IJburg. Vergunningstrajecten met de gemeente Amsterdam en welstandscommissies lopen vaak zes tot acht weken; dakkapellen op de Jordaan vragen om beeldkwaliteits-akkoord. Veel werk loopt via woningcorporaties Ymere, Stadgenoot en Eigen Haard, met meerjarige raamovereenkomsten.',
    cityFaqs: [
      {
        q: 'Hoe lang van tevoren moet ik een aannemer in Amsterdam boeken voor een verbouwing?',
        a: 'Voor een gemiddelde verbouwing in Amsterdam zijn aannemers doorgaans drie tot zes maanden vooruit volgeboekt; voor de grachtengordel en Oud-Zuid vaak nog langer door welstands- en vergunningstrajecten. Klantkraan boekt offerteaanvragen direct in als terugbel-afspraak in uw Cal.com-agenda, zodat aanvragen niet drie dagen blijven liggen voordat u kunt reageren.',
      },
      {
        q: 'Wat kost een dakkapel in Amsterdam gemiddeld?',
        a: 'In Amsterdam ligt de prijs voor een standaard dakkapel doorgaans tussen €7.500–14.000 inclusief vergunning en plaatsing; in de grachtengordel en Jordaan loopt dat hoger door welstandseisen en bereikbaarheid (vaak kraanwerk vanuit de straat). Klantkraan noemt alleen tarieven die u zelf in uw systeem heeft gezet.',
      },
    ],
  },
  // ---- Priority 16
  {
    city: 'rotterdam',
    niche: 'aannemer',
    nicheNote:
      'Rotterdamse aannemers vinden een groot deel van de orderportefeuille in stadsvernieuwing: galerijflats in Zuidwijk en Pendrecht uit de jaren ’50–’60 die nu casco-gerenoveerd worden, en grootschalige hoogbouw rond de Wilhelminapier en het Schiekadeblok. Particulier werk concentreert zich in Kralingen en Hillegersberg, met badkamer- en keukenrenovaties als standaardklus. Veel werk loopt via de woningcorporaties Vestia, Havensteder en Woonstad onder meerjarige onderhoudscontracten. Industrieel werk in Botlek en Pernis vraagt aparte certificering.',
    cityFaqs: [
      {
        q: 'Welke aannemers in Rotterdam doen ook stadsvernieuwingsprojecten?',
        a: 'In Rotterdam werken meerdere aannemers in vaste raamovereenkomsten met Vestia, Havensteder en Woonstad voor casco-renovaties in Zuidwijk, Pendrecht en het Oude Noorden. Klantkraan onderscheidt particuliere en projectaanvragen in het intake-gesprek, zodat u die wachtrijen gescheiden kunt houden — handig als u in beide werelden actief bent.',
      },
      {
        q: 'Wat kost een verbouwing in Rotterdam gemiddeld?',
        a: 'In Rotterdam ligt het uurtarief voor aannemers doorgaans tussen €55–80 ex BTW, met een gemiddelde badkamerrenovatie tussen €9.000–18.000 inclusief sanitair en tegelwerk. In Kralingen en Hillegersberg loopt dat hoger door grotere woningen; industriële opdrachten op de Wilhelminapier worden per project geoffreerd. Klantkraan noemt alleen tarieven die u zelf heeft ingesteld.',
      },
    ],
  },
  // ---- Priority 17
  {
    city: 'eindhoven',
    niche: 'schilder',
    nicheNote:
      'Eindhovense schilders splitsen hun werk tussen herhalingsopdrachten voor VvE’s van galerijflats in Woensel en Achtse Barrier, en hoogwaardig binnenwerk voor particulieren in Gestel en Tongelre. De omgebouwde Philips-panden in Strijp-S en Strijp-T vragen om industriële verfsystemen met certificering; veel lofts hebben betonnen wanden die specifieke voorbehandeling vereisen. Aan de rand van de stad — rond de High Tech Campus en Brainport Industries Campus — werken schilders aan bedrijfspanden met meerjarige onderhoudscontracten. De lente-piek loopt van eind maart tot juni.',
    cityFaqs: [
      {
        q: 'Hoe lang van tevoren moet ik een schilder in Eindhoven boeken voor buitenwerk?',
        a: 'Voor buitenwerk in het hoogseizoen (april–september) zijn de meeste Eindhovense schilders vier tot zes weken vooruit volgeboekt. Klantkraan boekt offerteaanvragen direct in als terugbel-afspraak in uw Cal.com-agenda, zodat aanvragen niet drie dagen blijven liggen voordat u kunt reageren — een typische lekkage in het schildersseizoen.',
      },
      {
        q: 'Hoeveel kost binnenschilderwerk in Eindhoven gemiddeld?',
        a: 'In Eindhoven rekenen schilders voor binnenwerk doorgaans €28–42 per m² inclusief sausen en aflakken; voor de lofts in Strijp-S en Strijp-T loopt dat hoger door specifieke voorbehandeling van betonnen wanden. Klantkraan kan een eerste m²-indicatie geven aan de hand van uw eigen tarieven en de opgegeven oppervlakte.',
      },
    ],
  },
  // ---- Priority 18
  {
    city: 'eindhoven',
    niche: 'aannemer',
    nicheNote:
      'De groei van Eindhoven loopt grotendeels via het ASML-ecosysteem en de Brainport-regio; aannemers werken aan expat-woningen rond de High Tech Campus, dakkapellen op de naoorlogse rijwoningen in Woensel en grootschalige nieuwbouw in Meerhoven en Acht. De omgebouwde Philips-panden in Strijp-S en Strijp-T leveren een continue stroom afbouw- en interieuropdrachten op. Veel aannemers werken met meerjarige raamovereenkomsten van de corporatie Woonbedrijf, naast particuliere verbouwingen in Gestel en Tongelre.',
    cityFaqs: [
      {
        q: 'Hoe lang van tevoren moet ik een aannemer in Eindhoven boeken voor een verbouwing?',
        a: 'Voor een gemiddelde verbouwing in Eindhoven zijn aannemers doorgaans twee tot vier maanden vooruit volgeboekt; voor projecten rond de High Tech Campus en Brainport Industries Campus kunnen vergunningstrajecten dat verlengen. Klantkraan boekt offerteaanvragen direct in als terugbel-afspraak, zodat aanvragen niet blijven liggen tijdens uw drukste maanden.',
      },
      {
        q: 'Wat kost een dakkapel in Eindhoven gemiddeld?',
        a: 'In Eindhoven ligt de prijs voor een standaard dakkapel doorgaans tussen €6.500–11.500 inclusief vergunning en plaatsing; voor de vooroorlogse rijwoningen in het Philipsdorp loopt dat soms hoger door welstandsadvies. Klantkraan noemt alleen tarieven die u zelf in uw systeem heeft gezet — geen verrassingen voor uw klant.',
      },
    ],
  },
  // ---- Priority 19
  {
    city: 'utrecht',
    niche: 'aannemer',
    nicheNote:
      'Utrechtse aannemers werken in een breed gespreide markt: monumentenrenovatie langs de Oudegracht en in Wijk C onder welstandstoezicht, hoogwaardig particulier werk in Tuindorp en Oog in Al, en grootschalige nieuwbouw in Leidsche Rijn en Vleuten-De Meern waar elk jaar duizenden woningen worden opgeleverd. Veel werk loopt via de woningcorporaties Mitros en Bo-Ex onder meerjarige raamovereenkomsten. Dakkapellen op de naoorlogse rijwoningen in Kanaleneiland en Overvecht vormen een stabiele orderstroom; verbouwingen voor expats rond De Uithof zijn typisch korte trajecten.',
    cityFaqs: [
      {
        q: 'Hoe lang van tevoren moet ik een aannemer in Utrecht boeken voor een verbouwing?',
        a: 'Voor een gemiddelde verbouwing in Utrecht zijn aannemers doorgaans drie tot vijf maanden vooruit volgeboekt; voor monumenten langs de Oudegracht of in Wijk C lopen welstands- en vergunningstrajecten daar nog zes tot acht weken bovenop. Klantkraan boekt offerteaanvragen direct in als terugbel-afspraak in uw Cal.com-agenda, zodat aanvragen niet blijven liggen.',
      },
      {
        q: 'Wat kost een dakkapel in Utrecht gemiddeld?',
        a: 'In Utrecht ligt de prijs voor een standaard dakkapel doorgaans tussen €7.000–12.500 inclusief vergunning en plaatsing; voor monumentale panden langs de Oudegracht loopt dat hoger door welstandseisen en bereikbaarheid. In Leidsche Rijn worden veel dakkapellen via aannemerscontracten gefactureerd. Klantkraan noemt alleen tarieven die u zelf heeft ingesteld.',
      },
    ],
  },
  // ---- Priority 20
  {
    city: 'haarlem',
    niche: 'loodgieter',
    nicheNote:
      'Haarlemse loodgieters werken voornamelijk in oude woningvoorraad: 17e- en 18e-eeuwse grachtenpanden langs het Spaarne en in de Vijfhoek hebben krappe leidingschachten en historische koper- en loodleidingen die bij vorst snel scheuren. In Schalkwijk en de Slachthuisbuurt staan grote naoorlogse galerijflats met collectieve standleidingen die nu aan vervanging toe zijn. Veel werk loopt via de woningcorporaties Ymere, Pré Wonen en Elan Wonen. Spoedwerk piekt rond vorstweekenden in januari en februari, met een hoge concentratie meldingen uit de Vijfhoek.',
    cityFaqs: [
      {
        q: 'Hoe snel kan een loodgieter in Haarlem ter plaatse zijn bij een lekkage?',
        a: 'Bij spoedmeldingen die vóór 16:00 binnenkomen sturen aangesloten loodgieters in Haarlem doorgaans nog dezelfde dag iemand voor een tijdelijke afdichting; bij meldingen na 16:00 is dat de volgende ochtend tussen 8:00 en 10:00. Klantkraan herkent spoed (vorstschade, gaslucht, riool-overstroming) automatisch en stuurt direct een sms naar de dienstdoende loodgieter met een Cal.com-link voor inplanning.',
      },
      {
        q: 'Wat zijn gangbare tarieven voor loodgieters in Haarlem?',
        a: 'In Haarlem ligt het uurtarief voor loodgieters doorgaans tussen €60–85 ex BTW, met voorrijkosten van €70–100 — iets boven het landelijke gemiddelde door de nabijheid van Amsterdam en parkeerdruk in de Vijfhoek. Klantkraan noemt alleen tarieven die u zelf in uw systeem heeft gezet — geen verrassingen voor uw klant.',
      },
    ],
  },
]

// Helper: which Wave-2 niches exist for a given city — mirrors wave1.ts so the
// page template can render cross-niche links in the same stad once Wave 2 is
// wired into getStaticPaths.
export function nichesForCityWave2(citySlug: string): NicheSlug[] {
  return wave2.filter((c) => c.city === citySlug).map((c) => c.niche)
}

// Helper: which Wave-2 cities exist for a given niche — used for lateral
// SEO link blocks at the bottom of each page.
export function citiesForNicheWave2(nicheSlug: NicheSlug): CitySlug[] {
  return wave2.filter((c) => c.niche === nicheSlug).map((c) => c.city)
}

// Re-export Faq so consumers of wave2 don't need to import from niches.ts
// directly — keeps the import surface symmetric with wave1.ts.
export type { Faq }
