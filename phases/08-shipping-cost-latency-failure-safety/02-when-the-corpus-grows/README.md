# 2. When the corpus grows

> **The search reads all 217 sentences for every question, so at 217,000
> sentences it reads 217,000 of them.**
>
> The fix is an index, it is seven lines, and it returns exactly the same
> answers. The optimisation it then tempts you into is six times faster again
> and makes the system worse.

**You will:** build an inverted index, confirm it changes nothing, then take the obvious next step and watch a threshold in another phase silently change meaning.

**You need:** [lesson 1](../01-counting-the-work/).

<br>

## An index is a dictionary the other way round

The corpus maps a sentence to its words. Turn it over:

```python
def build_index(sentences):
    postings = defaultdict(list)

    for index, sentence in enumerate(sentences):
        for word in set(sentence.split()):
            postings[word].append(index)

    return postings
```

Now scoring a question means looking up each of its words and counting how often each sentence comes back. A sentence sharing no words with the question is never touched, where before it was compared and scored zero.

The cost stops being *the corpus* and becomes *the sentences that hold your words*.

<br>

## Your turn

Score all 25 questions three ways and write `.work/index.tsv`:

```
search                   comparisons  same answer  right  declined  correct
scan every sentence      32984        25           9      8         17
an inverted index        4051         25           9      8         17
the index without 'the'  707          21           5      10        15
```

The index cost is the total length of every postings list it reads.

<br>

## What the solution prints

<!-- output: solve.py -->
```text
A corpus of 217 sentences holding 608 distinct words.

  the 10 commonest, and how many sentences hold each:
    the         176 of 217   81.1%
    and          68 of 217   31.3%
    was          48 of 217   22.1%
    a            46 of 217   21.2%
    to           27 of 217   12.4%
    it           25 of 217   11.5%
    is           22 of 217   10.1%
    on           21 of 217    9.7%
    not          18 of 217    8.3%
    than         15 of 217    6.9%

Three ways to find the same sentence, over 25 questions:

  search                     comparisons   of the scan   same answer   correct
  scan every sentence              32984        100.0%   25 of 25    17 of 25
  an inverted index                 4051         12.3%   25 of 25    17 of 25
  the index without 'the'            707          2.1%   21 of 25    15 of 25

The index reads 4051 where the scan reads 32984, and returns the
same sentence for all 25 questions. Nothing about the system changed.

Dropping 'the' reads 707, which is 6 times less again, and the answers move
on 4 questions. Right answers go from 9 to 5 and refusals from 8 to 10.

Why: 16 of 25 questions lost a point of overlap, because 'the' was
matching. The number clearing a threshold of 3 fell from 13 to 5.

The threshold was not touched. It was set in phase 6 and it now means something
different, because the scale underneath it moved.
```
<!-- end output -->

<br>

## This is what an optimisation looks like

**32,984 comparisons become 4,051, and all 25 answers are identical.**

Eight times less work, no behaviour change, seven lines. There is nothing to weigh up and no trade to consider. Take it.

> [!TIP]
> The test for a real optimisation is that you can check it by equality.
> Compute the old way and the new way over your whole test set and assert the
> outputs match, then delete the old way once it passes.
>
> If you cannot make that assertion, you are not optimising. You are changing
> the system and hoping, and the thing you have built needs measuring by
> everything in phase 7.

<br>

## And this is what a change looks like

The index makes the cost depend on how common your words are, which makes the
next move obvious. The word `the` is in **176 of 217 sentences**, so looking it
up reads four fifths of the corpus for almost no information. Drop it.

**707 comparisons. Six times faster again. 2.1% of the original scan.**

| | Comparisons | Same answer | Right | Declined | Correct |
| --- | --- | --- | --- | --- | --- |
| Inverted index | 4,051 | 25 of 25 | 9 | 8 | **17 of 25** |
| Without `the` | **707** | 21 of 25 | 5 | 10 | 15 of 25 |

Right answers fell from nine to five. The system got faster and worse, and the reason is not that `the` was carrying meaning.

<br>

## A threshold in another phase changed meaning

The scorer counts shared words. Remove a word that was matching and every score that included it falls by one.

**Sixteen of the 25 questions lost exactly one point of overlap.** The threshold is 3, set in phase 6 lesson 3 and never revisited, and the number of questions clearing it fell from **13 to 5**.

Nobody edited the threshold. It is still `BAR = 3` in a file nobody opened. What changed is the scale it sits on, and a constant that means "a decent match" on one scale means "an exceptional match" on another.

> [!CAUTION]
> This is the failure mode that makes performance work dangerous, and it is
> not carelessness. The change was local, correct, well motivated and
> obviously beneficial. It broke something two phases away through a shared
> numeric scale that appears in neither file.
>
> Any constant compared against a computed score is coupled to every
> component that contributes to that score. Changing the tokeniser,
> normalising differently, adding a field, removing a stop word: all of them
> move the scale and none of them touch the constant.

<br>

## Which is what the expectations file is for

Phase 7 lesson 5 recorded what every question does. Run this change against it and the report is not "2.1% of the scan", it is four named questions that moved, and the diff sits in the pull request next to the speedup.

That is the only reason the coupling above is survivable. Nobody is going to remember that `BAR = 3` depends on the stop word list. Something has to notice on their behalf.

> [!NOTE]
> If you do want the speed, the repair is to make the threshold relative
> rather than absolute: a share of the question's length, or the gap between
> the best sentence and the second best. Both remove the dependence on the
> scale, and both need remeasuring from scratch, because they are a different
> system rather than a faster one.

<br>

## Check yourself

```
python tools/run_lessons.py phases/08-shipping-cost-latency-failure-safety/02-when-the-corpus-grows
```

The check insists the index agrees with the scan on every question, and says in those words that an optimisation which changes an answer is not an optimisation.

<br>

## Going further

Optional, and there is no check for it.

Make the threshold a fraction of the question length instead of a constant, then drop `the` again and see whether the damage goes away. This is the honest version of the speedup and it is a different system, so measure it with phase 7 lesson 2's paired test rather than eyeballing the total.

Then look at what the index costs to hold. The corpus is 2,019 words and the postings hold 1,834 entries, one per distinct word per sentence, so the index is very nearly the size of the thing it indexes. Every index is that trade, and the reason a scan exists at all is that at 217 sentences the trade is not obviously worth making.

<br>

## What you learned

- An inverted index maps each word to the sentences holding it, and makes a query cost the length of its postings rather than the size of the corpus.
- Here it does identical work for 12% of the comparisons, and returns the same answer to all 25 questions.
- The test of a real optimisation is that you can assert the old and new outputs are equal; if you cannot, it is a change.
- Dropping the commonest word is six times faster again and costs two questions, because it is a change rather than an optimisation.
- Removing a matching word lowers every score by one, so a fixed threshold set two phases earlier went from admitting 13 questions to 5.
- Any constant compared against a computed score is coupled to everything that contributes to the score, and nothing in either file records that.
- A recorded expectations file is what notices, since nobody will remember the coupling.

**Next:** [3. When something fails](../03-when-something-fails/), where a component stops working and the fallback turns out to be the dangerous part.
