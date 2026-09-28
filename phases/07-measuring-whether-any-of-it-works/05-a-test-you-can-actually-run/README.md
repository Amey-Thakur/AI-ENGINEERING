# 5. A test you can actually run

> **Four lessons of careful measurement, and none of it stops somebody
> breaking the system on a Tuesday afternoon.**
>
> A measurement is something you do. A test is something that happens whether
> anybody remembers or not, and the two obvious ways to test this system both
> fail.

**You will:** watch a score-based test miss a change that moves a quarter of the questions, then write the test that catches it, and find that the whole thing rests on the system being deterministic.

**You need:** [lesson 4](../04-the-test-set-you-keep-looking-at/).

<br>

## The first attempt, and why it is worse than nothing

```python
assert correct == 40
```

It breaks on every improvement. Somebody makes search better, three more questions come right, the test goes red, and the next person to see it red deletes it.

And when it does go red it says `43 != 40`. Not which question changed, not in which direction, not whether anything got worse. Three questions improved and two regressed nets out to `+1`, and the test reports a single number that hides both.

<br>

## The second attempt, which is the sophisticated one

Lesson 1 gives a principled band. 40 of 48 puts the true rate between **69.8% and 92.5%**, so assert the score stays inside it:

```python
assert 0.698 <= correct / asked <= 0.925
```

This is the version people reach for once they have understood that a score is a sample. It is much better reasoned than the first attempt, and here it is useless.

| A change that sets the bar to | Score | Questions moved | A band test |
| --- | --- | --- | --- |
| 2 | 35 of 48 | **12** (9 worse, 3 better) | passes |
| 4 | 34 of 48 | **12** (8 worse, 4 better) | passes |

Both changes move a quarter of the questions and slip straight through, because 35 of 48 is comfortably inside the interval around 40 of 48. The band is wide for exactly the reason lesson 1 gave, and a wide band is a test that notices nothing.

<br>

## Your turn

Record what the agent currently does for all 48 questions, then check both proposed changes against that record and write `.work/drift.tsv`:

```
bar  correct  moved  worse  better  inside the band
2    35       12     9      3       yes
4    34       12     8      4       yes
```

A question has moved when its outcome differs from the recorded one. It is worse or better according to this ordering, which is phase 6's pricing written down as data:

```python
PREFERENCE = {WRONG: 0, HELD_BACK: 1, RIGHT: 2, DECLINED: 2}
```

<br>

## What the solution prints

<!-- output: solve.py -->
```text
48 recorded outcomes, taken from the agent as it stands.

  right        32
  wrong         4
  held back     4
  declined      8

That is 40 of 48 handled correctly, and lesson 1 puts the true rate
between 69.8% and 92.5%.

A change that moves the threshold from 3 to 2:
  the score goes from 40 to 35, a difference of -5
  12 of 48 questions changed: 9 worse, 3 better
  a test on the score alone would pass, seeing nothing
    held back  -> right       'why did the server restart'
    held back  -> right       'how long did the rollback take'
    held back  -> right       'where does the documentation live'
    held back  -> wrong       'what is the vault for'

A change that moves the threshold from 3 to 4:
  the score goes from 40 to 34, a difference of -6
  12 of 48 questions changed: 8 worse, 4 better
  a test on the score alone would pass, seeing nothing
    right      -> held back   'how long does the test suite take'
    right      -> held back   'how often are credentials rotated'
    wrong      -> held back   'what did the code review catch'
    right      -> held back   'which day do we deploy on'

And the agent as it stands, against the same file: 0 questions changed.
That is what a passing run looks like, and it is the only test here that is exact.
```
<!-- end output -->

<br>

## Minus five was twelve

The score said `-5`. Twelve questions moved, and three of them moved in your favour.

That gap between the net and the gross is the whole argument. A change is not a number, it is a set of questions that now behave differently, and the number is a sum in which regressions and improvements cancel. You cannot review a sum.

Read the named rows and the change explains itself: lowering the bar released four questions that were being held back, three of which were right and one of which was wrong, and it started answering unanswerable questions again. That is a description somebody can have an opinion about.

<br>

## The file records what the system does, not what it should do

`expectations.tsv` is 48 lines and four of them say `wrong`. It is not a specification. It is a snapshot, including the failures, and that is the point:

```
who is on call this weekend	declined
what did the code review catch	wrong
how long does the test suite take	right
```

When a change is deliberate, you regenerate the file and commit it **in the same commit as the change**. Then the pull request contains the diff, and the diff is the review:

```
-why did the server restart	held back
+why did the server restart	right
-who is on call this weekend	declined
+who is on call this weekend	wrong
```

Nobody has to be told that the second line is a problem.

> [!IMPORTANT]
> Recording failures as expected is the part people resist, and it is what
> makes the test work.
>
> A file that says what the system *should* do is red from the day you write
> it, so it gets an exclusion list, and the exclusion list grows until the
> test is measuring the exclusion list. A file that says what the system
> *does* is green today, goes red the moment anything moves, and every red is
> real.
>
> The four `wrong` lines are not approval. They are the current position, and
> the test's job is to tell you when the position changes without anybody
> deciding it should.

<br>

## What a failure looks like

```
FAIL  1 of 48 questions no longer do what expectations.tsv records
      right -> declined  'who is on call this weekend'
      if the change was deliberate, rerun solve.py and commit the new file alongside it
```

One line for what moved, one line for what to do. This lesson's `check.py` is that test, rather than a description of it.

> [!TIP]
> Give the failure message the command that fixes it. A test that says what
> is wrong but not what to type gets a reputation, and a test with a
> reputation gets skipped in CI with a comment saying `# flaky, fix later`.

<br>

## And none of it works without determinism

Every word above depends on one thing: run the agent twice and it does the same thing. That is what lets a test be exact, and being exact is what lets it name the question.

Take determinism away and there is nothing left but the band, which two lessons of arithmetic have just shown cannot see a change that moves twelve questions of forty-eight. A system that varies between runs cannot be regression tested at the level of the example, only at the level of the average, and the average is where the information goes to die.

> [!CAUTION]
> So determinism is not fastidiousness, and it is not about reproducible
> papers. It is the difference between a test that names the broken question
> and a test that cannot tell you anything happened.
>
> Where the system genuinely cannot be deterministic, a hosted model at
> temperature for instance, the move is to pin down everything around it: a
> fixed seed where one is offered, the temperature at zero for the test run,
> the prompt frozen in a file, and the nondeterministic call recorded once
> and replayed. What is left over gets the band, and you accept that the band
> will not catch much.

This course holds itself to it. [`tools/check_determinism.py`](../../../tools/check_determinism.py) runs every solution under three different string hash seeds and fails if the output moves, and it exists because a lesson in this phase shipped with `max(set(labels), key=labels.count)` in it, which picks a different winner depending on the order a set happens to have.

<br>

## Check yourself

```
python tools/run_lessons.py phases/07-measuring-whether-any-of-it-works/05-a-test-you-can-actually-run
```

<br>

## Going further

Optional, and there is no check for it.

Change one thing in the agent, anything at all, and run the check. Then decide from the named rows alone whether you would merge it, without looking at the score.

Then break the ordering: set `HELD_BACK` above `RIGHT` and watch the same changes get reported as improvements. Every regression test contains a value judgement about which failures are worse, and it is better to have it on one line in the open than spread through the reasoning of whoever reads the diff.

<br>

## What you learned

- A measurement is something you do; a test is something that happens without anybody remembering.
- Asserting an exact score breaks on improvements, so it gets deleted.
- Asserting the score stays inside a statistically honest band cannot see a change that moved 12 of 48 questions, because the band is wide for real reasons.
- Recording the outcome of every question turns a change from a number into a named list, and the net figure hid three improvements inside a loss of five.
- The record is a snapshot of current behaviour, failures included, not a specification, which is what keeps it green until something genuinely moves.
- Regenerate it in the same commit as the change, and the diff becomes the review.
- All of it requires the system to be deterministic, which is the precondition for a test that can name a question rather than average one.

<br>

## Phase 7 complete

```
python tools/run_lessons.py phases/07-measuring-whether-any-of-it-works
```

You put an interval on every number this course has reported and found most of them establish very little, compared two agents properly and found one difference real and the other unresolved, measured the systems that do nothing and found one of them beats most of the course, put phase 6's threshold on questions it had never seen, and turned the whole thing into a file that fails a pull request.

The phase has one idea in it. **A number is a claim, and a claim needs a denominator, a baseline, a comparison, and a set of examples that existed before the thing being measured.** Four of those are usually missing, and that is why so much reported progress is not.

**Next:** [Phase 8](../08-shipping-cost-latency-failure-safety/), where the system meets a user, a bill, and a bad day.
