"""The platform registry — the one config-driven source for per-platform facts.

Reads the `platforms:` block of content_strategy.yaml and hands the rest of the code
normalized descriptors (label, delivery, char_limit, writing guidance, media rules),
so no module hardcodes a platform list again. Adding a platform = editing config.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from .settings import strategy

# auto = post via API on approval · buffer = queue via Buffer, its schedule decides
# when · assisted = hand text over to paste · draft = upload media via API, founder
# finishes in-app (TikTok inbox flow)
_DELIVERIES = ("auto", "buffer", "assisted", "draft")
_MEDIA = ("none", "image", "video", "both")


@lru_cache(maxsize=1)
def registry() -> dict[str, dict[str, Any]]:
    """Enabled platforms only, in config order, defaults filled in and validated."""
    raw = strategy().get("platforms") or {}
    reg: dict[str, dict[str, Any]] = {}
    for name, cfg in raw.items():
        if not cfg.get("enabled", False):
            continue
        desc = dict(cfg)
        desc.setdefault("media", "none")
        desc.setdefault("media_required", False)
        desc.setdefault("char_limit", None)
        if desc.get("delivery") not in _DELIVERIES:
            raise ValueError(
                f"platform '{name}': delivery must be one of {_DELIVERIES}, "
                f"got {desc.get('delivery')!r}"
            )
        if desc["media"] not in _MEDIA:
            raise ValueError(
                f"platform '{name}': media must be one of {_MEDIA}, got {desc['media']!r}"
            )
        reg[name] = desc
    return reg


def enabled_platforms() -> list[str]:
    return list(registry())


def auto_platforms() -> list[str]:
    return [n for n, d in registry().items() if d["delivery"] == "auto"]


def buffer_platforms() -> list[str]:
    return [n for n, d in registry().items() if d["delivery"] == "buffer"]


def assisted_platforms() -> list[str]:
    return [n for n, d in registry().items() if d["delivery"] == "assisted"]


def draft_platforms() -> list[str]:
    return [n for n, d in registry().items() if d["delivery"] == "draft"]


def spec(name: str) -> dict[str, Any]:
    reg = registry()
    if name not in reg:
        raise KeyError(f"unknown or disabled platform '{name}' (enabled: {', '.join(reg)})")
    return reg[name]
