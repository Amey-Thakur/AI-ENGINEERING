# Phase 9. Attention, and the block

**Two lessons of a planned five. About ninety minutes for what exists. Still nothing installed.**

Phase 4 built a model that predicts the next word from the one before it, and phase 8 shipped a system with that model inside it. This phase is about the limit that sits underneath all of it: a word that decides the answer can be further away than the model can see, and widening the window runs into the vocabulary wall from the other direction.

Attention removes the limit by addressing a position by what is in it rather than by how far away it is. One head, three projections, a softmax and a weighted sum, written out and trained by a backward pass you derive yourself.

> [!WARNING]
> **This phase is being written.** Two of its five lessons are finished and
> the other three are not, so it does not yet close the way the earlier
> phases do. The two that exist are complete, checked and measured to the
> same standard as everything before them.

<br>

## The lessons

| # | Lesson | The idea underneath it |
| --- | --- | --- |
| 1 | [The thing a bigram cannot see](01-the-thing-a-bigram-cannot-see/) | A ceiling no amount of training moves |
| 2 | [Looking at every word at once](02-looking-at-every-word-at-once/) | One head clears it, and its weights do not explain how |
| 3 | *It works without looking* | Being written |
| 4 | *Where a word sits* | Being written |
| 5 | *The block* | Being written |

<br>

## The data

`agreement.tsv` holds sixty sentences in thirty pairs. Each pair differs only in whether its subject is singular or plural, and the word that has to agree with it sits five words later.

```
the server  that the engineer restarted was  slow
the servers that the engineer restarted were slow
```

Every sentence is eight words long, with the subject always at position 1 and the target always at position 6. That rigidity is deliberate: a lesson can then name a position rather than search for one, and the checks can assert that the corpus has not drifted.

The corpus is built so that **every word preceding a target is followed by `was` exactly as often as by `were`**. That is what makes the bigram's ceiling exactly half rather than approximately half, and the check in lesson 1 refuses to pass if any context tips.

<br>

## Two results worth carrying

**A bigram trained on all sixty sentences and scored on all sixty answers thirty.** Not as a training score, as a ceiling. Every one of the sixty predictions is a tie, because every context is balanced, and a tie broken the same way every time is right for exactly half. No optimiser, no smoothing and no quantity of data of this shape moves that number, which is the same shape of argument as phase 2's XOR lesson.

**One attention head, eight numbers wide, reaches 16 of 20 on sentences it was not trained on.** A model that could do no better than guess reaches that 0.59% of the time, so luck is not a plausible explanation. What made it possible is not scale and not more data: the corpus is sixty sentences and the model is tiny. It is that a position can be addressed by its content instead of by its distance.

> [!CAUTION]
> The head's attention weights are nearly flat, and nearly identical between
> the two sentences it is distinguishing. The average weight on the subject,
> the one word that decides the answer, is 0.19 where spreading the weight
> evenly would give 0.17.
>
> So the thing that is usually presented as an explanation of what a model
> used is, here, not an account of how it decided. Lesson 3 is about where
> the signal actually is.

<br>

## Check the phase

```
python tools/run_lessons.py phases/09-attention-and-the-block
```

<br>

**Previous:** [Phase 8](../08-shipping-cost-latency-failure-safety/), which shipped the system this phase goes back underneath.
