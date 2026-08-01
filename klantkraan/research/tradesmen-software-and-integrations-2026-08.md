# Tradesmen software & integrations — cross-market research + decision

Date: 2026-08-01. Method: 5 parallel research agents (Benelux, DACH, UK/IE/AU/NZ, US/CA, positioning strategy),
each with live web verification of pricing/API pages. Vendor user counts are self-claims unless noted.
Question answered: should Klantkraan list integrations on the site, and which ones are worth building?

---

## 1. Decision: list integrations — as one honest sentence, not a logo wall

**Yes, but minimal and truthful.** One compatibility sentence naming only what is live (Google Agenda,
WhatsApp/e-mail samenvatting), category language for the rest ("werkt naast elk werkbonpakket"). No
integrations page, no logos of tools we don't integrate with, no roadmap page.

Why:
- **The trades-native Dutch rivals already converged on this pattern.** InstallatieTelefoniste: one
  sentence, no logos ("Werkt met veelgebruikte software zoals Exact en Afas, of via e-mail-notificatie").
  Beller.io: one generic sentence. Voicelabs: FAQ only ("richten we op maat in"). The rivals that DO show
  logo grids show the wrong ones — Cowcierge lists Salesforce/HubSpot/Calendly, Secretaresse.ai lists a
  healthcare stack (Medicom, Promedico) on its vakspecialisten pitch. Wrong-vertical logos actively signal
  "not for you" to a loodgieter.
- **The ICP evidence says a big integrations list adds fear, not trust.** The 1–15 FTE buyer runs on paper
  agenda + phone + WhatsApp; our own discovery script probes for software-burn scars. For SMB buyers,
  time-to-value and setup simplicity convert; integration grids are a mid-market SaaS pattern.
- **Legal line:** naming a real integration is lawful referential use (Gillette C-228/03, art. 14(1)(c)
  EUTMR — plain text, no logo styling, no implied partnership). Claiming an unbuilt koppeling is a
  misleading commercial practice (art. 6:193c / 6:194 BW, ACM-enforceable). This was verified in the wild:
  Tradify (UK/NZ, 20k customers) has **no public API**, yet startups claim "Tradify integration" — claims
  that cannot be real API integrations. We don't play that game; honesty is our positioning (art. 50 wedge).

Escalation tiers:
1. **Now:** outcome language + one named tool. "Werkt met de agenda die u al heeft" + Google Agenda +
   WhatsApp/e-mail samenvatting + the paper-agenda promise ("wij zetten er een voor u op").
2. **When built and proven on ≥1 client:** add the tool name to the sentence (text, not logo). Order:
   Outlook/Microsoft 365 → first werkbon-pakket.
3. **At ~10+ clients, ≥4 real integrations + a client quote per category:** a short koppelingen section on
   /prijzen. A screenshot of a booked job in a client's real agenda beats any logo grid.
4. **Never:** "koppelt met 5.000+ apps via Zapier" — imports the software-project frame and rings false.

### Drop-in site copy (Dutch)

Homepage / prijzen, under the agenda feature:

> **Werkt met de agenda die u al heeft.** Google Agenda koppelen we in één dag — de afspraak staat er
> direct in, alleen op momenten die u zelf vrijgeeft. Andere agenda of alles nog op papier? Dan zetten wij
> een agenda voor u op die u gewoon op uw telefoon meeleest. Van elke afspraak krijgt u bovendien een
> samenvatting per WhatsApp of e-mail.

FAQ:

> **Moet ik nieuwe software leren of installeren?**
> Nee. U installeert niets en leert niets nieuws. Wij koppelen uw bestaande Google Agenda, of zetten er
> een voor u op. Elke afspraak en elk terugbelverzoek komt daarnaast per WhatsApp of e-mail bij u binnen —
> naast elk werkbonpakket dat u al gebruikt.

> **Werkt Klantkraan samen met mijn werkbon-software (OutSmart, TimeMate, Simple-Simon)?**
> De afspraak staat direct in uw agenda en de samenvatting in uw mail — dat werkt naast elk pakket, zonder
> koppeling. Gebruikt u een werkbon-app en wilt u de klus daar automatisch in hebben? Zeg het in het
> kennismakingsgesprek; dan kijken we of dat voor u in te richten is.

Sales-call line: "Welk pakket gebruik je? … Mooi — dan zorg ik dat alles wat de receptionist aanneemt daar
terechtkomt, te beginnen met je agenda en je mail."

---

## 2. Integration build priorities (NL/BE, verified API surfaces)

| # | Integration | Why | API reality (verified 2026-08-01) |
|---|---|---|---|
| 1 | **Microsoft 365 / Outlook Agenda** | The only other calendar with real NL SMB penetration (bouw tilts Microsoft when it formalizes; OneDrive 38% vs Google Drive 25% of Dutch business cloud). Closes ~all of the digital-agenda market. | Microsoft Graph; same `calendar_store.py` seam swap — bodies change, signatures stay. |
| 2 | **OutSmart** | Werkbon marktleider NL+BE: 5,172 companies, 20k daily technicians, explicitly targets installateurs on "papier + Excel + WhatsApp". First integration that lets sales say "de klus staat meteen op de werkbon" — no Dutch AI-receptionist rival offers this. | Open REST API (work orders, customers, hours; keys on request, Postman docs). No webhooks. out-smart.com/features/integrations/outsmart-api |
| 3 | **Solvari lead webhook** | The ONLY NL/BE lead platform with an official customer-facing API/webhook (every Pro tier). Lets the receptionist respond to a Solvari lead in under a minute — speed-to-lead is the whole game there (3–30 rivals per lead). Also: Trustoo/Trustlocal deliver leads by WhatsApp, which we already speak natively — zero-integration interception. | pro.solvari.nl/api/customer-docs |
| 4 | **TimeMate** | #1 werkbon app on Appwiki, 1,000+ companies, cheapest in market (€4.95–9.95/user/mo) — the tool the smallest ICP firms actually buy. | Public API (developer.timemate.nl) + official Zapier connector — unique in the micro-FSM segment. |
| 5 | **Moneybird** (later) | ~380–400k users; best developer experience in the whole landscape (REST, OAuth2, webhooks, estimates API incl. accept/send). Relevant when we touch offertes/facturen, not for booking. | developer.moneybird.com |
| 0 | **Productize the e-mail/WhatsApp samenvatting as the universal koppeling** | Already exists (Resend + WhatsApp notify). Every werkbon tool ingests structured e-mail. This is the truthful "works with everything" answer today — InstallatieTelefoniste sells exactly this. | Zero build. |

Rule of thumb from the discovery script: add "welke werkbon-app gebruik je?" to every call and build
whatever the first three paying clients actually run — that also produces the client quote tier 3 needs.

**Closed boxes — never promise:** Cafca (BE incumbent, no API), Syntess (partner-gated), Admicom/Kraan
(both now ECI, closed), Van Meijel, Simple-Simon (curated koppelingen only), Werkspot (no pro API, no
Zapier), Tellow, SnelStart (certification-gated). Dead names to purge from any sales material: WerkbonApp
(= OutSmart), Bouw7 (= Exact Online Bouw), Casius (= Solvari), HomiGo (dead).

---

## 3. What the mature markets teach (US, UK/AU/NZ, DACH)

**Integration depth is price-tiered, everywhere:**
- Below ~$300/mo, calendar-only players win the micro segment: Rosie ($49–299), Goodcall ($79–249),
  Voctiv ($29) thrive on "Zapier + Google Calendar" because 1–5 person shops often have no FSM at all.
- Above ~$400/mo, deep FSM integration is table-stakes: Avoca ($1k–3.5k/mo, entire brand = deepest
  ServiceTitan integration, per-integration landing pages + certified-app badge), Sameday ($449+/mo,
  site organized around FSM logos, "books directly into ServiceTitan").
- Klantkraan at €149/€299 sits in the defensible vertical-micro band — calendar + WhatsApp is genuinely
  enough at this price point *today*.

**The platform-bundling pincer is real and already moving:**
- US/AU: Jobber AI Receptionist $99/mo add-on; Housecall Pro CSR AI; Workiz "Jessica" ~$200/mo;
  ServiceM8 Phone Agent from **+$13/mo** (Connect Plus $32/mo incl. AI, 500 min).
- DACH: plancraft bundles its PORTA phone AI **free (60 min/mo) into every plan** — and plancraft is
  **already live in the Netherlands** (€38M Series B, Aug 2025, 30k+ users). HERO Voice bundled 60–150
  min/mo; ToolTime Assistant 24/7; pds "Hey Telo"; Labelwin "IDA".
- Specialist counter-move: HalloPetra (DE, founded Sep 2024, €99–499/mo, 2,500+ businesses) built its
  moat as **22 Handwerkersoftware/ERP connectors** incl. an official OneQrew partnership.
- Implication: NL has no native-AI FSM yet — Klantkraan is in the window US standalones had in 2023–24.
  The moat to build before Dutch planning tools bundle AI answering: werkbon write-back (OutSmart/TimeMate)
  + WhatsApp-first, which **no player in any researched market ships as the primary channel** (US is
  voice-first because WhatsApp isn't the US channel; DACH WhatsApp is universally "coming soon").

**The winning marketing kit (recurs across every winner in every market):**
1. Missed-call math as hero copy. Clean citable chain: Matelso 2024 (DE, n=100): 23% of calls unanswered,
   ~80% leave no message, ~85% never call back. Fix Radio survey (UK, n=220): 34% lost work from missed
   calls. Bitkom 2025 (DE, n=504): **85% of trades firms say customers expect constant reachability**;
   62% already use messengers with customers. HalloPetra's hero: "3 van 4 bellen geen tweede keer."
2. "Boekt direct in je agenda" — the verb is always *book*, the differentiator always *direct*. Never
   "takes a message."
3. A published booking-rate number (ServiceTitan 70–85%, Sameday 92%). We should measure and publish ours.
4. Cost-vs-human framing (receptionist salary vs €149–299/mo).
5. Live demo over testimonials: AU leaders (Never Miss a Call, AiDial) are testimonial-free and instead say
   "ring our AI right now." Our /demo + WhatsApp demo number is exactly this — feature it harder.
6. Per-tool SEO pages: Goodcall runs programmatic "AI for [FSM tool]" pages capturing demand *before*
   integrations exist. Honest NL variant: "AI-receptionist naast OutSmart/TimeMate/Simple-Simon" pages
   describing coexistence (samenvatting per mail naast je pakket) — truthful, and captures the searches.
7. Emergency/after-hours wedge: "73% of emergency trade calls come in after hours" (AU); spoedmelding
   triage is a sellable feature, not a nice-to-have.

**WhatsApp is the open flank in every non-US market:**
- NL: 13.8M users, 12.1M daily (Newcom 2026). Flanders: 88% monthly, 66% daily (digimeter 2025).
- DE: 55% of German WhatsApp users have already booked appointments with businesses via WhatsApp
  (Capterra n=1,029); 62% of Handwerksbetriebe use messengers (Bitkom 2025).
- No FSM tool in any market has a live customer-facing WhatsApp channel; no AI receptionist in DACH/UK/AU
  ships text-first. This is Klantkraan's structural differentiator — keep leading with it.

**Belgium timing note:** the Peppol B2B e-invoicing mandate (1 Jan 2026, fines €1,500–5,000) just forced
even one-man Flemish loodgieters onto invoicing software — but not onto planning software. The realistic
Flemish stack is now Billit/Accountable + paper/WhatsApp planning: exactly the calendar/intake gap we fill.
Trustlocal (Belgian Trustoo, 50 branches live) delivers leads by WhatsApp. Flanders is a near-zero-
adaptation expansion market when ready.

**Adoption reality check (NL):** facturatie is 92% digitized in bouw, offertes 75%, boekhouding 72% —
but werkbon/planning/intake is the laggard layer (Exact MKB Barometer 2024); ~34% of the smallest Dutch
firms buy no cloud services at all. The "paper agenda + WhatsApp" segment is real and large; the
"geen digitale agenda? wij zetten er een voor u op" line converts the largest single segment and no
competitor says it.

---

## 4. Threats & watch list

- **plancraft NL** — free bundled AI phone agent, funded, already localized. The most concrete future
  collision. Watch their NL go-to-market.
- **Klushulp.io** — AI offerte-from-conversation for exactly our ICP (500+ vakmensen). Adjacent, not
  competing yet; a natural partner or acquirer of attention.
- **Plumbly.nl** — ZZP-loodgieter vertical newcomer, same wedge logic.
- **HalloPetra playbook** — if it works in DE (integration-moat receptionist), expect a clone aimed at NL.
  Our counter is being first with OutSmart/TimeMate write-back + WhatsApp-first.

## 5. Source reports

Full regional reports (with per-claim URLs) live in the agent outputs behind this synthesis; the
load-bearing sources are cited inline above. Related existing research: competitor-landscape-2026-07.md,
secretaresse-ai-2026-07-30.md, onboarding-technical-integration.md (Google Calendar service-account path),
lead-source-platforms.md.
