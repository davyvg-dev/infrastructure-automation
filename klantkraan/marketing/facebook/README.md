# Facebook-groepen — value-first posting kit

A compliant way to use Facebook groups as a channel: **you post by hand, on a
schedule, with pre-written Dutch drafts.** No bots.

## Why no auto-poster

Meta **killed the Facebook Groups API in April 2024** (removed `publish_to_groups`
and all third-party group access, to stop spam). No legitimate tool — Buffer,
Hootsuite, Make, n8n — can post to a group anymore. The only thing left is a
browser bot that logs in as you and clicks; that breaks Meta's Terms and risks a
ban on the account that *is* the business. So this kit schedules and drafts; a
human does the 30-second paste. Auto-posting to **Facebook Pages** (not groups)
is still allowed — see the upgrade path below.

## What's here

```
marketing/facebook/
├── README.md            ← this file
├── groups.md            ← YOUR groups + each group's promo rules (fill in)
├── posting-calendar.md  ← cadence, 4:1 value:promo ratio, anti-spam rules
├── schedule.mjs         ← CLI: tells you what to post this week + the text
└── drafts/              ← 6 Dutch value-first posts (no links, no fabrication)
```

## How to use it

1. **Fill in `groups.md`** once — list the groups you're in and read each one's
   rules (most ban promo or restrict it to a weekly thread).
2. **Each posting day, run the scheduler:**
   ```bash
   node schedule.mjs            # what's due this week + paste-ready text
   node schedule.mjs --week 2   # peek at a specific week
   node schedule.mjs --all      # whole plan at a glance
   node schedule.mjs --post 003 # one draft
   ```
   Edit `START_DATE` at the top of `schedule.mjs` to the Monday you start.
3. **Copy the printed body**, pick a matching group from `groups.md` (mind the
   `group_rule_type`), tweak the opening line so you're not pasting identical text
   across groups, and post.
4. **Log it** in the table in `posting-calendar.md` so you keep the 4:1 ratio and
   don't double-post.

## Rules baked into the drafts

- No invented pilots, clients, or stats (same holdback rule as
  `../linkedin/posting-calendar.md`).
- No model names, no emoji, no marketing-jargon — per `docs/09-brand/voice-and-tone.md`.
- Value before ask: 5 of the 6 drafts sell nothing. `fb-006` is the only promo and
  goes out last, only where promo is allowed.

## Upgrade path (later, optional)

When n8n + CM.com are live, an `infra/n8n/facebook-post-reminder.json` workflow can
push the day's draft to your WhatsApp/e-mail each posting morning — so the
*reminder* is automated even though the *posting* stays manual. The same channel
could run a real **Facebook Page** on autopilot (Pages allow scheduled posting via
the official API), separate from groups. Not built yet; needs the same creds gate
as the voice agent.
