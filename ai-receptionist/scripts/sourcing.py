"""Build the prospect list from the KVK Handelsregister instead of by hand.

The 45-row CSV in klantkraan/docs/02-sales/prospects was researched one company at a
time. That is roughly a month of outreach at any honest send rate, and the sequence
engine now spends four touches per prospect rather than one, so the list is what runs
out first. This turns list-building into a command.

Two stages, because they cost different amounts:

    discover   KVK Zoeken API      free       names + KVK numbers, from config/sourcing.yaml
    qualify    KVK Basisprofiel    EUR 0.02   rechtsvorm, SBI, headcount, non-mailing flag

Discover is a wide net cast by name -- Zoeken cannot filter on SBI, and a Dutch trade
almost always carries the trade in its company name. Qualify is the sieve, and it is the
part that spends money, so every profile is cached under data/sourcing/profiles/ and a
second run over the same companies costs nothing.

What the register does NOT have, at all: e-mail, telephone, website. Nothing in the KVK
product line returns them. So this produces a qualified list of real BVs in the right
trade, and finding the address to mail is a separate step (scripts/enrich.py).

The BV gate is the reason to use the register rather than scraping a directory. Cold mail
to an eenmanszaak or VOF without opt-in is not allowed and cold mail to a BV is, and
`rechtsvorm` here is the registrar's own answer rather than an inference off the name.

    python -m scripts.sourcing discover                    # free, writes raw.json
    python -m scripts.sourcing qualify --limit 50          # costs 50 x EUR 0.02
    python -m scripts.sourcing export --out prospects.csv

Set KVK_API_KEY in .env for live data. Without it this runs against KVK's test
environment, which has a handful of fake companies -- enough to prove the plumbing,
useless as a list. Subscription is EUR 6.40/month at developers.kvk.nl; Zoeken is
included, Basisprofiel is EUR 0.02 per call.

Run from the ai-receptionist directory with ./.venv/bin/python.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ModuleNotFoundError:
    pass

import os  # noqa: E402

CONFIG = Path("config/sourcing.yaml")
OUT = Path("data/sourcing")
RAW = OUT / "raw.json"
PROFILES = OUT / "profiles"

LIVE_BASE = "https://api.kvk.nl/api"
TEST_BASE = "https://api.kvk.nl/test/api"
TEST_KEY = "l7xx1f2691f2520d487b902f4e0b57a0b197"  # KVK publishes this one for the sandbox

PER_PAGE = 100  # the API's maximum
BASISPROFIEL_COST = 0.02  # EUR, per developers.kvk.nl/pricing (2026-07)

# KVK asks for courtesy rather than publishing a hard rate limit on the paid APIs. A
# tenth of a second between calls keeps a 500-company qualify run under a minute of
# wall clock and still nowhere near anything that looks like abuse.
DELAY = 0.1


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Trade:
    name: str
    keywords: list[str]
    sbi_prefixes: list[str]


@dataclass(frozen=True)
class Filters:
    rechtsvorm_contains: list[str]
    skip_non_mailing: bool
    staff_min: int
    staff_max: int
    keep_unknown_staff: bool


@dataclass(frozen=True)
class Config:
    trades: list[Trade]
    cities: list[str]
    filters: Filters

    @property
    def sbi_prefixes(self) -> dict[str, list[str]]:
        return {t.name: t.sbi_prefixes for t in self.trades}


def load_config(path: Path = CONFIG) -> Config:
    raw = yaml.safe_load(path.read_text())
    return Config(
        trades=[Trade(name, t["keywords"], t["sbi_prefixes"]) for name, t in raw["trades"].items()],
        cities=raw["cities"],
        filters=Filters(**raw["filters"]),
    )


# ---------------------------------------------------------------------------
# The API
# ---------------------------------------------------------------------------


def credentials() -> tuple[str, str, bool]:
    """(base_url, api_key, is_live). No key means the sandbox, loudly."""
    key = os.getenv("KVK_API_KEY")
    return (LIVE_BASE, key, True) if key else (TEST_BASE, TEST_KEY, False)


def get(url: str, key: str) -> dict:
    req = urllib.request.Request(url, headers={"apikey": key, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        if exc.code == 404:  # a KVK number with no profile; not fatal, just not a prospect
            return {}
        body = exc.read().decode(errors="replace")[:200]
        raise SystemExit(f"KVK API {exc.code} on {url}\n  {body}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"could not reach the KVK API: {exc.reason}") from exc


def zoeken(base: str, key: str, *, naam: str, plaats: str) -> list[dict]:
    """Every page of one name+city query. Zoeken is free, so pagination is not rationed."""
    found, page = [], 1
    while True:
        qs = urllib.parse.urlencode(
            {
                "naam": naam,
                "plaats": plaats,
                "type": "hoofdvestiging",
                "resultatenPerPagina": PER_PAGE,
                "pagina": page,
            }
        )
        data = get(f"{base}/v2/zoeken?{qs}", key)
        found.extend(data.get("resultaten") or [])
        # `totaal` is the whole result set; stop when this page did not fill.
        if len(data.get("resultaten") or []) < PER_PAGE:
            return found
        page += 1
        time.sleep(DELAY)


def basisprofiel(base: str, key: str, kvk: str, *, cache: Path = PROFILES) -> dict:
    """One company profile, cached on disk because each live call is charged."""
    cached = cache / f"{kvk}.json"
    if cached.exists():
        return json.loads(cached.read_text())
    data = get(f"{base}/v1/basisprofielen/{kvk}", key)
    cache.mkdir(parents=True, exist_ok=True)
    cached.write_text(json.dumps(data, ensure_ascii=False))
    time.sleep(DELAY)
    return data


# ---------------------------------------------------------------------------
# The sieve
# ---------------------------------------------------------------------------


@dataclass
class Candidate:
    kvk: str
    name: str
    city: str
    trade: str
    matched_on: str = ""
    rechtsvorm: str = ""
    sbi: list[str] = field(default_factory=list)
    staff: int | None = None
    non_mailing: bool = False
    street: str = ""
    postcode: str = ""

    @property
    def slug(self) -> str:
        """The demo config slug, which is also the ?client= value, so it has to survive a
        URL untouched."""
        s = re.sub(r"\b(b\.?v\.?|n\.?v\.?|v\.?o\.?f\.?)\b", "", self.name.lower())
        s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
        return re.sub(r"-+", "-", s)[:48]


def verdict(c: Candidate, f: Filters, sbi_prefixes: list[str]) -> str | None:
    """None if the candidate is mailable, else the reason it is not.

    Order matters only for the message the operator reads; every check is independent."""
    if not any(v.lower() in c.rechtsvorm.lower() for v in f.rechtsvorm_contains):
        return f"rechtsvorm {c.rechtsvorm or 'onbekend'}"
    if f.skip_non_mailing and c.non_mailing:
        return "non-mailing indicator"
    if not any(code.startswith(p) for code in c.sbi for p in sbi_prefixes):
        return f"SBI {','.join(c.sbi) or 'geen'} outside the trade"
    if c.staff is None or c.staff == 0:
        return None if f.keep_unknown_staff else "headcount unknown"
    if not (f.staff_min <= c.staff <= f.staff_max):
        return f"{c.staff} staff"
    return None


def from_profile(c: Candidate, profile: dict) -> Candidate:
    """Fold a Basisprofiel response into the candidate. Missing keys stay falsy rather
    than raising: a sparse profile is a disqualification, not a crash."""
    c.rechtsvorm = ((profile.get("_embedded") or {}).get("eigenaar") or {}).get("rechtsvorm", "")
    c.sbi = [a.get("sbiCode", "") for a in (profile.get("sbiActiviteiten") or [])]
    c.staff = profile.get("totaalWerkzamePersonen")
    c.non_mailing = profile.get("indNonMailing") == "Ja"
    c.name = profile.get("statutaireNaam") or profile.get("naam") or c.name
    hoofd = (profile.get("_embedded") or {}).get("hoofdvestiging") or {}
    for adres in hoofd.get("adressen") or []:
        if adres.get("type") == "bezoekadres":
            c.street = f"{adres.get('straatnaam', '')} {adres.get('huisnummer', '')}".strip()
            c.postcode = adres.get("postcode", "") or ""
            c.city = adres.get("plaats", "") or c.city
    return c


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def cmd_discover(args: argparse.Namespace) -> None:
    cfg = load_config()
    base, key, live = credentials()
    if not live:
        print("no KVK_API_KEY -- using the test sandbox, which has fake companies\n")

    seen: dict[str, Candidate] = {}
    queries = [(t, kw, city) for t in cfg.trades for kw in t.keywords for city in cfg.cities]
    for i, (trade, keyword, city) in enumerate(queries, 1):
        results = zoeken(base, key, naam=keyword, plaats=city)
        fresh = 0
        for r in results:
            kvk = r.get("kvkNummer")
            if not kvk or kvk in seen:
                continue
            adres = (r.get("adres") or {}).get("binnenlandsAdres") or {}
            seen[kvk] = Candidate(
                kvk=kvk,
                name=r.get("naam", ""),
                city=adres.get("plaats") or city,
                trade=trade.name,
                matched_on=keyword,
                street=adres.get("straatnaam", ""),
            )
            fresh += 1
        print(f"[{i:3}/{len(queries)}] {keyword:22} {city:22} {len(results):4} hits, {fresh} new")
        time.sleep(DELAY)

    OUT.mkdir(parents=True, exist_ok=True)
    RAW.write_text(json.dumps([asdict(c) for c in seen.values()], ensure_ascii=False, indent=2))
    print(f"\n{len(seen)} unique companies -> {RAW}")
    print(
        f"next: qualify them ({len(seen)} x EUR {BASISPROFIEL_COST:.2f} = "
        f"EUR {len(seen) * BASISPROFIEL_COST:.2f} at most, cached calls are free)"
    )


def cmd_qualify(args: argparse.Namespace) -> None:
    cfg = load_config()
    base, key, live = credentials()
    if not RAW.exists():
        sys.exit(f"{RAW} missing -- run `discover` first")

    candidates = [Candidate(**c) for c in json.loads(RAW.read_text())]
    todo = [c for c in candidates if not (PROFILES / f"{c.kvk}.json").exists()]
    if args.limit:
        todo = todo[: args.limit]

    billable = len(todo) if live else 0
    print(
        f"{len(candidates)} discovered, {len(todo)} to look up "
        f"(EUR {billable * BASISPROFIEL_COST:.2f}), the rest are cached"
    )
    if billable * BASISPROFIEL_COST > 1.0 and not args.yes:
        sys.exit("that is over EUR 1.00 -- re-run with --yes if that is intended")

    for i, c in enumerate(todo, 1):
        basisprofiel(base, key, c.kvk)
        if i % 25 == 0 or i == len(todo):
            print(f"  {i}/{len(todo)} profiles")

    kept, rejected = [], []
    for c in candidates:
        path = PROFILES / f"{c.kvk}.json"
        if not path.exists():
            continue
        c = from_profile(c, json.loads(path.read_text()))
        why = verdict(c, cfg.filters, cfg.sbi_prefixes[c.trade])
        (rejected if why else kept).append((c, why))

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "qualified.json").write_text(
        json.dumps([asdict(c) for c, _ in kept], ensure_ascii=False, indent=2)
    )

    print(f"\n{len(kept)} qualified, {len(rejected)} rejected")
    reasons: dict[str, int] = {}
    for _, why in rejected:
        reasons[why] = reasons.get(why, 0) + 1
    for why, n in sorted(reasons.items(), key=lambda kv: -kv[1])[:8]:
        print(f"  {n:4}  {why}")
    print(f"\n-> {OUT}/qualified.json")


def cmd_export(args: argparse.Namespace) -> None:
    path = OUT / "qualified.json"
    if not path.exists():
        sys.exit(f"{path} missing -- run `qualify` first")
    rows = json.loads(path.read_text())

    out = Path(args.out)
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(
            fh,
            fieldnames=[
                "slug",
                "company_name",
                "kvk",
                "city",
                "postcode",
                "street",
                "trade",
                "entity_type",
                "staff",
                "sbi",
                "email",
                "website",
            ],
        )
        w.writeheader()
        for r in rows:
            c = Candidate(**r)
            w.writerow(
                {
                    "slug": c.slug,
                    "company_name": c.name,
                    "kvk": c.kvk,
                    "city": c.city,
                    "postcode": c.postcode,
                    "street": c.street,
                    "trade": c.trade,
                    "entity_type": "bv",
                    "staff": c.staff if c.staff is not None else "",
                    "sbi": " ".join(c.sbi),
                    "email": "",  # the register has none; scripts/enrich.py fills these
                    "website": "",
                }
            )
    print(f"{len(rows)} rows -> {out}")
    print("email and website are empty: KVK has neither. Next: python -m scripts.enrich")


def main() -> None:
    ap = argparse.ArgumentParser(description="Build the prospect list from the KVK register.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("discover", help="KVK Zoeken across the config grid (free)")
    d.set_defaults(func=cmd_discover)

    q = sub.add_parser("qualify", help="KVK Basisprofiel + the BV/SBI/headcount sieve (paid)")
    q.add_argument("--limit", type=int, help="only look up N new profiles this run")
    q.add_argument("--yes", action="store_true", help="approve a run costing over EUR 1.00")
    q.set_defaults(func=cmd_qualify)

    e = sub.add_parser("export", help="write the qualified list as CSV")
    e.add_argument("--out", default="data/sourcing/prospects.csv")
    e.set_defaults(func=cmd_export)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
