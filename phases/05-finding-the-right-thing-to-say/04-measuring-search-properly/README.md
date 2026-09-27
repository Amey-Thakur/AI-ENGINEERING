# 4. Measuring search properly

> **Lesson 2 asked how often the right answer came first, and that measurement
> threw away almost everything.**
>
> A search that puts the answer second and one that buries it at place two
> hundred both score zero. They are not remotely the same system, and one of
> them is nearly perfect.

**You will:** score the same three searches several ways, and find that which one is best depends on the question you asked.

**You need:** [lesson 3](../03-finding-it-by-meaning/).

<br>

## Keep the place, not the verdict

For each question, record **where** the right sentence came in the ranking. Then that one number answers every question you might have.

**Found by place k.** How often was the answer in the top k? Choose k to match how results are used. A person scanning a page sees ten. A dropdown shows five. A program taking the first result has k of 1.

**Average of one over the place.** First is worth 1, second 0.5, third 0.33. One number that rewards being near the top without ignoring everything below it. Its usual name is **mean reciprocal rank**.

**The worst place.** Your tail. This is the number that tells you how badly the system fails when it fails, and it is usually the one nobody reports.

<br>

## Your turn

Measure all three searches and write `.work/results.tsv`:

```
method          found_by_1  found_by_3  found_by_5  found_by_10  mean_reciprocal_rank  worst_place  asked
shared words    15          18          20          20           0.8392                5            20
```

<br>

## What the solution prints

<!-- output: solve.py -->
```text
  method          top 1   top 3   top 5   top 10   average 1/place   worst place
  shared words    15 of 20  18 of 20  20 of 20  20 of 20       0.839            5
  rare words      12 of 20  16 of 20  19 of 20  20 of 20       0.744            8
  bm25            13 of 20  15 of 20  16 of 20  20 of 20       0.741            9

Where the right sentence actually came:

  shared words   place 1: 15, place 2: 2, place 3: 1, place 4: 1, place 5: 1
  rare words     place 1: 12, place 2: 4, place 4: 3, place 8: 1
  bm25           place 1: 13, place 2: 2, place 4: 1, place 6: 1, place 7: 2, place 9: 1
```
<!-- end output -->

<br>

## The ranking of the systems changes with the question

Look at **rare words** against **bm25**.

| | rare words | bm25 |
| --- | --- | --- |
| Found first | 12 | **13** |
| Found by place 5 | **19** | 16 |
| Worst place | **8** | 9 |

If your program takes the top result and acts on it, bm25 is better. If a person sees five results, rare words is clearly better, by three whole questions out of twenty.

**Neither is the better system.** The question "which is better" was incomplete, and the metric you picked was quietly answering a different question than the one your product asks.

> [!IMPORTANT]
> Pick the cutoff from how the result is used, before you measure. A retrieval
> system feeding three sentences to a model should be measured at 3. One
> answering a question directly should be measured at 1. Choosing the metric
> afterwards, once you have seen the numbers, is how you end up reporting
> whichever one happened to favour the thing you built.

<br>

## And the distribution says more than any of them

> shared words: place 1: 15, place 2: 2, place 3: 1, place 4: 1, place 5: 1
> bm25: place 1: 13, place 2: 2, place 4: 1, place 6: 1, place 7: 2, place 9: 1

Word matching **never puts the answer below place 5**, on any of the twenty questions. That is a much stronger statement than "75% correct", and it is actionable: show five results and this system is right every single time.

Bm25 has a tail out to place 9. Same rough accuracy at the top, and a worse failure mode.

> [!TIP]
> Print the distribution before you print the average. A single number cannot
> distinguish a system that is usually right and occasionally close from one
> that is usually right and occasionally lost, and those two need completely
> different work.

<br>

## Check yourself

```
python tools/run_lessons.py phases/05-finding-the-right-thing-to-say/04-measuring-search-properly
```

<br>

## Going further

Optional, and there is no check for it.

Twenty questions is a small evaluation set, and the gap between 12 and 13 found first is one question. Work out how much of the difference between these systems could be luck: if you had written twenty different questions, would the ranking hold? That instinct, distrusting a one question gap, is worth more than any metric on this page.

<br>

## What you learned

- Recording the place keeps the information that a verdict throws away.
- Found-by-k, average reciprocal place and worst place each answer a different question.
- Two systems can swap order depending on the cutoff, and both orderings are correct.
- Choose the cutoff from how the result is used, before measuring.
- The distribution of places says more than the average, and names the failure mode.
- A one question gap on twenty questions is not a result.

**Next:** [5. Retrieve, then answer](../05-retrieve-then-answer/), where search and the language model are put together, and the join between them turns out to be where the difficulty lives.
