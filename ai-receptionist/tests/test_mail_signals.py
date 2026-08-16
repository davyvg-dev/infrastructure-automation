"""Mail signals for the morning digest: DSN detection, watch list, rendering. Offline —
imaplib is monkeypatched; nothing here opens a network connection."""

from __future__ import annotations

import email
import email.policy

from app import mail_signals, oversight

GMAIL_DSN = b"""\
From: Mail Delivery Subsystem <mailer-daemon@googlemail.com>
Subject: Delivery Status Notification (Failure)
X-Failed-Recipients: prospect@bedrijf.nl
Content-Type: multipart/report; report-type=delivery-status; boundary="b"

--b
Content-Type: text/plain

Address not found.
--b
Content-Type: message/delivery-status

Reporting-MTA: dns; googlemail.com

Final-Recipient: rfc822; prospect@bedrijf.nl
Action: failed
--b--
"""

STANDARD_DSN = b"""\
From: postmaster@ander-bedrijf.nl
Subject: Undeliverable
Content-Type: multipart/report; report-type=delivery-status; boundary="b"

--b
Content-Type: message/delivery-status

Reporting-MTA: dns; mail.ander-bedrijf.nl

Original-Recipient: rfc822; weg@ander-bedrijf.nl
Action: failed
--b--
"""

REPLY = b"""\
From: Jordan <jiromorgan17@gmail.com>
Subject: Re: Voice demo Cool Global
Content-Type: text/plain

Sounds good, let's talk.
"""


def _parse(raw: bytes) -> email.message.EmailMessage:
    return email.message_from_bytes(raw, policy=email.policy.default)


def test_dsn_detected_and_failed_recipient_extracted():
    item = mail_signals._classify(_parse(GMAIL_DSN), watch=())
    assert item.is_dsn
    assert item.bounced == "prospect@bedrijf.nl"


def test_standard_dsn_without_gmail_header_still_yields_recipient():
    item = mail_signals._classify(_parse(STANDARD_DSN), watch=())
    assert item.is_dsn, "postmaster sender + multipart/report must both count as DSN"
    assert item.bounced == "weg@ander-bedrijf.nl"


def test_watched_sender_is_flagged_and_a_plain_reply_is_not_a_dsn():
    item = mail_signals._classify(_parse(REPLY), watch=("jiromorgan17@gmail.com",))
    assert item.watched and not item.is_dsn
    other = mail_signals._classify(_parse(REPLY), watch=("slotenmakerdrs.nl",))
    assert not other.watched


def test_render_puts_bounces_and_watched_deals_on_top():
    items = [
        mail_signals.MailItem(sender="Nieuwsbrief <n@x.nl>", subject="Weekoverzicht"),
        mail_signals.MailItem(
            sender="Jordan <jiromorgan17@gmail.com>", subject="Re: demo", watched=True
        ),
        mail_signals.MailItem(
            sender="mailer-daemon@googlemail.com",
            subject="Failure",
            is_dsn=True,
            bounced="prospect@bedrijf.nl",
        ),
    ]
    lines = mail_signals.render(items)
    assert lines[0] == "MAIL (last 24h)"
    assert "3 inbound · 1 bounce · 1 watched" in lines[1]
    assert lines[2] == "  ⚠ BOUNCE → prospect@bedrijf.nl"
    assert lines[3].startswith("  ● Jordan"), "the live deal outranks the newsletter"
    assert lines[4].startswith("  • Nieuwsbrief")


def test_render_caps_the_list_and_counts_the_rest():
    items = [
        mail_signals.MailItem(sender=f"a{i}@x.nl", subject=f"mail {i}")
        for i in range(mail_signals._MAX_LISTED + 3)
    ]
    lines = mail_signals.render(items)
    assert lines[-1] == "  … +3 more in the inbox"


def test_render_empty_inbox():
    assert mail_signals.render([]) == ["MAIL (last 24h)", "  no inbound mail"]


def test_digest_section_skips_when_unconfigured(monkeypatch):
    for var in ("IMAP_USER", "IMAP_APP_PASSWORD", "GMAIL_USER", "GMAIL_APP_PASSWORD"):
        monkeypatch.delenv(var, raising=False)
    (line,) = mail_signals.digest_section()
    assert line.startswith("MAIL: skipped")


def test_digest_section_reports_a_broken_mailbox_without_raising(monkeypatch):
    monkeypatch.setenv("GMAIL_USER", "davy@klantkraan.nl")
    monkeypatch.setenv("GMAIL_APP_PASSWORD", "x")

    def boom(host, timeout=None):
        raise OSError("connection refused")

    monkeypatch.setattr(mail_signals.imaplib, "IMAP4_SSL", boom)
    (line,) = mail_signals.digest_section()
    assert line.startswith("MAIL: collector broken") and "OSError" in line


def test_fetch_items_reads_inbox_readonly_and_newest_first(monkeypatch):
    monkeypatch.setenv("GMAIL_USER", "davy@klantkraan.nl")
    monkeypatch.setenv("GMAIL_APP_PASSWORD", "app pass word")  # spaces must be stripped
    monkeypatch.setenv("MAIL_WATCH_SENDERS", "jiromorgan17@gmail.com")

    class FakeIMAP:
        def __init__(self, host, timeout=None):
            self.calls: list[tuple] = []

        def login(self, user, password):
            assert (user, password) == ("davy@klantkraan.nl", "apppassword")

        def select(self, box, readonly=False):
            assert box == "INBOX" and readonly is True

        def search(self, charset, query):
            assert query.startswith("(SINCE ")
            return "OK", [b"1 2"]

        def fetch(self, msg_id, spec):
            assert spec == "(BODY.PEEK[])"
            raw = {b"1": GMAIL_DSN, b"2": REPLY}[msg_id]
            return "OK", [(b"header", raw)]

        def logout(self):
            pass

    monkeypatch.setattr(mail_signals.imaplib, "IMAP4_SSL", FakeIMAP)
    items = mail_signals.fetch_items()
    assert [i.watched for i in items] == [True, False], "newest (id 2, the reply) first"
    assert items[1].bounced == "prospect@bedrijf.nl"


# --- digest wiring: mail only on the CLI path ---------------------------------------------


def test_build_digest_appends_mail_section_only_when_asked(monkeypatch, data_dir, clients_dir):
    monkeypatch.setattr(
        mail_signals, "digest_section", lambda now=None: ["MAIL (last 24h)", "  no inbound mail"]
    )
    assert "MAIL" in oversight.build_digest(today=True, mail=True)

    def explode(now=None):
        raise AssertionError("default digest must not touch the mailbox")

    monkeypatch.setattr(mail_signals, "digest_section", explode)
    assert "MAIL" not in oversight.build_digest(today=True)
