"""Draft queue persistence — a tiny JSON store. No database needed at this scale.

A draft record looks like:
{
  "id": "20260710-a1b2",
  "pillar": "build_log",
  "topic": "handling reschedules without a human",
  "status": "pending" | "approved" | "posted" | "queued" | "skipped",
  "created_at": "2026-07-10T09:00:00+02:00",
  "variants": {"x": "...", "linkedin": "...", "reddit": "..."},
  "x_url": "https://x.com/.../status/123",   # set once posted
  "linkedin_queued": "Klantkraan — goes out 2026-07-31T09:00:00Z",  # in Buffer's queue
}

"queued" means handed to Buffer and not live yet; there is no URL until Buffer sends it.
"""

from __future__ import annotations

import json
import threading
from datetime import UTC, datetime
from typing import Any

from .settings import data_dir, ensure_dirs

_lock = threading.Lock()


def _queue_path():
    return data_dir() / "queue.json"


def _state_path():
    return data_dir() / "state.json"


def _read(path) -> Any:
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _write(path, data: Any) -> None:
    ensure_dirs()
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    tmp.replace(path)


def load_queue() -> list[dict[str, Any]]:
    with _lock:
        return _read(_queue_path()) or []


def save_draft(draft: dict[str, Any]) -> None:
    with _lock:
        queue = _read(_queue_path()) or []
        queue.append(draft)
        _write(_queue_path(), queue)


def update_draft(draft_id: str, **fields: Any) -> dict[str, Any] | None:
    with _lock:
        queue = _read(_queue_path()) or []
        found = None
        for d in queue:
            if d["id"] == draft_id:
                d.update(fields)
                found = d
                break
        if found is not None:
            _write(_queue_path(), queue)
        return found


def get_draft(draft_id: str) -> dict[str, Any] | None:
    for d in load_queue():
        if d["id"] == draft_id:
            return d
    return None


# --- lightweight state (e.g. pillar rotation cursor, last reddit date) ---


def get_state(key: str, default: Any = None) -> Any:
    with _lock:
        state = _read(_state_path()) or {}
        return state.get(key, default)


def set_state(key: str, value: Any) -> None:
    with _lock:
        state = _read(_state_path()) or {}
        state[key] = value
        _write(_state_path(), state)


def now_iso() -> str:
    return datetime.now(UTC).astimezone().isoformat(timespec="seconds")
