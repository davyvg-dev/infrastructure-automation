# DNS / NS troubleshooting — TransIP → Cloudflare

> This domain (`klantkraan.nl` and `klantkraan.com`) is registered at TransIP but should resolve via Cloudflare nameservers so the marketing site can be served at the canonical apex. The NS swap was initiated 2026-05-20 but hasn't propagated. This doc is the founder's checklist to confirm or repair the swap.

## What we want at the end

```
$ dig NS klantkraan.nl +short
xxxx.ns.cloudflare.com.
yyyy.ns.cloudflare.com.
```

(Both nameservers will end in `.ns.cloudflare.com`. The `xxxx` and `yyyy` are Cloudflare-assigned, specific to your zone.)

## What we see today (2026-05-20)

```
$ dig NS klantkraan.nl +short
ns0.transip.net.
ns1.transip.nl.
ns2.transip.eu.
```

The domain is still being served by TransIP's own nameservers. Either:

1. The NS swap at TransIP was never saved (UI confirmed but didn't persist)
2. The swap was saved but to wrong values
3. The swap was saved correctly but propagation is still pending after >24h (unusual)

## Step 1 — Find your Cloudflare-assigned nameservers

You can't just type any `*.ns.cloudflare.com` — Cloudflare assigns specific NS pairs per zone.

1. Log in: https://dash.cloudflare.com
2. Click on the `klantkraan.nl` zone (left sidebar or zone list)
3. Scroll down to the **DNS** section, or look in the **Overview** tab
4. Under "Cloudflare nameservers" you'll see two records like:

   ```
   ada.ns.cloudflare.com
   walt.ns.cloudflare.com
   ```

   (Names are random words, not "ada" and "walt" specifically — copy what Cloudflare shows you.)

5. **Write these two values down.** You'll paste them into TransIP next.

Repeat for `klantkraan.com`. Cloudflare will assign a _different_ pair of nameservers per zone.

## Step 2 — Confirm what TransIP shows

1. Log in: https://www.transip.nl/cp/
2. Domeinen & hosting → klik op `klantkraan.nl`
3. Look for the **Nameservers** section (or "DNS instellingen")
4. You should see 2 or 3 nameserver entries

**What's there right now matters**:

- If you see `ns0.transip.net` / `ns1.transip.nl` / `ns2.transip.eu` → the swap was **not** saved. Go to Step 3.
- If you see the Cloudflare pair from Step 1 → the swap was saved. Go to Step 4.
- If you see Cloudflare-looking nameservers but they don't match Step 1 → wrong values were entered. Go to Step 3 and re-enter.

## Step 3 — Re-do the nameserver swap at TransIP

1. In the TransIP control panel, on the `klantkraan.nl` domain page, find **Wijzig nameservers** (or similar — sometimes labelled "Externe nameservers gebruiken")
2. Select the "Custom nameservers" / "Externe nameservers" option (not TransIP's default)
3. Paste in the Cloudflare nameservers from Step 1:
   - NS 1: `<first>.ns.cloudflare.com`
   - NS 2: `<second>.ns.cloudflare.com`
4. **Save / Bevestigen.** TransIP may ask for 2FA confirmation.
5. Note the timestamp — propagation starts now.

Repeat for `klantkraan.com` with **its own** Cloudflare nameservers (different pair).

## Step 4 — Check propagation

Open Terminal and run:

```bash
dig NS klantkraan.nl +short
dig NS klantkraan.com +short
```

What you'll see:

- Within minutes of saving: **still old nameservers** (this is normal — local DNS caches stale value)
- After 1–4 hours: **mix of old + new** as caches expire region by region
- After 24 hours: **only new nameservers** worldwide

To bypass local cache, query Google's public resolver directly:

```bash
dig @8.8.8.8 NS klantkraan.nl +short
```

If that shows Cloudflare values but your normal `dig` still shows TransIP, your ISP's DNS is just slow. Wait.

## Step 5 — When the swap is confirmed propagated

Tell Claude (or do it yourself):

```bash
# from klantkraan/apps/marketing-site
../api/node_modules/.bin/wrangler pages domains add klantkraan.nl --project-name=klantkraan-marketing
../api/node_modules/.bin/wrangler pages domains add www.klantkraan.nl --project-name=klantkraan-marketing
```

Cloudflare Pages will verify the domain (instant, since it now controls DNS), then issue a TLS cert (typically <10 min via Let's Encrypt / CF managed). The site goes live at `https://klantkraan.nl` immediately after.

## When to escalate to TransIP support

Only after **>48 hours** since the most recent save at TransIP and `dig @8.8.8.8 NS klantkraan.nl +short` still shows transip.net values.

Email to use: `support@transip.nl` (Dutch) or via the control panel "Vraag stellen" function.

Template message:

```
Hallo,

Op 20 mei 2026 heb ik voor de domeinen klantkraan.nl en klantkraan.com
externe nameservers ingesteld (Cloudflare). Bij wijziging meldt TransIP
"opgeslagen", maar `dig NS klantkraan.nl +short` blijft ns0.transip.net,
ns1.transip.nl, ns2.transip.eu tonen — ook na 48+ uur en bij directe
query op 8.8.8.8.

Kunt u nakijken of de nameserver-wijziging daadwerkelijk is doorgevoerd
naar het SIDN-register? Wellicht is er iets misgegaan in de propagatie
tussen TransIP en het register.

Met vriendelijke groet,
[uw naam]
```

## Reference — Cloudflare side

If Cloudflare can't see your domain after >24h, log into the dashboard and re-add the zone — Cloudflare may have de-activated it after 7+ days without successful NS verification. The flow:

1. Cloudflare dashboard → "Add a Site"
2. Type `klantkraan.nl`, click "Continue"
3. Pick the Free plan (sufficient for our setup)
4. Cloudflare will fetch existing DNS records (mostly empty if nothing was migrated)
5. You'll get a **new** pair of NS nameservers — write these down and **redo Step 3** with the new values
