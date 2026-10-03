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

from PIL import Image, ImageDraw, ImageFont

import build_mark
import lesson
import typeface

OUT = lesson.ROOT / ".github" / "social-preview.png"

SIZE = (1280, 640)

BACKGROUND = (0xFA, 0xFB, 0xFC)
INK = (0x22, 0x30, 0x3C)
PALE = (0x5B, 0x6B, 0x78)
ACCENT = (0x37, 0x76, 0xAB)
DIM = (0x87, 0x94, 0xA0)
EDGE = (0xD7, 0xDD, 0xE3)

NAME = "AI Engineering"
SUBTITLE = "Learn to build AI systems by building them"
KEYWORDS = "no dependencies · no API key · offline"
FOOTER = "AI Engineering · MIT · github.com/Amey-Thakur"

#: The lockup: how tall the mark is, the gap to the name, and the name's size.
MARK_H = 86
MARK_GAP = 28
NAME_SIZE = 96

#: Anchors. The lockup and the footer are asserted; the rest sit between them.
LOCKUP_TOP = 168
SUB_TOP = 322
RULE_Y, RULE_W = 400, 344
KEY_TOP = 440
FOOT_TOP = 575

#: How far a band's centre may sit from the middle of the card.
OFF_CENTRE = 2.0

#: A row counts as inked when a pixel differs from the ground by this much,
#: summed across the three channels.
THRESHOLD = 18

#: Rows closer together than this belong to the same band.
BAND_GAP = 6

#: How many bands the card is meant to have.
BANDS = 5

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


def lockup(card: Image.Image) -> None:
    """The mark, then the name, as one block centred on the card.

    The name sits on the mark's own bottom edge rather than on its centre,
    which is what stops the letters looking as though they float beside it.
    """
    mark = build_mark.cropped_to_ink(
        build_mark.prompt(MARK_H * 6, MARK_H * 5, INK, ACCENT))
    mark = mark.resize(
        (round(mark.width * MARK_H / mark.height), MARK_H), Image.LANCZOS)

    name = rendered(NAME, typeface.of("black", NAME_SIZE), INK)
    span = mark.width + MARK_GAP + name.width
    left = round((SIZE[0] - span) / 2)
    base = LOCKUP_TOP + max(mark.height, name.height)

    card.paste(mark, (left, base - mark.height), mark)
    card.paste(name, (left + mark.width + MARK_GAP, base - name.height), name)


def draw() -> Image.Image:
    card = Image.new("RGB", SIZE, BACKGROUND)
    pen = ImageDraw.Draw(card)

    lockup(card)

    centred(card, SUBTITLE, typeface.of("sans", 31), PALE, SUB_TOP)

    pen.line([(SIZE[0] - RULE_W) / 2, RULE_Y, (SIZE[0] + RULE_W) / 2, RULE_Y],
             fill=EDGE)

    centred(card, KEYWORDS, typeface.of("mono", 26), ACCENT, KEY_TOP)
    centred(card, FOOTER, typeface.of("mono", 21), DIM, FOOT_TOP)

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


def check_layout(card: Image.Image) -> list[tuple[int, int]]:
    """The card is only right if it lands on its own measured geometry."""
    pixels = card.convert("RGB").load()
    ground = pixels[5, 5]
    found = bands(pixels, ground)
    problems = []

    if len(found) != BANDS:
        problems.append(f"expected {BANDS} bands, drew {len(found)}")

    for top, bottom in found:
        left = right = None

        for x in range(SIZE[0]):
            if any(_inked(pixels, ground, x, y)
                   for y in range(top, bottom + 1)):
                left = x if left is None else left
                right = x

        if left is None:
            continue

        middle = (left + right + 1) / 2

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
    OUT.parent.mkdir(parents=True, exist_ok=True)
    card = draw()

    for top, bottom in check_layout(card):
        print(f"  band y={top}-{bottom}")

    card.save(OUT, optimize=True)

    print(f"  {OUT.relative_to(lesson.ROOT).as_posix()}  "
          f"{SIZE[0]}x{SIZE[1]}  {OUT.stat().st_size // 1024} KB  "
          f"{BANDS} bands, every one centred")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
