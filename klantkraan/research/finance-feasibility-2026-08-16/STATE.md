# Financial-plan feasibility research — state, 2026-08-16

Seven parallel agents were sent at the load-bearing assumptions of the financial plan
(`docs/07-finance/unit-economics.md`, `cogs-per-tier.md`, `docs/01-strategy/offer-and-pricing.md`,
`docs/04-legal/insurance.md`). The Anthropic session limit hit mid-run at ~16:37 and killed four
agents before they could summarise — but six of the seven had already written their findings to
disk. Those six files are here, complete and unabridged.

## What is in this folder

| File | Status | Summarised in chat? |
| ---- | ------ | ------------------- |
| `research-insurance.md` | complete | YES — read and reported |
| `research-churn.md` | complete | YES — read and reported |
| `research-cac.md` | complete | **NO — agent died before summarising. UNREAD.** |
| `research-internal.md` | complete | **NO — UNREAD.** Repo reality check: real clients, measured funnel, billing blocker, founder hours |
| `research-market.md` | complete | **NO — UNREAD.** TAM, competitor pricing, incumbent bundling |
| `research-tax.md` | complete | **NO — UNREAD.** Eenmanszaak vs BV, BTW on prepay, invoice validity |
| `research-cogs.md` | **MISSING** — agent died before writing | — |

Four files have never been read by anyone. Read them before acting on anything in them.

## Findings already confirmed (from the two agents that reported)

### Churn — the model was optimistic by ~2x

| | Plan | Corrected |
| --- | --- | --- |
| Monthly churn | 1.84% | **4.0%** (band 3.0–5.5%) |
| Client life | 54 mo | **25 mo** |
| LTV | EUR 15,000 | **EUR 7,228** |
| LTV/CAC @ EUR 400 | 48–130x | **18.1x** |

The plan's "EUR 600 CAC still yields 15x+" claim fails — it becomes 12.0x.

**The ceiling, not the treadmill, is the problem.** Replacing churn at 10 clients needs only
0.4 new clients/month. But sustainable book = deals per month / churn rate, so at 2 deals/month
the founder plateaus at **50 clients / EUR 14,950 MRR**, not the ~109 clients / EUR 32,500 the plan
implies. A 2.2x overstatement of terminal size that stays invisible for ~18 months.

Three findings past the brief:
1. **No expansion revenue exists.** One flat EUR 299 price means logo churn = revenue churn and NRR
   is capped at 100% by construction. Every 96–110% NRR benchmark in the plan is unreachable.
2. **BV filter shrinks TAM hard** — only 13.1% of 143,395 SBI-43 firms are rechtspersonen, 85% are
   one-person. Addressable pool ~18,700, not 143k.
3. **CBS: SBI 43 closures tripled**, 3,695 (2021) -> 10,395 (2025). Business death alone puts a
   3.1–5.0%/yr floor under churn before anyone chooses to cancel.

Closest structural comparable is Weave (NYSE: WEAV) — month-to-month, ~$503 ARPU, small practices —
gross dollar retention decaying 94->92->91->89% across FY22–25, and that is *with* VoIP hardware
lock-in and EHR integration. Klantkraan has zero switching cost, so 89% is a ceiling not a base case.

Method note: that agent's WebSearch budget was exhausted, so it worked from SEC 10-Ks (filed Mar
2026) and the live CBS OData API instead. Stronger evidence. One gap: the "first 90 days cliff"
number is modelled, not sourced.

### Insurance — two problems, one of them structural

Corrected premium: **EUR 165–340/mo (plan on EUR 250)**, not the EUR 150–200 in `docs/04-legal/insurance.md`.
The cheap quotes found online (Yezzer EUR 35.30/mo ICT-consultant, Goudse EUR 37.50/mo) are for
**EUR 250k cover, not the EUR 500k/EUR 1M the plan specifies**; the EUR 20/mo ZZP cyber tier caps at
EUR 100k/yr. Add 21% assurantiebelasting.

**Standard NL beroepsaansprakelijkheid probably does not cover the thing we sell.** ISO AI
exclusions CG 40 47/48 and CG 35 08 went live 1 Jan 2026; 60+ P&C groups filed to adopt them.
Dutch brokers name the excluded profile explicitly — *"zelflerende systemen zonder menselijke
controle"* (Bavspecialist). Gartner via AG Connect, 14 Apr 2026: insurers increasingly refuse cover
for AI-agent and chatbot implementations. Hiscox NL *is* affirmative on AI but conditions it on
documented human oversight, testing and bias monitoring.

Verdict: **CONDITIONAL, defaulting to NO.** Three conditions all required — no generative-AI
exclusion by form number, AI activity inside the written *verzekerde hoedanigheid*, conduct
conditions met. Affirmative AI cover exists at EUR 390–1,170/mo, unaffordable until ~EUR 150k revenue.

Consequences:
- **"Cheapest risk transfer" is wrong.** A liability cap in the AV/DPA is cheaper and more certain
  (NLdigital caps ICT suppliers at EUR 500k). An uncapped DPA indemnity is contractually assumed
  liability, uninsured, and personal while the founder is an eenmanszaak. **Do this first.**
- Buying a EUR 35/mo online "ICT-consultant" policy produces the same nil outcome silently, plus an
  art. 7:928 BW misrepresentation argument.
- Claims-made + inlooprisico: clients live today are uninsured in a way retroactive cover will not
  repair. Bind sooner rather than later, but bind the *right* thing.
- AVG fines are conditionally insurable in NL (Aon; De Clercq 11 Mar 2026) but voided by grove
  nalatigheid — treat as bonus, not cover.

Genuine positives: Klantkraan is **not** Annex III high-risk. Art. 50 became applicable 2 Aug 2026
and Klantkraan is the *provider*, so the disclosure duty is its own — already implemented. The
existing evals / Cekura baselines / logs are exactly the governance pack that moves an AI-agent
quote from declination to quoted.

### Incumbent bundling — the category is empty by choice (bonus agent, complete)

**No Dutch or Belgian accounting or SMB-CRM vendor ships customer-facing AI answering.** Checked
and explicitly negative: SnelStart (full sitemap), Moneybird (MCP + doc recognition only),
e-Boekhouden.nl, Twinfield, Archie, PerfectView, Jortt (support bot answers *Jortt's* users),
Exact / Exact Bouw / Exact Gripp (7 AI agents, all internal — the Support Agent answers the
*builder's* how-to questions about Exact), Teamleader Focus AI (launched Jun 2026, internal only),
Simplicate Maistro (ships Oct, page states *"Maistro is geen chatbot of zoekfunctie"*).

Only two agents anywhere touch the outside world and both are outbound: Exact's Debtor Agent
(dunning) and Tribe CRM's outreach writer.

The only real AI-answering options are HubSpot Breeze Customer Agent (Professional tier only,
~$90–100/seat/mo before credits at $0.50/resolution, voice still beta, Dutch supported) and
Salesforce Agentforce ($2/conversation, no SMB entry). Neither is reachable from the EUR 30–100/mo
band a Dutch loodgieter already pays.

**The exposure is narrower than "will Exact do this":** a trade already paying for Exact Bouw
(EUR 129–359/mo) hears "AI-agents inbegrepen" and assumes the phone is covered. That is a positioning
problem, not a product one — worth one line of copy distinguishing *answering your customers* from
*helping you do your books*.

## Numbers this research has already invalidated

From `docs/07-finance/unit-economics.md` and `docs/04-legal/insurance.md`, do not reuse until fixed:
- 20% annual churn / 54-month life / EUR 15,000 LTV / 48–130x LTV/CAC
- "even at fully-loaded CAC of EUR 600, LTV/CAC stays 15x+"
- insurance EUR 150–200/mo, and the claim that it is the cheapest available risk transfer
- the implied ~109-client terminal book

Unverified and still to check: Chat COGS EUR 10 / Compleet EUR 35 (the COGS agent died before writing
anything — **WhatsApp moved to per-message pricing during 2025, so the EUR 3.00 WhatsApp line is the
prime suspect**), CAC EUR 150–250, TAM, tax reserve 35%, months-to-10-clients.

## Next actions when the session resets (17:50 Europe/Lisbon)

1. Read the four unread files: `research-internal.md` first (it is the reality check on actual
   clients, measured funnel and the invoice blocker), then `research-cac.md`, `research-market.md`,
   `research-tax.md`.
2. Re-run the COGS agent — it is the only missing dimension. Brief is in the chat history; the
   WhatsApp per-message repricing is the thing to nail.
3. Assemble one corrected feasibility document with a revised stage plan, and update
   `docs/07-finance/unit-economics.md` rather than leaving two contradictory sets of numbers in the
   repo.

## Unrelated but unpushed

`c7133be` — TODO T10, the site-factory composer. It turned out to be a live bug, not a missing
feature: `royaal` was already in the composer's vocabulary while `indeling.hero` defaulted to
`gesplitst`, the one pair the schema refuses, so every composed voorstel with the big display type
silently failed `pnpm build`. Fixed by removing the illegal value from the choice set before the
model sees it. 418 pytest, 49 node tests, `pnpm check` clean over 10 pages.
