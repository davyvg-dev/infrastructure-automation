"""Monthly nieuwsbrief drafter — its own draft kind on the shared approval queue.

A nieuwsbrief draft is NOT a social post: no per-platform variants, a page-sized token
budget, and approval writes an .md file instead of publishing anywhere. The record shares
the queue's lifecycle fields (status/awaiting/delivered_at) so the bot's durable-approval
machinery (redelivery, restart resurfacing, rewrite notes) works unchanged:

{
  "id": "20260901-a1b2",
  "kind": "newsletter",
  "pillar": "nieuwsbrief",
  "edition": "editie-2026-09",       # also the output file stem
  "topic": "bereikbaarheid in de herfstdrukte",
  "status": "pending" | "approved" | "skipped",
  "subject": "...", "preheader": "...", "body": "...",
  "file": "data/trades/newsletters/editie-2026-09.md",   # set on approval
}

Approval writes markdown(draft) to data/<vertical>/newsletters/<edition>.md and marks the
draft approved — nothing else. Sending is a separate founder command in the receptionist
repo (`kk nieuwsbrief send`, ai-receptionist/app/nieuwsbrief.py), which parses exactly the
front-matter + paragraphs/heading/button format produced here and appends the signoff
itself, so drafts must never contain one.

The pre-approval check mirrors src/verify.py (one Haiku judge + one auto-revise, fail-open)
but with newsletter criteria, plus deterministic local checks (register, dashes, founder
name, numbers, signoff, format, lengths) that need no API at all.
"""

from __future__ import annotations

import json
import logging
import re
import uuid
from datetime import date
from pathlib import Path
from typing import Any

import anthropic

from . import prompts, store, verify
from .settings import data_dir, dry_run, env, strategy, verify_enabled

log = logging.getLogger(__name__)

KIND = "newsletter"

SUBJECT_MAX = 55
PREHEADER_MAX = 90
WORDS_MIN, WORDS_MAX = 150, 350
ALLOWED_BUTTON_URLS = ("https://klantkraan.nl/demo/", "https://klantkraan.nl/rekentool/")
ALLOWED_NUMBERS = {"299", "499"}  # Klantkraan's own prices; "24/7" is stripped before checking

_MONTHS = [
    "januari", "februari", "maart", "april", "mei", "juni",
    "juli", "augustus", "september", "oktober", "november", "december",
]

_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "topic": {
            "type": "string",
            "description": "Short label for this edition's angle (a few words, Dutch).",
        },
        "subject": {
            "type": "string",
            "description": f"E-mail subject line, max {SUBJECT_MAX} characters, Dutch.",
        },
        "preheader": {
            "type": "string",
            "description": f"Inbox preview line, max {PREHEADER_MAX} characters, Dutch; "
            "complements the subject.",
        },
        "body": {
            "type": "string",
            "description": f"The mail body in plain markdown: {WORDS_MIN}-{WORDS_MAX} words, "
            "paragraphs separated by blank lines, optional '## ' headings, at most one "
            "standalone '[label](url)' button line. No salutation, no signoff.",
        },
    },
    "required": ["topic", "subject", "preheader", "body"],
}


# --------------------------------------------------------------------------- #
# Drafting
# --------------------------------------------------------------------------- #


def _client() -> anthropic.Anthropic:
    # Reads ANTHROPIC_API_KEY from the environment (loaded by settings).
    env("ANTHROPIC_API_KEY")
    return anthropic.Anthropic()


def _request(brief: str) -> dict[str, Any]:
    """One structured-output drafting call; the only function that touches the API."""
    model_cfg = strategy()["model"]
    response = _client().messages.create(
        model=model_cfg["id"],
        max_tokens=4000,  # page-sized: a full mail, not a tweet
        thinking={"type": "adaptive"},
        output_config={
            "effort": model_cfg.get("effort", "medium"),
            "format": {"type": "json_schema", "schema": _SCHEMA},
        },
        system=[
            {
                "type": "text",
                "text": prompts.newsletter_system_prompt(),
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": brief}],
    )
    text = "".join(b.text for b in response.content if b.type == "text")
    return json.loads(text)


def _one_line(text: str) -> str:
    return " ".join(str(text).split())


def _fields(payload: dict[str, Any]) -> dict[str, str]:
    return {
        "topic": _one_line(payload["topic"]),
        "subject": _one_line(payload["subject"]),
        "preheader": _one_line(payload["preheader"]),
        "body": payload["body"].strip(),
    }


def current_edition(today: date | None = None) -> str:
    return f"editie-{today or date.today():%Y-%m}"


def month_label(today: date | None = None) -> str:
    today = today or date.today()
    return f"{_MONTHS[today.month - 1]} {today.year}"


def recent_topics(limit: int = 6) -> list[str]:
    """Topics of earlier editions, so the model doesn't repeat itself."""
    topics = [d["topic"] for d in store.load_queue() if d.get("kind") == KIND and d.get("topic")]
    return topics[-limit:]


def generate_newsletter(today: date | None = None) -> dict[str, Any]:
    """Generate one nieuwsbrief draft for the current month."""
    today = today or date.today()
    payload = _request(prompts.newsletter_brief(month_label(today), recent_topics()))
    return {
        "id": f"{today:%Y%m%d}-{uuid.uuid4().hex[:4]}",
        "kind": KIND,
        "pillar": "nieuwsbrief",
        "edition": current_edition(today),
        "status": "pending",
        "created_at": store.now_iso(),
        **_fields(payload),
    }


def regenerate(draft: dict[str, Any], note: str) -> dict[str, str]:
    """Rewrite the whole edition given a feedback note; returns the updated fields."""
    payload = _request(prompts.newsletter_revise_brief(draft, note))
    return _fields(payload)


def open_edition_draft(today: date | None = None) -> dict[str, Any] | None:
    """This month's edition, if one is already pending or approved (dedupe for the job)."""
    edition = current_edition(today)
    for d in store.load_queue():
        if d.get("kind") == KIND and d.get("edition") == edition and d.get("status") in (
            "pending",
            "approved",
        ):
            return d
    return None


# --------------------------------------------------------------------------- #
# Output file (the format ai-receptionist/app/nieuwsbrief.py parses)
# --------------------------------------------------------------------------- #


def markdown(draft: dict[str, Any]) -> str:
    """Front matter + body, exactly what `kk nieuwsbrief send` consumes."""
    return (
        "---\n"
        f"subject: {_one_line(draft.get('subject', ''))}\n"
        f"preheader: {_one_line(draft.get('preheader', ''))}\n"
        "---\n"
        f"{draft.get('body', '').strip()}\n"
    )


def filename(draft: dict[str, Any]) -> str:
    return f"{draft.get('edition') or draft['id']}.md"


def approve(draft: dict[str, Any]) -> Path:
    """Write the approved .md and mark the draft approved. Nothing is sent from here:
    the file IS the deliverable, so it is written in dry-run too — dry-run approvals
    just carry the tag, exactly like post approvals."""
    path = data_dir() / "newsletters" / filename(draft)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown(draft), encoding="utf-8")
    fields: dict[str, Any] = {
        "status": "approved",
        "approved_at": store.now_iso(),
        "file": str(path),
    }
    if dry_run():
        fields["dry_run"] = True
    store.update_draft(draft["id"], **fields)
    return path


# --------------------------------------------------------------------------- #
# Pre-approval checks: deterministic local rules + a Haiku judge (verify.py's
# pattern: one auto-revise, then deliver flagged; fail-open on judge errors)
# --------------------------------------------------------------------------- #

_DASH_RE = re.compile(r"[—–]")
_FOUNDER_RE = re.compile(r"davy", re.IGNORECASE)
_JE_RE = re.compile(r"\b(je|jij|jou|jouw|jullie)\b", re.IGNORECASE)
_NUMBER_RE = re.compile(r"\d+")
_BUTTON_LINE_RE = re.compile(r"^\[[^\]]+\]\((https?://[^)]+)\)$")
_SIGNOFF_RE = re.compile(
    r"met vriendelijke groet|hartelijke groet|vriendelijke groeten"
    r"|^\s*groet(en)?\s*,?\s*$|team klantkraan",
    re.IGNORECASE | re.MULTILINE,
)

# Judge criteria (ids feed the failure records + Telegram flags, like verify.CRITERIA).
CRITERIA: dict[str, str] = {
    "u_register": (
        "The mail addresses the reader formally with 'u'/'uw' throughout. FAIL on any "
        "informal 'je', 'jij', 'jou(w)' or 'jullie' aimed at the reader."
    ),
    "ai_tells": (
        "The text reads like a professional copywriter, not AI. FAIL on em-dashes (—) "
        "or AI-tell phrasing (hollow hype, 'game-changer', filler openers)."
    ),
    "founder_name": (
        "The founder's first name ('Davy') must NOT appear anywhere. The mail says "
        "'de oprichter' or 'Klantkraan' instead. FAIL on any occurrence."
    ),
    "invented_stats": (
        "No statistics or numeric claims at all. The only numbers allowed are the prices "
        "€299 and €499 and the phrase '24/7'. FAIL on any other number, percentage or "
        "amount, however it is framed."
    ),
    "pricing": (
        "The ONLY amounts that may appear as Klantkraan pricing are €299 (chat) and €499 "
        "(Compleet). Any other Klantkraan price, discount or payment term FAILS. A mail "
        "naming no price passes."
    ),
    "tone": (
        "One clear practical topic, genuinely useful to a trade-business owner, at most "
        "one soft CTA, never salesy. No salutation and no signoff (the sender appends "
        "the signoff automatically). FAIL otherwise."
    ),
}

_VERDICT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "checks": {
            "type": "array",
            "description": "Exactly one entry per criterion.",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "criterion": {"type": "string", "enum": list(CRITERIA)},
                    "passed": {"type": "boolean"},
                    "reason": {
                        "type": "string",
                        "description": "One short sentence on why it failed; empty when passed.",
                    },
                },
                "required": ["criterion", "passed", "reason"],
            },
        },
    },
    "required": ["checks"],
}


def _fail(criterion: str, reason: str) -> dict[str, str]:
    return {"criterion": criterion, "reason": reason}


def local_failures(draft: dict[str, Any]) -> list[dict[str, str]]:
    """Deterministic checks; no API. Same failure shape as the judge produces."""
    subject = draft.get("subject", "")
    preheader = draft.get("preheader", "")
    body = draft.get("body", "")
    everything = "\n".join((subject, preheader, body))
    failures: list[dict[str, str]] = []

    if not subject.strip():
        failures.append(_fail("format", "front matter needs a subject"))
    if not preheader.strip():
        failures.append(_fail("format", "front matter needs a preheader"))
    if not body.strip():
        failures.append(_fail("format", "the body is empty"))

    if len(subject) > SUBJECT_MAX:
        failures.append(_fail("length", f"subject is {len(subject)} chars (max {SUBJECT_MAX})"))
    if len(preheader) > PREHEADER_MAX:
        failures.append(
            _fail("length", f"preheader is {len(preheader)} chars (max {PREHEADER_MAX})")
        )
    words = len(body.split())
    if body.strip() and not WORDS_MIN <= words <= WORDS_MAX:
        failures.append(_fail("length", f"body is {words} words (need {WORDS_MIN}-{WORDS_MAX})"))

    if _DASH_RE.search(everything):
        failures.append(_fail("ai_tells", "contains an em/en-dash"))
    if _FOUNDER_RE.search(everything):
        failures.append(_fail("founder_name", "names the founder"))
    match = _JE_RE.search(everything)
    if match:
        failures.append(_fail("u_register", f"informal register: '{match.group(0)}'"))
    if _SIGNOFF_RE.search(body):
        failures.append(_fail("signoff", "ends with a signoff; the sender appends one itself"))

    numbers = set(_NUMBER_RE.findall(everything.replace("24/7", ""))) - ALLOWED_NUMBERS
    if numbers:
        listed = ", ".join(sorted(numbers))
        failures.append(_fail("invented_stats", f"contains numbers beyond the prices: {listed}"))

    buttons = [
        m for line in body.splitlines() if (m := _BUTTON_LINE_RE.match(line.strip())) is not None
    ]
    if len(buttons) > 1:
        failures.append(_fail("format", f"{len(buttons)} button lines (max one)"))
    for m in buttons:
        url = m.group(1)
        if url.rstrip("/") not in {u.rstrip("/") for u in ALLOWED_BUTTON_URLS}:
            failures.append(_fail("format", f"button links to a non-allowed URL: {url}"))
    inline_links = sum(1 for line in body.splitlines() if "](http" in line) - len(buttons)
    if inline_links > 0:
        failures.append(
            _fail("format", "inline markdown links in running text (the mailer renders "
                  "them literally); only a standalone button line is allowed")
        )
    return failures


def _judge_brief(draft: dict[str, Any]) -> str:
    return (
        f"EDITION: {draft.get('edition', '')}\n"
        f"SUBJECT ({len(draft.get('subject', ''))} chars, max {SUBJECT_MAX}): "
        f"{draft.get('subject', '')}\n"
        f"PREHEADER ({len(draft.get('preheader', ''))} chars, max {PREHEADER_MAX}): "
        f"{draft.get('preheader', '')}\n\n"
        f"BODY:\n{draft.get('body', '')}"
    )


def judge_failures(draft: dict[str, Any]) -> list[dict[str, str]]:
    """One Haiku judge call. Raises on API error (check_and_revise fails open)."""
    rules = "\n".join(f"- {key}: {text}" for key, text in CRITERIA.items())
    system = (
        "You are the pre-publication reviewer for the monthly Klantkraan nieuwsbrief "
        "(klantkraan.nl), an e-mail to Dutch trade-business owners. You grade one draft "
        "against a fixed checklist. Be strict and literal.\n\n"
        f"Checklist:\n{rules}\n\n"
        "Return one check per criterion with passed true/false and, on failure, a short "
        "concrete reason that quotes or names the offending part."
    )
    response = _client().messages.create(
        model=verify.JUDGE_MODEL,
        max_tokens=1000,
        temperature=0,
        output_config={"format": {"type": "json_schema", "schema": _VERDICT_SCHEMA}},
        system=[{"type": "text", "text": system}],
        messages=[{"role": "user", "content": _judge_brief(draft)}],
    )
    text = "".join(b.text for b in response.content if b.type == "text")
    verdict = json.loads(text)
    return [
        _fail(c.get("criterion", "unknown"), (c.get("reason") or "").strip())
        for c in verdict.get("checks", [])
        if not c.get("passed", False)
    ]


def _all_failures(draft: dict[str, Any]) -> list[dict[str, str]]:
    return local_failures(draft) + judge_failures(draft)


def _revision_note(failures: list[dict[str, str]]) -> str:
    issues = "; ".join(f"{f['criterion']}: {f['reason']}" for f in failures)
    return (
        f"An editorial review flagged these issues: {issues}. "
        f"Rewrite the newsletter to fix ALL of them while keeping the same core topic "
        f"and every rule from the system prompt."
    )


def check_and_revise(draft: dict[str, Any]) -> dict[str, Any]:
    """The pre-approval pass, verify.py semantics: always returns the draft, never raises,
    never drops. Annotates draft['verify'] (rendered by formatting.verify_flags)."""
    if not verify_enabled():
        return draft
    try:
        failures = _all_failures(draft)
        if not failures:
            draft["verify"] = {"status": "pass", "failures": [], "revised": False}
            return draft

        log.info(
            "nieuwsbrief %s failed pre-check (%d issue(s)); revising once",
            draft.get("id"),
            len(failures),
        )
        try:
            draft.update(regenerate(draft, _revision_note(failures)))
        except Exception:  # keep the original; the re-check will flag it
            log.exception("nieuwsbrief revise failed; keeping the original")

        failures = _all_failures(draft)
        status = "fail" if failures else "pass"
        draft["verify"] = {"status": status, "failures": failures, "revised": True}
        return draft
    except Exception as exc:
        # Fail-open: the founder still gets the draft, with an errored-check note.
        log.exception("nieuwsbrief verify pass errored; sending draft to Telegram unchecked")
        draft["verify"] = {"status": "error", "failures": [], "error": str(exc)}
        return draft
