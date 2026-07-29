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
    python -m scripts.outreach_send --send --slug barendse

Dry run is the default and --send is the only thing that opens a socket. Sends are
recorded in build/outreach/sent.json and already-sent prospects are skipped, because
the one unrecoverable mistake here is mailing the same cold prospect twice.

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
import json
import os
import smtplib
import ssl
import sys
import time
from datetime import UTC, datetime
from email.message import EmailMessage
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.outreach_mail import PROSPECTS, render  # noqa: E402

try:  # same optional-dotenv contract as app/settings.py, which this script does not import.
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ModuleNotFoundError:
    pass

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

FROM_NAME = "Davy"
OUT = Path("build/outreach")
SENT_LOG = OUT / "sent.json"

# Gmail's own guidance for a young domain is to trickle, not burst. 90s between sends
# spreads a six-mail morning over ten minutes and keeps the batch looking hand-sent.
DEFAULT_DELAY = 90.0


def load_sent() -> dict[str, str]:
    """Slug -> ISO timestamp of the send. Missing file means nothing has gone out."""
    if not SENT_LOG.exists():
        return {}
    try:
        return json.loads(SENT_LOG.read_text())
    except json.JSONDecodeError:
        # Better to refuse than to re-mail 23 businesses off a truncated file.
        sys.exit(f"{SENT_LOG} is corrupt; fix or delete it before sending")


def record_sent(sent: dict[str, str], slug: str) -> None:
    """Write after every single send, not once at the end: a crash or a Ctrl-C halfway
    through the batch must not lose the record of what already left."""
    sent[slug] = datetime.now(UTC).isoformat(timespec="seconds")
    OUT.mkdir(parents=True, exist_ok=True)
    SENT_LOG.write_text(json.dumps(sent, indent=2, sort_keys=True))


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
    msg.set_content(mail["text"])
    msg.add_alternative(mail["html"], subtype="html")
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
    sent = {} if args.resend else load_sent()
    if args.test_to:
        # A rehearsal, not a send: one mail, to the tester, never written to the sent log --
        # so the real prospect still gets their mail later.
        queue, skipped, sent = chosen[:1], 0, dict(sent)
    else:
        queue = [p for p in chosen if p.slug not in sent]
        skipped = len(chosen) - len(queue)
        if args.limit:
            queue = queue[: args.limit]

    if args.dump:
        OUT.mkdir(parents=True, exist_ok=True)
        sender = os.getenv("GMAIL_USER", "davy@klantkraan.nl")
        for p in queue:
            path = OUT / f"{p.slug}.eml"
            path.write_bytes(build(render(p), sender).as_bytes())
        print(f"{len(queue)} .eml -> {OUT}/  (nothing sent)")
        return

    if not queue:
        print(f"nothing to send ({skipped} already in {SENT_LOG})")
        return

    if not args.send:
        print(f"DRY RUN -- {len(queue)} mail(s) would go out, {skipped} already sent:")
        for p in queue:
            print(f"  {p.slug:28} -> {args.test_to or p.email}")
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
            for i, p in enumerate(queue):
                mail = render(p)
                if args.test_to:
                    mail = {**mail, "to": args.test_to}
                smtp.send_message(build(mail, sender))
                if not args.test_to:
                    record_sent(sent, p.slug)
                print(f"sent {p.slug} -> {mail['to']}")
                if i < len(queue) - 1:
                    time.sleep(args.delay)
    except smtplib.SMTPAuthenticationError as exc:
        sys.exit(
            f"Gmail refused the login ({exc.smtp_code}). Check that 2-Step Verification is on, "
            "that the app password is current, and that the Workspace admin allows app passwords."
        )
    except smtplib.SMTPException as exc:
        # Whatever left is already in sent.json; the rest can be picked up by re-running.
        sys.exit(f"SMTP failed after {len(sent)} recorded send(s): {exc}")

    if args.test_to:
        print(f"\ntest mail sent to {args.test_to}; nothing recorded, no prospect was mailed")
    else:
        print(f"\n{len(queue)} sent, recorded in {SENT_LOG}")


if __name__ == "__main__":
    main()
