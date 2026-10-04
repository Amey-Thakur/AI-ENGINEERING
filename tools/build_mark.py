"""
File: tools/build_mark.py
Author: Amey Thakur
GitHub: https://github.com/Amey-Thakur
Repository: https://github.com/Amey-Thakur/AI-ENGINEERING
License: MIT

Description:
Draws the mark, at the sizes and in the formats the repository uses it.

The mark is a shell prompt: a chevron and a cursor. That is the most literal
thing this course is. Lesson 1 is opening a terminal, the whole promise is
that nothing is installed and everything runs in a shell, and the first thing
any reader meets is a prompt waiting for them.

The cursor blinks. A real one does, on for about half a second and off for
about half a second, switching rather than fading, so the animation here is a
square wave on a 1.06 second cycle rather than a pulse. That is the detail
that makes it read as a terminal and not as a logo of one.

Both formats come off one set of numbers. geometry() computes the lockup once
and the raster and the vector both lay out from it, so the blinking SVG and
the flat PNG cannot drift apart.

Colours come from the launch kit's colour reference rather than invention.
Slate is the documented neutral spine for a project card that belongs to no
institution, and the accent is Python's own blue, because the one product this
course names is Python.

    assets/ai-engineering-mark.png    192x192 plated, for anywhere static
    assets/ai-engineering-mark.svg    the same, with the cursor blinking
    assets/mark-on-slate.svg          paper ink, blinking, for a title bar
    assets/favicon.png                64x64 plated, for the browser tab
    .github/assets/mark-flat.png      its own ink size, for the social card

Usage:
    python tools/build_mark.py
"""

from __future__ import annotations

from PIL import Image, ImageDraw

import lesson

SQUARE = lesson.ROOT / "assets" / "ai-engineering-mark.png"
SQUARE_SVG = lesson.ROOT / "assets" / "ai-engineering-mark.svg"
ON_SLATE = lesson.ROOT / "assets" / "mark-on-slate.svg"
FAVICON = lesson.ROOT / "assets" / "favicon.png"
FLAT = lesson.ROOT / ".github" / "assets" / "mark-flat.png"

#: Supersampled, then resampled down, which is the only way a stroked chevron
#: comes out with clean edges.
SS = 4

SLATE = (0x2F, 0x3E, 0x4A)
PYTHON = (0x37, 0x76, 0xAB)
PAPER = (0xFA, 0xFB, 0xFC)

RADIUS = 42

#: How opaque a pixel has to be to count as ink worth cropping to.
VISIBLE = 40

#: The sibling cards give the mark a 64 pixel band, so the flat mark's ink
#: fills that height rather than sitting inset inside a box of that size.
FLAT_INK_HEIGHT = 64

#: A real cursor is on for about half a second and off for about half a
#: second, and it switches rather than fades.
BLINK_SECONDS = 1.06


def ink(colour: tuple[int, int, int]) -> str:
    return "#%02X%02X%02X" % colour


def geometry(width: float, height: float) -> dict:
    """The lockup, measured once, for both the raster and the vector.

    Laid out on a unit grid and then placed so the ink is centred. A lockup
    positioned by eye lands a few pixels left, and the social card's layout
    check measures ink and would refuse it.
    """
    unit = min(width, height)
    stroke = max(2.0, round(unit * 0.085))
    middle = height / 2
    reach = unit * 0.17
    rise = unit * 0.17
    gap = unit * 0.09
    bar = unit * 0.30

    span = (reach + stroke / 2) + gap + bar
    start = (width - span) / 2 + stroke / 2
    point = start + reach
    bar_left = point + gap

    return {
        "stroke": stroke,
        "chevron": [(start, middle - rise), (point, middle),
                    (start, middle + rise)],
        "cursor": (bar_left, middle + rise - stroke, bar_left + bar,
                   middle + rise),
        "radius": round(stroke * 0.4),
    }


#: The ink box of the lockup, as a share of the box geometry() is given. Both
#: fall out of the ratios above and are used to size a mark by its ink rather
#: than by the padding around it.
INK_WIDTH = 0.6025
INK_HEIGHT = 0.3825


def lockup(target_height: float) -> dict:
    """The lockup scaled so its ink is `target_height` tall.

    Returns the ink size and the cursor rect measured from the ink's own top
    left, so a caller can place the mark and then put a blinking cursor
    exactly on top of it without having to track a crop and a resize.
    """
    unit = target_height / INK_HEIGHT
    shape = geometry(unit, unit)
    left = shape["chevron"][0][0] - shape["stroke"] / 2
    top = shape["chevron"][0][1] - shape["stroke"] / 2
    x0, y0, x1, y1 = shape["cursor"]

    return {
        "unit": unit,
        "size": (unit * INK_WIDTH, unit * INK_HEIGHT),
        "origin": (left, top),
        "chevron": [(x - left, y - top) for x, y in shape["chevron"]],
        "cursor": (x0 - left, y0 - top, x1 - left, y1 - top),
        "stroke": shape["stroke"],
        "radius": shape["radius"],
    }


def prompt(width: int, height: int, colour, cursor, plate=None,
           radius: int = RADIUS) -> Image.Image:
    """A chevron and a cursor, drawn to fill the box it is given."""
    card = Image.new("RGBA", (width * SS, height * SS), (0, 0, 0, 0))
    pen = ImageDraw.Draw(card)

    if plate is not None:
        pen.rounded_rectangle([0, 0, width * SS - 1, height * SS - 1],
                              radius=radius * SS, fill=plate + (255,))

    shape = geometry(width, height)

    pen.line([(x * SS, y * SS) for x, y in shape["chevron"]],
             fill=colour + (255,), width=round(shape["stroke"]) * SS,
             joint="curve")

    left, top, right, bottom = shape["cursor"]
    pen.rounded_rectangle([left * SS, top * SS, right * SS, bottom * SS],
                          radius=shape["radius"] * SS, fill=cursor + (255,))

    return card


def svg(width: int, height: int, colour, cursor, plate=None,
        radius: int = RADIUS) -> str:
    """The same mark as a vector, with the cursor blinking.

    The blink is a CSS animation inside the document rather than a script, so
    it runs where an SVG is loaded as an image, which is how both GitHub and
    the site's title bar load it.
    """
    shape = geometry(width, height)
    points = " ".join(f"{x:.2f},{y:.2f}" for x, y in shape["chevron"])
    left, top, right, bottom = shape["cursor"]
    half = BLINK_SECONDS / 2

    backdrop = ""
    if plate is not None:
        backdrop = (f'\n  <rect width="{width}" height="{height}" '
                    f'rx="{radius}" fill="{ink(plate)}"/>')

    return f"""\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}"
     width="{width}" height="{height}" role="img"
     aria-label="AI Engineering: a shell prompt with a blinking cursor">
  <title>AI Engineering</title>
  <style>
    /* On for half the cycle, off for the other half, switching rather than
       fading, which is what a terminal cursor actually does. */
    @keyframes blink {{
      0%, 50% {{ opacity: 1; }}
      50.01%, 100% {{ opacity: 0; }}
    }}
    .cursor {{
      animation: blink {BLINK_SECONDS}s steps(1, end) infinite;
    }}
    /* Anybody who has asked not to be shown motion gets a steady cursor. */
    @media (prefers-reduced-motion: reduce) {{
      .cursor {{ animation: none; opacity: 1; }}
    }}
  </style>{backdrop}
  <polyline points="{points}" fill="none" stroke="{ink(colour)}"
            stroke-width="{shape['stroke']:.0f}" stroke-linecap="round"
            stroke-linejoin="round"/>
  <rect class="cursor" x="{left:.2f}" y="{top:.2f}"
        width="{right - left:.2f}" height="{bottom - top:.2f}"
        rx="{shape['radius']}" fill="{ink(cursor)}"/>
</svg>
"""


def cropped_to_ink(card: Image.Image) -> Image.Image:
    """Trim to the ink that will actually show, not to any trace of alpha."""
    box = card.getchannel("A").point(
        lambda value: 255 if value > VISIBLE else 0).getbbox()

    return card.crop(box) if box else card


def main() -> int:
    SQUARE.parent.mkdir(parents=True, exist_ok=True)

    plated = prompt(192, 192, PAPER, PYTHON, SLATE, RADIUS).resize(
        (192, 192), Image.LANCZOS)
    plated.save(SQUARE, optimize=True)

    SQUARE_SVG.write_text(svg(192, 192, PAPER, PYTHON, SLATE, RADIUS),
                          encoding="utf-8", newline="\n")

    # The title bar is slate, so its mark is drawn in paper on nothing. The
    # viewBox is cropped to the lockup so the bar does not pad it with air.
    shape = geometry(142, 96)
    left = shape["chevron"][0][0] - shape["stroke"] / 2
    right = shape["cursor"][2]
    top = shape["chevron"][0][1] - shape["stroke"] / 2
    bottom = shape["cursor"][3]
    bare = svg(142, 96, PAPER, PYTHON)
    bare = bare.replace(
        'viewBox="0 0 142 96"\n     width="142" height="96"',
        f'viewBox="{left:.2f} {top:.2f} {right - left:.2f} '
        f'{bottom - top:.2f}"\n     width="{right - left:.0f}" '
        f'height="{bottom - top:.0f}"')
    ON_SLATE.write_text(bare, encoding="utf-8", newline="\n")

    favicon = plated.resize((64, 64), Image.LANCZOS)
    favicon.save(FAVICON, optimize=True)

    # Drawn large and trimmed, so the ink fills the band the card gives it.
    big = cropped_to_ink(prompt(320, 280, SLATE, PYTHON))
    flat = big.resize(
        (round(big.width * FLAT_INK_HEIGHT / big.height), FLAT_INK_HEIGHT),
        Image.LANCZOS)
    FLAT.parent.mkdir(parents=True, exist_ok=True)
    flat.save(FLAT, optimize=True)

    for path in (SQUARE, SQUARE_SVG, ON_SLATE, FAVICON, FLAT):
        print(f"  {path.relative_to(lesson.ROOT).as_posix():36} "
              f"{path.stat().st_size // 1024} KB")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
