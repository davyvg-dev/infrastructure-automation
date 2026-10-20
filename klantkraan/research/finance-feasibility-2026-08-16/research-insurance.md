# Klantkraan — insurance assumptions stress-test

Researched 2026-08-16. All figures from live web sources, cited inline. Nothing from memory.

Business profile assumed: ZZP/eenmanszaak, NL, SBI 6201/7022, omzet €40–80k year 1, 8–20 clients,
product = autonomous generative-AI agent (Claude API) that answers in Dutch, quotes client service
info, **books appointments into the client's calendar**, captures leads, escalates. Processor under
AVG. Sub-processors: Anthropic, Meta/WhatsApp, telephony. Voice inbound planned.

---

## 0. Verdict in one paragraph

The premium numbers are roughly the right order of magnitude but are quoted against **coverage
limits the cheap ZZP products do not actually sell**, and the plan's core belief — that insurance is
"the cheapest risk transfer available" — is false. The cheapest risk transfer is contractual (a
liability cap in the algemene voorwaarden and the verwerkersovereenkomst). More seriously: the
single loss scenario this business can realistically cause — the AI states a wrong price, books a
wrong appointment, or gives wrong advice — is the exact scenario the 2025–2026 insurance market has
spent eighteen months writing exclusions against. A policy bought carelessly online will cost
~€200/mo and pay nothing for the only claim it will ever face.

---

## 1. Are the premiums realistic? Measured market data, 2026

### 1a. Beroepsaansprakelijkheid (BAV / professional indemnity, ICT)

**Plan assumes: €40–80/mo at €500k per claim / €1M aggregate.**

Measured comparison data:

| Source | Date | Profile | Limit | Premium |
|---|---|---|---|---|
| [Yezzer price table](https://www.yezzer.nl/verzekeringen/beroepsaansprakelijkheidsverzekering/info/wat-kost-een-beroepsaansprakelijkheidsverzekering) | **4 Aug 2026** | ICT-consultant, zzp, €50k omzet, €250 eigen risico | €250k/claim | **€35,30/mo** (€423,60/yr) |
| same | 4 Aug 2026 | marketing/comms adviseur (cheapest listed) | €250k | €13,38/mo |
| same | 4 Aug 2026 | architect (most expensive listed) | €250k | €51,88/mo |
| [De Goudse — BAV voor ICT](https://www.goudse.nl/ondernemer/mijnbedrijf/aansprakelijkheid/beroepsaansprakelijkheidsverzekering-voor-ict) | 2026 | ICT, €75k omzet, €750 eigen risico | €250k/claim, €500k/yr | **€37,50/mo** excl. assurantiebelasting |
| [Centraal Beheer BAV](https://www.centraalbeheer.nl/zakelijk/bedrijfsverzekeringen/beroepsaansprakelijkheidsverzekering) | 2026 | ICT'er, €50k omzet, 0 medewerkers, €250 eigen risico | €250k | **vanaf €25,20/mo** |
| [zzpverzekeraar.nl](https://zzpverzekeraar.nl/blog/beste-beroepsaansprakelijkheidsverzekering-zzp/) | 2026 | IT-consultant / software developer (indicative) | €250k–€1M | €40–70/mo |
| [zzpverzekeraar.nl ICT](https://zzpverzekeraar.nl/blog/beroepsaansprakelijkheidsverzekering-zzp-ict/) | 2026 | small ICT ops / mid-size projects | — | €30–60 / €60–120/mo |
| [ikwordzzper.nl](https://www.ikwordzzper.nl/zzp-kennisbank/verzekeringen/dit-is-wat-je-betaalt-voor-een-beroepsaansprakelijkheidsverzekering/) | 2026 | standalone policies generally | tiers listed incl. €500k/€1M | €650–€2.500/yr = **€54–€208/mo**; collectief €350–550/yr |

**Read.** The €25–37/mo figures that dominate the comparison sites are all at **€250.000 per
claim** — one notch below what the plan specifies. ikwordzzper confirms €500k/claim–€1M/yr is a
standard tier and puts standalone policies at €650–2.500/yr. Goudse offers €250k / €500k / €1M with
annual payout capped at 2× the per-claim limit.

Two adders the plan omits:
- **Assurantiebelasting 21%** — Goudse's €37,50 is explicitly ex tax; Interpolis quotes incl. Always
  normalise.
- **Risk classification.** Every one of the prices above is for *"ICT-consultant"* or
  *"softwareontwikkelaar"* — a person who advises or builds to order. Klantkraan sells an
  **autonomous agent that acts on the client's behalf**. That is a heavier class and, per §3 below,
  frequently referred out of the online ZZP channel entirely.

**Corrected BAV: €45–95/mo** at €500k/€1M if written as plain ICT with no AI loading.
**€70–150/mo** if the insurer correctly classifies it as an AI-agent product vendor. The plan's
€40–80 is achievable *only at €250k limits or by mis-describing the business*.

### 1b. Bedrijfsaansprakelijkheid (AVB)

**Plan assumes: €15–25/mo at min €1M per claim.**

| Source | Premium | Limit |
|---|---|---|
| [Veza](https://vezaverzekeringen.nl/artikelen/wat-kost-een-bedrijfsaansprakelijkheidsverzekering) | €8–€35/mo for zzp | standard NL limits **€1.250.000 or €2.500.000 per gebeurtenis** |
| [Interpolis](https://www.interpolis.nl/zakelijk/aansprakelijkheid/kosten) | ~€20/mo incl. 21% assurantiebelasting | — |
| [Knab](https://www.knab.nl/zakelijk/verzekeren/zzp/aansprakelijkheidsverzekering) | vanaf €9,08/mo | — |
| [Insify](https://www.insify.nl/verzekering/it/) | vanaf €7,95/mo | — |
| [Univé software producent](https://www.unive.nl/zakelijk/bedrijfsaansprakelijkheidsverzekering/beroepsaansprakelijkheidsverzekering/software-producent) | — | max €2.500.000 per claim |

**This is the one assumption that holds.** €15–25/mo is right, and the NL market standard limit
(€1,25M–€2,5M) is *above* the plan's €1M ask, so the plan under-specifies in its own favour.

One structural note the plan misses: **AVB is often not optional.** Centraal Beheer sells BAV only
bundled with AVB; Univé sells BAV strictly as "aanvullende dekking op je
Bedrijfsaansprakelijkheidsverzekering." Budget it as a dependency, not a choice.

### 1c. Cyberverzekering

**Plan assumes: €50–120/mo at €1M, with €250k AVG-defence sub-limit and €100k breach notification.**

| Source | Premium | Limit |
|---|---|---|
| [Polisselect — zzp tier](https://polisselect.nl/zakelijk/cyberrisico/) | **vanaf €20/mo** (+ €25 bemiddeling eenmalig, €1,95/mo servicekosten) | **max €100.000 per kalenderjaar**, €125 eigen risico na 48 uur |
| [Polisselect — mkb tier](https://polisselect.nl/zakelijk/cyberrisico/) | **vanaf €48/mo** (+ €199 eenmalig, €6,35/mo) | **€250.000 – €1.000.000** per jaar, naar omzet; €1.000 eigen risico |
| [Zicht Adviseurs](https://www.zichtadviseurs.nl/zakelijk/zzp/cyberverzekering-voor-zzpers) | €20–€70/mo | — |
| [Van Passe](https://vanpasse.nl/en/knowledge-base/insurance/cyber-insurance-zzp/) | €20–€70/mo | — |
| [Cyberverzekeringen.nl](https://www.cyberverzekeringen.nl/blog/is-een-cyberverzekering-ook-van-toepassing-voor-zzpers/) | €10–€30/mo basic | — |
| [Beterverzekeren](https://www.beterverzekeren.nl/bedrijfsverzekeringen/cybercrime-verzekering/) | **€834,90/yr incl. assurantiebelasting = €69,58/mo** | at **€250.000** max |
| [Datarisk](https://www.datariskverzekeringen.nl/premies-en-kosten-datariskverzekering) | vanaf €195/yr cheapest; vanaf €395/yr "more complete" | scales with omzet + limit |

**Read.** The €20/mo headline is a **€100.000** product. It cannot carry the plan's €1M, and €100k
would not survive one multi-client breach across 20 trade businesses' customer lists. To reach €1M
you must buy the commercial/mkb tier. Beterverzekeren's €69,58/mo at only €250k is the best
calibration point available: extrapolating to €1M lands around €100–180/mo.

**Corrected cyber: €90–175/mo** for a genuine €1M limit with a third-party privacy section.
The plan's €50–120 corresponds to roughly €250k–€500k, not €1M.

What Polisselect's policy actually contains, which is the shape to demand:
- first response 24/7, IT-forensisch onderzoek, PR
- eigen schade: data-restoration, ransomware, **meldkosten datalek**
- **derdenaansprakelijkheid** bij privacy- of netwerkbeveiligingsincidenten
- **bestuurlijke boetes als gevolg van privacy-incidenten** + verweer tegen de toezichthouder

Exclusions to check hard (Polisselect's list, likely representative):
opzettelijke nalatigheid; illegale software/data; maatregelen opgelegd door (semi-)overheid;
infrastructuurfalen; and — critically for Klantkraan — **"persoonsgegevens van buiten EU/EER/UK."**
Anthropic, Meta/WhatsApp and telephony routing can put data outside the EEA. If that exclusion is
in the policy, the entire privacy section can be argued away. **This is a live, specific defect.**

### 1d. Rechtsbijstand zakelijk

**Plan assumes: €25–40/mo, deferred.**

| Source | Premium |
|---|---|
| [Centraal Beheer zzp](https://www.centraalbeheer.nl/zakelijk/bedrijfsverzekeringen/rechtsbijstandsverzekering/zzp) | €20–€50/mo |
| [rechtsbijstandsverzekeringvergelijker.nl](https://www.rechtsbijstandsverzekeringvergelijker.nl/wat-kost-een-rechtsbijstandsverzekering/) | €8–€20/mo (2026) |
| [allekosten.nl](https://allekosten.nl/wat-kost-een-rechtsbijstandsverzekering-in-2026/) | €12–€35/mo (2026) |
| [Yezzer](https://www.yezzer.nl/verzekeringen/rechtsbijstandsverzekering/info/beste-rechtsbijstandsverzekering) | €300–€400/yr = €25–33/mo |

**Realistic and correctly deferred.** €20–40/mo. Note both BAV and cyber already fund legal defence
for covered claims, so the marginal value here is debtor collection and supplier/landlord disputes.

---

## 2. THE CRITICAL QUESTION — does standard NL PI cover autonomous-AI loss?

### Answer: **CONDITIONAL — and trending hard toward NO by default.**

A standard Dutch BAV will pay for an AI-caused loss **only if all three hold**:
1. the policy carries **no generative-AI exclusion endorsement**;
2. the AI activity falls inside the **verzekerde hoedanigheid** written on the polisblad; and
3. the insured met the conduct conditions (human oversight, testing, GDPR/AI Act compliance).

Miss any one and the answer is no. In the 2026 market, (1) is being removed from policies wholesale
and (2) is where a solo founder buying online will silently fail.

### Evidence that it CAN be covered

[**Hiscox NL publishes a dedicated AI liability page**](https://www.hiscox.nl/beroepsaansprakelijkheid-ai)
— the single most important source found. Its position:

- *"AI-activiteiten worden beoordeeld binnen de bestaande verzekerde technologieactiviteiten"* —
  AI work is assessed **within** existing insured technology activities, *"tenzij uitdrukkelijk
  uitgesloten in de polisvoorwaarden."*
- Naming AI in the wording **does not expand** cover; it clarifies existing scope.
- Explicitly within scope: **incorrect AI output causing third-party liability** within insured
  professional services; **an AI model failing to meet agreed specifications** as a potential
  beroepsfout; integration, customisation and in-house development of AI.

So Hiscox NL will, in principle, pay for "the AI quoted the wrong price and it cost the client
money" — because that is a classic vermogensschade beroepsfout. Same logic in
[De Goudse's ICT wording](https://www.goudse.nl/ondernemer/mijnbedrijf/aansprakelijkheid/beroepsaansprakelijkheidsverzekering-voor-ict)
("gebrekkige software die servers van klanten platlegt") and
[Hiscox ICT](https://www.hiscox.nl/beroepsaansprakelijkheidsverzekering-ICT), which unusually covers
**contractbreuk én garanties**, data loss/corruption, and service credits — valuable for a SaaS
vendor with an SLA.

### Evidence that it increasingly WON'T be

**Hiscox's own conditions.** The same page requires the insured to: *"monitor en beperk de
vooroordelen"*, protect personal data and comply with applicable regulation, **document tests**,
secure systems, **maintain human oversight of AI systems**, verify IP up front, anticipate
unexpected consequences. And it warns that non-compliance with the **EU AI Act**
*"kan invloed hebben op aansprakelijkheid"*, with *"het niet naleven van toepasselijke wetgeving"*
sitting outside cover alongside contractual liability beyond policy limits and guarantees exceeding
policy allowances.

**A fully autonomous booking agent is the exact profile insurers name as excluded.**
[Bavspecialist.nl](https://www.bavspecialist.nl/nieuws/ai-en-aansprakelijkheid-een-complexe-realiteit)
tells buyers to hunt their wordings for precisely: *"geen dekking voor schade veroorzaakt door
zelflerende systemen zonder menselijke controle"* and *"uitsluiting voor technologieën waarvan de
werking onvoldoende beheersbaar of reproduceerbaar is."* It lists the standard restriction triggers:
absence of human oversight or review; self-learning systems operating autonomously; advice resting
entirely on non-transparent algorithms.

**Dutch market direction, April 2026.**
[AG Connect, 14 Apr 2026](https://www.agconnect.nl/business/juridisch/overweeg-het-afsluiten-van-een-gerichte-ai-verzekering)
(Gartner, Alissa Lugo): *"steeds meer verzekeraars weigeren dekking bij implementaties van AI-agents
of -chatbots"* — naming hallucinations, algorithmic bias, IP infringement and physical damage from
faulty agent-based actions. Advice: review policies for AI exclusion clauses **now**, pursue
dedicated AI cover, invest in governance to qualify at better rates. Gartner expects insurers to
require *"sterke AI-risicobeheersmaatregelen"* as a condition of cover by 2030.

**The global wordings arriving in NL via reinsurance and London.**
- ISO/Verisk endorsements **CG 40 47, CG 40 48, CG 35 08 effective 1 January 2026**, letting carriers
  exclude generative-AI bodily injury, property damage and personal/advertising injury from CGL.
  ([The Insurer, 23 Jul 2026](https://www.theinsurer.com/ti/analysis/more-than-60-pc-insurance-groups-file-to-adopt-ai-exclusions-2026-07-23/);
  [Claims Journal, 20 Jul 2026](https://www.claimsjournal.com/news/national/2026/07/20/338950.htm))
- **More than 60 P&C insurance groups had filed to adopt AI exclusions** by July 2026.
- **Berkley** — absolute AI exclusion on D&O, E&O and Fiduciary: claims *"based upon, arising out of,
  or attributable to"* actual or alleged AI use, deployment or development, **expressly listing
  chatbot communications and inadequate AI governance**.
  ([Zelle LLP, 31 Oct 2025](https://www.zellelaw.com/AI_Update_The_Growing_Trend_of_AI-Related_Insurance_Policy_Exclusions))
- **Hamilton Insurance Group** — generative-AI exclusion on **professional liability**, defined as
  *"any system that produces content such as text, imagery, audio, or synthetic data in response to
  user prompts."* That definition captures Klantkraan's product exactly and completely.
- Specimen wording now in circulation, per
  [Haynes Boone, 13 Apr 2026](https://www.haynesboone.com/news/alerts/ai-exclusions-in-insurance-policies-what-to-do):
  > *"This Policy does not apply to any claim, wrongful act, damages or defense costs based upon,
  > arising out of, or in any way involving any actual or alleged use of generative artificial
  > intelligence by the insured."*

  Haynes Boone calls this "exceedingly broad" and flags **"in any way involving"** as the killer:
  it bites wherever generative AI appears anywhere in the causal chain. For Klantkraan, generative AI
  is in *every* chain. One such endorsement voids the policy for the entire business.
- **CFC** has written explicit AI provisions into E&O, professional liability **and cyber**. Willis
  documents carriers moving between Jan 2025 and Jan 2026 *"from implicit assumptions about AI toward
  explicit guarantees or absolute exclusions."* A Gallagher 2026 survey found 1 in 5 insurance
  professionals had clients that already sustained AI-related losses.
  ([Risk & Business NL](https://riskenbusiness.nl/nieuws/verzekeraars-lopen-risico-op-verborgen-aansprakelijkheid-door-ai-agenten-nu-de-risicos-toenemen/))
- The AIUC "Underwriting the Agent Economy" report: **>90% of insurers' AI-agent exposure sits in
  conventional policies never designed for it** ("silent AI"). Agents differ from chatbots because
  they *"execute tasks instead of generating answers."* Klantkraan books appointments — it is on the
  agent side of that line, which is the side insurers are actively retreating from.

### Applied to the three scenarios in the brief

| Scenario | Standard NL BAV, no AI exclusion, correct hoedanigheid | Same policy + generative-AI exclusion |
|---|---|---|
| AI books a wrong appointment, client loses a job | **Likely pays** — vermogensschade uit beroepsfout | **No** |
| AI states a wrong price, client must honour it | **Arguable** — may be recast as the client's own contractual choice, and "onjuiste kostenraming" is an explicit Centraal Beheer exclusion | **No** |
| AI gives wrong advice that costs the client money | **Likely pays** — the textbook beroepsfout | **No** |

Note the middle row independently: **Centraal Beheer's BAV explicitly excludes "onjuiste
kostenraming"** (incorrect cost estimates). A product whose job includes quoting the client's service
information runs straight into that. Check it per insurer.

### The wording actually needed

Ask the broker for these in writing, by clause and by form number:

1. **Written confirmation that no generative-AI / AI exclusion endorsement is attached** — ask for it
   negatively and by name (ISO CG 40 47 / CG 40 48 / CG 35 08 or carrier equivalents), not "we don't
   think so."
2. **Verzekerde hoedanigheid** (the load-bearing field) must describe the actual business:
   *"het ontwikkelen, leveren en exploiteren van een AI-gestuurde communicatie- en afspraakagent voor
   derden, inclusief geautomatiseerd inplannen van afspraken en het geautomatiseerd verstrekken van
   informatie namens opdrachtgevers."* Anything narrower ("ICT-advies") is a claim-time defence for
   the insurer under art. 7:928 BW mededelingsplicht.
3. **Affirmative AI endorsement** covering: erroneous or hallucinated output; failure to perform to
   specification; and privacy liability arising from model output.
4. **Human-oversight condition defined achievably** — logging, escalation to the owner, and sampled
   review — *not* "a human approves every output," which would destroy the product. Negotiate this
   before binding; it is unarguable afterwards.
5. **Data-loss / privacy liability extension** and IP-infringement cover. Note Hiscox ICT excludes
   patent and trade-secret infringement; Univé and Centraal Beheer exclude IP entirely.
6. **Onjuiste kostenraming carve-back** if the agent quotes prices.

---

## 3. Is a solo operator underwritable?

**Two different questions with two different answers.**

**As a ZZP ICT'er: yes, trivially.** Hiscox, De Goudse, Centraal Beheer, Insify, Univé, Knab,
Interpolis and Yezzer all sell online to zzp'ers in ICT at €40–80k omzet. Hiscox ICT explicitly
accepts developers, system engineers, network admins, security specialists, database managers,
product owners, scrum masters. Klantkraan is not in
[Insify's declined high-risk tech list](https://www.insify.nl/verzekering/it/) (procesbesturing,
embedded systems, medische/lab systemen, betaal- en cryptosystemen) — appointment booking is not on
it. Good.

**As a vendor of an autonomous AI agent: not off the shelf.** Per the
[AI Agent Insurance Europe market guide, June 2026](https://agentinsured.eu/articles/ai-agent-insurance-europe-complete-market-guide-2026):

> No EU-domiciled licensed carrier sells "a standardised, off-the-shelf AI agent liability product
> that a small or mid-sized operator can purchase directly from a website." Cover "can be obtained,
> but it requires a broker, it is negotiated rather than bought off the shelf, and the conditions
> attached to it are documentation requirements that most operators are not yet meeting."

> "An operator without documented governance is likely to face either a **declination** or a quote
> with **heavy AI-specific exclusions**."

Conditions underwriters demand (documented, not hypothetical):
- agent description — purpose, model, scope, user base
- **pre-deployment test results**
- **human oversight mechanisms**
- **incident logs**
- a structured governance assessment aligned to **AIUC-1**, **ISO/IEC 42001** or **NIST AI RMF**
- *"The single largest pricing factor an operator can influence is documentation quality."*

Affirmative AI market pricing, 2026 (USD, annual):

| Profile | $1M limit |
|---|---|
| Documented low-risk agent, non-regulated sector | **$5.000–15.000/yr** (≈ €390–1.170/mo) |
| Undocumented / partial documentation | $15.000–35.000/yr **or declination** |
| SME with governance gaps | AI exclusion loading applied |

Carriers with affirmative AI appetite reachable from NL, all broker-only:
**Armilla** (MGA + Lloyd's coverholder — covers *"errors, inaccurate outputs, hallucinations"*,
AI agent mistakes, non-breach privacy/data leakage via model output, regulatory defence;
[armilla.ai](https://www.armilla.ai/)),
**Munich Re aiSure** (parametric first-party performance cover),
**HSB** (Munich Re small-business AI liability, launched US March 2026, EU availability unconfirmed),
**Counterpart** (affirmative AI on professional liability/D&O), **Lloyd's syndicates** (bespoke,
above minimum premium). Reinsurance capacity from Swiss Re and SCOR.

The Lloyd's/Armilla product's trigger is worth understanding before relying on it: per
[ICT Magazine, 16 May 2025](https://www.ictmagazine.nl/nieuws/ai-verzekering-lloyds-dekt-nu-fouten-van-kunstmatige-intelligentie/),
it pays on **degradation below an audited performance baseline** — "a chatbot that usually answers
95% of questions correctly but suddenly reaches only 85%." A prior technical audit is required, and
**structurally defective models and hallucinations are typically excluded**. So it insures
*regression*, not *wrongness*. Klantkraan's repo already runs goldens and Cekura evals — that is
exactly the baseline such a product needs, and it is a real asset here.

**The actual risk is not decline — it is mis-classification.** If the founder buys a €35/mo
"ICT-consultant" BAV online, states the hoedanigheid as ICT-advies, and an AI-caused claim lands,
the insurer has a clean argument that the loss falls outside the insured hoedanigheid and/or that
the mededelingsplicht (art. 7:928 BW) was breached. That gap is invisible and free right up to the
moment it is total.

**Also urgent — inlooprisico.** BAV is claims-made. Goudse gives 3 years of retroactive cover for
errors caused before inception and discovered after, at no extra premium; Univé standard 3-year
run-in. But retroactive cover only applies to circumstances **not yet known** at inception. Klantkraan
already has live demos and prospects touching real customer data. **Every month of delay is an
uninsured month that retroactive cover will not repair once a circumstance is known.** Buy before the
next client goes live, not after.

**Voice adds underwriting questions.** Inbound telephony brings call recording, consent, a wider
sub-processor chain, and — because a phone call has no visual disclosure surface — a sharper art. 50
compliance burden. Expect a separate underwriting question and possibly a separate rating. Do not
assume the text policy extends.

---

## 4. What the EU AI Act does to insurability and premiums

**Dates (from [Art. 113 / the official timeline](https://artificialintelligenceact.eu/implementation-timeline/)):**
- **2 Feb 2025** — prohibitions + **Art. 4 AI literacy** apply. Binds providers *and* deployers.
- **2 Aug 2025** — penalty provisions (Art. 99–100).
- **2 Aug 2026** — **Art. 50 transparency applies.** *Live as of today, 16 Aug 2026 — two weeks in.*
- 2 Aug 2027 / 2 Aug 2030 — remaining high-risk tranches.

**Klantkraan's position under Art. 50.** Per
[the Art. 50 text](https://artificialintelligenceact.eu/article/50/), providers of AI systems that
interact directly with natural persons must ensure people are informed they are interacting with AI,
*"in a clear and distinguishable manner at the latest at the time of the first interaction"*, unless
obvious to a reasonably well-informed, observant and circumspect person, and must meet accessibility
requirements. Klantkraan develops and places the system on the market under its own name — it is the
**provider**; the trade businesses are **deployers**. So the Art. 50(1) design-level duty sits on
Klantkraan. The repo's hard rule never to disable the disclosure is legally correct and, as of two
weeks ago, is a **legal minimum rather than a differentiator**. Marketing copy should stop treating
it as a feature and start treating it as table stakes — and as underwriting evidence.

**Is Klantkraan high-risk?** Almost certainly **no**. A customer-service and appointment-booking
assistant for trades is not an Annex III use case (not credit scoring, employment, education,
essential public/private services access, law enforcement, migration or justice). So no conformity
assessment, no EU-database registration, no FRIA. **This is a material positive the plan should state
explicitly**, because risk class drives both compliance cost and premium. Sources on the high-risk
perimeter: [Munich Re](https://www.munichre.com/automation-solutions/en/resources/insights/ai/new-eu-act-regulates-ai-in-insurance.html),
[MIT HDSR](https://hdsr.mitpress.mit.edu/pub/19cwd6qx). **Caveat:** if the voice agent ever triages
emergency or safety callouts, re-run the Annex III test — that could pull it into high-risk.

**Is AI Act compliance a condition of cover in 2026?** Not usually as an express condition precedent
in NL retail wordings — **but it is already a coverage-defeating argument**. Hiscox NL states
non-compliance *"kan invloed hebben op aansprakelijkheid"* and places failure to comply with
applicable legislation outside cover. Meanwhile underwriters increasingly demand "governance
evidence" ([agentinsured.eu](https://agentinsured.eu/articles/who-insures-ai-agents-in-europe)),
and D&O underwriters already scrutinise AI governance posture in pricing
([aiclear.org](https://aiclear.org/blog/ai-governance-insurance-d-and-o-pillar)). Gartner expects
formal AI risk-management requirements by 2030, with **lower premiums for those with governance**.

**Turn compliance into an underwriting asset.** The evidence pack an underwriter wants is largely
already produced by this repo — Art. 50 disclosure text and where it fires, escalation rules,
eval/golden results and Cekura runs (baseline performance), conversation logs, the sub-processor
register, and the DPA. Packaging that is what moves a quote from "declination" to the
$5–15k/yr documented-low-risk band. Add an Art. 4 AI-literacy note for self and clients — cheap,
rarely done, and it reads well in a submission.

---

## 5. AVG/GDPR as a processor — needed vs nice-to-have

**Are AVG fines insurable in NL? Yes, conditionally — and NL is one of the few EU countries where
this is true.**

- [Aon](https://www.aon.com/netherlands/persberichten/2019/AVG-boete-Nederland-onder-voorwaarden-verzekerbaar.jsp):
  *"Boetes opgelegd op basis van de AVG zijn onder voorwaarden verzekerbaar. Nederland is daarmee een
  van de weinige landen in Europa waar dit mogelijk is."* Basis: Dutch law contains no prohibition on
  insuring such fines; AP fines are **bestuurlijke** not criminal penalties; no court ruling says
  otherwise.
- [De Clercq Advocaten, 11 Mar 2026](https://declercq.com/blogs/zijn-cyberboetes-verzekerbaar-de-stand-van-zaken-in-nederland):
  *"bestuurlijke boetes zijn in beginsel verzekerbaar."* Two live objections: conflict with openbare
  orde/goede zeden, and the argument that some AVG fines are punitive enough to be uninsurable.
  Dutch courts have **not** definitively ruled. Insurers therefore write it *"onder voorbehoud van
  wettelijke toelaatbaarheid."*
- Universal exclusions: **opzet, bewuste roekeloosheid, grove nalatigheid.**
- Associated costs — proceedings, investigation, remediation, victim compensation — are
  *"vrijwel altijd verzekerbaar"*
  ([ManagementSite](https://www.managementsite.nl/tql/tools-tips/privacy-wetgeving-avg-gdpr/is-het-avg-boeterisico-te-verzekeren)).

**Practical consequence: treat AVG-fine cover as a bonus, never as the reason to buy.** It is
reserved, untested in court, and voidable for gross negligence — which is exactly what an AP
investigation into a small vendor would try to establish. The defence costs and breach-response
costs are the reliably insurable part, and they are also the part that actually bankrupts a solo
operator.

**MUST HAVE for a processor:**
1. **Third-party privacy liability.** Under **art. 82 AVG a data subject has a direct right of action
   against the processor** where it breached processor-specific obligations or acted outside the
   controller's lawful instructions. Klantkraan can be sued directly by a trade client's customer —
   not only via the client. This must be a **third-party** section, not a first-party-only "zzp
   cyber" bundle.
2. **Breach response** — forensics, notification to the AP and to data subjects, legal.
3. **Regulatory defence costs** — separate from, and more important than, fine cover.
4. **Limit sized to the aggregate, not one client.** 20 trade businesses × their customer lists is
   one correlated loss. €100.000 (the Polisselect zzp tier) does not survive it.

**NICE TO HAVE:** AVG fine cover itself; reputation/PR; business interruption; cyber extortion.

**TWO SPECIFIC DEFECTS TO CHECK BEFORE BINDING:**

- **Extraterritorial data exclusion.** Polisselect excludes *"persoonsgegevens van buiten
  EU/EER/UK."* Klantkraan's sub-processors (Anthropic, Meta/WhatsApp, telephony) may process or route
  outside the EEA. Read this clause word by word; a US-region Anthropic endpoint could void the
  privacy section entirely. Pin sub-processor regions and name them in the submission.
- **Contractually assumed liability.** If the verwerkersovereenkomst gives clients an uncapped
  indemnity for AVG fines and third-party claims, that is **assumed** liability, not legal liability.
  [Legalz.nl](https://www.legalz.nl/aansprakelijkheid) confirms BAV commonly does not cover
  contractual penalties (boetebedingen), and Hiscox NL's AI page expressly places contractual
  liability beyond policy limits and guarantees exceeding policy allowances outside cover. An uncapped
  DPA indemnity is therefore a liability the founder personally carries, in an eenmanszaak, with no
  corporate veil.

**Fix the contract, not the policy.** NL market caps to align to:
NLdigital standard caps ICT supplier liability at **€500.000**; GIBIT allows up to 4× the service fee
capped at €5M ([Legalz](https://www.legalz.nl/aansprakelijkheid)). For a solo vendor at €299–499/mo,
a cap of **12 months' fees** (€3.588–€5.988 per client) is defensible and orders of magnitude below
any policy limit. Cap the DPA and the algemene voorwaarden **at or below the policy limit** — never
above it.

---

## 6. Corrected number and the biggest gap

### Corrected monthly insurance line

At the plan's own stated limits, standard NL market, no affirmative AI endorsement:

| Cover | Plan | Corrected | Note |
|---|---|---|---|
| Beroepsaansprakelijkheid (€500k/€1M) | €40–80 | **€45–95** (plain ICT) / **€70–150** (AI-agent classification) | market comparables are all at €250k |
| Bedrijfsaansprakelijkheid (AVB) | €15–25 | **€10–30** | ✅ holds; NL standard limit €1,25–2,5M, above the ask |
| Cyber (€1M, third-party privacy) | €50–120 | **€90–175** | €20/mo zzp tier caps at €100k, not €1M |
| Rechtsbijstand (deferred) | €25–40 | **€20–40** | ✅ holds |
| **Blended, excl. rechtsbijstand** | **€150–200** | **€145–300** | |
| **Blended, incl. rechtsbijstand** | — | **€165–340** | |

**Plan with €250/mo (€3.000/yr).** That is 3,8–7,5% of a €40–80k omzet. Add 21% assurantiebelasting
where quotes are ex tax. Add ~€200–250 one-off bemiddelingskosten if placed via a broker platform.

**If the founder wants the AI risk genuinely transferred** — an affirmative AI endorsement or an
Armilla/Lloyd's placement — add **€390–1.170/mo** at $1M for a *documented* low-risk agent. That is
6–17% of year-1 revenue and is not viable now. **That unaffordability is itself the finding:** at
this revenue, the AI risk cannot be bought away. It must be **contracted** away (liability cap +
"AI output is not advice, client verifies bookings and prices") and **engineered** down (escalation,
logging, evals, confirmation loops). Revisit affirmative AI cover at ~€150k revenue.

**Correct one framing error.** The plan calls insurance "the cheapest risk transfer available." It is
not. The cheapest is a liability cap in the algemene voorwaarden and the verwerkersovereenkomst —
one afternoon with a lawyer, transferring more risk per euro than any premium. Insurance is the
second-cheapest, and it only works once the contract has already capped the exposure to something an
insurer will price.

### THE SINGLE BIGGEST COVERAGE GAP

**Affirmative AI cover: the policy pays for everything except the thing the business actually does.**

For a solo software business, the conventional risks a €200/mo stack insures — a visitor tripping in
an office, a stolen laptop, damage to a client's property — are close to nil. The *only* realistic
route to a claim is the AI producing a wrong output that costs a trade client money. And that is
precisely the peril the 2025–2026 market has been systematically excluding: ISO CG 40 47/48 live
1 Jan 2026, 60+ P&C groups filed by July 2026, Berkley's absolute exclusion naming chatbot
communications, Hamilton's generative-AI exclusion on professional liability defined to cover any
prompt-driven text generator, and Gartner reporting NL insurers refusing cover for AI-agent and
chatbot deployments outright.

The gap has two faces and both must be closed before binding:

1. **The exclusion** — a single "based upon, arising out of, or in any way involving … generative
   artificial intelligence" endorsement makes the entire premium a donation, because generative AI is
   in the causal chain of every claim this business can produce.
2. **The hoedanigheid** — buying a €35/mo "ICT-consultant" policy online without disclosing that the
   product is an autonomous agent acting on clients' behalf creates the same nil outcome, but
   silently, and with a mededelingsplicht argument on top.

**Runner-up gap:** an uncapped liability/indemnity in the verwerkersovereenkomst. Contractually
assumed liability is not covered by BAV, and in an eenmanszaak it lands on the founder personally.
It costs nothing to fix and is the highest-return hour available.

### Action list, in order

1. **Cap the contracts first.** Liability cap at 12 months' fees in the algemene voorwaarden and the
   DPA; "AI output is not advice, client verifies bookings and prices"; cap at or below the eventual
   policy limit. Cheapest, fastest, biggest effect.
2. **Go through a broker, not a comparison site.** Yezzer/Insify/Centraal Beheer online funnels
   cannot classify this business correctly, and a mis-classified policy is worse than none because it
   buys false confidence.
3. **Get the hoedanigheid wording right** — the AI-agent description in §2, on the polisblad.
4. **Get written confirmation of no AI exclusion**, by form number and clause text.
5. **Negotiate the human-oversight condition** to logging + escalation + sampled review before
   binding.
6. **Buy before the next client goes live** — claims-made + inlooprisico means delay is uninsured
   time that retroactive cover will not repair.
7. **Assemble the governance pack** — Art. 50 disclosure, escalation rules, eval/Cekura baselines,
   logs, sub-processor register, DPA. It lowers the rate and is already 80% built.
8. **Check the extraterritorial personal-data exclusion** against Anthropic/Meta/telephony regions.
9. **Re-underwrite before voice launches.** Do not assume the text policy extends.

---

## Sources

- https://www.hiscox.nl/beroepsaansprakelijkheid-ai — **key source**, Hiscox NL affirmative AI position
- https://www.hiscox.nl/beroepsaansprakelijkheidsverzekering-ICT
- https://www.yezzer.nl/verzekeringen/beroepsaansprakelijkheidsverzekering/info/wat-kost-een-beroepsaansprakelijkheidsverzekering — measured price table, 4 Aug 2026
- https://www.goudse.nl/ondernemer/mijnbedrijf/aansprakelijkheid/beroepsaansprakelijkheidsverzekering-voor-ict
- https://www.centraalbeheer.nl/zakelijk/bedrijfsverzekeringen/beroepsaansprakelijkheidsverzekering
- https://www.centraalbeheer.nl/zakelijk/bedrijfsverzekeringen/rechtsbijstandsverzekering/zzp
- https://www.unive.nl/zakelijk/bedrijfsaansprakelijkheidsverzekering/beroepsaansprakelijkheidsverzekering/software-producent
- https://www.insify.nl/verzekering/it/
- https://zzpverzekeraar.nl/blog/beroepsaansprakelijkheidsverzekering-zzp-ict/
- https://zzpverzekeraar.nl/blog/beste-beroepsaansprakelijkheidsverzekering-zzp/
- https://www.ikwordzzper.nl/zzp-kennisbank/verzekeringen/dit-is-wat-je-betaalt-voor-een-beroepsaansprakelijkheidsverzekering/
- https://vezaverzekeringen.nl/artikelen/wat-kost-een-bedrijfsaansprakelijkheidsverzekering
- https://polisselect.nl/zakelijk/cyberrisico/ — cyber tiers and limits
- https://www.beterverzekeren.nl/bedrijfsverzekeringen/cybercrime-verzekering/
- https://www.datariskverzekeringen.nl/premies-en-kosten-datariskverzekering
- https://www.cyberverzekeringen.nl/blog/is-een-cyberverzekering-ook-van-toepassing-voor-zzpers/
- https://www.zichtadviseurs.nl/zakelijk/zzp/cyberverzekering-voor-zzpers
- https://vanpasse.nl/en/knowledge-base/insurance/cyber-insurance-zzp/
- https://www.rechtsbijstandsverzekeringvergelijker.nl/wat-kost-een-rechtsbijstandsverzekering/
- https://allekosten.nl/wat-kost-een-rechtsbijstandsverzekering-in-2026/
- https://www.bavspecialist.nl/nieuws/ai-en-aansprakelijkheid-een-complexe-realiteit — NL AI exclusion triggers
- https://www.agconnect.nl/business/juridisch/overweeg-het-afsluiten-van-een-gerichte-ai-verzekering — Gartner, 14 Apr 2026
- https://riskenbusiness.nl/nieuws/verzekeraars-lopen-risico-op-verborgen-aansprakelijkheid-door-ai-agenten-nu-de-risicos-toenemen/
- https://www.haynesboone.com/news/alerts/ai-exclusions-in-insurance-policies-what-to-do — specimen exclusion wording, 13 Apr 2026
- https://www.zellelaw.com/AI_Update_The_Growing_Trend_of_AI-Related_Insurance_Policy_Exclusions — Berkley, Hamilton wordings
- https://www.theinsurer.com/ti/analysis/more-than-60-pc-insurance-groups-file-to-adopt-ai-exclusions-2026-07-23/
- https://www.claimsjournal.com/news/national/2026/07/20/338950.htm — CG 40 48 scope
- https://agentinsured.eu/articles/ai-agent-insurance-europe-complete-market-guide-2026 — AI agent market, premiums, conditions
- https://agentinsured.eu/articles/who-insures-ai-agents-in-europe
- https://www.armilla.ai/
- https://www.ictmagazine.nl/nieuws/ai-verzekering-lloyds-dekt-nu-fouten-van-kunstmatige-intelligentie/ — Lloyd's/Armilla trigger
- https://artificialintelligenceact.eu/article/50/
- https://artificialintelligenceact.eu/implementation-timeline/
- https://www.aon.com/netherlands/persberichten/2019/AVG-boete-Nederland-onder-voorwaarden-verzekerbaar.jsp
- https://declercq.com/blogs/zijn-cyberboetes-verzekerbaar-de-stand-van-zaken-in-nederland — 11 Mar 2026
- https://www.managementsite.nl/tql/tools-tips/privacy-wetgeving-avg-gdpr/is-het-avg-boeterisico-te-verzekeren
- https://www.legalz.nl/aansprakelijkheid — NLdigital €500k cap, contractual penalties not covered
- https://aiclear.org/blog/ai-governance-insurance-d-and-o-pillar
