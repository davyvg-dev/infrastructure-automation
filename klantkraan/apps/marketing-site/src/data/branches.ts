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
  /** Cornerstone path. */
  href: string
  /** 1-line description used on the /voor-wie hub cards (max ~90 chars). */
  hubLine: string
  /** Optional path under src/components/illustrations to render on hub card. */
  illustration:
    | 'TapValve'
    | 'StormCloud'
    | 'PaintRoller'
    | 'HardHat'
    | 'RingingPhone'
    | null
}

export const branches: Branch[] = [
  {
    slug: 'loodgieters',
    labelSingular: 'Loodgieter',
    labelPlural: 'Loodgieters',
    href: '/loodgieters',
    hubLine: 'Spoed-oproepen, voorrijkosten en standleiding-werk uit elkaar gehouden.',
    illustration: 'TapValve',
  },
  {
    slug: 'dakdekkers',
    labelSingular: 'Dakdekker',
    labelPlural: 'Dakdekkers',
    href: '/dakdekkers',
    hubLine: 'Storm-protocol dat lekkages direct naar uw mobiel escaleert.',
    illustration: 'StormCloud',
  },
  {
    slug: 'schilder',
    labelSingular: 'Schilder',
    labelPlural: 'Schilders',
    href: '/schilder',
    hubLine: 'Offerteaanvragen, planning-vragen en leveranciers gescheiden in één agenda.',
    illustration: 'PaintRoller',
  },
  {
    slug: 'installateur',
    labelSingular: 'Installateur',
    labelPlural: 'Installateurs',
    href: '/installateur',
    hubLine: 'CV-storingen, warmtepomp-aanvragen en spoedwerk naar de juiste prioriteit.',
    illustration: null,
  },
  {
    slug: 'elektricien',
    labelSingular: 'Elektricien',
    labelPlural: 'Elektriciens',
    href: '/elektricien',
    hubLine: 'Spoedklachten, projectofferte-aanvragen en VvE-werk gescheiden afgehandeld.',
    illustration: null,
  },
  {
    slug: 'aannemer',
    labelSingular: 'Aannemer',
    labelPlural: 'Aannemers',
    href: '/aannemer',
    hubLine: 'Offerteaanvragen, meerwerk en leveranciers uit elkaar terwijl u op de bouwplaats staat.',
    illustration: 'HardHat',
  },
]
