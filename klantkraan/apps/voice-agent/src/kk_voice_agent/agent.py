"""The receptionist brain: ports the Synthflow config to a stack we own.

- prompt source-of-truth: packages/prompts/nl/<vertical>.<client>.rendered.md
  (passed in as ``instructions``; this module keeps no second copy)
- tools mirror: packages/synthflow/agents/<vertical>.v1.json
- disclosure verbatim: docs/04-legal/ai-act-disclosure.md
"""

from __future__ import annotations

import asyncio
import json
import urllib.request

from livekit.agents import Agent, RunContext, function_tool

from .config import ClientConfig
from .disclosure import render_disclosure


class KlantkraanReceptionist(Agent):
    def __init__(self, instructions: str, client: ClientConfig) -> None:
        super().__init__(instructions=instructions)
        self._client = client

    async def on_enter(self) -> None:
        # say() speaks exact text (no LLM paraphrase) -- required for the
        # non-waivable art. 50 disclosure. Interruption-lock verified in phase 3.
        await self.session.say(
            render_disclosure(self._client.agent_naam, self._client.client_name)
        )

    @function_tool()
    async def schedule_callback(
        self,
        context: RunContext,
        caller_name: str,
        caller_phone: str,
        job_summary: str,
        intent: str,
        urgency: str,
        postcode: str | None = None,
        preferred_window: str | None = None,
    ) -> str:
        """Leg een terugbelverzoek vast voor de eigenaar. Gebruik bij NIEUW_WERK
        of BESTAANDE_KLANT. Zet nooit zelf een agenda-afspraak zonder dat de
        beller datum en tijd expliciet heeft bevestigd.

        Args:
            caller_name: Voor- en achternaam van de beller.
            caller_phone: Telefoonnummer in E.164, bijv. +31612345678.
            job_summary: Korte omschrijving van de klus (max ~200 tekens).
            intent: Een van NIEUW_WERK, BESTAANDE_KLANT, LEVERANCIER.
            urgency: Een van LOW, MED, HIGH.
            postcode: Postcode + huisnummer.
            preferred_window: Bijv. 'binnen 4 uur', 'morgenochtend', 'deze week'.
        """
        c = self._client
        await _post_json(
            f"{c.api_base_url}/api/voice/callback",
            {
                "clientId": c.client_id,
                "callerName": caller_name,
                "callerPhone": caller_phone,
                "postcode": postcode,
                "jobSummary": job_summary,
                "intent": intent,
                "urgency": urgency,
                "preferredWindow": preferred_window,
            },
        )
        return (
            f"Genoteerd. {c.owner_naam} belt {caller_name} terug op "
            f"{_spell_out(caller_phone)}, binnen 4 uur op werkdagen. "
            "Bevestig dit kort naar de beller en spel het nummer terug."
        )

    @function_tool()
    async def transfer_emergency(
        self,
        context: RunContext,
        spoed_type: str,
        caller_phone: str,
        summary: str,
        address: str | None = None,
    ) -> str:
        """Verbind direct door naar de eigenaar bij SPOED (water-overstroming,
        gaslucht, geen warm water in de winter, CV-storing bij vorst,
        riool-overstort). Roep dit aan VOOR het uitvragen van extra gegevens.

        Args:
            spoed_type: WATER_OVERSTROMING, GASLUCHT, GEEN_WARM_WATER_WINTER,
                CV_STORING_VORST, RIOOL_OVERSTORT of OVERIG_SPOED.
            caller_phone: Telefoonnummer in E.164.
            summary: Een zin samenvatting voor de eigenaar.
            address: Adres incl. postcode.
        """
        c = self._client
        await _post_json(
            f"{c.api_base_url}/api/voice/emergency",
            {
                "clientId": c.client_id,
                "transferTo": c.escalation_number,
                "priority": "HIGH",
                "spoedType": spoed_type,
                "callerPhone": caller_phone,
                "address": address,
                "summary": summary,
            },
        )
        # Actual SIP transfer (REFER to escalation_number) is wired in the
        # telephony layer -- see README phase 3.
        return (
            f"Spoed gemeld bij {c.owner_naam}. Zeg tegen de beller: "
            '"Ik verbind u direct door, blijft u aan de lijn, een moment alstublieft."'
        )

    @function_tool()
    async def lookup_tariff(self, context: RunContext, tariff_kind: str) -> str:
        """Geef tariefcontext (voorrijkosten, uurtarief, spoedtoeslag,
        materiaalopslag). Alleen aanroepen als de beller er expliciet om vraagt.
        Noemt nooit een vaste prijs voor de klus zelf.

        Args:
            tariff_kind: voorrijkosten, uurtarief, spoedtoeslag, materiaalopslag
                of alles.
        """
        c = self._client
        if not c.may_quote_prices:
            return (
                f"Voor prijzen verwijs ik u naar {c.owner_naam}. "
                "Hij belt u binnen vier uur terug."
            )
        return _tariff_line(tariff_kind, c)


def _tariff_line(kind: str, c: ClientConfig) -> str:
    t = c.tariff
    vast = (
        f"Een vaste prijs voor de klus maakt {c.owner_naam} pas na een korte "
        "beoordeling ter plaatse."
    )
    if kind == "voorrijkosten":
        return f"Voorrijkosten zijn {_eur(t.voorrijkosten)}. {vast}"
    if kind == "uurtarief":
        return f"Het uurtarief is {_eur(t.uurtarief)} exclusief BTW. {vast}"
    if kind == "spoedtoeslag":
        return (
            f"Spoed buiten kantooruren: plus {t.spoedtoeslag_pct:g} procent op het "
            f"uurtarief, of {_eur(t.spoedtoeslag_eur)} forfaitaire voorrijkosten. {vast}"
        )
    if kind == "materiaalopslag":
        return (
            f"Materialen worden doorberekend tegen inkoop plus "
            f"{t.materiaalopslag_pct:g} procent. {vast}"
        )
    return (
        f"Voorrijkosten {_eur(t.voorrijkosten)}, uurtarief {_eur(t.uurtarief)} "
        f"exclusief BTW, spoedtoeslag plus {t.spoedtoeslag_pct:g} procent, materialen "
        f"inkoop plus {t.materiaalopslag_pct:g} procent. {vast}"
    )


def _eur(x: float) -> str:
    return f"EUR {x:g}"


def _spell_out(phone: str) -> str:
    """Spell a phone number character-by-character for spoken read-back."""
    return " ".join(ch for ch in phone.replace(" ", ""))


async def _post_json(url: str, body: dict[str, object]) -> None:
    # urllib is blocking; run it off the audio event loop. Phase 4 swaps this
    # for an async client with HMAC signing + retries (see apps/api routes).
    def _do() -> None:
        payload = {k: v for k, v in body.items() if v is not None}
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            url, data=data, headers={"content-type": "application/json"}, method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:  # noqa: S310
            if resp.status >= 400:
                raise RuntimeError(f"POST {url} failed: {resp.status}")

    await asyncio.to_thread(_do)
