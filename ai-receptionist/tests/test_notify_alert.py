"""Unit-failure alerts (systemd OnFailure -> kk-alert@ -> app.notify alert): the journal
tail travels with the alert, PII is scrubbed, and the CLI exit code is honest about
delivery. Offline — journalctl and delivery channels are stubbed, nothing is sent."""

from __future__ import annotations

import pytest

from app import notify


@pytest.fixture
def reports(monkeypatch: pytest.MonkeyPatch) -> list[tuple[str, str]]:
    """Capture (subject, text) handed to owner_report, reporting successful delivery."""
    captured: list[tuple[str, str]] = []
    monkeypatch.setattr(
        notify,
        "owner_report",
        lambda subject, text: (captured.append((subject, text)), {"telegram": True})[1],
    )
    return captured


def test_alert_carries_unit_name_and_journal_tail(
    monkeypatch: pytest.MonkeyPatch, reports: list[tuple[str, str]]
) -> None:
    monkeypatch.setattr(notify, "_journal_tail", lambda unit: "Traceback: boom")
    notify.unit_failed_alert("ai-receptionist-digest.service")
    (subject, text) = reports[0]
    assert "ai-receptionist-digest.service" in subject
    assert "ai-receptionist-digest.service" in text
    assert "Traceback: boom" in text


def test_alert_redacts_pii_from_the_journal(
    monkeypatch: pytest.MonkeyPatch, reports: list[tuple[str, str]]
) -> None:
    # A digest failure can echo customer contact details into the journal; the alert goes
    # out through Telegram/e-mail and must carry the masked form only.
    monkeypatch.setattr(
        notify, "_journal_tail", lambda unit: "lead +31 6 12345678 jan@example.com lost"
    )
    notify.unit_failed_alert("ai-receptionist-digest.service")
    (_, text) = reports[0]
    assert "+31 6 12345678" not in text and "jan@example.com" not in text
    assert "[phone]" in text and "[email]" in text


def test_journal_tail_survives_missing_journalctl(monkeypatch: pytest.MonkeyPatch) -> None:
    def no_journalctl(*args, **kwargs):
        raise FileNotFoundError("journalctl")

    monkeypatch.setattr(notify.subprocess, "run", no_journalctl)
    assert "journal unavailable" in notify._journal_tail("x.service")


def test_cli_exit_codes_reflect_delivery(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(notify, "_journal_tail", lambda unit: "boom")

    monkeypatch.setattr(notify, "owner_report", lambda s, t: {"telegram": True, "email": False})
    assert notify.main(["app.notify", "alert", "x.service"]) == 0

    monkeypatch.setattr(notify, "owner_report", lambda s, t: {"telegram": False, "email": False})
    assert notify.main(["app.notify", "alert", "x.service"]) == 1

    assert notify.main(["app.notify", "alert"]) == 2
