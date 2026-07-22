// Branches (niches) shared between Header, Footer and the /voor-wie hub.
// Single source of truth — order here drives nav order, footer order and
// hub-page card order.

export interface Branch {
  /** URL slug (no leading slash). Used to derive href. */
  slug: string
  /** Singular label, used in body copy ("een loodgieter"). */
  labelSingular: string
  /** Plural label, used in nav + hub cards ("Loodgieters"). */
  labelPlural: string
  /** English plural label, used in the /en nav + footer + /en/voor-wie hub. */
  labelPluralEn: string
  /** Cornerstone path. */
  href: string
  /** 1-line description used on the /voor-wie hub cards (max ~90 chars). */
  hubLine: string
  /** English hub-card line, used on /en/voor-wie. */
  hubLineEn: string
  /** Optional path under src/components/illustrations to render on hub card. */
  illustration:
    | 'TapValve'
    | 'StormCloud'
    | 'PaintRoller'
    | 'HardHat'
    | 'RingingPhone'
    | 'Dumbbell'
    | null
}

export const branches: Branch[] = [
  {
    slug: 'sportscholen',
    labelSingular: 'Sportschool',
    labelPlural: 'Sportscholen',
    labelPluralEn: 'Gyms',
    href: '/sportscholen/',
    hubLine: 'Proefles-aanvragen in de avond en het weekend direct beantwoord én ingepland.',
    hubLineEn: 'Trial-class requests in the evening and at weekends answered and booked on the spot.',
    illustration: 'Dumbbell',
  },
  {
    slug: 'loodgieters',
    labelSingular: 'Loodgieter',
    labelPlural: 'Loodgieters',
    labelPluralEn: 'Plumbers',
    href: '/loodgieters/',
    hubLine: 'Spoed-oproepen, voorrijkosten en standleiding-werk uit elkaar gehouden.',
    hubLineEn: 'Emergency calls, call-out charges and standard jobs kept apart and prioritised.',
    illustration: 'TapValve',
  },
  {
    slug: 'dakdekkers',
    labelSingular: 'Dakdekker',
    labelPlural: 'Dakdekkers',
    labelPluralEn: 'Roofers',
    href: '/dakdekkers/',
    hubLine: 'Storm-protocol dat lekkages direct naar uw mobiel escaleert.',
    hubLineEn: 'A storm protocol that escalates leaks straight to your phone.',
    illustration: 'StormCloud',
  },
  {
    slug: 'schilder',
    labelSingular: 'Schilder',
    labelPlural: 'Schilders',
    labelPluralEn: 'Painters',
    href: '/schilder/',
    hubLine: 'Offerteaanvragen, planning-vragen en leveranciers gescheiden in één agenda.',
    hubLineEn: 'Quote requests, scheduling questions and suppliers kept separate in one calendar.',
    illustration: 'PaintRoller',
  },
  {
    slug: 'installateur',
    labelSingular: 'Installateur',
    labelPlural: 'Installateurs',
    labelPluralEn: 'Installers',
    href: '/installateur/',
    hubLine: 'CV-storingen, warmtepomp-aanvragen en spoedwerk naar de juiste prioriteit.',
    hubLineEn: 'Boiler faults, heat-pump enquiries and emergency work sorted to the right priority.',
    illustration: null,
  },
  {
    slug: 'elektricien',
    labelSingular: 'Elektricien',
    labelPlural: 'Elektriciens',
    labelPluralEn: 'Electricians',
    href: '/elektricien/',
    hubLine: 'Spoedklachten, projectofferte-aanvragen en VvE-werk gescheiden afgehandeld.',
    hubLineEn: 'Emergency call-outs, project quotes and property-management work handled separately.',
    illustration: null,
  },
  {
    slug: 'aannemer',
    labelSingular: 'Aannemer',
    labelPlural: 'Aannemers',
    labelPluralEn: 'Contractors',
    href: '/aannemer/',
    hubLine: 'Offerteaanvragen, meerwerk en leveranciers uit elkaar terwijl u op de bouwplaats staat.',
    hubLineEn: 'Quote requests, variations and suppliers kept apart while you are on site.',
    illustration: 'HardHat',
  },
]
