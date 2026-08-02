"""Prospect -> client state machine: qualify gate, readiness gate, sign promotion. Offline."""

from __future__ import annotations

import pytest

from app import pipeline

# A go-live-ready demo config: a real price and the art. 50 disclosure in the greeting.
_READY = (
    "business:\n  name: Proef BV\n"
    'greeting: "Hallo, ik ben de digitale receptionist van Proef BV."\n'
    'services:\n  - name: Spoed\n    price: "vanaf €90"\n'
)


@pytest.fixture
def pipeline_root(monkeypatch, tmp_path):
    """Redirect the pipeline's on-disk state (records + promoted client configs) to a tmp tree.

    pipeline.py holds ROOT / PIPELINE_DIR / CLIENTS_DIR as module globals, so each is patched
    directly."""
    monkeypatch.setattr(pipeline, "ROOT", tmp_path)
    monkeypatch.setattr(pipeline, "PIPELINE_DIR", tmp_path / "data" / "pipeline")
    monkeypatch.setattr(pipeline, "CLIENTS_DIR", tmp_path / "config" / "clients")
    return tmp_path


def _add_and_qualify():
    pipeline.add("Proef BV", slug="proef-bv", email="info@proef.nl", entity="bv")
    return pipeline.qualify("proef-bv")


def _stage_demo(root):
    """Move the prospect to the demo stage with a staged config file, as a real run would."""
    staged = root / "config" / "proef-bv.yaml"
    staged.parent.mkdir(parents=True, exist_ok=True)
    staged.write_text(_READY, encoding="utf-8")
    pipeline.advance("proef-bv", "demo")
    rec = pipeline.load("proef-bv")
    rec["config"] = "config/proef-bv.yaml"
    pipeline.save(rec)
    return staged


def test_nl_bv_qualifies(pipeline_root):
    assert _add_and_qualify()["decision"] == "qualified"


def test_call_logs_dials_and_computes_funnel(pipeline_root):
    _add_and_qualify()
    pipeline.call("proef-bv", "no-answer")
    pipeline.call("proef-bv", "voicemail", note="bouwvak, msg left")
    out = pipeline.call("proef-bv", "demo", note="di 10:00", next_="2099-01-02")
    assert out["next_call"] == "2099-01-02"
    assert "advance" in out["hint"]

    text = pipeline.calls_text()
    assert "3 dials over 1 prospect" in text
    assert "reach 1/3" in text
    assert "reach→demo 1/1" in text
    assert "2099-01-02" in text and "proef-bv" in text  # planned callback surfaced

    with pytest.raises(ValueError):
        pipeline.call("proef-bv", "ghosted")
    with pytest.raises(ValueError):
        pipeline.call("proef-bv", "callback", next_="tomorrow")


def test_call_reached_outcome_clears_pending_callback(pipeline_root):
    _add_and_qualify()
    pipeline.call("proef-bv", "callback", next_="2099-01-02")
    pipeline.call("proef-bv", "talked", note="callback happened, no next step")
    assert pipeline.load("proef-bv").get("next_call") is None


def test_call_opt_out_suppresses_phone(pipeline_root, monkeypatch):
    monkeypatch.setattr(pipeline, "SUPPRESSION_FILE", pipeline_root / "suppression.txt")
    pipeline.add("Proef BV", slug="proef-bv", phone="0182-686300", entity="bv")
    pipeline.call("proef-bv", "rejected", opt_out=True)
    assert pipeline.qualify("proef-bv")["decision"] == "disqualified"


def test_readiness_gate_blocks_unfilled_price(pipeline_root):
    _add_and_qualify()
    staged = _stage_demo(pipeline_root)
    staged.write_text(_READY.replace('"vanaf €90"', '"PRIJS?"'), encoding="utf-8")
    with pytest.raises(ValueError):
        pipeline.sign("proef-bv")


def test_sign_promotes_config_then_is_idempotent(pipeline_root):
    _add_and_qualify()
    staged = _stage_demo(pipeline_root)

    out = pipeline.sign("proef-bv")
    assert out["status"] == "signed"
    assert (pipeline.CLIENTS_DIR / "proef-bv.yaml").exists(), "config promoted to config/clients/"
    assert not staged.exists(), "sign should move, not copy, the staging config"
    rec = pipeline.load("proef-bv")
    assert rec["config"] == "config/clients/proef-bv.yaml"
    assert any("signed" in h.get("event", "") for h in rec["history"])

    # Re-signing finalizes in place: nothing new promoted, status stays signed.
    out2 = pipeline.sign("proef-bv")
    assert not out2["promoted"]
    assert pipeline.load("proef-bv")["status"] == "signed"
