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
        "pop_cuts": True,       # cut typing/waiting entirely: keep only the moments
                                # around screen changes, so messages pop in back-to-back
        "scene_threshold": 0.08,  # how big a frame change counts as "something happened"
        "dwell_seconds": 1.4,   # max hold on each pop before jumping to the next
        "title_seconds": 1.8,
        "end_seconds": 2.4,
        "cta_headline": "",     # end-card text; falls back to brand footer
        "cta_sub": "",
    }
    values.update((strategy().get("media") or {}).get("reel") or {})
    return values


def font_path(bold: bool = False) -> Path:
    return brand()["font_bold" if bold else "font_regular"]
