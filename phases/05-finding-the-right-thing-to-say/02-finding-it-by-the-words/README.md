# 2. Finding it by the words

> **The model got 0 of 20. Counting shared words gets 15.**
>
> No training, no vectors, no model of any kind. Take the question, take a
> sentence, count how many words they have in common, and sort.

**You will:** build the simplest search that works, compare it against four more sophisticated ones, and find out which actually wins.

**You need:** [lesson 1](../01-it-has-read-it-and-cannot-recall-it/).

<br>

## The simplest thing

```python
def shared(query, document):
    return len(set(query) & set(document))
```

That is the whole search engine. *How often are credentials rotated* shares *credentials* and *rotated* with the right sentence and shares less with everything else, so it wins.

<br>

## Four refinements worth trying

**Divide by length.** A long sentence has more words, so it has more chances to share one. Dividing by the square root of its length stops length alone winning.

**Weight rare words.** *Credentials* appearing in both is far more telling than *the* appearing in both. This is the same surprise idea from phase 3, and it has the same name here: **inverse document frequency**.

**Both together.**

**BM25.** What real search engines use. Rare words count for more, repeated words count for progressively less as they repeat, and length is corrected against the corpus average. It has been the standard for thirty years.

<br>

## Your turn

Score all five and write `.work/results.tsv`:

```
method           first    within_three    asked
shared words     15       18              20
bm25             13       15              20
```

<br>

## What the solution prints

<!-- output: solve.py -->
```text
217 sentences to search, 20 questions

  method              right first    in the top 3
  shared words        15 of 20    75%     18 of 20    90%
  shared / length     13 of 20    65%     16 of 20    80%
  rare words          12 of 20    60%     16 of 20    80%
  rare / length       14 of 20    70%     15 of 20    75%
  bm25                13 of 20    65%     15 of 20    75%

Best: shared words

  asked:  how long does the test suite take
  found:  the test suite takes twelve minutes to run
          correct

  asked:  how often are credentials rotated
  found:  credentials in the vault are rotated every ninety days
          correct

  asked:  where are the credentials kept
  found:  credentials in the vault are rotated every ninety days
          wanted: the vault holds the credentials the service reads at startup

  asked:  how many users did the incident affect
  found:  the incident lasted twenty minutes and affected four hundred users
          correct
```
<!-- end output -->

<br>

## The simplest one wins

| Method | Right first | In the top 3 |
| --- | --- | --- |
| **shared words** | **15 of 20, 75%** | **18 of 20, 90%** |
| shared / length | 13, 65% | 16, 80% |
| rare words | 12, 60% | 16, 80% |
| rare / length | 14, 70% | 15, 75% |
| bm25 | 13, 65% | 15, 75% |

Thirty years of refinement, beaten by counting.

> [!IMPORTANT]
> Do not take the wrong lesson from this. BM25 is not worse than counting
> words. BM25 is better than counting words on the corpora it was designed
> for, which are millions of documents of wildly varying length, where a
> thousand word page would otherwise beat a ten word answer every time.
>
> This corpus is 217 sentences, all roughly the same short length, and the
> questions are short too. Every problem BM25 solves has been removed from it.
> Its extra machinery has nothing to fix and some noise to add: with 217
> documents the rarity estimates are themselves unreliable.
>
> The lesson is not "use the simple thing". It is **measure on your data**. A
> method's reputation was earned on somebody else's problem.

<br>

## Where it still fails

> asked: *where are the credentials kept*
> found: *credentials in the vault are rotated every ninety days*
> wanted: *the vault holds the credentials the service reads at startup*

Both sentences contain *credentials*. Both contain *vault*. The question asks where something is **kept**, and the right sentence says **holds**, which shares no letters with *kept*.

Word matching cannot see that *kept* and *holds* mean the same thing. It has no idea that any two words are related, which is exactly the wall from phase 3 lesson 1, met again in a different job.

And this is the characteristic failure of keyword search generally: it fails when the asker and the document chose different words for the same thing, which is most of the time in real use.

<br>

## Check yourself

```
python tools/run_lessons.py phases/05-finding-the-right-thing-to-say/02-finding-it-by-the-words
```

<br>

## Going further

Optional, and there is no check for it.

Remove the twenty commonest words from both the query and the sentences before matching, which is what a **stop word list** does. Then measure. It helps on some queries and hurts on others, and whether it helps overall is a question about your corpus that nobody can answer from a blog post.

<br>

## What you learned

- Counting shared words is a working search engine, and it beat the language model 15 to 0.
- Length normalisation, rarity weighting and BM25 all exist to fix real problems.
- None of them helped here, because this corpus does not have those problems.
- A method's reputation was earned on a different corpus from yours.
- Word matching cannot connect *kept* with *holds*, and that is its defining failure.

**Next:** [3. Finding it by meaning](../03-finding-it-by-meaning/), where the vectors from phase 3 get a job that actually suits them.
