"""POST /api/checkout: the marketing site's buy path. Offline — Mollie and Telegram are
stubbed, leads land in a throwaway data dir. The contract under test: the lead ALWAYS
persists first, and Mollie trouble degrades to checkout_url=None, never to a lost lead."""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from app import billing, notify, server

_BUYER = {
    "naam": "Jan de Vries",
    "bedrijf": "De Vries Installatietechniek BV",
    "telefoon": "+31 6 1234 5678",
    "email": "jan@devries.nl",
    "vak": "installateur",
    "plan": "chat",
    "bericht": "Graag deze week starten.",
}

_CHECKOUT_URL = "https://www.mollie.com/checkout/select-method/abc123"


@pytest.fixture
def sent(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    captured: list[str] = []
    monkeypatch.setattr(
        notify, "owner", lambda text, chat_id=None: bool(captured.append(text)) or True
    )
    return captured


@pytest.fixture
def mollie(monkeypatch: pytest.MonkeyPatch) -> dict[str, list]:
    """Stub the two billing calls; record what they were asked to do."""
    calls: dict[str, list] = {"customers": [], "payments": []}

    def create_customer(name: str, email: str) -> str:
        calls["customers"].append((name, email))
        return "cst_test"

    def create_first_payment(customer_id, amount_eur, description, plan) -> str:
        calls["payments"].append((customer_id, amount_eur, description, plan))
        return _CHECKOUT_URL

    monkeypatch.setattr(billing, "create_customer", create_customer)
    monkeypatch.setattr(billing, "create_first_payment", create_first_payment)
    return calls


@pytest.fixture
def client(data_dir, sent) -> TestClient:
    server._hits.clear()
    return TestClient(server.app)


def test_checkout_saves_lead_and_returns_mollie_url(
    client: TestClient, data_dir, sent, mollie
) -> None:
    resp = client.post("/api/checkout", json=_BUYER)

    assert resp.status_code == 200
    assert resp.json() == {"ok": True, "checkout_url": _CHECKOUT_URL}
    record = json.loads((data_dir / "leads.jsonl").read_text(encoding="utf-8"))
    assert record["naam"] == "Jan de Vries" and record["checkout"] is True
    assert sent, "the founder still gets the signup ping"
    # Mollie got the business name (fallback: person's name) and the founding-offer amount.
    assert mollie["customers"] == [("De Vries Installatietechniek BV", "jan@devries.nl")]
    assert mollie["payments"] == [
        ("cst_test", billing.FIRST_MONTH_EUR, "Klantkraan Chat eerste maand", "chat")
    ]


def test_person_name_when_no_company(client: TestClient, data_dir, mollie) -> None:
    resp = client.post("/api/checkout", json={**_BUYER, "bedrijf": ""})
    assert resp.status_code == 200
    assert mollie["customers"] == [("Jan de Vries", "jan@devries.nl")]


def test_mollie_down_degrades_to_lead_only(
    client: TestClient, data_dir, sent, monkeypatch: pytest.MonkeyPatch
) -> None:
    def boom(name: str, email: str) -> str:
        raise billing.MollieUnreachable("mollie down")

    monkeypatch.setattr(billing, "create_customer", boom)
    resp = client.post("/api/checkout", json=_BUYER)

    assert resp.status_code == 200
    assert resp.json() == {"ok": True, "checkout_url": None}
    assert (data_dir / "leads.jsonl").exists(), "the lead survives a Mollie outage"


def test_missing_api_key_degrades_to_lead_only(
    client: TestClient, data_dir, sent, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Force the no-key path → billing raises MissingSetting inside the try. The tripwire on
    # the HTTP seam guarantees this test can never reach real Mollie, whatever .env holds.
    monkeypatch.delenv("MOLLIE_API_KEY", raising=False)
    monkeypatch.setattr(
        billing, "_request", lambda *a, **k: (_ for _ in ()).throw(AssertionError("real HTTP"))
    )
    resp = client.post("/api/checkout", json=_BUYER)
    assert resp.status_code == 200
    assert resp.json() == {"ok": True, "checkout_url": None}
    assert (data_dir / "leads.jsonl").exists()


def test_honeypot_pretends_success_but_stores_nothing(
    client: TestClient, data_dir, sent, mollie
) -> None:
    resp = client.post("/api/checkout", json={**_BUYER, "website": "https://spam.example"})

    assert resp.status_code == 200 and resp.json() == {"ok": True, "checkout_url": None}
    assert not (data_dir / "leads.jsonl").exists()
    assert not sent and not mollie["customers"]


def test_email_is_required(client: TestClient) -> None:
    assert client.post("/api/checkout", json={**_BUYER, "email": ""}).status_code == 422
    assert client.post("/api/checkout", json={**_BUYER, "email": "   "}).status_code == 422


def test_only_the_chat_plan_can_be_bought(client: TestClient) -> None:
    resp = client.post("/api/checkout", json={**_BUYER, "plan": "compleet"})
    assert resp.status_code == 422, "compleet is not self-serve until voice ships"


# --- Native form posts: the zero-JS fallback. The browser is navigating, so every answer
# --- must be a 303 — into Mollie on success, back to the form on bad input.

_REFERER = {"referer": "https://klantkraan.nl/aanmelden/"}


def test_native_form_post_redirects_into_mollie(client: TestClient, data_dir, sent, mollie) -> None:
    resp = client.post("/api/checkout", data=_BUYER, headers=_REFERER, follow_redirects=False)

    assert resp.status_code == 303 and resp.headers["location"] == _CHECKOUT_URL
    record = json.loads((data_dir / "leads.jsonl").read_text(encoding="utf-8"))
    assert record["naam"] == "Jan de Vries" and record["checkout"] is True


def test_native_interest_plan_is_a_lead_not_a_buy(
    client: TestClient, data_dir, sent, mollie
) -> None:
    payload = {**_BUYER, "plan": "compleet-interesse", "email": ""}
    resp = client.post("/api/checkout", data=payload, headers=_REFERER, follow_redirects=False)

    assert resp.status_code == 303
    assert resp.headers["location"] == "https://klantkraan.nl/bedankt/"
    assert not mollie["customers"], "interest-only never touches Mollie"
    record = json.loads((data_dir / "leads.jsonl").read_text(encoding="utf-8"))
    assert record["plan"] == "compleet-interesse" and "checkout" not in record


def test_native_invalid_input_bounces_back_to_the_form(
    client: TestClient, data_dir, mollie
) -> None:
    resp = client.post(
        "/api/checkout",
        data={**_BUYER, "email": ""},
        headers={"referer": "https://klantkraan.nl/en/aanmelden/"},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert resp.headers["location"] == "https://klantkraan.nl/en/aanmelden/?fout=1"
    assert not (data_dir / "leads.jsonl").exists()


def test_native_locale_thanks_page_follows_the_referer(client: TestClient, sent, mollie) -> None:
    resp = client.post(
        "/api/checkout",
        data={**_BUYER, "plan": "compleet-interesse"},
        headers={"referer": "https://klantkraan.nl/es/aanmelden/"},
        follow_redirects=False,
    )
    assert resp.headers["location"] == "https://klantkraan.nl/es/bedankt/"


def test_native_foreign_referer_is_never_echoed(client: TestClient, sent, mollie) -> None:
    resp = client.post(
        "/api/checkout",
        data={**_BUYER, "email": ""},
        headers={"referer": "https://evil.example/aanmelden/"},
        follow_redirects=False,
    )
    assert resp.headers["location"] == "https://klantkraan.nl/aanmelden/?fout=1"


def test_native_honeypot_redirects_to_thanks_but_stores_nothing(
    client: TestClient, data_dir, sent, mollie
) -> None:
    resp = client.post(
        "/api/checkout",
        data={**_BUYER, "website": "https://spam.example"},
        headers=_REFERER,
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert resp.headers["location"] == "https://klantkraan.nl/bedankt/"
    assert not (data_dir / "leads.jsonl").exists() and not mollie["customers"]


def test_native_mollie_down_still_lands_on_thanks(
    client: TestClient, data_dir, sent, monkeypatch: pytest.MonkeyPatch
) -> None:
    def boom(name: str, email: str) -> str:
        raise billing.MollieUnreachable("mollie down")

    monkeypatch.setattr(billing, "create_customer", boom)
    resp = client.post("/api/checkout", data=_BUYER, headers=_REFERER, follow_redirects=False)

    assert resp.status_code == 303
    assert resp.headers["location"] == "https://klantkraan.nl/bedankt/"
    assert (data_dir / "leads.jsonl").exists(), "the lead survives a Mollie outage"
