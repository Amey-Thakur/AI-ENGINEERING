"""
File: tools/social_preview.py
Author: Amey Thakur
GitHub: https://github.com/Amey-Thakur
Repository: https://github.com/Amey-Thakur/AI-ENGINEERING
License: MIT

Description:
Draws the card that appears when the repository is shared.

The card says what the course is and what is unusual about it, in the fewest
words that are still true. The one graphic on it is not decoration: it is the
course, drawn to scale. Nine steps, one per phase, each rising by the number
of lessons that phase actually contains, so the shape of the climb is the
shape of the material. If a phase is added the staircase grows a step, and if
a lesson is deleted a step gets shorter.

Every number and every measurement on the card is counted from the repository
rather than typed, so the card cannot fall out of step with the course the way
a hand written one would.

Usage:
    python tools/social_preview.py
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import lesson

OUT = lesson.ROOT / ".github" / "social-preview.png"
FONTS = Path("C:/Windows/Fonts")

# GitHub renders the card at 1280 by 640. Everything is drawn at twice that
# and resampled down, which is the cheapest way to get clean edges on text.
SIZE = (1280, 640)
SCALE = 2

INK = (247, 249, 252)
DIM = (150, 160, 176)
FAINT = (92, 102, 120)
ACCENT = (110, 231, 183)
BACKGROUND = (13, 16, 22)
RULE = (38, 44, 56)

MARGIN = 96

# The staircase occupies the space the title does not. The left edge is set
# from the measured width of the longest line beside it, not by eye.
CHART_LEFT = 720
CHART_RIGHT = SIZE[0] - MARGIN
CHART_BASE = 318
CHART_TALLEST = 180
CHART_GAP = 9


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / name), size * SCALE)


def counted() -> list[tuple[str, int]]:
    """Every phase and how many lessons it holds, counted rather than claimed."""
    tally: dict[str, int] = {}

    for directory in lesson.find():
        tally[directory.parent.name] = tally.get(directory.parent.name, 0) + 1

    return sorted(tally.items())


def blend(start: tuple[int, int, int], end: tuple[int, int, int],
          share: float) -> tuple[int, int, int]:
    """A colour part of the way between two others."""
    return tuple(round(a + (b - a) * share) for a, b in zip(start, end))


def staircase(pen: ImageDraw.ImageDraw, phases: list[tuple[str, int]]) -> None:
    """The course drawn to scale: one step per phase, rising by its lessons."""
    steps = len(phases)
    total = sum(count for _, count in phases)
    span = (CHART_RIGHT - CHART_LEFT) * SCALE
    width = (span - CHART_GAP * SCALE * (steps - 1)) / steps
    climbed = 0

    for index, (name, count) in enumerate(phases):
        climbed += count
        height = CHART_TALLEST * SCALE * climbed / total
        left = CHART_LEFT * SCALE + index * (width + CHART_GAP * SCALE)

        pen.rectangle(
            [left, CHART_BASE * SCALE - height, left + width,
             CHART_BASE * SCALE],
            fill=blend(FAINT, ACCENT, index / (steps - 1)),
        )

        # The phase number, under its own step.
        pen.text((left + width / 2, (CHART_BASE + 13) * SCALE),
                 name.split("-")[0].lstrip("0") or "0",
                 font=font("consola.ttf", 20), fill=FAINT, anchor="ma")

    pen.line([CHART_LEFT * SCALE, CHART_BASE * SCALE, CHART_RIGHT * SCALE,
              CHART_BASE * SCALE], fill=RULE, width=2 * SCALE)


def draw() -> Image.Image:
    card = Image.new("RGB", (SIZE[0] * SCALE, SIZE[1] * SCALE), BACKGROUND)
    pen = ImageDraw.Draw(card)

    left = MARGIN * SCALE
    phases = counted()
    lessons = sum(count for _, count in phases)

    # A single accent rule, top left, instead of a logo.
    pen.rectangle([left, 92 * SCALE, left + 64 * SCALE, 98 * SCALE],
                  fill=ACCENT)

    pen.text((left, 128 * SCALE), "AI Engineering",
             font=font("calibrib.ttf", 92), fill=INK)

    pen.text((left, 248 * SCALE),
             "Learn to build AI systems by building them.",
             font=font("calibri.ttf", 34), fill=INK)
    pen.text((left, 294 * SCALE),
             "From nothing installed, to shipping.",
             font=font("calibri.ttf", 34), fill=DIM)

    # Names the axis, which is what a chart needs and what a caption is for.
    pen.text((CHART_RIGHT * SCALE, 90 * SCALE), "cumulative lessons",
             font=font("calibri.ttf", 22), fill=FAINT, anchor="ra")

    staircase(pen, phases)

    pen.line([left, 382 * SCALE, (SIZE[0] - MARGIN) * SCALE, 382 * SCALE],
             fill=RULE, width=2 * SCALE)

    # The four things that are actually unusual about it.
    claims = [
        ("0", "dependencies"),
        ("$0", "to run"),
        ("Offline", "no API key, no GPU"),
        (f"{lessons}", f"lessons across {len(phases)} phases"),
    ]

    column = left
    for value, caption in claims:
        pen.text((column, 424 * SCALE), value,
                 font=font("calibrib.ttf", 44), fill=ACCENT)
        pen.text((column, 480 * SCALE), caption,
                 font=font("calibri.ttf", 26), fill=DIM)
        column += 262 * SCALE

    pen.text((left, 556 * SCALE), "github.com/Amey-Thakur/AI-ENGINEERING",
             font=font("consola.ttf", 26), fill=DIM)

    return card.resize(SIZE, Image.LANCZOS)


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    draw().save(OUT, optimize=True)

    phases = counted()
    lessons = sum(count for _, count in phases)
    print(f"{OUT.relative_to(lesson.ROOT).as_posix()}  "
          f"{SIZE[0]}x{SIZE[1]}  {OUT.stat().st_size // 1024} KB  "
          f"({lessons} lessons across {len(phases)} phases, counted from the "
          f"repository)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
