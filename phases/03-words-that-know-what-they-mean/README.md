# Phase 3. Words that know what they mean

**Five lessons. About four hours. Still nothing installed.**

Phases 1 and 2 both ended pointing at the same thing. The held back messages were full of words the model had never seen, and nothing about knowing *server* told it anything about *database*. Capacity did not fix it, because the problem was never capacity.

This phase changes what a word *is*.

<br>

## The lessons

| # | Lesson | The idea underneath it |
| --- | --- | --- |
| 1 | [The vocabulary wall](01-the-vocabulary-wall/) | One-hot words are all exactly the same distance apart |
| 2 | [The company a word keeps](02-the-company-a-word-keeps/) | Meaning can be counted, and raw counts fail |
| 3 | [Surprise is the signal](03-surprise-is-the-signal/) | Divide by chance and meaning appears |
| 4 | [Fewer numbers that say more](04-fewer-numbers-that-say-more/) | Compressing removes noise rather than detail |
| 5 | [Does it help?](05-does-it-help/) | A representation is only good for a particular task |

<br>

## The corpus

`corpus.txt`: **217 sentences of ordinary technical English**, written for this course so that nothing in it belongs to anyone else and nothing can be withdrawn.

It is small, deliberately. You can read all of it in five minutes, which means when a result looks strange you can go and find the sentences that caused it. It is also small enough to strain, and the lessons say where.

<br>

## What you will have built

Word vectors, from nothing but counting: co-occurrence profiles, weighted by how much each pairing beats chance, compressed from 608 numbers to 24 by power iteration written out by hand.

By the end, *server* is close to *memory* and *load*, *incident* is close to *postmortem* and *monitoring*, and *deploy* is close to *failed*, *version* and *staging*. Nobody wrote any of that down. It was counted.

<br>

## How it ends

With the worst result in the course so far: **55%**, against 50% for guessing and 90% for the rule you wrote in phase 1.

The diagnosis is the phase. Averaging destroyed word order, which is what this task turns on. Dense features overfit forty examples faster than sparse ones. And most importantly the vectors encode *subject matter*, while the task turns on *grammar*, so the better representation was better at the wrong thing.

> [!IMPORTANT]
> Three phases, three honest measurements, and the nine line rule is still in
> front. Each phase built something more capable than the last and each one
> failed for a reason that was specific, measurable and worth knowing.
>
> That is the actual shape of this work, and courses that hide it produce
> engineers who cannot tell a promising result from a lucky one.

<br>

## Check the phase

```
python tools/run_lessons.py phases/03-words-that-know-what-they-mean
```

**Next:** [Phase 4](../04-a-language-model-you-wrote-yourself/), where order becomes the thing the model is built around rather than the thing it throws away.
