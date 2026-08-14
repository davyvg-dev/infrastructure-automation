"""Turn a scraped prospect into a proposal website config (client-sites `modus: preview`).

    python -m app.sitedraft "Jansen Loodgieters" --url https://jansen-loodgieters.nl --near Utrecht
    python -m app.sitedraft "Jansen Loodgieters" --from-json extraction.json --slug jansen

Writes `klantkraan/apps/client-sites/clients/<slug>/client.yaml`, which the founder then builds
with `CLIENT=<slug> pnpm build`. This is the bridge the pilot kit was missing: `extract.py`
already gathers cited facts about a prospect for the receptionist demo, and roughly two thirds
of a client.yaml is the same data in Dutch keys.

Division of labour, on purpose:
  * mechanical fields (telefoon, openingstijden) are mapped in code from the extraction, so a
    wrong phone number can only come from a wrong source, never from a model;
  * copy fields (vak, plaats, werkgebied, dienstomschrijvingen, usps, spoedtekst) come from one
    Claude call constrained by a schema, grounded in the same sources, and told to paraphrase.

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

from . import extract, settings

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

# Brand defaults for a proposal: a neutral dark blue that carries white text (the client-sites
# schema enforces WCAG contrast >= 4.5:1) plus a warm accent. Override with --kleur/--accent
# once the prospect's own colours are known.
DEFAULT_PRIMARY = "#1f3a5f"
DEFAULT_ACCENT = "#c2703d"

_HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
_TIME_RE = re.compile(r"^\d{2}:\d{2}$")

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
        "werkgebied": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 5},
        "diensten": {
            "type": "array",
            "minItems": 3,
            "maxItems": 8,
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
        "usps": {"type": "array", "items": {"type": "string"}, "minItems": 2, "maxItems": 4},
        "spoed_beschikbaar": {"type": "boolean"},
        "spoed_tekst": {"type": "string"},
    },
    "required": ["vak", "plaats", "werkgebied", "diensten", "usps", "spoed_beschikbaar", "spoed_tekst"],
}

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
    "5. `usps` alleen als ze uit de bronnen blijken. Kun je er maar twee onderbouwen, geef er dan "
    "twee. Geen lege beloftes zoals 'de beste van de regio'.\n"
    "6. `spoed_beschikbaar` alleen true als de bronnen spoed, 24/7 of storingsdienst noemen; is "
    "dat niet zo, zet hem op false en schrijf in `spoed_tekst` alleen hoe men contact opneemt.\n"
    "7. `omschrijving` is een of twee zinnen over wat de dienst voor de klant oplost.\n"
    "8. `werkgebied`: alleen plaatsen die in de bronnen staan, maximaal vijf, `plaats` als eerste."
)


class DraftError(RuntimeError):
    """Raised when the prospect cannot be turned into a config without guessing."""


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


def check_primary(hex_color: str) -> str:
    hex_color = check_colour(hex_color)
    if _contrast_with_white(hex_color) < 4.5:
        raise DraftError(
            f"kleur_primair {hex_color} is te licht voor witte tekst (WCAG contrast >= 4.5:1); "
            "kies een donkerder variant van de merkkleur"
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


def build_config(
    name: str,
    extraction: dict,
    draft: dict,
    *,
    telefoon: str | None = None,
    kleur_primair: str = DEFAULT_PRIMARY,
    kleur_accent: str = DEFAULT_ACCENT,
) -> dict:
    """Assemble the client.yaml body. Preview-only: no legal identifiers are invented."""
    phone_raw = telefoon or (extraction.get("phone") or {}).get("value") or ""
    uren = openingstijden(extraction.get("hours") or {})
    if not uren:
        raise DraftError(
            "geen openingstijden gevonden in de bronnen; vul ze na het genereren met de hand aan "
            "(de site toont anders alleen 'Gesloten')"
        )

    plaats = draft["plaats"].strip()
    werkgebied = [p.strip() for p in draft["werkgebied"] if p.strip()]
    if plaats not in werkgebied:
        werkgebied.insert(0, plaats)

    return {
        "modus": "preview",
        "bedrijf": {
            "naam": name,
            "vak": draft["vak"].strip().lower(),
            "telefoon": nl_phone(phone_raw),
            "adres": {"plaats": plaats},
            "werkgebied": werkgebied[:5],
        },
        "branding": {
            "kleur_primair": check_primary(kleur_primair),
            "kleur_accent": check_colour(kleur_accent),
        },
        "diensten": [
            {"naam": d["naam"].strip(), "omschrijving": d["omschrijving"].strip()}
            for d in draft["diensten"]
        ],
        "openingstijden": uren,
        "spoed": {
            "beschikbaar": bool(draft["spoed_beschikbaar"]),
            "tekst": draft["spoed_tekst"].strip(),
        },
        "usps": [u.strip() for u in draft["usps"]],
        # A proposal never claims the receptionist and never republishes their reviews.
        "receptionist": False,
    }


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


def dump_config(config: dict) -> str:
    return yaml.dump(
        config, Dumper=_Dumper, allow_unicode=True, sort_keys=False, default_flow_style=False
    )


def write_config(slug: str, config: dict, out_dir: Path | None = None) -> Path:
    root = out_dir or CLIENTS_DIR
    target = root / slug
    path = target / "client.yaml"
    if path.exists():
        raise DraftError(f"{path} bestaat al; verwijder hem of kies een andere --slug")
    target.mkdir(parents=True, exist_ok=True)
    path.write_text(_HEADER + "\n" + dump_config(config), encoding="utf-8")
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

        draft = draft_copy(args.name, extraction, sources)
        config = build_config(
            args.name,
            extraction,
            draft,
            telefoon=args.telefoon,
            kleur_primair=args.kleur,
            kleur_accent=args.accent,
        )
        slug = args.slug or slugify(args.name)
        path = write_config(slug, config, Path(args.out_dir) if args.out_dir else None)
    except DraftError as err:
        print(f"❌ {err}", file=sys.stderr)
        return 1

    print(f"✅ Wrote {path}")
    print("\nControleer telefoon, plaats en diensten met eigen ogen. Daarna:")
    print(f"  cd klantkraan/apps/client-sites && CLIENT={slug} pnpm build")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
