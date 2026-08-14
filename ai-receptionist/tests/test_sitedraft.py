"""sitedraft: extraction -> client-sites proposal config. Offline — the Claude call is never
made; `draft_copy` is the only thing that talks to the API and it is not exercised here."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from app import sitedraft
from app.sitedraft import DraftError

EXTRACTION = {
    "business_type": {"value": "loodgieter", "snippet": "Uw loodgieter in Zeist"},
    "phone": {"value": "030 - 123 45 67", "snippet": "Bel 030 - 123 45 67"},
    "region": {"value": "Zeist en omgeving", "snippet": "werkzaam in Zeist en omgeving"},
    "services": [
        {"name": "Lekkage", "category": "lekkage-reparatie", "snippet": "lekkages", "confidence": "high"},
    ],
    "hours": {
        "monday": {"open": "08:00", "close": "17:00", "snippet": "ma 8-17"},
        "saturday": {"open": "09:00", "close": "13:00", "snippet": "za 9-13"},
        "sunday": {"open": "", "close": "", "snippet": ""},
    },
}

DRAFT = {
    "vak": "Loodgieter",
    "plaats": "Zeist",
    "werkgebied": ["Zeist", "Utrecht", "De Bilt"],
    "diensten": [
        {"naam": "Lekkage verhelpen", "omschrijving": "Wij sporen de lekkage op en dichten hem."},
        {"naam": "Ontstoppen", "omschrijving": "Een verstopte afvoer weer laten doorstromen."},
        {"naam": "Sanitair", "omschrijving": "Kraan of toilet vervangen en netjes aansluiten."},
    ],
    "usps": ["Vaste prijs vooraf", "Eigen monteurs"],
    "spoed_beschikbaar": True,
    "spoed_tekst": "Bij een lekkage komen wij dezelfde dag langs.",
}


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("030 - 123 45 67", "+31 301234567"),
        ("06 12345678", "+31 612345678"),
        ("0031612345678", "+31 612345678"),
        ("+31 (0)10 1234567", "+31 101234567"),
    ],
)
def test_nl_phone_normalises_scraped_shapes(raw: str, expected: str) -> None:
    assert sitedraft.nl_phone(raw) == expected


def test_nl_phone_refuses_rather_than_guesses() -> None:
    with pytest.raises(DraftError):
        sitedraft.nl_phone("bel ons")


def test_openingstijden_maps_days_and_drops_the_uncited_ones() -> None:
    uren = sitedraft.openingstijden(EXTRACTION["hours"])
    assert uren == {"maandag": ["08:00", "17:00"], "zaterdag": ["09:00", "13:00"]}
    assert "zondag" not in uren  # empty times are absent, not rendered as 00:00


def test_build_config_is_a_proposal_and_invents_nothing() -> None:
    config = sitedraft.build_config("Jansen Loodgieters", EXTRACTION, DRAFT)
    assert config["modus"] == "preview"
    assert config["receptionist"] is False
    # The fields a proposal must not carry: legal identifiers, a domain, reviews, prices.
    assert set(config["bedrijf"]) == {"naam", "vak", "telefoon", "adres", "werkgebied"}
    assert "domein" not in config
    assert "reviews" not in config
    assert config["bedrijf"]["vak"] == "loodgieter"
    assert config["bedrijf"]["telefoon"] == "+31 301234567"
    assert config["bedrijf"]["adres"] == {"plaats": "Zeist"}


def test_build_config_caps_werkgebied_and_keeps_the_home_town_first() -> None:
    draft = {**DRAFT, "plaats": "Bunnik", "werkgebied": ["A", "B", "C", "D", "E"]}
    config = sitedraft.build_config("X BV", EXTRACTION, draft)
    assert config["bedrijf"]["werkgebied"] == ["Bunnik", "A", "B", "C", "D"]


def test_build_config_refuses_a_site_without_hours() -> None:
    with pytest.raises(DraftError, match="openingstijden"):
        sitedraft.build_config("X BV", {**EXTRACTION, "hours": {}}, DRAFT)


def test_build_config_refuses_a_brand_colour_white_text_cannot_sit_on() -> None:
    with pytest.raises(DraftError, match="te licht"):
        sitedraft.build_config("X BV", EXTRACTION, DRAFT, kleur_primair="#ffe08a")


def test_slugify() -> None:
    assert sitedraft.slugify("Jansen Loodgieters B.V.") == "jansen-loodgieters-b-v"
    with pytest.raises(DraftError):
        sitedraft.slugify("!!!")


def test_write_config_round_trips_and_never_overwrites(tmp_path: Path) -> None:
    config = sitedraft.build_config("Jansen Loodgieters", EXTRACTION, DRAFT)
    path = sitedraft.write_config("jansen", config, tmp_path)
    assert path == tmp_path / "jansen" / "client.yaml"

    body = path.read_text(encoding="utf-8")
    assert body.startswith("# VOORSTEL-config")
    assert yaml.safe_load(body) == config
    # Times and the phone number are quoted: unquoted "17:00" is 1020 under YAML 1.1, and the
    # site build must never receive a number where it expects text.
    assert "'17:00'" in body and "'08:00'" in body
    assert "'+31 301234567'" in body

    with pytest.raises(DraftError, match="bestaat al"):
        sitedraft.write_config("jansen", config, tmp_path)
