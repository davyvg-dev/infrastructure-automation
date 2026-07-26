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
