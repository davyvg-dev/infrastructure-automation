"""Ledger honesty in the approval flow. Offline — Telegram, publishers, and the
store are all monkeypatched; nothing posts and nothing touches queue.json.

Guards the 2026-08-12 audit fixes: dry-run approvals must never write
status="posted"/"queued" or fake URLs, and failed pushes must leave a durable
per-platform error on the draft record.
"""

from __future__ import annotations

import asyncio

import pytest

from src import bot


class FakeBot:
    async def send_message(self, chat_id, text, **kwargs):
        pass


class FakeContext:
    bot = FakeBot()


def make_draft():
    return {
        "id": "20260812-test",
        "pillar": "problem",
        "topic": "gemiste oproepen",
        "status": "pending",
        "variants": {"x": "post voor x", "linkedin": "post voor linkedin"},
    }


@pytest.fixture()
def updates(monkeypatch):
    """Capture every store.update_draft call as (fields) dicts; no disk I/O.
    get_draft reflects the accumulated state so the queued-vs-posted guard sees
    what a real store would."""
    calls: list[dict] = []
    state: dict = {}

    def fake_update(draft_id, **fields):
        calls.append(fields)
        state.update(fields)
        return dict(state)

    monkeypatch.setattr(bot.store, "update_draft", fake_update)
    monkeypatch.setattr(bot.store, "get_draft", lambda draft_id: dict(state))
    monkeypatch.setattr(bot.platforms, "auto_platforms", lambda: ["x"])
    monkeypatch.setattr(bot.platforms, "buffer_platforms", lambda: ["linkedin"])
    monkeypatch.setattr(bot.platforms, "draft_platforms", lambda: [])
    monkeypatch.setattr(bot.platforms, "assisted_platforms", lambda: [])
    monkeypatch.setattr(bot, "_media_for", lambda draft, platform: None)
    return calls


def merged(calls):
    out = {}
    for c in calls:
        out.update(c)
    return out


def test_dry_run_never_advances_past_approved(monkeypatch, updates):
    monkeypatch.setattr(bot, "dry_run", lambda: True)
    monkeypatch.setitem(bot._PUBLISHERS, "x", lambda d, t, m: "(dry-run: not actually posted)")
    monkeypatch.setattr(bot.publish_buffer, "queue", lambda p, t: "(dry-run: not queued in Buffer)")

    asyncio.run(bot._approve(FakeContext(), 1, make_draft()))

    fields = merged(updates)
    assert fields.get("dry_run") is True
    assert fields.get("status") == "approved"  # never "posted" or "queued"
    assert "x_url" not in fields
    assert "linkedin_queued" not in fields


def test_live_success_records_posted_and_queued(monkeypatch, updates):
    monkeypatch.setattr(bot, "dry_run", lambda: False)
    monkeypatch.setitem(bot._PUBLISHERS, "x", lambda d, t, m: "https://x.com/i/1")
    monkeypatch.setattr(bot.publish_buffer, "queue", lambda p, t: "goes out later")

    asyncio.run(bot._approve(FakeContext(), 1, make_draft()))

    fields = merged(updates)
    assert fields["x_url"] == "https://x.com/i/1"
    assert fields["linkedin_queued"] == "goes out later"
    assert fields["status"] == "posted"
    assert "dry_run" not in fields


def test_push_failures_leave_durable_error_records(monkeypatch, updates):
    monkeypatch.setattr(bot, "dry_run", lambda: False)

    def boom(*args):
        raise RuntimeError("rate limited")

    monkeypatch.setitem(bot._PUBLISHERS, "x", boom)
    monkeypatch.setattr(bot.publish_buffer, "queue", boom)

    asyncio.run(bot._approve(FakeContext(), 1, make_draft()))

    fields = merged(updates)
    assert "rate limited" in fields["x_error"]
    assert "rate limited" in fields["linkedin_error"]
    assert fields.get("status") == "approved"  # failed pushes never claim posted
