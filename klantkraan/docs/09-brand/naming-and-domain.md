# Naming and Domain

> The brand name has to do four jobs: (1) be unambiguous in Dutch, (2) survive KvK + BOIP checks, (3) carry a metaphor a vakman immediately gets, (4) leave room to expand beyond loodgieters and dakdekkers. **Klantkraan** is the locked priority-1 pick. Priority 2 and 3 fallbacks are listed so a single blocked check doesn't restart the whole branding exercise.

## 1. The chosen name — Klantkraan

| Attribute          | Value                                                                                                                                  |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------- |
| Spelling           | `Klantkraan` (single word, lowercase logotype, capital K in body copy)                                                                 |
| Pronunciation      | /klɑnt.kraːn/ — two syllables, hard K, long ā                                                                                          |
| Meaning            | "Customer tap" — a tap (kraan) you turn on and customers come out. Doubles on `kraan` = crane (loodgieter / installateur association). |
| Category           | `klantenmotor` (category-creation play, see `01-strategy/positioning.md`)                                                              |
| Legal vehicle      | Handelsnaam under existing **T4 Software Consulting BV** — no new BV, no notary cost                                                   |
| Sector codes (SBI) | 6201 (custom software), 7311 (advertising), 7320 (market research) — already on T4                                                     |

### Why this name wins on each criterion

| Test                                                                | Klantkraan                                                          |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| Dutch-native (a vakman gets it in 1 second)                         | Yes — `kraan` is in every plumber's daily vocabulary                |
| Trade-cross-over (works for dakdekker, elektricien, schilder later) | Yes — the metaphor is "customers", not "water"                      |
| Speakable on the phone (no spelling clarifications)                 | Yes — `K-L-A-N-T-K-R-A-A-N` is phonetically unambiguous in Dutch    |
| Short (≤12 chars)                                                   | 10 chars                                                            |
| No collision with English defaults                                  | `kraan` is Dutch-only, lowers global confusion risk                 |
| Logo-able                                                           | Strong K-K alliteration; valve / tap icon ready-made                |
| Doesn't sound like an agency                                        | Avoids "Studio / Lab / Digital / AI" tropes that tradesmen distrust |
| Will it embarrass us at €30k MRR                                    | No — the metaphor scales                                            |

### Risks specific to this name

| Risk                                                                   | Mitigation                                                                                                                               |
| ---------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Confusion with sanitaire kraan-sellers (Hansgrohe, Grohe distributors) | Logo + payoff text make context unambiguous; SEO domain language is "AI-receptionist", not "kraan"                                       |
| Boring                                                                 | Klantkraan is intentionally not edgy. Tradesmen reward clarity over novelty (Hofstede masculinity 14, see `01-strategy/positioning.md`). |
| English-language scaling later                                         | UK / DE / ES require local naming. Plan: see § 5 below.                                                                                  |

## 2. Priority 2 fallback — Vakflow

| Attribute | Value                                                                                  |
| --------- | -------------------------------------------------------------------------------------- |
| Spelling  | `Vakflow`                                                                              |
| Meaning   | `vak` (trade/profession) + `flow` — the flow that your trade business runs on          |
| Risk      | English "flow" feels less Dutch-native; `vak` collides with vakman.nl, vakgarage, etc. |
| Use when  | Klantkraan blocked at KvK / BOIP / domain registration                                 |

## 3. Priority 3 fallback — Afspraakmotor

| Attribute | Value                                                        |
| --------- | ------------------------------------------------------------ |
| Spelling  | `Afspraakmotor`                                              |
| Meaning   | "Appointment engine" — closer to functional, less metaphor   |
| Risk      | 13 chars (longer), and `motor` is overused in NL SaaS naming |
| Use when  | Both Klantkraan and Vakflow blocked                          |

## 4. Domain status — actions required (founder, see `00-MASTER-PLAN.md § 5`)

**Status 2026-05-20:** `klantkraan.nl`, `klantkraan.com`, KvK handelsnaam search, and BOIP class 35+42 trademark search all confirmed clear. Brand name **Klantkraan** is locked. Fallback names in §§ 2–3 stay documented for posterity only.

| #   | Domain                   | Where to check                     | Status / next action                                                                 |
| --- | ------------------------ | ---------------------------------- | ------------------------------------------------------------------------------------ |
| 1   | `klantkraan.nl`          | https://www.sidn.nl/en/whois       | Available — **register at TransIP (~€5/yr)**                                         |
| 2   | `klantkraan.com`         | https://lookup.icann.org/en/lookup | Available — **register at Namecheap (~€10/yr, defensive)**                           |
| 3   | `klantkraan.eu`          | https://eurid.eu/en/find-a-domain/ | Not yet checked — recheck at registration time; register if free (~€5/yr, defensive) |
| 4   | `klantkraan.io` / `.app` | Namecheap                          | Skip — not needed                                                                    |
| 5   | `klantkraan.co.uk`       | https://www.nominet.uk/lookup/     | Skip until UK month 6+                                                               |

### Subdomain plan

| Subdomain                                | Purpose                                                              |
| ---------------------------------------- | -------------------------------------------------------------------- |
| `klantkraan.nl` (apex)                   | Marketing site (Astro on Cloudflare Pages)                           |
| `app.klantkraan.nl`                      | Client dashboard (per-client `/r/{slug}` for now, full app later)    |
| `demo.klantkraan.nl`                     | Public AI demo number landing + ROI calc                             |
| `n8n.klantkraan.nl`                      | n8n self-host UI (basic auth + Cloudflare Access)                    |
| `status.klantkraan.nl`                   | Uptime Kuma public page                                              |
| `mail-{1..9}.klantkraan-{de,nl,com}.com` | Smartlead burner domains (see `06-outbound/deliverability-stack.md`) |

The cold-email burner domains are **never** under `klantkraan.nl` — that's the deliverability-protection rule. Burner domains are registered as `klantkraan-de.com`, `klantkraan-nl.com`, `klantkraanmedia.com`, etc., each on its own Workspace.

### DNS provider

Cloudflare free tier — same account as the hosting. Reasons:

- Free DDoS protection
- Workers for the lead-form-to-Attio edge function
- DNS API for programmatic SPF / DKIM / DMARC management of burner domains
- EU PoPs

### Email DNS records (apex `klantkraan.nl`)

| Type | Host                | Value                                                                       | Why                           |
| ---- | ------------------- | --------------------------------------------------------------------------- | ----------------------------- |
| MX   | @                   | Google Workspace (1 ASPMX..., 5 ALT1..., 5 ALT2..., 10 ALT3..., 10 ALT4...) | Founder inbox + transactional |
| TXT  | @                   | `v=spf1 include:_spf.google.com include:_spf.resend.com -all`               | Authenticate sender           |
| TXT  | `_dmarc`            | `v=DMARC1; p=reject; rua=mailto:dmarc@klantkraan.nl; fo=1; adkim=s; aspf=s` | Hard fail for anyone not us   |
| TXT  | `google._domainkey` | (from Workspace console)                                                    | DKIM                          |
| TXT  | `resend._domainkey` | (from Resend console)                                                       | Transactional DKIM            |
| TXT  | `@`                 | `v=verifyowner; <token>`                                                    | Workspace domain proof        |

DMARC `p=reject` from day 1 because the brand name is small and we'd rather break a misconfig than ever risk impersonation of the founder.

## 5. International naming plan

| Market | Year | Approach                                                                                                                                                                  |
| ------ | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| NL     | 1    | `Klantkraan`                                                                                                                                                              |
| UK     | 1 H2 | **Rebrand likely** — `kraan` doesn't translate. Test names: `ClientTap`, `Booker`, `Trades Receptionist`. Decision deferred to month 6 with one Dutch case study in hand. |
| DE     | 2    | `Klantkraan` works phonetically (similar Dutch/German), keep brand if KvK-equivalent (Handelsregister) allows.                                                            |
| ES     | 2+   | Translate — `Grifo de clientes` is literal but clunky. Defer naming.                                                                                                      |

The brand book (visual identity) is intentionally **language-agnostic** so a UK rebrand is a logo-text swap, not a full identity redo. See `09-brand/visual-identity-brief.md`.

## 6. Trademark posture

| Class                                       | Use                                            | File when                                                   |
| ------------------------------------------- | ---------------------------------------------- | ----------------------------------------------------------- |
| Class 35 (advertising, business management) | Lead generation, marketing automation services | After 2 paid clients + €1k MRR — €244 Benelux fee (BOIP)    |
| Class 42 (software-as-a-service)            | The Klantkraan platform itself                 | Same filing, both classes — €244 covers both at BOIP        |
| EU (EUIPO)                                  | EU-wide protection                             | Defer to year 2 unless UK / DE pilots demand it — €850 base |

Pre-launch trademark search is in the founder-action list (`00-MASTER-PLAN.md § 5 item 4`). Conflict triggers fall-back to Vakflow.

## 7. KvK handelsnaam filing

| Step                                                      | Cost                | Where                                                                      |
| --------------------------------------------------------- | ------------------- | -------------------------------------------------------------------------- |
| Search "Klantkraan" in KvK Handelsregister                | €0                  | https://www.kvk.nl/zoeken/                                                 |
| File handelsnaamwijziging under T4 Software Consulting BV | €0 (free amendment) | https://www.kvk.nl/inschrijven-en-wijzigen/wijzigen/handelsnaam-toevoegen/ |
| Extract bewijs of new handelsnaam                         | €2.99               | KvK                                                                        |

This is **the** legal step that turns the name into a usable business identity. Without it, invoices issued under "Klantkraan" are not enforceable.

## 8. Brand registry checklist

| Surface                      | Handle                                       | Owner / status                                                      |
| ---------------------------- | -------------------------------------------- | ------------------------------------------------------------------- |
| KvK handelsnaam              | "Klantkraan" under T4                        | **To do**                                                           |
| Domain `.nl` + `.com`        | TransIP / Namecheap                          | **To do**                                                           |
| Google Workspace primary     | `davy@klantkraan.nl`                         | After domain                                                        |
| Google Workspace burners × 9 | per `06-outbound/deliverability-stack.md`    | After M1 inbox warmup begins                                        |
| LinkedIn company page        | `linkedin.com/company/klantkraan`            | After domain                                                        |
| LinkedIn personal            | `linkedin.com/in/<founder>` headline updated | Manual founder action                                               |
| GitHub org                   | `github.com/klantkraan` (free)               | After domain                                                        |
| Twitter / X                  | `@klantkraan` (defensive)                    | Defer, optional                                                     |
| Instagram                    | `@klantkraan` (defensive)                    | Defer, optional                                                     |
| TikTok                       | n/a                                          | Founder constraint: no face-on-camera; faceless TikTok not in scope |
| YouTube                      | `@klantkraan`                                | Required for screen-rec series (see `05-content/`)                  |
| Mollie merchant              | "Klantkraan"                                 | After KvK handelsnaam filed                                         |
| Moneybird tenant             | "Klantkraan"                                 | After KvK                                                           |
| Attio workspace              | "Klantkraan"                                 | Immediately                                                         |
| Notion workspace             | "Klantkraan"                                 | Immediately                                                         |

## 9. Naming dont's

- ❌ Don't add a TLA / acronym ("KK", "KKR") — Dutch tradesmen don't bond with initials.
- ❌ Don't add "AI" in the brand name. AI is the technology, not the value. ("Klantkraan AI" would shrink the category to one feature.)
- ❌ Don't add a `.io` or `.app` suffix in copy. We're not a developer tool.
- ❌ Don't use "Klantkraan™" in marketing until the BOIP filing returns registered status (~6 months).
- ❌ Don't capitalize internally (`KlantKraan`, `KLANTKRAAN`). One word, sentence case, always.

## Sources

- KvK handelsnaam search: https://www.kvk.nl/zoeken/
- SIDN `.nl` whois: https://www.sidn.nl/en/whois
- ICANN lookup: https://lookup.icann.org/en/lookup
- BOIP trademark register: https://www.boip.int/en/trademarks-register
- EUIPO trademark filing: https://euipo.europa.eu/
- Hofstede Netherlands (low-masculinity, low-PDI naming preference): https://www.hofstede-insights.com/country/the-netherlands/
- Cross-references: `01-strategy/positioning.md`, `06-outbound/deliverability-stack.md`, `09-brand/visual-identity-brief.md`
