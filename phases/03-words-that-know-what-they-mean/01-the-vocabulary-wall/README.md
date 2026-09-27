# 1. The vocabulary wall

> **Two phases have now pointed at the same thing.**
>
> Phase 1: the held back messages were full of words the model had no weight
> for. Phase 2: five hundred parameters could not fix it, because the problem
> was never capacity. This lesson measures the wall properly, and finds it is
> worse than either phase suggested.

**You will:** measure how much of the vocabulary is missing, and then prove that the representation has no idea any two words are related.

**You need:** [phase 2](../../02-a-network-you-wrote-yourself/).

<br>

## The obvious half

Training sees 40 messages. Those contain 128 different words. The 20 held back messages use **54 words that never appeared in training**.

The model has nothing to say about any of them. Not a weak opinion, no opinion: they contribute exactly zero, and the message gets decided on whatever else is in it.

> [!NOTE]
> Phase 1 lesson 5 reported 56, and this lesson reports 54. Both are right,
> because they count different things. That count was words the model had **no
> weight for**, which includes words it saw during training but never got wrong,
> so never moved. This is words it **never saw at all**. Two precise numbers,
> two different questions.

<br>

## The half nobody mentions

Here is the deeper problem, and it applies to the 128 words the model *does* know.

In every model so far, a word is a position in a list. *server* is "the vector with a 1 in slot 96". *deployment* is "the vector with a 1 in slot 31". This is called **one-hot**, and it is what `word in words` has quietly meant all along.

So ask the obvious question: how far apart are two words?

```python
def one_hot(word, vocabulary):
    return [1.0 if other == word else 0.0 for other in vocabulary]
```

Two different words have their 1 in different slots and 0 everywhere else. The distance between them is always **√2**. Every time. For every pair.

<br>

## Your turn

Measure it. Write `.work/findings.tsv`:

```
finding                        value
vocabulary_trained             128
unseen_words_in_held_back      54
distance_server_deployment     1.414214
distance_server_friday         1.414214
```

<br>

## What the solution prints

<!-- output: solve.py -->
```text
Training saw 128 different words.
The held back messages use 54 words it never saw.

How far apart are these words, in the representation we have been
using all along?

  server     and deployment   1.414214
  password   and vault        1.414214
  server     and friday       1.414214
  password   and tuesday      1.414214

Distinct distances among those four pairs: 1
Distinct distances among 1,770 pairs of the first 60 words: 1
That one distance is 1.414214, which is the square root of 2.
```
<!-- end output -->

<br>

## Sit with that last line

**1,770 pairs of words. One distinct distance between them.**

*server* and *deployment* are exactly as far apart as *server* and *friday*. *password* and *vault* are exactly as far apart as *password* and *tuesday*.

The representation does not merely fail to know that those words are related. It cannot express relatedness at all. Every word is a corner of a very high dimensional box, all corners the same distance from all others, and the geometry has no room for the idea that two of them belong together.

> [!IMPORTANT]
> This is why more data and more layers both failed.
>
> More layers cannot help, because there is no structure in the input to build
> on. More data helps only in the dumbest way: it tells you about *dashboard*
> only when it shows you *dashboard*, and it never tells you anything about
> *dashboard* by showing you *server*.
>
> Every word has to be learned from scratch, separately, and that is the wall.

<br>

## What would fix it

Suppose a word were not a slot but a handful of numbers, arranged so that words used in similar ways ended up close together. *server* near *deployment*. *friday* somewhere else entirely.

Then a model that had learned something about *server* would already know most of it about *database*, without ever having seen the word. Evidence would spread between related words instead of stopping at each one.

That is what the rest of this phase builds. The question it turns on is where those numbers could possibly come from, given that nobody is going to sit and assign meanings to 128 words by hand, let alone a million.

The answer, in the next lesson, is one of the genuinely good ideas in this field, and it is old enough to have been written down in 1957.

<br>

## Check yourself

```
python tools/run_lessons.py phases/03-words-that-know-what-they-mean/01-the-vocabulary-wall
```

<br>

## Going further

Optional, and there is no check for it.

Work out how many dimensions the one-hot representation uses. It is one per word in the vocabulary, so 182 here and about 170,000 for English. Then consider that each word uses exactly one of them and ignores the rest. It is an enormous, almost entirely empty representation that stores one fact per word: which word it is.

<br>

## What you learned

- 54 of the held back words were never seen in training, and the model has literally nothing to say about them.
- One-hot means every word is a slot, and slots carry no relationships.
- Every pair of distinct words sits exactly √2 apart, measured across 1,770 pairs.
- Relatedness is not weakly represented, it is unrepresentable, and that explains why both more data and more capacity failed.
- The fix is to change what a word *is*, before changing anything about the model.

**Next:** [2. The company a word keeps](../02-the-company-a-word-keeps/), where meaning gets built out of nothing but counting.
