// Niche definitions for the programmatic /[stad]/[vak] route.
// Mirrors the tone, painStats and FAQ pattern of each cornerstone page so
// programmatic pages feel like a coherent sibling, not a thin clone.
// Per-city differentiation lives in cities.ts + wave1.ts.

export type NicheSlug = 'loodgieter' | 'dakdekker' | 'schilder' | 'aannemer'

export interface Feature {
  icon: 'phone' | 'message-square' | 'calendar-check'
  title: string
  body: string
}

export interface Faq {
  q: string
  a: string
  href?: string
  linkLabel?: string
}

export interface PainStat {
  value: string
  caption: string
}

export interface Niche {
  slug: NicheSlug
  // Singular noun used in URL + meta + H1 ("Loodgieter")
  label: string
  // Plural used in copy ("loodgieters")
  labelPlural: string
  // Path to existing cornerstone (with trailing slash; trailingSlash: 'always')
  cornerstonePath: string
  // schema.org type for LocalBusiness wrapper on the trade being described
  schemaType: 'Plumber' | 'RoofingContractor' | 'HousePainter' | 'GeneralContractor'
  // Average job value (€) used for ROI snippet on the page
  jobValueEur: number
  features: Feature[]
  baseFaqs: Faq[]
  painStats: PainStat[]
}

const sharedFeatures = (kind: NicheSlug): Feature[] => {
  // The three core modules are identical product-wise but the framing changes
  // per niche so the page reads as written for that trade.
  const leadLine = {
    loodgieter:
      'Elke aanvraag en elk terugbelverzoek komt direct als bericht op uw telefoon binnen, met naam, nummer en de vraag van de klant. Geen klant blijft hangen in uw voicemail.',
    dakdekker:
      'Meldt iemand een lekkage terwijl u op een dak staat, dan staat de melding direct als bericht op uw telefoon, met naam, nummer en adres. Geen lekkagemelding raakt zoek.',
    schilder:
      'Vraagt een particulier na werktijd een offerte aan, dan staat de aanvraag direct als bericht op uw telefoon. Geen aanvraag raakt zoek terwijl u op de stelling staat.',
    aannemer:
      'Meldt een opdrachtgever zich terwijl u aan het inmeten bent, dan staat de aanvraag direct als bericht op uw telefoon. Geen opdrachtgever blijft hangen in uw voicemail.',
  }[kind]
  return [
    {
      icon: 'message-square',
      title: 'Digitale receptionist op uw site en WhatsApp',
      body: {
        loodgieter:
          "Beantwoordt klantvragen in vlot Nederlands, ook 's avonds en in het weekend. Kent uw voorrijkosten, spoedtoeslag en materiaalopslag, en noemt alleen tarieven die u zelf heeft ingesteld.",
        dakdekker:
          "Beantwoordt klantvragen in vlot Nederlands, ook 's avonds en in het weekend. Kent uw inspectietarief, spoedtoeslag bij lekkage en regiotoeslag, en noemt alleen tarieven die u zelf heeft ingesteld.",
        schilder:
          "Beantwoordt klantvragen in vlot Nederlands, ook 's avonds en in het weekend. Kent uw voorrijkosten, m²-tarief binnen en buiten, meerprijs voor een kleurproef en toeslag voor spuitwerk, en noemt alleen tarieven die u zelf heeft ingesteld.",
        aannemer:
          "Beantwoordt klantvragen in vlot Nederlands, ook 's avonds en in het weekend. Kent uw uurtarief, uw regio en het verschil tussen een advies-, inmeet- en regiebezoek, en noemt alleen tarieven die u zelf heeft ingesteld.",
      }[kind],
    },
    {
      icon: 'calendar-check',
      title: 'Afspraken direct in uw agenda',
      body: {
        loodgieter:
          'De receptionist plant terugbel- en klusafspraken rechtstreeks in uw agenda, alleen op momenten die u zelf heeft vrijgegeven. U belt en mailt niet meer heen en weer.',
        dakdekker:
          'De receptionist plant inspectie- en offerteafspraken rechtstreeks in uw agenda, alleen op momenten die u zelf heeft vrijgegeven. U ziet elke ochtend wat er op de planning staat.',
        schilder:
          'De receptionist plant opname- en offerteafspraken rechtstreeks in uw agenda, alleen op momenten die u zelf heeft vrijgegeven. U belt en mailt niet meer heen en weer.',
        aannemer:
          'De receptionist plant advies- en inmeetafspraken rechtstreeks in uw agenda, alleen op momenten die u zelf heeft vrijgegeven. U ziet elke ochtend wat er op de planning staat.',
      }[kind],
    },
    {
      icon: 'phone',
      title: 'Aanvragen en terugbelverzoeken op uw telefoon',
      body: leadLine,
    },
  ]
}

const baseFaqs: Faq[] = [
  {
    q: 'Hoe komt de receptionist op mijn website?',
    a: 'Wij plaatsen één klein script op uw website en koppelen uw WhatsApp. U hoeft zelf niets te doen. U houdt uw eigen site, nummer en huisstijl.',
  },
  {
    q: 'Weet de klant dat het AI is?',
    a: 'Ja. Elk gesprek begint met de melding dat de klant met een digitale assistent van uw bedrijf chat. Dat is wettelijk verplicht (artikel 50 van de Europese AI-verordening), dus die melding staat altijd aan.',
    href: '/legal/ai-disclosure/',
    linkLabel: 'Lees de volledige AI-disclosure',
  },
  {
    q: 'Wat als de AI iets verkeerd zegt over mijn prijzen?',
    a: 'Dat kan niet gebeuren. De assistent noemt alleen tarieven die u zelf heeft ingesteld. Kent hij een prijs niet, dan verzint hij niets en krijgt de klant een terugbelafspraak. Wij testen elke instelling voordat u live gaat.',
  },
  {
    q: 'Is het echt per maand opzegbaar?',
    a: 'Ja. U zegt op met één mail, wanneer u wilt. Er is geen jaarcontract en geen verborgen verlenging. De receptionist werkt tot het einde van de betaalde maand; daarna incasseren wij niets meer. Betaalt u liever 6 of 12 maanden vooruit, dan krijgt u 15% of 20% korting.',
    href: '/legal/voorwaarden/',
    linkLabel: 'Lees de algemene voorwaarden',
  },
]

export const niches: Record<NicheSlug, Niche> = {
  loodgieter: {
    slug: 'loodgieter',
    label: 'Loodgieter',
    labelPlural: 'loodgieters',
    cornerstonePath: '/loodgieters/',
    schemaType: 'Plumber',
    jobValueEur: 450,
    features: sharedFeatures('loodgieter'),
    baseFaqs,
    painStats: [
      { value: '28%', caption: 'van uw oproepen wordt gemist tijdens spoed- en avonddiensten.' },
      { value: '€\u00a0450', caption: 'gemiddelde waarde van een gemiste loodgietersklus.' },
      { value: '0', caption: 'reviews van een klus die u misloopt.' },
    ],
  },
  dakdekker: {
    slug: 'dakdekker',
    label: 'Dakdekker',
    labelPlural: 'dakdekkers',
    cornerstonePath: '/dakdekkers/',
    schemaType: 'RoofingContractor',
    jobValueEur: 600,
    features: sharedFeatures('dakdekker'),
    baseFaqs,
    painStats: [
      {
        value: '32%',
        caption: 'van de spoedmeldingen komt na 17:00 binnen, na zware regen of storm.',
      },
      { value: '€\u00a0600', caption: 'gemiddelde waarde van een gemiste inspectie- of spoedklus.' },
      {
        value: '24 uur',
        caption:
          'is de gewenste reactietijd bij stormschade. Met alleen uw eigen telefoon haalt u dat moeilijk.',
      },
    ],
  },
  schilder: {
    slug: 'schilder',
    label: 'Schilder',
    labelPlural: 'schilders',
    cornerstonePath: '/schilder/',
    schemaType: 'HousePainter',
    jobValueEur: 2500,
    features: sharedFeatures('schilder'),
    baseFaqs,
    painStats: [
      { value: '37%', caption: 'van uw offerteaanvragen komt binnen na 17:00 uur.' },
      { value: '€\u00a02.500', caption: 'gemiddelde waarde van een binnenschilderklus in een woning.' },
      { value: '3×', caption: 'meer aanvragen van maart tot en met mei.' },
    ],
  },
  aannemer: {
    slug: 'aannemer',
    label: 'Aannemer',
    labelPlural: 'aannemers',
    cornerstonePath: '/aannemer/',
    schemaType: 'GeneralContractor',
    jobValueEur: 5000,
    features: sharedFeatures('aannemer'),
    baseFaqs,
    painStats: [
      {
        value: '41%',
        caption: 'van de offerteaanvragen verdwijnt als u niet binnen 24 uur reageert.',
      },
      { value: '€\u00a05.000', caption: 'gemiddelde waarde van een gemiste verbouwing of dakkapel.' },
      {
        value: '1 op 3',
        caption: 'aanvragen wordt klant als u dezelfde dag een afspraak inplant.',
      },
    ],
  },
}
