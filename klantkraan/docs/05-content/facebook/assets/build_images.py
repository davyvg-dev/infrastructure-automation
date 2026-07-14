"""Build Klantkraan Facebook post images (1080x1080): flat brand SVGs + the real logo.

Palette: kraan-blue #0F4C81, cream #FAF6EE, rust #C75A2B (accent only).
Type: Helvetica Neue (Inter Tight stand-in on macOS), lowercase wordmark.
Logo: the actual @Klantkraan mark (klantkraan-logo-x.jpg), composited as a rounded
badge with Pillow so it doesn't depend on the SVG renderer supporting <image>.

Regenerate:  python3 build_images.py   (needs macOS `qlmanage` + Pillow)
"""
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw

OUT = Path(__file__).parent
LOGO = OUT / "klantkraan-logo-x.jpg"
BLUE = "#0F4C81"
CREAM = "#FAF6EE"
RUST = "#C75A2B"
STONE7 = "#4a463d"
STONE5 = "#8c8474"
STONE2 = "#d9d2c0"
FONT = "Helvetica Neue, Helvetica, Arial, sans-serif"

W = H = 1080
BADGE = 120                 # logo badge size
BADGE_XY = (96, 88)         # top-left of the badge
WORD_X = BADGE_XY[0] + BADGE + 26   # wordmark sits right of the badge
WORD_Y = BADGE_XY[1] + 74           # baseline, vertically centred on the badge


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def headline(head):
    return "".join(
        f'<text x="96" y="{460 + i*92}" font-family="{FONT}" font-size="78" '
        f'font-weight="700" letter-spacing="-1.5" fill="{c}">{esc(t)}</text>'
        for i, (t, c) in enumerate(head))


def concept_a() -> str:
    """Problem angle, cream background."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="{CREAM}"/>
  <text x="{WORD_X}" y="{WORD_Y}" font-family="{FONT}" font-size="40" font-weight="700" letter-spacing="-1" fill="{BLUE}">klantkraan</text>
  {headline([("Elke gemiste oproep", BLUE), ("is een klus voor de", BLUE), ("concurrent.", RUST)])}
  <text x="96" y="770" font-family="{FONT}" font-size="32" fill="{STONE7}">Een digitale receptionist die 24/7 opneemt, vragen</text>
  <text x="96" y="812" font-family="{FONT}" font-size="32" fill="{STONE7}">beantwoordt en de afspraak meteen inplant.</text>
  <rect x="96" y="928" width="888" height="4" fill="{RUST}"/>
  <text x="96" y="1002" font-family="{FONT}" font-size="40" font-weight="700" fill="{BLUE}">klantkraan.nl</text>
  <text x="984" y="1000" text-anchor="end" font-family="{FONT}" font-size="26" fill="{STONE5}">loodgieters &#183; dakdekkers &#183; installateurs</text>
</svg>"""


def concept_b() -> str:
    """Benefit angle, kraan-blue background."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="{BLUE}"/>
  <text x="{WORD_X}" y="{WORD_Y}" font-family="{FONT}" font-size="40" font-weight="700" letter-spacing="-1" fill="{CREAM}">klantkraan</text>
  {headline([("Nooit meer een klus", CREAM), ("mislopen door een", CREAM), ("gemiste oproep.", RUST)])}
  <text x="96" y="770" font-family="{FONT}" font-size="32" fill="{STONE2}">24/7 antwoord op elke oproep en WhatsApp — elke</text>
  <text x="96" y="812" font-family="{FONT}" font-size="32" fill="{STONE2}">klant te woord gestaan, elke afspraak ingepland.</text>
  <rect x="96" y="928" width="888" height="4" fill="{CREAM}"/>
  <text x="96" y="1002" font-family="{FONT}" font-size="40" font-weight="700" fill="{CREAM}">klantkraan.nl</text>
  <text x="984" y="1000" text-anchor="end" font-family="{FONT}" font-size="26" fill="{STONE2}">de digitale receptionist voor de vakman</text>
</svg>"""


def _badge() -> tuple[Image.Image, Image.Image]:
    """The logo resized to BADGE px with an anti-aliased rounded-square alpha mask."""
    logo = Image.open(LOGO).convert("RGB").resize((BADGE, BADGE), Image.LANCZOS)
    ss = 4
    mask = Image.new("L", (BADGE * ss, BADGE * ss), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, BADGE * ss - 1, BADGE * ss - 1], radius=28 * ss, fill=255)
    return logo, mask.resize((BADGE, BADGE), Image.LANCZOS)


def render(svg: str, stem: str, pad="#FAF6EE"):
    svg_path = OUT / f"{stem}.svg"
    svg_path.write_text(svg, encoding="utf-8")
    (OUT / f"{stem}.svg.png").unlink(missing_ok=True)
    subprocess.run(["qlmanage", "-t", "-s", str(W), "-o", str(OUT), str(svg_path)],
                   capture_output=True)
    raw = OUT / f"{stem}.svg.png"
    img = Image.open(raw).convert("RGB")
    if img.size != (W, H):  # normalize any QL padding to an exact square
        canvas = Image.new("RGB", (W, H), pad)
        canvas.paste(img, ((W - img.width) // 2, (H - img.height) // 2))
        img = canvas
    logo, mask = _badge()
    img.paste(logo, BADGE_XY, mask)
    img.save(OUT / f"{stem}.png")
    raw.unlink(missing_ok=True)
    print(f"{OUT / f'{stem}.png'}  {img.size}")


render(concept_a(), "fb-post-problem", pad=CREAM)
render(concept_b(), "fb-post-benefit", pad=BLUE)
