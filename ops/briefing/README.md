# Daily ops briefing — founder setup

Every morning 08:30 one Telegram message: replies/bounces that need action
today, outreach touches due, pipeline movement, call-log anomalies. Read-only;
it never sends mail, never replies, never touches the outreach ledger.
Design + safety clauses: `SPEC.md`.

## 1. Telegram (5 min)

Simplest: **reuse the existing bot** (the growth-engine/receptionist bot — same
`TELEGRAM_BOT_TOKEN` you already have on the ops server). No new bot needed;
the briefing just needs your personal chat id.

1. Send the bot any message from your own Telegram account (once).
2. Print your chat id:

   ```sh
   cd ai-receptionist
   TELEGRAM_BOT_TOKEN=<token> ./.venv/bin/python -m app.notify chatid
   ```

   It prints `OWNER_TELEGRAM_CHAT_ID=<nummer>` — that number is your
   `TELEGRAM_CHAT_ID`.

Prefer a separate bot instead? @BotFather → `/newbot` → copy the token, then
do the two steps above with the new token.

## 2. Gmail app password (5 min)

For the mailbox where outreach replies land (davy@klantkraan.nl):

1. Google Account → Security → 2-Step Verification (must be on).
2. Security → App passwords → create one named `klantkraan-briefing`.
3. That 16-character string is `IMAP_APP_PASSWORD`; `IMAP_USER` is the address.

The agent logs in read-only (`readonly=True` + `BODY.PEEK`) — nothing gets
marked as read.

## 3. Env file (NOT in the repo)

```sh
cat > ~/.klantkraan-briefing.env <<'EOF'
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
IMAP_USER=davy@klantkraan.nl
IMAP_APP_PASSWORD=...
# IMAP_HOST=imap.gmail.com   # default, alleen zetten als het afwijkt
EOF
chmod 600 ~/.klantkraan-briefing.env
```

`agent.sh` sources this file itself; launchd never sees the secrets.

## 4. Test

```sh
ops/briefing/agent.sh --dry-run
```

Prints the briefing instead of posting. Works without any creds (email section
says SKIPPED); with creds it shows exactly what Telegram would receive. The
signals dump alone: `python3 ops/briefing/fetch_signals.py`.

Then one real post: `ops/briefing/agent.sh` — check your Telegram.

## 5. Turn on the schedule

```sh
cp ops/briefing/com.klantkraan.briefing.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.klantkraan.briefing.plist
launchctl start com.klantkraan.briefing   # optioneel: nu meteen één run
```

Log: `~/Library/Logs/klantkraan-briefing.log`. Off:
`launchctl unload ~/Library/LaunchAgents/com.klantkraan.briefing.plist`.

## Notes

- Runs on the Max subscription (`claude -p`, model sonnet) — fine for internal
  founder tooling; the customer-facing product stays on the API (see SPEC.md).
- The voice-call section reads the ElevenLabs log via
  `klantkraan/apps/voice-agent/demo/calls.py`; it uses the creds already in
  that app's `.env` — nothing extra to configure.
- A broken signal source makes the run exit nonzero and prefixes the briefing
  with a warning — a thin briefing never pretends to be a healthy one.
