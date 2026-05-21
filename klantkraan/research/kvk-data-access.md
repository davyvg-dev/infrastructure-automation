# KvK Data Access: BV-Filtered Prospect Database for Dutch Trades

_Research date: 2026-05-21. Target: BVs only, niches installateur / loodgieter / dakdekker / aannemer / schilder, ≥1 FTE._

---

## Executive summary

KvK's free **Open Dataset Basis Bedrijfsgegevens** (CC BY 4.0) contains BV/NV legal form and SBI codes but strips company names and full addresses — making it useful for population sizing, not for direct outreach. The cheapest viable CLI path to a named, filterable, exportable BV prospect list is **Ad Hoc Data** at €0.08/record (no subscription required for one-off pulls), or their €55/month subscription for ongoing refreshes. Third-party resellers (BoldData/CompanyData, Ad Hoc Data) all draw from the KvK Handelsregister and support BV + SBI filtering natively. The AVG/GDPR legal basis for B2B outreach to BVs via legitimate interest is defensible, but cold email to natural persons (eenmanszaak/ZZP) is prohibited without prior consent — making the BV-only filter legally necessary, not just a business preference. Population across the five niches is approximately 5,000–15,000 BVs with ≥1 FTE total.

---

## 1. KvK Handelsregister Data Products

### 1a. Open Dataset Basis Bedrijfsgegevens (Free)

- **What's included:** Active/inactive flag, insolvency code, legal form (BV or NV only — eenmanszaak excluded), first two digits of postcode, SBI activity codes, country. Delivered as a daily-updated CSV ZIP.
- **What's excluded:** Company name, full KvK number, complete address, employee count, contact details.
- **Price:** Free under Creative Commons BY 4.0.
- **Refresh:** Every working day.
- **Access:** Bulk ZIP download via `https://developers.kvk.nl/nl/documentation/open-dataset-basis-bedrijfsgegevens-api`. No API key required for the download; there is a lookup-by-KvK-number endpoint.
- **ToS restrictions:** Enriching the dataset so that individual natural persons can be identified is prohibited. Forwarding data to third parties is not allowed. Commercial use is otherwise permitted with attribution.
- **Verdict:** Good for building a BV universe by SBI code at postcode-region level. Not usable alone for outreach (no names or full addresses).

### 1b. KvK API (Zoeken / Basisprofiel / Vestigingsprofiel)

- **What's included:** Full company name, address, KvK number, SBI codes, legal form, trade names, branch locations. The Zoeken (search) endpoint is free per call. Basisprofiel and Vestigingsprofiel cost €0.02/query.
- **Price as of 1 Jan 2026:** €6.40/month subscription fee (VAT-exempt) + €0.02 per Basisprofiel or Vestigingsprofiel call. Search (Zoeken) endpoint: €0.00/call. [3.5% CPI indexation applied from 2025 tariffs.]
- **Refresh:** Live Handelsregister data.
- **Access:** REST/JSON. Sign up at `developers.kvk.nl`. Rate limit: 100 queries per 5 minutes.
- **ToS:** Non-Mailing Indicator (NMI) must be respected for postal direct mail (see Section 5). Forwarding or reselling retrieved data is prohibited. B2B prospecting within your own CRM is allowed.
- **Verdict:** Best for enriching a KvK-number list you already have, or for automated company lookups. Not designed for bulk prospecting queries by SBI code.

### 1c. KvK Mutatieservice API

- **What's included:** Push notifications when any company record in the Handelsregister changes (new registrations, address changes, dissolution, etc.).
- **Price as of 1 Jan 2026:** €1,279/year (flat).
- **Access:** REST/JSON webhook. Subscription via `developers.kvk.nl`.
- **Use case:** Keeping a prospect database fresh — new BV registrations in target SBI codes arrive automatically.

### 1d. KvK Dataservice (HR-DS) — SOAP/PKI Legacy

- **What's included:** Full extract data including officials, UBO (authorised institutions only), certified PDF extracts.
- **Price as of 1 Jan 2026:** €1,279 one-time connection fee + €9.60 per Business Register extract requested. [Same 3.5% 2026 indexation applies.]
- **Access:** SOAP-WS, requires PKI certificates (6–8 week procurement). XML output.
- **Verdict:** Disproportionate setup cost and complexity for a launch-phase prospecting task. Skip unless you need legally certified extracts.

### 1e. KvK Open Dataset Jaarrekeningen (Annual Accounts)

- **What's included:** XBRL financial statements filed by BVs. Revenue, balance sheet data.
- **Price:** Free (separate CC BY 4.0 dataset).
- **Access:** Bulk XML download, multiple files due to size. Via `data.overheid.nl`.
- **Use case:** Qualifying prospects by revenue after initial list build.

---

## 2. SBI 2008/2025 Codes per Niche

KvK migrated from SBI 2008 to **SBI 2025** during the weekend of 6–7 September 2025. SBI 2025 adds a fifth digit (zero appended) to existing 4-digit codes. Both code sets are cross-referenceable. Use SBI 2025 for any new API calls against the current Handelsregister.

| Niche | SBI 2008 code | SBI 2025 equivalent | Label |
|---|---|---|---|
| Elektrotechnisch installateur | **43.21** | **43210** | Elektrotechnische bouwinstallatie |
| Werktuigbouwkundig installateur (HVAC/klimaat) | **43.22.2** | **43222** | Installatie van verwarmings- en luchtbehandelingsapparatuur |
| Loodgieter (sanitair) | **43.22.1** | **43221** | Loodgieters- en fitterswerk; installatie van sanitair |
| Overige bouwinstallatie (incl. mechanisch) | **43.29** | **43290** | Overige bouwinstallatie |
| Dakdekker | **43.91** | **43910** | Dakdekken en bouwen van dakconstructies |
| Aannemer algemeen (burgerlijke & utiliteitsbouw) | **41.20** | **41200** | Algemene burgerlijke en utiliteitsbouw |
| Aannemer woningbouw / projectontwikkeling | **41.10** | **41100** | Projectontwikkeling |
| Schilder en glaszetter | **43.34** | **43340** | Schilderen en glaszetten |

**Priority codes for Klantkraan targeting:**
- Installateur: query `43210` + `43222` + `43290` (catch HVAC/klimaat)
- Loodgieter: `43221` (often overlaps with 43.22 parent)
- Dakdekker: `43910`
- Aannemer: `41200` (primary); optionally `41100`
- Schilder: `43340`

**Note:** Many companies register multiple SBI codes. A single BV may appear under both `43221` and `43222`. Deduplicate by KvK number.

---

## 3. Population Estimates

These are total company counts (all legal forms). BV share is typically 15–25% in specialized construction trades; eenmanszaak/ZZP dominate numerically.

| Niche | SBI code | Total companies (all legal forms, ~Q1 2026) | Estimated BV share | Estimated BV count (≥1 FTE) |
|---|---|---|---|---|
| Installateur (elektrotechnisch + HVAC) | 43.21 + 43.22 | ~41,950 (SBI group 4321+4322 combined) | ~15% BV | ~3,000–4,500 BVs; subset ≥1 FTE likely 2,000–3,000 |
| Loodgieter | 43.22.1 | Subset of above ~10,000 | ~12% | ~800–1,200 |
| Dakdekker | 43.91 | 6,255 (Q1 2026, FirmFocus/CBS) | ~18% | ~700–1,000 |
| Aannemer (41.20) | 41.20 | Part of >97,000 gespecialiseerde bouw total; 41.20 alone est. 8,000–12,000 | ~25% | ~1,500–2,500 |
| Schilder | 43.34 | est. 12,000–15,000 | ~10% | ~800–1,200 |

**Total addressable BV universe across all 5 niches: approximately 5,800–9,900 BVs with ≥1 FTE.**

For launch targeting (hundreds to low-thousands), the realistic active prospect pool — after filtering for ≥2 FTE, active trading, no NMI flag — is 2,000–4,000 companies.

_Sources: FirmFocus sector data (Q1 2026); CBS table 81589NED; CompanyData/BoldData installateur count (30,827 total installateurs, all legal forms); Marktdata dakdekkerbedrijven growth report._
[unverified: exact BV % per niche — CBS table 81588NED (bedrijven naar rechtsvorm) provides this but requires StatLine download to get 4-digit SBI + rechtsvorm cross-tab. The percentages above are estimated from industry knowledge and should be validated before making purchasing commitments.]

---

## 4. Third-Party Data Resellers

### Ad Hoc Data (adhocdata.nl)

- **Coverage:** Full Dutch Handelsregister + enrichment (building data, energy labels, email addresses).
- **BV/SBI filter:** Yes — explicit legal form filter and SBI code tree. Employee count filter available.
- **Pricing (2025, verified on site):** €0.08/record (pay-per-record, no subscription). Subscription from €55/month for 2,500 records. Full subscription with all fields (Complete tier): €75/month.
- **Export:** CSV/Excel, delivered within 24 hours.
- **Refresh:** Regular, draws from KvK + enrichment layers.
- **CLI-friendly:** No native CLI, but exports to CSV which is scriptable. No dashboard dependency for one-off pulls.
- **Verdict:** Best value for a one-off launch list. ~€40–80 for a 500–1,000 BV target list.

### CompanyData.com (formerly BoldData)

- **Coverage:** 5+ million Dutch company locations from Handelsregister.
- **BV/SBI filter:** Yes — legal form, SBI code, employee count, region.
- **Pricing:** Minimum order ~€425 for ~1,000 records (includes name, address, phone, email, KvK number, legal form). Per-record cost ~€0.43 at minimum tier — higher than Ad Hoc Data.
- **Export:** Excel within 24 hours.
- **Refresh:** Live KvK data.
- **Verdict:** More expensive than Ad Hoc Data for small volumes. Better brand recognition; may have higher email coverage.

### Altares Dun & Bradstreet Netherlands (altares.nl)

- **Coverage:** Global D-U-N-S network; NL coverage via KvK + proprietary enrichment.
- **BV/SBI filter:** Yes via D&B Hoovers and D&B Market Insight products (prospect filtering on many criteria).
- **Pricing:** No public pricing. Enterprise contracts only. [unverified — contact required for quote. Typically €5,000+/year for SME access.]
- **Export:** Via CRM integrations or exports.
- **Verdict:** Overkill for launch phase. Revisit at scale.

### Creditsafe Netherlands

- **Coverage:** KvK-based + financial ratings.
- **Note:** Acquired Graydon NL from Atradius — Graydon's Dutch data is now part of Creditsafe.
- **BV/SBI filter:** Yes — supports legal form and industry filtering.
- **Pricing:** [unverified — no public pricing found for 2025/2026. Contact required. Estimated €1,500–4,000/year for prospect list access based on Belgian/UK public pricing.]
- **Export:** CSV/Excel.
- **Verdict:** Credible option, especially if you also need credit risk data on prospects. Pricing opaque; requires sales contact.

### Company.info (companyinfo.nl)

- **Coverage:** NL Handelsregister + enrichment.
- **NMI handling:** Company.info explicitly states it respects the Non-Mailing Indicator (NMI) — NMI-flagged companies are filtered out from their prospect exports automatically.
- **BV/SBI filter:** Yes.
- **Pricing:** [unverified — no public 2025/2026 pricing page found. Historically ~€0.10–0.20/record for prospect lists.]
- **Verdict:** NMI-compliance built-in is a plus; reduces legal overhead. Pricing needs direct inquiry.

### OpenKvK.nl

- **Coverage:** Free, open, 5+ million active Dutch company locations since 2009. No registration required.
- **BV/SBI filter:** Open dataset is BV/NV only by definition. SBI filtering possible via the API.
- **Pricing:** Free.
- **Export:** API-based. Python package `OpenKVK` on PyPI. No bulk CSV download.
- **Limitation:** No contact details (email, phone). Useful for building a KvK-number list, then enriching via the paid KvK API or a reseller.
- **CLI-friendly:** Yes — Python library `pip install OpenKVK`, REST queries scriptable.

---

## 5. AVG/GDPR Legal Basis for B2B Prospecting Using KvK Data

### Applicable framework

The GDPR (AVG in Dutch) applies whenever you process personal data. For BVs, the general contact address (e.g., `info@bedrijf.nl`) is typically not personal data because it belongs to the legal entity. However, any data that identifies a natural person — including a sole trader's name, a named contact, or a private mobile number — is personal data subject to full GDPR protection.

**The BV-only filter is legally significant:** Outreach to a BV at a role-based address (not a named individual) sits in a lower-risk category than outreach to an eenmanszaak/ZZP, where the data necessarily relates to a natural person.

### Legitimate interest (Art. 6(1)(f) GDPR)

B2B outreach to companies can rely on **legitimate interest** as the legal basis when:
1. You have a genuine commercial interest (offering relevant services to the prospect's business).
2. The processing is necessary for that interest (i.e., you need the data to make contact).
3. The interest is not overridden by the data subject's fundamental rights.

The CJEU ruled in **KNLTB (C-621/22)** that commercial interests can qualify as legitimate interest — the AP's previous position that commercial interest was automatically excluded was wrong. The AP settled this point in 2025. This strengthens the legitimate interest basis for B2B prospecting.

### Channel-specific rules

| Channel | Rule |
|---|---|
| Physical mail (post) | Must respect NMI flag. NMI-flagged companies: do not mail. |
| Door-to-door | NMI applies. |
| Email (cold) | **Telecomwet / Spam ban applies.** For BVs (legal entities), cold email to role-based addresses is in a grey zone — the AP considers the risk lower than for natural persons, but prior consent or an existing relationship is safest. Cold email to named individuals at any company requires prior consent or a prior business relationship. |
| Phone | KvK does not publish phone numbers in the open dataset. Phone numbers from resellers require the same legitimate interest assessment. |

### Non-Mailing Indicator (NMI)

Any company can request an NMI from KvK (free). The NMI appears on Business Register extracts and in paid data deliveries from resellers. **NMI restricts physical mail and door-to-door visits only — it does not restrict email or phone.** Any list purchased from KvK-compliant resellers (e.g., Company.info) will have NMI-flagged records pre-filtered.

### AP enforcement context

The AP has not (as of May 2026) issued fines specifically targeting B2B prospecting from KvK data. The 2022 KvK court proceedings concerned bulk data resale by third parties, not end-use B2B prospecting. The AP's guidance on B2B marketing notes reduced risk for outreach to legal entities versus natural persons. No recent Dutch enforcement actions targeting BV-to-BV prospecting were found in this research.

**Bottom line:** Klantkraan's BV-only, role-address, opt-out-respecting outreach model is legally defensible under legitimate interest. Document your balancing test. Provide clear opt-out in every touchpoint. Do not cold email named individuals without consent.

_Sources: bedrijfsdata.nl AVG B2B analysis; GDPRWise.eu; KvK NMI page; CJEU KNLTB ruling C-621/22; AP website._

---

## 6. Free / Low-Cost Alternatives

### KvK Open Dataset + OpenKvK.nl (free)

- **Feasibility:** High for list building. Download the daily CSV, filter `rechtsvormCode = BV`, filter `activiteiten` array for target SBI codes, extract the KvK numbers. Then query the KvK Basisprofiel API (€0.02/call) for each KvK number to get the actual name and address.
- **Cost estimate:** 2,000 records × €0.02 = €40 in API calls + €6.40/month subscription.
- **ToS risk:** Low — this is the intended use of the official KvK API.
- **Missing:** Email addresses, phone numbers. Requires separate enrichment.

### OpenKvK.nl (free, unofficial)

- **Feasibility:** Medium. Provides company name and address for free. No email/phone.
- **ToS risk:** OpenKvK.nl republishes open KvK data — usage is within CC BY 4.0 terms. Not a scraping risk.
- **CLI-friendly:** Yes, via `pip install OpenKVK` or direct REST calls.

### Scraping public KvK pages (kvk.nl/zoeken)

- **Feasibility:** Low. KvK actively blocks scrapers. ToS explicitly prohibits automated scraping of the search portal.
- **ToS risk:** High — direct violation of KvK terms. Do not do this.

### OpenStreetMap / Google Maps business data

- **Feasibility:** Low for B2B prospecting. OSM business data is sparse and unstructured for NL trades. No legal form data available.
- **ToS risk:** Google Maps Terms prohibit scraping. OSM data is free but incomplete.

### OpenCorporates (opencorporates.com)

- **Coverage:** Aggregates KvK data. Free tier allows lookups; bulk access requires paid plan.
- **BV filter:** Yes — legal form searchable.
- **Pricing:** [unverified for 2025/2026 NL bulk access — contact required.]
- **Verdict:** Useful for one-off lookups but not cost-effective for bulk NL prospecting vs. native KvK options.

---

## 7. Recommendation

### Situation

- Target: ~2,000–4,000 BV prospects across 5 niches, enriched with name + address + ideally email.
- Founder: prefers CLI, no dashboards, minimal recurring cost at launch.
- Budget: minimize at launch; acceptable to spend more at 12 months if ROI proves.

### Recommended path

**Month 1 (launch): Ad Hoc Data one-off export**

1. Go to `adhocdata.nl/en/leadlist`, build a selection: legal form = BV, SBI codes = `43210, 43221, 43222, 43290, 43910, 41200, 43340`, employee count ≥ 1.
2. Download CSV. Estimated record count: 3,000–6,000 BVs. At €0.08/record: **€240–€480 one-time cost**.
3. Import into a CRM or simple SQLite/CSV workflow. No dashboard dependency after export.
4. Run deduplication by KvK number (bash: `sort -t, -k<kvk_col> -u`).

**Month 1 cost estimate: €240–€500 total.**

**Months 2–12 (refresh): KvK Open Dataset + KvK API hybrid**

1. Daily: download the free KvK Open Dataset CSV (BV + SBI filter in Python/bash).
2. Diff against your existing list to find new BV registrations in target SBI codes.
3. For each new KvK number: call KvK Basisprofiel API (€0.02) to get name + address.
4. Estimated new BVs per month in 5 niches combined: 50–150.
5. Monthly API cost: ~50–150 × €0.02 = **€1–€3/month** in query costs + **€6.40/month** subscription.

**Months 2–12 total: ~€85 (subscription) + €10–30 (API calls) + €0 (open data) = ~€100–€115 for 11 months.**

**12-month total cost estimate: €340–€615.**

### Alternative: Ad Hoc Data monthly subscription

- €55/month × 12 = **€660/year** — includes 2,500 fresh records/month, pre-enriched with email where available. Simpler, no coding required. Worthwhile if email enrichment matters.

### What to avoid

- KvK Dataservice (HR-DS): €1,279 setup fee alone exceeds the full-year CLI path.
- Altares / Creditsafe: enterprise pricing, dashboards, no CLI export.
- Scraping kvk.nl: ToS violation, fragile, not worth the legal risk.

---

## Sources & Freshness

All URLs retrieved May 2026.

| Source | URL | Last verified |
|---|---|---|
| KvK 2026 tariff announcement | https://www.kvk.nl/pers/kvk-past-tarieven-aan-per-1-januari-2026/ | 2026-05-21 |
| KvK API pricing page | https://developers.kvk.nl/pricing | 2026-05-21 |
| KvK Dataservice product page | https://www.kvk.nl/en/ordering-products/kvk-dataservice/ | 2026-05-21 |
| KvK Open Dataset documentation | https://developers.kvk.nl/nl/documentation/open-dataset-basis-bedrijfsgegevens-api | 2026-05-21 |
| KvK Open Dataset product page | https://www.kvk.nl/en/ordering-products/kvk-business-register-open-data-set/ | 2026-05-21 |
| KvK Terms of Use (Business Register) | https://www.kvk.nl/en/about-the-business-register/terms-of-use-business-register/ | 2026-05-21 |
| KvK Non-Mailing Indicator | https://www.kvk.nl/en/about-the-business-register/the-non-mailing-indicator/ | 2026-05-21 |
| KvK SBI overview | https://www.kvk.nl/over-het-handelsregister/overzicht-standaard-bedrijfsindeling-sbi-codes-voor-activiteiten/ | 2026-05-21 |
| KvK SBI 2025 revision for data users | https://www.kvk.nl/en/about-the-business-register/sbi-revision-for-users-kvk-data/ | 2026-05-21 |
| SBI codes list (FaillissementsDossier) | https://www.faillissementsdossier.nl/nl/sbi-codes.aspx | 2026-05-21 |
| CBS Standard Industrial Classifications | https://www.cbs.nl/en-gb/our-services/methods/classifications/activiteiten/standard-industrial-classifications | 2026-05-21 |
| CBS bedrijven bedrijfstak table 81589NED | https://www.cbs.nl/nl-nl/cijfers/detail/81589NED | 2026-05-21 |
| CBS bedrijven rechtsvorm table 81588NED | https://www.cbs.nl/nl-nl/cijfers/detail/81588NED | 2026-05-21 |
| FirmFocus bouwinstallatie sector (Q1 2026) | https://www.firmfocus.biz/NL/BI/branche/bouwinstallatie | 2026-05-21 |
| FirmFocus dakdekken sector (Q1 2026) | https://www.firmfocus.biz/NL/BI/branche/dakdekken-en-bouwen-van-dakconstructies | 2026-05-21 |
| CompanyData installateurs count | https://bolddata.nl/nl/bedrijven/nederland/installateurs/ (redirects to companydata.com) | 2026-05-21 |
| Altares D&B products | https://www.altares.nl/en/products/ | 2026-05-21 |
| Ad Hoc Data pricing and filters | https://www.adhocdata.nl/en/leadlists | 2026-05-21 |
| Ad Hoc Data home page | https://www.adhocdata.nl/en | 2026-05-21 |
| OpenKvK.nl | https://openkvk.nl/ | 2026-05-21 |
| OpenKVK PyPI package | https://pypi.org/project/OpenKVK/ | 2026-05-21 |
| Creditsafe acquires Graydon | https://www.biia.com/creditsafe-acquires-b2b-information-services-company-graydon-from-atradius/ | 2026-05-21 |
| Company.info NMI handling | https://companyinfo.nl/veelgestelde-vragen/hoe-gaat-company-info-om-met-de-non-mailing-indicator-nmi/ | 2026-05-21 |
| AVG B2B marketing analysis | https://www.bedrijfsdata.nl/privacy-en-bedrijfsdata-wat-mag-wel-en-niet-bij-b2b-marketing/ | 2026-05-21 |
| GDPRWise B2B GDPR NL | https://gdprwise.eu/nl/kennisbank/verplichtingen/b2b-gdpr-van-toepassing/ | 2026-05-21 |
| KNLTB CJEU case C-621/22 (AP settlement) | https://www.ictrecht.nl/en/blog/2025-in-vogelvlucht-wat-is-er-in-het-afgelopen-jaar-allemaal-gebeurd | 2026-05-21 |
| KvK direct marketing page | https://www.kvk.nl/over-kvk/direct-marketing-en-regelgeving/ | 2026-05-21 |
| Marktdata dakdekkerbedrijven growth | https://www.marktdata.nl/nieuws/Sterke-groei-aantal-dakdekkerbedrijven | 2026-05-21 |
| NextBI leadlijsten kopen | https://nextbi.nl/leadlijsten-kopen/ | 2026-05-21 |
| BoldData minimum order pricing | https://www.adhocdata.nl (cross-referenced via search results) | 2026-05-21 |
