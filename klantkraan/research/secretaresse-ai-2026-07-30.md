# Secretaresse.ai — teardown (2026-07-30)

> Requested by the founder: what do they charge, and how does that land against **Compleet (€499)**.
> Method: their site is a JS-rendered SPA (WebFetch returns only the `<title>`), so pricing and copy
> were read out of the built bundle `/assets/index-Ci3z53ku.js` (1.86 MB) plus `sitemap.xml`.
> All quotes below are verbatim from that bundle.

## What they charge

| | Secretaresse.ai |
|---|---|
| Monthly | **€397** — one flat tier, no packages found in the bundle |
| Included | **Onbeperkte gesprekken**, 24/7, weekends and holidays. No per-call, no per-minute |
| Setup | **€497 eenmalig**, charged *after* the trial ("€497 (na proefperiode)") |
| Trial | **14 dagen gratis, geen creditcard** |
| BTW | **Never stated anywhere on the site** — not on the price, not on the setup fee |
| Year 1 total | **€5.261** (12 × €397 + €497) |

Verbatim: *"Secretaresse.ai werkt met een vast tarief van 397 euro per maand voor onbeperkte
gesprekken, 24 uur per dag, ook in het weekend en op feestdagen. Geen verrassingen achteraf."*

The BTW silence is worth noting: Dutch B2B convention makes €397 almost certainly excl. BTW, but
they never write it. Klantkraan states "Alle bedragen excl. 21% BTW" on `/prijzen`. That is the
correct side of that line — keep it.

## What €397 buys

- Voice on the client's existing number — call forwarding, no number change, "werkt met KPN,
  Vodafone, T-Mobile, elke provider", live in 5 minutes
- Webchat, plus SMS / WhatsApp / e-mail, plus Facebook and Instagram DMs
- Real-time calendar booking; confirmations by SMS or WhatsApp
- Urgency triage and warm transfer to a human; callback requests with a written summary
- No-show reminders; Google-review collection
- 10 languages: *"Nederlands, Engels, Duits, Frans, Spaans en 5 andere talen"*
- API/Zapier integrations (healthcare stack named: Medicom, Promedico, HIS Online)
- Live within 48 hours of signup
- Named persona ("Suzanne")

## Head-to-head at the €499 tier

| | Klantkraan Compleet | Secretaresse.ai |
|---|---|---|
| Monthly | €499 | €397 |
| Voice volume | 750 min included, **€0,40/min over** | unlimited, flat |
| Setup | €249 | €497 |
| **Year 1** | **€6.237** | **€5.261** |
| Trial | 30-day money-back | 14 days free, no card |
| Channels | webchat + WhatsApp (two-way) + voice | voice + webchat + SMS + WhatsApp + e-mail + FB/IG |
| Languages | NL (EN/ES on the site, not the agent) | 10 |
| Status | **voice not live** | live, selling |

**The founder's concern is correct, and the gap is wider than the sticker.** Compleet is 19% more
expensive over year 1 *and* metered. A loodgieter taking 15 calls/day at ~3 min is ~990 min/month:
240 min over the bundle, +€96, so **€595 effective vs their €397 flat** — 50% more. Their
"geen verrassingen achteraf" line is aimed exactly at that.

Two further facts that matter more than the price:

1. **They are the same buyer.** `/voor-vakspecialisten` — *"Op locatie? Toch bereikbaar."* —
   targets *"Klusbedrijven, loodgieters, elektriciens en hoveniers"* by name. Not an adjacent
   player. The same prospect list.
2. **They are a serious operator.** 61-URL programmatic-SEO site, a dedicated comparison page
   against every named rival (Voicelabs, MINDD, Aurora TeleQ, Klinik, Antwoordservice Nederland),
   two Meta Pixels and VWO A/B testing running. Funded and iterating.

## Where Klantkraan actually wins

**1. There is no €299 competitor.** Secretaresse.ai has no text-only tier. Their floor to first
payment is €397 + €497 = **€894**. Klantkraan Chat founding rate is **€149 and no setup** — a 6×
lower barrier to a first paying client. Chat is the strong position; Compleet is the weak one.

**2. EU AI Act art. 50 — binding 2 August 2026, three days from now.** Secretaresse.ai does not
mention the AI Act anywhere in the bundle. Worse, non-disclosure is a *selling point* for them:

- *"Klanten merken niks, behalve dat je altijd opneemt."*
- *"De meeste bellers merken niet dat ze met een digitale assistent praten."*
- *"veel bellers merken het verschil niet."*

Art. 50 requires disclosure to the *person talking to the system*, not to the buyer. Every one of
those lines is copy they will have to retract or defend. Klantkraan discloses in the greeting by
default, in every config, and has done since before it was required. That is a live, dated,
checkable differentiator — and it is worth more against this competitor than €50 of price.

**3. Two-way WhatsApp as the product, not as a confirmation.** Their WhatsApp is outbound: booking
confirmations and reminders. Klantkraan's is the conversation itself. Against a prospect whose
customers already app, that is a different product, not a cheaper one.

## Open decision for the founder (not actioned here)

Compleet at €499/750 min was priced on the **Synthflow** margin model. Voice has since moved to
self-hosted **LiveKit**, where per-minute COGS should be far lower. Compleet is not sellable today
(voice not live), so nothing is on fire — but the €499 number is already public on `/prijzen`.
Three options, in order of preference:

1. **Reprice to €449 flat with a fair-use cap** once LiveKit COGS is measured. Kills the metering
   objection, which is the part they attack, and lands under their year-1 total.
2. **Hold €499 but drop the meter** — same fix, keeps the anchor, thinner margin.
3. **Hold as-is and sell Chat.** Defensible while voice is dormant; do not walk into a
   feature-for-feature Compleet comparison before the price is fixed.

Do not reprice before real LiveKit per-minute cost is on paper.

## Also checked: Watermelon

Different market — a DIY chatbot builder for webshops, with no calendar booking at any tier. The
comparable trade setup is €224/mo, not the €99 headline. Full teardown:
`watermelon-2026-07-30.md`.

## Sources

- https://secretaresse.ai/ (bundle `/assets/index-Ci3z53ku.js`, retrieved 2026-07-30)
- https://secretaresse.ai/telefoonservice-zzp
- https://secretaresse.ai/wat-kost-een-antwoordservice
- https://secretaresse.ai/sitemap.xml
