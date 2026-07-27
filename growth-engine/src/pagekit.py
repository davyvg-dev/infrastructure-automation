"""One-time page kit — profile assets for a vertical's IG / TikTok / FB pages.

Renders the avatar (a stylized tap — "kraan"), a Facebook cover, four Instagram
highlight covers, a pinned 4:5 intro card, and a demo reel cover, all in the same
visual language as media.py's cards: flat brand color, accent bar, Inter, tracked
headlines. Run once per vertical:

    GROWTH_CONFIG=config/fitness.yaml python -m src.pagekit

Everything lands in data/<vertical>/pagekit/ (gitignored) for the founder to upload
by hand — setup checklist and paste-ready copy live in docs/PAGE-KIT.md.

`render_cover()` is the one piece meant for reuse: the reel flow can call it to give
every reel a branded cover frame whose content survives all grid crops.
"""

from __future__ import annotations

import hashlib
import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from . import brand
from .settings import data_dir

_PAD = 96
_TRACKING = -0.02  # headline letter-spacing, fraction of font size (brand: -0.02em)

# Reel/highlight covers render at 1080x1920 but are judged in crops: the IG grid
# shows the center 3:4 (top/bottom ~480px cut), TikTok's grid shows the center square
# and overlays its caption on the bottom ~270px (docs/REELS.md §4). The centered
# 1080x1080 square is the only region every surface shows — all content stays inside.
_PORTRAIT = (1080, 1920)
_SQUARE_TOP = (_PORTRAIT[1] - _PORTRAIT[0]) // 2          # 420
_SQUARE_BOTTOM = _SQUARE_TOP + _PORTRAIT[0]               # 1500


# Tiny helpers duplicated from media.py (they are private there, by design).
def _pick(key: str, n: int) -> int:
    """Deterministic index from a key — stable across reruns, varied across keys."""
    return int(hashlib.sha1(key.encode()).hexdigest(), 16) % n


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont,
          max_width: int, tracking: float = 0.0) -> list[str]:
    """Greedy word-wrap by measured pixel width."""
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


def _font(bold: bool, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(brand.font_path(bold=bold)), size)


def _drop(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int, fill: str) -> None:
    """Teardrop: a circle with a triangular apex on top — the water-drop brand motif."""
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill)
    draw.polygon([(cx, cy - 2 * r),
                  (cx - int(0.74 * r), cy - int(0.62 * r)),
                  (cx + int(0.74 * r), cy - int(0.62 * r))], fill=fill)


# --------------------------------------------------------------------------- #
# Avatar
# --------------------------------------------------------------------------- #

def render_avatar(out_dir: Path) -> Path:
    """1080x1080 profile mark: a stylized tap ("kraan") with one accent drop.

    Three thick bars and a drop, huge and flat on purpose — profile pictures render
    as a ~40px circle, so everything sits well inside the circle crop and survives it.
    """
    b = brand.brand()
    img = Image.new("RGB", (1080, 1080), b["bg"])
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((300, 280, 470, 700), radius=84, fill=b["text"])  # riser
    d.rounded_rectangle((300, 280, 780, 450), radius=84, fill=b["text"])  # arm
    d.rounded_rectangle((640, 280, 780, 510), radius=70, fill=b["text"])  # spout
    _drop(d, 710, 745, 104, b["accent"])
    path = out_dir / "avatar.png"
    img.save(path, "PNG")
    return path


def render_avatar_preview(avatar: Path, out_dir: Path) -> Path:
    """The avatar circle-cropped at real UI sizes so the founder can judge legibility."""
    src = Image.open(avatar)
    canvas = Image.new("RGB", (640, 300), "#FAF6EE")
    d = ImageDraw.Draw(canvas)
    label_font = _font(bold=False, size=26)
    x = 70
    for size in (160, 80, 40):
        mask = Image.new("L", (size * 4, size * 4), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, size * 4, size * 4), fill=255)
        mask = mask.resize((size, size), Image.LANCZOS)
        disc = src.resize((size, size), Image.LANCZOS)
        canvas.paste(disc, (x, 50 + (160 - size) // 2), mask)
        label = f"{size}px"
        lw = d.textlength(label, font=label_font)
        d.text((x + (size - lw) / 2, 236), label, font=label_font, fill="#1A1A1A")
        x += size + 80
    path = out_dir / "avatar-preview.png"
    canvas.save(path, "PNG")
    return path


# --------------------------------------------------------------------------- #
# Facebook cover
# --------------------------------------------------------------------------- #

def render_fb_cover(out_dir: Path) -> Path:
    """820x312 Facebook page cover; all content inside the centered 640x312
    mobile-safe area (phones crop the sides off the desktop canvas)."""
    b = brand.brand()
    width, height = 820, 312
    img = Image.new("RGB", (width, height), b["bg"])
    d = ImageDraw.Draw(img)
    x = (width - 640) // 2 + 36                     # safe area + inner padding
    max_w = 640 - 2 * 36
    head_font = _font(bold=True, size=44)
    lines = _wrap(d, "Elk bericht direct beantwoord. 24/7.", head_font, max_w, _TRACKING)
    step = int(head_font.size * 1.14)
    url_font = _font(bold=True, size=30)
    block = 14 + 24 + len(lines) * step + 18 + 38
    y = (height - block) // 2
    d.rectangle((x, y, x + 96, y + 14), fill=b["accent"])
    y += 14 + 24
    for line in lines:
        _tracked_text(d, (x, y), line, head_font, b["text"], _TRACKING)
        y += step
    y += 18
    d.rectangle((x, y + 6, x + 20, y + 26), fill=b["accent"])
    d.text((x + 34, y), b["footer"] or b.get("website", ""), font=url_font,
           fill=b["muted"])
    path = out_dir / "fb-cover.png"
    img.save(path, "PNG")
    return path


# --------------------------------------------------------------------------- #
# Instagram highlight covers
# --------------------------------------------------------------------------- #

def _glyph_demo(d: ImageDraw.ImageDraw, cx: int, cy: int, accent: str, bg: str) -> None:
    d.polygon([(cx - 62, cy - 96), (cx + 108, cy), (cx - 62, cy + 96)], fill=accent)


def _glyph_resultaten(d: ImageDraw.ImageDraw, cx: int, cy: int, accent: str,
                      bg: str) -> None:
    bar_w, gap = 56, 32
    x = cx - (3 * bar_w + 2 * gap) // 2
    base = cy + 100
    for h in (88, 138, 196):
        d.rounded_rectangle((x, base - h, x + bar_w, base), radius=14, fill=accent)
        x += bar_w + gap


def _glyph_uitleg(d: ImageDraw.ImageDraw, cx: int, cy: int, accent: str,
                  bg: str) -> None:
    d.rounded_rectangle((cx - 130, cy - 95, cx + 130, cy + 55), radius=42, fill=accent)
    d.polygon([(cx - 70, cy + 45), (cx - 10, cy + 45), (cx - 92, cy + 118)],
              fill=accent)
    for i, w in enumerate((150, 100)):
        y = cy - 48 + i * 44
        d.rounded_rectangle((cx - 92, y, cx - 92 + w, y + 18), radius=9, fill=bg)


def _glyph_over_ons(d: ImageDraw.ImageDraw, cx: int, cy: int, accent: str,
                    bg: str) -> None:
    _drop(d, cx, cy + 38, 88, accent)


_HIGHLIGHTS: list[tuple[str, Callable[..., None]]] = [
    ("Demo", _glyph_demo),
    ("Resultaten", _glyph_resultaten),
    ("Uitleg", _glyph_uitleg),
    ("Over ons", _glyph_over_ons),
]


def render_highlights(out_dir: Path) -> list[Path]:
    """Four 1080x1920 highlight covers: ring + glyph + label, one consistent scheme.

    IG displays a highlight cover as the circle inscribed in the image center, so the
    motif sits within ~430px of (540, 960) — comfortably inside every crop.
    """
    b = brand.brand()
    paths = []
    for name, glyph in _HIGHLIGHTS:
        img = Image.new("RGB", _PORTRAIT, b["bg"])
        d = ImageDraw.Draw(img)
        cx, cy = 540, 900
        d.ellipse((cx - 220, cy - 220, cx + 220, cy + 220), outline=b["text"],
                  width=14)
        glyph(d, cx, cy, b["accent"], b["bg"])
        label = name.upper()
        label_font = _font(bold=True, size=54)
        tracking = 0.12
        lw = (d.textlength(label, font=label_font)
              + tracking * label_font.size * max(len(label) - 1, 0))
        _tracked_text(d, (int((1080 - lw) / 2), 1190), label, label_font,
                      b["text"], tracking)
        path = out_dir / f"highlight-{name.lower().replace(' ', '-')}.png"
        img.save(path, "PNG")
        paths.append(path)
    return paths


# --------------------------------------------------------------------------- #
# Pinned intro card
# --------------------------------------------------------------------------- #

def render_pinned(out_dir: Path) -> Path:
    """1080x1350 (4:5) intro card in the media.py card style — the profile's anchor
    post, so it uses the base brand scheme, not a rotated one."""
    b = brand.brand()
    headline = "Elk bericht direct beantwoord. Elke proefles meteen geboekt."
    sub = ("Klantkraan bouwt de AI-ledenassistent voor sportclubs: leden en leads "
           "krijgen 24/7 direct antwoord en de proefles staat meteen in de agenda. "
           "Hier zie je hem werken — echte gesprekken, echte boekingen.")
    size = (1080, 1350)
    img = Image.new("RGB", size, b["bg"])
    d = ImageDraw.Draw(img)
    text_w = size[0] - 2 * _PAD

    sub_font = _font(bold=False, size=44)
    sub_lines = _wrap(d, sub, sub_font, text_w)
    sub_step = int(sub_font.size * 1.4)

    top_min = _PAD + 140
    bottom = size[1] - _PAD - 120
    for pt in (96, 84, 72, 62, 54):
        head_font = _font(bold=True, size=pt)
        head_lines = _wrap(d, headline, head_font, text_w, _TRACKING)
        head_step = int(pt * 1.14)
        block = len(head_lines) * head_step + 48 + len(sub_lines) * sub_step
        if len(head_lines) <= 5 and top_min + block <= bottom:
            break
    y = top_min + max(0, (bottom - top_min - block) // 2)

    d.rectangle((_PAD, y - 78, _PAD + 140, y - 58), fill=b["accent"])
    for line in head_lines:
        _tracked_text(d, (_PAD, y), line, head_font, b["text"], _TRACKING)
        y += head_step
    y += 48
    for line in sub_lines:
        d.text((_PAD, y), line, font=sub_font, fill=b["muted"])
        y += sub_step

    if b["footer"]:
        footer_font = _font(bold=True, size=38)
        fy = size[1] - _PAD - 46
        d.rectangle((_PAD, fy + 6, _PAD + 26, fy + 32), fill=b["accent"])
        d.text((_PAD + 46, fy), b["footer"], font=footer_font, fill=b["text"])

    path = out_dir / "pinned-post.png"
    img.save(path, "PNG")
    return path


# --------------------------------------------------------------------------- #
# Reel cover — the reusable piece (wired into the reel flow later)
# --------------------------------------------------------------------------- #

def render_cover(headline: str, stem: str) -> Path:
    """1080x1920 reel cover with all content inside the centered 1080x1080 square.

    One bold Dutch title plus the footer URL; color scheme rotates deterministically
    by stem — the same key the draft's cards hash on, so cover and cards match.
    Writes next to the reel in data/<vertical>/media/.
    """
    schemes = brand.schemes()
    scheme: dict[str, Any] = schemes[_pick(stem, len(schemes))]
    b = brand.brand()
    img = Image.new("RGB", _PORTRAIT, scheme["bg"])
    d = ImageDraw.Draw(img)
    text_w = _PORTRAIT[0] - 2 * _PAD

    footer_font = _font(bold=True, size=40)
    fy = _SQUARE_BOTTOM - 60 - 48                    # footer stays inside the square
    top = _SQUARE_TOP + 60 + 100                     # room for the accent bar
    bottom = fy - 40
    for pt in (112, 96, 84, 72, 62, 54):
        head_font = _font(bold=True, size=pt)
        lines = _wrap(d, headline, head_font, text_w, _TRACKING)
        step = int(pt * 1.14)
        block = len(lines) * step
        if len(lines) <= 5 and top + block <= bottom:
            break
    y = top + max(0, (bottom - top - block) // 2)

    d.rectangle((_PAD, y - 78, _PAD + 140, y - 58), fill=scheme["accent"])
    for line in lines:
        _tracked_text(d, (_PAD, y), line, head_font, scheme["text"], _TRACKING)
        y += step
    if b["footer"]:
        d.rectangle((_PAD, fy + 6, _PAD + 26, fy + 32), fill=scheme["accent"])
        d.text((_PAD + 46, fy), b["footer"], font=footer_font, fill=scheme["text"])

    out = data_dir() / "media" / f"{stem}-cover.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG")
    return out


# --------------------------------------------------------------------------- #

def main() -> None:
    out_dir = data_dir() / "pagekit"
    out_dir.mkdir(parents=True, exist_ok=True)
    avatar = render_avatar(out_dir)
    paths = [
        avatar,
        render_avatar_preview(avatar, out_dir),
        render_fb_cover(out_dir),
        *render_highlights(out_dir),
        render_pinned(out_dir),
    ]
    demo = render_cover("Proefles geboekt om 22:47 — zonder personeel.", "pagekit-demo")
    reel_cover = out_dir / "reel-cover.png"
    shutil.copyfile(demo, reel_cover)
    paths.append(reel_cover)
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
