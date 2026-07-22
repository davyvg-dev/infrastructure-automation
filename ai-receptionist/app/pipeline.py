"""One record per prospect, from first outreach touch to a live receptionist.

The single source of truth for deal flow: each prospect is one
`data/pipeline/<slug>.yaml` file (gitignored — it holds third-party PII). The `slug`
is the through-line: it is the same slug that names the branded demo
`config/<slug>.yaml` and, once signed, the live `config/clients/<slug>.yaml`. So the
thing that sold them is the thing that goes live — no re-entry between sales and delivery.

    python -m app.pipeline add "Cool Global Mallorca" --email info@x.com --country ES --lang en
    python -m app.pipeline qualify airco-mallorca
    python -m app.pipeline advance airco-mallorca demo --note "close pack sent"
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

# Entity gate for NL *cold* outreach: the BV-only rule is non-negotiable (CLAUDE.md § Forbidden).
# A VOF / eenmanszaak / zzp may not be cold-emailed without opt-in; a BV may. Non-NL prospects
# (a different opt-out regime) and inbound prospects (opt-in satisfied) bypass this gate — see
# qualify().
ENTITY_OK = {"bv"}
ENTITY_BLOCKED = {"vof", "eenmanszaak", "zzp"}
ENTITY_CHOICES = ["bv", "vof", "eenmanszaak", "zzp", "unknown"]

# The CLI's local opt-out list (one entry per line: an email, an @domain, or a phone; `#`
# comments allowed). Optional — a missing file means "nothing suppressed". The canonical
# AVG store is Neon (`apps/api` isSuppressed); this file is the offline mirror for the CLI.
SUPPRESSION_FILE = DATA_DIR / "suppression.txt"


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


# --- qualification helpers ---------------------------------------------------------------


def infer_entity(name: str) -> str:
    """Best-effort legal entity from the business name (Dutch trade names carry it: 'B.V.')."""
    n = f" {(name or '').lower()} "
    if "b.v." in n or " bv " in n:
        return "bv"
    if "v.o.f." in n or " vof " in n:
        return "vof"
    if "eenmanszaak" in n:
        return "eenmanszaak"
    if " zzp " in n:
        return "zzp"
    return "unknown"


def _norm_phone(value: str | None) -> str:
    return re.sub(r"\D", "", value or "")


def _load_suppression() -> list[str]:
    if not SUPPRESSION_FILE.exists():
        return []
    out = []
    for line in SUPPRESSION_FILE.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            out.append(line)
    return out


def suppressed_by(contact: dict) -> str | None:
    """The matching opt-out entry if this contact is suppressed, else None. An entry matches a
    full email, an `@domain` suffix, or a phone by digits (>=7, suffix match to survive
    country-code formatting differences)."""
    email = (contact.get("email") or "").strip().lower()
    phone = _norm_phone(contact.get("phone"))
    for entry in _load_suppression():
        e = entry.strip().lower()
        if not e:
            continue
        if e.startswith("@"):
            if email and email.endswith(e):
                return entry
        elif "@" in e:
            if email and email == e:
                return entry
        else:
            ed = _norm_phone(entry)
            if ed and len(ed) >= 7 and phone and phone.endswith(ed):
                return entry
    return None


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
    entity: str | None = None,
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
        "entity": entity,
        "config": config,
        "created": _now_date(),
        "updated": _now_date(),
        "history": history,
    }
    save(record)
    return record


def qualify(slug: str, *, entity: str | None = None) -> dict:
    """Run the AVG suppression check + the country-aware entity/BV gate, mutating the record.

    Decision order: suppression → non-NL bypass → inbound/opt-in bypass → NL entity rule.
    QUALIFIED advances a `lead` to `qualified` (a no-op for records already further along, so
    re-running it audits the board). DISQUALIFIED pulls the prospect off the board. HOLD means
    the entity is unknown — confirm a BV or an opt-in before contacting.
    """
    record = load(slug)
    if record is None:
        raise FileNotFoundError(f"no pipeline record for {slug!r}")

    contact = record.get("contact") or {}
    resolved = (entity or record.get("entity") or infer_entity(record.get("business", ""))).lower()
    country = (record.get("country") or "NL").upper()
    inbound = bool(record.get("inbound"))
    hit = suppressed_by(contact)

    if hit:
        decision, reason = "disqualified", f"on the suppression list ({hit})"
    elif country != "NL":
        decision, reason = "qualified", f"{country}: Dutch BV opt-out regime N/A; keep a clear opt-out in outreach"
    elif inbound:
        decision, reason = "qualified", "inbound/opt-in: BV cold-outreach gate satisfied by their contact"
    elif resolved in ENTITY_OK:
        decision, reason = "qualified", "NL BV: meets the BV-only cold-outreach rule"
    elif resolved in ENTITY_BLOCKED:
        decision, reason = "disqualified", f"NL {resolved}: cold outreach without opt-in is forbidden (BV filter)"
    else:
        decision, reason = "hold", "NL entity unknown: confirm a BV (--entity bv) or an opt-in before contacting"

    record["entity"] = resolved
    verdict = {"decision": decision, "reason": reason, "entity": resolved}

    if decision == "qualified":
        if record.get("status") == "lead":
            record["history"].append({"ts": _now_ts(), "event": f"qualified — {reason}"})
            record["status"] = "qualified"
            verdict["moved"] = "lead → qualified"
        else:
            verdict["moved"] = f"no status change (already at {record.get('status')})"
    elif decision == "disqualified":
        record["history"].append({"ts": _now_ts(), "event": f"disqualified — {reason}"})
        record["status"] = "disqualified"
        verdict["moved"] = "→ disqualified"
    else:
        verdict["moved"] = "no change (needs review)"
    save(record)
    return verdict


def advance(slug: str, status: str, *, note: str | None = None) -> dict:
    if status not in ALL_STATUSES:
        raise ValueError(f"status must be one of {ALL_STATUSES}, not {status!r}")
    record = load(slug)
    if record is None:
        raise FileNotFoundError(f"no pipeline record for {slug!r}")
    old = record.get("status")
    event = f"{old} → {status}" + (f": {note}" if note else "")
    record["history"].append({"ts": _now_ts(), "event": event})
    record["status"] = status
    save(record)
    return record


def note(slug: str, text: str) -> dict:
    record = load(slug)
    if record is None:
        raise FileNotFoundError(f"no pipeline record for {slug!r}")
    record["history"].append({"ts": _now_ts(), "event": text})
    save(record)
    return record


def stage(slug: str, *, force: bool = False) -> dict:
    """Build the branded demo config for a record via scaffold, then advance it to `staged`.

    Writes `config/<slug>.yaml` (the staging location); slice-4 `sign` promotes it to
    `config/clients/`. Honors the record's `lang` so a non-Dutch prospect gets the right
    template (the Dutch trade template no longer fits an English airco client on Mallorca).
    """
    record = load(slug)
    if record is None:
        raise FileNotFoundError(f"no pipeline record for {slug!r}")
    if record.get("config") and not force:
        raise FileExistsError(f"{slug} already points at {record['config']}; use --force to rebuild")

    from . import scaffold  # lazy: scaffold pulls in the Anthropic SDK via extract

    contact = record.get("contact") or {}
    cfg = scaffold.build_config(
        record["business"],
        lang=record.get("lang", "nl"),
        type=record.get("type"),
        phone=contact.get("phone"),
    )
    path = scaffold.CONFIG_DIR / f"{slug}.yaml"
    if path.exists() and not force:
        raise FileExistsError(f"config/{slug}.yaml already exists; use --force to overwrite")
    scaffold.write_config(cfg, path)

    rel = f"config/{slug}.yaml"
    record["config"] = rel
    record["history"].append({"ts": _now_ts(), "event": f"staged demo → {rel}"})
    if record.get("status") in ("lead", "qualified"):
        record["status"] = "staged"
    save(record)
    return {"config": rel, "status": record["status"]}


def _fmt_contact(record: dict) -> str:
    c = record.get("contact") or {}
    parts = [c.get("email"), c.get("phone")]
    return "  ".join(p for p in parts if p) or "—"


def show_text(slug: str) -> str:
    record = load(slug)
    if record is None:
        return f"No pipeline record for {slug!r}. Add one with:  pipeline add \"<name>\""
    entity = record.get("entity") or infer_entity(record.get("business", ""))
    direction = "inbound" if record.get("inbound") else "outbound"
    lines = [
        f"{record['business']}  [{slug}]",
        f"  status    {record['status']}   → {NEXT_ACTION.get(record['status'], '?')}",
        f"  market    {record.get('country', '?')} / {record.get('lang', '?')}"
        f"   ({direction} · {entity})",
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


def _trunc(text: str, width: int) -> str:
    return text if len(text) <= width else text[: width - 1] + "…"


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
            biz = _trunc(rec.get("business", ""), 32)
            lines.append(f"  {rec['slug']:<22} {biz:<32} [{src}, {tag}]")
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
    p_add.add_argument("--entity", choices=ENTITY_CHOICES, help="Legal entity (else inferred at qualify).")
    p_add.add_argument("--note", help="A free-text note for the history log.")
    p_add.add_argument("--force", action="store_true", help="Overwrite an existing record.")

    p_qual = sub.add_parser("qualify", help="Run the suppression + entity/BV gate.")
    p_qual.add_argument("slug")
    p_qual.add_argument("--entity", choices=ENTITY_CHOICES, help="Override the entity for the gate.")

    p_adv = sub.add_parser("advance", help="Move a record to a new status.")
    p_adv.add_argument("slug")
    p_adv.add_argument("status", choices=ALL_STATUSES)
    p_adv.add_argument("--note", help="Why — logged with the move.")

    p_stage = sub.add_parser("stage", help="Build the branded demo config (scaffold) and mark staged.")
    p_stage.add_argument("slug")
    p_stage.add_argument("--force", action="store_true", help="Rebuild even if a config exists.")

    p_note = sub.add_parser("note", help="Append a note to a record's history.")
    p_note.add_argument("slug")
    p_note.add_argument("text")

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
                entity=args.entity, note=args.note, force=args.force,
            )
        except (ValueError, FileExistsError) as exc:
            parser.error(str(exc))
        print(f"✅ {record_path(rec['slug']).relative_to(DATA_DIR.parent)}")
        print()
        print(show_text(rec["slug"]))
        return 0
    if args.cmd == "qualify":
        try:
            v = qualify(args.slug, entity=args.entity)
        except FileNotFoundError as exc:
            parser.error(str(exc))
        icon = "✅" if v["decision"] == "qualified" else "⚠️ "
        print(f"{icon} {args.slug}: {v['decision'].upper()} — {v['reason']}")
        print(f"   entity={v['entity']}  ({v['moved']})")
        return 0
    if args.cmd == "advance":
        try:
            rec = advance(args.slug, args.status, note=args.note)
        except (ValueError, FileNotFoundError) as exc:
            parser.error(str(exc))
        print(f"✅ {args.slug}: → {rec['status']}")
        return 0
    if args.cmd == "stage":
        try:
            r = stage(args.slug, force=args.force)
        except (FileNotFoundError, FileExistsError) as exc:
            parser.error(str(exc))
        print(f"✅ {args.slug}: staged → {r['config']}  (status={r['status']})")
        print(f"   demo: BUSINESS_CONFIG={r['config']} python -m app.server")
        return 0
    if args.cmd == "note":
        try:
            note(args.slug, args.text)
        except FileNotFoundError as exc:
            parser.error(str(exc))
        print(f"✅ noted on {args.slug}")
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
