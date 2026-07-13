// Niche definitions for the programmatic /[stad]/[vak] route.
// Mirrors the tone, painStats and FAQ pattern of each cornerstone page so
// programmatic pages feel like a coherent sibling, not a thin clone.
// Per-city differentiation lives in cities.ts + wave1.ts.

export type NicheSlug = 'loodgieter' | 'dakdekker' | 'schilder' | 'aannemer'

export interface Feature {
  icon: 'phone-call' | 'message-square' | 'star'
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
  // Path to existing cornerstone (no trailing slash; Astro adds it)
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
  const reviewLine = {
    loodgieter:
      'De volgende ochtend om 10:00 stuurt het systeem een korte review-uitnodiging aan uw klant. Soft follow-up per e-mail op dag 7. Geen handmatig werk.',
    dakdekker:
      'Na de dakinspectie of oplevering stuurt het systeem automatisch een korte review-uitnodiging. Soft follow-up op dag 7. Uw lokale ranking voor "dakdekker + plaats" stijgt zonder dat u erover hoeft na te denken.',
    schilder:
      'Op de dag na oplevering stuurt het systeem een korte review-uitnodiging aan uw klant. Soft follow-up per e-mail op dag 7. Geen handmatig werk — uw lokale ranking voor "schilder + plaats" stijgt vanzelf.',
    aannemer:
      'Na elke oplevering stuurt het systeem automatisch een korte review-uitnodiging. Soft follow-up per e-mail op dag 7. Pasende reviews per project-type — verbouwing, dakkapel, badkamer — versterken uw lokale autoriteit.',
  }[kind]
  return [
    {
      icon: 'phone-call',
      title: 'AI-receptionist die uw vak spreekt',
      body: {
        loodgieter:
          "Neemt op in vlot Nederlands, ook 's avonds en in het weekend. Kent uw voorrijkosten, spoedtoeslag en materiaalopslag — en noemt alleen tarieven die u zelf heeft ingesteld.",
        dakdekker:
          "Neemt op in vlot Nederlands, ook 's avonds en in het weekend. Kent uw inspectietarief, spoedtoeslag bij lekkage en regio-toeslag — en noemt alleen tarieven die u zelf heeft ingesteld.",
        schilder:
          "Neemt op in vlot Nederlands, ook 's avonds en in het weekend. Kent uw voorrijkosten, m²-tarief binnen en buiten, kleurproef-meerprijs en spuitwerk-toeslag — en noemt alleen tarieven die u zelf heeft ingesteld.",
        aannemer:
          "Neemt op in vlot Nederlands, ook 's avonds en in het weekend. Kent uw uurtarief, het verschil tussen advies-, inmeet- en regiebezoek, en uw regio — en noemt alleen tarieven die u zelf heeft ingesteld.",
      }[kind],
    },
    {
      icon: 'message-square',
      title: 'Missed-call SMS binnen 60 seconden',
      body: {
        loodgieter:
          'Mist u een oproep, dan krijgt de beller binnen een minuut een Nederlandstalig bericht met een directe terugbel-link via Cal.com. Geen klant raakt verloren in een voicemail.',
        dakdekker:
          'Mist u een oproep tijdens een dakinspectie of bij stormwacht, dan krijgt de beller binnen een minuut een Nederlandstalig bericht met een terugbel-link via Cal.com. Geen lekkage-melding raakt verloren.',
        schilder:
          'Belt een particulier na werktijd voor een offerte? De beller krijgt direct een Nederlandstalig bericht met een terugbel-link via Cal.com. Geen prospect raakt verloren in een voicemail terwijl u op de stelling staat.',
        aannemer:
          'Belt een opdrachtgever tijdens een inmeet-bezoek? Klantkraan stuurt binnen 60 seconden een Nederlandstalig bericht met een directe terugbel-link via Cal.com. Geen prospect raakt verloren in een voicemail.',
      }[kind],
    },
    {
      icon: 'star',
      title: 'Google-reviews na elke klus',
      body: reviewLine,
    },
  ]
}

const baseFaqs: Faq[] = [
  {
    q: 'Werkt het ook met mijn huidige telefoonnummer?',
    a: "Ja. Wij koppelen Klantkraan aan uw bestaande nummer via een doorschakeling. U houdt hetzelfde nummer op uw bus, visitekaartjes en Google-vermelding. Doorschakelen kan altijd, alleen 's avonds, of alleen bij geen gehoor — u bepaalt.",
  },
  {
    q: 'Hoort de klant dat het AI is?',
    a: 'Ja. Direct na de begroeting meldt de assistent dat het gesprek door een AI gevoerd wordt, namens uw bedrijf. Dat is geen marketing-keuze maar een wettelijke verplichting onder de Europese AI-wet (artikel 50). De disclosure blijft altijd aan staan.',
    href: '/legal/ai-disclosure',
    linkLabel: 'Lees de volledige AI-disclosure',
  },
  {
    q: 'Wat als de AI iets verkeerd zegt over mijn prijzen?',
    a: 'Dat kan niet gebeuren. De assistent noemt alleen tarieven die u zelf in uw systeem heeft gezet. Onbekende prijzen worden niet verzonnen; de klant krijgt dan een terugbel-afspraak. Wij testen elke configuratie voor u live gaat.',
  },
  {
    q: 'Per maand opzegbaar — echt waar?',
    a: 'Ja. Geen jaarcontract, geen verborgen verlenging. U zegt op via een mail; opzegtermijn is één maand. Voor wie liever 6 of 12 maanden vooruit betaalt is er korting (15% respectievelijk 20%), maar dat is een keuze, geen standaard.',
    href: '/legal/voorwaarden',
    linkLabel: 'Lees de algemene voorwaarden',
  },
]

export const niches: Record<NicheSlug, Niche> = {
  loodgieter: {
    slug: 'loodgieter',
    label: 'Loodgieter',
    labelPlural: 'loodgieters',
    cornerstonePath: '/loodgieters',
    schemaType: 'Plumber',
    jobValueEur: 450,
    features: sharedFeatures('loodgieter'),
    baseFaqs,
    painStats: [
      { value: '28%', caption: 'van uw oproepen wordt gemist tijdens spoed-en-avonddiensten.' },
      { value: '€450', caption: 'gemiddelde waarde per gemiste loodgieters-klus.' },
      { value: '0', caption: 'reviews per klus die u handmatig zou kunnen verzamelen.' },
    ],
  },
  dakdekker: {
    slug: 'dakdekker',
    label: 'Dakdekker',
    labelPlural: 'dakdekkers',
    cornerstonePath: '/dakdekkers',
    schemaType: 'RoofingContractor',
    jobValueEur: 600,
    features: sharedFeatures('dakdekker'),
    baseFaqs,
    painStats: [
      { value: '32%', caption: 'van de spoed-meldingen komt na 17:00 uur (na zware regen of storm).' },
      { value: '€600', caption: 'gemiddelde waarde per gemiste inspectie- of spoedklus.' },
      { value: '24u', caption: 'is de gewenste reactietijd bij stormschade — moeilijk waar te maken met losse telefoon.' },
    ],
  },
  schilder: {
    slug: 'schilder',
    label: 'Schilder',
    labelPlural: 'schilders',
    cornerstonePath: '/schilder',
    schemaType: 'HousePainter',
    jobValueEur: 2500,
    features: sharedFeatures('schilder'),
    baseFaqs,
    painStats: [
      { value: '37%', caption: 'van uw offerteaanvragen komt binnen na 17:00 uur.' },
      { value: '€2.500', caption: 'gemiddelde waarde per binnen-schilderklus huis.' },
      { value: '3×', caption: 'meer aanvragen in maart–mei (lente-piek).' },
    ],
  },
  aannemer: {
    slug: 'aannemer',
    label: 'Aannemer',
    labelPlural: 'aannemers',
    cornerstonePath: '/aannemer',
    schemaType: 'GeneralContractor',
    jobValueEur: 5000,
    features: sharedFeatures('aannemer'),
    baseFaqs,
    painStats: [
      { value: '41%', caption: 'van offerte-aanvragen verdwijnt als u niet binnen 24 uur reageert.' },
      { value: '€5.000', caption: 'gemiddelde waarde per gemiste verbouwings- of dakkapel-klus.' },
      { value: '1 op 3', caption: 'aanvragen wordt klant zodra u dezelfde dag een afspraak inboekt.' },
    ],
  },
}
