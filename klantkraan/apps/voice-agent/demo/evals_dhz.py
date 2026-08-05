"""Eval harness for the DHZ Autoservice garage voice agent: simulated calls, no phone.

    python3 evals_dhz.py                 # list scenarios
    python3 evals_dhz.py run <name>      # run one scenario
    python3 evals_dhz.py run all         # run every scenario; exit 1 on failure

Same simulate-conversation pattern as evals.py (DRS). Webhook tools do not fire
during simulation, so lookup_kenteken is mocked with an RDW-shaped payload and
lookup_address with a PDOK-shaped one. The mock returns the same payload on every
call, so the wrong-plate scenario tests the empty-result ladder instead of a
second, corrected hit. Reads ELEVENLABS_API_KEY and ELEVENLABS_DHZ_AGENT_ID
from ../.env.
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


def rdw(kenteken: str, merk: str, model: str, kleur: str, toelating: str) -> str:
    """An RDW opendata response like the real lookup_kenteken webhook returns."""
    return json.dumps(
        [
            {
                "kenteken": kenteken,
                "merk": merk,
                "handelsbenaming": model,
                "eerste_kleur": kleur,
                "datum_eerste_toelating": toelating,
            }
        ]
    )


def pdok(*weergavenamen: str) -> str:
    """A PDOK locatieserver response like the real lookup_address webhook returns."""
    docs = [{"weergavenaam": w} for w in weergavenamen]
    return json.dumps({"response": {"numFound": len(docs), "docs": docs}})


PERSONA_BASE = (
    "Je speelt een Nederlandse beller die een autogarage belt. Spreek uitsluitend "
    "Nederlands, in korte spreektaal-zinnen zoals aan de telefoon. Geef alleen "
    "informatie waar de assistent om vraagt, niet alles tegelijk. Als de assistent "
    "het gesprek samenvat en afrondt, bedank kort en beëindig het gesprek. "
)

SCENARIOS: list[dict] = [
    {
        "name": "apk-afspraak",
        "about": "APK booking, kenteken via spelling names, RDW readback check",
        "persona": PERSONA_BASE
        + "Je wilt een APK-keuring voor je auto, het liefst dinsdag ochtend. Je kenteken "
        "is R331FG; zeg het precies zo: 'er, drie drie één, ferdinand gerard'. Je rijdt "
        "een grijze Volkswagen Polo. Je heet Henk Jansen. Vroeg in het gesprek vraag je "
        "één keer: 'Wat kost een APK bij jullie?'. Als naar je telefoonnummer wordt "
        "gevraagd of ernaar verwezen wordt: terugbellen op dit nummer is prima.",
        "mock_kenteken": rdw("R331FG", "VOLKSWAGEN", "POLO", "GRIJS", "20180614"),
        "mock_address": pdok(),
        "criteria": {
            "car_readback": "De assistent bevestigde de auto door merk en model (en bij "
            "voorkeur bouwjaar) uit de kenteken-opzoeker voor te lezen, bijvoorbeeld een "
            "Volkswagen Polo, en liet de beller bevestigen dat het klopt. Fout is: geen "
            "controle, of een auto noemen die niet uit de opzoeker komt.",
            "apk_vanaf_price": "Op de prijsvraag noemde de assistent uitsluitend 'vanaf "
            "vijftig euro' voor de APK; geen totaalprijs of ander bedrag.",
            "no_agenda_promise": "De assistent beloofde geen definitieve dag of tijd, maar "
            "noteerde de wens (dinsdag ochtend) en zei dat een collega terugbelt om de "
            "afspraak te bevestigen.",
        },
    },
    {
        "name": "kenteken-onvindbaar",
        "about": "plate not in RDW: one retry teken-voor-teken, then note literally",
        "persona": PERSONA_BASE
        + "Je wilt een kleine onderhoudsbeurt. Je kenteken is ZH882L; zeg het als 'zet ha, "
        "acht acht twee, el'. Waarom het niet gevonden wordt weet je niet, en je vertelt "
        "niet uit jezelf iets over je auto. Als de assistent vraagt het kenteken teken "
        "voor teken te zeggen, zeg je: 'zet, ha, acht, acht, twee, el'. Je rijdt een "
        "blauwe Skoda Fabia uit tweeduizend twintig; dat vertel je alleen als ernaar "
        "gevraagd wordt. Je heet Petra de Groot en terugbellen op dit nummer is prima. Een "
        "voorkeursdag heb je niet, volgende week vrijdag zou kunnen.",
        "mock_kenteken": "[]",
        "mock_address": pdok(),
        "criteria": {
            "no_invented_car": "De assistent noemde nooit zelf een merk, model of bouwjaar "
            "dat niet door de beller was gezegd; na een lege zoekopdracht werd geen auto "
            "verzonnen.",
            "fallback_ladder": "Na de mislukte zoekopdracht vroeg de assistent het kenteken "
            "één keer teken voor teken, en toen dat ook niets opleverde noteerde hij het "
            "kenteken letterlijk en vroeg hij het merk en type gewoon uit, zonder er een "
            "punt van te maken of te blijven doorvragen.",
            "lead_complete": "Naam, terugbelnummer, kenteken (letterlijk genoteerd) en merk "
            "en type zijn vastgelegd, en de samenvatting zei dat een collega terugbelt.",
        },
    },
    {
        "name": "prijsdruk",
        "about": "grote beurt + caller pushes for an all-in price",
        "persona": PERSONA_BASE
        + "Je wilt een grote beurt voor je Renault Clio. Voordat je je kenteken geeft "
        "vraag je eerst: 'Wat kost een grote beurt?'. Welk antwoord je ook krijgt, je "
        "dringt daarna nog één keer aan met precies deze vraag: 'Kan het voor "
        "tweehonderd euro all-in?'. Pas daarna werk je gewoon mee. Je kenteken is "
        "KL789B, zeg het als 'ka el, zeven acht negen, bee'. Je heet Fatima Yildiz en "
        "terugbellen op dit nummer is prima. Donderdag middag komt je het beste uit.",
        "mock_kenteken": rdw("KL789B", "RENAULT", "CLIO", "BLAUW", "20160321"),
        "mock_address": pdok(),
        "criteria": {
            "only_vanaf_price": "De assistent noemde als prijs uitsluitend 'vanaf "
            "tweehonderdvijftig euro' voor de grote beurt en gaf nooit een totaalprijs, "
            "schatting of ander bedrag, ook niet toen de beller tweehonderd euro all-in "
            "voorstelde; de monteur bevestigt de precieze prijs vooraf.",
            "no_allin_agreement": "De assistent ging niet akkoord met tweehonderd euro "
            "all-in en wekte ook niet de indruk dat dat zou kunnen.",
            "kept_collecting": "Na de prijsdruk verzamelde de assistent gewoon de rest van "
            "de gegevens en rondde het gesprek netjes af met de terugbel-afspraak.",
        },
    },
    {
        "name": "pech-onderweg",
        "about": "breakdown in Hilversum: reassure, locate via lookup, no arrival promise",
        "persona": PERSONA_BASE
        + "Je staat met pech: je auto start niet meer, waarschijnlijk de accu, en je "
        "staat geparkeerd langs de Larenseweg ter hoogte van nummer dertig in Hilversum. "
        "Je bent gehaast en een beetje gestrest. Je kenteken is XN205P, zeg het als "
        "'iks en, twee nul vijf, pee'. Je heet Kees Vermeulen en terugbellen op dit "
        "nummer is prima. Je vraagt één keer: 'Hoe snel kunnen jullie er zijn?'.",
        "mock_kenteken": rdw("XN205P", "FORD", "FOCUS", "ZWART", "20150910"),
        "mock_address": pdok("Larenseweg 30, 1221CL Hilversum"),
        "criteria": {
            "location_readback": "De assistent zocht de locatie op en las de gevonden "
            "straat en plaats (Larenseweg, Hilversum) voor ter controle, of bevestigde de "
            "locatie expliciet.",
            "no_arrival_time": "De assistent noemde nooit een concrete aanrijtijd of hoe "
            "laat iemand er is; alleen dat het team het zo snel mogelijk oppakt en de "
            "collega die terugbelt zegt hoe laat.",
            "reassured": "De assistent gaf de gestreste beller eerst kort erkenning of "
            "geruststelling voordat hij verder ging met vragen.",
        },
    },
    {
        "name": "storing-prijs",
        "about": "warning light, price of uitlezen is not in the fixed facts",
        "persona": PERSONA_BASE
        + "Er brandt een geel motorlampje op je dashboard en je wilt de storing laten "
        "uitlezen. Je vraagt vroeg in het gesprek: 'Wat kost dat uitlezen?'. Je kenteken "
        "is TB446X, zeg het als 'tee bee, vier vier zes, iks'. Je rijdt een rode Toyota "
        "Aygo. Je heet Samira el Amrani en terugbellen op dit nummer is prima. Morgen "
        "einde van de middag zou mooi zijn.",
        "mock_kenteken": rdw("TB446X", "TOYOTA", "AYGO", "ROOD", "20190405"),
        "mock_address": pdok(),
        "criteria": {
            "no_invented_price": "Voor het uitlezen van de storing noemde de assistent "
            "geen enkel bedrag (uitlezen staat niet in de prijslijst): hij zei eerlijk "
            "dat de monteur of de collega die terugbelt de prijs bevestigt. Een "
            "vanafprijs voor een andere genoemde dienst is toegestaan.",
            "no_diy_advice": "De assistent gaf geen doe-het-zelf-diagnose of technisch "
            "advies over het motorlampje, maar bood een afspraak aan.",
            "lead_complete": "Naam, terugbelnummer, kenteken en de storing zijn "
            "vastgelegd, met de gewenste dag, en de samenvatting zei dat een collega "
            "terugbelt om de afspraak te bevestigen.",
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
                "lookup_kenteken": {
                    "default_return_value": scenario["mock_kenteken"],
                    "default_is_error": False,
                },
                "lookup_address": {
                    "default_return_value": scenario["mock_address"],
                    "default_is_error": False,
                },
            },
        },
        "extra_evaluation_criteria": [
            {"id": cid, "name": cid, "conversation_goal_prompt": prompt}
            for cid, prompt in scenario["criteria"].items()
        ],
        "new_turns_limit": 30,
    }
    agent = env("ELEVENLABS_DHZ_AGENT_ID")
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
            print(f"  {s['name']:<20} {s['about']}")
        print("\nrun with: python3 evals_dhz.py run <name|all>")
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
