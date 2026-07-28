"""Fetch the site's photos from Pexels and apply the brand treatment.

Pinned photo ids keep every run reproducible; outputs land in public/photos/ and are
committed, so this script only needs to run again when a photo is added or replaced.
Pexels license: free commercial use, no attribution required.

Run from the repo root (Pillow lives in the growth-engine venv):

    export PEXELS_API_KEY=$(grep '^PEXELS_API_KEY=' growth-engine/.env | cut -d= -f2)
    growth-engine/.venv/bin/python klantkraan/apps/marketing-site/scripts/site-photos.py

Treatment = chalk duotone (night #0f1c1e shadows -> chalk #f4efe6 highlights) blended
with 15% of the original color: photos read as one set on the dark design, faces keep
their warmth. Each slug emits {slug}.jpg (1400x900) and {slug}-sm.jpg (700x450).
"""

from __future__ import annotations

import os
import sys
import urllib.request
from pathlib import Path

from PIL import Image, ImageOps

# slug -> Pexels photo id (picked by eye from search sheets, 2026-07-28)
PHOTOS = {
    "home-hero": 6196229,  # tradesperson at the open van, warm evening light
    "loodgieters": 6419128,  # hands tightening a pipe under a sink
    "dakdekkers": 37677394,  # roofer kneeling on a roof, laying tiles
    "installateurs": 32497161,  # technician inspecting an outdoor unit by flashlight
    "elektriciens": 27928762,  # electrician working in a switch panel
    "aannemers": 28196526,  # foreman on site, helmet under his arm
    "schilders": 7218683,  # painter on a ladder rolling a wall
    "sportscholen": 3215519,  # member checking in at the front desk
}

SIZE = (1400, 900)
SIZE_SM = (700, 450)
OUT = Path(__file__).resolve().parent.parent / "public" / "photos"
UA = "klantkraan-site-photos/1.0"  # Pexels 403s urllib's default UA

NIGHT = (15, 28, 30)  # --color-night
MID = (84, 96, 92)  # desaturated between night and dim
CHALK = (244, 239, 230)  # --color-chalk
COLOR_BLEND = 0.15


def _original_url(photo_id: int) -> str:
    # The stable original-file URL scheme; sized variants are derived via query params.
    return (
        f"https://images.pexels.com/photos/{photo_id}/pexels-photo-{photo_id}.jpeg"
        "?auto=compress&cs=tinysrgb&w=2400"
    )


def _fetch(photo_id: int) -> Image.Image:
    req = urllib.request.Request(_original_url(photo_id), headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read()
    tmp = OUT / f".tmp-{photo_id}.jpg"
    tmp.write_bytes(raw)
    img = Image.open(tmp).convert("RGB")
    img.load()
    tmp.unlink()
    return img


def _cover(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    tw, th = size
    scale = max(tw / img.width, th / img.height)
    img = img.resize((round(img.width * scale), round(img.height * scale)))
    left = (img.width - tw) // 2
    top = (img.height - th) // 2
    return img.crop((left, top, left + tw, top + th))


def _lut() -> list[int]:
    stops = [(0, NIGHT), (128, MID), (255, CHALK)]
    luts: list[list[int]] = [[], [], []]
    for lum in range(256):
        for (l0, c0), (l1, c1) in zip(stops, stops[1:]):
            if l0 <= lum <= l1:
                t = (lum - l0) / max(1, l1 - l0)
                for ch in range(3):
                    luts[ch].append(round(c0[ch] + t * (c1[ch] - c0[ch])))
                break
    return luts[0] + luts[1] + luts[2]


def treat(img: Image.Image) -> Image.Image:
    gray = ImageOps.autocontrast(img.convert("L"), cutoff=1)
    duo = Image.merge("RGB", [gray] * 3).point(_lut())
    return Image.blend(duo, img, COLOR_BLEND)


def main() -> int:
    if not os.getenv("PEXELS_API_KEY", "").strip():
        # The image CDN itself needs no key, but keep the guard so a future switch to the
        # search API (new picks) fails loudly rather than silently skipping.
        print("note: PEXELS_API_KEY not set; fetching pinned ids from the CDN only")
    OUT.mkdir(parents=True, exist_ok=True)
    for slug, photo_id in PHOTOS.items():
        img = _fetch(photo_id)
        for size, name in ((SIZE, f"{slug}.jpg"), (SIZE_SM, f"{slug}-sm.jpg")):
            treat(_cover(img, size)).save(OUT / name, quality=80, progressive=True)
        print(f"{slug}: {photo_id} -> photos/{slug}.jpg + -sm")
    return 0


if __name__ == "__main__":
    sys.exit(main())
