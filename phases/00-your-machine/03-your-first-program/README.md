# 3. Your first program

> **A program is a text file.**
>
> That is the entire secret, and it is deliberately unglamorous. Everything
> else in this course, every model and every agent, is that same fact with
> more lines in the file.

**You will:** write a file, make the computer run it, break it on purpose, and read the error properly.

**You need:** [lesson 2](../02-files-and-paths/).

<br>

## A program is a text file

There is no magic in the file. It is text. You write instructions in it, one per line, and the computer does them from top to bottom.

The only thing that makes it a program is that you hand it to something that knows how to read it. That is what `python` is: a program whose job is to read your file and do what it says.

```
python hello.py
```

Reads as *Python, read hello.py and do it.*

<br>

## Write one

Open a text editor. Notepad works. TextEdit works if you set Format to Make Plain Text. [VS Code](https://code.visualstudio.com/) is free and is what most people in this field use, and it will offer to install a Python extension the first time you open a `.py` file, which is worth accepting.

Type this and save it as `hello.py` inside `.work`:

```python
name = "AI Engineering"
print(f"{name} has {len(name)} characters")
```

Then run it:

```
python .work/hello.py
```

Four ideas are in those two lines.

**A variable** is a name for a value. `name = "AI Engineering"` means *from now on, `name` means that text*. The `=` is not equality. It is assignment, an instruction to store.

**A string** is text, in quotes. The quotes are how Python knows where the text starts and stops, which is why a missing one breaks everything after it.

**A function** is a thing that takes something and gives something back. `len(name)` hands `name` to `len`, which answers with how long it is.

**An f-string** is a string with holes in it. The `f` before the quote lets you put `{name}` and `{len(name)}` inside, and Python fills them in. Without the `f` you would get the braces printed literally, which is a good mistake to make once.

`print` puts the result on the screen. Without it the program still computes, silently, and you see nothing. A surprising amount of early confusion is a program that worked and never said so.

<br>

## Try this

> [!NOTE]
> ```
> python -c "import this"
> ```
>
> Nineteen lines of guidance that have been hidden inside every copy of
> Python for more than twenty years. *Simple is better than complex. Readability counts.*
> They are worth reading now and worth reading again in a year, when you
> have written enough code to disagree with one of them.

<br>

## Break it on purpose

Delete the closing quote after `AI Engineering` and run it again. You get something like:

```
  File "hello.py", line 1
    name = "AI Engineering
           ^
SyntaxError: unterminated string literal (detected at line 1)
```

> [!IMPORTANT]
> Read an error backwards. Python writes the useful part last, so the
> final line is what went wrong and the line above it is where.

- **`SyntaxError: unterminated string literal`** is what is wrong. A string was opened and never closed.
- **`line 1`** is where.
- **`^`** points at the character it lost patience at.

That shape never changes. The last line says what, the line above says where. When you are stuck at two in the morning in a year's time, it will still be the last line that matters, and you will read it first because you started reading it first here.

<br>

## Your turn

1. Make `.work/hello.py` with the two lines above.
2. Run it. You should see `AI Engineering has 14 characters`.
3. Break it, run it, read the error, fix it. Do this at least once on purpose, so that the first time you see a traceback is not the first time something matters.

<br>

## What the solution prints

<!-- output: solve.py -->
```text
Wrote .work/hello.py
Running it printed: AI Engineering has 14 characters
```
<!-- end output -->

<br>

## Check yourself

From the repository root:

```
python tools/run_lessons.py phases/00-your-machine/03-your-first-program
```

The check runs your file and reads what it prints, so it is checking your program, not a copy of the answer.

<br>

## Going further

Optional, and there is no check for it.

Change the program to count words rather than characters. You will need
`name.split()`, which cuts the text wherever there is a space and hands
back a list of the pieces, and `len` on that list. Two functions, working
on each other's output, is most of programming.

<br>

## What you learned

- A program is a text file, and `python file.py` is you asking Python to read it.
- `=` stores a value under a name.
- A function takes something and gives something back. `len` gives a length.
- An f-string has holes that Python fills in.
- Without `print`, work happens and nothing is said.
- An error's last line is what went wrong, the line above is where.

**Next:** [4. An isolated environment](../04-an-isolated-environment/), which is the habit that stops two projects breaking each other.
