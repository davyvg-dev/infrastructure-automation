"""Environment + config loading. One place that reads .env and the strategy YAML.

Multi-vertical: each vertical is its own process. GROWTH_CONFIG selects the strategy
YAML (default: the trades config); the YAML's `vertical:` key names the vertical, which
scopes the data dir (data/<vertical>/) and the per-vertical env overlay (.env.<vertical>
— each vertical needs its OWN Telegram bot token, one poller per token).
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"

try:  # python-dotenv is a convenience; env vars can also be set directly.
    from dotenv import load_dotenv
except ModuleNotFoundError:
    load_dotenv = None  # type: ignore[assignment]

if load_dotenv:
    load_dotenv(ROOT / ".env")

# After load_dotenv, so GROWTH_CONFIG can come from .env as well as the process env.
CONFIG_PATH = ROOT / os.getenv("GROWTH_CONFIG", "config/content_strategy.yaml")


class MissingSetting(RuntimeError):
    """Raised when a required environment variable is not set."""


def env(name: str, required: bool = True, default: str | None = None) -> str | None:
    value = os.getenv(name, default)
    if required and not value:
        raise MissingSetting(
            f"{name} is not set. Copy .env.example to .env and fill it in (see docs/SETUP.md)."
        )
    return value


@lru_cache(maxsize=1)
def strategy() -> dict[str, Any]:
    """The parsed strategy YAML (GROWTH_CONFIG, default content_strategy.yaml)."""
    with CONFIG_PATH.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def vertical() -> str:
    return strategy().get("vertical", "trades")


def data_dir() -> Path:
    return DATA_DIR / vertical()


def active_cadence() -> dict[str, Any]:
    cad = strategy()["cadence"]
    return cad["profiles"][cad["active"]]


def dry_run() -> bool:
    """When set, generate + notify but never actually post to X."""
    return os.getenv("GROWTH_ENGINE_DRY_RUN", "").strip() not in ("", "0", "false", "False")


def verify_enabled() -> bool:
    """Pre-approval LLM-judge pass on every draft (src/verify.py). ON by default;
    set GROWTH_ENGINE_VERIFY=0 to disable without a deploy."""
    return os.getenv("GROWTH_ENGINE_VERIFY", "").strip() not in ("0", "false", "False")


def ensure_dirs() -> None:
    data_dir().mkdir(parents=True, exist_ok=True)
    if vertical() == "trades":
        # One-time migration: queue/state lived flat in data/ before multi-vertical.
        for name in ("queue.json", "state.json"):
            legacy, target = DATA_DIR / name, data_dir() / name
            if legacy.exists() and not target.exists():
                legacy.replace(target)


# Per-vertical secrets overlay: .env.<vertical> overrides the shared .env. Guarded so a
# broken/missing YAML surfaces at the first strategy() call, not as an import crash.
if load_dotenv:
    try:
        _overlay = ROOT / f".env.{vertical()}"
    except Exception:
        pass
    else:
        if _overlay.exists():
            load_dotenv(_overlay, override=True)
