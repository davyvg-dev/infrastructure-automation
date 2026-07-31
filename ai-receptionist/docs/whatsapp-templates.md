# WhatsApp utility templates (Dutch, generic)

> Six templates covering the outbound modules in `WORKFLOW-MOAT.md` and the missed-call funnel. Written once, approved once,
> reused across the entire client base. **Do not create per-client templates** — approval is not
> instant and every onboarding would then be gated on Meta.
>
> Status: **drafted 2026-07-29, not submitted.** Submission is blocked on a production WhatsApp
> sender; we are on the Twilio *sandbox*, which cannot send approved templates. That blocker needs
> Meta Business verification, which needs the KvK/BTW numbers (TODO §D).
>
> Category rules verified against Meta's template-categorization docs via context7
> (`/websites/developers_facebook_business-messaging_whatsapp`, 2026-07-29).

---

## 1. What actually makes a template "utility"

This decides the price. Utility is under $0.03 in NL; marketing is $0.16–0.18, among the highest
rates in the world. The Dutch wording is the whole difference.

Meta's stated criteria:

1. **Strictly non-promotional, with no persuasive intent.**
2. **Tied to a specific user action or request** about their account, order, or service — or
   essential/critical to the user.
3. **Mixed content is fatal.** A template that is 90% transaction status and 10% offer is
   categorized as marketing in full. There is no partial credit.

Meta **re-categorizes automatically**, after approval, without asking. Audit periodically:

```
GET /<WABA_ID>/message_templates?source=AUTO_GENERATED&correct_category=MARKETING
```

If a template shows up there, its price went up roughly 5× and nobody sent an invoice explaining
why. Put this in the monthly ops pass once the sender exists.

**The three phrases that would break any template below** (all real temptations):
- *"deze week 10% korting"* — an offer. Marketing.
- *"onze andere diensten"* — cross-sell. Marketing.
- *"laatste kans"* / *"op=op"* — manufactured urgency, i.e. persuasive intent. Marketing.

Writing rule: **state the status of a thing the customer already started.** Never propose a new one.

---

## 2. The templates

Positional `{{n}}` placeholders, matching Twilio's Content API. (Meta also supports named
parameters via `parameter_format` + `body_text_named_params`; positional is what Twilio maps to,
so stay positional while Twilio is the sender.)

Every template signs off with the business name as the last variable. The sender number already
identifies the business, but trades customers receive messages from many unknown numbers and the
profile name is not always visible in a notification. One variable buys unambiguous identification.

No emoji, no opt-out footer. Opt-out language is a marketing-template convention and adding it
here muddies the category signal. (Opt-outs are still honoured — that is handled at the
conversation level, not in the template.)

---

### 2.1 `offerte_opvolging_1_nl` — quote follow-up, first nudge

**Fires:** job status `quoted`, no reply after ~2 days. **Risk: low.**

```
Hallo {{1}}, je offerte voor {{2}} staat nog open. Bedrag: {{3}}. Geldig tot {{4}}.

Wil je dat we hem doorzetten, of moet er iets aangepast worden? Een berichtje terug is genoeg.

{{5}}
```

| Var | Meaning | Example |
|---|---|---|
| `{{1}}` | Voornaam klant | `Jeroen` |
| `{{2}}` | Werkomschrijving | `het vervangen van de cv-ketel` |
| `{{3}}` | Bedrag | `€ 1.850` |
| `{{4}}` | Geldig tot | `12 augustus` |
| `{{5}}` | Bedrijfsnaam | `Loodgietersbedrijf Meijer` |

**Why utility:** reports the status and validity of a quote the customer themselves requested. No
discount, no urgency, no new offer. "Wil je dat we hem doorzetten" concerns the existing
transaction, which is exactly the line Meta draws.

---

### 2.2 `offerte_opvolging_2_nl` — quote follow-up, expiry notice

**Fires:** job status `quoted`, still no reply, ~2 days before the quote expires. **Last attempt —
after this, hand the job to the owner and stop messaging.** **Risk: low.**

```
Hallo {{1}}, je offerte voor {{2}} verloopt op {{3}}.

Daarna vervalt de prijs en maken we zo nodig een nieuwe. Laat gerust weten of je ermee verder wilt. Ook een nee is prima, dan sluiten we hem netjes af.

{{4}}
```

| Var | Meaning | Example |
|---|---|---|
| `{{1}}` | Voornaam klant | `Jeroen` |
| `{{2}}` | Werkomschrijving | `het vervangen van de cv-ketel` |
| `{{3}}` | Vervaldatum | `12 augustus` |
| `{{4}}` | Bedrijfsnaam | `Loodgietersbedrijf Meijer` |

**Why utility:** an expiry notice on an existing quote. *"Ook een nee is prima"* is deliberate: it
removes persuasive intent, which is the exact thing Meta tests for, and it is also how a decent
tradesperson talks. Do not let anyone "improve" this line into a closing technique.

---

### 2.3 `afspraak_herinnering_nl` — appointment reminder

**Fires:** the day before a scheduled appointment. **Risk: very low** — the textbook utility case.

```
Hallo {{1}}, een korte herinnering aan je afspraak: {{2}} om {{3}}, op {{4}}.

Komt het niet meer uit? Laat het weten, dan plannen we hem om.

{{5}}
```

| Var | Meaning | Example |
|---|---|---|
| `{{1}}` | Voornaam klant | `Jeroen` |
| `{{2}}` | Datum | `dinsdag 5 augustus` |
| `{{3}}` | Tijd | `09:00` |
| `{{4}}` | Adres | `Van Ostadestraat 12, Amsterdam` |
| `{{5}}` | Bedrijfsnaam | `Loodgietersbedrijf Meijer` |

**Why utility:** an appointment the customer booked. Also the highest-ROI template in the set —
reminders cut no-shows, and a no-show is a wasted van, not a wasted message.

---

### 2.4 `review_verzoek_nl` — review request

**Fires:** job status `completed`. **Risk: HIGH — this is the one that will be re-categorized.**

`WORKFLOW-MOAT.md` counts review requests inside the ~125 utility messages a month. Against Meta's
published criteria that is optimistic: asking a customer to do something that benefits the business
is persuasive intent, even though nothing is being sold. Expect this template to be classified as
marketing, or approved and then silently re-categorized.

**Consequences are small but should be stated:** ~40 review requests a month at the marketing rate
instead of utility is roughly €5/month per client, not a business risk. The real risk is discovering
the reclassification by accident.

**Two mitigations, in order:**

1. **Prefer the free path.** If the customer messaged within the last 24 hours, this needs no
   template at all — it goes as a normal service reply inside the session window. Have
   `messaging.send()` check the window before reaching for a template. (Note: service messages
   become billable from 1 Oct 2026, so this saving has an expiry date.)
2. **Submit variant A first.** If it is rejected or re-categorized, switch to variant B and accept
   the marketing rate rather than fighting it.

**Variant A (conservative, submit this one):**

```
Hallo {{1}}, {{2}} is afgerond. Bedankt voor de opdracht.

Wil je laten weten hoe het ging? Dat kan hier: {{3}}

Is er iets niet goed gegaan, stuur ons dan liever een bericht. Dan lossen we het op.

{{4}}
```

**Variant B (direct, only if A fails):** replace the middle line with
*"Als je tevreden bent, helpt een review ons enorm: {{3}}"*. Clearer ask, higher response, and
almost certainly marketing-rated.

| Var | Meaning | Example |
|---|---|---|
| `{{1}}` | Voornaam klant | `Jeroen` |
| `{{2}}` | Werkomschrijving | `Het vervangen van de cv-ketel` |
| `{{3}}` | Review-link | `https://g.page/r/…` |
| `{{4}}` | Bedrijfsnaam | `Loodgietersbedrijf Meijer` |

The "is er iets niet goed gegaan" line is not padding. It routes unhappy customers to a private
channel instead of a public one-star review, which is the entire point of owning the timing.

---

### 2.5 `factuur_herinnering_nl` — invoice reminder

**Fires:** invoice past its due date, no payment recorded. **Risk: very low.**

```
Hallo {{1}}, factuur {{2}} van {{3}} staat nog open. De vervaldatum was {{4}}.

Al betaald? Dan hebben onze berichten elkaar gekruist, laat het gerust weten.

{{5}}
```

| Var | Meaning | Example |
|---|---|---|
| `{{1}}` | Voornaam klant | `Jeroen` |
| `{{2}}` | Factuurnummer | `2026-0142` |
| `{{3}}` | Bedrag | `€ 1.850` |
| `{{4}}` | Vervaldatum | `22 juli` |
| `{{5}}` | Bedrijfsnaam | `Loodgietersbedrijf Meijer` |

**Why utility:** account/billing status on an existing transaction. **Keep the tone this mild.**
Payment chasing that turns threatening is both a category risk and a customer-relationship risk for
the client, and it is their name on the message, not ours. Escalation beyond a second reminder
belongs with the owner, never with an automated worker.

---

### 2.6 `gemiste_oproep_nl` — missed-call follow-up

**Fires:** the customer called the business, nobody answered, and the call was forwarded to
`POST /voice/missed` (`channels/voice_missed.py`). **Risk: low.**

```
Hallo, u belde net met {{1}} en we konden niet opnemen. Waar kunnen we u mee helpen? Stuur hier uw bericht, dan pakken we het direct op.
```

| Var | Meaning | Example |
|---|---|---|
| `{{1}}` | Bedrijfsnaam | `Klantkraan` |

**Why utility:** a direct response to a call the customer placed seconds earlier — tied to a
specific user action, no offer, no persuasion. The "u" register (not "je") because this is the
first contact with someone we may not know at all.

**Art. 50 note:** the template speaks as the business ("we"), which is accurate — a human may
pick the thread up. The moment the *receptionist* answers the customer's reply, the standard
config greeting disclosure applies, so the digital-assistant disclosure happens at the first
automated conversational turn. Do not weaken that greeting to make this flow feel smoother.

**Wiring:** after approval, put the returned Content SID in `.env` as
`WHATSAPP_MISSED_CALL_CONTENT_SID`. Without it the code falls back to a freeform send, which
only delivers on the sandbox or inside an open 24h window — fine for testing, not production.

---

## 3. Submission checklist

Run once, when the production sender exists.

- [ ] Meta Business verification complete; production WhatsApp sender live (not the Twilio sandbox).
- [ ] Template names exactly as above: lowercase, digits and underscores only.
- [ ] `category: "utility"` on all six. Language `nl`.
- [ ] Every `{{n}}` has an `example` value in the submission, or Meta rejects the template outright.
- [ ] Placeholders are never adjacent (`{{1}} {{2}}`) and never open or close the body — a common
      silent rejection cause.
- [ ] Submit 2.4 as **variant A**.
- [ ] Record each returned `content_sid` against the template name; `messaging.send(template=...)`
      maps to it.
- [ ] Subscribe to the `message_template_status_update` webhook so a rejection or re-categorization
      surfaces instead of being discovered in a bill.
- [ ] After approval, run the `correct_category=MARKETING` audit query once, then monthly.

**Twilio Content API surface** (Twilio remains the sender):

```python
client.messages.create(
    from_=..., to=...,
    content_sid=...,                      # the approved template
    content_variables=json.dumps({"1": "Jeroen", "2": "...", ...}),
)
```

---

## 4. What these five deliberately do not cover

- **Anything marketing.** Not a gap; it is the Forbidden list in `CLAUDE.md`.
- **Recurring maintenance reminders** (annual cv-onderhoud). Legitimately utility and probably the
  sixth template, but it needs a service-interval field per client that does not exist yet.
- **Spoed/emergency dispatch.** Time-critical enough to deserve its own template, but it needs the
  owner channel from the workflow-depth plan to know a job went out at all.
- **Per-client tone.** These are generic on purpose. A client who wants their own wording gets it
  at the config level in the *receptionist's* replies, not in approved templates.

---

## Sources

- Template categorization, utility criteria, auto-recategorization and the flagged-template query:
  Meta business-messaging docs via context7 `/websites/developers_facebook_business-messaging_whatsapp`
  (fetched 2026-07-29).
- NL utility/marketing rates and the 1 Oct 2026 service-message change: `WORKFLOW-MOAT.md` §
  "Outbound economics" (checked 2026-07-28).
