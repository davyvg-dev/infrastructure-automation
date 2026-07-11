# Channels

The receptionist answers on three channels, all sharing one conversation store
(`app/sessions.py`) and one brain (`app/receptionist.py`):

| Channel | How it runs | Public URL needed? |
|---|---|---|
| **Web widget** | `python -m app.server` → http://127.0.0.1:8000 | No |
| **Telegram** | `python -m app.channels.telegram_bot` (polling) | No |
| **WhatsApp** | Twilio webhook → `POST /whatsapp` on the FastAPI server | Yes (Twilio must reach it) |

You can run any subset. The web widget and WhatsApp both live in the FastAPI server; the
Telegram bot is a separate process.

---

## Telegram

1. Create a **second** bot with **@BotFather** (`/newbot`). This is the *receptionist* bot
   — keep it separate from the growth-engine approval bot.
2. Put its token in `.env` as `TELEGRAM_BOT_TOKEN`.
3. Run it:
   ```bash
   python -m app.channels.telegram_bot
   ```
4. Open the bot in Telegram, send `/start` (greeting) then chat normally — try booking an
   appointment. Each Telegram chat is its own conversation.

That's it — no public URL, because it polls Telegram.

---

## WhatsApp (Twilio)

Twilio is the standard, easiest path to WhatsApp. The **sandbox** lets you test for free
without WhatsApp Business approval.

### 1. Start the server (it hosts the webhook)

```bash
python -m app.server        # exposes POST /whatsapp on port 8000
```

### 2. Make it reachable (dev)

Twilio needs a public HTTPS URL. In another terminal:

```bash
ngrok http 8000             # gives you https://<something>.ngrok-free.app
```

### 3. Point Twilio at it

1. In the [Twilio Console](https://console.twilio.com) → **Messaging → Try it out →
   WhatsApp sandbox**.
2. Join the sandbox from your phone (send the `join <code>` message it shows to the Twilio
   number).
3. Set **"When a message comes in"** to:
   `https://<your-ngrok>.ngrok-free.app/whatsapp`  (HTTP POST).
4. (Recommended) Put your **Auth token** from the console into `.env` as
   `TWILIO_AUTH_TOKEN` so incoming webhooks are signature-validated. In dev you can leave
   it blank to skip validation.

### 4. Test

Message the sandbox number from your phone. The receptionist replies over WhatsApp, books
appointments, the works. Each phone number is its own conversation.

> Going live for a real client means a Twilio WhatsApp sender (a business number approved
> by Meta) instead of the sandbox. The code doesn't change — only the Twilio config and the
> `From` number do.

> **Staging vs production:** Telegram and WhatsApp each allow only one active webhook per
> app, and pointing a test setup at your bot overwrites production. Use **separate bot
> tokens / Twilio numbers for staging and production** so testing never hijacks a live
> client's channel.

---

## Adding another channel later

Any messaging platform maps to the same three lines:

```python
from app import sessions
reply = sessions.respond("<channel-name>", "<user-id>", inbound_text)
# then send `reply` back on that platform
```

Instagram DMs, SMS, a website's existing live-chat — all just adapters around
`sessions.respond`.
