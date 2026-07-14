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
# Platform UI covers the frame edges: captions/buttons eat the bottom ~670px on the
# worst platform (Facebook) and ~250px at the top. All TEXT stays inside this band;
# the demo footage itself may run larger.
_SAFE_TOP = 250
_SAFE_BOTTOM = 670
_VID_H = 1560  # demo footage height on the 1920 canvas — near full-bleed phone


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


def _render_stage(out_path: Path, scheme: dict[str, Any],
                  hole: tuple[int, int]) -> None:
    """Frame laid OVER the demo footage: brand surround with a rounded phone window
    (thin accent bezel, no logo lockups) and the footer URL pinned in the safe zone."""
    b = brand.brand()
    img = Image.new("RGBA", _REEL_SIZE, scheme["bg"])
    hw, hh = hole
    x0, y0 = (_REEL_SIZE[0] - hw) // 2, (_REEL_SIZE[1] - hh) // 2
    box = (x0, y0, x0 + hw, y0 + hh)
    mask = Image.new("L", _REEL_SIZE, 255)
    ImageDraw.Draw(mask).rounded_rectangle(box, radius=44, fill=0)
    img.putalpha(mask)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(box, radius=44, outline=scheme["accent"], width=4)
    if b["footer"]:
        font = ImageFont.truetype(str(b["font_bold"]), 40)
        tw = draw.textlength(b["footer"], font=font)
        bx = (_REEL_SIZE[0] - tw) / 2
        by = _REEL_SIZE[1] - _SAFE_BOTTOM - 84  # above the platform caption zone
        draw.rounded_rectangle((bx - 22, by - 14, bx + tw + 22, by + 54),
                               radius=14, fill=(10, 10, 10, 200))
        draw.text((bx, by), b["footer"], font=font, fill="#FAF6EE")
    img.save(out_path, "PNG")


def _render_overlay(headline: str, sub: str, y_top: int, out_path: Path) -> None:
    """Text on a translucent scrim, overlaid on moving footage (hook / end CTA).

    Sized for 35-55 eyes on a phone: ≥44px, ≤3 lines, high contrast; the box stays
    inside the platform-safe band and clear of the right-hand icon rail."""
    b = brand.brand()
    img = Image.new("RGBA", _REEL_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    max_w = 748
    size = 64
    while True:
        font = ImageFont.truetype(str(b["font_bold"]), size)
        lines = _wrap(draw, headline, font, max_w)
        if len(lines) <= 3 or size <= 44:
            break
        size -= 4
    step = int(size * 1.3)
    sub_font = ImageFont.truetype(str(b["font_bold"]), 44)
    pad = 36
    widths = [draw.textlength(ln, font=font) for ln in lines]
    if sub:
        widths.append(draw.textlength(sub, font=sub_font))
    bw = max(widths) + 2 * pad
    bh = pad + len(lines) * step + (66 if sub else 0) + pad - (step - size)
    x0 = (_REEL_SIZE[0] - bw) / 2
    draw.rounded_rectangle((x0, y_top, x0 + bw, y_top + bh), radius=20,
                           fill=(10, 10, 10, 205))
    y = y_top + pad
    for ln in lines:
        lw = draw.textlength(ln, font=font)
        draw.text(((_REEL_SIZE[0] - lw) / 2, y), ln, font=font, fill="#FAF6EE")
        y += step
    if sub:
        lw = draw.textlength(sub, font=sub_font)
        draw.text(((_REEL_SIZE[0] - lw) / 2, y + 8), sub, font=sub_font,
                  fill="#FAF6EE")
    img.save(out_path, "PNG")


def _frame_scores(raw: Path, crop: str) -> list[tuple[float, float]]:
    """(time, scene_score) for every frame of the (cropped) recording.

    The score measures how much a frame differs from the previous one: a message
    popping in scores high, a keystroke scores low but nonzero, a typing indicator
    or the status-bar clock stays near zero.
    """
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-v", "info", "-i", str(raw),
         "-vf", f"{crop},select='gte(scene,0)',"
                "metadata=mode=print:key=lavfi.scene_score",
         "-f", "null", "-"],
        capture_output=True, text=True, timeout=180,
    )
    frames: list[tuple[float, float]] = []
    t: float | None = None
    for line in result.stderr.splitlines():
        m = re.search(r"pts_time:([0-9]+\.?[0-9]*)", line)
        if m:
            t = float(m.group(1))
            continue
        m = re.search(r"lavfi\.scene_score=([0-9.eE+-]+)", line)
        if m and t is not None:
            frames.append((t, float(m.group(1))))
            t = None
    return frames


def _subtract(run: tuple[float, float],
              holds: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Pieces of `run` not covered by any hold."""
    pieces = [run]
    for hs, he in holds:
        nxt = []
        for s, e in pieces:
            if he <= s or hs >= e:
                nxt.append((s, e))
                continue
            if s < hs:
                nxt.append((s, hs))
            if he < e:
                nxt.append((he, e))
        pieces = nxt
    return [(s, e) for s, e in pieces if e - s > 0.1]


def _cut_plan(frames: list[tuple[float, float]], duration: float,
              cfg: dict[str, Any], usable: float
              ) -> list[tuple[float, float, float]] | None:
    """(start, end, speed) segments: pops hold at 1×, typing runs fast, idle is cut.

    A pop (big change — a message appearing) holds `dwell` so it can be read; the
    reply therefore lands on screen instantly, with the wait before it gone. Typing
    (small but real activity) stays visible at `typing_speed`. Everything else —
    typing indicators, dead waiting — never makes the cut.
    """
    pop_thr = float(cfg["scene_threshold"])
    typ_thr = float(cfg["typing_threshold"])
    pops = [t for t, s in frames if s >= pop_thr]
    typing = [t for t, s in frames if typ_thr <= s < pop_thr]
    if not pops and not typing:
        return None

    starts = [0.0]
    for t in sorted(pops):
        if t - starts[-1] >= 0.25:  # double-triggers within one pop animation
            starts.append(max(t - 0.05, 0.0))
    dwell = max(0.5, min(float(cfg["dwell_seconds"]), usable / len(starts)))
    holds: list[tuple[float, float]] = []
    for s in starts:
        e = min(s + dwell, duration)
        if holds and s <= holds[-1][1] + 0.05:
            holds[-1] = (holds[-1][0], max(holds[-1][1], e))
        else:
            holds.append((s, e))

    # Typing runs: nearby keystrokes coalesce; holds win where the two overlap.
    runs: list[tuple[float, float]] = []
    for t in typing:
        if runs and t - runs[-1][1] <= 0.6:
            runs[-1] = (runs[-1][0], t)
        else:
            runs.append((t, t))
    speed = float(cfg["typing_speed"])
    segs = [(s, e, 1.0) for s, e in holds]
    for run in runs:
        if run[1] - run[0] < 0.2:  # single-frame blips are noise, not typing
            continue
        segs.extend((s, e, speed) for s, e in _subtract(run, holds))
    return sorted(segs)


def _slice_args(raw: Path, segs: list[tuple[float, float, float]],
                crop: str, first_idx: int) -> tuple[list[str], str]:
    """One seeked input per segment (may play out of source order — cold open).

    Input-level -ss/-t decodes only each segment's window; a single decode fanned
    out with split+trim deadlocks when concat drains the branches out of order.
    """
    args: list[str] = []
    parts: list[str] = []
    for i, (s, e, v) in enumerate(segs):
        args += ["-ss", f"{s:.3f}", "-t", f"{e - s:.3f}", "-i", str(raw)]
        parts.append(
            f"[{first_idx + i}:v]{crop},setpts=(PTS-STARTPTS)/{v:.2f}[t{i}];"
        )
    parts.append("".join(f"[t{i}]" for i in range(len(segs)))
                 + f"concat=n={len(segs)}:v=1:a=0[cut];")
    return args, "".join(parts)


def build_reel(raw: Path, stem: str, headline: str, sub: str = "",
               beats: list[tuple[float, float]] | None = None,
               out_dir: Path | None = None) -> dict[str, Any]:
    """Cut a raw screen recording into a branded 1080×1920 reel; returns a media record.

    With `pop_cuts` (default) each frame is classified by how much the screen changes:
    a message appearing holds at natural speed so it can be read, typing stays visible
    but fast (`typing_speed`), and dead time — typing indicators, waiting on the reply —
    is cut entirely, so responses land instantly. A cold open replays the payoff
    message first, one suspense beat of real waiting survives before the final reply,
    the hook text rides the opening footage (no static title card), and the CTA rides
    a freeze of the last frame so the loop back to the hook is seamless. Total stays
    under `target_seconds`. Explicit `beats` (start, end) override the detection; if
    no activity is detected the whole clip is sped up instead. Audio is dropped —
    screen recordings are silent and IG/TikTok music is added in-app.
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
    # Budget for the demo footage: the CTA rides a freeze of the last frame, so it
    # is the only non-demo time in the cap.
    usable = max(float(cfg["target_seconds"]) - float(cfg["cta_seconds"]), 3.0)
    plan = [(s, e, 1.0) for s, e in beats] if beats else None
    if plan is None and cfg["pop_cuts"]:
        plan = _cut_plan(_frame_scores(raw, crop), duration, cfg, usable)
    if plan:
        holds = [i for i, seg in enumerate(plan) if seg[2] == 1.0]
        if holds:
            last_s, last_e, _ = plan[holds[-1]]
            # One "..." beat of real waiting survives, right before the payoff.
            beat = float(cfg["suspense_seconds"])
            if beat > 0 and last_s > beat:
                plan.insert(holds[-1], (last_s - beat, last_s, 1.0))
            # Cold open: show the payoff first, then replay the chat as an open loop.
            if cfg["cold_open"]:
                plan.insert(0, (last_s, min(last_s + 1.0, last_e), 1.0))
    # Output seconds the plan produces; a residual uniform speed-up covers the rest.
    kept = sum((e - s) / v for s, e, v in plan) if plan else duration
    speed = min(max(kept / usable, 1.0), float(cfg["max_speed"]))
    out_dur = kept / speed

    # The demo footage runs near full-bleed; scaled width follows the source aspect.
    src_h = height - crop_top - crop_bottom
    vid_w = int(width * _VID_H / src_h) // 2 * 2

    schemes = brand.schemes()
    scheme = schemes[_pick(stem, len(schemes))]  # same scheme as the draft's card
    b = brand.brand()
    cta_headline = str(cfg["cta_headline"]).strip() or b["footer"] or headline
    with tempfile.TemporaryDirectory() as tmp:
        stage_png, hook_png, cta_png = (Path(tmp) / n for n in
                                        ("stage.png", "hook.png", "cta.png"))
        _render_stage(stage_png, scheme, (vid_w, _VID_H))
        _render_overlay(headline, "", _SAFE_TOP, hook_png)
        _render_overlay(cta_headline, str(cfg["cta_sub"]).strip(), 640, cta_png)

        bg = str(scheme["bg"]).replace("#", "0x")
        if plan:
            slice_args, cut = _slice_args(raw, plan, crop, first_idx=1)
            n_vid = len(plan)
        else:
            slice_args, cut, n_vid = ["-i", str(raw)], f"[1:v]{crop}[cut];", 1
        hook_idx, cta_idx = n_vid + 1, n_vid + 2
        graph = (
            cut +
            f"[cut]setpts=PTS/{speed:.4f},scale={vid_w}:{_VID_H},fps={_FPS},"
            f"pad={_REEL_SIZE[0]}:{_REEL_SIZE[1]}:(ow-iw)/2:(oh-ih)/2:color={bg},"
            f"tpad=stop_mode=clone:stop_duration={float(cfg['cta_seconds']):.2f}"
            f"[base];"
            # shortest=1 everywhere: the looped PNGs are endless, the video chain
            # (base, tpad included) is what bounds the reel — without it the
            # graph runs forever.
            f"[base][0:v]overlay=0:0:shortest=1[framed];"
            f"[framed][{hook_idx}:v]overlay=0:0:shortest=1:"
            f"enable='lt(t,{float(cfg['hook_seconds']):.2f})'[hooked];"
            f"[hooked][{cta_idx}:v]overlay=0:0:shortest=1:"
            f"enable='gte(t,{out_dur:.2f})',"
            f"setsar=1,fps={_FPS},format=yuv420p[out]"
        )
        cmd = [
            "ffmpeg", "-y", "-v", "error",
            "-loop", "1", "-i", str(stage_png),
            *slice_args,
            "-loop", "1", "-i", str(hook_png),
            "-loop", "1", "-i", str(cta_png),
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
