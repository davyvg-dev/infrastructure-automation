"""RDW license-plate lookup against the open-data vehicle register (no API key).

The unique key for a garage customer is the kenteken: one lookup identifies the exact
car (make, model, colour, build year) and — gold for a garage — when its APK expires.
Only offered to businesses whose config sets `kenteken_lookup: true`.
"""

from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from typing import Any

RDW_URL = "https://opendata.rdw.nl/resource/m9d7-ebf2.json"


def normalize(kenteken: str) -> str:
    """'g-393-gh' / 'G 393 GH' -> 'G393GH' — the register stores plates bare and uppercase."""
    return re.sub(r"[^A-Z0-9]", "", (kenteken or "").upper())


def _date(raw: str) -> str:
    """RDW dates come as 'YYYYMMDD'; return 'YYYY-MM-DD' (or the raw value if malformed)."""
    return f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}" if raw and len(raw) == 8 and raw.isdigit() else raw


def lookup(kenteken: str) -> dict[str, Any]:
    plate = normalize(kenteken)
    if not 4 <= len(plate) <= 8:
        return {"found": False, "error": "invalid_kenteken"}
    query = urllib.parse.urlencode({"kenteken": plate})
    with urllib.request.urlopen(f"{RDW_URL}?{query}", timeout=10) as resp:
        rows = json.load(resp)
    if not rows:
        return {"found": False, "kenteken": plate}
    row = rows[0]
    toelating = _date(row.get("datum_eerste_toelating", ""))
    return {
        "found": True,
        "kenteken": plate,
        "merk": row.get("merk", ""),
        "model": row.get("handelsbenaming", ""),
        "kleur": row.get("eerste_kleur", ""),
        "bouwjaar": toelating[:4],
        "apk_vervaldatum": _date(row.get("vervaldatum_apk", "")),
        "voertuigsoort": row.get("voertuigsoort", ""),
    }
