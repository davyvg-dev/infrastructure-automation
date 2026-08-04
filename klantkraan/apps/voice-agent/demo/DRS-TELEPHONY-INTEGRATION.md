# Slotenmaker DRS — wiring the ElevenLabs agent into Vialer/Verbonden

Researched 2026-08-04 (two web-research agents, sources in the reports; key claims
verified against wiki.voipgrid.nl, help.voys.nl/help.verbonden.nl, elevenlabs.io/docs).
DRS answers ~1,700 calls/mo on the Vialer app; provider is Verbonden.nl, a white-label
of the VoIPGRID platform (rebranded Voys Partners 2025). Goal: the agent as an
overflow step in their existing belplan — nothing replaced, one dial-plan rule.

## The shape that works with stock features

VoIPGRID belplans are top-down step lists; every step has a **beltijd** (ring seconds)
and falls through to the next step on no-answer. The insert, done in mijn.verbonden.nl:

1. Step 1 (existing): **Openingstijden** — closed branch also points at the agent's number.
2. Step 2 (existing): **Belgroep** rings the locksmiths' Vialer apps, beltijd 20–25 s.
3. Step 3 (new): **Vaste Bestemming** = the agent's Dutch phone number, with
   nummerweergave = **"Oorspronkelijke Beller"**.

That last dropdown is the whole caller-id story: the forwarded leg then presents the
ORIGINAL caller's number, so `{{system__caller_id}}` and the agent's confirm-the-number
flow keep working. The alternatives ("Oorspronkelijk Gebelde Nummer" / privacy) would
show DRS's own number and break it. Verify with one real test call before go-live —
carrier CLI delivery is standard practice but not guaranteed end-to-end.

Trap: if the external step has a keypress-confirm option enabled (used to defeat
mobile voicemail), the AI can never press a key — it must be OFF on the agent step.

## How the call reaches ElevenLabs: a number, not a SIP URI

Verbonden's dashboard forwards to phone numbers only; an arbitrary external SIP URI is
not a documented destination. ElevenLabs' native SIP trunk (`sip.rtc.elevenlabs.io`,
TLS 5061, digest auth, G.711/722) would remove the middleman, but reaching it needs a
platform-side VoIP trunk that Verbonden would have to provision — possible, unverified,
not worth blocking the pilot on. So:

- **Pilot route: Twilio NL number imported into ElevenLabs** (Phone Numbers tab →
  Twilio SID + auth token; ElevenLabs rewrites the voice webhook itself, then assign
  the agent). Twilio account already verified on the ops server; the NL number still
  needs the regulatory bundle: KvK excerpt + NL address (prefix-local for geographic
  numbers) + VAT number. A Dutch 06 needs no paperwork but forwards at mobile rates
  and looks odd — prefer 085 or geographic.
- **Later: ask Verbonden about a trunk to an external SIP host.** If they can point
  one at ElevenLabs' SIP ingress, Twilio drops out entirely (no number rental, no
  bundle, only agent minutes billed).

Twilio-native also buys one feature SIP doesn't have: **warm transfer with a spoken
briefing** (`transfer_to_number` agent_message is Twilio-only; SIP gets conference or
REFER transfer, no briefing). Relevant if DRS wants "put me through" instead of
callback later.

## Go-live item: dynamic variables on phone calls

The agent errors without its custom variables (placeholders are dashboard-test values
only — proven on the widget). The widget supplies them via its attribute; a phone call
cannot. Two fixes, pick one before the first live call:

- **Simplest (single tenant): bake the DRS values into the agent config** — inline
  business_name/service_area/price_from/regio_team/callback_window in the prompt, or
  a DRS-dedicated agent.
- **Scalable: conversation-initiation webhook** — ElevenLabs POSTs
  `caller_id`/`called_number`/`agent_id` to our server pre-pickup; the response sets
  dynamic_variables (and may override prompt/first message per call). Enable in
  Settings + the agent's Security tab. Documented for Twilio inbound; this becomes the
  multi-client seam when more voice clients arrive.

## Money (DRS side + ours)

- Forwarded leg: billed to DRS as a normal outbound call — €0.0354/min fixed/085
  (+€0.04 start), €0.1046/min mobile. Overflow-only at their volume ≈ €35–50/mo.
  State this in the proposal so it never surfaces as a surprise.
- Verbonden modules: Vast/Mobiel forwarding is free; Openingstijden €23 + €6/mo if
  not already active; their Webhook module (€115 + €29.50/mo) exists for dynamic
  routing later — not needed for the pilot.
- ElevenLabs: no telephony surcharge (telephony "at cost"), $0.08/min agent overage,
  burst = $0.16/min so keep burst OFF. Pro $99/mo = 1,238 min, concurrency 20 —
  fits the overflow pilot inside the €499 Compleet tier math.
- Twilio: number rental + inbound minutes on our account, cents-range.

## Pitch line (unchanged, now verified)

"U vervangt niets. Eén regel in uw belplan erbij: neemt uw team niet op binnen
twintig seconden, dan neemt onze assistent aan — en uw slotenmaker belt binnen een
kwartier terug met alle gegevens al genoteerd." Every claim above is a stock
mijn.verbonden.nl feature.

## Pilot checklist

- [ ] Founder: upgrade ElevenLabs tier (quota exhausted; Creator for demos, Pro for pilot).
- [ ] Twilio NL regulatory bundle (KvK + address + VAT) → buy 085/geographic number.
- [ ] Import number into ElevenLabs, assign agent, burst OFF.
- [ ] Fix dynamic variables for phone calls (bake in DRS values or initiation webhook).
- [ ] DRS (or founder screen-share): belplan step 3 Vaste Bestemming + beltijd 20–25 s
      + nummerweergave "Oorspronkelijke Beller"; keypress-confirm OFF; openingstijden
      closed branch → same number.
- [ ] One test call through the full chain: check CLI passthrough shows the caller's
      number, agent confirms it, lead lands in data collection.
- [ ] Confirm forwarded-leg billing with Verbonden (inside "onbeperkt" bundle or not).
