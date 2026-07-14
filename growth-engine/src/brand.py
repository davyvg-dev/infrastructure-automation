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


def font_path(bold: bool = False) -> Path:
    return brand()["font_bold" if bold else "font_regular"]
