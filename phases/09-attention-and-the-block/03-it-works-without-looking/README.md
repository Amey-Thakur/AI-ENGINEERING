# 3. It works without looking

> **The head from lesson 2 clears a ceiling no n-gram can reach, and its
> attention weights are nearly flat.**
>
> On the two sentences it is distinguishing it spreads the weight almost
> identically: **0.28 / 0.08** against **0.29 / 0.06**. The subject, the one
> word that decides the answer, gets 0.19 on average where spreading the
> weight evenly would give 0.17.
>
> Something is carrying the signal. On this evidence it is not the weights.

**You will:** find the signal by taking things away, and finish with a model that has no query and no key in it and scores within one question of the head.

**You need:** [lesson 2](../02-looking-at-every-word-at-once/).

<br>

## Three questions, each answered by removing something

| Question | What to remove |
|:---------|:---------------|
| Does the head **need** its weights? | Train one with the weights nailed to an even share, so there is no query and no key anywhere in it. |
| Does the trained head **use** its weights? | Force its own weights to an even share at test time, without retraining. |
| Where is the signal, then? | Zero one position's value at a time and see which one matters. |

Both models start from the same seed, so they begin from identical weights and the only difference between them is whether the attention is learned at all.

<br>

## Your turn

Train both, run the ablations, and write `.work/located.tsv`:

```
what                               trained on  held back
the attention head                 38          16
an even share, trained that way    34          15
the head, weights evened at test   33          15
position 0 silenced                38          15
position 1 silenced                20          10
...
```

<br>

## What the solution prints

<!-- output: solve.py -->
```text
40 sentences to train on, 20 held back. Chance is 10 of 20.

  what                                 trained on   held back
  the attention head                   38 of 40    16 of 20
  an even share, trained that way      34 of 40    15 of 20
  the head, weights evened at test     33 of 40    15 of 20

Does it need the weights? An even share, with no query and no key anywhere in it,
reaches 15 of 20 where the head reaches 16. The learned weights are worth 1.

Does the trained head use them? Evening its own weights at test time costs it
1 of 20. It had barely been relying on them.

So where is the signal? Silence one position's value at a time:

  silenced                             trained on   held back
  position 0                             38 of 40    15 of 20
  position 1                             20 of 40    10 of 20  <- the subject
  position 2                             38 of 40    16 of 20
  position 3                             38 of 40    15 of 20
  position 4                             36 of 40    15 of 20
  position 5                             36 of 40    16 of 20

Silencing the subject's value takes it to 10 of 20, which is chance.
Silencing any other position leaves it at 15 or better.

The signal is one vector: the value at the subject's position. The weights decide
how much of it reaches the output, and an even share passes enough of it along.
```
<!-- end output -->

<br>

## The weights are worth one question

**An even share reaches 15 of 20. The learned head reaches 16.**

That model has no query matrix and no key matrix. It cannot score a position against anything, because there is nothing to score with. It takes the mean of the values and hands that to the output layer, and it clears lesson 1's ceiling just as decisively.

And the trained head barely uses what it learned: **evening its own weights at test time costs it one question.** It spent 150 passes learning a query and a key and then produced an answer that hardly depends on them.

> [!NOTE]
> One question on twenty is not a difference. [Phase 7 lesson 1](../../07-measuring-whether-any-of-it-works/01-the-number-has-error-bars/)
> puts 16 of 20 at 56.3% to 94.3% and 15 of 20 at 50.9% to 91.3%, and those
> intervals sit almost on top of each other. The honest statement is that on
> this task, at this size, **a mean beats nothing and attention beats a
> mean by an amount too small to measure.**

<br>

## And the signal is one vector

Silence the subject's value and the model lands on **10 of 20 and 20 of 40**. Both are exactly half. Not degraded, not worse: chance, as though the pair had become indistinguishable, which is precisely what happened.

Silence any other position and it loses at most one question.

| Silenced | Held back | |
|:---------|:---------:|:--|
| position 0, `the` | 15 of 20 | |
| **position 1, the subject** | **10 of 20** | **chance** |
| position 2, `that` | 16 of 20 | unchanged |
| position 3, `the` | 15 of 20 | |
| position 4, the actor | 15 of 20 | |
| position 5, the verb | 16 of 20 | unchanged |

So the whole mechanism is this: the subject's value vector carries singular or plural, the blend includes a share of it whatever the weights are, and the output layer reads it. The weights decide **how much** of that vector arrives. An even share passes along a fifth of it, and a fifth is plenty.

> [!CAUTION]
> This is why an attention heatmap is not an explanation.
>
> The weights here are a near-uniform smear. A reader shown that picture would
> conclude the model was using everything a little and nothing in particular,
> and would be wrong: it is using exactly one position and ignoring the rest.
> The information about *what the model used* is in the values, which the
> picture does not show.
>
> Attention weights tell you how a blend was mixed. They do not tell you which
> ingredient mattered, because an ingredient with a loud value matters at any
> mixing ratio above zero. Published attention maps are routinely read as
> accounts of a model's reasoning, and this is a twelve line experiment
> showing why that reading does not follow.

<br>

## What attention is actually for, then

Not this task. A dependency that one position decides, in a six word window, with a vocabulary of forty one words, is solved by a mean and a wide enough output layer.

What attention buys is the ability to be **selective when selection matters**: many positions, most of them irrelevant, and a different one relevant for each query. None of those conditions hold here, which is why the head's weights went flat and nothing was lost by it going flat. A mechanism is not demonstrated by a task that does not need it.

That is worth holding on to the next time a result is attributed to an architecture. The way to find out is the experiment in this lesson: take the mechanism out, leave everything else, and see whether the number moves.

<br>

## Check yourself

```
python tools/run_lessons.py phases/09-attention-and-the-block/03-it-works-without-looking
```

The check insists that silencing the subject lands on chance exactly, that no other position costs more than three questions, and that the learned weights stay worth at most two. If the head ever pulls properly ahead of the mean, this lesson is wrong and should be rewritten rather than the check relaxed.

<br>

## Going further

Optional, and there is no check for it.

Silence two positions at once and look for a pair that costs more than the sum of silencing each alone. If none exists, nothing in this model is distributed across positions, which is worth knowing before anybody describes it as building a representation.

Then print the value vectors for `server` and `servers` and compare them to a pair that does not differ in number, such as `engineer` and `reviewer`. The distance that matters is the one the output layer reads, and you can see it directly.

<br>

## What you learned

- A mechanism's contribution is measured by removing it and leaving everything else, not by looking at what it produced.
- A model with no query and no key, taking the mean of the values, comes within one question of the learned head on this task.
- The trained head barely used its own weights: evening them at test time cost one question.
- Silencing the subject's value lands the model on exactly chance, and silencing any other position costs at most one, so the signal is a single vector.
- Attention weights describe how a blend was mixed, not which ingredient mattered, which is why a heatmap is not an account of what a model used.
- Attention earns its place when selection matters, and nothing here needed selecting.

**Next:** [4. Where a word sits](../04-where-a-word-sits/), where the mean that did so well turns out not to know the order of anything.
