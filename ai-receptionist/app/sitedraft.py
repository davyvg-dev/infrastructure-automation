"""Turn a scraped prospect into a proposal website config (client-sites `modus: preview`).

    python -m app.sitedraft "Jansen Loodgieters" --url https://jansen-loodgieters.nl --near Utrecht
    python -m app.sitedraft "Jansen Loodgieters" --from-json extraction.json --slug jansen
    python -m app.sitedraft "Jansen Loodgieters" --url https://... --voorbeeld https://zecc.nl

Writes `klantkraan/apps/client-sites/clients/<slug>/client.yaml`, which the founder then builds
with `CLIENT=<slug> pnpm build`. This is the bridge the pilot kit was missing: `extract.py`
already gathers cited facts about a prospect for the receptionist demo, and roughly two thirds
of a client.yaml is the same data in Dutch keys.

Division of labour, on purpose:
  * mechanical fields (telefoon, openingstijden) are mapped in code from the extraction, so a
    wrong phone number can only come from a wrong source, never from a model;
  * copy fields (vak, plaats, werkgebied, dienstomschrijvingen, usps, spoedtekst) come from one
    Claude call constrained by a schema, grounded in the same sources, and told to paraphrase;
  * the skin comes from `app.sitestyle`, off the `--voorbeeld` sites when the founder has one
    to point at and composed from the vak, the name and the colours when he has not. Every
    proposal gets one: two voorstellen sent in the same week that are recognisably the same
    document is the defect section R exists to fix.

Three invariants, enforced here and again by the Zod schema on the other side:
  1. ALWAYS `modus: preview`. A scraped config is a proposal, never a live client site: no KvK,
     no btw-id, no eigen domein, no receptionist claim.
  2. NO PRICES. `extract.py`'s schema has no price field and the draft schema below has none
     either; the site template refuses to render prices at all.
  3. NO REVIEWS and no photos. A prospect's reviews and work photos are not ours to republish;
     the template's colour-block fallback covers the missing photos.

Docs fetched via the claude-api skill (2026-08-14): structured outputs through
`output_config.format`, adaptive thinking (`budget_tokens` is rejected on current models).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import anthropic
import yaml

from . import extract, settings, sitestyle

# Drafting Dutch marketing copy from cited snippets wants deliberate reasoning; effort is set
# a notch below extraction because the schema does most of the constraining here.
_MODEL = {"id": "claude-opus-5", "effort": "high"}

# Where the client-sites app looks for configs (klantkraan/apps/client-sites/clients/<slug>/).
CLIENTS_DIR = settings.ROOT.parent / "klantkraan" / "apps" / "client-sites" / "clients"

_DAY_NL = {
    "monday": "maandag",
    "tuesday": "dinsdag",
    "wednesday": "woensdag",
    "thursday": "donderdag",
    "friday": "vrijdag",
    "saturday": "zaterdag",
    "sunday": "zondag",
}

# Brand defaults for a proposal: a neutral dark blue that carries white text and can itself
# be read as text on the pages' own surfaces (the client-sites schema enforces WCAG contrast
# with white >= 5.25:1, mirrored below in _MIN_CONTRAST) plus a warm accent. Override with
# --kleur/--accent once the prospect's own colours are known.
DEFAULT_PRIMARY = "#1f3a5f"
DEFAULT_ACCENT = "#c2703d"

_HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
_TIME_RE = re.compile(r"^\d{2}:\d{2}$")

# Array counts live in the prompt and in build_config, never here. Structured outputs reject
# `maxItems` outright ("property 'maxItems' is not supported") and accept `minItems` only as 0
# or 1 ("'minItems' values other than 0 or 1 are not supported"), both with a 400 — probed
# against claude-opus-5 on 2026-08-14, so only werkgebied's minItems 1 survives. The Zod schema
# on the client-sites side is the real gate (werkgebied 1-5, diensten 3-8, usps 2-4);
# build_config truncates to those ceilings and refuses anything under the floors, so a model
# that miscounts costs a dropped item or a clear Dutch error, never a broken build.
_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        # Lowercase singular Dutch trade noun; the template writes "Uw <vak> in <plaats>".
        "vak": {"type": "string"},
        # The town the business is based in, as a bare name ("Zeist", not "Zeist en omgeving").
        "plaats": {"type": "string"},
        # 1-5 towns actually named in the sources. The template renders one page per town and
        # Google's doorway-page rules punish more than a handful of near-identical local pages.
        "werkgebied": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        "diensten": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "naam": {"type": "string"},
                    "omschrijving": {"type": "string"},
                },
                "required": ["naam", "omschrijving"],
            },
        },
        "usps": {"type": "array", "items": {"type": "string"}},
        "spoed_beschikbaar": {"type": "boolean"},
        "spoed_tekst": {"type": "string"},
        # The sentences that used to belong to the template and now belong to the business.
        #
        # Until 2026-08-16 the copy around the diensten came from one of two fixed registers
        # in client-sites/src/lib/toon.ts, so every mobiel voorstel said the same ~15
        # sentences with the nouns swapped: two prospects, different vakken, different towns,
        # shared a 40-word identical passage. These eight fields are what makes two
        # voorstellen two businesses. Not required: each one falls back to the register when
        # the sources say nothing worth writing, which is the honest outcome for a thin
        # prospect and a great deal better than an invented story.
        "kop": {"type": "string"},
        "belofte": {"type": "string"},
        "intro_kop": {"type": "string"},
        "werkwijze": {"type": "string"},
        "bereik": {"type": "string"},
        "diensten_tekst": {"type": "string"},
        "slot_kop": {"type": "string"},
        "slot_tekst": {"type": "string"},
    },
    "required": ["vak", "plaats", "werkgebied", "diensten", "usps", "spoed_beschikbaar", "spoed_tekst"],
}

# The `teksten:` keys, in the order a reader meets them on the page. Order matters: the
# founder reads the block as copy before he sends the voorstel, and a headline sitting under
# a closing line reads as a mistake in the tool.
_TEKST_VELDEN = (
    "kop",
    "belofte",
    "intro_kop",
    "werkwijze",
    "bereik",
    "diensten_tekst",
    "slot_kop",
    "slot_tekst",
)

_SYSTEM = (
    "Je schrijft de Nederlandse tekst voor een voorstel-website van een vakbedrijf (loodgieter, "
    "dakdekker, installateur, elektricien). De site wordt gemaakt op basis van openbare bronnen, "
    "voordat het bedrijf klant is, dus alles wat je schrijft moet uit de bronnen te herleiden "
    "zijn.\n\n"
    "Harde regels:\n"
    "1. Gebruik ALLEEN de bronnen. Verzin geen diensten, geen werkgebied, geen certificeringen, "
    "geen jaartallen, geen garanties en geen bedrijfsgeschiedenis.\n"
    "2. Schrijf in het Nederlands, in de u-vorm, als een professionele copywriter. Korte zinnen. "
    "Geen uitroeptekens, geen gedachtestreepjes, geen emoji, geen marketingsuperlatieven.\n"
    "3. NOOIT prijzen, tarieven, voorrijkosten of bedragen. Ook geen percentages of statistieken.\n"
    "4. Herschrijf in je eigen woorden. Neem nooit meer dan zes woorden achter elkaar letterlijk "
    "over uit een bron: de tekst van de prospect is niet van ons.\n"
    "5. `usps` alleen als ze uit de bronnen blijken: minimaal twee, maximaal vier. Kun je er maar "
    "twee onderbouwen, geef er dan twee. Geen lege beloftes zoals 'de beste van de regio'.\n"
    "6. `spoed_beschikbaar` alleen true als de bronnen spoed, 24/7 of storingsdienst noemen; is "
    "dat niet zo, zet hem op false en schrijf in `spoed_tekst` alleen hoe men contact opneemt.\n"
    "7. `diensten`: minimaal drie, maximaal acht. `omschrijving` is een of twee zinnen over wat "
    "de dienst voor de klant oplost.\n"
    "8. `werkgebied`: alleen plaatsen die in de bronnen staan, maximaal vijf, `plaats` als eerste.\n"
    "9. De acht tekstvelden (`kop`, `belofte`, `intro_kop`, `werkwijze`, `bereik`, "
    "`diensten_tekst`, `slot_kop`, `slot_tekst`) zijn de zinnen op de pagina zelf. Zonder "
    "die velden krijgt elk bedrijf dezelfde standaardzinnen, dus schrijf ze alsof je ze voor "
    "dit ene bedrijf schrijft:\n"
    "   - `kop` is de H1, de grootste tekst op het scherm. Noem het vak en waar ze zitten, of "
    "iets concreets wat dit bedrijf doet. Nooit de bedrijfsnaam zelf: die staat al in de "
    "kop van de pagina.\n"
    "   - `belofte` is een zin onder de kop over wat de klant krijgt als hij belt.\n"
    "   - `intro_kop` en `werkwijze` gaan over hoe zij werken. Wees specifiek over dit vak: "
    "een dak beoordeel je niet vanaf de stoep, een verstopping zit zelden waar je hem "
    "verwacht. Zulke zinnen kan geen ander bedrijf overnemen.\n"
    "   - `bereik` zegt waar zij werken of waar hun klanten vandaan komen.\n"
    "   - `slot_kop` en `slot_tekst` sluiten de pagina af met de reden om te bellen.\n"
    "   Geen opsomming van drie ('van X en Y tot Z'), geen drie bijvoeglijke naamwoorden "
    "achter elkaar, en niet elke kop een zelfstandig naamwoord van twee woorden: dat is "
    "precies hoe automatisch gegenereerde tekst eruitziet. Laat een veld leeg als de bronnen "
    "je niets geven om over te schrijven; een weggelaten zin valt terug op een nette "
    "standaardzin en dat is beter dan een verzonnen verhaal.\n"
    "10. Rijdt dit bedrijf naar de klant, of komt de klant naar hen toe? Bij een winkel, "
    "salon of praktijk (kapper, tandarts, trimsalon, garage) mag geen enkele zin beloven dat "
    "jullie langskomen, en gebruik dan ook geen bouwwoorden als 'klus', 'offerte' of "
    "'oplevering'."
)


class DraftError(RuntimeError):
    """Raised when the prospect cannot be turned into a config without guessing."""


# Hours are the one required field no model may invent: without GOOGLE_PLACES_API_KEY they can
# only come from the prospect's own site, and plenty of trade sites never publish them. main()
# checks this before paying for the copy call, so a prospect that cannot work costs a second
# instead of a minute.
NO_HOURS = (
    "geen openingstijden gevonden in de bronnen; er is niets geschreven. Zet de openingstijden "
    "in een extraction-JSON (app.extract -o) en draai opnieuw met --from-json, of maak deze "
    "prospect met de hand (de site toont anders alleen 'Gesloten')"
)


# --- deterministic mapping ---------------------------------------------------------------


def slugify(name: str) -> str:
    """Business name -> clients/<slug> directory name."""
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    if not slug:
        raise DraftError(f"kan geen slug maken van {name!r}; geef er een op met --slug")
    return slug[:63].rstrip("-")


def nl_phone(raw: str) -> str:
    """Normalise a scraped Dutch number to the +31 form the site schema requires.

    Accepts the shapes that actually turn up on trade websites: "010 - 123 45 67",
    "06 12345678", "0031612345678", "+31 (0)10 1234567".
    """
    digits = re.sub(r"\D", "", raw or "")
    if digits.startswith("0031"):
        digits = digits[4:]
    elif digits.startswith("31") and len(digits) > 10:
        digits = digits[2:]
    digits = digits.lstrip("0")
    if len(digits) != 9:
        raise DraftError(
            f"telefoonnummer {raw!r} levert geen 9 nationale cijfers op; controleer de bron of "
            "geef het nummer mee met --telefoon"
        )
    return f"+31 {digits}"


def openingstijden(hours: dict) -> dict[str, list[str]]:
    """Extraction hours (english keys, cited) -> the site's Dutch openingstijden block.

    Days that were not found are simply absent, which the template renders as "Gesloten".
    """
    out: dict[str, list[str]] = {}
    for eng, nl in _DAY_NL.items():
        block = (hours or {}).get(eng)
        if not isinstance(block, dict):
            continue
        opens, closes = block.get("open", ""), block.get("close", "")
        if _TIME_RE.match(opens or "") and _TIME_RE.match(closes or ""):
            out[nl] = [opens, closes]
    return out


def _contrast_with_white(hex_color: str) -> float:
    """Mirror of the client-sites WCAG check, so a bad --kleur fails here and not at build."""

    def channel(c: int) -> float:
        s = c / 255
        return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4

    n = int(hex_color[1:], 16)
    lum = (
        0.2126 * channel((n >> 16) & 0xFF)
        + 0.7152 * channel((n >> 8) & 0xFF)
        + 0.0722 * channel(n & 0xFF)
    )
    return 1.05 / (lum + 0.05)


def check_colour(hex_color: str) -> str:
    if not _HEX_RE.match(hex_color or ""):
        raise DraftError(f"kleur {hex_color!r} moet een #rrggbb hex-waarde zijn")
    return hex_color.lower()


# Must equal MIN_CONTRAST_WITH_WHITE in klantkraan/apps/client-sites/src/lib/client.ts.
# This gate runs BEFORE the paid draft call and the Zod schema runs at build; if the two
# ever disagree, a voorstel pays for a draft that the build then refuses -- which is the
# whole reason the colour check sits this early. 5.25 rather than 4.5 because the brand
# colour is also text on paper, card and the tinted bands, not only white-on-brand.
_MIN_CONTRAST = 5.25


def check_primary(hex_color: str) -> str:
    hex_color = check_colour(hex_color)
    if _contrast_with_white(hex_color) < _MIN_CONTRAST:
        raise DraftError(
            f"kleur_primair {hex_color} is te licht: hij moet witte tekst dragen en zelf als "
            f"tekst op papier en getinte banden staan (WCAG contrast met wit >= "
            f"{_MIN_CONTRAST}:1); kies een donkerder variant van de merkkleur"
        )
    return hex_color


# --- drafting -----------------------------------------------------------------------------


def _user_message(name: str, extraction: dict, sources: dict[str, str]) -> str:
    blocks = [f"Bedrijfsnaam: {name}", ""]
    for label, text in sources.items():
        blocks.append(f"--- BRON: {label} ---\n{text}\n")
    blocks.append("--- EERDER GEEXTRAHEERDE FEITEN (met citaten) ---")
    blocks.append(json.dumps(extraction, ensure_ascii=False, indent=2))
    blocks.append(
        "\nSchrijf de sitetekst volgens het schema. Alles moet in de bronnen of de geciteerde "
        "feiten terug te vinden zijn. Geen prijzen, geen verzonnen claims."
    )
    return "\n".join(blocks)


def draft_copy(name: str, extraction: dict, sources: dict[str, str]) -> dict:
    """One schema-constrained Claude call for the fields that are copy, not data."""
    settings.env("ANTHROPIC_API_KEY")
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=_MODEL["id"],
        max_tokens=16000,
        thinking={"type": "adaptive"},
        output_config={
            "effort": _MODEL["effort"],
            "format": {"type": "json_schema", "schema": _SCHEMA},
        },
        system=_SYSTEM,
        messages=[{"role": "user", "content": _user_message(name, extraction, sources)}],
    )
    if response.stop_reason == "refusal":
        raise DraftError("Claude weigerde deze prospect te verwerken; doe deze site met de hand.")
    text = next((b.text for b in response.content if b.type == "text"), "")
    return json.loads(text)


def vak_van(draft: dict) -> str:
    """The trade as the site writes it. Read in two places -- the config and the skin -- and
    the composer's answer changes with it, so it is normalised once."""
    return draft["vak"].strip().lower()


def _teksten_van(draft: dict) -> dict:
    """The `teksten:` block, in page order, with the empty ones left out.

    The model is told to skip a field it has nothing to say about, and it takes that offer
    often on a thin prospect. Dropping the empties here rather than in the template keeps the
    fallback in one place: an absent key means the register sentence, and there is no second
    kind of absence to reason about.
    """
    return {
        veld: draft[veld].strip()
        for veld in _TEKST_VELDEN
        if isinstance(draft.get(veld), str) and draft[veld].strip()
    }


def build_config(
    name: str,
    extraction: dict,
    draft: dict,
    *,
    telefoon: str | None = None,
    kleur_primair: str = DEFAULT_PRIMARY,
    kleur_accent: str = DEFAULT_ACCENT,
    stijl: dict | None = None,
) -> dict:
    """Assemble the client.yaml body. Preview-only: no legal identifiers are invented."""
    phone_raw = telefoon or (extraction.get("phone") or {}).get("value") or ""
    uren = openingstijden(extraction.get("hours") or {})
    if not uren:
        raise DraftError(NO_HOURS)

    plaats = draft["plaats"].strip()
    werkgebied = [p.strip() for p in draft["werkgebied"] if p.strip()]
    if plaats not in werkgebied:
        werkgebied.insert(0, plaats)

    # The schema cannot carry these floors (see _SCHEMA), so catch a thin draft here rather
    # than writing a yaml the client-sites build will reject with a Zod error.
    for veld, minimum in (("diensten", 3), ("usps", 2)):
        if len(draft[veld]) < minimum:
            raise DraftError(
                f"de bronnen leverden maar {len(draft[veld])} {veld} op (minimaal {minimum} "
                f"nodig); vul {veld} met de hand aan of doe deze prospect handmatig"
            )

    return {
        "modus": "preview",
        "bedrijf": {
            "naam": name,
            "vak": vak_van(draft),
            "telefoon": nl_phone(phone_raw),
            "adres": {"plaats": plaats},
            "werkgebied": werkgebied[:5],
        },
        "branding": {
            "kleur_primair": check_primary(kleur_primair),
            "kleur_accent": check_colour(kleur_accent),
        },
        # Right after branding because that is what it is: the skin the colours sit in.
        # Absent means the pre-vocabulary look, which is a valid config, not a broken one.
        **({"stijl": stijl} if stijl else {}),
        # Only the fields the model actually filled. An empty string is not a sentence, and
        # writing one would override the register default with nothing -- the site would
        # render a blank heading and pass every gate, because every gate here checks that
        # copy is absent-or-legal, not that it is present.
        **({"teksten": teksten} if (teksten := _teksten_van(draft)) else {}),
        "diensten": [
            {"naam": d["naam"].strip(), "omschrijving": d["omschrijving"].strip()}
            for d in draft["diensten"][:8]
        ],
        "openingstijden": uren,
        "spoed": {
            "beschikbaar": bool(draft["spoed_beschikbaar"]),
            "tekst": draft["spoed_tekst"].strip(),
        },
        "usps": [u.strip() for u in draft["usps"][:4]],
        # A proposal never claims the receptionist and never republishes their reviews.
        "receptionist": False,
    }


def choose_stijl(
    name: str,
    vak: str,
    voorbeelden: list[dict],
    *,
    kleur_primair: str,
    kleur_accent: str,
) -> dict:
    """The skin for this proposal: read off the reference sites, or composed when there are
    none. Returns sitestyle's answer whole -- the axes go into the yaml as data, the reasons
    above them as comments.

    Never a fallback to the default look. Two voorstellen sent in the same week that are
    recognisably the same document is the defect section R exists to fix, and a factory that
    composes only when asked will be asked on the first prospect and never again.
    """
    if voorbeelden:
        return sitestyle.map_to_stijl(voorbeelden, vak, name)
    return sitestyle.compose_stijl(vak, name, kleur_primair, kleur_accent)


_HEADER = """\
# VOORSTEL-config, automatisch opgebouwd uit openbare bronnen door `python -m app.sitedraft`.
# Nog GEEN klant: modus preview betekent noindex, geen KvK/btw-id, geen eigen domein en een
# banner die Klantkraan als afzender noemt.
#
# Controleer voor het versturen ALTIJD met eigen ogen:
#   - telefoonnummer en plaats (een fout nummer op een lead-site is de duurste fout die er is)
#   - diensten en openingstijden tegen de site van de prospect
#   - of de teksten kloppen met wat dit bedrijf echt doet
# Daarna: cd klantkraan/apps/client-sites && CLIENT=<slug> pnpm build
"""


class _Dumper(yaml.SafeDumper):
    """Quotes the scalars a second YAML parser could read as something other than text."""


def _quoted_when_ambiguous(dumper: yaml.SafeDumper, value: str) -> yaml.ScalarNode:
    # "17:00" is a sexagesimal integer under YAML 1.1 and a string under 1.2; a phone number
    # starts with '+'. Quote both rather than depend on which spec the reader implements.
    style = "'" if _TIME_RE.match(value) or value.startswith("+") else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", value, style=style)


_Dumper.add_representer(str, _quoted_when_ambiguous)


def _dump(fragment: dict) -> str:
    return yaml.dump(
        fragment, Dumper=_Dumper, allow_unicode=True, sort_keys=False, default_flow_style=False
    )


def dump_config(config: dict, stijl_blok: str | None = None) -> str:
    """The config as yaml, one top-level key at a time.

    Dumped per key rather than in one go so that `stijl:` can be written by sitestyle
    instead, which puts the reason for each choice in a comment above it. yaml.dump cannot
    carry a comment, and a skin whose reasoning the founder cannot read is one he cannot
    judge before the voorstel goes out. Every top-level key dumps the same at indent 0
    either way, so a config without a block is byte-for-byte what it was before.
    """
    chunks = [
        stijl_blok.rstrip("\n")
        if key == "stijl" and stijl_blok
        else _dump({key: value}).rstrip("\n")
        for key, value in config.items()
    ]
    return "\n".join(chunks) + "\n"


def write_config(
    slug: str, config: dict, out_dir: Path | None = None, stijl_blok: str | None = None
) -> Path:
    root = out_dir or CLIENTS_DIR
    target = root / slug
    path = target / "client.yaml"
    if path.exists():
        raise DraftError(f"{path} bestaat al; verwijder hem of kies een andere --slug")
    target.mkdir(parents=True, exist_ok=True)
    path.write_text(_HEADER + "\n" + dump_config(config, stijl_blok), encoding="utf-8")
    return path


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="app.sitedraft",
        description="Scrape a prospect and write a client-sites proposal config (modus: preview).",
    )
    parser.add_argument("name", help="The prospect's business name, as it should appear on the site.")
    parser.add_argument("--url", help="The prospect's website (homepage).")
    parser.add_argument("--near", help="Town/city to disambiguate the Google Maps lookup.")
    parser.add_argument("--from-json", help="Reuse an extraction JSON from `app.extract -o`.")
    parser.add_argument("--slug", help="Directory name under clients/ (default: from the name).")
    parser.add_argument("--telefoon", help="Override the scraped phone number.")
    parser.add_argument("--kleur", default=DEFAULT_PRIMARY, help="Brand colour (#rrggbb).")
    parser.add_argument("--accent", default=DEFAULT_ACCENT, help="Accent colour (#rrggbb).")
    parser.add_argument(
        "--voorbeeld",
        action="append",
        default=[],
        metavar="URL",
        help="A website whose look this proposal should take (skin only). Repeatable. "
        "Without one the skin is composed from the vak, the name and the colours.",
    )
    parser.add_argument("--out-dir", help="Write under this dir instead of the client-sites app.")
    args = parser.parse_args(argv[1:])

    try:
        if args.from_json:
            extraction = json.loads(Path(args.from_json).read_text(encoding="utf-8"))
            sources = extract.gather_sources(args.name, args.url, args.near) if args.url else {}
        else:
            if not args.url:
                raise DraftError("geef --url (of --from-json); zonder bron valt er niets te maken.")
            sources = extract.gather_sources(args.name, args.url, args.near)
            if not sources:
                raise DraftError(
                    f"geen bruikbare bronnen gevonden voor {args.name!r}; deze prospect kan niet "
                    "automatisch, doe hem met de hand of sla hem over."
                )
            extraction = extract.extract(args.name, url=args.url, near=args.near)

        if not (extraction.get("services") or sources):
            raise DraftError("de extractie bevat geen diensten en er zijn geen bronnen; stoppen.")
        # Before the copy call, not after: build_config would raise the same error a minute and
        # one Opus request later, having written nothing either way.
        if not openingstijden(extraction.get("hours") or {}):
            raise DraftError(NO_HOURS)
        # Both gates below are free and both guard paid calls, same reason as the hours.
        # The colours because the composer is handed them and would reject a typo as a
        # warning, after which build_config would reject it again as an error; and the
        # references because a mistyped --voorbeeld should cost a second, not an Opus request.
        check_primary(args.kleur)
        check_colour(args.accent)
        voorbeelden = sitestyle.measure_all(args.voorbeeld) if args.voorbeeld else []

        draft = draft_copy(args.name, extraction, sources)
        try:
            stijl = choose_stijl(
                args.name,
                vak_van(draft),
                voorbeelden,
                kleur_primair=args.kleur,
                kleur_accent=args.accent,
            )
        except sitestyle.StyleError as err:
            # The copy call is paid for by now. A voorstel in the default look is worth more
            # than a run thrown away, so write it and say what to run to give it a skin.
            print(f"⚠️  stijl overgeslagen: {err}", file=sys.stderr)
            stijl = None

        config = build_config(
            args.name,
            extraction,
            draft,
            telefoon=args.telefoon,
            kleur_primair=args.kleur,
            kleur_accent=args.accent,
            stijl=sitestyle.keuzes(stijl) if stijl else None,
        )
        slug = args.slug or slugify(args.name)
        path = write_config(
            slug,
            config,
            Path(args.out_dir) if args.out_dir else None,
            stijl_blok=sitestyle.as_yaml(stijl) if stijl else None,
        )
    except (DraftError, sitestyle.StyleError) as err:
        print(f"❌ {err}", file=sys.stderr)
        return 1

    print(f"✅ Wrote {path}")
    if stijl is None:
        print("\nDeze site heeft nog geen eigen stijl. Haal er een op met:")
        print(
            f"  python -m app.sitestyle --vak {config['bedrijf']['vak']} "
            f'--naam "{args.name}" --kleur {args.kleur} --accent {args.accent}'
        )
        print("en plak het blok in de client.yaml.")
    print("\nControleer telefoon, plaats en diensten met eigen ogen. Daarna:")
    print(f"  cd klantkraan/apps/client-sites && CLIENT={slug} pnpm build")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
