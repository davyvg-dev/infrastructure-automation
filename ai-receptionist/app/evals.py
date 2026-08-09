"""Chat evals for the real-estate qualification flows — the text analog of the voice
agent's demo/evals.py: an LLM plays the customer, the REAL receptionist (prompt, tools,
config) answers, and an LLM judge scores the transcript against per-scenario criteria.

    ./.venv/bin/python -m app.evals            # list scenarios
    ./.venv/bin/python -m app.evals run buyer  # one scenario, print transcript + verdicts
    ./.venv/bin/python -m app.evals run all    # every scenario; exit 1 if any criterion fails

Online (Anthropic API); leads and bookings land in a throwaway DATA_DIR, never data/.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from typing import Any

import anthropic

from . import settings

# The receptionist runs on its config model; the simulated customer and the judge run on
# the current Opus. Low effort for the role-play, full effort for judging.
SIM_MODEL = "claude-opus-5"
JUDGE_MODEL = "claude-opus-5"
MAX_TURNS = 12

PERSONA_BASE = (
    "You are role-playing a CUSTOMER texting with a real-estate agency's chat "
    "assistant. Write short, natural chat messages in English, one message per turn. "
    "Only give information the assistant asks for — don't volunteer everything at "
    "once. Never break character, never mention this is a simulation. When your goal "
    "below is met and the assistant has wrapped up, reply with exactly [END]. "
)

SCENARIOS: list[dict[str, Any]] = [
    {
        "name": "buyer",
        "about": "qualified cash buyer, all five fields, lead registered",
        "client": "solvista-demo",
        "persona": PERSONA_BASE
        + "Your goal: find an apartment to buy and leave your contact details. You are "
        "Anna Keller (anna.keller@example.com). You want to buy an apartment in "
        "Estepona or Marbella, up to 300,000 euros, at least 2 bedrooms, a pool would "
        "be nice. You want to move within the next 3 months and you are a cash buyer. "
        "When shown listings, pick one you like by its reference.",
        "criteria": {
            "ai_disclosure": (
                "The assistant's very first message disclosed that it is a digital or "
                "AI assistant."
            ),
            "required_fields_asked": (
                "Before or while registering the lead, the conversation established "
                "all five buyer fields: areas/towns, budget, bedrooms, timeline, and "
                "financing. The assistant asked for any the customer had not "
                "volunteered; none was skipped."
            ),
            "real_listings_only": (
                "Every property reference or price the assistant presented came from "
                "a search_listings tool result in this conversation — nothing "
                "invented."
            ),
            "lead_registered": (
                "register_buyer_lead was called with intent=buyer, a timeline value "
                "of 0-3, and financing=cash as structured fields."
            ),
        },
    },
    {
        "name": "seller",
        "about": "seller with address readback, valuation booked, lead registered",
        "client": "solvista-demo",
        "persona": PERSONA_BASE
        + "Your goal: sell your villa and get a valuation booked. You are Jorge Ruiz "
        "(+34 600 111 222). You want to sell your villa at Calle Los Naranjos 8, "
        "29602 Marbella — a 3-bedroom villa, recently renovated, good condition. You "
        "want it sold within the next year. Accept a free valuation and agree to the "
        "first time slot the assistant proposes.",
        "criteria": {
            "address_readback": (
                "The assistant repeated the property address back to the customer to "
                "confirm it before moving on."
            ),
            "valuation_booked": (
                "A valuation appointment was actually booked via the book_appointment "
                "tool, after checking availability — no invented time slots."
            ),
            "lead_registered": (
                "register_buyer_lead was called with intent=seller, the property "
                "address in property_address, a timeline value, and "
                "valuation_booked=true."
            ),
            "no_valuation_estimate": (
                "The assistant never estimated or guessed the property's market "
                "value — valuation is the human agent's job."
            ),
        },
    },
    {
        "name": "renter",
        "about": "renter with move-in date, rent search, lead registered",
        "client": "solvista-demo",
        "persona": PERSONA_BASE
        + "Your goal: rent a flat and leave your contact details. You are Lisa de "
        "Boer (lisa.deboer@example.com). You want to rent a 2-bedroom flat in "
        "Marbella, up to 1,700 euros per month, moving in next month. When shown a "
        "listing you like, say so by its reference; accept a viewing if offered.",
        "criteria": {
            "required_fields_asked": (
                "Before or while registering the lead, the conversation established "
                "the town, the monthly budget, the number of bedrooms, and the "
                "move-in timing; the assistant asked for any the customer had not "
                "volunteered."
            ),
            "rent_search": (
                "search_listings was called with operation=rent and the customer's "
                "criteria."
            ),
            "lead_registered": (
                "register_buyer_lead was called with intent=renter and a timeline "
                "value reflecting the move-in date."
            ),
        },
    },
    {
        "name": "existing",
        "about": "existing client: no re-qualification, honest, routed to agent",
        "client": "solvista-demo",
        "persona": PERSONA_BASE
        + "Your goal: get a callback about your ongoing purchase. You are Tom Bakker "
        "(+31 6 12 34 56 78), already buying property SV-1002 through this agency "
        "with agent Maria. You want to know when the notary date is. If the "
        "assistant can't tell you, ask for a callback from Maria.",
        "criteria": {
            "no_requalification": (
                "The assistant did NOT run the buyer qualification script on this "
                "existing client — no questions about budget, bedrooms, or which "
                "towns to search."
            ),
            "no_invented_facts": (
                "The assistant did not invent the notary date or any other detail of "
                "the customer's file — it was honest about not having access."
            ),
            "lead_registered": (
                "register_buyer_lead was called with intent=existing and a note that "
                "tells the agent what the customer needs."
            ),
        },
    },
]


def _client() -> anthropic.Anthropic:
    settings.env("ANTHROPIC_API_KEY")
    return anthropic.Anthropic()


def _next_customer_message(
    client: anthropic.Anthropic, persona: str, transcript: list[tuple[str, str]]
) -> str:
    """The simulated customer's next message. The conversation is presented from the
    customer's perspective: assistant (agency) turns become user turns and vice versa."""
    messages = [
        {"role": "user" if speaker == "bot" else "assistant", "content": text}
        for speaker, text in transcript
        if speaker in ("bot", "you")
    ]
    response = client.messages.create(
        model=SIM_MODEL,
        max_tokens=200,
        output_config={"effort": "low"},
        system=persona,
        messages=messages,
    )
    return next((b.text for b in response.content if b.type == "text"), "").strip()


def _judge(
    client: anthropic.Anthropic, criteria: dict[str, str], transcript_text: str
) -> dict[str, dict[str, Any]]:
    """Score the transcript against every criterion; returns {id: {passed, rationale}}."""
    schema = {
        "type": "object",
        "properties": {
            cid: {
                "type": "object",
                "properties": {
                    "passed": {"type": "boolean"},
                    "rationale": {"type": "string"},
                },
                "required": ["passed", "rationale"],
                "additionalProperties": False,
            }
            for cid in criteria
        },
        "required": list(criteria),
        "additionalProperties": False,
    }
    criteria_text = "\n".join(f"- {cid}: {text}" for cid, text in criteria.items())
    response = client.messages.create(
        model=JUDGE_MODEL,
        max_tokens=2000,
        output_config={"format": {"type": "json_schema", "schema": schema}},
        messages=[
            {
                "role": "user",
                "content": (
                    "You are grading a chat transcript between a real-estate "
                    "agency's AI receptionist ('bot') and a simulated customer "
                    "('you'). Lines starting with [tool] are the actual tool calls "
                    "the receptionist made, with their inputs and outputs — treat "
                    "them as ground truth. Judge each criterion strictly on the "
                    "evidence in the transcript.\n\nCriteria:\n"
                    f"{criteria_text}\n\nTranscript:\n{transcript_text}"
                ),
            }
        ],
    )
    text = next(b.text for b in response.content if b.type == "text")
    return json.loads(text)


def run_scenario(scenario: dict[str, Any]) -> bool:
    from . import calendar_store, receptionist

    print(f"\n=== {scenario['name']} — {scenario['about']}")
    client = _client()
    token = settings.use_slug(scenario["client"])
    orig_dir, orig_cal = settings.DATA_DIR, calendar_store.DATA_DIR
    transcript: list[tuple[str, str]] = []

    def say(speaker: str, text: str) -> None:
        transcript.append((speaker, text))
        print(f"  {speaker:>5}: {text}" if speaker != "tool" else f"   tool: {text}")

    try:
        with tempfile.TemporaryDirectory() as tmp:
            settings.DATA_DIR = Path(tmp)
            calendar_store.DATA_DIR = Path(tmp)
            say("bot", receptionist.greeting())
            history: list = []
            for _ in range(MAX_TURNS):
                msg = _next_customer_message(client, scenario["persona"], transcript)
                if not msg or msg == "[END]":
                    break
                say("you", msg)
                telemetry = {"input_tokens": 0, "output_tokens": 0, "tools": [], "model": ""}
                reply, history = receptionist.run_turn(history, msg, telemetry)
                for call in telemetry["tools"]:
                    say(
                        "tool",
                        f"{call['name']}({json.dumps(call['input'], ensure_ascii=False)}) "
                        f"-> {str(call['output'])[:300]}",
                    )
                say("bot", reply)
    finally:
        settings.DATA_DIR, calendar_store.DATA_DIR = orig_dir, orig_cal
        settings.clear_slug(token)

    transcript_text = "\n".join(
        f"[tool] {text}" if speaker == "tool" else f"{speaker}: {text}"
        for speaker, text in transcript
    )
    verdicts = _judge(client, scenario["criteria"], transcript_text)
    ok = True
    for cid, verdict in verdicts.items():
        if not verdict["passed"]:
            ok = False
        mark = "PASS" if verdict["passed"] else "FAIL"
        print(f"  [{mark}] {cid}: {verdict['rationale'].strip()}")
    return ok


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print("scenarios:")
        for s in SCENARIOS:
            print(f"  {s['name']:<10} {s['about']}")
        print("\nrun with: python -m app.evals run <name|all>")
        return
    if args[0] != "run" or len(args) != 2:
        sys.exit(__doc__)
    which = [s for s in SCENARIOS if args[1] in ("all", s["name"])]
    if not which:
        sys.exit(f"unknown scenario '{args[1]}'")
    failed = [s["name"] for s in which if not run_scenario(s)]
    if failed:
        sys.exit(f"\nFAILED: {', '.join(failed)}")
    print(f"\nall criteria passed ({len(which)} scenario{'s' if len(which) > 1 else ''})")


if __name__ == "__main__":
    main()
