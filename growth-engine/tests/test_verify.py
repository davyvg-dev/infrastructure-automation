"""Pre-approval verify pass: routing logic (pass / fail+revise / error). Offline —
the judge API call and the drafting-model revise are monkeypatched, never hit."""

from __future__ import annotations

import pytest

from src import formatting, verify


def make_draft(**overrides):
    draft = {
        "id": "20260810-test",
        "pillar": "problem",
        "topic": "gemiste oproepen",
        "status": "pending",
        "variants": {
            "x": "Een gemiste oproep is vaak een verloren klus.",
            "linkedin": "Een gemiste oproep is vaak een verloren klus.\n\nWat doe jij eraan?",
        },
    }
    draft.update(overrides)
    return draft


def all_pass():
    return {"checks": [{"criterion": c, "passed": True, "reason": ""} for c in verify.CRITERIA]}


def with_failure(criterion="founder_name", reason="the post names 'Davy'"):
    checks = [
        {"criterion": c, "passed": c != criterion, "reason": reason if c == criterion else ""}
        for c in verify.CRITERIA
    ]
    return {"checks": checks}


@pytest.fixture(autouse=True)
def _verify_on(monkeypatch):
    # Default-on toggle; make each test explicit and independent of the caller's env.
    monkeypatch.delenv("GROWTH_ENGINE_VERIFY", raising=False)


def test_toggle_defaults_on_and_can_be_disabled(monkeypatch):
    from src import settings

    assert settings.verify_enabled()
    monkeypatch.setenv("GROWTH_ENGINE_VERIFY", "0")
    assert not settings.verify_enabled()
    monkeypatch.setenv("GROWTH_ENGINE_VERIFY", "1")
    assert settings.verify_enabled()


def test_disabled_toggle_skips_the_judge_entirely(monkeypatch):
    monkeypatch.setenv("GROWTH_ENGINE_VERIFY", "0")

    def boom(draft):  # would fail the test if the judge were consulted
        raise AssertionError("judge called while disabled")

    monkeypatch.setattr(verify, "verify_draft", boom)
    draft = make_draft()
    out = verify.check_and_revise(draft)
    assert out is draft
    assert "verify" not in out


def test_pass_proceeds_unchanged(monkeypatch):
    monkeypatch.setattr(verify, "verify_draft", lambda d: all_pass())
    monkeypatch.setattr(
        verify.generate,
        "regenerate_variant",
        lambda *a: pytest.fail("no revise on a passing draft"),
    )
    draft = make_draft()
    original_variants = dict(draft["variants"])
    out = verify.check_and_revise(draft)
    assert out["verify"] == {"status": "pass", "failures": [], "revised": False}
    assert out["variants"] == original_variants
    # A passing draft adds nothing to the approval message.
    assert formatting.verify_flags(out) == []


def test_fail_revises_once_then_passes(monkeypatch):
    verdicts = iter([with_failure(), all_pass()])
    monkeypatch.setattr(verify, "verify_draft", lambda d: next(verdicts))
    revised = []

    def fake_revise(draft, platform, note):
        revised.append((platform, note))
        return f"herschreven {platform}"

    monkeypatch.setattr(verify.generate, "regenerate_variant", fake_revise)
    out = verify.check_and_revise(make_draft())
    assert out["verify"]["status"] == "pass"
    assert out["verify"]["revised"] is True
    assert out["variants"] == {"x": "herschreven x", "linkedin": "herschreven linkedin"}
    # Every variant got exactly one revise, carrying the failed criterion.
    assert [p for p, _ in revised] == ["x", "linkedin"]
    assert all("founder_name" in note for _, note in revised)
    assert formatting.verify_flags(out) == []


def test_fail_twice_still_delivers_with_flags(monkeypatch):
    calls = []

    def judge(draft):
        calls.append(1)
        return with_failure()

    monkeypatch.setattr(verify, "verify_draft", judge)
    monkeypatch.setattr(verify.generate, "regenerate_variant", lambda d, p, n: f"nog fout {p}")
    out = verify.check_and_revise(make_draft())
    # Exactly two judge calls — never more than one revise loop.
    assert len(calls) == 2
    assert out["verify"]["status"] == "fail"
    assert out["verify"]["failures"] == [
        {"criterion": "founder_name", "reason": "the post names 'Davy'"}
    ]
    # The draft is NOT dropped: it goes to Telegram with the reasons prepended.
    flags = formatting.verify_flags(out)
    assert flags and "Pre" in flags[0]
    # MarkdownV2 escaping turns founder_name into founder\_name — check the stem.
    assert any("founder" in line for line in flags)
    assert "Pre" in formatting.preview(out).splitlines()[0]


def test_judge_error_fails_open(monkeypatch):
    def boom(draft):
        raise RuntimeError("api down")

    monkeypatch.setattr(verify, "verify_draft", boom)
    draft = make_draft()
    out = verify.check_and_revise(draft)
    assert out["verify"]["status"] == "error"
    assert "api down" in out["verify"]["error"]
    flags = formatting.verify_flags(out)
    assert flags and "UNCHECKED" in flags[0]
    # The approval message leads with the errored-check warning.
    assert "UNCHECKED" in formatting.preview(out).splitlines()[0]


def test_revise_error_keeps_original_variant(monkeypatch):
    verdicts = iter([with_failure(), with_failure()])
    monkeypatch.setattr(verify, "verify_draft", lambda d: next(verdicts))

    def broken_revise(draft, platform, note):
        raise RuntimeError("draft model down")

    monkeypatch.setattr(verify.generate, "regenerate_variant", broken_revise)
    draft = make_draft()
    original_variants = dict(draft["variants"])
    out = verify.check_and_revise(draft)
    # Originals survive a broken revise, and the re-judge still flags the draft.
    assert out["variants"] == original_variants
    assert out["verify"]["status"] == "fail"


def test_empty_draft_skips_verification(monkeypatch):
    monkeypatch.setattr(
        verify, "verify_draft", lambda d: pytest.fail("judge called on empty draft")
    )
    out = verify.check_and_revise(make_draft(variants={}))
    assert "verify" not in out


def test_failures_extraction_tolerates_partial_verdicts():
    verdict = {"checks": [{"criterion": "pricing", "passed": False}]}
    assert verify._failures(verdict) == [{"criterion": "pricing", "reason": ""}]
    assert verify._failures({}) == []


def test_brief_carries_pillar_language_and_limits():
    brief = verify._brief(make_draft())
    assert "PILLAR: problem" in brief
    assert "Dutch" in brief and "build_log" in brief
    assert "hard limit 280" in brief  # X char_limit from the platform registry
    assert "gemiste oproep" in brief
