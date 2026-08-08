"""Render the batch-3 cold outreach mails as branded HTML + plain text.

Until this existed the outreach batch was 23 hand-written plain-text mails pasted
into Gmail one at a time. Two things went wrong with that. Gmail auto-linkified the
bare demo URL and wrote its own google.com/url redirect into the visible body, and
every mail looked like a terminal dump next to the transactional mail the same
company sends after someone pays.

So the batch renders through mail_layout, the same blocks the welcome mail uses:
one document, an HTML part and a text part that cannot drift, an explicit anchor
whose text is the real URL, and the house band and footer around it.

The per-prospect copy lives in PROSPECTS below. It is deliberately data, not prose
in a docstring: the markdown in klantkraan/docs/02-sales/outreach-batch-3-*.md is
the human-readable twin and must be kept in step by hand -- if you change a price
or a hook, change it in both, or the doc will quietly disagree with what was sent.

    python -m scripts.outreach_mail            # write build/outreach/*.json
    python -m scripts.outreach_mail --slug meijer --html   # one mail to stdout

Run from the ai-receptionist directory with ./.venv/bin/python.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import mail_layout  # noqa: E402

DEMO = "https://demo.klantkraan.nl/?client="

# The opt-out. A cold mail to a BV is allowed under the opt-out regime, but only if the
# recipient can stop it in one reply -- Telecommunicatiewet art. 11.7. mail_layout's own
# footer carries the KvK and the terms; this is the line it has no room for.
OPT_OUT = 'Geen interesse? Antwoord met "stop" en je hoort niets meer.'

SIGNOFF_NAME = "Davy"
SIGNOFF_EMAIL = "davy@klantkraan.nl"

# What the receptionist does, in one sentence. Three variants, because a dakdekker quotes
# where a loodgieter books, and the review-gap prospects are being sold the review loop.
BOOK = (
    "Daarvoor is Klantkraan gebouwd: een AI-receptionist die 24/7 in het Nederlands "
    "je websitechat en WhatsApp opneemt, vragen beantwoordt en meteen een afspraak inplant."
)
QUOTE = (
    "Daarvoor is Klantkraan gebouwd: een AI-receptionist die 24/7 in het Nederlands "
    "je websitechat en WhatsApp opneemt, vragen beantwoordt en meteen een afspraak of "
    "offerte inplant."
)
REVIEW = (
    "Daarvoor is Klantkraan gebouwd: een AI-receptionist die 24/7 in het Nederlands "
    "je websitechat en WhatsApp opneemt, vragen beantwoordt, meteen een afspraak inplant "
    "en na de klus netjes om een Google-review vraagt."
)

# The oprichtersklant terms, as the reader sees them. One month at half price, plus the
# 6-months-prepaid rung: decided 2026-07-31 on the founder's call (canonical:
# klantkraan/docs/02-sales/founding-member-offer.md). Nothing here promises a cancellation
# term -- that is still undecided, and a cold mail is a bad place to promise something we
# may retract. If a prospect asks, the founder answers.
OFFER_LINES = [
    "Eerste maand €149 in plaats van €299 (excl. btw)",
    "Of 6 maanden vooruit: €894 in plaats van €1.644, oprichterstarief het hele halfjaar",
    "Geen opstartkosten",
    "30 dagen geld-terug, zonder kleine lettertjes",
    "Binnen 48 uur live op je site",
]
OFFER_INTRO = (
    "We nemen een klein aantal oprichtersklanten aan. In ruil vragen we een kort "
    "verhaal zodra hij zich bewezen heeft, zodat de volgende ondernemer weet wat "
    "hij eraan heeft."
)
ASK = "Zal ik 'm voor jullie klaarzetten?"


@dataclass(frozen=True)
class Prospect:
    slug: str  # demo config slug, also the ?client= value
    company: str  # legal-ish name, for the record
    salutation: str  # what the mail calls them
    short: str  # what the demo sentence calls them
    email: str
    pain: str
    product: str


PROSPECTS = [
    Prospect(
        "dak-garantie-amsterdam",
        "Dak Garantie Amsterdam B.V.",
        "Dak Garantie Amsterdam",
        "Dak Garantie Amsterdam",
        "info@dakgarantieamsterdam.nl",
        "Drie vestigingen, één telefoonnummer. Zodra die lijn bezet is, lopen aanvragen "
        "uit meerdere stadsdelen tegelijk mis, zonder dat iemand het merkt.",
        QUOTE,
    ),
    Prospect(
        "md-dak",
        "MD Dak & Klusbedrijf B.V.",
        "MD Dak & Klusbedrijf",
        "MD Dak",
        "info@dakdekkerutrechtbv.nl",
        "Op jullie site staat dag-en-nacht bereikbaarheid, maar zelf een 24/7-lijn "
        "bemannen is duur en zwaar. In de praktijk valt een nachtelijke stormmelding "
        "dan alsnog buiten de boot.",
        QUOTE,
    ),
    Prospect(
        "duckdekker",
        "Duckdekker B.V.",
        "Duckdekker",
        "Duckdekker",
        "info@duckdekker.nl",
        "Jullie sluiten om 17:00, maar stormschade en daklekkages melden zich ook "
        "'s avonds en in het weekend. Zonder opvang gaat die spoedklus naar een "
        "dakdekker die wel opneemt, of je draait er zelf een dure nachtdienst voor.",
        QUOTE,
    ),
    Prospect(
        "aj-dakwerken",
        "AJ Dakwerken B.V.",
        "AJ Dakwerken",
        "AJ Dakwerken",
        "info@ajdakwerken.nl",
        "Met 108 beoordelingen en een eigen showroom hebben jullie flink in acquisitie "
        "geïnvesteerd. Des te zonde als een beller buiten kantooruren geen gehoor krijgt "
        "en alsnog bij de concurrent uitkomt.",
        QUOTE,
    ),
    Prospect(
        "smits-installaties",
        "Smits Installaties B.V.",
        "Smits Installaties",
        "Smits",
        "info@smits-installaties.nl",
        "Klanten die buiten kantooruren bellen moeten bij jullie een apart 088-nummer "
        "onthouden. In de praktijk pakt lang niet iedereen dat, en die beller belt "
        "gewoon de volgende loodgieter.",
        BOOK,
    ),
    Prospect(
        "derwort",
        "Derwort Loodgieters B.V.",
        "Derwort",
        "Derwort",
        "info@derwort.nu",
        "Jullie staan sterk op Google, maar voor spoed na 16:30 is er geen zichtbare "
        "opvang. Een gemiste oproep op vrijdagmiddag is een klant die maandag bij "
        "iemand anders zit.",
        BOOK,
    ),
    Prospect(
        "valkenburg",
        "Andries Valkenburg Loodgieters & Verwarming B.V.",
        "Valkenburg",
        "Valkenburg",
        "info@valkenburgloodgieters.nl",
        "Jullie zijn 's ochtends bereikbaar van negen tot half één. Tussen de middag en "
        "na sluitingstijd loopt een beller vast, en iemand met een lekkage wacht niet "
        "tot morgen.",
        BOOK,
    ),
    Prospect(
        "frauenfelder",
        "Gas en Sanitair Installatie Bureau P.H. Frauenfelder B.V.",
        "Frauenfelder",
        "Frauenfelder",
        "info@phfrauenfelder.nl",
        "Jullie bestaan sinds 1944 en werken voor particulier en zakelijk. Maar wie na "
        "kantoortijd belt, bereikt niemand, en een lekkage wacht niet tot de volgende "
        "ochtend.",
        BOOK,
    ),
    Prospect(
        "w-janssen",
        "Technisch Bureau W. Janssen B.V.",
        "W. Janssen",
        "W. Janssen",
        "info@wjanssen.nl",
        "Bijna 90 jaar loodgieterswerk in Den Haag, en toch krijgt wie na vijven belt "
        "geen gehoor. Op jullie site staat wel een WhatsApp-nummer, maar zonder iemand "
        "die erop reageert blijft dat een dichte deur.",
        BOOK,
    ),
    Prospect(
        "visser-van-der-hell",
        "Visser & Van der Hell Loodgietersbedrijf B.V.",
        "Visser & Van der Hell",
        "Visser & Van der Hell",
        "info@visservanderhell.nl",
        "Een klant die om half zes belt en geen gehoor krijgt, zoekt online verder en "
        "belt de volgende loodgieter. Juist buiten kantooruren, als een lekkage niet "
        "kan wachten, gaat er zo omzet langs je heen.",
        BOOK,
    ),
    Prospect(
        "loodgieter-utrecht-bv",
        "Loodgieter Utrecht B.V.",
        "Loodgieter Utrecht",
        "Loodgieter Utrecht",
        "info@loodgieterutrechtbv.nl",
        "Je belooft klanten dat je direct terugbelt, maar zonder automatische opvolging "
        "valt er op een drukke dag altijd wel een oproep tussen wal en schip. Eén "
        "gemiste beller is zo een misgelopen klus.",
        BOOK,
    ),
    Prospect(
        "vdp-dakbedekking",
        "VDP Dakbedekking B.V.",
        "VDP Dakbedekking",
        "VDP Dakbedekking",
        "info@vdpdakbedekking.nl",
        "Op jullie site staat dat je telefonisch geen offertes opneemt. Maar wie "
        "'s avonds belt na een daklekkage wil juist meteen geholpen worden. Die beller "
        "krijgt nu niets terug en gaat verder zoeken.",
        QUOTE,
    ),
    Prospect(
        "buddingh",
        "Buddingh Dakdekkersbedrijf B.V.",
        "Buddingh",
        "Buddingh",
        "info@buddingh-dak.nl",
        "Veertig jaar dakwerk in Amsterdam, en online staat er alleen een telefoonnummer. "
        "Geen formulier, geen WhatsApp. Wie 's avonds belt en niemand treft, is een "
        "aanvraag die je nooit gezien hebt.",
        REVIEW,
    ),
    Prospect(
        "lohmann",
        "Lohmann Groep B.V.",
        "Lohmann Groep",
        "Lohmann",
        "info@lohmannbv.nl",
        "Jullie zijn 24/7 bereikbaar, maar zonder automatische bevestiging weet je nooit "
        "hoeveel bellers alsnog afhaken. En na een klus blijft de Google-review vaak "
        "liggen, terwijl juist die je de volgende klant oplevert.",
        REVIEW,
    ),
    Prospect(
        "dv-dakdekkers",
        "DV Dakdekkers B.V.",
        "DV Dakdekkers",
        "DV Dakdekkers",
        "info@dvdakdekkers.nl",
        "Een perfecte 5.0 op meer dan vijftig beoordelingen, daar loop je op voor. Toch "
        "draait er een kortingsactie, en die trekt vooral prijskopers. Sneller reageren "
        "op serieuze aanvragen laat je op kwaliteit concurreren in plaats van op prijs.",
        QUOTE,
    ),
    Prospect(
        "dekker",
        "Dekker Installatietechniek B.V.",
        "Dekker Installatietechniek",
        "Dekker",
        "info@dekkerinstallatietechniek.eu",
        "Jullie storingsdienst draait 24/7, maar online is Dekker nauwelijks zichtbaar: "
        "geen WhatsApp, geen online afspraak, weinig beoordelingen. Nieuwe klanten die "
        "vergelijken haken daar stilletjes op af.",
        REVIEW,
    ),
    Prospect(
        "buiteman",
        "Warmtetechnisch Bureau Joop Buiteman B.V.",
        "Buiteman",
        "Buiteman",
        "info@buiteman.nl",
        "Met 36 monteurs op de weg ronden jullie elke dag flink wat klussen af. Zonder "
        "een vast opvolgmoment blijft de Google-review daarna liggen, en dat is precies "
        "wat een nieuwe klant als eerste checkt.",
        REVIEW,
    ),
    Prospect(
        "meijer",
        "Loodgietersbedrijf Meijer B.V.",
        "Loodgietersbedrijf Meijer",
        "Meijer",
        "info@loodgietermeijer.nl",
        "120 jaar vakmanschap en tien monteurs op de weg, en toch staan er maar 23 "
        "beoordelingen op Google. Dat is niet wat jullie waard zijn, en juist die "
        "eerste indruk is waar een nieuwe klant op afgaat.",
        REVIEW,
    ),
    Prospect(
        "herfst",
        "Herfst B.V.",
        "Herfst",
        "Herfst",
        "info@herfstbv.nl",
        "Met veertien man en meer dan vijftig jaar vakwerk hoort daar een sterkere "
        "online reputatie bij dan er nu te zien is. Elke tevreden klant die geen "
        "beoordeling achterlaat, is een gemiste kans om de volgende binnen te halen.",
        REVIEW,
    ),
    Prospect(
        "van-der-herp",
        "Loodgieters- en Installatiebedrijf W.J. van der Herp B.V.",
        "Van der Herp",
        "Van der Herp",
        "info@vanderherp.nl",
        "Ruim 75 jaar vakmanschap sinds 1946, en online staan er 24 beoordelingen. Dat "
        "doet jullie staat van dienst tekort. En wie na kantoortijd belt krijgt geen "
        "gehoor, terwijl de spoedklus dan juist binnenkomt.",
        REVIEW,
    ),
    Prospect(
        "barendse",
        "A. Barendse & Zn. B.V.",
        "Barendse",
        "Barendse",
        "info@barendseleiden.nl",
        "Op Google staan er 11 beoordelingen op jullie naam, terwijl Barendse al 65 jaar "
        "tevreden klanten heeft. Al die stille tevreden klanten leveren nu geen nieuwe op.",
        REVIEW,
    ),
    Prospect(
        "verkuylen",
        "T.I.B. Verkuylen bv",
        "Verkuylen",
        "Verkuylen",
        "info@tib-verkuylen.nl",
        "Al meer dan 55 jaar actief in Leiden, en online staan er negen beoordelingen. "
        "Dat weerspiegelt jullie vakmanschap niet. En wie na half vijf belt, krijgt "
        "geen gehoor.",
        REVIEW,
    ),
    Prospect(
        "van-der-wiel",
        "L van der Wiel b.v.",
        "Van der Wiel",
        "Van der Wiel",
        "info@lvanderwielbv.nl",
        "Meer dan 60 jaar loodgieterswerk in Den Haag, en toch staan er online maar een "
        "handvol beoordelingen. Dat doet je vakmanschap tekort, want juist die reviews "
        "leveren de volgende klant op.",
        REVIEW,
    ),
    # Added 2026-08-08. One entry for two entiteiten (Bol B.V. Installatietechniek +
    # Vermeulen B.V. Loodgietersbedrijf, KvK 29051477/29051479): zelfde kantoor, zelfde
    # site, zelfde eigenaar -- twee mails zou dubbel mailen zijn. Adres staat op hun
    # eigen contactpagina (bol-vermeulen.nl/contact, gelezen 2026-08-08).
    Prospect(
        "bol-vermeulen",
        "Bol B.V. Installatietechniek / Vermeulen B.V. Loodgietersbedrijf",
        "Bol & Vermeulen",
        "Bol & Vermeulen",
        "opdrachten@bol-vermeulen.nl",
        "Twee bedrijven, twee telefoonnummers, één kantoor in Gouda. Wie 's avonds een "
        "cv-storing of lekkage heeft, vindt op jullie site een formulier - en belt "
        "ondertussen gewoon de volgende.",
        BOOK,
    ),
]


def subject_for(p: Prospect) -> str:
    return f"Een AI-receptionist voor {p.salutation}, al klaargezet"


def blocks_for(p: Prospect) -> list[mail_layout.Block]:
    """The mail as blocks. Prose first, then the demo, then the numbers boxed off, then
    one ask. The offer is a Panel rather than a paragraph because it is what the reader
    scrolls back to before replying."""
    return [
        mail_layout.Para(f"Beste team van {p.salutation},"),
        mail_layout.Para(p.pain),
        mail_layout.Para(p.product),
        mail_layout.Para(
            f"Ik heb er alvast een voor {p.short} klaargezet, met jullie diensten erin. "
            "Stel 'm gerust een lastige vraag, hij houdt stand."
        ),
        mail_layout.Button(f"Probeer de receptionist van {p.short}", f"{DEMO}{p.slug}"),
        mail_layout.Heading("Als oprichtersklant"),
        mail_layout.Para(OFFER_INTRO),
        mail_layout.Panel(OFFER_LINES),
        mail_layout.Para(ASK),
        mail_layout.Signoff(SIGNOFF_NAME, SIGNOFF_EMAIL),
    ]


def render(p: Prospect) -> dict[str, str]:
    blocks = blocks_for(p)
    return {
        "slug": p.slug,
        "to": p.email,
        "subject": subject_for(p),
        "text": mail_layout.to_text(blocks, footer_note=OPT_OUT),
        "html": mail_layout.to_html(
            blocks,
            subject=subject_for(p),
            preheader=f"Ik heb er alvast een voor {p.short} klaargezet.",
            footer_note=OPT_OUT,
        ),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--slug", help="render one prospect to stdout instead of writing files")
    ap.add_argument("--html", action="store_true", help="with --slug, print HTML not text")
    ap.add_argument("--out", default="build/outreach", help="output directory")
    args = ap.parse_args()

    by_slug = {p.slug: p for p in PROSPECTS}

    if args.slug:
        if args.slug not in by_slug:
            sys.exit(f"unknown slug: {args.slug} (have {', '.join(sorted(by_slug))})")
        mail = render(by_slug[args.slug])
        print(mail["html"] if args.html else mail["text"])
        return

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    mails = [render(p) for p in PROSPECTS]
    (out / "batch3.json").write_text(json.dumps(mails, ensure_ascii=False, indent=2))
    for mail in mails:
        (out / f"{mail['slug']}.html").write_text(mail["html"])
    print(f"{len(mails)} mails -> {out}/batch3.json (+ one .html each)")


if __name__ == "__main__":
    main()
