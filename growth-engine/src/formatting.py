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
