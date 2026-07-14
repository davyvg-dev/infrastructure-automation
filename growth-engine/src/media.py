"""Generated media — image cards (pure Pillow) and reels (ffmpeg + Pillow cards).

A card is the draft's sharpest claim as a branded image: flat background (or a stock
photo under a dark scrim), accent bar, big headline, optional sub-line, footer. Color
schemes rotate deterministically per draft so the feed doesn't look like one repeated
template. Rendered in the two aspects social platforms want and attached to the draft's
`media` list; delivery stays assisted (the founder posts by hand, per platform ToS).

Stock photos come from the Pexels API (free key, commercial use allowed, no attribution
required). Any photo failure falls back to a flat card — a missing photo must never
kill a draft.

A reel is a raw screen recording (the founder demos the receptionist on their phone)
turned into a branded 9:16 video: iOS status bar cropped off, dead time (typing,
waiting) pop-cut away so messages appear back-to-back, placed on a brand stage,
book-ended with Pillow-rendered title/end cards. All text is Pillow — this ffmpeg
build has no drawtext.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
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


# Pexels 403s python-urllib's default User-Agent; identify ourselves properly.
_UA = "klantkraan-growth-engine/1.0"


def _search(query: str, orientation: str, key: str) -> list[dict[str, Any]]:
    params = urllib.parse.urlencode(
        {"query": query, "orientation": orientation, "per_page": 5}
    )
    req = urllib.request.Request(
        f"https://api.pexels.com/v1/search?{params}",
        headers={"Authorization": key, "User-Agent": _UA},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.load(resp).get("photos") or []


def _stock_photo(query: str, orientation: str, variant: int = 0) -> Path | None:
    """Fetch a Pexels photo for the query, or None (no key / no hit / any error).

    The config `media.stock.theme` is appended to keep results in-industry; if that
    themed search is too narrow to match anything, retry with the bare query. `variant`
    picks among the top results so similar queries don't repeat the same photo.
    """
    key = os.getenv("PEXELS_API_KEY", "").strip()
    if not key or not query:
        return None
    theme = str(brand.stock().get("theme", "")).strip()
    try:
        photos = _search(f"{query} {theme}".strip(), orientation, key)
        if not photos and theme:
            photos = _search(query, orientation, key)
        if not photos:
            print(f"stock photo: no results for {query!r}", file=sys.stderr)
            return None
        photo = photos[variant % len(photos)]
        url = photo["src"]["large2x"]
        out = data_dir() / "media" / "stock" / f"{photo['id']}-{orientation}.jpg"
        if not out.exists():
            out.parent.mkdir(parents=True, exist_ok=True)
            dl = urllib.request.Request(url, headers={"User-Agent": _UA})
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
    variant = _pick(stem, 5)
    records = []
    for aspect, (w, h, orientation) in _SIZES.items():
        photo = _stock_photo(photo_query, orientation, variant) if use_photo else None
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


# --------------------------------------------------------------------------- #
# Reels
# --------------------------------------------------------------------------- #

_REEL_SIZE = (1080, 1920)
_FPS = 30


def attach_reel_task(draft: dict[str, Any], requested: list[str]) -> None:
    """Append a pending-recording video task when the draft targets video platforms.

    The task is fulfilled later via the bot's 🎬 flow (founder uploads a screen
    recording, build_reel turns it into the branded reel). It never blocks approval —
    captions and image cards deliver regardless.
    """
    if not brand.reel()["enabled"]:
        return
    reg = platforms.registry()
    targets = [
        p for p in requested if reg.get(p, {}).get("media") in ("video", "both")
    ]
    if not targets:
        return
    draft.setdefault("media", []).append({
        "type": "video",
        "status": "pending_recording",
        "platform_targets": targets,
    })


def _probe(path: Path) -> tuple[int, int, float]:
    """Source video (width, height, duration in seconds) via ffprobe."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-show_entries", "format=duration",
         "-of", "json", str(path)],
        capture_output=True, text=True, check=True,
    )
    info = json.loads(out.stdout)
    stream = info["streams"][0]
    return int(stream["width"]), int(stream["height"]), float(info["format"]["duration"])


def _render_stage(out_path: Path, scheme: dict[str, Any]) -> None:
    """The 9:16 backdrop the demo video sits on — brand color, accent bar, footer."""
    b = brand.brand()
    img = Image.new("RGB", _REEL_SIZE, scheme["bg"])
    draw = ImageDraw.Draw(img)
    draw.rectangle((_PAD, _PAD, _PAD + 140, _PAD + 20), fill=scheme["accent"])
    if b["footer"]:
        footer_font = ImageFont.truetype(str(b["font_bold"]), 38)
        fy = _REEL_SIZE[1] - _PAD - 46
        draw.rectangle((_PAD, fy + 6, _PAD + 26, fy + 32), fill=scheme["accent"])
        draw.text((_PAD + 46, fy), b["footer"], font=footer_font, fill=scheme["text"])
    img.save(out_path, "PNG")


def _detect_change_times(raw: Path, crop: str, threshold: float) -> list[float]:
    """Seconds at which the (cropped) screen visibly changes — a message popping in.

    Typing indicators and the status-bar clock move too little to cross the scene
    threshold, so the quiet stretches between changes carry no timestamps.
    """
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-v", "info", "-i", str(raw),
         "-vf", f"{crop},select='gt(scene,{threshold})',showinfo",
         "-f", "null", "-"],
        capture_output=True, text=True, timeout=120,
    )
    return [float(m) for m in re.findall(r"pts_time:([0-9]+\.?[0-9]*)", result.stderr)]


def _pop_beats(times: list[float], duration: float, usable: float,
               dwell_max: float) -> list[tuple[float, float]]:
    """Keep-segments from change moments: each pop holds just long enough to read.

    The dwell shrinks as pops multiply so the demo fits `usable` seconds; overlapping
    holds merge so rapid sequences play through uncut.
    """
    starts = [0.0]
    for t in sorted(times):
        if t - starts[-1] >= 0.25:  # double-triggers within one pop animation
            starts.append(max(t - 0.05, 0.0))
    dwell = max(0.5, min(dwell_max, usable / len(starts)))
    beats: list[tuple[float, float]] = []
    for s in starts:
        e = min(s + dwell, duration)
        if beats and s <= beats[-1][1] + 0.05:
            beats[-1] = (beats[-1][0], max(beats[-1][1], e))
        else:
            beats.append((s, e))
    return [(s, e) for s, e in beats if e - s > 0.05]


def _cut_filter(crop: str, beats: list[tuple[float, float]]) -> str:
    """Jump-cut filter: crop once, then keep only the given (start, end) segments."""
    n = len(beats)
    parts = [f"[1:v]{crop},split={n}" + "".join(f"[c{i}]" for i in range(n)) + ";"]
    for i, (s, e) in enumerate(beats):
        parts.append(f"[c{i}]trim=start={s:.3f}:end={e:.3f},setpts=PTS-STARTPTS[t{i}];")
    parts.append("".join(f"[t{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[cut];")
    return "".join(parts)


def build_reel(raw: Path, stem: str, headline: str, sub: str = "",
               beats: list[tuple[float, float]] | None = None,
               out_dir: Path | None = None) -> dict[str, Any]:
    """Cut a raw screen recording into a branded 1080×1920 reel; returns a media record.

    With `pop_cuts` (default) the dead time — typing, waiting on replies — is cut out
    entirely: only a short hold around each screen change survives, so messages pop in
    back-to-back and the finished reel stays under `target_seconds` (cards included).
    Explicit `beats` (start, end) override the detection; if no changes are detected
    the whole clip is sped up instead. Audio is dropped — screen recordings are silent
    and IG/TikTok music is added in-app.
    """
    for tool in ("ffmpeg", "ffprobe"):
        if shutil.which(tool) is None:
            raise RuntimeError(f"{tool} is not installed (needed for reels)")
    cfg = brand.reel()
    out_dir = out_dir or data_dir() / "media"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{stem}-reel.mp4"

    width, height, duration = _probe(raw)
    crop_top = int(height * float(cfg["crop_top"])) // 2 * 2
    crop_bottom = int(height * float(cfg["crop_bottom"])) // 2 * 2
    crop = f"crop=iw:ih-{crop_top + crop_bottom}:0:{crop_top}"
    # Budget for the demo footage once the title and end cards take their share.
    usable = max(
        float(cfg["target_seconds"]) - float(cfg["title_seconds"])
        - float(cfg["end_seconds"]),
        3.0,
    )
    if beats is None and cfg["pop_cuts"]:
        times = _detect_change_times(raw, crop, float(cfg["scene_threshold"]))
        if times:
            beats = _pop_beats(times, duration, usable, float(cfg["dwell_seconds"]))
    kept = sum(e - s for s, e in beats) if beats else duration
    speed = min(max(kept / usable, 1.0), float(cfg["max_speed"]))

    # The demo video sits inside the stage between the accent bar and the footer.
    box_w = _REEL_SIZE[0] - 2 * _PAD
    box_h = _REEL_SIZE[1] - 2 * (_PAD + 150)

    schemes = brand.schemes()
    scheme = schemes[_pick(stem, len(schemes))]  # same scheme as the draft's card
    b = brand.brand()
    cta_headline = str(cfg["cta_headline"]).strip() or b["footer"] or headline
    with tempfile.TemporaryDirectory() as tmp:
        title_png, end_png, stage_png = (Path(tmp) / n for n in
                                         ("title.png", "end.png", "stage.png"))
        _render(headline, sub, _REEL_SIZE, title_png, scheme, None)
        _render(cta_headline, str(cfg["cta_sub"]).strip(), _REEL_SIZE, end_png,
                scheme, None)
        _render_stage(stage_png, scheme)

        card = f"setsar=1,fps={_FPS},format=yuv420p"
        cut = _cut_filter(crop, beats) if beats else f"[1:v]{crop}[cut];"
        graph = (
            f"[0:v]{card}[title];"
            + cut +
            f"[cut]setpts=PTS/{speed:.4f},"
            f"scale={box_w}:{box_h}:force_original_aspect_ratio=decrease:"
            f"force_divisible_by=2,fps={_FPS}[vid];"
            f"[3:v]{card}[stage];"
            f"[stage][vid]overlay=(W-w)/2:(H-h)/2:shortest=1,{card}[main];"
            f"[2:v]{card}[end];"
            f"[title][main][end]concat=n=3:v=1:a=0[out]"
        )
        cmd = [
            "ffmpeg", "-y", "-v", "error",
            "-loop", "1", "-t", str(cfg["title_seconds"]), "-i", str(title_png),
            "-i", str(raw),
            "-loop", "1", "-t", str(cfg["end_seconds"]), "-i", str(end_png),
            "-loop", "1", "-i", str(stage_png),
            "-filter_complex", graph, "-map", "[out]", "-an",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-movflags", "+faststart", str(out_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg failed: {result.stderr.strip()[-400:]}")

    video_platforms = [
        name for name, desc in platforms.registry().items()
        if desc["media"] in ("video", "both")
    ]
    return {
        "type": "video",
        "path": str(out_path),
        "aspect": "story",
        "platform_targets": video_platforms,
        "status": "ready",
    }
