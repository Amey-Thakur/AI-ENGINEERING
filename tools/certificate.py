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
It does, all forty-five lessons, and it exits without writing a file if a
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


def font(role: str, size: int) -> ImageFont.FreeTypeFont:
    """A font for a role, at the size the card is drawn at."""
    return typeface.of(role, size * SCALE)


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

    pen.rectangle([left, 150 * SCALE, left + 96 * SCALE, 158 * SCALE],
                  fill=ACCENT)

    pen.text((left, 186 * SCALE), "A I   E N G I N E E R I N G",
             font=font("sans bold", 26), fill=DIM)

    pen.text((left, 240 * SCALE), "Record of completion",
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

    pen.text((left, 1188 * SCALE), "github.com/Amey-Thakur/AI-ENGINEERING",
             font=font("mono", 24), fill=FAINT)

    # The signature, bottom right, above its own rule.
    block = 400
    edge = SIZE[0] - MARGIN - block
    height = signature_on(card, (edge * SCALE, 960 * SCALE), block * SCALE)

    base = 960 + (height // SCALE) + 4
    pen.text((edge * SCALE, (base + 16) * SCALE), "Amey Thakur",
             font=font("serif bold", 30), fill=INK)
    pen.text((edge * SCALE, (base + 60) * SCALE),
             "Author, AI Engineering", font=font("serif", 24), fill=DIM)

    return card.resize(SIZE, Image.LANCZOS)


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
