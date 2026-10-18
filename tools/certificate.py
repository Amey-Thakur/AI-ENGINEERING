"""
File: tools/certificate.py
Author: Amey Thakur
GitHub: https://github.com/Amey-Thakur
Repository: https://github.com/Amey-Thakur/AI-ENGINEERING
License: MIT

Description:
Issues a record of completion, and refuses to issue one otherwise.

Most course certificates assert something about the holder that nobody can
check. This one asserts something narrow and checkable instead: that on a
given date, at a given commit, every check in this course ran and passed on
the holder's own machine. It prints the command to re-verify that on its own
face, so a reader does not have to take it on trust any more than a reader of
the lessons does.

Which means the tool has to actually run the course before it draws anything.
It does, all fifty lessons, and it exits without writing a file if a
single one fails. There is no flag to skip that.

The credential number is a hash of the name, the commit and the score, so the
same three inputs always produce the same number and a changed one produces a
different number. It is an identifier, not a secret.

Usage:
    python tools/certificate.py --name "Your Name"
    python tools/certificate.py --name "Your Name" --date 2026-09-28
    python tools/certificate.py --name "Your Name" --out ~/Desktop/record.png
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import build_mark
import lesson
import typeface

SIGNATURE = lesson.ROOT / ".github" / "assets" / "signature.png"

# A4 landscape at about 170 dots per inch, so it prints without looking soft.
SIZE = (2000, 1414)
SCALE = 2

#: The same paper, slate and Python blue the mark, the header and the card
#: use, so a record printed from this repository looks like it came from it.
BACKGROUND = (0xFA, 0xFB, 0xFC)
INK = (0x22, 0x30, 0x3C)
DIM = (0x5B, 0x6B, 0x78)
FAINT = (0x87, 0x94, 0xA0)
ACCENT = (0x37, 0x76, 0xAB)
RULE = (0xD7, 0xDD, 0xE3)

MARGIN = 160

#: The lockup, in the same proportions the card and the README header use:
#: the mark, a gap, then the name set on the mark's own bottom edge.
MARK_H = 64
MARK_GAP = 22
NAME_SIZE = 58


def font(role: str, size: int) -> ImageFont.FreeTypeFont:
    """A font for a role, at the size the card is drawn at."""
    return typeface.of(role, size * SCALE)



def rendered(text: str, face: ImageFont.FreeTypeFont,
             fill: tuple[int, int, int]) -> Image.Image:
    """The text on its own layer, trimmed to the ink it actually produced."""
    layer = Image.new("RGBA", (len(text) * face.size + 200, face.size * 3),
                      (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((100, face.size), text, font=face,
                               fill=fill + (255,))
    box = layer.getbbox()

    return layer.crop(box) if box else layer


def lockup_on(card: Image.Image, at: tuple[int, int]) -> int:
    """The mark and the name as one block. Returns the height it took.

    Drawn with build_mark rather than redrawn here, so the record cannot
    drift away from the mark the rest of the repository uses.
    """
    height = MARK_H * SCALE
    mark = build_mark.cropped_to_ink(
        build_mark.prompt(height * 6, height * 5, INK, ACCENT))
    mark = mark.resize((round(mark.width * height / mark.height), height),
                       Image.LANCZOS)
    name = rendered("AI Engineering", font("black", NAME_SIZE), INK)
    base = at[1] + max(mark.height, name.height)
    card.paste(mark, (at[0], base - mark.height), mark)
    card.paste(name, (at[0] + mark.width + MARK_GAP * SCALE,
                      base - name.height), name)

    return max(mark.height, name.height)


def commit() -> str:
    """The commit the course was at when the checks were run."""
    try:
        found = subprocess.run(
            ["git", "-C", str(lesson.ROOT), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return "unknown"

    return found.stdout.strip() if found.returncode == 0 else "unknown"


def phases() -> list[tuple[str, str, int]]:
    """Each phase as (number, title, lessons), titled as its README titles it."""
    counted: dict[str, int] = {}

    for directory in lesson.find():
        counted[directory.parent.name] = counted.get(
            directory.parent.name, 0) + 1

    found = []

    for name in sorted(counted):
        heading = (lesson.PHASES / name / "README.md")
        title = name.split("-", 1)[-1].replace("-", " ")

        if heading.exists():
            first = heading.read_text(encoding="utf-8").splitlines()[0]
            # "# Phase 8. Shipping: cost, latency, failure, safety"
            if ". " in first:
                title = first.split(". ", 1)[1].strip()

        found.append((name.split("-")[0].lstrip("0") or "0", title,
                      counted[name]))

    return found


def credential(name: str, at: str, passed: int, total: int) -> str:
    """Reproducible from its inputs, and different if any of them differ."""
    seed = f"{name}|{at}|{passed}/{total}".encode("utf-8")
    digest = hashlib.sha256(seed).hexdigest()[:12].upper()

    return "-".join(digest[start:start + 4] for start in (0, 4, 8))


def verify() -> tuple[int, int, list[str]]:
    """Runs the whole course. Returns (passed, total, names that failed)."""
    lessons = lesson.find()
    environment = lesson.environment()
    failed = []

    for index, directory in enumerate(lessons, start=1):
        name = lesson.name(directory)
        print(f"  [{index:2}/{len(lessons)}] {name}", flush=True)

        missing = lesson.missing(directory)

        if missing:
            failed.append(f"{name} is missing {', '.join(missing)}")
            continue

        solved, output, _ = lesson.run(directory, "solve.py", environment)

        if not solved:
            failed.append(f"{name} solve.py did not run")
            continue

        checked, output, _ = lesson.run(directory, "check.py", environment)

        if not checked:
            first = output.splitlines()[0] if output else "no output"
            failed.append(f"{name} {first}")

    return len(lessons) - len(failed), len(lessons), failed


def signature_on(card: Image.Image, at: tuple[int, int], width: int) -> int:
    """Places the signature and returns the height it took."""
    if not SIGNATURE.exists():
        return 0

    mark = Image.open(SIGNATURE).convert("RGBA")
    box = mark.getbbox()

    if box:
        mark = mark.crop(box)

    height = round(width * mark.height / mark.width)
    card.paste(mark.resize((width, height), Image.LANCZOS), at, mark.resize(
        (width, height), Image.LANCZOS))

    return height


def draw(name: str, at: str, when: str, passed: int, total: int,
         number: str) -> Image.Image:
    card = Image.new("RGB", (SIZE[0] * SCALE, SIZE[1] * SCALE), BACKGROUND)
    pen = ImageDraw.Draw(card)

    left = MARGIN * SCALE
    right = (SIZE[0] - MARGIN) * SCALE

    # A hairline frame, so it reads as a document rather than a screenshot.
    pen.rectangle([56 * SCALE, 56 * SCALE, (SIZE[0] - 56) * SCALE,
                   (SIZE[1] - 56) * SCALE], outline=RULE, width=2 * SCALE)

    lockup_on(card, (left, 148 * SCALE))

    pen.text((left, 266 * SCALE), "Record of completion",
             font=font("serif bold", 82), fill=INK)

    pen.line([left, 396 * SCALE, right, 396 * SCALE], fill=RULE,
             width=2 * SCALE)

    pen.text((left, 436 * SCALE), "This records that",
             font=font("serif", 32), fill=DIM)

    pen.text((left, 490 * SCALE), name, font=font("serif bold", 78),
             fill=ACCENT)

    pen.text((left, 612 * SCALE),
             f"ran every check in this course and passed all {total} of them.",
             font=font("serif", 34), fill=INK)
    pen.text((left, 662 * SCALE),
             "It records that this happened. It does not claim anything "
             "further.",
             font=font("serif", 28), fill=DIM)

    # The receipt. Monospaced, because every line of it is checkable.
    rows = [
        ("lessons", f"{passed} of {total} passed"),
        ("commit", at),
        ("date", when),
        ("credential", number),
    ]

    top = 760
    for label, value in rows:
        pen.text((left, top * SCALE), label,
                 font=font("mono", 26), fill=FAINT)
        pen.text((left + 240 * SCALE, top * SCALE), value,
                 font=font("mono", 26), fill=INK)
        top += 44

    pen.line([left, 966 * SCALE, left + 760 * SCALE, 966 * SCALE], fill=RULE,
             width=2 * SCALE)

    # What the holder actually did, which is the substance of the document.
    column = 1060
    listed = phases()
    counts = {count for _, _, count in listed}

    # A column of identical numbers says nothing, so say it once instead. If
    # the phases ever differ in length the column comes back on its own.
    even = len(counts) == 1
    heading = "What this covered"

    if even:
        heading += f", {len(listed)} phases of {counts.pop()} lessons"

    pen.text((column * SCALE, 436 * SCALE), heading,
             font=font("sans bold", 26), fill=DIM)

    row = 492
    for number, title, count in listed:
        pen.text((column * SCALE, row * SCALE), number,
                 font=font("mono", 22), fill=FAINT)
        pen.text(((column + 40) * SCALE, (row - 3) * SCALE), title,
                 font=font("serif", 27), fill=INK)

        if not even:
            pen.text((right, row * SCALE), f"{count}",
                     font=font("mono", 22), fill=FAINT, anchor="ra")

        row += 42

    pen.text((left, 1000 * SCALE), "Verify it without asking anybody",
             font=font("sans bold", 26), fill=INK)
    pen.text((left, 1042 * SCALE),
             f"git clone https://github.com/Amey-Thakur/AI-ENGINEERING && "
             f"cd AI-ENGINEERING",
             font=font("mono", 20), fill=DIM)
    pen.text((left, 1074 * SCALE),
             f"git checkout {at[:12]} && python tools/run_lessons.py",
             font=font("mono", 20), fill=DIM)

    # A footer band, so the document closes on a line rather than trailing
    # off. Its bottom margin matches the space above the lockup.
    pen.line([left, 1196 * SCALE, right, 1196 * SCALE], fill=RULE,
             width=2 * SCALE)
    pen.text((left, 1226 * SCALE), "github.com/Amey-Thakur/AI-ENGINEERING",
             font=font("mono", 24), fill=FAINT)
    pen.text((right, 1226 * SCALE),
             "MIT licence  ·  issued by the repository, not by a provider",
             font=font("mono", 24), fill=FAINT, anchor="ra")

    # The signature, bottom right, above its own rule.
    block = 400
    edge = SIZE[0] - MARGIN - block
    height = signature_on(card, (edge * SCALE, 960 * SCALE), block * SCALE)

    base = 960 + (height // SCALE) + 4
    pen.text((edge * SCALE, (base + 16) * SCALE), "Amey Thakur",
             font=font("serif bold", 30), fill=INK)
    pen.text((edge * SCALE, (base + 60) * SCALE),
             "Author, AI Engineering", font=font("serif", 24), fill=DIM)

    finished = card.resize(SIZE, Image.LANCZOS)
    check_layout(finished)

    return finished



#: Where the content begins and ends inside the frame, measured on the drawn
#: pixels. The record is a document somebody prints, so these are asserted
#: rather than assumed.
FRAME_INSET = 56
CONTENT_TOP = 148
FOOTER_BASELINE = 1226

#: The two margins inside the frame should agree to within this, or the page
#: reads as top-heavy however carefully each element was placed.
MARGINS_WITHIN = 24

#: A pixel darker than this counts as ink. Paper is 0xFA.
INKED = 235


def check_layout(card: Image.Image) -> None:
    """Refuse to save a record that has drifted off its geometry."""
    grey = card.convert("L")
    width, height = grey.size
    pixels = grey.load()
    # Inside the frame on all four sides: its own lines are not content, and
    # the two vertical ones would otherwise mark every row as inked.
    inset = FRAME_INSET + 60
    rows = [y for y in range(FRAME_INSET + 20, height - FRAME_INSET - 20)
            if any(pixels[x, y] < INKED
                   for x in range(inset, width - inset, 2))]
    problems = []

    if not rows:
        raise SystemExit("the record came out blank")

    first, last = min(rows), max(rows)
    inner_top = FRAME_INSET + 2
    inner_bottom = height - FRAME_INSET - 2

    if abs(first - CONTENT_TOP) > 2:
        problems.append(f"the content starts at {first}, not {CONTENT_TOP}")

    above = first - inner_top
    below = inner_bottom - last

    if abs(above - below) > MARGINS_WITHIN:
        problems.append(f"{above}px above the content and {below}px below it, "
                        f"which is more than {MARGINS_WITHIN}px apart")

    if last < FOOTER_BASELINE:
        problems.append(f"the content ends at {last}, above the footer at "
                        f"{FOOTER_BASELINE}, so the footer did not draw")

    # The lockup is the only blue in the top band, and it has to be there or
    # the document does not look as though this repository issued it.
    patch = card.convert("RGB").crop(
        (FRAME_INSET, CONTENT_TOP - 8, width // 2, CONTENT_TOP + 140))
    blue = sum(1 for red, green, blue_ in patch.getdata()
               if blue_ > red + 24 and blue_ > 90)

    if blue < 200:
        problems.append(f"only {blue} accent pixels in the lockup band, so "
                        f"the mark is missing or has lost its cursor")

    if problems:
        raise SystemExit("the record drifted off its geometry:\n  "
                         + "\n  ".join(problems))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Issue a record of completion, after running the course.")
    parser.add_argument("--name", required=True,
                        help="the name to put on it, as you want it written")
    parser.add_argument("--date", default=None,
                        help="YYYY-MM-DD, defaulting to today")
    parser.add_argument("--out", default=None,
                        help="where to write the png")
    parsed = parser.parse_args()

    name = " ".join(parsed.name.split())

    if not name:
        print("FAIL  --name is empty")
        return 1

    when = parsed.date or datetime.date.today().isoformat()

    try:
        datetime.date.fromisoformat(when)
    except ValueError:
        print(f"FAIL  {when!r} is not a date in YYYY-MM-DD form")
        return 1

    print(f"Running the course before issuing anything. This takes a couple "
          f"of minutes.")
    passed, total, failed = verify()
    print()

    if failed:
        print(f"FAIL  {len(failed)} of {total} lessons did not pass, so there "
              f"is nothing to certify")

        for note in failed[:5]:
            print(f"      {note}")

        if len(failed) > 5:
            print(f"      and {len(failed) - 5} more")

        print("      run `python tools/progress.py` to see where you are")
        return 1

    at = commit()
    number = credential(name, at, passed, total)
    out = Path(parsed.out) if parsed.out else (
        lesson.ROOT / ".work" / f"record-of-completion.png")
    out.parent.mkdir(parents=True, exist_ok=True)

    draw(name, at, when, passed, total, number).save(out, optimize=True)

    print(f"PASS  {passed} of {total} lessons")
    print(f"      {out}")
    print(f"      {SIZE[0]}x{SIZE[1]}, {out.stat().st_size // 1024} KB")
    print(f"      credential {number}, at commit {at[:12]}, dated {when}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
