"""Property listings: search inventory and register qualified buyer leads, via a pluggable
provider — the real-estate analogue of calendar_store.

The public seam is `search()` and `register_lead()` — their SIGNATURES are fixed; only the
backing inventory changes per client. The provider is chosen in the business config:

    listings:
      provider: sim | resales     # default: sim
      file: config/listings/solvista-demo.json   # sim inventory (repo-shipped, not data/)

- `sim`     — a local JSON file of listings shaped like Resales-Online WebAPI V6 records.
              Zero external setup; used for demos and prospect showcases.
- `resales` — the client's own Resales-Online MLS account (WebAPI V6, plain GET, JSON).
              Needs RESALES_P1 + RESALES_P2 in .env (the agency mints an IP-locked key in
              their dashboard: Properties -> Feed Out -> API Keys) and in the config:
                listings:
                  provider: resales
                  agency_filter_id: 1
              Docs: https://webapi-v6.learning.resales-online.com/

Lead routing: the config lists the human agents and what they cover; `register_lead()`
picks one, persists the lead (append-only JSONL), pings that agent's Telegram (fallback:
the client's own recipient, then the founder) and — with provider resales — also registers
the lead in the agency's Resales CRM. Same honesty contract as notify.take_message: the
returned dict reflects what actually happened.

    agents:
      - name: "Maria"
        areas: ["Marbella", "Estepona"]       # match on the buyer's locations
        languages: ["es", "en"]               # match on the conversation language
        telegram_chat_id: ""                  # optional; falls back to notify.telegram_chat_id
        default: true                         # catch-all when no rule matches
"""

from __future__ import annotations

import json
import threading
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any

from . import lead_score, notify, settings
from .settings import active_client, business, ensure_dirs

_lock = threading.Lock()

_ROOT = Path(__file__).resolve().parent.parent

# Resales WebAPI V6 language ids (P_Lang); the sim provider ignores language.
_RESALES_LANGS = {"en": 1, "es": 2, "de": 3, "fr": 4, "nl": 5, "da": 6, "ru": 7, "sv": 8}


def _cfg() -> dict[str, Any]:
    return business().get("listings") or {}


def _provider_name() -> str:
    return str(_cfg().get("provider", "sim")).lower()


# --- sim provider: a repo-shipped JSON inventory ------------------------------------------


def _sim_load() -> list[dict[str, Any]]:
    rel = _cfg().get("file")
    if not rel:
        raise RuntimeError("listings.file missing in config (sim provider needs an inventory)")
    path = (_ROOT / rel).resolve()
    if not str(path).startswith(str(_ROOT)):
        raise RuntimeError(f"listings.file escapes the app root: {rel}")
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _matches(prop: dict[str, Any], c: dict[str, Any]) -> bool:
    if c.get("operation") and prop.get("Operation", "sale") != c["operation"]:
        return False
    price = int(prop.get("Price", 0))
    if c.get("min_price") and price < int(c["min_price"]):
        return False
    if c.get("max_price") and price > int(c["max_price"]):
        return False
    if c.get("min_bedrooms") and int(prop.get("Bedrooms", 0)) < int(c["min_bedrooms"]):
        return False
    if c.get("min_bathrooms") and int(prop.get("Bathrooms", 0)) < int(c["min_bathrooms"]):
        return False
    if c.get("locations"):
        wanted = [loc.strip().lower() for loc in c["locations"]]
        if prop.get("Location", "").lower() not in wanted:
            return False
    if c.get("property_type"):
        if c["property_type"].lower() not in prop.get("PropertyType", "").lower():
            return False
    for feat in c.get("features") or []:
        hay = " ".join(prop.get("Features", [])).lower()
        if feat.lower() not in hay:
            return False
    return True


def _sim_search(criteria: dict[str, Any]) -> dict[str, Any]:
    props = [p for p in _sim_load() if _matches(p, criteria)]
    props.sort(key=lambda p: int(p.get("Price", 0)))
    limit = int(criteria.get("max_results") or 5)
    return {"count": len(props), "showing": min(limit, len(props)), "properties": props[:limit]}


# --- resales provider: the agency's own Resales-Online WebAPI V6 --------------------------


def _resales_get(function: str, params: dict[str, Any]) -> dict[str, Any]:
    base = {
        "p1": settings.env("RESALES_P1"),
        "p2": settings.env("RESALES_P2"),
        "P_Agency_FilterId": _cfg().get("agency_filter_id", 1),
        "p_output": "JSON",
    }
    query = urllib.parse.urlencode({**base, **{k: v for k, v in params.items() if v}})
    url = f"https://webapi.resales-online.com/V6/{function}?{query}"
    with urllib.request.urlopen(url, timeout=20) as resp:
        payload = json.loads(resp.read())
    if (payload.get("transaction") or {}).get("status") == "error":
        raise RuntimeError(f"Resales {function} error: {payload['transaction']}")
    return payload


def _resales_search(c: dict[str, Any]) -> dict[str, Any]:
    lang = _RESALES_LANGS.get(str(c.get("language", "en")).lower(), 1)
    payload = _resales_get(
        "SearchProperties",
        {
            "P_Min": c.get("min_price"),
            "P_Max": c.get("max_price"),
            "P_Beds": f"{c['min_bedrooms']}x" if c.get("min_bedrooms") else None,
            "P_Baths": f"{c['min_bathrooms']}x" if c.get("min_bathrooms") else None,
            "P_Location": ",".join(c.get("locations") or []),
            "P_Lang": lang,
            "p_PageSize": int(c.get("max_results") or 5),
            "P_SortType": 5,  # newest listed first — freshest inventory sells the demo
        },
    )
    props = payload.get("Property") or []
    count = int((payload.get("QueryInfo") or {}).get("PropertyCount", len(props)))
    return {"count": count, "showing": len(props), "properties": props}


def _resales_register_lead(
    name: str, contact: str, criteria: dict[str, Any], references: list[str]
) -> None:
    first, _, last = name.partition(" ")
    email = contact if "@" in contact else ""
    phone = "" if "@" in contact else contact
    _resales_get(
        "RegisterLead",
        {
            "M1": first or name,
            "M2": last or "-",
            "M3": phone,
            "M5": email or "unknown@lead.invalid",
            "M6": "Lead via Klantkraan receptionist",
            "M7": f"Qualified buyer profile: {json.dumps(criteria, ensure_ascii=False)}",
            "W3": ",".join(criteria.get("locations") or []),
            "W6": f"{criteria['min_bedrooms']}x" if criteria.get("min_bedrooms") else None,
            "W8": criteria.get("min_price"),
            "W9": criteria.get("max_price"),
            "Source": "Klantkraan",
            "RsId": ";".join(references),
        },
    )


# --- lead routing: pick the right human agent from the config -----------------------------


def route_agent(criteria: dict[str, Any]) -> dict[str, Any] | None:
    """Pick the agent whose areas/languages match the buyer; else the default agent."""
    agents = business().get("agents") or []
    lang = str(criteria.get("language", "")).lower()
    locations = [loc.strip().lower() for loc in criteria.get("locations") or []]
    best, best_score = None, 0
    for agent in agents:
        score = 0
        areas = [a.lower() for a in agent.get("areas") or []]
        if locations and areas and any(loc in areas for loc in locations):
            score += 2
        if lang and lang in [str(x).lower() for x in agent.get("languages") or []]:
            score += 1
        if score > best_score:
            best, best_score = agent, score
    if best:
        return best
    return next((a for a in agents if a.get("default")), agents[0] if agents else None)


# --- public seam --------------------------------------------------------------------------


def search(criteria: dict[str, Any]) -> dict[str, Any]:
    """Search the inventory. Criteria keys: operation ('sale'|'rent'), locations (list),
    min_price, max_price, min_bedrooms, min_bathrooms, property_type, features (list),
    language, max_results. The result shape is provider-independent."""
    if _provider_name() == "resales":
        return _resales_search(criteria)
    return _sim_search(criteria)


def register_lead(
    customer_name: str,
    contact: str,
    criteria: dict[str, Any],
    references: list[str] | None = None,
    notes: str = "",
) -> dict[str, Any]:
    """Persist a qualified buyer lead, route it to the right agent, notify them.

    Returns {"ok", "saved", "notified", "agent"} reflecting what actually happened, so the
    receptionist can be honest when neither channel worked."""
    client = active_client()
    agent = route_agent(criteria)
    record = {
        "at": datetime.now().isoformat(timespec="seconds"),
        "client": client,
        "customer_name": customer_name,
        "contact": contact,
        "intent": lead_score.resolve_intent(criteria),
        "temperature": lead_score.temperature(criteria),
        "criteria": criteria,
        "references": references or [],
        "notes": notes,
        "agent": (agent or {}).get("name", ""),
    }
    saved = _save_lead(record)

    if _provider_name() == "resales":
        # Best-effort: the local record + Telegram ping are the source of truth; the
        # agency-CRM copy is a bonus that must not sink the lead when Resales is down.
        try:
            _resales_register_lead(customer_name, contact, criteria, references or [])
        except Exception as exc:
            print(f"[listings:register_lead] Resales CRM push failed ({exc})")

    wants = ", ".join(
        str(v)
        for v in (
            criteria.get("operation"),
            f"{'/'.join(criteria.get('locations') or [])}" or None,
            f"up to €{criteria['max_price']:,}" if criteria.get("max_price") else None,
            f"{criteria['min_bedrooms']}+ beds" if criteria.get("min_bedrooms") else None,
        )
        if v
    )
    matched = f"\nMatches: {', '.join(references)}" if references else ""
    note_line = f"\nNotes: {notes}" if notes else ""
    # Temperature first: the agent triages this on a phone lock screen — "HOT seller"
    # must be readable before the notification is even opened.
    flame = "🔥" if record["temperature"] == "hot" else "🏠"
    text = (
        f"[{business()['business']['name']}] {flame} {record['temperature'].upper()} "
        f"{record['intent']} lead{' for ' + agent['name'] if agent else ''}: "
        f"{customer_name} ({contact})\nLooking for: {wants or '—'}{matched}{note_line}"
    )
    chat_id = (agent or {}).get("telegram_chat_id") or (
        (business().get("notify") or {}).get("telegram_chat_id")
    )
    notified = notify.owner(text, chat_id=chat_id or None)
    return {
        "ok": saved or notified,
        "saved": saved,
        "notified": notified,
        "agent": (agent or {}).get("name", ""),
    }


def _save_lead(record: dict[str, Any]) -> bool:
    try:
        with _lock:
            ensure_dirs()
            path = settings.DATA_DIR / f"listing-leads-{record['client']}.jsonl"
            with path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        return True
    except Exception as exc:
        print(f"[listings:register_lead] persist failed ({exc})")
        return False
