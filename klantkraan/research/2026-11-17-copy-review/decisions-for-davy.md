# Copy review 17 Nov 2026: what only Davy can decide

The copywriters fixed grammar, AI tells and cuts on every page (changelogs in this folder: copy-home, copy-services, copy-trades, copy-content, copy-intl). Prices and terms are unchanged.

## 0. Claims already corrected (same in NL, EN and ES; say the word and any goes back)
- /aanmelden/: "Aanmelden verplicht u tot niets. Wij nemen eerst contact op" (untrue: both plans go straight to Mollie) is now "Per maand opzegbaar, per mail en zonder opzegtermijn. Eerste maand 50% korting." (terms /prijzen/ already states).
- /prijzen/ Compleet: "Gemiste oproepen bestaan niet meer." removed (absolute promise; the plan takes up to 5 calls at once).
- /over/: "gehost in Nederland" is now "gehost in de EU" (the page lists Hetzner FSN1, Germany). "Registered in the Netherlands" stays.
- /gratis/: "Vier dingen die u vandaag weet" is now "Vier eerste stappen" (the scan takes 1 werkdag, the openings 5).
- /ai-receptionist/: "Daar loopt u een boete mee op. Met Klantkraan niet." is now "Daarmee riskeert u een boete." (implied a legal guarantee).
- EN trade pages: "Disclosure on by default" is now "Disclosure always on"; endings no longer promise trade-specific demos that don't exist.
- /demo/sportscholen/: "Geen verplichting." cut.

Below: the claims they found that may be untrue or contradict each other, and left for you. Ranked by risk.

## 1. Possibly untrue, legal or money risk
1. **Data location.** /over/, the privacy policy and the DPA say "geen export naar de VS" / "opslag uitsluitend in de EU", but /legal/subprocessors/ lists Anthropic, Twilio and Resend in the US. Hosting is "Hetzner Frankfurt" in the DPA and trade FAQs, "FSN1" (Falkenstein) in the footer. Brevo is missing from the subprocessor list. Needs one true version.
2. **/aanmelden/:** corrected in all three languages (see 0). Confirm the wording.
3. **Legal name.** "T4 Software Consulting BV" on every page (footer, /over/, privacy, voorwaarden). It is an eenmanszaak.
4. **Phone claims.** The dakdekkers storm scenario and three FAQs say the receptionist answers calls, texts back within 60 seconds and sends review requests. Other pages say it "staat los van uw telefoonlijn", and review requests are listed as not built.
5. **Results without clients.** City pages say "aangesloten dakdekkers/loodgieters"; blog posts and guides describe client results. If there are no such clients yet, these go.
6. **Setup fee.** /prijzen/: "inrichting vanaf € 249, gratis voor pilotklanten". /ai-receptionist/ shows no setup fee; the blog says "geen opstartkosten".
7. **Price FAQ** on the trade pages opens with "Dat kan niet gebeuren." (a guarantee).
8. **Legal pages:** the AI Act art. 50 citations look wrong; the SLA promises a status page that is not live; liability says "per geval" in one line and "per gebeurtenis" in the next; "Btw verlegd voor klanten buiten Nederland" holds for business customers in other EU countries only.

## 2. Naming and positioning
9. "De Klantenmotor voor ..." (footer tagline, trade page H1s) next to "Het licht blijft aan." on the homepage. Keep both, or one?
10. / and /ai-receptionist/ share the H1 "Het licht blijft aan."
11. Unsourced numbers: 28% missed calls (the site's own guide calls it "verkoopfolklore"), dakdekker € 650 vs € 600 and 35% vs 32% between pages, aannemer 41% meaning two things.

## 3. Small, can be done on a yes
12. / ends with "Begin klein, of begin gratis" and then the same "Gratis" block above the footer: drop the block on / (`offerArea={false}`).
13. /rekentool/ counts phone calls while the service is chat and WhatsApp; the payback shows "< 1 maand" for almost any input; decimals print with a point (1.6).
14. /es/voor-wie/ cards link to the English trade pages.
15. Brevo template #10 (outside the repo) is still in "je".
