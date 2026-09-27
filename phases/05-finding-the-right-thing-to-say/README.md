# Phase 5. Finding the right thing to say

**Five lessons. About four hours. Still nothing installed.**

Phase 4 ended with a language model that beat counting by 12% and still could not tell you a single fact. This phase is about the difference between those two things, and about the idea that fixes it: stop asking the model to remember, and go and look it up.

<br>

## The lessons

| # | Lesson | The idea underneath it |
| --- | --- | --- |
| 1 | [It has read it and cannot recall it](01-it-has-read-it-and-cannot-recall-it/) | Storing statistics about text is not storing the text |
| 2 | [Finding it by the words](02-finding-it-by-the-words/) | A dozen lines beat the model 15 to 0 |
| 3 | [Finding it by meaning](03-finding-it-by-meaning/) | What semantic search actually costs |
| 4 | [Measuring search properly](04-measuring-search-properly/) | The metric quietly answers a different question |
| 5 | [Retrieve, then answer](05-retrieve-then-answer/) | Every component you add can subtract |

<br>

## The data

Alongside the corpus, this phase adds two files of twenty questions each, both answered by sentences already in the corpus.

`questions.tsv` words each question much as its answer is worded. `paraphrases.tsv` asks for the same twenty sentences while avoiding their words: *why did the machine reboot* for *the server ran out of memory and restarted itself*.

That second file exists because the first one flatters keyword search without meaning to, and a benchmark written alongside a system will always do that unless somebody checks. Measured: the first set shares 2.9 words with its answers, the second 0.7.

<br>

## Four results worth carrying

**The model recalls 0 of 20 answers that are in its own training data.** It has counted every one of those sentences. Specific facts are the first thing a statistical summary discards.

**Counting shared words beats BM25 here.** Thirty years of search refinement, losing to `len(set(a) & set(b))`, because this corpus has none of the problems BM25 was built to solve. The lesson is not "use the simple thing", it is that a method's reputation was earned on somebody else's data.

**Meaning based search scores zero on paraphrases**, with three different ways of averaging. Connecting *reboot* to *restarted* needs far more text than 2,019 words. "Just use embeddings" assumes somebody else already spent the compute.

**Adding the generator made the system worse**, from 15 of 20 down to 0. Every correct retrieval, destroyed by the step after it.

> [!IMPORTANT]
> Retrieval sets the ceiling for everything downstream. If search finds the
> right passage 75% of the time, the honest maximum for the whole system is
> 75%, and any number above that is the model answering from memory rather
> than from your documents.

<br>

## Check the phase

```
python tools/run_lessons.py phases/05-finding-the-right-thing-to-say
```

**Next:** [Phase 6](../06-tools-and-agents/), where the model stops producing text about the world and starts taking actions in it.
