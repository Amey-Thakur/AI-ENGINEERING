"""
Lesson 1: the check.

A check is a small program that looks at what you produced and says whether it
is right. It is written to be read: if it fails, the reason it prints should be
enough to fix the problem without asking anyone.

Run it with:  python check.py
"""

import sys
from pathlib import Path

HERE = Path(__file__).parent
LISTING = HERE / ".work" / "here.txt"

MINIMUM_PYTHON = (3, 10)


def fail(reason: str, fix: str) -> None:
    print(f"FAIL  {reason}")
    print(f"      {fix}")
    sys.exit(1)


def main() -> None:
    # 1. The Python you are running this with.
    if sys.version_info < MINIMUM_PYTHON:
        running = ".".join(str(part) for part in sys.version_info[:3])
        wanted = ".".join(str(part) for part in MINIMUM_PYTHON)
        fail(
            f"this is Python {running}, and the course needs {wanted} or higher",
            "install a newer Python, then open a new terminal so it is found",
        )

    # 2. The file the lesson asked for.
    if not LISTING.exists():
        fail(
            "there is no .work/here.txt in this lesson folder",
            "run the listing command with > .work/here.txt, or run: python solve.py",
        )

    text = LISTING.read_text(encoding="utf-8")

    if not text.strip():
        fail(
            ".work/here.txt is empty",
            "the command printed nothing, so check you ran it inside this folder",
        )

    names = [line.strip() for line in text.splitlines() if line.strip()]

    # 3. The file holds a listing of this folder, not of somewhere else.
    if "README.md" not in names:
        fail(
            "README.md is not in the listing, so it was taken from another folder",
            "move into this lesson folder with cd, then run the command again",
        )

    version = ".".join(str(part) for part in sys.version_info[:3])
    print(f"PASS  Python {version}, and .work/here.txt lists {len(names)} entries")


if __name__ == "__main__":
    main()
