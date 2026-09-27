"""
Lesson 3: the check.

It runs your program and reads what it prints, rather than comparing your file
to an answer. Your wording can differ. The number cannot.

Run it with:  python check.py
"""

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROGRAM = HERE / ".work" / "hello.py"

EXPECTED_LENGTH = "14"


def fail(reason: str, fix: str) -> None:
    print(f"FAIL  {reason}")
    print(f"      {fix}")
    sys.exit(1)


def main() -> None:
    if not PROGRAM.exists():
        fail(
            "there is no .work/hello.py",
            "write the two line program into .work/hello.py, or run: python solve.py",
        )

    finished = subprocess.run(
        [sys.executable, PROGRAM.name],
        cwd=PROGRAM.parent,
        capture_output=True,
        text=True,
        timeout=30,
    )

    if finished.returncode != 0:
        last = finished.stderr.strip().splitlines()[-1] if finished.stderr.strip() else ""
        fail(
            f"hello.py stopped with an error: {last}",
            "read the last line of the error first: it says what went wrong",
        )

    printed = finished.stdout.strip()

    if not printed:
        fail(
            "hello.py ran but printed nothing",
            "the work happened silently: wrap the result in print(...)",
        )

    if EXPECTED_LENGTH not in printed:
        fail(
            f"hello.py printed {printed!r}, which does not contain the length {EXPECTED_LENGTH}",
            "use len(name) rather than counting the characters by hand",
        )

    print(f"PASS  hello.py ran and printed: {printed}")


if __name__ == "__main__":
    main()
