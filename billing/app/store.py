"""Local slug -> Mollie record map so re-running the CLI never duplicates a
customer or loses the subscription id. Lives in data/customers.json (gitignored)."""
from __future__ import annotations

import json

from . import settings

_PATH = settings.DATA_DIR / "customers.json"


def _load() -> dict:
    if _PATH.exists():
        return json.loads(_PATH.read_text() or "{}")
    return {}


def _save(data: dict) -> None:
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    _PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def get(slug: str) -> dict | None:
    return _load().get(slug)


def all_records() -> dict:
    return _load()


def put(slug: str, record: dict) -> None:
    data = _load()
    data[slug] = record
    _save(data)
