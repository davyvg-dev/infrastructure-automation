# Klantkraan — Legal Outreach Landscape (NL/EU)
**Status as of 2026-05-21. Review after any AP, ACM, or EU Commission publication.**

---

## Executive Summary (5 lines)

1. **Cold calling BVs without prior consent is lawful** under Dutch Telecommunicatiewet as long as the number is publicly disclosed and the BV is the intended end-user of the service — the BV filter is the correct call.
2. **Eenmanszaak and VOF are explicitly protected** against unsolicited telemarketing the same as consumers; calling them without opt-in violates Tw art. 11.7 (post-July 2021) and AVG simultaneously.
3. **Cold B2B email to BVs** can rely on legitimate interest (GDPR art. 6(1)(f)) with a documented Legitimate Interest Assessment (LIA), but director-level email addresses are personal data after CJEU C-710/23 (April 2025) and require full AVG handling.
4. **EU AI Act art. 50 transparency obligation applies from 2 August 2026**: every AI voice agent interacting with a natural person must disclose its AI nature in the opening seconds — keeping the Synthflow disclosure always on is mandatory, not optional.
5. **Recording AI voice calls** in NL: companies face stricter rules than individuals; AVG-basis (legitimate interest or consent) is required, callers must be informed, and voice data is personal data requiring a DPIA if processed at scale.

---

## 1. EU AI Act Article 50 — Transparency Obligations

### 1.1 In-Force Date

Article 50 enters application on **2 August 2026**. The broader AI Act entered into force on 1 August 2024 (published OJ L 2024/1689); prohibited practices applied from 2 February 2025; GPAI obligations from 2 August 2025. Article 50 belongs to the third wave: **2 August 2026**.

Source: EU AI Act art. 113(b); Eur-Lex OJ L 2024/1689.

### 1.2 Exact Disclosure Obligation for Voice Agents

Article 50(1) (verbatim, official EN text):

> "Providers shall ensure that AI systems intended to interact directly with natural persons are designed and developed in such a way that the natural persons concerned are informed that they are interacting with an AI system, unless this is obvious from the point of view of a natural person who is reasonably well-informed."

Key implementation details confirmed by EU Commission guidance (December 2025 draft Code of Practice):

- Disclosure must occur **at the latest at the time of the first interaction**.
- For voice agents: disclosure must be **audible**, in the language of the call, within the first seconds of the opening.
- A Code of Practice on AI-generated content is expected June 2026 (weeks before enforcement); it will add labeling standards for audio output.
- "Obvious from context" is a **narrow exception** — a voice that sounds human and introduces itself by a human name does not qualify. A clearly synthetic/robotic voice may qualify but is legally risky to rely on without documented reasoning.

### 1.3 Enforcement Guidance — EU Commission and Dutch AP/ACM (to May 2026)

- The EU Commission published the first draft Code of Practice on 17 December 2025; near-final version expected June 2026. No binding sectoral guidelines for voice agents yet.
- No Dutch AP-specific guidance on art. 50 enforcement has been published as of 2026-05. The AP enforces AVG/GDPR; AI Act enforcement in NL falls primarily under the **ACM** (designated national market surveillance authority for certain AI Act obligations) and potentially a new designated AI authority. **Watch for NL designation announcement in 2026.**
- No enforcement actions under art. 50 have been reported as of 2026-05 (the provision is not yet in force).

**Status: Statutory text settled. Implementing detail (Code of Practice) pending final publication June 2026. No case law yet.**

### 1.4 Penalty Structure

Article 50 non-compliance: **up to €15 million or 3% of global annual turnover**, whichever is higher (AI Act art. 99(4)).

### 1.5 Implications for Synthflow-Style Outbound/Inbound Voice Agents

- **Outbound calls** from an AI voice agent: the disclosure fires on the first utterance of the call. The agent cannot open with "Goedemiddag, u spreekt met Lisa van Klantkraan" without also immediately stating it is an AI system.
- **Inbound calls** (prospect-initiated): same rule applies — first interaction must include the disclosure.
- **Transfer from AI to human**: if the agent hands off to a human agent, the disclosure obligation on the AI leg is already satisfied; the human leg obviously does not need the AI disclosure.
- **Synthflow "AI disclosure" toggle**: this must be enabled at all times. Disabling it post-August 2026 constitutes a direct violation of art. 50 with no de minimis exception.

---

## 2. Dutch Telemarketing Rules — Telecommunicatiewet

### 2.1 Statutory Framework

Controlling statute: **Telecommunicatiewet (Tw) art. 11.7**, as amended effective **1 July 2021** (opt-in system replacing the old opt-out / bel-me-niet-register). Further amendment effective **1 July 2026** (abolition of soft opt-in for consumer calls; see 2.5 below).

Enforcer: **ACM** (Autoriteit Consument en Markt). Fine authority: up to €900,000 per violation or higher under UAVG/AVG for data-related breaches.

### 2.2 B2B vs Consumer — Current State

| Entity type | Cold call without prior consent? | Legal basis |
|---|---|---|
| Consument (natural person, private) | No — explicit opt-in required | Tw art. 11.7(1) |
| Eenmanszaak / VOF / maatschap | No — same protection as consumer | Tw art. 11.7(1) + AVG (natural person data) |
| BV / NV / vereniging / coöperatie / stichting (rechtspersoon) | **Yes, conditionally** | Tw art. 11.7(5) — rechtspersonen are excluded from the consumer protection scope |

**Conditions for a permitted cold call to a BV:**

1. The publicly disclosed phone number was disclosed by the BV for commercial contact (e.g., listed on KvK extract, website, or business directory without NMI flag).
2. The BV itself (not a natural person employed there) is the intended end-user/purchaser of the product or service.
3. The caller must identify themselves, the company they represent, and the commercial purpose of the call **at the start of the call**.
4. Automated calling systems (robocalls without a live agent) are still restricted — but an AI voice agent that functions as a live conversational agent, discloses it is AI, and represents a real business offer to a BV is not automatically prohibited. **This is a gray area; no ACM ruling has specifically addressed AI voice agents to BVs.**

### 2.3 Bel-me-niet-register — Current Status

The original opt-out register was **superseded by the opt-in system on 1 July 2021**. The register still formally exists for consumer numbers and can still be checked, but it is operationally secondary — the primary rule is now "no call without opt-in" for consumers/eenmanszaak. For BVs, the register is irrelevant (BVs are not in scope for consumer protections).

Source: Business.gov.nl (official government portal); ACM enforcement publications.

### 2.4 BV vs Eenmanszaak — Calling Rules in Plain Terms

**BV:** Lawful to call cold (outbound, no prior consent) if: public number, BV is end-user, caller identifies upfront, and call is not automated mass-dialing. AI voice agent calling a BV's listed number about relevant B2B services = **permitted under current law**, subject to AI Act art. 50 disclosure from August 2026.

**Eenmanszaak:** The owner is a natural person — the business name, address, phone, and email in KvK are that person's personal data (AP confirmed; same as consumer for Tw purposes). Cold calling requires **explicit prior opt-in**. No exceptions. Same result as calling a consumer.

**VOF:** Same as eenmanszaak — partners are natural persons, protected.

### 2.5 July 2026 Amendment

From **1 July 2026**: soft opt-in (calling existing customers without explicit consent based on prior purchase relationship) is abolished for commercial telephone outreach. Exceptions: charities, political parties, press/media subscriptions.

This does **not change** the BV-vs-eenmanszaak distinction. BVs remain outside the consumer protection scope. The amendment primarily tightens consumer/eenmanszaak rules.

### 2.6 ACM Enforcement — Last 24 Months (2024-2025)

- **March 2024**: ACM fined **Global Marketing Bridge** and its directors **€515,000** for misleading energy contract sales calls — failure to state commercial purpose at call opening. Directors fined personally.
- **March 2024**: ACM fined **Allround Hollands Energie B.V. (HEM)** **€1,100,000** for misleading consumer telemarketing (energy sector).
- **April 2025**: ACM audit programme launched; energy and telecom sectors primary targets. ACM board member Manon Leijten stated telemarketing is "a persistent problem" requiring immediate change.
- **July 2025**: Post-audit enforcement expected. ACM has indicated it will pursue the contracting business (not just the contracted telemarketer) for chain-liability violations.

Pattern: ACM targets (1) failure to disclose purpose at opening, (2) inability to demonstrate consent, (3) energy and telecom sectors. No published enforcement against AI-specific voice agents yet.

---

## 3. Cold Email to BVs Under AVG/GDPR

### 3.1 Legal Basis — Legitimate Interest

GDPR art. 6(1)(f) (legitimate interest) is the standard basis for B2B cold email in NL. Requirements (three-part test):

1. **Legitimate interest exists**: commercial interest qualifies — confirmed by CJEU in KNLTB judgment (4 October 2024, C-252/21 context). The Dutch AP had previously argued commercial interests alone could not suffice; the CJEU overruled that position.
2. **Processing is necessary**: email outreach must be the proportionate means — not mass untargeted blasting; targeted by sector, company size, relevance to the offer.
3. **Interests of data subject do not override**: for a BV-level email address (info@bv.nl), this balancing typically favors the sender given low privacy impact. For a director's personal email, the balance is closer (see 4.3).

**A Legitimate Interest Assessment (LIA) is not legally required to be a formal document**, but without one you have no defence during an AP investigation. Write and maintain an LIA.

### 3.2 The "B2B Exemption" — Does It Exist in NL?

There is **no explicit B2B exemption** in Dutch or EU law. What exists is:

- Recital 14 GDPR: data of legal entities is outside GDPR scope. The BV's company data (KvK number, trade name, registered address, generic business email) is not personal data — no GDPR basis needed.
- The Telecommunicatiewet art. 11.7 applies to **electronic mail** as well as calls; it requires prior consent for unsolicited commercial email to natural persons, but **legal entities (BVs) are explicitly excluded from this protection**.

Practical result: emailing info@somebv.nl about a relevant B2B service is **lawful without prior consent** provided you use legitimate interest as basis, conduct an LIA, and provide opt-out. This is settled in NL practice but not a formal statutory "exemption."

**Status: Settled practice, not codified exemption. Low enforcement risk for targeted BV outreach with LIA and opt-out.**

### 3.3 AP Position — KvK Data and Directory Prospecting

The AP has not issued a specific recent ruling on KvK-to-email prospecting. KvK is a public register; KvK itself states its data may not be used for direct marketing without complying with applicable privacy legislation and any NMI flag set by the registrant.

Key risk: The **Non-Mailing Indicator (NMI)** on a KvK extract signals the entity has opted out of unsolicited advertising. Using NMI-flagged data for cold email is a violation. Check NMI status before any outreach based on KvK data.

For Belgian-jurisdiction insight (useful as neighboring DPA): Belgian DPA draft recommendation 01/2025 (March 2025) found that data being publicly listed in a commercial register does not automatically confer legitimate interest for reselling or using that data for direct marketing. Dutch AP has not published an equivalent but the EDPB guidelines (October 2024) apply.

### 3.4 Required Elements for Every Cold B2B Email

Under Tw art. 11.7 and AVG:

- Full sender identity (company name, registration number, address).
- Subject line that is not misleading.
- Clear commercial purpose stated within the email.
- **One-click unsubscribe** (or clearly worded opt-out instruction) in every email.
- Privacy notice or link to privacy policy.
- Response to any DSAR (data subject access/erasure request) within 30 days (AVG art. 12).

### 3.5 Recent Enforcement on B2B Cold Email (2024-2026)

No major Dutch AP enforcement specifically targeting B2B cold email to BVs has been published as of 2026-05. AP enforcement has focused on consumer-facing violations. The **Experian Nederland** fine (€2.7 million) was about processing and profiling of consumer personal data without adequate disclosure — relevant for data broker-style KvK enrichment use cases.

**Status: Low enforcement history for targeted BV cold email with proper LIA + opt-out. Risk rises sharply if eenmanszaak data is mixed in.**

---

## 4. The BV-Only Filter — What It Legally Buys You

### 4.1 AVG Exposure Reduction

Personal data under GDPR/AVG = data relating to an **identified or identifiable natural person** (GDPR art. 4(1)). A BV's trade name, KvK number, registered address, and generic email address (info@, contact@) are data of a legal person — **outside GDPR scope by Recital 14**. Processing BV-level data for outreach requires no GDPR legal basis, no DSAR response rights, and no AVG retention limits.

Eenmanszaak data = personal data of the owner. Full AVG applies: legal basis required, data subject rights apply, retention limits apply, breach notification applies.

The BV filter eliminates the highest-risk category of data subjects from your pipeline.

### 4.2 AP Guidance — Legal-Person Data Out of AVG Scope

The AP's published position (autoriteitpersoonsgegevens.nl, "What are personal data?") confirms: "Information about legal entities such as companies is not personal data." This aligns with GDPR Recital 14 and is settled Dutch law.

Source: AP — "What are personal data?" (autoriteitpersoonsgegevens.nl/en/themes/basic-gdpr/privacy-and-personal-data/what-are-personal-data).

### 4.3 Edge Case: BV Director's Personal Email — CJEU C-710/23 (April 2025)

**CJEU ruling of 3 April 2025 (Case C-710/23)** settled a previously gray area: a company director's name, signature, email address, and telephone number **are personal data under GDPR even when the director acts in a professional capacity** on behalf of a legal entity. The fact that the data identifies someone acting in a professional role is irrelevant to the personal data classification.

**Practical implication for Klantkraan:**

- `info@bv.nl` — generic role address, not personal data, outside AVG scope. Can be used without GDPR legal basis.
- `jan.devries@bv.nl` — personal email linked to an identified natural person (Jan de Vries), **is personal data**. GDPR/AVG applies: requires legal basis (legitimate interest with LIA), must honour DSAR and erasure requests, counts toward retention limits.
- KvK director data (name of bestuurder in extract): personal data under C-710/23.

**Do not treat a named director's email as BV-level data just because the BV is the target company.**

### 4.4 Minimum Data Hygiene for BV-Only Outreach

Even with a pure BV filter:

1. Maintain a suppression list (unsubscribed/opted-out BVs) and honour it.
2. Check NMI flag on KvK extracts before outreach.
3. If using named director contacts: run an LIA, document it, provide opt-out, respond to DSARs.
4. Keep acquisition source logged for every record (demonstrates compliance intent to AP/ACM).
5. Retention: generic BV data — set a reasonable limit (e.g., 24 months without any engagement); personal director data — shorter limit justified in LIA.

---

## 5. Synthflow AI Voice Agent — Specifics

### 5.1 Recording Rules in NL

The Netherlands applies a **modified one-party consent** framework:

- A private individual can record their own calls without informing the other party, provided the recording is not publicly disclosed without consent (Wetboek van Strafrecht art. 139a–d; no wiretapping equivalent for one-party participation).
- **Companies face stricter rules**: organizations recording calls for business purposes must have (a) a legitimate interest or contractual basis under AVG art. 6(1)(b)/(f), and (b) inform callers before recording starts. Pre-call disclosure ("Dit gesprek kan worden opgenomen...") is the minimum standard.
- Works council (OR) approval is required to implement call recording for employees whose calls are recorded (Wet op de ondernemingsraden art. 27).
- Voice recordings = personal data under AVG (voice is biometric-adjacent; biometric voiceprints are special category data under art. 9). Store with access controls, log access, define retention period.

**Source: Sound of Data "Recording phone calls" analysis; AP telemarketing guidance.**

### 5.2 AI Act Art. 50 Disclosure — Required Dutch Wording

No official Dutch-language template has been published by the EU Commission, AP, or ACM as of 2026-05. The Code of Practice (expected June 2026) may provide language guidance. Based on the statutory obligation:

**Minimum compliant Dutch opening for an outbound AI voice agent:**

> "Goedemiddag, u spreekt met een geautomatiseerde assistent van Klantkraan. Dit is een AI-systeem — geen medewerker. Ik bel u namens [bedrijfsnaam] over [onderwerp]. Wilt u verdergaan?"

Translation note: "geautomatiseerde assistent" (automated assistant) or "AI-systeem" are both acceptable. "Virtuele assistent" alone is ambiguous and may not satisfy the "informed they are interacting with an AI system" standard.

**Required elements:**
- Company name of the deployer (Klantkraan or its client)
- Explicit statement it is an AI / automated system (not a person)
- Purpose of the call
- Opportunity for the recipient to decline

### 5.3 Where Disclosure Must Appear

- **Outbound calls**: first utterance, before any data collection or sales pitch. Within approximately 5 seconds of the call connecting.
- **Inbound calls**: first utterance of the agent's greeting, before the caller provides any information.
- **After a transfer from AI to human**: not required again — the obligation is satisfied by the AI leg. However, good practice is for the human agent to acknowledge the prior AI interaction.
- **Per-session, not per-conversation-turn**: one disclosure per call session is sufficient; repeating it on every turn is not required.

### 5.4 Combined AVG + AI Act Compliance Pattern for Voice Agents

| Layer | Requirement | When |
|---|---|---|
| AI Act art. 50 | Audible AI disclosure in Dutch | First 5 seconds of every call |
| Tw art. 11.7 | Caller ID + company name + purpose | Same opening statement |
| AVG art. 13/14 | Inform subject of processing purpose, legal basis, retention | Opening statement or follow-up email/URL |
| AVG art. 6 | Legal basis for voice data processing | Before call: document legitimate interest or consent |
| AVG recording | Inform caller before recording, apply retention limits | Opening statement |
| AI Act art. 50(2) | Machine-readable marking of AI-generated audio (for recorded output) | At output generation level — Synthflow provider obligation, verify in contract |

**DPIA requirement**: If processing voice data at scale (many calls per month involving natural persons), a DPIA under AVG art. 35 is likely required given the sensitivity of voice data. Run one before scaling outbound campaigns.

---

## 6. Cheat Sheet — What Klantkraan CAN and CANNOT Do

### Outbound AI Voice Agent to a BV

**ALLOWED** under current law (to 2 August 2026), provided:
- Called number is publicly disclosed by the BV (KvK, website, directory).
- No NMI flag on the KvK extract.
- Agent opens with: company name + commercial purpose + AI disclosure (the AI disclosure is not legally mandatory until 2 August 2026, but keep it on regardless — it is on in Synthflow and must remain on).
- The BV is the intended end-user of the service.

**From 2 August 2026**: also legally required to include the AI disclosure (art. 50) or face up to €15M / 3% global turnover penalty.

---

### Outbound AI Voice Agent to an Eenmanszaak / VOF

**NOT ALLOWED** without prior explicit opt-in. The owner is a natural person; the same consumer telemarketing rules apply. No AI-specific exception exists. Eenmanszaak numbers in your dialing list without documented opt-in = Tw art. 11.7 violation + AVG violation simultaneously. **BV filter must exclude these.**

---

### Cold Email to a BV (generic address, e.g., info@bv.nl)

**ALLOWED** without prior consent, provided:
- Legitimate interest basis documented in an LIA.
- Email is relevant to the BV's business sector and size.
- No NMI flag on KvK.
- Every email contains: sender identity, unsubscribe mechanism, privacy policy link.
- Suppression list is maintained and honoured.

---

### Cold Email to an Eenmanszaak / VOF, or to a Named Director's Personal Email

**NOT ALLOWED** without prior opt-in for eenmanszaak/VOF (same as consumer under Tw art. 11.7 + AVG full scope).

For **named director email at a BV** (jan.devries@bv.nl): AVG applies (CJEU C-710/23, April 2025). Requires LIA, opt-out, DSAR response capability. Cold email is not automatically prohibited but requires stricter handling than a generic BV address. AP has not yet issued specific guidance post-C-710/23.

---

### Inbound AI Voice Agent (Prospect-Initiated Call)

**ALLOWED**, subject to:
- AI disclosure in opening greeting (mandatory from 2 August 2026; keep on now).
- Call recording: inform caller at opening if calls are recorded.
- AVG art. 13 information provided (purpose, retention, rights) — via opening statement, post-call email, or website privacy notice linked during the call.
- DPIA if processing at scale.

---

### Recording Calls

**ALLOWED** for business purposes, with:
- Pre-recording notification to the caller ("Dit gesprek wordt opgenomen voor [doel]").
- AVG legal basis documented (legitimate interest typical; or contractual necessity if call is intake for a signed engagement).
- Works council approval if employees' calls are recorded.
- Defined retention period. Recommended: 90 days for intake quality review; delete unless needed for dispute resolution.
- Do not store biometric voiceprints without explicit consent (AVG art. 9).

---

### Data Retention

| Data type | Recommended retention | Legal basis |
|---|---|---|
| BV-level contact data (no natural person) | 24 months post last engagement | Outside AVG scope; internal policy |
| Named director data | 12 months or duration of sales cycle | LIA, document |
| Call recordings | 90 days (or longer only if needed for dispute) | Legitimate interest / contractual |
| Opt-out / suppression list | Indefinitely (to honour the opt-out) | Legal obligation |
| Consent records | Duration of consent + 3 years | Burden of proof (Tw) |

---

### Required Disclosures — Exact Dutch Wording Examples

**Outbound AI voice agent opening (post 2 August 2026 compliant, usable from now):**

> "Goedemiddag. U spreekt met een AI-assistent van Klantkraan — dit is geen medewerker maar een geautomatiseerd systeem. Ik bel namens Klantkraan om [doel van het gesprek]. Heeft u een moment?"

**Call recording notification (if applicable):**

> "Dit gesprek kan worden opgenomen voor kwaliteitsdoeleinden. Als u hiermee niet akkoord gaat, kunt u dit aangeven."

**Cold email unsubscribe footer:**

> "U ontvangt dit bericht omdat [naam bedrijf] een legitiem belang heeft om contact op te nemen over [categorie diensten]. Wilt u geen berichten meer ontvangen? Klik hier om u af te melden: [link]. Klantkraan B.V. | KvK [nummer] | [adres]."

---

## Source List

All sources accessed 2026-05-21. Distinguish: (S) = statute/official text; (G) = regulator guidance; (P) = published analysis/commentary.

**EU AI Act**
- (S) EU AI Act, OJ L 2024/1689, art. 50 and art. 113: https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=OJ:L_202401689
- (G) EU Commission AI Act Service Desk, art. 50: https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-50
- (G) EU Commission digital strategy — Navigating the AI Act: https://digital-strategy.ec.europa.eu/en/faqs/navigating-ai-act
- (G) EU Commission Code of Practice on AI-generated content (draft Dec 2025): https://digital-strategy.ec.europa.eu/en/policies/code-practice-ai-generated-content
- (P) artificialintelligenceact.eu art. 50 text and guide: https://artificialintelligenceact.eu/article/50/ and https://artificialintelligenceact.eu/transparency-rules-article-50/
- (P) aiactblog.nl (NL-focused): https://www.aiactblog.nl/en/ai-act/artikel/50

**Dutch Telemarketing / Telecommunicatiewet**
- (S) Telecommunicatiewet art. 11.7 (official text): https://zoek.officielebekendmakingen.nl/kst-35421-3.html
- (G) ACM — step up telemarketing enforcement: https://www.acm.nl/en/publications/acm-step-its-enforcement-compliance-telemarketing-rules
- (G) ACM — warning on demonstrating explicit consent: https://www.acm.nl/en/publications/acm-issues-warning-telemarketers-must-be-able-demonstrate-explicit-consent
- (G) ACM — next step in heightened oversight: https://www.acm.nl/en/publications/acm-takes-next-step-heightened-oversight-over-unsolicited-telemarketing-calls
- (G) Business.gov.nl — telesales rules: https://business.gov.nl/regulations/telesales/
- (G) Business.gov.nl — telemarketing amendment: https://business.gov.nl/amendments/telemarketing-no-more-unsolicited-calling-your-customers/
- (P) Fieldfisher — new telemarketing rules NL: https://www.fieldfisher.com/en/insights/new-rules-for-telemarketing-in-the-netherlands
- (P) Considerati — end of soft opt-in July 2026: https://www.considerati.com/publications/end-of-soft-opt-in-for-telemarketing-new-rules-starting-july-2026/
- (P) DDMA — B2B telemarketing clarity: https://ddma.nl/kennisbank/meer-duidelijkheid-over-b2b-telemarketing-bij-wetswijziging-telemarketing/
- (P) Lexology — HEM energy fine €1.1M: https://www.lexology.com/library/detail.aspx?g=6e6ffb0e-e957-41df-92b3-36dc600e631f

**AVG/GDPR — Personal Data, Legitimate Interest, B2B Email**
- (G) AP — What are personal data: https://www.autoriteitpersoonsgegevens.nl/en/themes/basic-gdpr/privacy-and-personal-data/what-are-personal-data
- (G) AP — Legal bases from GDPR explained: https://www.autoriteitpersoonsgegevens.nl/en/themes/basic-gdpr/gdpr-basics/legal-bases-from-the-gdpr-explained
- (G) AP — digital direct marketing: https://www.autoriteitpersoonsgegevens.nl/en/themes/internet-and-smart-devices/advertising/digital-direct-marketing
- (G) AP — telemarketing: https://www.autoriteitpersoonsgegevens.nl/en/themes/internet-and-smart-devices/advertising/telemarketing
- (G) EDPB — Guidelines 1/2024 on legitimate interest (draft October 2024): https://www.edpb.europa.eu/news/news/2024/edpb-adopts-opinion-processors-guidelines-legitimate-interest-statement-draft_en
- (S) CJEU judgment C-252/21 (KNLTB, 4 October 2024) — commercial interest qualifies as legitimate interest: confirmed via AP and EDPB publications
- (S) CJEU judgment C-710/23 (3 April 2025) — director contact details are personal data: https://www.ictrechtswijzer.be/en/are-the-contact-details-of-the-director-of-a-company-also-personal-data/
- (P) Cyberinsider — AP fines Experian €2.7M: https://cyberinsider.com/experian-fined-e2-7-million-in-the-netherlands-for-illegal-data-processing/

**KvK / Non-Mailing Indicator**
- (G) KvK — Non-Mailing Indicator: https://www.kvk.nl/en/about-the-business-register/the-non-mailing-indicator/
- (G) KvK — privacy and business register FAQ: https://www.kvk.nl/over-kvk/veelgestelde-vragen-over-privacy-en-het-handelsregister/

**Call Recording**
- (P) Sound of Data — recording calls NL: https://www.soundofdata.com/recording-phone-calls/
- (P) recordinglaw.com NL: https://recordinglaw.com/netherlands-recording-laws/

**Voice AI Compliance**
- (P) Knowlee — AI cold calling EU 2026: https://www.knowlee.ai/blog/ai-cold-calling-compliance-eu-2026
- (P) DILR.ai — art. 50 voice disclosure guide: https://www.dilr.ai/blog/ai-voice-disclosure-compliance-eu-ai-act-article-50

---

*This document is an operational research summary, not legal advice. Consult a Dutch-qualified privacy/telecom lawyer before scaling outreach operations or responding to regulatory inquiry. Refresh after any AP, ACM, or EU Commission publication.*
