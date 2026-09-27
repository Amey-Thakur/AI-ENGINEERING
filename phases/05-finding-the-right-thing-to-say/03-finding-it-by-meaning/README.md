# 3. Finding it by meaning

> **Keyword search fails when the asker and the document chose different words.**
>
> That is most of the time in real use, and it is exactly what word vectors
> were supposed to fix. This lesson builds that fix, tests it honestly, and
> reports what happened.

**You will:** search by meaning instead of by words, on two sets of questions designed to tell the two approaches apart.

**You need:** [lesson 2](../02-finding-it-by-the-words/), [phase 3](../../03-words-that-know-what-they-mean/).

<br>

## Making the test fair first

Look at the questions from lesson 2:

> *how often are credentials rotated* → *credentials in the vault are **rotated** every ninety days*

The question uses the answer's own words. Of course word matching wins: the test was built in its favour without anyone intending it.

So `paraphrases.tsv` asks for the same twenty sentences in different words:

> *how frequently do secrets change* → *credentials in the vault are rotated every ninety days*
> *why did the machine reboot* → *the server ran out of memory and restarted itself*

Measured, rather than asserted: the original questions share **2.9** words with their answers, the paraphrases share **0.7**.

> [!IMPORTANT]
> Doing this is the lesson as much as anything that follows. A benchmark
> written by the person who built one of the systems will flatter that system,
> usually by accident. Before believing any comparison, look at what the
> queries are and ask who they suit.

<br>

## Searching by meaning

Average the word vectors in the sentence, average the word vectors in the query, and rank by cosine. If *reboot* and *restarted* have nearby vectors, the right sentence should come back even with no word in common.

Three ways of averaging are tried, because averaging is where this approach usually goes wrong: every word, then skipping the 25 commonest, then weighting by rarity.

<br>

## Your turn

Measure both methods on both question sets. Write `.work/results.tsv`:

```
questions                 method            first    within_three    asked
worded like the answer    matching words    15       18              20
worded differently        matching words    0        0               20
```

<br>

## What the solution prints

<!-- output: solve.py -->
```text
217 sentences, 608 words with vectors

Words a question shares with its own answer:
  worded like the answer   2.9
  worded differently       0.7

Questions worded like the answer:
  matching words                 first 15 of 20   top 3 18 of 20
  meaning, every word            first  6 of 20   top 3  8 of 20
  meaning, without the commonest first  3 of 20   top 3  7 of 20
  meaning, weighted by rarity    first  6 of 20   top 3 11 of 20

Questions worded differently:
  matching words                 first  0 of 20   top 3  0 of 20
  meaning, every word            first  0 of 20   top 3  0 of 20
  meaning, without the commonest first  0 of 20   top 3  0 of 20
  meaning, weighted by rarity    first  0 of 20   top 3  0 of 20
```
<!-- end output -->

<br>

## Two results, and the second one matters more

**When questions use the answer's words**, matching words wins easily: 15 of 20 against 6. Averaged vectors blur a sentence into its general subject, and every sentence about deployment looks alike, so the specific one is hard to pick out. Same failure as phase 3 lesson 5, in a new job.

**When questions are worded differently, everything scores zero.** Word matching gets 0 of 20, which was expected. Meaning based search gets 0 of 20, which was not the plan.

All three ways of averaging: zero. Not "worse", not "a bit unreliable". None of the twenty.

<br>

## Why the honest answer is "not enough text"

*Reboot* appears in the corpus once. *Restarted* appears four times. For their vectors to end up near each other, the corpus has to contain enough sentences using both in similar company for the statistics to notice.

With 2,019 words of corpus, it does not, and no amount of rearranging the averaging changes that. The information is not in the data.

> [!IMPORTANT]
> This is what "semantic search" costs, and it is rarely stated plainly.
>
> The sentence encoders that make it work are trained on billions of words,
> because connecting *reboot* to *restarted* requires having seen both used
> many times in many contexts. "Just use embeddings" is not advice, it is an
> assumption that somebody else already spent the compute.
>
> Building the representation yourself from the corpus you happen to have
> gives you what you see here: zero.

<br>

## So what should you actually do

At this scale, **use keyword search**. It gets 15 of 20 when the words line up, it is a dozen lines, it needs no training, it never invents anything, and you can always see why it returned what it did.

If your users really do ask in words your documents never use, you need a representation trained on far more text than you own, which means using one somebody else trained. That is a legitimate choice with real costs: a dependency, a download, and a model you cannot inspect.

What is not legitimate is reaching for vectors because they sound more advanced, without measuring whether word matching was already enough.

<br>

## Check yourself

```
python tools/run_lessons.py phases/05-finding-the-right-thing-to-say/03-finding-it-by-meaning
```

The check verifies for itself that the paraphrases really do avoid their answers' words, before it accepts any conclusion drawn from them.

<br>

## Going further

Optional, and there is no check for it.

Take one paraphrase, *why did the machine reboot*, and look up the nearest neighbours of *reboot* and of *machine* in the vectors. Neither will be near *server* or *restarted*. You are looking directly at the reason the search failed, which is a better habit than concluding that a method does not work.

<br>

## What you learned

- A benchmark written alongside a system will flatter that system unless you check.
- Averaging word vectors blurs a sentence towards its subject, losing what makes it specific.
- On questions worded like the answer, word matching beat meaning search 15 to 6.
- On questions worded differently, everything scored zero, with three different ways of averaging.
- Connecting two words that mean the same thing requires far more text than a small corpus has.
- Keyword search is the right default at this scale, and "use embeddings" assumes someone else's compute.

**Next:** [4. Measuring search properly](../04-measuring-search-properly/), where counting how often the first result is right turns out to be the wrong measurement.
