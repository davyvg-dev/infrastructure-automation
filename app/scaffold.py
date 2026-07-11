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

# Home-services (plumbing/heating) template — the niche you're starting with. Tweak the
# defaults here once and every scaffolded prospect inherits them.
_TEMPLATE: dict = {
    "business": {
        "name": "",  # filled from the prospect name
        "type": "plumbing & heating company",
        "timezone": "Europe/Amsterdam",
        "phone": "+31 20 000 0000",
        "address": "Amsterdam & surrounding areas",
    },
    "persona": {
        "name": "Sam",
        "tone": (
            "Friendly, calm, and quick — like a helpful person at the front desk. Short "
            "sentences. Reassuring for urgent problems (a leak, no heating). Confirms "
            "details back."
        ),
        "goals": (
            "1) Answer the caller's question. 2) If they need a visit, find a time and book "
            "it. 3) Capture the caller's name, a phone number, and a short description of the "
            "problem before booking. 4) Treat major leaks or no-heat-in-winter as "
            "emergencies and offer the soonest slot."
        ),
        "guardrails": (
            "Only book slots the check_availability tool returns. Never quote exact repair "
            "prices beyond the services list — give the call-out/inspection price and say "
            "the engineer confirms on site. Never give DIY safety advice for gas or "
            "electrical work; advise booking or calling instead. When booking, set the "
            "service to a short description of the job (e.g. 'Emergency: no hot water'). Keep "
            "replies short."
        ),
    },
    "services": [
        {"name": "Emergency call-out", "price": "from €90", "duration_min": 60},
        {"name": "Boiler service", "price": "€120", "duration_min": 60},
        {"name": "Leak / repair visit", "price": "from €75", "duration_min": 60},
        {"name": "Quote / inspection", "price": "free", "duration_min": 30},
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
         "a": "Yes — we keep emergency call-out slots each day. I can check the soonest time."},
        {"q": "Do you charge a call-out fee?",
         "a": "Emergency call-outs start from €90; quotes and inspections are free."},
        {"q": "What areas do you cover?", "a": "We cover Amsterdam and the surrounding areas."},
        {"q": "How soon can someone come out?",
         "a": "It depends on the day — I can check today's availability right now."},
    ],
    "greeting": "",  # generated from name + persona
    "model": {"id": "claude-opus-4-8", "effort": "low"},
}


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "prospect"


def _greeting(business_name: str, persona_name: str) -> str:
    return (
        f"Hi! I'm {persona_name} at {business_name}. I can answer questions or book you a "
        "visit — including emergencies. What do you need?"
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
    parser.add_argument("--type", help="Business type (default: plumbing & heating company).")
    parser.add_argument("--phone")
    parser.add_argument("--address")
    parser.add_argument("--timezone")
    parser.add_argument("--persona", help="Receptionist name (default: Sam).")
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
