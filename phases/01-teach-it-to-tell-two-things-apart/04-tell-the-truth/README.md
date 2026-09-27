# 4. Tell the truth

> **98.3% was not a real number, and this lesson is where you find out what it cost.**
>
> If you take one thing from this entire course, take this one. More projects
> die here than at any other point, and they die confidently, with a good score
> on a slide.

**You will:** hold data back, score on it, and watch a model you were proud of lose a quarter of its accuracy.

**You need:** [lesson 3](../03-let-it-learn/).

<br>

## Why the old number was a lie

The model in lesson 3 was scored on the same sixty messages it trained on. It had already been told the answer to every one of them.

Some of that score was understanding, which will work on a message it has never met. Some of it was memory, which will not. And nothing in the number separates the two.

This has a name, and the name is doing a lot of work: **overfitting**. A model that fits the data it was given so closely that it has learned the accidents in it, not just the pattern.

Look again at what it learned: *these*, *working*, *those*, *revert*. Those are not facts about questions. They are facts about sixty particular messages.

<br>

## The fix is embarrassingly simple

Keep some data back. Train on the rest. Score on the part it never saw.

Here, the first forty messages train the model and the last twenty test it. The messages alternate question, statement, question, statement down the file, so both halves come out balanced without doing anything clever.

```python
training  = rows[:40]
held_back = rows[40:]

weights, bias = train(training)          # the last twenty do not exist here
```

> [!CAUTION]
> The held back data must not touch training in any way. Not to pick how many
> passes to run, not to choose which words to keep, not to decide when to stop.
> Every one of those leaks the answers back in, and the score quietly becomes a
> lie again. This is the most common serious mistake in applied machine
> learning, and it is usually made by accident.

<br>

## Your turn

Train on the first 40, score both halves, and write two files.

`.work/weights.tsv`, as before, from training on the first 40 only.

`.work/scores.tsv`:

```
split    right    total    accuracy
train    39       40       0.9750
test     15       20       0.7500
```

> [!NOTE]
> The check is unusual. It rebuilds your model from your weights, scores it on
> the held back messages itself, and compares that with what you reported. A
> model that scores badly still passes. A report that does not match the model
> does not. That is the right way round.

<br>

## What the solution prints

<!-- output: solve.py -->
```text
Trained on 40 messages, tested on 20 it never saw

  On what it learned from:  39 of 40   97.5%
  On what it never saw:     15 of 20   75.0%

The held back messages contain 56 words the model has no weight for.
It is deciding those messages on the words it does know, and on the bias.
```
<!-- end output -->

<br>

## The number that should stop you

**97.5% on what it learned from. 75.0% on what it never saw.**

A gap of twenty-two points. That gap is the part of the model that was memory rather than understanding, and there was no way to see it before this lesson.

Now the part that should genuinely sting. Your nine-line rule from lesson 2, the one with no learning in it at all, scores **90% on those same twenty messages**. It never saw them either.

| Model | On the held back twenty |
| --- | --- |
| The rule you wrote by hand | **90%** |
| The model that learned | 75% |

The learned model lost to nine lines of code and one afternoon of thinking about English.

> [!IMPORTANT]
> This is not an argument against learning. It is an argument against measuring
> badly, and against reaching for a model before you have a baseline to beat.
> Had you skipped lesson 2, you would have shipped the 98.3% and never known.

<br>

## Why it lost

The output names the reason: the twenty held back messages contain **56 words the model has no weight for**. It never met them, so they contribute nothing, and those messages get decided on a handful of familiar words and the bias.

Forty messages is not enough data to learn a vocabulary from. The hand written rule did not need data: it was built on a fact about English that holds everywhere, and a fact that holds everywhere does not care how much data you have.

That trade sits underneath the whole field. Knowledge you bring costs thinking and generalises. Patterns learned from data cost data and generalise only as far as the data went.

<br>

## Check yourself

```
python tools/run_lessons.py phases/01-teach-it-to-tell-two-things-apart/04-tell-the-truth
```

<br>

## Going further

Optional, and there is no check for it.

Train on the first 20 instead of 40, then on all 59 with one held back. Plot the test score against how much you trained on. The shape of that curve tells you whether your problem needs more data or a better idea, and it is the cheapest useful experiment in this field.

<br>

## What you learned

- A score on data you trained with is not a score.
- Overfitting is learning the accidents in your data along with the pattern, and it looks identical from the inside.
- Holding data back is the cheapest honest measurement there is.
- Anything that touches the held back data during training leaks the answers, including choices you make by hand.
- A simple rule built on real knowledge can beat a learned model, and you only find out if you measured the simple rule first.
- Report the number you got, not the number you liked.

**Next:** [5. When it breaks](../05-when-it-breaks/), where you stop looking at the score and start reading the failures.
