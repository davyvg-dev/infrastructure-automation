"""Scrape a prospect's website + Google Maps, then draft a cited config with Claude.

    python -m app.extract "Jansen Loodgieters" --url https://jansen-loodgieters.nl --near Utrecht
    python -m app.extract "Jansen Loodgieters" --url https://... -o extraction.json

The point of this module is a *do-it-for-them* intake: instead of a 32-field form, we scrape
what's public, have Claude extract only what it can cite, and hand `scaffold.py --from-json` a
draft the founder confirms by chatting with the demo.

Two hard guarantees, enforced by the schema — not just the prompt:
  1. PRICES ARE NEVER EXTRACTED. `_SCHEMA` has no price field anywhere, so a price cannot be
     invented; `scaffold.py` writes the literal `PRIJS?` and the founder fills it in.
  2. CITATION-OR-BLANK. Every value carries a verbatim `snippet` from its source; a value with
     an empty snippet is uncited and dropped at merge time.

Sources are best-effort: the site pages that exist plus Google Places details if
`GOOGLE_PLACES_API_KEY` is set. With no sources at all we emit an empty (but valid) extraction
rather than let Claude guess — fall back to the 3-field Tally form for those prospects.

Docs fetched via context7 (2026-07-14): Google Places API (New) searchText + Place Details
field masks; Anthropic structured outputs via output_config.format (adaptive-thinking safe).
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

import anthropic

from . import settings

# Extraction wants more deliberate reasoning than a single chat turn, so it runs a notch above
# the receptionist's effort. Static (model + effort) so the system prompt + schema prefix stays
# cacheable across prospects; per-request variation lives entirely in the user message.
_MODEL = {"id": "claude-opus-4-8", "effort": "high"}

# Controlled Dutch-trade vocabulary the model must classify each service into. Keep in sync with
# scaffold._duration below (offerte/inspectie are shorter jobs).
SERVICE_CATEGORIES = [
    "spoedservice",
    "cv-ketel onderhoud",
    "lekkage-reparatie",
    "installatie",
    "inspectie/offerte",
    "dakwerk",
    "elektra",
    "sanitair",
    "overig",
]

# The site pages worth scraping ("" = homepage). Dutch-trade sites almost always use these slugs.
_PAGES = ("", "diensten", "tarieven", "contact")
_UA = "KlantkraanIntake/1.0 (+https://klantkraan.nl)"

# A cited scalar: a value is only trusted when it carries a verbatim snippet from a source.
_CITED_STR = {
    "type": "object",
    "additionalProperties": False,
    "properties": {"value": {"type": "string"}, "snippet": {"type": "string"}},
    "required": ["value", "snippet"],
}
_CITED_HOURS = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "open": {"type": "string"},
        "close": {"type": "string"},
        "snippet": {"type": "string"},
    },
    "required": ["open", "close", "snippet"],
}
_DAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")

# NOTE: there is deliberately no price/rate/amount field anywhere in this schema. selftest
# `intake` asserts that invariant. Structured outputs guarantee the response validates against it.
_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "business_type": _CITED_STR,  # the trade, in Dutch (e.g. "loodgieter")
        "phone": _CITED_STR,
        "region": _CITED_STR,  # the area served (e.g. "Utrecht en omgeving")
        "services": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "name": {"type": "string"},
                    "category": {"type": "string", "enum": SERVICE_CATEGORIES},
                    "snippet": {"type": "string"},
                    "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
                },
                "required": ["name", "category", "snippet", "confidence"],
            },
        },
        "hours": {
            "type": "object",
            "additionalProperties": False,
            "properties": {day: _CITED_HOURS for day in _DAYS},
        },
    },
    "required": ["business_type", "phone", "region", "services", "hours"],
}

_SYSTEM = (
    "You extract structured facts about a Dutch trades business (loodgieter, installatiebedrijf, "
    "dakdekker, elektricien, etc.) from the SOURCES the user provides, to pre-fill a receptionist "
    "config that the owner will confirm.\n\n"
    "Absolute rules:\n"
    "1. Use ONLY the provided sources. Never use outside knowledge. If a fact is not in the "
    "sources, return an empty value with an empty snippet — do NOT guess.\n"
    "2. For every value you DO return, put a short verbatim quote from the source it came from "
    "into its `snippet`. No snippet means no value.\n"
    "3. NEVER output any price, rate, tariff, call-out fee or euro amount. Those are collected "
    "from the owner separately and are not part of your output.\n"
    "4. `services`: include a service only if it is named or described in the sources. Classify "
    "each into exactly one `category` from the allowed list. Put the verbatim source text in "
    "`snippet`. Drop anything you cannot ground in a source.\n"
    "5. `hours`: only from Google opening hours or a page. Use 24h HH:MM for open/close. Omit any "
    "day you cannot find.\n"
    "6. `business_type` in Dutch; `phone` prefer the Google Maps number; `region` is the area "
    "served, not the street address.\n"
    "Write values in Dutch."
)

_EMPTY: dict = {
    "business_type": {"value": "", "snippet": ""},
    "phone": {"value": "", "snippet": ""},
    "region": {"value": "", "snippet": ""},
    "services": [],
    "hours": {},
}


def _duration(category: str) -> int:
    """Default job length by category — quotes/inspections are short, everything else 60 min."""
    return 30 if category == "inspectie/offerte" else 60


# --- source gathering (stdlib only) -----------------------------------------------------


class _TextExtractor(HTMLParser):
    """Collapse an HTML page to visible text, skipping script/style/head."""

    _SKIP = {"script", "style", "noscript", "head", "svg"}

    def __init__(self) -> None:
        super().__init__()
        self._depth = 0
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: object) -> None:
        if tag in self._SKIP:
            self._depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in self._SKIP and self._depth:
            self._depth -= 1

    def handle_data(self, data: str) -> None:
        if not self._depth:
            text = data.strip()
            if text:
                self._parts.append(text)

    def text(self) -> str:
        return " ".join(self._parts)


def fetch_site(base_url: str, *, timeout: int = 10, per_page_chars: int = 8000) -> dict[str, str]:
    """Best-effort: return {page: text} for the pages that load. Never raises."""
    base = base_url.rstrip("/")
    out: dict[str, str] = {}
    for page in _PAGES:
        url = base if page == "" else f"{base}/{page}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": _UA})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if getattr(resp, "status", 200) != 200:
                    continue
                raw = resp.read(400_000)
            parser = _TextExtractor()
            parser.feed(raw.decode("utf-8", "replace"))
            text = parser.text()
            if text:
                out[page or "home"] = text[:per_page_chars]
        except Exception:
            continue
    return out


def fetch_place(name: str, near: str | None = None, *, timeout: int = 10) -> dict | None:
    """Google Places (New): resolve name -> place_id (searchText) -> Place Details. Optional —
    returns None if GOOGLE_PLACES_API_KEY is unset or nothing is found. Never raises."""
    key = settings.env("GOOGLE_PLACES_API_KEY", required=False)
    if not key:
        return None
    query = f"{name} {near}".strip() if near else name
    search_body = json.dumps(
        {
            "textQuery": query,
            "languageCode": "nl",
            "regionCode": "NL",
            "includePureServiceAreaBusinesses": True,  # plumbers/cleaners with no shopfront
        }
    ).encode("utf-8")
    try:
        req = urllib.request.Request(
            "https://places.googleapis.com/v1/places:searchText",
            data=search_body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "X-Goog-Api-Key": key,
                "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            places = json.loads(resp.read()).get("places") or []
    except Exception:
        return None
    if not places or not places[0].get("id"):
        return None
    place_id = places[0]["id"]
    mask = (
        "displayName,nationalPhoneNumber,internationalPhoneNumber,regularOpeningHours,"
        "primaryType,primaryTypeDisplayName,websiteUri,formattedAddress,pureServiceAreaBusiness"
    )
    try:
        req = urllib.request.Request(
            f"https://places.googleapis.com/v1/places/{urllib.parse.quote(place_id)}",
            headers={"X-Goog-Api-Key": key, "X-Goog-FieldMask": mask},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception:
        return None


def gather_sources(name: str, url: str | None, near: str | None) -> dict[str, str]:
    """Collect the labelled source blocks Claude will cite from. Empty dict => no grounding."""
    sources: dict[str, str] = {}
    if url:
        for page, text in fetch_site(url).items():
            sources[f"Website ({page})"] = text
    place = fetch_place(name, near)
    if place:
        sources["Google Maps"] = json.dumps(place, ensure_ascii=False, indent=2)
    return sources


# --- extraction --------------------------------------------------------------------------


def _client() -> anthropic.Anthropic:
    settings.env("ANTHROPIC_API_KEY")
    return anthropic.Anthropic()


def _user_message(name: str, sources: dict[str, str]) -> str:
    blocks = [f"Business name: {name}", ""]
    for label, text in sources.items():
        blocks.append(f"--- SOURCE: {label} ---\n{text}\n")
    blocks.append(
        "Extract the fields defined by the schema from the sources above. Remember: no prices, "
        "and every value needs a verbatim snippet or it must be left empty."
    )
    return "\n".join(blocks)


def extract(name: str, url: str | None = None, near: str | None = None) -> dict:
    """Return a cited extraction dict for `name`. With no sources, returns `_EMPTY` (no API call,
    no fabrication)."""
    sources = gather_sources(name, url, near)
    if not sources:
        return dict(_EMPTY)
    client = _client()
    response = client.messages.create(
        model=_MODEL["id"],
        max_tokens=8192,
        thinking={"type": "adaptive"},
        output_config={
            "effort": _MODEL["effort"],
            "format": {"type": "json_schema", "schema": _SCHEMA},
        },
        system=_SYSTEM,
        messages=[{"role": "user", "content": _user_message(name, sources)}],
    )
    text = next((b.text for b in response.content if b.type == "text"), "")
    return json.loads(text)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="app.extract",
        description="Scrape a prospect's site + Google Maps and draft a cited extraction JSON.",
    )
    parser.add_argument("name", help="The prospect's business name.")
    parser.add_argument("--url", help="The prospect's website (homepage).")
    parser.add_argument("--near", help="Town/city to disambiguate the Google Maps lookup.")
    parser.add_argument("-o", "--out", help="Write the extraction JSON here (default: stdout).")
    args = parser.parse_args(argv[1:])

    data = extract(args.name, url=args.url, near=args.near)
    grounded = (
        any(
            (isinstance(v, dict) and v.get("snippet"))
            for v in (data.get("business_type"), data.get("phone"), data.get("region"))
        )
        or bool(data.get("services"))
        or bool(data.get("hours"))
    )
    if not grounded:
        print(
            "⚠️  No usable sources found — nothing to extract. Use the 3-field Tally fallback "
            "(prices / spoed / lead-destination) for this prospect.",
            file=sys.stderr,
        )

    blob = json.dumps(data, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(blob + "\n", encoding="utf-8")
        print(f"✅ Wrote {args.out}")
        print(f"\nNext: python -m app.scaffold {args.name!r} --from-json {args.out}")
    else:
        print(blob)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
