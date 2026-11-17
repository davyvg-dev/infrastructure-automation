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
  /** Spanish plural label, used in the /es nav + footer + /es/voor-wie hub. */
  labelPluralEs: string
  /** Cornerstone path. */
  href: string
  /** 1-line description used on the /voor-wie hub cards (max ~90 chars). */
  hubLine: string
  /** English hub-card line, used on /en/voor-wie. */
  hubLineEn: string
  /** Spanish hub-card line, used on /es/voor-wie. */
  hubLineEs: string
  /** Optional path under src/components/illustrations to render on hub card. */
  illustration:
    | 'TapValve'
    | 'StormCloud'
    | 'PaintRoller'
    | 'HardHat'
    | 'RingingPhone'
    | 'Dumbbell'
    | 'Plug'
    | 'Radiator'
    | null
}

// Order: trades A-Z first, non-trade niches (sportscholen) last.
export const branches: Branch[] = [
  {
    slug: 'aannemer',
    labelSingular: 'Aannemer',
    labelPlural: 'Aannemers',
    labelPluralEn: 'Contractors',
    labelPluralEs: 'Contratistas',
    href: '/aannemer/',
    hubLine:
      'Houdt offerteaanvragen, meerwerk en leveranciers uit elkaar terwijl u op de bouwplaats staat.',
    hubLineEn: 'Quote requests, variations and suppliers kept apart while you are on site.',
    hubLineEs:
      'Presupuestos, trabajos adicionales y proveedores, separados mientras usted está en obra.',
    illustration: 'HardHat',
  },
  {
    slug: 'dakdekkers',
    labelSingular: 'Dakdekker',
    labelPlural: 'Dakdekkers',
    labelPluralEn: 'Roofers',
    labelPluralEs: 'Tejadores',
    href: '/dakdekkers/',
    hubLine: 'Een stormprotocol dat spoedlekkages direct op uw mobiel meldt.',
    hubLineEn: 'A storm protocol that sends leaks straight to your phone.',
    hubLineEs: 'Un protocolo de tormentas que le avisa de las goteras directamente al móvil.',
    illustration: 'StormCloud',
  },
  {
    slug: 'elektricien',
    labelSingular: 'Elektricien',
    labelPlural: 'Elektriciens',
    labelPluralEn: 'Electricians',
    labelPluralEs: 'Electricistas',
    href: '/elektricien/',
    hubLine: 'Houdt spoed, offerteaanvragen voor projecten en VvE-werk uit elkaar.',
    hubLineEn:
      'Emergency call-outs, project quotes and property-management work handled separately.',
    hubLineEs:
      'Urgencias, presupuestos de obra y trabajos para comunidades, gestionados por separado.',
    illustration: 'Plug',
  },
  {
    slug: 'installateur',
    labelSingular: 'Installateur',
    labelPlural: 'Installateurs',
    labelPluralEn: 'Heating engineers',
    labelPluralEs: 'Instaladores',
    href: '/installateur/',
    hubLine: 'Zet cv-storingen, vragen over warmtepompen en spoedwerk op volgorde van urgentie.',
    hubLineEn: 'Boiler faults, heat-pump enquiries and emergency work given the right priority.',
    hubLineEs:
      'Averías de calderas, consultas de bombas de calor y urgencias, ordenadas por prioridad.',
    illustration: 'Radiator',
  },
  {
    slug: 'loodgieters',
    labelSingular: 'Loodgieter',
    labelPlural: 'Loodgieters',
    labelPluralEn: 'Plumbers',
    labelPluralEs: 'Fontaneros',
    href: '/loodgieters/',
    hubLine: 'Houdt spoedvragen, vragen over voorrijkosten en werk aan standleidingen uit elkaar.',
    hubLineEn: 'Emergency calls, call-out charges and drain work kept apart and prioritised.',
    hubLineEs:
      'Urgencias, gastos de desplazamiento y trabajos de desagüe, separados y priorizados.',
    illustration: 'TapValve',
  },
  {
    slug: 'schilder',
    labelSingular: 'Schilder',
    labelPlural: 'Schilders',
    labelPluralEn: 'Painters',
    labelPluralEs: 'Pintores',
    href: '/schilder/',
    hubLine: 'Houdt offerteaanvragen, vragen over de planning en leveranciers uit elkaar.',
    hubLineEn: 'Quote requests, scheduling questions and suppliers kept separate in one calendar.',
    hubLineEs: 'Presupuestos, dudas de planificación y proveedores, separados en una sola agenda.',
    illustration: 'PaintRoller',
  },
  {
    slug: 'sportscholen',
    labelSingular: 'Sportschool',
    labelPlural: 'Sportscholen',
    labelPluralEn: 'Gyms',
    labelPluralEs: 'Gimnasios',
    href: '/sportscholen/',
    hubLine: 'Beantwoordt proeflesaanvragen in de avond en het weekend en plant ze direct in.',
    hubLineEn:
      'Trial-class requests in the evening and at weekends answered and booked on the spot.',
    hubLineEs:
      'Solicitudes de clase de prueba por la tarde y el fin de semana, respondidas y agendadas al momento.',
    illustration: 'Dumbbell',
  },
]
