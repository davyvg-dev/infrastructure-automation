import { mkdir, writeFile } from 'node:fs/promises'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import sharp from 'sharp'

const __dirname = dirname(fileURLToPath(import.meta.url))
const outPath = resolve(__dirname, '../public/og-default.png')

const BG = '#0F4C81'
const FG = '#FAF6EE'
const ACCENT = '#C75A2B'
const MUTED = '#D9D2C0'

const wordmark = 'klantkraan'
const headline1 = 'De Klantenmotor voor'
const headline2 = 'Nederlandse vakmensen'
const footer = 'klantkraan.nl'

const fontStack = "'Helvetica Neue', Helvetica, Arial, sans-serif"

const svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <rect width="1200" height="630" fill="${BG}"/>
  <rect x="96" y="120" width="72" height="8" fill="${ACCENT}"/>
  <text x="96" y="200" fill="${FG}" font-family="${fontStack}" font-size="44" font-weight="600" letter-spacing="-1">${wordmark}</text>
  <text x="96" y="340" fill="${FG}" font-family="${fontStack}" font-size="76" font-weight="700" letter-spacing="-2">${headline1}</text>
  <text x="96" y="430" fill="${FG}" font-family="${fontStack}" font-size="76" font-weight="700" letter-spacing="-2">${headline2}</text>
  <line x1="96" y1="520" x2="1104" y2="520" stroke="${MUTED}" stroke-opacity="0.35" stroke-width="1"/>
  <text x="96" y="568" fill="${MUTED}" font-family="${fontStack}" font-size="28" font-weight="500" letter-spacing="0.5">${footer}</text>
</svg>`

await mkdir(dirname(outPath), { recursive: true })
await sharp(Buffer.from(svg))
  .png({ compressionLevel: 9 })
  .toFile(outPath)

const { size } = await import('node:fs').then((fs) => fs.promises.stat(outPath))
console.log(`Wrote ${outPath} (${(size / 1024).toFixed(1)} KB)`)
