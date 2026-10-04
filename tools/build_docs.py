"""
File: tools/build_docs.py
Author: Amey Thakur
GitHub: https://github.com/Amey-Thakur
Repository: https://github.com/Amey-Thakur/AI-ENGINEERING
License: MIT

Description:
Assembles the published site from the markdown already in the repository.

Nothing is written twice. Every page on the site is a file a reader can also
read on GitHub, copied into place rather than restated, so the two cannot
disagree. The navigation is counted from the phase and lesson directories, so
a new lesson appears in the sidebar by existing rather than by being
registered somewhere.

The tree under `phases/` is mirrored exactly, with each `README.md` becoming
an `index.md` in the same directory. That is what keeps every relative link in
the course working untouched: a lesson's `../03-when-it-chooses-wrong/` means
the same thing on the site as it does on GitHub.

Links to files the site does not publish, a licence, a script, a workflow,
are rewritten to point at GitHub, because that is where they actually live.

This writes `mkdocs.yml` as well. The theme belongs in one place, and a nav
that is generated cannot drift from the course it describes.

Usage:
    python tools/build_docs.py
    python tools/build_docs.py --serve
"""

from __future__ import annotations

import argparse
import re
import posixpath
import shutil
import subprocess
import sys
from pathlib import Path, PurePosixPath

import lesson

DOCS = lesson.ROOT / "docs"
CONFIG = lesson.ROOT / "mkdocs.yml"
REPO = "https://github.com/Amey-Thakur/AI-ENGINEERING"
BLOB = f"{REPO}/blob/main"
TREE = f"{REPO}/tree/main"

#: Top level markdown, and the name each one takes on the site.
TOP = {
    "README.md": "index.md",
    "GLOSSARY.md": "glossary.md",
    "FAQ.md": "faq.md",
    ".github/CONTRIBUTING.md": "contributing.md",
    ".github/SECURITY.md": "security.md",
    ".github/CODE_OF_CONDUCT.md": "code-of-conduct.md",
}

#: Images the pages reference.
ASSETS = lesson.ROOT / "assets"

#: Anything linked that is not published becomes a link to GitHub.
LINK = re.compile(r"\]\((?!https?:|#|mailto:)([^)#]+)(#[^)]*)?\)")

#: The README centres its header and footer in a div. Python-Markdown leaves
#: markdown inside block level HTML alone unless the element opts in, so the
#: headings and badges in those blocks would render as literal text.
CENTRED = '<div align="center">'
OPTED_IN = '<div align="center" markdown="1">'

THEME = """\
# Written by tools/build_docs.py. Edit the constants in that file instead of
# this one, which is regenerated on every build.
site_name: AI Engineering
site_url: https://amey-thakur.github.io/AI-ENGINEERING/
site_author: Amey Thakur
site_description: >-
  Learn to build AI systems by building them. A course that runs on the Python
  standard library alone: no account, no API key, no GPU, no paid service and
  no network at any point.

repo_url: https://github.com/Amey-Thakur/AI-ENGINEERING
repo_name: Amey-Thakur/AI-ENGINEERING
edit_uri: edit/main/
copyright: >-
  Copyright &copy; 2026 <strong>Amey Thakur</strong> &nbsp;&middot;&nbsp;
  <a href="https://github.com/Amey-Thakur/AI-ENGINEERING/blob/main/LICENSE">MIT</a>
  &nbsp;&middot;&nbsp; Built with the Python standard library, and nothing else

docs_dir: docs
site_dir: _site
use_directory_urls: true
strict: true

hooks:
  - tools/docs_hooks.py

theme:
  name: material
  custom_dir: overrides
  logo: assets/mark-on-slate.svg
  favicon: assets/favicon.png
  font:
    text: Inter
    code: JetBrains Mono
  icon:
    repo: fontawesome/brands/github
  features:
    # The guided spine: a sidebar in course order, a next and previous link at
    # the foot of every page, and a table of contents that tracks the reader.
    - navigation.indexes
    - navigation.sections
    - navigation.top
    - navigation.footer
    - navigation.tracking
    - toc.follow
    - search.suggest
    - search.highlight
    - search.share
    - content.code.copy
    - content.action.edit
  palette:
    # Material's own two schemes, retinted to slate, paper and Python blue in
    # assets/palette.css. Extending them rather than inventing a scheme name
    # means every variable the theme relies on, including the code
    # highlighting, is already defined and only the identity changes.
    - media: "(prefers-color-scheme: light)"
      scheme: default
      primary: custom
      accent: custom
      toggle:
        icon: material/weather-night
        name: Switch to dark
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      primary: custom
      accent: custom
      toggle:
        icon: material/weather-sunny
        name: Switch to light

extra_css:
  - assets/palette.css

extra:
  social:
    - icon: fontawesome/brands/github
      link: https://github.com/Amey-Thakur
      name: Amey Thakur on GitHub
    - icon: fontawesome/brands/linkedin
      link: https://www.linkedin.com/in/amey-thakur
      name: Amey Thakur on LinkedIn
    - icon: fontawesome/solid/id-card
      link: https://orcid.org/0000-0001-5644-1575
      name: ORCID 0000-0001-5644-1575

markdown_extensions:
  - admonition
  - attr_list
  - md_in_html
  - tables
  - toc:
      permalink: true
      toc_depth: 3
  - pymdownx.details
  - pymdownx.superfences
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.inlinehilite
  - pymdownx.smartsymbols
  - pymdownx.tilde
"""

#: The two palettes, written as a stylesheet because Material's own schemes do
#: not carry these values. Every hex here is the one the mark, the card and the
#: README header are drawn with.
PALETTE = """\
/* Written by tools/build_docs.py. One palette, two lightnesses, three hues:
   slate, paper and Python's blue, which are the colours the mark is drawn in.
   Editing this file by hand will be undone on the next build.

   These extend Material's own `default` and `slate` schemes rather than
   replacing them, so the theme keeps every value it relies on and only the
   identity changes. */

:root,
[data-md-color-scheme="default"] {
  --md-primary-fg-color:           #2F3E4A;
  --md-primary-fg-color--light:    #3E5160;
  --md-primary-fg-color--dark:     #22303C;
  --md-primary-bg-color:           #FAFBFC;
  --md-primary-bg-color--light:    #D7DDE3;

  --md-accent-fg-color:            #3776AB;
  --md-accent-fg-color--transparent: #3776AB14;
  --md-accent-bg-color:            #FAFBFC;

  --md-default-bg-color:           #FAFBFC;
  --md-default-fg-color:           #22303C;
  --md-default-fg-color--light:    #5B6B78;
  --md-default-fg-color--lighter:  #8794A0;
  --md-default-fg-color--lightest: #D7DDE3;

  /* The typeset reads its own variables, which is why setting only the
     default colours above left the body text untouched. */
  --md-typeset-color:              #22303C;
  --md-typeset-a-color:            #2A6494;

  --md-code-bg-color:              #F1F4F7;
  --md-code-fg-color:              #22303C;

  --md-footer-bg-color:            #22303C;
  --md-footer-bg-color--dark:      #1A2630;
  --md-footer-fg-color:            #FAFBFC;
  --md-footer-fg-color--light:     #AEBAC4;
  --md-footer-fg-color--lighter:   #7D8B98;
}

[data-md-color-scheme="slate"] {
  /* Slate builds its greys from one hue. Moving it to 210 degrees tilts the
     whole dark theme towards the blue-slate the mark is drawn in, rather
     than the violet it ships with. */
  --md-hue: 210;

  --md-primary-fg-color:           #1E2832;
  --md-primary-fg-color--light:    #2A3744;
  --md-primary-fg-color--dark:     #141C23;
  --md-primary-bg-color:           #E6ECF2;
  --md-primary-bg-color--light:    #9AA8B4;

  --md-accent-fg-color:            #6BA6DE;
  --md-accent-fg-color--transparent: #6BA6DE1F;
  --md-accent-bg-color:            #11181E;

  --md-default-bg-color:           #161E26;
  --md-default-fg-color:           #E6ECF2;
  --md-default-fg-color--light:    #9AA8B4;
  --md-default-fg-color--lighter:  #74828F;
  --md-default-fg-color--lightest: #2C3845;

  --md-typeset-color:              #E6ECF2;
  --md-typeset-a-color:            #6BA6DE;

  --md-code-bg-color:              #1B242E;
  --md-code-fg-color:              #E6ECF2;

  --md-footer-bg-color:            #11181E;
  --md-footer-bg-color--dark:      #0D1317;
  --md-footer-fg-color:            #E6ECF2;
  --md-footer-fg-color--light:     #9AA8B4;
  --md-footer-fg-color--lighter:   #6B7885;
}

/* The mark in the title bar sits beside the name, so give it room and keep it
   from being scaled into mush. */
.md-header__button.md-logo :is(img, svg) {
  height: 1.4rem;
  width: auto;
}

/* The course reads better with a measured line length than with the full
   width of a monitor. */
.md-typeset {
  font-size: .78rem;
  line-height: 1.7;
}

/* Tables carry most of the measured results, so they are built to be read
   rather than to decorate. */
.md-typeset table:not([class]) {
  font-size: .70rem;
  border: 1px solid var(--md-default-fg-color--lightest);
}

.md-typeset table:not([class]) th {
  background: var(--md-default-fg-color--lightest);
  color: var(--md-default-fg-color);
  font-weight: 600;
}

/* Every lesson opens on a quotation, which is the hook, so let it look like
   one rather than like an aside. */
.md-typeset blockquote {
  border-left: 2px solid var(--md-accent-fg-color);
  color: var(--md-default-fg-color);
}

/* The palette control, drawn as a switch rather than left as a bare icon.
   Material shows exactly one of the two labels at a time, so the label is the
   track and its icon is the knob: parked left while the light scheme is on,
   slid right while the dark one is. */
form[data-md-component="palette"] {
  display: flex;
  align-items: center;
}

form[data-md-component="palette"] > label.md-header__button {
  position: relative;
  box-sizing: border-box;
  width: 2.4rem;
  height: 1.2rem;
  margin: 0 .35rem;
  padding: 0;
  border: 1px solid rgba(255, 255, 255, .34);
  border-radius: 1rem;
  background: rgba(255, 255, 255, .16);
  opacity: 1;
  transition: background .25s, border-color .25s;
}

form[data-md-component="palette"] > label.md-header__button:hover {
  background: rgba(255, 255, 255, .26);
  border-color: rgba(255, 255, 255, .5);
}

form[data-md-component="palette"] > label.md-header__button svg {
  position: absolute;
  top: 50%;
  width: .96rem;
  height: .96rem;
  padding: .16rem;
  border-radius: 50%;
  background: var(--md-primary-bg-color);
  color: var(--md-primary-fg-color);
  transform: translateY(-50%);
  transition: left .25s ease;
}

[data-md-color-scheme="default"] form[data-md-component="palette"] > label svg {
  left: .08rem;
}

[data-md-color-scheme="slate"] form[data-md-component="palette"] > label svg {
  left: calc(100% - 1.04rem);
}

/* The repository name, in full. Material allows it 11.7rem and
   "Amey-Thakur/AI-ENGINEERING" is wider than that, so it arrived ellipsised. */
/* Material lets this shrink, which is what was clipping the name: raising
   max-width changed nothing because the flex layout, not the maximum, was
   the constraint. Sizing it to its content and refusing to shrink fixes it,
   and the maximum stays as a guard so a longer name cannot crowd the search
   box out. */
.md-header__source {
  flex: 0 0 auto;
  width: auto;
  max-width: 19rem;
  margin-left: .6rem;
}

/* Wide enough for the whole name, and still clipping rather than overlapping
   if a longer one ever arrives. */
.md-source__repository {
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: .68rem;
}

/* Below the width where both fit, the name goes and the icon stays, which is
   better than half a name. */
@media screen and (max-width: 76.1875em) {
  .md-header__source {
    max-width: none;
  }
}

/* Authorship, on its own line at the foot of every page. */
.md-footer-meta__inner {
  flex-wrap: wrap;
}

.md-copyright {
  width: 100%;
}

.md-copyright__highlight {
  color: var(--md-footer-fg-color);
}
"""

#: The one thing the theme has no setting for: the card a link shows when the
#: site is shared. It points at the same image GitHub uses, so a link to the
#: site and a link to the repository look the same.
OVERRIDE = """\
{% extends "base.html" %}

<!-- Written by tools/build_docs.py. Edit that file instead of this one. -->

{% block extrahead %}
  {% set page_title = page.title | default(config.site_name) %}
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="{{ config.site_name }}">
  <meta property="og:title" content="{{ page_title }}">
  <meta property="og:description" content="{{ config.site_description }}">
  <meta property="og:url" content="{{ page.canonical_url }}">
  <meta property="og:image" content="{{ config.site_url }}assets/social-preview.png">
  <meta property="og:image:width" content="1280">
  <meta property="og:image:height" content="640">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{{ page_title }}">
  <meta name="twitter:description" content="{{ config.site_description }}">
  <meta name="twitter:image" content="{{ config.site_url }}assets/social-preview.png">
{% endblock %}
"""


HOOKS = '''\
"""
File: tools/docs_hooks.py
Author: Amey Thakur
Repository: https://github.com/Amey-Thakur/AI-ENGINEERING
License: MIT

Description:
Turns GitHub's alert blocks into the ones the site's theme understands.

GitHub renders

    > [!NOTE]
    > Something worth knowing.

as a coloured callout. Material renders the same markdown as a plain
blockquote with a stray `[!NOTE]` on the first line, and this course leans on
those callouts in nearly every lesson.

Rewriting the source would fix the site and break GitHub, where most people
will read the material. So the rewrite happens here, at build time, and the
files on disk stay GitHub-native.

Written by tools/build_docs.py. Edit that file instead of this one.
"""

import re

KINDS = {
    "NOTE": "note",
    "TIP": "tip",
    "IMPORTANT": "info",
    "WARNING": "warning",
    "CAUTION": "danger",
}

TITLES = {
    "NOTE": "Note",
    "TIP": "Tip",
    "IMPORTANT": "Important",
    "WARNING": "Warning",
    "CAUTION": "Caution",
}

OPENS = re.compile(r"^(\\s*)>\\s*\\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\\]\\s*$")
QUOTED = re.compile(r"^(\\s*)>\\s?(.*)$")


def on_page_markdown(markdown, page=None, config=None, files=None):
    lines = markdown.split("\\n")
    out = []
    at = 0

    while at < len(lines):
        opened = OPENS.match(lines[at])

        if not opened:
            out.append(lines[at])
            at += 1
            continue

        indent, kind = opened.group(1), opened.group(2)
        at += 1
        body = []

        while at < len(lines):
            quoted = QUOTED.match(lines[at])

            if quoted is None:
                break

            body.append(quoted.group(2))
            at += 1

        out.append(f'{indent}!!! {KINDS[kind]} "{TITLES[kind]}"')
        out.append("")

        for line in body:
            out.append(f"{indent}    {line}" if line.strip()
                       else f"{indent}")

        out.append("")

    return "\\n".join(out)
'''


def phase_title(directory: Path) -> str:
    """The phase's own heading, so the sidebar says what the page says."""
    heading = directory / "README.md"

    if heading.exists():
        first = heading.read_text(encoding="utf-8").splitlines()[0]

        if ". " in first:
            return first.split(". ", 1)[1].strip()

    return directory.name


def lesson_title(directory: Path) -> str:
    heading = directory / "README.md"

    if heading.exists():
        first = heading.read_text(encoding="utf-8").splitlines()[0]

        return first.lstrip("# ").strip()

    return directory.name


def published() -> dict[str, str]:
    """Every source markdown path mapped to where it lands under docs/."""
    where = dict(TOP)

    for directory in sorted((lesson.ROOT / "phases").glob("*")):
        if not directory.is_dir():
            continue

        here = directory.relative_to(lesson.ROOT).as_posix()

        if (directory / "README.md").exists():
            where[f"{here}/README.md"] = f"{here}/index.md"

        for inner in sorted(directory.glob("*")):
            if inner.is_dir() and (inner / "README.md").exists():
                deep = inner.relative_to(lesson.ROOT).as_posix()
                where[f"{deep}/README.md"] = f"{deep}/index.md"

    return where


def rewrite(text: str, source: str, where: dict[str, str]) -> str:
    """Point every link at where the site actually publishes the target.

    Resolved through the published mapping rather than left alone, because a
    few files are renamed on the way in (GLOSSARY.md becomes glossary.md,
    .github/CONTRIBUTING.md becomes contributing.md) and a directory link has
    to arrive at that directory's index. Anything the site does not publish
    becomes a link to GitHub, because that is where it lives.
    """
    here = (lesson.ROOT / source).parent
    mine = PurePosixPath(where[source]).parent

    def fix(match: re.Match) -> str:
        target, fragment = match.group(1), match.group(2) or ""

        try:
            absolute = (here / target).resolve()
            inside = absolute.relative_to(lesson.ROOT).as_posix()
        except ValueError:
            return match.group(0)

        landing = where.get(inside) or where.get(f"{inside}/README.md")

        if landing:
            relative = posixpath.relpath(landing, mine.as_posix() or ".")

            return f"]({relative}{fragment})"

        if absolute.is_dir():
            return f"]({TREE}/{inside}{fragment})"

        return f"]({BLOB}/{inside}{fragment})"

    return LINK.sub(fix, text)


def nav(where: dict[str, str]) -> str:
    """The sidebar, in course order, counted from the directories."""
    def label(text: str) -> str:
        """Quoted, because a lesson title may hold a colon and YAML would
        read that as a mapping."""
        return '"' + text.replace('"', "'") + '"'

    lines = ["nav:",
             "  - Start here: index.md",
             "  - The course:"]

    for directory in sorted((lesson.ROOT / "phases").glob("*")):
        if not directory.is_dir() or not (directory / "README.md").exists():
            continue

        here = directory.relative_to(lesson.ROOT).as_posix()
        number = directory.name.split("-")[0].lstrip("0") or "0"
        lines.append(f"      - {label(f'{number}. ' + phase_title(directory))}:")
        lines.append(f"          - {here}/index.md")

        for inner in sorted(directory.glob("*")):
            if inner.is_dir() and (inner / "README.md").exists():
                deep = inner.relative_to(lesson.ROOT).as_posix()
                lines.append(f"          - {label(lesson_title(inner))}: "
                             f"{deep}/index.md")

    lines += [
        "  - Reference:",
        "      - Glossary: glossary.md",
        "      - Questions: faq.md",
        "  - Taking part:",
        "      - Contributing: contributing.md",
        "      - Security: security.md",
        "      - Code of conduct: code-of-conduct.md",
    ]

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Assemble the site from the repository's markdown.")
    parser.add_argument("--serve", action="store_true",
                        help="build, then serve it locally")
    parsed = parser.parse_args()

    where = published()

    if DOCS.exists():
        shutil.rmtree(DOCS)

    for source, target in sorted(where.items()):
        origin = lesson.ROOT / source

        if not origin.exists():
            print(f"FAIL  {source} is listed for the site and does not exist")
            return 1

        landing = DOCS / target
        landing.parent.mkdir(parents=True, exist_ok=True)
        body = rewrite(origin.read_text(encoding="utf-8"), source, where)
        body = body.replace(CENTRED, OPTED_IN)
        landing.write_text(body, encoding="utf-8", newline="\n")

    shutil.copytree(ASSETS, DOCS / "assets", dirs_exist_ok=True)
    (DOCS / "assets" / "palette.css").write_text(PALETTE, encoding="utf-8",
                                                 newline="\n")

    # The card a shared link shows. The same file GitHub serves, so a link to
    # the site and a link to the repository look alike.
    card = lesson.ROOT / ".github" / "social-preview.png"

    if card.exists():
        shutil.copyfile(card, DOCS / "assets" / "social-preview.png")

    overrides = lesson.ROOT / "overrides"
    overrides.mkdir(exist_ok=True)
    (overrides / "main.html").write_text(OVERRIDE, encoding="utf-8",
                                         newline="\n")

    (lesson.ROOT / "tools" / "docs_hooks.py").write_text(
        HOOKS, encoding="utf-8", newline="\n")

    CONFIG.write_text(THEME + "\n" + nav(where), encoding="utf-8",
                      newline="\n")

    pages = len(where)
    phases = sum(1 for key in where if key.startswith("phases/")
                 and key.count("/") == 2)
    lessons = sum(1 for key in where if key.startswith("phases/")
                  and key.count("/") == 3)

    print(f"  docs/            {pages} pages, {phases} phases, "
          f"{lessons} lessons")
    print(f"  mkdocs.yml       written, nav counted from the repository")
    print(f"  overrides/main.html  written")
    print(f"  tools/docs_hooks.py  written")

    if parsed.serve:
        return subprocess.call([sys.executable, "-m", "mkdocs", "serve"],
                               cwd=lesson.ROOT)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
