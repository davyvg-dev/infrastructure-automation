"""The receptionist agent: builds a persona from the business config and runs a tool-use
loop against Claude for each customer turn.

Uses a manual agentic loop (not the beta tool-runner) so the flow is fully transparent —
easy to explain in build-in-public content and to hand to a client.
"""

from __future__ import annotations

import json
import logging
from datetime import date
from typing import Any

import anthropic

from . import notify, tools
from .settings import business, env

log = logging.getLogger("receptionist")


def build_system_prompt() -> str:
    cfg = business()
    b, p = cfg["business"], cfg["persona"]
    services = "\n".join(
        f"  - {s['name']} ({s.get('price', 'ask')}, {s.get('duration_min', '?')} min)"
        for s in cfg.get("services", [])
    )
    faq = "\n".join(f"  - Q: {f['q']}\n    A: {f['a']}" for f in cfg.get("faq", []))
    hours = "\n".join(f"  - {day}: {h[0]}–{h[1]}" for day, h in cfg.get("hours", {}).items())

    # Scope of work: the receptionist must confidently take on ANY job within the business's
    # trade, not only the handful of priced line items in `services`. Without this frame, a
    # specific but perfectly in-scope request ("kunt u ons kantoor schilderen?") gets pushed
    # into the can't-help / take-a-message path. Scope is DERIVED from business.type by default
    # (so every config benefits with zero edits), and an optional `scope:` block tunes it:
    #   scope:
    #     does: "Alle schilderwerk binnen en buiten — woningen, kantoren, kozijnen, ..."
    #     does_not: "geen stukadoors- of dakwerk"
    scope_cfg = cfg.get("scope") or {}
    scope_does = str(scope_cfg.get("does", "")).strip()
    scope_does_not = str(scope_cfg.get("does_not", "")).strip()
    scope_does_line = f"\nSpecifically, this includes: {scope_does}" if scope_does else ""
    scope_does_not_line = (
        f"\n- Out of scope (a different trade): {scope_does_not}. For these, don't pretend to "
        "help — take a message or point them to the right kind of company."
        if scope_does_not
        else ""
    )

    # On-site trades (a plumber/electrician who comes to the customer) must know WHERE to go,
    # and whether the address is inside the service area — a config flag, off for come-to-us
    # businesses like a clinic or salon so their flow is untouched.
    booking_cfg = cfg.get("booking", {})
    onsite_block = ""
    if booking_cfg.get("onsite"):
        area = booking_cfg.get("service_area") or b.get("address", "the service area")
        onsite_block = f"""

# On-site visits (this business comes to the customer)
- Before you book, you MUST have the customer's full service address: street + number, postcode,
  and town. Ask for it in one step if it's missing. Pass it as `address` to book_appointment.
- Service area: {area}. If the address is clearly outside it, do NOT book. Say it's outside the
  area, and offer to take a message so the team can call back — use take_message.
- If you're unsure whether an address is in the area, take a message rather than promise a visit."""

    # Prescriptive, labeled sections with the most load-bearing rules at the top and the
    # "never do this" list at the bottom — where models attend most reliably.
    return f"""# Role
You are {p["name"]}, the virtual receptionist for {b["name"]}, a {b["type"]} in \
{b.get("address", "")} ({b["timezone"]} timezone). Today is {date.today():%A, %Y-%m-%d}.

# Tone
{p["tone"]} Keep every reply short and natural — you're chatting, not writing an email.
Ask at most one question per reply.

# Goals
{p["goals"]}

# Booking flow (follow exactly)
1. Call check_availability to find real open slots before offering any time. NEVER invent a slot.
2. Collect the customer's name and a contact (phone or email).
3. Confirm the service and the exact time back to the customer in plain language.
4. Only then call book_appointment. After it succeeds, read back the confirmation code and the date/time.
{onsite_block}

# What you know
Services (common jobs and their prices — a starting point, not the limit of what you do):
{services or "  (none listed)"}
Opening hours (days not listed are CLOSED):
{hours}
FAQ:
{faq or "  (none)"}

# What we do (scope of work)
{b["name"]} is a {b["type"]}. You confidently handle the FULL range of work that trade covers —
not only the specific services priced above.{scope_does_line}
- If a customer describes a job that fits this trade — even a large, unusual, or commercial one,
  and even if it isn't in the list above — say yes, we can help, and move toward booking. Never
  turn away a job that belongs to our trade.
- If the job has no fixed price, do NOT quote and do NOT refuse: offer a free inspection or quote
  (offerte) to confirm the price on site, and book that.{scope_does_not_line}

# When you can't help
This means a job for a DIFFERENT trade, a complaint, or a special request you genuinely can't
resolve — NOT an in-scope job (see scope above). For those, collect the customer's name + contact
and call take_message so a human follows up. For anything urgent, give the phone number:
{b.get("phone", "(not provided)")}.

# What you do NOT know — never guess these (these are facts, not the scope of your trade)
- Exact prices for jobs not in the list above — offer an inspection/offerte instead of quoting.
- Medical/clinical advice, outcomes, or DIY instructions for gas/electrical work.
- Availability you haven't confirmed with check_availability this conversation.
- Anything about a specific customer's history or records.
If asked about any of these, say you don't have that and offer to take a message or book a
consultation. Do not make up an answer. Lacking a fact is never a reason to turn away a job that
fits our trade — book an inspection instead.

# Hard rules
{p["guardrails"]}
- Never invent slots, prices, confirmations, or facts. If unsure, use a tool or take a message.
- Never turn away a job that fits our trade — confirm it and book an inspection or offerte.
- When you have enough information to act, act. When you've answered or booked, stop —
  don't pad with extra questions."""


def _client() -> anthropic.Anthropic:
    env("ANTHROPIC_API_KEY")
    return anthropic.Anthropic()


def greeting() -> str:
    return business().get("greeting", "Hi! How can I help?").strip()


def run_turn(
    history: list[dict[str, Any]],
    user_message: str,
    telemetry: dict[str, Any] | None = None,
) -> tuple[str, list[dict[str, Any]]]:
    """Append the user's message, run the tool-use loop to completion, return (reply, history).

    If `telemetry` is passed (a dict with 'input_tokens'/'output_tokens'/'tools'/'model'),
    it's filled in-place with token usage and the tool calls made this turn — the durable
    capture in sessions.respond reads it. Passing None keeps the loop untouched.
    """
    cfg = business()
    model_cfg = cfg["model"]
    client = _client()
    history = history + [{"role": "user", "content": user_message}]

    for _ in range(8):  # generous cap; a booking is 1-2 tool calls
        response = client.messages.create(
            model=model_cfg["id"],
            max_tokens=1024,
            thinking={"type": "adaptive"},
            output_config={"effort": model_cfg.get("effort", "low")},
            system=build_system_prompt(),
            tools=tools.for_business(),
            messages=history,
        )
        if telemetry is not None:
            usage = getattr(response, "usage", None)
            telemetry["input_tokens"] += int(getattr(usage, "input_tokens", 0) or 0)
            telemetry["output_tokens"] += int(getattr(usage, "output_tokens", 0) or 0)
            telemetry["model"] = model_cfg["id"]
        history = history + [{"role": "assistant", "content": response.content}]

        if response.stop_reason == "tool_use":
            results = []
            for block in response.content:
                if block.type == "tool_use":
                    # A tool that raises (a real calendar API timing out, once one is
                    # plugged into calendar_store) must not kill the customer's turn:
                    # hand the model an instructive error so it can recover in-chat.
                    failed = False
                    try:
                        output = tools.execute(block.name, block.input)
                    except Exception as exc:
                        failed = True
                        log.exception("tool %s failed", block.name)
                        notify.owner_exception(exc, context=f"tool {block.name}")
                        output = json.dumps(
                            {
                                "ok": False,
                                "error": "This system is temporarily unreachable. Do not "
                                "retry it now. Apologize, then take a message with "
                                "take_message, or give the customer the business phone "
                                "number.",
                            }
                        )
                    # Observable tool trace — you'll want this when debugging "why did it
                    # book the wrong slot?" support questions.
                    log.info("tool %s(%s) -> %s", block.name, block.input, output)
                    if telemetry is not None:
                        telemetry["tools"].append(
                            {"name": block.name, "input": block.input, "output": output}
                        )
                    results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": output,
                            "is_error": failed,
                        }
                    )
            history = history + [{"role": "user", "content": results}]
            continue

        if response.stop_reason == "pause_turn":
            continue  # server-side pause; re-send to resume

        text = "".join(b.text for b in response.content if b.type == "text").strip()
        return text or "(no response)", history

    log.warning("receptionist hit the turn cap without finishing")
    notify.owner(
        "⚠️ The receptionist got stuck on a conversation and couldn't finish. "
        "A customer may need a callback."
    )
    return "Sorry — I got stuck. Please call us and we'll help right away.", history
