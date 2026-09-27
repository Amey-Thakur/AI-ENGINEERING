# 1. The terminal

> **Why does every serious tool in this field still hand you a line of text to type?**
>
> Not nostalgia. A line can be written down, sent to someone, pasted into a
> bug report and repeated exactly a year later. A sequence of clicks cannot.
> That is the whole reason the terminal outlived the mouse.

**You will:** open a terminal, run three commands, read what comes back, send the answer to a file, and install Python.

**You need:** a computer. Nothing else.

<br>

## What a terminal is

A terminal is a window where you type the name of a program and press Enter, and the program runs. That is the whole idea.

The buttons in any other application are doing the same thing with a picture in front of it. The terminal removes the picture. This is worth learning for one reason: almost every tool in this field is offered to you as a line to type, and a line can be written down, shared, and repeated exactly. A sequence of clicks cannot.

You will not memorise commands. You will look them up for the rest of your life. What you are learning here is what the pieces are, so that a line someone hands you stops being a spell.

<br>

## Open one

**Windows.** Press the Windows key, type `powershell`, press Enter.

**macOS.** Press Command and Space, type `terminal`, press Enter.

**Linux.** Press Ctrl, Alt and T together. If that does nothing, look for Terminal in your applications.

A window opens with some text and a blinking cursor. The text before the cursor is the **prompt**. It is the terminal saying it is ready. Yours will not look like anyone else's, and that does not matter.

<br>

## Three commands

Type each one and press Enter.

**Where am I.**

| System | Command |
| --- | --- |
| Windows | `pwd` |
| macOS and Linux | `pwd` |

It prints one line: the folder you are in right now. A terminal is always somewhere. That place is called the **working directory**, and commands act on it unless you tell them otherwise.

**What is here.**

| System | Command |
| --- | --- |
| Windows | `dir` |
| macOS and Linux | `ls` |

It lists what is in the working directory.

**What version.**

```
python --version
```

This asks a program to say what it is. If Python is installed you get something like `Python 3.12.4`. If it is not, you get an error, which is the next thing to learn to read.

<br>

## Reading an error

An error is not a punishment. It is the most useful output a program produces, because it names the thing that is wrong. The one you are most likely to see now is some version of:

```
python: command not found
```

or on Windows:

```
'python' is not recognized as an internal or external command
```

Both say the same thing in different words: *I looked for a program called python and there is not one.* Not "you broke it". Not "something went wrong". A specific, fixable fact.

That is how to read every error you meet from here on. Find the noun. The noun tells you what is missing or wrong, and the rest is context.

<br>

## Install Python

Every check in this course is a small Python program, so this is the one install you cannot skip.

**Windows.** In the terminal:

```
winget install Python.Python.3.12
```

> [!IMPORTANT]
> Close the terminal and open a new one afterwards. A terminal reads its
> settings when it starts, so it does not know about a program installed
> after it opened. This is the single most common reason an install that
> worked appears not to have.

**macOS.** If you have Homebrew, `brew install python`. If you do not, download the installer from [python.org/downloads](https://www.python.org/downloads/) and run it.

**Linux.** `sudo apt install python3 python3-venv` on Debian or Ubuntu. Your distribution's package manager otherwise.

Now ask again:

```
python --version
```

> [!TIP]
> On macOS and Linux you may need `python3 --version`. Both are fine.
> Wherever this course writes `python`, use whichever one answers on your
> machine.

You are looking for **3.10 or higher**. If you get 3.9 or lower, install a newer one before going on.

<br>

## Try this

> [!NOTE]
> Run this, exactly as written:
>
> ```
> python -c "print(2 ** 1000)"
> ```
>
> That is two multiplied by itself a thousand times, printed instantly, all
> 302 digits of it. Most languages cannot do that: their whole numbers stop
> at about nineteen digits and quietly wrap around. Python's do not have a
> ceiling at all. The `-c` flag means *run this line and exit*, which is how
> you ask Python a question without making a file first.

<br>

## Sending output somewhere

One more piece of syntax, because it turns the terminal from a place you read into a place you produce things.

The `>` character takes what a command would have printed and puts it in a file instead.

| System | Command |
| --- | --- |
| Windows | `dir /b > .work\here.txt` |
| macOS and Linux | `ls -1 > .work/here.txt` |

Nothing is printed, because the output went into the file. That is the point.

<br>

## Your turn

From inside this lesson's folder:

1. Make a folder called `.work` if it is not already there: `mkdir .work`
2. Send a plain listing of this folder into `.work/here.txt`, using the command for your system above.
3. Open the file and look at it. `type .work\here.txt` on Windows, `cat .work/here.txt` on macOS and Linux.

`README.md` should be one of the lines.

<br>

## What the solution prints

`solve.py` does exactly what you just did, running the real command for whichever system it finds itself on. It prints:

<!-- output: solve.py -->
```text
Listing written to .work/here.txt
README.md present in the listing: yes
```
<!-- end output -->

<br>

## Check yourself

From the repository root:

```
python tools/run_lessons.py phases/00-your-machine/01-the-terminal
```

`pass` means your terminal works, Python is installed, and you can put the output of a command into a file. That is a real foundation, and most people never lay it.

<br>

## Going further

Optional, and there is no check for it.

Find out which shell you are actually using. `echo $SHELL` on macOS and
Linux, `$PSVersionTable` in PowerShell. There are several, they differ in
small ways, and knowing which one is answering you explains why a command
from a blog post sometimes behaves differently on your machine.

<br>

## What you learned

- A terminal runs the program you name, in the folder you are standing in.
- `pwd` says where you are, `dir` or `ls` says what is there, `--version` asks a program to identify itself.
- An error names a missing thing. Read it for the noun.
- `>` redirects output into a file.
- Your Python is 3.10 or higher, and you proved it rather than assumed it.

**Next:** [2. Files and paths](../02-files-and-paths/) explains where things actually live, so that a path in an error message stops being a wall of text.
