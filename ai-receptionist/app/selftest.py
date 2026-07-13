"""Isolated checks + an interactive terminal chat — test each layer before the web UI.

    python -m app.selftest config      # config loads, no network
    python -m app.selftest routing     # multi-tenant slug -> config resolution, no network
    python -m app.selftest calendar    # slot generation + a booking round-trip, no network
    python -m app.selftest calendar-google  # live Google Calendar (needs creds + provider: google)
    python -m app.selftest agent       # scripted booking conversation (needs ANTHROPIC_API_KEY)
    python -m app.selftest chat        # interactive terminal chat with the receptionist
    python -m app.selftest all         # config + calendar + agent, in order
"""

from __future__ import annotations

import sys
import tempfile
import textwrap
from pathlib import Path

from . import settings
from .settings import MissingSetting, business, env


def _ok(m: str) -> None:
    print(f"  ✅ {m}")


def _fail(m: str) -> bool:
    print(f"  ❌ {m}")
    return False


def check_config() -> bool:
    print("• config")
    try:
        cfg = business()
    except Exception as exc:
        return _fail(f"could not load config: {exc}")
    _ok(f"business: {cfg['business']['name']} ({cfg['business']['type']})")
    _ok(f"persona: {cfg['persona']['name']}")
    _ok(f"services: {', '.join(s['name'] for s in cfg.get('services', []))}")
    _ok(f"model: {cfg['model']['id']} (effort={cfg['model'].get('effort', 'low')})")
    return True


def check_routing() -> bool:
    print("• routing (multi-tenant, no network)")
    if settings.current_slug() is not None:
        return _fail("expected no active client at rest")
    default_name = business()["business"]["name"]
    _ok(f"default client (no slug) resolves to: {default_name}")

    orig_dir = settings.CLIENTS_DIR
    with tempfile.TemporaryDirectory() as tmp:
        settings.CLIENTS_DIR = Path(tmp)
        (settings.CLIENTS_DIR / "acme-loodgieter.yaml").write_text(
            textwrap.dedent(
                """\
                business:
                  name: "Acme Loodgieter"
                  type: "loodgieter"
                  timezone: "Europe/Amsterdam"
                """
            ),
            encoding="utf-8",
        )
        try:
            if settings.resolve_slug("demo-1-2-3-4.sslip.io") is not None:
                return _fail("an unknown host must not resolve to a client")
            if settings.client_config_path("../secrets") is not None:
                return _fail("a path-traversal slug must be rejected")
            slug = settings.resolve_slug("acme-loodgieter.klantkraan.nl")
            if slug != "acme-loodgieter":
                return _fail(f"host subdomain routing failed: got {slug!r}")
            _ok("unknown host -> default; traversal slug rejected; subdomain -> slug")

            token = settings.use_slug(slug)
            try:
                if settings.active_client() != "acme-loodgieter":
                    return _fail("active_client() did not track the slug")
                if settings.config_path().name != "acme-loodgieter.yaml":
                    return _fail("config_path() did not point at the client file")
                if business()["business"]["name"] != "Acme Loodgieter":
                    return _fail("business() did not switch to the client config")
            finally:
                settings.clear_slug(token)
            _ok("active request -> client config swapped in (business/config_path/active_client)")
        finally:
            settings.CLIENTS_DIR = orig_dir

    if settings.current_slug() is not None or business()["business"]["name"] != default_name:
        return _fail("did not fall back to the default client after the request scope ended")
    _ok("falls back to the default client once the request scope ends")
    return True


def check_calendar() -> bool:
    print("• calendar (no network)")
    from . import calendar_store

    avail = calendar_store.availability()
    days = avail.get("open_days", {})
    if not days:
        return _fail("no open days generated — check the 'hours' config")
    first_day, slots = next(iter(days.items()))
    _ok(f"{len(days)} open day(s); {first_day} has {len(slots)} slots, first={slots[0]}")

    booking = calendar_store.book("Test User", "test@example.com", "Check-up", slots[0])
    if not booking.get("ok"):
        return _fail(f"booking failed: {booking}")
    _ok(f"booked {slots[0]} → {booking['confirmation']}")

    again = calendar_store.availability(first_day)
    if slots[0] in again.get("open_slots", []):
        return _fail("slot still shows open after booking")
    _ok("booked slot no longer offered (double-booking prevented)")
    return True


def check_calendar_google() -> bool:
    print("• google calendar (needs calendar.provider: google + GOOGLE_CALENDAR_SA_JSON)")
    provider = str((business().get("calendar") or {}).get("provider", "sim")).lower()
    if provider != "google":
        _ok(f"provider is '{provider}', not google — skipping. Set calendar.provider: google to test.")
        return True
    try:
        env("GOOGLE_CALENDAR_SA_JSON")
    except MissingSetting as exc:
        return _fail(str(exc))
    from . import calendar_store

    try:
        avail = calendar_store.availability()
    except Exception as exc:
        return _fail(f"live Google Calendar call failed: {exc}")
    days = avail.get("open_days", {})
    if not days:
        _ok("connected to Google Calendar; no open days in the horizon (fully busy or closed?)")
        return True
    first_day, slots = next(iter(days.items()))
    _ok(f"connected to Google Calendar; {len(days)} open day(s); {first_day} has {len(slots)} slots")
    return True


def check_agent() -> bool:
    print("• agent (needs ANTHROPIC_API_KEY)")
    try:
        env("ANTHROPIC_API_KEY")
    except MissingSetting as exc:
        return _fail(str(exc))
    from . import receptionist

    script = [
        "Hi, do you have anything for a check-up this week?",
        "Let's take the earliest one.",
        "Name is Sam Jansen, phone 0612345678.",
    ]
    history: list = []
    try:
        for turn in script:
            print(f"    🧑 {turn}")
            reply, history = receptionist.run_turn(history, turn)
            print(f"    🤖 {reply}")
    except Exception as exc:
        return _fail(f"agent turn failed: {exc}")
    _ok("agent completed a scripted booking conversation")
    return True


def interactive_chat() -> bool:
    from . import receptionist

    print(f"\n{receptionist.greeting()}\n(type 'quit' to exit)\n")
    history: list = []
    while True:
        try:
            msg = input("you › ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if msg.lower() in ("quit", "exit"):
            break
        if not msg:
            continue
        reply, history = receptionist.run_turn(history, msg)
        print(f"bot › {reply}\n")
    return True


CHECKS = {
    "config": check_config,
    "routing": check_routing,
    "calendar": check_calendar,
    "calendar-google": check_calendar_google,
    "agent": check_agent,
}
ORDER = ["config", "routing", "calendar", "agent"]


def main(argv: list[str]) -> int:
    which = argv[1] if len(argv) > 1 else "all"
    if which == "chat":
        return 0 if interactive_chat() else 1
    names = ORDER if which == "all" else [which]
    if which != "all" and which not in CHECKS:
        print(f"Unknown check '{which}'. Choose: {', '.join(CHECKS)}, chat, all")
        return 2
    for name in names:
        if not CHECKS[name]():
            print(f"\nStopped at '{name}'. Fix it, then re-run.")
            return 1
        print()
    print("All requested checks passed. ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
