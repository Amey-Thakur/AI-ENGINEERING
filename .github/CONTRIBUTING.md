# Contributing

Thank you for reading this far. The bar here is unusual, and it is worth
knowing what it is before you spend an evening on a lesson.

<br>

## The contract

A lesson is a directory holding exactly three files.

| File | What it must do |
| --- | --- |
| `README.md` | Teach one thing. State what the reader will do and what they need. End with what they learned and a link to what is next. |
| `solve.py` | Solve it, and be worth reading. It is the explanation for anyone who gets stuck. |
| `check.py` | Look at what the reader produced and, on failure, print the reason on one line and the fix on the next. |

<br>

## The four rules

**1. It runs everywhere, every time.** Your lesson is executed on Linux, macOS
and Windows. Derive paths rather than typing them, and never assume a
separator.

**2. It imports only from the standard library.** There is no exception to this,
including in the later phases. A neural network, an autograd engine and a
tokeniser can all be written in plain Python over small data, and writing them
is the point rather than an obstacle to it.

**3. It never touches the network.** Lessons run with connections refused. If a
lesson needs data, the data is small enough to sit in the repository.

**4. Its output is generated, not typed.** If your lesson shows what the code
prints, mark the block and let the tool fill it in:

```
<!-- output: solve.py -->
```text
```
<!-- end output -->
```

Then run `python tools/check_output.py --fix`. That is the only way a number is
allowed into the prose.

<br>

## Two more things that matter

**Re-runnable.** Running `solve.py` twice must work. A solution that only works
on a folder it has not already touched is not finished.

**Deterministic.** Same input, same output, every time. No clock, no unseeded
randomness, no machine-specific path in anything you print.

<br>

## Before you open a pull request

```
python tools/run_lessons.py
python tools/check_output.py
python tools/check_imports.py
```

All three must pass. They are the same three that run on your pull request, so
there are no surprises waiting for you.

<br>

## Writing

Short sentences. Say the thing. A reader who is stuck at eleven at night is not
looking for a personality, they are looking for the fact that unblocks them.

Explain why something is the way it is, not only what to type. A reader who
knows why can work out the next thing on their own, which is the entire point.
