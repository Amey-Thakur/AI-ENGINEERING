"""
File: tools/glyphs.py
Author: Amey Thakur
GitHub: https://github.com/Amey-Thakur
Repository: https://github.com/Amey-Thakur/AI-ENGINEERING
License: MIT

Description:
Draws the few outside marks the artwork needs, from vendored path data.

A card that points at a repository should carry the mark a reader recognises,
and the footer of every card here does. Fetching it at build time would mean
the artwork could not be rebuilt offline, which is the one thing this course
will not do, so the outline is vendored as the path data it is and rasterised
here.

The GitHub mark below is the simple-icons outline, which is published under
CC0. It is a single closed subpath of cubic curves, so flattening the curves
and filling one polygon reproduces it exactly, with no need for a renderer
that understands fill rules or holes.

Everything is drawn at several times the final size and resampled down, which
is how a curve this small comes out clean.

Usage:
    python tools/glyphs.py        write a sheet of the marks, to look at
"""

from __future__ import annotations

import re

from PIL import Image, ImageDraw

import lesson

#: The simple-icons GitHub mark, CC0. Its viewBox is 24 by 24.
GITHUB = (
    "M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82"
    "-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C"
    "4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084"
    " 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417"
    "-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235"
    "-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98"
    "-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23"
    ".645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805"
    " 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0"
    " .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12"
    "-12"
)

VIEWBOX = 24.0

#: Drawn this many times larger, then resampled. A mark 28 pixels tall has
#: curves far smaller than a pixel, and nothing below this is clean.
SS = 8

#: Segments per curve. The longest curve on this mark is under a third of its
#: width, so this is well past the point where more makes a visible
#: difference.
STEPS = 24

NUMBER = re.compile(r"-?\d*\.?\d+(?:[eE][-+]?\d+)?")
COMMAND = re.compile(r"[A-Za-z]")


def numbers(chunk: str) -> list[float]:
    return [float(found) for found in NUMBER.findall(chunk)]


def cubic(start, one, two, end, steps: int) -> list[tuple[float, float]]:
    """A cubic curve as points, the start excluded so runs join cleanly."""
    points = []
    for step in range(1, steps + 1):
        t = step / steps
        u = 1 - t
        points.append((
            u * u * u * start[0] + 3 * u * u * t * one[0]
            + 3 * u * t * t * two[0] + t * t * t * end[0],
            u * u * u * start[1] + 3 * u * u * t * one[1]
            + 3 * u * t * t * two[1] + t * t * t * end[1],
        ))
    return points


def outline(path: str, steps: int = STEPS) -> list[tuple[float, float]]:
    """The path as one closed polygon, in viewBox units.

    Only the commands this mark uses are handled: a moveto and cubics, in
    both cases carrying on with the same command when more numbers follow,
    which is how compact path data is written.
    """
    pieces = [piece for piece in COMMAND.split(path)]
    letters = COMMAND.findall(path)

    points: list[tuple[float, float]] = []
    here = (0.0, 0.0)

    for letter, chunk in zip(letters, pieces[1:]):
        values = numbers(chunk)

        if letter in "Mm":
            relative = letter == "m"
            first, rest = values[:2], values[2:]
            here = ((here[0] + first[0], here[1] + first[1]) if relative
                    else (first[0], first[1]))
            points.append(here)
            # Numbers after a moveto are linetos, which this mark does not use.
            if rest:
                raise SystemExit("glyphs: a moveto carried extra numbers")
            continue

        if letter not in "Cc":
            raise SystemExit(f"glyphs: unhandled path command {letter!r}")

        relative = letter == "c"
        if len(values) % 6:
            raise SystemExit("glyphs: a cubic run was not a multiple of six")

        for index in range(0, len(values), 6):
            group = values[index:index + 6]
            if relative:
                one = (here[0] + group[0], here[1] + group[1])
                two = (here[0] + group[2], here[1] + group[3])
                end = (here[0] + group[4], here[1] + group[5])
            else:
                one, two, end = ((group[0], group[1]), (group[2], group[3]),
                                 (group[4], group[5]))
            points.extend(cubic(here, one, two, end, steps))
            here = end

    return points


def github(height: int, colour: tuple[int, int, int]) -> Image.Image:
    """The GitHub mark, `height` pixels tall, on a transparent ground."""
    side = height * SS
    layer = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    scale = side / VIEWBOX
    scaled = [(x * scale, y * scale) for x, y in outline(GITHUB)]
    ImageDraw.Draw(layer).polygon(scaled, fill=colour + (255,))

    return layer.resize((height, height), Image.LANCZOS)


def main() -> int:
    sheet = Image.new("RGB", (560, 160), (0x22, 0x30, 0x3C))
    left = 40
    for height in (28, 44, 72):
        mark = github(height, (0xFA, 0xFB, 0xFC))
        sheet.paste(mark, (left, round((160 - height) / 2)), mark)
        left += height + 40

    out = lesson.ROOT / ".github" / "cards" / "glyph-sheet.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, "PNG", optimize=True)
    print(f"  {out.relative_to(lesson.ROOT).as_posix()}  "
          f"{sheet.width}x{sheet.height}")
    print(f"  {len(outline(GITHUB))} points in the outline")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
