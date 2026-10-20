"""Shared fixtures. Every offline test runs against throwaway dirs so it never touches the
real data/ store or the committed client configs.

DATA_DIR is bound two different ways in the code: settings.py reads its own module global at
call time, while calendar_store.py did `from .settings import DATA_DIR` (a separate name
captured at import). Isolation therefore patches both bindings.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app import calendar_store, settings


@pytest.fixture
def data_dir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    """Point every DATA_DIR-backed store (analytics db, sim bookings) at a throwaway dir."""
    d = tmp_path / "data"
    d.mkdir()
    monkeypatch.setattr(settings, "DATA_DIR", d)
    monkeypatch.setattr(calendar_store, "DATA_DIR", d)
    return d


@pytest.fixture
def clients_dir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    """An empty config/clients dir for the multi-tenant routing tests."""
    d = tmp_path / "clients"
    d.mkdir()
    monkeypatch.setattr(settings, "CLIENTS_DIR", d)
    return d
