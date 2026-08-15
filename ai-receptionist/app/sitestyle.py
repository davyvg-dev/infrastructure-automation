"""Read the visual design of a reference website and map it onto the client-sites vocabulary.

    python -m app.sitestyle --voorbeeld https://voorbeeld.nl
    python -m app.sitestyle --voorbeeld https://a.nl --voorbeeld https://b.nl --vak dakdekker
    python -m app.sitestyle --voorbeeld https://a.nl --feiten     # measure only, no API call

and, with no reference to point at, the factory composes a look itself:

    python -m app.sitestyle --vak dakdekker --naam "Dakwerken Bos" --kleur "#1f3a5f"

Prints the `stijl:` block for a clients/<slug>/client.yaml. The founder points at sites he
likes instead of describing them; the reference drives the SKIN ONLY (see TODO section R),
so layout and section order are untouched by everything below.

Two halves, and the split is the whole point:

  * MEASURING is code. Fetch the page and its stylesheets, then parse out font stacks,
    type sizes, weights, tracking, corner radii, section padding, colours and image
    ratios. The result is numbers, hex values and typeface names -- nothing else.
  * CHOOSING is one schema-constrained Claude call. It picks a named value per axis and
    writes one Dutch line saying why. It never emits CSS: every value it can return is
    already in `src/lib/stijl.ts` and has been looked at once on a real build.

The composing path is the same call with the measurements replaced by the three things a
prospect always has -- vak, company name, brand colours -- and a shortlist per axis instead
of the whole vocabulary. Both paths end in the same schema, the same validator and the same
yaml block, so there is one place where a look can go wrong.

Design parameters are facts about a page. Its copy, photographs and logo are not ours, so
the extractor collects no text at all -- there is no path by which a sentence from the
reference could reach the model, let alone a client's site. The one free-text field that
does travel is the typeface name, and that is sanitised to [A-Za-z0-9 -] before it goes.
(The client's own name does travel on the composing path. It is ours, it is already in
every sitedraft call, and it is the one input the look has to survive.)

The vocabulary is read out of stijl.ts rather than restated here: a value this module
offers that the resolver does not know would fail the Zod schema at build time, on the
founder's machine, after the voorstel was already written.

Docs fetched via the claude-api skill (2026-08-15): structured outputs support `enum` and
`const`, and require `additionalProperties: false` on every object; adaptive thinking is on
by default on claude-opus-5 and `max_tokens` caps thinking plus text together.
"""

from __future__ import annotations

import argparse
import colorsys
import hashlib
import json
import re
import statistics
import sys
import textwrap
import urllib.parse
import urllib.request
from collections import Counter
from collections.abc import Iterator
from html.parser import HTMLParser

import anthropic

from . import settings

# The mapping is a judgement call over a table of numbers, and the schema does most of the
# constraining, so this sits a notch below the copy call in sitedraft.
_MODEL = {"id": "claude-opus-5", "effort": "medium"}

_UA = "KlantkraanIntake/1.0 (+https://klantkraan.nl)"

# The design vocabulary, single-sourced from the resolver that has to render it.
STIJL_TS = (
    settings.ROOT.parent / "klantkraan" / "apps" / "client-sites" / "src" / "lib" / "stijl.ts"
)

# TS constant -> client.yaml key. Both halves are load-bearing: the TS name is what we parse
# out of stijl.ts, the yaml key is what the Zod schema expects back.
_AS_CONST = {
    "LETTERONTWERPEN": "letterontwerp",
    "SCHALEN": "schaal",
    "VORMEN": "vorm",
    "RITMES": "ritme",
    "PALETTEN": "palet",
    "KLEURINGEN": "kleuring",
    "FOTOZETTINGEN": "foto",
}

# Fetch budget. A reference site is read once, by hand, for one voorstel; these caps exist so
# a single pathological page (a 6 MB Tailwind bundle, forty stylesheets) cannot hang the run.
_MAX_SHEETS = 8
_MAX_BYTES = 400_000
_TIMEOUT = 10


class StyleError(RuntimeError):
    """Raised when a reference cannot be measured, or the mapping cannot be trusted."""


# --- the vocabulary -----------------------------------------------------------------------

_CONST_RE = re.compile(r"export const (\w+) = \[(.*?)\] as const", re.S)
_QUOTED_RE = re.compile(r"'([a-z]+)'")

_vocabulaire: dict[str, list[str]] | None = None


def vocabulaire() -> dict[str, list[str]]:
    """{axis: [allowed values]}, read from stijl.ts and cached.

    Parsed rather than restated because these two files have to agree exactly: a value only
    this module knows about would pass the API schema here and fail Zod at build time.
    """
    global _vocabulaire
    if _vocabulaire is not None:
        return _vocabulaire
    try:
        source = STIJL_TS.read_text(encoding="utf-8")
    except OSError as err:
        raise StyleError(f"kan de stijl-vocabulaire niet lezen ({STIJL_TS}): {err}") from err
    found = {name: _QUOTED_RE.findall(body) for name, body in _CONST_RE.findall(source)}
    axes: dict[str, list[str]] = {}
    for const, key in _AS_CONST.items():
        values = found.get(const)
        if not values:
            raise StyleError(
                f"{STIJL_TS.name} bevat geen bruikbare `{const}`; is de vocabulaire hernoemd?"
            )
        axes[key] = values
    _vocabulaire = axes
    return axes


# The length of `bedrijf.naam` above which the `groot` type scale is withdrawn.
#
# The H1 is "<bedrijf.naam>: vakwerk waar u op kunt rekenen." in the hero's half-width
# column, which stops growing at ~480px because max-w-5xl does. Measured in the browser on a
# real build at 1440x800: at `groot` a 33-character name sets in four lines, a 35-character
# one in five, and "Installatietechniek Van der Veldenhuizen" turns the first screen into a
# five-line wall with the WhatsApp button below the fold. `normaal` still holds four lines
# there. R1 capping `groot` at 3.5rem is what keeps the call button on screen at all; this
# is the other half of the same defect, the headline that is legal but unreadable.
NAAM_MAX_GROOT = 34


def allowed(naam: str | None = None) -> dict[str, list[str]]:
    """The vocabulary minus the values this particular client cannot have.

    Applied to both paths, because it is a property of the client rather than of the mode:
    a reference site with a 64px display face is no reason to set a 39-character company
    name at `groot`, and the resulting page is the same page either way.
    """
    axes = {axis: list(values) for axis, values in vocabulaire().items()}
    if naam and len(naam.strip()) >= NAAM_MAX_GROOT:
        axes["schaal"] = [v for v in axes["schaal"] if v != "groot"]
    return axes


# `systeem` is the one value the composer is never offered. It is not a look, it is what a
# page looks like when nobody chose a typeface (R2), and a factory asked to compose one
# cannot answer "none". Measuring a reference genuinely set in Arial still maps to it --
# that is a reading, not a decision.
_NIET_COMPONEERBAAR = {"letterontwerp": {"systeem"}}

# How many values per axis the composer gets to choose between. Two: enough that the choice
# is still a judgement about this client, few enough that two clients rarely share a shortlist.
# The cost is real -- a shortlist sometimes withholds the value that would have been best,
# `ritme: ruim` above all -- and that is the trade being made on purpose. Handed the whole
# vocabulary the model would keep reaching for the same best answer, which is a factory that
# builds one site with a longer prompt.
_KANDIDATEN = 2


def _seed(naam: str) -> int:
    """A stable integer from a company name. blake2b rather than hash(), which is salted per
    process -- the same client has to compose the same site tomorrow, or the founder cannot
    fix a typo in the yaml without redesigning the page."""
    genormaliseerd = re.sub(r"[^a-z0-9]", "", naam.lower())
    return int.from_bytes(hashlib.blake2b(genormaliseerd.encode(), digest_size=8).digest(), "big")


def candidates(naam: str) -> dict[str, list[str]]:
    """Per-axis shortlists for the composer, rotated by the client's name.

    Why the composer is not simply handed the whole vocabulary: its inputs are the vak, the
    name and the brand colours, and sitedraft gives every prospect the same DEFAULT_PRIMARY
    until the founder overrides it. Six dakdekkers drafted in one week would arrive with
    near-identical inputs and leave with an identical skin -- which is the defect section R
    exists to fix, rebuilt one layer up. A prompt asking for variety is a hope; a shortlist
    that differs per client is a rule, and it is the same kind of rule as the enum itself.

    What it is not: a preset. The shortlist says which two values are on the table, the
    model still has to argue from the vak and the colours which of them this client gets.
    """
    zaad = _seed(naam)
    out: dict[str, list[str]] = {}
    for i, (axis, values) in enumerate(allowed(naam).items()):
        pool = [v for v in values if v not in _NIET_COMPONEERBAAR.get(axis, frozenset())]
        if len(pool) <= _KANDIDATEN:
            out[axis] = pool
            continue
        # A separate slice of the digest per axis, so the axes rotate independently: one
        # shared offset would tie palet to vorm and give the whole vocabulary seven looks.
        start = (zaad >> (7 * i)) % len(pool)
        out[axis] = [pool[(start + n) % len(pool)] for n in range(_KANDIDATEN)]
    return out


_HEX_OK = re.compile(r"^#[0-9a-fA-F]{6}$")


def _check_hex(kleur: str) -> str:
    """Format only. Whether a primary is dark enough for white text is the client-sites
    schema's job and sitedraft's; here the colour is an input to a judgement, not a value
    written to yaml, so re-asserting it would only give the founder two errors for one typo."""
    if not _HEX_OK.match(kleur or ""):
        raise StyleError(f"kleur {kleur!r} moet een #rrggbb hex-waarde zijn")
    return kleur.lower()


# --- fetching -----------------------------------------------------------------------------


class _Assets(HTMLParser):
    """Collect stylesheet links, inline <style> bodies and image dimensions.

    Deliberately blind to text: no handle_data outside <style>, so no sentence of the
    reference's copy is ever held in memory, and none can leak into the model call.
    """

    def __init__(self) -> None:
        super().__init__()
        self.sheets: list[str] = []
        self.styles: list[str] = []
        self.ratios: list[float] = []
        self._in_style = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "style":
            self._in_style = True
        elif tag == "link":
            rels = a.get("rel", "").lower().split()
            if "stylesheet" in rels and a.get("href"):
                self.sheets.append(a["href"])
        elif tag == "img":
            ratio = _ratio(a.get("width", ""), a.get("height", ""))
            if ratio:
                self.ratios.append(ratio)

    def handle_endtag(self, tag: str) -> None:
        if tag == "style":
            self._in_style = False

    def handle_data(self, data: str) -> None:
        if self._in_style:
            self.styles.append(data)


def _ratio(width: str, height: str) -> float | None:
    """An <img> width/height pair as w/h, or None when either is missing or nonsense."""
    try:
        w, h = float(re.sub(r"[^\d.]", "", width)), float(re.sub(r"[^\d.]", "", height))
    except ValueError:
        return None
    if w <= 0 or h <= 0 or not 0.1 < w / h < 10:
        return None
    return round(w / h, 2)


def _get(url: str) -> str:
    """Fetch one URL as text. Returns '' on anything that is not a 200 -- never raises."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": _UA})
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            if getattr(resp, "status", 200) != 200:
                return ""
            return resp.read(_MAX_BYTES).decode("utf-8", "replace")
    except Exception:
        return ""


def _google_fonts(href: str) -> list[dict]:
    """Families and weights out of a fonts.googleapis.com URL.

    Parsed from the query rather than fetched: the stylesheet behind it is a list of
    @font-face rules pointing at binaries, and the URL already carries everything we
    measure. It also keeps one more third-party request out of the run.
    """
    query = urllib.parse.urlparse(href).query
    out = []
    for key, value in urllib.parse.parse_qsl(query):
        if key != "family" or not value:
            continue
        family, _, axes = value.partition(":")
        gewichten = sorted({int(n) for n in re.findall(r"\b([1-9]00)\b", axes.rpartition("@")[2])})
        naam = _familie(family)
        if naam:
            out.append({"familie": naam, "gewichten": gewichten})
    return out


def gather_css(url: str) -> tuple[str, list[float], list[dict]]:
    """Fetch a page and its stylesheets. Returns (css, image ratios, google font links)."""
    html = _get(url)
    if not html:
        raise StyleError(f"{url} gaf geen leesbare pagina terug; controleer de URL")
    assets = _Assets()
    assets.feed(html)

    css = list(assets.styles)
    fonts: list[dict] = []
    seen: set[str] = set()
    for href in assets.sheets:
        full = urllib.parse.urljoin(url, href)
        if not full.startswith(("http://", "https://")) or full in seen:
            continue
        seen.add(full)
        if "fonts.googleapis.com" in full:
            fonts.extend(_google_fonts(full))
            continue
        if len(seen) > _MAX_SHEETS:
            break
        sheet = _get(full)
        if sheet:
            css.append(sheet)
    return "\n".join(css), assets.ratios, fonts


# --- CSS parsing --------------------------------------------------------------------------
#
# A regex-and-brace-counting parser, not a spec-compliant one. It is looking for the
# distribution of a handful of properties across a whole stylesheet, so a rule mangled by a
# brace inside a string costs one sample out of hundreds. A real CSS parser would be a
# dependency and a maintenance surface for no measurable gain.

_COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)
# At-rules whose body is more rules rather than declarations, so we descend into them.
_NESTING_AT = {"media", "supports", "layer", "container", "scope"}


def _iter_rules(css: str, depth: int = 0) -> Iterator[tuple[str, str]]:
    """Yield (selector, declaration block) for every rule, @font-face included."""
    if depth > 4:
        return
    i, n = 0, len(css)
    while i < n:
        brace = css.find("{", i)
        if brace == -1:
            return
        prelude = css[i:brace].strip()
        level, j = 1, brace + 1
        while j < n and level:
            if css[j] == "{":
                level += 1
            elif css[j] == "}":
                level -= 1
            j += 1
        body, i = css[brace + 1 : j - 1], j
        if not prelude.startswith("@"):
            yield prelude, body
            continue
        at = prelude[1:].split(None, 1)[0].lower()
        if at in _NESTING_AT:
            yield from _iter_rules(body, depth + 1)
        elif at == "font-face":
            yield "@font-face", body
        # @keyframes and friends: animation frames are not design parameters.


def _decls(body: str) -> Iterator[tuple[str, str]]:
    """Yield (property, value) pairs, splitting on top-level semicolons only."""
    depth, buf, parts = 0, [], []
    for ch in body:
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth = max(0, depth - 1)
        if ch == ";" and depth == 0:
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    parts.append("".join(buf))
    for part in parts:
        prop, sep, value = part.partition(":")
        prop = prop.strip().lower()
        if sep and prop and re.fullmatch(r"-?[a-z-]+", prop):
            yield prop, value.strip()


# Every length is resolved against one assumed desktop viewport. A stylesheet has no
# viewport, so a vw length has no px value until you pick one; 1440x900 is the screen these
# sites are art-directed on, and it is the width the founder will be looking at when he
# compares the reference to the build. rem is assumed to be 16px -- sites that move the root
# size exist, but carrying that uncertainty into every measurement costs more than it buys.
_VIEWPORT_W, _VIEWPORT_H = 1440.0, 900.0
_LEN_RE = re.compile(r"(-?\d*\.?\d+)\s*(px|rem|em|pt|vw|vh|vmin|vmax)\b", re.I)
_UNIT_PX = {
    "px": 1.0,
    "rem": 16.0,
    "em": 16.0,
    "pt": 4 / 3,
    "vw": _VIEWPORT_W / 100,
    "vh": _VIEWPORT_H / 100,
    "vmin": min(_VIEWPORT_W, _VIEWPORT_H) / 100,
    "vmax": max(_VIEWPORT_W, _VIEWPORT_H) / 100,
}
# Only the flat form: a clamp() carrying a calc() has nested parens this cannot split, and
# those fall through to the max-of-all-lengths path below.
_CLAMP_RE = re.compile(r"clamp\(([^()]*)\)", re.I)


def _lengths(value: str) -> list[float]:
    return [float(n) * _UNIT_PX[u.lower()] for n, u in _LEN_RE.findall(value)]


def _px(value: str) -> float | None:
    """A value's px equivalent at the assumed viewport, or None when it has no length.

    clamp() is resolved rather than maximised. `clamp(1.9rem, 4.5vw, 3rem)` is a fluid type
    scale, and at 1440px the middle term is 64.8px while the ceiling is 48px -- taking the
    largest number present would report a size the browser never renders, and would do it
    on exactly the sites that set their type this way (including ours).
    """
    flat = _CLAMP_RE.search(value)
    if flat:
        args = [_lengths(a) for a in flat.group(1).split(",")]
        if len(args) == 3 and all(args):
            lo, mid, hi = (a[0] for a in args)
            return round(min(max(lo, mid), hi), 1)
    sizes = _lengths(value)
    return max(sizes) if sizes else None


def _em(value: str) -> float | None:
    """A tracking value in em (letter-spacing is authored in em far more often than px)."""
    for n, u in _LEN_RE.findall(value):
        if u.lower() in ("em", "rem"):
            return float(n)
        if u.lower() == "px":
            return round(float(n) / 16, 4)
    return None


def _first(value: str) -> str:
    """The first whitespace-separated component of a shorthand (`padding: 5rem 1rem`)."""
    return value.split()[0] if value.split() else ""


_HEX_RE = re.compile(r"#([0-9a-fA-F]{3,8})\b")
_RGB_RE = re.compile(r"rgba?\(\s*([\d.]+)[\s,]+([\d.]+)[\s,]+([\d.]+)", re.I)


def _colour(value: str) -> str | None:
    """First colour in a value, normalised to #rrggbb. None for none/transparent/var()."""
    hexes = _HEX_RE.search(value)
    if hexes:
        raw = hexes.group(1)
        if len(raw) in (3, 4):
            raw = "".join(c * 2 for c in raw[:3])
        if len(raw) >= 6:
            return f"#{raw[:6].lower()}"
    rgb = _RGB_RE.search(value)
    if rgb:
        try:
            r, g, b = (min(255, max(0, int(float(c)))) for c in rgb.groups())
        except ValueError:
            return None
        return f"#{r:02x}{g:02x}{b:02x}"
    return None


def hsl(hex_colour: str) -> dict:
    """#rrggbb -> hue/saturation/lightness, which is what separates the palet axis.

    warm, koel, neutraal and zand differ by the hue and the few percent of saturation in an
    off-white; comparing raw hex values cannot see that, and the model should not be asked
    to do colour arithmetic in its head.
    """
    n = int(hex_colour[1:], 16)
    r, g, b = ((n >> 16) & 0xFF) / 255, ((n >> 8) & 0xFF) / 255, (n & 0xFF) / 255
    h, lightness, s = colorsys.rgb_to_hls(r, g, b)
    return {
        "hex": hex_colour,
        "tint": round(h * 360),
        "verzadiging": round(s * 100),
        "lichtheid": round(lightness * 100),
    }


# --- measuring ----------------------------------------------------------------------------

# Families that mean "nobody chose a typeface": the CSS generics, the system-ui stack, and
# the four faces every default stack falls back to. A reference site whose only font-family
# is one of these is measured as `systeem`, which is exactly what it looks like.
# Comma-separated because two of them contain a space, and one per line is 25 lines of noise.
_GENERIEK = {
    n.strip()
    for n in (
        "sans-serif, serif, monospace, cursive, fantasy, system-ui, ui-sans-serif, ui-serif, "
        "ui-monospace, ui-rounded, inherit, initial, unset, revert, -apple-system, "
        "blinkmacsystemfont, segoe ui, roboto, helvetica neue, helvetica, arial, sans, emoji, "
        "math, fangsong, apple color emoji, segoe ui emoji, segoe ui symbol, noto color emoji, "
        "sfmono-regular, menlo, monaco, consolas, liberation mono, courier new, courier"
    ).split(",")
}

# Georgia and Times New Roman are deliberately NOT above. _familie only ever returns the
# FIRST family in a stack, so those names are reached only when the site actually chose
# them -- a page set in Georgia really is `redactioneel`. Arial and Helvetica are in the set
# because Arial-first is what a default looks like, not what a decision looks like.

_FAMILIE_OK = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 \-]{0,39}$")


def _familie(value: str) -> str | None:
    """The first real typeface named in a font-family value.

    The only free text that reaches the model, so it is whitelisted rather than escaped: a
    name that is not plainly a typeface name is dropped instead of cleaned up.
    """
    for part in value.split(","):
        naam = part.strip().strip("\"'").replace("+", " ")
        naam = re.sub(r"\s+", " ", naam)
        # Next.js and friends emit a metric-matched "<Family> Fallback" face next to every
        # real one, purely to stop layout shift. It is never a typeface anybody chose.
        if naam.lower().endswith(" fallback"):
            continue
        if not naam or naam.lower() in _GENERIEK or naam.startswith("var("):
            continue
        if _FAMILIE_OK.match(naam):
            return naam
    return None


# The suffix on the hero/display alternation is required, not optional: a bare `display`
# matches half the utility classes in a Tailwind build and would drag every one of their
# font sizes into the H1 sample.
_KOP1 = re.compile(r"(^|[\s,>+~])h1\b|\b(hero|display)[-_](title|heading|kop)\b", re.I)
_KOP2 = re.compile(r"(^|[\s,>+~])h2\b", re.I)
_KOPPEN = re.compile(r"(^|[\s,>+~])h[1-3]\b", re.I)
_TEKST = re.compile(r"(^|[\s,>+~])(html|body|p)\b|:root", re.I)
# The page's own ground, which sets the palet. Narrower than _TEKST on purpose: a tinted
# paragraph is not the colour of the paper.
_PAGINA = re.compile(r"(^|[\s,>+~])(html|body)\b|:root", re.I)
_BEELD = re.compile(r"\b(img|figure|picture|image|photo|foto)\b", re.I)
_VOL_BEELD = re.compile(r"100vw|calc\(\s*50%\s*-\s*50vw\s*\)|100dvw")


def measure(url: str) -> dict:
    """Everything measurable about one reference site's skin. Numbers, colours, typefaces."""
    css, ratios, google = gather_css(url)
    if not css.strip():
        raise StyleError(
            f"{url} leverde geen CSS op (mogelijk volledig client-side gerenderd); kies een "
            "andere voorbeeldsite of vul de stijl met de hand in"
        )

    families: Counter[str] = Counter()
    webfonts: set[str] = set()
    kop1: list[float] = []
    kop2: list[float] = []
    tekst: list[float] = []
    alle_groottes: Counter[float] = Counter()
    kop_gewicht: Counter[int] = Counter()
    tracking: list[float] = []
    radii: list[float] = []
    pillen = 0
    padding: list[float] = []
    achtergronden: Counter[str] = Counter()
    pagina_bg: str | None = None
    beeld_radius: list[float] = []
    vol_beeld = len(_VOL_BEELD.findall(css))

    for selector, body in _iter_rules(_COMMENT_RE.sub(" ", css)):
        is_font_face = selector == "@font-face"
        is_kop = bool(_KOPPEN.search(selector))
        for prop, value in _decls(body):
            if prop == "font-family":
                naam = _familie(value)
                if not naam:
                    continue
                # Inside @font-face the name is a declaration of what the site ships; in an
                # ordinary rule it is a use, and uses are what say which face carries the page.
                if is_font_face:
                    webfonts.add(naam)
                else:
                    families[naam] += 1
            elif prop == "font-size" and not is_font_face:
                size = _px(value)
                if size and 8 <= size <= 200:
                    # Every size, whatever the selector. A hand-written stylesheet names h1
                    # and body and the three fields below fill up; a compiled one (Next,
                    # Tailwind, CSS modules) names .styles_heading__x7f2 and they all stay
                    # empty. The histogram is the only type-scale signal that survives both,
                    # and it is readable: the size with the highest count is the body text,
                    # the top of the range is the display size.
                    alle_groottes[round(size * 2) / 2] += 1
                    if _KOP1.search(selector):
                        kop1.append(size)
                    elif _KOP2.search(selector):
                        kop2.append(size)
                    elif _TEKST.search(selector):
                        tekst.append(size)
            elif prop == "font-weight" and is_kop:
                if value.strip().isdigit():
                    kop_gewicht[int(value.strip())] += 1
                elif value.strip().lower() == "bold":
                    kop_gewicht[700] += 1
            elif prop == "letter-spacing" and is_kop:
                em = _em(value)
                if em is not None and -0.2 < em < 0.5:
                    tracking.append(em)
            elif prop.startswith("border") and prop.endswith("radius"):
                first = _first(value)
                if "%" in first or (_px(first) or 0) > 100:
                    pillen += 1
                    continue
                r = _px(first)
                if r is not None and 0 <= r <= 100:
                    radii.append(r)
                    if _BEELD.search(selector):
                        beeld_radius.append(r)
            elif prop in ("padding", "padding-top", "padding-bottom", "padding-block"):
                # Vertical only: the first component is the top edge in every shorthand form,
                # and the rhythm axis is about air above and below a section, not beside it.
                p = _px(_first(value))
                if p is not None and 32 <= p <= 300:
                    padding.append(p)
            elif prop in ("background", "background-color"):
                colour = _colour(value)
                if colour:
                    achtergronden[colour] += 1
                    if pagina_bg is None and _PAGINA.search(selector):
                        pagina_bg = colour
            elif prop == "aspect-ratio":
                nums = re.findall(r"[\d.]+", value)
                if len(nums) == 2 and float(nums[1]):
                    r = round(float(nums[0]) / float(nums[1]), 2)
                    if 0.1 < r < 10:
                        ratios.append(r)

    for entry in google:
        webfonts.add(entry["familie"])

    def _stat(values: list[float]) -> dict | None:
        if not values:
            return None
        return {
            "mediaan": round(statistics.median(values), 1),
            "max": round(max(values), 1),
            "metingen": len(values),
        }

    return {
        "bron": url,
        "lettertypes": [{"naam": n, "voorkomen": c} for n, c in families.most_common(6)],
        "webfonts": sorted(webfonts)[:8],
        "google_fonts": google[:6],
        "kop1_px": _stat(kop1),
        "kop2_px": _stat(kop2),
        "tekst_px": _stat(tekst),
        # Sorted big to small rather than by count: read as a type scale, which is what it is.
        "tekstgroottes_px": sorted(
            ({"px": px, "voorkomen": n} for px, n in alle_groottes.most_common(10)),
            key=lambda s: -s["px"],
        ),
        "kop_gewicht": [g for g, _ in kop_gewicht.most_common(3)],
        "kop_letterafstand_em": round(statistics.median(tracking), 3) if tracking else None,
        "radius_px": _stat(radii),
        "pil_vormen": pillen,
        "sectie_padding_px": _stat(padding),
        "pagina_achtergrond": hsl(pagina_bg) if pagina_bg else None,
        "achtergrondkleuren": [{**hsl(c), "voorkomen": n} for c, n in achtergronden.most_common(8)],
        "beeld_radius_px": _stat(beeld_radius),
        "beeldverhoudingen": [
            {"verhouding": r, "voorkomen": n} for r, n in Counter(ratios).most_common(5)
        ],
        "volle_breedte_beeld": vol_beeld,
    }


def measure_all(urls: list[str]) -> list[dict]:
    """Measure every reference, refusing only when none of them could be read."""
    facts, fouten = [], []
    for url in urls:
        try:
            facts.append(measure(url))
        except StyleError as err:
            fouten.append(str(err))
    if not facts:
        raise StyleError("; ".join(fouten) or "geen voorbeeldsites opgegeven")
    for fout in fouten:
        print(f"overgeslagen: {fout}", file=sys.stderr)
    return facts


# --- mapping ------------------------------------------------------------------------------


def schema(axes: dict[str, list[str]] | None = None) -> dict:
    """Structured-output schema: one enum per axis, plus one Dutch line of reasoning each.

    Every value is an `enum` drawn from stijl.ts, so the model cannot invent a look the
    resolver has no tokens for; `additionalProperties: false` is required on each object.

    The enums are narrowed rather than described. A withdrawn `groot` or a two-value
    shortlist could have been a sentence in the system prompt, and then the run that ignored
    it would produce a five-line headline on a live proposal. Removing the value means the
    model cannot return it at all, which is the same reason the vocabulary is closed.
    """
    axes = axes or vocabulaire()
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            **{axis: {"type": "string", "enum": values} for axis, values in axes.items()},
            "redenen": {
                "type": "object",
                "additionalProperties": False,
                "properties": {axis: {"type": "string"} for axis in axes},
                "required": list(axes),
            },
        },
        "required": [*axes, "redenen"],
    }


# Appended to both prompts. The schema already makes it impossible to return `groot` for a
# long name; this exists so the model does not spend its reasoning wanting a value that is
# not there, and does not write a `reden` explaining a scale it was never offered.
_LANGE_NAAM = (
    "\n\nDe bedrijfsnaam staat voluit in de H1, in een halve kolom. Is die naam lang, dan "
    f"is de schaal `groot` niet beschikbaar (vanaf {NAAM_MAX_GROOT} tekens): de kop zet dan "
    "vijf regels en duwt de belknop van het eerste scherm. Staat een waarde niet in de "
    "aangeboden lijst, dan bestaat hij voor deze site niet -- noem hem dan ook niet."
)

_SYSTEM = (
    "Je vertaalt gemeten ontwerpkenmerken van een voorbeeldwebsite naar een vaste "
    "ontwerptaal voor vakbedrijf-websites (loodgieter, dakdekker, installateur, "
    "elektricien). Je kiest per as een van de toegestane waarden. Meer niet.\n\n"
    "Wat je krijgt zijn metingen: lettertypenamen, groottes in pixels, gewichten, "
    "letterafstand, hoekrondingen, sectie-witruimte, kleuren met tint/verzadiging/lichtheid "
    "en beeldverhoudingen. Geen tekst van de voorbeeldsite, en die heb je ook niet nodig.\n\n"
    "Harde regels:\n"
    "1. Kies ALLEEN uit de toegestane waarden per as. Je schrijft nooit CSS, geen hex-"
    "waarden, geen pixelmaten: de gekozen naam bepaalt die al.\n"
    "2. Baseer elke keuze op de metingen. Zegt de meting niets over een as, kies dan de "
    "neutrale middenwaarde en schrijf dat op.\n"
    "3. Bij meerdere voorbeeldsites: kies wat ze delen. Verschillen ze op een as, volg dan "
    "de eerste site.\n"
    "4. De as `letterontwerp` gaat over het KARAKTER van de letter, niet over de naam: een "
    "brede, stevige grotesk is `industrieel`, een gewone humanistische grotesk is "
    "`grotesk`, een schreefletter voor koppen is `redactioneel`. Meet de voorbeeldsite "
    "alleen system-ui of Arial (dus geen echte webfont), dan is het `systeem`.\n"
    "5. De as `schaal` volgt de VERHOUDING tussen kop en broodtekst, niet de kopgrootte "
    "alleen: een kop van 48px op 16px tekst is iets anders dan 48px op 21px. Staan "
    "`kop1_px` of `tekst_px` op null (dat gebeurt bij sites met samengestelde klassenamen), "
    "lees de verhouding dan uit `tekstgroottes_px`: de grootte met het hoogste `voorkomen` "
    "is de broodtekst, de bovenkant van de reeks is de kop. Let ook op `metingen`: een "
    "waarde uit twee metingen weegt minder dan een uit twintig.\n"
    "6. De as `kleuring` gaat over hoeveel merkkleur de pagina draagt: vlakken met "
    "verzadigde achtergronden zijn `royaal`, een pagina van wit en grijs met alleen "
    "gekleurde knoppen is `spaarzaam`.\n"
    "7. `redenen`: per as een zin in het Nederlands die de meting noemt waarop je de keuze "
    "baseert ('kop 56px op 18px tekst'). Geen marketingtaal, geen uitroeptekens."
) + _LANGE_NAAM

# The composing path. Same job, but the evidence is what a prospect always has instead of
# what a reference site measures: the trade, the name and the brand colours.
_COMPONEER_SYSTEM = (
    "Je stelt het uiterlijk samen van een website voor een Nederlands vakbedrijf "
    "(loodgieter, dakdekker, installateur, elektricien). Er is geen voorbeeldsite: je "
    "componeert de look zelf, uit het vak, de bedrijfsnaam en de eigen merkkleuren.\n\n"
    "Je krijgt per as een lijst met aangeboden waarden. Die lijst is al ingeperkt voor deze "
    "klant. Je kiest daaruit, en je onderbouwt elke keuze met een gegeven dat je hebt.\n\n"
    "Harde regels:\n"
    "1. Kies ALLEEN uit de aangeboden waarden per as. Je schrijft nooit CSS, geen hex-"
    "waarden, geen pixelmaten: de gekozen naam bepaalt die al.\n"
    "2. Kies niet de behoudende optie omdat hij behoudend is. Deze site wordt ongevraagd "
    "naar een ondernemer gestuurd, naast die van zijn concurrent. Een pagina die eruitziet "
    "als een sjabloon kost meer dan een pagina die een richting kiest.\n"
    "3. `palet` moet de merkkleur dragen, niet tegenwerken. Kijk naar de tint: een warme "
    "merkkleur (tint ruwweg 15-60) op koelgrijs papier vloekt, een koele merkkleur (tint "
    "ruwweg 180-260) op zandkleurig papier ook. `neutraal` is de uitweg als de merkkleur "
    "nauwelijks verzadigd is.\n"
    "4. `kleuring` volgt hoe verzadigd en hoe donker de merkkleur is: een ingehouden donkere "
    "kleur draagt `royaal` gekleurde vlakken, een felle verzadigde kleur wordt daarmee "
    "schreeuwerig en hoort bij `spaarzaam`.\n"
    "5. `letterontwerp` gaat over het karakter van de letter, niet over de naam: "
    "`industrieel` is breed en stevig en past bij zwaar bouw- en dakwerk, `grotesk` is "
    "neutraal en zakelijk, `redactioneel` zet een schreefletter in de koppen en leest als "
    "een bedrijf dat zijn werk als vak presenteert.\n"
    "6. `ritme` en `foto`: veel witruimte en beeld dat tot de rand doorloopt is wat een "
    "vakbedrijf onderscheidt van een brochure. Weeg dat tegen het vak -- spoedwerk wil de "
    "informatie dichter op elkaar dan renovatiewerk.\n"
    "7. `redenen`: per as een zin in het Nederlands die het gegeven noemt waarop je de "
    "keuze baseert ('merkkleur tint 212 en 51% verzadiging, dus koel papier'). Geen "
    "marketingtaal, geen uitroeptekens."
) + _LANGE_NAAM


def _axes_block(axes: dict[str, list[str]]) -> str:
    return "Aangeboden waarden per as:\n" + json.dumps(axes, ensure_ascii=False, indent=2)


def _user_message(facts: list[dict], vak: str | None, axes: dict[str, list[str]]) -> str:
    blocks = []
    if vak:
        blocks.append(f"Het vakbedrijf waarvoor de site gebouwd wordt: {vak}.")
    blocks.append(f"Gemeten kenmerken van {len(facts)} voorbeeldsite(s):")
    blocks.append(json.dumps(facts, ensure_ascii=False, indent=2))
    blocks.append(_axes_block(axes))
    blocks.append("\nKies per as een waarde en licht elke keuze toe met de meting erachter.")
    return "\n".join(blocks)


def _componeer_message(vak: str, naam: str, kleuren: dict, axes: dict[str, list[str]]) -> str:
    blocks = [
        f"Vak: {vak}.",
        f"Bedrijfsnaam: {naam} ({len(naam.strip())} tekens). Die naam staat voluit in de H1.",
    ]
    if kleuren:
        blocks.append("Merkkleuren:\n" + json.dumps(kleuren, ensure_ascii=False, indent=2))
    else:
        blocks.append("Merkkleuren: niet opgegeven. Componeer dan uit het vak alleen.")
    blocks.append(_axes_block(axes))
    blocks.append("\nKies per as een waarde en licht elke keuze toe met het gegeven erachter.")
    return "\n".join(blocks)


def _choose(system: str, message: str, axes: dict[str, list[str]]) -> dict:
    """The one Claude call, shared by both paths: offered values in, chosen values out."""
    settings.env("ANTHROPIC_API_KEY")
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=_MODEL["id"],
        max_tokens=8000,
        output_config={
            "effort": _MODEL["effort"],
            "format": {"type": "json_schema", "schema": schema(axes)},
        },
        system=system,
        messages=[{"role": "user", "content": message}],
    )
    if response.stop_reason == "refusal":
        raise StyleError("Claude weigerde deze aanvraag; vul de stijl met de hand in.")
    text = next((b.text for b in response.content if b.type == "text"), "")
    return check_stijl(json.loads(text), axes)


def map_to_stijl(facts: list[dict], vak: str | None = None, naam: str | None = None) -> dict:
    """Measurements in, named vocabulary values out. The whole vocabulary is on offer here:
    the reference decides the look, and narrowing it further would be us overruling the site
    the founder pointed at. The one exception is the client's own name (see `allowed`)."""
    axes = allowed(naam)
    return _choose(_SYSTEM, _user_message(facts, vak, axes), axes)


def compose_stijl(
    vak: str, naam: str, kleur_primair: str | None = None, kleur_accent: str | None = None
) -> dict:
    """No reference: compose a look from the vak, the name and the client's own colours.

    Colours travel as hue/saturation/lightness as well as hex, for the same reason the
    reference path converts them: whether a brand colour wants warm or cool paper is a
    question about its hue, and the model should not be asked to do that arithmetic in
    its head.
    """
    kleuren = {}
    if kleur_primair:
        kleuren["primair"] = hsl(_check_hex(kleur_primair))
    if kleur_accent:
        kleuren["accent"] = hsl(_check_hex(kleur_accent))
    axes = candidates(naam)
    return _choose(_COMPONEER_SYSTEM, _componeer_message(vak, naam, kleuren, axes), axes)


def check_stijl(raw: dict, axes: dict[str, list[str]] | None = None) -> dict:
    """Second gate on the model's answer, in case the schema ever stops being enforced."""
    axes = axes or vocabulaire()
    for axis, values in axes.items():
        if raw.get(axis) not in values:
            raise StyleError(f"as `{axis}` kwam terug als {raw.get(axis)!r}, niet uit {values}")
    return raw


# --- output -------------------------------------------------------------------------------


def as_yaml(stijl: dict) -> str:
    """The `stijl:` block, with each choice's reason as the comment above it.

    Written by hand rather than through yaml.dump because the comments are the point: the
    founder reads this block to decide whether the analyser understood the reference, and a
    bare list of seven words does not let him.
    """
    redenen = stijl.get("redenen", {})
    lines = ["stijl:"]
    for axis in vocabulaire():
        # Collapsed first so a reason containing a newline cannot break out of the comment
        # and produce a client.yaml that does not parse; wrapped second because these run to
        # 180 characters and the founder reads them in an editor, not through `less -S`.
        reden = " ".join(str(redenen.get(axis, "")).split())
        lines.extend(f"  # {line}" for line in textwrap.wrap(reden, width=92))
        lines.append(f"  {axis}: {stijl[axis]}")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="app.sitestyle",
        description="Pick a client-sites skin: from reference websites, or composed when "
        "there are none.",
    )
    parser.add_argument(
        "--voorbeeld",
        action="append",
        default=[],
        metavar="URL",
        help="Reference site whose look the client likes. Repeatable.",
    )
    parser.add_argument("--vak", help="The client's trade, as context for the mapping.")
    parser.add_argument(
        "--naam",
        help="The client's company name. Withdraws `groot` when it is long, and seeds the "
        "shortlists when there is no reference to measure.",
    )
    parser.add_argument(
        "--kleur", help="Brand colour (#rrggbb), for composing without a reference."
    )
    parser.add_argument("--accent", help="Accent colour (#rrggbb), same.")
    parser.add_argument(
        "--feiten",
        action="store_true",
        help="Print what the model would be given as JSON and stop (no API call).",
    )
    args = parser.parse_args(argv[1:])

    try:
        if args.voorbeeld:
            facts = measure_all(args.voorbeeld)
            if args.feiten:
                print(json.dumps(facts, ensure_ascii=False, indent=2))
                return 0
            stijl = map_to_stijl(facts, args.vak, args.naam)
        else:
            if not (args.vak and args.naam):
                raise StyleError(
                    "zonder --voorbeeld componeert de fabriek de stijl zelf, en daarvoor zijn "
                    "--vak en --naam nodig (--kleur en --accent maken hem beter)"
                )
            if args.feiten:
                # The composing path has no measurements, so --feiten prints its inputs
                # instead: the shortlists this client's name produced. Same promise as on the
                # reference path -- see what the call will be judged on without paying for it.
                print(
                    json.dumps(
                        {
                            "vak": args.vak,
                            "naam": args.naam,
                            "naam_tekens": len(args.naam.strip()),
                            "kleuren": {
                                sleutel: hsl(_check_hex(kleur))
                                for sleutel, kleur in (
                                    ("primair", args.kleur),
                                    ("accent", args.accent),
                                )
                                if kleur
                            },
                            "kandidaten": candidates(args.naam),
                        },
                        ensure_ascii=False,
                        indent=2,
                    )
                )
                return 0
            stijl = compose_stijl(args.vak, args.naam, args.kleur, args.accent)
    except StyleError as err:
        print(f"❌ {err}", file=sys.stderr)
        return 1

    print(as_yaml(stijl))
    # Flushed before the note: stdout is block-buffered when piped into a file and stderr is
    # not, so without this the instructions land above the block they are about.
    sys.stdout.flush()
    print("\nPlak dit blok in clients/<slug>/client.yaml en bouw met:", file=sys.stderr)
    print("  cd klantkraan/apps/client-sites && CLIENT=<slug> pnpm build", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
