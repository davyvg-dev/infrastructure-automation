"""Tool definitions the receptionist can call, plus their handlers.

Two tools: look up open slots, and book one. Handlers return JSON strings so Claude gets
structured data back.
"""

from __future__ import annotations

import json
from typing import Any

from . import calendar_store, notify

TOOLS: list[dict[str, Any]] = [
    {
        "name": "check_availability",
        "description": (
            "Look up open appointment slots. Call this before offering or booking any time. "
            "Optionally pass a specific date; otherwise it returns the next few open days."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "Optional specific day in YYYY-MM-DD format.",
                },
            },
        },
    },
    {
        "name": "book_appointment",
        "description": (
            "Book a specific open slot. Only call this after you have the customer's name, "
            "a contact (phone or email), the service, and a slot confirmed open by "
            "check_availability."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_name": {"type": "string"},
                "contact": {"type": "string", "description": "Phone or email."},
                "service": {"type": "string"},
                "slot": {"type": "string", "description": "Exact slot as 'YYYY-MM-DD HH:MM'."},
            },
            "required": ["customer_name", "contact", "service", "slot"],
        },
    },
    {
        "name": "take_message",
        "description": (
            "Capture a message for the human team when you can't fully help — a question "
            "you can't answer, a special request, a complaint, or a callback request. "
            "Always collect the customer's name and a contact first. This saves the "
            "message and notifies the owner so a human can follow up. If the result has "
            "ok: false, apologize and give the customer the business phone number instead "
            "— do not claim the message was passed on."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_name": {"type": "string"},
                "contact": {"type": "string", "description": "Phone or email."},
                "message": {"type": "string", "description": "What to pass to the team."},
            },
            "required": ["customer_name", "contact", "message"],
        },
    },
]


def execute(name: str, tool_input: dict[str, Any]) -> str:
    if name == "check_availability":
        return json.dumps(calendar_store.availability(tool_input.get("date")))
    if name == "book_appointment":
        return json.dumps(calendar_store.book(
            customer_name=tool_input.get("customer_name", ""),
            contact=tool_input.get("contact", ""),
            service=tool_input.get("service", ""),
            slot=tool_input.get("slot", ""),
        ))
    if name == "take_message":
        return json.dumps(notify.take_message(
            customer=tool_input.get("customer_name", "unknown"),
            contact=tool_input.get("contact", "no contact"),
            message=tool_input.get("message", ""),
        ))
    return json.dumps({"error": f"Unknown tool: {name}"})
