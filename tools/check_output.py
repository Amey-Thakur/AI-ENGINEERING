"""
File: tools/check_output.py
Author: Amey Thakur
GitHub: https://github.com/Amey-Thakur
Repository: https://github.com/Amey-Thakur/AI-ENGINEERING
License: MIT

Description:
Proves that the output printed in a lesson is the output the lesson produces.

A lesson page may show what its code prints. Every course does this, and in
every course it drifts: the code is edited, the page is not, and a reader who
runs the example gets something other than what they were shown. It is a small
dishonesty that teaches people not to trust the page in front of them.

Here the shown output is not written by hand. A lesson marks the block:

    <!-- output: solve.py -->
    ```text
    ...
    ```
    <!-- end output -->

and this tool runs solve.py and compares. On a mismatch it fails and prints the
difference. With --fix it writes the real output back into the page, which is
the only way a number is ever allowed into the prose.

The rule this places on a lesson is that its output must be the same every
time. No clock, no unseeded randomness, no machine-specific path. A lesson that
cannot meet that is a lesson printing something it should be deriving.

Usage:
    python tools/check_output.py           check every lesson
    python tools/check_output.py --fix     rewrite the blocks from real output
"""

from __future__ import annotations

import argparse
import difflib
import io
import re
import subprocess
import sys
from pathlib import Path

import lesson

ROOT = lesson.ROOT
PHASES = lesson.PHASES

BLOCK = re.compile(
    r"(?P<open><!-- output: (?P<script>[\w./-]+) -->\r?\n```(?:\w+)?\r?\n)"
    r"(?P<body>.*?)"
    r"(?P<close>```\r?\n<!-- end output -->)",
    re.DOTALL,
)


def produced(directory: Path, script: str, env: dict[str, str]) -> str:
    """What the lesson actually prints, normalised for line endings only."""
    finished = subprocess.run(
        [sys.executable, script],
        cwd=directory,
        env=env,
        capture_output=True,
        text=True,
        timeout=lesson.TIMEOUT_SECONDS,
    )

    if finished.returncode != 0:
        raise SystemExit(
            f"{lesson.name(directory)}: {script} exited {finished.returncode}\n"
            f"{finished.stdout}{finished.stderr}"
        )

    return finished.stdout.replace("\r\n", "\n").strip("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check shown output against real output.")
    parser.add_argument("--fix", action="store_true", help="rewrite the blocks")
    arguments = parser.parse_args()

    env = lesson.environment()
    pages = sorted(PHASES.glob("*/*/README.md"))
    checked = 0
    stale: list[str] = []

    for page in pages:
        text = io.open(page, encoding="utf-8", newline="").read()
        newline = "\r\n" if "\r\n" in text else "\n"
        rewritten = text

        for match in BLOCK.finditer(text):
            checked += 1
            directory = page.parent
            name = lesson.name(directory)

            shown = match.group("body").replace("\r\n", "\n").strip("\n")
            real = produced(directory, match.group("script"), env)

            if shown == real:
                continue

            if arguments.fix:
                body = real.replace("\n", newline) + newline
                rewritten = rewritten.replace(
                    match.group(0),
                    match.group("open") + body + match.group("close"),
                    1,
                )
                print(f"fixed {name}")
                continue

            stale.append(name)
            print(f"FAIL  {name}: the page shows output the code does not produce")
            for line in difflib.unified_diff(
                shown.splitlines(),
                real.splitlines(),
                fromfile="shown on the page",
                tofile="printed by the code",
                lineterm="",
            ):
                print("      " + line)

        if arguments.fix and rewritten != text:
            io.open(page, "w", encoding="utf-8", newline="").write(rewritten)

    print()
    print(f"{checked - len(stale)} of {checked} output blocks match")
    return 1 if stale else 0


if __name__ == "__main__":
    raise SystemExit(main())
