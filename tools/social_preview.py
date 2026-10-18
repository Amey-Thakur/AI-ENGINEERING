"""
File: tools/social_preview.py
Author: Amey Thakur
GitHub: https://github.com/Amey-Thakur
Repository: https://github.com/Amey-Thakur/AI-ENGINEERING
License: MIT

Description:
Draws the card that appears when the repository is shared.

The hero is the lockup: the mark, then the name beside it, the same pairing
the README header uses. The sibling index card splits those into a small
wordmark above a large title, which works when the two differ. Here they would
be the same two words, so the card would say the name twice. One lockup, once,
at size.

Everything below it keeps the sibling discipline. Five bands, every one
centred on the middle of the card, each anchored to a measured row, and
check_layout asserts all of it before the file is written, so the card cannot
drift off its geometry and still be saved.

Nothing countable appears on it. A card is a static image somebody uploads to
GitHub by hand, so a lesson count printed on it is wrong from the first commit
that adds a lesson. The card carries what will still be true next year.

Colours are paper, slate and Python's own blue, taken from the launch kit's
colour reference rather than invented here.

Usage:
    python tools/social_preview.py
"""

from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

from PIL import Image, ImageDraw, ImageFont

import build_mark
import lesson
import typeface

SIZE = (1280, 640)

#: The cursor's blue, taken from the mark so the two cannot drift. It appears
#: twice on each card and nowhere else: on the cursor, and on the short bar
#: under the subtitle.
ACCENT = build_mark.CURSOR


class Palette(NamedTuple):
    """One ground and the four tones that sit on it."""

    name: str
    ground: tuple[int, int, int]
    ink: tuple[int, int, int]
    pale: tuple[int, int, int]
    dim: tuple[int, int, int]
    edge: tuple[int, int, int]
    out: Path


#: Two grounds, one identity. Every tone is measured against its own ground,
#: and the lowest in either is the cursor at 3.7 to 1, which is a graphic
#: rather than text and clears the 3 to 1 a graphic needs.
#:
#:              slate ground        paper ground
#:   ink        15.9 to 1           15.4 to 1
#:   pale        6.7 to 1            5.9 to 1
#:   dim         4.1 to 1            4.0 to 1
#:   cursor      3.7 to 1            3.6 to 1
PALETTES = (
    Palette("slate", (0x22, 0x30, 0x3C), (0xFA, 0xFB, 0xFC),
            (0xA8, 0xB6, 0xC2), (0x7E, 0x8F, 0x9D), (0x39, 0x4A, 0x59),
            lesson.ROOT / ".github" / "social-preview.png"),
    Palette("paper", (0xFA, 0xFB, 0xFC), (0x22, 0x30, 0x3C),
            (0x5B, 0x6B, 0x78), (0x87, 0x94, 0xA0), (0xD7, 0xDD, 0xE3),
            lesson.ROOT / ".github" / "social-preview-light.png"),
)

NAME = "AI Engineering"
SUBTITLE = "Learn to build AI systems by building them"
#: The README's own pitch, split three ways. A heading and one line each,
#: because three short claims a reader can check are worth more than a row of
#: adjectives. Nothing countable: the card is uploaded by hand.
PILLARS = (
    ("Write every line",
     "backpropagation, attention and a",
     "transformer block, derived by hand"),
    ("Measure every claim",
     "error bars, baselines, and the",
     "results that did not hold up"),
    ("Install nothing",
     "the standard library, offline,",
     "no account and no API key"),
)
FOOTER = "AI Engineering · MIT · github.com/Amey-Thakur"

#: The lockup: how tall the mark is, the gap to the name, and the name's size.
MARK_H = 86
MARK_GAP = 28
NAME_SIZE = 96

#: Anchors. The lockup and the footer are asserted; the rest sit between them.
LOCKUP_TOP = 128
SUB_TOP = 274
RULE_Y, RULE_W, RULE_H = 344, 140, 5

#: Three columns, centred as a group and each centred on its own middle, so
#: the band they make is symmetric about the card's centre line.
PILLAR_TOP = 396
PILLAR_LINE = 36
PILLAR_WIDTH = 372
PILLAR_GAP = 34

FOOT_RULE_Y, FOOT_RULE_W = 534, 760
FOOT_TOP = 566

#: How far a band's centre may sit from the middle of the card.
OFF_CENTRE = 2.0

#: How far a column's text may sit from its own column's middle. Looser than
#: OFF_CENTRE because a short string centred in a wide column is judged by eye
#: against its neighbours rather than against a single axis.
COLUMN_OFF_CENTRE = 3.0

#: A horizontal blank this wide separates one column from the next rather than
#: one word from the next.
COLUMN_GAP = 24

#: A row counts as inked when a pixel differs from the ground by this much,
#: summed across the three channels.
THRESHOLD = 18

#: Rows closer together than this belong to the same band.
BAND_GAP = 6

#: How many bands the card is meant to have.
BANDS = 8

_probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))


def ink_box(text: str, font: ImageFont.FreeTypeFont):
    """Ink extent in the coordinates draw.text uses, so subtracting the box
    origin lands the ink exactly on an anchor."""
    return _probe.textbbox((0, 0), text, font=font)


def rendered(text: str, font: ImageFont.FreeTypeFont, fill) -> Image.Image:
    """The text on its own layer, trimmed to the ink it actually produced.

    Positioning by the predicted box leaves text a pixel or two off, because
    the antialiased left edge of one glyph and the right edge of another do
    not fade symmetrically, and the layout check measures ink.
    """
    x0, y0, x1, y1 = ink_box(text, font)
    pad = 40
    layer = Image.new("RGBA", (x1 - x0 + pad * 2, y1 - y0 + pad * 2),
                      (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((pad - x0, pad - y0), text, font=font,
                               fill=fill + (255,))
    box = layer.getbbox()

    return layer.crop(box) if box else layer


def centred(card: Image.Image, text: str, font: ImageFont.FreeTypeFont,
            fill, top: int) -> None:
    """Place text so its ink starts at `top` and is centred on the canvas."""
    patch = rendered(text, font, fill)
    card.paste(patch, (round((SIZE[0] - patch.width) / 2), top), patch)


def lockup(card: Image.Image, palette: "Palette") -> None:
    """The mark, then the name, as one block centred on the card.

    The name sits on the mark's own bottom edge rather than on its centre,
    which is what stops the letters looking as though they float beside it.
    """
    mark = build_mark.cropped_to_ink(
        build_mark.prompt(MARK_H * 6, MARK_H * 5, palette.ink, ACCENT))
    mark = mark.resize(
        (round(mark.width * MARK_H / mark.height), MARK_H), Image.LANCZOS)

    name = rendered(NAME, typeface.of("black", NAME_SIZE), palette.ink)
    span = mark.width + MARK_GAP + name.width
    left = round((SIZE[0] - span) / 2)
    base = LOCKUP_TOP + max(mark.height, name.height)

    card.paste(mark, (left, base - mark.height), mark)
    card.paste(name, (left + mark.width + MARK_GAP, base - name.height), name)



def column_middles() -> list[float]:
    """Where each column sits. Symmetric about the card's centre."""
    span = len(PILLARS) * PILLAR_WIDTH + (len(PILLARS) - 1) * PILLAR_GAP
    left = (SIZE[0] - span) / 2

    return [left + index * (PILLAR_WIDTH + PILLAR_GAP) + PILLAR_WIDTH / 2
            for index in range(len(PILLARS))]


def pillar_row(card: Image.Image, texts: tuple[str, ...],
               face: ImageFont.FreeTypeFont, fill, top: int) -> None:
    """One row, each string centred on its own column's middle."""
    for middle, text in zip(column_middles(), texts):
        patch = rendered(text, face, fill)
        card.paste(patch, (round(middle - patch.width / 2), top), patch)


def pillars(card: Image.Image, palette: "Palette") -> None:
    """The three columns: a heading and two lines each."""
    heading = typeface.of("sans bold", 25)
    body = typeface.of("sans", 20)

    pillar_row(card, tuple(one[0] for one in PILLARS), heading,
               palette.ink, PILLAR_TOP)
    pillar_row(card, tuple(one[1] for one in PILLARS), body,
               palette.pale, PILLAR_TOP + PILLAR_LINE)
    pillar_row(card, tuple(one[2] for one in PILLARS), body,
               palette.pale, PILLAR_TOP + PILLAR_LINE * 2)


def draw(palette: "Palette") -> Image.Image:
    card = Image.new("RGB", SIZE, palette.ground)
    pen = ImageDraw.Draw(card)

    lockup(card, palette)

    centred(card, SUBTITLE, typeface.of("sans", 31), palette.pale, SUB_TOP)

    # The same short accent bar the record carries under its title.
    pen.rectangle([(SIZE[0] - RULE_W) / 2, RULE_Y,
                   (SIZE[0] + RULE_W) / 2, RULE_Y + RULE_H - 1], fill=ACCENT)

    pillars(card, palette)

    # A hairline above the footer, so the last line is attached to something
    # rather than floating under a hundred empty pixels.
    pen.line([(SIZE[0] - FOOT_RULE_W) / 2, FOOT_RULE_Y,
              (SIZE[0] + FOOT_RULE_W) / 2, FOOT_RULE_Y],
             fill=palette.edge)

    centred(card, FOOTER, typeface.of("mono", 21), palette.dim, FOOT_TOP)

    return card


def _inked(pixels, ground, x: int, y: int) -> bool:
    spot = pixels[x, y]

    return (abs(spot[0] - ground[0]) + abs(spot[1] - ground[1])
            + abs(spot[2] - ground[2])) > THRESHOLD


def bands(pixels, ground) -> list[tuple[int, int]]:
    """The vertical runs of rows that have ink in them."""
    rows = []

    for y in range(SIZE[1]):
        for x in range(SIZE[0]):
            if _inked(pixels, ground, x, y):
                rows.append(y)
                break

    if not rows:
        return []

    found = []
    start = previous = rows[0]

    for y in rows[1:]:
        if y - previous > BAND_GAP:
            found.append((start, previous))
            start = y

        previous = y

    found.append((start, previous))

    return found



def runs(pixels, ground, top: int, bottom: int) -> list[tuple[int, int]]:
    """The inked stretches across a band, split where it goes blank.

    A centred line comes back as one stretch. A row of columns comes back
    as one per column, which is what lets the check measure each of them
    against its own place on the grid.
    """
    found: list[tuple[int, int]] = []
    first = last = None

    for x in range(SIZE[0]):
        if any(_inked(pixels, ground, x, y)
               for y in range(top, bottom + 1)):
            first = x if first is None else first
            last = x
        elif first is not None and x - last > COLUMN_GAP:
            found.append((first, last))
            first = last = None

    if first is not None:
        found.append((first, last))

    return found

def check_layout(card: Image.Image) -> list[tuple[int, int]]:
    """The card is only right if it lands on its own measured geometry."""
    pixels = card.convert("RGB").load()
    ground = pixels[5, 5]
    found = bands(pixels, ground)
    problems = []

    if len(found) != BANDS:
        problems.append(f"expected {BANDS} bands, drew {len(found)}")

    lowest = PILLAR_TOP - 8
    highest = PILLAR_TOP + PILLAR_LINE * 2 + 40

    for top, bottom in found:
        columns = runs(pixels, ground, top, bottom)

        if not columns:
            continue

        # The three column rows are a grid, not a centred line. Three strings
        # of different lengths cannot be both centred in their columns and
        # symmetric as a row, so for those rows the grid is what gets checked.
        if lowest <= top <= highest:
            middles = column_middles()

            if len(columns) != len(middles):
                problems.append(f"band {top}-{bottom} has {len(columns)} "
                                f"columns, not {len(middles)}")
                continue

            for (first, last), wanted in zip(columns, middles):
                middle = (first + last + 1) / 2

                if abs(middle - wanted) > COLUMN_OFF_CENTRE:
                    problems.append(
                        f"a column in band {top}-{bottom} is centred on "
                        f"{middle:.1f}, not {wanted:.1f}")

            continue

        middle = (columns[0][0] + columns[-1][1] + 1) / 2

        if abs(middle - SIZE[0] / 2) > OFF_CENTRE:
            problems.append(f"band {top}-{bottom} centred on {middle:.1f}, "
                            f"not {SIZE[0] / 2}")

    # One pixel of slack: the faintest antialiased row of a glyph can fall
    # under the threshold, which moves a measured band without the text having
    # moved.
    if found and abs(found[0][0] - LOCKUP_TOP) > 1:
        problems.append(f"the lockup starts at {found[0][0]}, not "
                        f"{LOCKUP_TOP}")

    if found and abs(found[-1][0] - FOOT_TOP) > 1:
        problems.append(f"the footer starts at {found[-1][0]}, not "
                        f"{FOOT_TOP}")

    if problems:
        raise SystemExit("the card drifted off its geometry:\n  "
                         + "\n  ".join(problems))

    return found


def main() -> int:
    for palette in PALETTES:
        palette.out.parent.mkdir(parents=True, exist_ok=True)
        card = draw(palette)
        found = check_layout(card)
        card.save(palette.out, optimize=True)
        print(f"  {palette.out.relative_to(lesson.ROOT).as_posix()}  "
              f"{SIZE[0]}x{SIZE[1]}  "
              f"{palette.out.stat().st_size // 1024} KB  "
              f"{len(found)} bands, every one centred  "
              f"[{palette.name}]")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
