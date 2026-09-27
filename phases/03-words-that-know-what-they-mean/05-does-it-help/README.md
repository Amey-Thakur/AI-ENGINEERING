# 5. Does it help?

> **You have built something genuinely good.**
>
> *server* knows about *memory*. *incident* knows about *postmortem*. Evidence
> spreads between related words, which is precisely what phases 1 and 2 said
> was missing. So it should work.
>
> It does not, and the reasons are three mistakes that are made constantly, at
> every scale, by people who know better.

**You will:** put the vectors on the real problem, measure honestly, and diagnose a failure properly.

**You need:** [lesson 4](../04-fewer-numbers-that-say-more/).

<br>

## One vector per message

A message is several words, and each word is 24 numbers. The simplest way to get one vector for the message is to average them.

```python
known = [vectors[word] for word in message.split() if word in vectors]
return [sum(v[i] for v in known) / len(known) for i in range(DIMENSIONS)]
```

This is a real technique with a real name, **mean pooling**, and it is still used. Then train the same classifier on the same first forty messages.

<br>

## Your turn

Build the message vectors, train on the first 40, predict the last 20, and compare against the rule from phase 1.

Write `.work/predictions.tsv` and `.work/scores.tsv`:

```
measure            value
vectors_train      0.9750
vectors_test       0.5500
hand_rule_test     0.9000
```

<br>

## What the solution prints

<!-- output: solve.py -->
```text
608 words have vectors, from the corpus

  On what it learned from:  39 of 40   97.5%
  On what it never saw:     11 of 20   55.0%

On the same twenty held back messages:

  Hand written rule, phase 1      18 of 20   90.0%
  Bag of words, phase 1           15 of 20   75.0%
  Network, phase 2                15 of 20   75.0%
  Word vectors, this phase        11 of 20   55.0%

The same vectors, used three ways:

  average of every word        train 39 of 40   test 11 of 20   55%
  first word only              train 35 of 40   test 12 of 20   60%
  first word and the average   train 40 of 40   test 13 of 20   65%

Two numbers that explain it:

  Messages whose first word has a vector: 48 of 60
  Question openers appearing in the corpus at all: 18 of 21
```
<!-- end output -->

<br>

## The scoreboard, complete

| Model | Held back twenty | Built in |
| --- | --- | --- |
| **Hand written rule** | **90%** | Phase 1, lesson 2 |
| Bag of words | 75% | Phase 1, lesson 4 |
| Two layer network | 75% | Phase 2, lesson 5 |
| **Word vectors** | **55%** | This lesson |

The best representation in the course produced the worst result. Guessing scores 50%.

<br>

## Why, in three parts

### 1. Averaging throws away the thing that mattered

The task is decided by **which word comes first**. Averaging destroys order completely: *is the server down* and *the server is down* average to exactly the same vector.

This is measurable rather than arguable, and the output measures it:

| How the same vectors are used | Held back |
| --- | --- |
| Average of every word | 55% |
| First word only | 60% |
| First word **and** the average | **65%** |

Keeping one piece of order is worth ten points. Order is real signal and mean pooling discards all of it.

### 2. Dense features overfit small data far faster

97.5% on the training forty and 55% on the twenty. A wider gap than either earlier model produced.

Bag of words was sparse: most features were zero for most messages, so most weights barely moved. These 24 features are dense and non-zero for every message, so every weight tunes to every example. With forty examples, that is memorisation with the lid off.

### 3. The vectors encode topic, and the task is not about topic

This is the deep one.

Lessons 3 and 4 proved what these vectors capture: *server* near *memory*, *deploy* near *staging*, *incident* near *postmortem*. **Subject matter.**

Now look at what the task actually asks. *What time does the meeting start* and *the meeting starts at ten* are about exactly the same subject. One is a question and one is not, and the difference is grammatical.

The representation is excellent, and it is excellent at a property this task does not depend on.

> [!IMPORTANT]
> There is no such thing as a good representation in the abstract. There is
> only a representation that captures what a particular task depends on.
>
> A quick check before you invest: name the property your task turns on, then
> name the property your representation encodes. If they are not the same
> property, more of it will not help, and nothing in a validation score will
> tell you why.

<br>

## What this does not mean

It does not mean word vectors are bad, and it does not mean the phase was wasted.

Put these same vectors on a task that *is* about subject matter, "is this message about infrastructure or about scheduling", and they would beat the hand written rule easily, because that is the property they carry. The corpus never saw the sixty messages and still knows *dashboard* belongs with *server*.

The lesson is about fit between representation and task, not about the quality of either.

<br>

## Check yourself

```
python tools/run_lessons.py phases/03-words-that-know-what-they-mean/05-does-it-help
```

<br>

## Going further

Optional, and there is no check for it.

Concatenate the first word's vector, the second word's vector, and the average. Order is partly preserved and the score climbs again. Then notice what you are building: a model that handles position by giving each position its own slot, which stops working the moment sentences vary in length. Holding position properly is what the next phase is for.

<br>

## Phase 3 complete

```
python tools/run_lessons.py phases/03-words-that-know-what-they-mean
```

You proved that one-hot words are all exactly √2 apart, built profiles by counting company, weighted them by surprise until meaning appeared, squeezed 608 numbers into 24 with power iteration, and then measured honestly and found it did not help here.

Three phases have now ended with the nine line rule from phase 1 still in front. That is not a joke at your expense. It is what the measurement says, and a course that hid it would be worth less than one that shows it.

**Next:** [Phase 4](../04-a-language-model-you-wrote-yourself/), where order stops being something a model discards and becomes the thing it is built around.
