"""Generated media — image cards rendered with pure Pillow (no ffmpeg, no macOS tools).

A card is the draft's sharpest claim as a branded image: flat background (or a stock
photo under a dark scrim), accent bar, big headline, optional sub-line, footer. Color
schemes rotate deterministically per draft so the feed doesn't look like one repeated
template. Rendered in the two aspects social platforms want and attached to the draft's
`media` list; delivery stays assisted (the founder posts by hand, per platform ToS).

Stock photos come from the Pexels API (free key, commercial use allowed, no attribution
required). Any photo failure falls back to a flat card — a missing photo must never
kill a draft.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from . import brand, platforms, store
from .settings import data_dir

# (width, height, pexels orientation) per aspect. Square feeds IG/FB feed; story is 9:16.
_SIZES = {"square": (1080, 1080, "square"), "story": (1080, 1920, "portrait")}
_PAD = 96
_TRACKING = -0.02  # headline letter-spacing, fraction of font size (brand: -0.02em)
_SCRIM_ALPHA = 168  # ink overlay on photo cards — keeps text readable, stays flat


def _pick(key: str, n: int) -> int:
    """Deterministic index from a draft id — stable across reruns, varied across drafts."""
    return int(hashlib.sha1(key.encode()).hexdigest(), 16) % n


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont,
          max_width: int, tracking: float = 0.0) -> list[str]:
    """Greedy word-wrap by measured pixel width (Pillow has no built-in wrapping)."""
    def width(s: str) -> float:
        return draw.textlength(s, font=font) + tracking * font.size * max(len(s) - 1, 0)

    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if current and width(candidate) > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def _tracked_text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str,
                  font: ImageFont.FreeTypeFont, fill: str, tracking: float) -> None:
    """Draw text with letter-spacing (Pillow has no native tracking)."""
    x, y = xy
    step = tracking * font.size
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + step


def _cover(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Scale + center-crop to fill `size` (CSS object-fit: cover)."""
    scale = max(size[0] / img.width, size[1] / img.height)
    img = img.resize((round(img.width * scale), round(img.height * scale)))
    left = (img.width - size[0]) // 2
    top = (img.height - size[1]) // 2
    return img.crop((left, top, left + size[0], top + size[1]))


def _stock_photo(query: str, orientation: str) -> Path | None:
    """Fetch one Pexels photo for the query, or None (no key / no hit / any error)."""
    key = os.getenv("PEXELS_API_KEY", "").strip()
    if not key or not query:
        return None
    try:
        params = urllib.parse.urlencode(
            {"query": query, "orientation": orientation, "per_page": 1}
        )
        # Pexels 403s python-urllib's default User-Agent; identify ourselves properly.
        headers = {"Authorization": key, "User-Agent": "klantkraan-growth-engine/1.0"}
        req = urllib.request.Request(
            f"https://api.pexels.com/v1/search?{params}", headers=headers
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            photos = json.load(resp).get("photos") or []
        if not photos:
            return None
        url = photos[0]["src"]["large2x"]
        out = data_dir() / "media" / "stock" / (
            hashlib.sha1(f"{query}-{orientation}".encode()).hexdigest()[:12] + ".jpg"
        )
        if not out.exists():
            out.parent.mkdir(parents=True, exist_ok=True)
            dl = urllib.request.Request(url, headers={"User-Agent": headers["User-Agent"]})
            with urllib.request.urlopen(dl, timeout=30) as resp, out.open("wb") as fh:
                fh.write(resp.read())
        return out
    except Exception as exc:  # degrade to a flat card, but say so
        print(f"stock photo lookup failed ({query!r}): {exc}", file=sys.stderr)
        return None


def _render(headline: str, sub: str, size: tuple[int, int], out_path: Path,
            scheme: dict[str, Any], photo: Path | None) -> None:
    b = brand.brand()
    if photo is not None:
        img = _cover(Image.open(photo).convert("RGB"), size)
        scrim = Image.new("RGBA", size, (26, 26, 26, _SCRIM_ALPHA))  # kraan-ink
        img = Image.alpha_composite(img.convert("RGBA"), scrim).convert("RGB")
        text_color, muted_color = "#FAF6EE", "#D9D2C0"  # fixed for contrast on photos
    else:
        img = Image.new("RGB", size, scheme["bg"])
        text_color, muted_color = scheme["text"], scheme["muted"]
    draw = ImageDraw.Draw(img)
    width, height = size
    text_width = width - 2 * _PAD

    sub_font = ImageFont.truetype(str(b["font_regular"]), 44)
    sub_lines = _wrap(draw, sub, sub_font, text_width) if sub else []
    sub_step = int(sub_font.size * 1.4)

    # Scale the headline down until the whole text block (headline + sub) fits between
    # the accent bar's zone and the footer zone.
    top_min = _PAD + 140
    bottom = height - _PAD - (120 if b["footer"] else 40)
    for pt in (112, 96, 84, 72, 62, 54):
        head_font = ImageFont.truetype(str(b["font_bold"]), pt)
        head_lines = _wrap(draw, headline, head_font, text_width, _TRACKING)
        head_step = int(pt * 1.14)
        block_height = (
            len(head_lines) * head_step
            + (48 + len(sub_lines) * sub_step if sub_lines else 0)
        )
        if len(head_lines) <= 6 and top_min + block_height <= bottom:
            break
    y = top_min + max(0, (bottom - top_min - block_height) // 2)

    # Accent bar above the headline — the only ornament (brand rule: flat, no gradients).
    draw.rectangle((_PAD, y - 78, _PAD + 140, y - 58), fill=scheme["accent"])
    for line in head_lines:
        _tracked_text(draw, (_PAD, y), line, head_font, text_color, _TRACKING)
        y += head_step
    if sub_lines:
        y += 48
        for line in sub_lines:
            draw.text((_PAD, y), line, font=sub_font, fill=muted_color)
            y += sub_step

    if b["footer"]:
        footer_font = ImageFont.truetype(str(b["font_bold"]), 38)
        fy = height - _PAD - 46
        draw.rectangle((_PAD, fy + 6, _PAD + 26, fy + 32), fill=scheme["accent"])
        draw.text((_PAD + 46, fy), b["footer"], font=footer_font, fill=text_color)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG")


def _photo_turn() -> bool:
    """Strict rotation: every Nth card with a photo query becomes a photo card.

    A stored counter, not a hash of the draft id — a per-draft coin flip guarantees
    only the long-run ratio and happily skips photos four drafts in a row.
    """
    stock_cfg = brand.stock()
    if not stock_cfg["enabled"]:
        return False
    n = int(store.get_state("photo_card_cycle", 0))
    store.set_state("photo_card_cycle", n + 1)
    return n % int(stock_cfg["every"]) == 0


def render_cards(headline: str, sub: str, stem: str, out_dir: Path | None = None,
                 photo_query: str = "", use_photo: bool = False) -> list[dict[str, Any]]:
    """Render one card per aspect; returns media records for the draft.

    The stem is the variation key for the color scheme; the photo decision is the
    caller's (attach_cards rotates it via _photo_turn).
    """
    out_dir = out_dir or data_dir() / "media"
    schemes = brand.schemes()
    scheme = schemes[_pick(stem, len(schemes))]
    use_photo = use_photo and bool(photo_query)
    image_platforms = [
        name for name, desc in platforms.registry().items()
        if desc["media"] in ("image", "both")
    ]
    records = []
    for aspect, (w, h, orientation) in _SIZES.items():
        photo = _stock_photo(photo_query, orientation) if use_photo else None
        path = out_dir / f"{stem}-{aspect}.png"
        _render(headline, sub, (w, h), path, scheme, photo)
        records.append({
            "type": "image",
            "path": str(path),
            "aspect": aspect,
            "style": "photo" if photo else "flat",
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
    photo_query = card.get("photo_query", "").strip()
    draft["media"] = render_cards(
        headline,
        card.get("sub", "").strip(),
        draft["id"],
        photo_query=photo_query,
        # Only spend a rotation turn on drafts that actually have a query, so a
        # query-less draft can't swallow the photo slot.
        use_photo=bool(photo_query) and _photo_turn(),
    )
