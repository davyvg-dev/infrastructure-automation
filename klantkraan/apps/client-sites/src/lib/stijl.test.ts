// Tests for the design vocabulary (stijl.ts) -- the resolver, not the chooser.
//
// `app.sitestyle` picks a stijl and has its own 41 tests on the Python side. What those
// cannot see is what a chosen stijl actually resolves to, because the tokens live here.
// The division: sitestyle's tests prove the choice stays inside the vocabulary; these
// prove the vocabulary means something coherent once resolved.
//
// The bug class this exists for is silence. Every axis is a plain record spread into one
// object, so a missing key does not throw -- it drops a custom property, the stylesheet
// default takes over, and one client's site is subtly wrong in a way no build step
// notices. Same for a stack naming a font family whose directory was never copied: the
// page falls back to Arial on a stranger's screen and nothing anywhere goes red.
//
// `pnpm check` (R6) already gates the built page, but only for the one combination that
// client actually got. These sweep all 1728 of them, which is what makes adding a new
// value to an axis safe.

import { test } from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

import {
  FOTOZETTINGEN,
  KLEURINGEN,
  LETTERONTWERPEN,
  MATEN,
  PALETTEN,
  RITMES,
  SCHALEN,
  STANDAARD_STIJL,
  VORMEN,
  fontDirs,
  resolveStijl,
  stijlStyle,
  type Stijl,
} from './stijl.ts'
import { ClientSchema } from './client.ts'
import manifest from '../../fonts/manifest.json' with { type: 'json' }

const appRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..')

/** Every stijl the vocabulary can express: 4 x 3 x 3 x 3 x 4 x 2 x 2 x 3. */
function alleStijlen(): Stijl[] {
  const out: Stijl[] = []
  for (const letterontwerp of LETTERONTWERPEN)
    for (const schaal of SCHALEN)
      for (const vorm of VORMEN)
        for (const ritme of RITMES)
          for (const palet of PALETTEN)
            for (const kleuring of KLEURINGEN)
              for (const foto of FOTOZETTINGEN)
                for (const maat of MATEN)
                  out.push({ letterontwerp, schaal, vorm, ritme, palet, kleuring, foto, maat })
  return out
}

const ALLE = alleStijlen()

/** The default with one axis moved, for isolating what a single value does. */
const met = (axis: Partial<Stijl>): Stijl => ({ ...STANDAARD_STIJL, ...axis })

/** A length token to rem. Handles `1.05rem`, `0px`, and both ends of a clamp(). */
function rem(value: string, end: 'min' | 'max' = 'max'): number {
  const clamp = value.match(/^clamp\(\s*([^,]+),\s*([^,]+),\s*([^)]+)\)$/)
  if (clamp) return rem(end === 'min' ? clamp[1] : clamp[3])
  const m = value.trim().match(/^(-?[\d.]+)(rem|px|em)$/)
  assert.ok(m, `not a length: "${value}"`)
  return m![2] === 'px' ? Number(m![1]) / 16 : Number(m![1])
}

/**
 * The webfont a stack asks for, or null when it leads with a system face. Only the first
 * family can be the webfont -- everything after it is the fallback tail, which names system
 * faces that are quoted too (`'Segoe UI'`).
 */
function leadingFamily(stack: string): string | null {
  const eerste = stack.split(',')[0].trim()
  return eerste.match(/^'(.+)'$/)?.[1] ?? null
}

/** One level of var() indirection inside a resolved token set. */
const deref = (tokens: Record<string, string>, value: string): string => {
  const ref = value.match(/^var\(\s*(--[\w-]+)\s*\)$/)
  return ref ? (tokens[ref[1]] ?? assert.fail(`dangling var(${ref[1]})`)) : value
}

// --- the shape of what comes out ----------------------------------------------------------
//
// The three assertions that make every later test meaningful: nothing is missing, nothing
// is empty, and no two axes are quietly overwriting each other.

test('every combination resolves the same set of properties', () => {
  const expected = Object.keys(resolveStijl(STANDAARD_STIJL)).sort()
  assert.ok(expected.length > 0)
  for (const stijl of ALLE) {
    const got = Object.keys(resolveStijl(stijl)).sort()
    assert.deepEqual(got, expected, `${JSON.stringify(stijl)} emits a different token set`)
  }
})

test('no combination resolves a property to nothing', () => {
  for (const stijl of ALLE) {
    for (const [prop, value] of Object.entries(resolveStijl(stijl))) {
      assert.equal(typeof value, 'string', `${prop} is not a string in ${JSON.stringify(stijl)}`)
      assert.ok(value.trim().length > 0, `${prop} is empty in ${JSON.stringify(stijl)}`)
      assert.ok(!value.includes('undefined'), `${prop} is "${value}" in ${JSON.stringify(stijl)}`)
    }
  }
})

test('the axes write disjoint properties', () => {
  // Two axes writing the same custom property means the later spread wins and the earlier
  // axis is dead: the founder moves a knob and nothing on the page changes.
  const base = new Set(Object.keys(resolveStijl(STANDAARD_STIJL)))
  const claimed = new Map<string, string>()
  const axes: [string, Partial<Stijl>[]][] = [
    ['letterontwerp', LETTERONTWERPEN.map((v) => ({ letterontwerp: v }))],
    ['schaal', SCHALEN.map((v) => ({ schaal: v }))],
    ['vorm', VORMEN.map((v) => ({ vorm: v }))],
    ['ritme', RITMES.map((v) => ({ ritme: v }))],
    ['palet', PALETTEN.map((v) => ({ palet: v }))],
    ['kleuring', KLEURINGEN.map((v) => ({ kleuring: v }))],
    ['foto', FOTOZETTINGEN.map((v) => ({ foto: v }))],
    ['maat', MATEN.map((v) => ({ maat: v }))],
  ]
  for (const [naam, waarden] of axes) {
    // Which properties this axis moves: the ones whose value is not the same for every
    // value of the axis. An axis that moves nothing is a knob wired to nothing.
    const moved = [...base].filter((prop) => {
      const seen = new Set(waarden.map((w) => resolveStijl(met(w))[prop]))
      return seen.size > 1
    })
    assert.ok(moved.length > 0, `axis ${naam} changes no property`)
    for (const prop of moved) {
      const eerder = claimed.get(prop)
      assert.equal(eerder, undefined, `${prop} is written by both ${eerder} and ${naam}`)
      claimed.set(prop, naam)
    }
  }
})

// --- the default is the old look ----------------------------------------------------------

test('the default skin is the look that shipped before the vocabulary', () => {
  // The promise in stijl.ts: a client.yaml with no `stijl:` block builds the same bytes it
  // did yesterday. The visible half of that is the type -- no webfont, no font directory,
  // nothing for the build to copy.
  const tokens = resolveStijl(STANDAARD_STIJL)
  assert.equal(STANDAARD_STIJL.letterontwerp, 'systeem')
  assert.equal(tokens['--font-sans'], tokens['--font-display'])
  // Nothing prepended: the stack leads with system-ui, the way it did before webfonts.
  // (`'Segoe UI'` and `'Helvetica Neue'` further down are quoted for their spaces and are
  // system faces, so a quote anywhere in the stack proves nothing -- only the lead does.)
  assert.equal(leadingFamily(tokens['--font-sans']), null)
  assert.ok(tokens['--font-sans'].startsWith('system-ui'))
  assert.deepEqual(fontDirs(STANDAARD_STIJL.letterontwerp), [])
})

test('the schema fills every axis in, so an old config still has a full skin', () => {
  const leeg = ClientSchema.shape.stijl.parse(undefined)
  assert.deepEqual(leeg, STANDAARD_STIJL)
  // A partial block ("just make it roomier") is a config, not an error.
  const deels = ClientSchema.shape.stijl.parse({ ritme: 'ruim' })
  assert.deepEqual(deels, { ...STANDAARD_STIJL, ritme: 'ruim' })
})

test('the schema takes every vocabulary value and nothing else', () => {
  for (const stijl of ALLE) assert.deepEqual(ClientSchema.shape.stijl.parse(stijl), stijl)
  // The R3 fixture bug: a value from one axis put on another rode all the way to a Zod
  // refusal at build time because nothing earlier checked it against the vocabulary.
  assert.throws(() => ClientSchema.shape.stijl.parse(met({ ritme: 'royaal' as never })))
  assert.throws(() => ClientSchema.shape.stijl.parse(met({ palet: 'zwart' as never })))
})

// --- type ---------------------------------------------------------------------------------

test('every pairing leads with the family the manifest names', () => {
  // The stacks are built here, the bytes are copied by astro.config.mjs, and both read
  // fonts/manifest.json. This is the assertion that keeps them the same file's worth of
  // truth: what the CSS asks for first is what the build was told to ship.
  for (const naam of LETTERONTWERPEN) {
    const pairing = manifest[naam] as {
      dirs: string[]
      display: string | null
      body: string | null
    }
    const tokens = resolveStijl(met({ letterontwerp: naam }))
    for (const [prop, familie] of [
      ['--font-sans', pairing.body],
      ['--font-display', pairing.display],
    ] as const) {
      assert.equal(leadingFamily(tokens[prop]), familie, `${naam} ${prop}: ${tokens[prop]}`)
    }
  }
})

test('only the serif pairing falls back to a serif', () => {
  // A sans-serif page whose webfont fails to load should land on another sans. Georgia
  // behind Figtree is a visible fault, not a fallback, and it only shows up on the
  // connections too slow to have loaded the woff2 -- the ones least likely to be looked at.
  for (const naam of LETTERONTWERPEN) {
    const display = resolveStijl(met({ letterontwerp: naam }))['--font-display']
    assert.equal(
      /serif$/.test(display) && display.includes('Georgia'),
      naam === 'redactioneel',
      `${naam} display stack: ${display}`,
    )
  }
})

test('every family a stack names has a directory the build really has', () => {
  // The silent-Arial bug: a stack asking for a family whose woff2 was never copied does
  // not fail anything, it just quietly renders in the fallback on a client's live site.
  for (const naam of LETTERONTWERPEN) {
    const tokens = resolveStijl(met({ letterontwerp: naam }))
    const gevraagd = new Set(
      [tokens['--font-sans'], tokens['--font-display']]
        .map(leadingFamily)
        .filter((f) => f !== null)
        .map((familie) => familie.toLowerCase().replace(/\s+/g, '')),
    )
    assert.deepEqual([...gevraagd].sort(), [...fontDirs(naam)].sort(), `${naam} stacks vs dirs`)
    for (const dir of fontDirs(naam)) {
      const bestanden = fs.readdirSync(path.join(appRoot, 'fonts', dir))
      assert.ok(
        bestanden.some((f) => f.endsWith('.woff2')),
        `fonts/${dir}/ has no woff2 for ${naam}`,
      )
    }
  }
})

test('the fallback tail behind every sans stack is the same one', () => {
  // The tail is what a visitor reads while the woff2 is still in flight, and on the
  // connections where that matters most it is what they read full stop. One tail for every
  // pairing means the unstyled page is the same page, not a different design per client.
  const tails = new Set(
    LETTERONTWERPEN.map((naam) => {
      const stack = resolveStijl(met({ letterontwerp: naam }))['--font-sans']
      return leadingFamily(stack) === null ? stack : stack.slice(stack.indexOf(',') + 1).trim()
    }),
  )
  assert.equal(tails.size, 1, `sans fallbacks differ: ${[...tails].join(' | ')}`)
  assert.ok([...tails][0].startsWith('system-ui'))
})

test('display weight and tracking suit the face', () => {
  for (const naam of LETTERONTWERPEN) {
    const tokens = resolveStijl(met({ letterontwerp: naam }))
    for (const prop of ['--text-h1--font-weight', '--text-h2--font-weight']) {
      const gewicht = Number(tokens[prop])
      assert.ok(
        Number.isInteger(gewicht / 100) && gewicht >= 100 && gewicht <= 900,
        `${naam} ${prop} is ${tokens[prop]}`,
      )
    }
    // Never positive: letterspacing a headline out is a 1990s tell, and at h1 size the
    // default tracking is already too loose for every face here.
    const tracking = rem(tokens['--display-tracking'])
    assert.ok(tracking <= 0, `${naam} tracks out at ${tokens['--display-tracking']}`)
    // Instrument Serif is the one high-contrast face: negative tracking collides its thin
    // strokes, so it is the only pairing allowed to sit at 0.
    assert.equal(tracking === 0, naam === 'redactioneel', `${naam} tracking ${tracking}`)
  }
})

test('the type scale runs downhill inside every schaal', () => {
  const trap = ['--text-h1', '--text-h2', '--text-h3', '--text-body', '--text-small']
  for (const schaal of SCHALEN) {
    const tokens = resolveStijl(met({ schaal }))
    for (const end of ['min', 'max'] as const) {
      const sizes = trap.map((prop) => rem(tokens[prop], end))
      for (let i = 1; i < sizes.length; i++) {
        assert.ok(
          sizes[i] < sizes[i - 1],
          `${schaal} ${end}: ${trap[i]} (${sizes[i]}) is not below ${trap[i - 1]} (${sizes[i - 1]})`,
        )
      }
    }
  }
})

test('the schalen are ordered at every step', () => {
  const trap = ['--text-h1', '--text-h2', '--text-h3', '--text-body', '--text-small']
  const perSchaal = SCHALEN.map((s) => resolveStijl(met({ schaal: s })))
  for (const prop of trap) {
    for (const end of ['min', 'max'] as const) {
      const sizes = perSchaal.map((t) => rem(t[prop], end))
      for (let i = 1; i < sizes.length; i++) {
        assert.ok(
          sizes[i] > sizes[i - 1],
          `${prop} ${end}: ${SCHALEN[i]} (${sizes[i]}) is not above ${SCHALEN[i - 1]} (${sizes[i - 1]})`,
        )
      }
    }
  }
})

test('no fluid step sizes itself on viewport width alone', () => {
  // WCAG 2.2 SC 1.4.4. `clamp(1.9rem, 4.5vw, 3rem)` -- what every step used to be -- does
  // not respond to browser zoom: the viewport unit is measured in CSS pixels, which zoom
  // does not change, so the glyphs stay put while the page around them grows. A reader at
  // 200% gets a headline that is now, relatively, half the size it was. The preferred term
  // has to carry a rem for the zoom to have anything to act on.
  //
  // Checked across every combination rather than over SCHAAL_TOKENS, so a later axis that
  // introduces a fluid token of its own is held to the same rule.
  for (const stijl of ALLE) {
    for (const [prop, value] of Object.entries(resolveStijl(stijl))) {
      const preferred = value.match(/^clamp\(\s*[^,]+,\s*([^,]+),\s*[^)]+\)$/)?.[1]
      if (!preferred) continue
      assert.ok(
        !/v(w|h|min|max)/.test(preferred) || /r?em/.test(preferred),
        `${prop} scales on viewport alone: "${value}" (${JSON.stringify(stijl)})`,
      )
    }
  }
})

test('every fluid step still meets its endpoints at a phone and at a desktop', () => {
  // The rem+vw rewrite is only safe if it did not quietly resize the pages that already
  // exist. Each pair was solved to hold the old bounds at the two viewports that matter,
  // so the clamp must bottom out at or below its minimum on a 375px phone and reach its
  // maximum by a 1440px desktop -- outside that band the clamp itself takes over and the
  // preferred term is not what the reader sees.
  const px = (value: string, viewport: number) => {
    const m = value.match(/^([\d.]+)rem \+ ([\d.]+)vw$/)
    assert.ok(m, `preferred term is not "<rem> + <vw>": "${value}"`)
    return Number(m![1]) * 16 + (Number(m![2]) / 100) * viewport
  }
  for (const schaal of SCHALEN) {
    const tokens = resolveStijl(met({ schaal }))
    for (const prop of ['--text-h1', '--text-h2']) {
      const clamp = tokens[prop].match(/^clamp\(\s*([^,]+),\s*([^,]+),\s*([^)]+)\)$/)
      assert.ok(clamp, `${schaal} ${prop} is not a clamp`)
      const [min, preferred, max] = [rem(clamp![1]) * 16, clamp![2], rem(clamp![3]) * 16]
      // Within half a pixel: the coefficients are rounded to two decimals on purpose, so
      // they stay readable in the stylesheet.
      assert.ok(
        Math.abs(px(preferred, 375) - min) < 0.5,
        `${schaal} ${prop} is ${px(preferred, 375).toFixed(1)}px at 375, want ${min}px`,
      )
      assert.ok(
        Math.abs(px(preferred, 1440) - max) < 0.5,
        `${schaal} ${prop} is ${px(preferred, 1440).toFixed(1)}px at 1440, want ${max}px`,
      )
    }
  }
})

test('every schaal a split hero can carry stays under the half-column ceiling', () => {
  // Q9's finding, from a build rather than a test: the h1 sits in a HALF-WIDTH hero column,
  // and at 68px a long Dutch headline ran to five lines and pushed the call button off a
  // 1000px screen. A trade site that hides its phone number below the fold has lost the only
  // conversion it has. 3.5rem is the cap that survived.
  //
  // `royaal` is the deliberate exception and the reason this test is phrased around the
  // arrangement rather than the type: 88px is what the award reference set does, it needs
  // the whole column to do it, and ClientSchemaChecked refuses it next to `hero: gesplitst`.
  // The ceiling is a property of the layout, so it is asserted against the layouts that
  // actually have to survive it.
  for (const schaal of SCHALEN) {
    if (schaal === 'royaal') continue
    const h1 = resolveStijl(met({ schaal }))['--text-h1']
    assert.ok(rem(h1, 'max') <= 3.5, `${schaal} h1 tops out at ${h1}`)
  }
  // And the exception is really an exception: it would fail the rule above.
  assert.ok(rem(resolveStijl(met({ schaal: 'royaal' }))['--text-h1'], 'max') > 3.5)
})

// --- rhythm and shape ---------------------------------------------------------------------

test('the ritmes are ordered and the photo band always carries more air', () => {
  const perRitme = RITMES.map((r) => resolveStijl(met({ ritme: r })))
  for (const prop of ['--ritme-y', '--ritme-y-md', '--ritme-band-y', '--ritme-band-y-md']) {
    const air = perRitme.map((t) => rem(t[prop]))
    for (let i = 1; i < air.length; i++) {
      assert.ok(air[i] > air[i - 1], `${prop}: ${RITMES[i]} is not roomier than ${RITMES[i - 1]}`)
    }
  }
  for (const [i, ritme] of RITMES.entries()) {
    const t = perRitme[i]
    // The band has always been the roomiest thing on the page; that relationship is what
    // makes it read as a break rather than another section, and it has to hold at every
    // density or `dicht` loses the break entirely.
    assert.ok(rem(t['--ritme-band-y']) > rem(t['--ritme-y']), `${ritme} band is not roomier`)
    assert.ok(rem(t['--ritme-band-y-md']) > rem(t['--ritme-y-md']), `${ritme} band md`)
    // Wider viewport, more air, never less.
    assert.ok(rem(t['--ritme-y-md']) > rem(t['--ritme-y']), `${ritme} md is not roomier`)
    assert.ok(rem(t['--ritme-band-y-md']) > rem(t['--ritme-band-y']), `${ritme} band md`)
  }
})

test('the maten are ordered and the prose never outgrows the page', () => {
  const perMaat = MATEN.map((m) => resolveStijl(met({ maat: m })))
  for (const prop of [
    '--maat-kolom',
    '--maat-band',
    '--maat-kop',
    '--maat-tekst',
    '--maat-gutter',
  ]) {
    const breedtes = perMaat.map((t) => rem(t[prop]))
    for (let i = 1; i < breedtes.length; i++) {
      // Weak ordering: the gutter is allowed to stay put between two maten, the columns
      // are not, and the loop below is what separates those two cases.
      assert.ok(
        breedtes[i] >= breedtes[i - 1],
        `${prop}: ${MATEN[i]} (${breedtes[i]}) is narrower than ${MATEN[i - 1]} (${breedtes[i - 1]})`,
      )
    }
  }
  for (const [i, maat] of MATEN.entries()) {
    const t = perMaat[i]
    const [kolom, band, kop, tekst] = [
      '--maat-kolom',
      '--maat-band',
      '--maat-kop',
      '--maat-tekst',
    ].map((p) => rem(t[p]))
    // A reading measure wider than the container it sits in is a token that does nothing:
    // the container clips it and the founder moves a knob with no effect on the page.
    assert.ok(tekst < kolom, `${maat}: text measure ${tekst} is not inside the ${kolom} column`)
    // The photo band interrupts the page by being wider than it. A band narrower than the
    // text above it reads as a mistake rather than as a frame.
    assert.ok(band > kolom, `${maat}: band ${band} is not wider than the ${kolom} column`)
    // Headings want a shorter line than running text, not a longer one. This is the
    // relationship that stops a wide site setting its H2 across the full column.
    assert.ok(kop < tekst, `${maat}: heading measure ${kop} is not under the text measure ${tekst}`)
  }
})

test('a wider page buys margin and photographs, not longer lines', () => {
  // The failure this exists for: scaling every measure by the same factor, which is what
  // makes a "roomier" site read as a harder one to read. Body text at 1.0625rem lands
  // around 8.5px per character, so 48rem is already ~90 characters -- past the 45-75 a
  // typographer would ask for, and the ceiling this axis must not push through.
  const smal = resolveStijl(met({ maat: 'smal' }))
  const breed = resolveStijl(met({ maat: 'breed' }))
  const groei = (prop: string) => rem(breed[prop]) - rem(smal[prop])
  assert.ok(
    groei('--maat-tekst') <= groei('--maat-kolom') / 2,
    `the container grows ${groei('--maat-kolom')}rem against ${groei('--maat-tekst')}rem of prose`,
  )
  for (const maat of MATEN) {
    const tekst = rem(resolveStijl(met({ maat }))['--maat-tekst'])
    // The band the award reference set measured at: 44-64 characters, which at 1.0625rem
    // body is roughly 26-38rem. The old literals sat at 48rem (~90ch), well outside it.
    assert.ok(tekst >= 26 && tekst <= 38, `${maat} sets running text across ${tekst}rem`)
  }
})

test('maat normaal keeps the old container and deliberately narrows the measure', () => {
  // The literals this axis replaced were max-w-5xl (64rem), max-w-2xl (42rem), max-w-3xl
  // (48rem) and px-6 (1.5rem). The CONTAINERS still hold those numbers, so the silhouette of
  // an existing site did not move.
  const t = resolveStijl(met({ maat: 'normaal' }))
  assert.equal(t['--maat-kolom'], '64rem')
  assert.equal(t['--maat-gutter'], '1.5rem')
  assert.equal(STANDAARD_STIJL.maat, 'normaal')
  // The reading measures deliberately did move, and this is the assertion that says so out
  // loud rather than letting a later reader think it was a slip. 48rem of Dutch body text is
  // ~90 characters a line; the sixteen award sites measured run 44-64ch. See MAAT_TOKENS.
  assert.ok(rem(t['--maat-kop']) < 42, 'the heading measure was supposed to come down')
  assert.ok(rem(t['--maat-tekst']) < 48, 'the prose measure was supposed to come down')
})

test('the framed photo band is wider than the page and follows it', () => {
  // --foto-kolom used to be pinned at 72rem while the page was pinned at 64: the band was
  // deliberately the wider of the two. Now that `maat` moves the page, a pinned band would
  // end up NARROWER than the column it sits in at maat: breed, which reads as a mistake
  // rather than as a frame. Deriving it keeps the relationship at every maat.
  for (const maat of MATEN) {
    const t = resolveStijl(met({ maat, foto: 'ingekaderd' }))
    assert.equal(deref(t, t['--foto-kolom']), t['--maat-band'])
    assert.equal(deref(t, t['--foto-gutter']), t['--maat-gutter'])
  }
  // At the default that is the 72rem/1.5rem the token was pinned at before the axis.
  const standaard = resolveStijl(STANDAARD_STIJL)
  assert.equal(rem(standaard['--maat-band']), 72)
  assert.equal(rem(standaard['--maat-gutter']), 1.5)
  // Bleeding still overrides both, whatever the maat says.
  for (const maat of MATEN) {
    assert.equal(resolveStijl(met({ maat, foto: 'randloos' }))['--foto-kolom'], '100%')
  }
})

test('one radius axis moves cards, buttons and photos together', () => {
  for (const vorm of VORMEN) {
    const t = resolveStijl(met({ vorm }))
    const [card, button, foto] = ['--radius-card', '--radius-button', '--radius-foto'].map((p) =>
      rem(t[p]),
    )
    // Sharp cards with pill buttons is two designs stapled together, which is the exact
    // tell this vocabulary exists to remove.
    assert.equal(vorm === 'scherp', card === 0 && button === 0 && foto === 0, `${vorm} radii`)
    // The hero photograph is one large plate and carries a bigger corner than the tiles,
    // which sit beside the dienst cards and match them.
    assert.ok(foto >= card, `${vorm}: photo radius ${foto} is under the card radius ${card}`)
  }
})

test('randloos squares every photo corner, whatever the vorm says', () => {
  // vorm and foto both have an opinion about the corner of the same photograph. The
  // framed variant spends the vorm token, the bleeding one zeroes it -- so they cannot
  // disagree, and a `rond` site set randloos does not ship one rounded tile.
  for (const vorm of VORMEN) {
    const randloos = resolveStijl(met({ vorm, foto: 'randloos' }))
    assert.equal(rem(deref(randloos, randloos['--foto-radius'])), 0, `${vorm} randloos hero`)
    assert.equal(rem(deref(randloos, randloos['--foto-tegel-radius'])), 0, `${vorm} randloos tile`)

    const ingekaderd = resolveStijl(met({ vorm, foto: 'ingekaderd' }))
    assert.equal(deref(ingekaderd, ingekaderd['--foto-radius']), ingekaderd['--radius-foto'])
    assert.equal(
      deref(ingekaderd, ingekaderd['--foto-tegel-radius']),
      ingekaderd['--radius-card'],
      `${vorm} framed tile does not follow the card`,
    )
  }
})

// --- colour --------------------------------------------------------------------------------
//
// Only the palet's own pairs, which are fixed hex and involve no client colour: sRGB
// luminance is the whole of the maths. The combinations that mix in --brand-primary are
// `pnpm check`'s job, on the built page, in OKLab -- the space they are actually mixed in.
// Restating that resolver here would give two implementations of one gate to keep in step.

const srgbToLinear = (c: number) => (c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4)
const luminance = (hex: string) => {
  const n = parseInt(hex.slice(1), 16)
  const [r, g, b] = [(n >> 16) & 255, (n >> 8) & 255, n & 255].map((c) => srgbToLinear(c / 255))
  return 0.2126 * r + 0.7152 * g + 0.0722 * b
}
const contrast = (a: string, b: string) => {
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x)
  return (hi + 0.05) / (lo + 0.05)
}

test('every palet clears AA for text on its own surfaces', () => {
  // Muted text is still text: --color-mist gets the same 4.5:1 as --color-ink, not the 3:1
  // a large-text exemption would buy. --color-line is absent on purpose -- a hairline
  // carries no information a visitor could lose, which is the case WCAG 1.4.11 exempts.
  for (const palet of PALETTEN) {
    const t = resolveStijl(met({ palet }))
    for (const fg of ['--color-ink', '--color-mist']) {
      for (const bg of ['--color-paper', '--color-card']) {
        const ratio = contrast(t[fg], t[bg])
        assert.ok(
          ratio >= 4.5,
          `${palet}: ${fg} (${t[fg]}) on ${bg} (${t[bg]}) is ${ratio.toFixed(2)}:1`,
        )
      }
    }
    // Ink outranks mist, or the hierarchy the two colours exist to express is inverted.
    assert.ok(luminance(t['--color-ink']) < luminance(t['--color-mist']), `${palet} ink vs mist`)
    // Card is the raised surface: it has to read as lighter than the paper behind it.
    assert.ok(luminance(t['--color-card']) > luminance(t['--color-paper']), `${palet} card`)
  }
})

test('spaarzaam leaves the bands untinted and royaal tints all three', () => {
  const spaarzaam = resolveStijl(met({ kleuring: 'spaarzaam' }))
  assert.equal(deref(spaarzaam, spaarzaam['--band-bg']), spaarzaam['--color-card'])
  assert.equal(deref(spaarzaam, spaarzaam['--band-line']), spaarzaam['--color-line'])

  const royaal = resolveStijl(met({ kleuring: 'royaal' }))
  for (const prop of ['--band-bg', '--band-line', '--band-foto-bg']) {
    assert.match(royaal[prop], /^color-mix\(in oklab, var\(--brand-primary\) \d+%/, prop)
  }
  // The tint is what --color-ink then has to survive, so it stays low. Above ~20% the
  // band stops being a surface and becomes a colour field, and body text on it goes.
  for (const kleuring of KLEURINGEN) {
    for (const [prop, value] of Object.entries(resolveStijl(met({ kleuring })))) {
      const mix = value.match(/color-mix\(in oklab, var\(--brand-primary\) ([\d.]+)%/)
      if (mix) assert.ok(Number(mix[1]) <= 20, `${kleuring} ${prop} mixes ${mix[1]}% brand`)
    }
  }
})

test('every band tint is mixed over the lightest surface, never over paper', () => {
  // R6b. The tint comes OUT of --brand-primary, so a darker client colour makes a darker
  // band -- the one direction a contrast floor on that colour cannot help with, because
  // raising the floor only makes the band darker still. Mixed over --color-paper, which is
  // already the darkest surface a palet owns, the two compound and the vocabulary has
  // combinations no floor can rescue (brand text bottomed out at 3.42:1). Over
  // --color-card the whole 1728-combination space clears AA at kleur_primair >= 5.25.
  for (const kleuring of KLEURINGEN) {
    for (const [prop, value] of Object.entries(resolveStijl(met({ kleuring })))) {
      const mix = value.match(/^color-mix\(in oklab, var\(--brand-primary\) [\d.]+%, (.+)\)$/)
      if (!mix) continue
      assert.ok(
        mix[1] === 'var(--color-card)' || mix[1] === 'var(--color-line)',
        `${kleuring} ${prop} tints over ${mix[1]}; only card (surfaces) and line (hairlines) are safe`,
      )
    }
  }
})

test('the photo band never gets more tint than the band it alternates with can carry', () => {
  // --band-foto-bg is the only surface that takes brand-coloured text (Werk's eyebrow) on
  // top of a brand-coloured tint, so it is where the colour meets itself and it cannot be
  // the most heavily tinted thing on the page. 13% is what R6b had to come down from.
  const royaal = resolveStijl(met({ kleuring: 'royaal' }))
  const pct = (v: string) => Number(v.match(/var\(--brand-primary\) ([\d.]+)%/)?.[1] ?? Number.NaN)
  assert.ok(pct(royaal['--band-foto-bg']) <= 8, `foto band mixes ${pct(royaal['--band-foto-bg'])}%`)
  for (const kleuring of KLEURINGEN) {
    const t = resolveStijl(met({ kleuring }))
    const foto = pct(t['--band-foto-bg'])
    if (Number.isNaN(foto)) continue
    // Both bands sit on the same page one after the other; a photo band tinted far past
    // the plain band reads as a different template, not a rhythm.
    const band = pct(t['--band-bg'])
    if (!Number.isNaN(band))
      assert.ok(foto - band <= 4, `${kleuring}: foto ${foto}% vs band ${band}%`)
  }
})

// --- what reaches <html> --------------------------------------------------------------------

test('stijlStyle emits declarations a browser can parse', () => {
  for (const stijl of ALLE) {
    const style = stijlStyle(stijl)
    const decls = style.split('; ')
    assert.equal(decls.length, Object.keys(resolveStijl(stijl)).length)
    for (const decl of decls) {
      assert.match(decl, /^--[a-z0-9-]+: [^;]+$/, `not a declaration: "${decl}"`)
    }
    // The whole thing goes into a double-quoted HTML attribute (Base.astro). A token
    // carrying a double quote would close it and the rest of the skin would become markup.
    assert.ok(!style.includes('"'), 'a token value carries a double quote')
  }
})

test('the brand hooks reach the page and the skin outranks them', () => {
  const extra = {
    '--brand-primary': '#0f4c81',
    '--brand-accent': '#f2a71b',
    // A caller cannot reach past the vocabulary: the skin is the last word on its own
    // tokens, so a one-off override in a layout cannot bypass what pnpm check gates.
    '--color-paper': '#000000',
  }
  const style = stijlStyle(met({ palet: 'zand' }), extra)
  assert.ok(style.includes('--brand-primary: #0f4c81'), 'brand primary dropped')
  assert.ok(style.includes('--brand-accent: #f2a71b'), 'brand accent dropped')
  assert.ok(style.includes('--color-paper: #f5f1ea'), 'the skin lost to the caller')
  assert.ok(!style.includes('#000000'))
})

test('kleuring: royaal can only tint a band because the brand hooks travel with it', () => {
  // The mix names var(--brand-primary), which is not a skin token: it comes from
  // client.yaml through the same inline style. If that ever stopped travelling together,
  // color-mix would fall back to nothing and the tinted bands would silently go flat.
  const style = stijlStyle(met({ kleuring: 'royaal' }), { '--brand-primary': '#0f4c81' })
  const genoemd = [...style.matchAll(/var\((--[\w-]+)\)/g)].map((m) => m[1])
  for (const prop of new Set(genoemd)) {
    assert.match(style, new RegExp(`(^|; )${prop}: `), `${prop} is referenced but never set`)
  }
})
