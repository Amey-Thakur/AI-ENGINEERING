# Phase 7. Measuring whether any of it works

**Five lessons. About three hours. Still nothing installed.**

Phase 6 finished with an agent, a scorecard and an open question about which of two versions was better. This phase answers it, and on the way it turns the same instruments on the previous six phases and finds that several of their headline numbers establish very little.

Nothing new is built here. Every measurement is made on systems this course already has, which is the only way to find out whether they work.

> [!NOTE]
> This is the phase that criticises the course. Phase 3's classifier turns out
> to be indistinguishable from a coin, phase 6's threshold turns out to have
> been chosen on the answers, and the entire retrieval half of the agent turns
> out to be invisible to the test set that was used to justify it.
>
> None of those were known when the lessons were written. They were found by
> the programs in this phase, which is what the programs are for.

<br>

## The lessons

| # | Lesson | The idea underneath it |
| --- | --- | --- |
| 1 | [The number has error bars](01-the-number-has-error-bars/) | Twenty examples buys plus or minus twenty points |
| 2 | [Is the difference real?](02-is-the-difference-real/) | Compare on the same examples, not on the totals |
| 3 | [The baseline you forgot](03-the-baseline-you-forgot/) | What does an empty function score |
| 4 | [The test set you keep looking at](04-the-test-set-you-keep-looking-at/) | The choice generalised, the number did not |
| 5 | [A test you can actually run](05-a-test-you-can-actually-run/) | Minus five was twelve questions |

<br>

## The data

`measurements.tsv` lists every score this course has reported, with its denominator, so that intervals can be put on all of them at once.

`fresh.tsv` and `fresh-impossible.tsv` hold twenty questions written after phase 6's threshold was fixed, from the corpus subjects rather than its sentences. They exist so that one number in the course has been measured on questions that did not influence it.

`expectations.tsv` records what the finished agent does on all 48 questions, one line each, failures included. It is the regression test, and it is 48 lines long because that is how long a useful one is.

<br>

## Five results worth carrying

**Every comparative number in phases 1 to 3 has an interval overlapping every other one.** Eighteen of twenty could truly be anywhere from 68% to 99%; eleven of twenty from 32% to 77%. Twenty examples cannot separate a rule from a network from a bag of word vectors.

**The course's soundest claim is its most negative one.** A score of 0 of 20 pins the true rate to 0% to 16.8%, the narrowest interval anywhere in the material. Showing that something does not work is cheap, and showing that one thing beats another needs ten times the data.

**The same two agents, the same 48 questions, two opposite answers.** Counting correct behaviour, 35 against 40, which chance produces 22.7% of the time. Counting false statements, 13 against 4, which chance produces 0.4% of the time. The accuracy gap is unresolved and the honesty gap is established.

**Deleting the whole search half costs seven questions and removes every false statement.** Against the confident agent, that difference arises by chance 83% of the time. Five phases of retrieval work cannot be distinguished from its own absence on the test set that was used to justify it.

**A change that read as minus five had moved twelve questions**, three of them for the better, and it passed a statistically honest band test without a murmur.

> [!IMPORTANT]
> A number is a claim, and a claim needs four things: a denominator, a
> baseline, a comparison on the same examples, and a set of examples that
> existed before the thing being measured.
>
> Most reported numbers are missing at least two of them. That is the whole
> phase.

<br>

## What it cost to find out

None of this needed a library, a GPU, or an hour. The exact binomial interval is a sum and forty halvings. McNemar's test is a coin and a binomial coefficient. A baseline is `return None`. A regression test is a tab separated file.

The reason these are rare in practice is not that they are difficult.

<br>

## Check the phase

```
python tools/run_lessons.py phases/07-measuring-whether-any-of-it-works
```

**Next:** [Phase 8](../08-shipping-cost-latency-failure-safety/), where the system meets a user, a bill, and a bad day.
