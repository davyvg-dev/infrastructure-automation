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
hash — never in the clear. Transcript text is stored as-is for the analyst layer, then
purged on an AVG retention window (purge_transcripts) — the aggregated `sessions` rollup,
which holds no message text, is kept as the ROI history.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import sqlite3
import sys
import threading
from datetime import datetime, time as dtime, timedelta
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
    # Layer 2: one row per analysed conversation. Derived by the nightly Claude "analyst"
    # (oversight.analyze_pending); kept beyond the transcript retention window since it holds
    # aggregated, lower-PII intelligence, not raw message text. See docs/client-intelligence.md.
    conn.execute(
        """CREATE TABLE IF NOT EXISTS insights (
            session_key       TEXT PRIMARY KEY,
            client            TEXT NOT NULL,
            analyzed_at       TEXT NOT NULL,
            analyst_model     TEXT,
            intent            TEXT,
            topics_json       TEXT,
            resolved          INTEGER,
            escalated         INTEGER,
            escalation_reason TEXT,
            unanswered_json   TEXT,
            out_of_scope_json TEXT,
            sentiment         TEXT,
            language          TEXT,
            customer_type     TEXT,
            lead_captured     INTEGER,
            booking_made      INTEGER,
            est_job_value_eur REAL,
            upsell_json       TEXT,
            quality_json      TEXT
        )"""
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_insights_client ON insights(client, analyzed_at)")
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


# --- retention (AVG) ---------------------------------------------------------------------

# Default window for keeping raw transcript text. 90 days is the top of the doc's 30-90d band;
# override with ANALYTICS_RETENTION_DAYS. The `sessions` rollup outlives this — it carries no
# message text, only counts/tokens/outcome, so it stays as the per-client ROI history.
_DEFAULT_RETENTION_DAYS = 90


def _retention_days() -> int:
    raw = os.getenv("ANALYTICS_RETENTION_DAYS", "")
    try:
        days = int(raw)
    except ValueError:
        return _DEFAULT_RETENTION_DAYS
    # A non-positive window would wipe all history — treat a misconfig as the safe default.
    return days if days >= 1 else _DEFAULT_RETENTION_DAYS


def purge_transcripts(retention_days: int | None = None, now: datetime | None = None) -> int:
    """Delete raw `turns` rows older than the retention window; return how many were removed.

    Only transcript text is purged — the aggregated `sessions` rollup is untouched, so
    per-client counts/tokens/ROI survive indefinitely while message content does not.

    Ordering note: the nightly analyst (Layer 2) reads `turns` well inside this window and
    persists its findings to `insights`, so purging old transcripts never costs an analysis.
    """
    days = _retention_days() if retention_days is None else retention_days
    now = now or datetime.now()
    cutoff = (now - timedelta(days=days)).isoformat(timespec="seconds")
    try:
        with _LOCK:
            conn = _connect()
            try:
                cur = conn.execute("DELETE FROM turns WHERE ts < ?", (cutoff,))
                conn.commit()
                deleted = cur.rowcount
            finally:
                conn.close()
        log.info("retention: purged %d transcript turn(s) older than %s", deleted, cutoff)
        return deleted
    except Exception as exc:
        log.warning("retention purge failed: %s", exc)
        return 0


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


def _count_turns() -> int:
    conn = _connect()
    try:
        return int(conn.execute("SELECT COUNT(*) FROM turns").fetchone()[0])
    finally:
        conn.close()


def active_clients(start_iso: str, end_iso: str) -> list[str]:
    """Slugs with at least one captured turn in [start_iso, end_iso)."""
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT DISTINCT client FROM turns WHERE ts >= ? AND ts < ? ORDER BY client",
            (start_iso, end_iso),
        ).fetchall()
        return [r[0] for r in rows]
    finally:
        conn.close()


def daily_stats(client: str, start_iso: str, end_iso: str) -> dict[str, Any]:
    """Aggregate one client's captured activity in [start_iso, end_iso) — the hard,
    deterministic numbers behind the oversight digest and (later) the client ROI report.

    A conversation is a distinct session in the window; leads/bookings are distinct sessions
    whose strongest in-window outcome was a message / a booking. Tokens are split by model so
    the caller can price them. Read-only; the analyst layer never touches this.
    """
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT t.session_key, t.outcome, t.after_hours, t.input_tokens, t.output_tokens, "
            "s.model FROM turns t LEFT JOIN sessions s ON t.session_key = s.session_key "
            "WHERE t.client = ? AND t.ts >= ? AND t.ts < ?",
            (client, start_iso, end_iso),
        ).fetchall()
    finally:
        conn.close()

    sessions: set[str] = set()
    booked: set[str] = set()
    messaged: set[str] = set()
    after_hours = 0
    token_by_model: dict[str, list[int]] = {}
    for key, outcome, ah, in_tok, out_tok, model in rows:
        sessions.add(key)
        if ah:
            after_hours += 1
        if outcome == "booked":
            booked.add(key)
        elif outcome == "message":
            messaged.add(key)
        m = model or ""
        slot = token_by_model.setdefault(m, [0, 0])
        slot[0] += int(in_tok or 0)
        slot[1] += int(out_tok or 0)

    leads = messaged - booked  # a booked conversation is counted as a booking, not a lead
    return {
        "conversations": len(sessions),
        "turns": len(rows),
        "after_hours_turns": after_hours,
        "leads": len(leads),
        "bookings": len(booked),
        "token_by_model": {m: {"input": v[0], "output": v[1]} for m, v in token_by_model.items()},
    }


# --- Layer 2: transcripts in, insights out (the analyst reads/writes these) --------------

_INSIGHT_COLS = (
    "session_key", "client", "analyzed_at", "analyst_model", "intent", "topics_json",
    "resolved", "escalated", "escalation_reason", "unanswered_json", "out_of_scope_json",
    "sentiment", "language", "customer_type", "lead_captured", "booking_made",
    "est_job_value_eur", "upsell_json", "quality_json",
)


def pending_for_analysis(settled_before_iso: str, limit: int = 200) -> list[tuple[str, str]]:
    """(session_key, client) for settled sessions (last activity before the cutoff) that have
    no insight row yet — the analyst's work list. Settled avoids analysing a live chat."""
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT s.session_key, s.client FROM sessions s "
            "LEFT JOIN insights i ON s.session_key = i.session_key "
            "WHERE i.session_key IS NULL AND s.updated_at < ? ORDER BY s.updated_at LIMIT ?",
            (settled_before_iso, limit),
        ).fetchall()
        return [(r[0], r[1]) for r in rows]
    finally:
        conn.close()


def transcript(session_key: str) -> list[dict[str, str]]:
    """The ordered {user, reply} exchanges of one conversation (empty if already purged)."""
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT user_text, reply FROM turns WHERE session_key = ? ORDER BY id",
            (session_key,),
        ).fetchall()
        return [{"user": r[0] or "", "reply": r[1] or ""} for r in rows]
    finally:
        conn.close()


def save_insight(session_key: str, client: str, model: str, ins: dict[str, Any],
                 now: datetime | None = None) -> None:
    """Persist one analysed conversation. Arrays are stored as JSON; booleans as 0/1."""
    now = (now or datetime.now()).isoformat(timespec="seconds")
    values = (
        session_key, client, now, model,
        ins.get("intent", ""),
        json.dumps(ins.get("topics", []), ensure_ascii=False),
        1 if ins.get("resolved") else 0,
        1 if ins.get("escalated") else 0,
        ins.get("escalation_reason", ""),
        json.dumps(ins.get("unanswered_questions", []), ensure_ascii=False),
        json.dumps(ins.get("out_of_scope_requests", []), ensure_ascii=False),
        ins.get("sentiment", ""),
        ins.get("language", ""),
        ins.get("customer_type", ""),
        1 if ins.get("lead_captured") else 0,
        1 if ins.get("booking_made") else 0,
        float(ins.get("est_job_value_eur", 0) or 0),
        json.dumps(ins.get("upsell_signals", []), ensure_ascii=False),
        json.dumps(ins.get("quality_flags", []), ensure_ascii=False),
    )
    conn = _connect()
    try:
        placeholders = ",".join("?" * len(_INSIGHT_COLS))
        conn.execute(
            f"INSERT OR REPLACE INTO insights ({','.join(_INSIGHT_COLS)}) VALUES ({placeholders})",
            values,
        )
        conn.commit()
    finally:
        conn.close()


def insights_for_client(client: str, limit: int = 100) -> list[dict[str, Any]]:
    """Most-recent insight rows for one client, JSON columns decoded back to lists."""
    conn = _connect()
    try:
        cols = [c[1] for c in conn.execute("PRAGMA table_info(insights)").fetchall()]
        rows = conn.execute(
            "SELECT * FROM insights WHERE client = ? ORDER BY analyzed_at DESC LIMIT ?",
            (client, limit),
        ).fetchall()
    finally:
        conn.close()
    out = []
    for row in rows:
        d = dict(zip(cols, row))
        for key in ("topics_json", "unanswered_json", "out_of_scope_json", "upsell_json",
                    "quality_json"):
            try:
                d[key] = json.loads(d.get(key) or "[]")
            except Exception:
                d[key] = []
        out.append(d)
    return out


# --- CLI: the cron/systemd-timer entry point for retention -------------------------------


def main(argv: list[str]) -> int:
    cmd = argv[1] if len(argv) > 1 else ""
    if cmd == "purge":
        deleted = purge_transcripts()
        print(f"purged {deleted} transcript turn(s) older than {_retention_days()} days")
        return 0
    print("usage: python -m app.analytics purge")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
