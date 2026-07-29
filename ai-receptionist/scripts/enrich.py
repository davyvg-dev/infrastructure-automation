"""Find the e-mail address the register does not carry.

sourcing.py produces qualified BVs with no way to reach them: KVK holds no e-mail, no
telephone and no website in any of its products. This closes that gap by guessing the
company's domain from its name, proving the guess, and reading the address the company
publishes on its own contact page.

Guessing is the easy half and it is not reliable on its own. Every domain shape tried
here was read off a company that really owns it: the name run together (ajdakwerken.nl),
minus the trade word (visservanderhell.nl), hyphenated (smits-installaties.nl), with a
"bv" suffix (herfstbv.nl), surname plus trade (valkenburgloodgieters.nl). Between them
they reach 12 of the 14 domains among the current prospects whose domain is known. Some
are simply unreachable: MD Dak & Klusbedrijf trades as dakdekkerutrechtbv.nl, which no
transformation of its own name produces.

Proving the guess is the half that matters, because meijer.nl belongs to a different
Meijer entirely and mailing them a demo built for someone else is worse than not mailing.
Dutch law requires a business to publish its KVK number, so the number from the register
is looked for on the page first and that effectively settles it. Without one the company
name has to appear in the page's own <title>, never merely somewhere in the body -- that
distinction is exactly what stopped Loodgietersbedrijf Meijer resolving onto the stranger
at meijer.nl. A site that proves neither is dropped rather than guessed at.

Measured against the 23 prospects whose real addresses are known, this finds 30% of them
outright. That run had no KVK numbers to check, so it exercised only the weaker of the
two proofs; a live run carries one for every company and should do better, by how much
nobody has measured yet.

The other 70% land in a worklist CSV with a search URL per company, which is about thirty
seconds of a human's time each and much better than thirty seconds of guessing.

    python -m scripts.enrich                       # dry: resolve + verify, report only
    python -m scripts.enrich --write               # write enriched.csv + worklist.csv
    python -m scripts.enrich --limit 20            # trial run over the first 20

Polite by construction: one worker, a real User-Agent, robots.txt honoured, and a pause
between hosts. It reads pages a company publishes for exactly this purpose.

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
import urllib.robotparser
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.sourcing import OUT, Candidate  # noqa: E402

UA = "KlantkraanBot/1.0 (+https://klantkraan.nl; contact davy@klantkraan.nl)"
BOT_TOKEN = "KlantkraanBot"  # what a robots.txt would name us in a User-agent line
TIMEOUT = 12
DELAY = 1.0  # between hosts

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
KVK_RE = re.compile(r"\b(\d{8})\b")
TAG_RE = re.compile(r"<[^>]+>")

# What the company does, not which company it is -- useless for telling two Rotterdam
# plumbers apart. Dropped to find the distinctive part of a name.
TRADE_WORDS = {
    "loodgieter",
    "loodgieters",
    "loodgietersbedrijf",
    "dakdekker",
    "dakdekkers",
    "dakdekkersbedrijf",
    "dakbedekking",
    "dakwerken",
    "dak",
    "bedrijf",
    "installatie",
    "installaties",
    "installatietechniek",
    "installatiebedrijf",
    "techniek",
    "technisch",
    "bureau",
    "sanitair",
    "service",
    "groep",
    "warmtetechnisch",
    "gas",
}

# Part of the name rather than a description of it. visservanderhell.nl keeps its "van
# der"; dropping those was why that domain was never generated.
CONNECTIVES = {"en", "van", "der", "den", "de", "het", "zn", "zonen", "gebr"}

GENERIC = TRADE_WORDS | CONNECTIVES

# Stripped from the name before anything else. Splitting on word boundaries instead ate
# the B of T.I.B. Verkuylen and lost tib-verkuylen.nl.
LEGAL_FORM_RE = re.compile(r"\s*\b(b\.?\s?v\.?|n\.?\s?v\.?|v\.?o\.?f\.?)\s*$", re.I)

# Addresses that appear on a site without belonging to the business.
JUNK_LOCAL = {"example", "your", "email", "name", "user", "info@example", "sentry", "test"}
JUNK_DOMAIN = (
    "example.com",
    "example.nl",
    "sentry.io",
    "wixpress.com",
    "domain.com",
    "email.com",
    "godaddy.com",
    "squarespace.com",
)

# Preferred in this order: a role address is what a business publishes for new work and
# outlives whoever currently reads it.
PREFERRED = ("info@", "contact@", "mail@", "administratie@", "offerte@", "verkoop@")

CONTACT_HINTS = ("contact", "over-ons", "overons", "about", "kontakt")


@dataclass
class Hit:
    slug: str
    company: str
    kvk: str
    domain: str = ""
    email: str = ""
    verified_by: str = ""  # "kvk-nummer" | "naam" | ""
    note: str = ""


def tokens(name: str) -> list[str]:
    """Distinctive words in a company name, longest first."""
    words = re.findall(r"[a-z0-9]+", name.lower())
    return sorted((w for w in words if w not in GENERIC and len(w) > 2), key=len, reverse=True)


def collapse_initials(words: list[str]) -> list[str]:
    """Run of single letters becomes one token: T.I.B. Verkuylen -> tib verkuylen.

    Left as separate words it hyphenates to t-i-b-verkuylen.nl, and the domain the
    company actually owns is tib-verkuylen.nl."""
    out: list[str] = []
    for w in words:
        if len(w) == 1 and out and len(out[-1]) <= 3 and out[-1].isalpha() and len(out[-1]) < 4:
            out[-1] += w
        else:
            out.append(w)
    return out


def domain_candidates(name: str, city: str = "") -> list[str]:
    """Domains worth trying, best guess first.

    Every shape here was read off a domain a real prospect turned out to own, so the list
    is evidence rather than imagination: the whole name run together (ajdakwerken.nl), the
    name minus its trade word (visservanderhell.nl), the same hyphenated
    (smits-installaties.nl, tib-verkuylen.nl), a "bv" suffix (lvanderwielbv.nl,
    herfstbv.nl), the trade word glued to the surname in either order
    (valkenburgloodgieters.nl), and the surname plus the city (barendseleiden.nl).

    A handful stay out of reach -- MD Dak & Klusbedrijf trades as dakdekkerutrechtbv.nl,
    which no transformation of its own name produces. Those are what worklist.csv is for.
    """
    words = collapse_initials(re.findall(r"[a-z0-9]+", LEGAL_FORM_RE.sub("", name).lower()))
    if not words:
        return []
    no_trade = [w for w in words if w not in TRADE_WORDS]
    distinctive = [w for w in words if w not in GENERIC]
    trade = next((w for w in words if w in TRADE_WORDS and len(w) > 3), "")
    surname = distinctive[-1] if distinctive else ""

    def joined(parts: list[str], sep: str = "") -> str:
        return sep.join(parts)

    out = [
        joined(words),
        joined(no_trade),
        joined(no_trade, "-"),
        joined(words, "-"),
        joined(distinctive),
        joined(no_trade) + "bv",
        surname + trade,
        trade + surname,
        joined(distinctive) + trade,
        joined(distinctive) + re.sub(r"[^a-z]", "", city.lower()),
        joined(distinctive) + "bv",
    ]

    seen, uniq = set(), []
    for d in out:
        d = d.strip("-")
        if 3 < len(d) < 40 and d not in seen and not d.endswith("-"):
            seen.add(d)
            uniq.append(f"{d}.nl")
    return uniq[:8]


def fetch(url: str, *, want_html: bool = True) -> str | None:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            ctype = resp.headers.get("Content-Type", "")
            if resp.status != 200 or (want_html and ctype and "html" not in ctype):
                return None
            return resp.read(600_000).decode(
                resp.headers.get_content_charset() or "utf-8", "replace"
            )
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError):
        return None


def allowed(domain: str) -> bool:
    """robots.txt, failing open -- a site with no robots.txt has not said no.

    RobotFileParser.read() is deliberately not used: it fetches with Python's stock
    urllib User-Agent, which enough hosting stacks answer with a 403, and the parser
    reads any 403 as "disallow everything". That silently turned four sites whose
    robots.txt allows all crawlers into refusals. Fetching it ourselves and handing the
    parser the text avoids inventing a prohibition nobody wrote."""
    body = fetch(f"https://{domain}/robots.txt", want_html=False)
    if body is None:
        return True
    rp = urllib.robotparser.RobotFileParser()
    rp.parse(body.splitlines())
    return rp.can_fetch(BOT_TOKEN, f"https://{domain}/")


def emails_in(html: str, domain: str) -> list[str]:
    """Published addresses, own-domain first, role addresses before personal ones."""
    found = {m.group(0).lower().rstrip(".") for m in EMAIL_RE.finditer(html)}
    clean = [
        e
        for e in found
        if not e.endswith(JUNK_DOMAIN)
        and e.split("@")[0] not in JUNK_LOCAL
        and not re.search(r"\.(png|jpe?g|gif|svg|webp|css|js)$", e)
    ]
    root = domain.removeprefix("www.")

    def rank(e: str) -> tuple[int, int]:
        own = 0 if e.endswith(f"@{root}") or e.endswith(f".{root}") else 1
        role = next((i for i, p in enumerate(PREFERRED) if e.startswith(p)), len(PREFERRED))
        return (own, role)

    return sorted(clean, key=rank)


def headline(html: str) -> str:
    """The page's <title> and <h1>, letters and digits only.

    Matching the company name against the whole page is too loose -- a stranger's site
    mentioning "meijer" once is enough to pass. A business puts its own name in its
    title, so matching there is a far better proxy for "this site belongs to them"."""
    parts = re.findall(r"<title[^>]*>(.*?)</title>|<h1[^>]*>(.*?)</h1>", html, re.I | re.S)
    flat = " ".join(p for pair in parts for p in pair if p)
    return re.sub(r"[^a-z0-9]", "", TAG_RE.sub(" ", flat).lower())


def verify(html: str, kvk: str, name: str, *, rank: int) -> str | None:
    """How we know this site is the company we looked up, or None if we do not.

    The KVK number is near-proof: a Dutch business must publish it and no two companies
    share one, so when sourcing.py hands us one this is effectively settled.

    Without it we are guessing, and the validation run showed how that goes wrong:
    meijer.nl contains the word "meijer" and belongs to a different Meijer entirely, so
    Loodgietersbedrijf Meijer got "verified" onto a stranger. The name is therefore
    matched against the page title rather than its body, and a bare distinctive word is
    only accepted on the first, best-guess domain -- on the wilder later candidates a
    single matching word is coincidence more often than not.
    """
    text = TAG_RE.sub(" ", html).lower()
    if kvk and kvk in KVK_RE.findall(text):
        return "kvk-nummer"

    head = headline(html)
    if not head:
        return None
    words = collapse_initials(re.findall(r"[a-z0-9]+", LEGAL_FORM_RE.sub("", name).lower()))
    needle = "".join(w for w in words if w not in CONNECTIVES)
    if len(needle) > 5 and needle in head:
        return "naam"
    # Flattening the title loses word boundaries, so a short token matches inside longer
    # words -- "wiel" is a hit on "Wiel Autobanden". Six characters of distinctive name is
    # the least that identifies a company rather than a coincidence.
    distinctive = [w for w in words if w not in GENERIC and len(w) > 3]
    if (
        rank == 0
        and sum(map(len, distinctive[:2])) >= 6
        and all(t in head for t in distinctive[:2])
    ):
        return "naam"
    return None


def resolve(c: Candidate) -> Hit:
    hit = Hit(slug=c.slug, company=c.name, kvk=c.kvk)
    for rank, domain in enumerate(domain_candidates(c.name, c.city)):
        if not allowed(domain):
            hit.note = f"{domain}: robots.txt says no"
            continue
        html = fetch(f"https://{domain}") or fetch(f"https://www.{domain}")
        time.sleep(DELAY)
        if not html:
            continue
        proof = verify(html, c.kvk, c.name, rank=rank)
        if not proof:
            hit.note = f"{domain} resolved but is someone else"
            continue

        hit.domain, hit.verified_by = domain, proof
        found = emails_in(html, domain)
        if not found:  # the homepage often only links to the contact page
            for path in contact_paths(html):
                page = fetch(urllib.parse.urljoin(f"https://{domain}", path))
                time.sleep(DELAY)
                if page:
                    found = emails_in(page, domain)
                    if found:
                        break
        if found:
            hit.email = found[0]
            return hit
        hit.note = "site verified, no address published"
        return hit
    if not hit.note:
        hit.note = "no domain resolved"
    return hit


def contact_paths(html: str) -> list[str]:
    out = []
    for m in re.finditer(r'href=["\']([^"\']+)["\']', html, re.I):
        href = m.group(1)
        if any(h in href.lower() for h in CONTACT_HINTS) and not href.startswith(
            ("http", "mailto")
        ):
            out.append(href)
    return out[:2]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--in", dest="src", default=str(OUT / "qualified.json"))
    ap.add_argument("--limit", type=int, help="only the first N companies")
    ap.add_argument("--write", action="store_true", help="write the CSVs (default: report only)")
    args = ap.parse_args()

    src = Path(args.src)
    if not src.exists():
        sys.exit(f"{src} missing -- run `python -m scripts.sourcing qualify` first")
    rows = json.loads(src.read_text())[: args.limit]
    if not rows:
        sys.exit(f"{src} is empty")

    hits = []
    for i, row in enumerate(rows, 1):
        hit = resolve(Candidate(**row))
        hits.append(hit)
        mark = hit.email or hit.note
        print(f"[{i:3}/{len(rows)}] {hit.company[:34]:34} {mark}")

    found = [h for h in hits if h.email]
    print(f"\n{len(found)}/{len(hits)} addresses found ({len(found) * 100 // max(len(hits), 1)}%)")
    by_proof: dict[str, int] = {}
    for h in found:
        by_proof[h.verified_by] = by_proof.get(h.verified_by, 0) + 1
    for proof, n in by_proof.items():
        print(f"  {n:4} verified by {proof}")

    if not args.write:
        print("\nreport only -- re-run with --write to save")
        return

    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "enriched.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["slug", "company_name", "kvk", "email", "website", "verified_by"])
        for h in found:
            w.writerow([h.slug, h.company, h.kvk, h.email, f"https://{h.domain}", h.verified_by])

    misses = [h for h in hits if not h.email]
    with (OUT / "worklist.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["company_name", "kvk", "why", "search"])
        for h in misses:
            query = urllib.parse.quote_plus(f"{h.company} contact")
            w.writerow([h.company, h.kvk, h.note, f"https://duckduckgo.com/?q={query}"])

    print(f"\n{len(found)} -> {OUT}/enriched.csv")
    print(f"{len(misses)} -> {OUT}/worklist.csv (search URL each; ~30s of a human per row)")


if __name__ == "__main__":
    main()
