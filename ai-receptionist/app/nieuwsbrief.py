"""Nieuwsbrief broadcasts to the cursus list: one approved .md file, sent once to everyone.

The cursus (app/cursus.py) is a drip sequence; this module is the broadcast layer on the
SAME subscriber ledger. One afmelding therefore stops both: recipients are every subscriber
without a halt flag, minus the shared suppression list. There is no subscriber state here at
all — only a broadcast ledger (data/cursus/broadcasts.json) recording who already got which
edition, so a crashed or re-run send resumes instead of double-mailing (belt) on top of the
per-(broadcast, address) Idempotency-Key (suspenders).

Input is an approved markdown file (the growth-engine bot drafts them, the founder approves
in Telegram, `kk nieuwsbrief send` ships the file):

    ---
    subject: Onderwerp van deze editie
    preheader: De grijze regel naast het onderwerp in de inbox.
    ---
    Gewone alinea's gescheiden door witregels.

    ## Een tussenkop

    [Knoptekst](https://klantkraan.nl/demo/)

Sends are founder-triggered, never a timer, and paced (default one mail per second) because
mailer.send is a single synchronous POST per recipient. Every mail carries the same
List-Unsubscribe pair the lessons carry; Telecommunicatiewet art. 11.7 applies to a
nieuwsbrief exactly as it does to the cursus.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from . import cursus, mail_layout, mailer, suppression

_BUTTON_RE = re.compile(r"^\[(?P<label>[^\]]+)\]\((?P<url>https?://[^)]+)\)$")


def _now() -> datetime:
    return datetime.now(UTC)


def _iso(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds")


def ledger_path() -> Path:
    return cursus.cursus_dir() / "broadcasts.json"


def load_ledger() -> dict:
    path = ledger_path()
    if not path.exists():
        return {"broadcasts": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        # Same rule as the subscriber store: a corrupt ledger must never default to empty,
        # that would re-mail every edition to the whole list.
        sys.exit(f"corrupt broadcast ledger, fix or remove it first: {path}")
    data.setdefault("broadcasts", {})
    return data


def save_ledger(data: dict) -> None:
    path = ledger_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


# --- input file ---------------------------------------------------------------------------


def parse(path: Path) -> dict:
    """Front matter (subject, preheader) + body -> {"id", "subject", "preheader", "blocks"}.
    The broadcast id is the file stem, which makes re-sending the same file resumable."""
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, flags=re.DOTALL)
    if not m:
        sys.exit(f"{path}: missing front matter (--- subject/preheader ---)")
    meta: dict[str, str] = {}
    for line in m.group(1).splitlines():
        key, sep, value = line.partition(":")
        if sep:
            meta[key.strip().lower()] = value.strip()
    subject = meta.get("subject", "").strip()
    if not subject:
        sys.exit(f"{path}: front matter needs a subject")
    blocks = _blocks(m.group(2))
    if not blocks:
        sys.exit(f"{path}: empty body")
    return {
        "id": path.stem,
        "subject": subject,
        "preheader": meta.get("preheader", ""),
        "blocks": blocks,
    }


def _blocks(body: str) -> list:
    out: list = []
    for chunk in re.split(r"\n\s*\n", body.strip()):
        chunk = " ".join(ln.strip() for ln in chunk.strip().splitlines())
        if not chunk:
            continue
        if chunk.startswith("## "):
            out.append(mail_layout.Heading(chunk[3:].strip()))
        elif _BUTTON_RE.match(chunk):
            m = _BUTTON_RE.match(chunk)
            out.append(mail_layout.Button(m.group("label"), m.group("url")))
        else:
            out.append(mail_layout.Para(chunk))
    if out and not any(isinstance(b, mail_layout.Signoff) for b in out):
        out.append(mail_layout.Signoff("Klantkraan", "hallo@klantkraan.nl"))
    return out


def _footer_note(email: str) -> str:
    return (
        "U ontvangt deze nieuwsbrief omdat u zich heeft aangemeld via klantkraan.nl. "
        f"Afmelden: {cursus.unsubscribe_url(email)}"
    )


def render(edition: dict, email: str) -> tuple[str, str, str]:
    """(subject, text, html) for one recipient. Pure, so preview shows the real mail."""
    note = _footer_note(email)
    text = mail_layout.to_text(edition["blocks"], footer_note=note)
    html = mail_layout.to_html(
        edition["blocks"],
        subject=edition["subject"],
        preheader=edition["preheader"],
        lang="nl",
        footer_note=note,
    )
    return edition["subject"], text, html


# --- recipients + sending -----------------------------------------------------------------


def recipients() -> list[str]:
    """Every deliverable consenting address: no halt flag, not on the suppression list.
    Completed course members stay on the list; completion is not an afmelding."""
    subs = cursus.load()["subscribers"]
    blocked = suppression.entries()
    return sorted(
        email
        for email, sub in subs.items()
        if not (sub.get("unsubscribed") or sub.get("bounced")) and email not in blocked
    )


def send(
    path: Path,
    *,
    dry: bool = False,
    delay_s: float = 1.0,
    now: datetime | None = None,
) -> dict:
    """Send one edition to everyone who has not received it yet.

    Returns {"id", "subject", "recipients": [...], "sent": [...], "skipped": [...],
    "failed": [...]}. The ledger is written per successful send, so a crash resumes."""
    edition = parse(path)
    ledger = load_ledger()
    record = ledger["broadcasts"].setdefault(
        edition["id"], {"subject": edition["subject"], "started": _iso(now or _now())}
    )
    already = record.setdefault("sent", {})

    todo = recipients()
    report: dict = {
        "id": edition["id"],
        "subject": edition["subject"],
        "recipients": todo,
        "sent": [],
        "skipped": sorted(set(todo) & set(already)),
        "failed": [],
    }
    if dry:
        return report

    pending = [e for e in todo if e not in already]
    for i, email in enumerate(pending):
        if i and delay_s:
            time.sleep(delay_s)
        subject, text, html = render(edition, email)
        ok = mailer.send(
            email,
            subject,
            text,
            html=html,
            idempotency_key=f"nb-{edition['id']}-{email}",
            headers={
                "List-Unsubscribe": f"<{cursus.unsubscribe_url(email)}>",
                "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
            },
        )
        if not ok:
            report["failed"].append(email)
            continue
        already[email] = _iso(now or _now())
        save_ledger(ledger)
        report["sent"].append(email)
    return report


# --- CLI ----------------------------------------------------------------------------------


def cmd_board() -> None:
    ledger = load_ledger()
    if not ledger["broadcasts"]:
        print("nog geen edities verstuurd")
        return
    for bid, rec in sorted(ledger["broadcasts"].items()):
        print(f"{bid}: {rec.get('subject', '?')} · {len(rec.get('sent', {}))} verstuurd")


def cmd_send(path: Path, *, dry: bool) -> None:
    report = send(path, dry=dry)
    label = "zou gaan naar" if dry else "verstuurd naar"
    print(f"{report['id']}: {report['subject']}")
    print(f"  {label} {len(report['sent']) if not dry else len(report['recipients'])} adressen")
    if report["skipped"]:
        print(f"  {len(report['skipped'])} al ontvangen (overgeslagen)")
    if report["failed"]:
        print(f"  MISLUKT: {', '.join(report['failed'])}")
        sys.exit(1)


def cmd_preview(path: Path) -> None:
    edition = parse(path)
    subject, text, _ = render(edition, "voorbeeld@bedrijf.nl")
    print(f"Onderwerp: {subject}\n")
    print(text)


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="python -m app.nieuwsbrief")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("board", help="verstuurde edities")
    p_send = sub.add_parser("send", help="verstuur een goedgekeurde editie")
    p_send.add_argument("--file", required=True, type=Path)
    p_send.add_argument("--dry", action="store_true")
    p_prev = sub.add_parser("preview", help="toon de mail zoals de lezer hem krijgt")
    p_prev.add_argument("file", type=Path)
    args = ap.parse_args(argv)
    if args.cmd == "send":
        cmd_send(args.file, dry=args.dry)
    elif args.cmd == "preview":
        cmd_preview(args.file)
    else:
        cmd_board()


if __name__ == "__main__":
    main()
