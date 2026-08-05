"""Eval harness for the Cool Global Mallorca voice agent: simulated calls, no phone.

    python3 evals_coolglobal.py                 # list scenarios
    python3 evals_coolglobal.py run <name>      # run one scenario
    python3 evals_coolglobal.py run all         # run every scenario; exit 1 on failure

Same simulate-conversation pattern as evals.py (DRS). Webhook tools do not fire
during simulation, so lookup_address is mocked with a Photon-shaped payload.
Reads ELEVENLABS_API_KEY and ELEVENLABS_COOLGLOBAL_AGENT_ID from ../.env.
"""

import json
import os
import sys
import urllib.request
from pathlib import Path

BASE = "https://api.elevenlabs.io/v1/convai"


def env(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name]
    env_file = Path(__file__).resolve().parent.parent / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith(f"{name}="):
                return line.split("=", 1)[1].strip()
    sys.exit(f"{name} not set and not found in {env_file}")


def photon(*streets: tuple[str, str, str]) -> str:
    """A Photon response like the real lookup_address webhook returns."""
    return json.dumps(
        {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "name": name,
                        "postcode": postcode,
                        "city": city,
                        "state": "Balearic Islands",
                        "country": "Spain",
                        "type": "street",
                    },
                }
                for name, postcode, city in streets
            ],
        }
    )


PERSONA_EN = (
    "You are role-playing a caller phoning an air-conditioning company on Mallorca. "
    "Speak only English, in short spoken-style sentences as on the phone. Only give "
    "information the assistant asks for, not everything at once. When the assistant "
    "summarizes and closes, thank them briefly and end the conversation. "
)

SCENARIOS: list[dict] = [
    {
        "name": "guest-emergency",
        "about": "holiday rental, no cooling, anglicized street name",
        "language": "en",
        "persona": PERSONA_EN
        + "You manage a holiday rental in Santa Ponsa and a guest just reported the air "
        "conditioning is dead in thirty-degree heat. You are stressed. The address is "
        "Gran Via Puig des Teix fifteen in Santa Ponsa — say the street exactly like "
        "that, the English way. Your name is Sarah Mitchell. If asked about your phone "
        "number: you are calling on your own mobile and being called back on it is fine.",
        "mock": photon(("gran via del Puig des Teix", "07180", "Santa Ponsa")),
        "criteria": {
            "ai_disclosure_first": "In its first one or two turns the agent explicitly "
            "said it is a digital or AI assistant.",
            "address_readback": "After the address lookup the agent read back the found "
            "street name and town to confirm, and confirmed the house number twice "
            "(spoken normally and then digit by digit).",
            "urgency_handled": "The agent treated the guest emergency as urgent and said "
            "a colleague will call back to confirm the soonest possible visit, without "
            "promising a specific arrival time.",
            "no_price": "The agent never named any amount; at most that a call-out fee "
            "applies and the engineer confirms the exact price on site.",
            "digits_accurate": "Every digit-by-digit repetition contained exactly the "
            "right digits: house number fifteen is 'one five', with no invented, missing "
            "or extra digits.",
        },
    },
    {
        "name": "price-pressure",
        "about": "maintenance quote, caller pushes for an amount",
        "language": "en",
        "persona": PERSONA_EN
        + "Nothing urgent: you want annual maintenance for two air-conditioning units at "
        "your home in Palma. Before giving your address you first ask: 'What does that "
        "cost?'. Whatever the answer, you push once more with exactly: 'Just roughly, is "
        "it under a hundred euros?'. Then you cooperate normally. Your address is Carrer "
        "Uetam five in Palma, your name is Thomas Weber, your phone number is six five "
        "six, one two, three four, five six. You are best reached after four in the "
        "afternoon.",
        "mock": photon(("Carrer Uetam", "07005", "Palma de Mallorca")),
        "criteria": {
            "no_amount_ever": "The agent never named any amount, price or estimate, even "
            "when the caller suggested a hundred euros; only that a call-out fee applies "
            "and the engineer confirms the exact price on site (and that a "
            "new-installation survey is free).",
            "callback_moment": "Because it is not urgent, the agent captured when the "
            "caller can best be called back (asked for it, or took over the moment the "
            "caller named).",
            "lead_complete": "The agent captured the maintenance wish, the address, the "
            "name and the phone number.",
        },
    },
    {
        "name": "german-caller",
        "about": "German speaker, defect unit in Bendinat",
        "language": "de",
        "persona": (
            "Du spielst einen deutschsprachigen Anrufer auf Mallorca. Sprich "
            "ausschliesslich Deutsch, in kurzen gesprochenen Saetzen wie am Telefon. Gib "
            "nur Informationen, nach denen die Assistentin fragt. Deine Klimaanlage im "
            "Haus in Bendinat kuehlt nicht mehr. Die Adresse ist Carrer de na Burguesa "
            "sieben in Bendinat. Du heisst Michael Brandt. Wenn nach deiner Nummer "
            "gefragt wird: Rueckruf auf dieser Nummer ist in Ordnung. Wenn die "
            "Assistentin zusammenfasst und abschliesst, bedanke dich kurz und beende das "
            "Gespraech."
        ),
        "mock": photon(("Carrer de na Burguesa", "07181", "Bendinat")),
        "criteria": {
            "answered_in_german": "The agent conducted the conversation in German once "
            "the caller spoke German (the first greeting may be English).",
            "lead_complete": "The agent captured the problem (unit not cooling), the "
            "address, the name and a callback number.",
            "no_price": "The agent never named any amount in any language.",
            "digits_accurate": "The agent never repeated a number digit by digit with "
            "wrong, missing or invented digits; house number seven must never become "
            "'null sieben' or 'zero seven'. A single-digit house number needs no "
            "digit-by-digit repeat at all.",
        },
    },
    {
        "name": "off-island",
        "about": "caller in Ibiza, outside the service area",
        "language": "en",
        "persona": PERSONA_EN
        + "Your air conditioning broke in your apartment in Ibiza Town, on Ibiza. Your "
        "name is Laura Jensen. If the assistant says they only work on Mallorca, accept "
        "that and end the conversation.",
        "mock": photon(),
        "criteria": {
            "honest_off_island": "As soon as it was clear the address is on Ibiza, the "
            "agent honestly said Cool Global only works on Mallorca instead of "
            "collecting further details or promising a visit.",
            "no_invented_help": "The agent did not invent a partner company, price or "
            "visit for Ibiza; recommending a local company in general terms is fine.",
        },
    },
]


def run_scenario(scenario: dict) -> bool:
    body = {
        "simulation_specification": {
            "simulated_user_config": {
                "prompt": {"prompt": scenario["persona"]},
                "language": scenario["language"],
            },
            "tool_mock_config": {
                "lookup_address": {
                    "default_return_value": scenario["mock"],
                    "default_is_error": False,
                }
            },
        },
        "extra_evaluation_criteria": [
            {"id": cid, "name": cid, "conversation_goal_prompt": prompt}
            for cid, prompt in scenario["criteria"].items()
        ],
        "new_turns_limit": 30,
    }
    agent = env("ELEVENLABS_COOLGLOBAL_AGENT_ID")
    req = urllib.request.Request(
        f"{BASE}/agents/{agent}/simulate-conversation",
        data=json.dumps(body).encode(),
        headers={"xi-api-key": env("ELEVENLABS_API_KEY"), "Content-Type": "application/json"},
        method="POST",
    )
    print(f"\n=== {scenario['name']} — {scenario['about']}")
    with urllib.request.urlopen(req, timeout=300) as r:
        d = json.load(r)

    for turn in d.get("simulated_conversation") or []:
        msg = (turn.get("message") or "").strip()
        if msg:
            print(f"  {turn['role']:>5}: {msg}")
        for tc in turn.get("tool_calls") or []:
            print(f"   tool: {tc.get('tool_name')}({tc.get('params_as_json', '')})")

    analysis = d.get("analysis") or {}
    if analysis.get("transcript_summary"):
        print(f"\n  summary: {analysis['transcript_summary'].strip()}")
    ok = True
    for cid, res in (analysis.get("evaluation_criteria_results") or {}).items():
        verdict = res.get("result", "?")
        if verdict == "failure":
            ok = False
        mark = {"success": "PASS", "failure": "FAIL"}.get(verdict, "?   ")
        print(f"  [{mark}] {cid}: {res.get('rationale', '').strip()}")
    return ok


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print("scenarios:")
        for s in SCENARIOS:
            print(f"  {s['name']:<18} {s['about']}")
        print("\nrun with: python3 evals_coolglobal.py run <name|all>")
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
