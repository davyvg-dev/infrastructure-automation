/**
 * Renders the raster brand assets that HTML e-mail and social scrapers need.
 *
 * E-mail clients do not load web fonts and Gmail refuses SVG outright, so the
 * lockup that lives as CSS on the site has to exist as a PNG here. The wordmark
 * is drawn with the real Bricolage Grotesque ExtraBold (scripts/fonts/, OFL, the
 * same face public/fonts/ serves) rather than a system substitute, so the mail
 * header and the site header are the same logo.
 *
 * Run after any palette change:  node scripts/build-brand.mjs
 */
import { mkdir } from 'node:fs/promises'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import sharp from 'sharp'

const __dirname = dirname(fileURLToPath(import.meta.url))
const DISPLAY = resolve(__dirname, 'fonts/BricolageGrotesque-ExtraBold.ttf')
const BODY = resolve(__dirname, 'fonts/HankenGrotesk-Medium.ttf')
const PUBLIC = resolve(__dirname, '../public')

// Mirrors src/styles/global.css. Kept literal because sharp cannot read CSS
// custom properties -- if the palette moves there, move it here too.
const NIGHT = '#0f1c1e'
const CHALK = '#f4efe6'
const SODIUM = '#ffb84d'
const DIM = '#93a6a2'
const LINE = '#26403f'

/**
 * Render one line to a transparent RGBA buffer. `text` is Pango markup, so a
 * headline can carry two colours in a single run.
 */
async function line(text, { size, font = 'display' }) {
  const png = await sharp({
    text: {
      text,
      font:
        font === 'display'
          ? `Bricolage Grotesque ExtraBold ${size}`
          : `Hanken Grotesk Medium ${size}`,
      fontfile: font === 'display' ? DISPLAY : BODY,
      rgba: true,
      dpi: 72,
    },
  })
    .png()
    .toBuffer()
  const { width, height } = await sharp(png).metadata()
  return { png, width, height }
}

const paint = (t, color) => `<span foreground="${color}">${t}</span>`

/**
 * The lockup: the sodium lamp that "stays on", then the wordmark. Transparent
 * background so one asset works on any band colour; the mail template paints
 * the same night behind it.
 */
function lamp(dot) {
  return Buffer.from(
    `<svg xmlns="http://www.w3.org/2000/svg" width="${dot}" height="${dot}">` +
      `<circle cx="${dot / 2}" cy="${dot / 2}" r="${dot / 2}" fill="${SODIUM}"/></svg>`
  )
}

/** The lockup as its own layer, so both the mail logo and the OG card can place it. */
async function lockup(size) {
  const dot = Math.round(size * 0.5)
  const gap = Math.round(size * 0.42)
  const mark = await line(paint('klantkraan', CHALK), { size })
  return {
    width: dot + gap + mark.width,
    height: mark.height,
    layers: (top, left) => [
      { input: lamp(dot), top: top + Math.round((mark.height - dot) / 2), left },
      { input: mark.png, top, left: left + dot + gap },
    ],
  }
}

async function buildEmailLogo() {
  const kk = await lockup(56)
  const { width, height } = kk

  const out = resolve(PUBLIC, 'email/logo.png')
  await mkdir(dirname(out), { recursive: true })
  await sharp({
    create: { width, height, channels: 4, background: { r: 0, g: 0, b: 0, alpha: 0 } },
  })
    .composite(kk.layers(0, 0))
    .png({ compressionLevel: 9 })
    .toFile(out)

  // The template renders it at half size, so the asset is retina-sharp.
  console.log(`logo.png        ${width}x${height} (display ${width / 2}x${height / 2})`)
}

/**
 * The card LinkedIn, WhatsApp and Slack show when someone shares a link. It had
 * been left on the pre-redesign navy and the old "Klantenmotor" line, so a
 * shared link advertised a company the site no longer looks or sounds like.
 */
async function buildOgCard() {
  const W = 1200
  const H = 630
  const PAD = 96

  const kk = await lockup(34)
  const head = await line(`${paint('Het licht blijft', CHALK)} ${paint('aan.', SODIUM)}`, {
    size: 92,
  })
  const sub = await line(
    paint('De digitale receptionist voor uw website en WhatsApp. Dag en nacht.', DIM),
    { size: 32, font: 'body' }
  )
  const foot = await line(paint('klantkraan.nl', DIM), { size: 26, font: 'body' })

  const rule = Buffer.from(
    `<svg xmlns="http://www.w3.org/2000/svg" width="${W - PAD * 2}" height="1">` +
      `<rect width="${W - PAD * 2}" height="1" fill="${LINE}"/></svg>`
  )

  const out = resolve(PUBLIC, 'og-default.png')
  await sharp({ create: { width: W, height: H, channels: 4, background: NIGHT } })
    .composite([
      ...kk.layers(PAD, PAD),
      { input: head.png, top: 250, left: PAD },
      { input: sub.png, top: 250 + head.height + 36, left: PAD },
      { input: rule, top: H - 132, left: PAD },
      { input: foot.png, top: H - 100, left: PAD },
    ])
    .png({ compressionLevel: 9 })
    .toFile(out)

  console.log(`og-default.png  ${W}x${H}`)
}

await buildEmailLogo()
await buildOgCard()
