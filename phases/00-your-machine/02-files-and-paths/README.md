# 2. Files and paths

> **Ask a working engineer what wasted their afternoon last week.**
>
> A surprising share of the time the answer is a path: a file that was
> there, a program that looked somewhere else, and forty minutes spent
> on the wrong question. Ten minutes here buys those afternoons back.

**You will:** read a path the way the computer reads it, move around with `cd`, and make a folder inside a folder.

**You need:** [lesson 1](../01-the-terminal/).

<br>

## Everything is in a tree

Your files are not in a pile. They are in a tree, and every file has exactly one place in it.

```
/
└── Users
    └── you
        ├── Desktop
        └── Projects
            └── AI-ENGINEERING
                └── phases
                    └── 00-your-machine
                        └── 02-files-and-paths
                            └── README.md
```

Writing out that whole route is a **path**. On macOS and Linux the parts are joined with `/` and the tree starts at `/`. On Windows they are joined with `\` and the tree starts at a drive such as `C:\`. That is the only real difference, and it is the reason a path copied from someone else's machine often does not work on yours.

<br>

## Absolute and relative

There are two ways to say where something is, and they are the same two ways you use in a city.

**Absolute** is the full address, starting from the top of the tree. `/Users/you/Projects/AI-ENGINEERING/README.md`. It means the same thing typed from anywhere.

**Relative** is directions from where you are standing. `phases/00-your-machine` means *from here, go into phases, then into 00-your-machine*. It only means something if you know where "here" is, which is why `pwd` matters.

Three pieces of shorthand appear in almost every relative path:

| Shorthand | Means |
| --- | --- |
| `.` | here, the folder you are in |
| `..` | one folder up, towards the top of the tree |
| `~` | your home folder, on macOS and Linux |

So `../01-the-terminal` means *go up one, then into 01-the-terminal*, which from this folder is the previous lesson. You will type `..` for the rest of your life.

<br>

## Moving

`cd` changes the directory you are standing in. It is the command you will use most.

```
cd phases
cd ..
cd phases/00-your-machine
```

Three habits that save hours:

- `cd` with nothing after it takes you home.
- Press Tab while typing a name and the terminal finishes it for you. If it refuses, the thing you are typing does not exist, and you have found a spelling mistake without running anything.
- Put quotes around a path with a space in it: `cd "My Projects"`. Without quotes the terminal reads it as two separate arguments, which is the cause of most "file not found" errors on a path that is plainly right there.

<br>

## Making things

```
mkdir notes
```

makes a folder called `notes` inside the folder you are in. `mkdir` works the same on all three systems.

To make a folder inside a folder that does not exist yet, ask for the whole route at once:

| System | Command |
| --- | --- |
| Windows | `mkdir .work\notes` |
| macOS and Linux | `mkdir -p .work/notes` |

<br>

## Try this

> [!NOTE]
> Run `cd ..` over and over, checking `pwd` each time. Eventually it stops
> moving. You have hit the root of the tree, the one folder with nothing
> above it, and every file on the machine is somewhere beneath where you are
> standing. Then get home in one step with `cd ~` on macOS or Linux, or
> `cd ~` in PowerShell.

<br>

## Why a path in an error is good news

When something fails, it usually prints a path. That path is the most useful part of the message, because it says exactly where the program looked. Nine times out of ten the file is real and the program was standing somewhere else, and `pwd` tells you that in one line.

> [!NOTE]
> A name starting with a dot, such as `.work`, is hidden from an ordinary
> listing. It is not secret and nothing is wrong. `ls -a` shows it on macOS
> and Linux, `dir /a` on Windows. This course keeps everything you produce
> in `.work`, so your experiments never get mixed up with the lesson.

<br>

## Your turn

From inside this lesson's folder:

1. Run `pwd` and read the answer. That is where you are.
2. Make a folder inside a folder: `.work/notes`.
3. Put a file in it called `day-one.txt` containing one line of text.
4. Go up two folders with `cd ../..`, run `pwd` again, and see that you moved.

<br>

## What the solution prints

<!-- output: solve.py -->
```text
Made .work/notes/day-one.txt
This lesson, written from the repository root: phases/00-your-machine/02-files-and-paths
The repository root is 3 folders above this one
```
<!-- end output -->

That third line is the same fact as `../../..`, counted out.

<br>

## Check yourself

From the repository root:

```
python tools/run_lessons.py phases/00-your-machine/02-files-and-paths
```

<br>

## Going further

Optional, and there is no check for it.

Go home with `cd ~`, then get back to this lesson using a relative path
only, with no `~` and no absolute path. It is fiddly on purpose. Doing it
once is what makes relative paths stop being abstract.

<br>

## What you learned

- Every file sits in one place in a tree, and a path is the route to it.
- Absolute paths start at the top and work anywhere. Relative paths start where you are standing.
- `.` is here, `..` is up one, `~` is home.
- `cd` moves, Tab completes and quietly checks your spelling, quotes rescue paths with spaces.
- A path in an error message is telling you where the program looked, which is usually the answer.

**Next:** [3. Your first program](../03-your-first-program/), where you write a file and make the computer run it.
