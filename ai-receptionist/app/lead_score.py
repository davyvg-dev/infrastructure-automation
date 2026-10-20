"""Lead temperature scoring for the real-estate vertical — pure functions, no I/O.

Rules v1 (founder-approved 2026-08-09):
- seller with a valuation booked                      -> hot
- timeline 0-3 months AND concrete criteria           -> hot
- timeline 0-3 months without concrete criteria       -> warm
- timeline 3-12 months                                -> warm
- existing client (service request, not a sales lead) -> warm
- 12+ months, just browsing, or no timeline given     -> nurture

Concrete criteria: buyer/renter = at least one location AND a budget ceiling;
seller = a property address. Unknown or malformed inputs always degrade toward
nurture, never toward hot — an inflated temperature pages a human for nothing.
"""

from __future__ import annotations

from typing import Any

TEMPERATURES = ("hot", "warm", "nurture")

INTENTS = ("buyer", "seller", "renter", "existing")

# Timeline buckets the register_buyer_lead tool schema enumerates.
TIMELINES = ("0-3", "3-12", "12+", "browsing")


def resolve_intent(criteria: dict[str, Any]) -> str:
    """The lead's intent; falls back on the search operation when not stated."""
    intent = str(criteria.get("intent") or "").strip().lower()
    if intent in INTENTS:
        return intent
    operation = str(criteria.get("operation") or "").strip().lower()
    return {"sale": "buyer", "rent": "renter"}.get(operation, "buyer")


def _concrete(intent: str, criteria: dict[str, Any]) -> bool:
    if intent == "seller":
        return bool(criteria.get("property_address"))
    return bool(criteria.get("locations")) and bool(criteria.get("max_price"))


def temperature(criteria: dict[str, Any]) -> str:
    """Score a lead's criteria dict to 'hot' | 'warm' | 'nurture'."""
    intent = resolve_intent(criteria)
    if intent == "existing":
        return "warm"
    if intent == "seller" and criteria.get("valuation_booked"):
        return "hot"
    timeline = str(criteria.get("timeline") or "").strip()
    if timeline == "0-3":
        return "hot" if _concrete(intent, criteria) else "warm"
    if timeline == "3-12":
        return "warm"
    return "nurture"
