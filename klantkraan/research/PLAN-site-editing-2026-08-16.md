# How a delivered site gets edited without breaking

Founder requirement, verbatim: _"every website I deliver needs to be editable in an easy
way. So if I were to generate a website off a template, the user (me and the client) need to
be able to easily make changes (photos, copy, etc) without breaking any existing
functionality. That last point is crucial."_

Researched 2026-08-16 against every serious option. This is the decision doc; §1 is the
recommendation and §5 is what remains to be built. **Nothing in §5 is built yet** — §4 is,
and it is the half that carries the "without breaking anything" clause.

---

## 1. The recommendation

**Do not buy a CMS. Generate the edit form from the Zod schema that already gates the build.**

Every off-the-shelf option fails on one of two hard constraints, and both failures are
disqualifying rather than annoying:

- **Sveltia CMS** is the better software by a distance — 976 commits in six months against
  Decap's 76 human ones, in-browser WebP conversion and resize on upload, `max_file_size`,
  a phone-friendly PWA. It requires a **GitHub, GitLab or Gitea account** to log in.
  Git-gateway is explicitly unsupported, custom backends were closed "not planned"
  (issue #589, 2026-01-03), and there is no email or magic-link path. A Dutch tradesman will
  not create a GitHub account. Its Cloudflare Worker is an OAuth relay, not an identity
  provider — the user still lands on a GitHub login page.
- **Decap + DecapBridge** ($9/mo) is the only combination with email-invite and password
  login, and **Decap has no image processing at all**: a 12MB phone photo goes into the repo
  at 12MB and onto the site at 12MB.
- **Pages CMS** genuinely solves auth — verified in its source, an invited collaborator gets
  a 6-digit email OTP, never touches GitHub, and writes go through the App installation
  token. But it has no image optimization either, an **open unfixed 413 on normal phone
  photos** (issue #425, 2026-08-10), needs Node + Postgres to self-host, has **no preview
  and no PR flow**, one maintainer with 474 of ~490 commits, and an unanswered GDPR DPA
  question on the hosted instance (issue #422, 2026-07-27).

And the finding that rules out the whole category regardless of auth: **Decap and Sveltia
both destroy YAML comments.** Proven at source level — neither round-trips a `Document`, both
stringify a plain JS object. Measured against `voorbeeld-kapper-rotterdam/client.yaml`:
**47 comment lines and 12 blank lines out of 122 (39%)** would be deleted the first time a
client pressed save, including the header explaining why preview mode legally omits KvK and
btw-id. Decap can regenerate comments from a `comment:` property in its own config; Sveltia
cannot. Either way the config stops being a document anyone can read.

The alternative is small because the hard part is already done. `zodToJsonSchema(ClientSchema)`
was verified to emit a clean 4,954-byte draft-07 schema covering all 13 top-level fields
including the `openingstijden` tuple. That means:

- **one source of truth.** The schema that fails the build is the schema that renders the
  form. They cannot drift, because there is only one.
- **we own the writer**, so the comments survive and the file stays a document.
- **Dutch labels and help text live in a `uiSchema`**, outside the validation contract, so
  editor cosmetics never pollute the thing the build depends on.

Runner-up if this turns out to be more work than it looks: **Pages CMS, self-hosted on the
Hetzner box**, accepting the comment loss and putting a hard image gate in front of it. Its
auth story is genuinely good and it is the only option that solves the tradesman login for
free.

**Worth saying plainly: the honest option is also "not yet".** There are zero paying client
sites. The current flow — the client emails what they want changed, the founder runs the
factory — has none of these problems, and a CMS is build-heavy work justified by client
volume that does not exist. §4 below is worth doing at any volume. §5 should wait for a
client who has actually asked to edit their own site.

---

## 2. What the client's experience has to be

Narrated, because if this story is bad the option is bad. A 52-year-old loodgieter wants to
change Thursday's closing time and swap the photo of the van.

1. He opens a link we sent him. Not a login page he has to remember — a link.
2. He types his email. A six-digit code arrives. He types it. (No password to forget, no
   account to create, no GitHub.)
3. He sees his own site's fields in Dutch, in the order they appear on the page, with the
   current values filled in. Not YAML. Not a file tree.
4. He changes `donderdag` from `18:00` to `21:00`. The field will not accept `9 uur 's
avonds` — it says, in Dutch, that it wants `uu:mm`.
5. He drags a photo off his phone onto the van picture. It is 11MB and HEIC. It is accepted,
   converted and resized before it is stored — not rejected with an error he cannot act on.
6. He presses **Bekijk wijziging**. He gets a link to his site as it will look. Not live yet.
7. He presses **Zet online**. Ninety seconds later it is live.
8. If anything in that chain fails, **the site that is already live stays exactly as it is.**

Steps 4, 5, 6 and 8 are the whole requirement. Steps 1–3 are why the off-the-shelf options
were evaluated at all.

---

## 3. Why an edit cannot break the site — the layers

Five, and they are independent on purpose. A single validation step that runs in the editor
is the weakest possible place to put this: Storyblok shipped API-side enforcement of its own
field limits only in **May 2026**, having been UI-only for years, which is what "validated in
the CMS" is worth.

| #   | Layer                                                         | Catches                                                                                                                      |
| --- | ------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| 1   | Field validation at edit time (from the Zod schema)           | wrong shape, missing required field, bad time format, over-length H1                                                         |
| 2   | **The same Zod schema at build time** (`ClientSchemaChecked`) | anything that reached the file another way — a hand edit, an import, a script                                                |
| 3   | The fact gate over the rendered HTML (`pnpm check`)           | prices, placeholders, a missing legal field on a live build — things a schema cannot see because they are about the _output_ |
| 4   | The build fails closed                                        | a broken config produces no deploy, so **the last good version stays up**                                                    |
| 5   | Preview deploy before promote                                 | everything the first four cannot: does it actually look right                                                                |

Layer 2 is the load-bearing one and it already exists. Layer 1 is a convenience that makes
layer 2 fire less often.

---

## 4. What is already built (2026-08-16)

The half that does not depend on choosing an editor, and the half that carries the "without
breaking anything" clause:

- **Client photographs cannot break the site any more.** `scripts/client-fotos.py` takes the
  originals as the client sends them — any size, any format, iPhone HEIC included — and cuts
  the same four renditions the stock sets use. Verified end to end on a 4032px phone JPEG, a
  portrait carrying an EXIF rotation flag (which Pillow ignores by default and every browser
  honours, so without correction the client's best photo ships on its side), and a HEIC.
  All three land at 22–26KB on the page.
- **Photo roles are named, not positional.** `fotos/` used to be read with `readdir().sort()`
  and `fotos[0]` became the hero, so which photograph led the site was decided by
  **alphabetical order** — adding `afspraak.jpg` silently replaced it. `client.yaml` now
  names them in order and the loader reads a manifest.
- **Dimensions are known at build time**, so the page reserves the box and does not reflow
  as photos load. Client photos previously shipped with no `width`/`height` at all.
- **Alt text is required**, in Dutch, minimum ten characters, or the script refuses.
- **A stale manifest fails the build** rather than silently serving last month's photo.
- **Content length is gated where a design ceiling was measured**: `teksten.kop` at 55/70/90
  characters depending on `schaal`, and `schaal: royaal` refused next to `hero: gesplitst`.
- **The CSS floor** means copy that gets past all of that still cannot overflow:
  `overflow-wrap: break-word` on every heading, `min-width: 0` and `minmax(0, 1fr)` in the
  hero grid, headings capped in `ch`.

---

## 5. What remains, in order

1. **`kk site fotos <slug>`** — wire the script into the CLI next to `kk site build`. ~1h.
2. **Emit the JSON Schema at build time** — `zodToJsonSchema(ClientSchema)` to a file, so the
   form and the gate cannot drift. ~2h.
3. **Add `.describe()` to every field in `ClientSchema`.** It is used **zero** times today,
   and a description becomes the form's help text. This is the single cheapest thing on the
   list and it is what decides whether the form is self-explanatory. ~2h.
4. **The form itself** — `@rjsf/core` 6.8.0 + `@rjsf/validator-ajv8`, fed the JSON Schema,
   with a Dutch `uiSchema`. RJSF never imports Zod, so the editor UI is decoupled from the
   Zod 3 → 4 migration. Costs adding React to a repo that has none, which is the one real
   objection. ~1-2 days.
5. **Auth** — Cloudflare Access + one-time PIN is **€0 up to 50 users** and zero code. Seats
   never auto-free (revoking does not release one; only removing does), and Pages' Access
   wiring has two documented traps: the toggle does not cover the bare `*.pages.dev`, and a
   custom domain must be added _before_ the policy. Above 50 clients, or to avoid seat
   management, an HMAC magic link on a Worker plus Resend (free tier covers the volume). ~1d.
6. **The write path** — a Worker committing `client.yaml` via `PUT /repos/.../contents/...`
   with a GitHub App installation token. **The commit is itself the build trigger**: a push
   written with an App installation token does fire `on: push`, so no `repository_dispatch`
   is needed. Watch the secondary limit (80 content-generating requests/minute), not the
   hourly one. ~1d.
7. **The deploy** — GitHub Actions + `cloudflare/wrangler-action@v4`. **Free at this scale**:
   150 builds/month is ~450 of 2,000 free minutes, and it stays free to roughly 220 sites.

### The one architectural decision the founder has to make

**Cloudflare Pages cannot promote a preview to production without re-uploading.** There is no
promote endpoint; rollback only targets prior _production_ deployments. So step 7 of the
client's story ("Zet online") means a second build, and the thing he approved is not
byte-for-byte the thing that goes live.

**Workers Static Assets can** — `wrangler versions upload` gives a stable preview URL,
`wrangler versions deploy` promotes that exact version, and as of **2026-08-14** an Access
policy attaches to a Worker and covers its previews automatically. Against it: **Workers
cannot serve custom domains outside Cloudflare zones**, and tradesmen who keep their domain
at their own registrar will need exactly that. Pages supports it.

That trade — approve-the-exact-bytes versus serve-any-registrar's-domain — is the founder's
call, and it should be made before step 7 rather than after.

Two other facts that constrain this: Pages is **not** deprecated (the "maintenance mode"
claim is a community paraphrase of one April-2025 blog sentence), the cap is 100 projects per
account against 500 Workers; and `/cdn-cgi/image/` **does not work on `*.pages.dev`**, so any
plan to resize client uploads at the edge rather than at build time needs a real custom
domain first. Doing it at build time, as §4 does, sidesteps that entirely.
