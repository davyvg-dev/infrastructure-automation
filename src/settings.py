"""Environment + config loading. One place that reads .env and the strategy YAML."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
CONFIG_PATH = ROOT / "config" / "content_strategy.yaml"

load_dotenv(ROOT / ".env")


class MissingSetting(RuntimeError):
    """Raised when a required environment variable is not set."""


def env(name: str, required: bool = True, default: str | None = None) -> str | None:
    value = os.getenv(name, default)
    if required and not value:
        raise MissingSetting(
            f"{name} is not set. Copy .env.example to .env and fill it in "
            f"(see docs/SETUP.md)."
        )
    return value


@lru_cache(maxsize=1)
def strategy() -> dict[str, Any]:
    """The parsed content_strategy.yaml."""
    with CONFIG_PATH.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def active_cadence() -> dict[str, Any]:
    cad = strategy()["cadence"]
    return cad["profiles"][cad["active"]]


def dry_run() -> bool:
    """When set, generate + notify but never actually post to X."""
    return os.getenv("GROWTH_ENGINE_DRY_RUN", "").strip() not in ("", "0", "false", "False")


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
