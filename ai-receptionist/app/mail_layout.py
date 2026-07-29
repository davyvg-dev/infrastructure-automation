"""Brand layout for outgoing e-mail: one document, rendered as HTML and as text.

Until this existed every mail we sent was raw plain text. A EUR 299/mo customer's
first word from us looked like a terminal dump, which is a strange thing to receive
from a company selling a polished front desk.

The unit here is a *block*, not a string of HTML. Callers describe what they want to
say -- a heading, a paragraph, a numbered list, a button -- and this module decides
what that looks like. Two renderers consume the same blocks, so the HTML and the
plain-text alternative can never drift apart, and the copy lives in exactly one place.

Why hand-rolled tables instead of a template engine: mail clients are not browsers.
Outlook renders through Word, Gmail strips <head> styles from forwarded copies, and
neither supports flexbox or grid. Nested tables with inline styles is the only layout
that survives all of them, and it needs no dependency.

Every mail ships both parts. The text one is not a courtesy: it is what plain-text
clients, screen readers in text mode and spam filters read, and a message with no
text alternative scores worse on delivery.

The images live on klantkraan.nl (see marketing-site/scripts/build-brand.mjs), because
a mail client will not render an attachment as a layout image and inlining base64 wrecks
deliverability. Images are also blocked by default in many clients, so nothing here
carries meaning that only exists in a picture -- the mail reads complete with every
image switched off.
"""

from __future__ import annotations

import textwrap
from dataclasses import dataclass
from html import escape

# --- Brand ------------------------------------------------------------------------------
# Mirrors marketing-site/src/styles/global.css. The site is dark end to end; mail is not.
# A dark band carries the logo and a light card carries the words, because forced dark-mode
# in Gmail and Outlook.com mangles a fully dark mail, and a wall of dark HTML scores worse
# with spam filters. The accent stays the same sodium amber, so it still reads as us.

SITE = "https://klantkraan.nl"
LOGO = f"{SITE}/email/logo.png"

# The legal foot every mail carries. Transactional mail needs no unsubscribe -- it is not
# marketing -- but it does need to say who is writing and where the terms live. KvK from
# marketing-site/src/data/company.ts; the BTW number is still pending, and the site hides
# that field while it is empty, so this does too rather than print "BTW ".
_COMPANY = "Klantkraan is een handelsnaam van T4 Software Consulting BV — KvK 90232135"
_FOOTER_LINKS = [
    ("Privacy", f"{SITE}/legal/privacy/"),
    ("Voorwaarden", f"{SITE}/legal/voorwaarden/"),
]

_BAND = "#0f1c1e"  # header, same night as the site
_WRAP = "#e9eeed"  # page behind the card
_CARD = "#ffffff"
_INK = "#16292b"  # headings
_BODY = "#35474a"  # body copy
_MUTED = "#5f7371"  # footer, captions
_RULE = "#e2e8e7"
_SODIUM = "#ffb84d"

# Brand faces are web fonts; no mail client will load them. This stack is what the
# reader's OS already has, in the order that looks closest to Hanken Grotesk.
_FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif"

_WIDTH = 600
_PAD = 32
_TEXT_WRAP = 78  # plain-text column


# --- Blocks -----------------------------------------------------------------------------


@dataclass(frozen=True)
class Heading:
    """A section title. Sentence case here; the text renderer shouts it, because upper
    case is the only heading a plain-text mail has."""

    text: str


@dataclass(frozen=True)
class Para:
    text: str


@dataclass(frozen=True)
class Steps:
    """A numbered list. Numbered rather than bulleted wherever the reader is expected to
    do the items, so "point 2" means something when they reply."""

    items: list[str]


@dataclass(frozen=True)
class Panel:
    """A boxed summary -- an order, a subscription. Set off from the prose because the
    reader comes back to this later looking for exactly these numbers."""

    lines: list[str]


@dataclass(frozen=True)
class Button:
    label: str
    href: str


@dataclass(frozen=True)
class Photo:
    """Full-bleed, like the site. Decorative: `alt` describes it, but no block above or
    below may depend on the reader seeing it."""

    src: str
    alt: str
    width: int = 700
    height: int = 450


@dataclass(frozen=True)
class Signoff:
    name: str
    email: str


Block = Heading | Para | Steps | Panel | Button | Photo | Signoff


# --- HTML -------------------------------------------------------------------------------


def _cell(inner: str, *, top: int = 0, pad: int = _PAD) -> str:
    return (
        f'<tr><td style="padding:{top}px {pad}px 0 {pad}px;font-family:{_FONT};'
        f'font-size:16px;line-height:1.65;color:{_BODY};">{inner}</td></tr>'
    )


def _block_html(block: Block, *, first: bool, after_heading: bool) -> str:
    # A heading and the block it titles are one unit; the gap between them is smaller than
    # the gap between sections, or the heading floats between two paragraphs.
    top = 0 if first else 14 if after_heading else 24

    if isinstance(block, Heading):
        return _cell(
            f'<div style="font-size:17px;font-weight:700;color:{_INK};'
            f'letter-spacing:-0.01em;">{escape(block.text)}</div>'
            f'<div style="height:1px;background:{_RULE};margin-top:9px;"></div>',
            top=top + 8,
        )

    if isinstance(block, Para):
        return _cell(f"<div>{escape(block.text)}</div>", top=top)

    if isinstance(block, Steps):
        items = "".join(
            f'<li style="margin:0 0 6px 0;padding-left:4px;">{escape(item)}</li>'
            for item in block.items
        )
        return _cell(f'<ol style="margin:0;padding-left:22px;">{items}</ol>', top=top)

    if isinstance(block, Panel):
        lines = "".join(
            f'<div style="margin-top:{0 if i == 0 else 4}px;">{escape(line)}</div>'
            for i, line in enumerate(block.lines)
        )
        return _cell(
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" '
            f'border="0"><tr><td style="background:#f4f7f6;border:1px solid {_RULE};'
            f"border-radius:10px;padding:16px 18px;font-family:{_FONT};font-size:15px;"
            f'line-height:1.6;color:{_BODY};">{lines}</td></tr></table>',
            top=top,
        )

    if isinstance(block, Button):
        # Table-cell button: Outlook ignores padding on <a>, but honours it on a <td>.
        # 46px tall on purpose -- the same 44px minimum the site's .btn keeps for thumbs.
        return _cell(
            f'<table role="presentation" cellpadding="0" cellspacing="0" border="0">'
            f'<tr><td align="center" bgcolor="{_SODIUM}" style="background:{_SODIUM};'
            f'border-radius:10px;"><a href="{escape(block.href, quote=True)}" '
            f'style="display:inline-block;padding:14px 28px;font-family:{_FONT};'
            f'font-size:16px;font-weight:700;color:{_BAND};text-decoration:none;">'
            f"{escape(block.label)}</a></td></tr></table>",
            top=top,
        )

    if isinstance(block, Photo):
        height = round(block.height * _WIDTH / block.width)
        return (
            f'<tr><td style="padding-top:{top + 6}px;font-size:0;line-height:0;">'
            f'<img src="{escape(block.src, quote=True)}" width="{_WIDTH}" height="{height}" '
            f'alt="{escape(block.alt, quote=True)}" style="display:block;border:0;width:100%;'
            f'max-width:{_WIDTH}px;height:auto;"></td></tr>'
        )

    if isinstance(block, Signoff):
        return _cell(
            f'<div style="color:{_INK};font-weight:600;">{escape(block.name)}</div>'
            f'<div><a href="mailto:{escape(block.email, quote=True)}" '
            f'style="color:{_BODY};text-decoration:underline;">{escape(block.email)}</a></div>',
            top=top,
        )

    raise TypeError(f"unknown block: {block!r}")


def _footer_html(note: str | None = None) -> str:
    links = ' <span style="color:#c3cecc;">·</span> '.join(
        f'<a href="{escape(href, quote=True)}" style="color:{_MUTED};'
        f'text-decoration:underline;">{escape(label)}</a>'
        for label, href in _FOOTER_LINKS
    )
    extra = f"<div>{escape(note)}</div>" if note else ""
    return (
        f'<tr><td style="padding:26px {_PAD}px 24px {_PAD}px;">'
        f'<div style="height:1px;background:{_RULE};margin-bottom:18px;"></div>'
        f'<div style="font-family:{_FONT};font-size:12px;line-height:1.7;color:{_MUTED};">'
        f"<div>{escape(_COMPANY)}</div><div>{links}</div>{extra}</div></td></tr>"
    )


def to_html(
    blocks: list[Block],
    *,
    subject: str,
    preheader: str,
    lang: str = "nl",
    footer_note: str | None = None,
) -> str:
    """Render the branded HTML part.

    `preheader` is the grey line the inbox shows next to the subject. Left unset, clients
    scrape it from the body and show "Hoi Jan, Uw betaling" -- a wasted line of the only
    preview a reader gets before deciding to open.

    `footer_note` appends one line under the legal foot. Transactional mail leaves it unset;
    cold sales mail puts the opt-out there, which Telecommunicatiewet art. 11.7 requires and
    the transactional footer deliberately has no room for.
    """
    body = ""
    after_heading = False
    for i, block in enumerate(blocks):
        body += _block_html(block, first=(i == 0), after_heading=after_heading)
        after_heading = isinstance(block, Heading)
    return (
        "<!doctype html>"
        f'<html lang="{escape(lang, quote=True)}"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="color-scheme" content="light">'
        '<meta name="supported-color-schemes" content="light">'
        f"<title>{escape(subject)}</title></head>"
        f'<body style="margin:0;padding:0;background:{_WRAP};-webkit-font-smoothing:antialiased;">'
        # Hidden preview line, then zero-width joiners so the client cannot pad the preview
        # with the first words of the body.
        f'<div style="display:none;max-height:0;max-width:0;opacity:0;overflow:hidden;'
        f'font-size:1px;line-height:1px;color:{_WRAP};">{escape(preheader)}'
        f"{'&#8204;&nbsp;' * 60}</div>"
        f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" '
        f'style="background:{_WRAP};"><tr><td align="center" style="padding:24px 12px;">'
        f'<table role="presentation" width="{_WIDTH}" cellpadding="0" cellspacing="0" border="0" '
        f'style="width:{_WIDTH}px;max-width:100%;background:{_CARD};border-radius:14px;'
        f'overflow:hidden;">'
        # Header band: the logo on the same night the site runs.
        f'<tr><td style="background:{_BAND};padding:26px {_PAD}px;">'
        f'<img src="{LOGO}" width="163" height="21" alt="Klantkraan" '
        f'style="display:block;border:0;width:163px;height:21px;"></td></tr>'
        f'<tr><td style="padding-top:{_PAD}px;"></td></tr>'
        f"{body}"
        f"{_footer_html(footer_note)}"
        "</table></td></tr></table></body></html>"
    )


# --- Plain text -------------------------------------------------------------------------


def _wrap(text: str) -> str:
    return textwrap.fill(text, width=_TEXT_WRAP, break_long_words=False, break_on_hyphens=False)


def _block_text(block: Block) -> str | None:
    if isinstance(block, Heading):
        return block.text.upper()
    if isinstance(block, Para):
        return _wrap(block.text)
    if isinstance(block, Steps):
        return "\n".join(f"{i}. {item}" for i, item in enumerate(block.items, start=1))
    if isinstance(block, Panel):
        return "\n".join(_wrap(line) for line in block.lines)
    if isinstance(block, Button):
        # A text reader cannot click anything, so give them the destination itself. A
        # mailto is an address, not a URL: "mailto:x@y?subject=Mijn%20gegevens" is noise.
        target = block.href
        if target.startswith("mailto:"):
            target = target[len("mailto:") :].split("?", 1)[0]
        return f"{block.label}: {target}"
    if isinstance(block, Photo):
        return None  # a picture has no plain-text equivalent worth inventing
    if isinstance(block, Signoff):
        return f"{block.name}\n{block.email}"
    raise TypeError(f"unknown block: {block!r}")


def to_text(blocks: list[Block], *, footer_note: str | None = None) -> str:
    """Render the plain-text alternative. Headings shout, because that is the only
    typography a text mail has, and they stay tight against the paragraph they title."""
    out = ""
    after_heading = False
    for block in blocks:
        rendered = _block_text(block)
        if rendered is None:
            continue
        if out:
            out += "\n" if after_heading else "\n\n"
        out += rendered
        after_heading = isinstance(block, Heading)

    # A text reader has no hyperlinks, so the footer spells its destinations out.
    footer = [_COMPANY] + [f"{label}: {href}" for label, href in _FOOTER_LINKS]
    if footer_note:
        footer.append(footer_note)
    return out + "\n\n" + "-" * 40 + "\n" + "\n".join(footer) + "\n"
