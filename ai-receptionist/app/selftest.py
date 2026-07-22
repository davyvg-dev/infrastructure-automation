"""Isolated checks + an interactive terminal chat — test each layer before the web UI.

    python -m app.selftest config      # config loads, no network
    python -m app.selftest routing     # multi-tenant slug -> config resolution, no network
    python -m app.selftest calendar    # slot generation + a booking round-trip, no network
    python -m app.selftest calendar-google  # live Google Calendar (needs creds + provider: google)
    python -m app.selftest intake      # scrape→draft merge: prices never inferred, no network
    python -m app.selftest analytics   # per-client capture store round-trip, no network
    python -m app.selftest digest      # deterministic oversight digest, no network
    python -m app.selftest agent       # scripted booking conversation (needs ANTHROPIC_API_KEY)
    python -m app.selftest scope       # takes on an in-trade job not on the price list (needs key)
    python -m app.selftest chat        # interactive terminal chat with the receptionist
    python -m app.selftest all         # config + calendar + agent + scope, in order
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


def check_intake() -> bool:
    print("• intake (scrape→draft merge, no network)")
    import json as _json

    from . import extract, scaffold

    # 1. Schema-level invariant: a price can NEVER be extracted (structural, not prompt-based).
    schema_blob = _json.dumps(extract._SCHEMA).lower()
    if "price" in schema_blob or "prijs" in schema_blob or "tarief" in schema_blob:
        return _fail("extraction schema references a price field — prices must be human-entered only")
    _ok("extraction schema has no price field (invented prices are structurally impossible)")

    fixture = {
        "business_type": {"value": "loodgieter", "snippet": "Loodgietersbedrijf in Utrecht"},
        "phone": {"value": "+31 30 123 4567", "snippet": "Bel ons: 030 123 4567"},
        "region": {"value": "", "snippet": ""},  # uncited -> must fall back to a safe default
        "services": [
            {"name": "Lekkage verhelpen", "category": "lekkage-reparatie",
             "snippet": "lekkage snel verholpen", "confidence": "high"},
            {"name": "Verzonnen dienst", "category": "overig",
             "snippet": "", "confidence": "low"},  # uncited -> dropped
        ],
        "hours": {
            "monday": {"open": "08:00", "close": "17:00", "snippet": "ma 08:00-17:00"},
            "sunday": {"open": "", "close": "", "snippet": ""},  # uncited -> dropped
        },
    }
    cfg = scaffold.merge_extraction("Testbedrijf Utrecht", fixture)

    for svc in cfg["services"]:
        if svc.get("price") != "PRIJS?":
            return _fail(f"service {svc['name']!r} has a non-placeholder price {svc.get('price')!r}")
    _ok(f"{len(cfg['services'])} service(s), every price is PRIJS? (no price ever inferred)")

    names = [s["name"] for s in cfg["services"]]
    if "Verzonnen dienst" in names:
        return _fail("an uncited service leaked into the draft")
    if "Lekkage verhelpen" not in names:
        return _fail("a cited service was dropped")
    _ok("uncited service dropped; cited service kept")

    if cfg["business"]["phone"] != "+31 30 123 4567":
        return _fail("cited phone was not applied")
    if not cfg["business"]["address"]:
        return _fail("uncited region should fall back to a safe template default, not blank")
    _ok("cited phone applied; uncited region fell back to a safe default (never guessed)")

    if cfg["hours"] != {"monday": ["08:00", "17:00"]}:
        return _fail(f"hours merge wrong: {cfg['hours']}")
    _ok("cited hours applied; uncited day dropped")

    if "digitale receptionist" not in cfg["greeting"]:
        return _fail("greeting lost the art. 50 digital-assistant disclosure")
    services_blob = _json.dumps(cfg["services"], ensure_ascii=False).lower()
    if "€" in services_blob or "eur" in services_blob:
        return _fail("a currency amount leaked into the services")
    _ok("art. 50 disclosure intact; no currency amount anywhere in the services")
    return True


def check_analytics() -> bool:
    print("• analytics (per-client capture store, no network)")
    from . import analytics

    # after-hours logic: a day with no configured hours is a closed day.
    closed = analytics.is_after_hours({"business": {}, "hours": {}})
    if not closed:
        return _fail("a day with no opening hours should count as after-hours")
    _ok("after-hours detection: a closed day is flagged after-hours")

    orig_dir = settings.DATA_DIR
    with tempfile.TemporaryDirectory() as tmp:
        settings.DATA_DIR = Path(tmp)
        try:
            # Turn 1: a plain answered turn. Turn 2: a successful booking, same conversation.
            analytics.record_turn(
                client="acme-loodgieter", channel="web", user_id="+31600000000",
                user_text="hi", reply="hello", input_tokens=100, output_tokens=20,
                model="claude-opus-4-8", tools=[], after_hours=True,
            )
            analytics.record_turn(
                client="acme-loodgieter", channel="web", user_id="+31600000000",
                user_text="book me in", reply="booked!", input_tokens=200, output_tokens=40,
                model="claude-opus-4-8",
                tools=[{"name": "book_appointment", "input": {},
                        "output": '{"ok": true, "confirmation": "AB12"}'}],
                after_hours=False,
            )
            sess = analytics.load_session("acme-loodgieter", "web", "+31600000000")
            if sess is None:
                return _fail("session was not persisted")
            if sess["turns"] != 2:
                return _fail(f"expected 2 turns, got {sess['turns']}")
            if sess["outcome"] != "booked":
                return _fail(f"outcome should escalate to 'booked', got {sess['outcome']!r}")
            if sess["input_tokens"] != 300 or sess["output_tokens"] != 60:
                return _fail(f"token totals wrong: {sess['input_tokens']}/{sess['output_tokens']}")
            if sess["after_hours_turns"] != 1:
                return _fail(f"after-hours turn count wrong: {sess['after_hours_turns']}")
            _ok("2 turns rolled up: outcome=booked, tokens=300/60, 1 after-hours turn")
            if "+31600000000" in sess["session_key"]:
                return _fail("raw phone number leaked into the store — must be hashed")
            _ok("channel user id is stored hashed, not in the clear")

            # AVG retention: an old transcript turn is purged; the rollup + recent turns stay.
            from datetime import datetime, timedelta

            conn = analytics._connect()
            try:
                old_ts = (datetime.now() - timedelta(days=120)).isoformat(timespec="seconds")
                conn.execute(
                    "INSERT INTO turns (session_key, client, ts, user_text, reply) "
                    "VALUES (?,?,?,?,?)",
                    ("acme-loodgieter:web:x", "acme-loodgieter", old_ts, "old", "old"),
                )
                conn.commit()
            finally:
                conn.close()
            before = analytics._count_turns()
            deleted = analytics.purge_transcripts(retention_days=90)
            after = analytics._count_turns()
            if deleted != 1 or after != before - 1:
                return _fail(f"retention should purge exactly the 1 old turn (deleted={deleted})")
            if analytics._count_turns() < 2:
                return _fail("retention purged recent turns — only >90d transcripts should go")
            if analytics.load_session("acme-loodgieter", "web", "+31600000000") is None:
                return _fail("retention deleted a session rollup — only raw turns should be purged")
            _ok("retention purges >90d transcripts, keeps recent turns + the session rollup")
        finally:
            settings.DATA_DIR = orig_dir
    return True


def check_digest() -> bool:
    print("• digest (deterministic oversight, no network)")
    from datetime import datetime

    from . import analytics, oversight

    # cost model: 1M input + 1M output of Haiku = ($1 + $5) * 0.92 EUR
    c = oversight.cost_eur({"claude-haiku-4-5": {"input": 1_000_000, "output": 1_000_000}})
    if round(c, 2) != 5.52:
        return _fail(f"cost model wrong: expected €5.52, got €{c:.2f}")
    _ok("cost model: 1M+1M Haiku tokens ≈ €5.52 (rates × USD→EUR)")

    orig_data, orig_clients = settings.DATA_DIR, settings.CLIENTS_DIR
    with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as ctmp:
        settings.DATA_DIR = Path(tmp)
        settings.CLIENTS_DIR = Path(ctmp)
        try:
            (settings.CLIENTS_DIR / "acme-loodgieter.yaml").write_text(
                'business:\n  name: "Acme Loodgieter"\n  type: "loodgieter"\n', encoding="utf-8")
            (settings.CLIENTS_DIR / "smit-dak.yaml").write_text(
                'business:\n  name: "Smit Dakwerken"\n  type: "dakdekker"\n', encoding="utf-8")
            # Acme: an after-hours lead (message taken). Smit: a booking.
            analytics.record_turn(
                client="acme-loodgieter", channel="web", user_id="+31600000001",
                user_text="hoi", reply="hallo", input_tokens=1000, output_tokens=200,
                model="claude-opus-4-8",
                tools=[{"name": "take_message", "input": {}, "output": '{"ok": true}'}],
                after_hours=True)
            analytics.record_turn(
                client="smit-dak", channel="web", user_id="+31600000002",
                user_text="afspraak", reply="geboekt", input_tokens=2000, output_tokens=400,
                model="claude-opus-4-8",
                tools=[{"name": "book_appointment", "input": {},
                        "output": '{"ok": true, "confirmation": "X1"}'}],
                after_hours=False)

            text = oversight.build_digest(now=datetime.now(), today=True)
            if "2/2 bots active" not in text:
                return _fail(f"header should show 2/2 bots active:\n{text}")
            if "2 conversations · 1 leads · 1 bookings" not in text:
                return _fail(f"totals wrong:\n{text}")
            _ok("header rolls up 2 active bots: 2 conversations, 1 lead, 1 booking")

            if "Acme Loodgieter" not in text or "1 leads" not in text or "100% after-hours" not in text:
                return _fail(f"Acme line missing lead / after-hours share:\n{text}")
            if "Smit Dakwerken" not in text or "1 booked" not in text:
                return _fail(f"Smit line missing its booking:\n{text}")
            _ok("per-client lines show the lead, the booking, and the after-hours share by name")

            if "NEEDS ATTENTION" in text:
                return _fail(f"nothing should be flagged on a clean window:\n{text}")
            _ok("no false attention items on a clean window")
        finally:
            settings.DATA_DIR, settings.CLIENTS_DIR = orig_data, orig_clients
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


# A job squarely in the installateur's trade but NOT one of the priced service lines — exactly the
# case that used to get refused. The receptionist must take it on and steer to an inspection/offerte,
# never turn the customer away. Regression guard for the scope-of-work frame in build_system_prompt.
_SCOPE_CONFIG = "config/klantkraan-demo.yaml"
_SCOPE_REQUEST = "Goedemiddag, kunnen jullie bij ons in de woonkamer vloerverwarming aanleggen?"
_REFUSAL_MARKERS = (
    "kan ik u niet helpen", "kan ik niet helpen", "kunnen wij niet helpen",
    "kunnen we u niet helpen", "dat doen wij niet", "dat doen we niet",
    "niet mogelijk", "helaas kunnen we",
)
_HELP_MARKERS = (
    "offerte", "inspectie", "afspraak", "inplann", "beschikbaar", "langskomen", "opmeten",
)


def check_scope() -> bool:
    print("• scope (in-trade job not on the price list; needs ANTHROPIC_API_KEY)")
    try:
        env("ANTHROPIC_API_KEY")
    except MissingSetting as exc:
        return _fail(str(exc))
    import os

    from . import receptionist

    prev = os.environ.get("BUSINESS_CONFIG")
    os.environ["BUSINESS_CONFIG"] = _SCOPE_CONFIG
    try:
        print(f"    🧑 {_SCOPE_REQUEST}")
        reply, _ = receptionist.run_turn([], _SCOPE_REQUEST)
        print(f"    🤖 {reply}")
    except Exception as exc:
        return _fail(f"scope turn failed: {exc}")
    finally:
        if prev is None:
            os.environ.pop("BUSINESS_CONFIG", None)
        else:
            os.environ["BUSINESS_CONFIG"] = prev

    low = reply.lower()
    if any(m in low for m in _REFUSAL_MARKERS):
        return _fail("refused an in-scope job — it should offer an inspection/offerte instead")
    if not any(m in low for m in _HELP_MARKERS):
        return _fail("didn't steer an in-scope job toward booking/inspection")
    _ok("takes on an in-trade job that isn't a listed service and steers to an inspection/offerte")
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
    "intake": check_intake,
    "analytics": check_analytics,
    "digest": check_digest,
    "agent": check_agent,
    "scope": check_scope,
}
ORDER = ["config", "routing", "calendar", "intake", "analytics", "digest", "agent", "scope"]


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
