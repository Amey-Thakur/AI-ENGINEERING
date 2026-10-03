# 5. Retrieve, then answer

> **You have a search that finds the right sentence 75% of the time, and a
> model that knows how to produce text.**
>
> The obvious move is to join them: find the sentence, hand it to the model,
> let the model answer. That shape has a name and a great deal of enthusiasm
> behind it. This lesson measures whether the second half earns its place.

**You will:** build the full pipeline, measure it against each half alone, and find that adding the model makes the system strictly worse.

**You need:** [lesson 4](../04-measuring-search-properly/).

<br>

## Three systems, one measurement

**The model alone.** Lesson 1: 0 of 20.

**Retrieve and return it.** Search, then hand back the sentence you found, unchanged. No generation at all.

**Retrieve, then generate.** Search, then let the language model continue from what was found, the way a real system would have it rephrase or answer in context.

All three scored the same way: does the reply contain the part of the answer the question did not already have?

<br>

## Your turn

Build all three and write `.work/results.tsv`:

```
system                    right    asked
model alone               0        20
retrieve and return it    15       20
retrieve then generate    0        20
```

<br>

## What the solution prints

<!-- output: solve.py -->
```text
  system                    right
  model alone, lesson 1      0 of 20    0%
  retrieve and return it    15 of 20   75%
  retrieve then generate     0 of 20   0%

  asked:      how long does the test suite take
  retrieved:  the test suite takes twelve minutes to run
              the right sentence
  generated:  the meeting was watching
              lost the answer

  asked:      how often are credentials rotated
  retrieved:  credentials in the vault are rotated every ninety days
              the right sentence
  generated:  credentials the readme is a baseline that takes longer than expected and were never rotated
              lost the answer

  asked:      where are the credentials kept
  retrieved:  credentials in the vault are rotated every ninety days
              wrong sentence
  generated:  credentials in the suite locally takes longer than delete them
              lost the answer

Questions where retrieval was right and generating lost it: 15
Questions where retrieval was wrong, so nothing downstream could help: 5
```
<!-- end output -->

<br>

## The generate step destroys the answer

| System | Right |
| --- | --- |
| Model alone | 0 of 20 |
| **Retrieve and return it** | **15 of 20** |
| Retrieve, then generate | 0 of 20 |

Read the first example. Search found *the test suite takes twelve minutes to run*, which is exactly right. The model then turned it into *the meeting was watching*.

**Fifteen questions where retrieval was right and generating lost it.** Every single correct retrieval, destroyed by the step that came after it.

> [!WARNING]
> A pipeline is not the sum of its parts. Every stage can lose information the
> previous one had, and a stage that is worse than doing nothing makes the
> whole system worse than its own middle.
>
> The version of this that matters in practice is quieter: a model that
> summarises retrieved text, and drops the qualifier. A reranker that demotes
> the right document. A rewriter that turns a precise question into a vague
> one. Each looks like an improvement on its own terms.

<br>

## So when is the generate step worth it?

Not never. It earns its place when it can do something returning the sentence cannot:

- **Combining** several retrieved passages into one answer
- **Answering in context**: "no, that applies to the old version"
- **Rephrasing** to match the question, rather than making the reader translate
- **Declining**: saying the documents do not contain the answer

Every one of those requires a generator strong enough to add something. A bigram model is not, and neither is a weak model at any scale. The question is not whether generation is good, it is whether **your** generator beats doing nothing, and that is measurable before you build anything on it.

> [!TIP]
> The measurement in this lesson takes twenty questions and an afternoon. It
> is worth running before adopting a pipeline shape, not after. Returning the
> retrieved passage is a perfectly good product, it is cheap, it cannot invent
> anything, and it shows its source.

<br>

## The ceiling nothing downstream can raise

Five questions had the wrong sentence retrieved. For those, no generator, however capable, could produce the right answer: the information never reached it.

**Retrieval sets the ceiling of everything after it.** If search finds the right passage 75% of the time, the whole system's honest maximum is 75%, and any reported number above that is the model answering from memory rather than from your documents, which is the thing retrieval was added to prevent.

That makes lesson 4's measurement the important one in this phase. Improving retrieval raises the ceiling. Improving generation only closes the gap to it.

<br>

## Check yourself

```
python tools/run_lessons.py phases/05-finding-the-right-thing-to-say/05-retrieve-then-answer
```

<br>

## Going further

Optional, and there is no check for it.

Hand the model the top **three** retrieved sentences instead of one. Retrieval's ceiling rises from 15 to 18, because the answer is in the top three that often. Then measure whether the generated reply improves. It does not, and the gap between the raised ceiling and the unchanged result is the clearest picture you will get of which half of your pipeline is the problem.

<br>

## Phase 5 complete

```
python tools/run_lessons.py phases/05-finding-the-right-thing-to-say
```

You showed a model cannot recall what it has read, built a search that beat it 15 to 0 with a dozen lines, found the simplest scoring beat BM25 on this corpus, built meaning based search and measured it honestly to zero on paraphrases, learned to measure search by where the answer lands rather than whether it came first, and then joined the pieces and found the join made things worse.

The engineering lesson of the phase is the last one. **Every component you add can subtract.** The only way to know is to measure the system with it and without it, which almost nobody does, because the shape came recommended.

**Next:** [Phase 6](../../06-tools-and-agents/), where the model stops answering from text and starts deciding to do things.
