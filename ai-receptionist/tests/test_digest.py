"""Deterministic oversight digest: per-client rollups + analyst signals fold in. Offline."""

from __future__ import annotations

from datetime import datetime, timedelta

from app import analytics, mailer, notify, oversight


def test_cost_model_matches_published_rates():
    # 1M input + 1M output of Haiku = ($1 + $5) * the USD->EUR rate.
    c = oversight.cost_eur({"claude-haiku-4-5": {"input": 1_000_000, "output": 1_000_000}})
    assert round(c, 2) == 5.52


def _seed_two_clients(clients_dir):
    """Acme takes an after-hours message; Smit gets a booking."""
    (clients_dir / "acme-loodgieter.yaml").write_text(
        'business:\n  name: "Acme Loodgieter"\n  type: "loodgieter"\n', encoding="utf-8"
    )
    (clients_dir / "smit-dak.yaml").write_text(
        'business:\n  name: "Smit Dakwerken"\n  type: "dakdekker"\n', encoding="utf-8"
    )
    analytics.record_turn(
        client="acme-loodgieter",
        channel="web",
        user_id="+31600000001",
        user_text="hoi",
        reply="hallo",
        input_tokens=1000,
        output_tokens=200,
        model="claude-opus-4-8",
        after_hours=True,
        tools=[{"name": "take_message", "input": {}, "output": '{"ok": true}'}],
    )
    analytics.record_turn(
        client="smit-dak",
        channel="web",
        user_id="+31600000002",
        user_text="afspraak",
        reply="geboekt",
        input_tokens=2000,
        output_tokens=400,
        model="claude-opus-4-8",
        after_hours=False,
        tools=[
            {
                "name": "book_appointment",
                "input": {},
                "output": '{"ok": true, "confirmation": "X1"}',
            }
        ],
    )


def test_digest_rolls_up_active_bots(data_dir, clients_dir):
    _seed_two_clients(clients_dir)
    text = oversight.build_digest(now=datetime.now(), today=True)
    assert "2/2 bots active" in text
    assert "2 conversations · 1 leads · 1 bookings" in text
    assert "Acme Loodgieter" in text and "1 leads" in text and "100% after-hours" in text
    assert "Smit Dakwerken" in text and "1 booked" in text
    assert "NEEDS ATTENTION" not in text, "a clean window should raise nothing"


def test_analyst_insight_surfaces_in_digest(data_dir, clients_dir):
    _seed_two_clients(clients_dir)
    future = (datetime.now() + timedelta(days=1)).isoformat(timespec="seconds")
    acme_key = next(k for k, s in analytics.pending_for_analysis(future) if s == "acme-loodgieter")
    analytics.save_insight(
        acme_key,
        "acme-loodgieter",
        "claude-haiku-4-5",
        {
            "intent": "spoed",
            "topics": ["lekkage"],
            "resolved": False,
            "escalated": True,
            "escalation_reason": "no slot",
            "unanswered_questions": ["Doen jullie spoed?"],
            "out_of_scope_requests": [],
            "sentiment": "neu",
            "language": "nl",
            "customer_type": "new",
            "lead_captured": True,
            "booking_made": False,
            "est_job_value_eur": 0,
            "upsell_signals": ["after_hours_share_high"],
            "quality_flags": ["refused_in_scope_job"],
        },
    )
    enriched = oversight.build_digest(now=datetime.now(), today=True)
    assert "SIGNALS" in enriched and "Doen jullie spoed?" in enriched, "FAQ gap should surface"
    assert "after_hours_share_high" in enriched, "upsell signal should surface"
    assert "refused_in_scope_job" in enriched and "quality flag" in enriched


# --- Delivery: a nightly report nobody receives is the same as no report ------------------


def _capture(monkeypatch, telegram_ok: bool, mail_ok: bool = True):
    """Stub both channels; return the lists they captured."""
    pings: list[str] = []
    mails: list[tuple[str, str]] = []

    def fake_owner(text, chat_id=None):
        pings.append(text)
        return telegram_ok

    def fake_send(to, subject, text, **kwargs):
        mails.append((to, subject))
        return mail_ok

    monkeypatch.setattr(notify, "owner", fake_owner)
    monkeypatch.setattr(mailer, "send", fake_send)
    return pings, mails


def test_digest_goes_to_telegram_when_it_is_configured(monkeypatch, data_dir, clients_dir):
    monkeypatch.setenv("OWNER_EMAIL", "davy@klantkraan.nl")
    pings, mails = _capture(monkeypatch, telegram_ok=True)

    assert oversight.send_digest() == {"telegram": True, "email": False}
    assert len(pings) == 1
    assert mails == [], "a working chat id must not also produce an e-mail"


def test_digest_falls_back_to_email_when_telegram_is_not_configured(
    monkeypatch, data_dir, clients_dir
):
    """The founder deferred the Telegram chat id, so the timers were delivering nowhere."""
    monkeypatch.setenv("OWNER_EMAIL", "davy@klantkraan.nl")
    pings, mails = _capture(monkeypatch, telegram_ok=False)

    assert oversight.send_digest() == {"telegram": False, "email": True}
    assert mails[0][0] == "davy@klantkraan.nl"
    assert mails[0][1].startswith("Klantkraan dagrapport")


def test_digest_reports_failure_when_neither_channel_is_configured(
    monkeypatch, data_dir, clients_dir
):
    monkeypatch.delenv("OWNER_EMAIL", raising=False)
    _capture(monkeypatch, telegram_ok=False)

    assert oversight.send_digest() == {"telegram": False, "email": False}


def test_a_report_too_long_for_telegram_goes_by_email_instead(monkeypatch):
    monkeypatch.setenv("OWNER_EMAIL", "davy@klantkraan.nl")
    pings, mails = _capture(monkeypatch, telegram_ok=True)

    result = notify.owner_report("lang rapport", "x" * (notify._TELEGRAM_LIMIT + 1))

    assert result == {"telegram": False, "email": True}
    assert pings == [], "Telegram would reject it outright; do not even try"


def test_an_over_long_report_is_truncated_rather_than_dropped(monkeypatch):
    """No mailbox configured and too long to send whole: a cut-off digest beats silence."""
    monkeypatch.delenv("OWNER_EMAIL", raising=False)
    pings, _ = _capture(monkeypatch, telegram_ok=True)

    result = notify.owner_report("lang rapport", "x" * (notify._TELEGRAM_LIMIT + 500))

    assert result["telegram"] is True
    assert len(pings[0]) <= notify._TELEGRAM_LIMIT and "afgekapt" in pings[0]
