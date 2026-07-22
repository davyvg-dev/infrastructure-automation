"""One record per prospect, from first outreach touch to a live receptionist.

The single source of truth for deal flow: each prospect is one
`data/pipeline/<slug>.yaml` file (gitignored — it holds third-party PII). The `slug`
is the through-line: it is the same slug that names the branded demo
`config/<slug>.yaml` and, once signed, the live `config/clients/<slug>.yaml`. So the
thing that sold them is the thing that goes live — no re-entry between sales and delivery.

    python -m app.pipeline add "Cool Global Mallorca" --email info@x.com --country ES --lang en
    python -m app.pipeline board
    python -m app.pipeline show airco-mallorca

This module owns pipeline *state* only. Config generation stays in `scaffold.py`; the two
compose (a later `stage` verb calls scaffold). One module, one job.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

from .settings import DATA_DIR

PIPELINE_DIR = DATA_DIR / "pipeline"

# The deal-flow stages, in order. A prospect walks these left to right; three terminal
# states sit off the board. `board` renders groups in exactly this order.
STAGES = ["lead", "qualified", "staged", "demo", "signed", "onboarding", "live"]
TERMINAL = ["disqualified", "lost", "churned"]
ALL_STATUSES = STAGES + TERMINAL

# The founder's next move per status — what `show` and `board` surface so the board is a
# to-do list, not just a snapshot. Playbook refs are `docs/03-delivery/onboarding-playbook.md`.
NEXT_ACTION = {
    "lead": "qualify: suppression + entity/BV check  (pipeline qualify <slug>)",
    "qualified": "stage a branded demo  (pipeline stage <slug>)",
    "staged": "send the demo link; run discovery",
    "demo": "send the proposal / close pack",
    "signed": "fill the 4 answers, connect the calendar, place the widget (playbook §2-5)",
    "onboarding": "verify the go-live checklist (playbook §9)",
    "live": "watch for the first real lead; weekly summary",
    "disqualified": "-",
    "lost": "-",
    "churned": "win-back later (playbook §8)",
}

# Mirrors settings._SLUG_RE: one DNS-label-ish token, no path separators or dots, so a slug
# can never traverse out of the pipeline dir or collide with a config path.
_SLUG_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "prospect"


def _now_date() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _now_ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --- store -------------------------------------------------------------------------------


def record_path(slug: str) -> Path:
    return PIPELINE_DIR / f"{slug}.yaml"


def load(slug: str) -> dict | None:
    path = record_path(slug)
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def save(record: dict) -> None:
    PIPELINE_DIR.mkdir(parents=True, exist_ok=True)
    record["updated"] = _now_date()
    path = record_path(record["slug"])
    with path.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(record, fh, sort_keys=False, allow_unicode=True, width=100)


def all_records() -> list[dict]:
    if not PIPELINE_DIR.exists():
        return []
    out = []
    for path in sorted(PIPELINE_DIR.glob("*.yaml")):
        with path.open(encoding="utf-8") as fh:
            rec = yaml.safe_load(fh)
        if isinstance(rec, dict) and rec.get("slug"):
            out.append(rec)
    return out


# --- commands ----------------------------------------------------------------------------


def add(
    name: str,
    *,
    slug: str | None = None,
    email: str | None = None,
    phone: str | None = None,
    country: str = "NL",
    lang: str = "nl",
    type_: str | None = None,
    source: str | None = None,
    status: str = "lead",
    config: str | None = None,
    inbound: bool = False,
    note: str | None = None,
    force: bool = False,
) -> dict:
    if status not in ALL_STATUSES:
        raise ValueError(f"status must be one of {ALL_STATUSES}, not {status!r}")
    slug = slug or slugify(name)
    if not _SLUG_RE.match(slug):
        raise ValueError(f"invalid slug {slug!r} — use lowercase letters, digits, hyphens")
    if record_path(slug).exists() and not force:
        raise FileExistsError(f"{record_path(slug).name} already exists; use --force to overwrite")

    history = [{"ts": _now_ts(), "event": f"added at status={status}"}]
    if note:
        history.append({"ts": _now_ts(), "event": note})
    record = {
        "slug": slug,
        "business": name,
        "status": status,
        "source": source,
        "country": country,
        "lang": lang,
        "type": type_,
        "contact": {"email": email, "phone": phone},
        "inbound": inbound,
        "config": config,
        "created": _now_date(),
        "updated": _now_date(),
        "history": history,
    }
    save(record)
    return record


def _fmt_contact(record: dict) -> str:
    c = record.get("contact") or {}
    parts = [c.get("email"), c.get("phone")]
    return "  ".join(p for p in parts if p) or "—"


def show_text(slug: str) -> str:
    record = load(slug)
    if record is None:
        return f"No pipeline record for {slug!r}. Add one with:  pipeline add \"<name>\""
    lines = [
        f"{record['business']}  [{slug}]",
        f"  status    {record['status']}   → {NEXT_ACTION.get(record['status'], '?')}",
        f"  market    {record.get('country', '?')} / {record.get('lang', '?')}"
        f"   ({'inbound' if record.get('inbound') else 'outbound'})",
        f"  type      {record.get('type') or '—'}",
        f"  source    {record.get('source') or '—'}",
        f"  contact   {_fmt_contact(record)}",
        f"  config    {record.get('config') or '— (none staged yet)'}",
        f"  added     {record.get('created', '?')}   updated {record.get('updated', '?')}",
    ]
    history = record.get("history") or []
    if history:
        lines.append("  history")
        for h in history:
            lines.append(f"    {h.get('ts', '?')}  {h.get('event', '')}")
    return "\n".join(lines)


def board_text() -> str:
    records = all_records()
    if not records:
        return "PIPELINE — empty. Add a prospect with:  pipeline add \"<name>\""

    by_status: dict[str, list[dict]] = {}
    for rec in records:
        by_status.setdefault(rec.get("status", "lead"), []).append(rec)

    lines = [f"PIPELINE — {len(records)} prospect{'s' if len(records) != 1 else ''}", ""]
    for status in ALL_STATUSES:
        group = by_status.get(status)
        if not group:
            continue
        lines.append(f"{status.upper()} ({len(group)})  — {NEXT_ACTION.get(status, '')}")
        for rec in sorted(group, key=lambda r: r.get("business", "")):
            tag = f"{rec.get('country', '?')}/{rec.get('lang', '?')}"
            src = rec.get("source") or "—"
            lines.append(f"  {rec['slug']:<22} {rec.get('business', ''):<32} [{src}, {tag}]")
        lines.append("")
    counts = " · ".join(f"{s} {len(by_status.get(s, []))}" for s in STAGES)
    lines.append(f"({counts})")
    return "\n".join(lines)


# --- cli ---------------------------------------------------------------------------------


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="app.pipeline", description="Prospect → client pipeline.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add", help="Add a prospect record.")
    p_add.add_argument("name", help="The prospect's business name.")
    p_add.add_argument("--slug", help="Override the derived slug (must match the demo config name).")
    p_add.add_argument("--email")
    p_add.add_argument("--phone")
    p_add.add_argument("--country", default="NL", help="ISO country (default NL).")
    p_add.add_argument("--lang", default="nl", help="Reply language (default nl).")
    p_add.add_argument("--type", dest="type_", help="Business type / vertical.")
    p_add.add_argument("--source", help="Where the lead came from (e.g. outreach-batch-1).")
    p_add.add_argument("--status", default="lead", choices=ALL_STATUSES)
    p_add.add_argument("--config", help="Path to an already-staged demo config, if any.")
    p_add.add_argument("--inbound", action="store_true", help="They replied/opted in (not cold).")
    p_add.add_argument("--note", help="A free-text note for the history log.")
    p_add.add_argument("--force", action="store_true", help="Overwrite an existing record.")

    p_show = sub.add_parser("show", help="Show one prospect record.")
    p_show.add_argument("slug")

    sub.add_parser("board", help="Print the pipeline as a text kanban.")

    args = parser.parse_args(argv[1:])

    if args.cmd == "add":
        try:
            rec = add(
                args.name, slug=args.slug, email=args.email, phone=args.phone,
                country=args.country, lang=args.lang, type_=args.type_, source=args.source,
                status=args.status, config=args.config, inbound=args.inbound,
                note=args.note, force=args.force,
            )
        except (ValueError, FileExistsError) as exc:
            parser.error(str(exc))
        print(f"✅ {record_path(rec['slug']).relative_to(DATA_DIR.parent)}")
        print()
        print(show_text(rec["slug"]))
        return 0
    if args.cmd == "show":
        print(show_text(args.slug))
        return 0
    if args.cmd == "board":
        print(board_text())
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
