# Auto-publish: Instagram + Facebook + TikTok drafts

What ships after Telegram ✅ once this is wired:

| Platform  | What happens                                   | Module               |
|-----------|------------------------------------------------|----------------------|
| Instagram | Reel or image + caption posts automatically    | `src/publish_meta`   |
| Facebook  | Page post (text / photo / reel) automatically  | `src/publish_meta`   |
| TikTok    | Reel lands as a DRAFT in your TikTok app inbox — you add a trending sound + paste the caption in-app, then post (sounds can only be added in-app anyway) | `src/publish_tiktok` |

Everything below is one-time setup. Two unavoidable dashboard visits (creating the
apps); every token step after that is a curl command. `GROWTH_ENGINE_DRY_RUN=1`
short-circuits all real posting, same as X.

---

## 1. Meta (Instagram + Facebook) — one app, one token

Prerequisites (in the apps, not the terminal):
- A Facebook Page for the vertical, and you are its admin.
- The Instagram account switched to **Professional** (Business or Creator):
  IG app → profile → ☰ → *Settings* → *Account type and tools* → *Switch to professional account*.
- The IG account linked to the Page: Facebook Page → *Settings* → *Linked accounts* → *Instagram* → connect.

### 1a. Create the dev app (dashboard, ~2 min)

1. https://developers.facebook.com/apps → **Create app**.
2. Use case: **Other** → type: **Business** → name it (e.g. `klantkraan-growth`) → create.
3. Leave the app in **Development mode**. That's enough: Standard Access lets the
   app publish for accounts whose owner has a role on the app (you're the admin),
   no App Review, no Business Verification.
   Ref: https://developers.facebook.com/docs/graph-api/overview/access-levels

### 1b. Get a short-lived token (Graph API Explorer, ~1 min)

1. https://developers.facebook.com/tools/explorer → pick your app top-right.
2. *Permissions* → add: `pages_show_list`, `pages_read_engagement`,
   `pages_manage_posts`, `instagram_basic`, `instagram_content_publish`,
   `business_management`.
3. **Generate Access Token** → log in, select your Page + IG account when asked → copy the token.

### 1c. Everything else is curl

```sh
APP_ID=...        # app dashboard → Settings → Basic
APP_SECRET=...    # same page
SHORT=...         # token from 1b

# 1) short-lived → long-lived user token (60 days)
curl -s "https://graph.facebook.com/v25.0/oauth/access_token?grant_type=fb_exchange_token&client_id=$APP_ID&client_secret=$APP_SECRET&fb_exchange_token=$SHORT"
LONG=...          # access_token from the response

# 2) Page id + PAGE token (page tokens fetched from a long-lived user token do not expire)
curl -s "https://graph.facebook.com/v25.0/me/accounts?access_token=$LONG"
PAGE_ID=...       # id
PAGE_TOKEN=...    # access_token  ← this is META_ACCESS_TOKEN

# 3) the IG professional-account id linked to the Page
curl -s "https://graph.facebook.com/v25.0/$PAGE_ID?fields=instagram_business_account&access_token=$PAGE_TOKEN"
IG_ID=...         # instagram_business_account.id
```

Fill `.env` (or `.env.<vertical>` — each vertical has its own Page/IG):

```
META_ACCESS_TOKEN=<PAGE_TOKEN>
META_FB_PAGE_ID=<PAGE_ID>
META_IG_USER_ID=<IG_ID>
```

Verify (never posts): `python -m src.publish_meta --check`
→ prints `Meta OK: Page '...' (...), IG @... (...)`.

If the token ever dies (password change, security event): redo 1b + 1c. The page
token otherwise has no expiry.

### 1d. IG image hosting — wiring needed on the server

Meta **downloads** IG images from a public URL (`image_url` on the container);
there is no local-upload path for images. Reels are fine — they use the resumable
upload (local file straight to `rupload.facebook.com`).

So before IG *image* posts can go out, the ops server (168.119.173.25) must serve
`growth-engine/data/<vertical>/media/` read-only over HTTPS, e.g. a Caddy block:

```
media.klantkraan.nl {
    root * /opt/growth-engine/data
    file_server
}
```

then `META_MEDIA_BASE_URL=https://media.klantkraan.nl/fitness/media`. Until that
exists, `publish_instagram` fails image posts with an actionable error; reels and
all Facebook posting work without it (FB photos upload the local file directly).

### 1e. Meta limits worth knowing

- IG: max 100 API-published posts per 24h per IG account.
- FB Reels: max 30 API-published reels per 24h per Page; specs 9:16, ≥540×960
  (1080×1920 recommended), 3–90 s, .mp4/H.264 — our reel pipeline output matches.

---

## 2. TikTok — draft-to-inbox

Why drafts, not direct posting: unaudited TikTok apps can only *direct-post* as
SELF_ONLY (private), and trending sounds can only be added in the app anyway. The
inbox upload (`video.upload` scope) works without the audit: the video arrives as
an inbox notification, you open it, add sound + caption, post. Limit: 5 pending
inbox uploads per 24h — plenty.
Refs: https://developers.tiktok.com/doc/content-posting-api-get-started ,
https://developers.tiktok.com/doc/content-posting-api-reference-upload-video

### 2a. Create the app (dashboard, ~3 min)

1. https://developers.tiktok.com → *Manage apps* → **Connect an app**.
2. Fill the basics (name, category; website can be klantkraan.nl).
3. *Add products* → **Login Kit** and **Content Posting API**.
4. Under Login Kit → *Redirect URI*: add one, e.g. `https://klantkraan.nl/tiktok-callback`
   (it only needs to receive a `?code=` query param once; a 404 page is fine —
   the code is in the URL bar).
5. Under Content Posting API: make sure scope `video.upload` is on. Do **not**
   request `video.publish` / the audit — not needed for drafts.
6. In **Sandbox** mode add your own TikTok account as a target/test user
   (Sandbox → Target Users), or submit the app for basic review to leave sandbox.
   Either way drafts work; sandbox just limits *which* accounts may authorize.

Copy *Client key* + *Client secret* into `.env`:

```
TIKTOK_CLIENT_KEY=...
TIKTOK_CLIENT_SECRET=...
TIKTOK_REDIRECT_URI=https://klantkraan.nl/tiktok-callback   # must match 2a-4 exactly
```

### 2b. One-time OAuth (CLI)

```sh
python -m src.publish_tiktok --auth-url     # prints a URL
# open it, log in with the founder's TikTok account, approve.
# the browser lands on TIKTOK_REDIRECT_URI?code=XXXX&... — copy the code value.
python -m src.publish_tiktok --code XXXX    # exchanges + saves the token
python -m src.publish_tiktok --check        # → "TikTok OK: open_id ..., scope ..."
```

Tokens live in `data/<vertical>/tiktok_token.json` (gitignored): access token 24 h,
refresh token 365 days, both rotate automatically on every refresh — no maintenance
until the 365-day mark, when `--check` will tell you to redo 2b.

---

## 3. Endpoints in use (recorded 2026-07, for future debugging)

Meta Graph API **v25.0** (`META_GRAPH_VERSION` overrides):
- IG container: `POST graph.facebook.com/v25.0/{ig-user-id}/media`
  (`image_url`+`caption`, or `media_type=REELS&upload_type=resumable`)
- IG reel bytes: `POST rupload.facebook.com/ig-api-upload/v25.0/{container-id}`
  (headers `Authorization: OAuth`, `offset: 0`, `file_size`; binary body)
- IG status: `GET .../{container-id}?fields=status_code` → wait for `FINISHED`
- IG publish: `POST .../{ig-user-id}/media_publish?creation_id=...` → permalink via
  `GET .../{media-id}?fields=permalink`
- FB text: `POST .../{page-id}/feed` · FB photo: `POST .../{page-id}/photos`
  (multipart `source`) · FB reel: `POST .../{page-id}/video_reels`
  `upload_phase=start` → rupload `video-upload` → `upload_phase=finish&video_state=PUBLISHED`
- Token exchange: `GET .../oauth/access_token?grant_type=fb_exchange_token&...`
- Docs: https://developers.facebook.com/documentation/instagram-platform/content-publishing ,
  https://developers.facebook.com/docs/video-api/guides/reels-publishing ,
  https://developers.facebook.com/docs/facebook-login/guides/access-tokens/get-long-lived

TikTok (open.tiktokapis.com):
- OAuth: `POST /v2/oauth/token/` (form-encoded; `authorization_code` / `refresh_token`)
- Init: `POST /v2/post/publish/inbox/video/init/` (`source_info: FILE_UPLOAD`,
  `video_size`, `chunk_size`, `total_chunk_count`)
- Bytes: `PUT {upload_url}` with `Content-Range: bytes S-E/TOTAL`
  (chunks 5–64 MB, final ≤128 MB, <5 MB whole-file; 206 = more, 201 = done)
- Status: `POST /v2/post/publish/status/fetch/` → `SEND_TO_USER_INBOX` = success
- Docs: https://developers.tiktok.com/doc/content-posting-api-reference-upload-video ,
  https://developers.tiktok.com/doc/oauth-user-access-token-management

---

## 4. Wiring checklist for the main loop (NOT done in this stream)

The publish modules are complete and standalone; nothing calls them yet. To go live:

1. **bot.py** — extend the approve dispatch. Today `_PUBLISHERS` maps
   `platform -> fn(text)`; the new publishers need the draft + a media record:
   - instagram → `publish_meta.publish_instagram(draft, media)` where `media` is
     the draft's ready video record if one targets instagram, else the `square`
     image record (IG rejects caption-only posts).
   - facebook → `publish_meta.publish_facebook(draft, media_or_None)` — `square`
     image if present, video record if the draft is reel-led, else None (text post).
   - tiktok → `publish_tiktok.upload_draft(draft, video_record)`; still send the
     tiktok caption text to Telegram (it can't ride along on inbox uploads).
   All three return a permalink/confirmation string and raise on failure — wrap in
   the existing surface-to-Telegram + hand-post fallback. Skip-not-fail when a
   video is still `pending_recording`.
2. **platforms.py** — allow `delivery: draft` in `_DELIVERIES` (TikTok is neither
   `auto` nor `assisted`: media auto-uploads, posting stays manual), plus a
   `draft_platforms()` helper or fold it into the auto dispatch.
3. **config/fitness.yaml** — flip `instagram.delivery: auto`,
   `facebook.delivery: auto`, `tiktok.delivery: draft` (labels lose "(paste)").
4. **selftest.py** — add `meta` and `tiktok` modes calling
   `publish_meta.verify_auth()` / `publish_tiktok.verify_auth()` (read-only, no posts).
5. **Server** — static HTTPS hosting for `data/<vertical>/media/` (§ 1d) +
   `META_MEDIA_BASE_URL`; then the new env vars into `.env.fitness` on the ops box
   and redeploy via `ops/hetzner/deploy.sh`.
