# Website-intake checklist

Two parts. Part 1 is client-facing Dutch: send it (or read it out) when the website is sold.
Part 2 is the internal procedure. Principle from the onboarding playbook §2: scrape-first,
do-it-for-them: the client only supplies what we cannot find or must not guess.

---

## Deel 1: Wat wij van u nodig hebben (klant)

Eén keer aanleveren, daarna doen wij de rest. De week-belofte gaat lopen zodra dit compleet
binnen is.

### Tien werkfoto's (met uw telefoon, liggend formaat)

Geen stockfoto's; echte foto's van uw eigen werk overtuigen. Niet mooier maken dan het is.

1. Uzelf of uw team, bij de bus of op de klus (gezicht zichtbaar)
2. De bus met bedrijfsnaam, schuin van voren
3. Een klus in uitvoering (handen aan het werk)
4. Nog een klus in uitvoering, ander soort werk
5. Een afgerond resultaat, voor de oplevering gefotografeerd
6. Nog een afgerond resultaat, ander soort werk
7. Uw gereedschap of werkplaats (netjes, hoeft niet showroom)
8. Een detailfoto van vakwerk waar u trots op bent
9. Een voor-en-na als u die heeft (mag ook twee losse foto's)
10. Iets wat uw bedrijf eigen maakt: het pand, een keurmerkcertificaat, een handdruk bij een
    klant (alleen met toestemming van die klant)

Lukt een nummer niet, sla hem over en maak een extra van een ander nummer. Minder dan tien
kan, de site heeft een nette terugval zonder foto's; met foto's verkoopt hij beter.

### Vijf korte vragen

1. Uw KvK-nummer en btw-id (komen verplicht in de footer).
2. Welke plaatsen of regio bedient u? Maximaal vijf plaatsnamen.
3. Wat wilt u dat een bezoeker als eerste doet: bellen, appen, of allebei?
4. Heeft u twee of drie tevreden klanten die wij met naam en plaats mogen citeren? Zo ja,
   stuur hun woorden letterlijk door (wij verzinnen geen reviews).
5. Welke domeinnaam wilt u? De domeinnaam komt op uw eigen naam te staan; hij is en blijft
   van u.

Prijzen vragen wij bewust niet: die horen in een gesprek, niet op een openbare pagina.

---

## Part 2: Internal procedure (English)

### Scrape first, then top up

1. `kk site new "<Bedrijfsnaam>" --url <site> --near <plaats>` (wraps `app.sitedraft`) writes
   `klantkraan/apps/client-sites/clients/<slug>/client.yaml` straight from the prospect's site
   and Google listing: telefoon and openingstijden mapped in code from the cited extraction,
   the Dutch copy drafted under a schema that forbids invented claims and any price. Same
   underlying rules as `app.extract`: citation-or-blank, prices are NEVER extracted.
   For the receptionist demo, `app.extract -o extraction.json` first and then
   `kk site new ... --from-json extraction.json` reuses one scrape for both configs.
2. The config lands as `modus: preview` (a voorstel). Check telefoon, plaats, werkgebied and
   diensten with your own eyes before anything is sent: `pnpm check` proves the site matches
   the config, not that the config matches reality. Promoting it to a live client site is the
   last section of `website-voorstel-playbook.md`.
   The receptionist config and the site config should never disagree; when both exist, the
   receptionist config is the source the site copies from.
3. The genuinely un-scrapeable set is exactly Deel 1: photos, KvK/btw-id, plaatsen choice,
   review quotes with permission, domain wish, primary CTA preference. Ask ONLY for what the
   scrape did not answer; never send the full list to someone whose site already told us
   half of it.

### Completeness gate (starts the clock)

The "binnen een week online" promise runs from COMPLETE intake. Incomplete intake gets one
reject-with-checklist reply naming exactly what is missing, nothing else. Photo minimum to
pass the gate: none (fallback design exists), but record in the timing log whether photos
were present, because it will show up in conversion later.

### Storage

`clients/<slug>/client.yaml` + `clients/<slug>/fotos/`. Client dirs are per-client data:
keep them out of git the same way `ai-receptionist/config/clients/` is kept out (real names,
real phone numbers). Photos never leave the repo dir; nothing goes to third-party storage.
