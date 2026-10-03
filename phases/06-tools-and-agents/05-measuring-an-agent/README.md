# 5. Measuring an agent

> **You now have an agent. Someone asks whether it is any good.**
>
> There are two versions of it. One gets more questions right. The other
> handles more questions correctly. Both statements are true at the same
> time, and choosing between them is not something a measurement can do for
> you.

**You will:** assemble the whole phase into one system, score three versions of it on six numbers instead of one, and work out the exact price at which the ranking flips.

**You need:** [lesson 4](../04-a-loop-that-can-stop/).

<br>

## The phase, assembled

```python
def agent(question):
    calls = 0
    picked = route(question)

    if picked != "search":
        calls += 1
        found = {"calculate": calculate, "count": count}[picked](question)

        if found is not REFUSED:
            return found, calls

    asked = question

    for _ in range(CAP if retry else 1):
        calls += 1
        found = search(asked)

        if found is not REFUSED:
            return found, calls

        asked = shorten(asked)

        if not asked:
            break

    return REFUSED, calls
```

A rule that picks a tool (lesson 2), tools that refuse work they cannot do (lesson 3), a search that declines rather than guessing, a bounded loop, and a count of what it all cost.

It runs against **48 questions**: the 38 from `tasks.tsv` that have answers, and the 10 from `impossible.tsv` that do not.

<br>

## Four outcomes, not two

Every question ends in exactly one of four states, and this is the part a single accuracy figure throws away:

| Outcome | What it means |
| --- | --- |
| **right** | Answered, correctly |
| **wrong** | Answered confidently, incorrectly |
| **held back** | Declined a question that did have an answer |
| **declined** | Declined a question that had none, which is the correct behaviour |

Two of those four are failures, and they are not remotely the same failure. A **held back** costs a user one trip to the documentation. A **wrong** puts a false statement into whatever reads the output next.

<br>

## Your turn

Score all three versions over all 48 questions and write `.work/scorecard.tsv`:

```
system                        right  wrong  held back  declined  behaved correctly  calls
answer whatever wins          35     13     0          0         35                 48
decline below overlap 3       32     4      4          8         40                 48
decline, then retry, cap 6    32     4      4          8         40                 103
```

Count every call the agent makes, including ones that were refused. A question with no answer that gets answered anyway is **wrong**.

<br>

## What the solution prints

<!-- output: solve.py -->
```text
The same agent, three ways, over all 48 questions.

  system                          right  wrong  held  decl  correct  calls
  answer whatever wins               35     13     0     0       35     48
  decline below overlap 3            32      4     4     8       40     48
  decline, then retry, cap 6         32      4     4     8       40    103

  right     answered correctly
  wrong     answered confidently and incorrectly
  held      declined a question that did have an answer
  decl      declined a question that had none, which is correct

Which of the first two is better depends on what you report:
  questions it got right          35 against 32, the first one wins
  questions it handled correctly  35 against 40, the second one wins
  confident wrong answers         13 against 4, the second one wins
  tool calls                      48 against 48, no difference

Score a right answer as 1 and a wrong answer as minus k, and declining as 0:
  the first scores  35 - 13k
  the second scores 32 - 4k
  they are equal at k = 1/3

  a wrong answer costs 0    of a right one:   35.00 against  32.00, the first
  a wrong answer costs 1/4  of a right one:   31.75 against  31.00, the first
  a wrong answer costs 1/3  of a right one:   30.67 against  30.67, a tie
  a wrong answer costs 1    of a right one:   22.00 against  28.00, the second
  a wrong answer costs 3    of a right one:   -4.00 against  20.00, the second

The third is the second with a retry bolted on. Identical on all four outcomes,
and 103 calls against 48. Only the cost column can see it.
```
<!-- end output -->

<br>

## The first two cannot be ranked

| What you report | Answer whatever wins | Decline below 3 | Winner |
| --- | --- | --- | --- |
| Right answers | **35** | 32 | The first |
| Handled correctly, all 48 | 35 | **40** | The second |
| Confident wrong answers | 13 | **4** | The second |
| Tool calls | 48 | 48 | Neither |

Every row is a measurement, every measurement is correct, and they do not agree. There is no further experiment that settles it, because the disagreement is not about what the systems do. It is about what the failures are worth.

<br>

## So price the failures

Score a right answer as 1, a decline as 0, and a wrong answer as minus **k**:

```
the first scores  35 - 13k
the second scores 32 - 4k
```

The first buys 3 extra right answers with 9 extra wrong ones. They are equal at **k = 1/3**.

So the whole comparison reduces to one question: **is a confident wrong answer more or less costly than a third of a right answer is valuable?** Above that line the cautious version wins, below it the confident one does.

> [!IMPORTANT]
> `k` is not in your data and no amount of measurement will produce it. It
> comes from what happens downstream of a wrong answer.
>
> A search box where a person reads the result and shrugs has a small `k`.
> The same search wired into something that files a ticket, emails a
> customer, or is read as fact by the next model in a chain has a large one.
> The identical model and the identical corpus give opposite answers in the
> two settings.
>
> Write your `k` down before you compare systems, and you will find the
> comparison mostly settles itself. Refuse to write it down and you will pick
> whichever system won on whichever number you happened to report.

<br>

## And the third one is invisible without cost

The retrying version is **identical on all four outcome columns** and makes **103 calls against 48**.

Report accuracy and the two are the same system. Report accuracy and cost and one of them is twice the price for nothing. This is the state a great many deployed systems are actually in, because the retry was added as a safeguard, the accuracy did not move, and nobody was counting calls.

> [!TIP]
> Put cost on the scorecard from the first measurement, not after the bill
> arrives. It is the cheapest column to collect (a counter) and the only one
> that catches work which changes no output.
>
> Latency belongs there for the same reason and behaves the same way: the
> retry made the slow questions six times slower and the accuracy identical.

<br>

## What a scorecard is for

Six numbers is not thoroughness for its own sake. Each column answers a question somebody will actually ask:

- **right**: does it work
- **wrong**: how often does it state something false
- **held back**: how often does it give up on something it could have done
- **declined**: can it admit it does not know
- **behaved correctly**: the honest single figure, if you must have one
- **calls**: what does it cost

A system that improves on one of these at the expense of another has not improved. It has moved, and the direction is a decision rather than a result.

<br>

## Check yourself

```
python tools/run_lessons.py phases/06-tools-and-agents/05-measuring-an-agent
```

The check verifies the four outcomes add up to 48 for every system, so nothing can be counted twice or quietly dropped, and that the retrying version differs from the plain one on cost alone.

<br>

## Going further

Optional, and there is no check for it.

Pick the `k` for something you have built and work out which of these two systems your own project would want. Then look at what your project actually reports, and whether that number would have chosen it.

Then try a bar of 2 and a bar of 4 and add them to the scorecard. The bar is a dial between the two columns, `held back` and `wrong`, and there is no setting that reduces both. Every threshold in every system you build is this dial, and the only question is whether somebody chose the setting deliberately.

<br>

## What you learned

- Every question an agent sees ends as right, wrong, held back, or declined, and one accuracy figure merges four different outcomes into two.
- Two versions of the same agent can each win on a correct measurement, at the same time.
- Pricing a wrong answer against a right one collapses the whole comparison to a single number, which for these two systems is 1/3.
- That number is a fact about your setting, not your data, and no experiment produces it.
- Cost catches changes that no accuracy column can see: 103 calls against 48, for identical answers.
- A threshold is a dial between declining too much and being wrong too often, and it has no setting that improves both.

<br>

## Phase 6 complete

```
python tools/run_lessons.py phases/06-tools-and-agents
```

You showed a model cannot produce a digit it has never seen and closed the gap with three small programs, took away the human who chose which program to use and measured the rule that replaced them, gave the tools the power to refuse and found it rescued one failure in five, built a loop that could stop and proved its retry could never have worked, and finished by finding that the two best versions of the result cannot be ranked without a business decision.

The thread through all five is that **the interesting number is almost never the one being reported.** 29 of 30 hid a human doing the hard part. 38 of 38 hid a rule fitted to the questions. 12 of 15 hid ten questions that had no answer. And 35 against 32 hid nine extra false statements.

**Next:** [Phase 7](../../07-measuring-whether-any-of-it-works/), where measurement stops being a step at the end and becomes the thing you build first.
