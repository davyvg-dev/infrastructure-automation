"""Durable per-client capture — the ground-truth layer under client oversight.

Every conversation turn is recorded to a local SQLite database (data/analytics.db),
namespaced by client slug, so a restart no longer wipes the record and per-client
usage/leads/bookings/cost become queryable. This is the deterministic Layer 1 from
docs/client-intelligence.md; a later nightly "analyst" pass derives insights on top.

Design seam (mirrors calendar_store): swap the SQLite bodies here for Postgres at ~10
clients without touching the call sites in sessions.py / receptionist.py. Stdlib only.

Capture must NEVER break a conversation: every public call swallows its own errors
(after logging) and returns quietly, exactly like notify.

Privacy: the channel user id (a phone number on WhatsApp) is stored only as a salted
hash — never in the clear. Transcript text is stored as-is for the analyst layer; a
retention/purge job (AVG) is the next sub-slice.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import sqlite3
import threading
from datetime import datetime, time as dtime
from typing import Any

from . import settings

log = logging.getLogger("analytics")

_LOCK = threading.Lock()

# Outcome ranking: a booking beats a captured message beats a plain answer. A session's
# outcome is the strongest thing that happened across its turns.
_OUTCOME_RANK = {"answered": 1, "message": 2, "booked": 3}


def _db_path() -> str:
    return str(settings.DATA_DIR / "analytics.db")


def _hash_user(user_id: str) -> str:
    salt = os.getenv("ANALYTICS_SALT", "klantkraan")
    return hashlib.sha256(f"{salt}:{user_id}".encode()).hexdigest()[:16]


def _connect() -> sqlite3.Connection:
    settings.ensure_dirs()
    conn = sqlite3.connect(_db_path(), timeout=10)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS sessions (
            session_key       TEXT PRIMARY KEY,
            client            TEXT NOT NULL,
            channel           TEXT NOT NULL,
            user_ref          TEXT NOT NULL,
            started_at        TEXT NOT NULL,
            updated_at        TEXT NOT NULL,
            turns             INTEGER NOT NULL DEFAULT 0,
            after_hours_turns INTEGER NOT NULL DEFAULT 0,
            outcome           TEXT NOT NULL DEFAULT 'answered',
            input_tokens      INTEGER NOT NULL DEFAULT 0,
            output_tokens     INTEGER NOT NULL DEFAULT 0,
            model             TEXT
        )"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS turns (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            session_key   TEXT NOT NULL,
            client        TEXT NOT NULL,
            ts            TEXT NOT NULL,
            user_text     TEXT,
            reply         TEXT,
            tools_json    TEXT,
            input_tokens  INTEGER NOT NULL DEFAULT 0,
            output_tokens INTEGER NOT NULL DEFAULT 0,
            after_hours   INTEGER NOT NULL DEFAULT 0,
            outcome       TEXT NOT NULL DEFAULT 'answered'
        )"""
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_turns_client ON turns(client, ts)")
    return conn


def _outcome_from_tools(tools: list[dict[str, Any]]) -> str:
    """The strongest outcome implied by the tools called this turn."""
    outcome = "answered"
    for t in tools or []:
        name = t.get("name")
        ok = False
        try:
            ok = bool(json.loads(t.get("output", "{}")).get("ok", name == "book_appointment"))
        except Exception:
            ok = False
        if name == "book_appointment" and ok:
            return "booked"
        if name == "take_message" and ok and _OUTCOME_RANK["message"] > _OUTCOME_RANK[outcome]:
            outcome = "message"
    return outcome


def is_after_hours(cfg: dict[str, Any], now: datetime | None = None) -> bool:
    """True if 'now' falls outside the business's configured opening hours (a closed day or
    outside the open/close window for today). Defensive: any parsing problem => not flagged."""
    try:
        hours = cfg.get("hours") or {}
        tzname = (cfg.get("business") or {}).get("timezone")
        if now is None:
            if tzname:
                from zoneinfo import ZoneInfo

                now = datetime.now(ZoneInfo(tzname))
            else:
                now = datetime.now()
        weekday = now.strftime("%A").lower()
        window = hours.get(weekday)
        if not window:
            return True  # a day with no hours is a closed day
        open_h, open_m = (int(x) for x in str(window[0]).split(":"))
        close_h, close_m = (int(x) for x in str(window[1]).split(":"))
        t = now.time()
        return not (dtime(open_h, open_m) <= t < dtime(close_h, close_m))
    except Exception:
        return False


def record_turn(
    *,
    client: str,
    channel: str,
    user_id: str,
    user_text: str,
    reply: str,
    input_tokens: int = 0,
    output_tokens: int = 0,
    model: str = "",
    tools: list[dict[str, Any]] | None = None,
    after_hours: bool = False,
) -> None:
    """Persist one respond() exchange. Never raises — capture must not break a conversation."""
    tools = tools or []
    outcome = _outcome_from_tools(tools)
    user_ref = _hash_user(user_id)
    key = f"{client}:{channel}:{user_ref}"
    now = datetime.now().isoformat(timespec="seconds")
    try:
        with _LOCK:
            conn = _connect()
            try:
                conn.execute(
                    "INSERT INTO turns (session_key, client, ts, user_text, reply, tools_json, "
                    "input_tokens, output_tokens, after_hours, outcome) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (key, client, now, user_text, reply, json.dumps(tools, ensure_ascii=False),
                     int(input_tokens), int(output_tokens), 1 if after_hours else 0, outcome),
                )
                row = conn.execute(
                    "SELECT outcome, input_tokens, output_tokens FROM sessions WHERE session_key=?",
                    (key,),
                ).fetchone()
                if row is None:
                    conn.execute(
                        "INSERT INTO sessions (session_key, client, channel, user_ref, started_at, "
                        "updated_at, turns, after_hours_turns, outcome, input_tokens, output_tokens, "
                        "model) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                        (key, client, channel, user_ref, now, now, 1, 1 if after_hours else 0,
                         outcome, int(input_tokens), int(output_tokens), model),
                    )
                else:
                    best = outcome if _OUTCOME_RANK[outcome] > _OUTCOME_RANK[row[0]] else row[0]
                    conn.execute(
                        "UPDATE sessions SET updated_at=?, turns=turns+1, "
                        "after_hours_turns=after_hours_turns+?, outcome=?, input_tokens=?, "
                        "output_tokens=?, model=? WHERE session_key=?",
                        (now, 1 if after_hours else 0, best, row[1] + int(input_tokens),
                         row[2] + int(output_tokens), model, key),
                    )
                conn.commit()
            finally:
                conn.close()
    except Exception as exc:  # never surface to the customer
        log.warning("analytics capture failed: %s", exc)


# --- read helpers (used by the selftest now; the digest/report will use these later) -----


def load_session(client: str, channel: str, user_id: str) -> dict[str, Any] | None:
    key = f"{client}:{channel}:{_hash_user(user_id)}"
    conn = _connect()
    try:
        cols = [c[1] for c in conn.execute("PRAGMA table_info(sessions)").fetchall()]
        row = conn.execute("SELECT * FROM sessions WHERE session_key=?", (key,)).fetchone()
        return dict(zip(cols, row)) if row else None
    finally:
        conn.close()
