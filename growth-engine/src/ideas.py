"""Pillar rotation + idea generation.

Picks the next pillar using weighted rotation (so aggressive volume stays varied), then
asks Claude for a fresh, specific topic within that pillar — avoiding recent repeats.
"""

from __future__ import annotations

import itertools
from typing import Any

from . import store
from .settings import strategy


def _weighted_pillar_cycle() -> list[str]:
    """Expand pillars by weight into a deterministic rotation list."""
    order: list[str] = []
    for p in strategy()["pillars"]:
        order.extend([p["key"]] * int(p.get("weight", 1)))
    return order


def next_pillar() -> dict[str, Any]:
    """Return the next pillar config, advancing a persistent cursor."""
    cycle = _weighted_pillar_cycle()
    cursor = int(store.get_state("pillar_cursor", 0)) % len(cycle)
    key = cycle[cursor]
    store.set_state("pillar_cursor", (cursor + 1) % len(cycle))
    return next(p for p in strategy()["pillars"] if p["key"] == key)


def recent_topics(limit: int = 30) -> list[str]:
    """Recent topics so the drafting engine doesn't repeat itself."""
    topics = [d.get("topic", "") for d in store.load_queue() if d.get("topic")]
    return list(itertools.islice(reversed(topics), limit))
