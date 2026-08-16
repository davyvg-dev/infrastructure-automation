# Klantkraan — tax & legal-structure stress test (2026 rules)

Researched 2026-08-16. All rates fetched live from Belastingdienst / Ondernemersplein /
wetten.overheid.nl. Calculations are mine, derived from those sourced rates.

Assumptions in every calculation: solo founder, below AOW age, eenmanszaak, no other
income, no fiscal partner effects, meets the urencriterium, Dutch resident.

---

## 0. The 2026 parameter set (all sourced)

| Parameter | 2026 value | Source |
|---|---|---|
| IB box 1 bracket 1 | up to **€38,883** @ **35.75%** (8.10% IB + 27.65% premies volksverz.) | belastingdienst box_1 |
| IB box 1 bracket 2 | €38,883–**€78,426** @ **37.56%** | idem |
| IB box 1 bracket 3 | above €78,426 @ **49.50%** | idem |
| Zelfstandigenaftrek | **€1,200** (phasing to €900 in 2027) | ondernemersplein |
| Startersaftrek | **€2,123**, max 3× in first 5 yrs | belastingdienst |
| MKB-winstvrijstelling | **12.70%** (of profit *after* ondernemersaftrek) | ondernemersplein |
| Tariefsaanpassing aftrekposten | deductions relieved at max **37.56%** | belastingdienst ondernemersaftrek |
| Algemene heffingskorting | max **€3,115**; full to €29,736; −6.398% above; €0 from €78,427 | belastingdienst tabel 2026 |
| Arbeidskorting | max **€5,685**; −6.510% above €45,592 | belastingdienst tabel 2026 |
| Bijdrage Zvw (aanslag, ondernemer) | **4.85%** (was 5.26%), max grondslag **€79,409** | belastingdienst |
| Werkgeversheffing Zvw | **6.10%** (was 6.51%) | idem |
| Vennootschapsbelasting | **19%** to €200,000; **25.8%** above | belastingdienst |
| Box 2 (dividend DGA) | **24.5%** to €68,843; **31%** above | belastingdienst box_2 |
| Gebruikelijk loon DGA | **€58,000** | KVK |
| Urencriterium | **1,225 h/yr** + more time on business than on other work | belastingdienst |
| KOR omzetgrens | **€20,000** per kalenderjaar | belastingdienst |
| BTW tijdvak default | **per kwartaal** | belastingdienst |

---

## 1. Eenmanszaak vs BV — and the "35% of profit" reserve

### Method
Belastbare winst = (winst − €1,200 zelfstandigenaftrek) × 87.30% (i.e. after 12.70%
MKB-winstvrijstelling). Box 1 tax on that, minus algemene heffingskorting and
arbeidskorting (winst uit onderneming counts as arbeidsinkomen), plus Zvw 4.85% on the
same base capped at €79,409. Tariefsaanpassing applied above €78,426.

### Eenmanszaak — total burden 2026

| Winst | Belastbare winst | IB na kortingen | Zvw 4.85% | **TOTAL** | **Effective** | 35% reserve | Over-reserved by |
|---|---|---|---|---|---|---|---|
| €34,000 | €28,634 | €1,767 | €1,389 | **€3,156** | **9.28%** | €11,900 | €8,744 |
| €40,000 | €33,872 | €3,802 | €1,643 | **€5,445** | **13.61%** | €14,000 | €8,555 |
| €80,000 | €68,792 | €20,532 | €3,336 | **€23,868** | **29.84%** | €28,000 | €4,132 |
| €100,000 | €86,252 | €31,231 | €3,851 | **€35,082** | **35.08%** | €35,000 | −€82 |

Year 1 with startersaftrek (€2,123 extra): €34k profit → €2,440 (7.18%); €40k → €4,610 (11.53%).

### VERDICT ON "35% of profit"

**35% is TOO HIGH as an average rate at every profit level in the plan.** It is exactly
right only at **≈ €99,500 profit**. At the €40k the plan is likely to hit in year 1 it
over-reserves by ~€8,500 of working capital.

**But it is TOO LOW as a marginal rate**, which is the trap:

| Profit band | Marginal rate on the next euro |
|---|---|
| €34k → €40k | **38.2%** |
| €40k → €80k | **45.6%** |
| at €80k | **48.3%** |

The marginal rate is brutal because three things phase out at once: algemene
heffingskorting (−6.398%), arbeidskorting (−6.510%), on top of 37.56% IB and 4.85% Zvw.

**Corrected rule:** reserve **30% of cumulative profit** (safe through ~€85k profit,
never over-reserves by more than ~€6k), and mentally price every *additional* euro of
profit above €40k at **~46% gone**. A single flat 35% is neither: it hoards cash at
low profit and understates the cost of growth.

### Eenmanszaak vs BV

BV modelled as: gebruikelijk loon €58,000 (capped at profit if lower), employer Zvw
6.10%, Vpb 19% on the remainder, full dividend distribution at box 2 24.5%.

| Winst | Eenmanszaak | BV | BV minus EZ | incl. ~€2k extra admin |
|---|---|---|---|---|
| €34,000 | €3,156 | €5,928 | **+€2,772 worse** | +€4,772 worse |
| €40,000 | €5,445 | €8,726 | **+€3,281 worse** | +€5,281 worse |
| €80,000 | €23,868 | €26,563 | **+€2,695 worse** | +€4,695 worse |
| €120,000 | €45,165 | €42,451 | −€2,713 better | −€713 better |
| €150,000 | €60,288 | €54,288 | −€6,001 better | −€4,001 better |

**Crossover: ~€97k profit on pure tax; ~€114k once you add ~€2,000/yr of extra BV
admin (jaarrekening deposit, loonadministratie for the DGA payroll, corporate filings);
~€130-135k if that admin realistically costs €4,000.**

**VERDICT: eenmanszaak wins decisively at €34k, €40k and €80k.** At the plan's stated
year-1 omzet of €40–80k, profit will be *below* revenue, so the BV question is not close
— it is €3,000–€5,000/yr of pure loss. Do not incorporate for tax reasons before profit
is durably above ~€120k.

Two reasons that could still justify a BV, neither of them tax:
- **Liability.** An AI receptionist that mis-handles an emergency plumbing call, books
  the wrong job, or leaks customer data is a real liability surface. Eenmanszaak = the
  founder's private assets, and a married founder's community property. This is the
  strongest argument for a BV here and it is independent of profit.
- **Credibility with larger clients** and cleaner cap table if outside money ever enters.

Why the BV loses so badly at low profit: the €58,000 gebruikelijk loon absorbs the
entire profit at €34–80k, so nothing reaches the cheap 19% Vpb layer, while the
eenmanszaak's 12.70% MKB-winstvrijstelling and €1,200 zelfstandigenaftrek are lost
entirely. A lower gebruikelijk loon can be defended when the BV genuinely cannot pay
€58,000, but that does not rescue the comparison at these levels.

---

## 2. BTW mechanics

**Quarterly is the default.** Belastingdienst: *"Btw-aangifte doet u meestal per
kwartaal. Maar er zijn uitzonderingen mogelijk."* The plan's assumption is correct.

- **Monthly** can be *imposed* as a sanction if returns or payments are late. It can
  also be requested voluntarily (only useful if structurally in a refund position — not
  this business).
- **Annual** filing requires BTW due < €1,883/yr plus other conditions. Klantkraan will
  blow past this with two clients.

### 2026 quarterly deadlines (return AND payment must both be received by)

| Period | Deadline |
|---|---|
| Q1 2026 | **30 april 2026** |
| Q2 2026 | **31 juli 2026** |
| Q3 2026 | **31 oktober 2026** |
| Q4 2026 | **31 januari 2027** |

Payment is separate from filing — the money must have *arrived*, not been sent, by the
deadline.

### KOR 2026

Threshold **€20,000 turnover per calendar year**. Under the KOR you charge **no BTW**
and **cannot deduct input BTW** on costs and investments. Registration must reach the
Belastingdienst **at least 4 weeks before** the start of the tijdvak; you may deregister
at any time, and **must** deregister once turnover exceeds €20,000 (the 3-year lock-in
that existed before 2025 is gone).

**Would they qualify?** Only in a stub year. €299/mo × 2 clients + one €500 installation
already puts them over €20,000 within a year.

**Would they want it? NO — it is strictly value-destroying here, for two reasons:**

1. **Their clients are BVs that reclaim BTW.** The 21% costs those clients nothing —
   they deduct it in their own return. So the KOR gives Klantkraan **zero price
   advantage** with its actual buyers. The KOR only helps when selling to parties that
   cannot reclaim (consumers, exempt bodies).
2. **They would lose all input BTW deduction** on exactly the costs this business is
   made of: Anthropic API, LiveKit, Hetzner, Cloudflare, Resend, Mollie fees, laptop,
   phone. For an AI business those are the dominant cost line, and the BTW on them is
   pure recoverable money thrown away.

Add the practical damage: KOR invoices may not show BTW, so crossing €20,000 mid-year
forces a mid-relationship switch to BTW-bearing invoices — a conversation with every
client for no gain.

**Recommendation: do not opt into the KOR. Not now, not as a starter.**

---

## 3. PREPAYMENT — the €894 six-month prepay

### The rule
**Artikel 13 Wet op de omzetbelasting 1968:** tax becomes due at the moment the invoice
is issued (or should have been issued), and **lid 2: where the payment is received
before the supply takes place, the tax becomes due at the moment of receipt.**

The factuurvereisten confirm this from the other side: a mandatory invoice element is
*"de datum waarop de levering of dienst heeft plaatsgevonden of is voltooid, **of de
datum waarop een vooruitbetaling is gedaan**"*.

### ANSWER
**All 21% BTW on the full €894 is due immediately — in the quarter the invoice is issued
or the money is received, whichever comes first. It is NOT spread across the six months
of service.**

€894 × 21% = **€187.74**, payable in that single quarter. Total collected from the
client on day 1: **€1,081.74**.

### Cash-timing consequence
The founder holds €187.74 of the Tax Office's money for **up to ~4 months** (money
received 1 February is remitted 30 April). Across several founding offers this is a
meaningful float that *feels* like revenue and is not. **The plan's instruction — move
21% to a separate account the day it arrives — is correct and is load-bearing precisely
because of this rule.**

### Deferred revenue — the mismatch to plan for
For **BTW** there is no deferral: the liability crystallises on receipt.
For **income tax**, goed koopmansgebruik works the opposite way: the €894 is revenue
*earned over six months*. The unearned portion sits on the balance sheet at 31 December
as **vooruitontvangen bedragen** (a liability), not as profit.

So a €894 prepay taken in November creates:
- BTW of €187.74 due 31 January 2027 (Q4 2026), and
- only ~2/6 of €894 = €298 recognised as 2026 profit, the other €596 shifting into 2027.

**This is a genuine trap:** the founder will have banked €1,081.74 but may only book
€298 of profit, while owing €187.74 in BTW within weeks. Cash in the account
overstates both profit and spendable money. Two separate reserves are needed — the BTW
account *and* an awareness that prepaid cash is an unearned obligation.

Related obligation: taking six months of money up front creates a **six-month delivery
obligation**. If Klantkraan stops delivering (or the founder takes a job), that is a
refundable debt, not revenue.

---

## 4. The 30-day money-back guarantee

### BTW treatment
**Artikel 29 Wet OB 1968** provides a teruggaaf of BTW where the fee is refunded in
whole or in part. Mechanism:

1. Issue a **creditfactuur** (credit note) that references the original invoice number
   and shows the negative net amount and negative BTW.
2. Refund the **gross** amount to the client.
3. Process the negative BTW in the **BTW return for the period in which the refund
   happens** — a refund is not an *error*, so it is a normal negative entry in the
   current return, not a correction of a past one.

### Refund the GROSS amount — a live risk in the plan as written
A €299 Chat first month invoices at €299 + €62.79 = **€361.79**. The refund owed is
**€361.79, not €299.** If the founder refunds only the net €299 he has short-changed the
client by €62.79 *and* his BTW reclaim will not match the credit note. The plan says
"full refund of the first month" without specifying which figure — **fix that wording**.

Same issue, much larger, on the founding offer: if the 30-day guarantee is ever read as
applying to the €894 prepay, the exposure is €894 + €187.74 = **€1,081.74**.

### If a correction is needed rather than a credit note
- Errors **≤ €1,000**: correct in the next BTW return.
- Errors **> €1,000**: file a **Suppletie btw** *"zo snel mogelijk, maar in elk geval
  binnen 8 weken nadat u de fout ontdekte"*.
- Corrections are possible **up to 5 years** after the year concerned.
- Belastingrente is waived if corrected within 3 months after year-end; penalties apply
  for failing to file the suppletie or filing it late.

### Provisioning
**No statutory BTW provisioning requirement.** The practical rule is behavioural: do not
spend either the BTW or the guaranteed month's fee until the 30 days have run. The
plan's separate-BTW-account discipline covers the BTW half; it does **not** cover the
€299 net, which is equally refundable. Consider holding the first month's net fee too
until day 31.

### Drafting gaps to close
- Does the guarantee apply to the €500 installation fee? Installation work is already
  performed and is the least refundable item. State it explicitly.
- Does it apply to the six-month prepay, and if so pro-rata or in full?
- The clients are businesses, so no consumer withdrawal right applies — this guarantee
  is purely contractual, which means **whatever the terms say is what binds.**

---

## 5. INVOICE VALIDITY

### Mandatory elements of a Dutch invoice, 2026 (factuurvereisten, art. 35a Wet OB)

1. Your full name and the buyer's full name (the legal names, not trade names alone)
2. Your full address and the buyer's address (the actual establishment address, not a PO box)
3. **Your btw-identificatienummer** (with the NL prefix)
4. **Your KVK-nummer** (if registered)
5. The invoice issue date
6. A **sequential invoice number** (opeenvolgend — no gaps, no restarts)
7. Description of the goods delivered — quantity and type
8. Description of the services provided — scope and nature
9. The date the supply/service took place or was completed, **or the date of a vooruitbetaling**
10. The amount charged **excluding** BTW (split per rate if more than one applies)
11. The BTW rate applied
12. The BTW amount

Also: invoices of **≤ €100 including BTW** may use simplified requirements. The btw-id
must additionally appear **on the website** if selling online.

**Issuing deadline:** *"uiterlijk op de 15e dag van de maand die volgt op de maand
waarin u hebt geleverd"* — the 15th of the month following supply. Monthly
subscriptions billed in advance satisfy this automatically.

Retention: invoices must be kept 7 years (10 for immovable property).

### Consequence of placeholder BTW-id and address — THIS IS THE REAL BLOCKER

**Can the client still reclaim the BTW?** Not safely. An invoice missing a valid
supplier btw-id and address is not a valid invoice for BTW purposes, and the
Belastingdienst can refuse the client's input deduction on audit. EU case law leans
toward substance-over-form where the tax authority holds all substantive data, but that
is a defence the *client* has to mount, at the client's cost. In practice: an
early-stage vendor hands a plumber's accountant a defective invoice and the accountant
bounces it. **This is a sales problem before it is a tax problem.**

**Exposure to the seller — asymmetric and bad:** Belastingdienst states plainly that
*"if you have incorrectly calculated VAT on an invoice, you must still remit that VAT"*
(art. 37 Wet OB). So charging 21% on a defective invoice means **the founder owes the
€62.79 to the Tax Office regardless, while the client cannot cleanly deduct it.** All
of the liability, none of the benefit. If invoices are issued showing BTW *before* the
btw-id exists at all, the position is worse still: BTW is owed under art. 37 with no
registration to file it under, and failing the administrative/invoice obligations is a
beboetbaar verzuim in its own right.

**Can it be corrected retroactively? YES.** Either (a) issue a credit note cancelling
the defective invoice and reissue a correct one, or (b) issue a **herstelfactuur**
carrying the missing details and referencing the original. The client's deduction then
attaches to the corrected document. BTW-return corrections run 5 years back; >€1,000
needs a suppletie within 8 weeks of discovery.

**VERDICT: the plan is right to treat this as blocking. Do not send a single invoice
until the KVK registration and the real btw-id are in hand.** Retroactive repair is
possible but it means going back to your first-ever clients — the ones whose trust is
least established — to say the paperwork was wrong. Zero clients today is the cheapest
moment this problem will ever be fixable. Fix it before client #1, not after.

---

## 6. Other findings that materially change the plan

### a) Urencriterium — 1,225 hours, and it is now barely worth chasing
Two conditions: **≥1,225 hours/yr** on the business, **and** more time on the business
than on other work (the second test is waived if you were not an entrepreneur in any of
the 5 preceding years). Required for zelfstandigenaftrek and startersaftrek. **Not**
required for the MKB-winstvrijstelling.

The strategic point: at €1,200, the zelfstandigenaftrek is now worth only about
**€430** in tax at a 35.75% marginal rate. It falls to €900 in 2027. **Do not
structure working life around clearing 1,225 hours** — the 12.70% MKB-winstvrijstelling
carries almost all the benefit and has no hours test. Do keep an hour log if claiming;
it is the first thing asked for.

Startersaftrek €2,123 is worth having — claim it in year 1 (max 3× in the first 5
years). It requires the urencriterium too.

### b) Tariefsaanpassing aftrekposten — not yet biting, worth knowing
In 2026 the ondernemersaftrek and MKB-winstvrijstelling relieve at a maximum of
**37.56%**, not 49.50%. At €80k profit the belastbare winst is €68,792 — below the
€78,426 threshold — so this does **not** bite at any level in the plan. It starts
costing money above roughly €90k profit.

### c) Reverse charge and EU clients — one repo artefact already triggers this
Services to a **BTW-registered business in another EU country**: BTW is **verlegd**
(reverse charge). The invoice shows 0% BTW, must state the client's btw-id, must carry
the words **"btw verlegd"**, and the transaction must additionally be reported in an
**opgaaf intracommunautaire prestaties (ICP)** filed alongside the BTW return. Verify
the client's btw-id in **VIES** before invoicing — an unverified number leaves the
Dutch BTW on the founder's account.

**This is not hypothetical for Klantkraan:** the repo history carries a Belgian
installer prospect (comfortec). The first Belgian client makes ICP filing a new
recurring obligation, not a one-off.

Non-EU business clients: outside the scope of Dutch BTW. EU *consumers* buying digital
services would pull in the OSS regime and the €10,000 threshold — not the stated market,
but relevant if a self-serve tier ever sells to a one-man band abroad.

### d) DBA / schijnzelfstandigheid — low risk for the product, real risk for the pivot
The Belastingdienst *"controleert sinds 1 januari 2025 weer volledig op
schijnzelfstandigheid"* — the handhavingsmoratorium is over and 2026 is a full
enforcement year. Belastingdienst publishes a **Handhavingsplan arbeidsrelaties 2026**
and a **Toelichting Beoordeling arbeidsrelaties**.

**Assessment for Klantkraan: LOW risk as designed.** A productized monthly subscription
sold to many trade businesses is a *product*, not labour. There is no gezagsverhouding,
no integration into the client's organisation, no personal-service obligation.

**Where the risk actually appears** — and the repo shows this drift starting:
- The DRS deal's new ask is to **automate customer→monteur dispatch**, i.e. bespoke
  build work for one client.
- The real-estate/Solvista track is a near-separate bespoke build.
- Revenue concentration: with zero clients today, client #1 will by definition be 100%
  of revenue for a while.

The combination that creates exposure is: one dominant client + bespoke work under
their direction + working to their hours/systems. Consequences land on the **client**
(naheffing loonheffingen, premies werknemersverzekeringen, Zvw, sometimes pension) —
which is exactly why a well-advised client will refuse the engagement rather than take
the risk. **The commercial damage arrives before any tax assessment does.**

Mitigations, all of which the productized model already supports: keep several clients,
sell a product with fixed deliverables and fixed price, use own tooling and own hours,
carry own risk (the 30-day guarantee actually *helps* here — it is genuine entrepreneurial
risk), and avoid hourly bespoke work for a single dominant client. If a big bespoke
engagement is taken, use a modelovereenkomst.

Uncertain: rijksoverheid 2026 news notes *"Het kabinet schrapt een deel van (nieuwe)
zzp-wetgeving"* — the status of the Wet VBAR could not be pinned down from the sources
reachable in this session. Worth re-checking before signing any single-client deal.

### e) The €149 first month and €894 prepay are just prices — no special BTW rule
BTW is 21% of the amount actually charged. €149 → €31.29 BTW. €894 → €187.74 BTW.
Show the discount on the invoice itself so the net, the rate and the BTW reconcile.
No approval, no notification, nothing special is required for discounting.

### f) Pricing "ex BTW" is correct for this market
B2B quoting excluding BTW is standard and correct in the Netherlands. The target buyers
(loodgieters, elektriciens, hoveniers) are businesses — including eenmanszaken, which
are still businesses for BTW and still reclaim. Keep "ex btw" unambiguous on every
public price; that label is what makes the ex-BTW quote lawful if a non-business ever
lands on the page.

### g) No employer safety net — a planning gap, not a tax rule
An eenmanszaak founder accrues no pension, gets no sick pay, and has no unemployment
cover. The fiscale oudedagsreserve is no longer available for new build-up. At €40–80k
omzet with the marginal rates above, an AOV premium and a pension contribution are the
two largest discretionary deductions available and both are worth modelling *before*
setting the reserve percentage.

### h) Registration sequencing (the actual unblock path)
1. Register the eenmanszaak with the KVK → receive KVK-nummer.
2. Belastingdienst issues the **btw-identificatienummer** (and the separate
   omzetbelastingnummer used for filing).
3. Put btw-id + KVK-nummer + real establishment address into the invoice template **and
   on the website** (required for online selling).
4. Confirm the BTW tijdvak is quarterly.
5. Only then invoice client #1.

---

## Sources

- Box 1 2026 brackets + premies split — https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/prive/inkomstenbelasting/heffingskortingen_boxen_tarieven/boxen_en_tarieven/box_1/box_1
- Box 1 rates overview — https://www.belastingdienst.nl/wps/wcm/connect/nl/werk-en-inkomen/content/hoeveel-inkomstenbelasting-betalen
- Box 2 2026 (24.5% / €68,843 / 31%) — https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/prive/inkomstenbelasting/heffingskortingen_boxen_tarieven/boxen_en_tarieven/box_2/box_2
- Algemene heffingskorting 2026 tabel — https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/prive/inkomstenbelasting/heffingskortingen_boxen_tarieven/heffingskortingen/algemene_heffingskorting/tabel-algemene-heffingskorting-2026
- Arbeidskorting 2026 tabel — https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/prive/inkomstenbelasting/heffingskortingen_boxen_tarieven/heffingskortingen/arbeidskorting/tabel-arbeidskorting-2026
- Zelfstandigenaftrek 2026 €1,200 — https://ondernemersplein.overheid.nl/zelfstandigenaftrek/
- Zelfstandigenaftrek voorwaarden — https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/zakelijk/winst/inkomstenbelasting/inkomstenbelasting_voor_ondernemers/ondernemersaftrek/zelfstandigenaftrek1/zelfstandigenaftrek
- Startersaftrek €2,123 — https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/zakelijk/winst/inkomstenbelasting/inkomstenbelasting_voor_ondernemers/ondernemersaftrek/startersaftrek
- Ondernemersaftrek overzicht + 37.56% tariefsaanpassing — https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/zakelijk/winst/inkomstenbelasting/inkomstenbelasting_voor_ondernemers/ondernemersaftrek/ondernemersaftrek
- MKB-winstvrijstelling 12.70% — https://ondernemersplein.overheid.nl/mkb-winstvrijstelling/
- Urencriterium 1,225 uur — https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/zakelijk/winst/inkomstenbelasting/inkomstenbelasting_voor_ondernemers/voorwaarden_urencriterium
- Vennootschapsbelasting 2026 19% / 25.8% — https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/zakelijk/winst/vennootschapsbelasting/tarieven_vennootschapsbelasting
- Gebruikelijk loon €58,000 + eenmanszaak vs BV — https://www.kvk.nl/starten/een-eenmanszaak-of-bv-als-rechtsvorm-kiezen/
- Zvw 2026 4.85% / 6.10% / max €79,409 — https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/prive/werk_en_inkomen/zorgverzekeringswet/veranderingen-bijdrage-zvw/
- BTW tijdvak (kwartaal = default) — https://www.belastingdienst.nl/wps/wcm/connect/nl/btw/content/wijziging-aangiftetijdvak-btw
- BTW deadlines 2026 — https://www.belastingdienst.nl/wps/wcm/connect/nl/btw/content/uiterste-aangifte-en-betaaldatums
- KOR €20,000 — https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/zakelijk/btw/hoe_werkt_de_btw/kleineondernemersregeling/kleineondernemersregeling
- KOR voorwaarden — https://www.belastingdienst.nl/wps/wcm/connect/nl/btw/content/kor-voorwaarden
- KOR afmelden / 4 weken / geen 3-jaarslock — https://ondernemersplein.overheid.nl/subsidies-en-regelingen/kleineondernemersregeling/
- Wet OB 1968 art. 12/13/14 (verschuldigdheid, vooruitbetaling) — https://wetten.overheid.nl/BWBR0002629/2026-01-01/afdrukken
- Factuureisen (12 elementen) — https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/zakelijk/btw/administratie_bijhouden/facturen_maken/factuureisen
- Factureringstermijn 15e dag volgende maand — https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/zakelijk/btw/administratie_bijhouden/facturen_maken/facturen_maken
- Art. 37 "ten onrechte gefactureerde btw blijft verschuldigd" — https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/zakelijk/btw/btw_berekenen_aan_uw_klanten/waarover_btw_berekenen
- Suppletie / €1,000 / 8 weken / 5 jaar — https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/zakelijk/btw/btw_aangifte_doen_en_betalen/aangifte_corrigeren
- btw-id op facturen en website, VIES — https://ondernemersplein.overheid.nl/btw-identificatienummer-opvragen-controleren-en-vermelden/
- Handhaving schijnzelfstandigheid sinds 1-1-2025 — https://www.rijksoverheid.nl/themas/werk/zelfstandigen-zonder-personeel-zzp/aanpak-schijnzelfstandigheid
- Handhavingsplan arbeidsrelaties 2026 — https://www.belastingdienst.nl/wps/wcm/connect/nl/arbeidsrelaties/
