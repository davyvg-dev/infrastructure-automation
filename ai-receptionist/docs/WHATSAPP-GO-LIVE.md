# WhatsApp go-live: move the business number from the app to the API

Goal: the Klantkraan WhatsApp number stops living in the WhatsApp Business *app* on the
founder's phone and becomes a Twilio WhatsApp *sender*, so the receptionist answers it,
takeover works from Telegram, and missed calls funnel in. A number lives on ONE surface at
a time — after this move the app no longer works for this number. That is the deal.

Everything below is founder action (console logins, the phone, OTPs). The code side is
done and deployed inert; it activates through `.env` alone.

---

## A. Prerequisites (blockers first)

- [ ] **Meta Business Manager** for Klantkraan with **business verification completed**.
      Needs the KvK extract and matching business details. Without this there is no
      production sender and no approved templates — it gates everything else.
      Start at business.facebook.com → Settings → Business verification.
- [ ] Twilio account upgraded (not trial), with the console login at hand.
- [ ] Decide chat-history fate: moving to the API abandons the app's chat history.
      Export anything worth keeping first (app → chat → Export chat).

## B. Create the WhatsApp sender in Twilio

1. - [ ] Twilio Console → **Messaging → Senders → WhatsApp senders → Create new sender**.
2. - [ ] Link the Meta Business Manager from step A when prompted (embedded signup).
3. - [ ] Enter the business number. **Before verifying:** delete the WhatsApp account in
         the app on the phone (WhatsApp Business app → Instellingen → Account → Account
         verwijderen). Registration fails while the number is still active in the app.
4. - [ ] Verify ownership via the SMS/voice code sent to the number.
5. - [ ] Fill the WhatsApp profile: display name **Klantkraan**, logo, the profile
         description, address, e-mail, website klantkraan.nl. (Meta reviews the display
         name against the verified business.)
6. - [ ] Set the sender's inbound webhook: `https://demo.klantkraan.nl/whatsapp`
         (HTTP POST).

## C. Server config (`.env` on the ops server)

- [ ] `TWILIO_ACCOUNT_SID=AC…` (console home)
- [ ] `TWILIO_AUTH_TOKEN=…` (should already be set for the sandbox; confirm)
- [ ] `TWILIO_WHATSAPP_FROM=whatsapp:+31…` (the moved number)
- [ ] `OWNER_TELEGRAM_CHAT_ID` set (it already is if Telegram lead alerts arrive) — this
      is what turns the takeover poller on.
- [ ] `systemctl restart ai-receptionist`, then check
      `journalctl -u ai-receptionist | grep takeover` for "takeover poller running".
- [ ] Send the number a WhatsApp message from another phone: the receptionist must answer.
- [ ] In Telegram, send the notify bot `wa` — the test conversation must be listed. Try
      `takeover 1`, answer, `release`.

## D. Templates (unblocks production missed-call delivery)

- [ ] Submit all six templates from `whatsapp-templates.md` (§3 checklist) via Twilio
      **Content Template Builder**, category *utility*, language `nl`.
- [ ] Record every returned Content SID; put the `gemiste_oproep_nl` SID in `.env` as
      `WHATSAPP_MISSED_CALL_CONTENT_SID` and restart.

## E. Missed-call funnel

1. - [ ] Buy a Twilio **voice** number. A Dutch +31 number needs a regulatory bundle
         (KvK + address, reviewed in days); a non-NL number also works since callers never
         dial it directly — it only receives forwarded calls.
2. - [ ] Set the number's voice webhook: `https://demo.klantkraan.nl/voice/missed`
         (HTTP POST).
3. - [ ] On the business phone, enable **conditional** call forwarding to that number
         (never unconditional — you still want to pick up when you can):
         - bij geen antwoord: dial `**61*<twilio-nummer>#`
         - bij bezet: `**67*<twilio-nummer>#`
         - bij onbereikbaar: `**62*<twilio-nummer>#`
         (GSM codes; work on KPN/Odido/Vodafone. iPhone: also visible under Instellingen →
         Telefoon → Doorschakelen for the unconditional variant only — use the codes.)
4. - [ ] Test: call the business number from another phone, don't pick up. Expect the
         Dutch spoken message, then a WhatsApp message on the calling phone, then a
         Telegram alert. Reply to the WhatsApp — the receptionist should take it.
5. - [ ] Test the failure path: call from a landline. Expect a Telegram alert saying the
         WhatsApp could not be delivered and this caller needs a callback.

## F. Aftercare

- [ ] Delete the sandbox webhook config so nothing stale points at the server.
- [ ] Add the monthly template-category audit (whatsapp-templates.md §1) to the ops pass.
- [ ] Costs to expect: Twilio number ~€1–6/mo, voice minutes on forwarded calls, WhatsApp
      utility conversations (< $0.03 each in NL), and from 1 Oct 2026 Meta also bills
      service conversations.

## Rollback

The move is reversible but lossy: deregister the sender in Twilio, then re-register the
number in the WhatsApp Business app (new OTP). API-era history stays in `data/` analytics;
the app starts empty.
