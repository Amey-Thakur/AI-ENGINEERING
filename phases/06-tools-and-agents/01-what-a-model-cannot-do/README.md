# 1. What a model cannot do

> **Ask the model what 47 times 13 is.**
>
> It cannot answer. Not "answers badly", not "is often wrong". There is no
> digit anywhere in its vocabulary, so the string `611` is not a thing it is
> able to emit, at any temperature, ever.

**You will:** measure a gap the model cannot close, then close it with three small programs, and notice that two of them are a different species from the third.

**You need:** [phase 5](../../05-finding-the-right-thing-to-say/).

<br>

## Thirty questions in three kinds

`tasks.tsv` holds thirty questions, each labelled with what would answer it:

```
what is 47 times 13                  calculate    611
how many letters are in deployment   count        10
how long does the test suite take    search       the test suite takes twelve minutes to run
```

Twenty of those thirty answers contain something the model has never seen. It is not a matter of the model being small: **the corpus contains zero digits**, so two thirds of these answers are outside what it can say.

> [!IMPORTANT]
> This is the honest version of "language models are bad at arithmetic". They
> are not bad at it, they are not doing it. A model produces likely
> continuations of text, and the likely continuation of *what is 47 times 13*
> is whatever followed similar text in training. Whether that string happens
> to be the product of two numbers was never part of the objective.
>
> Large models get arithmetic right more often because they have seen far more
> of it, not because anything in them multiplies.

<br>

## Three tools

```python
def calculate(question):
    words = question.split()
    first, last, operation = int(words[2]), int(words[-1]), words[3]
    ...

def count(question):
    return str(len(question.split()[-1]))
```

A **tool** is just a function the system can call instead of guessing. There is nothing more to the concept, and the plainness is the point: the useful thing about a tool is that it is not a model.

The third tool is phase 5's search, unchanged.

<br>

## Your turn

Run each tool on the questions marked for it, and write `.work/results.tsv`:

```
tool           right    asked
model alone    0        30
calculate      10       10
count          10       10
search         9        10
```

<br>

## What the solution prints

<!-- output: solve.py -->
```text
The model's vocabulary is 608 words, of which 0 contain a digit.
20 of the 30 answers contain something it has never seen, so it could not produce them at any temperature.

  tool         right        exact?
  model alone   0 of 30   no
  calculate    10 of 10   yes
  count        10 of 10   yes
  search        9 of 10   no

With the right tool for each question: 29 of 30

  search got 'what did the code review catch' wrong
    gave:  a comment explains why and the code explains what
    wanted: the code review caught the missing index
```
<!-- end output -->

<br>

## Two kinds of tool, and the difference matters enormously

| Tool | Right | Can it be wrong? |
| --- | --- | --- |
| calculate | 10 of 10 | **No** |
| count | 10 of 10 | **No** |
| search | 9 of 10 | Yes |

`calculate` is not right 100% of the time in the way a good model is right 100% of the time on a test set. It is right because multiplication is right. Run it a million times on a million machines and it will not drift.

`search` got 9 of 10. It is a tool in the sense that it is a function you call, and it is a model in the sense that it has an error rate, a failure mode and a ceiling. Phase 5 measured all three.

> [!TIP]
> When you inventory a system's tools, sort them into exact and approximate,
> and treat the two completely differently. Exact tools need testing once.
> Approximate tools need measuring continuously, and they need a plan for
> being wrong.
>
> Systems get into trouble by forgetting which is which: wrapping a search or
> a classifier in a function signature and then trusting its output the way
> you would trust arithmetic.

<br>

## And 29 of 30 is not the real score

With the right tool picked for every question, the system answers 29 of 30. That number is doing something dishonest, and the next lesson is about it.

**A person chose the tool.** The label was in the file. Nothing in the system worked out that *what is 47 times 13* needs the calculator, and that choice is the entire difficulty of building with tools.

<br>

## Check yourself

```
python tools/run_lessons.py phases/06-tools-and-agents/01-what-a-model-cannot-do
```

The check insists the two exact tools are perfect, because an exact tool that misses has a bug, not a limitation.

<br>

## Going further

Optional, and there is no check for it.

Give `calculate` the question *what is 1024 divided by 7*. It returns 146, silently dropping the remainder, because the code says `//`. Nothing is broken and nobody is told. Exact tools are only exact about the thing they actually compute, and the gap between that and what the caller assumed is where they hurt you.

<br>

## What you learned

- A language model cannot produce tokens outside its vocabulary, so some answers are impossible rather than unlikely.
- Models do not do arithmetic; they continue text, and correct arithmetic is a coincidence of having seen enough of it.
- A tool is any function the system can call instead of guessing.
- Exact tools cannot be wrong; approximate ones have error rates and need the same measurement as any model.
- Confusing the two is how systems come to trust a classifier the way they trust multiplication.
- 29 of 30 was achieved with a human choosing the tool, which is the part that is hard.

**Next:** [2. Choosing the tool](../02-choosing-the-tool/), where the system has to work out for itself which one to reach for.
