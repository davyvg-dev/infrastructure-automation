# Churn Prevention & Upkeep

> First 90 days = highest risk. The single biggest lever is *making the value visible*. Tradesmen
> don't read dashboards; they need to be *shown* what they would have lost without the product.
>
> §1–§4 are the post-go-live upkeep loop: what runs, who owns it, and how a change request is
> handled. §5 onward is the retention and off-boarding material. Read alongside
> `onboarding-playbook.md` — that doc ends at go-live, this one starts there. Scope of what an
> upkeep request costs is fixed in playbook §1c; do not renegotiate it per client.

---

## 1. The upkeep loop

One founder, many clients, €299/mo each. The loop has to be cheap by default and expensive only
on purpose. Everything below is either automated or capped at minutes.

| Cadence | What | Owner | Cost |
|---|---|---|---|
| Continuous | Liveness + deep-answer watchdog per host; self-heals a dead process, alerts on a dead API key | `watchdog.timer` | 0 |
| Daily | Digest per active client: conversations, leads, bookings, after-hours share, est. cost, plus NEEDS ATTENTION | `digest.timer` | 0 |
| Nightly | Claude analyst enriches the digest with quality flags and upsell signals | `analyst.timer` | ~cents |
| Nightly | AVG retention sweep (chat data aged out per the DPA window) | `retention.timer` | 0 |
| **Weekly, ~10 min** | Read the week of digests across all clients. Look for *zero-lead* weeks and *quality flags*, not for totals | Founder | 10 min |
| **Monthly, ~15 min/client** | **The tune** (§2) | Founder | 15 min |
| Monthly, auto | Value summary to the client: chats handled / after-hours leads / bookings | System | 0 |
| Day 30 / 60 / 90 | The 4-minute value Loom (§5.2) | Founder | 12 min |
| Day 45 | Case-study capture (§5.3) | Founder | 10 min |
| Quarterly | Re-read one full transcript per client end to end. Nothing else surfaces a slow drift in the config | Founder | 20 min |

**Steady-state cost per client: about 35 minutes a month.** If it exceeds that two months running,
something is wrong with the config, not with the client. Fix the config.

**The honest caveat:** the four timers are deployed on Hetzner, but Telegram delivery for the
digest and analyst is switched off pending `OWNER_TELEGRAM_CHAT_ID` and a dedicated bot token.
Monitoring you do not receive is not monitoring. Until that is wired, the weekly read is a manual
`python -m app.oversight digest --dry` and the whole NEEDS ATTENTION mechanism is dark. This is
the single highest-value hour of ops work outstanding.

---

## 2. The monthly tune

Fifteen minutes per client, calendar-blocked, same day each month. Not a call — a review of what
the receptionist actually did.

1. **Skim the flagged transcripts** the analyst raised. Ignore the good ones.
2. **Find the fumbles.** Every fumble is two things: a config fix for this client *and* a better
   default for every future client. Push the second one into `scaffold.py`'s template, not just
   into the client's YAML. This is the compounding step; skipping it means solving the same
   problem eleven times.
3. **Check the three drift points:** prices still current (they change and nobody tells us),
   opening hours over holidays, new services the client started offering.
4. **Verify the calendar share is still live.** A client who reorganises their Google account can
   silently revoke it; the booking then 403s and the first symptom is a lost customer.
5. **One proactive message** with anything found: *"Ik zag dat hij twee keer naar je zomertijden
   werd gevraagd, die heb ik bijgewerkt."* Unprompted maintenance is the cheapest retention there
   is, and it is invisible unless you say it out loud.

---

## 3. Change requests

Clients ask for changes over WhatsApp, in one line, usually badly specified. That is fine and it
should stay that way — a form here would kill the responsiveness that justifies the price.

**The rule:** anything on playbook §1c's *inbegrepen* list is done same working day and never
invoiced. Text, prices, hours, services, FAQ, spoed policy, persona. No approval step, no ticket.

**Anything else gets a number before any work starts.** Second location, second language,
integrations, voice, website work. Quote it even for a client you like, and especially for the
first one who asks: the moment one client's second location is free, it is free for everyone.

**Answer within the same working day, even when the answer is "morgen".** The response time is
the product. A same-day "ik pak het morgenochtend op" outperforms a silent two-day fix.

**Log every request**, one line in `app/pipeline.py` notes against the client. Three clients asking
for the same thing is a roadmap item, and it is the only signal source that costs nothing to
collect. This is the same tally that picks workflow-depth module 1 (`docs/01-strategy/workflow-depth-plan.md`).

---

## 4. Who owns what

Ambiguity here is where trades quietly disengage. Say it once at go-live, and again the first time
it matters.

| Thing | Klantkraan | Client |
|---|---|---|
| The receptionist answering correctly | ✅ | — |
| Uptime, hosting, model updates, security | ✅ | — |
| Prices, hours, services being *true* | Applies the change | **Tells us it changed** |
| The Google Calendar share staying live | Monitors + alerts | Owns the account |
| The website the snippet sits on | Places it once | Owns the site |
| Answering a lead the receptionist booked | — | ✅ |
| AVG towards the end customer | Processor (DPA) | **Controller** |
| Deciding the receptionist may not quote a price | ✅ (non-negotiable) | — |

The last row matters more than it looks. Clients will ask for prices and diagnoses in chat. The
answer is a permanent no, framed as protection: *"hij geeft nooit een prijs die jij niet hebt
opgegeven — dat voorkomt dat je vastzit aan een bedrag dat niet klopt."*

---

## 5. The four churn-killers

### 5.1 Monthly value summary (auto)

The owner gets concrete numbers pushed to them: chats handled, after-hours leads captured,
bookings won. **Pull-based beats any dashboard** — they read a message; they will not log in.
Weekly only once volume justifies it; monthly is the right default at low lead counts, because a
weekly "0 deze week" message actively teaches them to cancel.

**The leading indicator worth isolating: the first after-hours booking.** An appointment made at
21:40 is emotional proof they could not have captured that lead themselves. Flag it and celebrate
it back the same day.

### 5.2 Monthly 4-min Loom (founder, semi-manual)

At day 30, 60, 90 the founder records a screen walk-through of the top three conversations of the
month, with a concrete € estimate of what each was worth.

- The **day-30 Loom is the highest-leverage retention artefact in the entire business.** Send it
  over WhatsApp with one sentence: *"kort filmpje, 4 min, top-3 gesprekken deze maand."*
- This is the asset that makes an owner say to their partner: *"deze gasten zijn die €299 dik waard."*

### 5.3 Day-45 case-study capture (10 min)

> "Welk gesprek was voor jou de mooiste win?"

Two reasons: they articulate the value themselves, which binds them far harder than we can; and it
feeds marketing. Afterwards ask: *"mogen we dit anoniem als case gebruiken? Naam mag, mag ook niet
— jij kiest."*

### 5.4 "Powered by Klantkraan" badge (optional)

Client website footer + invoice footer link, €25/mo discount as incentive. Vendor visibility and
light lock-in, plus free top-of-funnel. Natural next to a chat widget.

---

## 6. Churn signals

Read these at the weekly digest pass, not on a schedule of their own.

| Signal | Risk | Action |
|---|---|---|
| **Zero conversations for 7 days on a live client** | High | Almost always a broken surface, not low demand. Check the snippet is still on the page, the widget loads, the site did not get rebuilt |
| Zero *bookings* while conversations continue | High | The receptionist is talking but not converting. Read the transcripts; usually a missing price or a too-narrow availability window |
| Calendar share revoked / booking 403s | Critical | Same-day fix; the client cannot see this failure and will blame the product |
| Client stops replying to the monthly summary (3×) | Medium | WhatsApp check-in: "Alles oké? Merk je er wat van?" |
| Client mentions price in any check-in | High | Trigger an early Loom + a plain € summary; offer 6-month prepay |
| Owner unresponsive >14 days | High | Personal call. If still silent, written notice about continued service |
| Repeated "kan hij ook…" for the same missing thing | Medium | Not a churn signal yet — a roadmap signal. Log it (§3) |
| Competitor mentioned by name | Medium | One-pager on the difference. No panic discount, ever |

---

## 7. Off-boarding

If an owner cancels, do not scramble to retain. A clean exit is worth more than a saved month.

1. Acknowledge within the hour: *"Dank voor je bericht, geen probleem."*
2. Offer a 15-minute exit call.
3. Ask: *"Welke één of twee dingen hadden we anders moeten doen?"* Listen. Do not defend.
4. Honour the notice period cleanly, per `/legal/voorwaarden`.
5. Cancel the Mollie subscription immediately. Never let a mandate outlive the relationship —
   one unexpected debit undoes every good thing above.
6. Send the data export (JSON/CSV) within the 30-day export window.
7. Delete per the DPA at day 30 + 30.
8. **Log the reason** as a note on the client in `app/pipeline.py`. Feeds the weekly review.

---

## 8. Win-back

Quiet outreach at +90 days:

```
Onderwerp: stiekem benieuwd

{{voornaam}},

Geen verkoop-mail.

Sinds je weg bent hebben we deze drie dingen verbeterd:
- {{verbetering_1}}
- {{verbetering_2}}
- {{verbetering_3}}

Wil je hem nog een keer proberen? Eerste maand gratis, echt nu,
geen verplichting. App me.
```

---

## 9. Saved-churn math

A saved churn is worth more than a new sale:

- New client: CAC ~€200, ARPU €299, LTV ~€15,000 at 20% churn (revised 2026-07-13).
- Saved churn: cost ~€0, recovers ~€3,000–5,000 of LTV (11–18 months of remaining life).

→ Spending up to €500 of founder time to save a churn is rational. Spending it on a client who has
already decided is not; that is what §7 is for.

**And the cheaper lever:** activation and churn move roughly 1:2 in 2026 SMB SaaS cohorts, so a
point of activation is worth about two points of churn. Getting the first booking to happen at all
(playbook §7) beats every retention tactic in this document.

---

## Sources

- SMB SaaS churn benchmarks (OpenView, Bessemer): https://optif.ai/learn/questions/b2b-saas-ltv-benchmark/
- Vanta SaaS churn rate benchmarks 2026: https://vantainsights.com/insights/saas-churn-rate
- Activation↔churn coupling and B2B-services activation rates (2026 cohorts):
  https://getperspective.ai/blog/2026-customer-onboarding-benchmark-activation-rates-by-industry
- Productized-service delivery and scope boundaries: https://manyrequests.com/blog/productized-service-guide
- Upkeep cadence and ownership split written 2026-07-29 against the deployed timers
  (`ops/hetzner/ai-receptionist-{watchdog,digest,analyst,retention}.timer`).
