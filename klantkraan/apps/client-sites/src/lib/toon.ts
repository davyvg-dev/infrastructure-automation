/**
 * The sentences that change when the business does not travel to the customer.
 *
 * The template was built for trades: the copy says "wij komen langs", the hero promises
 * "in <plaats> en omgeving", and every werkgebied plaats gets a page about going there.
 * All of that is true for a dakdekker and false for a kapper, a tandarts or a restaurant,
 * who have one address and want the customer to come to THEM. `bedrijf.bedrijfstype`
 * picks the register; `mobiel` is the default and reproduces the old copy exactly, so an
 * existing client.yaml renders the same bytes it did before this file existed.
 *
 * Why one module instead of a ternary in each component: these are eight sentences of
 * Dutch that the founder reads as copy, not as code. Spread across Hero, Intro,
 * Werkgebied, the city page, the final CTA and two <title>s they cannot be reviewed as a
 * voice at all, and the register drifts one component at a time. Here the two columns sit
 * next to each other and a mismatch is visible.
 *
 * The rules the copy inherits: u-register, no prices anywhere, no numeric claims, and
 * nothing that promises what the business has not said it does.
 */
import type { ClientConfig } from './client.ts'
import { capitalize, somOp } from './format.ts'

export interface Toon {
  /**
   * The H1. Lived in Hero.astro as `<naam>: vakwerk waar u op kunt rekenen.` until
   * 2026-08-16, which made the largest text on the first screen the same sentence for a
   * barber and a dakdekker, and was also wrong about the market: nearly every real Dutch
   * trade site puts vak + plaats in the H1 ("Timmerman in Waalwijk en omgeving"). This
   * factory had that in a tracked uppercase eyebrow ABOVE the H1 -- the badge-above-the-
   * headline pattern, which is the single most-scored tell in the taxonomy. So the eyebrow
   * is gone from the hero and its content is the headline, which is one fewer element and
   * two fewer tells.
   */
  kop: string
  /** Hero subline. */
  belofte: string
  /** Intro heading. Hardcoded in Intro.astro until 2026-08-16. */
  introKop: string
  /** Intro, first paragraph: how working with them goes. */
  werkwijze: string
  /** Intro, second paragraph: where they are, or where they go. */
  bereik: string
  /** Werkgebied section heading and body. */
  gebiedKop: string
  gebiedTekst: string
  /**
   * Nav label for the same section. Separate from gebiedKop because the header is a row
   * of three short words and "Waar u ons vindt" wraps it.
   */
  gebiedNav: string
  /** Final CTA heading and body. */
  slotKop: string
  slotTekst: string
  /** The line under "Onze diensten", on the homepage and on the diensten page. */
  dienstenTekst: string
  dienstenPaginaTekst: string
  /** Contact page <meta description>, for a client with no e-mail address. */
  contactOmschrijving: string
  /** Homepage <title> and <meta description>. */
  titel: string
  omschrijving: string
  /** City page: H1, body, <title>, <meta description>, and the footnote to the others. */
  plaatsKop: (plaats: string) => string
  plaatsTekst: (plaats: string) => string
  plaatsTitel: (plaats: string) => string
  plaatsOmschrijving: (plaats: string) => string
  plaatsAndere: (plaats: string, andere: string[]) => string
  /**
   * schema.org type for each areaServed entry. A mobiel bedrijf serves towns; a locatie
   * bedrijf's werkgebied is the neighbourhoods its customers travel from, which are not
   * Cities and should not claim to be.
   */
  gebiedType: 'City' | 'Place'
}

export function toon(config: ClientConfig): Toon {
  const basis = standaardToon(config)
  // Per-client copy from client.yaml, written by app.sitedraft off the prospect's own
  // sources or by hand. It merges OVER the register default rather than replacing the
  // block, so a client who has one good sentence gets that one sentence and keeps the rest
  // -- and a client with none renders exactly the bytes they rendered before `teksten`
  // existed, which is what keeps the live fleet still.
  const eigen = config.teksten ?? {}
  return {
    ...basis,
    ...(eigen.kop ? { kop: eigen.kop } : {}),
    ...(eigen.belofte ? { belofte: eigen.belofte } : {}),
    ...(eigen.intro_kop ? { introKop: eigen.intro_kop } : {}),
    ...(eigen.werkwijze ? { werkwijze: eigen.werkwijze } : {}),
    ...(eigen.bereik ? { bereik: eigen.bereik } : {}),
    ...(eigen.diensten_tekst ? { dienstenTekst: eigen.diensten_tekst } : {}),
    ...(eigen.slot_kop ? { slotKop: eigen.slot_kop } : {}),
    ...(eigen.slot_tekst ? { slotTekst: eigen.slot_tekst } : {}),
  }
}

function standaardToon(config: ClientConfig): Toon {
  const { bedrijf } = config
  const vak = capitalize(bedrijf.vak)
  const naam = bedrijf.naam
  const plaats = bedrijf.adres.plaats
  const gebied = somOp(bedrijf.werkgebied)

  if (bedrijf.bedrijfstype === 'locatie') {
    return {
      // No "en omgeving": a shop is in one place, and claiming a radius it does not
      // travel is the first sentence that would give the template away.
      kop: `${vak} in ${plaats}`,
      // "Wij komen langs" inverted. Deliberately not "u loopt binnen" alone -- plenty of
      // locatie vakken (tandarts, hondentrimmer) run on appointment only, and the copy
      // has to be true for all of them.
      //
      // The `Van <d1> en <d2> tot <d3>:` prefix this line carried until 2026-08-16 is gone.
      // It was a hardcoded rule of three -- the copy tell every detector regexes for -- and
      // it broke into nonsense the moment a dienst name contained "en": "Van lekkage
      // opsporen en verhelpen en ontstoppen tot sanitair vervangen". The diensten it was
      // naming are three sections further down the same page anyway.
      belofte: `U belt voor een afspraak en u weet vooraf waar u aan toe bent.`,
      introKop: 'Duidelijke afspraken, nette afwerking',
      werkwijze: `Een ${bedrijf.vak} zoeken en geen zin in gedoe? Zo werken wij: u belt of loopt binnen, u vertelt wat u zoekt, en wij zeggen eerlijk wat er mogelijk is en wanneer u terechtkunt.`,
      bereik: `${naam} zit in ${plaats}. Onze klanten komen uit ${gebied}. U spreekt altijd iemand die het vak zelf doet.`,
      gebiedKop: 'Waar u ons vindt',
      gebiedNav: 'Bezoek ons',
      gebiedTekst: `${naam} zit in ${plaats}. Onze klanten komen onder meer uit ${gebied}. Kom gerust langs of bel even, dan zetten wij u in de agenda.`,
      slotKop: 'Maak een afspraak',
      slotTekst:
        'Bel ons even en zeg wat u zoekt. U hoort direct wanneer u terechtkunt, zonder omwegen.',
      // "Klus" is a trade's word for a job. A barber does not do klussen, and the word is
      // the kind of small wrongness a reader feels without being able to name it.
      dienstenTekst:
        'Dit is waar u ons voor belt. Zoekt u iets anders? Vraag het gerust, wij denken met u mee.',
      dienstenPaginaTekst: `Hieronder ziet u waar ${naam} u mee helpt. Staat wat u zoekt er niet bij? Bel ons gerust, dan hoort u direct of wij u kunnen helpen.`,
      contactOmschrijving: `Neem contact op met ${naam} in ${plaats}. Bel ${bedrijf.telefoon} om een afspraak te maken.`,
      titel: `${naam} | ${vak} in ${plaats}`,
      omschrijving: `${naam} is uw ${bedrijf.vak} in ${plaats}. Bel ${bedrijf.telefoon} om een afspraak te maken.`,
      // "Voor", never "in": the shop is not in that neighbourhood, the customer is.
      plaatsKop: (p) => `${vak} voor ${p}`,
      plaatsTekst: (p) =>
        `Zoekt u een ${bedrijf.vak} voor ${p}? ${naam} zit in ${plaats} en u bent er zo. Bel even, dan staat er tijd voor u klaar.`,
      plaatsTitel: (p) => `${vak} voor ${p} | ${naam}`,
      plaatsOmschrijving: (p) =>
        `${naam} is de ${bedrijf.vak} voor ${p}, gevestigd in ${plaats}. Bel ${bedrijf.telefoon} om een afspraak te maken.`,
      plaatsAndere: (p, andere) => `Naast ${p} komen onze klanten uit ${somOp(andere)}.`,
      gebiedType: 'Place',
    }
  }

  // mobiel: the copy every client site had before this file existed. Changing a sentence
  // here changes every live trade site, so it is kept verbatim on purpose.
  return {
    kop: `${vak} in ${plaats} en omgeving`,
    // Tricolon prefix dropped 2026-08-16, see the locatie branch for why. The promise
    // itself is untouched: it is live on paying clients and pinned by toon.test.ts.
    belofte: `U belt, wij komen langs en u weet vooraf waar u aan toe bent.`,
    introKop: 'Duidelijke afspraken, nette afwerking',
    werkwijze: `Een ${bedrijf.vak} nodig en geen zin in gedoe? Zo werken wij: u legt uw situatie uit, wij komen kijken en u ontvangt een heldere offerte voordat het werk begint. Geen verrassingen achteraf.`,
    bereik: `${naam} werkt in ${gebied}. U spreekt altijd met iemand die het werk zelf kent, en wij laten de werkplek netjes achter.`,
    gebiedKop: 'Werkgebied',
    gebiedNav: 'Werkgebied',
    gebiedTekst: `${naam} werkt in ${gebied}. Woont u net daarbuiten? Bel gerust, vaak kunnen wij toch iets voor u betekenen.`,
    slotKop: 'Vertel ons wat er speelt',
    slotTekst:
      'Bel ons en leg uw situatie voor. U krijgt direct een eerlijk antwoord en een duidelijke afspraak.',
    dienstenTekst:
      'Dit is waar u ons voor belt. Staat uw klus er niet bij? Vraag het gerust, wij denken met u mee.',
    dienstenPaginaTekst: `Hieronder ziet u waar ${naam} u mee helpt. Twijfelt u of uw klus erbij staat? Bel ons gerust, dan hoort u direct of wij u kunnen helpen.`,
    contactOmschrijving: `Neem contact op met ${naam} in ${plaats}. Bel ${bedrijf.telefoon} voor een afspraak of een vrijblijvende offerte.`,
    titel: `${naam} | ${vak} in ${plaats} en omgeving`,
    omschrijving: `${naam} is uw ${bedrijf.vak} in ${gebied}. Bel ${bedrijf.telefoon} voor een afspraak of een vrijblijvende offerte.`,
    plaatsKop: (p) => `${vak} in ${p}`,
    plaatsTekst: (p) =>
      `Zoekt u een ${bedrijf.vak} in ${p}? ${naam} komt bij u langs, bekijkt de situatie en doet u een heldere offerte voordat het werk begint.` +
      (plaats === p
        ? ` Ons bedrijf zit in ${p}, dus wij zijn snel bij u.`
        : ` Vanuit ${plaats} zijn wij snel in ${p}.`),
    plaatsTitel: (p) => `${vak} in ${p} | ${naam}`,
    plaatsOmschrijving: (p) =>
      `${naam} is uw ${bedrijf.vak} in ${p}. Bel ${bedrijf.telefoon} voor een afspraak of een vrijblijvende offerte.`,
    plaatsAndere: (p, andere) => `Naast ${p} werken wij ook in ${somOp(andere)}.`,
    gebiedType: 'City',
  }
}
