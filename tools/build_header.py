"""
File: tools/build_header.py
Author: Amey Thakur
GitHub: https://github.com/Amey-Thakur
Repository: https://github.com/Amey-Thakur/AI-ENGINEERING
License: MIT

Description:
Builds the header plate that opens the README.

The mark and the wordmark are composited onto a slate plate. Dropped into a
README on transparency they would read on GitHub's dark theme and wash out on
its light one, so the plate gives one image that is correct in both, which is
the only reason this script exists and the same reason the sibling index
repository plates its logo.

The mark is drawn here by build_mark.prompt rather than loaded from a file,
because the plate needs it in paper rather than in slate and a third asset on
disk would be a third thing to keep in step.

The lockup and the strapline are centred as a single block rather than
separately, so the plate stays balanced if either line changes length.

Usage:
    python tools/build_header.py
"""

from __future__ import annotations

from PIL import Image, ImageDraw

import build_mark
import lesson
import typeface

OUT = lesson.ROOT / "assets" / "ai-engineering-header.png"

SIZE = (1000, 260)

#: Supersampled, then resampled down, which is how the small type comes out
#: clean.
SS = 3

#: Slate plate, paper type, Python blue cursor. The same three values the
#: mark and the card use, so the repository's artwork reads as one system.
GROUND = (0x2F, 0x3E, 0x4A)
INK = (0xFA, 0xFB, 0xFC)
DIM = (0xAE, 0xBA, 0xC4)

WORDMARK = "AI Engineering"
STRAP = "Learn to build AI systems by building them"

MARK_W, MARK_H = 92, 80
MARK_GAP = 24
WORDMARK_SIZE = 62
STRAP_SIZE = 21
STRAP_GAP = 26


def main() -> int:
    plate = Image.new("RGB", (SIZE[0] * SS, SIZE[1] * SS), GROUND)
    pen = ImageDraw.Draw(plate)

    word = typeface.of("sans", WORDMARK_SIZE * SS)
    strap = typeface.of("sans", STRAP_SIZE * SS)

    wx0, wy0, wx1, wy1 = pen.textbbox((0, 0), WORDMARK, font=word)
    word_w, word_h = wx1 - wx0, wy1 - wy0
    strap_w = pen.textlength(STRAP, font=strap)

    mark = build_mark.cropped_to_ink(
        build_mark.prompt(MARK_W * SS * 2, MARK_H * SS * 2, INK,
                          build_mark.PYTHON))
    mark = mark.resize(
        (round(mark.width * MARK_H * SS / mark.height), MARK_H * SS),
        Image.LANCZOS)

    lockup_w = mark.width + MARK_GAP * SS + word_w
    lockup_h = max(MARK_H * SS, word_h)
    block_h = lockup_h + STRAP_GAP * SS + STRAP_SIZE * SS
    top = (SIZE[1] * SS - block_h) / 2
    left = (SIZE[0] * SS - lockup_w) / 2

    plate.paste(mark, (round(left), round(top + lockup_h - mark.height)),
                mark)

    # The wordmark sits on the mark's own bottom edge, which is what stops the
    # letters looking as though they are floating beside it.
    pen.text((round(left + mark.width + MARK_GAP * SS - wx0),
              round(top + lockup_h - word_h - wy0)),
             WORDMARK, font=word, fill=INK)

    pen.text(((SIZE[0] * SS - strap_w) / 2,
              top + lockup_h + STRAP_GAP * SS),
             STRAP, font=strap, fill=DIM)

    plate = plate.resize(SIZE, Image.LANCZOS)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    plate.save(OUT, optimize=True)

    print(f"  {OUT.relative_to(lesson.ROOT).as_posix()}  "
          f"{SIZE[0]}x{SIZE[1]}  {OUT.stat().st_size // 1024} KB")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
