"""
Lesson 5: git and your copy.

Makes a small repository, stages a file, commits it, and reads the log back.

The identity is passed with -c rather than written into your global settings,
so running this does not change how git behaves anywhere else on your machine.
Signing is turned off for the same reason: if you sign your commits, this
practice repository should not try to.

Run it with:  python solve.py
"""

import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRACTICE = HERE / ".work" / "practice"
NOTE = PRACTICE / "notes.txt"

IDENTITY = [
    "-c", "user.name=Course Learner",
    "-c", "user.email=learner@example.com",
    "-c", "commit.gpgsign=false",
]


def git(*arguments: str) -> str:
    """Runs one git command inside the practice repository."""
    finished = subprocess.run(
        ["git", *IDENTITY, *arguments],
        cwd=PRACTICE,
        capture_output=True,
        text=True,
    )

    if finished.returncode != 0:
        # git says some of its most useful things on stdout rather than stderr,
        # "nothing to commit" among them, so both are reported here.
        raise SystemExit(
            f"git {' '.join(arguments)} failed:\n"
            f"{finished.stdout.strip()}\n{finished.stderr.strip()}".strip()
        )

    return finished.stdout.strip()


def main() -> None:
    # Start from nothing every time. A worked solution that only works on a
    # folder it has not already touched is not a worked solution: run it twice
    # and the second run would stop at "nothing to commit".
    if PRACTICE.exists():
        shutil.rmtree(PRACTICE, ignore_errors=True)

    PRACTICE.mkdir(parents=True, exist_ok=True)

    # -b main names the first branch. Older versions of git do not accept it,
    # so fall back rather than failing on somebody's machine.
    try:
        git("init", "-q", "-b", "main")
    except SystemExit:
        git("init", "-q")

    NOTE.write_text("A recorded moment.\n", encoding="utf-8")

    git("add", NOTE.name)
    git("commit", "-q", "-m", "First commit")

    log = git("log", "--oneline")
    commits = len([line for line in log.splitlines() if line.strip()])

    print(f"Made a repository in {PRACTICE.relative_to(HERE).as_posix()}")
    print(f"Staged and committed {NOTE.name}")
    print(f"The log shows {commits} commit")


if __name__ == "__main__":
    main()
