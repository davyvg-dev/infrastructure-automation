# Compliance Kill-List

> Practices that look fine on US/UK YouTube but will get us fined in NL or burn our deliverability. **Read this before any tactic gets shipped.**

## 1. Scraping LinkedIn → email finder → cold email at scale to eenmanszaak owners

**Why it's a problem**: opt-in regime for sole traders. No "legitimate interest" defence works. AP has fined for exactly this pattern.

**Do instead**: KvK API filtered on `rechtsvorm = BV`. Eenmanszaak owners reach via content/inbound/LinkedIn connect (no commercial DM).

## 2. WhatsApp blasts from a "warmed" number

**Why**: Tw 11.7 covers any electronic message. The number is almost always a personal mobile → natural-person treatment. No legitimate-interest defence.

**Do instead**: WhatsApp only after first contact established via permitted channel.

## 3. "Just add an unsubscribe link, you're fine"

**Why**: false for sole traders. Opt-out only legalises B2B-to-legal-entity sending. Adding "STOP" doesn't make eenmanszaak-targeting compliant.

**Do instead**: filter audience FIRST, then add the opt-out.

## 4. Buying lists from US/UK data brokers (Apollo bulk export, ZoomInfo, etc.)

**Why**: opaque provenance. AP places burden of proof on us. "I bought it" is not a defence. Most US brokers' EU compliance pages are aspirational.

**Do instead**: build first-party list from KvK + Outscraper, with documented provenance.

## 5. Using KvK Handelsregister data while ignoring the NMI flag

**Why**: explicit prohibition for direct mail. Signals bad faith to AP across all channels — they will read it as "you knew, you chose to ignore."

**Do instead**: filter NMI = true out of all outbound. Period.

## 6. Cold calling sole traders (or after July 2026, anyone without consent)

**Why**: ACM enforcement is active. Wet ongewenste telemarketing reform takes full effect 1 July 2026.

**Do instead**: don't cold call natural persons (eenmanszaak/VOF/zzp, or any 06). SUPERSEDED 2026-07-31 for rechtspersonen: manually calling a confirmed BV's kantoornummer is legal (Tw 11.7 protects natural persons only) and now allowed — rules in `../02-sales/cold-call-playbook.md` §0.

## 7. No DPIA / no LIA / no Records of Processing (Art. 30) for outbound

**Why**: required for any outbound at scale. Absent paperwork = automatic loss if challenged.

**Do instead**: 1-page LIA per campaign in Notion; Art. 30 RoPA spreadsheet with outbound as one row; DPIA template for the AI-receptionist product (separate from outbound but same compliance hygiene).

## 8. Fake personalisation tokens, spoofed sender names

**Why**: breaches Art. 11.7 sender-identification requirement and Art. 11.8 (no misleading subject).

**Do instead**: real name in `From`, real KvK in footer, accurate subject lines (no `re:` faking, no `[ACTION REQUIRED]` shouting).

## 9. Sending cold email from the main brand domain

**Why**: one spam complaint → AP-style enforcement OR Google/Workspace flags → real business email goes dark.

**Do instead**: secondary `.nl` domains (3 of them) ONLY for outbound. Brand domain reserved for inbound + transactional.

## 10. No DMARC `p=reject` + no `List-Unsubscribe` header

**Why**: Gmail/Yahoo bulk-sender rules (Feb 2024+) require both. Without them, ~30% of mail goes straight to spam regardless of content.

**Do instead**: SPF + DKIM + DMARC `p=reject` + List-Unsubscribe header on every campaign, from day 1.

## 11. Personalising cold email with private LinkedIn data scraped at scale

**Why**: LinkedIn ToS violation + AVG processing issue + creep factor. AP scrutinises "deep personalisation" patterns.

**Do instead**: use only publicly stated company info from KvK + their website. Don't reference their LinkedIn profile in cold emails.

## 12. AI-cloned voice / video for cold outreach

**Why**: EU AI Act Art. 50(4) — synthetic media must be disclosed. Cold outreach with AI-cloned voice without disclosure is non-compliant by default. Also: brand-suicide.

**Do instead**: no AI voice/video in cold outbound. AI receptionist is for inbound only and discloses itself.

## 13. "Reply Y if interested" / pretending to be a known contact

**Why**: misleading. Multiple US-template "soft-trick" hooks are misleading-handelspraktijken under art. 6:193b BW. Reclamecode Algemeen Deel art. 2 also bans deceptive presentation.

**Do instead**: direct hooks. The cold-email sequences (`02-sales/cold-email-sequences.md`) follow this.

## 14. Cold email + cold LinkedIn + cold WhatsApp to the same person within 7 days

**Why**: harassment under AVG + Tw. Pattern detected by AP as "spam regardless of opt-out compliance."

**Do instead**: one channel at a time. Spread touches over weeks. Suppression hash by person, not by channel.

## 15. Continuing to send after a "STOP" or unsubscribe

**Why**: highest-severity AVG breach.

**Do instead**: suppression hash applies immediately, across all channels, forever. Test it monthly by re-running a small batch against the suppression table.

## 16. Hidden tracking pixels claiming "we don't track"

**Why**: AVG art. 5 transparency. Either disclose tracking or don't track.

**Do instead**: minimal tracking (reply, click). Pixel-level opens are unreliable anyway (Apple Mail Privacy Protection blocks them).

## 17. Re-engaging an old list "because they engaged once"

**Why**: AP guidance: consent expires; previous engagement doesn't permanently legalise outreach. Especially if list is > 12 months old without engagement.

**Do instead**: 12-month engagement decay. After 12 months of no engagement, the contact returns to "cold" status.

## 18. Forwarding caller data to the LLM provider without DPA flow-down

**Why**: AVG art. 28 — every sub-processor needs the same obligations imposed.

**Do instead**: signed DPAs with Anthropic, Synthflow, ElevenLabs, etc. (see `04-legal/dpa-outline.md`). Sub-processor list updated when changes occur.

## 19. Disabling the AI Act art. 50 disclosure on client request

**Why**: non-waivable obligation on the provider (Klantkraan). Fines up to €15M.

**Do instead**: MSA includes the non-waivable clause (`04-legal/ai-act-disclosure.md`).

## 20. Promising 99.9% uptime as a solo founder

**Why**: 99.9% = 43 min downtime/mo. One Synthflow outage eats it. Then we owe service credits AND look unreliable.

**Do instead**: 99.0% SLA only (~7h/mo). Honest. (`04-legal/sla-annex.md`)

## Audit cadence

| When | Action |
|---|---|
| Before every new campaign | Verify it against this list. One paragraph note in Notion of any edge cases. |
| Monthly | Review last 30 days of outbound. Any kill-list violations? Document. |
| Quarterly | Re-read this doc as a team (or as solo + AI). Update with any new AP/ACM guidance. |
| Annually | Full external review (privacy lawyer or ICTRecht). |

## Source

- AP digital direct marketing: https://www.autoriteitpersoonsgegevens.nl/en/themes/internet-and-smart-devices/advertising/digital-direct-marketing
- art. 6:193b BW misleidende handelspraktijken: https://wetten.overheid.nl/BWBR0005289/
- Reclamecode Algemeen Deel: https://www.reclamecode.nl/nederlandse-reclame-code/algemeen-deel/
- Gmail bulk sender requirements: https://support.google.com/mail/answer/81126
- EU AI Act art. 50: https://artificialintelligenceact.eu/article/50/
