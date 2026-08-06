# Real-estate demo: listings API + HubSpot matching — research

Date: 2026-08-06. Three tracks: (1) which "agent version of Idealista" has an API, (2) HubSpot data model for listing↔buyer matching, (3) what the existing stack already covers.

## Verdict in one paragraph

Build on **Resales Online WebAPI V6** (the agent-to-agent MLS for Costa del Sol/Blanca/Cálida, 1,300+ agencies — the only Spanish platform with a real, documented, self-serve read API over multi-agency inventory), push into HubSpot's **native Listings object** (objectTypeId `0-420`, activatable on a free portal, no Enterprise needed), and do the matching **in our own backend** — HubSpot has no native buyer↔listing matching engine, which is exactly the whitespace an AI receptionist that qualifies the buyer AND writes the match fills. The receptionist half already exists in the repo (`ai-receptionist/config/real-estate-demo-{nl,en,es}.yaml`).

## 1. Listings source

| Platform | Read API? | Access | Fit |
|---|---|---|---|
| **Resales Online** | **Yes — WebAPI V6**, self-serve docs, whole MLS network inventory | API key minted in a subscribed agency's dashboard, **IP-whitelisted** → needs the prospect's credentials or our own membership | **Best.** Price/area/type/beds filters, new-listing + price-reduction signals native |
| Idealista Search API | Yes, but invitation-gated (contact form, discretionary approval) | ~100 req/month free, 50 results/call, OAuth2 | Fallback: enough for a scripted demo with brand-name data; ToS forbid storing/reusing listings commercially; **apply now** (approval lag) |
| idealista/data | Valuations/comparables B2B, enterprise sales | Sales contact | Wrong shape now; later "automated CMA" upsell story |
| Fotocasa Pro (Adevinta) | No — publish-only partner gateway | Business advisor | Not viable |
| Kyero | No — per-agency own-stock XML feeds | Agency account | Not the target, but **Kyero-XML import** makes the demo agency-agnostic (de-facto Spanish interchange format) |
| Inmovilla / Witei | Own-database API only | Agency account | Competitor on matching (Inmovilla has built-in demand matching); our edge = conversational layer + HubSpot |

Key asymmetry everywhere: agencies *feed listings in* to portals (Idealista ILC JSON/XML etc.); almost nobody gets to *read the market out*. Resales Online is the exception because it's an MLS, not a portal.

Geographic caveat: Resales Online is Costa del Sol/Blanca/Cálida — weak on Mallorca/Balearics (there, Inmobalia is the luxury MLS/CRM equivalent). Pick the prospect region before picking the provider.

Do not scrape Idealista or build on third-party scraper APIs — they litigate (EU database right), and a demo for real agencies can't sit on that.

## 2. HubSpot side

- **Data model**: activate the native **Listings object** (Data Management → Data Model, Super Admin). No tier gate on the object itself; the pre-built real-estate template (properties + buy/sell/rent pipelines) is Pro+ but unnecessary — add our own properties. Custom objects (Enterprise, ~$150/seat/mo) are obsolete for this.
- **Cheapest viable**: free portal + **private app token** ($0) — listings, unlabeled associations, owners API, search API all work. For a slicker screen-share (association labels like "Geïnteresseerd in", workflows): a free **developer test account** simulates Enterprise (90-day renewable).
- **API surface**: ingest `POST /crm/objects/2026-03/listings` (batch upsert exists); buyer criteria as contact properties (budget_min/max, area, beds, type, timeline — free portal allows 10 custom props, enough); match via `POST /crm/v3/objects/listings/search` (filterGroups: BETWEEN price, IN city, GTE beds); write match as v4 association contact↔listing; route by setting `hubspot_owner_id` (owners API lists agents — criteria-based routing is our code choosing the id; native round-robin is Pro+ and quirky).
- **Gotchas**: search API ~4 req/s and eventually-consistent (create demo listings ahead of time, not live on the call); create association labels in the UI, not via API (known 500s); Free/Starter limits 100 req/10s, 250k/day — irrelevant at demo scale.
- **Competitive whitespace**: no marketplace app does buyer↔listing matching (only feed-sync apps + Propertybase on Salesforce). "AI receptionist qualifies the buyer and writes the match into HubSpot" has no direct HubSpot-marketplace competitor.

## 3. What the repo already has vs. net-new

Exists: real-estate receptionist configs in 3 languages (Van Leeuwen Makelaars, persona "Noor", viewing/valuation booking, art. 50 disclosure); hardened tool loop; per-tenant chat demo (`demo.klantkraan.nl/?client=<slug>`) + demo-page template (`klantkraan/apps/marketing-site/src/pages/demo/`); Telegram routing to arbitrary chat ids; ElevenLabs voice pattern with webhook tools; local lead persistence.

Net-new (all of it):
1. **`listings_store.py`** — provider seam exactly like `calendar_store.py`: fixed-signature `search()`, `provider: sim | resales | idealista`; sim = local JSON (optionally seeded from Kyero-XML) so the demo works with zero external credentials.
2. **Tools** in `app/tools.py`: `search_listings` (+ maybe `register_buyer_profile`); tools are currently global to all tenants → add an optional per-config `tools:` allowlist in `run_turn`.
3. **Structured qualification capture** — today lead capture is free-text `take_message`; buyer criteria (budget/area/beds/timeline/financing) need to be structured fields so they can be written to HubSpot and matched.
4. **`hubspot.py`** — push listings + qualified contacts + associations + owner assignment; follow the take_message contract (persist locally first, then push, honest ok/saved/notified).
5. **Per-agent routing map** in the config (`notify.agents: {name: chat_id}` + HubSpot owner id) — the Telegram primitive exists, the map doesn't.

## 4. Recommended demo architecture

Buyer chats/calls → receptionist qualifies (structured criteria) → `search_listings` against the sim store (later: Resales/Idealista provider) → presents top matches → contact + criteria + associations + owner pushed to HubSpot → Telegram ping to the assigned "agent". Voice upsell: same `search_listings` as an ElevenLabs webhook tool, like the DHZ kenteken lookup.

Phase it: **(1)** sim provider + tools + demo page (zero external deps, sellable immediately, same playbook as DHZ/Cool Global) → **(2)** HubSpot push on a free portal/dev test account → **(3)** real provider behind the seam once a prospect supplies Resales credentials or Idealista approves access.

## 5. Founder decisions / actions

- Which region is the target prospect in? Costa del Sol/Blanca → Resales Online; Mallorca → coverage is weak there (Inmobalia niche), sim-first matters more.
- Apply for Idealista Search API access now (free, discretionary, days–weeks lag): https://developers.idealista.com/access-request
- Confirm HubSpot vehicle for demos: free portal vs developer test account (recommended: dev test account for labels/workflows).
- On the first real-estate discovery call, the ask mirrors DHZ: "create a Resales API key for our server IP" (Properties → Feed Out → API Keys).
