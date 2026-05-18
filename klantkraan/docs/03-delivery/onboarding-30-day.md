# 30-Day Client Onboarding Playbook

> Target: ≤ 2h 10m founder time per client, end-to-end. Magical experience for non-technical loodgieters/dakdekkers. Everything that *can* be automated *is*.

## Day-by-day

| Day | Step | Owner | Time | Auto? |
|---|---|---|---|---|
| 0 | Contract getekend → Tally intake-link via SMS + e-mail | System | 0 | AUTO |
| 0 | Welkomstvideo Loom (90s) bijgevoegd | System | 0 | AUTO |
| 1 | Intake binnen → n8n valideert volledigheid (32 velden) | System | 0 | AUTO |
| 1 | Founder reviewt intake, vult gaten via WhatsApp | Founder | 15m | FOUNDER |
| 2 | Kickoff-call 15 min via Cal.com | Founder | 15m | FOUNDER |
| 2 | CM.com Dutch landline geprovisioneerd | System | 0 | AUTO |
| 2 | Attio workspace + pipeline aangemaakt | System | 0 | AUTO |
| 3 | Synthflow agent gekloond + variabelen ingevuld | System | 0 | AUTO |
| 3 | Founder fine-tuned prompt (regio/FAQ/tone) | Founder | 30m | FOUNDER |
| 4 | Cal.com event-types + Google-calendar koppeling | System | 0 | AUTO |
| 4 | n8n flows (missed-call, review) gedeployed met `client_id` | System | 0 | AUTO |
| 4 | Carrier-specifieke call-forwarding Loom (KPN/Odido/Vodafone) verzonden | System | 0 | AUTO |
| 5 | Founder doet 5 testbellen (spoed/nieuw_werk/spam/leverancier/bestaande_klant) | Founder | 20m | FOUNDER |
| 5 | Cloudflare-Pages dashboard live op `klantkraan.nl/r/{slug}` | System | 0 | AUTO |
| 6 | Client doet 3 eigen testbellen, geeft go/no-go via WhatsApp | Client | 0 | — |
| 7 | Eventuele prompt-aanpassingen | Founder | 10m | FOUNDER |
| 8 | **Go-live**: forwarding geactiveerd, owner krijgt go-live SMS + dashboard-link | System | 0 | AUTO |
| 8–13 | Dagelijkse stats-SMS naar owner ("vandaag: 4 calls, 1 spoed, 2 boekingen") | System | 0 | AUTO |
| 14 | Check-in call 5 min | Founder | 5m | FOUNDER |
| 15–29 | Wekelijkse maandag-mail + dashboard-snapshot PNG | System | 0 | AUTO |
| 30 | Month-1 review-call + case-study Loom opnemen (top-3 recovered calls met €-schatting) | Founder | 45m | FOUNDER |

**Total founder time: 130 minutes ≈ 2h 10m**, with 50m buffer for the inevitable carrier-forwarding edge case or prompt bug.

## Pre-day-0 (contract just signed)

Trigger: PandaDoc/SignWell webhook fires `document.signed`.

n8n actions (within 2 minutes):
1. Create Attio "Client" record with status `Onboarding-Day-0`.
2. Generate unique `client_slug` (e.g., `bakker-loodgieters`).
3. Send Tally intake form link via SMS + e-mail.
4. Send personalised 90-sec Loom (pre-recorded by founder, generic) — but DM personally with their name.
5. Schedule Cal.com kickoff (15 min, day 2).
6. Trigger Mollie SEPA mandaat sign request.

## The kickoff call (day 2, 15 min)

Three goals:
1. Confirm the intake form data (skim, fill gaps).
2. Walk through what happens next ("dag 4 stuur ik je de forwarding-instructies; dag 5 test ik; dag 8 zijn we live").
3. Set the WhatsApp Business channel as the primary support line.

Don't sell. Don't upsell. Don't engineer-talk. Just clarity and confidence.

## Carrier-specific forwarding Loom (pre-recorded library)

| Carrier | Loom URL (placeholder) | GSM codes |
|---|---|---|
| KPN Mobiel | `loom.com/share/xxx-kpn` | `**61*+31{nieuw}*11*20#` |
| KPN Zakelijk (VoIP) | `loom.com/share/xxx-kpn-voip` | Via MijnKPN Zakelijk dashboard |
| Vodafone | `loom.com/share/xxx-vfn` | `**61*+31{nieuw}*11*20#` |
| Odido (ex-T-Mobile) | `loom.com/share/xxx-odi` | `*21*+31{nieuw}` (always) |
| Youfone | `loom.com/share/xxx-yfn` | `**61*+31{nieuw}*11*20#` |
| Simyo | `loom.com/share/xxx-smy` | `**61*+31{nieuw}*11*20#` |

Disable to test: `##002#`.

We never touch the SIM. The owner dials the codes themselves on a guided 3-min video. This eliminates porting liability and lets us flip live the same day if needed.

## Why conditional forwarding (not number porting)

| Approach | Time-to-live | Risk | Verdict |
|---|---|---|---|
| Full port to CM.com | 5–15 werkdagen | High — port window risks dead line | Only on explicit client request |
| **Conditional forwarding** | Same day, 5 min | Low — original SIM untouched | **DEFAULT** |
| New tracking number | Same day | Medium — needs publishing on Google/website | New businesses only |

## Day 30 — Month-1 review call

The single highest-leverage retention moment.

**Pre-call (founder, 30 min)**:
- Pull dashboard stats from Postgres
- Identify top-3 recovered calls (highest €-value or most dramatic save)
- Record a Loom (~4 min) walking through these:
  > "Hier zie je gesprek 17. Iemand belde dinsdagavond 22:43 met een lekkage. Klantkraan heeft postcode opgevraagd, terugbel-afspraak gemaakt. Inschatting €450 omzet. Hier nog 2 vergelijkbare. Dit is wat je deze maand zou hebben gemist."

**Call (founder + client, 15 min)**:
- Share the Loom on screen.
- Ask: "Welke call was voor jou de mooiste win?" — feed marketing.
- Ask: "Iets dat anders moet?"
- Upsell trigger: if Lite → Pro (showed enough volume), if Pro → Max (custom integration request).

## Churn-prevention touchpoints (first 90 days)

1. **Daily stats SMS** (auto) — first 14 days only, then weekly. "Vandaag: 4 calls, 1 spoed, 2 boekingen."
2. **Monthly Loom of top-3 recovered calls** — single highest churn-killer.
3. **Day-45 case-study capture call** (10 min) — "welke call was de mooiste win?" feeds marketing AND binds client emotionally.
4. **Optional "Powered by Klantkraan" badge** on client website/factuur footer → social proof + light vendor-lock. €25/mo korting voor deelnemers.

## What can go wrong (and how to recover)

| Risk | Mitigation |
|---|---|
| Carrier refuses forwarding | Provision a tracking number instead; client publishes it on Google + website |
| Synthflow agent says wrong thing on first day | Daily review of first 50 calls, manual prompt tweak, redeploy in <30 min |
| Client doesn't return testbel feedback | Day-6 WhatsApp escalation + 1 call attempt; if still no response after day 8, go live anyway with conservative settings |
| Mollie mandate fails | Manual invoice via Moneybird with iDEAL link; flag client for risk-review |
| Client wants to disable AI Act disclosure | Refuse in writing; cite MSA non-waivability clause (`04-legal/ai-act-disclosure.md`) |

## Source

- Day-by-day playbook + GSM codes: see `03-delivery/intake-form.md` and the agent research base
- KPN forwarding: https://www.kpn.com/service/ugs/doorschakelen-mobiel
- Odido forwarding: https://community.odido.nl/diensten-en-services-563/conditional-call-forwarding-347788
- Number porting NL: https://lnp.402t.com/countries/netherlands.html
- Synthflow integration: https://docs.synthflow.ai/
