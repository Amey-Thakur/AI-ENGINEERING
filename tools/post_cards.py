"""
File: tools/post_cards.py
Author: Amey Thakur
GitHub: https://github.com/Amey-Thakur
Repository: https://github.com/Amey-Thakur/AI-ENGINEERING
License: MIT

Description:
Draws one card per result, so a post about a finding carries that finding.

The social preview says what the course is. It is the right picture for the
repository and the wrong one for a post about a single measurement, and
attaching it to every post turns the pictures into furniture: by the fourth,
a reader has learned nothing from any of them.

Each card here shows the numbers of the lesson it belongs to, and the reading
of them. The bars are drawn against a visible track, so a score of nothing
reads as nothing rather than as a missing bar, and where a result only means
something against chance, chance is drawn as a line through the track.

Nothing about the identity is restated. The ground, the ink, the accent and
the mark come from social_preview and build_mark, and the footer carries the
GitHub mark from glyphs, so a card cannot drift away from the repository it
points at.

Usage:
    python tools/post_cards.py          draw every card
    python tools/post_cards.py --list   name them without drawing
"""

from __future__ import annotations

import argparse
from typing import NamedTuple

from PIL import Image, ImageDraw

import build_mark
import glyphs
import lesson
import social_preview
import typeface

#: Taller than the 2:1 preview. These are read in a feed rather than scraped
#: as an open graph image, and the extra height is what lets the chart and the
#: reading of it sit apart instead of being crammed together.
SIZE = (1280, 720)

ACCENT = social_preview.ACCENT
SLATE = next(p for p in social_preview.PALETTES if p.name == "slate")
PAPER = next(p for p in social_preview.PALETTES if p.name == "paper")

#: Where each ground is written. The dark card is the one a feed post
#: carries; the light one is for a page that is already white, such as the
#: newsletter, where a dark block would read as a hole in the page.
GROUNDS = {"slate": "", "paper": "light"}

OUT = lesson.ROOT / ".github" / "cards"

#: The mark says where it is, so the address does not have to repeat it.
REPOSITORY = "Amey-Thakur/AI-ENGINEERING"
AUTHOR = "Amey Thakur"
AVATAR = lesson.ROOT / ".github" / "assets" / "avatar.png"

#: One gutter governs every edge, so nothing on the card is aligned by eye.
MARGIN = 88
RIGHT = SIZE[0] - MARGIN

#: The signature: the mark, the name beside it, and the hairline beneath.
MARK_H = 44
MARK_GAP = 18
NAME_SIZE = 34
HEAD_TOP = 64
RULE_Y = 144

#: The lesson sits in the top right, opposite the mark. Every band on the card
#: is anchored at both gutters that way: the tag here, the values beside the
#: chart, the repository in the footer. Nothing is left hanging.
KICKER_SIZE = 23

HEADLINE_Y = 188
HEADLINE_SIZE = 56
STANDFIRST_Y = 272
STANDFIRST_SIZE = 25

#: The chart. Labels run from the gutter, the track is a fixed block, and the
#: value closes on the right gutter, so all three columns line up on every
#: card whatever the words are.
ROW_Y = 364
ROW_STEP = 66
LABEL_SIZE = 26
VALUE_SIZE = 32
TRACK_LEFT = 596
TRACK_RIGHT = 1014
TRACK_H = 18

TAKEAWAY_Y = 568
TAKEAWAY_SIZE = 26

FOOT_RULE_Y = 620
FOOT_Y = 646
FOOT_SIZE = 20
FOOT_MARK = 22
FOOT_FACE = 32

#: Bars and rules are drawn large and resampled, which is the only way a
#: rounded end this small comes out smooth.
SS = 4


class Row(NamedTuple):
    """One measurement. `fraction` is None when the number is context rather
    than something that can be compared on the same scale."""

    label: str
    value: str
    fraction: float | None = None
    accent: bool = False


class Card(NamedTuple):
    slug: str
    kicker: str
    headline: str
    rows: tuple[Row, ...]
    takeaway: str
    #: One line of setup, so the chart can be read by somebody who has not
    #: seen the lesson. Without it the numbers are a quiz.
    standfirst: str = ""
    reference: tuple[float, str] | None = None


#: Every figure is printed by the solve.py of the lesson in its kicker.
CARDS = (
    Card(
        "an-expensive-average",
        "Phase 9 · Lesson 3",
        "An expensive average",
        (
            Row("the attention head", "16 / 20", 16 / 20),
            Row("an even share, no query or key", "15 / 20", 15 / 20, True),
            Row("the subject's value silenced", "10 / 20", 10 / 20),
        ),
        "The whole mechanism was worth one answer out of twenty.",
        standfirst="Trained on 40 sentences, scored on 20 held back, with "
                   "pieces of the head removed.",
        reference=(10 / 20, "chance"),
    ),
    Card(
        "zero-of-twenty",
        "Phase 5 · Lesson 1",
        "Zero of twenty",
        (
            Row("sentences it was trained on", "217"),
            Row("words", "2019"),
            Row("answers recalled, five tries each", "0 / 20", 0.0, True),
        ),
        "Every answer was a sentence it had already read.",
        standfirst="A language model asked twenty questions about the corpus "
                   "it was trained on.",
    ),
    Card(
        "eighteen-points-for-nothing",
        "Phase 7 · Lesson 4",
        "Eighteen points for nothing",
        (
            Row("on the 48 it was chosen on", "83.3%", 0.833),
            Row("on 20 written afterwards", "65.0%", 0.650, True),
            Row("the difference", "18.3 points"),
        ),
        "The threshold was chosen on the questions it was then scored on.",
        standfirst="A confidence threshold picked on one set of questions, "
                   "then tried on fresh ones.",
    ),
    Card(
        "three-common-words",
        "Phase 8 · Lesson 4",
        "Three common words",
        (
            Row("private sentences returned, unprotected", "3 of 8", 3 / 8,
                True),
            Row("the same, with the question filtered", "2 of 8", 2 / 8),
            Row("the same, never indexed at all", "0 of 8", 0.0),
        ),
        "Only keeping the secret out of the corpus kept it out of the answers.",
        standfirst="Eight private sentences hidden in a corpus of 217, then "
                   "25 ordinary questions.",
    ),
)


def place(card, text, role, size, fill, left, top):
    patch = social_preview.rendered(text, typeface.of(role, size), fill)
    card.paste(patch, (left, top), patch)
    return patch


def place_right(card, text, role, size, fill, right, top):
    patch = social_preview.rendered(text, typeface.of(role, size), fill)
    card.paste(patch, (right - patch.width, top), patch)
    return patch


def signature(card: Image.Image, kicker: str, palette=SLATE) -> None:
    """The mark and the name at the left gutter, the lesson at the right,
    sharing one baseline."""
    mark = build_mark.cropped_to_ink(
        build_mark.prompt(MARK_H * 6, MARK_H * 5, palette.ink, ACCENT))
    mark = mark.resize(
        (round(mark.width * MARK_H / mark.height), MARK_H), Image.LANCZOS)
    card.paste(mark, (MARGIN, HEAD_TOP), mark)

    base = HEAD_TOP + mark.height
    name = social_preview.rendered(social_preview.NAME,
                                   typeface.of("black", NAME_SIZE), palette.ink)
    card.paste(name, (MARGIN + mark.width + MARK_GAP, base - name.height),
               name)

    tag = social_preview.rendered(kicker, typeface.of("mono", KICKER_SIZE),
                                  palette.dim)
    card.paste(tag, (RIGHT - tag.width, base - tag.height - 4), tag)


def portrait(height: int) -> Image.Image:
    """The author's photograph, cut to a circle with a clean edge."""
    side = height * SS
    face = Image.open(AVATAR).convert("RGBA").resize((side, side),
                                                     Image.LANCZOS)
    mask = Image.new("L", (side, side), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, side - 1, side - 1], fill=255)
    face.putalpha(mask)

    return face.resize((height, height), Image.LANCZOS)


def footer(card: Image.Image, palette=SLATE) -> None:
    """Who made it on the left, where it lives on the right, both sitting on
    one baseline so the card closes level."""
    face = portrait(FOOT_FACE)
    name = social_preview.rendered(AUTHOR, typeface.of("sans", FOOT_SIZE),
                                   palette.pale)
    mark = glyphs.github(FOOT_MARK, palette.dim)
    where = social_preview.rendered(REPOSITORY, typeface.of("sans", FOOT_SIZE),
                                    palette.dim)
    base = FOOT_Y + max(face.height, mark.height, name.height, where.height)

    card.paste(face, (MARGIN, base - face.height), face)
    card.paste(name, (MARGIN + face.width + 14, base - name.height - 4), name)

    span = mark.width + 10 + where.width
    left = RIGHT - span
    card.paste(mark, (left, base - mark.height - 3), mark)
    card.paste(where, (left + mark.width + 10, base - where.height - 4), where)


def chart(card: Image.Image, spec: Card, palette=SLATE) -> None:
    """The rows, drawn large and resampled so the ends stay round."""
    layer = Image.new("RGBA", (SIZE[0] * SS, SIZE[1] * SS), (0, 0, 0, 0))
    pen = ImageDraw.Draw(layer)
    span = TRACK_RIGHT - TRACK_LEFT
    radius = TRACK_H * SS / 2

    for index, row in enumerate(spec.rows):
        if row.fraction is None:
            continue
        top = (ROW_Y + index * ROW_STEP + 2) * SS
        pen.rounded_rectangle(
            [TRACK_LEFT * SS, top, TRACK_RIGHT * SS, top + TRACK_H * SS],
            radius=radius, fill=palette.edge + (255,))

        filled = round(span * row.fraction) * SS
        if filled > 0:
            pen.rounded_rectangle(
                [TRACK_LEFT * SS, top, TRACK_LEFT * SS + filled,
                 top + TRACK_H * SS],
                radius=radius,
                fill=(ACCENT if row.accent else palette.ink) + (255,))

    if spec.reference:
        fraction, _ = spec.reference
        at = (TRACK_LEFT + span * fraction) * SS
        first = (ROW_Y + 2) * SS
        last = (ROW_Y + (len(spec.rows) - 1) * ROW_STEP + 2 + TRACK_H) * SS
        pen.line([at, first - 14 * SS, at, last + 6 * SS],
                 fill=palette.pale + (255,), width=2 * SS)

    card.paste(layer.resize(SIZE, Image.LANCZOS), (0, 0),
               layer.resize(SIZE, Image.LANCZOS))

    for index, row in enumerate(spec.rows):
        top = ROW_Y + index * ROW_STEP
        place(card, row.label, "sans", LABEL_SIZE, palette.pale, MARGIN, top)
        place_right(card, row.value, "mono", VALUE_SIZE,
                    ACCENT if row.accent else palette.ink, RIGHT, top - 4)

    if spec.reference:
        fraction, caption = spec.reference
        at = TRACK_LEFT + span * fraction
        patch = social_preview.rendered(
            caption, typeface.of("sans", 19), palette.pale)
        card.paste(patch, (round(at - patch.width / 2), ROW_Y - 36), patch)


def draw(spec: Card, palette=SLATE) -> Image.Image:
    card = Image.new("RGB", SIZE, palette.ground)
    pen = ImageDraw.Draw(card)

    signature(card, spec.kicker, palette)
    pen.line([MARGIN, RULE_Y, RIGHT, RULE_Y], fill=palette.edge, width=2)

    head = place(card, spec.headline, "black", HEADLINE_SIZE, palette.ink,
                 MARGIN, HEADLINE_Y)
    if spec.standfirst:
        place(card, spec.standfirst, "sans", STANDFIRST_SIZE, palette.pale,
              MARGIN, STANDFIRST_Y)

    chart(card, spec, palette)

    place(card, spec.takeaway, "sans", TAKEAWAY_SIZE, palette.ink,
          MARGIN, TAKEAWAY_Y)
    pen.line([MARGIN, FOOT_RULE_Y, RIGHT, FOOT_RULE_Y], fill=palette.edge,
             width=2)
    footer(card, palette)

    if head.width > RIGHT - MARGIN:
        raise SystemExit(f"{spec.slug}: the headline overruns the gutter")

    return card


def main() -> int:
    parser = argparse.ArgumentParser(description="Draw one card per result.")
    parser.add_argument("--list", action="store_true",
                        help="name the cards without drawing them")
    arguments = parser.parse_args()

    if arguments.list:
        for spec in CARDS:
            print(f"  {spec.slug}  {spec.kicker}")
        return 0

    written = 0

    for name, folder in GROUNDS.items():
        palette = SLATE if name == "slate" else PAPER
        where = OUT / folder if folder else OUT
        where.mkdir(parents=True, exist_ok=True)

        for spec in CARDS:
            path = where / f"{spec.slug}.png"
            draw(spec, palette).save(path, "PNG", optimize=True)
            written += 1
            print(f"  {path.relative_to(lesson.ROOT).as_posix()}  "
                  f"{SIZE[0]}x{SIZE[1]}, {path.stat().st_size // 1024} KB")

    print()
    print(f"{written} card(s) on {len(GROUNDS)} grounds, "
          f"accent {build_mark.ink(ACCENT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
