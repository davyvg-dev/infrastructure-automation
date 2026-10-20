"""The business config loads and exposes the shape the receptionist depends on. Offline."""

from __future__ import annotations

from app.settings import business

_EFFORT_TIERS = {"low", "medium", "high", "xhigh", "max"}


def test_default_config_loads():
    cfg = business()
    assert cfg["business"]["name"]
    assert cfg["business"]["type"]


def test_persona_and_services_present():
    cfg = business()
    assert cfg["persona"]["name"]
    services = cfg.get("services", [])
    assert services, "config must define at least one service"
    assert all(s.get("name") for s in services), "every service needs a name"


def test_model_is_configured():
    model = business()["model"]
    assert model["id"], "the Claude model id must be set in config, never hard-coded"
    # effort is optional (the loop defaults to 'low'); if set it must be a real tier.
    assert model.get("effort", "low") in _EFFORT_TIERS
