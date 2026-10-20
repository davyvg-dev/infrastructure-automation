"""RDW kenteken lookup: normalization, parsing, and per-tenant tool gating. Offline —
the RDW endpoint is mocked, no network."""

from __future__ import annotations

import io
import json

import pytest

from app import rdw, settings, tools


def test_normalize_strips_dashes_spaces_and_case():
    assert rdw.normalize("g-393-gh") == "G393GH"
    assert rdw.normalize(" AB 123 c ") == "AB123C"
    assert rdw.normalize("12-ABC-3") == "12ABC3"


def test_invalid_plate_never_hits_the_network():
    assert rdw.lookup("") == {"found": False, "error": "invalid_kenteken"}
    assert rdw.lookup("!!")["found"] is False


def _fake_urlopen(rows):
    def fake(url, timeout=0):
        return io.BytesIO(json.dumps(rows).encode())

    return fake


def test_lookup_returns_car_and_apk_date(monkeypatch):
    monkeypatch.setattr(
        rdw.urllib.request,
        "urlopen",
        _fake_urlopen(
            [
                {
                    "kenteken": "G393GH",
                    "merk": "SEAT",
                    "handelsbenaming": "MII",
                    "eerste_kleur": "ZWART",
                    "datum_eerste_toelating": "20190712",
                    "vervaldatum_apk": "20280318",
                    "voertuigsoort": "Personenauto",
                }
            ]
        ),
    )
    result = rdw.lookup("g-393-gh")
    assert result["found"] is True
    assert result["merk"] == "SEAT"
    assert result["model"] == "MII"
    assert result["bouwjaar"] == "2019"
    assert result["apk_vervaldatum"] == "2028-03-18"


def test_lookup_empty_response_is_not_found(monkeypatch):
    monkeypatch.setattr(rdw.urllib.request, "urlopen", _fake_urlopen([]))
    assert rdw.lookup("XX999X") == {"found": False, "kenteken": "XX999X"}


@pytest.fixture
def dhz():
    token = settings.use_slug("dhz-autoservice")
    yield
    settings.clear_slug(token)


def test_garage_config_gets_the_kenteken_tool(dhz):
    names = [t["name"] for t in tools.for_business()]
    assert "lookup_kenteken" in names
    assert "search_listings" not in names


def test_default_config_has_no_kenteken_tool():
    assert "lookup_kenteken" not in [t["name"] for t in tools.for_business()]


def test_execute_routes_to_rdw(dhz, monkeypatch):
    monkeypatch.setattr(rdw, "lookup", lambda plate: {"found": False, "kenteken": plate})
    out = json.loads(tools.execute("lookup_kenteken", {"kenteken": "AB-123-C"}))
    assert out == {"found": False, "kenteken": "AB-123-C"}
