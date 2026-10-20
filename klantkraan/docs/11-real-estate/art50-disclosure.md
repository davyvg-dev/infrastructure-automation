# EU AI Act art. 50 disclosure — real estate voice agent

Non-negotiable, uninterruptible, first turn of every call. Pattern proven on
DRS ("de AI-assistent van…") and Cool Global (per-language `language_presets`
each carrying the disclosure in `first_message`). The Solvista agent (Phase 2)
uses these as `first_message` per language preset; the `ai_disclosure` eval
criterion from the DRS config guards it (success only if the agent states it is
an AI/digital assistant in its first one or two turns, unprompted).

Persona: Emma, Solvista Estates. Swap brand + name per client at onboarding —
the disclosure clause itself ("AI assistant" / "asistente digital" /
"digitale Assistentin") must survive every rebrand verbatim.

## EN (default)

> Hello, this is Emma, the AI assistant of Solvista Estates. How can I help
> you today?

## ES

> Hola, soy Emma, la asistente digital de Solvista Estates. ¿En qué puedo
> ayudarle?

## DE

> Hallo, hier ist Emma, die digitale Assistentin von Solvista Estates. Wie
> kann ich Ihnen helfen?

## Rules

- Disclosure is part of the greeting, never a separate skippable line, and the
  first message is not interruptible (ElevenLabs: greeting plays in full).
- Text chat carries the same disclosure in the widget intro (already live on
  the Solvista demo).
- Every eval suite for this vertical includes the `ai_disclosure` criterion.
- Never disable, soften, or move the disclosure later in the call — forbidden
  by repo policy and art. 50(1)/(4) AI Act (in force for these obligations
  since 2 Aug 2026).
