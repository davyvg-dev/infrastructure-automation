# GDPR / Telecommunicatiewet Compliance for B2B Outbound

> Single most important constraint on the acquisition plan. The rule that drives everything: **most Dutch trade businesses are eenmanszaak/VOF, treated as natural persons under Dutch law → opt-in regime applies**. We filter cold outbound to BVs only.

## The governing rules

| Rule | Source | What it says (B2B email) |
|---|---|---|
| ePrivacy Directive | EU 2002/58/EC | Member states implement direct-marketing consent rules |
| Telecommunicatiewet art. 11.7 | Dutch implementation | Direct marketing rules per recipient type |
| AVG (GDPR) art. 6 | EU 2016/679 | Legal basis required for any personal-data processing |
| EU AI Act art. 50 | EU 2024/1689 | (Doesn't apply to outbound directly, but to the receptionist AI we sell) |

Enforcers: **Autoriteit Persoonsgegevens (AP)** for AVG, **ACM** for telemarketing.

## Recipient classification (this is everything)

| Type | Treatment | Cold-email legality |
|---|---|---|
| **BV, NV, stichting, vereniging, coöperatie** | Legal entities | **Opt-out** regime — cold email allowed if address is publicly disclosed by company without restriction, message has clear sender ID, every message offers easy opt-out, legal basis is Art. 6(1)(f) legitimate interest with LIA documented |
| **eenmanszaak, VOF, maatschap, CV, ZZP'er** | Natural persons (Dutch law treats them as individuals) | **Opt-in** required. Cold email prohibited unless prior consent OR existing customer relationship for similar products/services |
| Sole director of a BV with `info@bedrijf.nl` | Treated by company (BV) | Opt-out OK |
| Sole director of a BV with `jan@bedrijf.nl` | Borderline — generic enough? | Conservative: BV opt-out; safer: treat as personal |

**Practical rule**: filter the outbound list strictly to BVs. KvK API provides this filter via `rechtsvorm` field. Eenmanszaak and VOF go on a different channel (LinkedIn DM is still tricky — see below — but content + inbound is safe).

## LinkedIn outreach legality

AP treats commercial LinkedIn messages as "digital direct marketing" under Tw 11.7 — **same rules as email**.

- Connection request with no commercial pitch: generally OK (no marketing message yet)
- DM after acceptance with commercial pitch to a sole-trader profile: **opt-in territory**
- DM with commercial pitch to a BV-employee profile (e.g., "Jan, owner of Klusbedrijf BV"): opt-out OK + LIA + opt-out link

Practical impact: LinkedIn outreach also filtered to BV-owner profiles in Phase 1.

## WhatsApp Business outreach

Unambiguously covered by Tw 11.7. Cold WhatsApp to a number obtained without consent is **non-compliant** for sole traders and **high-risk** even for BV contacts (the number is usually personal). 

**Verdict: do not cold WhatsApp.** Use WhatsApp only after a relationship is established (inbound lead, signed prospect, existing client).

## Cold calling

From **1 July 2026** the soft opt-in dies entirely (Wet ongewenste telemarketing). Calling sole traders without consent is already prohibited. ACM is actively enforcing. The founder's "no cold calling" constraint already aligns with the law — no change needed.

## What "legitimate interest" requires (Art. 6(1)(f) AVG)

Three-part test, documented in a Legitimate Interest Assessment (LIA):

1. **Purpose test** — is the interest legitimate? (Yes: B2B marketing of a relevant product to a relevant audience.)
2. **Necessity test** — is processing necessary for that interest? (Yes: no less-intrusive way to reach a public business email.)
3. **Balancing test** — does our interest override the data subject's rights? Factors: reasonable expectations of the recipient, public availability of the address, easy opt-out, no sensitive data.

LIA template: 1-page Notion doc per outbound campaign. Date, purpose, audience source, balancing notes, opt-out mechanism, retention.

## Required artefacts before first send

1. **LIA per campaign** (saved in Notion + linked from the campaign in n8n)
2. **Records of Processing Activities (Art. 30 AVG)** — outbound is one entry
3. **Privacy policy** at `klantkraan.nl/privacy` covering outbound processing
4. **Sender identification** in every email (real name, KvK, company)
5. **One-click opt-out** in body (reply "STOP" + List-Unsubscribe header for Gmail/Outlook)
6. **Suppression list** — n8n + Postgres `suppressions` table, queried before every send

## EU AI Act note (separate from outbound, but related)

If we ever use AI to generate hyper-personalised outbound at scale, the AP could argue the processing is "systematic + at scale" → may push the relationship into a higher-risk band. We:
- Personalise within reason (token replacement, light context-aware spinning)
- Do NOT feed personal data scraped from LinkedIn to an LLM for "deep personalisation"
- Do NOT use AI-generated voice for cold outreach

## What this means operationally

| Activity | Allowed | Filter |
|---|---|---|
| Cold email to `info@plumber-bv.nl` | Yes (opt-out) | BV only |
| Cold email to `jan@plumber-eenmanszaak.nl` | **No** | Excluded by KvK rechtsvorm filter |
| LinkedIn connection request, no pitch | Yes | All |
| LinkedIn DM, commercial pitch | Yes (opt-out) | BV-owner profiles only |
| Cold call | **No** | All |
| Cold WhatsApp | **No** | All |
| Newsletter signup → drip | Yes | Anyone who opted in |
| Lead-form submission → personal follow-up | Yes | Anyone who submitted |

## Compliance triggers (when to re-check)

- Any new outbound channel (e.g., considering Telegram in 2027) → re-do the legal analysis
- Any change in Tw 11.7 or AVG enforcement guidance (annual check)
- Expansion to UK → UK ICO PECR rules differ; corporate-subscriber loophole applies but documentation differs
- Expansion to Spain → Spanish AEPD has its own quirks; reverse opt-in like NL eenmanszaak

## Source

- AP digital direct marketing guidance: https://www.autoriteitpersoonsgegevens.nl/en/themes/internet-and-smart-devices/advertising/digital-direct-marketing
- Telemarketing soft opt-in ending July 2026: https://www.considerati.com/publications/end-of-soft-opt-in-for-telemarketing-new-rules-starting-july-2026/
- Fieldfisher overview NL telemarketing: https://www.fieldfisher.com/en/insights/new-rules-for-telemarketing-in-the-netherlands
- KvK direct marketing and the law: https://www.kvk.nl/en/about-kvk/direct-marketing-and-the-law/
- CMS new Dutch B2B spam law: https://cms.law/en/nld/publication/dutch-new-law-prohibits-b2b-spam
- Dealfront EU cold-emailing guide 2026: https://www.dealfront.com/blog/essential-guide-to-cold-calling-and-emailing/
