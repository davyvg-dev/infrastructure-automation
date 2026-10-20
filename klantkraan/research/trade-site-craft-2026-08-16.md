# What the top 1% of trade & local-service sites actually do

**Prepared:** 2026-08-16
**Scope:** the best websites that _sell a trade service_ — not agency portfolios. Dutch trades (loodgieter, dakdekker, elektricien, schilder, timmerman, hovenier, installateur) and locatie-businesses (kapper, tandarts, garage, trimsalon).
**Method:** ~60 live sites fetched and read; 36 of them additionally **measured mechanically** from raw HTML (`tel:` link count and document position, H1 word count, form field counts, image/alt counts, schema, third-party fingerprints, u/je register counts). Measurement script kept at `scratchpad/measure.mjs`; it is worth porting into the factory as a gate (see §7).

---

## The finding that governs everything else

The category splits into **two species that barely overlap**, and the split is measurable.

| Group (n)                      | avg `tel:` links | phone before the H1 | **zero** phone links | first phone at % of doc | no usable H1 | avg words |
| ------------------------------ | ---------------- | ------------------- | -------------------- | ----------------------- | ------------ | --------- |
| NL lead-gen / SEO plumbers (7) | **16.0**         | 86%                 | 0%                   | 39%                     | 0%           | 3314      |
| NL craft / portfolio (8)       | 1.5              | 38%                 | 13%                  | 63%                     | **50%**      | 586       |
| Award-tier international (7)   | **0.9**          | 14%                 | **29%**              | 48%                     | 29%          | 797       |
| US conversion-tier roofing (6) | 3.3              | 83%                 | 0%                   | 46%                     | 33%          | 1470      |
| **Best-of-breed (7)**          | **4.4**          | **71%**             | 29%¹                 | **34%**                 | **14%**      | 1697      |

¹ the two zeroes in the best-of-breed row are `cedarsprings.net` and `tuineninstijl.be` — included because their _content_ ideas are the best in the study, while their contact mechanics are the worst. See §6.

Read that table again. **The award-winning tier averages 0.9 phone links per homepage and 29% of them have none at all.** The Dutch craft tier — real, good, expensive interieurbouwers and hoveniers — has _no usable `<h1>` on half the sites measured_. `degroenhoveniers.nl` and `tonmaatwerk.nl` have no `<h1>` element whatsoever; `intia.nl`'s H1 is the single word "INTIA"; `hovenierhoeijmakers.nl`'s is "Impressies"; UK multi-award Master Builder `srdesignbuild.co.uk` has the H1 "Home" and its phone number at 83% of the way down the document.

Meanwhile the Dutch SEO tier gets the mechanics right and the substance catastrophically wrong: `mrloodgieteramsterdam.nl` carries **62 `tel:` links and 6,226 words** on one page, of which the vast majority is city-name permutation, and it ships `aggregateRating` schema (self-serving review markup Google ignores and may action).

Neither pole is the target. The target is the middle row, and the middle row is thinly populated — which is the opportunity for a factory that hits it by default.

---

## 1. The reference set

Verified live and read. The "one move worth stealing" column is the point of this table.

### Mobiel / comes-to-you trades

| URL                                                                   | Country | Trade         | Why it's good                                                                                                                                                     | The one move worth stealing                                                                                                                                                                                                                                              |
| --------------------------------------------------------------------- | ------- | ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [fixedtoday.com.au](https://fixedtoday.com.au/)                       | AU      | loodgieter    | 14 `tel:` links, sticky call bar carrying the number _and_ the offer, zero scroll libraries, sections written from inside the customer's panic                    | **Section headings from the customer's timeline: "Before you say yes", "While you wait", "Before you decide".** Nobody else writes headings from inside the emergency. "While you wait" exists only because someone is standing in water right now                       |
| [luecke-dachfassade.de](https://www.luecke-dachfassade.de/)           | DE      | dakdekker     | **39KB total page**, phone at 9.5% of the document, call + WhatsApp + mail + route as four equal buttons, hero photo is _their own building_ with a real alt text | **The one-click contact row that refuses to rank the channels.** Four equal buttons, no primary/secondary. It declines to guess how a stranger wants to reach a roofer                                                                                                   |
| [bigblueplumbing.au](https://bigblueplumbing.au/)                     | AU      | loodgieter    | Hero is a photo of the actual staff; phone in header, hero and sticky footer                                                                                      | **Section two is a money-anxiety strip, not a services list**: "No Hidden Fees / Senior Discount / Priced by the job, not by the hour". Answers _"will this man rip me off?"_ before _"what do you do?"_. The Senior Discount tile is aimed exactly at the 55+ homeowner |
| [spsplumbers.com.au](https://www.spsplumbers.com.au/)                 | AU      | loodgieter    | Licence number, guarantee stack, five-step process in place of a portfolio                                                                                        | **"48% of our 500 jobs per month are returning customers."** One computed statistic that does the work of thirty testimonials — repeat business is the only review metric a sceptic cannot dismiss as cherry-picked                                                      |
| [klindworthroofing.com](https://klindworthroofing.com/)               | US      | dakdekker     | Awwwards HM that kept its phone: 5 `tel:` links, first at 18.8% of doc, `LocalBusiness` + opening-hours schema, full-bleed real roof photography                  | **Projects named after the homeowner and town** — "Mertz — Magnolia, TX", not "Metal roof replacement". Signals _we remember whose house this was_                                                                                                                       |
| [artisanroofing.ca](https://artisanroofing.ca/)                       | CA      | dakdekker     | Sticky bar, 25-year workmanship warranty, drone photography sold as a deliverable                                                                                 | **A different phone number per service region, on the location card.** Turns a regional site into a local one for near-zero cost                                                                                                                                         |
| [ftcc.com.au](https://www.ftcc.com.au/)                               | AU      | timmerman     | Licence + ABN in the footer; agency's own note says "function and conversion over design"                                                                         | **Name the section after its evidentiary job**: "Proof of Quality" and "Real people, real words" instead of "Testimonials"                                                                                                                                               |
| [jeffsealsremodeling.com](https://www.jeffsealsremodeling.com/)       | US      | verbouw       | Per-suburb landing pages with real substance; FAQ; opening hours in footer                                                                                        | **"Before and After" as a top-level nav item**, not a buried gallery. For renovation trades it is the only thing the visitor came for                                                                                                                                    |
| [harryhelmet.com](https://harryhelmet.com/)                           | US      | dakdekker     | 12 `tel:` links, first at 31% of doc, phone before H1                                                                                                             | H1 = **"FAMILY OWNED & OPERATED FOR 40+ YEARS"** — ownership structure and duration as the headline, not the service                                                                                                                                                     |
| [mulderloodgieterservice.nl](https://www.mulderloodgieterservice.nl/) | NL      | loodgieter    | The single best Dutch headline found; 100% "u" register; KvK, vaste prijs, werkgebied, openingstijden, `LocalBusiness` schema                                     | **H1 = "Lekkage? Vandaag nog opgelost."** Four words: the customer's problem as a question, then the promise with a deadline in it. Compare to the six competitors whose H1 is the keyword "Loodgieter Amsterdam"                                                        |
| [akerbv.nl](https://www.akerbv.nl/)                                   | NL      | loodgieter/CV | 100% "u" register (je-count literally 0), KvK + voorwaarden, spoed framed concretely                                                                              | H1 **"24/7 spoed loodgieter & CV-monteur Amsterdam"** — puts the _urgency modifier first_, the trade second, the city last. The reverse of every competitor                                                                                                              |
| [sossnelservice.nl](https://www.sossnelservice.nl/)                   | NL      | loodgieter    | 83% "u", Techniek Nederland, 60 years trading, only 1,149 words — refreshingly un-stuffed for the vertical                                                        | Restraint. It is the only Amsterdam spoed-loodgieter in the sample under 1,500 words, and it ranks                                                                                                                                                                       |

### Craft tier — steal the content ideas, never the contact mechanics

| URL                                                                 | Country | Trade                 | Why it's good                                                                                                                                                                                           | The one move worth stealing                                                                                                                                                                                                                                                           |
| ------------------------------------------------------------------- | ------- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [cedarsprings.net](https://cedarsprings.net/)                       | CA      | hovenier              | Project cards carry **name, location, budget band, design duration, install duration** — verbatim: _"fire, water & alfresco — Oakville, ON \| $550-600k \| 2.5 months design \| 3 months installation"_ | **Publish the budget band and the timeline on every project tile.** Highest-leverage single element in the whole study: it self-qualifies leads brutally. NL form: `€18-22k · 3 weken`. ⚠️ its own phone number is JS-injected and absent from the HTML — measured `tel:` count **0** |
| [tuineninstijl.be](https://www.tuineninstijl.be/)                   | BE      | hovenier              | Dutch-language H1 in **first person singular** naming the emotional end-state: _"Ik transformeer je tuin tot een sfeervolle plek waar je kan ontspannen en waar jij je thuis voelt."_                   | The first-person headline. For a one-person Dutch trade business this beats "Wij zijn gespecialiseerd in…" outright. ⚠️ **no phone number exists anywhere on the site** — measured `tel:` count 0                                                                                     |
| [schreinerei-siegesmund.de](https://www.schreinerei-siegesmund.de/) | DE      | meubelmaker           | Craft photography, restrained trust claims                                                                                                                                                              | **The two-line contradiction headline**: "Moderne Premium Möbel / gefertigt wie vor 100 Jahren". Modern outcome, old method — a reusable formula for any traditional vak                                                                                                              |
| [unionconstruction.ca](https://unionconstruction.ca/)               | CA      | tegelzetter/verbouw   | Awwwards **Site of the Day** whose H1 is "Carrelage et rénovation de cuisines et salles de bain en Mauricie"                                                                                            | Proof that **award-level craft sits happily on a boringly literal headline** (service + service + region, no adjectives). Also: a _dated_ qualification ("Diplômé en charpenterie-menuiserie en 2002") out-trusts "20 jaar ervaring"                                                  |
| [bam-renovation.com](https://www.bam-renovation.com/)               | FR      | metselaar/restauratie | Construction-yellow `#ffcb03` on near-black — the trades' native colour, almost never claimed                                                                                                           | The register: _"Le bâti ancien ? C'est notre terrain de jeu préféré."_ A trade firm writing with affection for the work instead of competence-speak. ⚠️ no `tel:`, no form in the delivered HTML                                                                                      |
| [houtwerff.nl](https://www.houtwerff.nl/)                           | NL      | keukenmaker           | 100% "u", 43 images all with alt text, material-led navigation (warm hout / licht hout / bamboe)                                                                                                        | **Navigate by material, not by service.** Runner-up idea from [menuiserieretaise.fr](https://menuiserieretaise.fr/): **navigate by room** (Keukens, Slaapkamers, Badkamers) — homeowners think in spaces, not in trades                                                               |
| [dievorm.nl](https://dievorm.nl/)                                   | NL      | interieurbouwer       | The only NL craft site measured with the phone above the H1 _and_ a real 13-word H1                                                                                                                     | It simply does both. `DIEVORM ontwerpt, bouwt en monteert uw op maat gemaakte meubels in heel Nederland` — states the three verbs and the werkgebied in one line                                                                                                                      |

### The pure-conversion pole (study the mechanics, reject the tone)

| URL                                                           | Country | Trade      | Why it's here                                                                                             | Note                                                             |
| ------------------------------------------------------------- | ------- | ---------- | --------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| [rotorooter.com](https://www.rotorooter.com/)                 | US      | loodgieter | H1 "The Plumbing Experts You've Trusted for Over 90 Years"; ZIP-code locator as the hero's second element | Duration as the headline claim                                   |
| [mrrooter.com](https://www.mrrooter.com/)                     | US      | loodgieter | "Neighborly Done Right Promise® — If it's not right, we'll make it right"; "Upfront Flat Rate Pricing"    | A named, ownable guarantee beats an adjective                    |
| [mrloodgieteramsterdam.nl](https://mrloodgieteramsterdam.nl/) | NL      | loodgieter | **62 `tel:` links, 6,226 words, 5% "u"**                                                                  | The anti-model. Everything in §7 is derived from sites like this |

---

## 2. Page architecture that works

Two different animals. The factory currently has one section vocabulary (`Hero, Usps, Intro, Diensten, Werk, Reviews, Werkgebied, SpoedPanel, FinalCta` + `StickyCallBar`), which is a _mobiel_ shape. A locatie business needs roughly a third of its sections swapped.

### Mobiel (loodgieter, dakdekker, elektricien, schilder, timmerman, hovenier, installateur)

The customer has a **problem**, is often **anxious**, and wants to know _can you come, when, and what will it cost_.

1. **Hero** — problem-shaped headline + promise with a time in it, phone as a real button with the number visible, second channel (WhatsApp) as an equal, not a lesser, button.
2. **Money-anxiety strip** — the highest-value structural finding in this study. Not USPs about quality; the three fears: _hidden costs, call-out charges, hourly vs fixed_. Big Blue Plumbing puts this second, before services. Klantkraan's `usps:` field is currently generic quality claims ("Nette afwerking") — it should be re-pointed at price fear.
3. **Spoed panel** — only if genuinely offered, and it must say what actually happens (`akerbv.nl` and `mulderloodgieterservice.nl` both do this well: "Vandaag nog opgelost", not "24/7!!").
4. **Diensten** — the jobs, named as the customer names them ("Verstopte afvoer", not "Rioolreiniging").
5. **Werk** — project tiles. See §4: location + scope + (ideally) price band and duration.
6. **Proces** — "Zo werkt het", 3–5 steps. _Currently missing from the factory._ SPS Plumbers, Fixed Today and Big Blue all use a numbered process **in place of a portfolio**, which is exactly right for trades whose work is invisible after completion (loodgieter, elektricien, installateur). A lekkage has no portfolio; it has a process.
7. **Reviews** — with first name + plaats + the job.
8. **Werkgebied** — see §5.
9. **Final CTA** — repeat the phone, not a new idea.

**Section order rule:** the further a trade is from "emergency", the later the phone can appear and the earlier the work can. Loodgieter/dakdekker/elektricien = phone first, work later. Timmerman/hovenier/schilder = work early, phone still above the fold but the primary CTA can be "offerte".

### Locatie (kapper, tandarts, garage, trimsalon)

The customer must **travel to you** and **commit to a slot**. Every anxiety is different: _where is it, when are you open, can I park, who will I get, what does it cost, will it hurt / will they ruin my hair._

1. **Hero** — headline + **primary CTA is "Afspraak maken", not "Bel ons"**. Phone stays present but is secondary for anything non-urgent.
2. **Openingstijden — above the fold or immediately under it.** This is the single biggest structural difference. In the factory, `openingstijden:` currently renders **only in the footer**. For a locatie business that is a defect: it is the most-sought fact on the page. It also belongs in `openingHoursSpecification` schema so it surfaces in the Google panel.
3. **Adres + kaart + gevelfoto** — a photo of the _exterior_ so people recognise the door from the street. Trades never need this; locatie businesses always do.
4. **Bereikbaarheid** — parkeren, OV, toegankelijkheid. Cheap to write, disproportionately reassuring, and completely absent from every generated site.
5. **Behandelingen / diensten + prijs** — locatie businesses are expected to publish tariffs; mobiel trades are not (see §5).
6. **Team** — named individuals with a photo and a speciality, ideally "boek bij …". A kapper _is_ the person. The factory has no `team:` concept.
7. **Interieur** — 4–8 photos of the actual space. This is the locatie equivalent of a trade's project gallery.
8. **Eerste bezoek / wat kun je verwachten** — dominant on the best dental sites; converts anxiety into a known sequence.
9. **Reviews**, **FAQ**, **Final CTA (afspraak)**.

**What locatie needs that mobiel does not:** openingstijden above the fold, address + map + exterior photo, parking/OV, interior gallery, team profiles, price list, "first visit" content, booking integration.
**What mobiel needs that locatie does not:** werkgebied and city pages, spoed handling, call-out-cost transparency, project portfolio with locations, "we come to you" logistics.
**Shared and non-negotiable both ways:** phone above the fold, legal footer, reviews with real attribution, real photos.

---

## 3. Above the fold, measured

Measured on the best examples, expressed as rules with the numbers behind them.

**Why it matters, with the evidence:** in NN/g's eye-tracking corpus of **57,453 fixations**, users spend ~80% of viewing time above the fold, and attention drops ~84% across the fold boundary ([NN/g](https://www.nngroup.com/articles/scrolling-and-attention/), [Fold Manifesto](https://www.nngroup.com/articles/page-fold-manifesto/)). For this audience specifically: users 65+ are **43% slower** at using websites, and reading speed drops ~11% per 20 years of age ([NN/g, older users](https://www.nngroup.com/articles/usability-for-senior-citizens/)). Everything below is calibrated for a reader who is slower and less tolerant of hunting.

**The headline.** Best-in-class H1 length clusters at **3–9 words**:

| Site                       | H1                                                   | words |
| -------------------------- | ---------------------------------------------------- | ----- |
| mulderloodgieterservice.nl | "Lekkage? Vandaag nog opgelost."                     | 4     |
| bwconstructioncompany.com  | "Texas-Born. Family-Built."                          | 4     |
| northfaceconstruction.com  | "5-Star Minneapolis Roofing Contractor"              | 4     |
| fixedtoday.com.au          | "Your Local Sydney Plumbing Specialists."            | 5     |
| puetzconstruction.com      | "Southern Minnesota's #1 Roofing Partner"            | 5     |
| akerbv.nl                  | "24/7 spoed loodgieter & CV-monteur Amsterdam"       | 6     |
| harryhelmet.com            | "FAMILY OWNED & OPERATED FOR 40+ YEARS"              | 7     |
| bigblueplumbing.au         | "Big Blue Plumbing is SEQ's Premier Plumber"         | 7     |
| schreinerei-siegesmund.de  | "Moderne Premium Möbel gefertigt wie vor 100 Jahren" | 8     |

Failure modes at both tails, all measured: **1-word** H1s that are just the company name (`intia.nl` → "INTIA") or a nav label (`srdesignbuild.co.uk`, `thorsenconstruction.us` → "Home"; `leaflandscaping.net` → "Landing Page"); **no H1 at all** (`degroenhoveniers.nl`, `tonmaatwerk.nl`, `havenconstructions.com.au`, `tectaamerica.com`, `tomhillgardendesign.co.uk`); and **15–18-word run-ons** (`reinert-bau.de` 15w, `tuineninstijl.be` 18w — the latter is deliberate and works, but it is a craft-tier luxury, not a spoed pattern).

**Rule:** H1 between 3 and 9 words, containing either the customer's problem or a concrete promise. Never the company name alone. Never "Home".

**The phone.** Measured as position of the first `tel:` link as a percentage through the document:

- Best-of-breed group average: **34%**; `luecke-dachfassade.de` **9.5%**, `certifiedroofingsolutionsllc.com` **18.1%**, `klindworthroofing.com` **18.8%**.
- Craft/award tiers: 48–63%, i.e. below the halfway point of the document, which on mobile is several thumb-swipes down.
- **71% of the best-of-breed group put a `tel:` link before the `</h1>`** — that is the header phone, and it is the single most reliable marker separating the two species.

**Rule:** a real `tel:` link must appear **before the H1 closes** and the number must be **rendered as text**, not an icon. Between 4 and 8 `tel:` links per homepage is the healthy band — 1 is a portfolio, 60 is spam.

**The rest of the first screen.** What the good ones fit above the fold on a phone: headline, one supporting line, phone button with the number in it, second channel (WhatsApp / afspraak), and **one** credibility token (rating, licence number, or years). That is five elements. Everything else measured as noise.

**Hero media.** Static photo, always. Autoplay hero video is the leading cause of LCP failure on visually-rich sites, and the standing 2026 advice is a static image on mobile with video deferred ([Mintec](https://mintec.co/blog/video-lcp-hero-performance-2026/)). Note `luecke-dachfassade.de` ships the entire homepage in **39KB** against `cedarsprings.net`'s 361KB and `fixedtoday.com.au`'s 555KB — and the 39KB page is the better business site. The factory's existing split-hero (copy on paper, photo bleeding off the right edge) is the right call and should not be traded for a full-bleed text-over-photo hero, which forces a scrim that muddies the photo.

---

## 4. Trust mechanics, ranked

Ranked by observed power, and split by **what a new or fictional business can honestly use** versus **what requires real history**. This distinction matters because the factory builds `modus: preview` voorstel-sites for prospects who are not yet clients, and the honesty rule there is absolute.

### Tier 1 — strongest, requires real history

1. **Repeat-business statistic.** "48% of our 500 jobs per month are returning customers" (SPS). Unfakeable-feeling because it is a ratio, not a boast.
2. **Reviews with first name + plaats + the actual job.** The strongest testimonial shape observed compares you to the alternative — Jeff Seals' review reads _"a nice surprise from other contractors"_. 5+ visible reviews is the documented threshold for a meaningful conversion lift.
3. **Named projects with location and scope**, and where possible **budget band + duration** (Cedar Springs). This is simultaneously the best trust element and the best lead qualifier.
4. **Before/after pairs**, same angle, same distance. Before/after sets draw ~67% longer viewing time than finished-only galleries ([Fully Loaded Websites](https://fullyloadedwebsites.com/articles/contractor-photo-galleries-that-sell)). Put them on the _service_ page, not in a general gallery.
5. **Years trading, stated as a date rather than a duration.** "Diplômé in 2002" and "Sinds 1962" beat "jarenlange ervaring" — which is already a `tell-lint` `vulwoorden` violation and should stay one.

### Tier 2 — available to a brand-new business, honestly

6. **Licence / registration numbers.** KvK and btw-id are already required (§5); a new business has them on day one. AU/US sites lean hard on licence numbers and it works. NL equivalent: KvK, plus any vak-specific erkenning actually held.
7. **The owner's face and name, once.** BrightLocal's 4,000-consumer study: a genuine business-owner image inspired the most trust for 46% of respondents vs 33% for generic images. A new eenmanszaak has a face.
8. **A named guarantee.** "Neighborly Done Right Promise® — if it's not right, we'll make it right" (Mr. Rooter). A promise is a commitment you make, not a history you claim — a one-week-old business can offer one honestly.
9. **Price transparency.** Publishing voorrijkosten and uurtarief, or "vaste prijs vooraf", is a trust act available immediately. Big Blue's "Priced by the job, not by the hour" is a positioning statement, not a track record.
10. **The process, in numbered steps.** Requires zero history and substitutes for a portfolio when the work is invisible after completion. This is the single most under-used honest trust device for new trade businesses.
11. **Concrete availability.** "Bel voor 10:00, vandaag nog langs" is verifiable and specific; "24/7 altijd bereikbaar!!" is noise.
12. **Materials and brands used.** Lücke's partner-brand logo row borrows credibility from suppliers — available to anyone who actually uses those materials.
13. **Team headcount / composition.** Lücke's stat bar: "105 Jahre | 12 Mitarbeiter | 2 Ingenieure & Meister | **1 Team**". Note the fourth number is tonal, not quantitative, and it lands better than a fourth statistic would.

### Never, for a new or preview build

- Invented review counts, star ratings, or `aggregateRating` schema. **Measured: 5 of 7 NL lead-gen sites ship `aggregateRating`.** Self-serving review markup is ignored by Google and can trigger a manual action; the existing house policy (curated quotes + a link to the real Google profile, no review schema) is correct and should not be relaxed.
- Stock photos of models in hard hats. Homeowners identify them instantly and trust drops; authentic imagery is reported to lift conversion by up to ~35%, and 98% of consumers say authentic imagery matters for trust (Getty 2024). Notably **zero** sites in the entire measured corpus linked a stock-photo CDN — the good ones simply don't.
- Borrowed keurmerk logos. A VCA or Techniek Nederland badge is a factual claim about membership.
- Fabricated years ("sinds 2009") on a preview build.

---

## 5. The Dutch specifics

### Register: use "u", and the market agrees with the research

DirectResearch/Conversiewerkers: only **35% of Dutch people 66+** prefer "je" in a commercial context; preference for "u" is **66% among those with lower formal education** vs 54% higher. The trade-customer profile is exactly the "u" quadrant.

The measured Dutch corpus splits cleanly and tellingly:

| Site                                     | %"u"   | tier                             |
| ---------------------------------------- | ------ | -------------------------------- |
| akerbv.nl                                | 100%   | established, real business       |
| mulderloodgieterservice.nl               | 100%   | established, real business       |
| houtwerff.nl                             | 100%   | craft                            |
| hovenierhoeijmakers.nl                   | 100%   | craft                            |
| degroenhoveniers.nl                      | 97%    | craft                            |
| sossnelservice.nl                        | 83%    | established (60 yrs)             |
| dievorm.nl                               | 65%    | craft                            |
| cvloodgieter.nl                          | 55%    | mixed — reads as inconsistent    |
| loodgietersbedrijfamsterdam.com          | 14%    | SEO lead-gen                     |
| loodgieteramsterdam020.com               | 13%    | SEO lead-gen                     |
| **mrloodgieteramsterdam.nl**             | **5%** | SEO lead-gen                     |
| atelier19.nl / intia.nl / tonmaatwerk.nl | 0%     | design-led, younger/B2B audience |

Two readings. First, **"u" correlates with being a real operating business** rather than a lead-gen funnel — the pattern is strong enough that "je" plus a 6,000-word page is a reliable spam signature. Second, the 0%-u craft studios are selling €30k kitchens to a design-literate 35–50 audience, where "je" is defensible. **Recommendation: "u" as the factory default for every vak, with `je` available as an explicit per-client opt-in for design-led locatie/craft businesses.** Never mix — `cvloodgieter.nl` at 55% reads as a site written by three people, and mixed register is a linter-catchable defect.

### Legal footer — genuinely mandatory, not optional polish

Handelsregisterwet art. 29 requires the **KvK number** on business correspondence including the website; **btw-id** is required for services sold at distance under BW 3:15d (e-Commerce Directive art. 5) and 6:230b/c (Dienstenwet, Services Directive art. 22). Measured: only **4 of 7** NL lead-gen sites and **2 of 8** NL craft sites carry a detectable KvK; btw-id is rarer still. This is a genuine differentiator that costs nothing, and the factory already enforces it (`modus: live` blocks without KvK/btw) — that gate is well-designed and should be kept strict.

Footer set: bedrijfsnaam, adres, KvK, btw-id, telefoon, e-mail, algemene voorwaarden, privacyverklaring. **Cookie banner: none** — achievable and worth protecting. Measured third-party fingerprints in the NL corpus include `googletagmanager`, `complianz`, `cookieyes`, `trustindex`, `youtube.com/embed` and `google.com/maps` — every one of these is a consent obligation the generated sites currently avoid by construction. A Google-reviews widget (Trustindex/Elfsight) would forfeit that; keep curated quotes plus a link to the live Google profile.

### Keurmerken — observed, not theorised

Actually found in the measured NL corpus: **VCA** (3 sites), **Techniek Nederland** (2), and the generic word **"Erkend"** (5 — usually unqualified, which is close to meaningless). Not observed at all despite being searched for: InstallQ, Bouwgarant, KOMO, Groenkeur, Zeker van je Zaak, VSR.

The live landscape, corrected for recent mergers — this matters, because citing a dead keurmerk is worse than citing none:

- **InstallQ** — the current institute for installation/electrotechnical erkenningsregelingen. **KvINL and Sterkin merged into InstallQ on 1 Jan 2019.** A site claiming a "Sterkin-erkenning" today is citing a defunct mark; treat "Sterkin" as a linter warning.
- **Techniek Nederland** — branchevereniging (the former UNETO-VNI). "UNETO-VNI" is likewise stale.
- **VCA** — safety certification (VGM), about working safely, not about workmanship quality. Common and legitimate.
- **Groenkeur** — the only independent quality mark for the green sector; relevant for hovenier.
- **Bouwgarant / KOMO** — bouw-side; KOMO is product/process certification.

**Rule for the factory:** keurmerken are a `keurmerken:` list in the client YAML, rendered only from an allow-list of currently-live marks, never invented, and never rendered as a borrowed logo image without the client confirming membership.

### Spoed

The Dutch market is saturated with "24/7" — it has stopped carrying information. The good ones replace the claim with a **mechanism**:

- `mulderloodgieterservice.nl`: **"Lekkage? Vandaag nog opgelost."** — a deadline, in the H1.
- `akerbv.nl`: urgency modifier leads the H1 ("24/7 spoed loodgieter & CV-monteur Amsterdam").
- `cvloodgieter.nl` claims response within 5 minutes and on-site in 30–60 minutes — specific enough to be checkable, which is the point.

**Rule:** spoed copy must contain a time or a mechanism ("wij bellen binnen 15 minuten terug", "vandaag nog langs"), never a bare "24/7". The factory's `spoed.tekst` field is the right shape; the gate should reject a value that contains no time expression. And spoed must be **honest** — it is a promise about the business's operations, so `spoed.beschikbaar` should stay false unless the client confirms it.

### Werkgebied and city pages

Google's helpful-content classifier actively clusters near-duplicate page sets as doorway pages; duplicate copy with only the plaatsnaam swapped is the fastest route to a thin-content action, and ~60–70% of each page needs to be genuinely location-specific. John Mueller's public warning was about 1,300 location pages, but the risk is qualitative, not a threshold.

The existing house cap of **3–5 city pages with real local substance** is correct and this research reinforces it. What "real substance" means, taken from the sites that do it well: a named project _in that plaats_, the actual reistijd or travel note, local specifics (grachtenpand vs nieuwbouw, bekende wijken), and a review from someone in that town. If those four cannot be filled, the city does not get a page — it gets a line in the werkgebied list.

`artisanroofing.ca`'s **per-region phone number** is a stronger local signal than a city page, and cheaper.

### Telefoon conventions

- **Prefer a geographic netnummer** (020, 030, 010) over 085/088 for a local trade. Geographic numbers signal regional anchoring and read as local and familiar; 085 is national, less recognised, and reads as a callcentre. A 06 mobile is entirely acceptable for an eenmanszaak and reads as "you get the man himself".
- **Format with spaces, in the Dutch pattern**, and keep the digits visible as text: `020 616 6464`, `06 288 494 39`. The measured corpus renders these inconsistently — `+31202102601` unspaced is common and reads as machine output.
- `href` must be `tel:+31…` in E.164 while the **visible text stays in Dutch national format**. The factory's `telHref` already separates these; keep it.
- **WhatsApp is a first-class channel in NL, not a fallback.** Measured: only 3 of 15 NL sites offer it, all at the lead-gen end. Near-universal private adoption makes it the lowest-friction channel for a non-urgent enquiry, and it feeds the receptionist product. `luecke-dachfassade.de` treating call/WhatsApp/mail/route as four equal buttons is the pattern to copy.

### Prijzen

NL market norms are public and specific: uurtarief ~€45–85 ex btw, voorrijkosten ~€25–40, spoedtarief (na 18:00/weekend) ~€90–145. Homeowners can find these numbers in thirty seconds, so hiding them buys nothing. Publishing "voorrijkosten €35, uurtarief €65, vaste prijs vooraf bij grotere klussen" is a trust act. Measured, only 3 NL sites mention voorrijkosten and 3 mention uurtarief — it is an open flank.

---

## 6. Beautiful vs converting — the tension, resolved

### The tension is real and I can quantify it

Awwwards scores **Design 40% / Usability 30% / Creativity 20% / Content 10%** ([Awwwards evaluation](https://www.awwwards.com/about-evaluation/)). Content — the actual sentences that persuade a homeowner — is a tenth of the score. Judging happens in short sessions against a submission package, not a 30-minute task-completion test. So the awards select for what a designer admires in 30 seconds, and the measurements bear that out exactly: the award-tier group averages **0.9 phone links** and **29% have none at all**.

But the opposite pole is not the answer either. `mrloodgieteramsterdam.nl` has perfect contact mechanics — 62 `tel:` links — attached to 6,226 words of city-permutation filler, 5% "u", and review schema that invites a penalty. It converts the traffic it gets and repels anyone with taste, including exactly the homeowner with a €20k dakkapel budget.

### Where the two genuinely conflict — and which way to choose

| Conflict        | Beautiful wants                                   | Converting wants                              | **Choose**                                                                                                                                                                                                                 |
| --------------- | ------------------------------------------------- | --------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Phone in header | An icon, or nothing; the number is "clutter"      | The digits, as text, always visible           | **Converting, absolutely.** A phone icon alone is a defect for a 55-year-old. Digits as text                                                                                                                               |
| Hero            | Full-bleed photo, text over image, minimal chrome | Headline + phone + one proof token            | **Split the difference — literally.** The factory's split hero (copy on paper, photo bleeding off the edge) gets photographic warmth without a scrim, and keeps text contrast                                              |
| Scroll          | Lenis smooth-scroll, parallax, reveal-on-scroll   | Native scroll                                 | **Converting.** Inertia scrolling keeps moving after the thumb stops — measurably disorienting for older users. Ban it                                                                                                     |
| Loading screen  | A branded preloader                               | Nothing                                       | **Converting.** No exceptions. Observed on `cedarsprings.net`, `unionconstruction.ca`, `tuineninstijl.be`                                                                                                                  |
| Navigation      | Mysterious, exploratory ("Nos activités")         | Literal ("Diensten", "Werkgebied", "Contact") | **Converting**, with one steal from the craft tier: navigate by **room or material** where the vak allows it (keukenmaker, badkamer, timmerman) — that is both more beautiful _and_ better matched to how homeowners think |
| CTA verb        | "Start a project", "Ontdek onze aanpak"           | "Bel 020 616 6464"                            | **Depends on urgency, and this is the real axis.** See below                                                                                                                                                               |
| Word count      | 130–600 words, all whitespace                     | 3,000+                                        | **Neither.** The best-of-breed band is ~1,500–2,000                                                                                                                                                                        |
| Photography     | Moody, cropped, art-directed                      | Bright, literal, lots of it                   | **Beautiful wins here**, provided the photos are _real_. Art direction is the cheapest available luxury signal and it does not cost conversion                                                                             |
| Typography      | Distinctive display face                          | System sans, huge                             | **Beautiful wins.** Type choice is invisible to conversion and highly visible to perceived price. Just keep body text ≥17px and line length ≤70ch                                                                          |
| Colour          | Restrained, one accent                            | High-contrast safety colour                   | **Beautiful wins**, with a contrast floor. `bam-renovation.com`'s construction-yellow shows the trades' native colour can be both                                                                                          |

### The resolution

**The urgency of the vak decides the CTA, and nothing else in the design has to move.**

- **Emergency-shaped vakken** (loodgieter, dakdekker, elektricien, installateur, garage): primary CTA is the phone with the number rendered, WhatsApp equal-weight beside it, phone before the H1, sticky call bar on mobile.
- **Considered-purchase vakken** (timmerman, keukenmaker, hovenier, schilder, interieurbouwer): primary CTA is "Vrijblijvend advies" or "Bekijk het werk", phone still in the header as text, no sticky bar needed. Cedar Springs' budget-band tiles belong here.
- **Locatie businesses** (kapper, tandarts, trimsalon): primary CTA is "Afspraak maken"; the phone is the fallback channel and openingstijden are the fact people came for.

Everything _else_ — type, colour, photography, whitespace, section rhythm — can be as considered as the factory can make it, because **none of it is what breaks the award-tier sites**. What breaks them is a startlingly short list: no phone link, no H1, a preloader, smooth-scroll, and a JS-injected contact block. Those are five mechanical defects, all of them lintable, and none of them is the price of beauty. `luecke-dachfassade.de` is the existence proof: a 39KB page, no scroll library, no loader, phone at 9.5% of the document, four equal contact buttons — and an Awwwards nomination.

**The opinionated version:** for this audience, beauty is not in tension with conversion. _Interaction fashion_ is. Strip the fashion — the loaders, the inertia, the reveal animations, the icon-only phone — and keep the craft. The factory should therefore treat typography, colour, photography and spacing as free to vary (it already does, across seven skin axes), and treat contact mechanics as **invariant and gated**.

---

## 7. Anti-patterns — mechanical and linter-catchable

The existing `tell-lint.mjs` catches copy tells (`drieslag`, `titelkast`, `wenkbrauw`, `weesrij`, `vulwoorden`, `offerte-dichtheid`, `gedachtestreepje`) and `vloot.mjs` catches cross-site sameness. Neither yet catches **contact-mechanics failure or trade-category cheapness**, which is where every site in this study actually died. Proposed additions, each stated so it can be implemented as a counted rule over `dist/`.

### Contact mechanics (new rule family — highest value)

| Rule                   | Fails when                                                                    | Evidence                                                                                                         |
| ---------------------- | ----------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `telefoon-ontbreekt`   | zero `href^="tel:"` in the page                                               | 29% of the award tier; `thorsenconstruction.us`, `tuineninstijl.be`, `earthbounddesigns.com`, `cedarsprings.net` |
| `telefoon-te-laat`     | first `tel:` appears after the `</h1>` on the homepage                        | craft tier averages 63% into the document                                                                        |
| `telefoon-onzichtbaar` | a `tel:` link whose visible text contains no digits (icon-only)               | the classic "designer removed the number" defect                                                                 |
| `telefoon-spam`        | more than 12 `tel:` links on one page                                         | `mrloodgieteramsterdam.nl` = 62                                                                                  |
| `telefoon-opmaak`      | visible number is unspaced (`+31202102601`) rather than Dutch national format | observed on 4 NL sites                                                                                           |
| `kanaal-eenzaam`       | phone present but no second channel (WhatsApp / afspraak / form)              | 12 of 15 NL sites                                                                                                |

### Structure

| Rule                           | Fails when                                                                                                                          |
| ------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- | ------ | ----------------- |
| `geen-h1`                      | page has no `<h1>` — measured on 5 corpus sites                                                                                     |
| `h1-nietszeggend`              | H1 is ≤2 words, or matches the company name alone, or matches `/^(home                                                              | welkom | landing page)$/i` |
| `h1-te-lang`                   | H1 > 12 words (`reinert-bau.de` 15w)                                                                                                |
| `h1-plaatsnaam-stapel`         | H1 is bare `<vak> <plaats>` with no promise — the SEO-farm signature (4 of 7 NL lead-gen sites)                                     |
| `openingstijden-alleen-footer` | **locatie** business renders openingstijden only in the footer — current factory behaviour, and a defect for kapper/tandarts/garage |
| `adres-ontbreekt`              | locatie business with no address + map                                                                                              |

### Copy (extend `vulwoorden`)

Add to the existing list, all observed on the lead-gen end and on none of the good sites: `de klant staat bij ons centraal`, `met oog voor detail`, `scherpe prijzen`, `snel en vakkundig`, `24/7 bereikbaar` **without an accompanying time expression**, `vakmanschap sinds jaar en dag`, `professioneel en betrouwbaar`, `passie voor het vak`, `denken graag met u mee`, `geen verrassingen achteraf` (unless an actual price is stated on the page).

Plus two counted rules:

- `register-gemengd` — both "u/uw" and "je/jij/jouw" exceed 15% of the address-form total on one page. `cvloodgieter.nl` at 55/45 is the failure case.
- `plaatsnaam-dichtheid` — a single plaatsnaam appears more than ~8 times on one page, or the page exceeds ~2,500 words on a homepage. Catches the 6,226-word city-permutation wall.

### Trust and photography

| Rule                | Fails when                                                                                                                    |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `review-schema`     | `aggregateRating` or `Review` schema present — **already house policy, now enforceable**; 5 of 7 NL lead-gen sites violate it |
| `stockfoto-cdn`     | any `unsplash/pexels/shutterstock/istock/getty/adobestock/freepik` URL in the markup — zero good sites had one                |
| `alt-ontbreekt`     | any `<img>` without `alt` (`puetzconstruction.com` had 11)                                                                    |
| `foto-schaars`      | fewer than 6 images on a homepage for a visual vak (dakdekker, hovenier, timmerman, kapper)                                   |
| `keurmerk-verlopen` | copy cites `Sterkin`, `KvINL` or `UNETO-VNI` — all merged/renamed                                                             |
| `erkend-onbepaald`  | the word "erkend" with no named scheme after it (5 of 7 NL lead-gen sites)                                                    |

### Weight and motion

| Rule            | Fails when                                                                                                                                                                |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `preloader`     | any element matching `loading-screen`/`preloader`                                                                                                                         |
| `smooth-scroll` | Lenis / locomotive-scroll / `scroll-behavior: smooth` on `html`                                                                                                           |
| `paginagewicht` | homepage HTML > 150KB (best-of-breed `luecke-dachfassade.de` = 39KB; `fixedtoday.com.au` = 555KB is the outlier the factory should never reach)                           |
| `derde-partij`  | any request to a consent-triggering third party (GTM, Analytics, Facebook, Trustindex, Elfsight, YouTube embed, Google Maps iframe) — protects the no-cookie-banner story |

### The five that actually matter

If only five ship: **`telefoon-ontbreekt`, `telefoon-te-laat`, `geen-h1`, `h1-nietszeggend`, `review-schema`.** Those five separate every good site in this study from every bad one, and four of the five are already satisfied by the factory's current template — which means they are cheap regression guards, not new work.

---

## Sources

Measurement corpus and analysis: 36 sites measured mechanically (raw HTML), ~60 read. Key external sources:

- [NN/g — Scrolling and Attention](https://www.nngroup.com/articles/scrolling-and-attention/) · [The Fold Manifesto](https://www.nngroup.com/articles/page-fold-manifesto/) · [Usability for Older Adults](https://www.nngroup.com/articles/usability-for-senior-citizens/)
- [Awwwards Evaluation System](https://www.awwwards.com/about-evaluation/) · [We Are Tenet — design awards vs real UX results](https://www.wearetenet.com/thoughts/design-awards-vs-real-ux-results)
- [Invoca — Home Services Lead Conversion Benchmarks](https://www.invoca.com/reports/the-invoca-call-conversion-benchmarks-report-home-services-2025) · [Rocket Media — future of home service websites](https://rocketmedia.com/resources/future-of-home-service-websites)
- [Conversiewerkers/DirectResearch — "u" of "je" in zakelijke communicatie](https://conversiewerkers.nl/blog/tutoyeren-u-of-je-in-zakelijke-communicatie/)
- [TrustYourWebsite — KvK-nummer op je website verplicht](https://trustyourwebsite.com/nl/nl/guides/kvk-nummer-website-verplicht) · [Ondernemersplein — regels voor bedrijfscorrespondentie](https://ondernemersplein.overheid.nl/wetten-en-regels/regels-voor-bedrijfscorrespondentie/)
- [InstallQ](https://installq.nl/) (KvINL + Sterkin merged 2019-01-01) · [Elektricien.com — keurmerken](https://elektricien.com/keurmerk/)
- [Up North Media — doorway pages 2026](https://upnorthmedia.co/blog/doorway-pages-seo) · [CXL — stock vs real photos](https://cxl.com/blog/stock-photography-vs-real-photos-cant-use/) · [Fully Loaded Websites — before/after galleries](https://fullyloadedwebsites.com/articles/contractor-photo-galleries-that-sell)
- [Mintec — hero video vs LCP 2026](https://mintec.co/blog/video-lcp-hero-performance-2026/) · [Homedeal — loodgieter kosten](https://www.homedeal.nl/loodgieter/loodgieter-kosten/) · [Dstny — 085 vs netnummer](https://www.dstny.nl/zakelijk-netnummer/overzicht/vergelijken)
