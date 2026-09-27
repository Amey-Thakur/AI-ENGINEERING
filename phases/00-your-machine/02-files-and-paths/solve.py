"""
Lesson 2: files and paths.

Makes a folder inside a folder, puts a file in it, and works out where this
lesson sits relative to the top of the repository.

Note what it does not do: it never writes a path out by hand. Every path here
is built from where this file happens to be, which is why it works the same on
Windows, macOS and Linux, and why it would still work if the repository were
moved somewhere else entirely.

Run it with:  python solve.py
"""

from pathlib import Path

# __file__ is this file. .parent is the folder holding it. Everything else is
# derived from that, rather than typed.
HERE = Path(__file__).resolve().parent
NOTES = HERE / ".work" / "notes"
NOTE = NOTES / "day-one.txt"

LINE = "A folder inside a folder, made from a path I did not type by hand.\n"


def levels_up_to_root(start: Path) -> int:
    """How many folders above this lesson the repository root sits."""
    for distance, folder in enumerate(start.parents, start=1):
        if (folder / "phases").is_dir() and (folder / "tools").is_dir():
            return distance

    raise SystemExit("Could not find the repository root above this lesson.")


def main() -> None:
    # parents=True makes every missing folder on the way, which is what
    # mkdir -p does in the terminal. exist_ok=True means running this twice
    # is not an error.
    NOTES.mkdir(parents=True, exist_ok=True)
    NOTE.write_text(LINE, encoding="utf-8")

    distance = levels_up_to_root(HERE)
    root = HERE.parents[distance - 1]

    # as_posix keeps the forward slashes on Windows too, so that the lesson
    # prints one path rather than one path per operating system.
    relative = HERE.relative_to(root).as_posix()

    print(f"Made {NOTE.relative_to(HERE).as_posix()}")
    print(f"This lesson, written from the repository root: {relative}")
    print(f"The repository root is {distance} folders above this one")


if __name__ == "__main__":
    main()
