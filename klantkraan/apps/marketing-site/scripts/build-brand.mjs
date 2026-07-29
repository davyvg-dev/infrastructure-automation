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
const FONT = resolve(__dirname, 'fonts/BricolageGrotesque-ExtraBold.ttf')
const PUBLIC = resolve(__dirname, '../public')

// Mirrors src/styles/global.css. Kept literal because sharp cannot read CSS
// custom properties -- if the palette moves there, move it here too.
const NIGHT = '#0f1c1e'
const CHALK = '#f4efe6'
const SODIUM = '#ffb84d'

/** Render one line of Bricolage to a transparent RGBA buffer. */
async function wordmark(text, { size, color }) {
  const png = await sharp({
    text: {
      text: `<span foreground="${color}">${text}</span>`,
      font: `Bricolage Grotesque ExtraBold ${size}`,
      fontfile: FONT,
      rgba: true,
      dpi: 72,
    },
  })
    .png()
    .toBuffer()
  const { width, height } = await sharp(png).metadata()
  return { png, width, height }
}

/**
 * The lockup: the sodium lamp that "stays on", then the wordmark. Transparent
 * background so one asset works on any band colour; the mail template paints
 * the same night behind it.
 */
async function buildEmailLogo() {
  const size = 56
  const dot = Math.round(size * 0.5)
  const gap = Math.round(size * 0.42)
  const mark = await wordmark('klantkraan', { size, color: CHALK })

  const width = dot + gap + mark.width
  const height = mark.height
  const dotTop = Math.round((height - dot) / 2)

  const circle = Buffer.from(
    `<svg xmlns="http://www.w3.org/2000/svg" width="${dot}" height="${dot}">` +
      `<circle cx="${dot / 2}" cy="${dot / 2}" r="${dot / 2}" fill="${SODIUM}"/></svg>`
  )

  const out = resolve(PUBLIC, 'email/logo.png')
  await mkdir(dirname(out), { recursive: true })
  await sharp({
    create: { width, height, channels: 4, background: { r: 0, g: 0, b: 0, alpha: 0 } },
  })
    .composite([
      { input: circle, top: dotTop, left: 0 },
      { input: mark.png, top: 0, left: dot + gap },
    ])
    .png({ compressionLevel: 9 })
    .toFile(out)

  // The template renders it at half size, so the asset is retina-sharp.
  console.log(`logo.png        ${width}x${height} (display ${width / 2}x${height / 2})`)
}

await buildEmailLogo()
