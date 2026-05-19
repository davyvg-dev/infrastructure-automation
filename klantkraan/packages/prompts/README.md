# `packages/prompts` — Synthflow Dutch System Prompts

Versioned Synthflow agent prompts (Dutch), per vertical, per client overlay. Source of truth for everything the AI receptionist says during a call.

## Layout

```
packages/prompts/
├── README.md                          ← this file
└── nl/
    ├── _template.md                   ← shared skeleton (mustache placeholders)
    ├── loodgieter.v1.md               ← base prompt, loodgieter vertical
    ├── dakdekker.v1.md                ← base prompt, dakdekker vertical
    ├── loodgieter-faq.{client_id}.md  ← generated per client by client-onboarding.json
    └── dakdekker-faq.{client_id}.md   ← generated per client by client-onboarding.json
```

Rendered output (gitignored): `nl/<vertical>.<client_id>.rendered.md`.

## Versioning policy

- **Semver.** Filename carries the major version (`loodgieter.v1.md`, `loodgieter.v2.md`). Minor/patch tracked in commit messages and the `Version notes` line at the bottom of each file.
- **Immutable once shipped.** When a base prompt is used in production for any client, its content is frozen. Changes go in a new file (`.v2.md`). Never mutate `.v1.md` in place. This is required to keep the SHA-256 hash logged with each call honest for AI Act audit (`04-legal/ai-act-disclosure.md`).
- **Hash logged per call.** The Synthflow `call-end` webhook (`apps/api/.../webhook/synthflow/call-end`) writes the prompt hash to the `calls` table alongside audio, transcript, timestamp, model version, and voice id.
- **Disclosure is non-negotiable.** Every version, every vertical, every client overlay must contain the verbatim disclosure block from `04-legal/ai-act-disclosure.md`. CI rejects PRs that drift.

## How to add a new vertical

1. Copy `nl/_template.md` to `nl/<vertical>.v1.md`.
2. Fill in the vertical-specific blocks: identity, allowed actions, forbidden actions, spoed-protocol, tariff terms.
3. Update the `Supported placeholders` table in `_template.md` if the new vertical introduces tariff fields.
4. Add the vertical to `apps/api` intake validation and `infra/n8n/client-onboarding.json` switch node.
5. Add a Synthflow agent JSON in `packages/synthflow/agents/<vertical>.v1.json`.
6. Open a PR. CI runs the disclosure-drift check and prompt-lint.
7. Founder reviews tariff defaults + spoed-protocol with one domain expert before merge.

## How a per-client FAQ overlay is generated

1. Client completes Tally intake form (Q21 = top 10 FAQs with canonical answers).
2. `client-onboarding.json` n8n workflow extracts Q21 chunks.
3. Workflow renders `nl/<vertical>-faq.{client_id}.md` using a Handlebars-style template:

   ```
   ## FAQ
   {{#each faq_chunks}}
   **{{this.question}}**
   {{this.answer}}
   {{/each}}
   ```

4. Founder reviews + approves the rendered FAQ during day-3 onboarding call (30 min).
5. The base prompt `{{faq_overlay}}` placeholder pulls in the overlay at render time.
6. Hash of the combined rendered prompt is logged on first call and on every prompt update.

The FAQ overlay is the only per-client mutation. Anything else (tone, intent logic, spoed-protocol) requires a vertical-wide version bump.

## AI Act audit-trail expectations

For each call, the following must be persisted (see `04-legal/ai-act-disclosure.md` § Record-keeping, Art. 50(5)):

- Audio recording (`call.mp3`) — Cloudflare R2.
- Transcript (`call.txt`) — Cloudflare R2.
- Prompt hash (SHA-256 of the `.rendered.md`) — Neon `calls.prompt_hash`.
- Synthflow model version + ElevenLabs voice id — Neon `calls.model`, `calls.voice_id`.
- Disclosure confirmation log — separate row in `compliance_audits` proving the first 8 seconds of audio contain the disclosure text.
- Timestamp + duration.

Retention: contract duration + 6 months. Automatic deletion job in `infra/n8n/retention-sweep.json`.

## Required placeholders by tier

| Placeholder | Lite | Pro | Max |
|---|---|---|---|
| `{{client_name}}`                          | required | required | required |
| `{{client_id}}`                            | required | required | required |
| `{{client_kvk}}`                           | required | required | required |
| `{{client_vak}}`                           | required | required | required |
| `{{client_regio}}`                         | required | required | required |
| `{{owner_naam}}`                           | required | required | required |
| `{{owner_email}}`                          | required | required | required |
| `{{client_postcode_lijst}}`                | n/a      | required | required |
| `{{escalation_number}}`                    | n/a      | required | required |
| `{{agent_naam}}`                           | n/a      | required | required |
| `{{calcom_eventtype_url}}`                 | n/a      | required | required |
| `{{n8n_webhook_url}}`                      | n/a      | required | required |
| `{{client_voorrijkosten}}` (loodgieter)    | n/a      | optional (default applies) | required |
| `{{client_uurtarief}}` (loodgieter)        | n/a      | optional (default applies) | required |
| `{{client_spoedtoeslag}}` (loodgieter)     | n/a      | optional (default applies) | required |
| `{{client_materiaalopslag}}` (loodgieter)  | n/a      | optional (default applies) | required |
| `{{client_inspectie_tarief}}` (dakdekker)  | n/a      | optional (default applies) | required |
| `{{client_noodreparatie_toeslag}}` (dakdekker) | n/a  | optional (default applies) | required |
| `{{client_dakpannenslag_prijs_indicatief}}` (dakdekker) | n/a | optional (default applies) | required |
| `{{may_quote_prices}}`                     | n/a      | required (default false) | required |
| `{{faq_overlay}}`                          | n/a      | optional | required (FAQ-blok altijd ingevuld) |

(Lite = SMS-only tier, no voice agent — prompts only run for Pro and Max. Listed here so the Lite-to-Pro upgrade flow knows which fields to backfill from Attio.)

## Required placeholders by tier — rationale

- **Lite has no AI agent**, so most placeholders are n/a; only identity fields are kept so a Lite-to-Pro upgrade can render the prompt without a re-intake.
- **Pro tier** runs the full prompt with sensible defaults; founder may finetune tariffs on day 3.
- **Max tier** requires explicit tariff values — these clients pay €999/mo and expect every quote-context phrase to match their actual price card.

## Linting

`pnpm lint:prompts` (added in `package.json`) runs:

1. **Disclosure drift check** — greps every `.md` for the verbatim disclosure line; fails if missing or altered.
2. **Forbidden words** — checks against `09-brand/voice-and-tone.md` § 5 forbidden list.
3. **Placeholder schema** — validates that every `{{...}}` in the prompt is declared in `_template.md`'s table.
4. **Length cap** — each base prompt ≤ 3000 words.

## Source

- AI Act disclosure: `klantkraan/docs/04-legal/ai-act-disclosure.md`
- Voice and tone: `klantkraan/docs/09-brand/voice-and-tone.md`
- Repo architecture: `klantkraan/docs/08-tech/repo-architecture.md`
- Synthflow base prompt source: `klantkraan/docs/03-delivery/synthflow-system-prompt.md`
- Pricing / tariff schema: `klantkraan/docs/01-strategy/offer-and-pricing.md`
