---
description: Build, check, and deploy the marketing site to Cloudflare Pages production
allowed-tools: Bash(npm run:*), Bash(pnpm dlx wrangler@4 pages deploy:*), Bash(curl:*)
---

Deploy `klantkraan/apps/marketing-site` to production. Ralph rule: one step at a time, verify, STOP on any failure — fix the root cause, never bypass.

1. `cd klantkraan/apps/marketing-site && npm run typecheck` (= `astro check`). Errors → stop.
2. `npm run build`. Failure → stop.
3. Deploy:

   ```
   pnpm dlx wrangler@4 pages deploy ./dist --branch=production --project-name=klantkraan-marketing
   ```

   - `--branch=production` is REQUIRED — without it you get a preview deploy and klantkraan.nl does not change.
   - Cloudflare Pages has NO git integration here. Pushing commits deploys nothing; this wrangler call is the only deploy path.
4. Verify via the deployment alias URL wrangler prints (curl the changed pages: 200 + expected content), then spot-check https://klantkraan.nl.
5. If this deploy adds any NEW asset path: fetch it with a `?v=<n>` cache-buster when verifying. A fresh asset path can edge-cache the SPA HTML fallback — if an asset URL returns HTML, that's the poison; bust with `?v=` and re-verify.
6. If this change also touches the API (`klantkraan/apps/api` or the receptionist server): SITE FIRST, then the API. Never the reverse.

Report: deployment ID/alias, pages verified, any cache-busting done.
