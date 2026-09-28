# 4. A loop that can stop

> **Every system in this course has answered every question it was ever
> given.**
>
> Ask it *what is the database password* and it will return a sentence about
> build numbers, because returning the best available sentence is the only
> behaviour it has.

**You will:** add ten questions that have no answer, give the system a loop with three ways to stop, find that the retrying is worthless for a reason you could have proved in advance, and find that lesson 3 reached the wrong conclusion from a correct measurement.

**You need:** [lesson 3](../03-when-it-chooses-wrong/).

<br>

## Ten questions with no answer

`impossible.tsv` holds questions about this corpus that the corpus cannot answer:

```
who is on call this weekend              the corpus names no people
what is the database password            no credential appears in the corpus
how much revenue did the outage cost     the corpus contains no money
when will the migration finish           the corpus contains no dates in the future
```

These are not trick questions. They are the ordinary questions somebody asks a documentation search on their first day, and the honest answer to every one of them is that it is not in there.

<br>

## A loop with three exits

```python
def loop(question, cap):
    asked = question

    for step in range(1, cap + 1):
        found = only_if_confident(asked)

        if found is not REFUSED:
            return found, step, ANSWERED

        asked = shorten(asked)

        if not asked:
            return REFUSED, step, OUT_OF_MOVES

    return REFUSED, cap, OUT_OF_BUDGET
```

That is an agent. Not a simplified one for teaching: a loop that calls a tool, reads the result, decides whether to go again, and can terminate three different ways. Every framework you will meet adds features around this shape and none of them change it.

The three exits matter individually:

- **Answered.** A tool accepted and produced something.
- **Out of moves.** There is nothing left to try, so the system says it does not know.
- **Out of budget.** The cap stopped it, which is not a conclusion about the question, only about the spending.

<br>

## Your turn

Run all three systems over both sets of questions and write `.work/stopping.tsv`:

```
system                            questions         correct   declined   asked
answer whatever wins              15 answerable     12        0          15
only if overlap is 3 or more      15 answerable     9         4          15
loop, rewrite on refusal, cap 6   15 answerable     9         4          15
answer whatever wins              10 unanswerable   0         0          10
only if overlap is 3 or more      10 unanswerable   8         8          10
loop, rewrite on refusal, cap 6   10 unanswerable   8         8          10
```

Correct behaviour is answering an answerable question and **declining an unanswerable one**, so on the bottom three rows those two columns hold the same number.

<br>

## What the solution prints

<!-- output: solve.py -->
```text
Correct behaviour is answering an answerable question and declining an unanswerable one.

  system                            questions          correct   declined
  answer whatever wins              15 answerable     12 of 15   0
  only if overlap is 3 or more      15 answerable      9 of 15   4
  loop, rewrite on refusal, cap 6   15 answerable      9 of 15   4
  answer whatever wins              10 unanswerable    0 of 10   0
  only if overlap is 3 or more      10 unanswerable    8 of 10   8
  loop, rewrite on refusal, cap 6   10 unanswerable    8 of 10   8

  answer whatever wins              12 of 25 across both sets
  only if overlap is 3 or more      17 of 25 across both sets
  loop, rewrite on refusal, cap 6   17 of 25 across both sets

Raising the cap, on the questions that can be answered:
  cap 1: 9 of 15 right, 15 searches, 4 questions stopped by the cap
  cap 2: 9 of 15 right, 19 searches, 4 questions stopped by the cap
  cap 3: 9 of 15 right, 23 searches, 4 questions stopped by the cap
  cap 4: 9 of 15 right, 27 searches, 4 questions stopped by the cap
  cap 6: 9 of 15 right, 32 searches, 0 questions stopped by the cap

Every way the loop ended, on all 25 questions:
  answered             13
  ran out of rewrites   8
  hit the limit         4

Across 128 rewrites, the best overlap rose 0 times.
Dropping a word can only shrink the overlap with every sentence, so a question
below the bar of 3 can never get above it by being shortened.
```
<!-- end output -->

<br>

## The retrying is worth nothing

Read the cap sweep. **Nine of fifteen at every cap from 1 to 6**, while the number of searches goes from 15 to 32.

The loop doubles the work and returns the same answers. Not "a small gain for the cost", not "helps on some questions". Identical, at every budget.

<br>

## And it could never have worked

Search scores a sentence by how many words it shares with the question. Drop a word from the question and, for every sentence in the corpus, that count either stays the same or falls by one. It cannot rise.

So the best overlap across the corpus cannot rise either. A question that scored below 3 and was refused will score below 3 after being shortened, and after being shortened again, forever.

**128 rewrites, and the best overlap rose 0 times.** The measurement agrees with the algebra because the algebra was not optional.

> [!CAUTION]
> The retry loop is the single most common thing built on top of a tool, and
> here it was **provably incapable of succeeding** before a line of it was
> written. Two sentences of reasoning about the scoring function settle it.
>
> Nobody does that reasoning. The loop gets built, the results do not
> improve, and the next move is to raise the cap, which is why a system can
> end up spending four calls per question to produce what one call produced.
>
> Before you add a retry, say out loud what the second attempt knows that the
> first one did not. If the answer is nothing, you have built a delay.

<br>

## The rewrite does work, on a question the loop never reaches

This is worth seeing, because it shows the loop is broken in a more interesting way than the rewrite being useless.

Lesson 1's one search failure was *what did the code review catch*, which returned *a comment explains why and the code explains what*. Drop the leading word and it returns **the right sentence**. The rewrite fixes it.

The loop never tries. That question scores an overlap of 3, so `only_if_confident` accepts it, and the loop returns a confident wrong answer on its first step and stops.

> [!NOTE]
> The rewrite is triggered by the wrong condition. It fires when the score is
> **low**, and it is useful when the score is **high and wrong**, which is
> precisely the case no threshold can detect (lesson 3 measured exactly
> that).
>
> A retry that fires on the failures you can see, and is useful on the
> failures you cannot, will measure as worthless no matter how many times you
> raise the cap.

<br>

## The cap is still not optional

At caps of 1 through 4, **four questions were stopped by the cap** rather than by running out of rewrites. Those four would have kept going.

Here the loop terminates anyway, because a question runs out of words. That is a property of this particular rewrite and it will not survive the first change anybody makes: a rewrite that adds words, a tool that suggests another tool, a plan that can extend itself. The moment the next step is chosen at runtime, termination stops being something you can read off the code.

> [!IMPORTANT]
> Without a cap, the cost of a question is decided by the question. With a
> cap, it is decided by you. That is the whole argument, and it holds even
> when, as here, the cap never changes an answer.
>
> Put the cap in when you write the loop. It is the piece that is very hard
> to add later, because by then something is depending on the unbounded case.

<br>

## Lesson 3 measured correctly and concluded wrongly

Lesson 3 tested the overlap threshold and rejected it. Three right answers thrown away to suppress one wrong one, a 3 for 1 loss, and the recommendation was not to build the gate.

Every question in that measurement had an answer.

| System | 15 answerable | 10 unanswerable | Both sets |
| --- | --- | --- | --- |
| Answer whatever wins | **12 of 15** | 0 of 10 | 12 of 25 |
| Only if overlap is 3 or more | 9 of 15 | **8 of 10** | **17 of 25** |

The threshold costs three answers and buys eight refusals. It was never a 3 for 1 loss, it was a 3 for 8 gain, and lesson 3 could not see the second number because the second number does not exist in `tasks.tsv`.

> [!WARNING]
> **A test set made only of answerable questions cannot measure the ability
> to decline, and silently punishes it.**
>
> Every refusal is scored as a failure, every confident guess at an
> unanswerable question is scored as nothing at all, and the system that
> always answers wins. This is not a subtle effect: it moved the conclusion
> of a lesson from *do not build this* to *build this*.
>
> Almost every benchmark has this shape, because questions are usually
> written by reading the documents. If you are building something that ought
> to be able to say it does not know, you have to write the unanswerable
> questions yourself, and nobody will give you credit for the score.

<br>

## Check yourself

```
python tools/run_lessons.py phases/06-tools-and-agents/04-a-loop-that-can-stop
```

The check verifies both findings directly: that the loop scores exactly what the plain threshold scores, and that no rewrite anywhere raises the best overlap.

<br>

## Going further

Optional, and there is no check for it.

Two of the ten unanswerable questions get answered rather than declined. Find them (they score an overlap of 3) and read what comes back. Then write ten more unanswerable questions and measure again, and notice your second ten are harder for the system than your first ten were, because you now know what it uses to decide.

That is the ordinary experience of building an evaluation set: it gets more adversarial as you learn the system, which makes the numbers from different weeks incomparable. Date your question files and never edit one after you have reported a score from it.

<br>

## What you learned

- An agent is a loop that calls a tool, reads the result, and can stop three ways: answered, out of moves, out of budget.
- A retry is only worth building if the second attempt knows something the first did not, and here it provably did not: removing words cannot raise an overlap score.
- The retry loop doubled the number of searches and changed no answer at any cap.
- The rewrite genuinely helps on a question the loop never reaches, because it fires on low scores and is needed for high wrong ones.
- A cap does not have to change an answer to be necessary; it decides who controls the cost of a question.
- The ability to decline can only be measured on questions that have no answer, and adding ten of them reversed lesson 3's conclusion from 12 of 25 to 17 of 25.
- Benchmarks made by reading the documents contain no unanswerable questions, so they score honesty as failure.

**Next:** [5. Measuring an agent](../05-measuring-an-agent/), where the score stops being one number.
