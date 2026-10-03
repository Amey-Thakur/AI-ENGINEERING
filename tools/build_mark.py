"""
File: tools/build_mark.py
Author: Amey Thakur
GitHub: https://github.com/Amey-Thakur
Repository: https://github.com/Amey-Thakur/AI-ENGINEERING
License: MIT

Description:
Draws the mark, at the sizes the repository uses it.

The mark is a shell prompt: a chevron and a cursor. That is the most literal
thing this course is. Lesson 1 is opening a terminal, the whole promise is
that nothing is installed and everything runs in a shell, and the first thing
any reader sees is a prompt waiting for them.

It is drawn with strokes rather than set in a font, so the weight is the same
at 16 pixels and at 192 and nothing depends on which faces a machine has.

Colours come from the launch kit's colour reference rather than from
invention. Slate is the documented neutral spine for a project card that
belongs to no institution, and the accent is Python's own blue, because the
one product this course names is Python.

Two outputs, matching the sibling convention:

    assets/ai-engineering-mark.png        192x192, for the README footer
    .github/assets/mark-flat.png          74x64, for the social preview card

The square one is plated so it reads the same on GitHub's light and dark
themes. The flat one is transparent, because the card supplies its own ground.

Usage:
    python tools/build_mark.py
"""

from __future__ import annotations

from PIL import Image, ImageDraw

import lesson

SQUARE = lesson.ROOT / "assets" / "ai-engineering-mark.png"
FLAT = lesson.ROOT / ".github" / "assets" / "mark-flat.png"

#: Supersampled, then resampled down, which is the only way a stroked chevron
#: comes out with clean edges.
SS = 4

#: Slate, the documented neutral for a project card with no institution
#: behind it, and Python's own blue for the accent.
SLATE = (0x2F, 0x3E, 0x4A)
PYTHON = (0x37, 0x76, 0xAB)
PAPER = (0xFA, 0xFB, 0xFC)

RADIUS = 42


def prompt(width: int, height: int, ink, cursor, plate=None,
           radius: int = RADIUS) -> Image.Image:
    """A chevron and a cursor, drawn to fill the box it is given."""
    card = Image.new("RGBA", (width * SS, height * SS), (0, 0, 0, 0))
    pen = ImageDraw.Draw(card)

    if plate is not None:
        pen.rounded_rectangle([0, 0, width * SS - 1, height * SS - 1],
                              radius=radius * SS, fill=plate + (255,))

    # The lockup is laid out on a unit grid and then scaled, so the chevron
    # and the cursor keep their proportions at every size.
    unit = min(width, height)
    stroke = max(2, round(unit * 0.085))
    middle = height / 2
    reach = unit * 0.17
    rise = unit * 0.17
    gap = unit * 0.09
    bar = unit * 0.30

    # Measured from the strokes rather than guessed, then shifted so the ink
    # is centred. A lockup positioned by eye lands a few pixels left, and the
    # card's layout check measures ink and would refuse it.
    span = (reach + stroke / 2) + gap + bar
    start = (width - span) / 2 + stroke / 2
    point = start + reach

    pen.line(
        [start * SS, (middle - rise) * SS,
         point * SS, middle * SS,
         start * SS, (middle + rise) * SS],
        fill=ink + (255,), width=stroke * SS, joint="curve",
    )

    # A block cursor rather than an underscore: at sixteen pixels an
    # underscore is one row of grey and a block is still a cursor.
    bar_left = point + gap

    pen.rounded_rectangle(
        [bar_left * SS, (middle + rise - stroke) * SS,
         (bar_left + bar) * SS, (middle + rise) * SS],
        radius=round(stroke * 0.4) * SS, fill=cursor + (255,),
    )

    return card.resize((width, height), Image.LANCZOS)


#: How opaque a pixel has to be to count as ink worth cropping to.
VISIBLE = 40

#: The sibling cards give the mark a 64 pixel band, so the flat mark's ink
#: fills that height rather than sitting inset inside a box of that size.
FLAT_INK_HEIGHT = 64


def cropped_to_ink(card: Image.Image) -> Image.Image:
    """Trim to the ink that will actually show, not to any trace of alpha."""
    box = card.getchannel("A").point(
        lambda value: 255 if value > VISIBLE else 0).getbbox()

    return card.crop(box) if box else card


def main() -> int:
    SQUARE.parent.mkdir(parents=True, exist_ok=True)
    plated = prompt(192, 192, PAPER, PYTHON, SLATE, RADIUS)
    plated.save(SQUARE, optimize=True)

    # Drawn large and trimmed, so the ink fills the band the card gives it.
    # Drawing straight into a 74 by 64 box leaves the lockup inset and the
    # mark reads as lost under a hundred point title.
    big = cropped_to_ink(prompt(320, 280, SLATE, PYTHON))
    width = round(big.width * FLAT_INK_HEIGHT / big.height)
    flat = big.resize((width, FLAT_INK_HEIGHT), Image.LANCZOS)
    FLAT.parent.mkdir(parents=True, exist_ok=True)
    flat.save(FLAT, optimize=True)

    for path, card in ((SQUARE, plated), (FLAT, flat)):
        print(f"  {path.relative_to(lesson.ROOT).as_posix()}  "
              f"{card.width}x{card.height}  "
              f"{path.stat().st_size // 1024} KB")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
