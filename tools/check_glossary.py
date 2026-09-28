"""
File: tools/check_glossary.py
Author: Amey Thakur
GitHub: https://github.com/Amey-Thakur
Repository: https://github.com/Amey-Thakur/AI-ENGINEERING
License: MIT

Description:
Proves that the glossary still points at the course.

GLOSSARY.md maps the plain words the lessons use onto the words the field
uses, and every entry links to the lesson where the idea is built. Those links
are the whole value of the file: a definition is worth little next to the
thing you implemented, and worth a great deal beside it.

Links rot silently. A lesson gets renamed, a phase is renumbered, and the
glossary keeps rendering perfectly while sending readers to a 404 that only
they will see. So every link is resolved against the filesystem here, and
every lesson is checked for a mention, because a phase that gains a lesson
should gain a row.

Usage:
    python tools/check_glossary.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import lesson

GLOSSARY = lesson.ROOT / "GLOSSARY.md"

#: A markdown link whose target is inside phases/.
LINK = re.compile(r"\[[^\]]+\]\((phases/[^)#]+)\)")

#: Lessons a glossary is not expected to have a row for. Phase 0 teaches a
#: terminal and a text editor, and two of its lessons introduce no idea that
#: needs translating into anything.
UNTRANSLATED = {
    "phases/00-your-machine/03-your-first-program",
}


def main() -> int:
    if not GLOSSARY.exists():
        print(f"FAIL  there is no {GLOSSARY.name}")
        print("      the glossary is linked from the README, so it has to be "
              "there")
        return 1

    text = GLOSSARY.read_text(encoding="utf-8")
    targets = [match.group(1) for match in LINK.finditer(text)]

    if not targets:
        print(f"FAIL  {GLOSSARY.name} links to no lesson at all")
        print("      every entry names the lesson where the idea is built, "
              "which is the point of the file")
        return 1

    broken = []

    for target in sorted(set(targets)):
        if not (lesson.ROOT / target.rstrip("/")).is_dir():
            broken.append(target)

    for target in broken:
        print(f"FAIL  {GLOSSARY.name} links to {target}, which does not exist")
        print("      a lesson was renamed or renumbered, so the row needs the "
              "new path")

    linked = {target.rstrip("/") for target in targets}
    missing = []

    for directory in lesson.find():
        name = lesson.name(directory)

        if name not in linked and name not in UNTRANSLATED:
            missing.append(name)

    for name in missing:
        print(f"FAIL  {name} has no row in {GLOSSARY.name}")
        print("      a new lesson introduces something worth naming, or it "
              "belongs in UNTRANSLATED with a reason")

    if broken or missing:
        return 1

    lessons = len(lesson.find())
    print(f"{len(linked)} of {lessons} lessons are named in "
          f"{GLOSSARY.name}, and every link resolves")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
