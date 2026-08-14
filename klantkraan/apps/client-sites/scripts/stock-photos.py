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

import sys
import urllib.request
from pathlib import Path

from PIL import Image, ImageOps

# vak -> [(pexels id, photographer)], picked by eye from search sheets 2026-08-14
STOCK: dict[str, list[tuple[int, str]]] = {
    "dakdekker": [
        (31762405, "Gundula Vogel"),  # roofer in a cherry picker, red brick building
        (31745718, "Jef KoeleWijn"),  # scaffolding on a roof against blue sky
        (12484142, "Jan van der Wolf"),  # brick gable, orange tiles
        (6195500, "A."),  # brick house with tiled roof, autumn tree
        (4446029, "Francesco Ungaro"),  # tile close-up with lead flashing
        (37165058, "Priyanshi Garg"),  # clay tile texture
    ],
    "loodgieter": [
        (6419128, "Anil Karakaya"),  # hands fitting steel pipe
        (29226620, "Sergei Starostin"),  # gloved hands on blue pipe
        (5534767, "Roger Brown"),  # gloved hand, adjustable wrench
        (5414383, "Roger Brown"),  # wrenches and pliers
        (14953886, "AS Photography"),  # fittings on a blueprint
        (34295401, "Zulfugar Karimov"),  # chrome tap, running water
    ],
}

SIZE = (1200, 800)
SIZE_SM = (600, 400)
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
    for vak, photos in STOCK.items():
        dest = OUT / vak
        dest.mkdir(parents=True, exist_ok=True)
        for i, (photo_id, photographer) in enumerate(photos, start=1):
            img = _fetch(photo_id)
            ImageOps.fit(img, SIZE, Image.LANCZOS).save(
                dest / f"{vak}-{i}.jpg", quality=82, optimize=True
            )
            ImageOps.fit(img, SIZE_SM, Image.LANCZOS).save(
                dest / f"{vak}-{i}-sm.jpg", quality=82, optimize=True
            )
            print(f"{vak}-{i}.jpg  <- pexels {photo_id} ({photographer})")
    print(f"\nwrote {sum(len(v) for v in STOCK.values()) * 2} files to {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
