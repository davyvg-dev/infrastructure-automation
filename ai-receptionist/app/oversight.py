"""Oversight digest — captured data becomes a daily pocket summary for the founder.

Deterministic Layer 1 of docs/client-intelligence.md Slice 2: read the analytics capture
store and push one line per active client, plus a NEEDS ATTENTION block, through the existing
notify.owner Telegram seam. No LLM here — these are the hard ROI numbers (conversations, leads,
bookings, after-hours share, estimated cost). The nightly Claude "analyst" that enriches this
with quality flags and upsell signals is a later sub-slice; it sits on top of these numbers,
never replaces them.

Internal ops alert -> English, matching the other notify.owner messages (the client-facing
Dutch ROI PDF is Slice 4).

CLI (the cron / systemd-timer entry point):
  python -m app.oversight digest         # build + send yesterday's digest
  python -m app.oversight digest --dry   # print it, don't send
  python -m app.oversight digest --today # cover today-so-far (handy for a live check)
"""

from __future__ import annotations

import logging
import os
import sys
from datetime import datetime, time as dtime, timedelta
from typing import Any

from . import analytics, notify, settings

log = logging.getLogger("oversight")

# Published $/MTok (input, output) per model — context7 Anthropic pricing, 2026-07.
# Unknown models fall back to the Opus rate so cost is never silently understated.
_USD_PER_MTOK = {
    "claude-opus-4-8": (5.0, 25.0),
    "claude-opus-4-7": (5.0, 25.0),
    "claude-sonnet-5": (3.0, 15.0),
    "claude-haiku-4-5": (1.0, 5.0),
    "claude-haiku-4-5-20251001": (1.0, 5.0),
}
_DEFAULT_USD_PER_MTOK = (5.0, 25.0)


def _usd_to_eur() -> float:
    try:
        return float(os.getenv("OVERSIGHT_USD_TO_EUR", "0.92"))
    except ValueError:
        return 0.92


def _cost_alert_eur() -> float:
    try:
        return float(os.getenv("OVERSIGHT_COST_ALERT_EUR", "2.0"))
    except ValueError:
        return 2.0


def cost_eur(token_by_model: dict[str, dict[str, int]]) -> float:
    """Estimated € spend for a model->{input,output} token breakdown. An estimate: cache
    reads are billed as full-price input here, so this is an upper bound on true cost."""
    usd = 0.0
    for model, toks in token_by_model.items():
        in_rate, out_rate = _USD_PER_MTOK.get(model, _DEFAULT_USD_PER_MTOK)
        usd += toks.get("input", 0) / 1_000_000 * in_rate
        usd += toks.get("output", 0) / 1_000_000 * out_rate
    return usd * _usd_to_eur()


def _roster_size() -> int:
    """How many client bots are live = config/clients/<slug>.yaml files."""
    try:
        return sum(1 for p in settings.CLIENTS_DIR.glob("*.yaml"))
    except Exception:
        return 0


def _client_name(slug: str) -> str:
    try:
        cfg = settings.config_for(slug)
        return ((cfg or {}).get("business") or {}).get("name") or slug
    except Exception:
        return slug


def _day_window(now: datetime, today: bool) -> tuple[str, str, str]:
    """(start_iso, end_iso, label). Default = the whole of yesterday; --today = midnight..now."""
    midnight = datetime.combine(now.date(), dtime.min)
    if today:
        # End at tomorrow-midnight: nothing is stamped in the future, so this captures every
        # turn today without a same-second boundary race against `now`.
        start, end = midnight, midnight + timedelta(days=1)
        label = now.strftime("%Y-%m-%d (so far)")
    else:
        start, end = midnight - timedelta(days=1), midnight
        label = (midnight - timedelta(days=1)).strftime("%Y-%m-%d")
    return start.isoformat(timespec="seconds"), end.isoformat(timespec="seconds"), label


def build_digest(now: datetime | None = None, today: bool = False) -> str:
    now = now or datetime.now()
    start, end, label = _day_window(now, today)
    # Prior window of equal length, for the "went silent" signal.
    prev_start = (datetime.fromisoformat(start) - (datetime.fromisoformat(end) -
                  datetime.fromisoformat(start))).isoformat(timespec="seconds")

    active = analytics.active_clients(start, end)
    prev_active = set(analytics.active_clients(prev_start, start))

    lines: list[str] = [f"Klantkraan oversight — {label}"]
    if not active:
        lines.append("No conversations captured in this window.")
        went_silent = sorted(prev_active)  # everyone who was busy yesterday and is quiet now
        if went_silent:
            lines.append("")
            lines.append("NEEDS ATTENTION")
            for slug in went_silent:
                lines.append(f"  ⚠ {_client_name(slug)} went quiet (had traffic, now none)")
        return "\n".join(lines)

    rows = []
    tot_conv = tot_leads = tot_book = 0
    tot_cost = 0.0
    attention: list[str] = []
    alert = _cost_alert_eur()
    for slug in active:
        s = analytics.daily_stats(slug, start, end)
        c = cost_eur(s["token_by_model"])
        ah_share = round(100 * s["after_hours_turns"] / s["turns"]) if s["turns"] else 0
        rows.append((slug, s, c, ah_share))
        tot_conv += s["conversations"]
        tot_leads += s["leads"]
        tot_book += s["bookings"]
        tot_cost += c
        if c > alert:
            attention.append(f"  ⚠ {_client_name(slug)} cost spike: ~€{c:.2f} (> €{alert:.2f}/day)")

    went_silent = sorted(prev_active - set(active))
    for slug in went_silent:
        attention.append(f"  ⚠ {_client_name(slug)} went quiet (had traffic yesterday, none now)")

    lines.append(
        f"{len(active)}/{_roster_size()} bots active · {tot_conv} conversations · "
        f"{tot_leads} leads · {tot_book} bookings · ~€{tot_cost:.2f}"
    )
    lines.append("")
    for slug, s, c, ah in sorted(rows, key=lambda r: r[1]["conversations"], reverse=True):
        lines.append(
            f"• {_client_name(slug)}: {s['conversations']} conv · {s['leads']} leads · "
            f"{s['bookings']} booked · {ah}% after-hours · ~€{c:.2f}"
        )

    lines.append("")
    if attention:
        lines.append("NEEDS ATTENTION")
        lines.extend(attention)
    else:
        lines.append("No attention items.")
    return "\n".join(lines)


def send_digest(now: datetime | None = None, today: bool = False) -> bool:
    """Build the digest and push it to the founder (OWNER_TELEGRAM_CHAT_ID). True on delivery."""
    return notify.owner(build_digest(now, today))


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] != "digest":
        print("usage: python -m app.oversight digest [--dry] [--today]")
        return 2
    today = "--today" in argv
    text = build_digest(today=today)
    if "--dry" in argv:
        print(text)
        return 0
    ok = send_digest(today=today)
    print(text)
    print(f"\n[{'sent' if ok else 'NOT sent — configure OWNER_TELEGRAM_CHAT_ID'}]")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
