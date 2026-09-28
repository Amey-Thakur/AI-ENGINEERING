# 1. The thing a bigram cannot see

> **Two sentences. One letter between them.**
>
> ```
> the server  that the engineer restarted was  slow
> the servers that the engineer restarted were slow
> ```
>
> The word before the answer is `restarted` in both. Phase 4's model sees only
> that word, so whatever it predicts for one sentence it predicts for the
> other, and one of the two is wrong.

**You will:** train a bigram on the whole corpus, score it on the same corpus, and find it capped at exactly half. Not badly trained. Capped.

**You need:** [phase 4](../../04-a-language-model-you-wrote-yourself/), for the bigram, and nothing else.

<br>

## The corpus

`agreement.tsv` holds sixty sentences in thirty pairs. Each pair differs only in whether the subject is singular or plural, and the word that has to agree with it sits **five words later**.

Every sentence is the same shape, eight words long, with the subject always at position 1 and the target always at position 6. That rigidity is deliberate: the later lessons can then name a position rather than search for one.

```
the  server  that  the  engineer  restarted  was  slow
 0      1      2    3       4          5      6     7
```

<br>

## Your turn

Count a bigram from **all sixty sentences**, score it on **all sixty**, and write `.work/ceiling.tsv`:

```
context      was  were
checked      5    5
flagged      6    6
ignored      5    5
queued       4    4
restarted    4    4
reviewed     6    6
```

Nothing is held back. The point is not to measure generalisation, it is to measure the best this model could ever do.

<br>

## What the solution prints

<!-- output: solve.py -->
```text
60 sentences, 41 words, 30 pairs that differ by one letter.

A pair, in full:
  the server that the engineer restarted was slow
  the servers that the engineer restarted were slow

The target sits at position 6. The word before it is 'restarted' in both.

Every word that precedes a target, and what follows it:

  context      was   were
  checked        5      5
  flagged        6      6
  ignored        5      5
  queued         4      4
  restarted      4      4
  reviewed       6      6

Every context is balanced between the two: True

So the bigram, trained on all 60 sentences and then scored on them,
answers 30 of 60. All 60 were ties, and a tie broken the same way
every time is right for exactly half of them.

That is not a training score. It is the ceiling. No amount of data of this shape,
and no smoothing, moves it, because the information the answer needs is five words
away and the model cannot see that far by construction.
```
<!-- end output -->

<br>

## Thirty of sixty, and not one of them was a near miss

Look at the table. **Every single context is exactly balanced.** `restarted` is followed by `was` four times and `were` four times. `reviewed` six and six. There is no context in the corpus where one answer is even slightly more likely than the other.

So every one of the sixty predictions is a tie, and a tie broken the same way every time is right for half of them. Thirty. Exactly.

> [!IMPORTANT]
> This is a ceiling, not a score, and the difference matters.
>
> A bad score invites you to train longer, add smoothing, collect more data or
> pick a better optimiser. None of those move this number. Ten thousand more
> sentences of the same shape leave every context balanced, because the shape
> is what balances them. The model is not underfitting. It is being asked for
> information it cannot represent.
>
> Phase 2 lesson 1 had the same structure: a single straight line cannot
> separate XOR, and no amount of training fixes an architecture.

<br>

## Why the information is out of reach

The bigram's whole world is one word. Its parameters are a table of *what follows what*, and both sentences hand it the same key.

The thing that decides the answer is at position 1 and the answer is at position 6. Five words apart. An n-gram can be widened, and a 6-gram would see the subject here, but the number of contexts it has to count grows as the vocabulary to the power of the window, which is [phase 3's vocabulary wall](../../03-words-that-know-what-they-mean/01-the-vocabulary-wall/) arriving from a different direction. Widen the window far enough to catch a dependency and almost every context you need is one you have never seen.

What is wanted is a model that can **look** at position 1 from position 5, without having to have counted that exact pair of words together before.

<br>

## Check yourself

```
python tools/run_lessons.py phases/09-attention-and-the-block/01-the-thing-a-bigram-cannot-see
```

The check refuses to pass if any context in the corpus is unbalanced, because an unbalanced one would give the bigram a real signal, move the ceiling off 50%, and make every comparison in the next four lessons measure against the wrong floor.

<br>

## Going further

Optional, and there is no check for it.

Widen the model to a trigram and score it again. It sees `engineer restarted`, which is still the same in both sentences, so nothing changes. Then work out by hand how wide the window has to be for this corpus, and count how many of the contexts at that width appear exactly once.

Then write two sentences of your own where the dependency runs the other way, with the target before the thing it agrees with. Notice that the bigram is not worse on those, it is exactly the same, because it was never using direction in the first place.

<br>

## What you learned

- A dependency the architecture cannot span is not a training problem, and no optimiser, smoothing scheme or quantity of data fixes it.
- Scoring a model on its own training data measures its ceiling, which is the honest thing to measure when the question is whether the model *can* rather than whether it *has*.
- Every context in this corpus is exactly balanced, so all sixty predictions are ties and the ceiling is exactly half.
- Widening the window is a real fix and it runs into the vocabulary wall, because contexts grow as the vocabulary to the power of the window.
- What is needed instead is a model that can look at a distant position directly, without having counted that pair of words together before.

**Next:** [2. Looking at every word at once](../02-looking-at-every-word-at-once/), which is attention, and which clears this ceiling with about forty lines.
