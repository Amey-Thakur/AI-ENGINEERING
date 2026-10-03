# Phase 0. Your machine

**Five lessons. About two hours. Nothing installed beforehand.**

Every other course assumes this phase. It tells you to open a terminal, clone a repository and install a package, and if you have never done those things you are already lost on page one, in a way that feels like your fault and is not.

Nothing here is about AI. All of it is what the rest of the course, and the rest of the field, silently expects you to have.

<br>

## The lessons

| # | Lesson | You end up with |
| --- | --- | --- |
| 1 | [The terminal](01-the-terminal/) | A terminal you can use, and Python installed and proved |
| 2 | [Files and paths](02-files-and-paths/) | Knowing where things are, and reading a path in an error |
| 3 | [Your first program](03-your-first-program/) | A program you wrote, broke on purpose, and fixed |
| 4 | [An isolated environment](04-an-isolated-environment/) | The habit that stops two projects breaking each other |
| 5 | [Git and your copy](05-git-and-your-copy/) | A record of your work that belongs to you |

<br>

## How a lesson works

Every lesson in this course is the same three files, so that once you have done one you know how to do all of them.

| File | What it is |
| --- | --- |
| `README.md` | The lesson. Read it first. |
| `solve.py` | The worked solution. Read it when you are stuck, or after you have finished, to compare. |
| `check.py` | The check. It looks at what you produced and tells you whether it is right, and if not, why. |

Do the work yourself, then run the check:

```
python tools/run_lessons.py phases/00-your-machine
```

> [!TIP]
> A failing check is not a scolding. Every failure in this course prints the
> reason on one line and the fix on the next. If a check ever fails without
> telling you what to do about it, that is a bug in the course and an
> [issue](https://github.com/Amey-Thakur/AI-ENGINEERING/issues) is welcome.

<br>

## When the phase is done

Run all five at once:

```
python tools/run_lessons.py phases/00-your-machine
```

Five passes and you have a working machine, proved rather than assumed. [Phase 1](../01-teach-it-to-tell-two-things-apart/) begins the course proper.
