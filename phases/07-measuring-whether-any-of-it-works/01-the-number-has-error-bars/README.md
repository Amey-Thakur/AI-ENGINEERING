# 1. The number has error bars

> **Phase 5 built a search that found the right sentence 15 times out of 20
> and called it 75% accurate.**
>
> A system that is truly 50% accurate scores 15 or better out of 20 about
> twice in a hundred tries. A system that is truly 90% accurate does it about
> half the time. Both of those are alive after seeing 15 of 20, and they are
> not the same system.

**You will:** compute exactly what each score in this course establishes, find that the course's own comparisons rest on nothing, and work out how many examples a claim actually needs.

**You need:** nothing beyond [phase 6](../../06-tools-and-agents/). No new data.

<br>

## What a fraction establishes

Turn the question around. Instead of asking what the system's accuracy is, ask which accuracies could have produced what you saw.

```
a system truly   50% right scores 12 or more of 15   1.8% of the time
a system truly   60% right scores 12 or more of 15   9.1% of the time
a system truly   70% right scores 12 or more of 15  29.7% of the time
a system truly   80% right scores 12 or more of 15  64.8% of the time
a system truly   90% right scores 12 or more of 15  94.4% of the time
```

A true rate of 50% is a poor explanation of 12 of 15. A true rate of 70% is a perfectly ordinary one. Keep every rate that is not a poor explanation, in either direction, and you have the interval.

That is all a confidence interval is. The version computed here is the exact binomial one, sometimes called Clopper and Pearson after the 1934 paper, and it is worth knowing it has a name because you will want to look it up.

> [!NOTE]
> Nothing here is simulated. No resampling, no random seeds, no bootstrap.
> The chance of scoring `k` or more out of `n` at a given rate is a sum you
> can write down, and the two ends of the interval are found by halving a
> range forty times.
>
> This matters for the same reason the rest of the course cares: a number
> that comes out of a random process is a number somebody has to reproduce,
> and this one is identical on every machine forever.

<br>

## Your turn

For every row of `measurements.tsv`, compute the interval and write `.work/intervals.tsv`:

```
what                                       right  asked  low   high
phase 1 lesson 2, the hand written rule    18     20     68.3  98.8
phase 1 lesson 4, the perceptron           15     20     50.9  91.3
...
```

Write the ends as percentages. The check allows a fifth of a point either way, so the exact number of halvings is up to you.

<br>

## What the solution prints

<!-- output: solve.py -->
```text
Every score in this course, and what it establishes.

  measurement                                       score      could truly be        width
  phase 1 lesson 2, the hand written rule           18 of 20   68.3% to 98.8%   30.5%
  phase 1 lesson 4, the perceptron                  15 of 20   50.9% to 91.3%   40.4%
  phase 2, the network you wrote                    15 of 20   50.9% to 91.3%   40.4%
  phase 3, word vectors averaged                    11 of 20   31.5% to 76.9%   45.4%
  phase 3, the first word and the average           13 of 20   40.8% to 84.6%   43.8%
  phase 5, search finding the right sentence        15 of 20   50.9% to 91.3%   40.4%
  phase 5, the model recalling what it read          0 of 20    0.0% to 16.8%   16.8%
  phase 6, search on its own questions              12 of 15   51.9% to 95.7%   43.8%
  phase 6, the confident agent                      35 of 38   78.6% to 98.3%   19.7%
  phase 6, the cautious agent                       32 of 38   68.7% to 94.0%   25.2%
  phase 6, declining the unanswerable                8 of 10   44.4% to 97.5%   53.1%
  phase 6, the routing rule on held back questions   6 of  8   34.9% to 96.8%   61.9%

  widest:    phase 6, the routing rule on held back questions
             6 of 8 pins the true rate to within 62%
  narrowest: phase 5, the model recalling what it read
             0 of 20 pins it to within 17%

A system that is truly 80% right, measured on more and more questions:
     15 questions:   12 right, 51.9% to 95.7%, so 80% give or take 21.9%
     38 questions:   30 right, 62.7% to 90.4%, so 80% give or take 13.9%
    100 questions:   80 right, 70.8% to 87.3%, so 80% give or take 8.3%
    250 questions:  200 right, 74.5% to 84.8%, so 80% give or take 5.1%
   1000 questions:  800 right, 77.4% to 82.4%, so 80% give or take 2.5%

And what 12 of 15 rules out, which is less than you would hope:
  a system truly   50% right scores 12 or more of 15   1.8% of the time
  a system truly   60% right scores 12 or more of 15   9.1% of the time
  a system truly   70% right scores 12 or more of 15  29.7% of the time
  a system truly   80% right scores 12 or more of 15  64.8% of the time
  a system truly   90% right scores 12 or more of 15  94.4% of the time
```
<!-- end output -->

<br>

## Read the table against the course that produced it

The middle five rows are the spine of phases 1 to 3. A hand written rule got 18 of 20. A perceptron got 15. A network got 15. Word vectors got 11, and a better construction of them got 13. Each lesson reported its number and drew a conclusion from it.

Here are the same five numbers with their intervals:

| Measured | Score | Could truly be |
| --- | --- | --- |
| Hand written rule | 18 of 20 | 68.3% to 98.8% |
| Perceptron | 15 of 20 | 50.9% to 91.3% |
| The network | 15 of 20 | 50.9% to 91.3% |
| Word vectors averaged | 11 of 20 | 31.5% to 76.9% |
| First word and the average | 13 of 20 | 40.8% to 84.6% |

**Every one of those intervals overlaps every other one.** The rule at 90% and the word vectors at 55%, thirty-five points apart, share the range from 68% to 77%. Twenty examples cannot tell them apart.

> [!IMPORTANT]
> Be careful with what that does and does not prove.
>
> Overlapping intervals do **not** establish that two systems are equally
> good. Each interval above asks what one system's rate might be, in
> isolation. The systems were run on the **same twenty messages**, and a
> comparison of two systems on the same examples is a different question with
> a more powerful test, which is lesson 2.
>
> What this table establishes is narrower and still serious: **not one of
> those five numbers, on its own, pins its system down to better than thirty
> points.** Any conclusion resting on the value of a single one of them is
> resting on very little.

<br>

## The result that holds up is the negative one

The narrowest interval in the whole course belongs to the worst score in it. Phase 5's model recalled **0 of 20** facts from its own training data, and that establishes a true rate somewhere between **0% and 16.8%**.

That is a real finding. Whatever that model is doing, it is not recalling facts, and seventeen points of uncertainty does not threaten the conclusion.

> [!TIP]
> Showing that something does not work is cheap. Showing that one thing beats
> another is expensive, and the gap is not close.
>
> A score of 0 of 20 or 20 of 20 lands against the edge of the scale, where
> the interval is narrow. A score in the middle has the widest interval
> available. So the demonstrations you can afford on twenty examples are the
> ones where a system collapses, and the comparisons everyone wants to make
> need ten times the data.
>
> Phase 5's *the model cannot recall* and phase 6's *the corpus has no
> digits* are the load bearing claims in this course, and it is not an
> accident that both are negative.

<br>

## How many examples a claim needs

| Examples | A true 80% measures as | Give or take |
| --- | --- | --- |
| 15 | 51.9% to 95.7% | 22 points |
| 38 | 62.7% to 90.4% | 14 points |
| 100 | 70.8% to 87.3% | 8 points |
| 250 | 74.5% to 84.8% | **5 points** |
| 1000 | 77.4% to 82.4% | 2.5 points |

To say *about 80%, give or take five points* you need roughly **250 examples**. To resolve the two or three point differences that products are shipped on, you need a thousand.

Read that against the size of most evaluation sets, including every one in this course. Twenty examples is enough to find out whether something is broken. It is not enough to find out whether it improved.

> [!CAUTION]
> The cost is quadratic in the precision you want. Halving the error bar
> takes four times the examples, so there is no amount of diligence that gets
> you a tight number from a small set.
>
> This is the honest reason so many reported improvements evaporate. Nobody
> lied. The second measurement was inside the first one's error bar, and
> neither number was ever printed with one.

<br>

## Check yourself

```
python tools/run_lessons.py phases/07-measuring-whether-any-of-it-works/01-the-number-has-error-bars
```

<br>

## Going further

Optional, and there is no check for it.

Take the last accuracy figure you saw quoted anywhere, find the size of the test set behind it, and compute the interval. If the test set size is not stated, that is the finding.

Then compute the interval for 19 of 20 and for 20 of 20. The first is 75.1% to 99.9%, the second is 83.2% to 100%. A perfect score on twenty examples is compatible with failing one in six.

<br>

## What you learned

- A score is one sample from a system, and the interval is the set of true rates that could plausibly have produced it.
- It is computed exactly from the binomial distribution, with no sampling and no randomness.
- Twenty examples pin a mid range accuracy to about plus or minus twenty points, which is wider than most of the differences anyone argues about.
- Every comparative number in phases 1 to 3 has an interval overlapping every other one, so no single one of them establishes much.
- Overlapping intervals are not proof that two systems are the same; comparing systems on the same examples is a separate and better test.
- Scores at the edges of the scale have narrow intervals, so negative results are cheap and comparisons are expensive.
- About 250 examples buys five points of precision, and a thousand buys two and a half, because the cost grows with the square.

**Next:** [2. Is the difference real?](../02-is-the-difference-real/), where the two agents from phase 6 are compared properly, on the same questions, with the test this lesson was not allowed to use.
