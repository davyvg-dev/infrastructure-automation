"""Lead schema v1 + temperature scoring in the listings store. Offline, no network."""

from __future__ import annotations

import json

import pytest

from app import lead_score, listings_store, notify, settings, tools


@pytest.fixture
def solvista(data_dir, monkeypatch):
    """Activate the real solvista-demo config against a throwaway DATA_DIR and capture
    Telegram pings instead of sending them. Yields the list of (text, chat_id) pings."""
    token = settings.use_slug("solvista-demo")
    pings: list[tuple[str, str | None]] = []
    monkeypatch.setattr(
        notify, "owner", lambda text, chat_id=None: pings.append((text, chat_id)) or True
    )
    yield pings
    settings.clear_slug(token)


def _saved_leads(data_dir):
    path = data_dir / "listing-leads-solvista-demo.jsonl"
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh]


# --- 0.2 temperature rules: table-driven, all four intents ---------------------------------

CASES = [
    # buyer: 0-3 + concrete (locations AND max_price) = hot
    ({"intent": "buyer", "timeline": "0-3", "locations": ["Estepona"], "max_price": 250000}, "hot"),
    # buyer: 0-3 but vague = warm
    ({"intent": "buyer", "timeline": "0-3"}, "warm"),
    ({"intent": "buyer", "timeline": "3-12", "locations": ["Mijas"], "max_price": 300000}, "warm"),
    ({"intent": "buyer", "timeline": "12+", "locations": ["Mijas"], "max_price": 300000}, "nurture"),
    ({"intent": "buyer", "timeline": "browsing"}, "nurture"),
    ({"intent": "buyer"}, "nurture"),  # no timeline given -> never page a human
    # seller: valuation booked = hot regardless of timeline
    ({"intent": "seller", "valuation_booked": True}, "hot"),
    ({"intent": "seller", "timeline": "0-3", "property_address": "Calle Mar 3, Estepona"}, "hot"),
    ({"intent": "seller", "timeline": "0-3"}, "warm"),  # no address yet = not concrete
    ({"intent": "seller", "timeline": "3-12"}, "warm"),
    ({"intent": "seller"}, "nurture"),
    # renter: same ladder as buyer
    ({"intent": "renter", "timeline": "0-3", "locations": ["Fuengirola"], "max_price": 1600}, "hot"),
    ({"intent": "renter", "timeline": "3-12"}, "warm"),
    # existing client: service request, warm by definition
    ({"intent": "existing"}, "warm"),
    ({"intent": "existing", "timeline": "0-3"}, "warm"),
    # malformed input degrades toward nurture, never hot
    ({"intent": "astronaut", "timeline": "yesterday"}, "nurture"),
    ({}, "nurture"),
]


@pytest.mark.parametrize("criteria,expected", CASES)
def test_temperature_table(criteria, expected):
    assert lead_score.temperature(criteria) == expected


def test_intent_falls_back_on_operation():
    assert lead_score.resolve_intent({"operation": "sale"}) == "buyer"
    assert lead_score.resolve_intent({"operation": "rent"}) == "renter"
    assert lead_score.resolve_intent({}) == "buyer"
    assert lead_score.resolve_intent({"intent": "seller", "operation": "sale"}) == "seller"


# --- 0.1 lead schema v1: one persisted lead per intent type --------------------------------

LEADS = [
    (
        "buyer",
        "hot",
        {
            "intent": "buyer",
            "operation": "sale",
            "locations": ["Estepona"],
            "max_price": 250000,
            "min_bedrooms": 2,
            "timeline": "0-3",
            "financing": "mortgage_arranged",
            "language": "en",
        },
    ),
    (
        "seller",
        "hot",
        {
            "intent": "seller",
            "property_address": "Calle del Mar 3, Estepona",
            "valuation_booked": True,
            "timeline": "3-12",
            "language": "es",
        },
    ),
    (
        "renter",
        "warm",
        {
            "intent": "renter",
            "operation": "rent",
            "locations": ["Fuengirola"],
            "max_price": 1600,
            "timeline": "3-12",
            "language": "de",
        },
    ),
    ("existing", "warm", {"intent": "existing", "language": "en"}),
]


@pytest.mark.parametrize("intent,expected_temp,criteria", LEADS)
def test_register_lead_persists_schema_v1(solvista, data_dir, intent, expected_temp, criteria):
    result = listings_store.register_lead(
        customer_name=f"Test {intent.title()}",
        contact="+34600111222",
        criteria=criteria,
        references=["SV-1001"] if intent == "buyer" else [],
        notes="pytest lead",
    )
    assert result["ok"] and result["saved"] and result["notified"]

    (record,) = _saved_leads(data_dir)
    assert record["intent"] == intent
    assert record["temperature"] == expected_temp
    assert record["criteria"] == criteria
    assert record["client"] == "solvista-demo"
    assert len(solvista) == 1  # exactly one agent ping per lead
    ping_text = solvista[0][0]
    assert f"{expected_temp.upper()} {intent} lead" in ping_text  # triage-ready ping


def test_execute_flows_new_fields_into_criteria(solvista, data_dir):
    """The tools.execute exclusion tuple must keep letting schema fields through."""
    tools.execute(
        "register_buyer_lead",
        {
            "customer_name": "Flow Test",
            "contact": "flow@example.com",
            "intent": "seller",
            "timeline": "0-3",
            "financing": "cash",
            "property_address": "Av. Litoral 12, Marbella",
            "valuation_booked": True,
            "notes": "wants a quick sale",
        },
    )
    (record,) = _saved_leads(data_dir)
    assert record["intent"] == "seller"
    assert record["temperature"] == "hot"
    for key in ("timeline", "financing", "property_address", "valuation_booked"):
        assert key in record["criteria"], key
    assert record["notes"] == "wants a quick sale"
