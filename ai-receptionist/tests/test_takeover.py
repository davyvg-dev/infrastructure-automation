"""Offline tests for WhatsApp takeover: pause/relay/release state, owner commands, and the
auto-release backstop. No Telegram, no Twilio — both seams are monkeypatched."""

from __future__ import annotations

import json
from datetime import datetime, timedelta

import pytest

from app import notify, sessions, takeover
from app.channels import whatsapp
from app.settings import active_client


@pytest.fixture
def owner_inbox(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Capture notify.owner messages; owner() 'delivers' unless the test empties the box."""
    inbox: list[str] = []

    def fake_owner(text: str, chat_id: str | None = None) -> bool:
        inbox.append(text)
        return True

    monkeypatch.setattr(notify, "owner", fake_owner)
    return inbox


@pytest.fixture
def wa_outbox(monkeypatch: pytest.MonkeyPatch) -> list[tuple[str, str]]:
    outbox: list[tuple[str, str]] = []
    monkeypatch.setattr(whatsapp, "send", lambda to, text: outbox.append((to, text)) or "SM123")
    return outbox


SENDER = "whatsapp:+31612345678"


def test_not_paused_records_contact_and_lets_bot_answer(data_dir, owner_inbox):
    assert takeover.handle_inbound(SENDER, "hallo, mijn cv-ketel doet raar") is False
    state = json.loads((data_dir / "takeover.json").read_text())
    assert state["contacts"][0]["sender"] == SENDER
    assert owner_inbox == []  # no takeover, no relay noise


def test_takeover_relay_and_release_roundtrip(data_dir, owner_inbox, wa_outbox):
    takeover.handle_inbound(SENDER, "kan er iemand morgen komen?")

    listing = takeover.handle_owner_command("wa")
    assert "+31612345678" in listing

    confirm = takeover.handle_owner_command("takeover 1")
    assert "Overgenomen" in confirm

    # Customer message now relays to the founder instead of reaching the bot.
    assert takeover.handle_inbound(SENDER, "het lekt behoorlijk") is True
    assert any("het lekt behoorlijk" in m for m in owner_inbox)

    # Founder plain text goes out over WhatsApp to the taken-over customer.
    reply = takeover.handle_owner_command("Ik kom morgen om 9u langs")
    assert "+31612345678" in reply
    assert wa_outbox == [(SENDER, "Ik kom morgen om 9u langs")]

    # Release hands the conversation back (and resets the session).
    sessions._STORE[f"{active_client()}:whatsapp:{SENDER}"] = [{"role": "user", "content": "x"}]
    released = takeover.handle_owner_command("release")
    assert "terug naar de bot" in released
    assert f"{active_client()}:whatsapp:{SENDER}" not in sessions._STORE
    assert takeover.handle_inbound(SENDER, "nog een vraag") is False


def test_owner_text_without_target_is_not_sent(data_dir, owner_inbox, wa_outbox):
    reply = takeover.handle_owner_command("dit is nergens heen")
    assert "nergens heen gestuurd" in reply
    assert wa_outbox == []


def test_takeover_by_number_and_release_all(data_dir, owner_inbox, wa_outbox):
    takeover.handle_inbound(SENDER, "offerte graag")
    assert "Overgenomen" in takeover.handle_owner_command("takeover +31 6 12 34 56 78")
    assert takeover.handle_inbound(SENDER, "hallo?") is True
    assert "terug naar de bot" in takeover.handle_owner_command("release all")
    assert takeover.handle_inbound(SENDER, "hallo?") is False


def test_auto_release_after_idle(data_dir, owner_inbox):
    takeover.handle_inbound(SENDER, "eerste bericht")
    takeover.handle_owner_command("takeover 1")

    # Backdate the pause beyond the auto-release window.
    path = data_dir / "takeover.json"
    state = json.loads(path.read_text())
    stale = (datetime.now() - timedelta(hours=13)).isoformat(timespec="seconds")
    for entry in state["paused"].values():
        entry["last"] = stale
    path.write_text(json.dumps(state))

    assert takeover.handle_inbound(SENDER, "ben je er nog?") is False
    assert any("automatisch beëindigd" in m for m in owner_inbox)


def test_relay_failure_releases_so_customer_is_not_stranded(
    data_dir, wa_outbox, monkeypatch: pytest.MonkeyPatch
):
    takeover.handle_inbound(SENDER, "eerste bericht")
    takeover.handle_owner_command("takeover 1")
    # Telegram down: the relay can't reach the founder, so the bot must answer again.
    monkeypatch.setattr(notify, "owner", lambda text, chat_id=None: False)
    assert takeover.handle_inbound(SENDER, "hallo, is daar iemand?") is False
    assert takeover.handle_inbound(SENDER, "vervolg") is False  # released, stays released


def test_send_failure_is_reported_to_founder(data_dir, owner_inbox, monkeypatch):
    takeover.handle_inbound(SENDER, "eerste bericht")
    takeover.handle_owner_command("takeover 1")

    def boom(to: str, text: str) -> str:
        raise RuntimeError("Twilio zegt nee")

    monkeypatch.setattr(whatsapp, "send", boom)
    reply = takeover.handle_owner_command("dit komt niet aan")
    assert "NIET afgeleverd" in reply
