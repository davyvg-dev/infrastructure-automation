# Should Klantkraan sell custom automation? — longevity analysis

**Date:** 2026-07-28 · **Question:** the receptionist is a feature, not a platform. Does business-process automation extend the business, and if so in what form, at what price, against whom?

---

## Bottom line

**Yes to workflow depth. No to an automation agency.**

The instinct is right: an AI receptionist alone does not survive five years. It is already commoditizing on three fronts at once. But the obvious way to go deeper — selling custom automation projects to whoever will buy them — converts a ~95%-margin product business into a ~20%-margin consultancy where the founder is the product. That is the wrong trade at 3–7 hours a week.

The version that works: keep one buyer (the Dutch trade owner-operator), keep one architecture (config over code), and extend **forwards along the job the receptionist already starts**. Lead → quote → job → invoice → paid → review → next year's service. The receptionist owns the first two steps. Each further step is a **module built once and sold to every client**, not a project built once and sold once.

Sell modules. Never sell hours.

**Timing: do not build any of this yet.** Item E in `TODO.md` is still open — there is no paying pilot live. Reposition the story now (free, and it is what protects the business); build module 1 when the first clients exist and ask for it.

---

## 1. Why the longevity worry is correct

Three separate clocks are running against "we answer your phone."

**The compliance wedge expires in five days.** Art. 50 disclosure becomes mandatory for everyone on 2 Aug 2026. From that date "we tell your customer it's AI" stops being a differentiator and becomes table stakes. Already flagged in `competitor-landscape-2026-07.md`; worth restating because it lands this week.

**The price floor is collapsing.** VoxFlow €99, Cowcierge €149, InstallatieTelefoniste at €0.25/min with no subscription at all. Answering the phone is converging on a metered utility. Utilities do not hold €299.

**The platforms are absorbing the feature.** Jobber ships a native AI Receptionist that checks calendar availability and books jobs. Housecall Pro has built-in CSR AI that auto-books and extracts call details. FieldCamp bundles AI dispatch plus receptionist natively. The US field-service platforms are two years ahead of the Dutch ones (Gripp, Veldwerk, Cobry, Robaws, OutSmart, Bouw7), which tells you exactly what lands here next. A standalone receptionist gets eaten by whatever system already holds the customer's job data.

This confirms the position already recorded in the founder strategy work: compliance and Dutch-nativeness are a **wedge**, not a moat. The moat is workflow depth plus the proprietary data that depth produces.

---

## 2. Why the automation-agency version fails

The evidence against project-based automation work is consistent and unkind.

| Failure mode | Evidence |
|---|---|
| Revenue is one-time; the sales cycle restarts every deal | Founders commonly pivot within 12–18 months because project overhead becomes unsustainable |
| Margins invert | Traditional service work runs 15–30% margin vs 70–80% productized |
| Integration debt compounds permanently | Maintenance grows linearly per connector; connector upkeep becomes a permanent engineering function, not a one-off build |
| Most of it never ships | MIT: ~95% of AI agent pilots fail. RAND: 80%+ never reach production |
| Underscoping is structural | Fixed fees quoted before data-access and integration discovery is done |

Two more objections specific to this business.

**Wrong buyer.** The Dutch custom-automation buyer profile is an SME with €500k+ revenue, 1,000+ customers, and processes unusual enough to justify bespoke work — paying €6k–15k for a first integrated solution, or €8k–35k for genuine custom AI plus €300–1,500/mo maintenance. Klantkraan's ICP is a 2–8 person trade business. A loodgieter with four vans does not have €8k of "business process" to automate, and does not think of himself as having processes at all. Selling BPA means abandoning the ICP, the vertical proof, and every sales asset already built.

**Wrong market to enter cold.** The NL field is crowded and undifferentiated — hundreds of bureaus claiming to "do something with AI," sitting under established RPA and low-code shops (Ciphix, Incentro, Peacock, DataDream, Prikr). None of them publish pricing, which tells you it is a quote-per-deal consulting market. That is a knife fight with no product leverage, entered from zero reputation.

**The founder-time argument settles it.** Custom automation is the one business model that scales strictly with founder hours. At 3–7 hours a week with no paying pilot live, it is not affordable.

---

## 3. What to build instead: modules on the job spine

Every trade job runs the same spine:

```
inbound → qualified → quoted → scheduled → done → invoiced → paid → reviewed → recurring service
   └─ receptionist owns this ─┘
```

The receptionist already sits at the front. Everything downstream is the same customer, the same WhatsApp thread, the same config file, the same tool-calling loop. `tools.py` currently defines exactly three tools (`check_availability`, `book_appointment`, `take_message`). A module is a fourth tool plus a scheduled job. `calendar_store.py` is already documented as the real-integration seam. The architecture was built for this.

The rule that keeps it a product: **a module ships only when it works for every client from a YAML field.** If it needs client-specific Python, it is a project and the answer is no.

### Module roadmap, ranked

Ranked by revenue impact to the client per unit of build effort.

**1. Offerte-opvolging (quote follow-up) — build this first**
Trades write quotes and never chase them. The bot already knows the job; after a quote goes out it follows up on day 2, 5 and 10 over WhatsApp, answers the objection, and books the go-ahead. Sells on revenue won, not time saved, which is the easier sale by a distance. Needs no accounting integration — the quote amount can come from a WhatsApp message or a form.

**2. Onderhoudsherinneringen (recurring service reminders)**
CV-ketel onderhoud, dakinspectie, airco-service. The bot knows what job it booked twelve months ago and rebooks it. This creates *recurring revenue for the client*, which makes Klantkraan the thing they cannot cancel. Highest retention value of anything on this list. Effort is low: a date field and a scheduled send.

**3. Factuur- en betaalopvolging (invoice and payment chasing)**
Payment chasing is the job every owner-operator hates most. Polite, escalating, in Dutch, never forgets. Here an accounting integration genuinely helps — Moneybird first (see §5).

**4. Reviewverzoek na de klus**
One message at the right moment. Google reviews are the trade's main local-SEO asset. Trivial to build, easy to demo, weak on its own — bundle it, never sell it standalone.

**5. Werkbon → factuur**
Monteur sends photos and hours over WhatsApp; the bot drafts the invoice. High value, materially harder, and it starts to collide with the FSM platforms. Later.

Data point for the sales case: a zzp-installateur spends ~300 hours a year on quotes, invoices and bookkeeping, and decent tooling reclaims 100–200 of them. At trade billable rates that is €6k–12k of recovered capacity a year — before counting the quotes that follow-up converts. The average MKB owner spends 15–25 hours a week on admin.

---

## 4. Pricing

Do not build a second price list. Two axes, cleanly separated:

- **Channels** = the base subscription (what it answers on)
- **Workflows** = modules (what it does)

| | Monthly | Contents |
|---|---|---|
| **Chat** (existing) | €299 | webchat + WhatsApp receptionist, booking, messages |
| **Kantoor** (new) | €599 | Chat + quote follow-up + service reminders + review requests |
| **Compleet** (existing) | +€200 on either | adds the voice line |
| Individual module | +€99–149 | for clients who want one thing, not the bundle |
| Koppeling setup | €500–1,500 one-time | only for an integration already on the roadmap (§5) |

Why €599 holds:

- Red Factory prices a comparable trade tool stack at €250–450/mo — and that is software the owner still has to operate himself. Klantkraan at €599 is done-for-you and replaces several line items.
- The NL "mid-market no-code automation" band is €300–1,500/mo. €599 sits mid-band with a vertical-specific product, not a generic build.
- Against custom (€6k–35k build + €300–1,500/mo), €599 with no build fee is a different category of decision.
- The €299 entry stays intact, so nothing about the current funnel or the founding-member offer breaks. Kantoor is an **upsell to existing clients**, which is where it earns twice: expansion revenue, and something to deliver in months 2–3 — the documented churn danger window, right after go-live excitement fades.

The one-time koppeling fee is real cash without the agency trap, but only under §5's rule. Two clients on the same connector and it is a product; one client and it is a project wearing a product's clothes.

---

## 5. The integration policy (this is what kills you)

Integration debt is the single mechanism that turns a product company into an agency. Connectors need permanent upkeep, and a bug fix in the Exact connector does nothing for the Moneybird one.

The policy:

1. **Standalone by default.** Every module must work with zero integrations — WhatsApp in, WhatsApp out, state in Klantkraan's own store. The smallest trades run on a notebook and a phone. For them the automation *is* the system, which is a stronger sale than an integration.
2. **Two accounting integrations, maximum, for the first year: Moneybird and e-Boekhouden.** These are the SMB standard. Moneybird has the materially better API; e-Boekhouden's is more limited. Exact Online is the enterprise-ward option and can wait for demand.
3. **Never integrate with an FSM platform to become a feature of it.** Gripp, Veldwerk, Cobry, Robaws, Bouw7 are systems of record that will grow their own AI. Read from them if a client asks; do not build a dependency on one.
4. **Three-client rule.** A new connector is built when three clients need it, or one pays the full build cost knowing it becomes a product.

---

## 6. Who you compete with once you do this

The rival set changes, and improves.

| Competitor | Their move | The counter |
|---|---|---|
| **FSM/ERP platforms** (Gripp, Veldwerk, Cobry, Robaws, OutSmart) — the real long-term threat | Own the job data; will add AI on top | They require adopting a full system at €125–200/mo for 5 users, plus migration. Klantkraan is a layer on WhatsApp with nothing to migrate. The under-8-person trades that will not adopt an ERP are exactly the ICP. **Do not try to become an ERP.** |
| **NL AI/automation bureaus** (Red Factory, SiRo, Timmermans, aiagency.nl, +hundreds) | Generic AI automation, quoted per deal, ~6 weeks to first workflow | Fixed monthly price, no build fee, live in days, trade-native out of the box, one supplier. They sell a project; Klantkraan sells a subscription. |
| **Voice receptionist rivals** (Voicelabs, Cowcierge, VoxFlow, InstallatieTelefoniste) | Racing each other to the price floor on answering calls | Once Klantkraan does the office work too, they are competing on a feature, not the product. This is precisely the escape from the €99 floor. |
| **DIY** (n8n, Make, Zapier) | €9–16/mo and build it yourself | A loodgieter will not. Not a real competitor for this ICP, but it is why the *pricing* has to be justified by done-for-you, never by the technology. |

The proprietary-data point compounds here: every conversation is data on what Dutch trade customers actually ask, which jobs convert, which objections kill quotes. Modules should be chosen partly for the data they add. No bureau accumulates that, and no platform has it for this vertical.

---

## 7. How to talk about it

**Never say "business process automation" or "AI-automatisering" to a trade owner.** That is agency language, it is what every NL bureau is already shouting, and it describes a method rather than a result. It also invites a comparison against €6k project quotes.

Sell named jobs in Dutch, on the same page as the receptionist:

- *"Offertes die zichzelf opvolgen."*
- *"Je onderhoudsklanten komen vanzelf terug."*
- *"Facturen die er zelf achteraan gaan."*

Positioning line for the site: Klantkraan stops being "de AI-telefoniste" and becomes **"het kantoor dat meedraait"** — it answers, it quotes, it chases, it books next year. Same product, one level up the value chain, out of the reach of a €99 answering bot.

This repositioning is free and should happen regardless of when modules get built, because it is the part that defends the category position.

---

## 8. Sequencing

The dominant constraint: `TODO.md` item E is open. No pilot is live and no client is paying. Building a second product before the first has proof is the classic way to end up with two unproven products.

| When | Do |
|---|---|
| **Now** | Reposition the story only. Add "wat er daarna gebeurt" to the site and sales deck as roadmap, not features. Costs nothing, defends against the price floor, and every discovery call becomes free research into which module clients ask for. |
| **First 3 paying clients** | Nothing new. Prove the receptionist, get the case study the whole `competitor-landscape` doc says nobody else has. |
| **~5 paying clients** | Build **offerte-opvolging**. One module, config-driven, standalone. Offer it free to the first three clients in exchange for numbers. |
| **Module 1 proven** | Launch the €599 Kantoor tier. Upsell existing clients first; new-client acquisition stays at €299. |
| **~10 clients** | Build module 2 (onderhoudsherinneringen) and the Moneybird connector — by then real demand will have ranked them, and this analysis will be a year stale. |

Gate on demand, not on ideas: **build module N+1 only when three paying clients have asked for it.**

---

## 9. The cash exception, stated honestly

There is one real argument for taking custom automation work: it pays now. The master plan needs a €5–6k personal bridge, and a single €6k–15k automation project covers it, where MRR takes months to.

That is a genuine trade-off and worth naming rather than dismissing. But it competes for the exact resource the compounding business needs — founder hours — and it does so during the months that decide whether Klantkraan gets off the ground.

If it is taken at all, cap it hard:

- Inbound only. No outbound selling of project work, ever.
- One project at a time, maximum.
- Minimum €5k. Below that the context-switching costs more than it pays.
- Only if the build leaves behind a reusable module or connector on the roadmap above.
- It is a bridge, not a business line. It never goes on the website.

---

## 10. What to say no to

- Hourly work, and "we can build anything."
- Any client outside the trades vertical.
- Any integration used by exactly one client.
- RPA, Power Platform, enterprise process work. Different buyer, different sales motion, well-defended by incumbents.
- Becoming an ERP or FSM platform. That is a five-year, funded fight against companies that already own the data.
- A separate "Klantkraan Automation" brand or site. One product, one ladder. Splitting the brand doubles the marketing surface and halves the proof.

---

## Sources

Market and pricing figures captured 2026-07-28. Vendor pricing changes fast — re-check before any pricing decision.

- [AI automatisering MKB 2026: kosten](https://www.timmermansmedia.nl/blog/ai/kosten-ai-automatisering-mkb-2026/) — NL tiers €50–300 / €300–1,500 / €1,500–5,000+ per month; per-workflow setup and monthly bands; 14-month median payback; buyer profile €500k+ revenue
- [AI-installatiebedrijven](https://redfactory.nl/kennisbank/ai-automatisering/ai-installatiebedrijven/) — NL trade tool stack €250–450/mo; automation use cases for installateurs; Gripp/Veldwerk/Cobry
- [De 10 beste bureaus voor bedrijfsprocessen automatiseren](https://appfront.nl/beste-bureaus-bedrijfsprocessen-automatiseren) — NL BPA agency field, no published pricing
- [Why Build a Productized AI Service (Not an Automation Agency)](https://stormy.ai/blog/productized-ai-service-vs-ai-automation-agency) — project-revenue failure mode, 12–18 month pivot pattern
- [The AI Agency Business Model That Unlocks 70% Margins](https://www.vendasta.com/blog/ai-agency-business-model/) — 15–30% service vs 70–80% productized margins; month 2–3 churn window
- [How much does an AI automation agency make](https://automatonagency.com/insights/ai-automation-agency-economics) — setup $2.5k–15k, retainers $500–3k/mo
- [Integrations for AI Agents](https://www.getknit.dev/blog/integrations-for-ai-agents) — linear connector maintenance burden, integration debt as permanent function
- [ServiceTitan vs Jobber vs Housecall Pro](https://www.pinkcallers.com/blog/servicetitan-vs-jobber-vs-housecall-pro-for-call-center-integration) and [Jobber alternatives 2026](https://fieldcamp.ai/alternatives/jobber/) — native AI receptionists shipping inside FSM platforms
- [Vertical SaaS Is Winning](https://www.saasmag.com/vertical-saas-niche-beats-horizontal-2026/) and [Vertical AI Agents Are Eating Horizontal SaaS](https://www.saasmag.com/vertical-ai-agents-eating-horizontal-saas/) — embedded-workflow retention, data moat requires depth within one vertical
- [Uurtarief installateur 2026](https://www.digiboox.app/nl/gratis-tools/uurtarief-installateur) — ~300 h/yr admin for a zzp-installateur, 100–200 h reclaimable
- [De echte kosten van administratie voor MKB-ondernemers](https://www.hartai.nl/blog/de-echte-kosten-van-administratie-voor-mkb-ondernemers/) — 15–25 h/week admin load
- [n8n vs Make vs Zapier voor MKB](https://www.timmermansmedia.nl/blog/ai/n8n-vs-make-vs-zapier-vergelijking/) — DIY platform costs €9–16/mo
- [Moneybird vs e-Boekhouden 2026](https://bedrijfssoftwaregids.nl/blog/moneybird-vs-e-boekhouden-2026/) — relative API capability
- Internal: `research/competitor-landscape-2026-07.md`, `docs/00-MASTER-PLAN.md`, `klantkraan/TODO.md`
