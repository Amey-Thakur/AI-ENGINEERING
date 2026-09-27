"""
Lesson 4: an isolated environment.

Builds a virtual environment and then proves it is one, by asking the Python
inside it where it thinks it lives and comparing that with the Python that
built it.

Run it with:  python solve.py
"""

import subprocess
import sys
import venv
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENVIRONMENT = HERE / ".work" / ".venv"


def interpreter(environment: Path) -> Path:
    """Where the environment keeps its Python, which differs by system."""
    if sys.platform == "win32":
        return environment / "Scripts" / "python.exe"

    return environment / "bin" / "python"


def prefix_of(python: Path) -> str:
    """What that Python reports as its own root."""
    finished = subprocess.run(
        [str(python), "-c", "import sys; print(sys.prefix)"],
        capture_output=True,
        text=True,
    )

    if finished.returncode != 0:
        raise SystemExit(f"The environment's Python did not run:\n{finished.stderr}")

    return finished.stdout.strip()


def main() -> None:
    ENVIRONMENT.parent.mkdir(parents=True, exist_ok=True)

    # with_pip=False keeps this quick and needs nothing from the network. A
    # real project would leave pip in, which is the default.
    venv.EnvBuilder(with_pip=False, clear=True).create(ENVIRONMENT)

    python = interpreter(ENVIRONMENT)
    own = python.exists()
    separate = own and prefix_of(python) != sys.prefix

    print(f"Created {ENVIRONMENT.relative_to(HERE).as_posix()}")
    print(f"The environment has its own Python: {'yes' if own else 'no'}")
    print(f"Its Python is not the one that made it: {'yes' if separate else 'no'}")


if __name__ == "__main__":
    main()
