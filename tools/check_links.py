"""
File: tools/check_links.py
Author: Amey Thakur
GitHub: https://github.com/Amey-Thakur
Repository: https://github.com/Amey-Thakur/AI-ENGINEERING
License: MIT

Description:
Proves that every link inside the course still points at something.

A course is a web of cross references. Phase 7 sends the reader back to phase
1 for error bars, the glossary names the lesson where an idea is built, and the
front page links the lesson behind every result it quotes. Rename a lesson,
renumber a phase, or retitle a heading, and some of those quietly stop working.
The reader finds out, not the author.

Two kinds of target are checked, and both are checked against the repository as
it is on disk:

    a path        phases/09-attention-and-the-block/ must exist
    an anchor     README.md#the-course must match a real heading

Headings are turned into anchors the way GitHub does it, so the anchor a reader
clicks is the anchor that is checked. Repeated headings get the -1, -2 suffixes
GitHub gives them.

What is deliberately not checked is the network. No http link is fetched. The
course's own promise is that it runs with the network closed, and a guard that
fails when somebody else's server is down would teach the reader to ignore it.
An unreachable external link is a real problem, but it is not this program's,
and it cannot be fixed by the person who sees it fail.

Markdown inside a fenced block or a code span is not a link. The course prints
Python that contains `{"calculate": calculate}[picked](question)`, which reads
exactly like a link and is not one, so code is removed before anything is
looked for.

Usage:
    python tools/check_links.py        check every page
"""

from __future__ import annotations

import io
import re
from pathlib import Path

import lesson

ROOT = lesson.ROOT

#: Directories holding generated or borrowed files. The site under docs/ is
#: built from these pages by build_docs.py, so checking it would report every
#: fault twice and in the generated spelling rather than the written one.
SKIP = {"docs", "_site", ".git", ".work", "__pycache__"}

#: A fenced block, either flavour, and an inline code span. Removed before any
#: link is looked for. The fence pattern is first so that a span inside a block
#: is already gone by the time spans are considered.
FENCE = re.compile(r"^(?P<fence>```|~~~).*?^(?P=fence)[ \t]*$", re.DOTALL | re.MULTILINE)
SPAN = re.compile(r"`+[^`]*`+")

#: An inline markdown link or image, and the src or href of an HTML tag. The
#: title that may follow a target inside the brackets is not part of it.
MARKDOWN = re.compile(r"!?\[(?P<text>[^\]]*)\]\((?P<target>[^)\s]+)(?:\s+\"[^\"]*\")?\)")
ATTRIBUTE = re.compile(r"(?:src|href)=\"(?P<target>[^\"]+)\"")

#: A setext or atx heading. Only atx is used in this repository, but a page
#: that grows a setext heading should not silently stop having its anchors
#: checked.
ATX = re.compile(r"^(?P<hashes>#{1,6})[ \t]+(?P<text>.+?)[ \t]*#*[ \t]*$", re.MULTILINE)

#: Targets that leave the repository. Nothing is fetched, for the reason in the
#: description above.
ELSEWHERE = ("http://", "https://", "mailto:", "tel:", "data:", "ftp://")

#: What GitHub drops from a heading before it becomes an anchor: anything that
#: is not a letter, a digit, a space, a hyphen or an underscore.
UNSLUGGABLE = re.compile(r"[^\w \-]", re.UNICODE)


def readable(page: Path) -> str:
    """The page with its code removed, so code cannot look like a link."""
    text = io.open(page, encoding="utf-8", newline="").read().replace("\r\n", "\n")
    text = FENCE.sub(lambda match: "\n" * match.group(0).count("\n"), text)
    return SPAN.sub("", text)


def plain(heading: str) -> str:
    """The text a reader sees, with the markdown that decorated it removed."""
    heading = MARKDOWN.sub(lambda match: match.group("text"), heading)
    heading = re.sub(r"<[^>]+>", "", heading)
    heading = heading.replace("`", "")
    heading = re.sub(r"\*{1,3}", "", heading)
    return heading.strip()


def slug(heading: str) -> str:
    """A heading turned into an anchor the way GitHub turns it into one."""
    text = plain(heading).lower()
    text = UNSLUGGABLE.sub("", text)
    return text.replace(" ", "-")


def anchors(page: Path) -> set[str]:
    """Every anchor the page offers: its headings, plus any id it declares."""
    text = readable(page)
    found: set[str] = set()
    seen: dict[str, int] = {}

    for match in ATX.finditer(text):
        base = slug(match.group("text"))
        if not base:
            continue
        count = seen.get(base, 0)
        seen[base] = count + 1
        found.add(base if count == 0 else f"{base}-{count}")

    # A heading written as HTML, or an explicit anchor, is a real target too.
    found.update(re.findall(r"(?:id|name)=\"([^\"]+)\"", text))
    return found


def pages() -> list[Path]:
    """Every written page, in a stable order, with generated trees left out."""
    return sorted(
        page for page in ROOT.rglob("*.md")
        if not SKIP.intersection(page.relative_to(ROOT).parts)
    )


def main() -> int:
    written = pages()
    cache: dict[Path, set[str]] = {}
    checked = 0
    elsewhere = 0
    broken: list[str] = []

    for page in written:
        here = page.relative_to(ROOT).as_posix()
        text = readable(page)
        targets = [match.group("target") for match in MARKDOWN.finditer(text)]
        targets += [match.group("target") for match in ATTRIBUTE.finditer(text)]

        for target in targets:
            if target.startswith(ELSEWHERE) or target.startswith("//"):
                elsewhere += 1
                continue

            checked += 1
            path, _, fragment = target.partition("#")

            if path:
                landing = (page.parent / path).resolve()
                if not landing.exists():
                    broken.append(here)
                    print(f"FAIL  {here} links to {target}")
                    print("      nothing is at that path, so a lesson was "
                          "renamed, renumbered or moved")
                    continue
            else:
                landing = page

            if not fragment:
                continue

            if landing.is_dir() or landing.suffix != ".md":
                # A directory link carries the reader to its README, whose
                # headings are not this program's business to guess at.
                continue

            if landing not in cache:
                cache[landing] = anchors(landing)

            if fragment not in cache[landing]:
                broken.append(here)
                print(f"FAIL  {here} links to {target}")
                print(f"      {landing.relative_to(ROOT).as_posix()} has no "
                      f"heading that makes the anchor #{fragment}")

    print()
    print(f"{checked - len(broken)} of {checked} links inside the repository "
          f"resolve, across {len(written)} pages")
    print(f"{elsewhere} link(s) leave it and are not fetched")
    return 1 if broken else 0


if __name__ == "__main__":
    raise SystemExit(main())
