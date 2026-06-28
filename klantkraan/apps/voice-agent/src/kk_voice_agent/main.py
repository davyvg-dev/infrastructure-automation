"""Worker entrypoint. Run with:

    python -m kk_voice_agent.main dev    # local, connects to LiveKit playground
    python -m kk_voice_agent.main start  # production worker

Phase 2: a demo client + demo-rendered prompt so the agent talks in the
playground. Phase 4 replaces ``_demo_client`` with per-dialed-number resolution
from Attio/API.
"""

from __future__ import annotations

import logging
from pathlib import Path

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, RoomInputOptions, WorkerOptions, cli
from livekit.plugins import anthropic, deepgram, elevenlabs, silero

from .agent import KlantkraanReceptionist
from .config import ClientConfig, TariffConfig
from .prompt import render_prompt

load_dotenv()
logger = logging.getLogger("voice-agent")

# apps/voice-agent/src/kk_voice_agent/main.py -> klantkraan/
_REPO = Path(__file__).resolve().parents[4]
_PROMPTS = _REPO / "packages" / "prompts" / "nl"


def _demo_client() -> ClientConfig:
    """Demo client for local playground runs (P2 only)."""
    return ClientConfig(
        client_id="demo_loodgieter",
        vertical="loodgieter",
        client_name="Demo Loodgieters",
        owner_naam="Jan",
        agent_naam="Sanne",
        escalation_number="+31600000000",
        may_quote_prices=True,
        tariff=TariffConfig(
            voorrijkosten=45,
            uurtarief=75,
            spoedtoeslag_pct=50,
            spoedtoeslag_eur=90,
            materiaalopslag_pct=15,
        ),
        postcode_lijst=["1011", "1012", "1013"],
        api_base_url="https://api.klantkraan.nl",
    )


async def entrypoint(ctx: agents.JobContext) -> None:
    client = _demo_client()  # P4: resolve from ctx (dialed number) instead
    instructions = render_prompt(_PROMPTS / f"{client.vertical}.v1.md", client)

    session = AgentSession(
        stt=deepgram.STT(model="nova-2", language="nl"),
        llm=anthropic.LLM(model="claude-sonnet-4-6", temperature=0.3),
        tts=elevenlabs.TTS(
            # Set after the Dutch voice test (Daan/Sanne). This placeholder is
            # the original blocker: the agent cannot speak until it is resolved.
            voice_id="TODO_DUTCH_VOICE_ID",
            model="eleven_multilingual_v2",
        ),
        vad=silero.VAD.load(),
    )

    await ctx.connect()
    await session.start(
        room=ctx.room,
        agent=KlantkraanReceptionist(instructions=instructions, client=client),
        room_input_options=RoomInputOptions(),
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
