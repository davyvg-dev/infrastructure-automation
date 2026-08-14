"""Fetch the per-vak stock photo sets from Pexels.

Client sites show the client's own work photos (clients/<slug>/fotos/). When a client
has not supplied any -- and always on a voorstel, where we do not take a prospect's
images -- the photo band falls back to a stock set for their vak. Only the client's own
vak is copied into dist/ (see the clientStock integration in astro.config.mjs), so a
dakdekker's site never ships a loodgieter's photos.

Pinned photo ids keep every run reproducible; outputs land in stock/<vak>/ and are
committed, so this only needs to run again when a vak is added or a photo replaced.
Pexels license: free commercial use, no attribution required.

    growth-engine/.venv/bin/python klantkraan/apps/client-sites/scripts/stock-photos.py

No brand treatment on purpose. The marketing site duotones its photos to Klantkraan's
palette (see apps/marketing-site/scripts/site-photos.py); a client site carries the
CLIENT's colours, so a Klantkraan-tinted photo would fight the branding on every page.

Picking rule, applied by eye from search sheets (2026-08-14): no recognisable faces
(a stock person implying they work for a named client is a model-release problem), and
Northern European subject matter. The plain "roofer" queries return Mediterranean barrel
tile and US asphalt shingle almost exclusively, so the dakdekker set came from querying
gutters, scaffolding and brick facades instead. Every new vak needs that same pass.
"""

from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

from PIL import Image, ImageOps

# vak -> [(pexels id, photographer, roles, alt)], picked by eye from search sheets
# 2026-08-14.
#
# `roles` is the art direction: which crops this photo is cut to, and nothing more. Each
# vak spends one photo on the hero and gives the other six a tall or a wide tile, so a
# photo only gets the renditions its roles need and adding a ratio does not multiply the
# whole committed set. The hero photo takes no tile: seeing the same frame twice on one
# page is the thing that gives a stock set away.
#
# Six tiles, three tall and three wide, in the order TALL WIDE WIDE TALL TALL WIDE -- and
# that exact sequence is load-bearing, not tidiness. The work section is a CSS
# multi-column, which fills sequentially and cannot reorder to balance, so the source
# order decides the layout twice over:
#   - three talls in a row pile 1028px into one column against 536px in another, and the
#     short column reads as a missing photo rather than as rhythm;
#   - but a plain tall/wide alternation balances the columns and then puts every seam at
#     the same height, which is a ladder -- the thing the reference sites avoid.
# This sequence fills as [tall, wide] [wide, tall] [tall, wide]: every column ends level
# at 774px while the seams land at 536, 238 and 536. Level bottoms, ragged seams.
# Reordering this list reorders the page, and re-running is not enough to see it -- check
# the three column heights.
#
# Within that constraint the crop still follows the subject: the aerial, the tool spread
# and the facade are horizontal facts and take the wide slots, the gable, the standpipe
# and the tile courses are vertical ones and take the tall.
#
# Hero picks show a person doing the work rather than a finished object: a trade site
# sells the crew, and a photo with a human in it is the one thing a stock strip cannot
# fake. All remain face-free, per the picking rule above.
#
# `alt` is Dutch, and it describes what is IN the frame -- never who did it. That is the
# whole discipline: "Dakdekker werkt vanuit een hoogwerker" is a true description of a
# photograph, while anything naming the client would make a stock frame testify to work
# they may never have done. Written per photo rather than shared, because five images
# carrying one identical sentence is five identical announcements to a screen reader.
STOCK: dict[str, list[tuple[int, str, tuple[str, ...], str]]] = {
    "dakdekker": [
        # roofer in a cherry picker, red brick building: the only frame with a person
        # actually working, and it is already 3:2, so the hero crop keeps all of it.
        (
            31762405,
            "Gundula Vogel",
            ("hero", "og"),
            "Dakdekker werkt vanuit een hoogwerker aan een pannendak",
        ),
        # brick gable, orange tiles, deep blue sky: the triangle is centred, so it is one
        # of the few landscape frames that survives a 2:3 crop.
        (
            12484142,
            "Jan van der Wolf",
            ("tall",),
            "Puntgevel met oranje dakpannen en een strakke daklijst",
        ),
        (
            31745718,
            "Jef KoeleWijn",
            ("wide",),
            "Steigerwerk langs een dak in aanbouw tegen een blauwe lucht",
        ),
        (6195500, "A.", ("wide",), "Woning met pannendak en dakgoot, herfstboom ernaast"),
        (37165058, "Priyanshi Garg", ("tall",), "Rijen verweerde dakpannen op een hellend dak"),
        (
            4446029,
            "Francesco Ungaro",
            ("tall",),
            "Loodslabben rond dakpannen, van dichtbij gezien",
        ),
        # The set had five close and mid shots and no establishing frame: every photo sat
        # at roughly the same distance, which is its own kind of monotony. An aerial of
        # Dutch terraced roofs is the widest shot available and unmistakably not abroad,
        # which is the failure mode the picking rule was written against.
        (
            14493179,
            "Kelly",
            ("wide",),
            "Rijtjeshuizen van bovenaf met pannendaken en dakkapellen",
        ),
    ],
    "loodgieter": [
        (
            6419128,
            "Anil Karakaya",
            ("tall",),
            "Handen monteren een stalen leiding onder een wastafel",
        ),
        # gloved hands on blue pipe: workwear and a face-free person, the closest this
        # set gets to a crew shot.
        (
            29226620,
            "Sergei Starostin",
            ("hero", "og"),
            "Loodgieter monteert een koppeling op een waterleiding",
        ),
        (5414383, "Roger Brown", ("wide",), "Moersleutels en waterpomptang op een werkblad"),
        (
            5534767,
            "Roger Brown",
            ("wide",),
            "Hand met werkhandschoen en een verstelbare moersleutel",
        ),
        (
            14953886,
            "AS Photography",
            ("tall",),
            "Fittingen en flexibele slangen op een bouwtekening",
        ),
        # chrome tap, running water: the finished result, and the brightest frame of the
        # set, which the tall slot needs next to dark tool close-ups.
        (
            34295401,
            "Zulfugar Karimov",
            ("tall",),
            "Kraan met stromend water boven een rvs spoelbak",
        ),
        # Six frames of hands and tools and no installation: this set could have been any
        # trade. A cv-verdeler is the one object a Dutch homeowner recognises instantly as
        # loodgieterswerk.
        (
            7937299,
            "Erik Mclean",
            ("wide",),
            "Verdeler van een cv-installatie met pomp en leidingen",
        ),
    ],
}

# One rendition per role, cropped here rather than in CSS: a file whose pixels match the
# box it is drawn in keeps the <img> width/height honest (no layout shift), ships no
# pixels the page throws away, and lands well under the 200 KB that squirrelscan flags.
# Every source frame is 3:2 landscape, so "wide" is nearly a straight resize while "tall"
# is a real crop -- which is why only a deliberately chosen photo gets the tall role.
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
OUT = Path(__file__).resolve().parent.parent / "stock"
UA = "klantkraan-site-photos/1.0"  # Pexels 403s urllib's default UA


def _original_url(photo_id: int) -> str:
    return (
        f"https://images.pexels.com/photos/{photo_id}/pexels-photo-{photo_id}.jpeg"
        "?auto=compress&cs=tinysrgb&w=2400"
    )


def _fetch(photo_id: int) -> Image.Image:
    req = urllib.request.Request(_original_url(photo_id), headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read()
    from io import BytesIO

    return Image.open(BytesIO(raw)).convert("RGB")


def main() -> int:
    written = 0
    for vak, photos in STOCK.items():
        dest = OUT / vak
        dest.mkdir(parents=True, exist_ok=True)
        # filename -> alt, written next to the images so the descriptions travel with the
        # set they describe and src/lib/client.ts has one place to read them from. The
        # alternative -- a second copy of this text in TypeScript -- is a copy that drifts.
        alts: dict[str, str] = {}
        for i, (photo_id, photographer, roles, alt) in enumerate(photos, start=1):
            img = _fetch(photo_id)
            for role in roles:
                suffix, size, size_sm, quality = RENDITIONS[role]
                # The hero is named for its role -- the page asks for "the hero", never
                # "photo 2" -- while a tile keeps its index and carries its shape as a
                # suffix, which is how the loader reads the ratio back off the filename.
                stem = f"{vak}-{suffix}" if role in ("hero", "og") else f"{vak}-{i}-{suffix}"
                boxes = [(stem, size)] + ([(f"{stem}-sm", size_sm)] if size_sm else [])
                for name, box in boxes:
                    ImageOps.fit(img, box, Image.LANCZOS).save(
                        dest / f"{name}.webp", quality=quality, method=6
                    )
                    written += 1
                # The og card is never rendered in page markup, so it needs no alt.
                if role != "og":
                    alts[f"{stem}.webp"] = alt
                print(f"{stem}.webp  <- pexels {photo_id} ({photographer}) [{role}]")
        (dest / "alt.json").write_text(
            json.dumps(alts, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        written += 1
    print(f"\nwrote {written} files to {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
