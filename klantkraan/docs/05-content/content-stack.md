# Content Stack — Tools + Cost

> Total content-tooling budget: **~€222/mo**. Leaves headroom inside the €500/mo all-in marketing budget for ads + outbound infra.

## Stack table

| Tool                                                             | Purpose                                                      | Cost/mo             | Notes                                                                    |
| ---------------------------------------------------------------- | ------------------------------------------------------------ | ------------------- | ------------------------------------------------------------------------ |
| **Claude API** (Sonnet + Opus)                                   | Drafting, fact-check, repurposing                            | ~€40                | Sonnet for drafts, Opus for cornerstone blogs and high-stakes copy       |
| **n8n self-hosted** (on the Hetzner CX22 we use for client work) | Pipeline orchestration: RSS → draft → review queue → publish | €0 marginal         | Shares VPS with client automations                                       |
| **Buffer Essentials**                                            | LinkedIn + YouTube scheduling                                | €15                 | Cheaper than Hootsuite; Buffer's LinkedIn integration is the most stable |
| **Canva Pro**                                                    | Carousels, thumbnails, mock-ups                              | €12                 | NL-language templates available                                          |
| **ElevenLabs Starter**                                           | Dutch voice-over for screen-recs + Shorts                    | €5                  | "Daan" + "Sanne" voices already qualified                                |
| **Descript Creator**                                             | Screen-rec edit + auto-captions                              | €24                 | Captions are non-negotiable for LinkedIn video reach                     |
| **Loom Business**                                                | Async client + content recordings                            | €15                 | Loom (vs. Vimeo Record) for one-click branded share                      |
| **Ahrefs Webmaster Tools**                                       | Owned-site SEO monitoring                                    | €0                  | Free for verified domains                                                |
| **Ubersuggest**                                                  | Long-tail keyword discovery                                  | €12                 | Light KD scoring, enough at our scale                                    |
| **Perplexity Pro**                                               | Trend + competitor research                                  | €20                 | Replaces a paid news/RSS aggregator                                      |
| **Buttondown / Mailchimp**                                       | Newsletter                                                   | €10                 | Buttondown preferred (cleaner UI, better deliverability for SMB)         |
| **Plausible**                                                    | Privacy-first analytics                                      | €9                  | EU-hosted, AVG-clean, simpler than GA4                                   |
| **(shared) Apollo basic / Instantly seat**                       | List enrichment (overlaps with outbound)                     | counted in outbound | Not double-counted here                                                  |
| **(shared) Domain + VPS**                                        | Infra                                                        | counted in tech     | Not double-counted here                                                  |
| **Total content tools**                                          |                                                              | **~€162/mo**        | + sometimes €40 Claude API top-up at high volume                         |
| **Headroom for ad-spend**                                        | Google Ads test from M3                                      | €400                | Within €500 marketing total                                              |

## What we explicitly DO NOT pay for in year 1

| Tool                       | Why not                                                       |
| -------------------------- | ------------------------------------------------------------- |
| HubSpot Marketing          | Free tier rapidly becomes paid; Attio handles CRM             |
| Notion Plus                | Free tier covers internal SOPs                                |
| HeyGen / Synthesia / Argil | Dutch avatar quality not acceptable (see channel-strategy.md) |
| Vimeo Premium              | Loom + YouTube cover the use case                             |
| Final Cut / Premiere       | Descript is enough for screen-recs + Shorts                   |
| Semrush / Ahrefs full      | Overkill until €5k+ MRR                                       |
| ClickUp / Asana            | Linear free tier covers solo + 1 VA                           |

## Stack growth thresholds

| Trigger                             | Add                                                            |
| ----------------------------------- | -------------------------------------------------------------- |
| 3 weekly LinkedIn posts feel rushed | Hire a part-time content-writer freelancer (€500/mo, 4 posts)  |
| Site organic > 2k visits/mo         | Upgrade Ahrefs to Lite (~€100/mo) for proper keyword tracking  |
| Newsletter > 500 subs               | Move from Buttondown to ConvertKit/Mailerlite for segmentation |
| YouTube > 1k subs                   | Add Tubebuddy or VidIQ Pro (~€10–25/mo)                        |
| Founder time on content > 12h/wk    | Hire VA at €600/mo to handle scheduling + repurposing          |

## Workflow diagram

```
[RSS + Perplexity + Trends]
        │
        ▼
[n8n idea queue (Notion)]
        │
        ▼
[Claude API draft]  ←─ system prompt: Klantkraan voice & tone
        │
        ▼
[Founder 5-min edit in Descript / Canva]
        │
        ▼
[Buffer scheduler] ──→ LinkedIn + YouTube + GBP
        │
        ▼
[Plausible + LinkedIn analytics]
        │
        ▼
[Weekly KPI review (10-ops/weekly-kpi-review.md)]
```

## Source

- Claude API pricing: https://www.anthropic.com/pricing
- Buffer pricing: https://buffer.com/pricing
- Descript pricing: https://www.descript.com/pricing
- ElevenLabs pricing: https://elevenlabs.io/pricing
- Plausible pricing: https://plausible.io/pricing
- Buttondown pricing: https://buttondown.com/pricing
