"""Nieuwsbrief broadcasts: recipient filtering, resumable ledger, headers, pacing. Offline —
mailer.send is monkeypatched, everything lives in the data_dir fixture."""

from __future__ import annotations

from pathlib import Path

import pytest

from app import cursus, nieuwsbrief, suppression

EDITIE = """---
subject: Editie 1: de zomerstorm
preheader: Wat een gemiste spoedklus kost.
---
Goedemorgen. Dit is de eerste alinea.

## Een tussenkop

[Bekijk de demo](https://klantkraan.nl/demo/)
"""


@pytest.fixture
def editie(tmp_path: Path) -> Path:
    p = tmp_path / "editie-2026-08.md"
    p.write_text(EDITIE, encoding="utf-8")
    return p


@pytest.fixture
def sent(monkeypatch: pytest.MonkeyPatch) -> list[dict]:
    calls: list[dict] = []

    def fake_send(to, subject, text, **kwargs):
        calls.append({"to": to, "subject": subject, "text": text, **kwargs})
        return True

    monkeypatch.setattr(nieuwsbrief.mailer, "send", fake_send)
    return calls


def test_parse_maps_markdown_to_blocks(editie: Path) -> None:
    ed = nieuwsbrief.parse(editie)
    assert ed["id"] == "editie-2026-08"
    assert ed["subject"].startswith("Editie 1")
    kinds = [type(b).__name__ for b in ed["blocks"]]
    assert kinds == ["Para", "Heading", "Button", "Signoff"]


def test_recipients_filter_halts_and_suppression(data_dir, editie: Path) -> None:
    cursus.add("actief@bedrijf.nl")
    cursus.add("klaar@bedrijf.nl")
    cursus.load()  # ensure store exists before direct mutation below
    cursus.add("weg@bedrijf.nl")
    cursus.stop("weg@bedrijf.nl")
    cursus.add("dood@bedrijf.nl")
    cursus.stop("dood@bedrijf.nl", bounced=True)
    cursus.add("extern@bedrijf.nl")
    suppression.suppress("extern@bedrijf.nl")
    # A course completer is still a newsletter reader.
    data = cursus.load()
    data["subscribers"]["klaar@bedrijf.nl"]["completed"] = "2026-08-01T09:00:00+00:00"
    cursus.save(data)
    assert nieuwsbrief.recipients() == ["actief@bedrijf.nl", "klaar@bedrijf.nl"]


def test_send_records_resumes_and_carries_unsubscribe(data_dir, editie: Path, sent) -> None:
    cursus.add("a@bedrijf.nl")
    cursus.add("b@bedrijf.nl")
    report = nieuwsbrief.send(editie, delay_s=0)
    assert report["sent"] == ["a@bedrijf.nl", "b@bedrijf.nl"]
    assert all("List-Unsubscribe" in c["headers"] for c in sent)
    assert all("List-Unsubscribe-Post" in c["headers"] for c in sent)
    assert sent[0]["idempotency_key"] == "nb-editie-2026-08-a@bedrijf.nl"
    assert "Afmelden:" in sent[0]["text"]
    # Re-run: nobody gets the edition twice, a new subscriber still does.
    cursus.add("c@bedrijf.nl")
    report2 = nieuwsbrief.send(editie, delay_s=0)
    assert report2["sent"] == ["c@bedrijf.nl"]
    assert report2["skipped"] == ["a@bedrijf.nl", "b@bedrijf.nl"]
    assert len(sent) == 3


def test_dry_run_sends_nothing(data_dir, editie: Path, sent) -> None:
    cursus.add("a@bedrijf.nl")
    report = nieuwsbrief.send(editie, dry=True, delay_s=0)
    assert report["recipients"] == ["a@bedrijf.nl"]
    assert sent == [] and report["sent"] == []
    # A dry run leaves no trace: the ledger records deliveries, not intentions.
    assert not nieuwsbrief.load_ledger()["broadcasts"]


def test_failed_send_is_not_recorded_as_sent(data_dir, editie: Path, monkeypatch) -> None:
    cursus.add("a@bedrijf.nl")
    monkeypatch.setattr(nieuwsbrief.mailer, "send", lambda *a, **k: False)
    report = nieuwsbrief.send(editie, delay_s=0)
    assert report["failed"] == ["a@bedrijf.nl"] and report["sent"] == []
    ledger = nieuwsbrief.load_ledger()["broadcasts"].get("editie-2026-08", {})
    assert "a@bedrijf.nl" not in ledger.get("sent", {})


def test_corrupt_ledger_exits_loudly(data_dir, editie: Path, sent) -> None:
    nieuwsbrief.ledger_path().parent.mkdir(parents=True, exist_ok=True)
    nieuwsbrief.ledger_path().write_text("{not json", encoding="utf-8")
    with pytest.raises(SystemExit):
        nieuwsbrief.send(editie, delay_s=0)


def test_missing_front_matter_refuses(data_dir, tmp_path: Path) -> None:
    p = tmp_path / "kaal.md"
    p.write_text("gewoon tekst zonder front matter", encoding="utf-8")
    with pytest.raises(SystemExit):
        nieuwsbrief.parse(p)
