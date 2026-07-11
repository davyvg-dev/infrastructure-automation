"""Draft queue persistence — a tiny JSON store. No database needed at this scale.

A draft record looks like:
{
  "id": "20260710-a1b2",
  "pillar": "build_log",
  "topic": "handling reschedules without a human",
  "status": "pending" | "approved" | "posted" | "skipped",
  "created_at": "2026-07-10T09:00:00+02:00",
  "variants": {"x": "...", "linkedin": "...", "reddit": "..."},
  "x_url": "https://x.com/.../status/123",   # set once posted
}
"""

from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from typing import Any

from .settings import DATA_DIR, ensure_dirs

_QUEUE_PATH = DATA_DIR / "queue.json"
_STATE_PATH = DATA_DIR / "state.json"
_lock = threading.Lock()


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
        return _read(_QUEUE_PATH) or []


def save_draft(draft: dict[str, Any]) -> None:
    with _lock:
        queue = _read(_QUEUE_PATH) or []
        queue.append(draft)
        _write(_QUEUE_PATH, queue)


def update_draft(draft_id: str, **fields: Any) -> dict[str, Any] | None:
    with _lock:
        queue = _read(_QUEUE_PATH) or []
        found = None
        for d in queue:
            if d["id"] == draft_id:
                d.update(fields)
                found = d
                break
        if found is not None:
            _write(_QUEUE_PATH, queue)
        return found


def get_draft(draft_id: str) -> dict[str, Any] | None:
    for d in load_queue():
        if d["id"] == draft_id:
            return d
    return None


# --- lightweight state (e.g. pillar rotation cursor, last reddit date) ---

def get_state(key: str, default: Any = None) -> Any:
    with _lock:
        state = _read(_STATE_PATH) or {}
        return state.get(key, default)


def set_state(key: str, value: Any) -> None:
    with _lock:
        state = _read(_STATE_PATH) or {}
        state[key] = value
        _write(_STATE_PATH, state)


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
