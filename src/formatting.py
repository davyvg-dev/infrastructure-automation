"""Per-platform formatting for the approval message and for copy-paste delivery."""

from __future__ import annotations

from typing import Any

_LABELS = {
    "x": "𝕏 (auto-post)",
    "linkedin": "in LinkedIn (paste)",
    "reddit": "🔶 Reddit (paste)",
}


def preview(draft: dict[str, Any]) -> str:
    """The Telegram approval message body."""
    lines = [f"🧵 *{_esc(draft['pillar'])}* — {_esc(draft['topic'])}", ""]
    for platform, text in draft["variants"].items():
        label = _LABELS.get(platform, platform)
        warn = ""
        if platform == "x" and len(text) > 280:
            warn = f"  ⚠️ {len(text)} chars (over 280)"
        lines.append(f"*{_esc(label)}*{warn}")
        lines.append(_esc(text))
        lines.append("")
    return "\n".join(lines).strip()


def paste_block(platform: str, text: str) -> str:
    """A clean, code-fenced block the user can one-tap copy on mobile."""
    return f"Copy this for *{_esc(_LABELS.get(platform, platform))}*:\n```\n{text}\n```"


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
