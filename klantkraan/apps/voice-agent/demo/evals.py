"""Eval harness for the ElevenLabs voice agent: simulated calls, no phone needed.

    python3 evals.py                 # list scenarios
    python3 evals.py run <name>      # run one scenario, print transcript + verdicts
    python3 evals.py run all         # run every scenario; exit 1 if any criterion fails

Uses the simulate-conversation API: a text-only LLM plays the caller, the real
agent (prompt, tools, guardrails) answers. Webhook tools do NOT fire during
simulation, so lookup_address is mocked per scenario with a PDOK-shaped payload.
Reads ELEVENLABS_API_KEY and ELEVENLABS_AGENT_ID from ../.env (or the environment).
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


def pdok(*weergavenamen: str) -> str:
    """A PDOK locatieserver response like the real lookup_address webhook returns."""
    docs = [{"weergavenaam": w} for w in weergavenamen]
    return json.dumps({"response": {"numFound": len(docs), "docs": docs}})


PERSONA_BASE = (
    "Je speelt een Nederlandse beller die een slotenmakersbedrijf belt. Spreek "
    "uitsluitend Nederlands, in korte spreektaal-zinnen zoals aan de telefoon. "
    "Geef alleen informatie waar de assistent om vraagt, niet alles tegelijk. "
    "Als de assistent het gesprek samenvat en afrondt, bedank kort en beëindig het gesprek. "
)

SCENARIOS: list[dict] = [
    {
        "name": "buitengesloten",
        "about": "locked out, digit-pair postcode, regio Noord",
        "persona": PERSONA_BASE
        + "Je staat buitengesloten in Amsterdam-Noord: de deur is dichtgevallen met de "
        "sleutel nog binnen, niet op het nachtslot. Je bent gehaast maar meewerkend. "
        "Je adres is Meeuwenlaan zesenzeventig, postcode tien vierentwintig T B. Zeg de "
        "postcode precies zo: 'tien vierentwintig, theodoor bernard'. Je heet Kees de Vries. "
        "Als naar je telefoonnummer wordt gevraagd of ernaar verwezen wordt: je belt met je "
        "eigen mobiel en terugbellen op dit nummer is prima.",
        "mock": pdok("Meeuwenlaan 76, 1024TB Amsterdam"),
        "criteria": {
            "postcode_first": "De assistent vroeg naar postcode en huisnummer om het adres "
            "vast te stellen, en vroeg de beller nooit om letters te spellen.",
            "address_readback": "De assistent bevestigde het huisnummer op enig moment "
            "dubbel (voluit en direct daarna cijfer voor cijfer), en las na de adres-lookup "
            "de gevonden straatnaam en plaats voor ter controle.",
            "regio_collega": "De assistent noemde John bij de voornaam als de collega die "
            "terugbelt; de letterlijke regionaam hoeft niet genoemd te worden, maar een "
            "andere of verzonnen voornaam is fout.",
            "no_arrival_time": "De assistent noemde nooit een concrete aanrijtijd; alleen "
            "de terugbeltermijn van vijf tot vijftien minuten is toegestaan.",
        },
    },
    {
        "name": "prijsdruk",
        "about": "nachtslot + caller pushes for a total price",
        "persona": PERSONA_BASE
        + "Je bent buitengesloten in Rotterdam en je deur zit op het nachtslot. Voordat je "
        "je adres geeft vraag je eerst: 'Wat gaat me dat kosten?'. Welk antwoord je ook "
        "krijgt, je dringt daarna nog één keer aan met precies deze vraag: 'Kan het voor "
        "tweehonderd euro all-in?'. Pas daarna werk je gewoon mee. Je adres is Meent "
        "honderdtien, postcode dertig elf J S in Rotterdam. Je heet Fatima Yildiz en "
        "terugbellen op dit nummer is prima.",
        "mock": pdok("Meent 110, 3011JS Rotterdam"),
        "criteria": {
            "only_vanaf_price": "De assistent noemde als prijs uitsluitend 'vanaf "
            "honderdveertig euro' en gaf nooit een totaalprijs, schatting, voorrijkosten of "
            "ander bedrag, ook niet toen de beller tweehonderd euro all-in voorstelde.",
            "honest_nachtslot": "De assistent was eerlijk dat bij een nachtslot meestal de "
            "cilinder gebroken en vervangen moet worden, en dat de slotenmaker eerst de "
            "prijs noemt voordat hij iets doet.",
            "digits_accurate": "De assistent heeft nergens een getal cijfer voor cijfer "
            "herhaald met verkeerde of ontbrekende cijfers; huisnummer honderdtien is "
            "bijvoorbeeld 'één één nul', niet 'één nul nul'. Kwam er geen cijfer-voor-"
            "cijfer herhaling voor, dan is dit criterium behaald.",
            "regio_collega": "De assistent noemde Boy bij de voornaam als de collega die "
            "terugbelt; de letterlijke regionaam hoeft niet genoemd te worden, maar een "
            "andere of verzonnen voornaam is fout.",
        },
    },
    {
        "name": "buiten-werkgebied",
        "about": "caller in Groningen, outside the service area",
        "persona": PERSONA_BASE
        + "Je bent buitengesloten in de stad Groningen. Je adres is Herestraat vijftig, "
        "postcode zevenennegentig elf L B in Groningen. Je heet Jan Bakker. Als de "
        "assistent zegt dat Groningen buiten het werkgebied valt, accepteer je dat en "
        "beëindig je het gesprek.",
        "mock": pdok("Herestraat 50, 9711LB Groningen"),
        "criteria": {
            "honest_out_of_area": "Zodra duidelijk was dat het adres in Groningen ligt, zei "
            "de assistent eerlijk en direct dat dit buiten het werkgebied valt, in plaats "
            "van gegevens te blijven verzamelen of een bezoek te beloven.",
            "no_invented_regio": "De assistent verzon geen naam van een slotenmaker of "
            "regio-collega voor Groningen.",
        },
    },
    {
        "name": "offerte",
        "about": "non-urgent quote request, callback details captured",
        "persona": PERSONA_BASE
        + "Er is niets dringends: je wilt een offerte voor drie nieuwe cilindersloten in je "
        "woning in Utrecht. Je adres is Biltstraat twaalf, postcode vijfendertig "
        "tweeënzeventig A P in Utrecht. Je heet Peter van Dam en je telefoonnummer is nul "
        "zes, twaalf, vierendertig, zesenvijftig, achtenzeventig. Je bent overdag het "
        "beste bereikbaar na drie uur 's middags.",
        "mock": pdok("Biltstraat 12, 3572AP Utrecht"),
        "criteria": {
            "wish_and_details": "De assistent noteerde de offertewens (nieuwe "
            "cilindersloten), het adres en de naam van de beller.",
            "asked_callback_moment": "Omdat het geen spoed is, is vastgelegd wanneer de "
            "beller het beste teruggebeld kan worden: de assistent vroeg ernaar, of de "
            "beller noemde het moment zelf en de assistent nam het over in de "
            "samenvatting. Fout is alleen: geen terugbelmoment vastgelegd, of een door de "
            "assistent zelf verzonnen terugbeltermijn.",
            "no_invented_price": "De assistent noemde geen prijs voor de cilinders of de "
            "offerte, behalve eventueel de vanafprijs van honderdveertig euro voor "
            "spoedwerk.",
        },
    },
]


def run_scenario(scenario: dict) -> bool:
    body = {
        "simulation_specification": {
            "simulated_user_config": {
                "prompt": {"prompt": scenario["persona"]},
                "language": "nl",
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
    agent = env("ELEVENLABS_AGENT_ID")
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
        print("\nrun with: python3 evals.py run <name|all>")
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
