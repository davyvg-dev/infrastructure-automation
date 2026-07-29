"""app/billing.py + POST /api/mollie/webhook. Offline — the Mollie HTTP layer is a stub
(billing._request), Telegram is captured, events land in a throwaway data dir."""

from __future__ import annotations

import json
import sys
from decimal import Decimal
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app import billing, mail_layout, mailer, notify, server
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
        customer: dict[str, Any] | None = None,
        cancel_405: bool = False,
    ) -> None:
        self.cancel_405 = cancel_405
        self.calls: list[tuple[str, str, dict[str, Any] | None]] = []
        self.subscriptions = subscriptions if subscriptions is not None else []
        self.customer = (
            customer
            if customer is not None
            else {"name": "Jan de Vries BV", "email": "jan@devries.nl"}
        )
        self.payment = {
            "resource": "payment",
            "id": _PAYMENT_ID,
            "status": status,
            "sequenceType": sequence_type,
            "customerId": _CUSTOMER_ID,
            "amount": {"currency": "EUR", "value": "149.50"},
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
        if method == "GET" and path == f"/customers/{_CUSTOMER_ID}":
            return {"resource": "customer", "id": _CUSTOMER_ID, **self.customer}
        if method == "GET" and path == f"/customers/{_CUSTOMER_ID}/subscriptions":
            return {
                "count": len(self.subscriptions),
                "_embedded": {"subscriptions": list(self.subscriptions)},
            }
        if method == "POST" and path == f"/customers/{_CUSTOMER_ID}/subscriptions":
            sub = {"resource": "subscription", "id": "sub_new", "status": "active", **(data or {})}
            self.subscriptions.append(sub)
            return sub
        if method == "GET" and path == f"/customers/{_CUSTOMER_ID}/payments":
            return {"_embedded": {"payments": [self.payment]}}
        if method == "POST" and path == f"/payments/{_PAYMENT_ID}/refunds":
            return {"resource": "refund", "id": "re_1", **(data or {})}
        if method in ("DELETE", "POST") and path.startswith(
            f"/customers/{_CUSTOMER_ID}/subscriptions/"
        ):
            if self.cancel_405 and method == "DELETE":
                raise billing.MollieError("Mollie 405 on DELETE " + path)
            sub_id = path.rsplit("/", 1)[-1]
            for existing in self.subscriptions:
                if existing.get("id") == sub_id:
                    existing["status"] = "canceled"
                    return existing
            raise billing.MollieError("Mollie 404 on " + path)
        raise AssertionError(f"unexpected Mollie call: {method} {path}")

    def subscription_creates(self) -> list[dict[str, Any] | None]:
        # Endswith, not "in": a cancel can also POST to .../subscriptions/<id>.
        return [
            data
            for method, path, data in self.calls
            if method == "POST" and path.endswith("/subscriptions")
        ]


@pytest.fixture
def sent(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    captured: list[str] = []
    monkeypatch.setattr(
        notify, "owner", lambda text, chat_id=None: bool(captured.append(text)) or True
    )
    return captured


@pytest.fixture
def mailed(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, Any]]:
    """Capture the customer-facing mail instead of putting it on the wire."""
    captured: list[dict[str, Any]] = []

    def fake_send(to, subject, text, *, html=None, reply_to=None, idempotency_key=None):
        captured.append(
            {"to": to, "subject": subject, "text": text, "html": html, "key": idempotency_key}
        )
        return True

    monkeypatch.setattr(mailer, "send", fake_send)
    return captured


@pytest.fixture
def client(data_dir, sent, mailed) -> TestClient:
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


def _welcome(mailed: list[dict[str, Any]]) -> dict[str, Any]:
    """The welcome, out of everything the webhook sent. A paid first payment now also sends
    a factuur, so "the mail" is no longer unambiguous."""
    welcomes = [m for m in mailed if m["subject"] == billing.WELCOME_SUBJECT]
    assert len(welcomes) == 1, f"expected exactly one welcome, got {[m['subject'] for m in mailed]}"
    return welcomes[0]


def test_paying_customer_gets_a_welcome_mail(
    client: TestClient, data_dir, sent, mailed, monkeypatch
) -> None:
    _mollie(monkeypatch, FakeMollie())

    client.post("/api/mollie/webhook", data={"id": _PAYMENT_ID})

    mail = _welcome(mailed)
    assert mail["to"] == "jan@devries.nl"
    assert mail["subject"] == billing.WELCOME_SUBJECT
    assert "binnen één werkdag" in mail["text"].lower(), "the one-working-day promise (1b step 1)"
    assert "€ 299,00 per maand" in mail["text"]
    assert "€ 149,50" in mail["text"], "the first month actually charged"
    assert mail["key"] == f"welcome-{_CUSTOMER_ID}", "Resend must dedupe a webhook replay"
    assert "Welkomstmail verstuurd" in sent[0], "the founder ping says the customer heard from us"


def test_the_welcome_goes_out_branded_and_as_text(
    client: TestClient, data_dir, sent, mailed, monkeypatch
) -> None:
    """Both parts, from one description of the message. The text part is not optional:
    it is what plain-text clients render and what spam filters read."""
    _mollie(monkeypatch, FakeMollie())

    client.post("/api/mollie/webhook", data={"id": _PAYMENT_ID})

    mail = _welcome(mailed)
    assert mail["html"] and mail["html"].startswith("<!doctype html>")
    assert "https://klantkraan.nl/email/logo.png" in mail["html"], "logo must be an absolute URL"
    assert "€ 299,00 per maand" in mail["html"], "the price cannot differ between the parts"
    assert "<table" in mail["html"], "tables, not flexbox -- Outlook renders through Word"


def test_the_welcome_reads_complete_with_images_blocked(mailed) -> None:
    """Most clients block images until asked. Nothing may live only in a picture."""
    blocks = billing.welcome_blocks(person="Jan", plan="chat", monthly_eur="299.00")
    photos = [b for b in blocks if isinstance(b, mail_layout.Photo)]

    assert photos, "the welcome carries a photo"
    assert all(p.alt.strip() for p in photos), "every photo describes itself"
    text = mail_layout.to_text(blocks)
    assert all(p.src not in text for p in photos), "the text part invents no image caption"


def test_a_customer_name_cannot_break_out_of_the_html(mailed) -> None:
    """The name comes from a signup form, so it is attacker-controlled."""
    html = billing.welcome_html(
        person="<script>alert(1)</script> Vries", plan="chat", monthly_eur="299.00"
    )

    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_welcome_is_sent_once_even_if_mollie_retries(
    client: TestClient, data_dir, sent, mailed, monkeypatch
) -> None:
    _mollie(monkeypatch, FakeMollie())

    client.post("/api/mollie/webhook", data={"id": _PAYMENT_ID})
    client.post("/api/mollie/webhook", data={"id": _PAYMENT_ID})

    welcomes = [m for m in mailed if m["subject"] == billing.WELCOME_SUBJECT]
    assert len(welcomes) == 1, "the second webhook is already_subscribed: no second welcome"


def test_welcome_skips_the_website_question_when_the_form_already_asked(
    client: TestClient, data_dir, sent, mailed, monkeypatch
) -> None:
    notify.site_lead({"naam": "Jan de Vries", "email": "jan@devries.nl", "site": "devries.nl"})
    _mollie(monkeypatch, FakeMollie())

    client.post("/api/mollie/webhook", data={"id": _PAYMENT_ID})

    mail = _welcome(mailed)
    assert mail["text"].startswith("Hoi Jan,"), "greet the person, not the BV"
    assert "link naar uw website" not in mail["text"]


def test_a_failed_welcome_does_not_fail_the_webhook_but_alerts_the_founder(
    client: TestClient, data_dir, sent, monkeypatch
) -> None:
    _mollie(monkeypatch, FakeMollie())
    monkeypatch.setattr(mailer, "send", lambda *a, **k: False)
    monkeypatch.setattr(mailer, "configured", lambda: False)

    resp = client.post("/api/mollie/webhook", data={"id": _PAYMENT_ID})

    assert resp.status_code == 200, "the money moved; a mail problem cannot fail the webhook"
    (event,) = _webhook_events(data_dir)
    assert event["action"] == "subscription_created" and event["welcome_sent"] is False
    assert "GEEN welkomstmail" in sent[0] and "python -m app.billing welcome" in sent[0]


def test_customer_without_an_email_is_reported_not_crashed(
    client: TestClient, data_dir, sent, mailed, monkeypatch
) -> None:
    _mollie(monkeypatch, FakeMollie(customer={"name": "Jan de Vries BV"}))

    resp = client.post("/api/mollie/webhook", data={"id": _PAYMENT_ID})

    assert resp.status_code == 200 and mailed == []
    (event,) = _webhook_events(data_dir)
    assert "no e-mail" in event["welcome_reason"]


# --- Off-boarding: the decline path without the Mollie dashboard -------------------------

_LIVE_SUB = {"resource": "subscription", "id": "sub_live", "status": "active"}


def test_cancel_stops_a_live_subscription(data_dir, monkeypatch) -> None:
    fake = _mollie(monkeypatch, FakeMollie(subscriptions=[dict(_LIVE_SUB)]))

    billing.cancel_subscription(_CUSTOMER_ID, "sub_live")

    assert fake.subscriptions[0]["status"] == "canceled"
    assert not billing._has_live_subscription(_CUSTOMER_ID)


def test_cancel_falls_back_to_post_when_delete_is_refused(data_dir, monkeypatch) -> None:
    """Mollie's REST reference documents DELETE, their Python SDK documents POST. Whichever
    this account speaks, a cancel that silently does not happen keeps charging the customer."""
    fake = _mollie(monkeypatch, FakeMollie(subscriptions=[dict(_LIVE_SUB)], cancel_405=True))

    billing.cancel_subscription(_CUSTOMER_ID, "sub_live")

    verbs = [m for m, p, _ in fake.calls if "subscriptions/sub_live" in p]
    assert verbs == ["DELETE", "POST"]
    assert fake.subscriptions[0]["status"] == "canceled"


def test_refund_without_an_amount_refunds_what_was_actually_charged(data_dir, monkeypatch) -> None:
    """The founding-member first month is €149.50, not €299. Read the charge, never assume."""
    fake = _mollie(monkeypatch, FakeMollie())

    billing.refund_payment(_PAYMENT_ID)

    (refund,) = [d for m, p, d in fake.calls if p.endswith("/refunds")]
    assert refund["amount"] == {"currency": "EUR", "value": "149.50"}
    (event,) = [e for e in _webhook_events(data_dir) if e["event"] == "refund"]
    assert event["amount_eur"] == "149.50" and event["refund_id"] == "re_1"


def test_offboard_cancels_before_it_refunds(data_dir, monkeypatch) -> None:
    """A refunded customer left on a live mandate is the outcome that becomes a chargeback."""
    fake = _mollie(monkeypatch, FakeMollie(subscriptions=[dict(_LIVE_SUB)]))

    result = billing.offboard(_CUSTOMER_ID)

    order = [p for m, p, _ in fake.calls if "subscriptions/sub_live" in p or p.endswith("/refunds")]
    assert order[0].endswith("subscriptions/sub_live") and order[-1].endswith("/refunds")
    assert result["canceled"] == ["sub_live"]
    assert result["refund"]["amount_eur"] == "149.50"


def test_offboard_without_a_first_payment_reports_instead_of_crashing(
    data_dir, monkeypatch
) -> None:
    fake = FakeMollie(subscriptions=[dict(_LIVE_SUB)])
    fake.payment["status"] = "failed"  # nothing refundable on this customer
    _mollie(monkeypatch, fake)

    result = billing.offboard(_CUSTOMER_ID)

    assert result["canceled"] == ["sub_live"], "the mandate still had to stop"
    assert "no paid first payment" in result["refund"]["error"]


def test_money_moving_verbs_refuse_to_run_unattended_without_yes(monkeypatch) -> None:
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)

    assert billing._confirm(False, "€299 terugbetalen?") is False
    assert billing._confirm(True, "€299 terugbetalen?") is True


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
    # 149.50 net is what we advertise; 180.90 is what the bank account sees.
    assert body["amount"] == {"currency": "EUR", "value": "180.90"}
    assert body["sequenceType"] == "first" and body["customerId"] == _CUSTOMER_ID
    assert body["metadata"] == {
        "plan": "chat",
        "monthly_eur": "361.79",
        "monthly_net_eur": "299.00",
    }
    assert body["webhookUrl"].endswith("/api/mollie/webhook") and body["redirectUrl"]
    (event,) = _webhook_events(data_dir)
    assert event["event"] == "checkout_created" and event["payment_id"] == "tr_new1"


def test_a_test_checkout_makes_the_subscription_cheap_too(
    data_dir, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A EUR 1 first payment must not leave a EUR 299/month subscription behind it."""
    calls: list[dict[str, Any] | None] = []

    def fake(method: str, path: str, data=None):
        calls.append(data)
        return {"id": "tr_new1", "_links": {"checkout": {"href": "https://pay.example/x"}}}

    monkeypatch.setattr(billing, "_request", fake)

    billing.create_first_payment(
        _CUSTOMER_ID, "1.00", "Klantkraan Chat eerste maand", "chat", "1.00"
    )

    (body,) = calls
    assert body["amount"] == {"currency": "EUR", "value": "1.21"}
    assert body["metadata"]["monthly_eur"] == "1.21", "the webhook bills what this says"
    assert body["metadata"]["monthly_net_eur"] == "1.00"


# --- BTW ---------------------------------------------------------------------------------
# The advertised price is ex-BTW (klantkraan.nl/prijzen says so), so the charge is grossed
# up and the factuur splits that same gross back. These pin both directions.


@pytest.mark.parametrize(
    ("net", "gross"),
    [("299.00", "361.79"), ("149.50", "180.90"), ("1.00", "1.21"), ("499.00", "603.79")],
)
def test_the_advertised_price_is_grossed_up_for_the_charge(net: str, gross: str) -> None:
    assert billing.gross_eur(net) == gross


@pytest.mark.parametrize("gross", ["361.79", "180.90", "1.21", "0.01", "299.00"])
def test_net_plus_btw_always_sums_back_to_what_was_charged(gross: str) -> None:
    """The factuur must add up to the cent against the customer's bank statement."""
    net, btw = billing.split_gross(gross)
    assert Decimal(net) + Decimal(btw) == Decimal(gross)


def test_the_btw_treatment_is_switchable(monkeypatch: pytest.MonkeyPatch) -> None:
    """The founder may decide 299 is the gross after all; one env var, no code change."""
    monkeypatch.setenv("PRICES_INCLUDE_BTW", "1")
    assert billing.gross_eur("299.00") == "299.00", "the advertised price IS the charge"


# --- Factuur -----------------------------------------------------------------------------
# Which payments get invoiced, and what the founder is told. The document itself (numbering,
# the BTW split, rendering) is covered offline in test_invoice.py.


def _factuur(mailed: list[dict[str, Any]]) -> dict[str, Any] | None:
    return next((m for m in mailed if m["subject"].startswith("Factuur ")), None)


def test_a_paid_first_payment_gets_a_factuur_as_well_as_a_welcome(
    client: TestClient, data_dir, sent, mailed, monkeypatch
) -> None:
    """The gap this closes: the welcome went out, the factuur never did."""
    _mollie(monkeypatch, FakeMollie())

    client.post("/api/mollie/webhook", data={"id": _PAYMENT_ID})

    factuur = _factuur(mailed)
    assert factuur is not None, "a paying customer gets an invoice"
    assert factuur["to"] == "jan@devries.nl"
    assert factuur["subject"] == "Factuur 2026-0001 van Klantkraan"
    assert "eerste maand" in factuur["text"], "the first payment is not a normal month"
    # 149.50 charged splits into 123.55 + 25.95.
    assert "€ 123,55" in factuur["text"] and "€ 25,95" in factuur["text"]
    assert (data_dir / "invoices" / "factuur-2026-0001.html").exists(), "archived for 7 years"


def test_a_recurring_charge_is_invoiced_too(
    client: TestClient, data_dir, sent, mailed, monkeypatch
) -> None:
    """Month two is the one the client's bookkeeper chases us for."""
    _mollie(monkeypatch, FakeMollie(sequence_type="recurring", subscriptions=[{"id": "sub_1"}]))

    client.post("/api/mollie/webhook", data={"id": _PAYMENT_ID})

    factuur = _factuur(mailed)
    assert factuur is not None
    assert "maandabonnement" in factuur["text"]
    assert not [m for m in mailed if m["subject"] == billing.WELCOME_SUBJECT], "no second welcome"


def test_a_webhook_replay_does_not_issue_a_second_factuur(
    client: TestClient, data_dir, sent, mailed, monkeypatch
) -> None:
    _mollie(monkeypatch, FakeMollie())

    client.post("/api/mollie/webhook", data={"id": _PAYMENT_ID})
    client.post("/api/mollie/webhook", data={"id": _PAYMENT_ID})

    facturen = [m for m in mailed if m["subject"].startswith("Factuur ")]
    assert len(facturen) == 1, "the replay is already_subscribed and re-invoices nothing"
    assert facturen[0]["key"] == f"factuur-{_PAYMENT_ID}", "Resend dedupes it as well"


def test_an_unpaid_payment_is_never_invoiced(
    client: TestClient, data_dir, sent, mailed, monkeypatch
) -> None:
    _mollie(monkeypatch, FakeMollie(status="open"))

    client.post("/api/mollie/webhook", data={"id": _PAYMENT_ID})

    assert _factuur(mailed) is None, "an invoice states that money was received"


def test_the_founder_is_warned_the_factuur_is_not_yet_legally_valid(
    client: TestClient, data_dir, sent, mailed, monkeypatch
) -> None:
    """A placeholder BTW-id makes the document invalid; that warning repeats every time."""
    monkeypatch.delenv("BILLING_SELLER_BTW", raising=False)
    monkeypatch.delenv("BILLING_SELLER_ADDRESS", raising=False)
    _mollie(monkeypatch, FakeMollie())

    client.post("/api/mollie/webhook", data={"id": _PAYMENT_ID})

    assert "NIET RECHTSGELDIG" in sent[0]
    assert "BILLING_SELLER_BTW" in sent[0]


def test_the_warning_stops_once_the_real_details_are_set(
    client: TestClient, data_dir, sent, mailed, monkeypatch
) -> None:
    monkeypatch.setenv("BILLING_SELLER_BTW", "NL863455324B01")
    monkeypatch.setenv("BILLING_SELLER_ADDRESS", "Voorbeeldstraat 1, 1234 AB Amsterdam")
    _mollie(monkeypatch, FakeMollie())

    client.post("/api/mollie/webhook", data={"id": _PAYMENT_ID})

    assert "NIET RECHTSGELDIG" not in sent[0]
    assert "Factuur 2026-0001 verstuurd" in sent[0]


def test_a_failing_factuur_does_not_fail_the_paid_webhook(
    client: TestClient, data_dir, sent, mailed, monkeypatch
) -> None:
    """Mollie retries a non-200. Retrying a payment we already banked helps nobody.

    Stronger than a 200: the failure must be contained INSIDE handle_webhook, or it skips
    the event log and the founder ping that says a subscription just started.
    """
    from app import invoice

    monkeypatch.setattr(invoice, "send", lambda **kw: 1 / 0)
    fake = _mollie(monkeypatch, FakeMollie())

    resp = client.post("/api/mollie/webhook", data={"id": _PAYMENT_ID})

    assert resp.status_code == 200
    assert len(fake.subscription_creates()) == 1, "the subscription still happened"
    (event,) = _webhook_events(data_dir)
    assert event["action"] == "subscription_created", "the event was still logged"
    assert event["invoice_reason"].startswith("ZeroDivisionError")
    assert "abonnement gestart" in sent[0], "the founder still hears about the subscription"
    assert "GEEN factuur verstuurd" in sent[0], "and about the factuur that did not go out"
