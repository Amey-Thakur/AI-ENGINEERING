"""
File: tools/social_preview.py
Author: Amey Thakur
GitHub: https://github.com/Amey-Thakur
Repository: https://github.com/Amey-Thakur/AI-ENGINEERING
License: MIT

Description:
Draws the card that appears when the repository is shared.

The card says what the course is and what is unusual about it, and it says it
in the fewest words that are still true. There is no illustration, because
there is nothing to illustrate that a picture would say better than the
sentence it would be sitting next to, and a decorative graphic on a technical
card reads as marketing.

The numbers on it are counted from the repository rather than typed, so the
card cannot fall out of step with the course the way a hand written one would.

Usage:
    python tools/social_preview.py
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import lesson

OUT = lesson.ROOT / ".github" / "social-preview.png"
FONTS = Path("C:/Windows/Fonts")

# GitHub renders the card at 1280 by 640.
SIZE = (1280, 640)
SCALE = 2

INK = (247, 249, 252)
DIM = (150, 160, 176)
ACCENT = (110, 231, 183)
BACKGROUND = (13, 16, 22)
RULE = (38, 44, 56)

MARGIN = 96


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / name), size * SCALE)


def counted() -> tuple[int, int]:
    """Lessons and phases, counted rather than claimed."""
    lessons = lesson.find()
    phases = {directory.parent.name for directory in lessons}
    return len(lessons), len(phases)


def draw() -> Image.Image:
    card = Image.new("RGB", (SIZE[0] * SCALE, SIZE[1] * SCALE), BACKGROUND)
    pen = ImageDraw.Draw(card)

    left = MARGIN * SCALE
    lessons, phases = counted()

    # A single accent rule, top left, instead of a logo.
    pen.rectangle([left, 92 * SCALE, left + 64 * SCALE, 98 * SCALE], fill=ACCENT)

    pen.text((left, 132 * SCALE), "AI Engineering",
             font=font("calibrib.ttf", 92), fill=INK)

    pen.text((left, 248 * SCALE),
             "Learn to build AI systems by building them.",
             font=font("calibri.ttf", 40), fill=INK)
    pen.text((left, 300 * SCALE),
             "From nothing installed, to shipping.",
             font=font("calibri.ttf", 40), fill=DIM)

    pen.line([left, 382 * SCALE, (SIZE[0] - MARGIN) * SCALE, 382 * SCALE],
             fill=RULE, width=2 * SCALE)

    # The four things that are actually unusual about it.
    claims = [
        ("0", "dependencies"),
        ("$0", "to run"),
        ("Offline", "no API key, no GPU"),
        (f"{lessons}", f"lessons across {phases} phases"),
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

    lessons, phases = counted()
    print(f"{OUT.relative_to(lesson.ROOT).as_posix()}  "
          f"{SIZE[0]}x{SIZE[1]}  {OUT.stat().st_size // 1024} KB  "
          f"({lessons} lessons, {phases} phases counted from the repository)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
