"""Turn a client's own photographs into the renditions their site renders.

The editing promise this exists for: a client must be able to swap a photo without
breaking anything. Before this script there were three ways they could.

  1. `clients/<slug>/fotos/` was copied into the build verbatim. A 12 MB photo straight
     off an iPhone shipped as a 12 MB photo, on a page whose whole performance budget is
     200 KB an image. Nothing failed; the site just got slow for everyone.
  2. The pages read that directory with `readdir().sort()` and spent `fotos[0]` on the
     hero. Which photograph became the hero was therefore decided by ALPHABETICAL ORDER.
     Adding `afspraak.jpg` silently moved the hero, and renaming a file reshuffled the
     whole work band. There is no way for a client to guess that rule and no error when
     they trip it.
  3. Client photos had no known dimensions, so the <img> shipped without width/height and
     the page reflowed as each one loaded.

So: originals go in `foto-bron/`, the roles are named in `client.yaml`, and this script
cuts the renditions. Same shape as the per-vak stock sets (scripts/stock-photos.py) and
deliberately the same filenames and manifest, so src/lib/client.ts reads a client's own
set and a stock set through one code path.

    growth-engine/.venv/bin/python .../client-fotos.py <slug>

Re-running is safe and is the normal way to work: it re-cuts every rendition from the
originals, so it is the originals that are the artefact and `fotos/` is derived.

HEIC is handled. An iPhone hands over HEIC to Android/desktop browsers and to any upload
form that does not transcode, and "the client sent a photo the build cannot read" is
exactly the class of failure this file exists to remove.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml
from PIL import Image, ImageOps

# Registers the HEIF/HEIC decoder with Pillow. Import-and-register rather than a try/except
# fallback: a missing decoder must fail loudly at startup, not silently reject the one
# photograph the client cared about.
import pillow_heif

pillow_heif.register_heif_opener()

APP = Path(__file__).resolve().parent.parent
CLIENTS = APP / "clients"

# Same table as the stock sets, and it has to stay the same table: the pages draw a
# client's photographs into the boxes they draw stock into, so a different crop here would
# be a different layout for clients who supplied photos. See RENDITIONS in stock-photos.py
# for why each number is what it is.
#
# role -> (suffix, full size, -sm size or None, quality)
RENDITIONS: dict[str, tuple[str, tuple[int, int], tuple[int, int] | None, int]] = {
    "hero": ("hero", (1500, 1000), (750, 500), 72),
    "og": ("og", (1200, 630), None, 80),
    "tall": ("tall", (800, 1200), (400, 600), 78),
    "wide": ("wide", (900, 600), (450, 300), 78),
}

# The work band is a CSS multi-column: it fills sequentially and cannot reorder to balance,
# so this order is layout rather than tidiness. Identical to TEGELVOLGORDE in
# stock-photos.py, and identical for the same reason -- level column bottoms, ragged seams.
TEGELVOLGORDE = ("tall", "wide", "wide", "tall", "tall", "wide")

# Photo 1 is the hero and the share card; 2 onward are work tiles. A client who sends one
# photograph gets a hero and no band, which is the honest result rather than the same frame
# printed twice.
MAX_TEGELS = len(TEGELVOLGORDE)

LEESBAAR = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".tif", ".tiff"}


class FotoError(Exception):
    """A photo set that would build a broken page."""


def _laad_config(slug: str) -> dict:
    pad = CLIENTS / slug / "client.yaml"
    if not pad.exists():
        raise FotoError(f"geen config op clients/{slug}/client.yaml")
    return yaml.safe_load(pad.read_text(encoding="utf-8"))


def _open(pad: Path) -> Image.Image:
    """Read one original, orientation-corrected and in RGB.

    `exif_transpose` is not optional. A phone stores the sensor's own orientation and a
    rotation flag beside it; every browser honours the flag and Pillow does not, so
    without this a photo taken in portrait is cut in landscape and the client's best
    picture arrives on the page lying on its side.
    """
    try:
        img = Image.open(pad)
    except OSError as err:
        raise FotoError(f"{pad.name} is geen leesbare afbeelding: {err}") from err
    return ImageOps.exif_transpose(img).convert("RGB")


def _rollen(aantal: int) -> list[list[str]]:
    """Which renditions each photo in the list gets, by position."""
    rollen = [["hero", "og"]]
    for i in range(1, aantal):
        rollen.append([TEGELVOLGORDE[(i - 1) % len(TEGELVOLGORDE)]])
    return rollen


def render(slug: str) -> int:
    config = _laad_config(slug)
    fotos = config.get("fotos") or []
    if not fotos:
        raise FotoError(
            f"clients/{slug}/client.yaml heeft geen `fotos:` blok. Zonder dat blok valt de "
            "site terug op de stock-set van het vak, wat voor een voorstel de bedoeling is "
            "maar voor een betalende klant zonde van hun eigen foto's."
        )
    if len(fotos) > MAX_TEGELS + 1:
        raise FotoError(
            f"{len(fotos)} foto's, maximaal {MAX_TEGELS + 1}: een hero plus {MAX_TEGELS} "
            "tegels. De band vult in kolommen en loopt bij meer tegels scheef."
        )

    bron = CLIENTS / slug / "foto-bron"
    if not bron.exists():
        raise FotoError(
            f"geen clients/{slug}/foto-bron/. Zet daar de originelen neer zoals de klant "
            "ze aanlevert -- iedere maat, ieder formaat, ook rechtstreeks van de telefoon."
        )

    dest = CLIENTS / slug / "fotos"
    dest.mkdir(parents=True, exist_ok=True)
    # Derived output: wipe it, so a photo dropped from client.yaml really leaves the site
    # instead of lingering in dist/ because nothing deleted the file it was cut into.
    # The logo is NOT derived and is addressed by name from branding.logo, so it survives.
    logo = config.get("branding", {}).get("logo")
    for oud in dest.iterdir() if dest.exists() else []:
        if oud.is_file() and oud.name != logo:
            oud.unlink()

    manifest: list[dict] = []
    geschreven = 0
    for i, (foto, rollen) in enumerate(zip(fotos, _rollen(len(fotos))), start=1):
        bestand = foto.get("bestand")
        alt = (foto.get("alt") or "").strip()
        if not bestand:
            raise FotoError(f"foto {i} heeft geen `bestand:`")
        # Dutch alt text is required and cannot be defaulted: an undescribed photograph is
        # an accessibility hole, and these are content photographs on a trade site rather
        # than decoration, so alt="" is wrong too. Same rule the stock sets are held to.
        if len(alt) < 10:
            raise FotoError(
                f"foto {i} ({bestand}) heeft geen bruikbare `alt:`. Beschrijf in het "
                "Nederlands wat er te zien is, minstens tien tekens."
            )
        pad = bron / bestand
        if not pad.exists():
            beschikbaar = ", ".join(sorted(p.name for p in bron.iterdir() if p.is_file()))
            raise FotoError(
                f"clients/{slug}/foto-bron/{bestand} bestaat niet. Aanwezig: {beschikbaar or '(niets)'}"
            )
        if pad.suffix.lower() not in LEESBAAR:
            raise FotoError(f"{bestand}: {pad.suffix} wordt niet gelezen ({', '.join(sorted(LEESBAAR))})")

        img = _open(pad)
        for rol in rollen:
            suffix, size, size_sm, quality = RENDITIONS[rol]
            # Identical naming to the stock sets so one loader reads both: the hero and the
            # share card are named for their role, a tile keeps its index and carries its
            # shape in the suffix, which is how the page reads the ratio back.
            stem = suffix if rol in ("hero", "og") else f"{i}-{suffix}"
            for naam, box in [(stem, size)] + ([(f"{stem}-sm", size_sm)] if size_sm else []):
                # `fit` crops to fill rather than letterboxing: the page reserves the box
                # from these numbers, so a rendition that does not fill it would ship a
                # band of background inside the frame.
                ImageOps.fit(img, box, Image.LANCZOS).save(
                    dest / f"{naam}.webp", quality=quality, method=6
                )
                geschreven += 1
            if rol != "og":
                manifest.append(
                    {
                        "bestand": f"{stem}.webp",
                        "rol": rol,
                        "breedte": size[0],
                        "hoogte": size[1],
                        "alt": alt,
                    }
                )
            kb = (dest / f"{stem}.webp").stat().st_size // 1024
            print(f"{stem}.webp  <- {bestand} [{rol}] {kb} KB")

    (dest / "fotos.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return geschreven + 1


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("slug", help="clientmap onder clients/")
    args = parser.parse_args(argv)
    try:
        n = render(args.slug)
    except FotoError as err:
        print(f"[client-fotos] GESTOPT: {err}", file=sys.stderr)
        return 1
    print(f"[client-fotos] {n} bestanden geschreven naar clients/{args.slug}/fotos/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
