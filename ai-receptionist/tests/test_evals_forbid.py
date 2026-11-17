"""Offline checks for the eval harness's deterministic `forbid` verdict and the em dash
golden's wiring (the golden itself is online and runs via `python -m app.evals`)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app import evals, receptionist, tools

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


def test_model_sees_no_em_dash_in_demo_prompt_or_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    """The model copies the punctuation it is shown: the rendered demo system prompt and
    every tool description must be free of em dashes (the rule names the character by
    its code point instead of writing it)."""
    monkeypatch.setenv("BUSINESS_CONFIG", "config/klantkraan-demo.yaml")
    prompt = receptionist.build_system_prompt()
    assert EM not in prompt
    assert "U+2014" in prompt
    every_tool = tools.TOOLS + tools.VEHICLE_TOOLS + tools.LISTINGS_TOOLS
    assert EM not in json.dumps(every_tool, ensure_ascii=False)
