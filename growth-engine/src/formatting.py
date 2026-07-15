"""Per-platform formatting for the approval message and for copy-paste delivery."""

from __future__ import annotations

from typing import Any

from .platforms import registry


def preview(draft: dict[str, Any]) -> str:
    """The Telegram approval message body."""
    reg = registry()
    lines = [f"🧵 *{_esc(draft['pillar'])}* — {_esc(draft['topic'])}", ""]
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
        if any(m.get("type") == "video" and m.get("status") == "ready"
               for m in draft.get("media", [])):
            lines.append("🎬 " + _esc("Reel: demo attached — tap 🎬 to swap in "
                                      "your own screen recording."))
        else:
            lines.append("🎬 " + _esc("Reel: waiting for your screen recording — "
                                      "tap the 🎬 button and send the clip."))
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
