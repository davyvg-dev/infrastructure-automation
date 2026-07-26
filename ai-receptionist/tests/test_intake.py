"""Scrape -> draft merge: a price is structurally un-extractable, uncited data is dropped,
the art. 50 disclosure survives. Offline.
"""

from __future__ import annotations

import json

from app import extract, scaffold

# A cited service + an uncited one; a cited phone + an uncited region; a cited day + a blank one.
_FIXTURE = {
    "business_type": {"value": "loodgieter", "snippet": "Loodgietersbedrijf in Utrecht"},
    "phone": {"value": "+31 30 123 4567", "snippet": "Bel ons: 030 123 4567"},
    "region": {"value": "", "snippet": ""},
    "services": [
        {"name": "Lekkage verhelpen", "category": "lekkage-reparatie",
         "snippet": "lekkage snel verholpen", "confidence": "high"},
        {"name": "Verzonnen dienst", "category": "overig",
         "snippet": "", "confidence": "low"},
    ],
    "hours": {
        "monday": {"open": "08:00", "close": "17:00", "snippet": "ma 08:00-17:00"},
        "sunday": {"open": "", "close": "", "snippet": ""},
    },
}


def test_extraction_schema_has_no_price_field():
    # Structural, not prompt-based: a price simply cannot be extracted.
    blob = json.dumps(extract._SCHEMA).lower()
    assert "price" not in blob and "prijs" not in blob and "tarief" not in blob


def test_merge_never_infers_a_price():
    cfg = scaffold.merge_extraction("Testbedrijf Utrecht", _FIXTURE)
    assert all(s.get("price") == "PRIJS?" for s in cfg["services"])
    blob = json.dumps(cfg["services"], ensure_ascii=False).lower()
    assert "€" not in blob and "eur" not in blob


def test_merge_drops_uncited_keeps_cited():
    cfg = scaffold.merge_extraction("Testbedrijf Utrecht", _FIXTURE)
    names = [s["name"] for s in cfg["services"]]
    assert "Verzonnen dienst" not in names
    assert "Lekkage verhelpen" in names
    assert cfg["business"]["phone"] == "+31 30 123 4567"
    assert cfg["business"]["address"], "uncited region should fall back to a safe default, not blank"
    assert cfg["hours"] == {"monday": ["08:00", "17:00"]}


def test_merge_keeps_art50_disclosure():
    cfg = scaffold.merge_extraction("Testbedrijf Utrecht", _FIXTURE)
    assert "digitale receptionist" in cfg["greeting"]
