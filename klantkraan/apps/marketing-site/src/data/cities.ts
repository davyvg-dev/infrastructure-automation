// City data for the programmatic /[stad]/[vak] route.
// Per blueprint (research/programmatic-seo-blueprint.md §5): each city carries
// a city-unique intro paragraph (≥100 words), neighbourhood list, price tier
// descriptor and lateral-link list. Niche-specific framing lives in wave1.ts.

export type CitySlug = 'amsterdam' | 'rotterdam' | 'den-haag' | 'utrecht'

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
    lateralCitySlugs: ['rotterdam', 'den-haag', 'utrecht'],
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
    lateralCitySlugs: ['amsterdam', 'rotterdam', 'utrecht'],
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
    lateralCitySlugs: ['amsterdam', 'rotterdam', 'den-haag'],
  },
}
