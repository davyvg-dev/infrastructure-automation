"""Per-platform formatting for the approval message and for copy-paste delivery."""

from __future__ import annotations

from typing import Any

from .platforms import registry


def verify_flags(draft: dict[str, Any]) -> list[str]:
    """Pre-check warnings for the approval message (empty on pass / when disabled).

    A draft that still fails after its one auto-revise is never dropped — it goes
    to the founder with the failure reasons on top. Same for a judge error.
    """
    v = draft.get("verify") or {}
    if v.get("status") == "fail":
        lines = ["🚩 " + _esc("Pre-check failed (after 1 auto-rewrite) — review extra carefully:")]
        for f in v.get("failures", []):
            reason = f.get("reason") or "no reason given"
            lines.append("• " + _esc(f"{f.get('criterion', 'unknown')}: {reason}"))
        lines.append("")
        return lines
    if v.get("status") == "error":
        err = v.get("error", "unknown error")
        return ["⚠️ " + _esc(f"Verify pass errored — draft is UNCHECKED: {err}"), ""]
    return []


def preview(draft: dict[str, Any]) -> str:
    """The Telegram approval message body."""
    reg = registry()
    lines = verify_flags(draft)
    lines += [f"🧵 *{_esc(draft['pillar'])}* — {_esc(draft['topic'])}", ""]
    for platform, text in draft["variants"].items():
        # Stored drafts may predate a config change — fall back to the raw name.
        desc = reg.get(platform, {})
        label = desc.get("label", platform)
        limit = desc.get("char_limit")
        warn = ""
        if limit and len(text) > limit:
            warn = f"  ⚠️ {len(text)} chars (over {limit})"
        lines.append(f"*{_esc(label)}*{warn}")
        lines.append(_esc(text))
        lines.append("")
    if pending_reel(draft):
        if any(
            m.get("type") == "video" and m.get("status") == "ready" for m in draft.get("media", [])
        ):
            lines.append(
                "🎬 " + _esc("Reel: demo attached — tap 🎬 to swap in your own screen recording.")
            )
        else:
            lines.append(
                "🎬 "
                + _esc(
                    "Reel: waiting for your screen recording — tap the 🎬 button and send the clip."
                )
            )
    return "\n".join(lines).strip()


def newsletter_preview(draft: dict[str, Any]) -> str:
    """The Telegram approval message for a nieuwsbrief draft (kind='newsletter').

    The full .md rides along as a document attachment; this message is the readable
    summary the founder decides on, so it carries subject/preheader with their limits,
    the word count, and the whole body (truncated only if Telegram's cap forces it).
    """
    # Function-level import: formatting is imported by bot before newsletter is needed,
    # and newsletter pulls in the drafting stack — keep that out of module import time.
    from .newsletter import PREHEADER_MAX, SUBJECT_MAX, WORDS_MAX, WORDS_MIN

    subject = draft.get("subject", "")
    preheader = draft.get("preheader", "")
    body = draft.get("body", "")
    words = len(body.split())
    w_warn = "" if WORDS_MIN <= words <= WORDS_MAX else f" ⚠️ need {WORDS_MIN}-{WORDS_MAX}"
    s_warn = f" ⚠️ over {SUBJECT_MAX}" if len(subject) > SUBJECT_MAX else ""
    p_warn = f" ⚠️ over {PREHEADER_MAX}" if len(preheader) > PREHEADER_MAX else ""

    lines = verify_flags(draft)
    lines += [
        f"📰 *{_esc('nieuwsbrief')}* — {_esc(draft.get('edition', draft['id']))} "
        + _esc(f"({words} woorden{w_warn})"),
        "",
        f"*{_esc('Onderwerp:')}* " + _esc(f"{subject} ({len(subject)}/{SUBJECT_MAX}{s_warn})"),
        f"*{_esc('Preheader:')}* "
        + _esc(f"{preheader} ({len(preheader)}/{PREHEADER_MAX}{p_warn})"),
        "",
        _esc(body),
    ]
    text = "\n".join(lines).strip()
    if len(text) > 3900:  # Telegram message cap is 4096; the .md document has the full text
        text = text[:3900].rstrip("\\") + _esc("… (ingekort; volledige tekst in het bestand)")
    return text


def pending_reel(draft: dict[str, Any]) -> bool:
    """True when the draft still carries an unfulfilled recording task."""
    return any(
        m.get("type") == "video" and m.get("status") == "pending_recording"
        for m in draft.get("media", [])
    )


def _esc(text: str) -> str:
    """Escape Telegram MarkdownV2 special chars."""
    specials = r"_*[]()~`>#+-=|{}.!"
    out = []
    for ch in str(text):
        if ch in specials:
            out.append("\\" + ch)
        else:
            out.append(ch)
    return "".join(out)
