# Google Calendar setup (real client)

The demo uses a built-in simulator. For a paying client, connect their **own** Google Calendar so
the receptionist reads their real availability and writes real appointments. Design: one shared
service account, per-client calendar sharing, **no domain-wide delegation**.

## One-time (us) — create the service account

Do this once; the same service account is reused for every client.

1. https://console.cloud.google.com → create/select a project (e.g. `klantkraan`).
2. APIs & Services → **Enable APIs and services** → enable **Google Calendar API**.
3. IAM & Admin → **Service Accounts** → **Create service account**, e.g. `klantkraan-agenda`.
   Note its email: `klantkraan-agenda@<project>.iam.gserviceaccount.com`.
4. Open the service account → **Keys** → **Add key → Create new key → JSON** → download.
   Keep it secret and outside the repo — it's the private key for every client's calendar.

No OAuth consent screen, no domain-wide delegation needed.

## Per client (the client does this, ~1 minute, on a computer)

1. Google Calendar (calendar.google.com) → hover their calendar in the left list → **⋮** →
   **Settings and sharing**.
2. **Share with specific people or groups** → **Add people** → paste
   `klantkraan-agenda@<project>.iam.gserviceaccount.com`.
3. Permission: **Make changes to events** → **Send**.

Their **calendar ID** is normally their Gmail address (Settings and sharing → *Integrate
calendar* → **Calendar ID**). Works with a normal @gmail.com account — no Google Workspace
required.

## Wire it up (us)

In the client's config YAML:

```yaml
calendar:
  provider: google
  calendar_id: "client@gmail.com"
```

In `.env`:

```
GOOGLE_CALENDAR_SA_JSON=/path/to/klantkraan-agenda-sa.json
```

Smoke test (read-only, creates nothing):

```
BUSINESS_CONFIG=config/<client>.yaml python -m app.selftest calendar-google
```

Expect: `connected to Google Calendar; N open day(s); …`.

## Notes / gotchas

- Permission must be **Make changes to events** (writer). "See all event details" is read-only
  and booking will fail.
- We never set `attendees` on events — a service account without delegation can't add guests
  (Google returns `forbiddenForServiceAccounts`). The customer's name/phone go in the event
  **summary and description** instead.
- All times are sent in the business timezone (`business.timezone`, default `Europe/Amsterdam`).
- Availability = the business's opening hours (from the YAML) **minus** the calendar's busy
  blocks. The client blocks time off simply by putting anything on their own calendar.
