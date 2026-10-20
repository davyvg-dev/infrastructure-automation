"""Per-client configuration. Mirrors the {{placeholders}} in
packages/prompts/nl/<vertical>.v1.md, resolved at call time from the Attio
company record + Tally intake (production) or a demo fixture (local)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TariffConfig:
    voorrijkosten: float  # EUR
    uurtarief: float  # EUR excl. BTW
    spoedtoeslag_pct: float  # %
    spoedtoeslag_eur: float  # EUR forfaitair (voorrijkosten spoed)
    materiaalopslag_pct: float  # %


@dataclass
class ClientConfig:
    client_id: str
    vertical: str  # "loodgieter" | "dakdekker" | ...
    client_name: str
    owner_naam: str
    agent_naam: str  # "Daan" | "Sanne"
    escalation_number: str  # E.164 -- human/spoed transfer target
    may_quote_prices: bool
    tariff: TariffConfig
    postcode_lijst: list[str]
    api_base_url: str  # https://api.klantkraan.nl
