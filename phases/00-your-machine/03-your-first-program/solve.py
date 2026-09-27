"""
Lesson 3: your first program.

Writes the two line program from the lesson, then runs it the way you would
from a terminal, and reports what it printed.

Run it with:  python solve.py
"""

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROGRAM = HERE / ".work" / "hello.py"

SOURCE = '''name = "AI Engineering"
print(f"{name} has {len(name)} characters")
'''


def main() -> None:
    PROGRAM.parent.mkdir(parents=True, exist_ok=True)
    PROGRAM.write_text(SOURCE, encoding="utf-8")

    # sys.executable is the Python running this file. Using it rather than the
    # word "python" means the program is run by the same interpreter, even on a
    # machine where the word python points somewhere else.
    finished = subprocess.run(
        [sys.executable, PROGRAM.name],
        cwd=PROGRAM.parent,
        capture_output=True,
        text=True,
    )

    if finished.returncode != 0:
        raise SystemExit(f"hello.py failed:\n{finished.stderr}")

    print(f"Wrote {PROGRAM.relative_to(HERE).as_posix()}")
    print(f"Running it printed: {finished.stdout.strip()}")


if __name__ == "__main__":
    main()
