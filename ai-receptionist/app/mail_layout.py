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
# Amber at 8% and 22% over white. The accent is a signal colour, not a surface: a full-
# strength sodium panel is a highlighter pen, and amber text on white is unreadable at
# about 1.9:1. These two carry the brand as a tint while every glyph stays ink.
_TINT = "#fdf6ea"
_TINT_EDGE = "#f2e3c8"
_CHIP = "#fbecd2"

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
class Fine:
    """Small print tied to the block above it — an asterisked footnote under a Panel or
    Table. Rendered smaller and muted, and kept tight against its block, because at full
    paragraph size and spacing a footnote reads as the next point instead of an aside."""

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
class Amount:
    """The confirmation hero: what was received, in type you cannot miss.

    A payment mail's whole job in the first two seconds is "how much, for what". As a
    sentence in the body that answers itself only after the reader has parsed a paragraph,
    so it gets its own tinted card at the top.
    """

    label: str
    value: str
    note: str = ""


@dataclass(frozen=True)
class KeyValues:
    """Label/value rows, hairline-separated — the terms of a subscription.

    Prose is the wrong shape for numbers the reader comes back to check. A Panel of
    sentences makes them hunt; a two-column table lets them scan the left edge.
    """

    rows: list[tuple[str, str]]


@dataclass(frozen=True)
class Columns:
    """Two labelled address blocks side by side — the Van/Aan head of a factuur. Built as
    two 50% table cells, which is also what makes them stack on a phone without a media
    query: the cells simply run out of room."""

    left_label: str
    left_lines: list[str]
    right_label: str
    right_lines: list[str]


@dataclass(frozen=True)
class Table:
    """Line items. The last column is money and is right-aligned in both renderers, because
    a column of amounts that does not line up on the decimal is unreadable."""

    headers: list[str]
    rows: list[list[str]]


@dataclass(frozen=True)
class Totals:
    """The sum block under a Table. `grand` is set apart with a rule above it — the one
    number the reader is actually looking for."""

    lines: list[tuple[str, str]]
    grand: tuple[str, str]


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


Block = (
    Heading
    | Para
    | Fine
    | Steps
    | Panel
    | Amount
    | KeyValues
    | Columns
    | Table
    | Totals
    | Button
    | Photo
    | Signoff
)


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
        # A short amber bar instead of the full-width hairline that used to sit under every
        # heading: the rule made each section look like a spec sheet, and three of them made
        # a welcome mail look like documentation. The bar carries the brand and gives the
        # page rhythm without cutting it into slices. Built as a table cell, not a styled
        # div -- Outlook honours width/height/bgcolor on a <td> and little else.
        return _cell(
            '<table role="presentation" cellpadding="0" cellspacing="0" border="0">'
            f'<tr><td width="26" height="3" bgcolor="{_SODIUM}" style="width:26px;height:3px;'
            f'background:{_SODIUM};font-size:0;line-height:0;">&nbsp;</td></tr></table>'
            f'<div style="font-size:19px;font-weight:700;color:{_INK};letter-spacing:-0.015em;'
            f'padding-top:12px;">{escape(block.text)}</div>',
            top=top + 10,
        )

    if isinstance(block, Para):
        return _cell(f"<div>{escape(block.text)}</div>", top=top)

    if isinstance(block, Fine):
        # Tight to the block above regardless of section spacing: it belongs to it.
        return _cell(
            f'<div style="font-size:13px;line-height:1.6;color:{_MUTED};">'
            f"{escape(block.text)}</div>",
            top=0 if first else 10,
        )

    if isinstance(block, Steps):
        # Numbered chips rather than <ol>: list markers cannot be styled reliably across
        # clients, and Outlook indents them unpredictably. The numeral stays ink on a pale
        # amber chip -- amber numerals on white fall to about 1.9:1, which is not a contrast
        # ratio you put a number the reader has to read at.
        rows = "".join(
            f'<tr><td width="28" valign="top" style="padding:0 12px 10px 0;">'
            f'<table role="presentation" cellpadding="0" cellspacing="0" border="0">'
            f'<tr><td width="26" height="26" align="center" bgcolor="{_CHIP}" '
            f'style="width:26px;height:26px;background:{_CHIP};border-radius:7px;'
            f"font-family:{_FONT};font-size:13px;font-weight:700;color:{_INK};"
            f'line-height:26px;">{i}</td></tr></table></td>'
            f'<td valign="top" style="padding:0 0 10px 0;font-family:{_FONT};font-size:16px;'
            f'line-height:1.55;color:{_BODY};">{escape(item)}</td></tr>'
            for i, item in enumerate(block.items, start=1)
        )
        return _cell(
            '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" '
            f'border="0">{rows}</table>',
            top=top,
        )

    if isinstance(block, Amount):
        return _cell(
            '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" '
            f'border="0"><tr><td bgcolor="{_TINT}" style="background:{_TINT};'
            f"border:1px solid {_TINT_EDGE};border-radius:12px;padding:22px 24px;"
            f'font-family:{_FONT};">'
            f'<div style="font-size:11px;letter-spacing:0.09em;text-transform:uppercase;'
            f'color:{_MUTED};">{escape(block.label)}</div>'
            f'<div style="font-size:30px;font-weight:700;color:{_INK};letter-spacing:-0.02em;'
            f'padding-top:6px;line-height:1.2;">{escape(block.value)}</div>'
            + (
                f'<div style="font-size:13px;color:{_MUTED};padding-top:6px;">'
                f"{escape(block.note)}</div>"
                if block.note
                else ""
            )
            + "</td></tr></table>",
            top=top,
        )

    if isinstance(block, KeyValues):
        rows = ""
        for i, (label, value) in enumerate(block.rows):
            edge = "" if i == 0 else f"border-top:1px solid {_RULE};"
            rows += (
                f'<tr><td valign="top" style="{edge}padding:11px 12px 11px 0;font-family:{_FONT};'
                f'font-size:14px;color:{_MUTED};">{escape(label)}</td>'
                f'<td valign="top" align="right" style="{edge}padding:11px 0;font-family:{_FONT};'
                f'font-size:14px;font-weight:600;color:{_INK};">{escape(value)}</td></tr>'
            )
        return _cell(
            '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" '
            f'border="0">{rows}</table>',
            top=top,
        )

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

    if isinstance(block, Columns):

        def column(label: str, lines: list[str], pad_right: int) -> str:
            body = "<br>".join(escape(str(line)) for line in lines if line)
            return (
                f'<td width="50%" valign="top" style="font-family:{_FONT};font-size:14px;'
                f'line-height:1.6;color:{_BODY};padding-right:{pad_right}px;">'
                f'<div style="font-size:11px;letter-spacing:0.08em;text-transform:uppercase;'
                f'color:{_MUTED};padding-bottom:6px;">{escape(label)}</div>{body}</td>'
            )

        return _cell(
            '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" '
            f'border="0"><tr>{column(block.left_label, block.left_lines, 16)}'
            f"{column(block.right_label, block.right_lines, 0)}</tr></table>",
            top=top,
        )

    if isinstance(block, Table):
        th = (
            f"font-family:{_FONT};font-size:11px;letter-spacing:0.08em;text-transform:uppercase;"
            f"color:{_MUTED};padding:0 8px 8px 0;border-bottom:1px solid {_RULE};text-align:left;"
        )
        td = f"font-family:{_FONT};font-size:14px;color:{_BODY};padding:14px 8px 14px 0;"
        head = "".join(
            f'<th style="{th}{"text-align:right;padding-right:0;" if i == len(block.headers) - 1 else ""}">'
            f"{escape(h)}</th>"
            for i, h in enumerate(block.headers)
        )
        body = ""
        for row in block.rows:
            cells = "".join(
                (
                    f'<td align="right" style="{td}padding-right:0;">{escape(str(c))}</td>'
                    if i == len(row) - 1
                    else f'<td style="{td}">{escape(str(c))}</td>'
                )
                for i, c in enumerate(row)
            )
            body += f"<tr>{cells}</tr>"
        return _cell(
            '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" '
            f'border="0"><tr>{head}</tr>{body}</table>',
            top=top,
        )

    if isinstance(block, Totals):

        def total_row(label: str, value: str, *, grand: bool) -> str:
            weight = "700" if grand else "400"
            border = f"border-top:2px solid {_INK};" if grand else ""
            colour = _INK if grand else _BODY
            style = (
                f"font-family:{_FONT};font-size:{'16px' if grand else '14px'};color:{colour};"
                f"font-weight:{weight};{border}"
            )
            return (
                f'<tr><td style="{style}padding:9px 8px 9px 0;">{escape(label)}</td>'
                f'<td align="right" style="{style}padding:9px 0;">{escape(value)}</td></tr>'
            )

        rows = "".join(total_row(k, v, grand=False) for k, v in block.lines)
        rows += total_row(block.grand[0], block.grand[1], grand=True)
        # Right-aligned 280px stack: the totals belong under the amount column, not spanning
        # the full width, or the eye has to travel back across the page to pair them up.
        return _cell(
            '<table role="presentation" width="280" cellpadding="0" cellspacing="0" border="0" '
            f'align="right" style="width:280px;">{rows}</table>',
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
    if isinstance(block, Fine):
        return _wrap(block.text)
    if isinstance(block, Steps):
        return "\n".join(f"{i}. {item}" for i, item in enumerate(block.items, start=1))
    if isinstance(block, Panel):
        return "\n".join(_wrap(line) for line in block.lines)
    if isinstance(block, Amount):
        # The tinted card has no plain-text equivalent, so the emphasis comes from putting
        # the number on its own line under its label rather than inside a sentence.
        out = f"{block.label.upper()}\n{block.value}"
        return f"{out}\n{block.note}" if block.note else out
    if isinstance(block, KeyValues):
        width = max((len(label) for label, _ in block.rows), default=0)
        return "\n".join(f"{label.ljust(width)}  {value}" for label, value in block.rows)
    if isinstance(block, Columns):
        left = "\n".join(str(x) for x in block.left_lines if x)
        right = "\n".join(str(x) for x in block.right_lines if x)
        return f"{block.left_label.upper()}\n{left}\n\n{block.right_label.upper()}\n{right}"
    if isinstance(block, Table):
        # Pad every column to its widest cell so the amounts line up in a fixed-width font;
        # the money column is right-aligned, same as the HTML.
        grid = [list(map(str, block.headers))] + [list(map(str, r)) for r in block.rows]
        widths = [max(len(row[i]) for row in grid) for i in range(len(grid[0]))]
        last = len(widths) - 1
        lines = []
        for r, row in enumerate(grid):
            cells = [
                cell.rjust(widths[i]) if i == last else cell.ljust(widths[i])
                for i, cell in enumerate(row)
            ]
            lines.append("  ".join(cells).rstrip())
            if r == 0:
                lines.append("-" * len("  ".join(cells).rstrip()))
        return "\n".join(lines)
    if isinstance(block, Totals):
        pairs = list(block.lines) + [block.grand]
        width = max(len(label) for label, _ in pairs)
        body = [f"{label.ljust(width)}  {value}" for label, value in block.lines]
        grand = f"{block.grand[0].ljust(width)}  {block.grand[1]}"
        return "\n".join(body + ["-" * len(grand), grand])
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
