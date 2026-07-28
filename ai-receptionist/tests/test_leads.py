"""POST /api/lead: signup intake from the marketing site. Offline — Telegram is stubbed,
leads land in a throwaway data dir."""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from app import notify, server

_LEAD = {
    "naam": "Jan de Vries",
    "bedrijf": "De Vries Installatietechniek BV",
    "telefoon": "+31 6 1234 5678",
    "email": "jan@devries.nl",
    "vak": "installateur",
    "plan": "chat",
    "bericht": "Graag deze week starten.",
}


@pytest.fixture
def sent(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Capture what site_lead would send to Telegram."""
    captured: list[str] = []
    monkeypatch.setattr(
        notify, "owner", lambda text, chat_id=None: bool(captured.append(text)) or True
    )
    return captured


@pytest.fixture
def client(data_dir, sent) -> TestClient:
    server._hits.clear()  # each test starts with a fresh rate-limit window
    return TestClient(server.app)


def test_valid_lead_is_saved_and_notified(client: TestClient, data_dir, sent) -> None:
    resp = client.post("/api/lead", json=_LEAD)

    assert resp.status_code == 200 and resp.json() == {"ok": True}
    lines = (data_dir / "leads.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["naam"] == "Jan de Vries" and record["plan"] == "chat"
    assert record["at"], "every lead carries a timestamp"
    assert "website" not in record, "the honeypot field never persists"
    assert sent and "Jan de Vries" in sent[0] and "chat" in sent[0]


def test_leads_append_rather_than_overwrite(client: TestClient, data_dir, sent) -> None:
    client.post("/api/lead", json=_LEAD)
    client.post("/api/lead", json={**_LEAD, "naam": "Piet Bakker"})

    lines = (data_dir / "leads.jsonl").read_text(encoding="utf-8").splitlines()
    assert [json.loads(line)["naam"] for line in lines] == ["Jan de Vries", "Piet Bakker"]


def test_honeypot_pretends_success_but_stores_nothing(client: TestClient, data_dir, sent) -> None:
    resp = client.post("/api/lead", json={**_LEAD, "website": "https://spam.example"})

    assert resp.status_code == 200 and resp.json() == {"ok": True}, "bots must see success"
    assert not (data_dir / "leads.jsonl").exists()
    assert not sent


def test_missing_name_is_rejected(client: TestClient) -> None:
    payload = {k: v for k, v in _LEAD.items() if k != "naam"}
    assert client.post("/api/lead", json=payload).status_code == 422


def test_needs_phone_or_email(client: TestClient, data_dir) -> None:
    neither = {**_LEAD, "telefoon": "", "email": "  "}
    assert client.post("/api/lead", json=neither).status_code == 422

    phone_only = {**_LEAD, "email": ""}
    assert client.post("/api/lead", json=phone_only).status_code == 200


def test_malformed_email_is_rejected(client: TestClient) -> None:
    for bad in ("jan", "jan@devries", "jan @devries.nl", "@devries.nl", "jan@.n"):
        resp = client.post("/api/lead", json={**_LEAD, "email": bad})
        assert resp.status_code == 422, f"email {bad!r} must be rejected"


def test_malformed_phone_is_rejected(client: TestClient) -> None:
    for bad in ("06-12", "bel mij", "0612345678901234", "+31 6 12 phone"):
        resp = client.post("/api/lead", json={**_LEAD, "telefoon": bad})
        assert resp.status_code == 422, f"phone {bad!r} must be rejected"


def test_formatted_phone_numbers_pass(client: TestClient, data_dir) -> None:
    for ok in ("+31 6 1234 5678", "06-12345678", "(020) 123 4567", "0034612345678"):
        resp = client.post("/api/lead", json={**_LEAD, "telefoon": ok})
        assert resp.status_code == 200, f"phone {ok!r} must be accepted"


def test_notify_failure_never_fails_the_request(
    client: TestClient, data_dir, monkeypatch: pytest.MonkeyPatch
) -> None:
    def boom(text: str, chat_id: str | None = None) -> bool:
        raise RuntimeError("telegram down")

    monkeypatch.setattr(notify, "owner", boom)
    resp = client.post("/api/lead", json=_LEAD)

    assert resp.status_code == 200 and resp.json() == {"ok": True}
    assert (data_dir / "leads.jsonl").exists(), "the lead still lands on disk"


def test_cors_preflight_allows_the_marketing_site(client: TestClient) -> None:
    resp = client.options(
        "/api/lead",
        headers={
            "Origin": "https://klantkraan.nl",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert resp.status_code == 200
    assert resp.headers["access-control-allow-origin"] == "https://klantkraan.nl"


def test_cors_blocks_unknown_origins(client: TestClient) -> None:
    resp = client.options(
        "/api/lead",
        headers={
            "Origin": "https://evil.example",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert "access-control-allow-origin" not in resp.headers
