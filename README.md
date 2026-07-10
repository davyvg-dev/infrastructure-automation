# AI Receptionist (demo)

A working demo of the product you sell: a Claude-powered assistant that answers a
business's customers, qualifies them, and books appointments — 24/7, instantly.

It's a small web chat widget. The whole thing is driven by **one config file**
(`config/business.yaml`), so you can rebrand it for any prospect in a couple of minutes and
show them a live demo of *their* receptionist.

```
customer ──▶ chat widget (web) ──▶ FastAPI ──▶ Claude (tool use)
                                                   │
                                       ┌───────────┴───────────┐
                                 check_availability      book_appointment
                                       └──────── calendar store ┘
```

## Why this exists

- **Sell with it.** Spin up a branded demo for a prospect, screen-share it, close.
- **Post about it.** Every build step is build-in-public content (the `growth-engine/`
  project turns these into posts).
- **Ship it.** The `calendar_store.py` seam is where a real Google Calendar / Cal.com
  integration slots in for a paying client.

## Quick start

```bash
cd ai-receptionist
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # add your ANTHROPIC_API_KEY

# test the pieces before the web UI (see TASK.md):
python -m app.selftest config      # config, no network
python -m app.selftest calendar    # slot generation + booking, no network
python -m app.selftest agent       # a scripted booking conversation (needs API key)
python -m app.selftest chat        # interactive terminal chat

# run the web demo:
python -m app.server               # then open http://127.0.0.1:8000
```

## Channels

The same receptionist answers on three channels, all sharing one conversation store
(`app/sessions.py`):

| Channel | Run it with | Public URL? |
|---|---|---|
| Web widget | `python -m app.server` | No |
| Telegram | `python -m app.channels.telegram_bot` | No |
| WhatsApp (Twilio) | webhook on the server: `POST /whatsapp` | Yes (ngrok in dev) |

Run any subset. Full setup — creating the Telegram bot and wiring the Twilio WhatsApp
sandbox — is in **`docs/CHANNELS.md`**.

## Rebrand for a prospect

1. Copy `config/business.yaml` to `config/<prospect>.yaml`.
2. Edit the business name, services, hours, FAQ, and persona.
3. Set `BUSINESS_CONFIG=config/<prospect>.yaml` in `.env`.
4. Restart the server — the widget and the receptionist are now *their* business.

No code changes. That's the whole pitch: "here's what this looks like for you."

## Layout

```
ai-receptionist/
├── README.md
├── TASK.md                  # gated build/test checklist
├── requirements.txt
├── .env.example
├── config/
│   └── business.yaml        # ← the only file you edit to rebrand
├── app/
│   ├── settings.py          # config + env
│   ├── calendar_store.py    # simulated calendar (the real-integration seam)
│   ├── tools.py             # check_availability + book_appointment
│   ├── receptionist.py      # Claude tool-use loop + persona
│   ├── sessions.py          # shared conversation store (all channels)
│   ├── server.py            # FastAPI: web widget + WhatsApp webhook
│   ├── channels/
│   │   ├── telegram_bot.py  # Telegram polling bot
│   │   └── whatsapp.py      # Twilio WhatsApp webhook handler
│   └── selftest.py          # isolated checks + terminal chat
├── web/
│   └── index.html           # self-contained, theme-aware chat widget
└── docs/
    ├── DEMO.md              # how to run, film, and pitch it
    └── CHANNELS.md          # Telegram + WhatsApp setup
```

See `docs/DEMO.md` for how to record a demo clip and pitch it, and `TASK.md` to build it up
one tested step at a time.
