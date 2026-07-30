"""The follow-up sequence: what the second, third and fourth mail say, and the ledger
that remembers who has had which one.

Before this, outreach was one mail per prospect and `build/outreach/sent.json` was a
skip-list: a slug appearing in it meant "never mail this person again". That threw away
most of the yield. A cold mail to a dakdekker competes with a phone that rings all day;
the first one gets buried, and the reply -- when it comes -- usually comes off touch two
or three. One-shot outreach is not a small version of a sequence, it is a different and
much worse thing.

So the ledger records *touches*, not prospects:

    {"version": 2,
     "prospects": {"aj-dakwerken": {"touches": {"1": {"at": "...", "message_id": "<...>"}},
                                    "replied": null, "stopped": null}}}

Three rules the rest of the batch depends on:

- A prospect who replied is done. `sequence.py stop <slug> --replied` and no further
  touch is ever due. Mailing someone a breakup line after they said yes is the one
  mistake here that costs a deal rather than an impression.
- A prospect who answered "stop" is done and goes in data/suppression.txt as well
  (Telecommunicatiewet art. 11.7 -- the opt-out has to actually stop it).
- An address that hard-bounced is done too, but is *not* suppressed: a dead mailbox said
  nothing about consent, and suppression.txt is the opt-out record rather than a list of
  addresses that failed. Halting still matters -- sending touches 2, 3 and 4 into a 550
  is exactly what wrecks a sending domain's reputation. `stop <slug> --bounced`.
- Follow-ups thread. Every send stores its Message-ID, and touch N quotes it in
  In-Reply-To/References so the mail lands inside the original conversation rather than
  as a fresh one. That is what a person doing this by hand produces, and threading is
  also why the follow-ups here are plain prose with no branded shell: the first mail in
  a thread may look designed, the nudge under it may not.

The v1 flat {slug: iso} file is read as "touch 1 went out then", so the six mails that
left on 2026-07-29 keep their history and become due for touch 2 rather than starting
over.

    python -m scripts.sequence board             # who is due for what, today
    python -m scripts.sequence stop meijer --replied
    python -m scripts.sequence stop meijer --opt-out

Run from the ai-receptionist directory with ./.venv/bin/python.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.outreach_mail import (  # noqa: E402
    DEMO,
    OPT_OUT,
    PROSPECTS,
    SIGNOFF_EMAIL,
    SIGNOFF_NAME,
    Prospect,
    subject_for,
)

LEDGER = Path("build/outreach/sent.json")
SUPPRESSION = Path("data/suppression.txt")


# ---------------------------------------------------------------------------
# The sequence
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Touch:
    number: int
    day: int  # days after touch 1 that this becomes due
    label: str


# Day 0/3/7/14. The gaps widen on purpose: an owner-operator who did not read touch 1 on
# Tuesday will not read touch 2 on Wednesday either, and bunching them reads as a machine.
# Fourteen days for the breakup because two weeks is roughly one busy-season cycle -- long
# enough that "I keep meaning to reply" is still true when it lands.
TOUCHES = [
    Touch(1, 0, "de branded demo-mail"),
    Touch(2, 3, "korte nudge, link opnieuw"),
    Touch(3, 7, "een vraag, geen pitch"),
    Touch(4, 14, "afsluiter"),
]
LAST_TOUCH = TOUCHES[-1].number
BY_NUMBER = {t.number: t for t in TOUCHES}


def followup_text(p: Prospect, touch: int) -> str:
    """The follow-up body: plain text, no branded shell, because it goes inside the
    thread the first mail opened.

    Each one changes the angle rather than repeating the offer. Touch 2 assumes the mail
    was missed and re-serves the one link. Touch 3 drops the pitch entirely and asks a
    question a plumber can answer in four words from a van -- the cheapest possible reply,
    and a reply of any kind is what we are actually buying. Touch 4 leaves, and says so;
    the breakup mail reliably outdraws the three before it because it removes the
    obligation to be sold to.
    """
    if touch == 2:
        return (
            f"Hoi,\n\n"
            f"Mijn vorige mail is misschien ondergesneeuwd, dus hier is 'ie nog een keer "
            f"kort: ik heb een AI-receptionist voor {p.short} klaargezet die 24/7 de chat "
            f"en WhatsApp opneemt en meteen een afspraak inplant.\n\n"
            f"Zelf even proberen kan hier:\n{DEMO}{p.slug}\n\n"
            f"{SIGNOFF_NAME}\n{SIGNOFF_EMAIL}\n\n"
            f"{OPT_OUT}\n"
        )
    if touch == 3:
        return (
            f"Hoi,\n\n"
            f"Even zonder verkooppraatje, ik ben gewoon benieuwd: wie neemt bij "
            f"{p.short} op als jullie allemaal op een klus zitten en de telefoon gaat?\n\n"
            f"Als het antwoord voicemail is, weet ik waar ik jullie mee kan helpen. "
            f"Is het al goed geregeld, dan hoor ik dat ook graag. Dan laat ik het hierbij.\n\n"
            f"{SIGNOFF_NAME}\n{SIGNOFF_EMAIL}\n\n"
            f"{OPT_OUT}\n"
        )
    if touch == 4:
        return (
            f"Hoi,\n\n"
            f"Ik stop hier met mailen, geen enkel probleem.\n\n"
            f"De receptionist die ik voor {p.short} klaarzette laat ik gewoon staan. "
            f"Mocht het over een half jaar wel spelen, dan werkt deze link nog:\n"
            f"{DEMO}{p.slug}\n\n"
            f"Succes met de zaak.\n\n"
            f"{SIGNOFF_NAME}\n{SIGNOFF_EMAIL}\n"
        )
    raise ValueError(f"touch {touch} has no follow-up copy (1 is the branded mail)")


def followup_subject(p: Prospect) -> str:
    """One "Re:" and no more. Gmail collapses the thread on the References header, not on
    the subject, so stacking Re: Re: Re: only makes it look forwarded."""
    return f"Re: {subject_for(p)}"


# ---------------------------------------------------------------------------
# The ledger
# ---------------------------------------------------------------------------


@dataclass
class Record:
    touches: dict[int, dict[str, str]]  # touch number -> {"at": iso, "message_id": str}
    replied: str | None = None
    stopped: str | None = None
    bounced: str | None = None

    @property
    def done(self) -> bool:
        return bool(self.replied or self.stopped or self.bounced)

    @property
    def closed_because(self) -> str:
        if self.replied:
            return "replied"
        if self.stopped:
            return "opt-out"
        return "bounced"

    @property
    def last_touch(self) -> int:
        return max(self.touches) if self.touches else 0

    def sent_at(self, touch: int) -> datetime | None:
        entry = self.touches.get(touch)
        return datetime.fromisoformat(entry["at"]) if entry else None

    def message_id(self, touch: int) -> str | None:
        return (self.touches.get(touch) or {}).get("message_id") or None


def load(path: Path = LEDGER) -> dict[str, Record]:
    """Read the ledger, migrating the v1 flat {slug: iso} shape on the way in.

    A corrupt file exits rather than defaulting to empty: an empty ledger means "nobody
    has been mailed", and acting on that would re-mail live prospects."""
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text())
    except json.JSONDecodeError:
        sys.exit(f"{path} is corrupt; fix or delete it before sending")

    if isinstance(raw, dict) and raw.get("version") == 2:
        return {
            slug: Record(
                touches={int(n): e for n, e in (rec.get("touches") or {}).items()},
                replied=rec.get("replied"),
                stopped=rec.get("stopped"),
                bounced=rec.get("bounced"),
            )
            for slug, rec in (raw.get("prospects") or {}).items()
        }

    # v1: {"aj-dakwerken": "2026-07-29T16:46:08+00:00"} -- every entry is a touch 1.
    return {
        slug: Record(touches={1: {"at": at, "message_id": ""}})
        for slug, at in raw.items()
        if isinstance(at, str)
    }


def save(ledger: dict[str, Record], path: Path = LEDGER) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 2,
        "prospects": {
            slug: {
                "touches": {str(n): e for n, e in sorted(rec.touches.items())},
                "replied": rec.replied,
                "stopped": rec.stopped,
                "bounced": rec.bounced,
            }
            for slug, rec in sorted(ledger.items())
        },
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))


def record_touch(
    ledger: dict[str, Record], slug: str, touch: int, message_id: str, path: Path = LEDGER
) -> None:
    """Write after every single send, not once at the end: a crash or a Ctrl-C halfway
    through the batch must not lose the record of what already left."""
    rec = ledger.setdefault(slug, Record(touches={}))
    rec.touches[touch] = {
        "at": datetime.now(UTC).isoformat(timespec="seconds"),
        "message_id": message_id,
    }
    save(ledger, path)


# ---------------------------------------------------------------------------
# What is due
# ---------------------------------------------------------------------------


def due_touch(rec: Record | None, now: datetime | None = None) -> int | None:
    """Which touch this prospect should get right now, or None.

    Never-mailed means touch 1. Otherwise the next touch, once enough days have passed
    since touch 1 -- the schedule anchors on the first mail, so a batch that slipped by a
    day does not push the whole tail out with it."""
    if rec is None:
        return 1
    if rec.done or rec.last_touch >= LAST_TOUCH:
        return None
    nxt = rec.last_touch + 1
    first = rec.sent_at(1)
    if first is None:  # ledger without a touch 1: treat as unmailed
        return 1
    now = now or datetime.now(UTC)
    return nxt if now - first >= timedelta(days=BY_NUMBER[nxt].day) else None


def queue(
    prospects: list[Prospect], ledger: dict[str, Record], now: datetime | None = None
) -> list[tuple[Prospect, int]]:
    """Everything due today, oldest thread first, so the prospects deepest into the
    sequence get finished before new ones are opened."""
    now = now or datetime.now(UTC)
    out = []
    for p in prospects:
        touch = due_touch(ledger.get(p.slug), now)
        if touch:
            out.append((p, touch))
    out.sort(key=lambda pt: (-pt[1], pt[0].slug))
    return out


def suppress(email: str, path: Path = SUPPRESSION) -> bool:
    """Mirror an opt-out into the CLI suppression list. Returns False if already there."""
    existing = set()
    if path.exists():
        existing = {
            ln.strip().lower()
            for ln in path.read_text().splitlines()
            if ln.strip() and ln[0] != "#"
        }
    if email.lower() in existing:
        return False
    with path.open("a") as fh:
        fh.write(f"{email}\n")
    return True


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def cmd_board(args: argparse.Namespace) -> None:
    ledger = load()
    now = datetime.now(UTC)
    due = dict(queue(list(PROSPECTS), ledger, now))

    print(f"SEQUENCE -- {len(PROSPECTS)} prospects, {len(due)} due today\n")
    rows, done, waiting = [], [], []
    for p in PROSPECTS:
        rec = ledger.get(p.slug)
        at = rec.last_touch if rec else 0
        if rec and rec.done:
            done.append(f"  {p.slug:28} T{at}  {rec.closed_because}")
        elif p in due:
            rows.append(f"  {p.slug:28} T{at} -> T{due[p]}  {BY_NUMBER[due[p]].label}")
        elif rec:
            nxt = rec.last_touch + 1
            if nxt > LAST_TOUCH:
                done.append(f"  {p.slug:28} T{at}  sequence afgerond")
            else:
                first = rec.sent_at(1)
                when = (first + timedelta(days=BY_NUMBER[nxt].day)).date() if first else "?"
                waiting.append(f"  {p.slug:28} T{at}  -> T{nxt} op {when}")

    for title, block in (("DUE NOW", rows), ("WAITING", waiting), ("CLOSED", done)):
        if block:
            print(f"{title} ({len(block)})")
            print("\n".join(block))
            print()
    if not rows:
        print("niets te versturen vandaag")


def cmd_stop(args: argparse.Namespace) -> None:
    by_slug = {p.slug: p for p in PROSPECTS}
    if args.slug not in by_slug:
        sys.exit(f"unknown slug: {args.slug} (have {', '.join(sorted(by_slug))})")
    ledger = load()
    rec = ledger.setdefault(args.slug, Record(touches={}))
    stamp = datetime.now(UTC).isoformat(timespec="seconds")
    if args.opt_out:
        rec.stopped = stamp
        added = suppress(by_slug[args.slug].email)
        print(f"{args.slug}: opt-out recorded, no further touches")
        print(f"  {'added to' if added else 'already in'} {SUPPRESSION}")
    elif args.bounced:
        # Deliberately NOT suppressed: suppression.txt is the art. 11.7 opt-out record,
        # and a dead mailbox said nothing about consent. Halting is enough, and it has to
        # happen -- mailing a 550 three more times is what burns the sending domain.
        rec.bounced = stamp
        print(f"{args.slug}: hard bounce recorded, no further touches")
        print(f"  {by_slug[args.slug].email} is dead; find the real address to re-open")
    else:
        rec.replied = stamp
        print(f"{args.slug}: reply recorded, sequence halted -- follow up by hand")
    save(ledger)


def main() -> None:
    ap = argparse.ArgumentParser(description="Outreach sequence ledger.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("board", help="who is due for which touch, today").set_defaults(func=cmd_board)
    stop = sub.add_parser("stop", help="halt the sequence for one prospect")
    stop.add_argument("slug")
    stop.add_argument(
        "--replied", action="store_true", help="they answered; halt and handle by hand"
    )
    stop.add_argument(
        "--opt-out", action="store_true", help='they answered "stop"; halt and suppress'
    )
    stop.add_argument(
        "--bounced", action="store_true", help="the address hard-bounced; halt, do not suppress"
    )
    stop.set_defaults(func=cmd_stop)
    args = ap.parse_args()
    if args.cmd == "stop" and not (args.replied or args.opt_out or args.bounced):
        ap.error("say which: --replied, --opt-out or --bounced")
    args.func(args)


if __name__ == "__main__":
    main()
