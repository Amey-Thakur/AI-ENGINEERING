"""
File: tools/build_curriculum.py
Author: Amey Thakur
GitHub: https://github.com/Amey-Thakur
Repository: https://github.com/Amey-Thakur/AI-ENGINEERING
License: MIT

Description:
Writes CURRICULUM.md from the lessons themselves, and checks it is current.

The course is fifty lessons across ten phases, and the one thing a reader
wants before starting is the whole of it on one page: what each lesson does,
how long the phase takes, and where it sits. Writing that by hand means it is
wrong the first time a lesson is renamed, so it is derived instead.

Every line comes from the lesson it describes. The title is the lesson's own
heading and the sentence is the lesson's own `**You will:**` line, so the page
cannot drift from the material without this program noticing.

Usage:
    python tools/build_curriculum.py            write CURRICULUM.md
    python tools/build_curriculum.py --check    fail if it is out of date
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import lesson

PAGE = lesson.ROOT / "CURRICULUM.md"

#: The sentence every lesson uses to say what you do in it.
PROMISE = re.compile(r"^\*\*You will:\*\*\s*(.+?)\s*$", re.M)

#: The line every phase uses to say how long it takes.
LENGTH = re.compile(r"^\*\*(.+?)\*\*\s*$", re.M)

#: Markdown that means nothing once it is a table cell.
LINKED = re.compile(r"\[([^\]]*)\]\([^)]*\)")
MARKUP = re.compile(r"\*\*|__|[`*_]")

HEADER = """\
<div align="center">

# The curriculum

### Fifty lessons · Ten phases · About thirty-seven hours · Nothing installed

[![Back to the course](https://img.shields.io/badge/Back%20to-the%20course-1DE9B6.svg)](README.md)
[![Glossary](https://img.shields.io/badge/Read-the%20glossary-0969DA.svg)](GLOSSARY.md)

</div>

<br>

Every lesson on one page, in order, with what you do in each. Each one is a
directory holding a `README.md`, a `solve.py` you write, a `check.py` that
marks it, and the data it needs. Nothing is installed at any point.

**Tick them off as you go.** On [the website](https://amey-thakur.github.io/AI-ENGINEERING/curriculum/)
the boxes remember where you are, in your own browser and nowhere else.

<br>

"""

FOOTER = """
<br>

---

<div align="center">

**Fifty lessons. Ten phases. About thirty-seven hours.**

Nothing installed, no account, no API key, no GPU, and no network at any point.

[Start at phase 0](phases/00-your-machine/) &nbsp;·&nbsp;
[Read the FAQ](FAQ.md) &nbsp;·&nbsp;
[Read the glossary](GLOSSARY.md)

</div>
"""


def plain(text: str) -> str:
    """A sentence with its markdown taken off."""
    return MARKUP.sub("", LINKED.sub(r"\1", text)).strip()


def heading(path: Path) -> str:
    """The first heading in a file."""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return plain(line[2:])

    raise SystemExit(f"FAIL  {path} has no heading")


def promise(path: Path) -> str:
    """What the lesson says you will do in it."""
    found = PROMISE.search(path.read_text(encoding="utf-8"))

    if not found:
        raise SystemExit(f"FAIL  {path} has no '**You will:**' line")

    sentence = plain(found.group(1))

    return sentence[0].lower() + sentence[1:] if sentence else sentence


def length(path: Path) -> str:
    """The phase's own estimate of how long it takes."""
    body = path.read_text(encoding="utf-8")
    found = LENGTH.search(body)

    return plain(found.group(1)) if found else ""


def phases() -> list[tuple[Path, str, str, list[tuple[Path, str, str]]]]:
    collected = []

    for directory in sorted((lesson.ROOT / "phases").glob("*")):
        page = directory / "README.md"

        if not directory.is_dir() or not page.exists():
            continue

        lessons = []

        for inner in sorted(directory.glob("*")):
            inside = inner / "README.md"

            if inner.is_dir() and inside.exists():
                lessons.append((inner, heading(inside), promise(inside)))

        collected.append((directory, heading(page), length(page), lessons))

    return collected


def build() -> str:
    out = [HEADER]
    total = 0

    for directory, title, estimate, lessons in phases():
        here = directory.relative_to(lesson.ROOT).as_posix()
        out.append(f"## [{title}]({here}/)\n\n")

        if estimate:
            out.append(f"*{estimate}*\n\n")

        for inner, name, sentence in lessons:
            where = inner.relative_to(lesson.ROOT).as_posix()
            out.append(f"- [ ] **[{name}]({where}/)** &nbsp;&middot;&nbsp; "
                       f"{sentence}\n")
            total += 1

        out.append("\n<br>\n\n")

    if total != 50:
        raise SystemExit(f"FAIL  counted {total} lessons, and the course has "
                         f"50; either a lesson was added and the pages that "
                         f"say fifty need updating, or one has gone missing")

    return "".join(out).rstrip() + "\n" + FOOTER


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Write the curriculum page from the lessons.")
    parser.add_argument("--check", action="store_true",
                        help="fail if the page is out of date")
    parsed = parser.parse_args()
    wanted = build()

    if parsed.check:
        if not PAGE.exists():
            print("FAIL  CURRICULUM.md does not exist")
            print("      run: python tools/build_curriculum.py")

            return 1

        if PAGE.read_text(encoding="utf-8") != wanted:
            print("FAIL  CURRICULUM.md no longer matches the lessons")
            print("      run: python tools/build_curriculum.py")

            return 1

        count = sum(len(group[3]) for group in phases())
        print(f"  CURRICULUM.md lists all {count} lessons, and matches them")

        return 0

    PAGE.write_text(wanted, encoding="utf-8", newline="\n")
    count = sum(len(group[3]) for group in phases())
    print(f"  CURRICULUM.md   {count} lessons across "
          f"{len(phases())} phases")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
