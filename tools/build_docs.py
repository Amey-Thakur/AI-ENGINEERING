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
import json
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
    "CURRICULUM.md": "curriculum.md",
    "GLOSSARY.md": "glossary.md",
    "FAQ.md": "faq.md",
    ".github/CONTRIBUTING.md": "contributing.md",
    ".github/SECURITY.md": "security.md",
    ".github/CODE_OF_CONDUCT.md": "code-of-conduct.md",
}

#: Where the site is published. Kept beside the config that declares it.
SITE = "https://amey-thakur.github.io/AI-ENGINEERING/"

#: The one sentence every page falls back to, and the course's own summary in
#: its structured data.
SUMMARY = ("Learn to build AI systems by building them. A course that runs on "
           "the Python standard library alone: no account, no API key, no "
           "GPU, no paid service and no network at any point.")

#: Pages that open with a header plate rather than prose, so there is nothing
#: on them worth lifting. Written out, and kept short enough to survive a
#: search result intact.
WRITTEN_DESCRIPTIONS = {
    "index.md": SUMMARY,
    "faq.md": "What this course is, what it leaves out, how long it takes, "
              "and why it installs nothing. Fifty lessons, ten phases, the "
              "Python standard library and no network.",
    "curriculum.md": "All fifty lessons of the course on one page, in order, "
                     "with what you do in each. Ten phases, about "
                     "thirty-seven hours, and nothing installed at any point.",
    "glossary.md": "Every term this course uses, the name it usually goes by "
                   "elsewhere, and the lesson that measures it. Written so "
                   "you can read a paper after finishing the course.",
    "contributing.md": "How to report a lesson that does not run, a "
                       "measurement that disagrees, or an explanation that "
                       "does not land. Every number here is reproducible, so "
                       "a disagreement is a bug.",
    "security.md": "How to report a security issue in this repository. The "
                   "course runs offline on the standard library, so the "
                   "surface is small, and it is written down here anyway.",
    "code-of-conduct.md": "The standard of behaviour expected of everyone "
                          "taking part in this project, and how to report "
                          "behaviour that falls short of it.",
}

#: Material builds the edit link from the generated path. Overridden so it
#: uses the source the build recorded, and so the "view source" button points
#: at the same file rather than at a raw URL for something that is not there.
ACTIONS = """\
<!-- Written by tools/build_docs.py. Edit that file instead of this one. -->

{% set source = page.meta.source_url | default(page.edit_url, true) %}
{% if source %}
  {% if "content.action.edit" in features %}
    <a href="{{ source }}" title="{{ lang.t('action.edit') }}" class="md-content__button md-icon" rel="edit">
      {% set icon = config.theme.icon.edit or "material/file-edit-outline" %}
      {% include ".icons/" ~ icon ~ ".svg" %}
    </a>
  {% endif %}
  {% if "content.action.view" in features %}
    <a href="{{ source | replace('/edit/', '/blob/') }}" title="{{ lang.t('action.view') }}" class="md-content__button md-icon">
      {% set icon = config.theme.icon.view or "material/file-eye-outline" %}
      {% include ".icons/" ~ icon ~ ".svg" %}
    </a>
  {% endif %}
{% endif %}
"""

#: The curriculum page's boxes, made to remember. Nothing leaves the browser:
#: there is no account to keep this in and no server to send it to, which is
#: the same promise the rest of the course makes.
PROGRESS = """\
/* Written by tools/build_docs.py. Edit that file instead of this one. */

(function () {
  "use strict";

  var KEY = "ai-engineering:done";

  function read() {
    try {
      return JSON.parse(localStorage.getItem(KEY)) || {};
    } catch (error) {
      return {};
    }
  }

  function write(done) {
    try {
      localStorage.setItem(KEY, JSON.stringify(done));
    } catch (error) {
      /* A private window refuses to store anything. The page still works. */
    }
  }

  function setUp() {
    var list = document.querySelector(".md-content .task-list");

    if (!list) {
      return;
    }

    var items = document.querySelectorAll(".md-content .task-list-item");

    if (!items.length) {
      return;
    }

    var done = read();
    var bar = document.createElement("div");
    bar.className = "progress-note";
    var track = document.createElement("div");
    track.className = "progress-track";
    var fill = document.createElement("div");
    fill.className = "progress-fill";
    var said = document.createElement("p");
    said.className = "progress-said";
    track.appendChild(fill);
    bar.appendChild(said);
    bar.appendChild(track);

    var reset = document.createElement("button");
    reset.type = "button";
    reset.className = "progress-reset";
    reset.textContent = "Clear";
    bar.appendChild(reset);

    var boxes = [];

    Array.prototype.forEach.call(items, function (item) {
      var box = item.querySelector("input[type=checkbox]");
      var link = item.querySelector("a[href]");

      if (!box || !link) {
        return;
      }

      var id = link.getAttribute("href");
      box.disabled = false;
      box.removeAttribute("disabled");
      box.checked = Boolean(done[id]);
      item.classList.toggle("is-done", box.checked);
      boxes.push({ box: box, item: item, id: id });

      box.addEventListener("change", function () {
        var state = read();

        if (box.checked) {
          state[id] = true;
        } else {
          delete state[id];
        }

        write(state);
        item.classList.toggle("is-done", box.checked);
        show();
      });
    });

    function show() {
      var ticked = boxes.filter(function (each) {
        return each.box.checked;
      }).length;
      var share = boxes.length ? (ticked / boxes.length) * 100 : 0;
      fill.style.width = share.toFixed(1) + "%";
      track.setAttribute("role", "progressbar");
      track.setAttribute("aria-valuenow", String(ticked));
      track.setAttribute("aria-valuemin", "0");
      track.setAttribute("aria-valuemax", String(boxes.length));

      if (!ticked) {
        said.textContent = "Nothing ticked yet. " + boxes.length +
          " lessons ahead of you.";
      } else if (ticked === boxes.length) {
        said.textContent = "All " + boxes.length +
          " done. Go and claim the record of completion.";
      } else {
        said.textContent = ticked + " of " + boxes.length +
          " done, " + (boxes.length - ticked) + " to go.";
      }

      reset.hidden = ticked === 0;
    }

    reset.addEventListener("click", function () {
      write({});
      boxes.forEach(function (each) {
        each.box.checked = false;
        each.item.classList.remove("is-done");
      });
      show();
    });

    list.parentNode.insertBefore(bar, list);
    show();
  }

  if (window.document$ && window.document$.subscribe) {
    window.document$.subscribe(setUp);
  } else {
    document.addEventListener("DOMContentLoaded", setUp);
  }
}());
"""

#: Where a reader is sent to correct a page. The build appends the real source
#: path, which is not the path the page is published at.
EDIT = "https://github.com/Amey-Thakur/AI-ENGINEERING/edit/main/"

#: Pages whose markdown is itself generated. Editing the page would be undone
#: by the next build, so the button offers the program that writes it.
SOURCE_OVERRIDES = {"curriculum.md": "tools/build_curriculum.py"}

#: The homepage's own title. Without it the page is called "Start here",
#: which says nothing to anybody who meets it in a list of search results.
LANDING_TITLE = "AI Engineering: build it yourself, measure everything"

#: What a crawler is told at the root. Everything is open; the point of the
#: file is the sitemap line, which is how the rest gets found.
ROBOTS = """\
User-agent: *
Allow: /

Sitemap: https://amey-thakur.github.io/AI-ENGINEERING/sitemap.xml
"""

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
    - content.action.view
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

extra_javascript:
  - assets/progress.js

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
  - pymdownx.tasklist:
      custom_checkbox: true
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

/* The curriculum page's progress strip. The boxes are ordinary task list
   items everywhere else; here they are clickable and they keep their place
   in this browser, which is the only place that state exists. */

.progress-note {
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: center;
  gap: 0.4rem 0.8rem;
  margin: 1.2rem 0 1.6rem;
  padding: 0.9rem 1rem;
  border: 1px solid var(--md-default-fg-color--lightest);
  border-radius: 0.3rem;
  background: var(--md-code-bg-color);
}

.progress-said {
  grid-column: 1;
  margin: 0;
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--md-default-fg-color);
}

.progress-track {
  grid-column: 1 / -1;
  grid-row: 2;
  height: 0.3rem;
  overflow: hidden;
  border-radius: 0.3rem;
  background: var(--md-default-fg-color--lightest);
}

.progress-fill {
  width: 0;
  height: 100%;
  border-radius: 0.3rem;
  background: var(--md-primary-fg-color);
  transition: width 0.25s ease;
}

.progress-reset {
  grid-column: 2;
  grid-row: 1;
  padding: 0.25rem 0.7rem;
  font-size: 0.68rem;
  font-weight: 700;
  color: var(--md-primary-fg-color);
  cursor: pointer;
  background: transparent;
  border: 1px solid var(--md-default-fg-color--lightest);
  border-radius: 0.2rem;
}

.progress-reset:hover {
  border-color: var(--md-primary-fg-color);
}

.md-content .task-list-item {
  transition: opacity 0.2s ease;
}

.md-content .task-list-item.is-done {
  opacity: 0.55;
}

.md-content .task-list-item.is-done > .task-list-control ~ * {
  text-decoration: line-through;
  text-decoration-thickness: 1px;
}

.md-content .task-list-control input[type="checkbox"] {
  cursor: pointer;
}

.md-content .task-list-item label,
.md-content .task-list-control {
  cursor: pointer;
}

@media (prefers-reduced-motion: reduce) {
  .progress-fill,
  .md-content .task-list-item {
    transition: none;
  }
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
#: The page head. Every page gets its own description and its own place in a
#: breadcrumb trail, because one description repeated across sixty pages is
#: the single thing a search engine most reliably ignores. The three
#: __PLACEHOLDER__ tokens are filled in by main() with data read from the
#: repository, so nothing here has to be kept in step by hand.
OVERRIDE = """\
{% extends "base.html" %}

<!-- Written by tools/build_docs.py. Edit that file instead of this one. -->

{% block htmltitle %}
  {# Material appends the site name to every title. On the front page that
     repeats it, and a title over about sixty characters is cut short in a
     result list, so the front page carries its own and nothing is added. #}
  {% if page and page.canonical_url == config.site_url %}
    <title>{{ page.meta.title | default(config.site_name, true) }}</title>
  {% elif page and page.title %}
    <title>{{ page.title }} &middot; {{ config.site_name }}</title>
  {% else %}
    <title>{{ config.site_name }}</title>
  {% endif %}
{% endblock %}

{% block extrahead %}
  {# The 404 page is rendered without a page object, so everything below it
     has to be skipped rather than guessed at. #}
  {% if page %}
  {% set page_title = page.meta.title | default(page.title, true) | default(config.site_name, true) %}
  {% set page_description = page.meta.description | default(config.site_description, true) %}
  <meta property="og:type" content="{% if page.canonical_url == config.site_url %}website{% else %}article{% endif %}">
  <meta property="og:site_name" content="{{ config.site_name }}">
  <meta property="og:title" content="{{ page_title }}">
  <meta property="og:description" content="{{ page_description }}">
  <meta property="og:url" content="{{ page.canonical_url }}">
  <meta property="og:image" content="{{ config.site_url }}assets/social-preview.png">
  <meta property="og:image:alt" content="AI Engineering. Learn to build AI systems by building them.">
  <meta property="og:image:width" content="1280">
  <meta property="og:image:height" content="640">
  <meta property="og:locale" content="en_GB">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{{ page_title }}">
  <meta name="twitter:description" content="{{ page_description }}">
  <meta name="twitter:image" content="{{ config.site_url }}assets/social-preview.png">
  <meta name="twitter:image:alt" content="AI Engineering. Learn to build AI systems by building them.">
  <meta name="author" content="Amey Thakur">
  <link rel="author" href="https://github.com/Amey-Thakur">
  {% if page.ancestors %}
  <script type="application/ld+json">{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"{{ config.site_name }}","item":"{{ config.site_url }}"}{% for parent in page.ancestors | reverse %}{% if parent.title %},{"@type":"ListItem","position":{{ loop.index + 1 }},"name":"{{ parent.title | e }}"{% if parent.canonical_url is defined and parent.canonical_url %},"item":"{{ parent.canonical_url }}"{% endif %}}{% endif %}{% endfor %},{"@type":"ListItem","position":{{ (page.ancestors | length) + 2 }},"name":"{{ page.title | e }}","item":"{{ page.canonical_url }}"}]}</script>
  {% endif %}
  {% if page.canonical_url == config.site_url %}__COURSE__{% endif %}
  {% if page.file.src_uri == "faq.md" %}__FAQ__{% endif %}
  {% if page.file.src_uri == "glossary.md" %}__GLOSSARY__{% endif %}
  {% endif %}
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


#: How long a meta description may run before a search engine truncates it.
DESCRIPTION_LIMIT = 155

#: Markdown that carries no meaning once the tags are gone.
MARKUP = re.compile(r"\*\*|__|[`*_]|<[^>]+>")
LINKED = re.compile(r"\[([^\]]*)\]\([^)]*\)")
QUOTED = re.compile(r"^>\s?", re.M)
SPACES = re.compile(r"\s+")


def plain(text: str) -> str:
    """Markdown with the markup taken out, on one line."""
    text = LINKED.sub(r"\1", text)
    text = MARKUP.sub("", text)

    return SPACES.sub(" ", text).strip()


def describe(body: str, fallback: str) -> str:
    """A description for one page, taken from that page's own opening.

    Every lesson opens with a blockquote stating what it found, which is both
    the most accurate summary available and the one a reader would want to see
    under a search result. Falls back to the site's own description for pages
    that start with a header plate rather than prose.
    """
    lines = body.splitlines()
    start = 1 if lines and lines[0].startswith("# ") else 0
    blocks = re.split(r"\n\s*\n", "\n".join(lines[start:]))
    chosen = ""

    for block in blocks:
        stripped = block.strip()

        if not stripped:
            continue

        if stripped.startswith(">"):
            chosen = plain(QUOTED.sub("", stripped))
            break

        if stripped.startswith(("#", "<", "|", "```", "---", "[!", "[![",
                                "!!!", "*", "-")):
            continue

        chosen = plain(stripped)
        break

    if len(chosen) < 40:
        return fallback

    if len(chosen) <= DESCRIPTION_LIMIT:
        return chosen

    cut = chosen[:DESCRIPTION_LIMIT].rsplit(" ", 1)[0].rstrip(" ,;:.")

    return f"{cut}..."


def as_script(data: object) -> str:
    """One JSON-LD block, safe to drop inside a script tag."""
    body = json.dumps(data, ensure_ascii=False, separators=(",", ":"))

    return ('<script type="application/ld+json">'
            + body.replace("</", "<\\/") + "</script>")


def course_data(where: dict[str, str]) -> str:
    """The course itself, so a search engine can show it as a course."""
    syllabus = []

    for source_path in sorted(where):
        if not (source_path.startswith("phases/")
                and source_path.count("/") == 2):
            continue

        directory = lesson.ROOT / source_path
        body = directory.read_text(encoding="utf-8")
        title = body.splitlines()[0].lstrip("# ").strip()
        syllabus.append({
            "@type": "Syllabus",
            "name": title,
            "description": describe(body, title),
            "url": SITE + source_path.replace("/README.md", "/"),
        })

    author = {"@type": "Person", "name": "Amey Thakur",
              "url": "https://github.com/Amey-Thakur",
              "identifier": "https://orcid.org/0000-0001-5644-1575"}

    return as_script({
        "@context": "https://schema.org",
        "@type": "Course",
        "name": "AI Engineering",
        "description": SUMMARY,
        "url": SITE,
        "provider": author,
        "author": author,
        "inLanguage": "en",
        "isAccessibleForFree": True,
        "isFamilyFriendly": True,
        "license": "https://opensource.org/licenses/MIT",
        "educationalLevel": "Beginner to intermediate",
        "learningResourceType": ["Course", "Tutorial", "Exercise"],
        "teaches": [
            "Writing a classifier from scratch in Python",
            "Backpropagation derived and checked by hand",
            "Word vectors from co-occurrence counts",
            "Language modelling and perplexity",
            "Retrieval and why a generator can make it worse",
            "Tool use, agent loops and measuring an agent",
            "Confidence intervals, significance tests and baselines",
            "Cost, latency, failure and safety before shipping",
            "Attention, and a transformer block proved correct by hand",
        ],
        "coursePrerequisites": "Python installed. No account, no API key, "
                               "no GPU and no third-party packages.",
        "numberOfCredits": 0,
        "timeRequired": "PT37H",
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD",
                   "category": "Free",
                   "availability": "https://schema.org/InStock"},
        "hasCourseInstance": {
            "@type": "CourseInstance",
            "courseMode": "online",
            "courseWorkload": "PT37H",
            "instructor": author,
        },
        "syllabusSections": syllabus,
        "codeRepository": "https://github.com/Amey-Thakur/AI-ENGINEERING",
    })


def faq_data() -> str:
    """The questions on the FAQ page, as questions."""
    body = (lesson.ROOT / "FAQ.md").read_text(encoding="utf-8")
    asked = []

    for chunk in body.split("\n## ")[1:]:
        lines = chunk.splitlines()
        question = plain(lines[0])
        answer = []

        for line in lines[1:]:
            stripped = line.strip()

            if stripped.startswith("## "):
                break

            if stripped.startswith(("<", "|", "```", "---", "> [!")):
                continue

            if stripped:
                answer.append(plain(stripped))
            elif answer:
                break

        if question.endswith("?") and answer:
            asked.append({
                "@type": "Question",
                "name": question,
                "acceptedAnswer": {"@type": "Answer",
                                   "text": " ".join(answer)},
            })

    if not asked:
        return ""

    return as_script({"@context": "https://schema.org", "@type": "FAQPage",
                      "mainEntity": asked})


def glossary_data() -> str:
    """Every term the course defines, as terms."""
    body = (lesson.ROOT / "GLOSSARY.md").read_text(encoding="utf-8")
    terms = []

    for line in body.splitlines():
        if not line.startswith("| ["):
            continue

        cells = [cell.strip() for cell in line.strip("|").split("|")]

        if len(cells) < 3:
            continue

        name = plain(cells[0])
        definition = plain(cells[2])

        if not name or not definition:
            continue

        entry = {"@type": "DefinedTerm", "name": name,
                 "description": definition}
        aliases = [plain(part) for part in cells[1].split(",") if part.strip()]

        if aliases:
            entry["alternateName"] = aliases

        terms.append(entry)

    if not terms:
        return ""

    return as_script({
        "@context": "https://schema.org",
        "@type": "DefinedTermSet",
        "name": "AI Engineering glossary",
        "description": "Every term this course uses, the names it is usually "
                       "given elsewhere, and the lesson that measures it.",
        "url": SITE + "glossary/",
        "hasDefinedTerm": terms,
    })


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
             "  - Curriculum: curriculum.md",
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
        raw = origin.read_text(encoding="utf-8")
        body = rewrite(raw, source, where)
        body = body.replace(CENTRED, OPTED_IN)

        # Its own description, taken from its own opening, so that no two
        # pages arrive at a search engine looking like the same page.
        written = WRITTEN_DESCRIPTIONS.get(target)
        front = [f"description: "
                 f"{json.dumps(written or describe(raw, SUMMARY))}",
                 # The file this page was built from, so the edit button
                 # offers the lesson rather than a new, empty index.md.
                 f"source_url: "
                 f"{json.dumps(EDIT + SOURCE_OVERRIDES.get(target, source))}"]

        if target == "index.md":
            front.append(f"title: {json.dumps(LANDING_TITLE)}")

        landing.write_text("---\n" + "\n".join(front) + "\n---\n\n" + body,
                           encoding="utf-8", newline="\n")

    shutil.copytree(ASSETS, DOCS / "assets", dirs_exist_ok=True)
    (DOCS / "assets" / "palette.css").write_text(PALETTE, encoding="utf-8",
                                                 newline="\n")
    (DOCS / "assets" / "progress.js").write_text(PROGRESS, encoding="utf-8",
                                                 newline="\n")

    # The card a shared link shows. The same file GitHub serves, so a link to
    # the site and a link to the repository look alike.
    card = lesson.ROOT / ".github" / "social-preview.png"

    if card.exists():
        shutil.copyfile(card, DOCS / "assets" / "social-preview.png")

    overrides = lesson.ROOT / "overrides"
    overrides.mkdir(exist_ok=True)
    head = (OVERRIDE.replace("__COURSE__", course_data(where))
            .replace("__FAQ__", faq_data())
            .replace("__GLOSSARY__", glossary_data()))
    (overrides / "main.html").write_text(head, encoding="utf-8",
                                         newline="\n")
    partials = overrides / "partials"
    partials.mkdir(exist_ok=True)
    (partials / "actions.html").write_text(ACTIONS, encoding="utf-8",
                                           newline="\n")

    # A crawler looks for both of these at the root and neither existed.
    (DOCS / "robots.txt").write_text(ROBOTS, encoding="utf-8", newline="\n")
    guide = lesson.ROOT / "llms.txt"

    if guide.exists():
        shutil.copyfile(guide, DOCS / "llms.txt")

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
