"""Spin up a branded demo config for a prospect in ~60 seconds.

    python -m app.scaffold "Their Business Name"
    python -m app.scaffold "Jansen Loodgieters" --phone "+31 20 555 0199" --address "Utrecht"

Writes config/<slug>.yaml from a home-services template (your chosen niche), prefilled with
sensible defaults you tweak to match the prospect (pull services/hours from their website or
Google Business Profile). Then it prints the exact command to run their branded demo.

Run with no name on a terminal and it'll prompt you interactively.
"""

from __future__ import annotations

import argparse
import re
import sys
from copy import deepcopy
from pathlib import Path

import yaml

from .settings import ROOT

CONFIG_DIR = ROOT / "config"

# Dutch trades template (Klantkraan's niche). Customer-facing text is Dutch (repo style
# rule); tweak the defaults here once and every scaffolded prospect inherits them.
_TEMPLATE: dict = {
    "business": {
        "name": "",  # filled from the prospect name
        "type": "installatiebedrijf (cv, sanitair, lekkages)",
        "timezone": "Europe/Amsterdam",
        "phone": "+31 20 000 0000",
        "address": "Amsterdam en omgeving",
    },
    "persona": {
        "name": "Fleur",
        "tone": (
            "Je spreekt Nederlands; schakel alleen naar Engels als de klant in het Engels "
            "schrijft. Vriendelijk, rustig en snel — als een behulpzame collega aan de balie. "
            "Korte zinnen. Geruststellend bij spoed (een lekkage, geen verwarming). Bevestig "
            "details altijd terug."
        ),
        "goals": (
            "1) Beantwoord de vraag van de klant. 2) Wil de klant een afspraak, zoek dan een "
            "tijd en plan die in. 3) Vraag vóór het boeken om naam, telefoonnummer en een "
            "korte omschrijving van het probleem. 4) Behandel grote lekkages of geen "
            "verwarming in de winter als spoed en bied het eerstvolgende slot aan."
        ),
        "guardrails": (
            "Boek alleen tijden die check_availability teruggeeft. Noem geen exacte "
            "reparatieprijzen buiten de dienstenlijst — noem het starttarief en zeg dat de "
            "monteur het op locatie bevestigt. Geef nooit doe-het-zelfadvies voor gas- of "
            "elektrawerk; adviseer een afspraak of bellen. Zet bij het boeken een korte "
            "omschrijving van de klus als service (bijv. 'Spoed: geen warm water'). Houd "
            "antwoorden kort. Je bent een digitale assistent en doet je nooit voor als mens."
        ),
    },
    "services": [
        {"name": "Spoedservice (lekkage / storing)", "price": "vanaf €90", "duration_min": 60},
        {"name": "Cv-ketel onderhoud", "price": "€120", "duration_min": 60},
        {"name": "Reparatie / lekkage-afspraak", "price": "vanaf €75", "duration_min": 60},
        {"name": "Offerte / inspectie", "price": "gratis", "duration_min": 30},
    ],
    "hours": {
        "monday": ["08:00", "18:00"],
        "tuesday": ["08:00", "18:00"],
        "wednesday": ["08:00", "18:00"],
        "thursday": ["08:00", "18:00"],
        "friday": ["08:00", "18:00"],
        "saturday": ["09:00", "13:00"],
    },
    "booking": {"slot_minutes": 60, "horizon_days": 14},
    "faq": [
        {"q": "Doen jullie spoedklussen?",
         "a": "Ja — we houden elke dag spoedslots vrij. Ik kan direct de eerstvolgende tijd voor u nakijken."},
        {"q": "Rekenen jullie voorrijkosten?",
         "a": "Spoedservice vanaf €90; offertes en inspecties zijn gratis."},
        {"q": "In welke regio werken jullie?", "a": "We werken in de regio en omgeving."},
        {"q": "Hoe snel kan er iemand komen?",
         "a": "Dat hangt van de dag af — ik kan nu de beschikbaarheid voor u nakijken."},
    ],
    "greeting": "",  # generated from name + persona
    "model": {"id": "claude-opus-4-8", "effort": "low"},
}


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "prospect"


def _greeting(business_name: str, persona_name: str) -> str:
    # "digitale receptionist" stays in every greeting: EU AI Act art. 50 disclosure.
    return (
        f"Goedendag! Ik ben {persona_name}, de digitale receptionist van {business_name}. "
        "Ik beantwoord uw vragen en plan direct een afspraak in — ook bij spoed. Waarmee "
        "kan ik u helpen?"
    )


def build_config(name: str, **over: str | None) -> dict:
    cfg = deepcopy(_TEMPLATE)
    cfg["business"]["name"] = name
    for field in ("type", "phone", "address", "timezone"):
        if over.get(field):
            cfg["business"][field] = over[field]
    if over.get("persona"):
        cfg["persona"]["name"] = over["persona"]
    cfg["greeting"] = _greeting(name, cfg["persona"]["name"])
    return cfg


def write_config(cfg: dict, path: Path) -> None:
    rel = path.relative_to(ROOT)
    header = (
        f"# Demo config for {cfg['business']['name']}. Tweak services/hours/FAQ to match\n"
        f"# their real business (pull from their website / Google profile), then run:\n"
        f"#   BUSINESS_CONFIG={rel} python -m app.server\n\n"
    )
    with path.open("w", encoding="utf-8") as fh:
        fh.write(header)
        yaml.safe_dump(cfg, fh, sort_keys=False, allow_unicode=True, width=100)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="app.scaffold", description="Scaffold a prospect demo config.")
    parser.add_argument("name", nargs="?", help="The prospect's business name.")
    parser.add_argument("--type", help="Business type (default: installatiebedrijf).")
    parser.add_argument("--phone")
    parser.add_argument("--address")
    parser.add_argument("--timezone")
    parser.add_argument("--persona", help="Receptionist name (default: Fleur).")
    parser.add_argument("--force", action="store_true", help="Overwrite if the config exists.")
    args = parser.parse_args(argv[1:])

    name = args.name
    if not name and sys.stdin.isatty():
        name = input("Prospect business name: ").strip()
    if not name:
        parser.error("a business name is required (positional arg or interactive prompt)")

    path = CONFIG_DIR / f"{slug(name)}.yaml"
    if path.exists() and not args.force:
        print(f"⚠️  {path.relative_to(ROOT)} already exists. Use --force to overwrite.")
        return 1

    cfg = build_config(
        name, type=args.type, phone=args.phone, address=args.address,
        timezone=args.timezone, persona=args.persona,
    )
    write_config(cfg, path)

    rel = path.relative_to(ROOT)
    print(f"✅ Wrote {rel}")
    print("\nNext:")
    print(f"  1. Open {rel} and edit services / hours / FAQ to match the prospect.")
    print(f"  2. Run their branded demo:")
    print(f"       BUSINESS_CONFIG={rel} python -m app.server")
    print("     then open http://127.0.0.1:8000")
    print("  3. Record a 30-sec booking clip for your Loom / to send them.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
