# 5. The thing you ship

> **Eight phases, and what you hand over is not a model and not a score.**
>
> It is thirteen lines of numbers, each one traceable to the lesson that
> measured it, and four of them say the system cannot be shown to work.

**You will:** assemble everything the course built, produce the page you would actually give somebody, and write down what the numbers do not establish.

**You need:** [lesson 4](../04-what-it-must-not-say/), and everything before it.

<br>

## The system, finally

```python
def ask(question):
    picked = route(question)

    if picked != "search":
        found = {"calculate": calculate, "count": count}[picked](question)

        if found is not REFUSED:
            return found, None, 0

    words = set(question.split())
    hits = Counter()

    for word in words:
        holding = postings.get(word, ())
        cost += len(holding)

        for index in holding:
            hits[index] += 1

    overlap = max(hits.values()) if hits else 0

    if overlap < BAR:
        return REFUSED, overlap, cost

    ...
```

Every line of it came from a measurement:

| Part | Why it is there |
| --- | --- |
| `route` | Phase 6 lesson 2. Something has to choose the tool. |
| Tools that return `REFUSED` | Phase 6 lesson 3. A misroute that crashes beats one that answers. |
| `postings` rather than a scan | Phase 8 lesson 2. Identical answers, an eighth of the work. |
| `overlap < BAR` | Phase 6 lesson 4. Ten of the questions have no answer. |
| A corpus that excludes `private.txt` | Phase 8 lesson 4. The index is the only real control. |
| `cost` returned on every call | Phase 8 lesson 1. Nobody counts it later. |
| No retry loop | Phase 6 lesson 4. It cost 2.15 times the work and changed no answer. |

<br>

## Your turn

Assemble it, measure everything, and write `.work/release.tsv`:

```
property                         value                       measured in
handled correctly                40 of 48                    phase 6 lesson 5
true rate, 95 percent confident  69.8% to 92.5%              phase 7 lesson 1
false statements                 4                           phase 6 lesson 5
floor: decline everything        10 of 48                    phase 7 lesson 3
...
```

Every value is computed by the file. None of them is typed in.

<br>

## What the solution prints

<!-- output: solve.py -->
```text
What this system is, on one page.

  questions asked                  48                               phase 6, phase 7
  handled correctly                40 of 48                         phase 6 lesson 5
  true rate, 95 percent confident  69.8% to 92.5%                   phase 7 lesson 1
  false statements                 4                                phase 6 lesson 5
  questions declined               12                               phase 6 lesson 4
  private sentences returned       0                                phase 8 lesson 4
  floor: decline everything        10 of 48                         phase 7 lesson 3
  floor: tools only, no search     33 of 48                         phase 7 lesson 3
  dearest question                 220 comparisons                  phase 8 lesson 1
  median question                  44 comparisons                   phase 8 lesson 1
  whole run                        4051 comparisons                 phase 8 lesson 2
  healthy signal                   13 of 25 searches clear it       phase 8 lesson 3
  if the corpus is lost            33 of 48 survive                 phase 8 lesson 3

What the numbers above do not establish:

  The interval is 23% wide, so the true rate could be 70% or 93%.
  Reaching plus or minus 5 points needs about 250 questions rather than 48.
  Removing the whole search half leaves 33 of 48, and phase 7 could not
  distinguish that from the full system, so the retrieval half is unproven.
  The threshold of 3 was chosen on these questions. On twenty written later it
  was still the best value, and it scored 18 points lower.

What it must not be asked to do:

  Answer from a corpus it has not indexed, which is the only control on
  what it can say. 8 sentences are excluded and 0 were returned.
  Serve users with different permissions from this one index.
  Be trusted when the healthy signal falls, because accuracy will not move.
```
<!-- end output -->

<br>

## The three sections, and why the last two are the hard ones

**What it is.** Thirteen numbers. Not one of them is accuracy alone. Cost is there because somebody pays it, the two floors are there because 40 of 48 means nothing without them, and the healthy signal is there because it is the only number that notices an outage.

**What it does not establish.** Four sentences, all of them measured. This section is what almost no report contains, and writing it is what stops you being asked a question in six months you cannot answer.

**What it must not be asked to do.** The boundary, stated where somebody integrating it will read it. Not in a code comment, not in a ticket.

> [!IMPORTANT]
> The second section is the one that makes the first one trustworthy.
>
> A page of numbers with no limits section reads as a claim of completeness,
> and the reader has no way to know which numbers are solid. Here, *handled
> correctly, 40 of 48* and *private sentences returned, 0* are both on the
> sheet, and they are not the same kind of fact: the first has a 23 point
> interval around it and the second is a property of the code.
>
> Saying which is which costs four lines and is the difference between a
> measurement and a sales sheet.

<br>

## Read the two floors again

```
handled correctly              40 of 48
floor: decline everything      10 of 48
floor: tools only, no search   33 of 48
```

The system beats an empty function by thirty questions, which is real and significant by anything in phase 7.

It beats **deleting its entire retrieval half** by seven, which phase 7 lesson 3 could not distinguish from chance. Five phases of work on search, and the honest sheet says *unproven on this test set*.

That is not a reason to delete it. It is a reason that the next piece of work is forty more search questions rather than a better ranker, and the sheet is what makes that obvious to somebody who did not build it.

<br>

## Check yourself

```
python tools/run_lessons.py phases/08-shipping-cost-latency-failure-safety/05-the-thing-you-ship
```

The last check in the course verifies that the indexed system agrees with a plain scan on every question, that no private sentence is reachable, that the system beats the floor, and that every line of the sheet says where it came from.

<br>

## Going further

Optional, and there is no check for it.

Write the sheet for something you have actually built. You will find two or three lines you cannot fill in, and those are the measurements worth making this week.

Then put the sheet in the repository next to the code and regenerate it in CI, the way phase 7 lesson 5 regenerates its expectations. A page of numbers in a document is out of date within a month. A page of numbers that a program produces on every commit is the only kind that stays true.

<br>

## What you learned

- What you ship is a page of numbers with sources, not a score.
- Cost, the floors, and a signal that detects outages belong on it alongside accuracy.
- A limits section makes the rest trustworthy, because it says which numbers are solid and which have twenty-three points of uncertainty around them.
- The boundary of what a system must not be asked to do belongs where an integrator will read it.
- This system beats an empty function by thirty questions and its own ablation by seven, and only the first of those is established.
- Every part of the final system exists because something was measured, and the retry loop is absent for the same reason.
- A sheet a program regenerates stays true; a sheet in a document does not.

<br>

## Phase 8 complete

```
python tools/run_lessons.py phases/08-shipping-cost-latency-failure-safety
```

You counted the work and found an average no question costs, replaced a scan with an index that did identical work for an eighth of the price, watched the next obvious optimisation break a threshold two phases away, took the system apart while it ran and found the catastrophic failure invisible to every alarm, put a secret in the corpus and watched a question about budgets return an API key, and then wrote the page that says all of it out loud.

<br>

## The course is finished

```
python tools/run_lessons.py
python tools/progress.py
```

Forty-five lessons, nine phases, one system. No dependency was installed, no key was needed, nothing was downloaded, and every number in every lesson was produced by code that runs on your machine.

The thing worth keeping is not the agent. It is the habit the whole course was arranged to build: **when you cannot say how you would measure it, you do not know it yet.** That sentence is why the retry loop is not in the final system, why the word vector classifier was reported as a failure, why the threshold has an interval next to it, and why the sheet above has a section saying what it does not establish.

Everything else in this field will be replaced. That will not be.
