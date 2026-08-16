# LinkedIn Outreach Cadence

> Four touches over 12 days. Owner-operators check LinkedIn 1–2× per week, so we spread, not bunch. Tool: HeyReach (one seat $79/mo) + Sales Navigator Core (€89.50/mo).

## Targeting filters (Sales Navigator)

- Location: Netherlands
- Industry: Construction / Plumbing / Roofing
- Company size: 1–10 (owner-operator focus)
- Seniority: Owner / Founder / Director
- Years in role: 3+ (filters new hires)
- Keywords in profile: "loodgieter" OR "installateur" OR "dakdekker" OR "dakdekkersbedrijf"

Save 3 lead lists: Loodgieters NL, Dakdekkers NL, Mixed Randstad.

## The 4 touches

### T1 — Connection request (no note)

No note. Research consistently shows note vs no-note has equal acceptance rates (~26-30%). Saves the 300 chars for T2 where they're worth more.

### T2 — Day 1 after acceptance

```
Dank voor de connectie {{voornaam}}.

Korte vraag: nemen jullie zelf de telefoon op buiten kantooruren,
of gaat dat naar voicemail?

Vraag omdat ik AI-receptionisten bouw voor loodgieters in NL.
Ben benieuwd hoe jullie het oplossen.

[Voornaam]
```

### T3 — Day 5

```
Geen druk om te antwoorden.

Stuur je een korte demo-opname (1 min, NL)? Hoor graag wat je
ervan vindt.

[Demo link of 085-XXX-nummer]

[Voornaam]
```

### T4 — Day 12 (breakup)

```
Laatste bericht, beloofd.

Mocht het ooit spelen: hier is onze demo-lijn 085-XXX XX XX.
Bel hem gerust met een lastige vraag — hij houdt stand.

Succes.

[Voornaam]
```

## Reply handling

| Reply                          | Action                                                                                                    |
| ------------------------------ | --------------------------------------------------------------------------------------------------------- |
| Positief / interesse           | Direct stem-bericht (LinkedIn voice DM is 4x reply-rate vs text) of WhatsApp-uitnodiging voor 20-min Zoom |
| Informatie-vraag               | Beantwoord direct + voeg toe: "wil je het zien? cal.com/klantkraan/15min"                                 |
| "Niet nu"                      | "Snap ik. Ik bewaar je. Mag ik je over 3 maanden polsen?" → snooze in Attio                               |
| Niet relevant (geen tradesman) | "Sorry, foute connectie aan mijn kant — geen vervolg" → suppress                                          |
| Negatief                       | "Dank voor de duidelijkheid, succes" → suppress                                                           |

## Volume

- 300 connection requests/week (HeyReach hard limit safety = LinkedIn flags >100/day)
- ~30% acceptance → ~90 new connections/week
- ~15% reply on T2 → ~14 conversations/week
- ~3% to demo-booked → ~3 demos/week

Cumulative over a month: ~12 demos directly from LinkedIn — significant secondary channel.

## Content posting cadence (different from outreach)

LinkedIn is also content (see `05-content/channel-strategy.md`). Cadence: 5 posts/week from founder personal profile (real name, no face), 1 repost from Klantkraan company page.

Outreach DMs land warmer when the prospect saw a recent post — schedule connection requests Tuesday–Thursday after Tuesday/Wednesday posts.

## Tools + cost

- **HeyReach Starter** — $79/mo, 1 LinkedIn seat, inbox warmup, A/B testing.
- **LinkedIn Sales Navigator Core** — €89.50/mo, 50 InMail credits, Boolean search.
- **Attio integration** — n8n webhook from HeyReach → Attio "Replied" stage.

## Stop using LinkedIn for outreach if

- Acceptance rate drops below 18% for 2 weeks (saturated / poor targeting).
- LinkedIn flags warning emails (slow down or stop).
- Reply rate < 8% (message is wrong, not channel).

## Source

- LinkedIn outreach benchmarks 2026 (Cleverly, Belkins, Alsona): `02-sales/funnel-benchmarks.md`
- Voice DM 4x reply effect: https://www.belkins.io/blog/linkedin-outreach-study
- HeyReach: https://www.heyreach.io/pricing
