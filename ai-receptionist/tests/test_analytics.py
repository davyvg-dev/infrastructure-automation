"""Per-client capture store: 2-turn rollups, hashed user ids, AVG transcript retention. Offline."""

from __future__ import annotations

from datetime import datetime, timedelta

from app import analytics


def test_closed_day_counts_as_after_hours():
    # A day with no configured opening hours is a closed day -> after-hours.
    assert analytics.is_after_hours({"business": {}, "hours": {}})


def test_two_turns_roll_up_into_one_session(data_dir):
    common = dict(
        client="acme-loodgieter", channel="web", user_id="+31600000000", model="claude-opus-4-8"
    )
    analytics.record_turn(
        **common,
        user_text="hi",
        reply="hello",
        input_tokens=100,
        output_tokens=20,
        tools=[],
        after_hours=True,
    )
    analytics.record_turn(
        **common,
        user_text="book me in",
        reply="booked!",
        input_tokens=200,
        output_tokens=40,
        after_hours=False,
        tools=[
            {
                "name": "book_appointment",
                "input": {},
                "output": '{"ok": true, "confirmation": "AB12"}',
            }
        ],
    )

    sess = analytics.load_session("acme-loodgieter", "web", "+31600000000")
    assert sess is not None
    assert sess["turns"] == 2
    assert sess["outcome"] == "booked", "a booking tool call should escalate the outcome"
    assert (sess["input_tokens"], sess["output_tokens"]) == (300, 60)
    assert sess["after_hours_turns"] == 1


def test_user_id_is_stored_hashed(data_dir):
    analytics.record_turn(
        client="acme-loodgieter",
        channel="web",
        user_id="+31600000000",
        user_text="hi",
        reply="hello",
        input_tokens=1,
        output_tokens=1,
        model="claude-opus-4-8",
        tools=[],
        after_hours=False,
    )
    sess = analytics.load_session("acme-loodgieter", "web", "+31600000000")
    assert "+31600000000" not in sess["session_key"], "raw phone number must never be stored"


def test_retention_purges_old_transcripts_but_keeps_rollup(data_dir):
    analytics.record_turn(
        client="acme-loodgieter",
        channel="web",
        user_id="+31600000000",
        user_text="hi",
        reply="hello",
        input_tokens=1,
        output_tokens=1,
        model="claude-opus-4-8",
        tools=[],
        after_hours=False,
    )
    # Inject a transcript turn older than the retention window.
    conn = analytics._connect()
    try:
        old_ts = (datetime.now() - timedelta(days=120)).isoformat(timespec="seconds")
        conn.execute(
            "INSERT INTO turns (session_key, client, ts, user_text, reply) VALUES (?,?,?,?,?)",
            ("acme-loodgieter:web:x", "acme-loodgieter", old_ts, "old", "old"),
        )
        conn.commit()
    finally:
        conn.close()

    before = analytics._count_turns()
    deleted = analytics.purge_transcripts(retention_days=90)
    assert deleted == 1
    assert analytics._count_turns() == before - 1, "only the >90d transcript should be purged"
    # The rollup and the recent turn survive.
    assert analytics.load_session("acme-loodgieter", "web", "+31600000000") is not None
