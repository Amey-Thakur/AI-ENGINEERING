"""
Lesson 2: the check.

Run it with:  python check.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NOTES = HERE / ".work" / "notes"
NOTE = NOTES / "day-one.txt"


def fail(reason: str, fix: str) -> None:
    print(f"FAIL  {reason}")
    print(f"      {fix}")
    sys.exit(1)


def main() -> None:
    if not NOTES.is_dir():
        fail(
            "there is no .work/notes folder in this lesson",
            "make a folder inside a folder: mkdir -p .work/notes, "
            "or mkdir .work\\notes on Windows",
        )

    if not NOTE.exists():
        fail(
            ".work/notes exists but day-one.txt is not in it",
            "put a file called day-one.txt inside .work/notes",
        )

    text = NOTE.read_text(encoding="utf-8")

    if not text.strip():
        fail(
            "day-one.txt is empty",
            "write a line of text into it, then run this again",
        )

    # The file has to be in the nested folder, not beside it. This is the
    # mistake the lesson is actually about, so the check looks for it.
    stray = HERE / ".work" / "day-one.txt"
    if stray.exists() and not NOTE.exists():
        fail(
            "day-one.txt is in .work, not in .work/notes",
            "move it one folder deeper, into .work/notes",
        )

    lines = len(text.strip().splitlines())
    print(f"PASS  .work/notes/day-one.txt exists and holds {lines} line(s)")


if __name__ == "__main__":
    main()
