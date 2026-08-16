"""Search, pin and render the per-vak stock photo sets.

Client sites show the client's own work photos (clients/<slug>/fotos/). When a client
has not supplied any -- and always on a voorstel, where we do not take a prospect's
images -- the photo band falls back to a stock set for their vak. Only the client's own
vak is copied into dist/ (see the clientStock integration in astro.config.mjs), so a
dakdekker's site never ships a loodgieter's photos.

Two phases, because the hard part is choosing, not fetching:

    # 1. gather candidates for a vak we have no set for, and build a contact sheet
    growth-engine/.venv/bin/python .../stock-photos.py zoek kapper \
        --query "kapper schaar" --query "barbershop stoel" --query "kappersalon interieur"

    # 2. having LOOKED at stock/kandidaten/kapper/contactblad.webp, pin seven photos in
    #    stock/sets/kapper.json, then render the renditions the pages actually use
    growth-engine/.venv/bin/python .../stock-photos.py render --vak kapper

Phase 2 alone reproduces any committed set: the recipes in stock/sets/*.json pin photo
ids, so a re-run yields the same images. `render` with no --vak re-renders every set.

Pexels licence: free commercial use, no attribution required. `zoek` needs the free
PEXELS_API_KEY (growth-engine/.env); `render` does not -- it reads images by id straight
off the CDN, which is what keeps a rebuild working without credentials.

No brand treatment on purpose. The marketing site duotones its photos to Klantkraan's
palette (see apps/marketing-site/scripts/site-photos.py); a client site carries the
CLIENT's colours, so a Klantkraan-tinted photo would fight the branding on every page.

THE PICKING RULE, which `zoek` cannot apply for you and which is the whole reason the
contact sheet exists:

  - No recognisable faces. A stock person implying they work for a named client is a
    model-release problem, not a style preference.
  - Northern European subject matter. The plain "roofer" queries return Mediterranean
    barrel tile and US asphalt shingle almost exclusively, which is why the dakdekker set
    came from gutters, scaffolding and brick facades instead. Every new vak needs that
    same pass -- read the query notes in the recipe you are copying.
  - The hero shows a person DOING the work rather than a finished object: a trade site
    sells the crew, and a photo with a human in it is the one thing a stock strip cannot
    fake.
  - Vary the distance. Five close-ups and no establishing shot is its own monotony.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

APP = Path(__file__).resolve().parent.parent
OUT = APP / "stock"
SETS = OUT / "sets"
KANDIDATEN = OUT / "kandidaten"
UA = "klantkraan-site-photos/1.0"  # Pexels 403s urllib's default UA

# One rendition per role, cropped here rather than in CSS: a file whose pixels match the
# box it is drawn in keeps the <img> width/height honest (no layout shift), ships no
# pixels the page throws away, and lands well under the 200 KB that squirrelscan flags.
#
# Two ratios on the page, never square. Surveying twelve award-level construction and trade sites
# (Koto, Harold Leidner, Hobbs, Land Morphology, Strom, Keystone, Norm, Hutker et al.)
# turned up not one square content photo -- squares appear only at icon and news-thumb
# size. A grid of equal squares is the single loudest "template" signal there is, and it
# is what this set used to be. So the work section runs the pattern Koto uses: six
# photos, only a 2:3 portrait and a 3:2 landscape between them, with the landscape slots
# sitting at different positions per vak. Because a landscape cell is barely half the
# height of a portrait one, the columns never level off and the seam stays ragged.
#
# Crops follow the subject, which is the other half of it: a roof, a facade or a spread
# of tools is horizontal, a gable, a standpipe or a running tap is vertical.
#
# WebP, not JPEG: at 1500x1000 this hero costs ~200 KB as WebP against ~310 KB as JPEG,
# the difference between fitting the 200 KB squirrelscan budget and blowing it by half.
# Quality is per role because a detail-heavy hero (brick, scaffolding) compresses far
# worse than a studio close-up.
#
# Keep in sync with SHAPES in src/lib/client.ts, which turns these suffixes back into the
# width/height attributes the pages render.
#
# role -> (suffix, full size, -sm size or None, quality)
RENDITIONS: dict[str, tuple[str, tuple[int, int], tuple[int, int] | None, int]] = {
    # Beside the hero copy, bleeding off the page edge. 3:2 is the source ratio, so this
    # is the one crop that throws nothing away, and it matches the box the split hero
    # actually draws (a 16:9 would be cropped again by the layout).
    "hero": ("hero", (1500, 1000), (750, 500), 72),
    # The share card. Cut separately at 1200x630 rather than reusing the hero, because
    # every platform crops to roughly 1.91:1 and a 3:2 hero loses its top and bottom to
    # that crop. No -sm: nothing ever renders this on a page.
    "og": ("og", (1200, 630), None, 80),
    # Work-section tiles, drawn ~357px wide in the three-column desktop grid and ~342px
    # in the single-column phone layout, so these carry roughly 2x for retina and no more.
    # Wide was 1200px until an aerial of a hundred roof tiles came in at 291 KB: at a
    # 357px box those pixels were never going to be seen, and the budget is the budget.
    "tall": ("tall", (800, 1200), (400, 600), 78),
    "wide": ("wide", (900, 600), (450, 300), 78),
}

# The six tiles, in recipe order, must be exactly this -- and it is layout, not tidiness.
# The work section is a CSS multi-column, which fills sequentially and cannot reorder to
# balance, so the source order decides the page twice over:
#   - three talls in a row pile 1028px into one column against 536px in another, and the
#     short column reads as a missing photo rather than as rhythm;
#   - but a plain tall/wide alternation balances the columns and then puts every seam at
#     the same height, which is a ladder -- the thing the reference sites avoid.
# This sequence fills as [tall, wide] [wide, tall] [tall, wide]: every column ends level
# at 774px while the seams land at 536, 238 and 536. Level bottoms, ragged seams.
# It was a comment for one release and a new set got it wrong, so now it is a check.
TEGELVOLGORDE = ("tall", "wide", "wide", "tall", "tall", "wide")


class SetError(Exception):
    """A recipe that would render a broken or misordered set."""


def _original_url(photo_id: int) -> str:
    return (
        f"https://images.pexels.com/photos/{photo_id}/pexels-photo-{photo_id}.jpeg"
        "?auto=compress&cs=tinysrgb&w=2400"
    )


def _get(url: str, headers: dict[str, str] | None = None, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _fetch(photo_id: int) -> Image.Image:
    from io import BytesIO

    return Image.open(BytesIO(_get(_original_url(photo_id)))).convert("RGB")


# ---------------------------------------------------------------- recipes


def recept(vak: str) -> list[dict]:
    """Read stock/sets/<vak>.json and refuse anything that would render wrong.

    Validated here rather than at render time because every failure below produces a site
    that builds: a missing hero silently drops the hero image, a duplicated index
    overwrites a tile, and a wrong tile order just quietly ladders the work section.
    """
    pad = SETS / f"{vak}.json"
    if not pad.exists():
        raise SetError(
            f"geen recept voor '{vak}': {pad.relative_to(APP)} bestaat niet. "
            f"Draai eerst `stock-photos.py zoek {vak}` en kies zeven fotos."
        )
    doc = json.loads(pad.read_text(encoding="utf-8"))
    fotos = doc.get("fotos") or []
    for i, f in enumerate(fotos, start=1):
        ontbreekt = [k for k in ("id", "rollen", "alt") if not f.get(k)]
        if ontbreekt:
            raise SetError(f"{vak}.json foto {i}: mist {', '.join(ontbreekt)}")
        onbekend = [r for r in f["rollen"] if r not in RENDITIONS]
        if onbekend:
            raise SetError(f"{vak}.json foto {i}: onbekende rol {onbekend!r}")

    heroes = [f for f in fotos if "hero" in f["rollen"]]
    if len(heroes) != 1:
        raise SetError(f"{vak}.json: precies een foto krijgt de hero-rol, niet {len(heroes)}")
    if "og" not in heroes[0]["rollen"]:
        raise SetError(f"{vak}.json: de hero-foto draagt ook de og-rol (de deelkaart)")
    # The hero takes no tile: seeing the same frame twice on one page is the thing that
    # gives a stock set away.
    if {"tall", "wide"} & set(heroes[0]["rollen"]):
        raise SetError(f"{vak}.json: de hero-foto krijgt geen tegel, anders staat hij er twee keer")

    tegels = tuple(r for f in fotos for r in f["rollen"] if r in ("tall", "wide"))
    if tegels != TEGELVOLGORDE:
        raise SetError(
            f"{vak}.json: de tegelvolgorde is {list(tegels)} maar moet "
            f"{list(TEGELVOLGORDE)} zijn -- de multi-column vult op volgorde, dus deze "
            "lijst is de opmaak. Zie TEGELVOLGORDE."
        )
    return fotos


def render(vak: str) -> int:
    """Cut every rendition the pages ask for, plus the alt.json that describes them."""
    fotos = recept(vak)
    dest = OUT / vak
    dest.mkdir(parents=True, exist_ok=True)
    # filename -> alt, written next to the images so the descriptions travel with the
    # set they describe and src/lib/client.ts has one place to read them from. The
    # alternative -- a second copy of this text in TypeScript -- is a copy that drifts.
    alts: dict[str, str] = {}
    written = 0
    for i, foto in enumerate(fotos, start=1):
        img = _fetch(foto["id"])
        for rol in foto["rollen"]:
            suffix, size, size_sm, quality = RENDITIONS[rol]
            # The hero is named for its role -- the page asks for "the hero", never
            # "photo 2" -- while a tile keeps its index and carries its shape as a
            # suffix, which is how the loader reads the ratio back off the filename.
            stem = f"{vak}-{suffix}" if rol in ("hero", "og") else f"{vak}-{i}-{suffix}"
            boxes = [(stem, size)] + ([(f"{stem}-sm", size_sm)] if size_sm else [])
            for name, box in boxes:
                ImageOps.fit(img, box, Image.LANCZOS).save(
                    dest / f"{name}.webp", quality=quality, method=6
                )
                written += 1
            # The og card is never rendered in page markup, so it needs no alt.
            if rol != "og":
                alts[f"{stem}.webp"] = foto["alt"]
            print(f"{stem}.webp  <- pexels {foto['id']} ({foto.get('fotograaf', '?')}) [{rol}]")
    (dest / "alt.json").write_text(
        json.dumps(alts, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return written + 1


# ---------------------------------------------------------------- search


def _key() -> str:
    """The free Pexels key, from the environment or growth-engine/.env."""
    key = os.getenv("PEXELS_API_KEY", "").strip()
    if key:
        return key
    env = APP.parents[2] / "growth-engine" / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.startswith("PEXELS_API_KEY="):
                return line.split("=", 1)[1].strip()
    raise SetError(
        "geen PEXELS_API_KEY. Gratis sleutel via https://www.pexels.com/api/ , "
        "zet hem in growth-engine/.env"
    )


def _search(query: str, orientation: str, per_page: int, key: str) -> list[dict]:
    # locale=nl-NL makes Pexels return Dutch alt text and nudges results Dutchward, which
    # is the same bias the picking rule asks for by hand.
    params = urllib.parse.urlencode(
        {
            "query": query,
            "orientation": orientation,
            "per_page": per_page,
            "locale": "nl-NL",
        }
    )
    body = _get(
        f"https://api.pexels.com/v1/search?{params}", {"Authorization": key}, timeout=20
    )
    return json.loads(body).get("photos") or []


def _label(cell: Image.Image, n: int) -> None:
    """Burn the candidate number into the tile, so a pick cannot be an off-by-one."""
    draw = ImageDraw.Draw(cell)
    try:
        font = ImageFont.load_default(size=34)
    except TypeError:  # Pillow < 10.1: fixed-size bitmap font, still legible
        font = ImageFont.load_default()
    draw.rectangle((0, 0, 54, 46), fill=(17, 17, 17))
    draw.text((12, 4), f"{n:02d}", fill=(255, 255, 255), font=font)


def zoek(vak: str, queries: list[str], per_query: int) -> int:
    """Gather candidates for a vak and lay them out as one numbered contact sheet.

    Landscape AND portrait, because the source ratio decides how much a crop throws away:
    a portrait frame fills the 2:3 tall tile with nothing lost, where a landscape one has
    to give up its sides. `ratio` in the index says which is which.
    """
    key = _key()
    dest = KANDIDATEN / vak
    dest.mkdir(parents=True, exist_ok=True)
    from io import BytesIO

    gezien: set[int] = set()
    kandidaten: list[dict] = []
    for query in queries:
        for orientation in ("landscape", "portrait"):
            try:
                treffers = _search(query, orientation, per_query, key)
            except Exception as exc:
                print(f"zoek {query!r} ({orientation}) mislukt: {exc}", file=sys.stderr)
                continue
            for photo in treffers:
                if photo["id"] in gezien:
                    continue
                gezien.add(photo["id"])
                kandidaten.append(
                    {
                        "n": len(kandidaten) + 1,
                        "id": photo["id"],
                        "fotograaf": photo.get("photographer", ""),
                        # Pexels' own description, recorded for reference only. The alt we
                        # ship is written by hand: this one is auto-generated and regularly
                        # names things that are not in the frame.
                        "pexels_alt": photo.get("alt", ""),
                        "ratio": "liggend" if photo["width"] >= photo["height"] else "staand",
                        "query": query,
                        "url": photo.get("url", ""),
                    }
                )

    if not kandidaten:
        raise SetError(f"geen enkele treffer voor {queries!r} -- probeer andere zoektermen")

    # Grid of 4. The sheet is for triage (framing, faces, is this the right continent);
    # the per-candidate files next to it are for the closer look that decides a pick.
    CEL, KOL, PAD = (330, 248), 4, 8
    rijen = -(-len(kandidaten) // KOL)
    blad = Image.new(
        "RGB",
        (KOL * CEL[0] + (KOL + 1) * PAD, rijen * CEL[1] + (rijen + 1) * PAD),
        (245, 244, 242),
    )
    for k in kandidaten:
        raw = _get(
            f"https://images.pexels.com/photos/{k['id']}/pexels-photo-{k['id']}.jpeg"
            "?auto=compress&cs=tinysrgb&w=940"
        )
        img = Image.open(BytesIO(raw)).convert("RGB")
        img.save(dest / f"{k['n']:02d}.webp", quality=80, method=4)
        cel = ImageOps.fit(img, CEL, Image.LANCZOS)
        _label(cel, k["n"])
        i = k["n"] - 1
        blad.paste(
            cel,
            (PAD + (i % KOL) * (CEL[0] + PAD), PAD + (i // KOL) * (CEL[1] + PAD)),
        )
        print(f"{k['n']:02d}  pexels {k['id']}  {k['ratio']:8s} {k['query']!r}")

    blad.save(dest / "contactblad.webp", quality=82, method=4)
    (dest / "kandidaten.json").write_text(
        json.dumps({"vak": vak, "queries": queries, "kandidaten": kandidaten},
                   ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"\n{len(kandidaten)} kandidaten in {dest.relative_to(APP)}")
    print(f"BEKIJK {(dest / 'contactblad.webp').relative_to(APP)} en pas de keuzeregel toe.")
    print(f"Pin daarna zeven fotos in {(SETS / f'{vak}.json').relative_to(APP)}.")
    return 0


# ---------------------------------------------------------------- cli


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="stock-photos.py",
        description="Zoek, pin en render de stock-fotosets per vak.",
    )
    sub = parser.add_subparsers(dest="verb")

    p_zoek = sub.add_parser("zoek", help="kandidaten ophalen en een contactblad bouwen")
    p_zoek.add_argument("vak")
    p_zoek.add_argument(
        "--query",
        action="append",
        default=[],
        metavar="TERM",
        help="Zoekterm, herhaalbaar. Zonder dit wordt het vak zelf gezocht, wat zelden "
        "de beste set oplevert -- lees de keuzeregel bovenaan dit bestand.",
    )
    p_zoek.add_argument("--per-query", type=int, default=4, help="treffers per term per orientatie")

    p_render = sub.add_parser("render", help="renditions snijden uit de gepinde recepten")
    p_render.add_argument("--vak", help="een vak, of alle recepten wanneer weggelaten")

    args = parser.parse_args(argv[1:] or ["render"])

    try:
        if args.verb == "zoek":
            return zoek(args.vak, args.query or [args.vak], args.per_query)
        vakken = [args.vak] if args.vak else sorted(p.stem for p in SETS.glob("*.json"))
        if not vakken:
            raise SetError(f"geen recepten in {SETS.relative_to(APP)}")
        written = sum(render(vak) for vak in vakken)
        print(f"\nwrote {written} files to {OUT}")
    except SetError as err:
        print(f"❌ {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
