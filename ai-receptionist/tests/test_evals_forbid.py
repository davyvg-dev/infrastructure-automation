"""Offline checks for the eval harness's deterministic `forbid` verdict and the em dash
golden's wiring (the golden itself is online and runs via `python -m app.evals`)."""

from __future__ import annotations

from pathlib import Path

from app import evals

EM = "—"


def test_forbid_passes_clean_bot_lines() -> None:
    transcript = [("bot", "Ja, we doen spoed."), ("you", f"top {EM} dank"), ("tool", f"x {EM}")]
    assert evals._forbidden_verdict([EM], transcript)["passed"] is True


def test_forbid_fails_on_any_bot_line_and_quotes_it() -> None:
    transcript = [("bot", "Hoi!"), ("bot", f"Ja {EM} we houden spoedslots vrij.")]
    verdict = evals._forbidden_verdict([EM], transcript)
    assert verdict["passed"] is False
    assert "spoedslots" in verdict["rationale"]


def test_em_dash_golden_targets_the_site_demo_config() -> None:
    scenario = next(s for s in evals.SCENARIOS if s["name"] == "geen-gedachtestreep")
    assert scenario["forbid"] == [EM]
    root = Path(evals.__file__).resolve().parent.parent
    assert (root / scenario["config"]).is_file()
