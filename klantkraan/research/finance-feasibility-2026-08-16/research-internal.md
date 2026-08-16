# Klantkraan — internal reality check against the financial plan
Date of audit: 2026-08-16. Read-only pass over the repo's own records.
Repo root: `/Users/bigd/Documents/marketing/infrastructure-automation`

---

## 0. Verdict in one line

**Zero paying clients, €0 MRR, zero closes, zero churn observations, one logged phone call ever, 30 cold emails sent and 0 replies.** Every number in the financial plan — CAC €150-250, churn 20%/yr, Chat COGS €10, €500 install fee, €3,590 MRR at 10 clients — is an unvalidated estimate with n=0 behind it. The repo's own research said so six days ago and nothing changed.

---

## 1. REVENUE REALITY

### 1.1 Paying clients: **0**. MRR today: **€0**.

Money that has ever moved through the business, from the billing ledger
`/Users/bigd/Documents/marketing/infrastructure-automation/ai-receptionist/data/billing.jsonl` — the file contains **exactly one line**:

```
{"at": "2026-07-29T19:19:44", "event": "checkout_created", "payment_id": "tr_PsWKMJTY8JFM2a9DoZeUJ",
 "customer_id": "cst_xVgaUpxoQZ", "amount_eur": "1.00", "plan": "chat", "monthly_eur": "1.00", ...}
```

That is a **€1.00 self-test** on 2026-07-29. The event is `checkout_created` — there is no `paid` event, no `subscription_created`, no recurring charge, no invoice. **No customer has ever paid Klantkraan anything.**

### 1.2 The deal board — every named record

Source of truth: `ai-receptionist/data/pipeline/*.yaml` (25 records, gitignored/local-only, managed by `app/pipeline.py`). Stage ladder is `lead → qualified → staged → demo → signed → onboarding → live`.

| Slug | Business | Stage | Deal value | Last activity |
|---|---|---|---|---|
| airco-mallorca | **Cool Global Mallorca** (ES, airco) | **demo** | €499/mo + €945 install (offerte 10-08) | close pack sent 2026-07-22; offerte mailed 2026-08-10 |
| voltwerk | **VoltWerk Elektrotechniek** | **lead** | €300/mo promised (deviating) | cold call 2026-07-31; `next_call: 2026-08-06` **10 days overdue** |
| aj-dakwerken | AJ Dakwerken B.V. | staged | — | record 2026-07-22, mail T3 2026-08-08 |
| barendse | A. Barendse & Zn. B.V. | staged | — | T3 2026-08-08 |
| buddingh | Buddingh Dakdekkersbedrijf B.V. | staged | — | T3 2026-08-08 |
| buiteman | Wtb. Joop Buiteman B.V. | staged | — | T3 2026-08-08 |
| dak-garantie-amsterdam | Dak Garantie Amsterdam B.V. | staged | — | T3 2026-08-08 |
| dekker | Dekker Installatietechniek B.V. | staged | — | T3 2026-08-08 |
| derwort | Derwort Loodgieters B.V. | staged | — | T1 only, 2026-07-29 |
| duckdekker | Duckdekker B.V. | staged | — | T1 only, 2026-07-29 |
| dv-dakdekkers | DV Dakdekkers B.V. | staged | — | **hard bounce 2026-07-30** |
| frauenfelder | P.H. Frauenfelder B.V. | staged | — | T1 only, 2026-07-30 |
| herfst | Herfst B.V. | staged | — | T1 only, 2026-07-31 |
| lohmann | Lohmann Groep B.V. | staged | — | T1 only |
| loodgieter-utrecht-bv | Loodgieter Utrecht B.V. | staged | — | T1 only |
| md-dak | MD Dak & Klusbedrijf B.V. | staged | — | T1 only |
| meijer | Loodgietersbedrijf Meijer B.V. | staged | — | T1 only |
| smits-installaties | Smits Installaties B.V. | staged | — | T1 only |
| valkenburg | Andries Valkenburg B.V. | staged | — | T1 only |
| van-der-herp | W.J. van der Herp B.V. | staged | — | T1 only |
| van-der-wiel | L van der Wiel B.V. | staged | — | **never mailed** |
| vdp-dakbedekking | VDP Dakbedekking B.V. | staged | — | **never mailed** |
| verkuylen | T.I.B. Verkuylen B.V. | staged | — | **never mailed** |
| visser-van-der-hell | Visser & Van der Hell B.V. | staged | — | **never mailed** |
| w-janssen | Technisch Bureau W. Janssen B.V. | staged | — | **never mailed** |

Stage totals: **23 staged · 1 demo · 1 lead · 0 signed · 0 onboarding · 0 live · 0 lost · 0 churned.**

23 of 25 are at `staged`, which per `pipeline.py` NEXT_ACTION means "send the demo link; run discovery" — i.e. they have a branded demo built and an email sent, and nothing beyond that. They skipped the `qualified` gate entirely (they were bulk-imported from the outreach batch on 2026-07-22, all with the identical history line "Imported from existing branded demo").

### 1.3 The two real deals live OUTSIDE the pipeline CLI

Neither DRS nor Cool Global has a pipeline record with a value. They exist only as Markdown offer docs:

**Slotenmaker DRS** — `klantkraan/docs/02-sales/offerte-drs-2026-08.md`
- Offertenummer KK-2026-08-01, dated `{{06-08-2026}}`, **geldig tot `{{20-08-2026}}` — expires in 4 days**. Both fields are still template placeholders.
- €685,00/mo excl. BTW incl. 1.500 belminuten; €0,40/min overage; **€1.395,00 eenmalige installatie**, 50/50 payment schedule.
- Live Mollie iDEAL link `payment-links.mollie.com/payment/aSnDhBoYJguZ6Xokb6nTk`, **expires 20-08-2026**.
- Memory records a reply 2026-08-13 ("zeker geïnteresseerd") plus a NEW unpriced ask (customer→monteur dispatch automation). **Not reflected in any repo record.** The pipeline has no `drs` slug at all.

**Cool Global Mallorca** — `klantkraan/docs/02-sales/offerte-coolglobal-2026-08.md`
- Dated 10-08-2026, **valid until 24-08-2026 — expires in 8 days**.
- €499,00/mo excl. VAT incl. 750 min, first month 50% off (€249,50), €0,40/min overage, **€945,00 install**. Chat-only fallback €299/mo, no install.
- Sent 2026-08-10 to Jordan (jiromorgan17@gmail.com), re-sent same day with corrections. Pipeline still says `status: demo, updated: 2026-07-22`.

**Total actual MRR today: €0,00. Total contracted-but-unpaid: €0,00. Total offers outstanding: 2, worth €1.184/mo + €2.340 install, both expiring within 8 days.**

Also note a pricing inconsistency six days apart on the same product: DRS €685/mo for evening+weekend voice with €1.395 install; Cool Global €499/mo for 24/7 in three languages with €945 install.

---

## 2. SALES VELOCITY, MEASURED

### 2.1 Email — the only channel that actually ran

Ledger: `ai-receptionist/build/outreach/sent.json` (v2, touch-level). Computed:

| Metric | Measured |
|---|---|
| Prospects with a pipeline record | 25 |
| Prospects ever emailed | **18** (7 never mailed: 5 real prospects + airco-mallorca + voltwerk) |
| **Total touches sent** | **30** |
| Prospects at 1 touch | 12 |
| Prospects at 3 touches | 6 |
| First send | 2026-07-29 16:41 |
| **Last send** | **2026-08-08 07:14 — 8 days ago** |
| **Replies** | **0** |
| Opt-outs / "stop" | 0 |
| Hard bounces | 1 (dv-dakdekkers, 2026-07-30) |
| Demos delivered as a *booked* demo | 0 (30 branded demo pages exist; nobody was walked through one) |
| **Offers sent** | **2** (DRS 06-08, Cool Global 10-08) |
| **Closed** | **0** |

### 2.2 Phone

`pipeline.py` has a full dial-outcome funnel (`no-answer/voicemail/gatekeeper/bad-number/callback/talked/demo/close/rejected`). Across all 25 records there is **exactly one `call:` event in history — voltwerk, `call/talked`, 2026-07-31**. The repo's own audit (`research/first-client-market-research-2026-08-10.md`) states this plainly: *"exactly one logged phone call, ever."*

### 2.3 Measured conversion rates

- send → reply: **0 / 30 = 0.0%**
- prospect → reply: **0 / 18 = 0.0%**
- send → positive reply: **0 / 30 = 0.0%**
- send → demo booked: **0 / 30 = 0.0%**
- **send → client: 0 / 30 = 0.0%**
- offer sent → closed: **0 / 2 = 0.0%**
- dial → reach: 1 / 1 (n=1, meaningless)
- bounce rate: **1 / 18 prospects = 5.6%** (3.3% of sends) — the risk register R-COM-01 early warning fires at **>3% bounce**. It has fired and nobody has logged it.

### 2.4 Elapsed time from first touch to close

**Nothing has closed. There is no cycle time to measure.** The plan's assumed sales cycle is <14 days (weekly-kpi-review KPI 4, funnel-benchmarks). The oldest live prospect (Cool Global) has been in play since 2026-07-22 — **25 days and counting, no close**. Voltwerk: first contact 2026-07-31, `next_call` was 2026-08-06, **10 days overdue**.

### 2.5 Measured vs the plan's assumed 0.10-0.15% send→client

The plan's rate implies **1 client per 667-1,000 sends**. At 30 sends, the *expected* number of clients under the plan's own assumption is **0.03-0.045** — so 0 closes is entirely consistent with the plan and proves nothing about the rate. That is the important point: **the outreach volume to date is ~3-4% of what it takes to produce a single client at the plan's own conversion rate.** Nothing has been tested.

What *is* falsified is the reply rate. `docs/02-sales/funnel-benchmarks.md` targets **7% reply / 1.5% positive reply**, with an "investigate below" line at **<4% reply**. Measured: 0/30 = 0%. At a true 7% rate, P(0 replies in 30 sends) = 0.93^30 ≈ **11%** — not conclusive, but the funnel doc's own escalation threshold is already breached, and no escalation has been logged.

### 2.6 The volume the plan needs vs the volume the founder is allowed to send

- `funnel-benchmarks.md` builds its waterfall on **4,500 cold sends/month** (9 Smartlead inboxes × 25/day).
- Smartlead + 9 inboxes + 3 secondary .nl domains: **TODO Phase 2 "Smartlead inbox warm-up complete (3 weeks)" is UNCHECKED**; memory records secondary domains as BLOCKED.
- The binding operational constraint actually in force (`docs/03-delivery/website-voorstel-playbook.md`, CLAUDE.md, belsheet) is **6 sends/day = ~130/month** on one SMTP mailbox.
- **The plan's channel model is 35× the volume the business is currently permitted to send, and 88× the volume it has actually sent.**

---

## 3. TIME TO 10 CLIENTS — arithmetic

### 3.1 On measured velocity: undefined (infinite)

30 sends, 0 replies, 1 dial, 0 closes, **and 8 days of zero outreach activity**. A rate of 0 closes/month never reaches 10.

### 3.2 On the email path, using the plan's own conversion rate + real send capacity

10 clients × (667 to 1,000 sends per client) = **6,670 – 10,000 sends**.

| Send rate | Source | Months to 10 clients |
|---|---|---|
| 82/mo (2.7/day — the measured rate during the 11-day active window) | actual | **81 – 122 months (6.8 – 10.2 years)** |
| 130/mo (6/day — the founder's own compliance cap) | policy | **51 – 77 months (4.3 – 6.4 years)** |
| 4,500/mo (plan assumption) | `funnel-benchmarks.md` | 1.5 – 2.2 months — **requires infrastructure that does not exist** |

**Email alone cannot get to 10 clients under the constraints the business has actually adopted.**

### 3.3 On the phone path, using the playbook's own "what good looks like"

`docs/02-sales/cold-call-playbook.md` §6: **50 dials/week → 10-15 gesprekken → 1-2 demos/week** (realistic column). `funnel-benchmarks.md`: demo → won = 30-35%.

- 1-2 demos/wk × 4.3 wks = 4.3 – 8.6 demos/mo
- × 30% close = **1.3 – 2.6 clients/mo**
- 10 clients = **3.8 – 7.7 months of sustained 50 dials/week**

That is ~215 – 430 dials per client, and ~2,150 – 4,300 dials total. **Dials logged to date: 1.**

### 3.4 Realistic answer

If the founder starts and *sustains* 50 dials/week from the planned riool sprint (week of 24 Aug 2026):
- first client ≈ **late September / October 2026**
- 10th client ≈ **April – August 2027**, i.e. **8 – 12 months from today**, and that assumes no slippage, no bouwvak, no build weeks.

The plan's "10 clients" milestone corresponds to master-plan month 3-4 (8 clients at M3, 13 at M4). Against a start date of 2026-05-18 that was due **~August-September 2026**. On measured velocity it is **8-12 months late before it has begun.**

### 3.5 What 10 clients is actually worth (correcting the plan)

The plan claims 10 clients = **€3,590 MRR** — that is 10 × €359, the **70/30 Chat/Compleet blend**. Compleet cannot be sold (see §4). Corrected:

| Scenario | MRR at 10 clients |
|---|---|
| Plan (70/30 blend) | €3,590 |
| **Reality: Chat-only, all at list** | **€2,990** (−17%) |
| Reality: all 10 are founding members in month 1 (€149) | **€1,490** (−58%) |
| Reality: all 10 prepay 6×€149 = €894 | **€1,490/mo for six months** (−58%) |

Free cash at 10 Chat clients: €2,990 − COGS €100 − fixed €529 = **€2,361/mo**, vs the plan's €2,836 (−17%).

Founder draw of €3,500: 289N − 529 ≥ 3,500 → **N ≥ 14 Chat clients**, not 13. The plan's "13 clients covers €3,500" holds only on the blended €359 ARPU that requires a live voice product.

### 3.6 The €500 install fee assumption is contradicted by written policy

The plan assumes €500 average installation. Live documents:
- Chat setup fee is **€249**, and it is **waived for pilots** (`offer-and-pricing.md`) **and waived for every founding member** (`founding-member-offer.md`: *"Setup (normaal €249) waived for founding members"*).
- The founding cohort is capped at **exactly ten clients**.
- ⇒ **For the first 10 clients the install fee is €0 by written policy.** The plan books €5,000 of cash that policy forbids collecting.
- The only four-figure install fees in the repo are voice/website deals: DRS €1.395 (with an off-paper waiver lever), Cool Global €945, website €1.000.

---

## 4. WHAT IS ACTUALLY BUILT AND SELLABLE

### 4.1 Chat — technically deliverable, commercially not invoiceable

| Capability | Status | Evidence |
|---|---|---|
| Conversational product (Claude tool use, booking, take-message, art. 50 disclosure) | **Built and verified** | `ai-receptionist/app/`, goldens in `app/evals.py`, TODO §B all ticked |
| Per-client config + deploy | **Built**: `config/clients/<slug>.yaml` + Caddy vhost + `ops/hetzner/deploy.sh`; **manual per client** (DNS A record, grey cloud, Caddyfile edit, restart) | `docs/03-delivery/client-go-live-runbook.md` §1 |
| Server live | **Yes** — Hetzner, demo verified end-to-end 2026-07-14 | TODO §E |
| Widget embed | **Built**, `widget.js` live; per-CMS guide exists | runbook §2 |
| Monitoring | **Timers deployed** (watchdog / digest / analyst / retention in `ops/hetzner/*.timer`) but **delivery is dark** — `OWNER_TELEGRAM_CHAT_ID` unset, so "the whole NEEDS ATTENTION mechanism is dark" | `app/notify.py:84`, `churn-prevention.md` lines 34-38 |
| Checkout / recurring billing | **Mollie live key + webhook + subscription code shipped**; proven only with a €1 test | `app/billing.py`, `billing.jsonl` |
| **Invoicing** | **BROKEN — invoices are not legally valid** | `app/invoice.py` (see §5) |
| WhatsApp channel | **Twilio SANDBOX** — cannot send approved templates; blocks every outbound module. Needs Meta Business verification | TODO §D line 106 |
| Insurance (required before first paying client goes live) | **Not bought** — Hiscox quote box unticked | TODO Phase 0.5 |
| Moneybird | **Not opened** | TODO §D |

**Verdict: real money can be *collected* today (Mollie works), but it cannot be *invoiced* legally.** For a Dutch BV buyer that is a hard stop — they need a valid factuur per charge to reclaim BTW, and month two is when their bookkeeper chases it.

### 4.2 Compleet / voice — dormant, and being sold anyway

- `klantkraan/apps/voice-agent/README.md:3`: **"Status: DORMANT (2026-07)."** Blocked on LiveKit Cloud creds, Deepgram/ElevenLabs keys, and a Dutch `voice_id` — still literally `TODO_DUTCH_VOICE_ID` in `main.py`.
- `offer-and-pricing.md`: *"only Chat is sellable today… Compleet is quoted as the upgrade path, **never sold before voice is verified live**."* Repeated verbatim in `founding-member-offer.md` and `pilot-offer.md`.
- **Both live offertes violate this rule.** DRS (€685/mo) and Cool Global (€499/mo) are voice deals. They are being served by a **vendor ElevenLabs agent** (commit `72ba6d0` "DRS number live — +31 970 imported to ElevenLabs"), not the self-hosted LiveKit stack the unit economics assume — and memory records the founder must still upgrade the ElevenLabs tier.
- **COGS consequence:** `cogs-per-tier.md` puts Compleet at €35/mo assuming **150 voice minutes** and explicitly warns *"Do not treat as validated until the voice agent runs in production"* and *"TTS pricing is the dominant Compleet COGS line."* DRS is quoted **1.500 included minutes = 10×**. Scaling the per-minute lines (TTS €12 + STT €1 + telephony €1.50 + Claude €3 at 150 min) by 10 gives ≈ **€175 + €17.50 fixed ≈ €192/mo COGS on a €685 deal → ~72% GM, not 93%.** The blended 95.1% GM in `unit-economics.md` does not survive the deals actually on the table.

**What specifically blocks selling Compleet:** (1) LiveKit Cloud creds + Deepgram/ElevenLabs keys + a chosen Dutch `voice_id` — all founder actions, all still open; (2) no measured per-minute COGS, which `offer-and-pricing.md` makes a precondition for even requoting the price; (3) Synthflow Dutch voice test (master plan §5 item 8) never done; (4) CM.com Dutch landline (item 9) never reserved.

---

## 5. THE BILLING BLOCKER — exact location and fix

**File:** `/Users/bigd/Documents/marketing/infrastructure-automation/ai-receptionist/app/invoice.py`, lines 52-90.

```python
PLACEHOLDER_BTW = "NL000000000B00"
PLACEHOLDER_ADDRESS = "Adresgegevens volgen"

SELLER = {
    "name": "T4 Software Consulting BV",
    "trade_name": "Klantkraan",
    "kvk": "90232135",
    "btw":     os.getenv("BILLING_SELLER_BTW", "")     or PLACEHOLDER_BTW,
    "address": os.getenv("BILLING_SELLER_ADDRESS", "") or PLACEHOLDER_ADDRESS,
    "email":   os.getenv("BILLING_SELLER_EMAIL", "hallo@klantkraan.nl"),
    "iban":    os.getenv("BILLING_SELLER_IBAN", ""),
}
```

`identity_complete()` returns `(False, ["BILLING_SELLER_BTW", "BILLING_SELLER_ADDRESS"])` whenever those env vars are unset. Every send surfaces `result["placeholder_identity"]`, and the CLI prints:

> `⚠️  Nog niet rechtsgeldig: BILLING_SELLER_BTW, BILLING_SELLER_ADDRESS staat nog op een placeholder.` (line 337)

The docstring is explicit (line 83): *"A factuur with a placeholder BTW-id is not legally valid."*

**What is actually unset — and an important nuance:**
- The **BTW-id is known**. `klantkraan/apps/marketing-site/src/data/company.ts` already carries `kvk: '90232135'` and `btw: 'NL004800098B81'`, and the DRS offerte header prints `KvK 90232135 • BTW NL004800098B81`. **It has simply never been written into the production `.env` as `BILLING_SELLER_BTW`.** That is a one-line env edit plus a redeploy.
- The **address is genuinely unknown**. `PLACEHOLDER_ADDRESS = "Adresgegevens volgen"`, and the DRS offerte still ships `{{Adres}}` as a raw template placeholder on line 11. A Dutch factuur requires the seller's address; there is no filed business address anywhere in the repo.
- `BILLING_SELLER_IBAN` is also empty (defaults to `""`).

**Tracked as:** TODO `§P8` — two unticked FOUNDER boxes:
1. `FOUNDER: fix seller BTW-id/address placeholders (invoices not legally valid yet — also blocks §D and the BTW memory item)`
2. `FOUNDER: the pilot needs a real buyer`

Also blocked downstream: TODO `§D` first box (KvK + BTW → `company.ts` → renders on `/over`, legal pages, offerte template) is unticked even though `company.ts` now holds both numbers, and `website-pilot-runbook.md` Stage 0 carries the same blocker verbatim: *"seller BTW-id/address placeholders in the billing config make invoices legally invalid (see TODO §P8). Resolve before invoicing the pilot."*

**Effort to fix: ~10 minutes of typing plus one decision.** Set `BILLING_SELLER_BTW=NL004800098B81`, `BILLING_SELLER_ADDRESS=<real address>`, `BILLING_SELLER_IBAN=<iban>` in the prod `.env`, redeploy, re-run a €1 checkout and confirm `identity_complete()` returns `(True, [])`. The only real work is deciding/filing the business address. **This blocker has been open since at least 2026-07-29 and sits in front of every euro of revenue.**

---

## 6. FOUNDER THROUGHPUT — quantified

### 6.1 Per-client setup

`docs/03-delivery/onboarding-playbook.md` — headline: *"signed → live in ~5 days, ≤ ~2h founder time (~112 min to go-live)."*

| Step | Founder min |
|---|---|
| Pre-build (scrape + config + staged demo) | 15 |
| Day 1 paste prices/spoed/lead-destination, WhatsApp gap-fill, verify art. 50 | 25 |
| Day 2 kickoff (15 min) + calendar + test booking | 15 |
| Day 2-3 calendar provider + drop config + redeploy | 10 |
| Day 3 5 test chats + verify booking + notification | 20 |
| Day 3-4 widget install | 15 |
| Day 4-5 YAML tweaks from transcripts | 7 |
| Day 5 go-live confirm | 5 |
| **To go-live** | **112 min (1.87 h)** |
| + Day 14 check-in | 5 |
| + Day 30 review + case-study capture | 45 |
| **Through day 30** | **162 min (2.7 h)** |

Notes: the doc states "~157" for the 30-day total, which silently drops the day-14 check-in — the rows sum to 162. `first-hire-triggers.md` uses **130 min** as the planning number for a new client. 112 min against a ≤120 min budget is **8 minutes of slack**; the doc itself flags widget install ("can balloon on an awkward CMS") and the calendar connection as the two soft numbers. **Zero of this has ever been measured — no client has been onboarded.**

### 6.2 Per-client ongoing

`docs/03-delivery/churn-prevention.md` §1 — *"Steady-state cost per client: about 35 minutes a month."*

| Cadence | Founder min |
|---|---|
| Monthly tune | 15 |
| Day 30/60/90 value Loom | 12 |
| Quarterly full-transcript read (20 ÷ 3) | ~6.7 |
| **Per client / month (months 1-3)** | **~35** |
| Weekly digest read across ALL clients | 10 min/week (shared) |
| Day 45 case-study capture | 10 (one-off) |

The 12-min Loom only runs in months 1-3, so **true steady state after day 90 is ~22 min/client/month**. The doc's own honesty note: the automated 0-cost rows are **not currently delivering** — Telegram digest/analyst are switched off pending `OWNER_TELEGRAM_CHAT_ID`, so the weekly read is a manual `python -m app.oversight digest --dry`. And the shared "10 min/week to read all clients' digests" does not scale — at 20 clients that is 30 seconds per client.

Additional unbudgeted founder time:
- **~10 min per *prospect*** for a voorstel-site (`website-voorstel-playbook.md`) — pre-sale time spent on people who have bought nothing.
- Website pilot delivery: **~60 min target** (`website-pilot-timing-log.md`), really **~75 min** once the runbook's 15-min QA stage is counted (the timing log lists QA as 0). **The timing log is completely empty — every "Actual founder-min" and "Wall clock" cell is blank, the client name is still `____`, and git shows it has never been edited since creation. No pilot has ever run.**
- Included-scope change requests: unlimited text/price/hours edits, same working day, **never invoiced** (`onboarding-playbook.md` §1c).

### 6.3 Hours per month at 10 and 20 clients

Assuming plan pacing of 5 new clients/month and 130 min per onboarding:

| | 10 clients | 20 clients |
|---|---|---|
| Ongoing account management @35 min | 5.8 h/mo | 11.7 h/mo |
| Ongoing @22 min (post-day-90 steady state) | 3.7 h/mo | 7.3 h/mo |
| Weekly all-client digest read (10 min × 4.3) | 0.7 h/mo | 0.7 h/mo (understated) |
| New-client onboarding (5/mo × 130 min) | 10.8 h/mo | 10.8 h/mo |
| **Delivery subtotal** | **~15-17 h/mo (3.5-4 h/wk)** | **~19-23 h/mo (4.4-5.4 h/wk)** |

Delivery alone looks survivable. **The collision is with sales.** Using the repo's own numbers:

| Activity | Hours/week |
|---|---|
| Cold calling at 50 dials/wk (the rate §3.3 requires; ~3-5 min/dial incl. logging) | **4-5** |
| Discovery + offerte (`first-hire-triggers.md` M6 line) | **6** |
| Voorstel sites at 10 min × ~10 prospects/wk | **1.7** |
| Content (`first-hire-triggers.md`: 5 LI + 1 blog + 1 newsletter) | **8** |
| Delivery at 20 clients | **5.4** |
| Ops / stats QA / digests | **3** |
| **Total** | **28-29 h/wk** |

Against:
- `first-hire-triggers.md` founder budget: **12-15 h/wk**
- `weekly-kpi-review.md` §5 escalation trigger: **>25 h/wk for 2 consecutive weeks → post a VA job within 7 days**
- `risk-register.md` R-OPS-01 early warning: **>55 h/wk** (the register and the KPI doc disagree by 2.2×)
- 90-day roadmap off-track signal: **founder hours/week > 25h → productize onboarding to ≤2h** (already at 2h; there is no further slack there)

`first-hire-triggers.md` runs this same calculation for M6 / 22 active clients and concludes: *"~21 h/wk needed before any strategy/planning/ops. That's above the 15h budget. **Wall hit. VA averts it.**"*

**Quantified answer: the founder hits the throughput wall somewhere between 15 and 22 active clients, at roughly 21-29 h/wk, i.e. before the business reaches the 14 clients required to cover a €3,500 draw on Chat-only pricing.** The mitigation (a €600/mo VA at 12 active clients) costs €600/mo against 12 × €289 contribution = €3,468 — affordable, but it arrives *at* the wall, and the four planning docs disagree on when 12 clients lands (M4, M5-6, M6, or M9).

**The deeper problem is upstream of all of this.** At 0 clients the founder spends 0 h/wk on delivery and still has not sustained the ~10-11 h/wk of dialing + discovery the plan needs. Throughput is not currently the binding constraint — *initiation* is.

---

## 7. COMMITMENTS ALREADY MADE THAT BIND FUTURE PRICING

| # | Date | Commitment | Binding on |
|---|---|---|---|
| 1 | **2026-07-31** | **VoltWerk Elektrotechniek**, on a recorded cold call: *"eerste maand gratis, tweede maand 150 euro, en pas als u blij bent naar de volledige prijs van 300 euro per maand. Zonder opstartkosten, en 30 dagen geld terug."* Also inverted the guarantee. Resolution in `call-review-2026-08-01-voltwerk.md`: **"honor the promised terms for THIS prospect… put them in writing… never improvise pricing again."** | One client, **no expiry date attached anywhere**. Costs ~€149 more than the standard founding rate over months 1-2 and prices at €300 not €299 thereafter. |
| 2 | **2026-07-31** (decided) | **Founding-member offer**: first month €149, then €299. Or 6 months prepaid = **€894** excl. BTW, €299/mo from month 7. **Setup €249 waived.** Traded in writing for a testimonial, case-study permission and one reference call. | **Hard cap: 30 September 2026 or the 10th signed client, whichever comes first — 45 days left.** Applies to *exactly* the first 10 clients the financial plan models. |
| 3 | undated, `pilot-to-paid.md` | **"Founding 10 prijsvast: €299 vast voor 12 maanden"** for the first 10 of the July round. | A **12-month price freeze** that the canonical founding-member doc never mentions and never retires. Directly contradicts commitment #2. |
| 4 | **2026-08-06**, valid **t/m 20-08-2026** | **Slotenmaker DRS** offerte KK-2026-08-01: €685/mo incl. 1.500 min, €0,40/min over, €1.395 install 50/50. Live Mollie payment link expiring the same day. Plus: **"Uiterlijk zes weken na oplevering draait de dienst volledig op Europese servers, zonder meerkosten."** Plus an **off-paper €1.395 setup waiver** held as a conversation lever, contingent on conversion to a jaarcontract within a month. | **Expires in 4 days.** Reply received 2026-08-13 with a new unpriced ask (dispatch automation). Both the offer date and the expiry are still `{{template}}` placeholders. |
| 5 | **2026-08-10**, valid **until 24-08-2026** | **Cool Global Mallorca**: €499/mo incl. 750 min, first month 50% off (€249,50), €945 install, chat-only fallback €299 with no install. ES reverse-charge. Same **EU-servers-within-six-weeks** promise. | **Expires in 8 days.** |
| 6 | ongoing | **Website pilot pricing locked**: €1.000 ex btw (€749 bundled with a receptionist plan) + **€39/mo onderhoud**, max 2 text/photo edits per month, **max 10-15% discount on the site side only, never on the receptionist**, plus a mandatory **IP-transfer akte** on final payment. | Every future website deal. |
| 7 | planned M3, 90-day roadmap | **Accountant partnership: 10% rev-share for 12 months.** | Not yet signed — but it is the plan's own CAC assumption for the partnerships channel (~€60 effective). |
| 8 | `churn-prevention.md` | **"Powered by Klantkraan" badge = €25/mo discount.** Win-back template at +90 days offers **"Eerste maand gratis, echt nu, geen verplichting."** | Permanent 8.4% ARPU haircut per badged client; a free month contradicting the "no free trial" rule. |
| 9 | `onboarding-playbook.md` §1c | **Unlimited** text changes (prices, hours, services, FAQ, spoedbeleid, persona), same working day, **never invoiced**. | Every client, forever. |

**Policy conflicts worth flagging:** three mutually inconsistent first-client prices are live simultaneously (#1 vs #2 vs #3). `pilot-offer.md` is marked **superseded 2026-07-24** but `pilot-to-paid.md`, `demo-outreach.md`, `28-day-sprint.md` and the outreach batches still sell the retired free 14-day pilot and are flagged "pending alignment" — 23 days later, still unaligned. And both live offertes (#4, #5) sell Compleet, which `offer-and-pricing.md` forbids until voice is verified live.

---

## 8. TIMELINE SLIPPAGE

### 8.1 `docs/01-strategy/90-day-roadmap.md`

The roadmap contains **no absolute calendar dates** — every milestone is relative ("Month 1", "Week 12 (Day 89)") — and **not one milestone is marked done**. Anchoring Week 1 to the first strategy commit (`2026-05-18`), **today is Day 90**. Measured against that anchor:

| Milestone | Due | Plan target | Actual today |
|---|---|---|---|
| **M1 stop-gate (a)** demo rated "natuurlijk" by 5 outside listeners | ~mid-June | pass before outbound | **no record — never done** |
| **M1 stop-gate (b)** ≥1 pilot live | ~mid-June | 1 | **0** — TODO Phase 2 "2 pilot clients onboarded" UNCHECKED |
| **M1 stop-gate (c)** MSA + DPA signed with pilots | ~mid-June | signed | **no pilots to sign with** |
| **M1 stop-gate (d)** Mollie + Moneybird invoicing tested end to end | ~mid-June | pass | **FAILED** — Mollie €1 test only; Moneybird never opened; invoices legally invalid |
| M1: 2 pilot clients | ~mid-June | 2 | **0** |
| M1: 4 LinkedIn posts + 2 SEO cornerstones | ~mid-June | 4 + 2 | posts drafted, publishing unticked; cornerstones ticked |
| M2: Sequence A to ~1,500 prospects | ~mid-July | 1,500 | **30 sends to 18 prospects (2%)** |
| M2: 3-5 new paying clients | ~mid-July | 3-5 | **0** |
| M2: MRR end of month | ~mid-July | €1,500-2,000 | **€0** |
| M2 stop-gate: deliverability >95%, reply >5%, ≥1 client without an intro | ~mid-July | pass | **reply 0%, bounce 5.6%, 0 clients — FAILED** |
| M3: 8 paying clients | ~mid-Aug | 8 (bear 6 / bull 11) | **0** |
| M3: MRR | ~mid-Aug | €1,940-3,300 | **€0** |
| M3: Google Ads €400/mo live | Week 9 | live | **not launched** |
| M3: first accountant partnership (10% rev-share) | Week 10 | signed | **none approached** |
| M3: KPI dashboard automated | Week 10 | automated | **TODO §N5 unticked — founder must still run `kk deploy server`** |
| **Week 12 / Day 89: 90-day retrospective** | **~2026-08-15** | run it | **overdue; `01-strategy/quarterly-{YYYY-Qn}.md` does not exist** |

**Every outcome milestone is at zero. Both stop-gates failed. Outbound was started on 2026-07-29 anyway, with M1's four gate conditions all unmet.**

### 8.2 `docs/10-ops/risk-register.md`

The register has **55 rows, all owned by "Founder", none carrying a date, and no status column** despite the header defining one. It has **never been reviewed**: no quarterly memo exists, the 10 quarterly-checklist boxes are all `[ ]`, `10-ops/incidents/` does not exist, and `docs/regressions.md` holds a header with zero entries. Git shows only creation (2026-05-20), two July edits and a formatting-only pass on 2026-08-15.

Warnings that have **already fired and were never logged**:

| Risk | Early warning | Actual |
|---|---|---|
| **R-COM-01** cold-email deliverability | bounce **>3%** | **5.6% of prospects / 3.3% of sends** — fired |
| **R-FIN-01** cash bridge insufficient | cumulative cash **<€2k at M2 end** | ~3 months of €450-500/mo burn against **€0 revenue** — ~€1,350-1,500 spent, no offsetting income. The bridge is being consumed at plan rate with none of the plan's revenue |
| **R-COM-03** content engine stalls | founder logs **<3 publishing hours/wk** | 4 hook posts drafted 2026-08-14, pending in an uncommitted growth-engine queue, dry-run only — **nothing has been posted live** |
| Weekly KPI review escalation | MRR **<80% of plan for 2 consecutive weeks → 3h emergency reposition workshop** | €0 vs €300 plan at M1 = **0% of plan, continuously, for three months.** The workshop has never been held |
| Weekly KPI review itself | Friday 16:00, one Notion page per ISO week | **no week has ever been logged; `weekly-kpi-review.md` contains targets only, zero actuals** |

`docs/00-MASTER-PLAN.md` §5 / TODO Phase 0.5 — **7 of 14 blocking founder actions still unticked**, including **Hiscox liability insurance** (the master plan requires it *"in place before the first paying client goes live"*), the Synthflow Dutch voice test (item 8, the one that *"validates the core product promise before selling"*), CM.com landline, Moneybird, the €5-6k cash-bridge confirmation, and the LinkedIn audit.

One external date has also passed: **EU AI Act art. 50 became enforceable 2 August 2026** — 14 days ago. It is the sharpest hook in the belsheet (*"vanaf zondag verplicht; die van ons doet het al netjes"*) and it has been used in zero conversations since, because there have been zero conversations.

### 8.3 The sprint that was scheduled and did not happen

`research/first-client-market-research-2026-08-10.md` §7 set a first-client sprint for the **week of 11 August**, with an explicit principle — **"stop building, start dialing"** — and a hard success metric: **"25+ dials logged in `pipeline call` by Friday, 3+ demos delivered via WhatsApp, 1 pilot agreed."**

Measured outcome as of 2026-08-16:

| Sprint task | Target | Actual |
|---|---|---|
| Dials logged | **25+ by Fri 14-08** | **0** (pipeline files untouched since 2026-08-02) |
| Demos delivered via WhatsApp | 3+ | **0** |
| Pilot agreed | 1 | **0** |
| New A-list prospects added + qualified | 10-15 | **0** — no new pipeline yaml since voltwerk on 2026-08-02 |
| Clear sequence debt: 6 overdue T1s + 11 overdue T2s | send them | **0 sent** — last email in the ledger is 2026-08-08 07:14 |
| T4 for the first six | due 12/13-08 | **not sent** |
| Log DRS + Cool Global into the pipeline CLI | 2 records | **0 — still Markdown-only** |
| Chase DRS | call | reply arrived 13-08 unprompted; no repo record of a response |

**In the same six days, 103 commits landed.** Every one is engineering: the website design-vocabulary track, the anti-template gates, the photo pipeline, the stock-set factory, the email-cursus engine, prettier fixes. The 12 commits carrying a `sales:`/`air:` prefix are all code (`sitedraft`, `enrich.py`, cursus/nieuwsbrief plumbing) — **not one is an outreach action.**

---

## 9. THE PLAN, LINE BY LINE, AGAINST REALITY

| Plan claim | Repo reality | Verdict |
|---|---|---|
| 10 paying clients → **€3,590 MRR** | 10 × €359 assumes a 70/30 Chat/Compleet blend. Voice is DORMANT and forbidden to sell. Chat-only = **€2,990**; founding cohort in month 1 or on prepay = **€1,490** | **Overstated 17-58%** |
| **€2,836/mo free cash** at 10 | €2,990 − €100 COGS − €529 = **€2,361** | Overstated 17% |
| **13 clients** covers a €3,500 draw | On Chat-only: 289N − 529 ≥ 3,500 → **N ≥ 14** | Off by 1-2 clients |
| **CAC €150-250** | 0 clients acquired. Spend to date with 0 customers ⇒ CAC undefined/infinite. The €150-250 assumes a Smartlead/HeyReach machine at 4,500 sends/mo that **does not exist** | Unvalidated; the channel it rests on isn't running |
| **Churn 20%/yr** | 0 clients ever ⇒ **0 churn observations**. Unfalsifiable | Unvalidated |
| **Chat COGS €10** | `cogs-per-tier.md` is explicit: *"conservative estimates pending real usage data"*, assumes ~300 conversations/mo (never observed) and Hetzner amortised at **~30 clients/box** (€0.50). At 10 clients the box is €1.50/client, at 1 client ~€15 ⇒ real COGS **€11-25** | Optimistic at low client counts |
| **Fixed burn €529/mo** | `unit-economics.md`: **€450-500/mo** ex-ads — but that already amortises **insurance that has not been bought**, and excludes the **€400/mo Google Ads** the plan's own M3 assumes (**€900-1,000/mo total**) | Roughly right today, understates the planned state by €400 |
| **€500 average install fee** | Chat setup is **€249, waived for pilots AND all 10 founding members** ⇒ **€0 for the first ten clients** | Contradicted by written policy; ~€5,000 phantom cash |
| **Founding offer €149 first month / €894 prepaid** | Correct and canonical — but caps at **30 Sept 2026 or 10 clients**, and the prepay path means **€149/mo ARPU for six months, not €299** | Correct; its MRR consequence is not modelled |

---

## 10. THE SINGLE BIGGEST GAP

The plan models a **revenue business making a distribution decision**. The repo is a **product-engineering business that has not yet started selling**.

- Assets built: 30 branded demos, a 259-line cold-call playbook, a 193-line belsheet, a website factory, an email-cursus engine, a status dashboard, four systemd timers, a voice agent, a de-templating gate system.
- Selling done: **30 emails, 1 phone call, 2 offertes, 0 closes.**
- Six days ago the repo's own research named this exactly — *"The bottleneck is dials, not assets… No research finding matters more than this"* — and scheduled 25 dials by Friday. **103 commits later, the dial count is still 1.**

Every input the plan needs (CAC, churn, COGS, cycle time, install fee, activation rate, onboarding minutes) requires **one paying client** to become real. There is a €10-of-typing blocker (`BILLING_SELLER_BTW`) and one missing decision (the business address) standing between the business and its first legally invoiceable euro, and it has been open for at least 18 days while 103 commits of unrelated engineering shipped.
