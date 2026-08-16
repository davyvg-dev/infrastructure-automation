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

The site is then read for everything it publishes, not the address alone: a telephone
number and the company's own KVK number come off the same page for free. The number
matters more than the address for a trade, who answers a mobile and does not read e-mail.
The KVK number matters because it turns a name the rep typed into a register key.

Measured 2026-08-16 against the 24 NL prospects whose contacts are known, given nothing
but the business name: 8 domains resolved, and on those 8 the page yielded 8 telephone
numbers, 7 e-mail addresses and 5 KVK numbers. Six match the pipeline record exactly. One
(Smits Installaties) resolved onto smitsinstallaties.nl where the record says
smits-installaties.nl, and nothing short of a KVK number can say which is theirs; one
(Duckdekker) publishes an 085 number the record does not carry. So: extraction is close to
free once a domain resolves, and resolving the domain is the whole problem -- two thirds
never got that far and land in worklist.csv with a search URL, about thirty seconds of a
human each.

Read that precision honestly. A name-only proof is a guess with a good prior, not a fact,
and the two doubtful rows above are both name-only. A KVK number from the register turns
every one of them into certainty, which is what `sourcing.py` supplies and what the
--names mode, by construction, does not have.

Hand it the website instead and the same 23 companies go 21 reachable: 18 addresses, all
18 exactly right, 20 telephone numbers, 18 of them exactly right, and 8 KVK numbers. That
is the whole argument for the `website` argument. Guessing the domain is the only weak
link in here; a rep copying the site off a LinkedIn company page in ten seconds removes
it, and no amount of further cleverness in domain_candidates would come close.

One result in that run was a bug rather than a miss, and it is the reason to measure
against known answers rather than eyeball a sample: valkenburgloodgieters.nl echoes the
visitor's User-Agent into its HTML, ours names a contact address, and the crawler read its
own footprint back as the prospect's e-mail. See JUNK_DOMAIN.

    python -m scripts.enrich                       # dry: resolve + verify, report only
    python -m scripts.enrich --write               # write enriched.csv + worklist.csv
    python -m scripts.enrich --limit 20            # trial run over the first 20
    python -m scripts.enrich --names clips.txt --json out.json   # a rep's LinkedIn clips

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
from dataclasses import asdict, dataclass
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

# A bare run of eight digits is a postcode-plus-something as often as it is a KVK number,
# so the number is only believed when the page labels it one. Dutch sites write it a dozen
# ways -- "KvK-nummer:", "KVK nr.", "Kamer van Koophandel" -- hence the loose gap.
KVK_LABEL_RE = re.compile(r"(?:kvk|kamer\s+van\s+koophandel)[^0-9]{0,24}(\d{8})", re.I)

# tel: links are the only place a phone number is unambiguously marked as one. Everything
# else on a Dutch page that looks like a number might be a postcode, a BTW id or a year.
TEL_HREF_RE = re.compile(r'href=["\']tel:([^"\']+)["\']', re.I)

# The text fallback, deliberately narrow: 06-nummers, 3-digit area codes (010, 020, 070),
# 4-digit area codes (0182, 0341), 0800/0900 service numbers, and the +31 forms of each.
# Separators are optional and free-form because every site invents its own.
PHONE_TEXT_RE = re.compile(
    r"(?<![0-9A-Za-z])(?:\+31[\s\-.]?\(?0?\)?[\s\-.]?|0)"
    r"(?:6[\s\-.]?(?:\d[\s\-.]?){8}"
    r"|[1-9]\d[\s\-.]?(?:\d[\s\-.]?){7}"
    r"|[1-9]\d{2}[\s\-.]?(?:\d[\s\-.]?){6})"
    r"(?![\d])"
)

# Blanked before the fallback runs. A Dutch bank account is ten digits that pass every test
# a phone number passes -- NL91 ABNA 0417 1643 00 yields 0417164300 -- and it sits in the
# same footer as the number we actually want. Guarding the pattern is not enough: spaced
# IBANs put a legal separator exactly where the match wants to start.
IBAN_RE = re.compile(r"\b[A-Z]{2}\d{2}(?:\s?[A-Z0-9]){10,30}\b")

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

# Where the company works, not which company it is. Only ever used to refuse a name-based
# proof: a name made of nothing but a trade and a place identifies no one. Collisions with
# real surnames (Bergen, Ede) cost a missed hit, never a wrong one -- the company lands in
# worklist.csv for a human instead of on a stranger's telephone number.
PLACE_WORDS = {
    "alkmaar",
    "almere",
    "alphen",
    "amersfoort",
    "amstelveen",
    "amsterdam",
    "apeldoorn",
    "arnhem",
    "assen",
    "barneveld",
    "bergen",
    "breda",
    "brunssum",
    "capelle",
    "delft",
    "deventer",
    "doetinchem",
    "dordrecht",
    "drachten",
    "ede",
    "eindhoven",
    "emmen",
    "enschede",
    "etten",
    "geleen",
    "goes",
    "gouda",
    "groningen",
    "haag",
    "haarlem",
    "hardenberg",
    "heerlen",
    "helmond",
    "hertogenbosch",
    "hilversum",
    "hoogeveen",
    "hoorn",
    "houten",
    "ijsselstein",
    "kampen",
    "katwijk",
    "kerkrade",
    "leeuwarden",
    "leiden",
    "lelystad",
    "maastricht",
    "middelburg",
    "nieuwegein",
    "nijmegen",
    "oosterhout",
    "oss",
    "purmerend",
    "rijswijk",
    "roermond",
    "roosendaal",
    "rotterdam",
    "schiedam",
    "sittard",
    "sneek",
    "spijkenisse",
    "terneuzen",
    "tiel",
    "tilburg",
    "uden",
    "utrecht",
    "veenendaal",
    "veghel",
    "velsen",
    "venlo",
    "vlaardingen",
    "vlissingen",
    "waalwijk",
    "weert",
    "woerden",
    "zaanstad",
    "zeist",
    "zoetermeer",
    "zwolle",
}

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
    # Our own, and not paranoia. valkenburgloodgieters.nl runs a WordPress plugin that
    # prints the visitor's User-Agent into the page, and ours carries a contact address --
    # so the crawler read its own footprint back and reported davy@klantkraan.nl as the
    # prospect's e-mail. Escaping defeats stripping the UA string literally; refusing our
    # own domain cannot be evaded. We are never a prospect's contact address.
    "klantkraan.nl",
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
    phone: str = ""
    kvk_found: str = ""  # the KVK number the site publishes, when the register gave us none
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


def normalise_phone(raw: str) -> str:
    """A Dutch number in one shape, or "" if it is not one.

    Sites publish the same number a dozen ways -- 010-412 57 00, (010) 4125700,
    +31(0)10 412 5700 -- and the pipeline record, the suppression list and Notion all have
    to agree on which of them is "the number", or an opt-out silently stops matching.
    National 0-prefixed form is the one a Dutch reader recognises, so that is the one kept.
    """
    digits = re.sub(r"[^\d+]", "", raw)
    if digits.startswith("+31"):
        digits = "0" + digits[3:].lstrip("0")
    elif digits.startswith("0031"):
        digits = "0" + digits[4:].lstrip("0")
    digits = re.sub(r"\D", "", digits)
    if len(digits) != 10 or not digits.startswith("0") or digits[1] == "0":
        return ""
    return digits


def phones_in(html: str) -> list[str]:
    """Published telephone numbers, the ones the page marks as such first.

    A tel: href is the only unambiguous signal -- the site itself is asserting "this is a
    phone number". Free text is guesswork by comparison, which is why the fallback pattern
    only accepts real Dutch number shapes: a postcode, a BTW id and a KVK number all look
    like phone numbers to a loose regex, and all three sit in the same footer.
    """
    out: list[str] = []
    for m in TEL_HREF_RE.finditer(html):
        n = normalise_phone(m.group(1))
        if n and n not in out:
            out.append(n)
    if out:
        return out
    text = IBAN_RE.sub(" ", TAG_RE.sub(" ", html))
    for m in PHONE_TEXT_RE.finditer(text):
        n = normalise_phone(m.group(0))
        if n and n not in out:
            out.append(n)
    return out


def kvk_in(html: str) -> str:
    """The KVK number the site publishes, or "".

    Worth reading even though sourcing.py normally supplies one: a prospect the rep clipped
    off LinkedIn has no register lookup behind it, and Dutch law makes a company print this
    number on its own website. That turns a name into a register key for nothing.
    """
    text = TAG_RE.sub(" ", html)
    m = KVK_LABEL_RE.search(text)
    return m.group(1) if m else ""


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

    # A trade named after its city -- "Loodgieter Utrecht", "Dakdekker Amsterdam" -- owns no
    # distinctive word, and every competitor in that city owns a near-identical domain. The
    # ground-truth run proved it: loodgieterutrecht.nl passed the title test for Loodgieter
    # Utrecht B.V. and belongs to somebody else, whose number would then have been dialled.
    # Trade plus place is not an identity. Only the KVK number above can prove one of these.
    if not [w for w in words if w not in GENERIC and w not in PLACE_WORDS]:
        return None

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


def host_of(url: str) -> str:
    """The bare hostname out of whatever shape a human pasted the address in."""
    url = url.strip()
    if not url:
        return ""
    if "://" not in url:
        url = "https://" + url
    return urllib.parse.urlparse(url).netloc.removeprefix("www.").lower()


def resolve(c: Candidate, *, website: str = "") -> Hit:
    """Everything the company publishes about how to reach it.

    Pass `website` whenever anyone already knows it. The ground-truth run says guessing the
    domain is the only weak link in here -- it reached 8 of 24 companies, while the pages it
    did reach gave up a telephone number 8 times out of 8. So thirty seconds of a rep
    copying the website off a LinkedIn company page is worth more than any amount of extra
    cleverness in domain_candidates, and it skips the proof problem entirely: a human
    saying "this is their site" beats a name matched against a page title.
    """
    hit = Hit(slug=c.slug, company=c.name, kvk=c.kvk)
    given = host_of(website)
    for rank, domain in enumerate([given] if given else domain_candidates(c.name, c.city)):
        if not allowed(domain):
            hit.note = f"{domain}: robots.txt says no"
            continue
        html = fetch(f"https://{domain}") or fetch(f"https://www.{domain}")
        time.sleep(DELAY)
        if not html:
            hit.note = f"{domain} did not respond"
            continue
        # A KVK match still upgrades the proof: the rep can paste the wrong URL too.
        proof = verify(html, c.kvk, c.name, rank=rank) or ("opgegeven" if given else "")
        if not proof:
            hit.note = f"{domain} resolved but is someone else"
            continue

        hit.domain, hit.verified_by = domain, proof
        found = emails_in(html, domain)
        phones = phones_in(html)
        hit.kvk_found = kvk_in(html)

        # The homepage usually only links to the contact page. Walk it while anything is
        # still missing, not just when the address is -- a trade that publishes its number
        # on every page may still keep the mailbox and the KVK number on /contact alone.
        if not (found and phones and hit.kvk_found):
            for path in contact_paths(html):
                page = fetch(urllib.parse.urljoin(f"https://{domain}", path))
                time.sleep(DELAY)
                if not page:
                    continue
                found = found or emails_in(page, domain)
                phones = phones or phones_in(page)
                hit.kvk_found = hit.kvk_found or kvk_in(page)
                if found and phones and hit.kvk_found:
                    break

        hit.email = found[0] if found else ""
        hit.phone = phones[0] if phones else ""
        if not (hit.email or hit.phone):
            hit.note = "site verified, publishes neither address nor number"
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
    ap.add_argument(
        "--names",
        help="a text file of prospects, one per line, as 'Company, City | website'. "
        "City and website are both optional; the website is worth far more. "
        "For prospects that never came from the register -- a rep's LinkedIn clips.",
    )
    ap.add_argument("--limit", type=int, help="only the first N companies")
    ap.add_argument("--write", action="store_true", help="write the CSVs (default: report only)")
    ap.add_argument("--json", dest="json_out", help="also dump every hit as JSON to this path")
    args = ap.parse_args()

    if args.names:
        src = Path(args.names)
        if not src.exists():
            sys.exit(f"{src} missing")
        candidates = []
        for line in src.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            who, _, site = line.partition("|")
            name, _, city = who.partition(",")
            candidates.append(
                (Candidate(kvk="", name=name.strip(), city=city.strip(), trade=""), site.strip())
            )
        candidates = candidates[: args.limit]
    else:
        src = Path(args.src)
        if not src.exists():
            sys.exit(f"{src} missing -- run `python -m scripts.sourcing qualify` first")
        candidates = [(Candidate(**row), "") for row in json.loads(src.read_text())[: args.limit]]
    if not candidates:
        sys.exit(f"{src} is empty")

    hits = []
    for i, (c, site) in enumerate(candidates, 1):
        hit = resolve(c, website=site)
        hits.append(hit)
        mark = " ".join(x for x in (hit.email, hit.phone) if x) or hit.note
        print(f"[{i:3}/{len(candidates)}] {hit.company[:34]:34} {mark}")

    n = len(hits)
    mailable = [h for h in hits if h.email]
    callable_ = [h for h in hits if h.phone]
    reachable = [h for h in hits if h.email or h.phone]
    kvks = [h for h in hits if h.kvk_found]
    print(f"\n{len(reachable)}/{n} reachable ({len(reachable) * 100 // max(n, 1)}%)")
    print(f"  {len(mailable):4} with an e-mail address")
    print(f"  {len(callable_):4} with a telephone number")
    print(f"  {len(kvks):4} with a KVK number read off the site")
    by_proof: dict[str, int] = {}
    for h in reachable:
        by_proof[h.verified_by] = by_proof.get(h.verified_by, 0) + 1
    for proof, count in by_proof.items():
        print(f"  {count:4} verified by {proof}")

    if args.json_out:
        Path(args.json_out).write_text(json.dumps([asdict(h) for h in hits], indent=2))
        print(f"\n{n} -> {args.json_out}")

    if not args.write:
        print("\nreport only -- re-run with --write to save")
        return

    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "enriched.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(
            ["slug", "company_name", "kvk", "kvk_site", "email", "phone", "website", "verified_by"]
        )
        for h in reachable:
            w.writerow(
                [
                    h.slug,
                    h.company,
                    h.kvk,
                    h.kvk_found,
                    h.email,
                    h.phone,
                    f"https://{h.domain}",
                    h.verified_by,
                ]
            )

    misses = [h for h in hits if not (h.email or h.phone)]
    with (OUT / "worklist.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["company_name", "kvk", "why", "search"])
        for h in misses:
            query = urllib.parse.quote_plus(f"{h.company} contact")
            w.writerow([h.company, h.kvk, h.note, f"https://duckduckgo.com/?q={query}"])

    print(f"\n{len(reachable)} -> {OUT}/enriched.csv")
    print(f"{len(misses)} -> {OUT}/worklist.csv (search URL each; ~30s of a human per row)")


if __name__ == "__main__":
    main()
