# 4. A model that generalises

> **Counting can only tell you about what has already happened.**
>
> Lesson 2 proved it: the best counting model on this corpus was the one that
> ignored context entirely, because most contexts are seen once or never. The
> fix is a model that shares what it learns between similar words, and you
> already built the thing that makes words similar.

**You will:** train a language model on word vectors instead of counts, and get the first win of this entire course.

**You need:** [lesson 3](../03-making-it-talk/), [phase 2](../../02-a-network-you-wrote-yourself/), [phase 3](../../03-words-that-know-what-they-mean/).

<br>

## Why this can generalise and counting cannot

A counting model stores *the server restarted* and *the database restarted* as two unrelated facts. Seeing one teaches it nothing about the other.

Here, each word is a vector. When the model learns from *the server restarted*, it adjusts the vector for *server*. Any word whose vector is nearby is now also predicted slightly differently, **including words that never appeared in that sentence**.

The sharing is not a feature bolted on. It falls out of representing words as positions rather than slots.

<br>

## The model

One vector per word, one scoring row per word, one offset per word.

```python
scores = [sum(row[i] * vector[i] for i in range(DIMENSIONS)) + offset
          for row, offset in zip(scorers, offsets)]
```

Then turn those scores into probabilities with **softmax**: exponentiate and divide by the total.

```python
largest = max(scores)
raised = [exp(score - largest) for score in scores]
```

Subtracting the largest first changes nothing mathematically and prevents `exp` overflowing, which it will do on real numbers. Every serious implementation does this.

The gradient is remarkably clean. For softmax with this loss, the derivative with respect to each score is **the predicted probability, minus one for the word that actually came**:

```python
chances[position[second]] -= 1.0
```

One line. Everything else is phase 2's backward pass.

<br>

## Three splits, not two

Here is a problem that has been waiting since phase 1.

Training longer overfits, so you should stop early. But stopping early means choosing *when* to stop, and the obvious way is to watch the score on held back data and stop when it stops improving.

That is a decision made using the held back data. So the held back score is no longer clean: you chose the model that scores best on it, and it will flatter you.

The fix is a third split:

| Part | Sentences | What it decides |
| --- | --- | --- |
| Training | 0 to 160 | The weights |
| **Validation** | 160 to 190 | When to stop |
| **Test** | 190 to 217 | Nothing. It is only reported. |

> [!IMPORTANT]
> Anything you tune, choose or compare using a set has spent that set. How
> many layers, which learning rate, which features, when to stop: every one of
> those is a decision, and decisions leak.
>
> This is why papers report a test set they touched once, and why a team that
> has "improved the validation score" forty times has a validation score that
> means very little.

<br>

## Your turn

Train it, pick the epoch on validation, report on test. Write `.work/results.tsv`:

```
measure          value
vocabulary       101
best_epoch       4
counting_test    9.9861
neural_test      8.7598
```

<br>

## What the solution prints

<!-- output: solve.py -->
```text
vocabulary 101, 1644 pairs to train on, 304 to validate, 288 to test

  epoch   perplexity on validation
      1       8.93
      2       8.54
      3       8.42
      4       8.40   <- best
      5       8.48
      6       8.61
      7       8.74
      8       8.84
      9       8.94
     10       9.02
     11       9.09
     12       9.15

Stopped at epoch 4, chosen on validation and nothing else.

On the test part, which nothing has looked at until now:

  counting, mix 0.5     9.99
  neural                8.76
```
<!-- end output -->

<br>

## The first win

| Model | Test perplexity |
| --- | --- |
| Counting, mix 0.5 | 9.99 |
| **Neural** | **8.76** |

**12% better**, on a test set neither model was tuned against.

Four phases in, this is the first time something learned has beaten the simpler thing it was compared to. It is worth being clear about why, because it is not "neural networks are better".

It won because it can **share evidence between similar words**, and the counting model cannot. That is a specific advantage that applies when contexts are too numerous to count, which is exactly the situation language creates.

<br>

## And the overfitting is right there

Read the validation column: 8.93, 8.54, 8.42, **8.40**, 8.48, 8.61, 8.74, 8.84, 8.94, 9.02, 9.09, 9.15.

It improves for four epochs and then gets worse for eight, steadily, without ever crashing. Training loss was falling the whole time.

> [!WARNING]
> Nothing in the training process announces this. Loss on the training data
> improved every single epoch. The only way to know that epoch 5 was worse
> than epoch 4 is to have measured on data the model was not fitting.
>
> A model trained "until the loss stops improving" is a model trained far past
> its best point.

<br>

## Check yourself

```
python tools/run_lessons.py phases/04-a-language-model-you-wrote-yourself/04-a-model-that-generalises
```

This one trains the model twice, once in the solution and once in the check, so it takes about half a minute.

<br>

## Going further

Optional, and there is no check for it.

Set `DIMENSIONS` to 2 and to 32 and watch where the validation curve bottoms out each time. Smaller models take longer to overfit and plateau higher; larger ones reach a better point and then fall off a cliff. The best epoch is not a property of the problem, it is a property of the model you chose, which is why it has to be measured every time rather than remembered.

<br>

## What you learned

- Representing words as vectors lets a model share what it learns between similar words, which counting cannot do at all.
- Softmax turns scores into probabilities, and subtracting the largest first stops it overflowing.
- The gradient through softmax is the predicted probability minus one for the true word.
- Choosing when to stop is a decision made with data, so it needs its own split.
- Anything you tune with a set has spent that set.
- The first learned model to win in this course, by 12%, and it won for a reason you can name.

**Next:** [5. What it knows](../05-what-it-knows/), where you look inside the vectors it learned and find out what a language model picks up without being told.
