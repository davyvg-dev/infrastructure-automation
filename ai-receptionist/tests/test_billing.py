"""app/billing.py + POST /api/mollie/webhook. Offline — the Mollie HTTP layer is a stub
(billing._request), Telegram is captured, events land in a throwaway data dir."""

from __future__ import annotations

import json
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app import billing, notify, server
from app.settings import MissingSetting

_PAYMENT_ID = "tr_test1"
_CUSTOMER_ID = "cst_1"


class FakeMollie:
    """Stands in for billing._request; records every call and plays a Mollie account with
    one customer whose first payment is in the given state."""

    def __init__(
        self,
        status: str = "paid",
        sequence_type: str = "first",
        subscriptions: list[dict[str, Any]] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.calls: list[tuple[str, str, dict[str, Any] | None]] = []
        self.subscriptions = subscriptions if subscriptions is not None else []
        self.payment = {
            "resource": "payment",
            "id": _PAYMENT_ID,
            "status": status,
            "sequenceType": sequence_type,
            "customerId": _CUSTOMER_ID,
            "metadata": metadata
            if metadata is not None
            else {"plan": "chat", "monthly_eur": "299.00"},
        }

    def __call__(self, method: str, path: str, data: dict[str, Any] | None = None):
        self.calls.append((method, path, data))
        if method == "GET" and path == f"/payments/{_PAYMENT_ID}":
            return self.payment
        if method == "GET" and path.startswith("/payments/"):
            raise billing.MollieError("Mollie 404 on GET " + path)
        if method == "GET" and path == f"/customers/{_CUSTOMER_ID}/subscriptions":
            return {
                "count": len(self.subscriptions),
                "_embedded": {"subscriptions": list(self.subscriptions)},
            }
        if method == "POST" and path == f"/customers/{_CUSTOMER_ID}/subscriptions":
            sub = {"resource": "subscription", "id": "sub_new", "status": "active", **(data or {})}
            self.subscriptions.append(sub)
            return sub
        raise AssertionError(f"unexpected Mollie call: {method} {path}")

    def subscription_creates(self) -> list[dict[str, Any] | None]:
        return [
            data
            for method, path, data in self.calls
            if method == "POST" and "subscriptions" in path
        ]


@pytest.fixture
def sent(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    captured: list[str] = []
    monkeypatch.setattr(
        notify, "owner", lambda text, chat_id=None: bool(captured.append(text)) or True
    )
    return captured


@pytest.fixture
def client(data_dir, sent) -> TestClient:
    server._hits.clear()  # each test starts with a fresh rate-limit window
    return TestClient(server.app)


def _mollie(monkeypatch: pytest.MonkeyPatch, fake: FakeMollie) -> FakeMollie:
    monkeypatch.setattr(billing, "_request", fake)
    return fake


def _webhook_events(data_dir) -> list[dict[str, Any]]:
    path = data_dir / "billing.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_paid_first_payment_creates_the_subscription(
    client: TestClient, data_dir, sent, monkeypatch
) -> None:
    fake = _mollie(monkeypatch, FakeMollie())

    resp = client.post("/api/mollie/webhook", data={"id": _PAYMENT_ID})

    assert resp.status_code == 200 and resp.json() == {"ok": True}
    (create,) = fake.subscription_creates()
    assert create["amount"] == {"currency": "EUR", "value": "299.00"}
    assert create["interval"] == "1 month"
    assert create["description"] == "Klantkraan Chat maandabonnement"
    (event,) = _webhook_events(data_dir)
    assert event["action"] == "subscription_created" and event["subscription_id"] == "sub_new"
    assert event["at"], "every event carries a timestamp"
    assert sent and "abonnement gestart" in sent[0]


def test_second_webhook_for_same_payment_is_idempotent(
    client: TestClient, data_dir, sent, monkeypatch
) -> None:
    fake = _mollie(monkeypatch, FakeMollie())

    first = client.post("/api/mollie/webhook", data={"id": _PAYMENT_ID})
    second = client.post("/api/mollie/webhook", data={"id": _PAYMENT_ID})

    assert first.status_code == 200 and second.status_code == 200
    assert len(fake.subscription_creates()) == 1, "the retry must not create a second subscription"
    events = _webhook_events(data_dir)
    assert [e["action"] for e in events] == ["subscription_created", "already_subscribed"]


def test_customer_with_live_subscription_is_not_resubscribed(
    client: TestClient, data_dir, sent, monkeypatch
) -> None:
    existing = {"resource": "subscription", "id": "sub_old", "status": "active"}
    fake = _mollie(monkeypatch, FakeMollie(subscriptions=[existing]))

    resp = client.post("/api/mollie/webhook", data={"id": _PAYMENT_ID})

    assert resp.status_code == 200
    assert fake.subscription_creates() == []


def test_non_paid_status_is_ignored(client: TestClient, data_dir, sent, monkeypatch) -> None:
    fake = _mollie(monkeypatch, FakeMollie(status="expired"))

    resp = client.post("/api/mollie/webhook", data={"id": _PAYMENT_ID})

    assert resp.status_code == 200 and resp.json() == {"ok": True}
    assert fake.subscription_creates() == []
    (event,) = _webhook_events(data_dir)
    assert event["action"] == "ignored" and event["status"] == "expired"


def test_recurring_paid_payment_does_not_create_another_subscription(
    client: TestClient, data_dir, sent, monkeypatch
) -> None:
    fake = _mollie(monkeypatch, FakeMollie(sequence_type="recurring"))

    resp = client.post("/api/mollie/webhook", data={"id": _PAYMENT_ID})

    assert resp.status_code == 200
    assert fake.subscription_creates() == []
    (event,) = _webhook_events(data_dir)
    assert event["action"] == "recurring_paid"


@pytest.mark.parametrize("bad_id", ["", "abc", "tr_", "tr_abc/../x", "TR_UPPER", "sub_x1"])
def test_invalid_payment_id_shapes_are_rejected(client: TestClient, bad_id: str) -> None:
    assert client.post("/api/mollie/webhook", data={"id": bad_id}).status_code == 400


def test_missing_id_field_is_rejected(client: TestClient) -> None:
    assert client.post("/api/mollie/webhook", data={}).status_code == 400


def test_unknown_payment_id_logs_and_returns_200(
    client: TestClient, data_dir, sent, monkeypatch
) -> None:
    _mollie(monkeypatch, FakeMollie())  # only knows tr_test1

    resp = client.post("/api/mollie/webhook", data={"id": "tr_unknown"})

    assert resp.status_code == 200, "Mollie must stop retrying a payment it 404s on"
    (event,) = _webhook_events(data_dir)
    assert event["action"] == "ignored" and "404" in event["reason"]


def test_mollie_unreachable_returns_503_so_mollie_retries(
    client: TestClient, data_dir, sent, monkeypatch
) -> None:
    def down(method: str, path: str, data=None):
        raise billing.MollieUnreachable("connect timeout")

    monkeypatch.setattr(billing, "_request", down)

    assert client.post("/api/mollie/webhook", data={"id": _PAYMENT_ID}).status_code == 503
    assert _webhook_events(data_dir) == [], "an unfetched event is not logged as handled"


def test_missing_api_key_raises_a_clear_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MOLLIE_API_KEY", raising=False)

    with pytest.raises(MissingSetting, match="MOLLIE_API_KEY"):
        billing.create_customer("Jan de Vries BV", "jan@devries.nl")


def test_missing_api_key_defers_the_webhook(
    client: TestClient, data_dir, sent, monkeypatch
) -> None:
    monkeypatch.delenv("MOLLIE_API_KEY", raising=False)

    resp = client.post("/api/mollie/webhook", data={"id": _PAYMENT_ID})

    assert resp.status_code == 503, "retry until the key is configured — the event is money"


def test_notify_failure_never_fails_the_webhook(client: TestClient, data_dir, monkeypatch) -> None:
    def boom(text: str, chat_id: str | None = None) -> bool:
        raise RuntimeError("telegram down")

    monkeypatch.setattr(notify, "owner", boom)
    fake = _mollie(monkeypatch, FakeMollie())

    resp = client.post("/api/mollie/webhook", data={"id": _PAYMENT_ID})

    assert resp.status_code == 200
    assert len(fake.subscription_creates()) == 1, "the subscription is still created"


def test_create_first_payment_sends_the_stateless_metadata(
    data_dir, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[tuple[str, str, dict[str, Any] | None]] = []

    def fake(method: str, path: str, data=None):
        calls.append((method, path, data))
        return {"id": "tr_new1", "_links": {"checkout": {"href": "https://pay.example/x"}}}

    monkeypatch.setattr(billing, "_request", fake)

    url = billing.create_first_payment(
        _CUSTOMER_ID, "149.5", "Klantkraan Chat eerste maand", "chat"
    )

    assert url == "https://pay.example/x"
    ((method, path, body),) = calls
    assert (method, path) == ("POST", "/payments")
    assert body["amount"] == {"currency": "EUR", "value": "149.50"}, "amounts are 2-decimal strings"
    assert body["sequenceType"] == "first" and body["customerId"] == _CUSTOMER_ID
    assert body["metadata"] == {"plan": "chat", "monthly_eur": "299.00"}
    assert body["webhookUrl"].endswith("/api/mollie/webhook") and body["redirectUrl"]
    (event,) = _webhook_events(data_dir)
    assert event["event"] == "checkout_created" and event["payment_id"] == "tr_new1"
