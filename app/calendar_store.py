"""A simulated calendar: generates bookable slots from opening hours and records bookings.

Deliberately simple (a JSON file) so the demo runs with zero external setup. The functions
here are the seam where you'd later plug in Google Calendar / Cal.com for a real client —
swap the bodies, keep the signatures.
"""

from __future__ import annotations

import json
import threading
import uuid
from datetime import date, datetime, timedelta
from typing import Any

from .settings import DATA_DIR, business, ensure_dirs

_BOOKINGS_PATH = DATA_DIR / "bookings.json"
_lock = threading.Lock()

_WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def _load() -> list[dict[str, Any]]:
    if not _BOOKINGS_PATH.exists():
        return []
    with _BOOKINGS_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


def _save(bookings: list[dict[str, Any]]) -> None:
    ensure_dirs()
    tmp = _BOOKINGS_PATH.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(bookings, fh, ensure_ascii=False, indent=2)
    tmp.replace(_BOOKINGS_PATH)


def _slots_for_day(day: date) -> list[str]:
    cfg = business()
    hours = cfg["hours"].get(_WEEKDAYS[day.weekday()])
    if not hours:
        return []  # closed
    open_t = datetime.strptime(hours[0], "%H:%M").time()
    close_t = datetime.strptime(hours[1], "%H:%M").time()
    step = int(cfg["booking"]["slot_minutes"])
    cur = datetime.combine(day, open_t)
    end = datetime.combine(day, close_t)
    out = []
    while cur + timedelta(minutes=step) <= end:
        out.append(cur.strftime("%Y-%m-%d %H:%M"))
        cur += timedelta(minutes=step)
    return out


def _booked_slots() -> set[str]:
    return {b["slot"] for b in _load()}


def availability(on_date: str | None = None, days: int = 5) -> dict[str, Any]:
    """Return open slots. If on_date ('YYYY-MM-DD') is given, just that day; else next `days`
    open days within the booking horizon."""
    cfg = business()
    horizon = int(cfg["booking"]["horizon_days"])
    booked = _booked_slots()

    def free(day: date) -> list[str]:
        return [s for s in _slots_for_day(day) if s not in booked]

    if on_date:
        try:
            day = datetime.strptime(on_date, "%Y-%m-%d").date()
        except ValueError:
            return {"error": f"Could not parse date '{on_date}'. Use YYYY-MM-DD."}
        return {"date": on_date, "open_slots": free(day)}

    today = date.today()
    result: dict[str, list[str]] = {}
    checked = 0
    while len(result) < days and checked < horizon:
        day = today + timedelta(days=checked)
        checked += 1
        slots = free(day)
        if slots:
            result[day.isoformat()] = slots
    return {"open_days": result}


def book(customer_name: str, contact: str, service: str, slot: str) -> dict[str, Any]:
    """Book a slot if it's still open. Returns a confirmation or an error."""
    with _lock:
        bookings = _load()
        if any(b["slot"] == slot for b in bookings):
            return {"ok": False, "error": "That slot was just taken. Please pick another."}
        # Validate the slot is a real, open slot for its day.
        try:
            day = datetime.strptime(slot, "%Y-%m-%d %H:%M").date()
        except ValueError:
            return {"ok": False, "error": f"Invalid slot '{slot}'. Use 'YYYY-MM-DD HH:MM'."}
        if slot not in _slots_for_day(day):
            return {"ok": False, "error": "That time isn't a bookable slot."}
        confirmation = f"BK-{uuid.uuid4().hex[:6].upper()}"
        bookings.append({
            "confirmation": confirmation,
            "customer_name": customer_name,
            "contact": contact,
            "service": service,
            "slot": slot,
            "created_at": datetime.now().isoformat(timespec="seconds"),
        })
        _save(bookings)
        return {"ok": True, "confirmation": confirmation, "slot": slot, "service": service}
