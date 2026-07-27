# Contributing

Onboarding for developers working on this repo. It's the human companion to two other files:

- [`README.md`](README.md) — what the parts are, in one table.
- [`CLAUDE.md`](CLAUDE.md) — the operating rules (written for the AI agent, but the
  architectural guardrails apply to everyone; the [Non-negotiables](#non-negotiables) below
  are lifted from it).

Read this once before your first change. It gets you set up, tells you how to run and test the
two Python apps, and explains the conventions a PR is expected to follow.

## The one rule that explains the codebase

**Config over code.** Both Python apps are driven by YAML, and the YAML is the source of truth
for *what the app says and does* — offer, prices, hours, persona, voice, cadence, platforms.
You touch `.py` files for *how* it works, never for *what* it says.

- `ai-receptionist/` — one config per client. `config/<business>.yaml`; `BUSINESS_CONFIG` in
  `.env` selects it. Rebranding the receptionist for a new prospect is a new YAML file and
  **zero code**.
- `growth-engine/` — `config/content_strategy.yaml` is the single source of truth for offer,
  voice, pillars, platforms, cadence, and model.

If you find yourself hard-coding a business name, a price, or a piece of copy in Python, stop —
it belongs in config. This is the discipline the whole repo is built on; keep it.

## Repo layout

Two Python apps you'll actually run, plus supporting folders:

| Path | What it is | Progress file |
|---|---|---|
| `ai-receptionist/` | The product: text-first receptionist (FastAPI + Claude tool use). | `TASK.md` |
| `growth-engine/` | Content pipeline (Claude drafts → Telegram approval → X auto-post). | `TASK.md` |
| `klantkraan/` | Marketing site (Astro on Cloudflare Pages), sales docs, research. | `TODO.md` |
| `ops/` | Hetzner deploy kit (cloud-init, systemd, Caddy, deploy script). | — |

Everything else at the top level is unrelated legacy — ignore it.

## Prerequisites

- **Python 3.11+** (CI runs 3.12; `ruff`'s `target-version` is `py311`, the floor).
- **git**, and the `gh` CLI if you'll open PRs from the terminal.
- Node + **pnpm** only if you touch the marketing site (`klantkraan/apps/marketing-site`).
- An **`ANTHROPIC_API_KEY`** to run anything that actually calls Claude. Offline tests need none.

## Setup

Each Python app has its own virtualenv, requirements, and `.env`. They don't share state — set
up whichever you're working on.

```sh
cd ai-receptionist                       # or: cd growth-engine
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt      # requirements.txt + pytest + ruff (pinned)
cp .env.example .env                      # then fill in the secrets you need
```

`requirements-dev.txt` layers the test tooling on top of `requirements.txt`, so it's the only
install you need for development. **`ruff` is pinned to `0.16.0`** — formatter output is
version-sensitive, so local and CI must match. Don't bump it in one place without the others
(`requirements-dev.txt` in both apps + `.github/workflows/ci.yml`).

## Running locally

```sh
# ai-receptionist — web chat widget on http://127.0.0.1:8000 (needs ANTHROPIC_API_KEY)
cd ai-receptionist && python -m app.server

# growth-engine — ALWAYS dry-run in development so it never posts to a live platform
cd growth-engine && GROWTH_ENGINE_DRY_RUN=1 python -m src.run
```

> The growth engine posts to X via API. **Never run the bot without `GROWTH_ENGINE_DRY_RUN=1`
> during development.** There is no "oops" on a live social account.

## Testing

Two complementary layers. Know which one you're using and why:

### 1. `pytest` — the offline suite (this is what CI gates on)

Fast, hermetic, no network, no API key. Every test runs against throwaway temp dirs, so it
never touches the real `data/` store or the committed client configs. This is the suite you run
constantly and the one that must be green before you push.

```sh
cd ai-receptionist && source .venv/bin/activate
python -m pytest                 # ~0.4s, fully offline

# growth-engine has no pytest suite yet; CI compile-checks it and runs two offline selftests:
cd growth-engine
python -m src.selftest config
python -m src.selftest platforms
```

### 2. `selftest` — the CLI smoke-tester (some layers cost money)

`app/selftest.py` (receptionist) and `src/selftest.py` (growth-engine) are hand-run checks that
walk each layer in order. Some are offline and overlap with pytest; others make **real, paid
Claude calls** or need live credentials, which is exactly why they're *not* in CI. Use them to
sanity-check a live integration or debug interactively.

```sh
# receptionist — offline layers (no key): config routing calendar intake analytics digest insights pipeline
python -m app.selftest config
python -m app.selftest calendar
# live layers (cost money / need creds): agent, analyst, scope, chat
python -m app.selftest agent     # a scripted booking conversation — needs ANTHROPIC_API_KEY
python -m app.selftest chat      # interactive terminal chat

# growth-engine — telegram / x / meta / tiktok need live creds; run individually
python -m src.selftest all       # runs the full ladder in order, stops at the first failure
```

**When you add a feature, add an offline pytest for it** (see `ai-receptionist/tests/` for the
pattern — one focused file per concern, temp-dir fixtures in `conftest.py`). The offline
`selftest` layers were ported into pytest precisely so CI can cover them; keep that going.

## Lint and format

`ruff` handles both. Run these before every push — CI runs the exact same commands and will fail
the build otherwise:

```sh
ruff check   ai-receptionist/app ai-receptionist/tests   # lint
ruff format  ai-receptionist/app ai-receptionist/tests   # auto-format (drop --check to fix)
# same two commands for growth-engine/src
```

Config lives in each app's `pyproject.toml`: line length 100, rules `E/F/W/I/UP/B`, `E501`
ignored (the formatter owns line wrapping, so a few unavoidably long comments/strings are fine).
Formatting is full Black-style (double quotes) — let `ruff format` decide; don't fight it.

## Continuous integration

`.github/workflows/ci.yml` runs on every push and PR. It is **secret-free and needs no network** —
if it's red, a real problem exists. Three jobs:

| Job | What it does |
|---|---|
| `lint` | `ruff check` + `ruff format --check` on both apps. |
| `receptionist` | `py_compile` every module, then `python -m pytest`. |
| `growth-engine` | `py_compile` every module, then offline `selftest config` + `platforms` (with `GROWTH_ENGINE_DRY_RUN=1`). |

Green CI is the bar for merging. If CI catches something your local run didn't, note that CI has
no `.env`, so the receptionist runs against the tracked `config/business.yaml`, not your local
`BUSINESS_CONFIG`.

## Branching, commits, and PRs

- **`master`** is the main branch. Cut a feature branch off it, one branch per change, and open a
  PR back into `master`. (`claude/…` is the AI agent's own long-lived working branch — leave it
  to Claude; don't base your work on it.)
- **Commit messages describe the *why*,** not just the what. A future reader should learn the
  reason from `git log` without opening the diff.
- **No emojis** in code or commit messages.
- **Small steps.** Build → lint → run → eyeball the result → commit. Don't stack many unverified
  changes into one commit; if a step fails, fix the root cause rather than working around it.
- Before opening a PR: `ruff check` + `ruff format --check` clean, `pytest` green, and you've
  actually run the affected flow once.

## Secrets and config files

- Secrets live in each app's `.env`, which is **gitignored** — as is `data/`. Never commit either.
- **Add every new secret to that app's `.env.example`** (with a placeholder, not a real value) so
  the next person knows it exists.
- Client/business YAML under `config/` *is* committed — it's product configuration, not secrets.
  Keep real customer PII out of it.

## Language convention

- **Dutch** in anything a customer sees — receptionist replies, the marketing site, social posts
  the growth engine drafts.
- **English** in code, internal docs (including this file), and commit messages.
- Never put the founder's personal name in a customer-facing artefact — use "de oprichter" or
  "Klantkraan".

## Non-negotiables

These are correctness and legal constraints, not style. They're enforced in prompts and code
today; a change that removes one is a regression, not a simplification. Full list in
[`CLAUDE.md`](CLAUDE.md) — the ones most likely to bite:

- **EU AI Act art. 50 disclosure.** Every receptionist config discloses it's a digital assistant
  in its greeting. Never remove it, in any config or demo.
- **The receptionist only offers slots `check_availability` returned** — never invented times,
  prices, or advice. Enforced in the system prompt; keep it there.
- **`calendar_store.py` is the integration seam.** To wire a client's real calendar, swap the
  *bodies* of `availability()` / `book()`, never the signatures.
- **No auto-posting to LinkedIn or Reddit.** Their ToS forbid it. The growth engine drafts for
  those platforms; a human pastes. X is the only API auto-post.
- **One module, one job.** Both apps keep sharply separated modules (`settings` / `store` /
  `generate` / … ). Don't merge responsibilities to save a file.
- **Errors surface, they don't get swallowed.** Report failures to the user (Telegram or
  selftest output). The only allowed swallow is keeping a scheduled loop alive *after* reporting.

## External library docs

When you write code against an external SDK or API (Anthropic, FastAPI, Twilio, Cloudflare,
tweepy, python-telegram-bot, …), check the current docs rather than relying on memory — these
move fast. The repo's convention is to fetch versioned docs via context7 (see `CLAUDE.md`).
