"""Brand values for generated media — colors, fonts, footer from config `media.brand`.

Pure config access + validation; the actual rendering lives in media.py. Fonts are
bundled in assets/fonts/ (the VPS has no system Inter/Arial/Helvetica).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .settings import ROOT, strategy

_DEFAULTS = {
    "bg": "#0F4C81",        # kraan-blue
    "text": "#FAF6EE",      # kraan-cream
    "accent": "#C75A2B",    # kraan-rust
    "muted": "#4D80AD",     # kraan-blue-300
    "footer": "",
    "font_bold": "assets/fonts/Inter-Bold.ttf",
    "font_regular": "assets/fonts/Inter-Regular.ttf",
}


def cards_enabled() -> bool:
    return bool((strategy().get("media") or {}).get("cards", False))


def brand() -> dict[str, Any]:
    """Config `media.brand` merged over defaults, font paths resolved and checked."""
    values = {**_DEFAULTS, **((strategy().get("media") or {}).get("brand") or {})}
    for key in ("font_bold", "font_regular"):
        path = ROOT / values[key]
        if not path.exists():
            raise FileNotFoundError(f"media.brand.{key}: {path} does not exist")
        values[key] = path
    return values


def schemes() -> list[dict[str, Any]]:
    """Color schemes to rotate across cards (feed variety). Each scheme inherits any
    missing color from the top-level brand block, so old configs keep working."""
    b = brand()
    base = {k: b[k] for k in ("bg", "text", "accent", "muted")}
    raw = b.get("schemes") or [{}]
    return [{**base, **scheme} for scheme in raw]


def stock() -> dict[str, Any]:
    """Config `media.stock` — stock-photo cards (Pexels). Off unless enabled."""
    values = {"enabled": False, "every": 3}
    values.update((strategy().get("media") or {}).get("stock") or {})
    return values


def reel() -> dict[str, Any]:
    """Config `media.reel` — screen-recording → branded reel. Off unless enabled.

    Crop values are fractions of the source height (robust to Telegram re-encodes,
    which change pixel dimensions but not proportions)."""
    values = {
        "enabled": False,
        "crop_top": 0.0,        # iOS status bar — device-specific, tune once
        "crop_bottom": 0.0,     # home indicator, usually fine to keep
        "target_seconds": 15,   # max length of the FINISHED reel, cards included
        "max_speed": 4.0,       # never faster than this (unreadable beyond it)
        "pop_cuts": True,       # classify every frame: message pops hold at 1×, typing
                                # plays fast, waiting (typing dots, dead air) is cut
        "scene_threshold": 0.08,  # CEILING for "a message appeared"; the working
                                  # threshold adapts to each clip (6% of its biggest
                                  # frame change), so this only caps runaway clips
        "typing_threshold": 0.0006,  # keystroke floor, measured in the keyboard band
        "keys_band": 0.45,      # bottom fraction of the frame where typing happens
                                # (keyboard + input bar); changes concentrated here
                                # are keystrokes, changes above it are not
        "typing_speed": 3.0,    # typing stays visible, just this much faster
        "dwell_seconds": 1.4,   # max hold on each pop before jumping to the next
        "cold_open": True,      # open on the payoff message, then replay the chat
        "suspense_seconds": 0.6,  # one "..." beat of real waiting before the payoff
        "hook_seconds": 2.5,    # hook text rides the opening footage — no title card
        "cta_seconds": 1.0,     # CTA rides a freeze of the last frame — no end card
        "cta_headline": "",     # CTA text; falls back to brand footer
        "cta_sub": "",
    }
    audio_defaults = {
        "enabled": True,        # baked-in sound design (silent reels feel broken)
        "sfx": True,            # pops on messages, ticks while typing, ding on payoff
        "bed": "",              # founder-supplied licensed/CC0 ambient file; "" = none.
                                # NEVER commercial music — that stays in-app (REELS.md)
        "bed_gain_db": -24.0,   # bed sits far under the SFX
    }
    demo_defaults = {
        "enabled": False,       # scripted chat-demo reels: drawn from `scenarios`,
                                # perfectly synced by construction — no recording,
                                # no detection; the 🎬 upload stays as the override
        "business": "Demo",     # fictional business name in the demo chat header
        "greeting": "",         # widget greeting already on screen at the start —
                                # the natural home for the assistant disclosure
        "scenarios": [],        # list of conversations: [{from: klant|ai, text}]
    }
    values.update((strategy().get("media") or {}).get("reel") or {})
    # Nested merge so a partial (or absent) audio block keeps the other defaults.
    values["audio"] = {**audio_defaults, **(values.get("audio") or {})}
    values["demo"] = {**demo_defaults, **(values.get("demo") or {})}
    return values


def font_path(bold: bool = False) -> Path:
    return brand()["font_bold" if bold else "font_regular"]
