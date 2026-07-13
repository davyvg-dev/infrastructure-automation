# Churn Prevention

> First 90 days = highest risk. The single biggest lever is *making the value visible*. Tradesmen don't read dashboards; they need to be *shown* what they would have lost without the product.

## The four churn-killers

### 1. Daily stats SMS (auto, first 14 days, then weekly)

Owner gets an SMS every weekday evening with concrete numbers. This is the **#1 retention asset** because it's pull-based: the owner reads it; doesn't have to log in anywhere.

The old SMS template is retired; owner updates now go over WhatsApp/e-mail — see the onboarding playbook §5 (channel) and §8 (text-first churn swaps).

### 2. Monthly 4-min Loom (founder, semi-manual)

At day 30, 60, 90 the founder records a screen-recording walking through the top-3 recovered calls of the month, with concrete €-estimates of what each call was worth.

- Day-30 Loom is the **highest-leverage retention artefact in the entire business**. Send it directly via WhatsApp with one sentence: "kort filmpje, 4 min, top-3 calls deze maand."
- This is the asset that makes the owner say to their partner "deze gasten zijn die €600 dik waard."

### 3. Day-45 case-study capture call (10 min)

> "Welke call was voor jou de mooiste win?"

Two reasons:
1. **Bind emotionally** — they articulate the value themselves; cognitive dissonance forces them to keep paying.
2. **Feed marketing** — anonymised case studies for the LinkedIn carousel, the SEO blog, the next cold-email sequence.

After the call, ask: "kunnen we dit anoniem als case publiceren? Naam mag, mag ook niet — je kiest."

### 4. "Powered by Klantkraan" badge (optional)

- Client website footer + factuur-footer link.
- €25/mo discount as incentive.
- Side-effects: vendor visibility (light lock-in) + free top-of-funnel ads.

## Churn signals to watch (Friday KPI review)

| Signal | Risk level | Action |
|---|---|---|
| Owner doesn't read 3 consecutive daily-stats SMS | Medium | Founder WhatsApp check-in: "Alles oké?" |
| Dashboard not visited in 7 days | Low-Med | Include latest stats in the next stats SMS body |
| Zero calls recovered in week 1 post-go-live | High | Check call volume + forwarding + AI prompt — likely setup issue, not product issue |
| Negative review left for client (rare) | Med | Personal call to owner same day; offer to draft response |
| Owner mentions price in a check-in | High | Trigger an early Loom + accountant-style ROI summary; offer 6-mo prepay |
| New competitor (Cowcierge etc.) mentioned | Med | Send a one-pager comparing features; no panic discount |
| Owner unresponsive >14 days | High | Founder personal call; if still unresponsive, manager email re. continued service |

## Off-boarding (when churn happens)

If an owner does cancel, do NOT scramble to retain. Instead:

1. Acknowledge politely within 1 hour: "Dank voor je bericht, geen probleem."
2. Schedule a 15-min exit call.
3. Ask: "Welke 1 of 2 dingen hadden we anders moeten doen?" Listen, do not defend.
4. Honor the 30-day opzegtermijn cleanly.
5. Send a 30-day data export per the MSA.
6. Wipe data per the DPA at day 30 + 30 (retention window).
7. **Document the reason** in Attio's `churn_reason` field — feeds the weekly KPI review.

## Win-back

Quiet outreach at +90 days:

```
Onderwerp: stiekem benieuwd

{{voornaam}},

Geen verkoop-mail.

Sinds je weg bent, hebben we deze 3 dingen verbeterd:
- {{improvement_1}}
- {{improvement_2}}
- {{improvement_3}}

Wil je hem nog een keer proberen? Eerste maand gratis (echt nu),
geen verplichting. App me.

{{founder}}
```

## Saved-churn math

A saved churn is more valuable than a new sale:
- New client: CAC ~€200, ARPU €299, LTV ~€15,000 at 20% churn (herzien 2026-07-13)
- Saved churn: cost ~€0, recovers ~€3,000–5,000 of LTV (assumes 11–18 months of remaining life)

→ Spending up to €500 in founder time to save a churn is rational.

## Source

- SMB SaaS churn benchmarks (OpenView, Bessemer): https://optif.ai/learn/questions/b2b-saas-ltv-benchmark/
- Vanta SaaS churn rate benchmarks 2026: https://vantainsights.com/insights/saas-churn-rate
- Loom case-study research: implicit in the delivery research synthesis
