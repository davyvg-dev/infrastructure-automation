// City data for the programmatic /[stad]/[vak] route.
// Per blueprint (research/programmatic-seo-blueprint.md §5): each city carries
// a city-unique intro paragraph (≥100 words), neighbourhood list, price tier
// descriptor and lateral-link list. Niche-specific framing lives in wave1.ts.

export type CitySlug =
  | 'amsterdam'
  | 'rotterdam'
  | 'den-haag'
  | 'utrecht'
  | 'eindhoven'
  | 'haarlem'

export interface City {
  slug: CitySlug
  name: string // 'Amsterdam', 'Den Haag'
  province: string
  // Population per CBS Jan 2026 (Wikipedia citing CBS dataset 37230ned).
  population: number
  // Unique paragraph — 100+ words about housing stock + economy.
  // Must NOT be a templated city swap; this is the thin-content firewall.
  intro: string
  neighbourhoods: string[] // 6-8 districts, used for buurt-section
  priceTier: 'hoog' | 'gemiddeld-hoog' | 'gemiddeld'
  // 1-sentence price context for the niche-agnostic pricing block.
  priceContext: string
  // Slugs of neighbouring Wave-1 cities (for lateral SEO links).
  lateralCitySlugs: CitySlug[]
}

export const cities: Record<CitySlug, City> = {
  amsterdam: {
    slug: 'amsterdam',
    name: 'Amsterdam',
    province: 'Noord-Holland',
    population: 942500,
    intro:
      'De Amsterdamse grachtengordel telt ongeveer 7.000 monumentale woonhuizen uit de zeventiende en achttiende eeuw, waarvan een groot deel is opgesplitst tot appartementen en commerciële etages. Daaromheen liggen 19e-eeuwse uitbreidingen (Oud-West, De Pijp, Oud-Zuid, Jordaan) en grote naoorlogse blokken in Noord, Nieuw-West en Zuidoost. Voor vakmensen betekent dat: krappe leidingschachten in oude panden, smalle gevels die zonder kraan bereikt moeten worden, VvE-vergaderingen voor elke ingreep en strenge welstandseisen voor zichtbare werkzaamheden aan voorgevels in beschermd stadsgezicht. De prospect-mix is breed: particulieren, VvE-besturen, makelaars en commercieel vastgoed in de uitgaansgebieden. Tarieven liggen 20–30% boven het Nederlandse gemiddelde door parkeerkosten en de beperkte bereikbaarheid binnen de Ring A10.',
    neighbourhoods: [
      'Centrum',
      'De Pijp',
      'Oud-Zuid',
      'Oud-West',
      'Jordaan',
      'Noord',
      'Nieuw-West',
      'Zuidoost',
    ],
    priceTier: 'hoog',
    priceContext:
      'Voorrijkosten in Amsterdam liggen doorgaans tussen €85–120 en het uurtarief 20–30% boven het landelijke gemiddelde door parkeerdruk en de slechte bereikbaarheid binnen de Ring A10.',
    lateralCitySlugs: ['rotterdam', 'den-haag', 'utrecht', 'haarlem'],
  },
  rotterdam: {
    slug: 'rotterdam',
    name: 'Rotterdam',
    province: 'Zuid-Holland',
    population: 608500,
    intro:
      'Na het bombardement van mei 1940 is een groot deel van de Rotterdamse binnenstad herbouwd in modernistische bouwstijl; daarbuiten staat een uitgebreid arsenaal vooroorlogse blokken in Kralingen, Hillegersberg en het Oude Noorden, naast grote naoorlogse wijken als Zuidwijk en Pendrecht. Rotterdam heeft meer flats dan welke andere G4-stad ook — ruim 60% van de woningvoorraad — en daarmee een uitzonderlijk groot aantal VvE’s. Voor vakmensen betekent dit veel VvE-werk, hoge concentraties standleidingen in galerijflats, vlakke daken die om de tien jaar herzien moeten worden en een industriële opdrachtmarkt rond de haven, Schiekadeblok en Wilhelminapier. De Rotterdamse woningvoorraad veroudert ongelijk: zoutbelasting in de havenwijken (Charlois, Pernis) versnelt corrosie, terwijl het centrum vrij jong is. Tarieven liggen iets onder Amsterdam maar boven het landelijke gemiddelde.',
    neighbourhoods: [
      'Centrum',
      'Kralingen',
      'Hillegersberg',
      'Delfshaven',
      'Oude Noorden',
      'Charlois',
      'Feijenoord',
      'Prins Alexander',
    ],
    priceTier: 'gemiddeld-hoog',
    priceContext:
      'In Rotterdam liggen voorrijkosten rond €65–95 en het uurtarief 5–15% boven het landelijke gemiddelde; haven-, industrie- en hoogbouwopdrachten vragen wel om aparte calculaties.',
    lateralCitySlugs: ['amsterdam', 'den-haag', 'utrecht'],
  },
  'den-haag': {
    slug: 'den-haag',
    name: 'Den Haag',
    province: 'Zuid-Holland',
    population: 569000,
    intro:
      'Den Haag combineert een dichte ambtelijke kern (Centrum, Bezuidenhout, Statenkwartier) met grote 19e-eeuwse woongebieden zoals de Archipelbuurt en de Vogelwijk en naoorlogse wijken in het zuidwesten (Moerwijk, Morgenstond, Loosduinen). De stad telt veel rijksmonumenten en heeft strikte welstandseisen rond het regeringscentrum en in de Vogelwijk. Voor vakmensen betekent dat: relatief veel beleidsgevoelige opdrachtgevers — ministeries, ambassades, NGO’s — naast een grote particuliere markt rondom de Scheveningse zee. In Scheveningen en Duindorp speelt zoutdamp-corrosie, wat extra schuurwerk en grondering vraagt aan iedere buitenoppervlakte. Tarieven volgen Amsterdam vrij dicht; de onderhoudspiek voor buitenwerkzaamheden loopt van april tot oktober en valt vervroegd in jaren met natte voorjaren.',
    neighbourhoods: [
      'Centrum',
      'Scheveningen',
      'Bezuidenhout',
      'Statenkwartier',
      'Archipelbuurt',
      'Loosduinen',
      'Moerwijk',
      'Ypenburg',
    ],
    priceTier: 'hoog',
    priceContext:
      'In Den Haag liggen voorrijkosten op €75–110 en het uurtarief 15–25% boven het landelijke gemiddelde, met een opslag voor monumentenwerk in het centrum en Statenkwartier.',
    lateralCitySlugs: ['amsterdam', 'rotterdam', 'utrecht', 'eindhoven'],
  },
  utrecht: {
    slug: 'utrecht',
    name: 'Utrecht',
    province: 'Utrecht',
    population: 378000,
    intro:
      'De Utrechtse binnenstad telt zo’n 1.500 rijksmonumenten, vooral langs de Oudegracht en in Wijk C; daaromheen ligt een ring van 19e-eeuwse woonwijken (Wittevrouwen, Lombok, Vogelenbuurt) en grote naoorlogse buurten als Kanaleneiland en Overvecht. Sinds 2015 groeit Utrecht harder dan elke andere G4-stad — alleen Leidsche Rijn en Vleuten-De Meern voegen jaarlijks duizenden nieuwbouwwoningen toe. Voor vakmensen betekent dat een gemengde markt: monumentenwerk in het centrum, hoge tenant-turnover rond De Uithof en het NS-station, en grootschalig nieuwbouwwerk in het westen. Veel werk loopt via VvE’s en de woningcorporaties Mitros en Bo-Ex. Tarieven liggen 10–15% boven het landelijke gemiddelde; in Leidsche Rijn wordt veel onderhoud via aannemerscontracten gefactureerd.',
    neighbourhoods: [
      'Binnenstad',
      'Oost',
      'Lombok',
      'Wittevrouwen',
      'Kanaleneiland',
      'Overvecht',
      'Leidsche Rijn',
      'Vleuten-De Meern',
    ],
    priceTier: 'gemiddeld-hoog',
    priceContext:
      'In Utrecht liggen voorrijkosten op €65–95 en het uurtarief 10–15% boven het landelijke gemiddelde; in Leidsche Rijn worden veel werkzaamheden via aannemerscontracten gefactureerd.',
    lateralCitySlugs: ['amsterdam', 'rotterdam', 'den-haag', 'eindhoven'],
  },
  eindhoven: {
    slug: 'eindhoven',
    name: 'Eindhoven',
    province: 'Noord-Brabant',
    population: 249900,
    intro:
      'Eindhoven groeit harder dan welke andere stad buiten de Randstad ook, gedreven door het ASML-ecosysteem, de High Tech Campus en de Brainport-regio met Brainport Industries Campus aan de westflank. De woningvoorraad is uitzonderlijk gemengd: vooroorlogse arbeiderswoningen in het Philipsdorp en Drents Dorp, grote naoorlogse rijwoningen in Woensel en Achtse Barrier, omgebouwde fabriekspanden tot lofts in Strijp-S en Strijp-T, en grootschalige nieuwbouw in Meerhoven en Acht. Voor vakmensen betekent dat een breed werkpalet: monumentaal pannenwerk, vlakke bitumendaken op naoorlogse rijwoningen, industriële afbouwklussen in voormalige Philips-panden en bedrijfsmatig onderhoud rond de High Tech Campus. Veel werk loopt via de corporatie Woonbedrijf onder meerjarige raamovereenkomsten. De hoge expat-instroom zorgt voor tenant-turnover die reactief werk — lekkende kranen, defecte boilers, schilderbeurten bij oplevering — domineert. Tarieven liggen rond het landelijke gemiddelde, met opslag voor industriële opdrachten en bedrijfspanden.',
    neighbourhoods: [
      'Centrum',
      'Strijp',
      'Woensel',
      'Tongelre',
      'Stratum',
      'Gestel',
      'Meerhoven',
      'Philipsdorp',
    ],
    priceTier: 'gemiddeld',
    priceContext:
      'In Eindhoven liggen voorrijkosten op €55–85 en het uurtarief rond het landelijke gemiddelde; industriële opdrachten op de High Tech Campus en Brainport Industries Campus vragen om aparte calculaties met certificeringseisen.',
    lateralCitySlugs: ['den-haag', 'rotterdam', 'utrecht'],
  },
  haarlem: {
    slug: 'haarlem',
    name: 'Haarlem',
    province: 'Noord-Holland',
    population: 169000,
    intro:
      'Haarlem heeft een uitzonderlijk oude woningvoorraad: de Vijfhoek en de grachten langs het Spaarne tellen honderden 17e- en 18e-eeuwse panden met houten kozijnen, gemetselde topgevels en historische lood- en koperleidingen. Daaromheen liggen 19e-eeuwse uitbreidingen in de Bomenbuurt en Leidsebuurt, en grote naoorlogse blokken in Schalkwijk en de Slachthuisbuurt. De stad fungeert als welvarende commuter-stad voor Amsterdam, met hoge bereidheid tot kwalitatief schilder- en aannemerswerk. Voor vakmensen betekent dat: monumentenwerk onder strikt welstandstoezicht, krappe leidingschachten in oude panden langs het Spaarne, collectieve standleidingen in Schalkwijkse galerijflats die nu aan vervanging toe zijn, en een actieve VvE-markt. Veel werk loopt via de woningcorporaties Ymere, Pré Wonen en Elan Wonen. Tarieven liggen iets boven het landelijke gemiddelde door nabijheid van Amsterdam, parkeerdruk in de Vijfhoek en de gemiddeld hoger gewaardeerde woningvoorraad.',
    neighbourhoods: [
      'Centrum',
      'Vijfhoek',
      'Spaarndamse- en Zaanenbuurt',
      'Bomenbuurt',
      'Leidsebuurt',
      'Schalkwijk',
      'Slachthuisbuurt',
      'Haarlem-Noord',
    ],
    priceTier: 'gemiddeld-hoog',
    priceContext:
      'In Haarlem liggen voorrijkosten op €70–100 en het uurtarief 5–15% boven het landelijke gemiddelde door nabijheid van Amsterdam, parkeerdruk in de Vijfhoek en een opslag voor monumentenwerk langs het Spaarne.',
    lateralCitySlugs: ['amsterdam', 'utrecht', 'den-haag'],
  },
}
