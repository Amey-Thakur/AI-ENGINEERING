"""
Lesson 1: the terminal.

This is the worked solution. It runs the same command the lesson asked you to
type, choosing the one that belongs to the system it finds itself on, and puts
the result where the lesson said to put it.

It runs the real command rather than doing the same job in Python, on purpose.
That way the commands printed in the lesson are tested on Windows, macOS and
Linux every time this course is built, and a command that stops working is
found here rather than by somebody on their first day.

Run it with:  python solve.py
"""

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
WORK = HERE / ".work"
LISTING = WORK / "here.txt"


def listing_command() -> list[str]:
    """The plain listing command for this system, as printed in the lesson."""
    if sys.platform == "win32":
        # cmd is the program that understands dir; /b asks for bare names only.
        return ["cmd", "/c", "dir", "/b"]

    # -1 means one name per line, which is what makes the output a list.
    return ["ls", "-1"]


def main() -> None:
    WORK.mkdir(exist_ok=True)

    command = listing_command()
    finished = subprocess.run(command, cwd=HERE, capture_output=True, text=True)

    if finished.returncode != 0:
        raise SystemExit(
            f"{' '.join(command)} failed with {finished.returncode}:\n{finished.stderr}"
        )

    # This is what the > character does in the terminal: the text a command
    # would have printed goes into a file instead.
    LISTING.write_text(finished.stdout, encoding="utf-8")

    names = [line.strip() for line in finished.stdout.splitlines() if line.strip()]

    print(f"Listing written to {LISTING.relative_to(HERE).as_posix()}")
    print(f"README.md present in the listing: {'yes' if 'README.md' in names else 'no'}")


if __name__ == "__main__":
    main()
