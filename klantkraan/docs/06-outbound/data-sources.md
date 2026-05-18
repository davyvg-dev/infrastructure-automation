# Data Sources for the Outbound List

> Target: build a list of ~5,000 BV-registered loodgieters + dakdekkers across NL with name, email, phone, KvK number, postcode. Realistic enriched cost: ~€15–25 per 1,000 leads.

## Source ranking

| Source | Cost | Output quality | Recommended use |
|---|---|---|---|
| **KvK Handelsregister API** | €6.40/mo subscription + €0.02/query (Zoeken free) | Authoritative for KvK + rechtsvorm filter + SBI | Primary — start every list here |
| **Outscraper (Google Maps)** | ~€3/1k base + ~€11/1k email enrichment | Name + website + phone + sometimes email | Best price/quality combo |
| **Apify Google Maps Scraper** | $4/1k base + $2/1k emails/socials | Customizable | If Outscraper has gaps |
| **PhantomBuster** | $69/mo, 20h runtime | LinkedIn data | Skip unless we also do LinkedIn automation |
| **Werkspot / Bouwnu / Installatie.nl directories** | Free | Low quality | Cross-reference only |
| **Trade-association member lists** | Mostly public on websites | High trust signal | Manual extraction at small scale |
| **Apollo / ZoomInfo** | $$$ | Mostly US-skewed, NL coverage thin | Avoid — wrong geography + GDPR provenance issues |

## KvK Handelsregister API (canonical first step)

Endpoint: `https://api.kvk.nl/`.

Pricing 2026: €6.40/mo subscription + €0.02 per query (Search-API). The simple Zoeken-API is free for low volumes.

Query for "loodgieter BVs in Randstad":

```
GET /api/v2/handelsregister/zoeken
  ?sbiCode=4322
  &rechtsvorm=BV
  &postcode=2000..3500
  &handelsnaam=*
```

Returns: KvK-nummer, handelsnaam, vestigingsadres, SBI, rechtsvorm, hoofdvestiging boolean, **Non-Mailing Indicator (NMI)**.

**Critical**: filter out NMI = true. The NMI legally only covers physical direct mail, but it's a strong signal of privacy preference. Honor it across all channels.

SBI codes to use:

| SBI | Description |
|---|---|
| 4322 | Loodgieters- en fitterswerk, installatie van verwarmings- en luchtbehandelingsapparatuur en sanitair |
| 4321 | Elektrische installatie |
| 4329 | Overige bouwinstallatie (incl. dakdekkers koud-dakwerk) |
| 4391 | Dakdekkers (warm-dakwerk + zink etc.) |

Use 4322 + 4391 for the primary list.

## Outscraper (Google Maps enrichment)

Why: KvK gives you the entity, but rarely a contact email. Outscraper Google-Maps scrape gives you the email + the live phone.

Workflow (n8n):
1. Query KvK for candidate entities by SBI + rechtsvorm + postcode.
2. For each, run `Outscraper /maps/search` with `query = "{handelsnaam} {plaats}"` + `language = nl`.
3. Outscraper returns: phone, website, social, sometimes email.
4. If still no email, use `Outscraper /emails-validator` with the website domain or `Anymailfinder/Dropcontact` waterfall.
5. Verify with `MillionVerifier` or `Reoon` (€0.0008–0.002 per check).
6. Insert into Postgres `leads` table with `verified_at`, `source`, `quality_score`.

Per-1,000-lead cost estimate:

| Step | Cost / 1k |
|---|---|
| KvK Search-API queries | ~€20 |
| Outscraper Maps base | €3 |
| Outscraper email enrichment | €11 |
| Email verification (MillionVerifier) | €1 |
| **Total per 1k enriched, verified leads** | **~€35** |

## Trade-association member lists

- **Techniek Nederland** — public member-finder at https://www.technieknederland.nl/zoek-bedrijf — ~30k members, scrapable with attribution
- **OnderhoudNL** — public member list at https://onderhoudnl.nl/ledenoverzicht
- **Bouwend Nederland** — public member-search at https://www.bouwendnederland.nl/leden

These are high-quality signal — these owners are organized, business-minded. Cross-reference KvK list for higher win rate.

## Werkspot / Bouwnu / Installatie.nl

Lower quality (often eenmanszaak, often new/temporary listings). Use only to:
- Cross-reference whether a known BV is active
- Spot trending sub-niches (e.g., "warmtepomp installatie" volume by region)

Don't scrape as primary source.

## What NOT to use

| Source | Why not |
|---|---|
| **Apollo / ZoomInfo bulk export** | US-biased, lack documented Dutch GDPR provenance → AP would push the burden of proof onto us |
| **Buying lists from data brokers (Datatrek etc.)** | Provenance opaque, often duplicated, often illegally collected |
| **LinkedIn scrape → email finder** for eenmanszaak owners | Opt-in regime — non-compliant. AP has fined for exactly this. |
| **WhatsApp number scrape** | No legitimate-interest defence works under Tw 11.7 |
| **KvK list ignoring NMI** | Explicit prohibition for direct mail; signals bad faith regardless of channel |

## Suppression list (mandatory)

A single Postgres `suppressions` table covers all outbound channels:

```sql
CREATE TABLE suppressions (
  identifier_hash TEXT PRIMARY KEY, -- SHA-256 of email or phone-e164
  identifier_type TEXT CHECK (identifier_type IN ('email','phone')),
  reason          TEXT, -- 'STOP-reply','manual','unsubscribe-link','complaint','NMI'
  source          TEXT, -- channel where suppression originated
  added_at        TIMESTAMPTZ DEFAULT now()
);
```

n8n checks this table before EVERY send (email, SMS, LinkedIn DM). One source of truth.

## List hygiene cadence

| Cadence | Action |
|---|---|
| Daily | Refresh suppressions from incoming "STOP" replies, AP-Bel-Me-Niet check |
| Weekly | Re-verify the next-month send list via MillionVerifier |
| Monthly | Re-fetch NMI flags from KvK; suppress any flipped to NMI = true |
| Quarterly | De-duplicate; remove entries > 12 months old without engagement |
| Annually | Re-do the LIA balancing assessment per campaign type |

## Source

- KvK Developer Portal pricing: https://developers.kvk.nl/nl/pricing
- KvK Non-Mailing Indicator: https://www.kvk.nl/en/about-the-business-register/the-non-mailing-indicator/
- Outscraper pricing: https://outscraper.com/pricing/
- Apify Google Maps Scraper: https://blog.apify.com/best-google-maps-scrapers/
- B2B database NL comparison: https://syncgtm.com/blog/best-b2b-database-netherlands
- B2B data compliance index: https://b2bdataindex.com/compliance/
- Techniek Nederland member finder: https://www.technieknederland.nl/zoek-bedrijf
- OnderhoudNL leden: https://onderhoudnl.nl/ledenoverzicht
- Bouwend Nederland leden: https://www.bouwendnederland.nl/leden
