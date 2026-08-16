// Tests for the two copy registers (toon.ts).
//
// The bug class here is a sentence, not a crash. Every field is a string, so a locatie
// site that quietly promises "wij komen langs" builds, passes the fact gate, deploys, and
// tells a kapper's visitors the barber drives to their house. Nothing goes red; the site
// is simply lying in a way only a reader notices.
//
// So these tests do two things the type system cannot. They pin the mobiel sentences
// verbatim, because that copy is live on paying clients' sites and a refactor here must
// not reword it by accident. And they sweep the locatie register for the vocabulary of
// travelling to the customer, which is the specific mistake this file exists to prevent.

import { test } from 'node:test'
import assert from 'node:assert/strict'

import { BEDRIJFSTYPEN } from './client.ts'
import { toon, type Toon } from './toon.ts'

/** A config with only the fields toon() reads. */
function config(bedrijfstype: 'mobiel' | 'locatie', over: Record<string, unknown> = {}) {
  return {
    bedrijf: {
      naam: 'Testbedrijf',
      vak: 'kapper',
      bedrijfstype,
      telefoon: '+31 6 12 34 56 78',
      adres: { plaats: 'Rotterdam' },
      werkgebied: ['Kralingen', 'Delfshaven', 'Centrum'],
      ...over,
    },
    diensten: [
      { naam: 'Knippen', omschrijving: 'x' },
      { naam: 'Scheren', omschrijving: 'x' },
      { naam: 'Baard bijwerken', omschrijving: 'x' },
    ],
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
  } as any
}

/** Every string a register produces, including the per-plaats ones. */
function alleZinnen(t: Toon): string[] {
  const vast = [
    t.aanhef,
    t.belofte,
    t.werkwijze,
    t.bereik,
    t.gebiedKop,
    t.gebiedTekst,
    t.gebiedNav,
    t.slotKop,
    t.slotTekst,
    t.dienstenTekst,
    t.dienstenPaginaTekst,
    t.contactOmschrijving,
    t.titel,
    t.omschrijving,
  ]
  const perPlaats = ['Kralingen', 'Rotterdam'].flatMap((p) => [
    t.plaatsKop(p),
    t.plaatsTekst(p),
    t.plaatsTitel(p),
    t.plaatsOmschrijving(p),
    t.plaatsAndere(p, ['Delfshaven', 'Centrum']),
  ])
  return [...vast, ...perPlaats]
}

test('beide registers vullen elk veld', () => {
  for (const type of BEDRIJFSTYPEN) {
    for (const zin of alleZinnen(toon(config(type)))) {
      assert.ok(zin.trim().length > 0, `${type}: lege zin`)
      // A missing config field renders as the literal word, which is the other silent
      // failure: "undefined zit in Rotterdam" reads as copy until someone looks.
      assert.ok(!/undefined|NaN|\[object/.test(zin), `${type}: onopgeloste waarde in "${zin}"`)
    }
  }
})

// The whole point of the axis. These phrases are true for a dakdekker and false for a
// shop, and they are what the template said everywhere before bedrijfstype existed.
const RIJDT_NAAR_DE_KLANT = [
  /wij komen langs/i,
  /komt bij u langs/i,
  /wij komen kijken/i,
  /en omgeving/i,
  /zijn wij snel (bij u|in )/i,
  /werkgebied/i,
  /de werkplek/i,
]

test('locatie belooft nergens dat het bedrijf naar de klant komt', () => {
  for (const zin of alleZinnen(toon(config('locatie')))) {
    for (const patroon of RIJDT_NAAR_DE_KLANT) {
      assert.ok(!patroon.test(zin), `locatie zegt "${zin}" en dat matcht ${patroon}`)
    }
  }
})

// The other half of the register, and the half that is easier to miss: not a promise
// about travelling, just the wrong noun. A barber has no klus and writes no offerte, and
// those words read as slightly-off to a customer who cannot say why.
const VAKMANSTAAL = [/\bklus\b/i, /offerte/i, /oplevering/i]

test('locatie gebruikt geen woorden uit de bouw', () => {
  for (const zin of alleZinnen(toon(config('locatie')))) {
    for (const patroon of VAKMANSTAAL) {
      assert.ok(!patroon.test(zin), `locatie zegt "${zin}" en dat matcht ${patroon}`)
    }
  }
})

test('locatie zet de stad waar het bedrijf zit, niet de wijk, in de plaatskop', () => {
  const t = toon(config('locatie'))
  // "Kapper voor Kralingen", never "Kapper in Kralingen": the shop is in Rotterdam and a
  // page claiming otherwise is the doorway page the werkgebied cap exists to avoid.
  assert.equal(t.plaatsKop('Kralingen'), 'Kapper voor Kralingen')
  assert.match(t.plaatsTekst('Kralingen'), /zit in Rotterdam/)
})

test('mobiel houdt de zinnen die op live sites staan', () => {
  const t = toon(config('mobiel', { vak: 'dakdekker', naam: 'Voorbeeld Dakwerken' }))
  assert.equal(t.aanhef, 'Dakdekker in Rotterdam en omgeving')
  assert.equal(t.gebiedKop, 'Werkgebied')
  assert.equal(t.slotKop, 'Vertel ons wat er speelt')
  assert.match(t.belofte, /u belt, wij komen langs en u weet vooraf waar u aan toe bent\.$/)
  assert.match(t.werkwijze, /^Een dakdekker nodig en geen zin in gedoe\?/)
  assert.match(t.plaatsTekst('Kralingen'), /Vanuit Rotterdam zijn wij snel in Kralingen\./)
  // The client's own town gets the other half of that ternary.
  assert.match(
    t.plaatsTekst('Rotterdam'),
    /Ons bedrijf zit in Rotterdam, dus wij zijn snel bij u\./,
  )
})

test('areaServed claimt alleen City als het bedrijf er ook heen rijdt', () => {
  assert.equal(toon(config('mobiel')).gebiedType, 'City')
  assert.equal(toon(config('locatie')).gebiedType, 'Place')
})
