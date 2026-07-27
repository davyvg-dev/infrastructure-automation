"""Scripted chat-demo footage — renders a config scenario as reel-ready frames.

The elegant inverse of detection: instead of reverse-engineering events out of a
screen recording (thresholds, crops, scene scores), the demo is DRAWN frame by
frame from a scenario in config, on the final edited timeline — typing at a
readable pace, replies landing instantly, one suspense beat before the payoff.
Every keystroke, message pop and payoff ding is placed on the same 30fps frame
grid the video is built on, so audio/video sync is exact by construction.

One job: scenario -> (frame sequence dir, sound events, duration). The branded
stage, overlays and soundtrack stay in media.py; scenario text lives in config
(`media.reel.demo`) — Dutch, customer-facing, founder-editable. The rendered UI
is the product's own web-widget look (brand colors, "digitale assistent" in the
header per the disclosure rule), not a clone of any messenger app.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from . import brand

FPS = 30
_CHAR_FRAMES = 2        # one typed character every 2 frames (~15 chars/s on screen)
_SEND_FRAMES = 4        # beat between the last keystroke and the message popping
_MIN_DWELL = 18         # a message never holds shorter than this (0.6s)
_COLD_FRAMES = 34       # cold open: 4 pre-pop frames + 1s of the payoff on screen
_HEAD_H = 150           # chat header band height

# Widget palette — the product's web-chat look on brand tokens.
_BG = "#F1ECDF"
_INK = "#1A1A1A"
_CREAM = "#FAF6EE"
_BLUE = "#0F4C81"
_MUTED = "#A79F8E"
_LINE = "#DED7C6"


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont,
          max_width: int) -> list[str]:
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


class _Painter:
    """Renders one chat state to an image; caches by state so only unique frames
    cost a Pillow render — repeats become hard links in the sequence."""

    def __init__(self, size: tuple[int, int], business: str,
                 turns: list[dict[str, str]], tmp: Path):
        self.w, self.h = size
        self.business = business
        self.turns = turns
        self.font = ImageFont.truetype(str(brand.font_path()), 40)
        self.font_bold = ImageFont.truetype(str(brand.font_path(bold=True)), 44)
        self.font_small = ImageFont.truetype(str(brand.font_path()), 28)
        self.name_font = self._fit_name(business)
        b = brand.brand()
        self.accent = b["accent"]
        self.cache_dir = tmp / "cache"
        self.seq_dir = tmp / "seq"
        self.cache_dir.mkdir(parents=True)
        self.seq_dir.mkdir(parents=True)
        self.cache: dict[tuple, Path] = {}
        self.n = 0
        self.bubbles = [self._bubble(t) for t in turns]

    def _fit_name(self, business: str) -> ImageFont.FreeTypeFont:
        """Header name font, shrunk so a long business name fits beside the avatar
        (the text column runs from x=128 to a 24px right margin)."""
        probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        name_max = self.w - 128 - 24
        for size in (44, 40, 36, 32, 28):
            font = ImageFont.truetype(str(brand.font_path(bold=True)), size)
            if probe.textlength(business, font=font) <= name_max:
                return font
        return ImageFont.truetype(str(brand.font_path(bold=True)), 28)

    def _bubble(self, turn: dict[str, str]) -> Image.Image:
        probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        lines = _wrap(probe, turn["text"], self.font, 440)
        tw = max(probe.textlength(ln, font=self.font) for ln in lines)
        bw, bh = int(tw) + 52, len(lines) * 52 + 40
        img = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        ai = turn["from"] == "ai"
        d.rounded_rectangle((0, 0, bw - 1, bh - 1), radius=24,
                            fill="#FFFFFF" if ai else _BLUE,
                            outline=_LINE if ai else None)
        y = 20
        for ln in lines:
            d.text((26, y), ln, font=self.font, fill=_INK if ai else _CREAM)
            y += 52
        return img

    def _paint(self, msgs: int, typed: str, indicator: int) -> Image.Image:
        img = Image.new("RGB", (self.w, self.h), _BG)
        d = ImageDraw.Draw(img)
        # Header: avatar + business name + the standing "digitale assistent"
        # disclosure. Business identity only — the widget's own header, like a
        # real chat. The klantkraan.nl brand rides the "powered by" footer at the
        # bottom (media._render_footer), never crammed next to the disclosure.
        d.rectangle((0, 0, self.w, _HEAD_H), fill=_BLUE)
        av = 76
        ax, ay = 28, (_HEAD_H - av) // 2
        d.ellipse((ax, ay, ax + av, ay + av), fill="#4D80AD")
        initial = (self.business or "K")[0].upper()
        d.text((ax + av / 2, ay + av / 2 - 2), initial, font=self.font_bold,
               fill=_CREAM, anchor="mm")

        tx = ax + av + 24  # text column, right of the avatar
        name_asc, name_desc = self.name_font.getmetrics()
        stat_asc = self.font_small.getmetrics()[0]
        gap = 8
        top = (_HEAD_H - (name_asc + name_desc + gap + stat_asc)) // 2
        d.text((tx, top), self.business, font=self.name_font, fill=_CREAM)

        sy = top + name_asc + name_desc + gap  # status row, below the name
        dot = 15
        cy = sy + stat_asc * 0.58  # dot centered on the lowercase status text
        d.ellipse((tx, cy - dot / 2, tx + dot, cy + dot / 2), fill="#8FD49A")
        d.text((tx + dot + 14, sy), "digitale assistent • online",
               font=self.font_small, fill="#BCD2E4")
        # Input bar, above it the bubble stack (newest at the bottom).
        bar_top = self.h - 124
        d.rounded_rectangle((24, bar_top, self.w - 118, self.h - 40), radius=40,
                            fill="#FFFFFF", outline=_LINE)
        d.ellipse((self.w - 104, bar_top, self.w - 24, bar_top + 80),
                  fill=self.accent)
        d.polygon([(self.w - 80, bar_top + 26), (self.w - 44, bar_top + 40),
                   (self.w - 80, bar_top + 54)], fill=_CREAM)
        if typed:
            shown = typed
            while d.textlength(shown, font=self.font) > self.w - 118 - 24 - 76:
                shown = shown[1:]  # keep the tail visible, like a real input
            d.text((52, bar_top + 18), shown, font=self.font, fill=_INK)
            cx = 52 + d.textlength(shown, font=self.font) + 6
            d.rectangle((cx, bar_top + 16, cx + 4, bar_top + 62), fill=self.accent)
        else:
            d.text((52, bar_top + 18), "Typ een bericht…", font=self.font,
                   fill=_MUTED)
        y = bar_top - 28
        if indicator >= 0:
            d.rounded_rectangle((24, y - 72, 156, y), radius=24, fill="#FFFFFF",
                                outline=_LINE)
            for i in range(3):
                c = "#5A5A5A" if i == indicator else "#C9C2B2"
                d.ellipse((48 + i * 30, y - 44, 64 + i * 30, y - 28), fill=c)
            y -= 92
        for i in range(msgs - 1, -1, -1):
            b = self.bubbles[i]
            y -= b.height
            if y < _HEAD_H + 32:
                break  # older messages scroll off behind the header
            x = 24 if self.turns[i]["from"] == "ai" else self.w - b.width - 24
            img.paste(b, (x, y), b)
            y -= 20
        return img

    def emit(self, msgs: int, typed: str, indicator: int, frames: int) -> None:
        """Append `frames` copies of this state to the sequence."""
        key = (msgs, typed, indicator)
        path = self.cache.get(key)
        if path is None:
            path = self.cache_dir / f"{len(self.cache):04d}.png"
            self._paint(msgs, typed, indicator).save(path, "PNG")
            self.cache[key] = path
        for _ in range(frames):
            os.link(path, self.seq_dir / f"{self.n:05d}.png")
            self.n += 1


def _dwell(text: str, cap: int) -> int:
    """Frames a message holds: reading time for 35-55 eyes, capped by config."""
    return max(_MIN_DWELL, min(int((0.55 + 0.032 * len(text)) * FPS), cap))


def render(scenario: list[dict[str, str]], business: str, greeting: str,
           tmp: Path, size: tuple[int, int], cfg: dict[str, Any]
           ) -> tuple[Path, list[tuple[float, str]], float]:
    """Scenario -> (frame-sequence dir, (time, sfx) events, duration in seconds).

    Timeline: cold open on the payoff message, then replay — the widget's
    `greeting` bubble (the digital-assistant disclosure) is already on screen,
    customer messages are typed out (tick per character), replies pop instantly
    (pop per message), one suspense beat of the typing indicator survives before
    the payoff (ding). Budget-fits `target_seconds` by shrinking dwells, then
    typing pace, exactly like the recorded-footage cut plan would.
    """
    turns = [{"from": str(t.get("from", "")), "text": str(t.get("text", "")).strip()}
             for t in scenario]
    if not turns or any(t["from"] not in ("klant", "ai") or not t["text"]
                        for t in turns):
        raise ValueError("demo scenario turns need from: klant|ai and a text")
    if turns[-1]["from"] != "ai":
        raise ValueError("demo scenario must end with an ai turn (the payoff)")
    base = 1 if greeting.strip() else 0
    if base:  # the widget greeted before the demo starts — on screen throughout
        turns.insert(0, {"from": "ai", "text": greeting.strip()})

    played = turns[base:]  # the greeting is scenery, never typed or popped

    dwell_cap = max(int(float(cfg["dwell_seconds"]) * FPS), _MIN_DWELL)
    suspense = int(float(cfg["suspense_seconds"]) * FPS)
    budget = int((float(cfg["target_seconds"]) - float(cfg["cta_seconds"])) * FPS)

    def plan(char_frames: int, dwells: list[int]) -> int:
        total = _COLD_FRAMES + suspense
        for turn, dw in zip(played, dwells, strict=False):
            if turn["from"] == "klant":
                total += len(turn["text"]) * char_frames + _SEND_FRAMES
            total += dw
        return total + 12  # payoff lingers a little longer

    dwells = [_dwell(t["text"], dwell_cap) for t in played]
    char_frames = _CHAR_FRAMES
    if plan(char_frames, dwells) > budget:  # shrink dwells toward the floor first
        over = plan(char_frames, dwells) - budget
        room = sum(dw - _MIN_DWELL for dw in dwells)
        scale = max(1.0 - over / room, 0.0) if room else 0.0
        dwells = [max(_MIN_DWELL, int(_MIN_DWELL + (dw - _MIN_DWELL) * scale))
                  for dw in dwells]
    if plan(char_frames, dwells) > budget:
        char_frames = 1  # then type faster; config scenarios should stay short

    p = _Painter(size, business, turns, tmp)
    events: list[tuple[float, str]] = []

    def sound(name: str) -> None:
        events.append((p.n / FPS, name))

    # Cold open: the payoff pops within the first beats, then holds — the loop
    # back from the CTA freeze to this open is why the reel rewatches well.
    p.emit(len(turns) - 1, "", -1, 4)
    sound("pop")
    p.emit(len(turns), "", -1, _COLD_FRAMES - 4)
    for i, (turn, dw) in enumerate(zip(played, dwells, strict=False)):
        shown = base + i  # bubbles on screen before this turn lands
        final = i == len(played) - 1
        if turn["from"] == "klant":
            for j in range(len(turn["text"])):
                sound("tick")
                p.emit(shown, turn["text"][:j + 1], -1, char_frames)
            p.emit(shown, turn["text"], -1, _SEND_FRAMES)
        if final:
            for phase in range(3):  # one "..." beat of real waiting
                p.emit(shown, "", phase, max(suspense // 3, 1))
        sound("ding" if final else "pop")
        p.emit(shown + 1, "", -1, dw + (12 if final else 0))

    return p.seq_dir, events, p.n / FPS
