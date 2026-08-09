"""Tool definitions the receptionist can call, plus their handlers.

Core tools (every business): look up open slots, book one, take a message. Listings tools
(only businesses with a `listings:` config block — real-estate clients): search inventory
and register a qualified buyer lead. Handlers return JSON strings so Claude gets
structured data back.
"""

from __future__ import annotations

import json
from typing import Any

from . import calendar_store, listings_store, notify
from .settings import business

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
            "check_availability. For an on-site visit, also pass the customer's full service "
            "address (street + number + postcode + town) so the team knows where to go."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_name": {"type": "string"},
                "contact": {"type": "string", "description": "Phone or email."},
                "service": {"type": "string"},
                "slot": {"type": "string", "description": "Exact slot as 'YYYY-MM-DD HH:MM'."},
                "address": {
                    "type": "string",
                    "description": (
                        "The customer's full service address for an on-site visit: street + "
                        "number, postcode and town. Leave empty only if the visit is not on-site."
                    ),
                },
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

# Only offered to businesses with a `listings:` block in their config (real-estate
# clients) — a salon or plumber never sees these.
LISTINGS_TOOLS: list[dict[str, Any]] = [
    {
        "name": "search_listings",
        "description": (
            "Search the property inventory for listings matching the buyer's criteria. "
            "Call this once you know at least a budget or a location — refine as you "
            "learn more. Only ever present properties this tool returned; never invent "
            "listings, prices, or availability."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["sale", "rent"],
                    "description": "Buying = sale, long-term renting = rent.",
                },
                "locations": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Towns/areas the buyer wants, e.g. ['Estepona','Marbella'].",
                },
                "min_price": {"type": "integer"},
                "max_price": {"type": "integer", "description": "Budget ceiling in EUR."},
                "min_bedrooms": {"type": "integer"},
                "min_bathrooms": {"type": "integer"},
                "property_type": {
                    "type": "string",
                    "description": "E.g. apartment, penthouse, villa, townhouse.",
                },
                "features": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Must-have features, e.g. ['pool','sea views'].",
                },
                "max_results": {"type": "integer", "description": "Default 5."},
            },
        },
    },
    {
        "name": "register_buyer_lead",
        "description": (
            "Register a qualified lead — buyer, seller, renter or existing client — so "
            "the right human agent follows up. Call this once you have the customer's "
            "name, a contact (phone or email), their intent and their timeline; for "
            "buyers/renters typically after showing them matches (pass the references "
            "of listings they liked). If the result has ok: false, apologize and give "
            "the customer the business phone number instead — do not claim the lead "
            "was passed on."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_name": {"type": "string"},
                "contact": {"type": "string", "description": "Phone or email."},
                "intent": {
                    "type": "string",
                    "enum": ["buyer", "seller", "renter", "existing"],
                    "description": (
                        "Why they contacted us: buying, selling, renting, or an "
                        "existing client of the agency."
                    ),
                },
                "timeline": {
                    "type": "string",
                    "enum": ["0-3", "3-12", "12+", "browsing"],
                    "description": (
                        "Months until they want to move/complete; 'browsing' when "
                        "they are only orienting. Always ask before registering."
                    ),
                },
                "financing": {
                    "type": "string",
                    "enum": ["cash", "mortgage_arranged", "mortgage_needed", "unknown"],
                    "description": "How the purchase would be funded, if discussed.",
                },
                "property_address": {
                    "type": "string",
                    "description": (
                        "Sellers only: the property to sell, confirmed by reading it "
                        "back to the customer."
                    ),
                },
                "valuation_booked": {
                    "type": "boolean",
                    "description": "Sellers only: true once a valuation visit is agreed.",
                },
                "operation": {"type": "string", "enum": ["sale", "rent"]},
                "locations": {"type": "array", "items": {"type": "string"}},
                "min_price": {"type": "integer"},
                "max_price": {"type": "integer"},
                "min_bedrooms": {"type": "integer"},
                "language": {
                    "type": "string",
                    "description": "Conversation language code, e.g. en, nl, es, de.",
                },
                "references": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "References of listings the customer liked.",
                },
                "notes": {
                    "type": "string",
                    "description": "Timeline, financing status, viewing wishes, extras.",
                },
            },
            "required": ["customer_name", "contact"],
        },
    },
]


def for_business() -> list[dict[str, Any]]:
    """The tool set for the active tenant: core tools, plus listings tools when the
    config has a `listings:` block."""
    if business().get("listings"):
        return TOOLS + LISTINGS_TOOLS
    return TOOLS


def execute(name: str, tool_input: dict[str, Any]) -> str:
    if name == "check_availability":
        return json.dumps(calendar_store.availability(tool_input.get("date")))
    if name == "book_appointment":
        return json.dumps(
            calendar_store.book(
                customer_name=tool_input.get("customer_name", ""),
                contact=tool_input.get("contact", ""),
                service=tool_input.get("service", ""),
                slot=tool_input.get("slot", ""),
                address=tool_input.get("address", ""),
            )
        )
    if name == "take_message":
        return json.dumps(
            notify.take_message(
                customer=tool_input.get("customer_name", "unknown"),
                contact=tool_input.get("contact", "no contact"),
                message=tool_input.get("message", ""),
            )
        )
    if name == "search_listings":
        return json.dumps(listings_store.search(tool_input), ensure_ascii=False)
    if name == "register_buyer_lead":
        criteria = {
            k: v
            for k, v in tool_input.items()
            if k not in ("customer_name", "contact", "references", "notes") and v
        }
        return json.dumps(
            listings_store.register_lead(
                customer_name=tool_input.get("customer_name", "unknown"),
                contact=tool_input.get("contact", "no contact"),
                criteria=criteria,
                references=tool_input.get("references") or [],
                notes=tool_input.get("notes", ""),
            )
        )
    return json.dumps({"error": f"Unknown tool: {name}"})
