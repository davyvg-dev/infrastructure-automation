---
description: Log an agent regression, find the transcript, draft a golden — founder gates the commit
argument-hint: [client] [what happened]
---

A regression was observed: $ARGUMENTS

Work it like an incident, not a note. Small steps, verify each.

1. **Pin the root cause first.** Ask clarifying questions before writing anything: which channel (voice call / web chat / WhatsApp), roughly when, what the customer said, what the agent did wrong vs. what it should have done. Remember Aug-5: a "kenteken not recognized" regression turned out to be a FAKE test plate — rule out operator error before blaming the agent.
2. **Locate the evidence.**
   - Voice: `cd klantkraan/apps/voice-agent/demo && python3 calls.py` (list, newest first), then `python3 calls.py show <n|conv_id>` for the transcript + analysis, `latency <n>` if pacing is implicated.
   - Chat/WhatsApp: transcripts live on the ops server (168.119.173.25) in the receptionist's data stores — check `journalctl -u ai-receptionist` and the per-client analytics/oversight data under `/opt/klantkraan/ai-receptionist/data/`. (No single CLI exists for chat transcripts — say so if you can't retrieve one and work from the founder's account.)
3. **Record it.** Append a numbered entry to `klantkraan/docs/regressions.md` (create it with a two-line header if missing): date, client, channel, symptom, root cause, evidence pointer (conv id / log path), fix direction.
4. **Draft the golden.** Write a matching scenario for `ai-receptionist/app/evals.py` (SCENARIOS list: name, about, client, persona, criteria — mirror the existing DHZ/real-estate entries; Dutch persona for Dutch clients). Criteria must fail on today's behavior and pass once fixed. Do not run it against prod data dirs — evals already sandbox DATA_DIR.
5. **STOP.** Show the founder the regressions.md entry and the drafted golden in chat and wait for confirmation before committing anything (repo doc-change rule). Do not fix the agent in this command — that's a separate, confirmed step.
