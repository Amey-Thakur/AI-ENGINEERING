"""
Lesson 5: the check.

Run it with:  python check.py
"""

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRACTICE = HERE / ".work" / "practice"


def fail(reason: str, fix: str) -> None:
    print(f"FAIL  {reason}")
    print(f"      {fix}")
    sys.exit(1)


def git(*arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *arguments],
        cwd=PRACTICE,
        capture_output=True,
        text=True,
        timeout=60,
    )


def main() -> None:
    if not PRACTICE.is_dir():
        fail(
            "there is no .work/practice folder",
            "make it, move into it, and run: git init",
        )

    if not (PRACTICE / ".git").is_dir():
        fail(
            ".work/practice exists but is not a repository",
            "run git init inside it",
        )

    log = git("log", "--oneline")

    if log.returncode != 0:
        message = log.stderr.strip().splitlines()[-1] if log.stderr.strip() else ""
        fail(
            f"the repository has no commits yet: {message}",
            "stage a file with git add, then record it with git commit -m \"First commit\"",
        )

    commits = [line for line in log.stdout.splitlines() if line.strip()]

    if not commits:
        fail(
            "the repository exists but nothing has been committed",
            "git add a file, then git commit -m \"First commit\"",
        )

    tracked = git("ls-files")
    files = [line for line in tracked.stdout.splitlines() if line.strip()]

    if not files:
        fail(
            "there is a commit but no file in it",
            "check that you ran git add on the file before committing",
        )

    print(f"PASS  {len(commits)} commit recording {len(files)} file: {', '.join(files)}")


if __name__ == "__main__":
    main()
