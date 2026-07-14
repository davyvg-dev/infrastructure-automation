"""Generated media — image cards rendered with pure Pillow (no ffmpeg, no macOS tools).

A card is the draft's sharpest claim as a branded image: flat background, accent bar,
big headline, optional sub-line, footer. Rendered in the two aspects social platforms
want and attached to the draft's `media` list; delivery stays assisted (the founder
posts them by hand, per platform ToS).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from . import brand, platforms
from .settings import data_dir

# (width, height) per aspect. Square feeds IG/FB feed; story is the 9:16 surface.
_SIZES = {"square": (1080, 1080), "story": (1080, 1920)}
_PAD = 96


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont,
          max_width: int) -> list[str]:
    """Greedy word-wrap by measured pixel width (Pillow has no built-in wrapping)."""
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if current and draw.textlength(candidate, font=font) > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def _render(headline: str, sub: str, size: tuple[int, int], out_path: Path) -> None:
    b = brand.brand()
    img = Image.new("RGB", size, b["bg"])
    draw = ImageDraw.Draw(img)
    width, height = size
    text_width = width - 2 * _PAD

    # Scale the headline down until it fits in at most 6 lines.
    for pt in (96, 84, 72, 62):
        head_font = ImageFont.truetype(str(b["font_bold"]), pt)
        head_lines = _wrap(draw, headline, head_font, text_width)
        if len(head_lines) <= 6:
            break
    sub_font = ImageFont.truetype(str(b["font_regular"]), 44)
    sub_lines = _wrap(draw, sub, sub_font, text_width) if sub else []
    head_step = int(head_font.size * 1.18)
    sub_step = int(sub_font.size * 1.35)

    block_height = (
        len(head_lines) * head_step
        + (40 + len(sub_lines) * sub_step if sub_lines else 0)
    )
    y = max(_PAD + 200, (height - block_height) // 2)

    # Accent bar above the headline — the only ornament (brand rule: flat, no gradients).
    draw.rectangle((_PAD, y - 76, _PAD + 140, y - 56), fill=b["accent"])
    for line in head_lines:
        draw.text((_PAD, y), line, font=head_font, fill=b["text"])
        y += head_step
    if sub_lines:
        y += 40
        for line in sub_lines:
            draw.text((_PAD, y), line, font=sub_font, fill=b["muted"])
            y += sub_step

    if b["footer"]:
        footer_font = ImageFont.truetype(str(b["font_bold"]), 40)
        draw.text((_PAD, height - _PAD - 48), b["footer"], font=footer_font, fill=b["text"])

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG")


def render_cards(headline: str, sub: str, stem: str,
                 out_dir: Path | None = None) -> list[dict[str, Any]]:
    """Render one card per aspect; returns media records for the draft."""
    out_dir = out_dir or data_dir() / "media"
    image_platforms = [
        name for name, desc in platforms.registry().items()
        if desc["media"] in ("image", "both")
    ]
    records = []
    for aspect, size in _SIZES.items():
        path = out_dir / f"{stem}-{aspect}.png"
        _render(headline, sub, size, path)
        records.append({
            "type": "image",
            "path": str(path),
            "aspect": aspect,
            "platform_targets": image_platforms,
            "status": "ready",
        })
    return records


def attach_cards(draft: dict[str, Any]) -> None:
    """Render the draft's card spec (if any) and attach it as draft['media']."""
    if not brand.cards_enabled():
        return
    card = draft.get("card") or {}
    headline = card.get("headline", "").strip()
    if not headline:
        return
    draft["media"] = render_cards(headline, card.get("sub", "").strip(), draft["id"])
