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
import json
import re
import sys
from copy import deepcopy
from pathlib import Path

import yaml

from . import extract
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
    # What the business takes on, beyond the priced services below — so the receptionist says
    # "ja, dat doen we" to any in-scope job, not just the listed line items. Tune per prospect;
    # if removed, scope falls back to business.type. Never a place for prices (books an offerte).
    "scope": {
        "does": (
            "Alle installatie-, cv-, sanitair- en loodgieterswerk: cv-ketels plaatsen, "
            "onderhouden en repareren, warm water en verwarming, radiatoren en vloerverwarming, "
            "kranen, toiletten, leidingwerk, lekkages en verstoppingen — particulier en zakelijk."
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

# English/international template (positioning is now any-business, any-language — the first real
# client is an English/German airco company on Mallorca). Same shape as the Dutch template, but
# the locked parts — persona tone/goals/guardrails, greeting, FAQ — are English and the defaults
# are generic-service, not trade-specific. `type`/`services` are meant to be overridden per
# prospect. The art. 50 disclosure ("digital assistant") stays in the greeting.
_EN_TEMPLATE: dict = {
    "locale": "en",  # widget UI chrome in English
    "business": {
        "name": "",
        "type": "service business",
        "timezone": "Europe/Amsterdam",
        "phone": "+00 000 000 000",
        "address": "your service area",
    },
    "persona": {
        "name": "Robin",
        "tone": (
            "You speak English; switch to another language only if the customer writes in it. "
            "Friendly, calm, and quick, like a helpful person at the front desk. Short sentences. "
            "Reassuring in an emergency. Always confirm details back."
        ),
        "goals": (
            "1) Answer the customer's question. 2) If they want an appointment, find a time and "
            "book it. 3) Before booking, capture the customer's name, phone number, and a short "
            "description of the job. 4) Treat urgent problems as a priority and offer the soonest "
            "slot."
        ),
        "guardrails": (
            "Only book times that check_availability returns. Do not quote exact prices beyond the "
            "service list — give the starting or call-out fee and say the engineer confirms it on "
            "site. Never give DIY advice for gas, electrical, or other unsafe work; advise booking "
            "or calling instead. When booking, set a short description of the job as the service "
            "(e.g. 'Emergency: no hot water'). Keep replies short. You are a digital assistant and "
            "never pretend to be human; say so honestly if anyone asks."
        ),
    },
    "scope": {
        "does": (
            "The core services this business offers to private and commercial customers, including "
            "urgent call-outs during opening hours and, where offered, after hours."
        ),
    },
    "services": [
        {"name": "Emergency call-out", "price": "call-out fee applies, confirmed on site", "duration_min": 60},
        {"name": "Standard service visit", "price": "confirmed on site", "duration_min": 60},
        {"name": "Repair / breakdown visit", "price": "confirmed on site", "duration_min": 60},
        {"name": "Quote / site survey", "price": "free", "duration_min": 30},
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
        {"q": "Do you handle emergencies?",
         "a": "Yes — we keep room each day for urgent jobs. I can check the soonest time for you right now."},
        {"q": "Which areas do you cover?",
         "a": "We cover the local area and around it. Tell me your town and I'll check it's within our range."},
        {"q": "How soon can someone come?",
         "a": "It depends on the day — I can check availability for you now."},
        {"q": "What does a visit cost?",
         "a": "A call-out fee applies and the engineer confirms the exact price on site; a quote or survey is free. I can book you in whenever suits."},
    ],
    "greeting": "",  # generated from name + persona
    "model": {"id": "claude-opus-4-8", "effort": "low"},
}

# Template registry, keyed by language. build_config() selects on `lang`; unknown langs fall back
# to the Dutch template (the historical default, so existing callers are unaffected).
_TEMPLATES: dict[str, dict] = {"nl": _TEMPLATE, "en": _EN_TEMPLATE}


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "prospect"


def _greeting(business_name: str, persona_name: str) -> str:
    # "digitale receptionist" stays in every greeting: EU AI Act art. 50 disclosure.
    return (
        f"Goedendag! Ik ben {persona_name}, de digitale receptionist van {business_name}. "
        "Ik beantwoord uw vragen en plan direct een afspraak in — ook bij spoed. Waarmee "
        "kan ik u helpen?"
    )


def _greeting_en(business_name: str, persona_name: str) -> str:
    # "digital assistant" stays in every greeting: EU AI Act art. 50 disclosure.
    return (
        f"Hi, I'm {persona_name}, the digital assistant at {business_name}. I can answer your "
        "questions and book you an appointment, including urgent jobs. How can I help?"
    )


def build_config(name: str, lang: str = "nl", **over: str | None) -> dict:
    template = _TEMPLATES.get(lang, _TEMPLATE)
    cfg = deepcopy(template)
    cfg["business"]["name"] = name
    for field in ("type", "phone", "address", "timezone"):
        if over.get(field):
            cfg["business"][field] = over[field]
    if over.get("persona"):
        cfg["persona"]["name"] = over["persona"]
    greet = _greeting_en if lang == "en" else _greeting
    cfg["greeting"] = greet(name, cfg["persona"]["name"])
    _fit_scope_to_type(cfg, template["business"]["type"])
    return cfg


def _fit_scope_to_type(cfg: dict, default_type: str) -> None:
    """The template's curated `scope` describes its default trade. If the type has been changed to
    another trade, that scope no longer fits (a painter doesn't fit cv-ketels), so drop it — the
    receptionist then derives scope from business.type until the founder curates it."""
    if cfg.get("business", {}).get("type") != default_type:
        cfg.pop("scope", None)


# --- draft from a scraped extraction (app.extract) ---------------------------------------

_WEEK = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
_TIME_RE = re.compile(r"^\d{2}:\d{2}$")

# The template FAQ carries example euro amounts — safe as a demo, unsafe on a real prospect draft
# where a wrong price would be quoted. A from-json draft gets this price-free FAQ instead; the
# founder adds real answers during the confirm-in-chat step.
_PRICE_FREE_FAQ = [
    {"q": "Doen jullie spoedklussen?",
     "a": "Ja — we houden elke dag ruimte vrij voor spoed. Ik kan direct de eerstvolgende tijd voor u nakijken."},
    {"q": "In welke regio werken jullie?",
     "a": "We werken in de regio en omgeving. Geef uw plaats door, dan kijk ik of het binnen ons gebied valt."},
    {"q": "Hoe snel kan er iemand komen?",
     "a": "Dat hangt van de dag af — ik kan nu de beschikbaarheid voor u nakijken."},
]


def _cited(field: object) -> str | None:
    """A cited scalar's value, or None if it carries no verbatim snippet (uncited => dropped)."""
    if isinstance(field, dict):
        value, snippet = str(field.get("value", "")).strip(), str(field.get("snippet", "")).strip()
        if value and snippet:
            return value
    return None


def merge_extraction(name: str, extraction: dict, **over: str | None) -> dict:
    """Overlay an app.extract extraction onto the template: cited values win, uncited ones fall
    back to safe defaults, and NO price is ever inferred — every service is stamped `PRIJS?` for
    the founder to fill in. greeting / persona / guardrails / model stay template-owned."""
    cfg = build_config(name, **over)  # locked greeting/persona/guardrails/model + safe defaults

    if not over.get("type"):
        bt = _cited(extraction.get("business_type"))
        if bt:
            cfg["business"]["type"] = bt
            # a scraped type may not match the template's installateur scope
            _fit_scope_to_type(cfg, _TEMPLATE["business"]["type"])
    if not over.get("phone"):
        phone = _cited(extraction.get("phone"))
        if phone:
            cfg["business"]["phone"] = phone
    if not over.get("address"):
        region = _cited(extraction.get("region"))
        if region:
            cfg["business"]["address"] = region

    services = []
    for svc in extraction.get("services") or []:
        snippet = str(svc.get("snippet", "")).strip()
        svc_name = str(svc.get("name", "")).strip()
        if not (snippet and svc_name):
            continue  # citation-or-drop
        category = svc.get("category") or "overig"
        services.append(
            {"name": svc_name, "price": "PRIJS?", "duration_min": extract._duration(category)}
        )
    if services:
        cfg["services"] = services
    else:
        # No grounded services: keep the generic template set, but still price-free.
        for svc in cfg["services"]:
            svc["price"] = "PRIJS?"

    hours = {}
    for day, block in (extraction.get("hours") or {}).items():
        if day not in _WEEK or not isinstance(block, dict):
            continue
        if not str(block.get("snippet", "")).strip():
            continue
        opens, closes = str(block.get("open", "")).strip(), str(block.get("close", "")).strip()
        if _TIME_RE.match(opens) and _TIME_RE.match(closes):
            hours[day] = [opens, closes]
    if hours:
        cfg["hours"] = hours

    cfg["faq"] = deepcopy(_PRICE_FREE_FAQ)
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
    parser.add_argument("--lang", default="nl", choices=("nl", "en"),
                        help="Template language (default nl). --from-json is Dutch-only.")
    parser.add_argument("--from-json", dest="from_json",
                        help="An app.extract extraction JSON; merges cited values over the template.")
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

    over = dict(
        type=args.type, phone=args.phone, address=args.address,
        timezone=args.timezone, persona=args.persona,
    )
    if args.from_json:
        try:
            extraction = json.loads(Path(args.from_json).read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            parser.error(f"could not read extraction JSON {args.from_json!r}: {exc}")
        cfg = merge_extraction(name, extraction, **over)
    else:
        cfg = build_config(name, lang=args.lang, **over)
    write_config(cfg, path)

    rel = path.relative_to(ROOT)
    print(f"✅ Wrote {rel}")
    print("\nNext:")
    if args.from_json:
        print(f"  1. Open {rel} and fill in every 'PRIJS?' — prices are never scraped. Check the")
        print("     scraped services / hours / region too.")
    else:
        print(f"  1. Open {rel} and edit services / hours / FAQ to match the prospect.")
    print("  2. Run their branded demo:")
    print(f"       BUSINESS_CONFIG={rel} python -m app.server")
    print("     then open http://127.0.0.1:8000")
    print("  3. Record a 30-sec booking clip for your Loom / to send them.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
