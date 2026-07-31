"""Offline tests for the missed-call catcher: TwiML shape, signature gating, and the
WhatsApp follow-up (template vs freeform, and the not-delivered founder alert)."""

from __future__ import annotations

import pytest

from app import notify
from app.channels import voice_missed


class _InlineThread:
    """Runs the thread target synchronously so tests can assert on its effects."""

    def __init__(self, target, args=(), daemon=None):
        self._target, self._args = target, args

    def start(self) -> None:
        self._target(*self._args)


@pytest.fixture
def inline_threads(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(voice_missed.threading, "Thread", _InlineThread)


@pytest.fixture
def owner_inbox(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    inbox: list[str] = []
    monkeypatch.setattr(notify, "owner", lambda text, chat_id=None: inbox.append(text) or True)
    return inbox


@pytest.fixture
def unsigned_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TWILIO_AUTH_TOKEN", raising=False)
    monkeypatch.setenv("WHATSAPP_ALLOW_UNSIGNED", "1")


def test_rejects_unsigned_by_default(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("TWILIO_AUTH_TOKEN", raising=False)
    monkeypatch.delenv("WHATSAPP_ALLOW_UNSIGNED", raising=False)
    _, status = voice_missed.handle("https://x/voice/missed", None, {"From": "+31612345678"})
    assert status == 403


def test_answers_in_dutch_and_sends_freeform_followup(
    unsigned_ok, inline_threads, owner_inbox, monkeypatch
):
    monkeypatch.delenv("WHATSAPP_MISSED_CALL_CONTENT_SID", raising=False)
    sent: list[tuple[str, str]] = []
    monkeypatch.setattr(voice_missed, "send", lambda to, text: sent.append((to, text)) or "SM1")

    body, status = voice_missed.handle("https://x/voice/missed", None, {"From": "+31612345678"})

    assert status == 200
    assert 'language="nl-NL"' in body and "<Hangup/>" in body
    assert sent and sent[0][0] == "+31612345678"
    assert any("WhatsApp-opvang verstuurd" in m for m in owner_inbox)


def test_uses_template_when_content_sid_configured(
    unsigned_ok, inline_threads, owner_inbox, monkeypatch
):
    monkeypatch.setenv("WHATSAPP_MISSED_CALL_CONTENT_SID", "HX123")
    sent: list[tuple[str, str, dict]] = []
    monkeypatch.setattr(
        voice_missed,
        "send_template",
        lambda to, sid, variables=None: sent.append((to, sid, variables)) or "SM1",
    )

    voice_missed.handle("https://x/voice/missed", None, {"From": "+31612345678"})

    assert sent and sent[0][1] == "HX123"


def test_failed_followup_alerts_founder_to_call_back(
    unsigned_ok, inline_threads, owner_inbox, monkeypatch
):
    monkeypatch.delenv("WHATSAPP_MISSED_CALL_CONTENT_SID", raising=False)

    def boom(to: str, text: str) -> str:
        raise RuntimeError("63016: not a WhatsApp user")

    monkeypatch.setattr(voice_missed, "send", boom)
    body, status = voice_missed.handle("https://x/voice/missed", None, {"From": "+3120123456"})

    assert status == 200  # the caller still hears the spoken message
    assert any("NIET afgeleverd" in m and "terugbellen" in m for m in owner_inbox)


def test_anonymous_caller_gets_spoken_fallback_only(unsigned_ok, inline_threads, monkeypatch):
    called: list[str] = []
    monkeypatch.setattr(voice_missed, "send", lambda *a: called.append("x"))
    body, status = voice_missed.handle("https://x/voice/missed", None, {"From": "anonymous"})
    assert status == 200
    assert "WhatsApp-bericht" in body
    assert called == []
