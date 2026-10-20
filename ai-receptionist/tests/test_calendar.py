"""Sim-provider slot generation + a booking round-trip. No network, no shared state."""

from __future__ import annotations

from app import calendar_store


def test_availability_offers_open_days(data_dir):
    days = calendar_store.availability().get("open_days", {})
    assert days, "sim provider should offer open days from the configured hours"
    _, slots = next(iter(days.items()))
    assert slots, "an open day must have at least one bookable slot"


def test_booking_round_trip_prevents_double_booking(data_dir):
    first_day, slots = next(iter(calendar_store.availability()["open_days"].items()))
    slot = slots[0]

    booking = calendar_store.book("Test User", "test@example.com", "Check-up", slot)
    assert booking["ok"], f"booking failed: {booking}"
    assert booking["confirmation"]

    again = calendar_store.availability(first_day)
    assert slot not in again.get("open_slots", []), "a booked slot must not be offered again"
