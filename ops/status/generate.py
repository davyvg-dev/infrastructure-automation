#!/usr/bin/env python3
"""Klantkraan status page generator — one static page, no JS, no database.

Reads only state that already exists on this host (analytics.db, pipeline yamls,
outreach ledger, growth-engine queues, billing.jsonl, systemd) and renders it in
phone-glance order: RAG header, today's numbers, deals due, outreach, content
queue, billing, timer matrix. Every collector is fault-isolated: a broken source
turns its section amber instead of killing the page.

The deal board and outreach ledger live on the founder's Mac (deploy.sh excludes
ai-receptionist/data), so on the server those two sections come from an optional
pushed snapshot (`kk status push` writes data/status-snapshot.json here) and carry
its age.

Run with the ai-receptionist venv so app.* / scripts.* imports resolve:

    cd ai-receptionist && ./.venv/bin/python ../ops/status/generate.py --ansi

On the server, klantkraan-status.timer runs `--html /var/www/status/index.html`
every 15 minutes; Caddy serves it behind basic auth at status.<demo-host>.
"""

from __future__ import annotations

import argparse
import html
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AIR = REPO_ROOT / "ai-receptionist"
SNAPSHOT_PATH = AIR / "data" / "status-snapshot.json"
REGEN_MINUTES = 15  # keep in sync with ops/hetzner/klantkraan-status.timer
STALE_RUN_HOURS = 26  # digest/analyst are daily; a day + slack means the timer broke
SNAPSHOT_STALE_HOURS = 72

sys.path.insert(0, str(AIR))


def _safe(fn, *args):
    """Run one collector; a failure becomes data instead of a crash."""
    try:
        return fn(*args)
    except Exception as exc:  # noqa: BLE001 — the page must render past any one source
        return {"error": f"{type(exc).__name__}: {exc}"}


def _run(argv: list[str]) -> str | None:
    """Capture a command's stdout; None when the tool is absent or fails (e.g. no
    systemd on the Mac)."""
    try:
        proc = subprocess.run(argv, capture_output=True, text=True, timeout=20, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return proc.stdout if proc.returncode == 0 else None


# --------------------------------------------------------------------------- #
# Collectors (I/O) — one per section
# --------------------------------------------------------------------------- #


def collect_health(now: datetime) -> dict:
    state_path = AIR / "data" / "watchdog_state.json"
    watchdog = None
    if state_path.exists():
        raw = json.loads(state_path.read_text(encoding="utf-8"))
        age_min = (now.timestamp() - raw.get("ts", 0)) / 60
        watchdog = {
            "status": raw.get("status", "?"),
            "deep_status": raw.get("deep_status", "?"),
            "age_min": round(age_min),
        }

    failed_out = _run(["systemctl", "list-units", "--failed", "--plain", "--no-legend"])
    has_systemd = failed_out is not None
    failed = [ln.split()[0] for ln in failed_out.splitlines() if ln.strip()] if failed_out else []

    # Last successful run of the daily oneshots; a silent-dead timer is the failure
    # mode this whole command center exists to surface.
    last_run: dict[str, float | None] = {}
    if has_systemd:
        for unit in ("ai-receptionist-digest", "ai-receptionist-analyst"):
            out = _run(["systemctl", "show", f"{unit}.service",
                        "-p", "ExecMainExitTimestamp", "--value"])
            last_run[unit] = _timestamp_age_hours(out, now)

    alerts = None  # None = can't tell (no .env here); True/False otherwise
    env_path = AIR / ".env"
    if env_path.exists():
        alerts = _alerts_configured(env_path.read_text(encoding="utf-8"))

    return {
        "watchdog": watchdog,
        "has_systemd": has_systemd,
        "failed_units": failed,
        "last_run_hours": last_run,
        "alerts_configured": alerts,
    }


def _timestamp_age_hours(systemctl_value: str | None, now: datetime) -> float | None:
    """Age of a `systemctl show --value` timestamp like 'Tue 2026-08-12 07:30:02 CEST'."""
    if not systemctl_value or not systemctl_value.strip():
        return None
    parts = systemctl_value.split()
    for i in range(len(parts) - 1):
        try:
            # systemctl prints the host's local time; everything here compares local-naive.
            then = datetime.strptime(f"{parts[i]} {parts[i + 1]}", "%Y-%m-%d %H:%M:%S")  # noqa: DTZ007
        except ValueError:
            continue
        return round((now - then).total_seconds() / 3600, 1)
    return None


def _alerts_configured(env_text: str) -> bool:
    """Mirror of kk's ALERT_CONFIG_CHECK: Telegram (chat id + a token) or e-mail pair."""
    keys = {}
    for line in env_text.splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            keys[k.strip()] = v.strip()
    telegram = bool(keys.get("OWNER_TELEGRAM_CHAT_ID")) and bool(
        keys.get("NOTIFY_TELEGRAM_TOKEN") or keys.get("TELEGRAM_BOT_TOKEN")
    )
    email = bool(keys.get("OWNER_EMAIL")) and bool(keys.get("RESEND_API_KEY"))
    return telegram or email


def collect_today(now: datetime) -> dict:
    from app import analytics
    from app.oversight import _day_window, cost_eur

    start, end, label = _day_window(now, today=True)
    rows = []
    totals = {"conversations": 0, "leads": 0, "bookings": 0, "cost_eur": 0.0}
    for slug in analytics.active_clients(start, end):
        s = analytics.daily_stats(slug, start, end)
        c = cost_eur(s["token_by_model"])
        rows.append({"client": slug, "conversations": s["conversations"],
                     "leads": s["leads"], "bookings": s["bookings"], "cost_eur": round(c, 2)})
        totals["conversations"] += s["conversations"]
        totals["leads"] += s["leads"]
        totals["bookings"] += s["bookings"]
        totals["cost_eur"] = round(totals["cost_eur"] + c, 2)
    return {"label": label, "totals": totals, "clients": rows}


def collect_deals(now: datetime) -> dict:
    from app.pipeline import NEXT_ACTION, STAGES, all_records

    records = all_records()
    today = now.strftime("%Y-%m-%d")
    counts = {s: 0 for s in STAGES}
    active, due = [], []
    for rec in records:
        status = rec.get("status", "lead")
        if status in counts:
            counts[status] += 1
            active.append({
                "slug": rec.get("slug", "?"),
                "business": rec.get("business", ""),
                "status": status,
                "next_action": NEXT_ACTION.get(status, ""),
                "next_call": rec.get("next_call"),
            })
        if rec.get("next_call") and rec["next_call"] <= today:
            due.append({"slug": rec.get("slug", "?"), "next_call": rec["next_call"]})
    due.sort(key=lambda d: d["next_call"])
    return {"total": len(records), "counts": counts, "active": active, "due_callbacks": due}


def collect_outreach(now: datetime) -> dict:
    from scripts.sequence import LAST_TOUCH, PROSPECTS, SUPPRESSION, load, queue

    ledger = load()
    # The ledger stamps tz-aware UTC; queue() subtracts, so hand it an aware now.
    due = dict(queue(list(PROSPECTS), ledger, now.astimezone()))
    done = sum(1 for r in ledger.values() if r.done)
    at_last = sum(1 for r in ledger.values() if not r.done and r.last_touch >= LAST_TOUCH)
    suppressed = 0
    if SUPPRESSION.exists():
        suppressed = sum(1 for ln in SUPPRESSION.read_text(encoding="utf-8").splitlines()
                         if ln.strip())
    return {
        "prospects": len(PROSPECTS),
        "due_today": [{"slug": p.slug, "touch": t} for p, t in sorted(
            due.items(), key=lambda kv: kv[0].slug)],
        "closed": done,
        "sequence_complete": at_last,
        "suppressed": suppressed,
        # Phase 1 step 5: replies/DSNs live in the 07:30 digest (app.mail_signals).
        "dsn_note": "replies/DSNs: in the 07:30 morning digest",
    }


def collect_content(now: datetime) -> dict:
    verticals = []
    for qp in sorted((REPO_ROOT / "growth-engine" / "data").glob("*/queue.json")):
        try:
            drafts = json.loads(qp.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            verticals.append({"vertical": qp.parent.name, "error": str(exc)})
            continue
        if not isinstance(drafts, list):
            continue
        counts: dict[str, int] = {}
        errors = []
        for d in drafts:
            counts[d.get("status", "?")] = counts.get(d.get("status", "?"), 0) + 1
            for key, val in d.items():
                if key.endswith("_error"):
                    errors.append(f"{d.get('id', '?')} {key[:-6]}: {val}")
        verticals.append({
            "vertical": qp.parent.name,
            "total": len(drafts),
            "counts": counts,
            "dry_run": sum(1 for d in drafts if d.get("dry_run")),
            "push_errors": errors,
        })
    return {"verticals": verticals}


def collect_billing(now: datetime) -> dict:
    path = AIR / "data" / "billing.jsonl"
    events = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return summarize_billing(events)


def summarize_billing(events: list[dict]) -> dict:
    """Active subs + MRR from the append-only ledger: a subscription_created webhook
    opens one, cancel/offboard for the same customer closes it."""
    subs: dict[str, float] = {}
    last_webhook = None
    counts: dict[str, int] = {}
    for ev in events:
        kind = ev.get("event", "?")
        counts[kind] = counts.get(kind, 0) + 1
        if kind == "webhook":
            last_webhook = ev.get("at")
            if ev.get("action") == "subscription_created" and ev.get("customer_id"):
                try:
                    subs[ev["customer_id"]] = float(str(ev.get("monthly_eur", 0)).replace(",", "."))
                except ValueError:
                    subs[ev["customer_id"]] = 0.0
        elif kind in ("cancel", "offboard"):
            subs.pop(ev.get("customer_id", ""), None)
    return {
        "events": len(events),
        "counts": counts,
        "active_subs": len(subs),
        "mrr_eur": round(sum(subs.values()), 2),
        "last_webhook": last_webhook,
        "last_event": events[-1].get("at") if events else None,
    }


def collect_timers(now: datetime) -> dict:
    out = _run(["systemctl", "list-timers", "--all", "--no-pager"])
    return {"matrix": out.rstrip() if out else None}


COLLECTORS = [
    ("health", collect_health),
    ("today", collect_today),
    ("deals", collect_deals),
    ("outreach", collect_outreach),
    ("content", collect_content),
    ("billing", collect_billing),
    ("timers", collect_timers),
]


def collect(now: datetime | None = None) -> dict:
    now = now or datetime.now()  # noqa: DTZ005 — local-naive, same clock analytics stamps with
    data: dict = {"generated_at": now.isoformat(timespec="seconds"), "sections": {}}
    for name, fn in COLLECTORS:
        data["sections"][name] = _safe(fn, now)

    # No deal records on this host (the board lives on the Mac): fall back to the
    # snapshot `kk status push` left here, and carry its age so staleness is visible.
    deals = data["sections"]["deals"]
    if (deals.get("error") or deals.get("total") == 0) and SNAPSHOT_PATH.exists():
        snap = _safe(lambda: json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8")))
        if not snap.get("error"):
            data["sections"]["deals"] = snap.get("deals", deals)
            data["sections"]["outreach"] = snap.get("outreach", data["sections"]["outreach"])
            data["snapshot_at"] = snap.get("generated_at")

    data["rag"] = rag(data, now)
    return data


# --------------------------------------------------------------------------- #
# RAG verdict (pure)
# --------------------------------------------------------------------------- #


def rag(data: dict, now: datetime) -> dict:
    """Worst-signal-wins traffic light. Red = the product or a unit is down;
    amber = something is stale, unreadable, or alerting is dark; green otherwise."""
    red: list[str] = []
    amber: list[str] = []
    s = data["sections"]

    health = s.get("health", {})
    wd = health.get("watchdog")
    if wd:
        if wd["status"] == "down":
            red.append("receptionist DOWN (watchdog)")
        elif wd["deep_status"] == "silent":
            red.append("receptionist up but NOT ANSWERING (watchdog deep probe)")
        if health.get("has_systemd") and wd["age_min"] > 60:
            amber.append(f"watchdog state {wd['age_min']} min old — its timer may be broken")
    elif health.get("has_systemd"):
        amber.append("no watchdog state on this host")
    for unit in health.get("failed_units", []):
        red.append(f"failed unit: {unit}")
    for unit, age_h in (health.get("last_run_hours") or {}).items():
        if age_h is None:
            amber.append(f"{unit}: never ran")
        elif age_h > STALE_RUN_HOURS:
            amber.append(f"{unit}: last success {age_h:.0f}h ago")
    # Only meaningful where the units run; the Mac .env legitimately lacks owner keys.
    if health.get("has_systemd") and health.get("alerts_configured") is False:
        amber.append("ALERTS UNCONFIGURED — unit failures land only in the journal")

    for name, section in s.items():
        if isinstance(section, dict) and section.get("error"):
            amber.append(f"{name}: {section['error']}")

    for v in s.get("content", {}).get("verticals", []):
        for err in v.get("push_errors", []):
            amber.append(f"content push failed [{v['vertical']}]: {err}")

    snap_at = data.get("snapshot_at")
    if snap_at:
        try:
            age_h = (now - datetime.fromisoformat(snap_at)).total_seconds() / 3600
            if age_h > SNAPSHOT_STALE_HOURS:
                amber.append(f"deal/outreach snapshot {age_h / 24:.0f}d old — run: kk status push")
        except ValueError:
            amber.append("deal/outreach snapshot has no readable timestamp")

    level = "red" if red else ("amber" if amber else "green")
    return {"level": level, "reasons": red + amber}


# --------------------------------------------------------------------------- #
# Renderers
# --------------------------------------------------------------------------- #


def _section_lines(data: dict) -> list[tuple[str, list[str]]]:
    """The page content as (title, lines) — one source for both renderers."""
    s = data["sections"]
    out: list[tuple[str, list[str]]] = []

    t = s.get("today", {})
    if t.get("error"):
        out.append(("Vandaag", [f"unavailable: {t['error']}"]))
    else:
        tot = t.get("totals", {})
        lines = [(f"{tot.get('conversations', 0)} conversations · {tot.get('leads', 0)} leads · "
                  f"{tot.get('bookings', 0)} bookings · ~€{tot.get('cost_eur', 0.0):.2f}")]
        for row in t.get("clients", []):
            lines.append(f"{row['client']}: {row['conversations']} conv · {row['leads']} leads · "
                         f"{row['bookings']} booked · ~€{row['cost_eur']:.2f}")
        if not t.get("clients"):
            lines.append("no conversations yet today")
        out.append((f"Vandaag — {t.get('label', '')}", lines))

    d = s.get("deals", {})
    title = "Deals"
    if data.get("snapshot_at"):
        title += f" (snapshot {data['snapshot_at'][:16]})"
    if d.get("error"):
        out.append((title, [f"unavailable: {d['error']}"]))
    else:
        lines = [" · ".join(f"{k} {v}" for k, v in d.get("counts", {}).items())]
        for cb in d.get("due_callbacks", []):
            lines.append(f"CALL DUE {cb['next_call']}  {cb['slug']}")
        hot = [a for a in d.get("active", []) if a["status"] in
               ("demo", "signed", "onboarding")]
        for a in hot:
            lines.append(f"{a['slug']} [{a['status']}] → {a['next_action']}")
        if d.get("total", 0) == 0:
            lines = ["no deal data on this host — run: kk status push"]
        out.append((title, lines))

    o = s.get("outreach", {})
    if o.get("error"):
        out.append(("Outreach", [f"unavailable: {o['error']}"]))
    else:
        due = o.get("due_today", [])
        lines = [(f"{o.get('prospects', 0)} prospects · {len(due)} due today · "
                  f"{o.get('closed', 0)} closed · {o.get('suppressed', 0)} suppressed")]
        for item in due:
            lines.append(f"due: {item['slug']} → touch {item['touch']}")
        if o.get("dsn_note"):
            lines.append(o["dsn_note"])
        out.append(("Outreach", lines))

    c = s.get("content", {})
    if c.get("error"):
        out.append(("Content", [f"unavailable: {c['error']}"]))
    else:
        lines = []
        for v in c.get("verticals", []):
            if v.get("error"):
                lines.append(f"{v['vertical']}: unreadable ({v['error']})")
                continue
            summary = ", ".join(f"{n} {st}" for st, n in sorted(v["counts"].items()))
            dry = f" ({v['dry_run']} dry-run)" if v.get("dry_run") else ""
            lines.append(f"{v['vertical']}: {v['total']} drafts — {summary}{dry}")
            for err in v.get("push_errors", []):
                lines.append(f"  push failed: {err}")
        out.append(("Content", lines or ["no content queues on this host"]))

    b = s.get("billing", {})
    if b.get("error"):
        out.append(("Billing", [f"unavailable: {b['error']}"]))
    else:
        lines = [(f"{b.get('active_subs', 0)} active subs · MRR €{b.get('mrr_eur', 0.0):.2f} · "
                  f"{b.get('events', 0)} ledger events")]
        lines.append(f"last webhook: {b.get('last_webhook') or 'never'} · "
                     f"last event: {b.get('last_event') or 'never'}")
        out.append(("Billing", lines))

    return out


def render_ansi(data: dict) -> str:
    colors = {"green": "\033[32m", "amber": "\033[33m", "red": "\033[31m"}
    reset = "\033[0m"
    level = data["rag"]["level"]
    lines = [(f"{colors[level]}● {level.upper()}{reset}  klantkraan status — "
              f"generated {data['generated_at'][:16]}")]
    for reason in data["rag"]["reasons"]:
        lines.append(f"  ! {reason}")
    for title, body in _section_lines(data):
        lines.append("")
        lines.append(title.upper())
        lines.extend(f"  {ln}" for ln in body)
    matrix = data["sections"].get("timers", {}).get("matrix")
    if matrix:
        lines += ["", "TIMERS", *(f"  {ln}" for ln in matrix.splitlines())]
    return "\n".join(lines)


_HTML_COLORS = {"green": "#1a7f37", "amber": "#b58900", "red": "#c0392b"}


def render_html(data: dict) -> str:
    level = data["rag"]["level"]
    esc = html.escape
    reasons = "".join(f"<li>{esc(r)}</li>" for r in data["rag"]["reasons"])
    sections = []
    for title, body in _section_lines(data):
        items = "".join(f"<li>{esc(ln)}</li>" for ln in body)
        sections.append(f"<section><h2>{esc(title)}</h2><ul>{items}</ul></section>")
    matrix = data["sections"].get("timers", {}).get("matrix")
    if matrix:
        sections.append(f"<section><h2>Timers</h2><pre>{esc(matrix)}</pre></section>")
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="{REGEN_MINUTES * 60}">
<meta name="robots" content="noindex">
<title>Klantkraan status</title>
<style>
  body {{ font: 15px/1.5 -apple-system, system-ui, sans-serif; margin: 0; padding: 0 0 2rem;
         background: #f6f5f2; color: #222; }}
  header {{ background: {_HTML_COLORS[level]}; color: #fff; padding: 1rem 1.2rem; }}
  header h1 {{ margin: 0; font-size: 1.15rem; }}
  header p {{ margin: .3rem 0 0; opacity: .9; font-size: .85rem; }}
  header ul {{ margin: .5rem 0 0; padding-left: 1.2rem; font-size: .9rem; }}
  section {{ background: #fff; margin: .8rem; padding: .8rem 1rem; border-radius: 8px;
             box-shadow: 0 1px 2px rgba(0,0,0,.06); }}
  h2 {{ margin: 0 0 .4rem; font-size: .8rem; text-transform: uppercase;
        letter-spacing: .05em; color: #666; }}
  ul {{ margin: 0; padding-left: 1.1rem; }}
  li {{ margin: .15rem 0; }}
  pre {{ margin: 0; font-size: .72rem; overflow-x: auto; }}
</style></head><body>
<header>
  <h1>&#9679; {level.upper()} — Klantkraan</h1>
  <p>generated {esc(data["generated_at"][:16])} · regenerates every {REGEN_MINUTES} min —
     if this is older than {REGEN_MINUTES + 5} min, the status timer itself is broken</p>
  {f"<ul>{reasons}</ul>" if reasons else ""}
</header>
{"".join(sections)}
</body></html>
"""


def build_snapshot(data: dict) -> dict:
    """The Mac-side sections the server can't see, for `kk status push`."""
    return {
        "generated_at": data["generated_at"],
        "deals": data["sections"]["deals"],
        "outreach": data["sections"]["outreach"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--html", metavar="PATH", help="write the static page here")
    mode.add_argument("--ansi", action="store_true", help="print to the terminal (default)")
    mode.add_argument("--snapshot", metavar="PATH",
                      help="write the deals+outreach snapshot JSON here (for kk status push)")
    mode.add_argument("--json", action="store_true", help="dump the raw collected data")
    args = parser.parse_args(argv)

    data = collect()
    if args.html:
        out = Path(args.html)
        tmp = out.with_suffix(".tmp")  # atomic-ish: never serve a half-written page
        tmp.write_text(render_html(data), encoding="utf-8")
        tmp.replace(out)
        print(f"wrote {out} ({data['rag']['level']})")
    elif args.snapshot:
        Path(args.snapshot).write_text(
            json.dumps(build_snapshot(data), indent=1), encoding="utf-8")
        print(f"wrote {args.snapshot}")
    elif args.json:
        print(json.dumps(data, indent=1, default=str))
    else:
        print(render_ansi(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
