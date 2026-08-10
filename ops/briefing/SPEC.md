# Daily ops briefing agent — spec

One read-only agent, one message a day. Cron (launchd) runs a headless `claude -p`
over local business signals and posts a single summary to the founder's Telegram.
No dashboard, no inbox to check — the day's state comes to the founder.

## The four zones

| Zone | This agent |
|---|---|
| **Trigger** | launchd, daily 08:30 (`com.klantkraan.briefing.plist`). One-shot; no state carried between runs, so "never process a message twice" is moot — every run re-reads the last 24h and today's boards. |
| **Context** | `fetch_signals.py` — read-only collectors: (a) last 24h of Gmail INBOX via IMAP (headers + body preview, DSN/bounce detection, live-deal flagging for slotenmakerdrs.nl and jiromorgan17@gmail.com); (b) `app.pipeline board` + `scripts/sequence.py board` from ai-receptionist; (c) recent voice calls via `calls.py list`. One consolidated plain-text dump on stdout. |
| **Tools** | None. `claude -p` runs with `--tools ""` — the model only summarizes the piped signals dump. It cannot read files, run commands, or send anything. |
| **Output** | One Telegram message via the Bot API (`sendMessage`), posted by `agent.sh` with curl — never by the model. Truncated to fit Telegram's 4096-char limit. |

## Hard safety clauses

1. **Read-only, everywhere.** IMAP is opened with `select("INBOX", readonly=True)`
   and `BODY.PEEK[]` — no flags set, nothing marked read. The board commands are
   print-only views. The outreach ledger (`sequence.py`) has legal consent
   semantics (Telecommunicatiewet art. 11.7 opt-out records) and is NEVER
   written by this agent. No customer data is touched beyond reading.
2. **Never sends email, never replies.** The only outbound action in the whole
   chain is one Telegram `sendMessage` from `agent.sh`. The prompt instructs the
   model to flag replies, not draft them.
3. **Single allowed chat.** `agent.sh` refuses to run without `TELEGRAM_CHAT_ID`
   set, and posts only to that one id. There is no message routing, no group
   logic, no reply handling — the bot is used as a one-way pipe.
4. **No tools for the model.** `--tools ""` (verified against `claude --help`)
   disables every built-in tool; `--no-session-persistence` keeps the run
   stateless.
5. **Fail loudly.** A collector that is *configured but broken* marks its
   section `FAILED`, and `fetch_signals.py` exits nonzero; `agent.sh` prefixes
   the briefing with a collector-failure warning and itself exits nonzero, so a
   silently degraded briefing cannot masquerade as a healthy one. A collector
   that is simply *not configured yet* (e.g. IMAP creds unset) is a `SKIPPED`,
   not a failure — the run still emits every other section.

## Environment

Sourced by `agent.sh` from `~/.klantkraan-briefing.env` (outside the repo, chmod 600):

| Var | Meaning |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Bot token — reuse the existing growth-engine/receptionist bot (same var name there). |
| `TELEGRAM_CHAT_ID` | The founder's personal chat id. Required to post; `--dry-run` works without it. |
| `IMAP_USER` | Mailbox where outreach replies land (davy@klantkraan.nl). |
| `IMAP_APP_PASSWORD` | Google app password (needs 2FA on the account). |
| `IMAP_HOST` | Optional, default `imap.gmail.com`. |

## Cost / subscription note

Running `claude -p` on the founder's Max subscription is acceptable **for
internal founder tooling only** — one short Sonnet summarization per day. The
customer-facing product (receptionist, voice agent) stays on the API. Do not
point client-serving workloads at the subscription.

## Files

- `fetch_signals.py` — collectors, Python 3 stdlib only.
- `briefing_prompt.md` — the system-prompt addition for `claude -p`.
- `agent.sh` — glue: fetch → summarize → post (or `--dry-run` to print).
- `com.klantkraan.briefing.plist` — launchd template, NOT loaded by default.
- `README.md` — founder setup steps.
