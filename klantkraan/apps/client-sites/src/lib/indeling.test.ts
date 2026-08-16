// Tests for section omission (`indeling.weglaten`).
//
// The bug class here is a page that builds fine and is missing something load-bearing, or a
// nav item pointing at an anchor that is no longer on the page. Neither goes red anywhere
// else: the fact gate checks that what IS rendered is correct, not that a section a visitor
// needs is still there.

import { test } from 'node:test'
import assert from 'node:assert/strict'

import {
  ClientSchema,
  ClientSchemaChecked,
  DIENSTVORMEN,
  HEROS,
  HERO_VORM,
  STANDAARD_INDELING,
  WEGLAATBAAR,
  heroToontFoto,
  toont,
  type ClientConfig,
} from './client.ts'

const indeling = ClientSchema.shape.indeling

/** A config with only the field toont() reads. */
const config = (weglaten: string[] = []) => ({ indeling: { weglaten } }) as unknown as ClientConfig

test('zonder indeling-blok staat elke sectie er gewoon', () => {
  // The live fleet has no `indeling:`, so the default has to be "omit nothing" -- and it has
  // to survive the schema, not just toont(), because the default is what fills the field.
  const leeg = indeling.parse(undefined)
  assert.deepEqual(leeg.weglaten, [])
  for (const sectie of WEGLAATBAAR) {
    assert.equal(toont(config(leeg.weglaten), sectie), true)
  }
})

test('een weggelaten sectie is weg, de rest blijft', () => {
  const cfg = config(['werkgebied', 'usps'])
  assert.equal(toont(cfg, 'werkgebied'), false)
  assert.equal(toont(cfg, 'usps'), false)
  assert.equal(toont(cfg, 'intro'), true)
  assert.equal(toont(cfg, 'werk'), true)
})

test('hoogstens twee, anders oogt de pagina onaf', () => {
  // Nine sections minus two is six, which is where the real-site survey put the floor. A
  // third omission is not sparseness, it is an unfinished site, and it costs the trust the
  // sparseness was buying.
  assert.ok(indeling.safeParse({ weglaten: ['intro', 'werk'] }).success)
  assert.ok(!indeling.safeParse({ weglaten: ['intro', 'werk', 'usps'] }).success)
})

test('alleen de vier secties die een site echt kan missen', () => {
  // Hero, diensten, the closing CTA, the hours panel and the footer are how a visitor calls
  // the business or learns when it is open. None of them is offered here, and a yaml that
  // asks for one must fail loudly rather than be ignored quietly.
  assert.deepEqual([...WEGLAATBAAR], ['intro', 'werk', 'werkgebied', 'usps'])
  for (const verboden of ['hero', 'diensten', 'spoed', 'slot', 'contact', 'footer']) {
    assert.ok(
      !indeling.safeParse({ weglaten: [verboden] }).success,
      `${verboden} mag niet weggelaten kunnen worden`,
    )
  }
})

// --- de compositie: hero en diensten ---------------------------------------------------

test('een yaml met alleen weglaten krijgt nog steeds de oude compositie', () => {
  // Same promise STANDAARD_STIJL makes about the skin. The live fleet's client.yaml files
  // predate both axes, and a site that silently changed its hero on the next deploy is the
  // one failure mode a default exists to prevent.
  assert.deepEqual(indeling.parse(undefined), STANDAARD_INDELING)
  assert.deepEqual(indeling.parse({ weglaten: ['usps'] }), {
    ...STANDAARD_INDELING,
    weglaten: ['usps'],
  })
  assert.equal(STANDAARD_INDELING.hero, 'gesplitst')
  assert.equal(STANDAARD_INDELING.diensten, 'kaarten')
})

test('de compositie neemt elke waarde uit de woordenschat en niets anders', () => {
  for (const hero of HEROS) assert.equal(indeling.parse({ hero }).hero, hero)
  for (const diensten of DIENSTVORMEN) {
    assert.equal(indeling.parse({ diensten }).diensten, diensten)
  }
  // The R3 fixture bug in its indeling form: a value from one axis put on the other rides
  // to a Zod refusal at build time unless the enum catches it here.
  assert.ok(!indeling.safeParse({ hero: 'kaarten' }).success)
  assert.ok(!indeling.safeParse({ diensten: 'gesplitst' }).success)
  assert.ok(!indeling.safeParse({ hero: 'plaat' }).success)
})

test('elke hero-vorm is een andere vorm', () => {
  // An axis whose values resolve to the same arrangement is a knob wired to nothing: the
  // founder picks a different hero and the page does not move.
  const gezien = new Set(HEROS.map((h) => JSON.stringify(HERO_VORM[h])))
  assert.equal(gezien.size, HEROS.length, 'twee hero-waarden leveren dezelfde vorm op')
  for (const hero of HEROS) {
    const vorm = HERO_VORM[hero]
    // The photo is either beside the copy or under it. Both at once would draw the hero
    // frame twice on one screen, which no arrangement wants.
    assert.ok(!(vorm.kolommen && vorm.fotoBreed), `${hero} zet de foto twee keer neer`)
    // A hero that draws no photograph must not ask for a column to put one in.
    if (!heroToontFoto(hero)) {
      assert.equal(vorm.kolommen, false, `${hero} vraagt een fotokolom zonder foto`)
      assert.equal(vorm.fotoBreed, false, `${hero} vraagt een fotoband zonder foto`)
    }
  }
})

test('precies een hero-vorm laat de foto weg', () => {
  // Sized deliberately: `typografisch` is the honest arrangement for a vak whose stock set
  // has no hero frame worth the first screen, and a second photo-less value would just be
  // the same page with different padding.
  const zonder = HEROS.filter((h) => !heroToontFoto(h))
  assert.deepEqual(zonder, ['typografisch'])
})

test('een kop die de belknop onder de vouw duwt komt er niet doorheen', () => {
  // The other half of R4's measurement, re-aimed at the string the H1 now holds. Tested via
  // the checked schema because the cap depends on schaal, which lives in another block.
  const basis = {
    modus: 'preview',
    bedrijf: {
      naam: 'Voorbeeld Barbier',
      vak: 'kapper',
      telefoon: '+31 6 12 34 56 78',
      adres: { plaats: 'Rotterdam' },
      werkgebied: ['Kralingen'],
    },
    branding: { kleur_primair: '#1e463c', kleur_accent: '#b4762a' },
    diensten: [
      { naam: 'Knippen', omschrijving: 'Wassen, knippen en afwerken.' },
      { naam: 'Scheren', omschrijving: 'Klassiek nat scheren met het mes.' },
      { naam: 'Baard', omschrijving: 'Baard op lengte brengen en afwerken.' },
    ],
    openingstijden: { dinsdag: ['09:00', '18:00'] },
    spoed: { beschikbaar: false },
    usps: ['Vaste barbier', 'Ook zonder afspraak welkom'],
    receptionist: false,
  }
  const met = (kop: string, schaal: string) =>
    ClientSchemaChecked.safeParse({ ...basis, stijl: { schaal }, teksten: { kop } })

  assert.ok(met('Knippen en scheren aan de rand van Kralingen', 'groot').success)
  assert.ok(!met('K'.repeat(71), 'groot').success)
  // A smaller scale carries a longer line, so the same headline is fine one step down.
  assert.ok(met('K'.repeat(71), 'normaal').success)
  assert.ok(!met('K'.repeat(91), 'normaal').success)
})
