# Deliverability Stack

> 9 inboxes across 3 secondary `.nl` domains, sending ~225 emails/workday (~4,500/month). Total monthly stack cost: ~€146/mo. Scales to ~9,000/month at ~€210/mo.

## Architecture overview

```
┌──────────────────────────────────────────────────────────────┐
│  Smartlead (sending engine, ~$39/mo)                          │
│   ├── Inbox rotation with variable volume randomization      │
│   ├── Built-in warmup                                         │
│   └── Webhook → n8n → Attio (reply tracking)                 │
└──────────────────────────────────────────────────────────────┘
        │
        ├── Domain 1: getklantkraan.nl
        │     ├── jan@getklantkraan.nl
        │     ├── pieter@getklantkraan.nl
        │     └── info@getklantkraan.nl
        │
        ├── Domain 2: klantenmotor.nl
        │     ├── jan@klantenmotor.nl
        │     ├── pieter@klantenmotor.nl
        │     └── info@klantenmotor.nl
        │
        └── Domain 3: klantkraanpro.nl
              ├── jan@klantkraanpro.nl
              ├── pieter@klantkraanpro.nl
              └── info@klantkraanpro.nl
```

The brand domain `klantkraan.nl` is **NEVER** used for cold outbound. It exists only for transactional, content, and inbound traffic.

## Mailbox provider — Google Workspace

| Choice                                                       | Why                                                                                                                                                                                                |
| ------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Google Workspace Business Starter** (€6.90/user/mo ex VAT) | Best inbox-placement to other Gmail (57% of NL business email). Use OAuth (not SMTP), cap at 25-30 sends/inbox/day. Recent (late-2025) tenant suspensions for cold email mean: warm 3 weeks first. |
| Microsoft 365 (€6.10) — alternative                          | Equivalent ~95% placement. Slightly different reliability profile. Use as fallback or for a second-mode setup.                                                                                     |
| Self-hosted (Postmark/SES)                                   | Skip — too fragile for solo founder.                                                                                                                                                               |

Cost: 9 inboxes × €6.90 = **€62.10/mo**

## Sending tool — Smartlead

| Choice                               | Why                                                                                                                       |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------- |
| **Smartlead Basic** (~$39/mo ≈ €36)  | Unlimited sender accounts, inbox rotation with variable-volume randomization, built-in warmup, native Gmail/Outlook OAuth |
| Instantly Growth ($47) — alternative | Comparable, slightly different UI; pricier                                                                                |
| lemlist — alternative                | More expensive at scale; better for video personalization which we don't use                                              |

## Authentication stack (per domain)

| Record                      | Setting                                                                         | Why                                     |
| --------------------------- | ------------------------------------------------------------------------------- | --------------------------------------- |
| **SPF**                     | `v=spf1 include:_spf.google.com ~all`                                           | Authorise Google to send for the domain |
| **DKIM**                    | Google-generated 2048-bit key, published as `google._domainkey`                 | Sign all outbound mail                  |
| **DMARC**                   | `v=DMARC1; p=none; rua=mailto:dmarc@klantkraan.nl` → after 4 weeks → `p=reject` | Strong policy after warmup              |
| **MX**                      | Google MX records                                                               | Receive replies                         |
| **BIMI** (optional)         | After DMARC reject is live                                                      | Brand logo in inbox — nice-to-have      |
| **List-Unsubscribe header** | `<mailto:unsubscribe@klantkraan.nl>, <https://klantkraan.nl/unsubscribe?...>`   | Required by Gmail bulk-sender rules     |

## Warm-up protocol (3 weeks per new inbox)

| Week | Daily volume | Smartlead warmup    | Real sends |
| ---- | ------------ | ------------------- | ---------- |
| 1    | 0            | 5/day               | 0          |
| 2    | 5            | 10/day              | 5          |
| 3    | 10           | 15/day              | 10         |
| 4+   | 25           | continues at 10/day | 25         |

**Never exceed 25-30 real sends per inbox per day**, even after warmup. This is the Google soft-cap for cold email accounts.

## Domain warm-up (each .nl domain)

1. Register the `.nl` (TransIP, €5–10/yr).
2. Configure SPF/DKIM/MX immediately.
3. Set DMARC to `p=none` initially.
4. Add 3 inboxes (jan / pieter / info). Send 1-2 personal emails between inboxes the first day to bootstrap activity.
5. Connect to Smartlead. Start warmup.
6. Wait 3 weeks before real cold-email sends.
7. After 4 weeks of clean reputation → switch DMARC to `p=reject`.

## Per-domain redirect strategy

Each secondary `.nl` redirects (301) to `klantkraan.nl/from/{domain-slug}` so:

- Suspicious recipient who manually checks the domain → finds a legit-looking site
- Domain reputation builds organically
- Track click-through if the redirect parameter is set

Cloudflare Pages handles the redirect free.

## Send window + cadence

| Setting                    | Value                                                 |
| -------------------------- | ----------------------------------------------------- |
| Days                       | Tuesday – Thursday (best for B2B NL)                  |
| Window                     | 09:00–17:00 CET                                       |
| Send-rate randomization    | 25 ± 5 emails/inbox/day                               |
| Random delay between sends | 60–180 seconds                                        |
| Time-zone awareness        | Send to recipient's likely local time (NL = CET)      |
| Holiday calendar           | Skip NL public holidays + summer schoolvakantie weken |

## Monitoring + alerts

| Metric                | Tool                           | Alert threshold                    |
| --------------------- | ------------------------------ | ---------------------------------- |
| Spam-folder placement | Smartlead inbox-placement test | < 80% inbox = pause                |
| Bounce rate           | Smartlead                      | > 3% = pause inbox                 |
| Reply rate            | Smartlead → n8n → Attio        | < 3% over 2 weeks = rotate hooks   |
| Domain reputation     | Google Postmaster Tools        | Any "low" → pause domain           |
| DMARC reports         | Postmark DMARC Digests (free)  | Unauthorized sources = investigate |

## When deliverability collapses

| Signal                      | Recovery action                                                                    |
| --------------------------- | ---------------------------------------------------------------------------------- |
| Single inbox warning        | Pause that inbox for 7 days; restart warm-up                                       |
| Whole domain flagged        | Burn the domain. Buy a new one. Restart cycle. Cost: €5-10.                        |
| Google Workspace suspension | Migrate to Microsoft 365 fallback inboxes; switch Smartlead routing                |
| Multiple domains flagged    | Stop all cold email. Investigate root cause (likely list quality or hook content). |

Domain burning is normal in cold email at scale. Treat domains as consumables, not assets. Brand domain (`klantkraan.nl`) is the asset.

## Total cost

| Component                                            | Monthly      |
| ---------------------------------------------------- | ------------ |
| KvK API + Outscraper enrichment (~2k leads/mo)       | €36          |
| 3 × .nl domains                                      | €2.50        |
| Google Workspace 9 inboxes                           | €62.10       |
| Smartlead Basic                                      | €36          |
| Email verification (MillionVerifier)                 | €10          |
| DMARC monitoring (Postmark free, dmarcian community) | €0           |
| **Total**                                            | **~€146/mo** |

Optional LinkedIn lane (HeyReach $79 + Sales Navigator €89.50) brings total to ~€316/mo when added in month 2.

## Source

- Smartlead cold email open rates: https://www.smartlead.ai/blog/cold-email-open-rates
- Litemail Google Workspace cold-email safety 2026: https://litemail.ai/blog/google-workspace-cold-email-safe-2026
- Litemail "how many inboxes 2026": https://litemail.ai/blog/how-many-email-inboxes-do-you-need-for-cold-email-in-2026
- Smartlead vs Instantly 2026: https://prospeo.io/s/instantly-vs-smartlead
- Gmail bulk sender requirements 2024+: https://support.google.com/mail/answer/81126
