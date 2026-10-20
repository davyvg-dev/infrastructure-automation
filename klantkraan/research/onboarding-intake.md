# Klantkraan client intake — minimizing what we ask a non-technical tradesperson

**Goal:** collect enough to fill one `config/<business>.yaml` (see `ai-receptionist/config/klantkraan-demo.yaml`

- `ai-receptionist/app/scaffold.py`) with the **fewest human questions**, inside the ~2h/client founder budget,
  for a busy loodgieter/dakdekker/installateur who does not want a form.

**Headline recommendation:** _Scrape-first, confirm-in-chat._ Auto-extract everything scrapable from the
prospect's website + Google Maps into a pre-filled draft, then ask the human only the 4 things that
**cannot** be scraped (prices, spoed policy, where leads go, persona name), and confirm the rest by letting
them chat with their own branded demo — never by showing them YAML.

---

## 1. Every config field, classified: must-ask vs auto-fill vs default

The YAML has ~18 distinct fields. Only **one category genuinely needs a human**: prices + a couple of policy
decisions. Everything else is auto-fillable from public data or a safe Dutch-trade default.

| Field                     | Source strategy                                                                               | Why                                                                                                                                                                                                     |
| ------------------------- | --------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `business.name`           | **AUTO** (Places/site) → 1-tap confirm                                                        | Trivially scraped; verify spelling only                                                                                                                                                                 |
| `business.type`           | **AUTO-INFER** from Places `primaryType` + site → confirm                                     | e.g. `plumber` → "installatiebedrijf (cv, sanitair, lekkages)"                                                                                                                                          |
| `business.timezone`       | **DEFAULT** `Europe/Amsterdam`                                                                | Never varies for NL trades — never ask                                                                                                                                                                  |
| `business.phone`          | **AUTO** (Places `nationalPhoneNumber`) → confirm                                             | Reliable public field                                                                                                                                                                                   |
| `business.address`        | **AUTO** → confirm                                                                            | Most trades are _service-area_ businesses ("Amsterdam en omgeving"); Places flags this as `pureServiceAreaBusiness` and hides the street address, which matches the YAML's region-not-street convention |
| `persona.name`            | **DEFAULT** `Fleur` (offer to change)                                                         | Cosmetic; one optional question                                                                                                                                                                         |
| `persona.tone`            | **DEFAULT** (template)                                                                        | Identical for every trade; never ask                                                                                                                                                                    |
| `persona.goals`           | **DEFAULT** (template)                                                                        | Identical; never ask                                                                                                                                                                                    |
| `persona.guardrails`      | **DEFAULT / LOCKED** (template)                                                               | Contains safety rules + AI Act behaviour; never client-editable                                                                                                                                         |
| `services[].name`         | **AUTO-INFER** from site → **MUST-CONFIRM**                                                   | Scrapable but hallucination-prone (see §4)                                                                                                                                                              |
| `services[].price`        | **MUST-ASK (human)**                                                                          | _Not scrapable._ Places returns no per-service prices; trade sites rarely list them. The one true input.                                                                                                |
| `services[].duration_min` | **DEFAULT** 60 (30 for offerte/inspectie)                                                     | Booking granularity; client doesn't care                                                                                                                                                                |
| `hours`                   | **AUTO** (Places `regularOpeningHours`) else **DEFAULT** (Mon–Fri 08–18, Sat 09–13) → confirm | Public when set; safe default otherwise                                                                                                                                                                 |
| `booking.slot_minutes`    | **DEFAULT** 60                                                                                | Internal knob                                                                                                                                                                                           |
| `booking.horizon_days`    | **DEFAULT** 14                                                                                | Internal knob                                                                                                                                                                                           |
| `faq[]`                   | **DEFAULT template, auto-personalized** from region + prices + spoed answer                   | Regenerated from the 4 answers, not asked                                                                                                                                                               |
| `greeting`                | **GENERATED / LOCKED** from name + persona                                                    | Format is fixed for EU AI Act art. 50 disclosure — never hand-written                                                                                                                                   |
| `model`                   | **DEFAULT** `claude-opus-4-8` / `low`                                                         | Never client-facing                                                                                                                                                                                     |

**Adjacent operational fields (not in this YAML but required for the receptionist to actually work):**
where do bookings/leads land (`notify` destination — WhatsApp number / email / Telegram) and which calendar
backs `calendar_store`. These are must-ask operationally and belong in the same intake.

### The Minimum Viable Intake — the _only_ things a human must supply

Everything above collapses to **one confirmation + four questions**:

1. **Confirm the draft** — "Klopt dit?" over the auto-filled name / phone / region / hours / service list. (tap-level)
2. **Prices** — the starttarief per service + voorrijkosten (or "gratis offerte"). _The single unavoidable input._
3. **Spoed policy** — do you take emergencies? Any surcharge / after-hours? (yes/no + optional number)
4. **Where should leads/afspraken go?** — WhatsApp number / email, and which agenda to book into.
5. _(optional)_ **Persona name** — keep "Fleur" or pick another.

That's it. If the client answers nothing, the scraped draft + defaults still produce a working, _safe_ demo
(it just quotes no prices — which the guardrails already handle gracefully; see §4).

---

## 2. Intake method comparison

| Method                                                                                         | Founder effort                                                          | Accuracy                                            | Client friction                                                                                                                                                            | Verdict                                                                                                              |
| ---------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- | --------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| **(a) Structured form** (Tally/Typeform)                                                       | Low to build, but **client must type everything**                       | High _if completed_ — but trades abandon long forms | **High** — a busy tradesperson won't fill 18 fields; every field is a micro-commitment that risks abandonment (onboarding research: minimize fields, defer non-essentials) | Reject as the primary path; keep a **3-field fallback** form for prices/spoed/lead-destination when scraping is thin |
| **(b) 15-min kickoff call**                                                                    | **High** — a live call per client blows the 2h budget and doesn't scale | Highest (can probe)                                 | Low for the client (they just talk)                                                                                                                                        | Reject as default; reserve for the price/policy step only, async (WhatsApp voice note), not a scheduled call         |
| **(c) Auto-extraction** (Claude scrapes site + Google Maps → pre-fills YAML → client confirms) | **Low per client, front-loaded once**                                   | High on scrapable fields, **must not touch prices** | **Lowest** — client confirms, doesn't create                                                                                                                               | **Primary path**                                                                                                     |

**Why not the GBP API for scraping prospects:** the official Google Business Profile API only exposes profiles
you _own/manage_ (verified, 60+ days, access request). You cannot pull an arbitrary prospect's GBP through it.
For a prospect you don't manage, the public path is the **Google Maps Places API (Place Details)**, which returns
`displayName`, `nationalPhoneNumber`, `websiteUri`, `regularOpeningHours`, `primaryType`/`types`,
`businessStatus`, and `pureServiceAreaBusiness` — enough for name/phone/hours/type/region. It does **not** return
a service menu or per-service prices (`priceLevel`/`priceRange` are dining-oriented and irrelevant to trades).

---

## 3. Recommended hybrid: "scrape → Claude drafts → confirm in 5 minutes"

A four-step pipeline, mostly automated, ~15–20 min of founder attention per client.

**Step 0 — Inputs (what we feed Claude).** Collect automatically before Claude sees anything:

- **Website text**: fetch homepage + likely `/diensten`, `/tarieven`, `/contact`, `/over-ons` pages (plain text).
- **Google Maps Place Details JSON**: name, phone, website, `regularOpeningHours`, `primaryType`/`types`,
  `businessStatus`, `pureServiceAreaBusiness`, city.
- Optional: KvK trade description if to hand.

**Step 1 — Claude drafts a _structured extraction_, not free-form YAML.** Prompt Claude to emit JSON where every
field carries `value`, `source` (URL or "places"/"default"), `confidence` (high/med/low), and a **verbatim
snippet** it copied from. Rules baked into the prompt:

- Only fill `services[].name`, `hours`, `phone`, `address`, `type` from a cited source. No citation → leave blank
  and flag, **never invent**.
- **Never** populate `services[].price`. Emit every price as the literal placeholder `"PRIJS?"`.
- Classify services against a **controlled Dutch-trade vocabulary** (spoedservice, cv-ketel onderhoud,
  lekkage-reparatie, inspectie/offerte, dakinspectie, …) — classify, don't free-write.
- Leave spoed policy, booking rules, and lead-destination blank (not inferable).

**Step 2 — Assemble the draft config** by merging Claude's cited values over `scaffold.py`'s `_TEMPLATE`
(defaults fill every gap). Extend `scaffold.py` with a `--from-json` path so the extraction feeds it directly and
the greeting/persona/guardrails/model come from the locked template as today. Founder eyeballs the provenance
table (30 seconds): high-confidence rows pass, low-confidence rows get a quick manual check.

**Step 3 — Client confirms _in chat_, never in YAML.** Two confirmation surfaces, both non-technical:

- **Primary: the live branded demo.** Boot `BUSINESS_CONFIG=<draft> python -m app.server`, send the client a
  link (or the 30-sec booking clip scaffold.py already suggests) and one WhatsApp line:
  _"Ik heb alvast een digitale receptionist voor [bedrijf] gebouwd — praat er even mee. Klopt alles? Wat mag
  anders?"_ The client experiences the config instead of reviewing it, and naturally spots wrong hours/services.
- **Attached: a plain-Dutch one-pager** (no YAML) — name, hours grid, service+price table with `PRIJS?` rows
  highlighted, region, spoed line — so they can reply with corrections in one message
  ("cv-onderhoud is €135, geen zaterdag, spoed doen we wel — €95 voorrijden").

The founder pastes prices + spoed + lead-destination into the YAML, redeploys, done. This keeps the whole loop in
the same medium the _product_ uses (chat/WhatsApp), matches "CLI over dashboards," and never exposes YAML.

---

## 4. Accuracy / hallucination control — the non-negotiable part

The risk is Claude inventing a service the client doesn't offer, or a price. Defences, in order of importance:

1. **Prices are structurally un-inventable.** Claude is instructed to write `"PRIJS?"` for every price, and the
   pipeline refuses to ship a numeric price that wasn't typed by the client. Crucially, the receptionist's
   existing guardrail already says _"noem geen exacte reparatieprijzen buiten de dienstenlijst — noem het
   starttarief en zeg dat de monteur het op locatie bevestigt."_ So a **missing** price degrades safely: the bot
   simply defers to the monteur instead of quoting a wrong number. Empty is safe; invented is not — so we make it
   impossible to invent.
2. **Citation-or-blank for services/hours.** Every extracted service/hour must carry a verbatim source snippet.
   No snippet → field left blank and flagged, never guessed. This turns the model into a _copier_, not an author.
3. **Controlled vocabulary for services.** Claude classifies site text into a fixed Dutch-trade service list
   rather than free-writing names, so it can't hallucinate an oddly-worded or non-existent offering.
4. **Confidence gating.** Low-confidence rows never auto-write; they surface in the provenance table for the
   founder's 30-second check.
5. **Human confirmation is the ground truth.** Nothing goes live until the client has chatted with the demo
   and/or replied to the one-pager. The scrape is a _draft_, the client's reply is _truth_. Spoed policy and
   booking rules are always blank until the human states them — the AI never infers "yes we do emergencies."
6. **Locked fields stay locked.** `greeting`, `persona.guardrails`, and the AI-Act disclosure are template-owned
   and never touched by extraction, so auto-fill can't accidentally weaken a safety rule.

---

## 5. Sensible Dutch-trade defaults (so we don't have to ask)

Baked into `scaffold.py`'s template; only overridden when the scrape or client says otherwise.

- **Opening hours:** Mon–Fri 08:00–18:00, Sat 09:00–13:00, Sun closed. (Matches the demo; typical trade hours.)
- **Timezone:** `Europe/Amsterdam` — always.
- **Region format:** "`<Stad>` en omgeving" for service-area trades (confirmed by Places `pureServiceAreaBusiness`).
- **Durations:** 60 min per job, 30 min for offerte/inspectie.
- **Booking:** 60-min slots, 14-day horizon.
- **Tone/persona:** "Fleur", rustig/vriendelijk/kort, reassuring on spoed — one template for every trade.
- **Price _shape_ hints for the human** (from 2026 NL market data, shown as suggestions next to `PRIJS?`, never
  auto-filled): spoed/storing starttarief ~€90–130; voorrijkosten ~€20–40; cv-onderhoud ~€120–150;
  offerte/inspectie usually gratis; evening/weekend surcharge common for dakdekker spoed. These prime the client
  to answer fast — they still supply the real number.

---

## 6. Concrete build steps (fits the Ralph Higgums loop)

1. Add `app/extract.py`: fetch site pages + Places Details → call Claude (model/effort from config, JSON schema
   static for prompt caching) → return cited extraction JSON. (Fetch Places/Anthropic API surface via context7.)
2. Add `scaffold.py --from-json <extraction.json>`: merge cited values over `_TEMPLATE`, force every price to
   `PRIJS?`, keep greeting/guardrails/persona from template.
3. Add a `python -m app.selftest intake` layer that asserts: no price is ever written without human input, and
   uncited services are dropped.
4. Ship the client-facing one-pager generator (plain Dutch, no YAML) + the WhatsApp confirm script.
5. Keep a 3-field Tally fallback (prices / spoed / lead-destination) for prospects with no website or thin Maps.

---

## Sources

- [10 Client Onboarding Best Practices for B2B Agencies](https://www.unkoa.com/client-onboarding-best-practices/)
- [Customer Onboarding Best Practices (minimize fields / defer non-essentials)](https://userpilot.com/blog/customer-onboarding-process/)
- [Google Places API — Place Data Fields (New)](https://developers.google.com/maps/documentation/places/web-service/data-fields)
- [Google Places API — Place Details (New)](https://developers.google.com/maps/documentation/places/web-service/place-details)
- [Google Business Profile API — access requirements (owned profiles only)](https://developers.google.com/my-business/content/overview)
- [Loodgieter kosten / tarieven 2026 (Homedeal)](https://www.homedeal.nl/loodgieter/loodgieter-kosten/)
- [Kosten spoed dakdekker weekend 2026](https://www.kosten-dakdekker.nl/blogs/kosten-spoed-dakdekker-weekend/)
