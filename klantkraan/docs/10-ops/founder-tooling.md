# Founder Tooling

> This document is the founder's **personal operating layer** on top of the Klantkraan business stack (`08-tech/stack-decisions.md`). It is not the business stack — it specifies the laptop, browser profiles, password vaults, daily/weekly cadence, communication SLAs, focus rules, and mobile setup that one human uses to run a 22-client / €10k-MRR business solo from M1 to M5. The constraint that drives every choice here: sole operator until M6, so total tool count must stay low and context-switching cost near zero. Everything that does not survive the "could I do this with one less tab" test is rejected.

## 1. Hardware

| Item                      | Pick                                                   | Notes                                                                                                                                                                        |
| ------------------------- | ------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Primary laptop            | MacBook Air M-series (use what you have)               | Do **not** buy new in M1–M3. 8 GB RAM survives Astro + n8n SSH + Claude Code + 7 tabs. Upgrade only if compile/test time exceeds 30s on the monorepo.                        |
| Headset                   | Wired USB-C headset (Jabra Evolve 20 / Logitech H570e) | Predictable mic, predictable battery (none). AirPods drop on Synthflow test calls and skew Dutch voice testing. Wired = zero ambiguity when QA'ing a Dutch agent.            |
| Mobile primary            | Personal NL SIM on +316                                | Stays on the founder's existing carrier; this is the _founder_ number, never published.                                                                                      |
| Mobile secondary          | eSIM (KPN Prepaid or Lebara) for demo handover testing | When test-driving a client's carrier-forwarding (`03-delivery/onboarding-30-day.md`), test against your own second line, not your personal one. €10 prepaid is enough.       |
| Backup laptop             | None until M3                                          | Risk note: if the MacBook bricks pre-M3, recovery is ~24h via Apple Store walk-in + Time Machine restore. Document the laptop SSH keys on YubiKey, not on laptop-only paths. |
| Backup phone              | None                                                   | Personal phone loss = SIM swap at carrier shop, ~1h. Tolerable.                                                                                                              |
| External display          | Defer until ≥ M3                                       | At ≥10 active clients the daily dashboard + Linear + Slack volume justifies a 27" 4K. Pre-M3 is laptop-only.                                                                 |
| Standing desk             | Defer until ≥ M3                                       | Same reason. Add when daily seat-time exceeds 6h.                                                                                                                            |
| Keyboard / mouse          | Existing                                               | Don't change tactile inputs mid-build; muscle memory matters more than ergonomics until M3.                                                                                  |
| UPS for VPS-adjacent gear | None                                                   | Hetzner is the production surface; the laptop is the operator surface. A laptop battery is the UPS.                                                                          |

**Mobile OS configuration (one-time, day 0):**

- Workspace Mail app installed, signed in to `founder@klantkraan.nl`, push **off** at the iOS/Android setting level (not just in-app).
- Slack mobile installed, notifications off except direct messages from `@channel`.
- WhatsApp Business installed separately from personal WhatsApp.
- Synthflow mobile app installed for call-listening QA.
- Bitwarden mobile installed with biometric unlock.
- Authy or Bitwarden's TOTP used for 2FA codes — **no SMS 2FA anywhere**, ever. SMS 2FA is treated as a vulnerability and replaced the moment a vendor adds TOTP support.
- Personal Gmail app uninstalled from the phone for the first 6 months. Access via mobile Safari at lunch only.

## 2. Workstation software baseline

| Tool                                    | Role                                       | Why this over alternatives                                                                                                                                                                                   |
| --------------------------------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Arc** (or Brave)                      | Browser                                    | Native profile isolation. Spaces map cleanly to founder / personal / burner-rotation. Chrome works too but profile UX is worse.                                                                              |
| **Ghostty**                             | Terminal                                   | Fast, GPU-rendered, sensible defaults. iTerm2 if Ghostty is unstable on your macOS build.                                                                                                                    |
| **VS Code**                             | Editor                                     | Claude Code extension lives here. This is the actual repo workflow; the Ralph Higgums loop (`CLAUDE.md`) depends on a fast edit-build-eyeball cycle and VS Code's integrated terminal makes that one window. |
| **Obsidian**                            | Personal notes                             | Local-first, vault stored in `~/Library/CloudStorage/iCloudDrive/Obsidian/founder`. Used for daily journal, meeting notes, and half-thoughts that aren't ready for Notion.                                   |
| **Notion**                              | Business SOPs + KPI weekly page            | Shared surface for VA at M6. Anything a second person will ever read goes here, not Obsidian.                                                                                                                |
| **macOS Calendar**                      | Calendar UI                                | Native. Reads the Workspace Google Calendar via CalDAV.                                                                                                                                                      |
| **Cal.com** (web)                       | Booking surface                            | The external-facing booking link. Stays in browser, not native app.                                                                                                                                          |
| **Linear**                              | Tasks                                      | Free tier (`07-finance/first-hire-triggers.md`). Single source of truth for _every_ commitment. If it's not in Linear, it doesn't exist.                                                                     |
| **Bitwarden** (desktop + browser ext)   | Password vault                             | See § 5.                                                                                                                                                                                                     |
| **1Password** (desktop)                 | Client-handoff packages only               | See § 5.                                                                                                                                                                                                     |
| **Raycast**                             | Launcher + clipboard history + window mgmt | Replaces Spotlight + Magnet + Alfred + ClipMenu in one tool. Free tier sufficient.                                                                                                                           |
| **Slack** (desktop)                     | Business comms only                        | One workspace: `klantkraan.slack.com`. No community Slacks in this app — those go in browser.                                                                                                                |
| **WhatsApp Business** (desktop + phone) | Primary client support channel             | Per onboarding playbook, WhatsApp is the day-1 client support line. Desktop app keeps it out of the phone-distraction loop during work hours.                                                                |
| **Loom** (desktop + browser ext)        | Screen-rec for onboarding videos           | Used for the day-0 welcome video and the day-30 case-study Loom.                                                                                                                                             |
| **Rectangle**                           | Window snapping                            | Free, scriptable. Skip if Raycast window mgmt suffices.                                                                                                                                                      |

## 3. Browser profiles & tab discipline

| Profile                       | Identity                | Surfaces                                                                                                                                                                                                                                                                                                                                                                                                                  |
| ----------------------------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1 — Founder (work)**        | `founder@klantkraan.nl` | Workspace Mail/Drive/Calendar, Attio, Mollie, Moneybird, Cloudflare, Hetzner Cloud, Neon, GitHub, n8n web UI, Synthflow dashboard, CM.com portal, Resend, Sentry, Plausible, Linear, Notion, Tally, SignWell, Cal.com admin. **Production surfaces only.**                                                                                                                                                                |
| **2 — Personal**              | Personal Gmail          | Personal Gmail, ABN AMRO, LinkedIn personal, YouTube, news. LinkedIn personal lives here on purpose: it's a personal-brand surface (per `05-content/channel-strategy.md`) and you do not want a Workspace cookie sharing a tab tree with the LinkedIn algorithm.                                                                                                                                                          |
| **3 — Burner rotation (M2+)** | None — empty cookie jar | The 9 Workspace inboxes used by Smartlead live here only as a quarantine. **Never log into them directly.** Smartlead OAuth handles everything; touching them in a real browser session risks deliverability reputation (Google flags hand-session activity on cold inboxes). The only legitimate reason to open this profile is to verify DNS records on a domain via Workspace Admin, and that's once per domain, ever. |

**Tab discipline rule:** maximum 7 tabs per profile. No exceptions. More than 7 = it is a Linear task, not a tab. The rule is enforced manually; no extension. At 18:00 close everything not pinned.

Pinned tabs per profile:

| Profile 1       | Profile 2           | Profile 3                 |
| --------------- | ------------------- | ------------------------- |
| Workspace Mail  | Personal Gmail      | (none — opened on demand) |
| Linear          | LinkedIn personal   |                           |
| Attio           | Calendar (personal) |                           |
| Notion KPI page |                     |                           |

**Cookie / session hygiene:**

- Profile 1 never logs into LinkedIn. LinkedIn lives in Profile 2 only. A Workspace Google session that has also seen a LinkedIn session ends up correlated by LinkedIn's tracker network, which contaminates audience targeting.
- Profile 3 cookies are wiped weekly (Sunday evening, manually). It exists as a quarantine; no persistent session belongs there.
- No browser sync between profiles. Sync would defeat the purpose.

## 4. Password vault layout

Defaults from `08-tech/stack-decisions.md` (Bitwarden Business + 1Password). The founder's personal layout on top:

| Vault                       | Tool                                         | Contents                                                                                                                                                                                                                                                                                                          | 2FA |
| --------------------------- | -------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --- |
| `Klantkraan` (personal-org) | Bitwarden Business                           | All business credentials: Workspace admin, Cloudflare, Hetzner, Neon, Mollie, Moneybird, Attio, Synthflow, CM.com, Anthropic, OpenAI, Resend, Sentry, GitHub, KvK login, BOIP login, TransIP, Bunq Business, Belastingdienst Ondernemers. Every entry carries TOTP attached inside Bitwarden — **never SMS 2FA**. |
| `Client-handoff-<slug>`     | 1Password Business                           | Per-client handover package built at offboarding: client's Mollie mandate ref, dashboard URL, n8n flow IDs, Synthflow agent ID, CM.com line ref, MSA + DPA PDFs. Created at month-30 close; shared via 1Password Secure Share with the client.                                                                    |
| `Personal`                  | Bitwarden (personal account, separate login) | Personal banking, Apple ID, ABN AMRO, streaming, personal Gmail. Separate from `Klantkraan` to avoid one-breach-takes-all.                                                                                                                                                                                        |

**Master password discipline:**

- Length ≥ 20 characters. Diceware-style passphrase, not a constructed string.
- Written down **once**, on paper, in a sealed envelope at parents' home address. This is the only physical backup and the only place it exists outside the founder's head. Nowhere digital.
- This is a deliberate single-point-of-failure mitigation: a forgotten master password is a business-extinction event, and digital backups (file, Drive, photo) all defeat the purpose. Paper at a trusted off-site location is the lowest-tech, highest-survivability option.

**SSH + hardware keys:**

| Key                            | Where                                                 | Use                                                                                    |
| ------------------------------ | ----------------------------------------------------- | -------------------------------------------------------------------------------------- |
| YubiKey 5C NFC (primary)       | Always in laptop USB-C or on keyring                  | GitHub commits, Hetzner SSH, Neon admin, Cloudflare WebAuthn, Workspace admin WebAuthn |
| YubiKey 5C NFC (backup)        | Sealed at parents' home with master-password envelope | Identical enrollment as primary; rotated annually                                      |
| ed25519 SSH key (passphrase'd) | `~/.ssh/id_ed25519`                                   | Fallback for SSH when YubiKey unavailable. Passphrase stored in Bitwarden.             |

## 5. Daily cadence (M1–M5 weekday template)

| Time        | Block                            | Notes                                                                                                                             |
| ----------- | -------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| 07:00–08:00 | Deep work 1 — ship the one thing | The pre-committed single highest-leverage task of the day, defined the previous evening. Phone in another room.                   |
| 08:00–08:30 | Inbox triage                     | Workspace mail + Attio notifications only. **Not** personal Gmail. Process to zero per § 8.                                       |
| 08:30–11:00 | Deep work 2                      | M1–M3: product build / SOP writing. M4+: outbound batch + content drafting.                                                       |
| 11:00–12:00 | Sales calls / Zoom discovery     | Cal.com slots cluster here. Wired headset on.                                                                                     |
| 12:00–13:00 | Lunch + 30-min walk              | **Non-negotiable.** No phone on walk. See § 12.                                                                                   |
| 13:00–15:00 | Deep work 3 — delivery           | Onboarding tasks (`03-delivery/onboarding-30-day.md`): kickoff calls, prompt fine-tuning, test calls, day-14 check-ins.           |
| 15:00–16:00 | LinkedIn engagement window       | Read feed, leave 8–12 substantive comments. **No posting** in this window — posting belongs to 16:00.                             |
| 16:00–17:00 | Content production               | One LinkedIn post drafted + one section of an SEO cornerstone. Claude-drafted, founder-edited (`05-content/channel-strategy.md`). |
| 17:00–17:30 | Close ritual                     | Linear update (move tickets, set tomorrow's "one thing"), KPI numbers if Friday, incident log if anything fired.                  |
| 17:30+      | Off                              | Hard boundary. Workspace and Slack notifications muted on phone. Protects mental energy for M2+ when load goes up.                |

## 6. Weekly cadence

| Day       | Theme                   | Concrete output                                                                                                                              |
| --------- | ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| Monday    | Content + sales prep    | Weekly post calendar set; Cal.com slots reviewed; prospect list for the week pulled from Attio.                                              |
| Tuesday   | Outbound batch          | Smartlead campaign review, LinkedIn DM batch via HeyReach, cold-reply triage (M2+).                                                          |
| Wednesday | Delivery + product      | Onboarding tasks clustered here; n8n flow tweaks; Synthflow prompt iteration.                                                                |
| Thursday  | Admin + legal review    | Invoicing review in Moneybird, Mollie reconcile, DPA/MSA review queue, KvK/Belastingdienst correspondence.                                   |
| Friday    | KPI review + week-close | `10-ops/weekly-kpi-review.md` runs at 16:00. Numbers logged in Notion KPI page. Week-close at 17:00 with a written 5-line retro in Obsidian. |
| Saturday  | Light / optional        | Long-form reading, content stockpile (1–2 evergreen drafts). Max 2h.                                                                         |
| Sunday    | **Off**                 | Full off-day per § 12.                                                                                                                       |

**Friday week-close (17:00–17:30, fixed):**

1. Pull MRR / active clients / churn from Postgres into the Notion KPI page.
2. Tag the week's biggest unblocked task in Linear (the "ship the one thing" for Monday 07:00).
3. Write a 5-line retro in Obsidian: what shipped, what stalled, one process change for next week, one health-signal note, one number that moved.
4. Close every browser tab not pinned. Close Slack. Close Linear. Quit VS Code.
5. Phone Workspace + Slack DND on until Monday 07:00.

## 7. Inbox discipline

- **Workspace inbox processed to zero twice daily**: 08:00 and 17:00. Anything < 2 minutes is done immediately. Anything > 2 minutes becomes a Linear task with the email URL pasted into the description; the email is then archived (not deleted).
- **Workspace labels (not folders)**: one label per email. The label set:

| Label          | Use                                                                                                                     |
| -------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `delivery`     | Anything tied to an active client's onboarding or support                                                               |
| `sales`        | Cold replies, demo bookings, offerte threads                                                                            |
| `legal`        | DPAs, MSAs, AP correspondence, BOIP, KvK                                                                                |
| `vendor`       | Hetzner, Cloudflare, Mollie, Synthflow, CM.com etc.                                                                     |
| `kpi-evidence` | Anything that should be archived as proof for KPI / audit (Mollie payout emails, Moneybird BTW filings, Hiscox renewal) |

- **The 9 burner Workspace inboxes get zero direct human session.** Smartlead handles them via OAuth. The only signal the founder watches is the Smartlead reply dashboard → n8n → Attio pipeline. If a reply lands directly in a burner inbox UI it gets surfaced via the Smartlead notification, not by opening the inbox.
- **No personal Gmail before 11:00.** Phone notifications off; web tab closed. Personal Gmail is opened at most twice per day (lunch + after 17:30).

## 8. Communication channels & response SLAs

| Channel                       | Direction | SLA                                                                                                              |
| ----------------------------- | --------- | ---------------------------------------------------------------------------------------------------------------- |
| Client SMS / WhatsApp         | Inbound   | < 2h, business hours (08:00–17:30)                                                                               |
| Client email                  | Inbound   | < 8h, business hours                                                                                             |
| Client missed call            | Inbound   | Synthflow handles in real time; escalation per prompt → founder receives SMS summary, callback < 4h if escalated |
| Vendor / supplier email       | Inbound   | < 48h                                                                                                            |
| LinkedIn DM (cold)            | Inbound   | Triaged in Tuesday outbound batch                                                                                |
| LinkedIn DM (warm / referred) | Inbound   | < 24h                                                                                                            |
| Personal Slack / iMessage     | Inbound   | After 17:30 only                                                                                                 |
| Internal Linear               | n/a       | Reviewed at 17:00 close + 08:00 start                                                                            |

Out-of-office: any single day off (other than Sunday) requires an autoresponder set on Workspace and a pinned WhatsApp status. Vacation > 3 days requires the M6+ VA covered fallback (deferred until VA hires).

**Incident-response channel:**

- Sentry → Slack `#alerts` (founder DM). Anything firing here cuts through DND.
- Healthchecks.io / Uptime Kuma → SMS to personal +316 on `down` after 5-minute grace. SMS is privileged: only critical-path uptime alerts allowed to use it. Polluting the SMS channel defeats its purpose.
- Synthflow webhook failures → Sentry, not SMS.
- CM.com SMS delivery failures → n8n retries silently; surfaces in the Friday KPI review only.

## 9. Focus / anti-distraction layer

| Layer                              | Setting                                                                                                                                                              |
| ---------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Phone — Workspace Mail             | Push notifications **off**                                                                                                                                           |
| Phone — Workspace Slack            | Push notifications **off**                                                                                                                                           |
| Phone — WhatsApp Business          | On (client SLA)                                                                                                                                                      |
| Phone — only interrupt             | Direct calls to personal +316                                                                                                                                        |
| Mac — Focus mode `Work`            | 08:00–17:00 weekdays. Allows Calendar, Linear, business Slack, WhatsApp Business. Suppresses everything else including personal Slack, iMessage, Telegram.           |
| Browser — uBlock Origin            | Always on. Blocks ads everywhere.                                                                                                                                    |
| Browser — 1Blocker (or LeechBlock) | Blocks LinkedIn feed, YouTube homepage, X feed, Reddit homepage **during 08:00–17:00**. Direct URLs still resolve so you can post / comment / view specific threads. |
| Slack — Do Not Disturb             | 17:30–07:00, weekends                                                                                                                                                |
| macOS — system Stage Manager       | Off. Adds latency. Stick to single-desktop + Raycast window snap.                                                                                                    |

## 10. Personal financial / admin tooling — what NOT to mix with the business

| Domain               | Personal                                            | Business                                                                 |
| -------------------- | --------------------------------------------------- | ------------------------------------------------------------------------ |
| Bookkeeping          | Personal Moneybird tenant or none (own IB-aangifte) | Klantkraan Moneybird tenant (separate org)                               |
| Bank — daily         | ABN AMRO personal                                   | Bunq Business or Knab Business (NL, cheap, has API for Moneybird import) |
| Bank — savings       | ABN AMRO savings                                    | Business savings under same Bunq/Knab                                    |
| Tax filing — annual  | Belastingdienst Mijn Belastingdienst portal (IB)    | Moneybird → Belastingdienst (BTW kwartaal + ICP)                         |
| Pension              | DIY (Brand New Day / Meesman)                       | Not yet — revisit at €30k MRR                                            |
| Insurance — personal | Existing health/aansprakelijkheid                   | Hiscox PI + AVB + cyber (€150/mo, `00-MASTER-PLAN.md`)                   |

Never share a card across the boundary. The business card lives in Bunq/Knab, the personal card lives in ABN AMRO. Founder reimburses any accidental cross-charges via Moneybird at month-end close.

## 11. Health-of-the-founder rules

These are operational risk controls. Founder burnout is the highest-impact, highest-likelihood single risk in this business — it expands the R-OPS bus-factor entry in `10-ops/risk-register.md`.

| Rule                | Detail                                                                                                                                                                                        |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Full off-day        | Sunday default. Phone on Do Not Disturb. No Linear, no Workspace, no Slack.                                                                                                                   |
| Daily walk          | 30 minutes, blocks the 12:00 hour. Non-negotiable in calendar. Phone stays at desk.                                                                                                           |
| No work after 21:00 | Exception: declared incident-response window (one-line Linear ticket opened first, closed at end).                                                                                            |
| Annual leave        | 2 weeks minimum per year, scheduled into the calendar **before Q1 begins**. This document is the contract that protects it; renegotiating it requires writing a Linear ticket explaining why. |
| Sleep               | 7h minimum. Phone charges outside bedroom.                                                                                                                                                    |
| Annual physical     | Booked once per year via huisarts; calendar reminder set for January.                                                                                                                         |

## 12. Tooling handover triggers (M6 VA arrival)

Cross-ref: `07-finance/first-hire-triggers.md` Hire #1.

| Surface                     | Pre-VA                  | Post-VA                                                                                                      |
| --------------------------- | ----------------------- | ------------------------------------------------------------------------------------------------------------ |
| Workspace                   | Founder seat only       | `va@klantkraan.nl` seat added; VA inbox is `delivery`-labeled mail forwarded by filter                       |
| Notion                      | Founder editor          | VA editor (full); founder retains admin                                                                      |
| Attio                       | Founder admin           | VA read + comment; no record-delete permission                                                               |
| Linear                      | Founder source-of-truth | Stays source-of-truth; VA mirrors tasks here (no separate Trello/Asana ever)                                 |
| Mollie                      | Founder only            | VA has no access                                                                                             |
| Moneybird                   | Founder admin           | VA has read-only on `Klanten` + `Facturen`                                                                   |
| Hetzner / Neon / Cloudflare | Founder admin           | VA has no access                                                                                             |
| Synthflow / CM.com          | Founder admin           | VA has operator role (can edit prompts, cannot manage billing)                                               |
| Bitwarden                   | `Klantkraan` vault      | New collection `Klantkraan-VA` with only the credentials VA needs (Notion, Attio op-only, Synthflow op-only) |
| SOPs                        | Obsidian + ad-hoc Looms | All SOPs in Notion, every founder action done twice is documented in Notion _before_ delegation              |

The handover trigger is mechanical: at the 12-active-clients line per `07-finance/first-hire-triggers.md`, the founder spends one Thursday (admin day) converting the pre-VA column to the post-VA column.

**SOP-before-delegate rule:** any founder task done a second time must be documented in Notion before the VA inherits it. The SOP template:

1. Trigger (what kicks it off)
2. Steps (numbered, with screenshots)
3. Success criteria (how the VA knows it's done)
4. Escalation path (when to ping founder on WhatsApp)
5. Loom URL (2–4 min screen-rec)

This rule is what makes the M6 hire actually offload work instead of creating training overhead.

## 13. What we deliberately don't use

| Tool                          | €/mo     | Why not                                                                                                                                                          |
| ----------------------------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Superhuman                    | €30      | Workspace + keyboard shortcuts + Raycast give 90% of the speed. Two inbox-zero passes a day removes the rest of the gap.                                         |
| Notion AI add-on              | €10/seat | Claude already covers drafting; Notion AI summaries don't carry into the editorial pipeline.                                                                     |
| ChatGPT Plus / Pro (personal) | €20–€200 | Claude (Anthropic console + Claude Code) is already the LLM in stack-decisions. Adding a second provider doubles context-switching with no marginal output gain. |
| Calendly                      | €12      | Cal.com is the chosen booking tool per `08-tech/stack-decisions.md`.                                                                                             |
| Loom paid (Business)          | €15      | Free tier covers the founder's volume (one onboarding video per client + one monthly case-study Loom per client). Revisit if storage cap hits.                   |
| Sunsama                       | €20      | Linear + macOS Calendar is enough for one person. Sunsama's day-planning layer is overhead at this scale.                                                        |
| Reflect / Mem.ai              | €10–€20  | Obsidian local-first vault is faster and works offline.                                                                                                          |
| Krisp                         | €8       | Wired headset eliminates the need.                                                                                                                               |
| Arc Max (subscription)        | €20      | Free Arc covers what's needed; Max's AI features are duplicative with Claude.                                                                                    |

Re-evaluation rule: any tool on this list gets revisited if the founder week-close retro lists the same friction twice in a month.

## 14. Muscle-memory layer (keyboard shortcuts kept identical across tools)

Switching cost between tools is mostly cognitive. Picking one chord per action and keeping it identical across surfaces eliminates the hesitation.

| Action                             | Chord                 | Where it's mapped                                                     |
| ---------------------------------- | --------------------- | --------------------------------------------------------------------- |
| Open command palette / launcher    | `Cmd+K`               | Raycast (system), VS Code, Linear, Notion, Attio, Cal.com, Cloudflare |
| Switch app                         | `Cmd+Tab`             | macOS native                                                          |
| Switch browser profile             | `Ctrl+Shift+1/2/3`    | Arc Spaces                                                            |
| Switch tab within profile          | `Cmd+Opt+→/←`         | Arc + Chrome consistent                                               |
| New Linear task                    | `Cmd+K → t` then text | Linear (also from Raycast Linear extension)                           |
| New Notion block                   | `/`                   | Notion native                                                         |
| Quick-paste from clipboard history | `Cmd+Shift+V`         | Raycast                                                               |
| Start Claude Code session          | `Cmd+Esc`             | VS Code Claude Code extension default                                 |
| Lock screen                        | `Ctrl+Cmd+Q`          | macOS native — used at every standup-away                             |

Anything not in this table is fine to rely on the tool's default; the cost of relearning a default once is lower than the cost of one customisation breaking after a vendor UI update.

## 15. Pre-launch one-time setup checklist (M1 day 0)

Run once, before any other M1 work. Each row is a 5–30 minute action; total ~4 hours.

| #   | Action                                                                                                                         |
| --- | ------------------------------------------------------------------------------------------------------------------------------ |
| 1   | Order primary YubiKey + backup YubiKey from yubico.com (€110 total). Ships in ~3 working days.                                 |
| 2   | Create Bitwarden Business account; generate `Klantkraan` org; enable WebAuthn with YubiKey on arrival.                         |
| 3   | Create 1Password Business account (single seat) — used exclusively for `Client-handoff-*` vaults.                              |
| 4   | Install Arc; create three Spaces (founder, personal, burner). Disable cross-Space sync.                                        |
| 5   | Install Ghostty, VS Code, Obsidian, Linear, Slack, WhatsApp Business, Loom, Raycast, Rectangle, Bitwarden, 1Password.          |
| 6   | Generate ed25519 SSH keypair with passphrase; store passphrase in Bitwarden `Klantkraan`.                                      |
| 7   | Enroll YubiKey on GitHub, Hetzner, Neon, Cloudflare, Workspace admin.                                                          |
| 8   | Configure macOS Focus mode `Work` (08:00–17:00 weekdays). Allowlist Calendar, Linear, business Slack, WhatsApp Business.       |
| 9   | Configure phone: Workspace Mail + Slack push **off**, WhatsApp Business **on**, personal Gmail app uninstalled.                |
| 10  | Sealed envelope at parents' address: paper master password + backup YubiKey + recovery codes for Bitwarden, Workspace, GitHub. |
| 11  | Linear: create the four boards `Sales`, `Delivery`, `Product`, `Ops`.                                                          |
| 12  | Notion: create the KPI weekly page from `10-ops/weekly-kpi-review.md` template.                                                |
| 13  | Obsidian: create `~/Library/CloudStorage/iCloudDrive/Obsidian/founder` vault; verify iCloud sync.                              |
| 14  | Calendar: pre-block Sunday off + 12:00 walk + 17:30 hard stop for the full year.                                               |
| 15  | This document goes into Notion as the "Founder Operating System" SOP, linked from the KPI weekly page.                         |

Done = the operator surface is configured before any business surface. After this, M1 build per `00-MASTER-PLAN.md § 4` starts.

## 16. Sources

Internal:

- `CLAUDE.md`
- `00-MASTER-PLAN.md`
- `08-tech/stack-decisions.md`
- `06-outbound/deliverability-stack.md`
- `03-delivery/onboarding-30-day.md`
- `05-content/channel-strategy.md`
- `07-finance/first-hire-triggers.md`
- `10-ops/weekly-kpi-review.md` (referenced; lives in same folder)
- `10-ops/risk-register.md` (referenced R-OPS bus-factor entry; lives in same folder)

External:

- Bitwarden Business: https://bitwarden.com/products/business/
- 1Password Business: https://1password.com/business
- Cal.com self-host + cloud: https://cal.com/
- YubiKey 5C NFC: https://www.yubico.com/product/yubikey-5c-nfc/
- Arc browser profiles: https://arc.net/
- Ghostty terminal: https://ghostty.org/
- Obsidian sync model: https://obsidian.md/sync
- Raycast: https://www.raycast.com/
- Bunq Business: https://www.bunq.com/nl/business
- Knab Business: https://www.knab.nl/zakelijk
- Belastingdienst BTW filing: https://www.belastingdienst.nl/zakelijk/btw/
