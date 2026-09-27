# 3. Let it learn

> **In lesson 2 you chose the words. That was the intelligence, and it was yours.**
>
> Here you hand that job over. You will not tell the program which words matter.
> You will give it a way to be wrong and a rule for what to change when it is,
> and let it find them. That exchange is the whole idea behind every model you
> have heard of.

**You will:** write a learning loop, watch the mistakes fall, and see the program rediscover what you worked out by hand.

**You need:** [lesson 2](../02-a-rule-by-hand/).

<br>

## Give every word a number

Instead of a list of words that count, every word gets a **weight**: a number saying how much it argues for question, or against.

To judge a message, add up the weights of the words in it.

```python
total = bias
for word in words:
    total += weights.get(word, 0)
```

If the total comes out above zero, call it a question. Below, a statement.

The **bias** is one extra number added to every message regardless of its words. It is how the model expresses "in the absence of evidence, lean this way", and without it a model can only ever say something when it recognises a word.

> [!NOTE]
> This is a **linear model**. Multiply each feature by a weight, add them up,
> compare with a threshold. Every neural network in this course is built from
> this, stacked and bent. Not something more complicated: this, repeated.

<br>

## Start at nothing

Every weight begins at zero. The model starts with no opinions at all, which means it gets everything wrong at first, which is exactly what it needs to learn from.

<br>

## The rule for being wrong

Walk the messages one at a time. Guess. If the guess is right, change nothing.

If it is wrong, move every word in that message towards the answer it should have given:

```python
target = 1 if label == "question" else -1       # +1 or -1, so being wrong has a direction

if guess != target:
    for word in words:
        weights[word] = weights.get(word, 0) + target
    bias += target
```

That is it. That is the entire learning algorithm, and it is called the **perceptron rule**, from 1958.

Read what it does. A word sitting in a message you got wrong gets pushed. A word that is never in a mistake never moves. So words doing real work drift steadily in one direction, while words that are simply common get pushed both ways and end up near zero.

> [!IMPORTANT]
> Nothing in that loop knows what a question is. It knows only that it was
> wrong and which direction to move. Every model in this field learns this way:
> a measure of wrongness, and a rule for what to change because of it.

<br>

## Go round more than once

One pass is not enough. A weight fixed early gets undone by a later message, so you go over the data again, and again, until the mistakes stop falling. Each pass is called an **epoch**.

<br>

## Your turn

Train it, then write `.work/weights.tsv`:

```
word         weight
__bias__     -2
what         3
the          -1
```

The check builds a classifier from your file and scores it. It needs **90%**.

<br>

## What the solution prints

<!-- output: solve.py -->
```text
Learned 165 weights in 10 passes
Mistakes per pass: 44, 12, 10, 4, 6, 4, 2, 2, 2, 2
Right on the data it learned from: 59 of 60, 98.3%

Words it decided mean question:
  do           +4
  does         +4
  these        +3
  who          +3
  working      +3
  can          +2

Words it decided mean statement:
  works        -3
  ran          -2
  revert       -2
  those        -2
  unclear      -2
  with         -2
```
<!-- end output -->

<br>

## Three things in that output

**The mistakes fall, and then stop falling.** Forty-four, then twelve, then ten, and down to two, where it sits. It never reaches zero. With these features the two kinds cannot be perfectly separated, and the loop is honest enough to keep telling you so rather than pretending.

**It rediscovered your words.** Nobody told it about *do*, *does*, *can* or *who*. It found them by being wrong and adjusting, and it agrees with the table you built by hand in lesson 1. That agreement is worth pausing on, because it is the first evidence that the method is finding something real.

**And it learned some nonsense.** *These*, *working*, *those*, *revert*, *unclear*. None of those means anything about questions. They landed in a few messages the model happened to get wrong early, got pushed, and never got pushed back, because they are too rare to come up again.

> [!WARNING]
> Look at that score again: **98.3%**, better than your hand written rule.
>
> It is not a real number. The model was measured on the same sixty messages it
> learned from, so it has already seen every answer. Some of that 98.3% is
> understanding and some is memory, and nothing here can tell you how much.
>
> That is the next lesson, and it is the most important one in the phase.

<br>

## Check yourself

```
python tools/run_lessons.py phases/01-teach-it-to-tell-two-things-apart/03-let-it-learn
```

<br>

## Going further

Optional, and there is no check for it.

Change `PASSES` to 1, then 3, then 50. The mistakes per pass tell a story: a big drop, a slow grind, and then nothing. Training longer stops helping well before it stops running, and knowing when to stop is a skill you will need with models that take days rather than milliseconds.

<br>

## What you learned

- A weight per feature, summed and compared with a threshold, is a linear model, and it is the piece everything later is built from.
- The bias is the model's opinion before it has seen any evidence.
- Learning is a measure of being wrong plus a rule for what to change.
- Words that do real work drift one way; common words get pushed both ways and settle near zero.
- A model can learn genuine signal and coincidence at the same time, and the weights look identical either way.
- A score measured on the data you trained with is not a score.

**Next:** [4. Tell the truth](../04-tell-the-truth/), where you find out what this model is actually worth.
