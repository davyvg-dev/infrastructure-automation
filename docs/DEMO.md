# Demoing & pitching the AI receptionist

How to turn this into content and into a close.

## Record a demo clip (for content)

1. Run `python -m app.server` and open <http://127.0.0.1:8000> at phone width (in Chrome
   DevTools device mode, or just narrow the window).
2. Screen-record a natural booking, e.g.:
   - "Hi, do you have anything Thursday afternoon for a cleaning?"
   - "Perfect, 3pm works."
   - "Sam Jansen, 06 12345678."
   - → the bot reads back a confirmation code.
3. Keep it under ~30 seconds. The magic is the *instant, human* replies and the booking
   landing without a person involved.
4. Add one line of context when you post it (the `growth-engine` engine will draft the
   caption): what business it's for, and the pain it removes ("this clinic was missing
   ~15 calls a week").

## Content angles this unlocks

- **Build log:** "Today I taught the receptionist to stop double-booking. Here's the bug."
- **Proof/demo:** the clip above.
- **Teardown:** "A salon that misses 10 calls a week is leaving ~€X on the table. Here's the fix." then show the demo.

## Pitch a prospect (the close)

1. Scaffold their demo in one command, then tweak the details from their website/Google
   profile (2 minutes):
   ```bash
   python -m app.scaffold "Their Business Name" --phone "..." --address "..."
   ```
2. `BUSINESS_CONFIG=config/their-business-name.yaml python -m app.server`, then screen-share
   (or record a Loom over it and send before the call).
3. Let them try to book. Then: "This answers every customer instantly, day or night, and
   books them straight in. Want me to wire it to your real calendar and phone/WhatsApp?"
4. The paid work is the real integration (calendar, their channels, their branding) — the
   demo is what gets you there.

## Turning the demo into a real product (what you'd sell)

The demo simulates the calendar so it runs with zero setup. For a paying client you'd swap:

- **`app/calendar_store.py`** → their real calendar (Google Calendar / Cal.com API). The
  function signatures (`availability`, `book`) stay the same; you replace the bodies.
- **Channel** → today it's a web widget. Add WhatsApp/Telegram/phone by pointing those
  inbound messages at `receptionist.run_turn(...)` and returning its reply.
- **Handoff** → notify the owner (email/SMS) on each booking or when the bot can't help.
- **Persistence** → move `_SESSIONS` in `server.py` from memory to Redis/Postgres.

Price it as a setup fee (build + integrate) plus a monthly (hosting + the AI + tweaks).
