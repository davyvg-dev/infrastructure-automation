# Growth Strategy

The thinking the engine runs on, updated with a research round on how solo builders actually
**sell** AI services and **grow an audience**. Klantkraan's own market research (9 reports)
lives in `klantkraan/research/`. Edit `config/content_strategy.yaml` to change behavior;
this doc explains the *why*.

---

## 1. Positioning

**You:** the founder of **Klantkraan** (klantkraan.nl), shipping **AI receptionists** for
Dutch trades — a done-for-you assistant that answers a business's customers instantly, 24/7,
by phone, website, and WhatsApp, and books them straight into the calendar.

**Angle:** you don't *talk about* AI, you *ship it in public* and show it working. The demo is
proof; the content is the top of the funnel.

**Golden rule from the research:** your buyer is a **business owner, not the tech crowd**.
Build-in-public only sells when the audience you attract is the audience that buys. So lead
with their money and pain, and **never lead with "AI"** — say "24/7 call answering that stops
you losing jobs".

## 2. The niche (decided)

"One niche, one offer, one outcome." Niche fluency closes ~3× faster. Klantkraan's niche is
**Dutch trades** (installateurs, loodgieters, elektriciens, schilders): they grasp
"missed call = lost job" instantly, per-job value is high, and they already buy monthly
subscriptions. It is set in `config/content_strategy.yaml` → `brand.audience`. Expand only
once it works.

## 3. The offer & pricing

**Productize one fixed-scope package** (don't build a snowflake each time):
intake → availability check → calendar write → phone/web/WhatsApp → confirmation + reminder.
Klantkraan's voice agent (`klantkraan/apps/voice-agent`, LiveKit) plus the marketing site is
exactly this, rebrandable per client.

**Pricing is decided:** three tiers at **€349 / €599 / €849 per month** (set 2026-05-21 from
the research-aligned whitespace band; details in `klantkraan/docs/`).

**Where this sits:** above DIY tools (€25–65/mo, e.g. Upfirst/Aira) and below the managed tier
(Smith.ai €270–800/mo). You **never compete on price** — you win on *done-for-you + local +
managed*. Tie the retainer narratively to a KPI ("first response under a minute, every enquiry
captured") but **bill flat** (outcome-billing needs dashboards you shouldn't build solo yet).
Bake the Claude/WhatsApp per-message COGS into the retainer floor so margin survives busy
clients.

**Frame the outcome, not the tech** (Hormozi: Value = Dream Outcome × Likelihood ÷ Time ×
Effort). Example: *"Never lose another after-hours booking. It answers on your site, WhatsApp
and Telegram, books the slot into your calendar, and confirms it — so the 30–40% of enquiries
you miss turn into appointments."*

## 4. Content system

**One pipeline, two native variants — never the same string on both:**
- **LinkedIn = home platform** (B2B buyers live here; ~80% of B2B social leads). Native
  long-form: 150–400 words, hook in the first 1–3 lines, generous line breaks, one idea,
  question close. **No links in the post body** — put them in comment #1 or your Featured
  section. Carousels/native video perform best.
- **X = distribution + personality.** Punchier, hot takes, threads; links fine in-body.

**The 5 pillars** (weighted toward the buyer — see the config). Proof + Problem convert; a
dev-facing rotation grows the wrong audience:
- **Proof/demo (most)** — the receptionist working: a booking, a call answered, "it booked
  while I slept". Pair with a clip/screenshot.
- **Problem (high)** — the buyer's pain in money terms: "a plumber who misses 12 calls a week
  leaks ~€X/mo". Educate the problem → soft takeaway. Highest-converting.
- **Teardown** — a bad customer experience (a call that rang out) and how it should work.
- **Hot take** — industry-facing ("phone trees are dead"), not AI/tech debates.
- **Build log (least)** — an honest build note, tied back to the customer benefit. Sourced
  automatically from your git commits via `/buildlog`.

**Cadence (research-reconciled):**
- **Replies are the daily engine — and stay HUMAN.** LinkedIn: 5–10 substantive comments/day
  on 10–20 accounts whose followers are your buyers (commenting shows your name to 100% of a
  post's viewers — the real lever from a small following). X: 20–40 targeted replies/day on
  accounts 2–10× your size.
- **Original posts are batched, not heroic:** ~4–5 quality posts/week is the sustainable solo
  floor. LinkedIn 3×/week held for a full 90 days; one thread/week on X.
- Reply to every comment on your own posts within the first hour.

> The engine drafts **original posts** and pushes them for one-tap approval. It deliberately
> does **not** automate replies, comments, or DMs — every practitioner source says automating
> those kills reach and trust.

## 5. Profile = landing page (do this before posting)

- **Real headshot**, not a logo.
- **Headline = outcome:** "Ik help installateurs en loodgieters nooit meer een klus missen —
  AI-receptionist die 24/7 opneemt en inplant (klantkraan.nl)."
- **About:** positioning + who you help + one proof metric + a soft CTA ("DM me 'CALLS' for a
  2-min demo").
- **Featured / pinned:** a short demo clip + one case study — this is where your links live
  (dodging LinkedIn's body-link penalty).

## 6. The DM → client playbook (manual — this is where you close)

Content and demos are the easy part; the sales grind is what determines revenue. The loop:

1. **Door-opener — the free "after-hours" audit.** Call your target list after hours, log who
   missed the call. That log is your opener and your proof.
2. **Permission-based Loom.** Ask first ("mind if I send a 90-second video?"). Only for
   repliers, record a 2-min Loom that opens on *their* website, then shows *their* branded
   demo booking a slot. Personalized video lifts replies 2–3×.
3. **Rebrand the demo before the call.** Configure the Klantkraan voice agent with their
   details (pulled from their site/Google profile), deploy a demo URL + live test number.
   The "aha" is hearing it answer as *their* business.
4. **Discovery.** Pre-qualify by email (situation / what they've tried / questions). On the
   call run SPIN — *implication* questions make the missed-call cost concrete ("what's a missed
   new-customer call worth to you?") — and BANT to confirm they can say yes.
5. **Close on a 30-day pilot with exit criteria** ("if it captures X booked jobs, we continue
   at €Y/mo"). Charge a **small paid pilot (~€200, credited toward setup)** — it filters
   tire-kickers better than free.
6. **"Let me think about it"** → surface the real objection, then default to starting the pilot
   with a fixed check-back date. A running pilot is the best objection-handler.
7. **Referral after every win** — ask when they're happiest, be specific: "know 2 other
   plumbers who'd want to stop losing after-hours calls?"

**Outreach mechanics:** specificity is everything ("I called Tuesday at 7pm and got
voicemail…"); widening-gap follow-ups (≈+3, +5, +7 days), a new angle each; a one-line "bump"
beats a long follow-up. Don't expect double-digit reply rates without real personalization.

## 7. 90-day plan (audience + first clients, in parallel)

- **Week 0 — setup.** Real headshot; outcome bio; pin a "Day 1: here's what I'm building and
  why" post; build 3 lists (big voice-AI/SaaS accounts, target-niche owners, peers). Optimize
  the LinkedIn profile as a landing page. Build one polished reference demo.
- **Weeks 1–4 — reps + relationships.** Daily human replies from your lists; 4–5 posts/week
  across the pillars (engine-drafted, you approve); reply to every reply within an hour. Start
  the free after-hours-audit list for your niche. Goal: the habit + first ~200–500 followers,
  not virality.
- **Weeks 5–8 — find what lands.** Double down on the pillar that pulls profile clicks/DMs.
  Start a weekly thread. Send permission-Loom outreach to audited prospects; rebrand the demo
  for anyone who replies.
- **Weeks 9–12 — convert.** Treat inbound DMs as your warmest pipeline; book demo calls
  personally. Run 30-day pilots with exit criteria. Land the first 1–2 paying clients, capture
  a one-line case study, ask for a same-niche referral, repeat.

## 8. Honest caveats

- The punchy numbers in the research (conversion %, reach multipliers, retainer bands) are
  mostly single-source or self-reported — directional, not guarantees. The band above is the
  realistic solo-EU zone, not the aspirational US-agency $2–5k/mo figures.
- Self-serve competitors at €25–65/mo exist; you must sell done-for-you, never price.
- The pipeline gets attention; **you** close. Budget time for follow-up and trust-building,
  not just posting.

Full sources and the deeper findings are in `klantkraan/research/`.
