# 3. When something fails

> **Delete the corpus. The whole thing. Every sentence the system has ever
> been able to retrieve.**
>
> Accuracy falls from 40 of 48 to 33 of 48, and false statements fall from
> four to zero. On the two numbers anybody watches, a total outage looks like
> a slightly quiet day with an improvement in honesty.

**You will:** take pieces out of the running agent, measure what each costs, and find that the catastrophic failure is the one no ordinary alarm can see.

**You need:** [lesson 2](../02-when-the-corpus-grows/).

<br>

## Seven ways to be broken

A tool that is down does not explode. It refuses, the same way phase 6 taught it to refuse work it could not do, and the question falls through to search:

```python
def unavailable(question):
    """A tool that is down. It refuses, which is the polite way to fail."""
    return REFUSED
```

And a corpus does not vanish cleanly either. It comes back half loaded because one shard timed out, or a tenth loaded because the job was killed, or empty because the path was wrong in the new deployment.

<br>

## Your turn

Run all seven and write `.work/failures.tsv`:

```
failure                 correct  wrong  declined  cleared the bar
everything works        40       4      12        13
calculate unavailable   29       4      23        13
count unavailable       28       5      23        14
both tools unavailable  17       5      34        14
half the corpus loaded  36       4      16        9
a tenth of the corpus   34       0      24        1
no corpus at all        33       0      25        0
```

<br>

## What the solution prints

<!-- output: solve.py -->
```text
The agent with pieces taken away, over the same 48 questions.

  failure                   correct   said false   declined   mean overlap
  everything works          40 of 48            4         12           2.60
  calculate unavailable     29 of 48            4         23           2.42
  count unavailable         28 of 48            5         23           2.43
  both tools unavailable    17 of 48            5         34           2.33
  half the corpus loaded    36 of 48            4         16           2.28
  a tenth of the corpus     34 of 48            0         24           1.56
  no corpus at all          33 of 48            0         25           0.00

Losing the corpus entirely takes 40 correct to 33, a fall of 7.
It also takes false statements from 4 to 0.

  a monitor watching accuracy     sees 15%, which is a quiet Tuesday
  a monitor watching wrong answers sees an improvement
  the declined count             goes 12 to 25
  the mean overlap               goes 2.60 to 0.00

What the scores look like as the corpus disappears:
  everything works          mean overlap 2.60, 13 of 25 searches clear the bar
  half the corpus loaded    mean overlap 2.28,  9 of 25 searches clear the bar
  a tenth of the corpus     mean overlap 1.56,  1 of 25 searches clear the bar
  no corpus at all          mean overlap 0.00,  0 of 25 searches clear the bar

That last column is the only one that noticed.
```
<!-- end output -->

<br>

## The tool failures are fine, by accident

Losing `calculate` costs eleven questions. Losing `count` costs twelve. Losing both costs twenty-three, which is exactly the number of questions those tools answer.

**And in none of those cases do false statements go up.** The arithmetic questions fall through to search, search finds nothing that clears the threshold, and they are declined. The system loses capability and gains no dishonesty.

That is graceful degradation, and the system was not designed for it. It happens because a question like *what is 47 times 13* shares almost no words with a corpus about deployments, so the threshold catches it. Change the corpus to one about mathematics and the same fallback starts returning sentences.

> [!NOTE]
> A fallback is only safe when the thing it falls back to can tell it is
> being misused. Phase 6 lesson 3 made the same point about routing, and a
> failure turns every route into a misroute at once.
>
> If you have a fallback path, ask what it does with input it was never meant
> to see. Here the answer is good, and nobody arranged for it.

<br>

## The corpus failure is the one to worry about

| | Correct | Said false | Declined | Mean overlap |
| --- | --- | --- | --- | --- |
| Everything works | 40 of 48 | 4 | 12 | 2.60 |
| No corpus at all | **33 of 48** | **0** | 25 | **0.00** |

Seven questions. That is what total destruction of the retrieval half costs, and the reason is arithmetic rather than luck: 23 questions are answered by tools that still work, and 10 of the questions have no answer anyway, so declining them is now **correct**.

The system is failing completely and being rewarded for it, because refusing everything is the right response to ten of the forty-eight.

> [!CAUTION]
> Work through what each alarm sees.
>
> **Accuracy** drops 15%, which is inside the normal week and well inside the
> error bar phase 7 put on it.
>
> **False statements** go from four to zero, which reads as an improvement,
> and if anybody had shipped a change that week they would take the credit.
>
> **Latency** improves, because there is nothing to search.
>
> **Errors** are zero. Nothing raised. Every request returned successfully.
>
> There is no alarm on that list that fires. The outage is invisible to
> everything except somebody reading the answers.

<br>

## What does notice

The last column. **Searches clearing the threshold: 13, then 9, then 1, then 0.** The mean top overlap: 2.60, 2.28, 1.56, 0.00.

Those numbers say nothing about whether the system is right. They are a property of the inputs and the index, and that is exactly why they work: they are measurable on every request, in production, with no labels and no ground truth.

> [!IMPORTANT]
> Monitor the distribution of your scores, not just the outcomes.
>
> Correctness needs labels and arrives late. A retrieval score, a confidence,
> a match count, a tool selection rate, the share of requests that end in a
> refusal: all of those are free on every request and all of them move
> immediately when a component breaks.
>
> The alert that catches a corpus outage is "the share of searches clearing
> the threshold fell below half its usual value", and it would have fired on
> the half loaded corpus too, which is the case nobody would otherwise
> notice for a week.

<br>

## And the guard that hid it

There is a line in the search that makes all of this possible:

```python
if not documents:
    return REFUSED, 0
```

Without it, the next line does `ranked[0]` on an empty list and raises `IndexError`. That is what phase 6's search does today, and it is the **loud** failure: the deployment goes red, somebody is paged, and the wrong path in the config is found in ten minutes.

Adding the guard is the obvious defensive move, and it converts a total outage from an exception into a system that returns 200 and declines everything.

> [!WARNING]
> Error handling that hides a failure has not handled it. A component which
> cannot do its job and says so is far more useful than one which degrades
> quietly into a plausible shape.
>
> The rule worth carrying: handle the failures you can do something about,
> and let the rest crash. An empty corpus is not a condition the search can
> recover from, so catching it only delays the discovery.

<br>

## Check yourself

```
python tools/run_lessons.py phases/08-shipping-cost-latency-failure-safety/03-when-something-fails
```

The check insists that a total outage costs few questions and removes every false statement, because that is the finding and it should fail loudly if somebody makes the system honest enough to hide it less well.

<br>

## Going further

Optional, and there is no check for it.

Take the guard out and run the empty corpus case again. The lesson stops working and the system crashes, which is the better outcome.

Then write the alert. It is one line: the share of searches clearing the threshold, compared against the same figure from last week. Decide what fraction of a drop should page somebody, then check that number against the half loaded row, which is the case you actually want to catch.

<br>

## What you learned

- A tool that fails by refusing degrades safely here, because the fallback receives input it cannot match and declines it.
- That safety was not designed, and a corpus on a related subject would remove it.
- Losing the entire corpus costs 7 of 48 questions, because tools answer 23 and declining the 10 unanswerable ones is correct.
- The same outage takes false statements from four to zero, so honesty metrics read as improved.
- Accuracy, error rate and latency all fail to detect a total outage, and latency improves.
- Score distributions do detect it, cost nothing to collect, need no labels, and move immediately.
- The guard that prevents a crash is what turns a page-somebody failure into an invisible one.

**Next:** [4. What it must not say](../04-what-it-must-not-say/), where a secret is put in the corpus and search hands it to anybody who asks.
