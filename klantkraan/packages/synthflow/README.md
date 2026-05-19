# `packages/synthflow` — Synthflow Agent Configs

JSON exports for the Synthflow Dutch AI receptionists. One agent per vertical + version. The rendered system prompt is loaded from `packages/prompts/nl/` at deploy time; this folder owns the metadata, tools, webhooks, compliance flags, and voice config.

## Layout

```
packages/synthflow/
├── README.md            ← this file
└── agents/
    ├── loodgieter.v1.json
    └── dakdekker.v1.json
```

## How to import the JSON into Synthflow

1. Log in to the Synthflow console with the workspace owner account (creds in Bitwarden, item `Synthflow — workspace owner`).
2. Resolve the per-client variables: render `packages/prompts/nl/<vertical>.v1.md` with the mustache placeholders via `client-onboarding.json`. Output is `packages/prompts/nl/<vertical>.<client_id>.rendered.md`.
3. In the Synthflow console: `Agents → New → Import JSON`. Paste the contents of `agents/<vertical>.v1.json`.
4. Replace `"system_prompt": "PLACEHOLDER …"` with the full rendered Markdown (paste as plain text — Synthflow stores it as-is).
5. Replace `"voice_id": "TODO_ELEVENLABS_VOICE_ID"` with the resolved ElevenLabs voice id (`Daan` or `Sanne` — lookup table in `09-brand/voice-and-tone.md`).
6. Replace every `{{...}}` placeholder in the JSON itself (`transfer_phone_number`, `first_message`) with the rendered value — Synthflow does not run mustache server-side.
7. Save the agent. Note the Synthflow `agent_id` returned by the API.
8. Compute SHA-256 of the final rendered Markdown and store it on the client's Neon row (`clients.prompt_hash`, `clients.synthflow_agent_id`).
9. Configure the inbound phone number (CM.com → Synthflow) per `infra/n8n/client-onboarding.json`.
10. Run the 5-call smoke test from `03-delivery/onboarding-30-day.md` day 5.

Automation: in production, steps 2–8 are scripted via the Synthflow REST API (`POST /v1/agents`, `PATCH /v1/agents/{id}`) inside `client-onboarding.json`. This README documents the manual fallback when the API is down or for first-time clients during the pilot phase.

## Where the API tokens live

| Token | Location |
|---|---|
| Synthflow workspace API key       | Bitwarden item `Synthflow — workspace owner`, field `api_key`. |
| Synthflow per-agent webhook secret | Bitwarden item `Synthflow — webhook secret`. Used to verify `call_end` HMAC. |
| ElevenLabs API key                | Bitwarden item `ElevenLabs — workspace owner`. Voice ids in `09-brand/voice-and-tone.md`. |
| Cloudflare Workers env vars       | `wrangler secret put SYNTHFLOW_API_KEY` (project `klantkraan-api`). |
| n8n env vars                      | n8n Docker secret file mounted at `/run/secrets/synthflow_api_key`. |

Never commit any of these values. CI runs `gitleaks` on every push.

## How to roll back to a prior agent version

1. Find the previous version: `git log --oneline -- packages/synthflow/agents/<vertical>.v*.json` (and the matching prompt under `packages/prompts/nl/`).
2. Check out the prior file pair to a worktree (do not mutate `main` history).
3. Render the prior prompt with the **current** client variables (placeholder fills may have evolved).
4. Update the Synthflow agent via the API: `PATCH /v1/agents/{id}` with the prior `system_prompt` + prior `tools` + prior `compliance` block. Keep the same `agent_id` so the phone-number routing is unchanged.
5. Update `clients.prompt_hash` on Neon to the SHA-256 of the rolled-back rendered prompt.
6. Log the rollback in `compliance_audits` with `event_type='rollback'`, the old hash, the new hash, the operator, and a one-line reason.
7. Run one smoke test call to verify the disclosure still plays and the spoed-protocol routes correctly.

Rollbacks are reversible: roll forward by applying the original newer version the same way.

## Deploy hash audit trail

For AI Act Art. 50(5) record-keeping, every change to a deployed agent generates one row in `compliance_audits`:

```
{
  "id":                "ulid",
  "client_id":         "client_xxx",
  "agent_id":          "synthflow_agent_id",
  "event_type":        "deploy" | "rollback" | "update",
  "from_prompt_hash":  "sha256_hex_or_null",
  "to_prompt_hash":    "sha256_hex",
  "from_agent_json":   "<git sha of source JSON>",
  "to_agent_json":     "<git sha of source JSON>",
  "voice_id":          "elevenlabs_voice_id",
  "model":             "claude-sonnet-4-6",
  "operator":          "founder@klantkraan.nl",
  "reason":            "one-line free text",
  "deployed_at":       "ISO 8601 UTC"
}
```

This table is part of the AP audit defense (`04-legal/ai-act-disclosure.md` § What happens if AP audits). Retention: contract duration + 6 months; automated sweep in `infra/n8n/retention-sweep.json`.

## Schema source (note)

Synthflow is not currently indexed in context7 (verified 2026-05-20). The JSON shape in `agents/*.json` is **best-effort**, based on the public docs at `docs.synthflow.ai` and our internal master prompt (`klantkraan/docs/03-delivery/synthflow-system-prompt.md`). Before the first production deploy, the founder verifies the schema against the live Synthflow console export by:

1. Manually creating an agent in the console with the fields we use.
2. Exporting it via `GET /v1/agents/{id}` (or the console "Export JSON" button).
3. Diffing the exported shape against `agents/loodgieter.v1.json` and reconciling field names. Any divergence is committed as `agents/loodgieter.v2.json` with a changelog at the top.

## Source

- AI Act audit trail: `klantkraan/docs/04-legal/ai-act-disclosure.md`
- Prompt source-of-truth: `klantkraan/packages/prompts/`
- Onboarding workflow: `klantkraan/infra/n8n/client-onboarding.json`
- Repo architecture: `klantkraan/docs/08-tech/repo-architecture.md` § packages/prompts
