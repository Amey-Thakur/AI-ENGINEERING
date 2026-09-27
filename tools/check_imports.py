"""
File: tools/check_imports.py
Author: Amey Thakur
GitHub: https://github.com/Amey-Thakur
Repository: https://github.com/Amey-Thakur/AI-ENGINEERING
License: MIT

Description:
Proves that no lesson depends on anything that can be taken away.

Every import in every lesson must come from the Python standard library. Not
because third-party libraries are bad, but because a course that installs one
is a course with an expiry date: the package is renamed, the version is
yanked, the maintainer stops, the install needs a compiler that is not there,
and a person on their first day meets an error that has nothing to do with what
they came to learn.

The standard library is the one dependency that arrives with Python itself and
cannot be withdrawn by anyone. A lesson built only on it works on a laptop with
no network, on an old machine, behind a corporate proxy, and in ten years.

There is no exception to this, including in the later phases. A neural network,
an autograd engine, a tokeniser and a transformer can all be written in plain
Python over small data, and writing them is the point of the course rather than
an obstacle to it. The moment a course installs something to make that easier,
it has handed its lifespan to somebody else's release schedule.

Usage:
    python tools/check_imports.py
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import lesson

#: Modules that ship with Python. Available from 3.10 onwards.
STANDARD = set(sys.stdlib_module_names)

#: Modules a lesson may import from its own folder.
LOCAL = {"solve", "check"}


def imported_names(source: str) -> set[str]:
    """The top-level package name of every import in a file."""
    names: set[str] = set()

    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            # A relative import has no module of its own to resolve.
            if node.level == 0 and node.module:
                names.add(node.module.split(".")[0])

    return names


def main() -> int:
    outside: list[tuple[str, str]] = []
    files = 0

    for directory in lesson.find():
        for script in sorted(directory.glob("*.py")):
            files += 1
            source = script.read_text(encoding="utf-8")

            for name in sorted(imported_names(source)):
                if name in STANDARD or name in LOCAL:
                    continue

                where = script.relative_to(lesson.ROOT).as_posix()
                outside.append((where, name))

    for where, name in outside:
        print(f"FAIL  {where} imports {name}, which is not in the standard library")
        print("      a lesson may only use what arrives with Python itself, "
              "so that it still runs when that package does not")

    print()
    print(f"{files - len(outside)} of {files} lesson files import only from "
          f"the standard library")

    return 1 if outside else 0


if __name__ == "__main__":
    raise SystemExit(main())
