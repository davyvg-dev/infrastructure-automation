"""POST /api/resend/webhook: svix signature verification + bounce/complaint handling.
Offline — signatures are computed locally with the same scheme svix documents."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time

import pytest
from fastapi.testclient import TestClient

from app import cursus, server

SECRET = "whsec_" + base64.b64encode(b"testsleutel-0123456789abcdef").decode()


def _signed_headers(body: bytes, *, secret: str = SECRET, ts: int | None = None) -> dict:
    ts = int(time.time()) if ts is None else ts
    msg_id = "msg_test"
    key = base64.b64decode(secret.split("_", 1)[-1])
    signed = f"{msg_id}.{ts}.".encode() + body
    sig = base64.b64encode(hmac.new(key, signed, hashlib.sha256).digest()).decode()
    return {
        "svix-id": msg_id,
        "svix-timestamp": str(ts),
        "svix-signature": f"v1,{sig}",
    }


def _event(etype: str, to: list[str], **data) -> bytes:
    return json.dumps({"type": etype, "data": {"to": to, **data}}).encode()


@pytest.fixture
def client(data_dir, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("RESEND_WEBHOOK_SECRET", SECRET)
    return TestClient(server.app)


def test_unconfigured_secret_is_503(data_dir, monkeypatch) -> None:
    monkeypatch.delenv("RESEND_WEBHOOK_SECRET", raising=False)
    body = _event("email.bounced", ["jan@bedrijf.nl"])
    resp = TestClient(server.app).post(
        "/api/resend/webhook", content=body, headers=_signed_headers(body)
    )
    assert resp.status_code == 503


def test_valid_permanent_bounce_halts_without_suppression(client: TestClient, data_dir) -> None:
    cursus.add("jan@bedrijf.nl")
    body = _event("email.bounced", ["jan@bedrijf.nl"], bounce={"type": "Permanent"})
    resp = client.post("/api/resend/webhook", content=body, headers=_signed_headers(body))
    assert resp.status_code == 200
    sub = cursus.load()["subscribers"]["jan@bedrijf.nl"]
    assert "bounced" in sub
    path = data_dir / "suppression.txt"
    assert not path.exists() or "jan@bedrijf.nl" not in path.read_text()


def test_temporary_bounce_is_a_noop(client: TestClient, data_dir) -> None:
    cursus.add("jan@bedrijf.nl")
    body = _event("email.bounced", ["jan@bedrijf.nl"], bounce={"type": "Temporary"})
    resp = client.post("/api/resend/webhook", content=body, headers=_signed_headers(body))
    assert resp.status_code == 200
    assert "bounced" not in cursus.load()["subscribers"]["jan@bedrijf.nl"]


def test_complaint_halts_and_suppresses_even_unknown_addresses(
    client: TestClient, data_dir
) -> None:
    # A spam complaint is a consent signal, also when the address never took the course
    # (e.g. the paid-welcome mail): it must land on the opt-out record either way.
    cursus.add("jan@bedrijf.nl")
    body = _event("email.complained", ["Jan@Bedrijf.nl", "koper@extern.nl"])
    resp = client.post("/api/resend/webhook", content=body, headers=_signed_headers(body))
    assert resp.status_code == 200
    assert "unsubscribed" in cursus.load()["subscribers"]["jan@bedrijf.nl"]
    listed = (data_dir / "suppression.txt").read_text().lower()
    assert "jan@bedrijf.nl" in listed and "koper@extern.nl" in listed


def test_tampered_body_is_401(client: TestClient, data_dir) -> None:
    cursus.add("jan@bedrijf.nl")
    body = _event("email.bounced", ["jan@bedrijf.nl"], bounce={"type": "Permanent"})
    headers = _signed_headers(body)
    tampered = body.replace(b"jan@", b"eva@")
    resp = client.post("/api/resend/webhook", content=tampered, headers=headers)
    assert resp.status_code == 401
    assert "bounced" not in cursus.load()["subscribers"]["jan@bedrijf.nl"]


def test_stale_timestamp_is_401(client: TestClient, data_dir) -> None:
    body = _event("email.bounced", ["jan@bedrijf.nl"], bounce={"type": "Permanent"})
    headers = _signed_headers(body, ts=int(time.time()) - 3600)
    resp = client.post("/api/resend/webhook", content=body, headers=headers)
    assert resp.status_code == 401


def test_other_event_types_are_accepted_and_ignored(client: TestClient, data_dir) -> None:
    body = _event("email.delivered", ["jan@bedrijf.nl"])
    resp = client.post("/api/resend/webhook", content=body, headers=_signed_headers(body))
    assert resp.status_code == 200
    assert not (data_dir / "suppression.txt").exists()
