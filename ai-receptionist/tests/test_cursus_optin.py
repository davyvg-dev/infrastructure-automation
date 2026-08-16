"""POST /api/cursus + GET/POST /cursus/uitschrijven: course opt-in from the rekentool and
the token-checked afmeldpagina. Offline — mailer and Telegram are stubbed, the subscriber
ledger lives in a throwaway dir."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app import cursus, notify, server

_OPTIN = {"email": "jan@devries.nl", "naam": "Jan"}


@pytest.fixture
def mails(monkeypatch: pytest.MonkeyPatch) -> list[dict]:
    """Capture every mailer.send call; the mailer always accepts."""
    calls: list[dict] = []

    def fake_send(to, subject, text, **kwargs):
        calls.append({"to": to, "subject": subject, **kwargs})
        return True

    monkeypatch.setattr(cursus.mailer, "send", fake_send)
    return calls


@pytest.fixture
def pings(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    captured: list[str] = []
    monkeypatch.setattr(
        notify, "owner", lambda text, chat_id=None: bool(captured.append(text)) or True
    )
    return captured


@pytest.fixture
def client(data_dir, mails, pings) -> TestClient:
    server._hits.clear()  # each test starts with a fresh rate-limit window
    return TestClient(server.app)


def test_json_optin_subscribes_and_fires_lesson_1(client: TestClient, mails, pings) -> None:
    resp = client.post("/api/cursus", json=_OPTIN)

    assert resp.status_code == 200 and resp.json() == {"ok": True}
    sub = cursus.load()["subscribers"]["jan@devries.nl"]
    assert sub["name"] == "Jan" and "1" in sub["lessons"], "lesson 1 goes out immediately"
    assert len(mails) == 1 and mails[0]["to"] == "jan@devries.nl"
    assert pings and "jan@devries.nl" in pings[0]


def test_native_form_post_redirects_back_to_the_page(client: TestClient, mails) -> None:
    resp = client.post(
        "/api/cursus",
        data=_OPTIN,
        headers={"Referer": "https://klantkraan.nl/rekentool/"},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert resp.headers["location"] == "https://klantkraan.nl/rekentool/?cursus=ok"
    assert len(mails) == 1


def test_unknown_referer_falls_back_to_the_default_page(client: TestClient, mails) -> None:
    resp = client.post(
        "/api/cursus",
        data=_OPTIN,
        headers={"Referer": "https://evil.example/phish"},
        follow_redirects=False,
    )
    assert resp.headers["location"] == "https://klantkraan.nl/rekentool/?cursus=ok"


def test_honeypot_pretends_success_but_stores_nothing(client: TestClient, mails, pings) -> None:
    resp = client.post("/api/cursus", json={**_OPTIN, "website": "https://spam.example"})

    assert resp.status_code == 200 and resp.json() == {"ok": True}, "bots must see success"
    assert cursus.load()["subscribers"] == {} and not mails and not pings


def test_malformed_email_is_rejected(client: TestClient) -> None:
    assert client.post("/api/cursus", json={"email": "jan@devries"}).status_code == 422


def test_malformed_email_native_redirects_to_fout(client: TestClient) -> None:
    resp = client.post(
        "/api/cursus",
        data={"email": "jan@devries"},
        headers={"Referer": "https://klantkraan.nl/rekentool/"},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert resp.headers["location"] == "https://klantkraan.nl/rekentool/?cursus=fout"


def test_failed_send_still_subscribes(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(cursus.mailer, "send", lambda *a, **k: False)
    resp = client.post("/api/cursus", json=_OPTIN)

    assert resp.status_code == 200, "the ledger has the subscriber; the timer retries"
    sub = cursus.load()["subscribers"]["jan@devries.nl"]
    assert sub["lessons"] == {}, "an unsent lesson is not recorded as sent"


def test_broken_store_returns_503_and_pings_the_address(
    client: TestClient, pings, monkeypatch: pytest.MonkeyPatch
) -> None:
    def corrupt(*a, **k):
        raise SystemExit("cursus: store is corrupt")

    monkeypatch.setattr(cursus, "add", corrupt)
    resp = client.post("/api/cursus", json=_OPTIN)

    assert resp.status_code == 503
    assert any("NIET opgeslagen" in p and "jan@devries.nl" in p for p in pings)


def test_rate_limit_applies(client: TestClient) -> None:
    for _ in range(server._RATE_LIMIT_PER_MINUTE):
        assert server._rate_ok("cursus:testclient")
    assert client.post("/api/cursus", json=_OPTIN).status_code == 429


def test_afmeld_get_shows_confirmation_without_unsubscribing(client: TestClient) -> None:
    cursus.add("jan@devries.nl")
    resp = client.get(f"/cursus/uitschrijven?e=jan@devries.nl&t={cursus.token('jan@devries.nl')}")

    assert resp.status_code == 200 and "<form" in resp.text, "a prefetched GET must not act"
    assert "unsubscribed" not in cursus.load()["subscribers"]["jan@devries.nl"]


def test_afmeld_post_unsubscribes(client: TestClient) -> None:
    cursus.add("jan@devries.nl")
    resp = client.post(
        f"/cursus/uitschrijven?e=jan@devries.nl&t={cursus.token('jan@devries.nl')}",
        # RFC 8058 one-click body; the human confirm button sends an empty form instead.
        data={"List-Unsubscribe": "One-Click"},
    )

    assert resp.status_code == 200 and "afgemeld" in resp.text
    assert cursus.load()["subscribers"]["jan@devries.nl"]["unsubscribed"]


def test_afmeld_bad_token_is_rejected(client: TestClient) -> None:
    cursus.add("jan@devries.nl")
    for method in (client.get, client.post):
        resp = method("/cursus/uitschrijven?e=jan@devries.nl&t=deadbeef")
        assert resp.status_code == 404
    assert "unsubscribed" not in cursus.load()["subscribers"]["jan@devries.nl"]


def test_resignup_after_afmelding_is_fresh_consent(client: TestClient, mails) -> None:
    client.post("/api/cursus", json=_OPTIN)
    client.post(
        f"/cursus/uitschrijven?e=jan@devries.nl&t={cursus.token('jan@devries.nl')}", data={}
    )
    resp = client.post("/api/cursus", json=_OPTIN)

    assert resp.status_code == 200
    sub = cursus.load()["subscribers"]["jan@devries.nl"]
    assert "unsubscribed" not in sub, "a re-signup clears the halt"
    assert len(mails) == 1, "lesson 1 was already sent; it never goes out twice"
