"""Build the AmeyARC thinking cloud as a family of assets.

The mark on the site today is the thought balloon character, set in whichever
emoji font the reader's machine happens to have. That is fine on a web page and
wrong everywhere else: it renders differently on every system, it cannot be
recoloured, it cannot be animated, and on a machine with no emoji font it does
not render at all.

So the mark is rebuilt as geometry. The cloud is five overlapping circles, and
rather than shipping five circles the union outline is traced once and written
out as a single path, which is what lets it take a stroke, a gradient or an
animation later without seams showing where the lobes overlap.

Produces: the static mark, an animated mark that breathes and thinks, a GIF of
the same for places that will not take SVG, and a lockup with the wordmark.
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw

import signature_final as trace

OUT = Path(__file__).parent / "brand"
OUT.mkdir(exist_ok=True)

# The cloud, in a 120 by 104 box.
LOBES = [(60, 36, 25), (36, 47, 20), (85, 47, 20), (49, 60, 19), (73, 60, 19)]
BUBBLES = [(33, 82, 7.5), (21, 94, 4.5)]

BOX = (120, 104)
TRACE_SCALE = 10

TILE = (11, 13, 18)          # the dark square the mark has always sat on
CLOUD = (238, 242, 247)      # near white, as the emoji renders it


def cloud_path() -> str:
    """The union outline of the five lobes, as one path."""
    width, height = BOX[0] * TRACE_SCALE, BOX[1] * TRACE_SCALE

    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    pen = ImageDraw.Draw(canvas)

    for x, y, radius in LOBES:
        x, y, radius = x * TRACE_SCALE, y * TRACE_SCALE, radius * TRACE_SCALE
        pen.ellipse([x - radius, y - radius, x + radius, y + radius],
                    fill=(0, 0, 0, 255))

    loops = [trace.simplify(loop, tolerance=1.4)
             for loop in trace.contours(trace.mask(canvas))]
    loops = [loop for loop in loops if len(loop) > 6]

    if len(loops) != 1:
        raise SystemExit(f"expected one outline, traced {len(loops)}")

    points = [(x / TRACE_SCALE, y / TRACE_SCALE) for x, y in loops[0]]
    head = f"M{points[0][0]:.2f},{points[0][1]:.2f}"
    rest = "".join(f"L{x:.2f},{y:.2f}" for x, y in points[1:])

    return head + rest + "Z"


def static_mark(path: str) -> str:
    bubbles = "\n".join(
        f'        <circle cx="{x}" cy="{y}" r="{r}" />' for x, y, r in BUBBLES)

    return f"""<!--
  File: ameyarc-mark.svg
  Purpose: The AmeyARC thinking cloud.
  Description: The mark as geometry rather than as an emoji character, so it
    renders identically everywhere and can be recoloured. The cloud is one
    traced outline; the two bubbles are what make it a thought rather than
    speech. Inherits currentColor.
  License: MIT
  Author: Amey Thakur (https://github.com/Amey-Thakur)
-->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {BOX[0]} {BOX[1]}"
    role="img" aria-label="AmeyARC">
    <g fill="currentColor">
        <path d="{path}" />
{bubbles}
    </g>
</svg>
"""


def animated_mark(path: str) -> str:
    """The cloud breathing, with the two bubbles rising in turn."""
    return f"""<!--
  File: ameyarc-thinking.svg
  Purpose: The AmeyARC mark, thinking.
  Description: The cloud breathes, slowly, and the two bubbles rise and fade in
    turn beneath it, which is what a thought looks like forming. The motion is
    CSS inside the file, so it needs nothing around it, and it stops for anyone
    who has asked their system to reduce motion.
  License: MIT
  Author: Amey Thakur (https://github.com/Amey-Thakur)
-->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {BOX[0]} {BOX[1]}"
    role="img" aria-label="AmeyARC, thinking">
    <style>
        .cloud {{
            transform-origin: 60px 47px;
            animation: breathe 4s ease-in-out infinite;
        }}

        .bubble {{ animation: rise 4s ease-in-out infinite; }}
        .bubble--near {{ transform-origin: 33px 82px; animation-delay: -0.56s; }}
        .bubble--far {{ transform-origin: 21px 94px; animation-delay: -1.12s; }}

        @keyframes breathe {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
        }}

        @keyframes rise {{
            0%, 100% {{ transform: translateY(0) scale(0.74); opacity: 0.22; }}
            50% {{ transform: translateY(-5px) scale(1.10); opacity: 1; }}
        }}

        /* Motion is a courtesy, not a requirement. */
        @media (prefers-reduced-motion: reduce) {{
            .cloud, .bubble {{ animation: none; }}
        }}
    </style>
    <g fill="currentColor">
        <path class="cloud" d="{path}" />
        <circle class="bubble bubble--near" cx="{BUBBLES[0][0]}"
            cy="{BUBBLES[0][1]}" r="{BUBBLES[0][2]}" />
        <circle class="bubble bubble--far" cx="{BUBBLES[1][0]}"
            cy="{BUBBLES[1][1]}" r="{BUBBLES[1][2]}" />
    </g>
</svg>
"""


def rounded_tile(size: int, radius_fraction=0.22) -> Image.Image:
    tile = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(tile).rounded_rectangle(
        [0, 0, size - 1, size - 1],
        radius=int(size * radius_fraction),
        fill=(*TILE, 255),
    )
    return tile


def frame(size: int, phase: float, supersample: int = 3) -> Image.Image:
    """One frame of the loop, at the given point in the cycle."""
    big = size * supersample
    sheet = rounded_tile(big).resize((big, big), Image.LANCZOS)
    pen = ImageDraw.Draw(sheet)

    # The mark sits in the middle of the square with room around it.
    inset = big * 0.16
    span = big - inset * 2
    unit = span / BOX[0]

    def place(x, y, radius, scale=1.0, origin=None):
        ox, oy = origin if origin else (x, y)
        x = ox + (x - ox) * scale
        y = oy + (y - oy) * scale
        return (inset + x * unit, inset + y * unit, radius * unit * scale)

    breathe = 1 + 0.05 * math.sin(phase * 2 * math.pi)

    for x, y, radius in LOBES:
        cx, cy, r = place(x, y, radius, breathe, origin=(60, 47))
        pen.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*CLOUD, 255))

    for index, (x, y, radius) in enumerate(BUBBLES):
        # Each bubble runs the same cycle, a little behind the one before it,
        # and travels upward as it brightens: a thought rising into the cloud.
        local = (phase - 0.14 * (index + 1)) % 1.0
        wave = math.sin(local * 2 * math.pi)

        pulse = 0.74 + 0.36 * (0.5 + 0.5 * wave)
        fade = 0.22 + 0.78 * (0.5 + 0.5 * wave)
        lift = -5.0 * (0.5 + 0.5 * wave)

        cx, cy, r = place(x, y + lift, radius, pulse)
        colour = tuple(int(TILE[c] + (CLOUD[c] - TILE[c]) * fade) for c in range(3))
        pen.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*colour, 255))

    return sheet.resize((size, size), Image.LANCZOS)


def build_gif(size: int, frames: int, name: str) -> None:
    pictures = [frame(size, index / frames).convert("P", palette=Image.ADAPTIVE,
                                                    colors=128)
                for index in range(frames)]

    pictures[0].save(
        OUT / name,
        save_all=True,
        append_images=pictures[1:],
        duration=40,
        loop=0,
        optimize=True,
    )

    print(f"{name:32} {(OUT / name).stat().st_size // 1024} KB, {frames} frames")


def lockup(path: str) -> str:
    """The mark beside the name, for a header or a footer."""
    return f"""<!--
  File: ameyarc-lockup.svg
  Purpose: The AmeyARC mark beside the name.
  Description: The mark and the wordmark at a fixed relationship, so the two
    are never set at different sizes or spacings by hand. Inherits currentColor.
  License: MIT
  Author: Amey Thakur (https://github.com/Amey-Thakur)
-->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 104"
    role="img" aria-label="AmeyARC">
    <g fill="currentColor">
        <path d="{path}" />
        <circle cx="{BUBBLES[0][0]}" cy="{BUBBLES[0][1]}" r="{BUBBLES[0][2]}" />
        <circle cx="{BUBBLES[1][0]}" cy="{BUBBLES[1][1]}" r="{BUBBLES[1][2]}" />
        <text x="146" y="62" font-family="Outfit, Inter, system-ui, sans-serif"
            font-size="46" font-weight="600" letter-spacing="-0.5">AmeyARC</text>
    </g>
</svg>
"""


def main() -> None:
    path = cloud_path()
    print(f"cloud outline: {len(path)} characters")

    written = {
        "ameyarc-mark.svg": static_mark(path),
        "ameyarc-thinking.svg": animated_mark(path),
        "ameyarc-lockup.svg": lockup(path),
    }

    for name, content in written.items():
        (OUT / name).write_text(content, encoding="utf-8")
        print(f"{name:32} {(OUT / name).stat().st_size // 1024} KB")

    # A still, at the size the site already uses for its icon.
    frame(512, 0.0).convert("RGB").save(OUT / "ameyarc-mark-512.png")
    print(f"{'ameyarc-mark-512.png':32} "
          f"{(OUT / 'ameyarc-mark-512.png').stat().st_size // 1024} KB")

    build_gif(240, 50, "ameyarc-thinking.gif")
    build_gif(96, 50, "ameyarc-thinking-small.gif")


if __name__ == "__main__":
    main()
