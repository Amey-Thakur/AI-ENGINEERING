# 1. Words into numbers

> **A computer cannot read. It can only count.**
>
> Every system you have heard of, every model with a name, is doing arithmetic
> on numbers that used to be text. The interesting question is not how the
> arithmetic works. It is how the text became numbers in the first place, and
> that is a decision a person makes.

**You will:** read a data file, turn sentences into counts, and find out where the signal in a problem actually lives.

**You need:** [phase 0](../../00-your-machine/).

<br>

## The problem

In this folder is `messages.tsv`: sixty short messages, half of them questions and half statements.

```
label       message
question    what time does the meeting start
statement   the meeting starts at ten
question    how do i reset my password
statement   i reset my password this morning
```

Your job across this phase is to build something that can tell the two apart. Not by asking you. By looking at the words.

> [!NOTE]
> The question marks have been removed on purpose. With them the problem is one
> line of code and teaches nothing. Without them you have to find real signal,
> which is the situation you are always in with real data.

<br>

## Reading the file

`.tsv` means tab separated values: columns with a tab between them. It is the plainest useful data format there is, and you can read it with nothing but the `open` that comes with Python.

```python
with open("messages.tsv", encoding="utf-8") as handle:
    next(handle)                     # skip the header line

    for line in handle:
        label, message = line.strip().split("\t")
```

Three things worth naming:

- **`with`** closes the file for you when the block ends, including if something goes wrong inside it. Opening a file without `with` is a habit that costs people later.
- **`encoding="utf-8"`** says how the bytes turn into characters. Leave it out and Python guesses from your operating system, which is why a file that works on your machine breaks on someone else's.
- **`.strip()`** removes the newline at the end of the line. Without it your last word on every row is `start\n`, not `start`, and nothing matches.

<br>

## Turning a sentence into something countable

```python
words = message.split()
```

`split()` with nothing in the brackets cuts on whitespace. `"what time does it start"` becomes `["what", "time", "does", "it", "start"]`.

This is called **tokenising**, and this is the naive version of it. It is worth knowing now what it gets wrong, because you will fix these later in the course:

| It cannot tell | Example |
| --- | --- |
| Case | `The` and `the` are different words to it |
| Punctuation | `start.` and `start` are different words |
| Word forms | `run`, `runs` and `running` share nothing |
| Meaning | `quick` and `fast` are as unrelated as `quick` and `tuesday` |

Our data is already lowercase with no punctuation, so the first two do not bite today. They will.

<br>

## Counting, and one decision inside it

For each word, count how many messages of each kind contain it.

```python
for word in set(words):
    counts[word][label] += 1
```

Look at `set(words)`. A set throws away duplicates, so a word said twice in one message counts once.

That is a real decision and it could go the other way. Counting every occurrence measures enthusiasm; counting messages measures how widespread a word is. For sixty short messages, widespread is the more honest signal, because one message that says "the" four times should not get four votes.

> [!IMPORTANT]
> Decisions like this one are the actual work of this field, and they are
> invisible in the finished product. Nobody writes a paper about whether to use
> a set. It changes your results anyway.

<br>

## Your turn

Write `.work/counts.tsv`, with a header row and then one row per word:

```
word        question    statement
what        4           1
the         17          19
```

Every different word in the messages needs a row. Tabs between the columns.

<br>

## What the solution prints

<!-- output: solve.py -->
```text
60 messages: 30 questions, 30 statements
172 different words

Leans towards a question:
  does          5 of the questions,  0 of the statements
  do            4 of the questions,  0 of the statements
  can           4 of the questions,  1 of the statements
  how           4 of the questions,  1 of the statements
  this          7 of the questions,  4 of the statements
  what          4 of the questions,  1 of the statements

Leans towards a statement:
  in            0 of the questions,  4 of the statements
  minutes       0 of the questions,  2 of the statements
  next          0 of the questions,  2 of the statements
  takes         0 of the questions,  2 of the statements
  the          17 of the questions, 19 of the statements
  works         0 of the questions,  2 of the statements
```
<!-- end output -->

<br>

## Read that table again

The words leaning towards a question are the ones you would have guessed, and that is reassuring rather than boring: the method found, with no help, what a person already knows.

The statement side is more interesting. Those words are not meaningfully about statements. They are just common, and there happen to be slightly more of them on that side. A system built only on the strongest signals would be trusting noise.

> [!TIP]
> This is the whole shape of the field in one table. Some of your signal is
> real, some of it is an accident of the data you happened to collect, and
> nothing in the numbers tells you which is which. Only knowing what the data
> means does.

<br>

## Check yourself

From the repository root:

```
python tools/run_lessons.py phases/01-teach-it-to-tell-two-things-apart/01-words-into-numbers
```

The check reads the messages and works the counts out for itself, then compares them with yours. It is not holding a stored answer, so you cannot pass it by copying one.

<br>

## Going further

Optional, and there is no check for it.

Count every occurrence instead of one per message, by dropping the `set()`. Which words move? Nothing about the data changed, only what you decided to measure, and the answer is different. Keep that feeling.

<br>

## What you learned

- Text becomes numbers by a decision somebody makes, not by magic.
- `with open(..., encoding="utf-8")` is how you read a file safely and portably.
- `.split()` is the naive tokeniser, and you now know four things it gets wrong.
- Counting messages rather than occurrences is a choice that changes the answer.
- Signal and coincidence look identical in a table of counts.

**Next:** [2. A rule by hand](../02-a-rule-by-hand/), where you use these counts to make an actual decision, and find out how often you are right.
