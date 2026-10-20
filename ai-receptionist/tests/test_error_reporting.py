"""PII-scrubbed error reporting to the founder: no customer text leaks, phone/email are
masked, and a crash loop is deduped. Offline — Telegram is stubbed, nothing is sent."""

from __future__ import annotations

import pytest

from app import notify


@pytest.fixture
def sent(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Capture what owner_exception would send, and start from an empty dedup cache."""
    captured: list[str] = []
    monkeypatch.setattr(
        notify, "owner", lambda text, chat_id=None: bool(captured.append(text)) or True
    )
    notify._err_last_sent.clear()
    return captured


def test_report_omits_local_variable_values(sent: list[str]) -> None:
    # A customer's message lives only in a local variable at crash time. traceback formats the
    # stack, type, and message — never local values — so the secret must not appear.
    secret = "customer said: my card is 4111 1111 1111 1111"

    def crash() -> None:
        user_text = secret  # noqa: F841 — deliberately a local holding customer PII
        raise ValueError("upstream failed")

    try:
        crash()
    except ValueError as exc:
        notify.owner_exception(exc, context="chat")

    assert sent, "an unhandled error should be reported"
    assert secret not in sent[0]
    assert "customer said" not in sent[0]
    assert "ValueError" in sent[0] and "upstream failed" in sent[0], "type+message must survive"


def test_masks_phone_and_email_that_leaked_into_the_message(sent: list[str]) -> None:
    try:
        raise RuntimeError("lookup failed for +31 6 12345678 / jan@example.com")
    except RuntimeError as exc:
        notify.owner_exception(exc, context="chat")

    assert sent
    assert "+31 6 12345678" not in sent[0] and "jan@example.com" not in sent[0]
    assert "[phone]" in sent[0] and "[email]" in sent[0]


def test_dedup_suppresses_a_second_identical_crash(sent: list[str]) -> None:
    def crash() -> None:
        raise ValueError("same site")

    for _ in range(2):
        try:
            crash()
        except ValueError as exc:
            notify.owner_exception(exc, context="chat")

    assert len(sent) == 1, "the repeat at the same site must be suppressed within the window"


def test_dedup_still_lets_a_different_site_through(sent: list[str]) -> None:
    try:
        raise ValueError("site one")
    except ValueError as exc:
        notify.owner_exception(exc, context="chat")
    try:
        raise ValueError("site two")
    except ValueError as exc:
        notify.owner_exception(exc, context="chat")

    assert len(sent) == 2, "distinct crash sites are distinct signatures — both report"
