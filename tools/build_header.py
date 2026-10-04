"""
File: tools/build_header.py
Author: Amey Thakur
GitHub: https://github.com/Amey-Thakur
Repository: https://github.com/Amey-Thakur/AI-ENGINEERING
License: MIT

Description:
Builds the header plate that opens the README, with the cursor blinking.

Two files come out of one layout. The SVG is what the README shows, because a
prompt whose cursor does not blink is a picture of a terminal rather than one.
The PNG is the same plate held still, for anywhere an animation will not run.

The lettering is drawn by Pillow and embedded rather than set as SVG text. An
`<svg>` carrying a `font-family` renders in whatever face the reader's machine
happens to have, which means the plate would look different to everyone.
Embedding the type keeps it exact, and the cursor stays a vector rectangle on
top so it can still blink.

The mark is laid out from build_mark.lockup rather than drawn and then
cropped, so the cursor's position is arithmetic rather than something measured
back out of a bitmap.

Usage:
    python tools/build_header.py
"""

from __future__ import annotations

import base64
import io

from PIL import Image, ImageDraw

import build_mark
import lesson
import typeface

PNG = lesson.ROOT / "assets" / "ai-engineering-header.png"
SVG = lesson.ROOT / "assets" / "ai-engineering-header.svg"

SIZE = (1000, 260)

#: Supersampled, then resampled down, which is how the small type comes out
#: clean.
SS = 3

#: Slate plate, paper type, Python blue cursor. The same three values the mark
#: and the card use, so the repository's artwork reads as one system.
GROUND = (0x2F, 0x3E, 0x4A)
INK = (0xFA, 0xFB, 0xFC)
DIM = (0xAE, 0xBA, 0xC4)

WORDMARK = "AI Engineering"
STRAP = "Learn to build AI systems by building them"

MARK_H = 74
MARK_GAP = 26
WORDMARK_SIZE = 62
STRAP_SIZE = 21
STRAP_GAP = 26


def lettering(text: str, size: int, colour) -> Image.Image:
    """One line of type on its own transparent layer, trimmed to its ink."""
    font = typeface.of("sans", size * SS)
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    x0, y0, x1, y1 = probe.textbbox((0, 0), text, font=font)
    pad = 20 * SS
    layer = Image.new("RGBA", (x1 - x0 + pad * 2, y1 - y0 + pad * 2),
                      (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((pad - x0, pad - y0), text, font=font,
                               fill=colour + (255,))
    box = layer.getbbox()

    return layer.crop(box) if box else layer


def embedded(card: Image.Image) -> str:
    """A layer as a data URI, so the SVG carries its own lettering."""
    buffer = io.BytesIO()
    card.save(buffer, format="PNG", optimize=True)

    return ("data:image/png;base64,"
            + base64.b64encode(buffer.getvalue()).decode("ascii"))


def layout() -> dict:
    """Where everything sits on the plate, in plate coordinates."""
    shape = build_mark.lockup(MARK_H)
    word = lettering(WORDMARK, WORDMARK_SIZE, INK)
    strap = lettering(STRAP, STRAP_SIZE, DIM)

    mark_w, mark_h = shape["size"]
    word_w, word_h = word.width / SS, word.height / SS
    lockup_w = mark_w + MARK_GAP + word_w
    lockup_h = max(mark_h, word_h)
    block_h = lockup_h + STRAP_GAP + strap.height / SS
    top = (SIZE[1] - block_h) / 2
    left = (SIZE[0] - lockup_w) / 2

    return {
        "shape": shape,
        "word": word,
        "strap": strap,
        # Both sit on the lockup's own bottom edge, which is what stops the
        # letters looking as though they float beside the mark.
        "mark_at": (left, top + lockup_h - mark_h),
        "word_at": (left + mark_w + MARK_GAP, top + lockup_h - word_h),
        "strap_at": ((SIZE[0] - strap.width / SS) / 2,
                     top + lockup_h + STRAP_GAP),
    }


def main() -> int:
    plan = layout()
    shape = plan["shape"]
    mark_x, mark_y = plan["mark_at"]
    x0, y0, x1, y1 = shape["cursor"]

    # The raster plate, for anywhere an animation will not run.
    plate = Image.new("RGB", (SIZE[0] * SS, SIZE[1] * SS), GROUND)
    pen = ImageDraw.Draw(plate)

    pen.line([((mark_x + x) * SS, (mark_y + y) * SS)
              for x, y in shape["chevron"]],
             fill=INK, width=round(shape["stroke"]) * SS, joint="curve")
    pen.rounded_rectangle(
        [(mark_x + x0) * SS, (mark_y + y0) * SS,
         (mark_x + x1) * SS, (mark_y + y1) * SS],
        radius=round(shape["radius"] * SS), fill=build_mark.PYTHON)

    for layer, (x, y) in ((plan["word"], plan["word_at"]),
                          (plan["strap"], plan["strap_at"])):
        plate.paste(layer, (round(x * SS), round(y * SS)), layer)

    plate.resize(SIZE, Image.LANCZOS).save(PNG, optimize=True)

    # The vector plate, where the cursor blinks.
    points = " ".join(f"{mark_x + x:.2f},{mark_y + y:.2f}"
                      for x, y in shape["chevron"])
    word_x, word_y = plan["word_at"]
    strap_x, strap_y = plan["strap_at"]

    SVG.write_text(f"""\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SIZE[0]} {SIZE[1]}"
     width="{SIZE[0]}" height="{SIZE[1]}" role="img"
     aria-label="AI Engineering: learn to build AI systems by building them">
  <title>AI Engineering</title>
  <style>
    /* On for half the cycle, off for the other half, switching rather than
       fading, which is what a terminal cursor actually does. */
    @keyframes blink {{
      0%, 50% {{ opacity: 1; }}
      50.01%, 100% {{ opacity: 0; }}
    }}
    .cursor {{
      animation: blink {build_mark.BLINK_SECONDS}s steps(1, end) infinite;
    }}
    /* Anybody who has asked not to be shown motion gets a steady cursor. */
    @media (prefers-reduced-motion: reduce) {{
      .cursor {{ animation: none; opacity: 1; }}
    }}
  </style>
  <rect width="{SIZE[0]}" height="{SIZE[1]}" fill="{build_mark.ink(GROUND)}"/>
  <polyline points="{points}" fill="none" stroke="{build_mark.ink(INK)}"
            stroke-width="{shape['stroke']:.0f}" stroke-linecap="round"
            stroke-linejoin="round"/>
  <rect class="cursor" x="{mark_x + x0:.2f}" y="{mark_y + y0:.2f}"
        width="{x1 - x0:.2f}" height="{y1 - y0:.2f}"
        rx="{shape['radius']}" fill="{build_mark.ink(build_mark.PYTHON)}"/>
  <image x="{word_x:.2f}" y="{word_y:.2f}"
         width="{plan['word'].width / SS:.2f}"
         height="{plan['word'].height / SS:.2f}"
         href="{embedded(plan['word'])}"/>
  <image x="{strap_x:.2f}" y="{strap_y:.2f}"
         width="{plan['strap'].width / SS:.2f}"
         height="{plan['strap'].height / SS:.2f}"
         href="{embedded(plan['strap'])}"/>
</svg>
""", encoding="utf-8", newline="\n")

    for path in (PNG, SVG):
        print(f"  {path.relative_to(lesson.ROOT).as_posix():36} "
              f"{SIZE[0]}x{SIZE[1]}  {path.stat().st_size // 1024} KB")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
