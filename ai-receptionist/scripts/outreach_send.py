"""Send the batch-3 outreach mails over Gmail SMTP, as davy@klantkraan.nl.

Why this exists instead of staging Gmail drafts: anything composed through Gmail gets
its links rewritten. Every draft in the 2026-07-29 batch came back carrying

    https://www.google.com/url?q=https://demo.klantkraan.nl/?client%3Dbarendse&source=gmail&ust=...

in the stored body -- href and visible text both. That is not the mail viewer being
clever, it is what Gmail wrote down: a control mail from Resend, read back through the
same API, kept its hrefs untouched. There is no flag to turn the rewriting off, and it
lands after our HTML is handed over, so no amount of fixing the anchor helps.

A cold mail to a plumber whose one link resolves through a Google redirector reads as
phishing, and the wrapper percent-encodes the `=` in `?client%3D<slug>` -- the single
parameter that picks the branded demo. We have already been bitten once by a client
mangling that and loading the default business.

Authenticated SMTP submission skips the composer entirely: the MIME that
scripts/outreach_mail.py renders is the MIME that leaves the building. Sending stays on
davy@klantkraan.nl so replies land in the inbox the founder already watches, and the
domain reputation at stake is Workspace's rather than the transactional Resend stream
that carries invoices and welcome mails.

    python -m scripts.outreach_send --dump          # write .eml files, send nothing
    python -m scripts.outreach_send                 # dry run: show what would go
    python -m scripts.outreach_send --send --limit 6
    python -m scripts.outreach_send --send --touch 1 --limit 6   # only new prospects
    python -m scripts.outreach_send --send --slug barendse

Dry run is the default and --send is the only thing that opens a socket. What is due on
any given day comes from scripts/sequence.py, which owns the ledger and the 0/3/7/14-day
schedule; this file only knows how to render a touch and put it on the wire. Nobody is
mailed the same touch twice, because the one unrecoverable mistake here is mailing the
same cold prospect the same thing again.

Follow-ups go out threaded under the original where we know its Message-ID, and as plain
text either way. Note that Gmail may substitute its own Message-ID on submission; if it
does, our recorded one will not match what the prospect holds and the follow-up threads
on subject alone, which Gmail and Outlook both still do. `--test-to` proves which happens
without touching a prospect.

Setup (one founder action): Google account -> Security -> 2-Step Verification -> App
passwords, create one for "mail", then in .env

    GMAIL_USER=davy@klantkraan.nl
    GMAIL_APP_PASSWORD=abcd efgh ijkl mnop      # spaces are fine, they get stripped

Workspace admins can disable app passwords; if login fails with 535, that is the first
thing to check. Gmail SMTP submission is smtp.gmail.com:587 with STARTTLS.

Run from the ai-receptionist directory with ./.venv/bin/python.
"""

from __future__ import annotations

import argparse
import os
import smtplib
import ssl
import sys
import time
from email.message import EmailMessage
from email.utils import make_msgid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts import sequence  # noqa: E402
from scripts.outreach_mail import PROSPECTS, Prospect, render  # noqa: E402

try:  # same optional-dotenv contract as app/settings.py, which this script does not import.
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ModuleNotFoundError:
    pass

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

FROM_NAME = "Davy"
OUT = Path("build/outreach")

# Gmail's own guidance for a young domain is to trickle, not burst. 90s between sends
# spreads a six-mail morning over ten minutes and keeps the batch looking hand-sent.
DEFAULT_DELAY = 90.0


def build(mail: dict[str, str], sender: str) -> EmailMessage:
    """One multipart/alternative message: text part first, HTML second.

    Both parts come from mail_layout via outreach_mail.render, so they cannot disagree.
    The text part is not a formality -- it is what plain-text clients show and what spam
    filters read, and an HTML-only cold mail delivers measurably worse.

    No List-Unsubscribe header on purpose. This is a 1:1 mail to a BV, not a mailing;
    list headers mark it as bulk. The opt-out that Telecommunicatiewet art. 11.7 requires
    is the "antwoord met stop" line mail_layout puts in the footer.
    """
    msg = EmailMessage()
    msg["From"] = f"{FROM_NAME} <{sender}>"
    msg["To"] = mail["to"]
    msg["Subject"] = mail["subject"]
    msg["Reply-To"] = sender
    msg["Message-ID"] = make_msgid(domain=sender.split("@")[-1])
    msg.set_content(mail["text"])
    msg.add_alternative(mail["html"], subtype="html")
    return msg


def build_followup(p: Prospect, touch: int, sender: str, parent: str | None) -> EmailMessage:
    """Touches 2-4: text/plain only, threaded under touch 1 where we have its Message-ID.

    No HTML part on purpose. The branded shell earns its keep on the first mail, where it
    has to establish that a real company is writing; underneath that, in a thread, the
    same treatment reads as a newsletter and undoes the one thing a follow-up is for --
    looking like the sender typed it himself between two jobs.

    A missing parent (the six mails from before the ledger stored IDs) degrades to no
    threading headers rather than a fabricated reference, which would break the thread
    for the recipient instead of merely not building one.
    """
    msg = EmailMessage()
    msg["From"] = f"{FROM_NAME} <{sender}>"
    msg["To"] = p.email
    msg["Subject"] = sequence.followup_subject(p)
    msg["Reply-To"] = sender
    msg["Message-ID"] = make_msgid(domain=sender.split("@")[-1])
    if parent:
        msg["In-Reply-To"] = parent
        msg["References"] = parent
    msg.set_content(sequence.followup_text(p, touch))
    return msg


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--send", action="store_true", help="actually send (default: dry run)")
    ap.add_argument("--slug", help="only this prospect")
    ap.add_argument("--limit", type=int, help="stop after N mails (daily pacing)")
    ap.add_argument("--delay", type=float, default=DEFAULT_DELAY, help="seconds between sends")
    ap.add_argument("--dump", action="store_true", help="write .eml files instead of sending")
    ap.add_argument("--resend", action="store_true", help="ignore the sent log (dangerous)")
    ap.add_argument(
        "--touch",
        type=int,
        choices=range(1, sequence.LAST_TOUCH + 1),
        help="only this touch number, so new prospects and follow-ups can be paced apart",
    )
    ap.add_argument(
        "--test-to",
        metavar="ADDRESS",
        help="send ONE mail to this address instead of the prospect, and do not record it. "
        "Proves credentials, MIME and link integrity without touching the prospect list.",
    )
    args = ap.parse_args()

    by_slug = {p.slug: p for p in PROSPECTS}
    if args.slug and args.slug not in by_slug:
        sys.exit(f"unknown slug: {args.slug} (have {', '.join(sorted(by_slug))})")

    chosen = [by_slug[args.slug]] if args.slug else list(PROSPECTS)
    ledger = {} if args.resend else sequence.load()

    if args.test_to:
        # A rehearsal, not a send: one mail, to the tester, never written to the ledger --
        # so the real prospect still gets their mail later.
        queue, skipped = [(chosen[0], args.touch or 1)], 0
    else:
        queue = sequence.queue(chosen, ledger)
        if args.touch:
            queue = [(p, t) for p, t in queue if t == args.touch]
        skipped = len(chosen) - len(queue)
        if args.limit:
            queue = queue[: args.limit]

    def compose(p: Prospect, touch: int, sender: str) -> EmailMessage:
        if touch == 1:
            return build(render(p), sender)
        rec = ledger.get(p.slug)
        return build_followup(p, touch, sender, rec.message_id(1) if rec else None)

    if args.dump:
        OUT.mkdir(parents=True, exist_ok=True)
        sender = os.getenv("GMAIL_USER", "davy@klantkraan.nl")
        for p, touch in queue:
            suffix = "" if touch == 1 else f".t{touch}"
            (OUT / f"{p.slug}{suffix}.eml").write_bytes(compose(p, touch, sender).as_bytes())
        print(f"{len(queue)} .eml -> {OUT}/  (nothing sent)")
        return

    if not queue:
        print(f"nothing due today ({skipped} waiting or closed -- see `sequence board`)")
        return

    if not args.send:
        print(f"DRY RUN -- {len(queue)} mail(s) would go out, {skipped} not due:")
        for p, touch in queue:
            print(f"  T{touch}  {p.slug:28} -> {args.test_to or p.email}")
        print("\nre-run with --send to actually send")
        return

    sender = os.getenv("GMAIL_USER")
    password = (os.getenv("GMAIL_APP_PASSWORD") or "").replace(" ", "")
    if not (sender and password):
        sys.exit(
            "GMAIL_USER and GMAIL_APP_PASSWORD must be set in .env (see this file's docstring)"
        )

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as smtp:
            smtp.starttls(context=ssl.create_default_context())
            smtp.login(sender, password)
            for i, (p, touch) in enumerate(queue):
                msg = compose(p, touch, sender)
                if args.test_to:
                    del msg["To"]
                    msg["To"] = args.test_to
                smtp.send_message(msg)
                if not args.test_to:
                    # Record the Message-ID we set, so touch N+1 can thread under it.
                    sequence.record_touch(ledger, p.slug, touch, msg["Message-ID"])
                print(f"sent T{touch} {p.slug} -> {msg['To']}")
                if i < len(queue) - 1:
                    time.sleep(args.delay)
    except smtplib.SMTPAuthenticationError as exc:
        sys.exit(
            f"Gmail refused the login ({exc.smtp_code}). Check that 2-Step Verification is on, "
            "that the app password is current, and that the Workspace admin allows app passwords."
        )
    except smtplib.SMTPException as exc:
        # Whatever left is already in the ledger; the rest is picked up by re-running.
        sys.exit(f"SMTP failed partway through: {exc}")

    if args.test_to:
        print(f"\ntest mail sent to {args.test_to}; nothing recorded, no prospect was mailed")
    else:
        print(f"\n{len(queue)} sent, recorded in {sequence.LEDGER}")


if __name__ == "__main__":
    main()
