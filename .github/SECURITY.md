<!--
File: .github/SECURITY.md
Purpose: Say what the attack surface of this repository actually is.
Description: Most security policies are written for software that runs
  somewhere and talks to something. This one runs on the reader's laptop with
  the network closed, so the honest policy is mostly a description of why
  there is very little here, followed by the small number of things that would
  genuinely matter.
License: MIT
Author: Amey Thakur (https://github.com/Amey-Thakur)
-->

# Security

## What this repository is

Forty-five Python files that read small text files in the same directory and print to standard output. No lesson opens a socket, writes anywhere except its own `.work/` directory, or imports anything beyond the Python standard library.

The one exception is [phase 0](../phases/00-your-machine/), whose subject is the terminal, Git and virtual environments, so five of its lessons necessarily call `subprocess` to run a command and read what came back. No lesson in phases 1 through 8 does.

Those are not claims to take on trust. [`tools/check_imports.py`](../tools/check_imports.py) fails the build on any import from outside the standard library, and [`tools/guard/sitecustomize.py`](../tools/guard/) binds `socket.connect`, `connect_ex` and `create_connection` to a function that refuses, so a lesson that reaches for the network fails on the push that introduced it.

So the realistic attack surface is small, and saying so is more useful than a page implying otherwise.

<br>

## What is worth reporting

**Anything in a lesson that touches the filesystem outside its own directory.** A path built from a variable, a write above `.work/`, a `..` in a path, an `open()` in write mode on something vendored. None of these should exist, and one appearing would be a real defect rather than a style question.

**Anything that executes text.** No file anywhere in the repository uses `eval`, `exec`, `pickle`, `os.system` or `__import__`. A lesson in phases 1 through 8 calling `subprocess` is also a defect, since nothing in those phases has a reason to.

**A credential, key, token or personal detail anywhere in the repository**, including in a data file or a commit message. [`phases/08-.../private.txt`](../phases/08-shipping-cost-latency-failure-safety/private.txt) contains eight deliberately fake sentences used to teach a lesson about retrieval leaking secrets, and `hunter2` is a joke placeholder. Anything that is not obviously fabricated in that way should be reported.

**A workflow permission that is wider than it needs.** [`checks.yml`](workflows/checks.yml) requests `contents: read` and nothing else. An addition that requests write access, or that runs a third-party action on pull requests from forks, deserves a second look.

<br>

## What is not a vulnerability here

- A lesson teaching something insecure **on purpose**. [Phase 8 lesson 4](../phases/08-shipping-cost-latency-failure-safety/04-what-it-must-not-say/) demonstrates a retrieval system handing out an API key, and that is the lesson. If a lesson looks alarming, read the README next to it before reporting it.
- The models being weak, wrong, or easy to fool. That is measured throughout and is the subject of phases 7 and 8.
- A dependency advisory, since there are no dependencies.

<br>

## How to report

For anything in the two lists above that is not a deliberate teaching example, use GitHub's private vulnerability reporting on this repository, or email **ameythakur20@gmail.com** with `AI-ENGINEERING` in the subject.

Please include the file, the line, and what you think it does. A one-line reproduction is worth more than a long description.

There is no bounty. There is a credit in the commit and, if you want one, a mention in the lesson.

<br>

## Response

This is one person's repository, not a product with an on-call rota, so the honest commitment is modest and real rather than generous and imaginary:

- An acknowledgement within **seven days**.
- For anything in the reportable list, a fix or a written explanation of why it is not one within **thirty days**.
- No disclosure timeline demanded of you. If something is wrong the material should be fixed, and there is no user data to breach while that happens.
