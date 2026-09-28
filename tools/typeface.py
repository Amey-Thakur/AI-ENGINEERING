"""
File: tools/typeface.py
Author: Amey Thakur
GitHub: https://github.com/Amey-Thakur
Repository: https://github.com/Amey-Thakur/AI-ENGINEERING
License: MIT

Description:
Finds a usable font on whatever machine this is running on.

The two drawing tools in this directory need five kinds of letter: a very heavy
sans for card titles, a sans and a bold sans for labels, a serif and a bold serif for the display text, and
a monospace for anything a reader might retype. Asking for them by filename
works on exactly one computer, which is fine for a card the author regenerates
and not fine for tools/certificate.py, which is meant to be run by a learner
in their own fork on a machine nobody has seen.

So fonts are asked for by role. Each role has a list of candidates, most
preferred first, covering Windows, macOS and the fonts that are present on a
Linux CI runner. The first one that exists wins, and if none of them do the
error says which role failed and what to install rather than falling back to
a bitmap font that ignores the size argument.

Usage:
    import typeface
    pen.text(spot, "Record of completion", font=typeface.of("serif bold", 82))
"""

from __future__ import annotations

from pathlib import Path

from PIL import ImageFont

#: Where each platform keeps its fonts.
ROOTS = (
    Path("C:/Windows/Fonts"),
    Path("/usr/share/fonts"),
    Path("/System/Library/Fonts"),
    Path("/Library/Fonts"),
    Path.home() / ".fonts",
    Path.home() / "Library" / "Fonts",
)

#: Role, then candidate file names in order of preference. Names rather than
#: full paths, because the same font lives in a different directory on every
#: distribution.
CANDIDATES = {
    "black": (
        "seguibl.ttf", "Archivo-Black.ttf", "arialbd.ttf",
        "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf",
        "NotoSans-Black.ttf", "Helvetica.ttc",
    ),
    "sans": (
        "segoeui.ttf", "calibri.ttf", "arial.ttf",
        "DejaVuSans.ttf", "LiberationSans-Regular.ttf",
        "NotoSans-Regular.ttf", "Helvetica.ttc", "Arial.ttf",
    ),
    "sans bold": (
        "calibrib.ttf", "seguisb.ttf", "arialbd.ttf",
        "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf",
        "NotoSans-Bold.ttf", "Helvetica.ttc", "Arial Bold.ttf",
    ),
    "serif": (
        "cambria.ttc", "georgia.ttf", "times.ttf",
        "DejaVuSerif.ttf", "LiberationSerif-Regular.ttf",
        "NotoSerif-Regular.ttf", "Georgia.ttf", "Times New Roman.ttf",
    ),
    "serif bold": (
        "cambriab.ttf", "georgiab.ttf", "timesbd.ttf",
        "DejaVuSerif-Bold.ttf", "LiberationSerif-Bold.ttf",
        "NotoSerif-Bold.ttf", "Georgia Bold.ttf",
        "Times New Roman Bold.ttf",
    ),
    "mono": (
        "consola.ttf", "cour.ttf",
        "DejaVuSansMono.ttf", "LiberationMono-Regular.ttf",
        "NotoSansMono-Regular.ttf", "Menlo.ttc", "Courier New.ttf",
    ),
}

#: Resolved paths, so the directory walk happens once per role.
_found: dict[str, Path] = {}


class Missing(RuntimeError):
    """Raised when no candidate for a role exists on this machine."""


def _search(names: tuple[str, ...]) -> Path | None:
    """The first candidate that exists, preferring earlier names."""
    for name in names:
        for root in ROOTS:
            if not root.is_dir():
                continue

            direct = root / name

            if direct.is_file():
                return direct

            # Linux buries fonts one or two directories down.
            for found in root.rglob(name):
                if found.is_file():
                    return found

    return None


def path(role: str) -> Path:
    """Where the font for a role lives on this machine."""
    if role in _found:
        return _found[role]

    if role not in CANDIDATES:
        raise Missing(f"there is no font role called {role!r}, only "
                      f"{', '.join(sorted(CANDIDATES))}")

    found = _search(CANDIDATES[role])

    if found is None:
        raise Missing(
            f"no {role} font was found on this machine. Tried "
            f"{', '.join(CANDIDATES[role][:4])} and others under "
            f"{', '.join(str(root) for root in ROOTS if root.is_dir())}. "
            f"On Linux, `apt-get install fonts-dejavu` provides all four "
            f"roles."
        )

    _found[role] = found

    return found


def of(role: str, size: int) -> ImageFont.FreeTypeFont:
    """A font for a role at a size, in pixels."""
    return ImageFont.truetype(str(path(role)), size)


def main() -> int:
    """Says what this machine resolved each role to, which is the whole
    diagnostic anybody needs when a drawing tool will not run."""
    worst = 0

    for role in sorted(CANDIDATES):
        try:
            print(f"  {role:12} {path(role)}")
        except Missing as absent:
            print(f"  {role:12} MISSING")
            print(f"               {absent}")
            worst = 1

    return worst


if __name__ == "__main__":
    raise SystemExit(main())
