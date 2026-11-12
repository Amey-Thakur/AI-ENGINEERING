"""
File: tools/phase_posters.py
Author: Amey Thakur
GitHub: https://github.com/Amey-Thakur
Repository: https://github.com/Amey-Thakur/AI-ENGINEERING
License: MIT

Description:
Draws one poster per phase, so a phase can be shown rather than described.

The curriculum page lists fifty lessons, which is the right form for somebody
already reading and the wrong one for somebody deciding whether to start. A
poster carries one phase: what it is called, how long it takes, and the five
lessons in the order they are met.

Nothing here is written by hand. The phase title, the estimate and every
lesson title are read from the lessons themselves through build_curriculum,
which is the same source the curriculum page is built from, so a poster cannot
say a lesson exists after it has been renamed or removed.

The identity, the footer and the gutters come from post_cards, so a poster and
a result card are visibly the same family.

Usage:
    python tools/phase_posters.py          draw every poster
    python tools/phase_posters.py --list   name them without drawing
"""

from __future__ import annotations

import argparse

from PIL import Image, ImageDraw

import build_curriculum
import lesson
import post_cards
import social_preview
import typeface

SIZE = post_cards.SIZE
SLATE = post_cards.SLATE
ACCENT = post_cards.ACCENT
MARGIN = post_cards.MARGIN
RIGHT = post_cards.RIGHT

OUT = lesson.ROOT / ".github" / "posters"

HEADLINE_Y = 188
HEADLINE_SIZE = 56
#: The longest phase title is "Shipping: cost, latency, failure, safety", which
#: does not fit at the full size. Rather than set it smaller everywhere, the
#: size steps down until it fits, so most posters keep the larger title.
HEADLINE_FLOOR = 38

STANDFIRST_Y = 272
STANDFIRST_SIZE = 25

LESSON_Y = 344
LESSON_STEP = 56
NUMBER_SIZE = 23
LESSON_SIZE = 27
#: Where the lesson title starts, so every title lines up whatever its number.
LESSON_INDENT = 52


def split(title: str) -> tuple[str, str]:
    """"1. The thing a bigram cannot see" as its number and its words."""
    number, _, rest = title.partition(". ")
    return (number, rest) if rest else ("", title)


def fitted(text: str, role: str, start: int, floor: int, width: int):
    """The largest size at or below `start` whose ink fits inside `width`."""
    for size in range(start, floor - 1, -2):
        font = typeface.of(role, size)
        box = social_preview.ink_box(text, font)
        if box[2] - box[0] <= width:
            return font
    return typeface.of(role, floor)


def draw(number: str, title: str, estimate: str, lessons) -> Image.Image:
    card = Image.new("RGB", SIZE, SLATE.ground)
    pen = ImageDraw.Draw(card)

    post_cards.signature(card, f"Phase {number}")
    pen.line([MARGIN, post_cards.RULE_Y, RIGHT, post_cards.RULE_Y],
             fill=SLATE.edge, width=2)

    # The phase number is already in the corner, so the headline is the name.
    _, _, name = title.partition(". ")
    font = fitted(name or title, "black", HEADLINE_SIZE, HEADLINE_FLOOR,
                  RIGHT - MARGIN)
    head = social_preview.rendered(name or title, font, SLATE.ink)
    card.paste(head, (MARGIN, HEADLINE_Y), head)

    post_cards.place(card, estimate, "sans", STANDFIRST_SIZE, SLATE.pale,
                     MARGIN, STANDFIRST_Y)

    for index, (_, lesson_title, _) in enumerate(lessons):
        count, words = split(lesson_title)
        top = LESSON_Y + index * LESSON_STEP
        post_cards.place(card, count, "mono", NUMBER_SIZE, ACCENT,
                         MARGIN, top + 4)
        post_cards.place(card, words, "sans", LESSON_SIZE, SLATE.ink,
                         MARGIN + LESSON_INDENT, top)

    pen.line([MARGIN, post_cards.FOOT_RULE_Y, RIGHT, post_cards.FOOT_RULE_Y],
             fill=SLATE.edge, width=2)
    post_cards.footer(card)

    return card


def main() -> int:
    parser = argparse.ArgumentParser(description="Draw one poster per phase.")
    parser.add_argument("--list", action="store_true",
                        help="name the posters without drawing them")
    arguments = parser.parse_args()

    phases = build_curriculum.phases()

    if arguments.list:
        for directory, title, _, lessons in phases:
            print(f"  {directory.name}  {title}  ({len(lessons)} lessons)")
        return 0

    OUT.mkdir(parents=True, exist_ok=True)
    drawn = 0

    for directory, title, estimate, lessons in phases:
        number = directory.name.split("-")[0]
        path = OUT / f"phase-{number}.png"
        draw(number.lstrip("0") or "0", title, estimate, lessons).save(
            path, "PNG", optimize=True)
        drawn += 1
        print(f"  {path.relative_to(lesson.ROOT).as_posix()}  "
              f"{SIZE[0]}x{SIZE[1]}, {path.stat().st_size // 1024} KB")

    print()
    print(f"{drawn} poster(s), one per phase, titles read from the lessons")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
