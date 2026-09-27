# 4. An isolated environment

> **One day you will install something for a new project and an old one will break.**
>
> You changed nothing in the old project. It will still be broken. This
> lesson is twenty minutes now against the afternoon that costs you later.

**You will:** understand why installing a library can break a project you were not touching, and build the wall that prevents it.

**You need:** [lesson 3](../03-your-first-program/).

<br>

## The problem this solves

You build something in March that needs a library at version 1. In June you start something else that needs the same library at version 2. You install version 2. The March project breaks, on a machine where you changed nothing in it.

This happens because installing a library puts it in one shared place for the whole computer, so every project sees the same one, and two projects that want different versions cannot both be satisfied.

You will read advice to "just install it globally". It works until the day it costs you an afternoon, and that day always comes.

<br>

## The wall

A **virtual environment** is a folder that holds its own copy of Python and its own packages. A project that uses one is sealed off: what you install there is invisible everywhere else, and what someone else installed globally is invisible to it.

Make one:

```
python -m venv .venv
```

Read it as *Python, run the module called venv, and put the result in a folder called .venv*.

Then switch your terminal over to it:

| System | Command |
| --- | --- |
| Windows PowerShell | `.venv\Scripts\Activate.ps1` |
| Windows cmd | `.venv\Scripts\activate.bat` |
| macOS and Linux | `source .venv/bin/activate` |

Your prompt changes to show `(.venv)`. From now on in this terminal, `python` and `pip` mean the ones inside that folder. Type `deactivate` to leave.

<br>

## The trap everyone falls into

> [!WARNING]
> **Activation lasts only in the terminal where you did it.** Open a second
> terminal and it is not active there. Close the window and it is gone.
> When a package you definitely installed is suddenly missing, this is
> almost always the reason.

So when a package you definitely installed is suddenly not found, the first question is not "did the install fail". It is "am I in the environment". Ask your terminal which Python it is about to use:

| System | Command |
| --- | --- |
| Windows | `where python` |
| macOS and Linux | `which python` |

If the answer does not have `.venv` in it, that is your bug.

<br>

## Try this

> [!NOTE]
> With the environment active, run:
>
> ```
> python -c "import sys; print(sys.prefix)"
> ```
>
> Then `deactivate` and run exactly the same line again. The answer changes.
> Nothing about the command changed, and nothing about your machine changed.
> The only thing that changed is which Python the word `python` now means,
> which is the entire trick a virtual environment is built on.

<br>

## Writing down what you installed

```
pip install requests
pip freeze > requirements.txt
```

`pip freeze` prints every package with its exact version, and `>` puts that in a file, which you met in lesson 1. Someone else can then reproduce your setup exactly:

```
pip install -r requirements.txt
```

This is the difference between "it works on my machine" and a project someone else can run. It costs one line.

<br>

## Two rules

> [!CAUTION]
> **Never commit `.venv`.** It is large, it is specific to your machine,
> and it is rebuildable from `requirements.txt` in seconds. This
> repository's `.gitignore` already excludes it.

**One environment per project.** They are cheap. Delete the folder to throw one away.

<br>

## Your turn

From inside this lesson's folder:

1. `python -m venv .work/.venv`
2. Activate it with the line for your system, adjusting the path.
3. Run `which python` or `where python` and read where it points now.
4. `deactivate`, then run it again, and watch it point back.

<br>

## What the solution prints

<!-- output: solve.py -->
```text
Created .work/.venv
The environment has its own Python: yes
Its Python is not the one that made it: yes
```
<!-- end output -->

<br>

## Check yourself

From the repository root:

```
python tools/run_lessons.py phases/00-your-machine/04-an-isolated-environment
```

If `python -m venv` fails on Debian or Ubuntu, install the piece the distribution leaves out: `sudo apt install python3-venv`.

<br>

## Going further

Optional, and there is no check for it.

Make a second environment beside the first. Activate one, and ask it what
it can see. Activate the other and ask again. They know nothing about each
other, which is precisely what you are paying for.

<br>

## What you learned

- One shared install means two projects can want versions that cannot both exist.
- A virtual environment is a folder with its own Python and its own packages.
- `python -m venv .venv` makes one, activation switches your terminal into it.
- Activation is per terminal, and forgetting that is the most common cause of a package that is installed and cannot be found.
- `pip freeze > requirements.txt` turns your setup into something another person can rebuild.
- Never commit the folder.

**Next:** [5. Git and your copy](../05-git-and-your-copy/), the last thing you need before the course proper.
