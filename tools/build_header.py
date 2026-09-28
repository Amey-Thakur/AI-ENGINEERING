"""
File: tools/build_header.py
Author: Amey Thakur
GitHub: https://github.com/Amey-Thakur
Repository: https://github.com/Amey-Thakur/AI-ENGINEERING
License: MIT

Description:
Builds the header plate that opens the README.

The mark is mint on nothing. Dropped straight into a README it reads on
GitHub's dark theme and washes out on its light one, so the plate composites
the mark and the wordmark onto the repository's own ground. One image, correct
in both themes, which is the only reason this script exists.

The lockup and the strapline are centred as a single block rather than
separately, so the plate stays balanced if either line changes length.

Usage:
    python tools/build_header.py
"""

from __future__ import annotations

from PIL import Image, ImageDraw

import lesson
import typeface

OUT = lesson.ROOT / "assets" / "ai-engineering-header.png"
MARK = lesson.ROOT / ".github" / "assets" / "mark-flat.png"

SIZE = (1000, 260)

#: Supersampled, then resampled down, which is how the small type comes out
#: clean.
SS = 3

GROUND = (0x0D, 0x10, 0x16)
INK = (0xF7, 0xF9, 0xFC)
DIM = (0x8A, 0x94, 0xA4)

WORDMARK = "AI Engineering"
STRAP = "Learn to build AI systems by building them"

MARK_W, MARK_H = 92, 80
MARK_GAP = 24
WORDMARK_SIZE = 62
STRAP_SIZE = 21
STRAP_GAP = 26


def main() -> int:
    if not MARK.exists():
        print(f"FAIL  {MARK.relative_to(lesson.ROOT).as_posix()} is missing")
        print("      run `python tools/build_mark.py` first")
        return 1

    plate = Image.new("RGB", (SIZE[0] * SS, SIZE[1] * SS), GROUND)
    pen = ImageDraw.Draw(plate)

    word = typeface.of("sans", WORDMARK_SIZE * SS)
    strap = typeface.of("sans", STRAP_SIZE * SS)

    wx0, wy0, wx1, wy1 = pen.textbbox((0, 0), WORDMARK, font=word)
    word_w, word_h = wx1 - wx0, wy1 - wy0
    strap_w = pen.textlength(STRAP, font=strap)

    lockup_w = MARK_W * SS + MARK_GAP * SS + word_w
    lockup_h = max(MARK_H * SS, word_h)
    block_h = lockup_h + STRAP_GAP * SS + STRAP_SIZE * SS
    top = (SIZE[1] * SS - block_h) / 2
    left = (SIZE[0] * SS - lockup_w) / 2

    mark = Image.open(MARK).convert("RGBA").resize(
        (MARK_W * SS, MARK_H * SS), Image.LANCZOS)
    plate.paste(mark, (round(left), round(top + (lockup_h - MARK_H * SS) / 2)),
                mark)

    # The wordmark sits on the mark's own bottom edge, which is what stops the
    # letters looking as though they are floating beside it.
    pen.text((round(left + MARK_W * SS + MARK_GAP * SS - wx0),
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
