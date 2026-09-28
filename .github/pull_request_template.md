<!--
File: .github/pull_request_template.md
Purpose: Make the five guarantees the first thing a contributor sees.
Description: The checklist is the contract from CONTRIBUTING.md, restated where
  it is about to be needed. It is short because a long template gets deleted.
License: MIT
Author: Amey Thakur (https://github.com/Amey-Thakur)
-->

## What this changes

<!-- One or two sentences. If it is a new lesson, say the one thing it teaches. -->

## Why

<!-- If this corrects a claim, put the measurement here. A number and how you
     got it is worth more than a paragraph. -->

<br>

## The five guarantees

```bash
python tools/run_lessons.py && python tools/check_output.py && python tools/check_imports.py && python tools/check_determinism.py && python tools/check_glossary.py
```

- [ ] Every lesson runs
- [ ] Printed output matches real output (`python tools/check_output.py --fix` is how a number gets into a README)
- [ ] Nothing outside the Python standard library is imported
- [ ] The same output on every run: no clock, no unseeded randomness, no set iteration order, no machine path
- [ ] The glossary still resolves, and a new lesson has a row in it

<br>

## If this adds a lesson

- [ ] Three files: `README.md`, `solve.py`, `check.py`
- [ ] It teaches **one** thing, and the README says what at the top
- [ ] Data is vendored into the lesson directory, not shared by reference
- [ ] `check.py` explains itself on failure in two lines: what is wrong, then what to do
- [ ] The previous lesson's **Next** link points at it, and it has its own
- [ ] Any number in the README came out of `solve.py`, not out of your head

<br>

## If this changes a claim in an existing lesson

- [ ] The old claim and the new measurement are both stated, so a reader can see what changed
- [ ] Any other lesson that cited the old number has been updated
- [ ] `phases/*/README.md` for the affected phase still says something true
