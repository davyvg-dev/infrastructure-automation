"""Minimal mustache fill for local/dev runs.

Production rendering is done by the n8n client-onboarding flow, which writes
packages/prompts/nl/<vertical>.<client_id>.rendered.md and logs its SHA-256.
This helper exists only so the agent is runnable in the LiveKit playground (P2)
without standing up the full onboarding pipeline.
"""

from __future__ import annotations

from pathlib import Path

from .config import ClientConfig


def render_prompt(template_path: Path, client: ClientConfig) -> str:
    text = template_path.read_text(encoding="utf-8")
    t = client.tariff
    mapping = {
        "client_name": client.client_name,
        "client_kvk": "-",
        "client_regio": "-",
        "owner_naam": client.owner_naam,
        "owner_email": "-",
        "agent_naam": client.agent_naam,
        "escalation_number": client.escalation_number,
        "client_voorrijkosten": _num(t.voorrijkosten),
        "client_uurtarief": _num(t.uurtarief),
        "client_spoedtoeslag": _num(t.spoedtoeslag_pct),
        "client_spoedtoeslag_eur": _num(t.spoedtoeslag_eur),
        "client_materiaalopslag": _num(t.materiaalopslag_pct),
        "client_postcode_lijst": ", ".join(client.postcode_lijst),
        "may_quote_prices": "true" if client.may_quote_prices else "false",
        "n8n_webhook_url": f"{client.api_base_url}/api/voice/call-end",
        "calcom_eventtype_url": "-",
        "faq_overlay": "",
    }
    for key, value in mapping.items():
        text = text.replace("{{" + key + "}}", str(value))
    return text


def _num(x: float) -> str:
    return f"{x:g}"
