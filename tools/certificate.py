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
from PIL.PngImagePlugin import PngInfo

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
#: The cursor's blue, taken from the mark so the two cannot drift.
ACCENT = build_mark.CURSOR
RULE = (0xD7, 0xDD, 0xE3)

#: Written into every record, so a file from some other tool is not read as
#: one of these. tools/verify_certificate.py checks for it.
MARKER = "AI Engineering record of completion"

#: House green, from the launch kit's colour reference. The only green on the
#: document, and it appears once, on the seal.
SEAL = (0x2E, 0xA0, 0x43)

#: One centre line, two columns of equal width either side of it, which is the
#: same discipline the social card is held to.
MARGIN = 150
GUTTER = 80
COLUMN = (SIZE[0] - MARGIN * 2 - GUTTER) // 2
MIDDLE = SIZE[0] // 2

#: The lockup, in the proportions the card and the README header use.
MARK_H = 60
MARK_GAP = 20
NAME_SIZE = 54

#: Every anchor on the page, measured rather than nudged. check_layout holds
#: the document to the first and last of them.
TOP = 126
TITLE_Y = 228
RULE_Y, RULE_W = 334, 140
LEAD_Y = 372
HOLDER_Y = 414
CLAIM_Y = 548
ASIDE_Y = 594
SPLIT_Y = 652
HEADS_Y = 690
ROWS_Y = 734
ROW_STEP = 46
PHASE_STEP = 33
SEAL_Y = 952
CLOSE_Y = 1114
ACTION_Y = 1146
COMMAND_Y = 1184
COMMAND_STEP = 32
SIGN_Y = 1134
FOOT_Y = 1270

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


def lockup_on(card: Image.Image, top: int, centred: bool = False) -> int:
    """The mark and the name as one block. Returns the height it took.

    Drawn with build_mark rather than redrawn here, so the record cannot
    drift away from the mark the rest of the repository uses. The name sits
    on the mark's own bottom edge, which is what stops the letters looking as
    though they float beside it.
    """
    height = MARK_H * SCALE
    mark = build_mark.cropped_to_ink(
        build_mark.prompt(height * 6, height * 5, INK, ACCENT))
    mark = mark.resize((round(mark.width * height / mark.height), height),
                       Image.LANCZOS)
    name = rendered("AI Engineering", font("black", NAME_SIZE), INK)
    gap = MARK_GAP * SCALE
    span = mark.width + gap + name.width
    start = (round(MIDDLE * SCALE - span / 2) if centred else MARGIN * SCALE)
    base = top * SCALE + max(mark.height, name.height)
    card.paste(mark, (start, base - mark.height), mark)
    card.paste(name, (start + mark.width + gap, base - name.height), name)

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


def centred(card: Image.Image, text: str, face: ImageFont.FreeTypeFont,
            fill: tuple[int, int, int], top: int) -> Image.Image:
    """One line, centred on the page's own centre line.

    Centred on the ink it actually produced rather than on the box the
    renderer predicts, because the two differ by a pixel or two and the
    layout check measures ink.
    """
    patch = rendered(text, face, fill)
    card.paste(patch, (round(MIDDLE * SCALE - patch.width / 2), top * SCALE),
               patch)

    return patch


def seal_on(card: Image.Image, pen: ImageDraw.ImageDraw, at: tuple[int, int],
            passed: int, total: int) -> None:
    """A tick, and the one claim this document actually makes.

    Not a badge of authenticity: anybody can draw a tick. It marks that every
    check in the course passed, which is the thing the record asserts and the
    thing the verifier recomputes.
    """
    size = 46
    left, top = at
    box = [left * SCALE, top * SCALE, (left + size) * SCALE,
           (top + size) * SCALE]
    pen.ellipse(box, fill=SEAL)

    # The tick, drawn rather than set in a font, so it cannot go missing on a
    # machine whose fonts resolve differently.
    stroke = max(2, round(size * 0.11))
    points = [(left + size * 0.27, top + size * 0.52),
              (left + size * 0.43, top + size * 0.68),
              (left + size * 0.74, top + size * 0.33)]
    pen.line([(x * SCALE, y * SCALE) for x, y in points],
             fill=BACKGROUND, width=stroke * SCALE, joint="curve")

    beside = left + size + 18
    pen.text((beside * SCALE, (top + 4) * SCALE),
             f"All {total} checks passed",
             font=font("sans bold", 25), fill=INK)
    pen.text((beside * SCALE, (top + 26) * SCALE),
             "on the holder's own machine",
             font=font("serif", 21), fill=DIM)


def draw(name: str, at: str, when: str, passed: int, total: int,
         number: str) -> Image.Image:
    card = Image.new("RGB", (SIZE[0] * SCALE, SIZE[1] * SCALE), BACKGROUND)
    pen = ImageDraw.Draw(card)

    left = MARGIN * SCALE
    right = (SIZE[0] - MARGIN) * SCALE
    column_two = MARGIN + COLUMN + GUTTER

    # A hairline frame, so it reads as a document rather than a screenshot.
    pen.rectangle([56 * SCALE, 56 * SCALE, (SIZE[0] - 56) * SCALE,
                   (SIZE[1] - 56) * SCALE], outline=RULE, width=2 * SCALE)

    lockup_on(card, TOP, centred=True)

    centred(card, "Record of completion", font("serif bold", 70), INK,
            TITLE_Y)

    pen.rectangle([(MIDDLE - RULE_W // 2) * SCALE, RULE_Y * SCALE,
                   (MIDDLE + RULE_W // 2) * SCALE, (RULE_Y + 5) * SCALE],
                  fill=ACCENT)

    centred(card, "This records that", font("serif", 28), DIM, LEAD_Y)
    centred(card, name, font("serif bold", 84), ACCENT, HOLDER_Y)
    centred(card, f"ran every check in this course and passed all {total} "
                  f"of them.", font("serif", 32), INK, CLAIM_Y)
    centred(card, "It records that this happened. It does not claim anything "
                  "further.", font("serif", 24), DIM, ASIDE_Y)

    pen.line([left, SPLIT_Y * SCALE, right, SPLIT_Y * SCALE], fill=RULE,
             width=2 * SCALE)

    pen.text((left, HEADS_Y * SCALE), "THE RECORD",
             font=font("sans bold", 23), fill=DIM)
    pen.text((column_two * SCALE, HEADS_Y * SCALE), "WHAT IT COVERED",
             font=font("sans bold", 23), fill=DIM)

    # The receipt. Monospaced, because every line of it is checkable.
    rows = [
        ("lessons", f"{passed} of {total} passed"),
        ("commit", at),
        ("date", when),
        ("credential", number),
    ]
    top = ROWS_Y

    for label, value in rows:
        pen.text((left, top * SCALE), label,
                 font=font("mono", 25), fill=FAINT)
        pen.text((left + 200 * SCALE, top * SCALE), value,
                 font=font("mono", 25), fill=INK)
        top += ROW_STEP

    seal_on(card, pen, (MARGIN, SEAL_Y), passed, total)

    # What the holder actually did, which is the substance of the document.
    listed = phases()
    counts = {count for _, _, count in listed}
    even = len(counts) == 1
    row = ROWS_Y

    for index, title, count in listed:
        pen.text((column_two * SCALE, row * SCALE), index,
                 font=font("mono", 21), fill=FAINT)
        pen.text(((column_two + 38) * SCALE, (row - 3) * SCALE), title,
                 font=font("serif", 26), fill=INK)

        if not even:
            pen.text((right, row * SCALE), f"{count}",
                     font=font("mono", 21), fill=FAINT, anchor="ra")

        row += PHASE_STEP

    pen.line([left, CLOSE_Y * SCALE, right, CLOSE_Y * SCALE], fill=RULE,
             width=2 * SCALE)

    pen.text((left, ACTION_Y * SCALE), "Verify it without asking anybody",
             font=font("sans bold", 24), fill=INK)
    pen.text((left, COMMAND_Y * SCALE),
             "git clone https://github.com/Amey-Thakur/AI-ENGINEERING",
             font=font("mono", 21), fill=DIM)
    pen.text((left, (COMMAND_Y + COMMAND_STEP) * SCALE),
             f"git checkout {at[:12]} && python tools/verify_certificate.py",
             font=font("mono", 21), fill=DIM)

    # The signature, set against the right margin so it closes the column it
    # sits under rather than floating between the two.
    block = 300
    edge = SIZE[0] - MARGIN - block
    height = signature_on(card, (edge * SCALE, SIGN_Y * SCALE), block * SCALE)
    base = SIGN_Y + (height // SCALE)

    # Centred under the signature rather than pushed to the margin, so the
    # name sits square beneath the hand that wrote it.
    under = (edge + block // 2) * SCALE
    pen.text((under, (base + 6) * SCALE), "Amey Thakur",
             font=font("serif bold", 26), fill=INK, anchor="ma")
    pen.text((under, (base + 42) * SCALE), "Author, AI Engineering",
             font=font("serif", 20), fill=DIM, anchor="ma")

    centred(card, "MIT licence  \u00b7  issued by the repository, not by a "
                  "provider", font("mono", 20), FAINT, FOOT_Y)

    finished = card.resize(SIZE, Image.LANCZOS)
    check_layout(finished)

    return finished


#: A pixel darker than this counts as ink. Paper is 0xFA.
INKED = 235

#: The two margins inside the frame should agree to within this, or the page
#: reads as top-heavy however carefully each element was placed.
MARGINS_WITHIN = 24

#: How far a centred line may sit off the page's centre before it reads as
#: crooked. Two pixels, the same slack the social card allows.
OFF_CENTRE = 2.5


def check_layout(card: Image.Image) -> None:
    """Refuse to save a record that has drifted off its own geometry."""
    grey = card.convert("L")
    width, height = grey.size
    pixels = grey.load()
    inset = MARGIN - 20
    rows = [y for y in range(58 + 20, height - 58 - 20)
            if any(pixels[x, y] < INKED
                   for x in range(inset, width - inset, 2))]
    problems = []

    if not rows:
        raise SystemExit("the record came out blank")

    first, last = min(rows), max(rows)
    above = first - 58
    below = (height - 58) - last

    if abs(first - TOP) > 2:
        problems.append(f"the content starts at {first}, not {TOP}")

    if abs(above - below) > MARGINS_WITHIN:
        problems.append(f"{above}px above the content and {below}px below it, "
                        f"which is more than {MARGINS_WITHIN}px apart")

    if last < FOOT_Y:
        problems.append(f"the content ends at {last}, above the footer at "
                        f"{FOOT_Y}, so the footer did not draw")

    # Every line that is meant to be centred has to actually be centred, which
    # is the whole claim the layout makes.
    for name, top, bottom in (("the lockup", TOP, TOP + MARK_H),
                              ("the title", TITLE_Y, TITLE_Y + 80),
                              ("the accent rule", RULE_Y, RULE_Y + 5),
                              ("the holder's name", HOLDER_Y, HOLDER_Y + 100),
                              ("the footer", FOOT_Y, FOOT_Y + 26)):
        edges = [x for x in range(width)
                 if any(pixels[x, y] < INKED
                        for y in range(top, min(bottom, height - 1) + 1))]

        if not edges:
            problems.append(f"{name} did not draw")
            continue

        centre = (edges[0] + edges[-1] + 1) / 2

        if abs(centre - width / 2) > OFF_CENTRE:
            problems.append(f"{name} is centred on {centre:.1f}, "
                            f"not {width / 2}")

    # The seal is the only green on the page, and it has to be there.
    patch = card.convert("RGB").crop(
        (MARGIN - 10, SEAL_Y - 6, MARGIN + 60, SEAL_Y + 56))
    green = sum(1 for red, grn, blue in patch.getdata()
                if grn > red + 28 and grn > blue + 28)

    if green < 400:
        problems.append(f"only {green} seal pixels, so the tick is missing")

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

    # The fields go into the file as well as onto it, so the record can be
    # checked by a program rather than only read by a person.
    # tools/verify_certificate.py reads these back and recomputes the number.
    fields = PngInfo()
    fields.add_text("issued-by", MARKER)
    fields.add_text("name", name)
    fields.add_text("commit", at)
    fields.add_text("date", when)
    fields.add_text("passed", str(passed))
    fields.add_text("total", str(total))
    fields.add_text("credential", number)
    fields.add_text("verify", "python tools/verify_certificate.py "
                              + out.name)

    draw(name, at, when, passed, total, number).save(out, optimize=True,
                                                     pnginfo=fields)

    print(f"PASS  {passed} of {total} lessons")
    print(f"      {out}")
    print(f"      {SIZE[0]}x{SIZE[1]}, {out.stat().st_size // 1024} KB")
    print(f"      credential {number}, at commit {at[:12]}, dated {when}")
    print()
    print(f"      check it with:  python tools/verify_certificate.py {out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
