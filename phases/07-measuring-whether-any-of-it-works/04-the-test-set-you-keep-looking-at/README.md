# 4. The test set you keep looking at

> **Phase 6 set the search threshold to 3. Where did 3 come from?**
>
> It came from trying every value on the 48 questions and keeping whichever
> scored highest, which is the thing every course tells you never to do, and
> which this course did in front of you without mentioning it.

**You will:** repeat that sweep against twenty questions written afterwards, find that the warning does not land the way you expect, and find the thing that actually broke.

**You need:** [lesson 3](../03-the-baseline-you-forgot/).

<br>

## The shape of a number chosen on its own test set

```
bar 0   35 of 48
bar 1   35 of 48
bar 2   35 of 48
bar 3   40 of 48
bar 4   34 of 48
```

Look at that as a shape rather than a table. Three flat values, a **spike of five**, then a cliff. One setting is five questions better than either of its neighbours.

A threshold that is genuinely right is usually right over a range, because the quantity it cuts is continuous and the data on either side of the cut is similar. A single isolated peak is what a parameter looks like when it has found the particular questions in front of it.

> [!NOTE]
> This is the cheapest overfitting check there is, and it needs no held out
> data at all. Sweep the parameter and look at the curve. A plateau is a
> finding. A spike is a coincidence until something else says otherwise.

<br>

## Twenty questions written afterwards

`fresh.tsv` holds twelve more questions the corpus can answer, and `fresh-impossible.tsv` eight more it cannot. Both were written after the threshold was fixed, from the corpus subjects rather than from its sentences.

<br>

## Your turn

Sweep every threshold over both sets and write `.work/sweep.tsv`:

```
bar  chosen on  fresh  fresh answerable  fresh unanswerable
0    35         10     10                0
1    35         10     10                0
2    35         11     10                1
3    40         13     9                 4
4    34         11     3                 8
```

<br>

## What the solution prints

<!-- output: solve.py -->
```text
Every threshold, on the 48 questions it was chosen on and 20 written afterwards.

  bar   the 48 it was chosen on   the 20 written after
    0      35 of 48   72.9%         10 of 20   50.0%
    1      35 of 48   72.9%         10 of 20   50.0%
    2      35 of 48   72.9%         11 of 20   55.0%
    3      40 of 48   83.3%         13 of 20   65.0%  <= phase 6 picked this
    4      34 of 48   70.8%         11 of 20   55.0%
    5      34 of 48   70.8%          9 of 20   45.0%
    6      33 of 48   68.8%          8 of 20   40.0%

  best on the 48:      bar 3, scoring 83.3% there and 65.0% on the fresh questions
  best on the fresh 20: bar 3, scoring 65.0%
  choosing on the test set cost 0 questions

Where the fresh questions were lost, at the threshold that was chosen:

                      the 25 it was chosen on   the 20 written after
  answered correctly     9 of 15   60.0%           9 of 12   75.0%
  declined correctly     8 of 10   80.0%           4 of  8   50.0%
```
<!-- end output -->

<br>

## The choice was fine. The number was not.

Bar 3 is still the best threshold on questions it has never seen. Every other value is worse there too, in the same order. **Choosing on the test set cost zero questions.**

That is worth saying plainly, because the usual telling of this lesson implies the choice will be wrong, and here it is not. One parameter over seven values, with a real effect underneath it, transferred perfectly.

What did not transfer is the score. **83.3% became 65.0%**, a drop of eighteen points, for a system nobody changed.

> [!IMPORTANT]
> Two different things get called overfitting and they need separating,
> because only one of them happened here.
>
> **A choice that does not generalise**: the value you picked is worse than
> some other value on new data. Measured here, and it is zero.
>
> **A number that does not generalise**: the score you reported alongside the
> choice is higher than the system will ever achieve again. Measured here,
> and it is eighteen points.
>
> The second is guaranteed whenever you report the best of several
> measurements, even when the choice is perfect, because you reported a
> maximum and maxima are optimistic. It does not matter how principled the
> search was.

<br>

## Where the eighteen points went

| At bar 3 | The questions it was chosen on | The twenty written after |
| --- | --- | --- |
| Answered correctly | 9 of 15 (60.0%) | **9 of 12 (75.0%)** |
| Declined correctly | **8 of 10 (80.0%)** | 4 of 8 (50.0%) |

The answering got **better**. The declining **halved**.

The threshold exists for one purpose: to make the system refuse questions it cannot answer. That is the only thing it does. And it is the one thing that did not survive contact with new questions, because a bar of 3 was not fitted to the idea of an unanswerable question, it was fitted to **those particular ten**.

> [!CAUTION]
> The headline fell by eighteen points while one of its two halves rose. An
> average over sub-populations can move in the opposite direction to the
> thing you care about, and it does so most easily when the populations are
> different sizes.
>
> If your system has a job it does rarely and a job it does constantly, the
> overall number is a measurement of the constant one. Report them apart.

<br>

## And read the fresh column all the way down

```
bar    fresh answerable    fresh unanswerable
  3          9 of 12             4 of 8
  4          3 of 12             8 of 8
  6          0 of 12             8 of 8
```

By bar 4 the system declines every unanswerable question and has stopped answering nine of the twelve it could have. That is phase 6's dial, seen from the other side: there is no setting that is good at both, and the sweep is just a list of exchange rates between them.

<br>

## This one is twenty questions too

Lesson 1 applies to everything above. 13 of 20 puts the true rate somewhere between **40.8% and 84.6%**, and 65% against 83% is well inside what two samples of that size do on their own.

That is not a reason to ignore the result. The breakdown is where the finding lives, and 8 of 10 against 4 of 8 on a capability the threshold was tuned for is the kind of thing worth acting on before it is proven. It is a reason not to quote 65% as the number.

<br>

## Check yourself

```
python tools/run_lessons.py phases/07-measuring-whether-any-of-it-works/04-the-test-set-you-keep-looking-at
```

The check insists bar 3 wins on both sets, because the lesson is not that the choice was wrong.

<br>

## Going further

Optional, and there is no check for it.

Split the original 48 into a part you tune on and a part you report from, pick the threshold on the first, and score it on the second. You will get a number between 83% and 65%, and it will still be optimistic, because both halves were written on the same afternoon in the same mood.

Then write ten more unanswerable questions, deliberately about subjects the corpus does discuss, and watch the decline rate fall again. How hard your unanswerable questions are is a decision you make while writing them, and nobody who reads the score will know which decision you made.

<br>

## What you learned

- Sweeping a parameter and keeping the best is choosing on your test set, and a spike rather than a plateau is the free warning sign.
- A choice made that way can generalise perfectly, and here it did: bar 3 wins on fresh questions too, at a cost of zero.
- The score reported alongside it does not generalise, because it is a maximum over several measurements, and maxima are optimistic by construction.
- The chosen threshold's rate fell eighteen points on fresh questions while the system was not touched.
- The half that collapsed was declining the unanswerable, from 80% to 50%, which is the only job the threshold has.
- An average over sub-populations can fall while one of them rises, so report the parts separately.
- Twenty questions puts that 65% somewhere between 41% and 85%, and the breakdown is worth more than the headline.

**Next:** [5. A test you can actually run](../05-a-test-you-can-actually-run/), where all of this becomes a file that fails a pull request.
