# 28-Day Sprint — "20 receptionists live"

> Written 2026-07-14. A scrappy, compliance-clean push to put Klantkraan in front of Dutch
> trades and land live pilots FAST. This is NOT the M3 machine in `funnel-benchmarks.md`
> (4,500 cold emails/mo, HeyReach, 9 inboxes) — that targets an audience we're mostly
> forbidden from cold-emailing and takes weeks of warm-up we don't have. This is the
> next 28 days, by hand, using the one asset nobody else in this market has.

## The goal (honest)

**North star: 20 receptionists LIVE in 28 days** — free 14-day pilots + paid. A live pilot is
three things at once: a client relationship, a proof asset, and a month-2 paid conversion.

- Literal "20 _paid_ in July" won't happen on compliant channels from a cold start. Don't
  chase it and don't read a shortfall as failure.
- Realistic paid-in-July: **5-10**. The rest of the 20 are free pilots that convert in August
  off their own results ("het boekte 4 klussen in de eerste week").
- If we hit 20 live, month-2 paid revenue writes itself.

## The one mechanic

Everything routes to the same move:

```
python -m app.scaffold "Hun Bedrijf" --address "Utrecht"   # ~60s, pulls their services from their site
# → prints the command to run THEIR branded demo
```

Then: _"Hier is jóuw AI-receptionist — probeer 'm. Bevalt 't? Ik zet 'm 14 dagen gratis live,
volledig ingericht. Je betaalt pas als je 'm wilt houden."_

No competitor can hand a plumber a working version of _their own_ receptionist in a minute.
Lead with the demo, not the website. The website's job is only to not embarrass us after the demo.

## Compliant channel set (as of 2026-07-14)

OFF (founder rules + Wet ongewenste telemarketing, full effect 1 July 2026):

- ~~Cold calls to anyone without consent — including manual.~~ SUPERSEDED 2026-07-31: manual calls to confirmed BV kantoornummers are on — `cold-call-playbook.md` §0. Natural persons still never.
- Cold email to eenmanszaak/VOF.
- Commercial LinkedIn DMs to sole traders (connect + soft _question_ is fine; a pitch is not).
- WhatsApp before a permitted first contact is established.
- Any automated DMs / HeyReach-style connection blasts. Manual is the ceiling.

ON — the engine:

| Channel                           | Compliance basis             | Sprint role             | Effort            |
| --------------------------------- | ---------------------------- | ----------------------- | ----------------- |
| Paid ads → free-pilot demo        | They opt in                  | Inbound volume          | €300-500 + setup  |
| In-person / local                 | Not electronic, outside Tw   | Highest close rate      | Legs + calendar   |
| LinkedIn connect (question-led)   | Kill-list #1 carve-out       | Relationship, M2 payoff | 20-25 manual/day  |
| Email to the 32 confirmed BV only | Opt-out regime, legal entity | Small, warm, easy       | 37 contacts, once |
| Referral / warm network           | Consent-based                | Fastest first pilots    | Ask everyone      |

## Funnel math (compliant, 4 weeks)

Rough, deliberately conservative. Demos booked ≈ 30-45 across all channels:

| Source            | Demos booked (4 wk) | → Pilots live   | Notes                                            |
| ----------------- | ------------------- | --------------- | ------------------------------------------------ |
| Ads (€400)        | 10-15               | 6-10            | Free-pilot hook = cheap leads, but noisy quality |
| In-person / local | 6-12                | 4-8             | Closes highest; book demos on the spot           |
| LinkedIn (manual) | 5-10                | 3-6             | Slow burn, more of this lands in August          |
| BV email (37)     | 1-2                 | 1               | Marginal but free to run                         |
| Referral          | ?                   | 2-4             | Fastest; ask literally everyone you know         |
| **Total**         | **~30-45**          | **~16-24 live** | Free-pilot yes-rate >> paid demo close rate      |

The lever is the **offer**, not the channel: a free, done-for-you 14-day pilot converts far
above a normal paid demo. That's why 20 live is reachable where 20 paid is not.

## Week by week

**Week 0 — 1-2 days, before the blitz (build ammunition):**

- Sharpen the free-pilot offer (1-page Dutch, `02-sales/`, next step).
- Record a 60-sec demo video: the live text receptionist handling an after-hours plumbing
  request. This is asset #1 for ads + LinkedIn T3 + email.
- Launch the ad (€400, one angle: _"Mis nooit meer een klant"_ → free-pilot demo).
- Build/confirm the list: 37 BV emails + a Sales Navigator lead list + a shortlist of local
  spots (trade counters, ondernemersvereniging, bouwmarkt pro-desks) to visit.

**Weeks 1-2 — Pilot blitz (manufacture proof):**

- Daily cadence below. Goal: **land 5-8 pilots live**, each within 48h of a yes.
- Every prospect who engages gets their OWN scaffolded demo. No generic decks.
- Instrument every pilot: track calls/leads it handles so week-3 outreach has real numbers.

**Weeks 3-4 — Convert + scale (proof → paid):**

- Second outreach wave led by pilot results, not features.
- Convert week-1/2 pilots hitting day 14 to paid (Chat €299).
- Keep top-of-funnel full — the ads and LinkedIn burn continue.

## Daily cadence (full-court press)

Every working day:

- [ ] 20-25 manual LinkedIn connects to target trades (question-led, no pitch).
- [ ] Reply to every LinkedIn accept with the soft question (see `linkedin-cadence.md` T2 — but manual, not HeyReach).
- [ ] Scaffold + send branded demos to everyone who raised a hand.
- [ ] Respond to every ad lead within 15 min (speed-to-lead = 2-4x close).
- [ ] 1 block of in-person / local (2-3x per week minimum).
- [ ] Log every touch + stage in the tracker.

## Metrics — track daily, review Friday

1. Demos sent (branded scaffolds) — the leading indicator.
2. Demos actually tried by the prospect (did they message it?).
3. Pilots live (the north star) — running toward 20.
4. Pilot performance (leads/calls each handled) — the week-3 ammo.
5. Paid conversions.
6. Top objection this week (feed to `objection-handling.md`).

## Assets to build (next steps, in order)

1. Free-pilot offer — 1-page Dutch (`02-sales/pilot-offer.md`).
2. Per-prospect demo outreach messages — Dutch, one per channel (`02-sales/demo-outreach.md`).
3. Ad concept + copy + targeting — €300-500 Facebook/Instagram (`05-content/ad-free-pilot.md`).
4. Pilot-to-paid conversion message + case-study template (`02-sales/pilot-to-paid.md`).
5. In-person one-liner + leave-behind (QR to their demo).

## What this sprint deliberately ignores

- SEO / content compounding — real, but pays off in months, not this window. Keep the growth
  engine running in the background; don't expect July clients from it.
- The cold-email machine — don't build 9 inboxes for an audience we can't cold-email anyway.
- Voice / Compleet tier — not sold until voice is live. Everything here is text-first Chat €299.
