# Phase 8. Shipping: cost, latency, failure, safety

**Five lessons. About three hours. Still nothing installed.**

Phase 7 established what the system does and does not do. This phase is about everything else that decides whether it survives contact with a user: what it costs, what happens when the corpus is a thousand times bigger, what happens when a piece of it stops working, and what happens when somebody indexes a folder they should not have.

The last lesson is the course's deliverable: not a model and not a score, but the page you hand to somebody else.

<br>

## The lessons

| # | Lesson | The idea underneath it |
| --- | --- | --- |
| 1 | [Counting the work](01-counting-the-work/) | The average is a cost nothing has |
| 2 | [When the corpus grows](02-when-the-corpus-grows/) | An optimisation you can check by equality |
| 3 | [When something fails](03-when-something-fails/) | The total outage no alarm can see |
| 4 | [What it must not say](04-what-it-must-not-say/) | Retrieval cannot hold a boundary |
| 5 | [The thing you ship](05-the-thing-you-ship/) | Thirteen numbers, four of them negative |

<br>

## The data

Nothing new except `private.txt`: eight sentences that must never be returned, of the kind that reach a document store because a folder was included or a ticket quoted a config file. They are the only data in the course whose correct treatment is to be unreachable.

<br>

## Five results worth carrying

**The mean cost is a cost nothing has.** Twenty-three questions cost nothing because a tool answers them, twenty-five cost about 1300 because they search the whole corpus, and the mean of 687 falls in a gap containing zero questions. The mean is also below the median, which is the giveaway for two populations.

**Refusing costs more than answering.** A declined question costs 1284 comparisons against 488 for an answered one, because the corpus is searched in full before the result is found to be below the threshold and thrown away. Caution does not reduce the bill.

**An index does identical work for 12% of the comparisons.** Same answer to all 25 questions, seven lines. The next obvious step, dropping the commonest word, is six times faster again and lowers every score by one, so a threshold set two phases earlier went from admitting 13 questions to 5 without anybody editing it.

**A total corpus outage is invisible.** Accuracy falls 15%, false statements fall from four to zero, latency improves and nothing raises. The only number that moves decisively is the share of searches clearing the threshold, which goes from 13 of 25 to 0.

**A question about next quarter's budget returns an API key.** Two of three leaks came from questions that asked for nothing sensitive. A blocked word list on the question stopped one of three and refused a legitimate question about credential rotation. Not indexing the sentences stopped all three and cost nothing.

> [!WARNING]
> Robustness that swallows a failure is not robustness. The guard that stops
> an empty corpus raising `IndexError` is what turns a page-somebody outage
> into a system that returns 200 and quietly declines everything.
>
> Handle the failures you can do something about. Let the rest crash.

<br>

## Check the phase

```
python tools/run_lessons.py phases/08-shipping-cost-latency-failure-safety
```

<br>

## The end of the course

```
python tools/run_lessons.py
python tools/progress.py
```

Nine phases, one system, no dependency installed and nothing downloaded.

The habit the whole thing was arranged to build is in the last lesson: **when you cannot say how you would measure it, you do not know it yet.** It is why the retry loop is absent from the final system, why phase 3's classifier is reported as a failure, and why the release sheet has a section saying what it does not establish.
