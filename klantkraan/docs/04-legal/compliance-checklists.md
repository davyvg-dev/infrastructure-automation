# Compliance Checklists

> Two checklists: one for **before the first paid invoice**, one for **before the 10th client**. Both are blocking — do not skip.

## DO BEFORE FIRST CLIENT INVOICE

- [ ] **1. Handelsnaam registration** — file "Klantkraan" as a handelsnaam under T4 Software Consulting at KvK. €0–€20.
- [ ] **2. Domain registration** — `klantkraan.nl` + `klantkraan.com` registered.
- [ ] **3. Legal pages live** on `klantkraan.nl/legal`:
  - [ ] MSA / Algemene Voorwaarden
  - [ ] DPA / Verwerkersovereenkomst
  - [ ] Privacy Policy
  - [ ] SLA
  - [ ] AI-disclosure notice + retention policy
  - [ ] Sub-processor list (canonical, updated when changed)
- [ ] **4. Sub-processor DPAs signed** (click-through or email-signed):
  - [ ] Anthropic — https://www.anthropic.com/legal/data-processing-addendum
  - [ ] Synthflow — `dataprotectionofficer@synthflow.ai`
  - [ ] CM.com
  - [ ] Attio
  - [ ] Hetzner — https://www.hetzner.com/AV/DPA_en.pdf
  - [ ] Cloudflare
  - [ ] Neon — https://neon.com/dpa
  - [ ] Resend
  - [ ] Mollie
  - [ ] Moneybird
- [ ] **5. Records of Processing Activities (Art. 30 AVG)** — spreadsheet or Notion table with:
  - Verwerkingsdoel
  - Categorieën persoonsgegevens
  - Categorieën ontvangers
  - Doorgiften buiten EER (+ mechanisme)
  - Bewaartermijnen
  - Beveiligingsmaatregelen
- [ ] **6. DPIA done + signed off** for the AI receptionist service tier (voice + AI + caller profiling triggers it).
- [ ] **7. Synthflow agent baseline**:
  - [ ] Dutch Art. 50 disclosure as first turn, verbatim per `04-legal/ai-act-disclosure.md`
  - [ ] Disclosure-played log written for every call
- [ ] **8. Insurance bound**:
  - [ ] Hiscox PI (or equivalent) — min €500k cover
  - [ ] Hiscox AVB — min €1M cover
  - [ ] Cyber — min €1M cover
  - [ ] Certificates of insurance saved to `/legal/insurance/`
- [ ] **9. Moneybird configured**:
  - [ ] BTW 21% standaard + reverse-charge naar EU
  - [ ] ICP-opgave geactiveerd (quarterly)
  - [ ] Mollie integration
  - [ ] Default factuur-template met KvK + BTW-nummer + bank
- [ ] **10. BTW-nummer active** + VIES-validated (https://ec.europa.eu/taxation_customs/vies/)
- [ ] **11. Order form clause** — MSA signature flow includes:
  > "Klant warrants dat zij verwerkingsverantwoordelijke is voor alle persoonsgegevens van bellers/klanten en heeft rechtmatige grondslag (AVG art. 6) voor verwerking."
- [ ] **12. Incident response playbook** drafted (48h client notify, 72h AP-melding).

## DO BEFORE 10TH CLIENT

- [ ] **1. Convert to Holding-BV + Werk-BV** structure:
  - [ ] Notary appointment (~€1,000–1,500)
  - [ ] T4 → "T4 Holding B.V." (or rename)
  - [ ] New "Klantkraan B.V." als werk-BV, 100% gehouden door T4 Holding
  - [ ] Managementovereenkomst getekend (zakelijk/at-arm's-length)
  - [ ] UBO registered (KvK UBO-register)
- [ ] **2. Start DGA-loon €58.000/jaar payroll** (use Employes / Loket.nl)
- [ ] **3. Accountant aangenomen** for:
  - [ ] Vpb (vennootschapsbelasting)
  - [ ] Jaarrekening
  - [ ] Deelnemingsvrijstelling setup
  - Cost: ~€1,500–2,500/jaar
- [ ] **4. Privacy lawyer one-pass review** of MSA + DPA + DPIA + SLA. €1,500–2,500. Suggested: ICTRecht, Considerati.
- [ ] **5. Status page live** at `status.klantkraan.nl` (self-hosted Uptime Kuma) — evidentiary backing for the 99% SLA
- [ ] **6. Data breach response playbook tested** — tabletop exercise with notification templates ready (klant <48h, AP <72h via meldloket.autoriteitpersoonsgegevens.nl)
- [ ] **7. RoPA → tool**: move from spreadsheet to Vanta / ICTRecht Tool / Privacy Company when sub-processors > 20
- [ ] **8. If first UK client signed**:
  - [ ] B2B service "outside scope" of UK VAT — confirm invoice template
  - [ ] No UK tax rep needed (B2B only)
  - [ ] ICP-opgave quarterly (EU customers only — UK is separately tracked)
- [ ] **9. Sub-processor list refresh** — re-send 30-day change notice to all clients if sub-processors changed
- [ ] **10. Annual penetration test** budgeted (year 2 onwards). Quote from a Dutch firm (Computest, Northwave).

## Periodic compliance routines

| Frequency     | Task                                                                                                |
| ------------- | --------------------------------------------------------------------------------------------------- |
| **Daily**     | Monitor Sentry + Healthchecks.io alerts                                                             |
| **Weekly**    | Audit one random call for AI-Act disclosure playback                                                |
| **Monthly**   | Audit 10 random calls; refresh sub-processor list if needed; review insurance coverage vs. exposure |
| **Quarterly** | ICP-opgave to Belastingdienst; review RoPA; spot-check DPA-flow-down with new sub-processors        |
| **Annually**  | Re-read AI Act + AVG guidance; renew DPA versions; insurance renewal; pen test (year 2+)            |

## Where things live

- All policies + procedures: `klantkraan.nl/legal/*`
- Internal audit logs: Notion page "Compliance audits" + Postgres `compliance_audits` table
- Insurance certificates: `/legal/insurance/` (private GitHub repo or 1Password vault)
- Incident postmortems: Notion page "Incidents" + git PR template

## Source

- Pre-launch checklist: `04-legal/dpa-outline.md`, `04-legal/ai-act-disclosure.md`, `04-legal/insurance.md`
- AVG art. 30 RoPA: https://www.privacy-regulation.eu/nl/artikel-30-register-van-de-verwerkingsactiviteiten-EU-AVG.htm
- AP breach notification: https://www.autoriteitpersoonsgegevens.nl/en/topics/security/security-incidents
- KvK UBO register: https://www.kvk.nl/inschrijven-en-wijzigen/ubo-opgeven/
