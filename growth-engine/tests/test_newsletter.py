"""The nieuwsbrief drafter (src/newsletter.py + bot wiring). Offline — the Anthropic
calls, Telegram, and the store are monkeypatched; nothing hits the network or
queue.json.

Covers the locked contract: the produced .md parses with the exact front-matter +
paragraphs/heading/button format ai-receptionist/app/nieuwsbrief.py consumes, the
pre-approval checks catch planted violations (em-dash, founder name, statistic,
je-register, signoff), approval writes data/<vertical>/newsletters/<edition>.md and
marks approved and does NOTHING else (dry-run tags honestly), and an undecided
newsletter draft is resurfaced on restart like any other draft.
"""

from __future__ import annotations

import asyncio
import re
from datetime import date

import pytest

from src import bot, formatting, newsletter

# The exact regexes the send side uses (ai-receptionist/app/nieuwsbrief.py).
_FRONT_MATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)
_BUTTON_RE = re.compile(r"^\[(?P<label>[^\]]+)\]\((?P<url>https?://[^)]+)\)$")


def good_body(extra: str = "") -> str:
    """A rule-clean body inside the 150-350 word window: u-register, no numbers,
    one heading, one allowed button, no signoff."""
    filler = " ".join(["vakwerk"] * 140)
    return (
        "U kent het gevoel: de telefoon gaat terwijl u boven op een ladder staat.\n\n"
        "## Bereikbaar blijven in de drukte\n\n"
        f"{filler}\n\n"
        f"{extra}\n\n"
        "[Bekijk de demo](https://klantkraan.nl/demo/)"
    ).replace("\n\n\n\n", "\n\n")


def make_draft(**overrides):
    draft = {
        "id": "20260901-test",
        "kind": "newsletter",
        "pillar": "nieuwsbrief",
        "edition": "editie-2026-09",
        "topic": "bereikbaarheid in de najaarsdrukte",
        "status": "pending",
        "subject": "Bereikbaar blijven als het druk wordt",
        "preheader": "Zo mist u geen klussen wanneer de telefoon roodgloeiend staat.",
        "body": good_body(),
    }
    draft.update(overrides)
    return draft


def payload_from(draft):
    return {
        "topic": draft["topic"],
        "subject": draft["subject"],
        "preheader": draft["preheader"],
        "body": draft["body"],
    }


# --------------------------------------------------------------------------- #
# Generation + output format
# --------------------------------------------------------------------------- #


def test_generate_shapes_the_draft_and_markdown_roundtrips(monkeypatch):
    briefs = []
    monkeypatch.setattr(
        newsletter, "_request", lambda brief: briefs.append(brief) or payload_from(make_draft())
    )
    monkeypatch.setattr(newsletter, "recent_topics", lambda: ["eerdere editie"])

    draft = newsletter.generate_newsletter(today=date(2026, 9, 1))

    assert draft["kind"] == "newsletter"
    assert draft["edition"] == "editie-2026-09"
    assert draft["id"].startswith("20260901-")
    assert draft["status"] == "pending"
    assert draft["created_at"]
    # The brief carries the Dutch month and the used-up topics.
    assert "september 2026" in briefs[0] and "eerdere editie" in briefs[0]

    # The .md parses with the send side's own regexes.
    md = newsletter.markdown(draft)
    m = _FRONT_MATTER_RE.match(md)
    assert m, "front matter must match the kk nieuwsbrief send parser"
    meta = dict(
        (k.strip().lower(), v.strip())
        for k, _, v in (line.partition(":") for line in m.group(1).splitlines())
    )
    assert meta["subject"] == draft["subject"]
    assert meta["preheader"] == draft["preheader"]
    chunks = [c.strip() for c in re.split(r"\n\s*\n", m.group(2).strip())]
    assert any(c.startswith("## ") for c in chunks)  # heading block
    buttons = [c for c in chunks if _BUTTON_RE.match(c)]
    assert len(buttons) == 1  # exactly one button line
    assert newsletter.filename(draft) == "editie-2026-09.md"
    # No signoff in the draft: the sender appends it.
    assert "vriendelijke groet" not in md.lower()


# --------------------------------------------------------------------------- #
# Deterministic pre-approval checks
# --------------------------------------------------------------------------- #


def failed_criteria(draft):
    return {f["criterion"] for f in newsletter.local_failures(draft)}


def test_clean_draft_passes_local_checks():
    assert newsletter.local_failures(make_draft()) == []


@pytest.mark.parametrize(
    ("overrides", "criterion"),
    [
        ({"body": good_body("Dat kost u tijd — en dus geld.")}, "ai_tells"),  # em-dash
        ({"subject": "Davy vertelt over bereikbaarheid"}, "founder_name"),
        ({"body": good_body("Ruim 40 procent van de bellers hangt gewoon op.")},
         "invented_stats"),
        ({"body": good_body("Zo mis je nooit meer een klus.")}, "u_register"),
        ({"body": good_body() + "\n\nMet vriendelijke groet"}, "signoff"),
        ({"preheader": ""}, "format"),
        ({"subject": "Een onderwerpregel die veel en veel te lang is voor een inbox"},
         "length"),
        ({"body": "Veel te kort."}, "length"),
    ],
)
def test_local_checks_catch_planted_violations(overrides, criterion):
    assert criterion in failed_criteria(make_draft(**overrides))


def test_prices_and_24_7_are_allowed_but_other_numbers_are_not():
    ok = make_draft(body=good_body("Chat kost €299 per maand en Compleet €499, 24/7 actief."))
    assert "invented_stats" not in failed_criteria(ok)
    bad = make_draft(body=good_body("Voor €249 extra regelt Klantkraan ook de installatie."))
    assert "invented_stats" in failed_criteria(bad)


def test_second_button_and_foreign_url_fail_format():
    two = make_draft(
        body=good_body("[Nog een knop](https://klantkraan.nl/rekentool/)")
    )
    assert "format" in failed_criteria(two)
    foreign = make_draft(
        body=good_body().replace(
            "https://klantkraan.nl/demo/", "https://example.com/phishing/"
        )
    )
    assert "format" in failed_criteria(foreign)


# --------------------------------------------------------------------------- #
# check_and_revise: verify.py semantics (one auto-revise, then flag; fail-open)
# --------------------------------------------------------------------------- #


@pytest.fixture(autouse=True)
def _verify_on(monkeypatch):
    monkeypatch.delenv("GROWTH_ENGINE_VERIFY", raising=False)


def test_pass_proceeds_unchanged(monkeypatch):
    monkeypatch.setattr(newsletter, "judge_failures", lambda d: [])
    monkeypatch.setattr(
        newsletter, "regenerate", lambda *a: pytest.fail("no revise on a passing draft")
    )
    out = newsletter.check_and_revise(make_draft())
    assert out["verify"] == {"status": "pass", "failures": [], "revised": False}
    assert formatting.verify_flags(out) == []


def test_fail_revises_once_then_passes(monkeypatch):
    monkeypatch.setattr(newsletter, "judge_failures", lambda d: [])
    notes = []

    def fake_regenerate(draft, note):
        notes.append(note)
        return {"body": good_body()}  # the em-dash is gone after the revise

    monkeypatch.setattr(newsletter, "regenerate", fake_regenerate)
    dashed = make_draft(body=good_body("Dat kost u tijd — en dus geld."))
    out = newsletter.check_and_revise(dashed)
    assert out["verify"]["status"] == "pass"
    assert out["verify"]["revised"] is True
    assert len(notes) == 1 and "ai_tells" in notes[0]


def test_fail_twice_still_delivers_with_flags(monkeypatch):
    monkeypatch.setattr(newsletter, "judge_failures", lambda d: [])
    monkeypatch.setattr(newsletter, "regenerate", lambda d, n: {})  # revise fixes nothing
    out = newsletter.check_and_revise(make_draft(subject="Davy hier"))
    assert out["verify"]["status"] == "fail"
    assert any(f["criterion"] == "founder_name" for f in out["verify"]["failures"])
    flags = formatting.verify_flags(out)
    assert flags and any("founder" in line for line in flags)
    # The approval preview leads with the flags, like post previews do.
    assert "Pre" in formatting.newsletter_preview(out).splitlines()[0]


def test_judge_error_fails_open(monkeypatch):
    def boom(draft):
        raise RuntimeError("api down")

    monkeypatch.setattr(newsletter, "judge_failures", boom)
    out = newsletter.check_and_revise(make_draft())
    assert out["verify"]["status"] == "error"
    assert "api down" in out["verify"]["error"]
    assert "UNCHECKED" in formatting.newsletter_preview(out).splitlines()[0]


def test_disabled_toggle_skips_checks_entirely(monkeypatch):
    monkeypatch.setenv("GROWTH_ENGINE_VERIFY", "0")
    monkeypatch.setattr(
        newsletter, "judge_failures", lambda d: pytest.fail("judge called while disabled")
    )
    out = newsletter.check_and_revise(make_draft(subject="Davy hier"))
    assert "verify" not in out


# --------------------------------------------------------------------------- #
# Approval: writes the .md, marks approved, does nothing else
# --------------------------------------------------------------------------- #


@pytest.fixture()
def approve_env(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(newsletter, "data_dir", lambda: tmp_path)
    monkeypatch.setattr(
        newsletter.store, "update_draft", lambda draft_id, **f: calls.append((draft_id, f))
    )
    return tmp_path, calls


def test_approve_writes_md_and_marks_approved_under_dry_run(monkeypatch, approve_env):
    tmp_path, calls = approve_env
    monkeypatch.setattr(newsletter, "dry_run", lambda: True)
    draft = make_draft()

    path = newsletter.approve(draft)

    assert path == tmp_path / "newsletters" / "editie-2026-09.md"
    assert path.read_text(encoding="utf-8") == newsletter.markdown(draft)
    assert len(calls) == 1  # one honest ledger write, nothing else happens
    draft_id, fields = calls[0]
    assert draft_id == draft["id"]
    assert fields["status"] == "approved"  # never "posted"/"sent" — sending is kk's job
    assert fields["dry_run"] is True
    assert fields["file"] == str(path)
    assert fields.keys() == {"status", "approved_at", "file", "dry_run"}


def test_approve_live_has_no_dry_run_tag(monkeypatch, approve_env):
    _, calls = approve_env
    monkeypatch.setattr(newsletter, "dry_run", lambda: False)
    newsletter.approve(make_draft())
    assert "dry_run" not in calls[0][1]


def test_bot_routes_newsletter_approval_away_from_post_fanout(monkeypatch):
    draft = make_draft()
    monkeypatch.setattr(bot.store, "get_draft", lambda draft_id: dict(draft))
    monkeypatch.setattr(bot, "dry_run", lambda: False)
    approved = []
    monkeypatch.setattr(bot.newsletter, "approve", lambda d: approved.append(d["id"]) or "x.md")
    monkeypatch.setattr(
        bot, "_approve", lambda *a: pytest.fail("post publisher fanout ran for a newsletter")
    )

    sent = []

    class FakeBot:
        async def send_message(self, chat_id, text, **kwargs):
            sent.append(text)

    class FakeMsg:
        chat_id = 1

    class FakeQuery:
        data = f"approve:{draft['id']}"
        message = FakeMsg()

        async def answer(self):
            pass

        async def edit_message_reply_markup(self, reply_markup=None):
            pass

    update = type("U", (), {"callback_query": FakeQuery()})()
    context = type("C", (), {"bot": FakeBot()})()
    asyncio.run(bot.on_button(update, context))

    assert approved == [draft["id"]]
    assert any("approved and saved" in t for t in sent)


# --------------------------------------------------------------------------- #
# Bot wiring: delivery, restart resurfacing, note rewrite, schedule
# --------------------------------------------------------------------------- #


def test_deliver_sends_document_then_summary_with_buttons(monkeypatch):
    updates = []
    monkeypatch.setattr(
        bot.store, "update_draft", lambda draft_id, **f: updates.append(f) or None
    )
    events = []

    class FakeBot:
        async def send_document(self, chat_id, document=None, filename=None, **kwargs):
            events.append(("document", filename, document))

        async def send_message(self, chat_id=None, text=None, reply_markup=None, **kwargs):
            events.append(("message", text, reply_markup))

    app = type("A", (), {"bot": FakeBot()})()
    draft = make_draft()
    asyncio.run(bot._deliver_draft(app, 1, draft))

    assert events[0][0] == "document"
    assert events[0][1] == "editie-2026-09.md"
    assert events[0][2] == newsletter.markdown(draft).encode("utf-8")
    assert events[1][0] == "message" and events[1][2] is not None  # buttons last
    assert updates and updates[0].get("delivered_at")


def test_post_init_resurfaces_undecided_newsletter(monkeypatch):
    draft = make_draft(delivered_at="2026-09-01T09:00:00")
    monkeypatch.setattr(bot.store, "load_queue", lambda: [dict(draft)])
    monkeypatch.setattr(bot, "env", lambda key, **kw: "1")
    monkeypatch.setattr(bot, "schedule_jobs", lambda app, chat_id: None)
    monkeypatch.setattr(
        bot, "_deliver_draft", lambda *a: pytest.fail("delivered draft must not be redelivered")
    )

    sent = []

    class FakeBot:
        async def send_message(self, chat_id=None, text=None, **kwargs):
            sent.append((text, kwargs.get("reply_markup")))

    app = type("A", (), {"bot": FakeBot()})()
    asyncio.run(bot._post_init(app))

    resurfaced = [s for s in sent if s[1] is not None]
    assert len(resurfaced) == 1
    assert "nieuwsbrief" in resurfaced[0][0]  # newsletter preview, not the post preview


def test_note_rewrites_a_newsletter_draft(monkeypatch):
    draft = make_draft(awaiting="note")
    state = dict(draft)
    monkeypatch.setattr(bot.store, "load_queue", lambda: [dict(state)])
    monkeypatch.setattr(
        bot.store, "update_draft", lambda draft_id, **f: state.update(f) or dict(state)
    )
    monkeypatch.setattr(
        bot.newsletter, "regenerate", lambda d, note: {"subject": f"na: {note}"}
    )
    redelivered = []

    async def fake_deliver(app, chat_id, d):
        redelivered.append(d["subject"])

    monkeypatch.setattr(bot, "_deliver_draft", fake_deliver)

    class FakeMessage:
        text = "korter graag"

        async def reply_text(self, text, **kwargs):
            pass

    update = type(
        "U",
        (),
        {"message": FakeMessage(), "effective_chat": type("Chat", (), {"id": 1})()},
    )()
    context = type("C", (), {"application": object()})()
    asyncio.run(bot.on_note(update, context))

    assert state["awaiting"] is None
    assert state["subject"] == "na: korter graag"
    assert redelivered == ["na: korter graag"]


def test_schedule_registers_the_monthly_newsletter_job():
    calls = []

    class FakeJQ:
        def jobs(self):
            return []

        def run_daily(self, cb, **kwargs):
            calls.append(("daily", kwargs.get("name")))

        def run_monthly(self, cb, **kwargs):
            calls.append(("monthly", kwargs.get("name"), kwargs.get("day"), cb))

        def run_repeating(self, cb, **kwargs):
            calls.append(("repeating", kwargs.get("name")))

    app = type("A", (), {"job_queue": FakeJQ()})()
    bot.schedule_jobs(app, chat_id=1)

    monthly = [c for c in calls if c[0] == "monthly"]
    assert len(monthly) == 1
    assert monthly[0][1] == "newsletter"
    assert monthly[0][2] == 1  # the 1st of the month
    assert monthly[0][3] is bot.newsletter_job


def test_newsletter_job_skips_when_edition_already_drafted(monkeypatch):
    existing = make_draft()
    monkeypatch.setattr(bot.newsletter, "open_edition_draft", lambda: dict(existing))
    monkeypatch.setattr(
        bot.newsletter,
        "generate_newsletter",
        lambda *a, **kw: pytest.fail("must not draft a second edition"),
    )

    sent = []

    class FakeBot:
        async def send_message(self, chat_id, text, **kwargs):
            sent.append(text)

    context = type(
        "C",
        (),
        {
            "bot": FakeBot(),
            "job": type("J", (), {"chat_id": 1})(),
            "application": object(),
        },
    )()
    asyncio.run(bot.newsletter_job(context))
    assert any("already has a draft" in t for t in sent)
