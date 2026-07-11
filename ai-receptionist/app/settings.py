"""Config + env loading for the receptionist demo."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"

try:  # python-dotenv is optional; env vars can also be set directly.
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ModuleNotFoundError:
    pass


class MissingSetting(RuntimeError):
    pass


def env(name: str, required: bool = True, default: str | None = None) -> str | None:
    value = os.getenv(name, default)
    if required and not value:
        raise MissingSetting(f"{name} is not set. Copy .env.example to .env and fill it in.")
    return value


def config_path() -> Path:
    return ROOT / os.getenv("BUSINESS_CONFIG", "config/business.yaml")


@lru_cache(maxsize=1)
def business() -> dict[str, Any]:
    with config_path().open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
