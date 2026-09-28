"""
File: tools/social_preview.py
Author: Amey Thakur
GitHub: https://github.com/Amey-Thakur
Repository: https://github.com/Amey-Thakur/AI-ENGINEERING
License: MIT

Description:
Draws the card that appears when the repository is shared.

The geometry is the sibling geometry, measured from the other repositories
rather than invented here: a 1280 by 640 canvas, six bands, every one of them
centred on the middle of the card, the mark's ink starting at y=75, the title
sitting on a 300 pixel baseline, a 344 pixel rule at y=396, and the footer
starting at y=575. check_layout asserts all of that before the file is
written, so the card cannot drift off the family and still be saved.

Nothing countable appears on it. A card is a static image somebody uploads to
GitHub by hand, so a lesson count printed on it is wrong from the first commit
that adds a lesson. The card carries what will still be true next year: what
the course is, and the three things about it that are unusual.

Usage:
    python tools/social_preview.py
"""

from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont

import lesson
import typeface

OUT = lesson.ROOT / ".github" / "social-preview.png"
MARK = lesson.ROOT / ".github" / "assets" / "mark-flat.png"

SIZE = (1280, 640)

BACKGROUND = (0x0D, 0x10, 0x16)
INK = (0xF7, 0xF9, 0xFC)
PALE = (0xC6, 0xCE, 0xDA)
ACCENT = (0x6E, 0xE7, 0xB7)
DIM = (0x8A, 0x94, 0xA4)
EDGE = (0x2A, 0x3B, 0x34)

TITLE = "AI Engineering"
SUBTITLE = "Learn to build AI systems by building them"
KEYWORDS = "no dependencies · no API key · offline"
FOOTER = "AI Engineering · MIT · github.com/Amey-Thakur"

#: Anchors measured from the sibling cards.
MARK_W, MARK_H = 74, 64
LOGO_TOP = 75
TITLE_BASE = 300
TITLE_FITS = 760
SUB_TOP = 339
RULE_Y, RULE_W = 396, 344
KEY_TOP = 433
FOOT_TOP = 575

#: How far a band's centre may sit from the middle of the card.
OFF_CENTRE = 2.0

#: A row counts as inked when a pixel differs from the ground by this much,
#: summed across the three channels.
THRESHOLD = 18

#: Rows closer together than this belong to the same band.
BAND_GAP = 6

_probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))


def ink_box(text: str, font: ImageFont.FreeTypeFont):
    """Ink extent in the coordinates draw.text uses, so subtracting the box
    origin lands the ink exactly on an anchor."""
    return _probe.textbbox((0, 0), text, font=font)


def centred(card: Image.Image, text: str, font: ImageFont.FreeTypeFont,
            fill, top: int):
    """Place text so its ink starts at `top` and is centred on the canvas.

    The text is drawn on its own layer, cropped to the ink it actually
    produced, and only then positioned. Placing it by the predicted box
    instead leaves it a pixel or two off, because the antialiased left edge of
    one glyph and the right edge of another do not fade symmetrically, and the
    layout check below measures the ink rather than the prediction.
    """
    x0, y0, x1, y1 = ink_box(text, font)
    pad = 40
    layer = Image.new("RGBA", (x1 - x0 + pad * 2, y1 - y0 + pad * 2),
                      (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((pad - x0, pad - y0), text, font=font,
                               fill=fill + (255,))

    ink = layer.getbbox()

    if ink is None:
        return 0, 0

    cropped = layer.crop(ink)
    card.paste(cropped, (round((SIZE[0] - cropped.width) / 2), top), cropped)

    return cropped.width, cropped.height


def fit_title(text: str, target: int, largest: int = 124):
    """The largest black face that keeps the title inside `target`."""
    size = largest

    while size > 24:
        face = typeface.of("black", size)
        x0, _, x1, _ = ink_box(text, face)

        if x1 - x0 <= target:
            return face

        size -= 1

    return typeface.of("black", 24)


def draw() -> Image.Image:
    card = Image.new("RGB", SIZE, BACKGROUND)
    pen = ImageDraw.Draw(card)

    mark = Image.open(MARK).convert("RGBA")

    if mark.size != (MARK_W, MARK_H):
        mark = mark.resize((MARK_W, MARK_H), Image.LANCZOS)

    card.paste(mark, (round((SIZE[0] - MARK_W) / 2), LOGO_TOP), mark)

    # The title is placed by its bottom edge, not its top, so a longer or
    # shorter name still sits on the same line as the sibling cards.
    title = fit_title(TITLE, TITLE_FITS)
    _, top, _, bottom = ink_box(TITLE, title)
    centred(card, TITLE, title, INK, TITLE_BASE - (bottom - top))

    centred(card, SUBTITLE, typeface.of("sans", 29), PALE, SUB_TOP)

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
    """The card is only a sibling if it lands on the sibling geometry."""
    pixels = card.convert("RGB").load()
    ground = pixels[5, 5]
    found = bands(pixels, ground)
    problems = []

    if len(found) != 6:
        problems.append(f"expected 6 bands, drew {len(found)}")

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
    if found and abs(found[0][0] - LOGO_TOP) > 1:
        problems.append(f"the mark starts at {found[0][0]}, not {LOGO_TOP}")

    if found and abs(found[-1][0] - FOOT_TOP) > 1:
        problems.append(f"the footer starts at {found[-1][0]}, not {FOOT_TOP}")

    if problems:
        raise SystemExit("the card drifted off the sibling geometry:\n  "
                         + "\n  ".join(problems))

    return found


def main() -> int:
    if not MARK.exists():
        print(f"FAIL  {MARK.relative_to(lesson.ROOT).as_posix()} is missing")
        print("      run `python tools/build_mark.py` first")
        return 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    card = draw()

    for top, bottom in check_layout(card):
        print(f"  band y={top}-{bottom}")

    card.save(OUT, optimize=True)

    print(f"  {OUT.relative_to(lesson.ROOT).as_posix()}  "
          f"{SIZE[0]}x{SIZE[1]}  {OUT.stat().st_size // 1024} KB  "
          f"six bands, every one centred")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
