"""E-mailcursus: ledger, schedule, afmeldlink tokens, sending, pipeline scoring. Offline —
mailer.send is monkeypatched; the store and pipeline live in throwaway dirs."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from app import cursus, pipeline

T0 = datetime(2026, 8, 13, 8, 0, tzinfo=UTC)


@pytest.fixture
def pipeline_dir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    d = tmp_path / "pipeline"
    monkeypatch.setattr(pipeline, "PIPELINE_DIR", d)
    return d


@pytest.fixture
def sent(monkeypatch: pytest.MonkeyPatch) -> list[dict]:
    """Capture every mailer.send call; the mailer always accepts."""
    calls: list[dict] = []

    def fake_send(to, subject, text, **kwargs):
        calls.append({"to": to, "subject": subject, "text": text, **kwargs})
        return True

    monkeypatch.setattr(cursus.mailer, "send", fake_send)
    return calls


# --- ledger -------------------------------------------------------------------------------


def test_add_normalizes_and_is_idempotent(data_dir):
    a = cursus.add("  Jan@Bedrijf.NL ", name="Jan", source="rekentool", now=T0)
    b = cursus.add("jan@bedrijf.nl", now=T0 + timedelta(days=1))
    assert a["email"] == "jan@bedrijf.nl"
    assert b["opted_in"] == a["opted_in"]  # second signup does not move the anchor
    assert len(cursus.load()["subscribers"]) == 1


def test_add_rejects_non_addresses(data_dir):
    with pytest.raises(ValueError):
        cursus.add("geen-adres", now=T0)


def test_resignup_after_afmelding_is_fresh_consent_but_keeps_history(data_dir):
    cursus.add("jan@bedrijf.nl", now=T0)
    data = cursus.load()
    data["subscribers"]["jan@bedrijf.nl"]["lessons"] = {"1": {"at": cursus._iso(T0)}}
    cursus.save(data)
    cursus.stop("jan@bedrijf.nl", now=T0 + timedelta(days=1))
    sub = cursus.add("jan@bedrijf.nl", now=T0 + timedelta(days=30))
    assert "unsubscribed" not in sub
    assert sub["lessons"] == {"1": {"at": cursus._iso(T0)}}  # no second lesson 1
    assert sub["opted_in"] == cursus._iso(T0 + timedelta(days=30))


def test_corrupt_store_exits_instead_of_reading_empty(data_dir):
    cursus.cursus_dir().mkdir(parents=True)
    cursus.store_path().write_text("{niet json", encoding="utf-8")
    with pytest.raises(SystemExit):
        cursus.load()


# --- schedule -----------------------------------------------------------------------------


def test_schedule_walks_lessons_in_order(data_dir):
    sub = cursus.add("jan@bedrijf.nl", now=T0)
    assert cursus.due_lesson(sub, T0) == 1
    sub["lessons"] = {"1": {"at": cursus._iso(T0)}}
    assert cursus.due_lesson(sub, T0 + timedelta(days=1)) is None
    assert cursus.due_lesson(sub, T0 + timedelta(days=2)) == 2


def test_backlog_yields_one_lesson_not_a_burst(data_dir):
    sub = cursus.add("jan@bedrijf.nl", now=T0)
    # Timer was dead for two weeks: everything is overdue, but only lesson 1 comes out.
    assert cursus.due_lesson(sub, T0 + timedelta(days=14)) == 1


def test_halt_states_stop_the_schedule(data_dir):
    cursus.add("jan@bedrijf.nl", now=T0)
    cursus.stop("jan@bedrijf.nl")
    assert cursus.due_lesson(cursus.load()["subscribers"]["jan@bedrijf.nl"]) is None
    cursus.add("piet@bedrijf.nl", now=T0)
    cursus.stop("piet@bedrijf.nl", bounced=True)
    assert cursus.due_lesson(cursus.load()["subscribers"]["piet@bedrijf.nl"]) is None


# --- afmeldlink ---------------------------------------------------------------------------


def test_token_roundtrip_and_tamper(data_dir, monkeypatch):
    monkeypatch.setenv("CURSUS_SECRET", "testgeheim")
    tok = cursus.token("jan@bedrijf.nl")
    assert cursus.verify_token("Jan@Bedrijf.nl ", tok)  # normalization on both sides
    assert not cursus.verify_token("jan@bedrijf.nl", tok[:-1] + "0")
    assert not cursus.verify_token("piet@bedrijf.nl", tok)
    assert tok in cursus.unsubscribe_url("jan@bedrijf.nl")


def test_secret_autogenerates_once(data_dir, monkeypatch):
    monkeypatch.delenv("CURSUS_SECRET", raising=False)
    first = cursus.token("jan@bedrijf.nl")
    assert (cursus.cursus_dir() / "secret").exists()
    assert cursus.token("jan@bedrijf.nl") == first


# --- sending ------------------------------------------------------------------------------


def test_send_due_sends_records_and_carries_unsubscribe(data_dir, sent):
    cursus.add("jan@bedrijf.nl", name="Jan Jansen", now=T0)
    report = cursus.send_due(now=T0)
    assert report["sent"] == [("jan@bedrijf.nl", 1)]
    call = sent[0]
    assert call["idempotency_key"] == "cursus-jan@bedrijf.nl-les-1"
    assert "List-Unsubscribe" in call["headers"]
    assert cursus.unsubscribe_url("jan@bedrijf.nl") in call["text"]  # footer afmeldlink
    assert "Hoi Jan," in call["text"]
    # Recorded: same run again finds nothing due.
    assert cursus.send_due(now=T0)["due"] == []


def test_dry_run_touches_nothing(data_dir, sent):
    cursus.add("jan@bedrijf.nl", now=T0)
    report = cursus.send_due(now=T0, dry=True)
    assert report["due"] == [("jan@bedrijf.nl", 1)]
    assert sent == []
    assert cursus.load()["subscribers"]["jan@bedrijf.nl"]["lessons"] == {}


def test_refused_send_is_reported_and_not_recorded(data_dir, monkeypatch):
    monkeypatch.setattr(cursus.mailer, "send", lambda *a, **k: False)
    cursus.add("jan@bedrijf.nl", now=T0)
    report = cursus.send_due(now=T0)
    assert report["failed"] == [("jan@bedrijf.nl", 1)]
    assert cursus.load()["subscribers"]["jan@bedrijf.nl"]["lessons"] == {}


def test_cmd_send_exits_1_when_due_but_unconfigured(data_dir, monkeypatch, capsys):
    monkeypatch.delenv("RESEND_API_KEY", raising=False)
    # Anchor the opt-in in the past: cmd_send reads the real clock, and T0 may not
    # have arrived yet on the machine running this test.
    cursus.add("jan@bedrijf.nl", now=T0 - timedelta(days=30))
    assert cursus.main(["send"]) == 1
    assert "RESEND_API_KEY" in capsys.readouterr().err


def test_only_narrows_to_one_address(data_dir, sent):
    cursus.add("jan@bedrijf.nl", now=T0)
    cursus.add("piet@bedrijf.nl", now=T0)
    report = cursus.send_due(now=T0, only="Jan@Bedrijf.nl")
    assert report["sent"] == [("jan@bedrijf.nl", 1)]
    assert len(sent) == 1


# --- completion scoring -------------------------------------------------------------------


def _three_lessons_in(email: str, name: str | None = None) -> None:
    cursus.add(email, name=name, now=T0)
    data = cursus.load()
    data["subscribers"][cursus.normalize(email)]["lessons"] = {
        str(n): {"at": cursus._iso(T0)} for n in (1, 2, 3)
    }
    cursus.save(data)


def test_completion_scores_inbound_pipeline_lead(data_dir, pipeline_dir, sent):
    _three_lessons_in("jan@bedrijf.nl", name="Jansen Installatie")
    report = cursus.send_due(now=T0 + timedelta(days=9))
    assert report["sent"] == [("jan@bedrijf.nl", 4)]
    sub = cursus.load()["subscribers"]["jan@bedrijf.nl"]
    assert sub["completed"] and sub["scored"]
    rec = pipeline.load("jansen-installatie")
    assert rec["source"] == "e-mailcursus"
    assert rec["inbound"] is True
    assert rec["contact"]["email"] == "jan@bedrijf.nl"


def test_completion_slug_collision_never_writes_on_a_stranger(data_dir, pipeline_dir, sent):
    pipeline.add("Jansen Installatie", email="ander@bedrijf.nl")
    _three_lessons_in("jan@bedrijf.nl", name="Jansen Installatie")
    cursus.send_due(now=T0 + timedelta(days=9))
    stranger = pipeline.load("jansen-installatie")
    assert all("cursus" not in h["event"] for h in stranger["history"])
    ours = pipeline.load("jansen-installatie-jan")
    assert ours is not None and ours["contact"]["email"] == "jan@bedrijf.nl"


def test_completion_on_own_existing_record_appends_note(data_dir, pipeline_dir, sent):
    pipeline.add("Jansen Installatie", email="jan@bedrijf.nl")
    _three_lessons_in("jan@bedrijf.nl", name="Jansen Installatie")
    cursus.send_due(now=T0 + timedelta(days=9))
    rec = pipeline.load("jansen-installatie")
    assert any("cursus" in h["event"] for h in rec["history"])


# --- copy guardrails ----------------------------------------------------------------------


def test_lesson_copy_has_no_ai_tells_or_founder_name(data_dir):
    # Checked on the lesson blocks, not the rendered mail: mail_layout's shared legal
    # footer carries the registered company name with its own punctuation, and that
    # footer is not this module's copy.
    sub = {"email": "voorbeeld@bedrijf.nl", "name": "Jan"}
    for n, lesson in cursus.LESSONS.items():
        corpus = lesson["subject"] + " " + lesson["preheader"]
        for block in lesson["blocks"](sub):
            for value in vars(block).values():
                corpus += " " + " ".join(value) if isinstance(value, list) else f" {value}"
        assert "—" not in corpus, f"em-dash in les {n}"
        assert "davy" not in corpus.lower(), f"founder name in les {n}"
    # The pitch lesson quotes the locked price and points at the demo.
    _, text4, _ = cursus.render(4, sub)
    assert "299" in text4 and "klantkraan.nl/demo" in text4
