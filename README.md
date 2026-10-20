# Klantkraan

One business, three active parts. Klantkraan ([klantkraan.nl](https://klantkraan.nl)) sells AI receptionists to Dutch trades companies — text-first (website chat + WhatsApp + Telegram), voice as upsell.

| Part | What it is |
|---|---|
| [`klantkraan/`](klantkraan/) | Marketing site (Astro on Cloudflare Pages), business docs, sales material, research, and the dormant voice agent. Progress: [`klantkraan/TODO.md`](klantkraan/TODO.md). |
| [`ai-receptionist/`](ai-receptionist/) | The product: text-first receptionist (FastAPI + Claude tool use). One YAML config per client; the Klantkraan demo is `config/klantkraan-demo.yaml`. |
| [`growth-engine/`](growth-engine/) | Content pipeline that markets Klantkraan: Claude drafts → Telegram approval → X auto-post; LinkedIn/Reddit paste-ready. Progress: [`growth-engine/TASK.md`](growth-engine/TASK.md). |
| [`ops/`](ops/) | Hetzner deploy kit (cloud-init, systemd units, Caddy, deploy script) for the two Python apps. |

Operating rules for working in this repo: [`CLAUDE.md`](CLAUDE.md).

## Quick start

```sh
# Product demo (needs ANTHROPIC_API_KEY in ai-receptionist/.env)
cd ai-receptionist && python -m app.server   # web chat on http://127.0.0.1:8000

# Marketing site
cd klantkraan/apps/marketing-site && pnpm dev

# Growth engine selftest
cd growth-engine && python -m src.selftest all
```

Deploys of the marketing site are manual: `pnpm dlx wrangler@4 pages deploy ./dist --branch=production --project-name=klantkraan-marketing` (no Git integration).
