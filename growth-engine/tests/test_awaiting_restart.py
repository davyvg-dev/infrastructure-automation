"""Restart survival for founder-in-the-loop state. Offline — Telegram, store,
and generation are monkeypatched; nothing touches queue.json.

Guards the 2026-08-12 audit defect 8 fixes: rewrite/recording waits live on the
draft record (not chat_data), and delivered-but-undecided drafts are resurfaced
on startup instead of dying in Telegram scroll-back.
"""

from __future__ import annotations

import asyncio

import pytest

from src import bot


class FakeMessage:
    def __init__(self, text=""):
        self.text = text
        self.replies: list[str] = []

    async def reply_text(self, text, **kwargs):
        self.replies.append(text)


class FakeContext:
    chat_data: dict = {}


def make_draft(draft_id="20260813-test", **extra):
    return {
        "id": draft_id,
        "pillar": "problem",
        "topic": "gemiste oproepen",
        "status": "pending",
        "variants": {"x": "post voor x"},
        **extra,
    }


@pytest.fixture()
def queue(monkeypatch):
    """A fake store: load_queue serves `drafts`, update_draft merges into them."""
    drafts: list[dict] = []
    calls: list[tuple[str, dict]] = []

    def fake_update(draft_id, **fields):
        calls.append((draft_id, fields))
        for d in drafts:
            if d["id"] == draft_id:
                d.update(fields)
                return dict(d)
        return None

    monkeypatch.setattr(bot.store, "load_queue", lambda: [dict(d) for d in drafts])
    monkeypatch.setattr(bot.store, "update_draft", fake_update)
    monkeypatch.setattr(bot.formatting, "preview", lambda d: "preview")
    monkeypatch.setattr(bot.formatting, "pending_reel", lambda d: False)
    return drafts, calls


def test_note_rewrites_awaiting_draft_with_empty_chat_data(monkeypatch, queue):
    """The rewrite wait survives a restart: chat_data is empty (fresh process),
    the store flag alone routes the note to the right draft."""
    drafts, calls = queue
    drafts.append(make_draft(awaiting="note"))
    monkeypatch.setattr(
        bot.generate, "regenerate_variant", lambda draft, platform, note: f"rewritten: {note}"
    )

    update = type("U", (), {"message": FakeMessage("punchier hook")})()
    asyncio.run(bot.on_note(update, FakeContext()))

    fields = {k: v for _, f in calls for k, v in f.items()}
    assert fields["variants"] == {"x": "rewritten: punchier hook"}
    assert fields["awaiting"] is None  # cleared — a second text won't rewrite again


def test_note_ignored_when_nothing_awaiting(monkeypatch, queue):
    drafts, calls = queue
    drafts.append(make_draft())  # pending, but no rewrite requested

    called = []
    monkeypatch.setattr(
        bot.generate, "regenerate_variant", lambda *a: called.append(a) or "nope"
    )
    update = type("U", (), {"message": FakeMessage("random chat message")})()
    asyncio.run(bot.on_note(update, FakeContext()))

    assert not called and not calls


def test_note_skips_decided_drafts(monkeypatch, queue):
    """A stale awaiting flag on an already-approved draft must not eat text."""
    drafts, calls = queue
    drafts.append(make_draft(awaiting="note", status="approved"))

    update = type("U", (), {"message": FakeMessage("note")})()
    asyncio.run(bot.on_note(update, FakeContext()))

    assert not calls


def test_post_init_resends_stuck_and_resurfaces_delivered(monkeypatch, queue):
    drafts, _ = queue
    drafts.append(make_draft("stuck"))  # never reached Telegram
    drafts.append(make_draft("open", delivered_at="2026-08-12T09:00:00"))
    drafts.append(make_draft("done", delivered_at="2026-08-12T09:00:00", status="posted"))

    monkeypatch.setattr(bot, "env", lambda key, **kw: "1")
    monkeypatch.setattr(bot, "schedule_jobs", lambda app, chat_id: None)

    delivered = []

    async def fake_deliver(app, chat_id, draft):
        delivered.append(draft["id"])

    monkeypatch.setattr(bot, "_deliver_draft", fake_deliver)

    sent = []

    class FakeBot:
        async def send_message(self, chat_id=None, text=None, **kwargs):
            sent.append((text, kwargs.get("reply_markup")))

    app = type("A", (), {"bot": FakeBot()})()
    asyncio.run(bot._post_init(app))

    assert delivered == ["stuck"]  # full redelivery for the one that never arrived
    resurfaced = [s for s in sent if s[1] is not None]
    assert len(resurfaced) == 1  # buttons re-sent for the open draft, not the posted one
    assert any("1 draft(s) still await" in (s[0] or "") for s in sent)
