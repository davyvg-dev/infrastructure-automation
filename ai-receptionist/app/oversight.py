"""Oversight digest — captured data becomes a daily pocket summary for the founder.

Deterministic Layer 1 of docs/client-intelligence.md Slice 2: read the analytics capture
store and push one line per active client, plus a NEEDS ATTENTION block, through the existing
notify.owner Telegram seam. No LLM here — these are the hard ROI numbers (conversations, leads,
bookings, after-hours share, estimated cost). The nightly Claude "analyst" that enriches this
with quality flags and upsell signals is a later sub-slice; it sits on top of these numbers,
never replaces them.

Internal ops alert -> English, matching the other notify.owner messages (the client-facing
Dutch ROI PDF is Slice 4).

The CLI path also appends the MAIL section (inbound replies/bounces via app.mail_signals,
the merged remains of the retired Mac launchd briefing) so 07:30 is ONE morning message.

CLI (the cron / systemd-timer entry point):
  python -m app.oversight digest         # build + send yesterday's digest
  python -m app.oversight digest --dry   # print it, don't send
  python -m app.oversight digest --today # cover today-so-far (handy for a live check)
"""

from __future__ import annotations

import json
import logging
import os
import re
import sys
from datetime import datetime, timedelta
from datetime import time as dtime
from typing import Any

from . import analytics, mail_signals, notify, settings

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


def build_digest(now: datetime | None = None, today: bool = False, mail: bool = False) -> str:
    # mail=True (the CLI/timer path) appends the IMAP replies/bounces section; it stays off
    # by default so library callers and tests never touch the network.
    now = now or datetime.now()
    start, end, label = _day_window(now, today)
    # Prior window of equal length, for the "went silent" signal.
    prev_start = (
        datetime.fromisoformat(start)
        - (datetime.fromisoformat(end) - datetime.fromisoformat(start))
    ).isoformat(timespec="seconds")

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
        if mail:
            lines.append("")
            lines.extend(mail_signals.digest_section(now))
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

    # Layer 2: fold in what the analyst learned about the same conversations (if it has run).
    quality: dict[str, int] = {}
    unanswered: dict[str, int] = {}
    upsell: dict[str, int] = {}
    escalations = 0
    for ins in analytics.insights_in_window(start, end):
        escalations += 1 if ins.get("escalated") else 0
        for q in ins["quality_json"]:
            quality[q] = quality.get(q, 0) + 1
        for q in ins["unanswered_json"]:
            unanswered[q] = unanswered.get(q, 0) + 1
        for u in ins["upsell_json"]:
            upsell[u] = upsell.get(u, 0) + 1
    for flag, n in sorted(quality.items(), key=lambda kv: -kv[1]):
        attention.append(f"  ⚠ quality flag {n}×: {flag} (review the bot)")

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

    def _top(counter: dict[str, int]) -> list[str]:
        return [f"  {n}× {k}" for k, n in sorted(counter.items(), key=lambda kv: -kv[1])[:5]]

    if unanswered or upsell:
        lines.append("")
        lines.append("SIGNALS")
        if escalations:
            lines.append(f"  {escalations} escalation(s)")
        if unanswered:
            lines.append("  FAQ gaps (customers asked, bot couldn't answer):")
            lines.extend(_top(unanswered))
        if upsell:
            lines.append("  upsell radar:")
            lines.extend(_top(upsell))
    if mail:
        lines.append("")
        lines.extend(mail_signals.digest_section(now))
    return "\n".join(lines)


def send_digest(
    now: datetime | None = None,
    today: bool = False,
    mail: bool = False,
    text: str | None = None,
) -> dict[str, bool]:
    """Build the digest and push it to the founder: Telegram if configured, else e-mail.

    Returns which channels took it. A nightly timer whose output goes nowhere is worse than
    no timer, so the caller can tell the difference between delivered and merely printed.
    Pass `text` when the digest is already built — the mail section does a real IMAP fetch,
    which must not run twice for one send.
    """
    if text is None:
        text = build_digest(now, today, mail)
    subject = f"Klantkraan dagrapport {(now or datetime.now()).date().isoformat()}"
    return notify.owner_report(subject, text)


# --- Layer 2: the analyst (a cheap nightly Claude pass over finished conversations) ------

# One Haiku call per conversation extracts this structured intelligence. Kept in sync with the
# `insights` table and docs/client-intelligence.md. additionalProperties:false + every field
# required is what structured outputs needs; the model must fill each one.
_INSIGHT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "intent": {"type": "string"},
        "topics": {"type": "array", "items": {"type": "string"}},
        "resolved": {"type": "boolean"},
        "escalated": {"type": "boolean"},
        "escalation_reason": {"type": "string"},
        "unanswered_questions": {"type": "array", "items": {"type": "string"}},
        "out_of_scope_requests": {"type": "array", "items": {"type": "string"}},
        "sentiment": {"type": "string", "enum": ["pos", "neu", "neg"]},
        "language": {"type": "string"},
        "customer_type": {"type": "string", "enum": ["new", "existing", "vendor", "spam"]},
        "lead_captured": {"type": "boolean"},
        "booking_made": {"type": "boolean"},
        "est_job_value_eur": {"type": "number"},
        "upsell_signals": {"type": "array", "items": {"type": "string"}},
        "quality_flags": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "intent",
        "topics",
        "resolved",
        "escalated",
        "escalation_reason",
        "unanswered_questions",
        "out_of_scope_requests",
        "sentiment",
        "language",
        "customer_type",
        "lead_captured",
        "booking_made",
        "est_job_value_eur",
        "upsell_signals",
        "quality_flags",
    ],
}

_ANALYST_SYSTEM = """You analyse one finished conversation between a customer and a business's \
digital receptionist, and return structured intelligence for the business owner.

The business: {name} — a {btype}. Services and prices it offers:
{services}

Rules:
- Judge only from the transcript. Do not invent facts. Empty arrays are fine.
- unanswered_questions: questions the bot could not answer (FAQ gaps to fix).
- out_of_scope_requests: services the customer asked for that this trade does not list (upsell).
- quality_flags: bot mistakes to review — use tags like refused_in_scope_job, quoted_price_it_shouldnt, \
invented_slot, hallucinated_fact. Only flag what the transcript shows.
- upsell_signals: short tags, e.g. after_hours_share_high, language_mismatch:de, booking_intent_no_calendar.
- est_job_value_eur: a rough euro value of the job from the service prices above and the intent; 0 if unclear.
- language: the customer's language (ISO code like nl, de, en)."""

_EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
# 8+ digits allowing spaces/dashes/parens and an optional leading + — covers NL 06.., +31.., 0xx-.
_PHONE_RE = re.compile(r"\+?\d[\d\s().\-]{7,}\d")


def redact(text: str) -> str:
    """Strip obvious PII (email, phone) before a transcript leaves for the analyst (AVG)."""
    return _PHONE_RE.sub("[phone]", _EMAIL_RE.sub("[email]", text or ""))


def _analyst_model() -> str:
    # Haiku is the right tier for a cheap classification. It does NOT accept effort/adaptive
    # thinking (4.6+ only), so the analyst call carries neither — just structured output.
    return os.getenv("OVERSIGHT_ANALYST_MODEL", "claude-haiku-4-5-20251001")


def _services_summary(cfg: dict[str, Any]) -> str:
    lines = [
        f"  - {s.get('name', '?')} ({s.get('price', 'ask')})" for s in (cfg.get("services") or [])
    ]
    return "\n".join(lines) or "  (none listed)"


def _analyze(
    client: Any, model: str, cfg: dict[str, Any], turns: list[dict[str, str]]
) -> dict[str, Any]:
    """Run one structured-output call over a redacted transcript and return the parsed insight."""
    b = cfg.get("business") or {}
    system = _ANALYST_SYSTEM.format(
        name=b.get("name", "the business"),
        btype=b.get("type", "local business"),
        services=_services_summary(cfg),
    )
    convo = "\n".join(
        f"Customer: {redact(t['user'])}\nReceptionist: {redact(t['reply'])}" for t in turns
    )
    resp = client.messages.create(
        model=model,
        max_tokens=1024,
        system=system,
        output_config={"format": {"type": "json_schema", "schema": _INSIGHT_SCHEMA}},
        messages=[{"role": "user", "content": convo}],
    )
    text = "".join(b.text for b in resp.content if b.type == "text")
    return json.loads(text)


def analyze_pending(
    now: datetime | None = None, idle_minutes: int = 30, limit: int = 200
) -> dict[str, int]:
    """Analyse every settled, not-yet-analysed conversation. Per-conversation failures are
    logged and skipped so one bad transcript never stalls the batch. Needs ANTHROPIC_API_KEY."""
    import anthropic

    settings.env("ANTHROPIC_API_KEY")
    now = now or datetime.now()
    cutoff = (now - timedelta(minutes=idle_minutes)).isoformat(timespec="seconds")
    pending = analytics.pending_for_analysis(cutoff, limit)
    client = anthropic.Anthropic()
    model = _analyst_model()
    done = failed = 0
    for session_key, slug in pending:
        turns = analytics.transcript(session_key)
        if not turns:
            continue
        try:
            ins = _analyze(client, model, settings.config_for(slug) or {}, turns)
            analytics.save_insight(session_key, slug, model, ins)
            done += 1
        except Exception as exc:  # a bad transcript must not stall the batch
            log.warning("analyst failed for %s: %s", session_key, exc)
            failed += 1
    return {"analyzed": done, "failed": failed, "pending": len(pending)}


def backlog(slug: str, limit: int = 100) -> str:
    """A human-readable maintenance/upsell view for one client, mined from its insights."""
    rows = analytics.insights_for_client(slug, limit)
    if not rows:
        return f"No insights yet for {slug} (run the analyst first)."
    unanswered: dict[str, int] = {}
    upsell: dict[str, int] = {}
    quality: dict[str, int] = {}
    escalations = neg = 0
    for r in rows:
        for q in r["unanswered_json"]:
            unanswered[q] = unanswered.get(q, 0) + 1
        for u in r["upsell_json"]:
            upsell[u] = upsell.get(u, 0) + 1
        for q in r["quality_json"]:
            quality[q] = quality.get(q, 0) + 1
        escalations += 1 if r.get("escalated") else 0
        neg += 1 if r.get("sentiment") == "neg" else 0

    def _top(counter: dict[str, int]) -> list[str]:
        return [f"    {n}× {k}" for k, n in sorted(counter.items(), key=lambda kv: -kv[1])[:10]]

    out = [
        f"{_client_name(slug)} — {len(rows)} analysed conversation(s)",
        f"  escalations: {escalations} · negative sentiment: {neg}",
    ]
    if quality:
        out.append("  quality flags (review the bot):")
        out.extend(_top(quality))
    if unanswered:
        out.append("  unanswered questions (FAQ gaps):")
        out.extend(_top(unanswered))
    if upsell:
        out.append("  upsell signals:")
        out.extend(_top(upsell))
    return "\n".join(out)


def main(argv: list[str]) -> int:
    cmd = argv[1] if len(argv) > 1 else ""
    if cmd == "digest":
        today = "--today" in argv
        text = build_digest(today=today, mail=True)
        if "--dry" in argv:
            print(text)
            return 0
        delivered = send_digest(today=today, text=text)
        print(text)
        took = [channel for channel, ok in delivered.items() if ok]
        if took:
            print(f"\n[sent via {', '.join(took)}]")
            return 0
        print(
            "\n[NOT sent — nowhere to deliver it. Set OWNER_TELEGRAM_CHAT_ID "
            "(python -m app.notify chatid), or OWNER_EMAIL + RESEND_API_KEY.]"
        )
        return 1
    if cmd == "analyze":
        result = analyze_pending()
        print(
            f"analyst: {result['analyzed']} analysed, {result['failed']} failed, "
            f"{result['pending']} were pending"
        )
        return 0
    if cmd == "insights" and len(argv) > 2:
        print(backlog(argv[2]))
        return 0
    print("usage: python -m app.oversight {digest [--dry] [--today] | analyze | insights <slug>}")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
