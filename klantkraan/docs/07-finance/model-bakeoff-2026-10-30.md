# Receptionist model bake-off, 2026-10-30

Answers U12's open founder call: which model serves the chat receptionist.

## Method

`app.evals`: 14 scenarios (4 garage, 4 real estate, 6 hallucination), each run 3 times per
model = 42 conversations per model. A simulated customer and a judge (both Opus 5.5, judge at
effort high) score every transcript against per-scenario criteria. The receptionist runs the
real prompt, tools and config at effort low with adaptive thinking, and with prompt caching
(added to `receptionist.run_turn` in the same change).

```
EVAL_LOG=results.jsonl .venv/bin/python -m app.evals run all --model claude-haiku-5-5
```

## Result

| Model             | Scenarios pass | Criteria pass | USD / conversation | USD / customer turn |
| ----------------- | -------------: | ------------: | -----------------: | ------------------: |
| claude-opus-4-8   |            93% |           97% |             0.0695 |             0.01145 |
| claude-opus-5-5   |            93% |           97% |             0.0560 |             0.00960 |
| claude-sonnet-5-5 |            95% |           98% |             0.0305 |             0.00534 |
| claude-haiku-5-5  |            93% |           97% |             0.0015 |             0.00030 |

Cost covers the receptionist only, with caching (list prices; Haiku 5.5's cache-read rate is
assumed at 0.1x input). At the ~1,600 messages/client/month in the Meta re-model note, that
is about USD 0.48/client/month on Haiku 5.5 against about USD 18 on Opus 4.8 even with caching.

Failures were few and spread across all four models:
- `vage-aanvraag/interpretation_confirmed` failed on every model (Opus 4.8 3 of 3, Opus 5.5 2,
  Haiku 2, Sonnet 1). It is a prompt gap, not a model gap: the open "restate-before-booking"
  refinement in TODO §J.
- Haiku 5.5: `renter/required_fields_asked` once.
- Opus 5.5: `feestdag-onbekend` once.
- Sonnet 5.5: `buyer/real_listings_only` once.

## What it changes

- Quality does not separate the models on these goldens; cost separates them by 46x.
- The August "Haiku plus caching does not compose" trap was Haiku 4.5's 4,096-token floor.
  Haiku 5.5 caches from 512 tokens. Measured: 36k of 42k input tokens read from cache in one
  conversation.
- Not measured: latency to first reply, and Dutch tone judged by a human. Read a few
  Haiku transcripts before switching.

Switching is one line per client config (`model.id`) plus `kk deploy server`, both founder-gated.
