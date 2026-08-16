"""Analyst store: PII redaction before analysis, insight round-trip, backlog aggregation. Offline."""

from __future__ import annotations

from datetime import datetime, timedelta

from app import analytics, oversight

_ZONWERING_INSIGHT = {
    "intent": "out-of-scope enquiry",
    "topics": ["zonwering"],
    "resolved": True,
    "escalated": False,
    "escalation_reason": "",
    "unanswered_questions": [],
    "out_of_scope_requests": ["zonwering"],
    "sentiment": "neu",
    "language": "nl",
    "customer_type": "new",
    "lead_captured": False,
    "booking_made": False,
    "est_job_value_eur": 0,
    "upsell_signals": ["out_of_scope:zonwering"],
    "quality_flags": [],
}


def _record_zonwering_turn():
    analytics.record_turn(
        client="demo-test",
        channel="web",
        user_id="+31600000009",
        user_text="Doen jullie ook zonwering?",
        reply="Nee, dat is een andere vakman.",
        input_tokens=50,
        output_tokens=10,
        model="claude-opus-4-8",
        tools=[],
    )


def test_redaction_masks_phone_and_email():
    red = oversight.redact("bel 06-12345678 of mail jan@voorbeeld.nl")
    assert "06-12345678" not in red and "jan@voorbeeld.nl" not in red
    assert "[phone]" in red and "[email]" in red


def test_settled_conversation_is_queued_then_dequeued(data_dir):
    _record_zonwering_turn()
    future = (datetime.now() + timedelta(minutes=1)).isoformat(timespec="seconds")

    pending = analytics.pending_for_analysis(future)
    assert len(pending) == 1 and pending[0][1] == "demo-test"
    key = pending[0][0]
    convo = analytics.transcript(key)
    assert convo and "zonwering" in convo[0]["user"]

    analytics.save_insight(key, "demo-test", "claude-haiku-4-5", _ZONWERING_INSIGHT)
    assert not analytics.pending_for_analysis(future), "session should de-queue once analysed"
    rows = analytics.insights_for_client("demo-test")
    assert len(rows) == 1 and rows[0]["out_of_scope_json"] == ["zonwering"]


def test_backlog_aggregates_upsell_signal(data_dir):
    _record_zonwering_turn()
    future = (datetime.now() + timedelta(minutes=1)).isoformat(timespec="seconds")
    key = analytics.pending_for_analysis(future)[0][0]
    analytics.save_insight(key, "demo-test", "claude-haiku-4-5", _ZONWERING_INSIGHT)

    view = oversight.backlog("demo-test")
    assert "out_of_scope:zonwering" in view
