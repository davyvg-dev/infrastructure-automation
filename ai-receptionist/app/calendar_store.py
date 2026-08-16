"""Calendar access: generate bookable slots and record bookings, via a pluggable provider.

The public seam is `availability()` and `book()` — their SIGNATURES are fixed; only the
backing store changes per client. The provider is chosen in the business config:

    calendar:
      provider: sim | google      # default: sim

- `sim`    — a local JSON file. Zero external setup; used for demos and prospect showcases.
- `google` — the client's own Google Calendar (see app/calendar_google.py). The client shares
             their calendar with our service account; availability comes from free/busy and
             bookings become calendar events.

Owner notification on a successful booking is centralised here, so every provider behaves the
same from the caller's point of view.
"""

from __future__ import annotations

import json
import threading
import uuid
from datetime import date, datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from . import notify
from .settings import DATA_DIR, business, config_path, ensure_dirs

_lock = threading.Lock()

_WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


# --- shared helpers (provider-agnostic) -------------------------------------------------


def _now() -> datetime:
    """Naive 'now' in the business's own timezone — the frame all slot strings live in."""
    tz = business()["business"].get("timezone", "Europe/Amsterdam")
    return datetime.now(ZoneInfo(tz)).replace(tzinfo=None)


def slots_for_day(day: date) -> list[str]:
    """Candidate slot start-times within opening hours, excluding any already in the past.

    This is what's *bookable in principle* for the day; each provider then removes the slots
    that are actually taken (sim: from its JSON; google: from the calendar's free/busy)."""
    cfg = business()
    hours = cfg["hours"].get(_WEEKDAYS[day.weekday()])
    if not hours:
        return []  # closed
    open_t = datetime.strptime(hours[0], "%H:%M").time()
    close_t = datetime.strptime(hours[1], "%H:%M").time()
    step = int(cfg["booking"]["slot_minutes"])
    cur = datetime.combine(day, open_t)
    end = datetime.combine(day, close_t)
    now = _now()
    out = []
    while cur + timedelta(minutes=step) <= end:
        if cur > now:  # never offer a slot that has already started
            out.append(cur.strftime("%Y-%m-%d %H:%M"))
        cur += timedelta(minutes=step)
    return out


def slot_minutes() -> int:
    return int(business()["booking"]["slot_minutes"])


def horizon_days() -> int:
    return int(business()["booking"]["horizon_days"])


def _provider_name() -> str:
    cal = business().get("calendar") or {}
    return str(cal.get("provider", "sim")).lower()


# --- sim provider: a local JSON file (zero external setup) -------------------------------


def _bookings_path() -> Any:
    # One file per business config, so prospect demos don't share (and collide on) slots.
    return DATA_DIR / f"bookings-{config_path().stem}.json"


def _load() -> list[dict[str, Any]]:
    path = _bookings_path()
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _save(bookings: list[dict[str, Any]]) -> None:
    ensure_dirs()
    path = _bookings_path()
    tmp = path.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(bookings, fh, ensure_ascii=False, indent=2)
    tmp.replace(path)


def _booked_slots() -> set[str]:
    return {b["slot"] for b in _load()}


def _sim_availability(on_date: str | None, days: int) -> dict[str, Any]:
    horizon = horizon_days()
    booked = _booked_slots()

    def free(day: date) -> list[str]:
        return [s for s in slots_for_day(day) if s not in booked]

    if on_date:
        try:
            day = datetime.strptime(on_date, "%Y-%m-%d").date()
        except ValueError:
            return {"error": f"Could not parse date '{on_date}'. Use YYYY-MM-DD."}
        return {"date": on_date, "open_slots": free(day)}

    today = _now().date()
    result: dict[str, list[str]] = {}
    checked = 0
    while len(result) < days and checked < horizon:
        day = today + timedelta(days=checked)
        checked += 1
        slots = free(day)
        if slots:
            result[day.isoformat()] = slots
    return {"open_days": result}


def _sim_book(
    customer_name: str, contact: str, service: str, slot: str, address: str = ""
) -> dict[str, Any]:
    with _lock:
        bookings = _load()
        if any(b["slot"] == slot for b in bookings):
            return {
                "ok": False,
                "error": "That slot was just taken. Call check_availability again and "
                "offer the customer a fresh open slot.",
            }
        # Validate the slot is a real, open slot for its day.
        try:
            day = datetime.strptime(slot, "%Y-%m-%d %H:%M").date()
        except ValueError:
            return {"ok": False, "error": f"Invalid slot '{slot}'. Use 'YYYY-MM-DD HH:MM'."}
        if slot not in slots_for_day(day):
            return {
                "ok": False,
                "error": "That time isn't a bookable slot. Call check_availability and "
                "only offer times it returns.",
            }
        confirmation = f"BK-{uuid.uuid4().hex[:6].upper()}"
        bookings.append(
            {
                "confirmation": confirmation,
                "customer_name": customer_name,
                "contact": contact,
                "service": service,
                "slot": slot,
                "address": address,
                "created_at": datetime.now().isoformat(timespec="seconds"),
            }
        )
        _save(bookings)
        return {"ok": True, "confirmation": confirmation, "slot": slot, "service": service}


# --- public seam: dispatch to the configured provider, then notify the owner -------------


def availability(on_date: str | None = None, days: int = 5) -> dict[str, Any]:
    """Return open slots. If on_date ('YYYY-MM-DD') is given, just that day; else the next
    `days` open days within the booking horizon. The shape is provider-independent."""
    if _provider_name() == "google":
        from . import calendar_google

        return calendar_google.availability(on_date, days)
    return _sim_availability(on_date, days)


def book(
    customer_name: str, contact: str, service: str, slot: str, address: str = ""
) -> dict[str, Any]:
    """Book a slot if it's still open. Returns a confirmation or an error.

    `address` is the customer's on-site service address (empty for come-to-us businesses like a
    clinic or salon). It is stored with the booking and surfaced to the owner so the person who
    turns up knows where to go."""
    if _provider_name() == "google":
        from . import calendar_google

        result = calendar_google.book(customer_name, contact, service, slot, address)
    else:
        result = _sim_book(customer_name, contact, service, slot, address)
    if result.get("ok"):
        where = f"\nAddress: {address}" if address else ""
        notify.owner(
            f"📅 New booking: {customer_name} — {service} at {slot}"
            f"{where}\nContact: {contact}\nConfirmation: {result['confirmation']}"
        )
    return result
