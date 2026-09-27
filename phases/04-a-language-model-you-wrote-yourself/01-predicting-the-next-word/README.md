# 1. Predicting the next word

> **Every large language model does one thing: it predicts what comes next.**
>
> Everything else, answering questions, writing code, holding a conversation,
> is that one ability pointed in a direction. You are about to build the same
> thing, out of counting, in about forty lines.

**You will:** build a language model, watch it guess the next word, and measure how often it is right on sentences it has never seen.

**You need:** [phase 3](../../03-words-that-know-what-they-mean/).

<br>

## The whole idea

Read a lot of text. Count which word follows which. To predict, look up what usually came next.

```python
for word, next_word in zip(tokens, tokens[1:]):
    following[word][next_word] += 1
```

That is a **bigram model**: it looks at exactly one word of context. It is the simplest thing that deserves the name language model, and everything in this phase is a way of making the context longer and the counting smarter.

<br>

## Marking the edges

```python
return [START] + sentence + [END]
```

Two invented tokens. `<s>` lets the model learn how sentences *begin*, which is otherwise invisible: without it, the first word of every sentence has no context and the model has nothing to condition on. `</s>` lets it learn that sentences *stop*, which matters enormously the moment you generate text, as the next lessons will show.

<br>

## Measuring it

Train on the first 180 sentences of the corpus. Hold back the last 37. Then for every position in a held back sentence, guess the next word and check.

> [!IMPORTANT]
> The split is by position rather than random, so everybody gets the same one
> without needing a seed. And it is by *sentence*, not by word: splitting
> mid-sentence would leave half of a held back sentence in the training data,
> which is the leak from phase 1 lesson 4 wearing a different coat.

<br>

## Your turn

Build the counts and write `.work/results.tsv`:

```
measure            value
predictions        391
correct            54
unknown_context    112
never_seen_pair    302
```

> [!WARNING]
> One trap, and it caught me while writing this lesson. `following` is a
> `defaultdict`, and **reading a missing key from a defaultdict creates it**.
> So checking `following[word][next_word] == 0` while measuring quietly inserts
> empty contexts into the model you are measuring.
>
> Use `following.get(word, {}).get(next_word, 0)` instead. The check will tell
> you if you did not.

<br>

## What the solution prints

<!-- output: solve.py -->
```text
180 sentences to learn from, 37 held back
608 different words, 519 of them with something known to follow

What it expects next:

  after 'the'                    incident (9), customer (8), error (7), meeting (7)
  after 'server'                 cleared (1), doubled (1), ran (1), restarted (1)
  after 'we'                     added (1), cancelled (1), cut (1), deploy (1)
  after 'customer'               </s> (1), account (1), asked (1), confirmed (1)
  at the start of a sentence     the (100), a (16), we (10), coverage (3)

Guessing the next word on held back sentences:
  right          54 of 391   13.8%
  context never seen in training   112
  pair never seen in training      302 of 391   77%
```
<!-- end output -->

<br>

## What it has learned

Read the predictions. After *the*, it expects *incident*, *customer*, *error*, *meeting*. At the start of a sentence it expects *the*, a hundred times over.

Those are real facts about English and about this corpus, learned by nobody explaining anything. The same mechanism at a scale a billion times larger is what makes a modern model seem to know things.

<br>

## And where it collapses

**13.8% right.** Worse than that, look at the other two numbers.

| | |
| --- | --- |
| Predictions made | 391 |
| Contexts never seen in training | **112** |
| Pairs never seen in training | **302 of 391, or 77%** |

For 112 of the 391 predictions the model had never encountered the word it was asked to follow, so it had nothing at all to say.

And **77% of the word pairs in the held back sentences never occurred in training**. The model assigns each of those a probability of exactly zero: not "unlikely", but *impossible*. It is certain that a sentence a human wrote cannot exist.

> [!IMPORTANT]
> This is the defining problem of counting based language models, and it does
> not go away with more data. Language is combinatorial: a vocabulary of 600
> words has 360,000 possible pairs, and a real vocabulary of 50,000 has two and
> a half billion. Most valid pairs will never appear in any corpus, however
> large, simply because most sentences have never been written.
>
> Counting can only ever tell you about what has already happened. Language is
> mostly about what has not.

<br>

## Check yourself

```
python tools/run_lessons.py phases/04-a-language-model-you-wrote-yourself/01-predicting-the-next-word
```

<br>

## Going further

Optional, and there is no check for it.

Count triples instead of pairs: what follows *the server* rather than what follows *server*. The predictions become far more sensible where they exist, and the number of unseen contexts goes up sharply. That trade is the whole story of this phase, and it is why the answer turns out not to be longer counts.

<br>

## What you learned

- A language model predicts the next token, and that single ability underlies all the rest.
- Counting which word follows which is enough to build one.
- Start and end markers let a model learn how sentences begin and stop.
- Split held back data by sentence, or you leak.
- Reading a missing key from a defaultdict creates it, which can corrupt a model while you measure it.
- 77% of held back pairs get probability zero, and that is a property of language rather than of this corpus.

**Next:** [2. Never say never](../02-never-say-never/), where giving everything a small chance turns an impossible model into a usable one.
