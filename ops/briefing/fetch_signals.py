#!/usr/bin/env python3
"""Read-only signal collectors for the daily ops briefing.

Emits one consolidated plain-text dump on stdout:

    EMAIL     last 24h of INBOX headers + body previews (IMAP, read-only),
              with DSN/bounce detection and live-deal sender flagging
    SEQUENCE  the outreach sequence board (who is due for which touch)
    PIPELINE  the deal pipeline board (text kanban)
    CALLS     recent voice calls from the ElevenLabs call log

Strictly read-only: IMAP is opened readonly with BODY.PEEK, the board commands
are print-only views, and nothing here ever writes to the outreach ledger.

Each collector is wrapped so one failure cannot kill the run. A collector that
is not configured (missing creds) is SKIPPED; one that is configured but broken
is FAILED and makes the whole script exit 1 — fail loudly, never silently thin.

Python 3 stdlib only. No third-party imports.
"""

import email
import email.policy
import imaplib
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent  # ops/briefing/ -> repo root
RECEPTIONIST = ROOT / "ai-receptionist"
RECEPTIONIST_PY = RECEPTIONIST / ".venv" / "bin" / "python"
VOICE_DEMO = ROOT / "klantkraan" / "apps" / "voice-agent" / "demo"
VOICE_PY = ROOT / "klantkraan" / "apps" / "voice-agent" / ".venv" / "bin" / "python"

# Inbound mail from these senders is a live deal — the model must lead with it.
LIVE_DEAL_SENDERS = (
    "slotenmakerdrs.nl",       # DRS — offer sent, awaiting reply
    "jiromorgan17@gmail.com",  # Jordan / Cool Global — offer sent, awaiting reply
)

DSN_SENDER_HINTS = ("mailer-daemon", "postmaster", "mail delivery")

BODY_PREVIEW_LINES = 10
MAX_MESSAGES = 50
SUBPROCESS_TIMEOUT = 90

# collector name -> "OK ..." | "SKIPPED ..." | "FAILED ..."
STATUS: dict[str, str] = {}


def section(title: str, body: str) -> None:
    print(f"\n== {title} ==")
    print(body.rstrip() if body.strip() else "(leeg)")


# ---------------------------------------------------------------------------
# (a) IMAP — last 24h of INBOX, read-only
# ---------------------------------------------------------------------------


def _body_preview(msg: email.message.EmailMessage) -> str:
    part = msg.get_body(preferencelist=("plain",))
    if part is None:
        return "(geen tekst-body)"
    try:
        text = part.get_content()
    except Exception:
        payload = part.get_payload(decode=True) or b""
        text = payload.decode("utf-8", errors="replace")
    lines = [ln.rstrip() for ln in text.splitlines() if ln.strip()]
    preview = lines[:BODY_PREVIEW_LINES]
    if len(lines) > BODY_PREVIEW_LINES:
        preview.append(f"[... {len(lines) - BODY_PREVIEW_LINES} regels meer]")
    return "\n".join("    " + ln for ln in preview) or "(lege body)"


def _is_dsn(msg: email.message.EmailMessage, sender: str) -> bool:
    if msg.get_content_type() == "multipart/report":
        return True
    return any(hint in sender.lower() for hint in DSN_SENDER_HINTS)


def collect_email() -> None:
    user = os.environ.get("IMAP_USER")
    password = os.environ.get("IMAP_APP_PASSWORD")
    host = os.environ.get("IMAP_HOST", "imap.gmail.com")
    if not user or not password:
        STATUS["email"] = "SKIPPED (IMAP_USER/IMAP_APP_PASSWORD niet gezet)"
        section("EMAIL (laatste 24u INBOX)", "overgeslagen: IMAP niet geconfigureerd")
        return

    try:
        imap = imaplib.IMAP4_SSL(host, timeout=30)
        try:
            imap.login(user, password)
            imap.select("INBOX", readonly=True)  # read-only: geen flags, niets gemarkeerd
            since = (datetime.now() - timedelta(days=1)).strftime("%d-%b-%Y")
            _, data = imap.search(None, f"(SINCE {since})")
            ids = data[0].split()
            ids = ids[-MAX_MESSAGES:]  # nieuwste eerst na reverse
            out, dsn_count, deal_count = [], 0, 0
            for msg_id in reversed(ids):
                _, fetched = imap.fetch(msg_id, "(BODY.PEEK[])")
                raw = next((p[1] for p in fetched if isinstance(p, tuple)), None)
                if raw is None:
                    continue
                msg = email.message_from_bytes(raw, policy=email.policy.default)
                sender = str(msg.get("From", "?"))
                subject = str(msg.get("Subject", "(geen onderwerp)"))
                date = str(msg.get("Date", "?"))
                tags = []
                if _is_dsn(msg, sender):
                    tags.append("[DSN/BOUNCE]")
                    dsn_count += 1
                if any(d in sender.lower() for d in LIVE_DEAL_SENDERS):
                    tags.append("[LIVE DEAL — REPLY]")
                    deal_count += 1
                tag = (" ".join(tags) + " ") if tags else ""
                out.append(f"- {tag}Van: {sender}\n  Datum: {date}\n  Onderwerp: {subject}")
                out.append(_body_preview(msg))
            body = "\n".join(out) if out else "geen mail in de laatste 24 uur"
            section("EMAIL (laatste 24u INBOX)", body)
            STATUS["email"] = f"OK ({len(ids)} berichten, {dsn_count} DSN, {deal_count} live-deal)"
        finally:
            try:
                imap.logout()
            except Exception:
                pass
    except Exception as exc:  # geconfigureerd maar kapot -> luid falen
        STATUS["email"] = f"FAILED ({type(exc).__name__}: {exc})"
        section("EMAIL (laatste 24u INBOX)", f"COLLECTOR KAPOT: {exc}")


# ---------------------------------------------------------------------------
# (b) boards — subprocess capture of print-only views
# ---------------------------------------------------------------------------


def _capture(name: str, title: str, cmd: list[str], cwd: Path) -> None:
    if not Path(cmd[0]).exists():
        STATUS[name] = f"SKIPPED ({cmd[0]} ontbreekt)"
        section(title, f"overgeslagen: {cmd[0]} niet gevonden")
        return
    try:
        run = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, timeout=SUBPROCESS_TIMEOUT
        )
        if run.returncode != 0:
            STATUS[name] = f"FAILED (exit {run.returncode})"
            section(title, f"COLLECTOR KAPOT (exit {run.returncode}):\n{run.stdout}\n{run.stderr}")
            return
        section(title, run.stdout)
        STATUS[name] = "OK"
    except Exception as exc:
        STATUS[name] = f"FAILED ({type(exc).__name__}: {exc})"
        section(title, f"COLLECTOR KAPOT: {exc}")


def collect_sequence_board() -> None:
    _capture(
        "sequence",
        "OUTREACH SEQUENCE BOARD (touches due)",
        [str(RECEPTIONIST_PY), str(RECEPTIONIST / "scripts" / "sequence.py"), "board"],
        RECEPTIONIST,
    )


def collect_pipeline_board() -> None:
    _capture(
        "pipeline",
        "PIPELINE BOARD (deal kanban)",
        [str(RECEPTIONIST_PY), "-m", "app.pipeline", "board"],
        RECEPTIONIST,
    )


# ---------------------------------------------------------------------------
# (c) voice call log — calls.py list (line-based text view)
# ---------------------------------------------------------------------------


def collect_calls() -> None:
    name, title = "calls", "VOICE CALL LOG (recente gesprekken)"
    script = VOICE_DEMO / "calls.py"
    python = VOICE_PY if VOICE_PY.exists() else Path(sys.executable)
    if not script.exists():
        STATUS[name] = f"SKIPPED ({script} ontbreekt)"
        section(title, "overgeslagen: calls.py niet gevonden")
        return
    try:
        run = subprocess.run(
            [str(python), str(script), "list"],
            cwd=VOICE_DEMO,
            capture_output=True,
            text=True,
            timeout=SUBPROCESS_TIMEOUT,
        )
        combined = (run.stdout + run.stderr).strip()
        if run.returncode != 0:
            # calls.py sys.exit't met een duidelijke melding als de API key ontbreekt
            # — dat is "niet geconfigureerd", geen kapotte collector.
            if "not set and not found" in combined:
                STATUS[name] = "SKIPPED (ELEVENLABS creds niet gezet)"
                section(title, f"overgeslagen: {combined}")
            else:
                STATUS[name] = f"FAILED (exit {run.returncode})"
                section(title, f"COLLECTOR KAPOT (exit {run.returncode}):\n{combined}")
            return
        section(title, run.stdout)
        STATUS[name] = "OK"
    except Exception as exc:
        STATUS[name] = f"FAILED ({type(exc).__name__}: {exc})"
        section(title, f"COLLECTOR KAPOT: {exc}")


# ---------------------------------------------------------------------------


def main() -> int:
    print(f"KLANTKRAAN DAGELIJKSE SIGNALEN — {datetime.now():%Y-%m-%d %H:%M}")
    collect_email()
    collect_sequence_board()
    collect_pipeline_board()
    collect_calls()

    section("COLLECTOR STATUS", "\n".join(f"{k}: {v}" for k, v in STATUS.items()))
    failed = [k for k, v in STATUS.items() if v.startswith("FAILED")]
    if failed:
        print(f"\nLET OP: collector(s) kapot: {', '.join(failed)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
