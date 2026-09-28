"""
File: tools/build_mark.py
Author: Amey Thakur
GitHub: https://github.com/Amey-Thakur
Repository: https://github.com/Amey-Thakur/AI-ENGINEERING
License: MIT

Description:
Draws the mark, at the two sizes the repository uses it.

The course has one idea in its shape: it starts at a terminal nobody has
opened and ends at something shipped, and every phase is a step up from the
one before. So the mark is four ascending blocks, lightening as they rise.

Four, fixed, and not the number of anything. A mark that counted the phases
would be a number on a static image, which goes stale the moment a phase is
added, and the sibling repositories have a standing rule against exactly
that.

Two outputs, matching the sibling convention:

    assets/ai-engineering-mark.png        192x192, for the README footer
    .github/assets/mark-flat.png          74x64, for the social preview card

The flat one is drawn at its own size rather than resized down from the
square, because a 192 pixel square squashed into a 74 by 64 box shifts every
edge off the pixel grid and the blocks stop looking crisp.

The square one sits on the repository's own ground colour rather than on
transparency. Dropped into a README, a transparent mint mark is legible on
GitHub's dark theme and washes out on its light one, which is the same reason
the sibling index repository composites its logo onto a plate.

Usage:
    python tools/build_mark.py
"""

from __future__ import annotations

from PIL import Image, ImageDraw

import lesson

SQUARE = lesson.ROOT / "assets" / "ai-engineering-mark.png"
FLAT = lesson.ROOT / ".github" / "assets" / "mark-flat.png"

#: Supersampled, then resampled down, which is the only way small blocks come
#: out with clean edges.
SS = 4

#: Four blocks, fixed. See the note above about counting.
BLOCKS = 4

#: The climb, from a held-back green to the accent the rest of the repository
#: uses.
START = (0x3C, 0x6B, 0x5C)
END = (0x6E, 0xE7, 0xB7)

#: The ground the square mark is plated onto, and the radius of its corners.
GROUND = (0x0D, 0x10, 0x16)
RADIUS = 28


def blend(low: tuple[int, int, int], high: tuple[int, int, int],
          share: float) -> tuple[int, int, int]:
    return tuple(round(a + (b - a) * share) for a, b in zip(low, high))


def draw(width: int, height: int, pad_x: int, pad_y: int, gap: int,
         plated: bool = False) -> Image.Image:
    """The mark, bottom aligned inside its padding, plated or transparent."""
    card = Image.new("RGBA", (width * SS, height * SS), (0, 0, 0, 0))
    pen = ImageDraw.Draw(card)

    if plated:
        pen.rounded_rectangle(
            [0, 0, width * SS - 1, height * SS - 1],
            radius=RADIUS * SS, fill=GROUND + (255,))

    span = width - pad_x * 2
    block = (span - gap * (BLOCKS - 1)) / BLOCKS
    tallest = height - pad_y * 2
    base = height - pad_y

    for index in range(BLOCKS):
        share = (index + 1) / BLOCKS
        left = pad_x + index * (block + gap)
        top = base - tallest * share

        pen.rectangle(
            [round(left * SS), round(top * SS),
             round((left + block) * SS) - 1, round(base * SS) - 1],
            fill=blend(START, END, index / (BLOCKS - 1)) + (255,),
        )

    return card.resize((width, height), Image.LANCZOS)


def main() -> int:
    for path, size, pad_x, pad_y, gap, plated in (
        (SQUARE, (192, 192), 38, 42, 10, True),
        (FLAT, (74, 64), 0, 0, 5, False),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        mark = draw(size[0], size[1], pad_x, pad_y, gap, plated)
        mark.save(path, optimize=True)

        box = mark.getbbox()
        print(f"  {path.relative_to(lesson.ROOT).as_posix()}  "
              f"{size[0]}x{size[1]}  ink {box}  "
              f"{path.stat().st_size // 1024} KB")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
