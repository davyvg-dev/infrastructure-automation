"""The receptionist agent: builds a persona from the business config and runs a tool-use
loop against Claude for each customer turn.

Uses a manual agentic loop (not the beta tool-runner) so the flow is fully transparent —
easy to explain in build-in-public content and to hand to a client.
"""

from __future__ import annotations

from datetime import date
from typing import Any

import anthropic

from . import tools
from .settings import business, env


def build_system_prompt() -> str:
    cfg = business()
    b, p = cfg["business"], cfg["persona"]
    services = "\n".join(
        f"  - {s['name']} ({s.get('price', 'ask')}, {s.get('duration_min', '?')} min)"
        for s in cfg.get("services", [])
    )
    faq = "\n".join(f"  - Q: {f['q']}\n    A: {f['a']}" for f in cfg.get("faq", []))
    hours = "\n".join(f"  - {day}: {h[0]}–{h[1]}" for day, h in cfg.get("hours", {}).items())

    return f"""You are {p['name']}, the virtual receptionist for {b['name']}, a \
{b['type']} in {b.get('address', '')} ({b['timezone']} timezone).

Today's date is {date.today():%A, %Y-%m-%d}.

Tone: {p['tone']}

Your goals: {p['goals']}

Hard rules: {p['guardrails']}

Services:
{services or '  (none listed)'}

Opening hours (days not listed are closed):
{hours}

FAQ you can answer directly:
{faq or '  (none)'}

Phone for anything you can't handle: {b.get('phone', '(not provided)')}

Booking flow:
- Use check_availability to find real open slots before offering times. Never invent a slot.
- Collect the customer's name and a contact (phone or email) and confirm the service and
  time before calling book_appointment.
- After booking, read back the confirmation code and the date/time in plain language.
Keep every reply short and natural — you're chatting, not writing an email."""


def _client() -> anthropic.Anthropic:
    env("ANTHROPIC_API_KEY")
    return anthropic.Anthropic()


def greeting() -> str:
    return business().get("greeting", "Hi! How can I help?").strip()


def run_turn(history: list[dict[str, Any]], user_message: str) -> tuple[str, list[dict[str, Any]]]:
    """Append the user's message, run the tool-use loop to completion, return (reply, history)."""
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
            tools=tools.TOOLS,
            messages=history,
        )
        history = history + [{"role": "assistant", "content": response.content}]

        if response.stop_reason == "tool_use":
            results = []
            for block in response.content:
                if block.type == "tool_use":
                    results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": tools.execute(block.name, block.input),
                    })
            history = history + [{"role": "user", "content": results}]
            continue

        if response.stop_reason == "pause_turn":
            continue  # server-side pause; re-send to resume

        text = "".join(b.text for b in response.content if b.type == "text").strip()
        return text or "(no response)", history

    return "Sorry — I got stuck. Please call us and we'll help right away.", history
