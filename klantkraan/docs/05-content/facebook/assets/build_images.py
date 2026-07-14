"""Build Klantkraan Facebook post images (1080x1080) as flat brand SVGs, render to PNG.

Brand: kraan-blue #0F4C81, cream #FAF6EE, rust #C75A2B (accent only), dark #0a3960.
Type: Helvetica Neue (Inter Tight stand-in on macOS), lowercase wordmark. No gradients,
no shadows — Wim Crouwel / Dutch-functional per the logo brief.
"""
import subprocess
from pathlib import Path
from PIL import Image

OUT = Path(__file__).parent
BLUE = "#0F4C81"
BLUE_DK = "#0a3960"
CREAM = "#FAF6EE"
RUST = "#C75A2B"
STONE7 = "#4a463d"
STONE5 = "#8c8474"
STONE2 = "#d9d2c0"
FONT = "Helvetica Neue, Helvetica, Arial, sans-serif"

W = H = 1080


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def wordmark(x, y, sq_fill, k_fill, text_fill):
    """A 64px rounded-square 'k' mark + the lowercase wordmark, matching the favicon."""
    return f"""
  <rect x="{x}" y="{y}" width="64" height="64" rx="14" fill="{sq_fill}"/>
  <text x="{x+32}" y="{y+46}" text-anchor="middle" font-family="{FONT}" font-size="42"
        font-weight="700" fill="{k_fill}">k</text>
  <text x="{x+82}" y="{y+47}" font-family="{FONT}" font-size="40" font-weight="700"
        letter-spacing="-1" fill="{text_fill}">klantkraan</text>"""


def concept_a() -> str:
    """Problem angle, cream background."""
    head = [("Elke gemiste oproep", BLUE), ("is een klus voor de", BLUE),
            ("concurrent.", RUST)]
    lines = "".join(
        f'<text x="96" y="{460 + i*92}" font-family="{FONT}" font-size="78" '
        f'font-weight="700" letter-spacing="-1.5" fill="{c}">{esc(t)}</text>'
        for i, (t, c) in enumerate(head))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="{CREAM}"/>
  {wordmark(96, 96, BLUE, CREAM, BLUE)}
  {lines}
  <text x="96" y="770" font-family="{FONT}" font-size="32" fill="{STONE7}">Een digitale receptionist die 24/7 opneemt, vragen</text>
  <text x="96" y="812" font-family="{FONT}" font-size="32" fill="{STONE7}">beantwoordt en de afspraak meteen inplant.</text>
  <rect x="96" y="928" width="888" height="4" fill="{RUST}"/>
  <text x="96" y="1002" font-family="{FONT}" font-size="40" font-weight="700" fill="{BLUE}">klantkraan.nl</text>
  <text x="984" y="1000" text-anchor="end" font-family="{FONT}" font-size="26" fill="{STONE5}">loodgieters &#183; dakdekkers &#183; installateurs</text>
</svg>"""


def concept_b() -> str:
    """Benefit angle, kraan-blue background."""
    head = [("Nooit meer een klus", CREAM), ("mislopen door een", CREAM),
            ("gemiste oproep.", RUST)]
    lines = "".join(
        f'<text x="96" y="{460 + i*92}" font-family="{FONT}" font-size="78" '
        f'font-weight="700" letter-spacing="-1.5" fill="{c}">{esc(t)}</text>'
        for i, (t, c) in enumerate(head))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="{BLUE}"/>
  <text x="96" y="143" font-family="{FONT}" font-size="40" font-weight="700" letter-spacing="-1" fill="{CREAM}">klantkraan</text>
  {lines}
  <text x="96" y="770" font-family="{FONT}" font-size="32" fill="{STONE2}">24/7 antwoord op elke oproep en WhatsApp — elke</text>
  <text x="96" y="812" font-family="{FONT}" font-size="32" fill="{STONE2}">klant te woord gestaan, elke afspraak ingepland.</text>
  <rect x="96" y="928" width="888" height="4" fill="{CREAM}"/>
  <text x="96" y="1002" font-family="{FONT}" font-size="40" font-weight="700" fill="{CREAM}">klantkraan.nl</text>
  <text x="984" y="1000" text-anchor="end" font-family="{FONT}" font-size="26" fill="{STONE2}">de digitale receptionist voor de vakman</text>
</svg>"""


def render(svg: str, stem: str):
    svg_path = OUT / f"{stem}.svg"
    svg_path.write_text(svg, encoding="utf-8")
    for f in OUT.glob(f"{stem}.svg.png"):
        f.unlink()
    subprocess.run(["qlmanage", "-t", "-s", str(W), "-o", str(OUT), str(svg_path)],
                   capture_output=True)
    raw = OUT / f"{stem}.svg.png"
    img = Image.open(raw).convert("RGB")
    if img.size != (W, H):  # normalize any QL padding to an exact square
        canvas = Image.new("RGB", (W, H), "#FAF6EE")
        canvas.paste(img, ((W - img.width) // 2, (H - img.height) // 2))
        img = canvas
    final = OUT / f"{stem}.png"
    img.save(final)
    raw.unlink(missing_ok=True)
    print(f"{final}  {img.size}")


render(concept_a(), "fb-post-problem")
render(concept_b(), "fb-post-benefit")
