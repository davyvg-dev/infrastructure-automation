# `kk-voice-agent` — self-hosted Dutch AI receptionist

Replaces Synthflow with a stack we own: same Dutch prompt, same tools, same
art. 50 disclosure, same `call-end` webhook — but no proprietary console and no
per-minute platform margin. Built on **LiveKit Agents (Python)**.

## Why Python (not Node)

The repo is TypeScript, so Node was the first instinct. But verified against the
live npm registry (2026-06): **there is no `@livekit/agents-plugin-anthropic` for
Node** — the Node LLM plugins are openai/google/mistral/xai/etc. Our stack
mandates Claude (`docs/08-tech/stack-decisions.md`). The **Python** SDK has a
native Anthropic plugin (`livekit-plugins-anthropic`). Since this is a
standalone real-time service on the Hetzner box — separate from the TS
web/API/Workers — running it in Python costs us nothing in repo cohesion.

## Why this exists

Decision (2026-06): move off Synthflow to "own the stack." Justified by the
*control* motive only — see `stack-decisions.md` re-evaluation triggers. Cost is
**not** the reason: a Dutch call's price is dominated by ElevenLabs TTS, which we
keep either way.

## Architecture

| Layer | Choice | Notes |
|---|---|---|
| Framework | LiveKit Agents (Python) | Native Claude plugin; fullest real-time ecosystem |
| Media / SFU | LiveKit Cloud free tier → self-host on Hetzner later | Own the agent + data now; own the SFU when it pays off |
| STT | Deepgram `nova-2` (`language="nl"`) | Swap to self-host Whisper if we want zero external STT |
| LLM | Anthropic `claude-sonnet-4-6` | `livekit-plugins-anthropic` |
| TTS | ElevenLabs `eleven_multilingual_v2` | The Dutch-quality moat — unchanged from the Synthflow plan |
| Telephony | SIP trunk (Twilio) → LiveKit SIP | Inbound NL number rings the agent |
| Runtime | Python worker on the shared Hetzner box | Long-lived process; sits beside n8n |
| Fallback | CM.com conditional-forward to owner | If the agent is down, the phone still gets answered |

## How it maps to the existing repo (nothing is reinvented)

- **Prompt** — source of truth stays `packages/prompts/nl/<vertical>.v1.md`,
  rendered per client and passed in as `instructions`. No second copy lives here.
- **Tools** — `schedule_callback` / `transfer_emergency` / `lookup_tariff` mirror
  `packages/synthflow/agents/<vertical>.v1.json`.
- **Disclosure** — verbatim from `docs/04-legal/ai-act-disclosure.md`, spoken via
  `session.say()` (exact text), never paraphrased. See `disclosure.py`.
- **Webhook** — call-end summary keeps the same JSON shape; route moves from
  `/api/webhook/synthflow/call-end` to `/api/voice/call-end` (ours).
- **Compliance** — `compliance_audits` rows still logged per deploy/call.

## Layout

```
apps/voice-agent/
├── pyproject.toml
├── .env.example
└── src/kk_voice_agent/
    ├── disclosure.py   # verbatim art. 50 text + drift note
    ├── config.py       # ClientConfig / TariffConfig
    ├── prompt.py       # dev-only mustache fill (prod render = n8n flow)
    ├── agent.py        # KlantkraanReceptionist: 3 tools + on_enter disclosure
    └── main.py         # worker entrypoint (cli.run_app)
```

## Phased plan

- [x] **P1 — Agent brain**: `agent.py`, `disclosure.py`, scaffold.
- [x] **P2 — Runtime + session**: `main.py` entrypoint, `AgentSession` wiring
      STT/LLM/TTS/VAD, deps pinned, imports verified.
- [ ] **P2b — Live playground (needs founder)**: LiveKit Cloud project creds +
      Deepgram/ElevenLabs/Anthropic keys + the resolved Dutch `voice_id`, then
      talk to the agent in the playground.
- [ ] **P3 — Telephony**: SIP trunk → LiveKit SIP inbound; real Dutch number
      rings the agent; spoed `transfer_emergency` does a real SIP transfer.
- [ ] **P4 — Integration**: `/api/voice/*` routes in `apps/api`, call-end
      webhook, `compliance_audits` logging, disclosure-drift CI check, per-number
      client resolution (replaces `_demo_client`).
- [ ] **P5 — Deploy**: Hetzner service + healthcheck + CM.com forward-to-owner
      fallback; 5-call smoke test (`docs/03-delivery/onboarding-30-day.md` day 5).

## Run (after filling .env)

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env          # fill from Bitwarden + LiveKit Cloud
python -m kk_voice_agent.main download-files   # one-time: silero VAD weights
python -m kk_voice_agent.main dev              # joins the LiveKit playground
```

## Status

P2 complete: code wired, deps pinned, imports verified. **Not yet talking** —
P2b needs the LiveKit Cloud project + the three model API keys + the Dutch
`voice_id` (still `TODO_DUTCH_VOICE_ID` in `main.py`, pending the voice test).
