# 5. What it knows

> **Nobody asked the model to learn what words mean.**
>
> It was asked to guess the next word, and nothing else. The vectors were
> scratch paper it kept because they helped. This lesson reads the scratch
> paper, and what is on it is the idea the whole modern field rests on.

**You will:** look inside the vectors a language model invented, and find structure nobody put there.

**You need:** [lesson 4](../04-a-model-that-generalises/).

<br>

## Your turn

Train the model for the four epochs validation chose, then ignore its predictions entirely. Take the vector it learned for each word and find, by cosine, which other words ended up nearby.

Write `.work/neighbours.tsv`:

```
word      neighbour    closeness
the       same         0.931...
```

<br>

## What the solution prints

<!-- output: solve.py -->
```text
101 words, 8 numbers each, learned only by guessing the next word

  server     three +0.99, cluster +0.95, customer +0.95, monitoring +0.94
  the        same +0.93, an +0.86, no +0.79, a +0.68
  was        monitoring +0.99, three +0.97, were +0.95, server +0.94
  customer   nobody +0.99, server +0.95, release +0.94, agenda +0.93
  test       an +0.93, written +0.85, error +0.84, one +0.79

The closest pairs in the whole vocabulary:

  before       and caught       +0.997
  into         and within       +0.996
  customer     and nobody       +0.994
  code         and image        +0.994
  monitoring   and was          +0.993
  failure      and node         +0.993
```
<!-- end output -->

<br>

## Read the row for `the`

> `the` → **same**, **an**, **no**, **a**

Every one of those is a determiner. Words that go in front of a noun.

Nobody wrote down a list of determiners. Nobody labelled any data. The model was adjusting eight numbers per word in order to guess what came next, and *the*, *a* and *an* drifted together because they are followed by the same kinds of things.

Then `was` → **were**. Two forms of one verb.

And in the closest pairs across the whole vocabulary: **into** and **within**, at 0.996. Both prepositions.

> [!IMPORTANT]
> This is the observation behind every large language model.
>
> Train something to predict the next token, at sufficient scale, and
> structure you never specified appears in its internals, because that
> structure is *useful for the prediction*. Grammar, topic, sentiment, and at
> large enough scale, considerably more than that.
>
> Nobody designed the representation. It was the cheapest way to do the job.

<br>

## Two ways of learning, two different things learned

Phase 3 also produced word vectors, and they were not like these.

| | Method | `server` ended up near |
| --- | --- | --- |
| **Phase 3** | Counting words in a window, weighted by surprise | memory, load, incident |
| **Phase 4** | Predicting the next word | cluster, monitoring, customer |
| | | |
| **Phase 3** | | `the` was not notable |
| **Phase 4** | | `the` → same, an, no, a |

Phase 3 captured **what a word is about**. This captures **what grammatical role a word plays**.

Neither is more correct. They were trained on different tasks, and a representation encodes whatever its task rewarded. Predicting the immediately next word rewards knowing what kind of word comes next, which is largely a question of grammar. Counting across a four word window rewards knowing what a passage is about.

> [!TIP]
> That is the same lesson as phase 3 lesson 5, arriving from the other
> direction. There it explained a failure: vectors that knew about topic could
> not do a task about grammar. Here it explains a success. Both times, the
> task decides what the representation knows.

<br>

## The noise is real too

`customer` and **nobody** at 0.994. `server` near **three**. `monitoring` near **was**.

Those are not meaningful and it would be dishonest to pretend otherwise. Eight numbers per word, 1,644 training pairs, four epochs. There is not enough evidence for the structure to settle, so genuine grammatical grouping sits beside coincidence, and from the inside they look identical.

The fix is the same as it has been all course: more data. Not a cleverer objective.

What makes the real ones convincing is not any single pair. It is that determiners grouped with determiners, verb forms with verb forms, and prepositions with prepositions, which is not a coincidence you get four times by luck.

<br>

## Check yourself

```
python tools/run_lessons.py phases/04-a-language-model-you-wrote-yourself/05-what-it-knows
```

<br>

## Going further

Optional, and there is no check for it.

The model holds two sets of numbers per word: the `meanings` vector used when a word is the *context*, and the `scorers` row used when it is the *answer*. This lesson probed the first. Probe the second and compare. They encode related but different things, one about what a word predicts and one about what predicts it, and real implementations sometimes add them together or keep only one.

<br>

## Phase 4 complete

```
python tools/run_lessons.py phases/04-a-language-model-you-wrote-yourself
```

You built a language model by counting and measured it with perplexity, found it calls 77% of real sentences impossible, fixed that two ways, discovered the best counting model ignores context entirely, made it generate text and watched it forget its subject every two words, replaced counting with learned vectors and **beat it by 12% on a test set nothing had touched**, and then found grammar inside the numbers it invented on the way.

That last sentence is, in miniature, how the models everyone is talking about were built.

**Next:** [Phase 5](../../05-finding-the-right-thing-to-say/), where the model stops having to remember everything and learns to look things up instead.
