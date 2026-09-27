"""
File: tools/lesson.py
Author: Amey Thakur
GitHub: https://github.com/Amey-Thakur
Repository: https://github.com/Amey-Thakur/AI-ENGINEERING
License: MIT

Description:
What a lesson is, in one place.

Three small facts are needed by more than one tool: where the lessons are, how
to start a child process that cannot reach the network, and how to run one file
inside a lesson and collect what it said. They live here so that the runner and
the output checker cannot drift apart on the definition, and so that changing
the contract means changing one file.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PHASES = ROOT / "phases"
GUARD = ROOT / "tools" / "guard"

#: The three files every lesson holds.
REQUIRED = ("README.md", "solve.py", "check.py")

#: A lesson that has not finished in this long is one a learner abandons.
TIMEOUT_SECONDS = 120


def find(selector: str | None = None) -> list[Path]:
    """Every lesson directory in course order, narrowed by an optional path."""
    found = sorted(path.parent for path in PHASES.glob("*/*/check.py"))

    if not selector:
        return found

    wanted = (ROOT / selector).resolve()
    return [lesson for lesson in found if wanted in (lesson, *lesson.parents)]


def missing(lesson: Path) -> list[str]:
    """Which of the three required files a lesson does not have."""
    return [name for name in REQUIRED if not (lesson / name).exists()]


def environment() -> dict[str, str]:
    """A child environment with the network guard already on the path."""
    env = dict(os.environ)
    existing = env.get("PYTHONPATH", "")

    env["PYTHONPATH"] = str(GUARD) + (os.pathsep + existing if existing else "")
    env["PYTHONUNBUFFERED"] = "1"

    return env


def run(lesson: Path, script: str, env: dict[str, str]) -> tuple[bool, str, float]:
    """Runs one script inside a lesson. Returns (ok, output, seconds)."""
    started = time.perf_counter()

    try:
        finished = subprocess.run(
            [sys.executable, script],
            cwd=lesson,
            env=env,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return False, f"took longer than {TIMEOUT_SECONDS}s and was stopped", (
            time.perf_counter() - started
        )

    output = (finished.stdout + finished.stderr).strip()
    return finished.returncode == 0, output, time.perf_counter() - started


def name(lesson: Path) -> str:
    """The lesson written the way the repository refers to it."""
    return lesson.relative_to(ROOT).as_posix()
