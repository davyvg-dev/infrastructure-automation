"""Offline tests for the outreach sequence ledger.

The expensive mistake in this module is not a crash, it is a silent double-send to a live
prospect -- or a breakup mail to someone who already said yes. Both are decided by
due_touch(), so that is what most of this file pins down.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta

import pytest

from scripts import sequence
from scripts.sequence import Record

T0 = datetime(2026, 7, 29, 12, 0, tzinfo=UTC)


def rec(touch_days: dict[int, int], **kw) -> Record:
    """A record whose touch N went out `touch_days[N]` days after T0."""
    return Record(
        touches={
            n: {"at": (T0 + timedelta(days=d)).isoformat(), "message_id": f"<{n}@test>"}
            for n, d in touch_days.items()
        },
        **kw,
    )


def test_unmailed_prospect_is_due_for_touch_one():
    assert sequence.due_touch(None, T0) == 1


def test_touch_two_waits_three_days():
    r = rec({1: 0})
    assert sequence.due_touch(r, T0 + timedelta(days=2)) is None
    assert sequence.due_touch(r, T0 + timedelta(days=3)) == 2


def test_schedule_anchors_on_touch_one_not_on_the_previous_touch():
    """Touch 2 slipping to day 5 must not push touch 3 out to day 12; the sequence is a
    calendar off the first mail, not a chain of relative delays."""
    r = rec({1: 0, 2: 5})
    assert sequence.due_touch(r, T0 + timedelta(days=7)) == 3


def test_a_reply_halts_the_sequence():
    r = rec({1: 0}, replied=T0.isoformat())
    assert sequence.due_touch(r, T0 + timedelta(days=30)) is None


def test_an_opt_out_halts_the_sequence():
    r = rec({1: 0}, stopped=T0.isoformat())
    assert sequence.due_touch(r, T0 + timedelta(days=30)) is None


def test_sequence_ends_after_the_last_touch():
    r = rec({1: 0, 2: 3, 3: 7, 4: 14})
    assert sequence.due_touch(r, T0 + timedelta(days=90)) is None


def test_v1_flat_ledger_migrates_to_touch_one(tmp_path):
    """The six mails that left on 2026-07-29 were recorded as {slug: iso}. They must come
    back as touch 1 already sent -- not as unmailed, which would re-mail them."""
    path = tmp_path / "sent.json"
    path.write_text(json.dumps({"aj-dakwerken": T0.isoformat()}))

    ledger = sequence.load(path)

    assert ledger["aj-dakwerken"].last_touch == 1
    assert sequence.due_touch(ledger["aj-dakwerken"], T0 + timedelta(days=3)) == 2


def test_ledger_round_trips(tmp_path):
    path = tmp_path / "sent.json"
    ledger = {"meijer": rec({1: 0, 2: 3}, replied=T0.isoformat())}
    sequence.save(ledger, path)

    back = sequence.load(path)

    assert back["meijer"].last_touch == 2
    assert back["meijer"].replied == T0.isoformat()
    assert back["meijer"].message_id(1) == "<1@test>"


def test_corrupt_ledger_refuses_rather_than_defaulting_to_empty(tmp_path):
    """An empty ledger reads as "nobody has been mailed"; acting on that re-mails
    everyone. Exiting is the safe failure."""
    path = tmp_path / "sent.json"
    path.write_text("{not json")

    with pytest.raises(SystemExit):
        sequence.load(path)


def test_queue_finishes_open_threads_before_opening_new_ones():
    from scripts.outreach_mail import PROSPECTS

    ledger = {PROSPECTS[0].slug: rec({1: 0})}
    due = sequence.queue(list(PROSPECTS), ledger, T0 + timedelta(days=3))

    assert due[0] == (PROSPECTS[0], 2), "the prospect deepest in the sequence goes first"
    assert all(touch == 1 for _, touch in due[1:])


def test_every_touch_after_the_first_has_copy():
    from scripts.outreach_mail import PROSPECTS

    p = PROSPECTS[0]
    for touch in range(2, sequence.LAST_TOUCH + 1):
        body = sequence.followup_text(p, touch)
        assert p.short in body or "Succes" in body
        assert body.strip().endswith(('stop" en je hoort niets meer.', sequence.SIGNOFF_EMAIL))


def test_suppression_is_idempotent(tmp_path):
    path = tmp_path / "suppression.txt"
    path.write_text("# header\ninfo@example.nl\n")

    assert sequence.suppress("new@example.nl", path) is True
    assert sequence.suppress("INFO@example.nl", path) is False
    assert path.read_text().count("new@example.nl") == 1
