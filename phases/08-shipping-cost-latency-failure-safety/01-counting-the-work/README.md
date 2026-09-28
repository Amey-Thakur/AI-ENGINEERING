# 1. Counting the work

> **Every lesson in this course finishes in under a second, which is exactly
> the condition under which nobody counts anything.**
>
> The agent's average question costs 687 word comparisons. Not one of the 48
> questions costs anything between 1 and 1084.

**You will:** meter the system in units that do not depend on your laptop, find that its average describes a question that does not exist, and find that refusing to answer costs more than answering.

**You need:** [phase 7](../../07-measuring-whether-any-of-it-works/).

<br>

## Count work, not seconds

Seconds are a property of the machine. Run this on a faster laptop and every number changes without the system changing, which makes seconds useless for noticing that something got worse.

So count what the system does:

```python
class Meter:
    def __init__(self):
        self.calls = 0
        self.sentences = 0
        self.comparisons = 0
```

Search compares the question against every sentence, so one search costs the corpus size times the number of words in the question. That number is the same on every machine and in every year.

> [!TIP]
> Pick a unit of work that is proportional to the thing you will eventually
> be billed for, and count that instead of time. For a hosted model it is
> tokens in and out, for a database it is rows examined, for retrieval it is
> documents scanned.
>
> Latency follows the unit of work, but the unit of work is the thing you can
> reason about, compare across machines, and put in a test.

<br>

## Your turn

Meter all 48 questions and write `.work/spend.tsv`:

```
comparisons  questions
0            23
1085         9
1302         6
1519         9
1736         1
```

<br>

## What the solution prints

<!-- output: solve.py -->
```text
A corpus of 217 sentences and 2019 words, asked 48 questions.

  cheapest question        0 word comparisons
  median                1085
  mean                   687
  dearest               1736
  everything           32984

Every cost that occurs, and how many questions have it:
       0 comparisons   23 questions
    1085 comparisons    9 questions
    1302 comparisons    6 questions
    1519 comparisons    9 questions
    1736 comparisons    1 question

The mean is 687. The cheapest question that does any work at all costs 1085.
Questions costing between 1 and 1084: 0.

  23 questions are answered by a tool and never reach search, costing nothing
  25 reach search and cost 1319 each on average

  answered 36:   488 comparisons on average
  declined 12:  1284 comparisons on average
  the threshold buys honesty and saves nothing, because a question is searched
  in full before it is refused.

And the same 48 questions against a larger corpus:
      1 times the sentences (    217):       32984 comparisons
     10 times the sentences (   2170):      329840 comparisons
    100 times the sentences (  21700):     3298400 comparisons
   1000 times the sentences ( 217000):    32984000 comparisons
```
<!-- end output -->

<br>

## The average is a number nothing costs

There are five costs in the whole system: **0, 1085, 1302, 1519 and 1736**.

Twenty-three questions hit a tool and cost nothing at all. Twenty-five reach search and pay for the entire corpus. The mean of 687 sits in the gap between those two populations, and the count of questions costing anywhere near it is **zero**.

The mean is also **below the median**, which is the giveaway. A cost distribution with a mean under its median is usually two populations, not one.

> [!IMPORTANT]
> This is the shape of nearly every real system's cost, and it is why the
> average is the wrong number to provision on.
>
> A cache turns one population into two: hit and miss. A router turns one into
> three: the cheap tool, the expensive tool, the fallback. A retry doubles the
> expensive one. In every case the average lands in a valley where no request
> lives, and what the user waits for is the population they are in.
>
> Report the distribution, or at minimum the median and the worst case. If
> somebody asks what a request costs, the honest answer here is "nothing or
> about 1300, depending".

<br>

## Refusing is not cheaper than answering

| | Questions | Comparisons each |
| --- | --- | --- |
| Answered | 36 | 488 |
| Declined | 12 | **1284** |

A declined question costs two and a half times an answered one, and the reason is in the order the code does things: **the corpus is searched in full, and only then is the result found to be below the threshold and thrown away.**

Phase 6 measured the threshold as buying eight correct refusals for three lost answers. It buys them at full price. Every "I do not know" in this system is a complete search whose entire output is discarded.

> [!NOTE]
> Worth being precise about, because it is not a bug. There is no way to know
> the best overlap is below 3 without computing the best overlap.
>
> What it does mean is that adding caution to a system does not reduce its
> bill, which is the opposite of the intuition. A system that refuses half
> its traffic does the same work as one that answers all of it, and if you
> sized the machine on the assumption that refusals are cheap, half your
> capacity planning is wrong.

<br>

## And the corpus is 217 sentences

| Corpus | Comparisons for these 48 questions |
| --- | --- |
| 217 sentences | 32,984 |
| 2,170 | 329,840 |
| 21,700 | 3,298,400 |
| 217,000 | **32,984,000** |

Linear, exactly, because every question reads every sentence. Two hundred thousand sentences is a small wiki, and at that size these 48 questions cost 33 million comparisons, or about 687,000 each.

There is nothing wrong with the search. It is thirteen lines and it beat BM25 in phase 5. It simply has no index, and the whole of the next lesson is that sentence.

<br>

## Check yourself

```
python tools/run_lessons.py phases/08-shipping-cost-latency-failure-safety/01-counting-the-work
```

The check insists no question costs anything between nothing and a full search, because there is no middle for one to occupy.

<br>

## Going further

Optional, and there is no check for it.

Meter the retry loop from phase 6 lesson 4. Across the 25 questions that reach search it costs 70,959 comparisons against 32,984, so 2.15 times the work, with a worst case of 5,859 for one question. Phase 6 measured the same ratio in calls and found it improved nothing. Both measurements were available before the loop was written.

Then add a counter for the sort inside search. It sorts all 217 sentences to find the best one, which is a great deal of work to find a maximum. Replacing the sort with a single pass changes nothing about the answers and is the cheapest improvement in the course.

<br>

## What you learned

- Count work rather than seconds, because seconds measure the machine and work measures the system.
- The unit to count is whatever you will be billed for: tokens, rows, documents scanned.
- This system has five distinct costs, and its mean of 687 is a value no question has.
- A mean below the median is a sign of two populations rather than one, which is what a router, a cache or a fallback always produces.
- Refusing a question costs 1284 comparisons against 488 to answer one, because the search completes before the result is discarded.
- Adding caution to a system does not reduce its bill.
- With no index the cost is exactly linear in the corpus, so 217,000 sentences means 687,000 comparisons a question.

**Next:** [2. When the corpus grows](../02-when-the-corpus-grows/), where an index does identical work for an eighth of the cost, and the obvious next optimisation quietly breaks the system.
