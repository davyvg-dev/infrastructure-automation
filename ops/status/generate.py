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


# --------------------------------------------------------------------------- #
# HTML renderer — the branded cockpit ("dit is de cockpit die u krijgt").
# render_ansi/_section_lines above stay the terminal path; this one reads the
# structured section dicts directly. Every dynamic value goes through
# html.escape; no <script> ever.
# --------------------------------------------------------------------------- #

RAG_HEX = {"green": "#63d3ab", "amber": "#ffb84d", "red": "#e0654f"}
RAG_GLOSS = {"green": "alles in bedrijf", "amber": "aandacht nodig", "red": "storing"}

FONT_SRC = REPO_ROOT / "klantkraan" / "apps" / "marketing-site" / "public" / "fonts"
FONT_FILES = (
    "bricolage-700-latin.woff2",
    "hanken-400-latin.woff2",
    "hanken-500-latin.woff2",
    "spacemono-400-latin.woff2",
    "spacemono-700-latin.woff2",
)

_MONTHS_NL = ("januari", "februari", "maart", "april", "mei", "juni", "juli",
              "augustus", "september", "oktober", "november", "december")


def _write_assets(out_dir: Path) -> None:
    """Copy the page's woff2 subsets next to it; a host without the marketing-site
    checkout just serves the system-font fallback stack."""
    if not FONT_SRC.is_dir():
        return
    dest = out_dir / "fonts"
    dest.mkdir(parents=True, exist_ok=True)
    for name in FONT_FILES:
        src, dst = FONT_SRC / name, dest / name
        if src.is_file() and not dst.exists():
            dst.write_bytes(src.read_bytes())


def _nl_dt(iso: str | None) -> str:
    if not iso:
        return "onbekend"
    try:
        dt = datetime.fromisoformat(str(iso))
    except ValueError:
        return str(iso)
    out = f"{dt.day} {_MONTHS_NL[dt.month - 1]} {dt.year}"
    if len(str(iso)) > 10:
        out += f", {dt.strftime('%H:%M')}"
    return out


def _eur(value) -> str:
    try:
        return f"€ {float(value):.2f}".replace(".", ",")
    except (TypeError, ValueError):
        return "€ ?"


def _chip(text, kind: str = "") -> str:
    cls = f"chip {kind}".strip()
    return f'<span class="{cls}">{html.escape(str(text))}</span>'


def _panel(title: str, body: str, *, span2: bool = False, fault: bool = False) -> str:
    cls = "panel" + (" span2" if span2 else "") + (" fault" if fault else "")
    return f'<section class="{cls}"><h2>{html.escape(title)}</h2>{body}</section>'


def _fault_panel(title: str, err) -> str:
    body = ('<p class="fault-msg">Bron niet leesbaar: '
            f"<code>{html.escape(str(err))}</code></p>")
    return _panel(title, body, fault=True)


def _table(headers: list[tuple[str, bool]], rows: list[list[str]]) -> str:
    """headers: (label, numeric); row cells arrive as ready-made html."""
    def cell(tag: str, content: str, numeric: bool) -> str:
        cls = ' class="num"' if numeric else ""
        return f"<{tag}{cls}>{content}</{tag}>"

    head = "".join(cell("th", html.escape(h), num) for h, num in headers)
    body = "".join(
        "<tr>" + "".join(cell("td", c, headers[i][1]) for i, c in enumerate(row)) + "</tr>"
        for row in rows)
    return ('<div class="scroll"><table>'
            f"<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>")


def _facts(pairs: list[tuple[str, str]]) -> str:
    """Label/value grid; values arrive as ready-made html."""
    items = "".join(f"<dt>{html.escape(k)}</dt><dd>{v}</dd>" for k, v in pairs)
    return f'<dl class="facts">{items}</dl>'


def _tiles(s: dict) -> str:
    t, b, o = s.get("today", {}), s.get("billing", {}), s.get("outreach", {})
    terr, berr, oerr = bool(t.get("error")), bool(b.get("error")), bool(o.get("error"))
    tot = {} if terr else (t.get("totals") or {})

    def num(d: dict, key, err: bool) -> str:
        return "?" if err else html.escape(str(d.get(key, 0)))

    tiles = [
        ("Gesprekken vandaag", num(tot, "conversations", terr)),
        ("Leads vandaag", num(tot, "leads", terr)),
        ("Afspraken vandaag", num(tot, "bookings", terr)),
        ("Kosten vandaag", "?" if terr else "~" + html.escape(_eur(tot.get("cost_eur", 0)))),
        ("MRR", "?" if berr else html.escape(_eur(b.get("mrr_eur", 0)))),
        ("Actieve abonnementen", num(b, "active_subs", berr)),
        ("Outreach vandaag", "?" if oerr else html.escape(str(len(o.get("due_today") or [])))),
    ]
    inner = "".join(f'<div class="tile"><b>{v}</b><span>{html.escape(k)}</span></div>'
                    for k, v in tiles)
    return f'<div class="tiles">{inner}</div>'


def _render_today(t: dict) -> str:
    if t.get("error"):
        return _fault_panel("Vandaag per klant", t["error"])
    esc = html.escape
    rows = [[esc(str(r.get("client", "?"))),
             esc(str(r.get("conversations", 0))),
             esc(str(r.get("leads", 0))),
             esc(str(r.get("bookings", 0))),
             esc(_eur(r.get("cost_eur", 0)))]
            for r in t.get("clients") or []]
    if rows:
        body = _table([("Klant", False), ("Gesprekken", True), ("Leads", True),
                       ("Afspraken", True), ("Kosten", True)], rows)
    else:
        body = '<p class="note">Nog geen gesprekken vandaag.</p>'
    return _panel("Vandaag per klant", body, span2=True)


def _render_deals(d: dict) -> str:
    if d.get("error"):
        return _fault_panel("Deals", d["error"])
    esc = html.escape
    if not d.get("total"):
        body = ('<p class="note">Geen dealgegevens op deze host. Voer op de Mac '
                "<code>kk status push</code> uit.</p>")
        return _panel("Deals", body, span2=True)
    parts = []
    chips = "".join(_chip(f"{st} {n}") for st, n in (d.get("counts") or {}).items())
    if chips:
        parts.append(f'<p class="chips">{chips}</p>')
    due = d.get("due_callbacks") or []
    if due:
        items = "".join(
            f"<li>{_chip('vandaag bellen', 'fill')} <strong>{esc(str(cb.get('slug', '?')))}"
            f"</strong> · gepland {esc(_nl_dt(cb.get('next_call')))}</li>"
            for cb in due)
        parts.append(f'<ul class="due">{items}</ul>')
    rows = [[esc(str(a.get("business") or a.get("slug") or "?")),
             _chip(a.get("status", "?")),
             esc(str(a.get("next_action") or "")),
             esc(_nl_dt(a["next_call"])) if a.get("next_call") else ""]
            for a in d.get("active") or []]
    if rows:
        parts.append(_table([("Klant", False), ("Status", False),
                             ("Volgende stap", False), ("Terugbellen", False)], rows))
    else:
        parts.append('<p class="note">Geen actieve deals.</p>')
    return _panel("Deals", "".join(parts), span2=True)


def _render_outreach(o: dict) -> str:
    if o.get("error"):
        return _fault_panel("Outreach", o["error"])
    esc = html.escape
    due = o.get("due_today") or []
    chips = "".join([
        _chip(f"{o.get('prospects', 0)} prospects"),
        _chip(f"{len(due)} vandaag te doen", "acc" if due else ""),
        _chip(f"{o.get('closed', 0)} afgesloten"),
        _chip(f"{o.get('sequence_complete', 0)} reeks voltooid"),
        _chip(f"{o.get('suppressed', 0)} uitgesloten"),
    ])
    parts = [f'<p class="chips">{chips}</p>']
    if due:
        rows = [[esc(str(i.get("slug", "?"))), esc(str(i.get("touch", "?")))] for i in due]
        parts.append(_table([("Prospect", False), ("Stap", True)], rows))
    if o.get("dsn_note"):
        parts.append(f'<p class="note">{esc(str(o["dsn_note"]))}</p>')
    return _panel("Outreach", "".join(parts))


def _render_content(c: dict) -> str:
    if c.get("error"):
        return _fault_panel("Content", c["error"])
    esc = html.escape
    blocks = []
    for v in c.get("verticals") or []:
        name = esc(str(v.get("vertical", "?")))
        if v.get("error"):
            blocks.append(f'<div class="vert"><h3>{name}</h3><p class="fault-msg">'
                          f'Wachtrij niet leesbaar: <code>{esc(str(v["error"]))}</code></p></div>')
            continue
        chips = _chip(f"{v.get('total', 0)} concepten")
        chips += "".join(_chip(f"{n} {st}") for st, n in sorted((v.get("counts") or {}).items()))
        if v.get("dry_run"):
            chips += _chip(f"{v['dry_run']} dry-run", "acc")
        warns = "".join(f'<p class="warnline">push mislukt: {esc(str(e))}</p>'
                        for e in v.get("push_errors") or [])
        blocks.append(f'<div class="vert"><h3>{name}</h3><p class="chips">{chips}</p>{warns}</div>')
    body = "".join(blocks) or '<p class="note">Geen contentwachtrijen op deze host.</p>'
    return _panel("Content", body)


def _render_billing(b: dict) -> str:
    if b.get("error"):
        return _fault_panel("Facturatie", b["error"])
    esc = html.escape
    facts = _facts([
        ("Actieve abonnementen", esc(str(b.get("active_subs", 0)))),
        ("MRR", esc(_eur(b.get("mrr_eur", 0)))),
        ("Ledgerregels", esc(str(b.get("events", 0)))),
        ("Laatste webhook", esc(_nl_dt(b.get("last_webhook")) if b.get("last_webhook")
                                else "nooit")),
        ("Laatste gebeurtenis", esc(_nl_dt(b.get("last_event")) if b.get("last_event")
                                    else "nooit")),
    ])
    chips = "".join(_chip(f"{n} {kind}") for kind, n in sorted((b.get("counts") or {}).items()))
    tail = f'<p class="chips">{chips}</p>' if chips else ""
    return _panel("Facturatie", facts + tail)


def _render_system(h: dict, tm: dict) -> str:
    esc = html.escape
    fault = False
    parts = []
    if h.get("error"):
        fault = True
        parts.append('<p class="fault-msg">Systeembron niet leesbaar: '
                     f"<code>{esc(str(h['error']))}</code></p>")
    else:
        pairs: list[tuple[str, str]] = []
        wd = h.get("watchdog")
        if wd:
            status = str(wd.get("status", "?"))
            kind = {"up": "ok", "down": "bad"}.get(status, "")
            status_txt = {"up": "in bedrijf", "down": "niet bereikbaar"}.get(status, status)
            deep = str(wd.get("deep_status", "?"))
            deep_txt = {"answering": "beantwoordt gesprekken",
                        "silent": "beantwoordt niet"}.get(deep, deep)
            pairs.append(("Receptionist", _chip(status_txt, kind) + " " + esc(deep_txt)))
            pairs.append(("Watchdogmeting", esc(f"{wd.get('age_min', '?')} min geleden")))
        else:
            pairs.append(("Receptionist", esc("geen watchdogmeting op deze host")))
        failed = h.get("failed_units") or []
        if failed:
            pairs.append(("Gefaalde units", "".join(_chip(u, "bad") for u in failed)))
        elif h.get("has_systemd"):
            pairs.append(("Gefaalde units", esc("geen")))
        for unit, age_h in (h.get("last_run_hours") or {}).items():
            val = "nooit gedraaid" if age_h is None else f"laatste succes {age_h:g} uur geleden"
            pairs.append((str(unit), esc(val)))
        alerts = h.get("alerts_configured")
        if alerts is True:
            pairs.append(("Alerts", _chip("geconfigureerd", "ok")))
        elif alerts is False:
            pairs.append(("Alerts", _chip("niet geconfigureerd", "acc")))
        parts.append(_facts(pairs))
    if tm.get("error"):
        fault = True
        parts.append('<p class="fault-msg">Timerbron niet leesbaar: '
                     f"<code>{esc(str(tm['error']))}</code></p>")
    elif tm.get("matrix"):
        parts.append('<h3>Timers</h3><div class="scroll">'
                     f'<pre class="ledger">{esc(str(tm["matrix"]))}</pre></div>')
    return _panel("Systeem", "".join(parts), span2=True, fault=fault)


_FONT_CSS = """\
@font-face{font-family:'Bricolage Grotesque';font-style:normal;font-weight:700;
font-display:swap;src:url('fonts/bricolage-700-latin.woff2') format('woff2')}
@font-face{font-family:'Hanken Grotesk';font-style:normal;font-weight:400;
font-display:swap;src:url('fonts/hanken-400-latin.woff2') format('woff2')}
@font-face{font-family:'Hanken Grotesk';font-style:normal;font-weight:500;
font-display:swap;src:url('fonts/hanken-500-latin.woff2') format('woff2')}
@font-face{font-family:'Space Mono';font-style:normal;font-weight:400;
font-display:swap;src:url('fonts/spacemono-400-latin.woff2') format('woff2')}
@font-face{font-family:'Space Mono';font-style:normal;font-weight:700;
font-display:swap;src:url('fonts/spacemono-700-latin.woff2') format('woff2')}
"""

_CSS = """\
:root{--night:#0f1c1e;--panel:#16292b;--panel-2:#1c3335;--line:#26403f;
--chalk:#f4efe6;--dim:#93a6a2;--sodium:#ffb84d;--sodium-soft:#ffd089;
--confirm:#63d3ab;--ember:#e0654f;--ink:#241603;--r:11px;
--sans:'Hanken Grotesk',system-ui,-apple-system,'Segoe UI',sans-serif;
--display:'Bricolage Grotesque',system-ui,sans-serif;
--mono:'Space Mono',ui-monospace,'SF Mono','Cascadia Mono',monospace}
*{box-sizing:border-box}
body{margin:0;background:var(--night);color:var(--chalk);
font:400 15px/1.55 var(--sans);padding:0 0 2.5rem}
body.rag-green{--rag:var(--confirm)}
body.rag-amber{--rag:var(--sodium)}
body.rag-red{--rag:var(--ember)}
.ragbar{height:3px;background:var(--rag)}
.wrap{max-width:1060px;margin:0 auto;padding:0 clamp(14px,3vw,28px)}
header{display:flex;flex-wrap:wrap;align-items:flex-end;
justify-content:space-between;gap:12px 20px;padding:26px 0 4px}
.eyebrow{margin:0;font:700 11px/1.4 var(--mono);letter-spacing:.18em;
text-transform:uppercase;color:var(--sodium)}
h1{margin:2px 0 0;font:700 clamp(1.55rem,4vw,2.1rem)/1.05 var(--display);
letter-spacing:-.01em}
.meta{margin:.4rem 0 0;color:var(--dim);font-size:.85rem}
.meta.warn{color:var(--sodium)}
code{font-family:var(--mono);font-size:.92em;color:var(--sodium-soft)}
.pill{display:inline-flex;align-items:center;gap:.55em;border:1px solid var(--rag);
border-radius:999px;padding:.45em .95em;font:700 12px/1 var(--mono);
letter-spacing:.08em;white-space:nowrap}
.dot{width:9px;height:9px;border-radius:50%;background:var(--rag);flex:none}
.reasons{margin:14px 0 0;border:1px solid var(--line);border-left:3px solid var(--rag);
border-radius:var(--r);background:linear-gradient(var(--panel-2),var(--panel));
padding:12px 16px}
.reasons h2{margin:0;font:700 11px/1.4 var(--mono);letter-spacing:.16em;
text-transform:uppercase;color:var(--dim)}
.reasons ul{margin:.4rem 0 0;padding:0;list-style:none}
.reasons li{display:flex;gap:.6em;padding:.15rem 0;font-size:.9rem;
overflow-wrap:anywhere}
.reasons .dot{margin-top:.42em;width:7px;height:7px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(124px,1fr));
gap:12px;margin:18px 0 12px}
.tile{background:linear-gradient(var(--panel-2),var(--panel));
border:1px solid var(--line);border-radius:var(--r);padding:14px 16px 11px}
.tile b{display:block;font:700 1.5rem/1.15 var(--mono)}
.tile span{display:block;margin-top:3px;font-size:10.5px;font-weight:500;
letter-spacing:.08em;text-transform:uppercase;color:var(--dim)}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.panel{background:linear-gradient(var(--panel-2),var(--panel));
border:1px solid var(--line);border-radius:var(--r);padding:16px 18px;min-width:0}
.panel.span2{grid-column:1/-1}
.panel.fault{border-color:var(--sodium)}
.panel h2{margin:0 0 .7rem;font:700 11px/1.4 var(--mono);letter-spacing:.16em;
text-transform:uppercase;color:var(--dim)}
.panel h3{margin:.9rem 0 .4rem;font:700 .95rem/1.3 var(--display)}
.panel h3:first-child{margin-top:0}
.fault-msg{margin:.3rem 0;overflow-wrap:anywhere}
.meta{overflow-wrap:anywhere}
.scroll{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:.9rem}
th{font:500 10.5px/1.4 var(--sans);letter-spacing:.08em;text-transform:uppercase;
color:var(--dim);text-align:left;padding:.3rem .9rem .3rem 0;
border-bottom:1px solid var(--line)}
td{padding:.45rem .9rem .45rem 0;border-bottom:1px solid var(--line);
vertical-align:top}
tr:last-child td{border-bottom:0}
th.num,td.num{font-family:var(--mono);text-align:right;white-space:nowrap}
th:last-child,td:last-child{padding-right:0}
.chip{display:inline-block;border:1px solid var(--line);border-radius:999px;
padding:.16em .7em;font-size:.78rem;color:var(--dim);margin:0 .3em .25em 0;
white-space:nowrap}
.chip.acc{border-color:var(--sodium);color:var(--sodium)}
.chip.ok{border-color:var(--confirm);color:var(--confirm)}
.chip.bad{border-color:var(--ember);color:var(--ember)}
.chip.fill{background:var(--sodium);border-color:var(--sodium);color:var(--ink);
font-weight:700}
.chips{margin:.1rem 0 .4rem}
.due{margin:.2rem 0 .7rem;padding:0;list-style:none}
.due li{padding:.3rem 0;font-size:.92rem}
.note{color:var(--dim);font-size:.85rem;margin:.5rem 0 0}
.warnline{color:var(--sodium);font-size:.85rem;margin:.25rem 0}
.facts{display:grid;grid-template-columns:auto 1fr;gap:.3rem 1.2rem;margin:0}
.facts dt{color:var(--dim);font-size:.85rem;padding-top:.1em}
.facts dd{margin:0;font-size:.92rem}
.ledger{margin:0;font:400 11.5px/1.5 var(--mono);white-space:pre}
footer{margin-top:22px;color:var(--dim);font-size:.8rem}
@media(max-width:760px){.grid{grid-template-columns:1fr}
.facts{grid-template-columns:1fr;gap:.05rem}
.facts dd{margin-bottom:.45rem}}
"""


def render_html(data: dict) -> str:
    esc = html.escape
    s = data["sections"]
    level = data["rag"]["level"]
    rag_cls = level if level in RAG_HEX else "amber"
    reasons = data["rag"].get("reasons", [])
    n = len(reasons)
    count_txt = f" · {n} {'signaal' if n == 1 else 'signalen'}" if n else ""
    pill = (f'<span class="pill"><span class="dot"></span>{esc(level.upper())} · '
            f"{esc(RAG_GLOSS.get(level, 'onbekend'))}{esc(count_txt)}</span>")

    meta = (f'<p class="meta">Gegenereerd op {esc(_nl_dt(data.get("generated_at")))} · '
            f"wordt elke {REGEN_MINUTES} minuten ververst</p>")
    snap_html = ""
    snap_at = data.get("snapshot_at")
    if snap_at:
        snap_txt = f"Deal- en outreachgegevens: momentopname van {_nl_dt(snap_at)}."
        stale = False
        try:
            age_h = (datetime.fromisoformat(data["generated_at"])
                     - datetime.fromisoformat(str(snap_at))).total_seconds() / 3600
            stale = age_h > SNAPSHOT_STALE_HOURS
        except (ValueError, KeyError):
            pass
        if stale:
            snap_html = (f'<p class="meta warn">{esc(snap_txt)} Deze gegevens komen via een '
                         f"push vanaf de Mac en zijn ouder dan {SNAPSHOT_STALE_HOURS} uur; "
                         "voer <code>kk status push</code> uit.</p>")
        else:
            snap_html = f'<p class="meta">{esc(snap_txt)}</p>'

    reasons_html = ""
    if reasons:
        items = "".join(f'<li><span class="dot"></span>{esc(str(r))}</li>' for r in reasons)
        reasons_html = f'<aside class="reasons"><h2>Signalen</h2><ul>{items}</ul></aside>'

    panels = "".join([
        _render_today(s.get("today", {})),
        _render_deals(s.get("deals", {})),
        _render_outreach(s.get("outreach", {})),
        _render_billing(s.get("billing", {})),
        _render_content(s.get("content", {})),
        _render_system(s.get("health", {}), s.get("timers", {})),
    ])

    return f"""<!doctype html>
<html lang="nl"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="{REGEN_MINUTES * 60}">
<meta name="robots" content="noindex">
<title>Klantkraan Command Center</title>
<style>
{_FONT_CSS}{_CSS}</style></head><body class="rag-{rag_cls}">
<div class="ragbar"></div>
<div class="wrap">
<header>
  <div>
    <p class="eyebrow">Command Center</p>
    <h1>Klantkraan</h1>
    {meta}
    {snap_html}
  </div>
  {pill}
</header>
{reasons_html}
{_tiles(s)}
<div class="grid">
{panels}
</div>
<footer>Deze pagina wordt elke {REGEN_MINUTES} minuten ververst; een oudere pagina
betekent een kapotte statustimer.</footer>
</div>
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
        _write_assets(out.parent)
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
