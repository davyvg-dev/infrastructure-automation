"""Google Calendar provider: availability from free/busy, bookings as calendar events.

Selected per client with `calendar.provider: google` in the business config. The client shares
their OWN Google Calendar with our single service account (see docs/GOOGLE-CALENDAR.md). We use
no domain-wide delegation and never set event `attendees` — a service account without delegation
can't add guests (Google returns `forbiddenForServiceAccounts`), so the customer's name and
contact go in the event summary/description instead.

Config (business YAML):
    calendar:
      provider: google
      calendar_id: "client@gmail.com"      # the calendar shared with our service account

Secret (env): GOOGLE_CALENDAR_SA_JSON — path to the service-account key JSON.

Auth is a self-signed JWT exchanged for an access token. We depend on `google-auth` only for the
RSA signing; every Calendar call is plain REST via urllib (no google-api-python-client).
"""

from __future__ import annotations

import json
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from . import calendar_store
from .settings import business, env

_API = "https://www.googleapis.com/calendar/v3"
_SCOPE = "https://www.googleapis.com/auth/calendar"
_TOKEN_LEEWAY = 60  # refresh this many seconds before the token actually expires

_token_lock = threading.Lock()
_token: dict[str, Any] = {"value": None, "exp": 0.0}


def _tz() -> str:
    return business()["business"].get("timezone", "Europe/Amsterdam")


def _calendar_id() -> str:
    cid = (business().get("calendar") or {}).get("calendar_id")
    if not cid:
        raise RuntimeError("calendar.calendar_id is not set in the business config.")
    return str(cid)


# --- auth: self-signed JWT -> access token (cached) -------------------------------------


def _access_token() -> str:
    with _token_lock:
        now = time.time()
        if _token["value"] and now < _token["exp"] - _TOKEN_LEEWAY:
            return _token["value"]
        try:
            from google.auth import crypt, jwt
        except ModuleNotFoundError as exc:  # pragma: no cover - install-time guard
            raise RuntimeError(
                "google-auth is required for the Google Calendar provider "
                "(pip install google-auth)."
            ) from exc
        with open(env("GOOGLE_CALENDAR_SA_JSON"), encoding="utf-8") as fh:
            info = json.load(fh)
        signer = crypt.RSASigner.from_service_account_info(info)
        issued = int(now)
        assertion = jwt.encode(signer, {
            "iss": info["client_email"],
            "scope": _SCOPE,
            "aud": info["token_uri"],
            "iat": issued,
            "exp": issued + 3600,
        })
        if isinstance(assertion, bytes):
            assertion = assertion.decode("utf-8")
        data = urllib.parse.urlencode({
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": assertion,
        }).encode()
        with urllib.request.urlopen(
            urllib.request.Request(info["token_uri"], data=data), timeout=15
        ) as resp:
            payload = json.load(resp)
        _token["value"] = payload["access_token"]
        _token["exp"] = now + int(payload.get("expires_in", 3600))
        return _token["value"]


def _api(method: str, path: str, *, body: dict | None = None) -> dict[str, Any]:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{_API}{path}", data=data, method=method)
    req.add_header("Authorization", f"Bearer {_access_token()}")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        raise RuntimeError(
            f"Google Calendar API {method} {path} failed ({exc.code}): {detail}"
        ) from exc


# --- time helpers: naive-local <-> RFC3339 ----------------------------------------------


def _rfc3339(dt: datetime) -> str:
    """A naive local datetime -> RFC3339 string with the business tz offset."""
    return dt.replace(tzinfo=ZoneInfo(_tz())).isoformat()


def _to_local(rfc: str) -> datetime:
    """RFC3339 (any offset or 'Z') -> naive datetime in the business tz."""
    dt = datetime.fromisoformat(rfc.replace("Z", "+00:00"))
    return dt.astimezone(ZoneInfo(_tz())).replace(tzinfo=None)


def _busy_intervals(start: datetime, end: datetime) -> list[tuple[datetime, datetime]]:
    cid = _calendar_id()
    resp = _api("POST", "/freeBusy", body={
        "timeMin": _rfc3339(start),
        "timeMax": _rfc3339(end),
        "timeZone": _tz(),
        "items": [{"id": cid}],
    })
    cal = resp.get("calendars", {}).get(cid, {})
    if cal.get("errors"):
        raise RuntimeError(f"free/busy error for {cid}: {cal['errors']}")
    return [(_to_local(b["start"]), _to_local(b["end"])) for b in cal.get("busy", [])]


def _is_free(slot: str, minutes: int, busy: list[tuple[datetime, datetime]]) -> bool:
    start = datetime.strptime(slot, "%Y-%m-%d %H:%M")
    end = start + timedelta(minutes=minutes)
    return not any(start < b_end and b_start < end for b_start, b_end in busy)


# --- public provider interface (mirrors calendar_store.availability/book) ----------------


def availability(on_date: str | None, days: int) -> dict[str, Any]:
    minutes = calendar_store.slot_minutes()
    horizon = calendar_store.horizon_days()
    today = datetime.now(ZoneInfo(_tz())).replace(tzinfo=None).date()

    if on_date:
        try:
            day = datetime.strptime(on_date, "%Y-%m-%d").date()
        except ValueError:
            return {"error": f"Could not parse date '{on_date}'. Use YYYY-MM-DD."}
        start = datetime.combine(day, datetime.min.time())
        busy = _busy_intervals(start, start + timedelta(days=1))
        free = [s for s in calendar_store.slots_for_day(day) if _is_free(s, minutes, busy)]
        return {"date": on_date, "open_slots": free}

    start = datetime.combine(today, datetime.min.time())
    busy = _busy_intervals(start, start + timedelta(days=horizon))
    result: dict[str, list[str]] = {}
    checked = 0
    while len(result) < days and checked < horizon:
        day = today + timedelta(days=checked)
        checked += 1
        free = [s for s in calendar_store.slots_for_day(day) if _is_free(s, minutes, busy)]
        if free:
            result[day.isoformat()] = free
    return {"open_days": result}


def book(
    customer_name: str, contact: str, service: str, slot: str, address: str = ""
) -> dict[str, Any]:
    try:
        slot_start = datetime.strptime(slot, "%Y-%m-%d %H:%M")
    except ValueError:
        return {"ok": False, "error": f"Invalid slot '{slot}'. Use 'YYYY-MM-DD HH:MM'."}
    if slot not in calendar_store.slots_for_day(slot_start.date()):
        return {"ok": False, "error": "That time isn't a bookable slot."}

    minutes = calendar_store.slot_minutes()
    # Re-check against the live calendar to narrow the double-booking window.
    if not _is_free(slot, minutes, _busy_intervals(slot_start, slot_start + timedelta(minutes=minutes))):
        return {"ok": False, "error": "That slot was just taken. Please pick another."}

    confirmation = f"BK-{uuid.uuid4().hex[:6].upper()}"
    description = f"Contact: {contact}\nGeboekt via Klantkraan\nRef: {confirmation}"
    event: dict[str, Any] = {
        "summary": f"{service} — {customer_name}",
        "description": description,
        "start": {"dateTime": _rfc3339(slot_start), "timeZone": _tz()},
        "end": {"dateTime": _rfc3339(slot_start + timedelta(minutes=minutes)),
                "timeZone": _tz()},
    }
    # For an on-site visit, put the address in `location` so it's tappable-to-navigate in the
    # calendar app, and repeat it in the description where it's always visible.
    if address:
        event["location"] = address
        event["description"] = f"Adres: {address}\n{description}"
    try:
        _api("POST", f"/calendars/{urllib.parse.quote(_calendar_id())}/events", body=event)
    except RuntimeError as exc:
        return {"ok": False, "error": f"Could not create the calendar event: {exc}"}
    return {"ok": True, "confirmation": confirmation, "slot": slot, "service": service}
