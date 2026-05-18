# Claude — operating rules for this repo

## Project
`/klantkraan/` is the Klantkraan productized-marketing-automation business (Dutch trades). All other folders are unrelated legacy.

## Workflow — Ralph Higgums loop
- Small step → verify → next step. No multi-step leaps.
- Every code change: build, lint, run, eyeball the result, then commit.
- Every doc change: commit per subfolder, surface what changed in chat, wait for user confirmation before moving on.
- If a step fails: stop. Fix root cause. Do not bypass.
- Progress is tracked in `/klantkraan/TODO.md`. Tick boxes as you go.

## Docs source of truth — context7
- Before writing code that uses any external library/SDK (Astro, n8n, Synthflow, CM.com, Mollie, Cloudflare, Hetzner, Attio, Cal.com, ElevenLabs, Resend, Neon, Anthropic SDK, Tally, PandaDoc, SignWell, etc.), fetch current docs via the **context7 MCP**.
- If context7 is not connected, ask the user to enable it. Do not guess from training data.
- Cite the context7-fetched version in the PR / commit message when API surface matters.

## Branch
- All work on `claude/business-marketing-planning-FArXV`.
- Commit messages describe the *why*. Push with `-u origin <branch>`.

## Style
- Dutch in customer-facing artefacts. English in code, internal docs, and CLAUDE.md.
- No emojis in code or commits unless explicitly requested.
- Lean files, no fluff. If a section can be removed without losing meaning, remove it.

## Forbidden
- Cold-call automation (founder constraint).
- HeyGen/Synthesia avatars (Dutch viewers reject).
- Disabling the EU AI Act art. 50 disclosure in the Synthflow agent — ever.
- Cold email to eenmanszaak/VOF without opt-in. BV filter is non-negotiable.

## Pre-launch verification
See `/klantkraan/docs/00-MASTER-PLAN.md § 5`. Items 1–10 require real-world action by the founder.
