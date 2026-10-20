# Recording menu — daily content clips

The Track A production loop: **you record a demo scenario → send the file (Telegram/AirDrop) →
Claude cuts a reel (9:16, brand cards) + a matching image card + Dutch captions per platform →
you post.** Basics of recording a clip are in [DEMO.md](DEMO.md); this is the what-to-record menu
for the two verticals.

## Run the demo

```bash
BUSINESS_CONFIG=config/klantkraan-demo.yaml python -m app.server   # trades (Klantkraan)
BUSINESS_CONFIG=config/fitness-demo.yaml    python -m app.server   # fitness (Sportcentrum De Vaart)
```

Open <http://127.0.0.1:8000> at phone width (Chrome DevTools device mode), or the live demo host
on an actual phone.

## Recording rules (so the edit stays clean)

- Phone width, one scenario per clip.
- Type naturally — real typos-and-corrections read as authentic.
- Keep the raw clip under ~60 seconds.
- Pause a beat after each send, so the jump-cut has clean beats.
- Consistent light/dark mode across clips.

## The menu — trades (Klantkraan → LinkedIn / X / Facebook)

1. **After-hours spoed booking** — lekkage → 16:00 slot → lead capture → "Gelukt, code BK-…"
2. **Price question** — "wat kost cv-ketel onderhoud?" → quotes starttarief, defers exact to on-site
3. **Service-area FAQ** — "komen jullie in [plaats]?" → checks region, books
4. **Reschedule / second job** in one conversation
5. **"What the customer sees at 21:00"** — same booking, framed as missed-call recovery

## The menu — fitness (De Vaart → Instagram / TikTok / Facebook)

1. **Proefles booking** — "kan ik een gratis proefles boeken?" → books trial + captures contact
2. **Abonnement question** — "wat kost een maandabonnement?" → info, no invented prices
3. **Class schedule** — "wanneer is de spinningles?" → hours/FAQ, books a spot
4. **After-hours lead capture** — a 22:00 message that would otherwise be lost, booked
5. **Pause/cancel handling** — polite, on-brand

Each clip becomes one reel. Reels 2–3×/week; image cards daily.

## Cadence

1 hero asset per day, cross-posted to that vertical's 2–3 platforms, plus 1 image card — feels
like multiple daily posts without multiplying the recording work.
