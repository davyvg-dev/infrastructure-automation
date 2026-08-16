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
/** `over` overrides fields on bedrijf; `top` overrides the config itself (teksten). */
function config(
  bedrijfstype: 'mobiel' | 'locatie',
  over: Record<string, unknown> = {},
  top: Record<string, unknown> = {},
) {
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
    ...top,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
  } as any
}

/** Every string a register produces, including the per-plaats ones. */
function alleZinnen(t: Toon): string[] {
  const vast = [
    t.kop,
    t.belofte,
    t.introKop,
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
  assert.equal(t.kop, 'Dakdekker in Rotterdam en omgeving')
  assert.equal(t.gebiedKop, 'Werkgebied')
  assert.equal(t.slotKop, 'Vertel ons wat er speelt')
  // The promise is word for word what live sites have said since the template shipped. Only
  // the capital moved: it used to follow the "Van <d1> en <d2> tot <d3>:" tricolon that was
  // removed on 2026-08-16, so the sentence now starts the line instead of continuing one.
  assert.equal(t.belofte, 'U belt, wij komen langs en u weet vooraf waar u aan toe bent.')
  assert.match(t.werkwijze, /^Een dakdekker nodig en geen zin in gedoe\?/)
  assert.match(t.plaatsTekst('Kralingen'), /Vanuit Rotterdam zijn wij snel in Kralingen\./)
  // The client's own town gets the other half of that ternary.
  assert.match(
    t.plaatsTekst('Rotterdam'),
    /Ons bedrijf zit in Rotterdam, dus wij zijn snel bij u\./,
  )
})

test('geen enkele register-zin is nog een drieslag', () => {
  // "Van <d1> en <d2> tot <d3>:" was a hardcoded rule of three -- the copy tell every
  // detector regexes for -- and it broke into nonsense as soon as a dienst name contained
  // "en". scripts/tell-lint.mjs catches it on the rendered page; this catches it at the
  // source, so it cannot come back in a register that has no fixture built for it.
  const drieslag = /\bvan\s+[^.:;]{3,45}\s+en\s+[^.:;]{3,45}\s+tot\s+[^.:;]{3,45}/i
  for (const type of ['mobiel', 'locatie'] as const) {
    for (const zin of alleZinnen(toon(config(type)))) {
      assert.ok(!drieslag.test(zin), `${type} zegt "${zin}" en dat is een drieslag`)
    }
  }
})

test('teksten uit client.yaml winnen van de register-zin', () => {
  const eigen = {
    kop: 'Al dertig jaar het dak van de Rivierenbuurt',
    intro_kop: 'Wij komen kijken voordat wij iets beloven',
    slot_tekst: 'Bel even, dan staan wij morgen op uw dak.',
  }
  const t = toon(config('mobiel', {}, { teksten: eigen }))
  assert.equal(t.kop, eigen.kop)
  assert.equal(t.introKop, eigen.intro_kop)
  assert.equal(t.slotTekst, eigen.slot_tekst)
  // Everything not given falls back, so one good sentence never costs the rest.
  assert.equal(t.slotKop, toon(config('mobiel')).slotKop)
  assert.equal(t.werkwijze, toon(config('mobiel')).werkwijze)
})

test('zonder teksten-blok verandert er niets aan het register', () => {
  // The live fleet has no `teksten:` and must render the bytes it rendered before the block
  // existed. An empty block is the same case and is worth pinning separately: a drafter
  // that emits `teksten: {}` for a prospect it could say nothing new about must not be a
  // different site from one that omits it.
  const kaal = toon(config('mobiel'))
  const leeg = toon(config('mobiel', {}, { teksten: {} }))
  assert.deepEqual(alleZinnen(leeg), alleZinnen(kaal))
})

test('areaServed claimt alleen City als het bedrijf er ook heen rijdt', () => {
  assert.equal(toon(config('mobiel')).gebiedType, 'City')
  assert.equal(toon(config('locatie')).gebiedType, 'Place')
})
