# EU AI Act Article 50 — Compliance Notes

> Article 50 transparency obligations are in force from **2 August 2026**. The Klantkraan AI receptionist is a **limited-risk** AI system: interacts with humans, but does NOT make Annex III decisions (no credit, employment, healthcare). No conformity assessment, no Annex VIII registration. **But** Art. 50(1) disclosure is mandatory and non-waivable.

## What the law requires

| Obligation | Source | Klantkraan implementation |
|---|---|---|
| Disclose AI nature at first interaction | Art. 50(1) | First-turn line of every Synthflow call |
| Disclosure in plain language | Recital 132 | Plain Dutch, no jargon |
| Provide a path to human | Implied (and good practice) | "Zeg 'medewerker' voor een mens" |
| Record-keeping | Art. 50(5) | Audio recording + transcript + model version + prompt hash, retained |
| Annex VIII registration | NOT required for limited-risk | n/a |
| Conformity assessment | NOT required for limited-risk | n/a |

## The verbatim Dutch disclosure (use exactly)

> "Goedendag, u spreekt met {{agent_naam}}, de digitale assistent van {{bedrijfsnaam}}. Dit gesprek wordt gevoerd door een AI-systeem en kan worden opgenomen voor kwaliteits- en trainingsdoeleinden. Wilt u liever een mens spreken? Zeg dan 'medewerker'. Waarmee kan ik u helpen?"

Required elements present:
1. ✅ AI nature disclosed
2. ✅ First interaction (literally first sentence)
3. ✅ Plain Dutch
4. ✅ Recording disclosed
5. ✅ Human handoff path offered

## Non-waivable in the MSA

Article 50 obligations bind the **provider** (Klantkraan) regardless of what the deployer (client) wishes. If a client says "disable the AI disclosure", we refuse in writing.

The MSA contains the non-waivable clause:

> "Klant erkent dat de AI-disclosure op grond van art. 50 AI Act verplicht is en niet kan worden uitgeschakeld. Klant vrijwaart Klantkraan voor boetes voortvloeiend uit klant-veroorzaakte non-compliance."

Fines for non-compliance: up to **€15M or 3% global turnover** (art. 99(4)(g)).

## If a caller asks "Bent u echt?"

The AI never lies. Hard rule in the system prompt:

> "Nee, ik ben de digitale assistent van {{bedrijfsnaam}}. Maar uw bericht komt direct bij {{owner_naam}} terecht."

Lying about AI status would be a separate violation + reputational damage.

## Record-keeping (Art. 50(5))

For each call, we retain:
- Audio recording (call.mp3)
- Transcript (call.txt, plain text)
- Synthflow model version + voice ID
- System prompt hash (SHA-256)
- Timestamp + duration
- Disclosure confirmation log (separately stored proof the disclosure played)

Retention: duration of contract + minimum 6 maanden after termination (to cover any AP-melding window). After that, deleted automatically.

## Synthetic media (if we use it for marketing later)

If Klantkraan ever generates synthetic audio/video depicting a real person (e.g., a fake testimonial video), Art. 50(4) requires a clear disclosure that the content is AI-generated. We **don't currently do this** and **shouldn't** — fake testimonials are also Reclamecode violations.

## Deepfake / voice-cloning policy

Klantkraan does **NOT**:
- Clone the owner's voice for the AI receptionist
- Generate fake video testimonials
- Auto-translate client voices into other languages

This is a deliberate brand boundary, not just legal hygiene.

## Compliance checks (operational)

Monthly audit (founder, 15 min):
1. Pick 10 random call recordings.
2. Confirm disclosure played in first 8 seconds of each.
3. Spot-check transcript reflects the disclosure text.
4. Log audit result in `compliance_audits` table.

Quarterly:
1. Review Synthflow model version + voice — any drift?
2. Review prompt for any change that weakens the disclosure.

Annual:
1. Re-read Art. 50 + any AP guidance.
2. Update this document.
3. Re-train any sub-processor agreements.

## What happens if AP audits

1. Cooperate fully. Provide RoPA, DPA, DPIA, sample call recordings.
2. Show audit log.
3. Show the MSA non-waivable clause.
4. Show retention policy.

This is why the Art. 30 RoPA and audit logs aren't optional — they're our defense.

## Source

- Article 50 official text: https://artificialintelligenceact.eu/article/50/
- Article 50 practical guide: https://artificialintelligenceact.eu/transparency-rules-article-50/
- Article 99 (penalties): https://artificialintelligenceact.eu/article/99/
- Voice agents under the AI Act (2026 guide): https://aetherlink.ai/en/blog/ai-chatbots-voice-agents-eu-ai-act-compliance-in-2026-amsterdam
- AI Act compliance checklist for voice: https://ainora.lt/blog/eu-ai-act-voice-agents-what-businesses-need-to-know
