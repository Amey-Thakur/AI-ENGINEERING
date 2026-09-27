# 5. Git and your copy

> **Git's real gift is not backup.**
>
> It is that you stop hesitating. Once a version is recorded you can delete
> the part you suspect is wrong, try the idea that probably will not work,
> and rewrite the lot, because getting back is one command. People who use
> git well are not more careful. They are less careful, on purpose.

**You will:** record a version of a folder, see the record, and understand what forking this course actually does.

**You need:** [lesson 4](../04-an-isolated-environment/).

<br>

## What git is

Git keeps a record of what a folder looked like at moments you choose. Each recorded moment is a **commit**. Once something is committed you can always get back to it, which means you can change anything without being careful about it.

That is the real benefit, and it is not backup. It is that you stop hesitating. Delete the section you think is wrong. If you were wrong about being wrong, it is one command away.

Install it if `git --version` gives you an error: [git-scm.com/downloads](https://git-scm.com/downloads), or `sudo apt install git`, or `brew install git`.

Tell it who you are, once per machine:

```
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

> [!IMPORTANT]
> Every commit carries that name. Git refuses to commit without it, which
> surprises almost everyone on their first try.

<br>

## Three places, not one

This is the part that confuses everyone, and it is worth ten minutes now rather than a month of cargo culting.

A file you are working on is in the **working tree**: the folder as it is this second.

`git add` moves a change to the **staging area**: a holding pen for what will go into the next commit. This exists so you can record two unrelated changes as two commits instead of one muddle.

`git commit` writes what is staged into the **history**, permanently, with a message.

```
git status          what is changed, and what is staged
git add notes.txt   stage that file
git commit -m "Add notes"
git log --oneline   the history, one line each
```

> [!TIP]
> `git status` is the command to type whenever you are unsure of anything.
> It describes the current state in plain language and usually names the
> exact command you want next.

<br>

## Try this

> [!NOTE]
> In any repository with some history, run:
>
> ```
> git log --oneline
> ```
>
> Every line is a moment somebody decided was worth keeping. Pick one and
> run `git show` with its short code. You are reading the exact change that
> was made, by whom, and when. Every open source project you will ever use
> can be read this way, all the way back to its first day.

<br>

## Clone and fork

**Cloning** copies a repository onto your machine. You can read it, run it, and change it locally.

```
git clone https://github.com/Amey-Thakur/AI-ENGINEERING.git
```

**Forking** makes your own copy of it on GitHub, under your account, before you clone. It is a button on the repository page.

The difference matters here for a practical reason. As you work through this course you will produce things: files you wrote, checks you passed, notes to yourself. In a clone, those live on one machine. In a fork, they are yours, on your account, visible from anywhere, and they are a record of what you did. Nobody needs to give you permission, and nothing you do can affect the original.

So: **fork it, then clone your fork.** That is the only setup instruction this course gives you.

<br>

## Your turn

From inside this lesson's folder:

1. Make a folder `.work/practice` and move into it.
2. `git init` to start a repository there.
3. Create a file with a line of text in it.
4. `git status` and read what it says about the file.
5. `git add`, then `git status` again, and notice the wording changed.
6. `git commit -m "First commit"`.
7. `git log --oneline`.

Doing steps 4 and 5 in that order is the point of the exercise. The change in wording is the staging area becoming visible.

<br>

## What the solution prints

<!-- output: solve.py -->
```text
Made a repository in .work/practice
Staged and committed notes.txt
The log shows 1 commit
```
<!-- end output -->

<br>

## Check yourself

From the repository root:

```
python tools/run_lessons.py phases/00-your-machine/05-git-and-your-copy
```

<br>

## Going further

Optional, and there is no check for it.

Change the file, then run `git diff` before you stage anything. Git prints
exactly what is different, line by line, with a `-` for what left and a `+`
for what arrived. Read a diff once and you will read every code review for
the rest of your career more quickly.

<br>

## What you learned

- A commit is a recorded moment, and having them is what lets you change things fearlessly.
- Git needs your name and email before it will commit anything.
- A change travels from the working tree, through staging with `git add`, into history with `git commit`.
- `git status` answers "what is going on" and usually names the next command.
- Cloning copies the code. Forking gives you a copy of your own, which is where your work through this course should live.

<br>

## Phase 0 complete

Run every check in the phase at once:

```
python tools/run_lessons.py phases/00-your-machine
```

Five passes means you have a terminal you can use, a Python you proved, a grasp of where files live, a program you wrote and broke and fixed, an environment habit that will save you an afternoon, and a way to record your work.

Nothing in this phase was about AI. All of it is what the rest of the course assumes, and what most courses assume without ever saying.

**Next:** [Phase 1](../../01-the-mathematics-you-need/) begins the course proper.
