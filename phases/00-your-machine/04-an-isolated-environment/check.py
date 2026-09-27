"""
Lesson 4: the check.

Run it with:  python check.py
"""

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENVIRONMENT = HERE / ".work" / ".venv"


def fail(reason: str, fix: str) -> None:
    print(f"FAIL  {reason}")
    print(f"      {fix}")
    sys.exit(1)


def interpreter(environment: Path) -> Path:
    if sys.platform == "win32":
        return environment / "Scripts" / "python.exe"

    return environment / "bin" / "python"


def main() -> None:
    if not ENVIRONMENT.is_dir():
        fail(
            "there is no .work/.venv folder",
            "run: python -m venv .work/.venv  (on Debian or Ubuntu you may "
            "first need: sudo apt install python3-venv)",
        )

    python = interpreter(ENVIRONMENT)

    if not python.exists():
        fail(
            f"the folder exists but {python.name} is not inside it, so the "
            "environment was not finished",
            "delete .work/.venv and make it again",
        )

    finished = subprocess.run(
        [str(python), "-c", "import sys; print(sys.prefix)"],
        capture_output=True,
        text=True,
        timeout=60,
    )

    if finished.returncode != 0:
        fail(
            "the environment's Python would not run",
            "delete .work/.venv and make it again",
        )

    inside = finished.stdout.strip()

    if inside == sys.prefix:
        fail(
            "the environment reports the same root as the Python that made it, "
            "so it is not isolated",
            "delete .work/.venv and make it again with python -m venv",
        )

    print("PASS  the environment has its own Python, separate from the system one")


if __name__ == "__main__":
    main()
