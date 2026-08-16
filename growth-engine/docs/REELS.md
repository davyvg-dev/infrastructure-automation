# Reels playbook — chat-demo short-form for IG / TikTok / FB

## 0. Two ways a reel gets made

1. **Scripted (default, `media.reel.demo`)** — the pipeline draws the demo itself
   from a Dutch scenario in config: brand-styled web-widget chat (fictional
   business, "digitale assistent" disclosure in the header, klantkraan.nl brand
   mark), typing/pop/ding sound placed on the same frame grid the video is built
   on — sync exact by construction. Every video draft arrives in Telegram with a
   ready reel; scenarios rotate per draft. Edit the conversations in
   `config/*.yaml`, never in code.
2. **Recorded (🎬 button)** — the founder screen-records the real product, the
   pipeline detects messages/keystrokes (adaptive thresholds, keyboard band) and
   pop-cuts it. Sending a recording replaces the scripted reel for that draft.
   Use this when a post needs real-product proof (§3).

## 1. Verwerk in de pipeline
Ranked by impact/effort (highest first).

1. **Kill the static title card; overlay the hook on moving footage.** Composite the Dutch hook headline (drawtext/Pillow overlay, first ~2.5s) on top of the *first chat frames with a message already popping in* — motion from frame 1. Static cards read as ad intros; hooks under 2s show ~30% higher view duration and >60% 3s-hold correlates with 5–10x reach.
2. **Move the footer URL out of the dead zone.** Bottom ~35% of the frame (FB: ~670px, TikTok: ~440–480px, IG: ~320px) is covered by caption/UI. Place all persistent overlays (hook, URL, CTA) inside a centered ~900x1290px box: clear ≥250px top, ≥670px bottom (worst case = FB), ~120px right (icon rail). Keep the URL persistent throughout instead of end-card-only — most viewers never reach the last frame.
3. **Cold-open with the payoff, then replay.** Show the end state (~1s: booking confirmed + 22:47 timestamp, punch-in) before the conversation plays out. Converts the rest into an open loop ("how did that happen?"); buried ledes lose ~70% of viewers.
4. **Add one punch-in zoom on the key moment.** ffmpeg zoompan/crop keyframe on the confirmation bubble + timestamp. Record source above 1080p so the zoom stays sharp. Guides the eye with no voiceover; "produced zoom" aesthetic is what made demo reels travel.
5. **Re-insert exactly ONE typing-indicator beat (~0.5–1s of "...") before the payoff message.** Tradeoff vs. "cut all waits": total speed maximizes pace but discards the format's only suspense device — use it once, on the climax only.
6. **Shrink the end card to ~1s and design for loop.** Overlay the CTA on the final chat frames rather than a separate static card; cut hard from last frame back into the hook frame so replays feel seamless. A 2s static card is 13% of runtime after the payoff and drags completion — the top ranking signal. Replays count as watch time; sub-15s loops can push completion >100%.
7. **Target 10–12s finished, 15s hard cap.** If the chat doesn't fit, cut messages (question → availability → booked), never extend. Sub-15s + >65% retention is the strong-performer band for cold accounts.
8. **Enforce a visual change every 2–4s.** Message pops, the typing beat, the punch-in — never let the chat sit static >3s. B2B viewers need reading time, so 2–4 interrupts across 12s, not constant motion.
9. **Text rules for 35–55 eyes:** overlays ≥42px on the 1080 canvas, lines <30 chars, contrast ≥4.5:1, semi-transparent box behind text over footage, each element on screen ≥1–2s. Don't speed typing past Dutch-readability. QA step: watch the render on a phone, muted.
10. **Bake Dutch keywords into overlay text.** Both platforms OCR-index on-screen text for search: "sportschool", "proefles", "AI-assistent" belong in the hook/overlays, not just clever copy.
11. **Phone silhouette, minimal branding.** Rounded corners + thin bezel/shadow (the "peeking at someone's phone" genre cue), phone filling the frame up to the safe zones — no small phone floating in dead space. Tradeoff branded-stage vs. raw: minimal-logo content beats ad-format by +81% ROI, so accent bar stays subtle and logo lockups live on the end card only.
12. **Export CFR:** add `fps=30` / `-vsync cfr`, 1080x1920 H.264. Phone screen recordings are VFR and stutter after IG re-encode. One clean master, uploaded natively per platform.
13. **Auto-generate a cover frame (Pillow):** consistent branded template, one bold Dutch title per video, all key visuals in the center 1080x1080 square (grids crop to 1:1/3:4; TikTok overlays caption on bottom ~270px). The grid is the storefront a visiting gym owner judges.
14. **Baked-in sound design (`media.reel.audio`):** synthesized UI SFX from `assets/sfx/` — a pop as each message lands, soft ticks under typing, a ding on the payoff — plus an optional founder-supplied licensed/CC0 ambient bed at ~-24 dB. Silent files read as broken; this layer is copyright-safe because every sample is generated in-repo (`python -m src.sfx --make-sfx`). Commercial/trending music is still never baked in — that stays in-app (§2).

## 2. Bij het posten (founder, in-app)
- **Music — TikTok:** pick a *rising* sound (trending arrows in-app, <24h old = up to 3x views); low-energy/ambient only — never a meme sound on a demo. Audio communities are the biggest organic reach lever under 10k followers.
- **Music — Instagram:** business accounts only get the limited Sound Collection. Switch account type to **Creator** for the full trending library (keeps insights). Never bake music into the file server-side — copyright strike risk; in-app selection keeps Meta's license. (The pipeline's own baked-in layer — synthesized SFX + optional licensed bed, §1.14 — is fine; in-app music stacks on top of it.)
- **Music — Facebook:** optional. FB discovery runs on retention/shares, not audio; skipping music there costs nothing.
- **Captions:** primary Dutch search phrase in the first 125 chars ("AI-receptionist voor sportscholen — proefles geboekt om 22:47"), then context; **3–5 hashtags** max, 1 broad + 2–4 niche (#sportschool #fitnessondernemer #ondernemen) — no #fyp, no 30-tag spam (hurts search ranking).
- **Covers:** set the pipeline-generated cover on both IG and TikTok every post. Consistent grid = trust signal for a zero-follower account.
- **Cadence:** 3–4 posts/week, fixed schedule, one niche, ≥90 days before judging data. On FB, post fresh — same-day uploads get ~50% more distribution (Oct 2025 update). No burst-then-silence.
- **Account warm-up (TikTok):** 7–14 days before first post — follow Dutch fitness/business accounts, watch niche videos to completion, like/comment as a human. Cold-start seeds your first posts' audience from your own watch behavior.
- **Never re-upload a watermarked file.** Native upload of the clean master per platform; IG→FB via Meta's official crosspost toggle is fine (~23% more impressions). Watermark detection costs 40–70% reach.
- **Measure:** 3s hold >60% and completion >65% in-app; A/B hooks by re-rendering the same chat with 3 different headlines posted days apart (near-free with the pipeline — vary the opening frame, perceptual hashing weights the first 0.5s). At 1,000 IG followers, unlock Trial Reels for hook testing on non-followers.
- **Prioritize Facebook.** The 35–55 Dutch business owner lives there, 40%+ of the FB feed is recommended content from unfollowed accounts, and reels are tested on non-followers first — expect the best conversion there even at lower raw views.

## 3. Wat je opneemt (content)
- **One reel = one scenario = one question for one person.** Build an episodic series with a recognizable name/numbering in the cover title. Scenarios to rotate: late-night trial booking, cancellation handled, price question, weekend booking, question answered mid-class, missed-call recovery.
- **Frame every recording as proof, not promotion:** a visible timestamp in an unedited-looking chat is self-verifying evidence — real-results content outperforms polished promo 3–4x in fitness marketing. Outcome phrasing ("proefles geboekt om 22:47, zonder personeel"), never feature phrasing ("onze AI kan X").
- **Hooks:** stack identity-call (names the gym owner) + curiosity/loss framing + a concrete detail (exact time). Identity callouts also train the algorithm on who to show it to — critical at zero followers.
- **≥5s of real, readable in-app conversation per reel** (2–3x higher conversion than clips without live product footage). Sped-up typing fine; unreadable Dutch not.
- **The reel must work 100% muted** — hook, chat, timestamp, CTA all on-screen text. Music is distribution garnish, never the message.
- **End CTA: engineer sends, not clicks.** DM-shares between gym owners are the strongest non-follower signal; URL on screen + bio link is the real conversion path (captions aren't tappable).

Five hook lines (title/overlay):
1. "Sportschooleigenaar? Dit gebeurt om 22:47."
2. "Klant appt om 22:47. Kijk wat er gebeurt."
3. "Proefles geboekt om 22:47 — zonder personeel."
4. "Gemiste telefoontjes = gemiste leden."
5. "Je hebt geen receptionist nodig. Echt niet."

## 4. Platformverschillen in het kort

| | Instagram | TikTok | Facebook |
|---|---|---|---|
| Role | Testing ground (Trial Reels at 1k) | Reach/search engine | **Priority: where the buyer is (35–55)** |
| Music | Creator account for full library | Rising sound <24h, ambient | Optional, skip freely |
| Bottom dead zone | ~320px | ~440–480px + right rail 120px | ~670px (design to this worst case) |
| Discovery lever | Sends-per-reach, watch time | Completion + audio communities + search OCR | Completion + shares; same-day recency bonus |
| CTA style | "Stuur dit naar een sportschooleigenaar" | Search-keyword overlays | Direct, explicit instructions (older users) |
| Cover crop | 3:4 grid (top/bottom ~480px cut) | 1:1 grid + caption on bottom 270px | n.v.t. |

## 5. Niet doen
- No static logo/brand intro frame — ever. Lead with conflict, not context.
- No padding to fill 15s; cut messages instead.
- No fade-out or "finished"-feeling ending — it kills the replay loop.
- No re-uploading files downloaded from another platform (watermark = 40–70% reach penalty).
- No sideloaded commercial music in the ffmpeg output (copyright strike; in-app only). Synthesized SFX and a founder-licensed/CC0 bed (`media.reel.audio`) are the only audio allowed in the file.
- No high-energy meme sounds on a product demo — mismatched trending audio backfires.
- No hashtag spam (>5 tags) and no generic reach tags (#fyp) — niche tags define your topical cluster.
- No heavy branded stage during the demo: no logo lockups, no thick accent bars — save branding for the ~1s end card.
- No text/URL in the bottom 35% or right 120px of the frame.
- No scattering topics or burst-posting: 3–4/week, one niche, 90 days minimum before judging.
- No feature-speak hooks ("onze AI-assistent kan...") — outcome and problem framing only.
