# 2. Is the difference real?

> **Phase 6 ended with 35 against 40 and called the choice a business
> decision. Lesson 1 said a score that size on 48 questions carries about
> twenty points of uncertainty.**
>
> Neither of those is the sharpest question available, because both agents
> answered *the same 48 questions*, and that changes what you are allowed to
> ask.

**You will:** compare the two agents question by question instead of total by total, find they disagree about eleven times, and watch the conclusion reverse depending on which outcome you count.

**You need:** [lesson 1](../01-the-number-has-error-bars/).

<br>

## Stop comparing totals

The two agents differ in one place: whether search answers below an overlap of 3. On the 23 arithmetic and counting questions they are the same code and produce the same output.

So comparing 35 against 40 drags 37 questions into the comparison that cannot possibly distinguish the two systems. They are pure noise in the totals, and lesson 1's intervals paid for them in width.

Throw them out and look only at where the two disagree:

```
they agree on 37 of 48 questions and disagree on 11
 3 only the confident one,  8 only the cautious one
```

**Eleven questions carry the entire difference.** That is the comparison.

<br>

## The test is a coin

If the two agents were equally good, every disagreement would be a coin flip: no reason for it to fall one way rather than the other. So ask how often eleven coin flips come out 3 and 8 or worse, in either direction.

```python
def coin_flip_chance(wins, losses):
    total = wins + losses
    fewer = min(wins, losses)

    return min(1.0, 2 * sum(comb(total, i)
                            for i in range(0, fewer + 1)) / 2 ** total)
```

**22.7%.** About one time in four. Nothing to report.

> [!NOTE]
> This is McNemar's test, and doing it on the exact binomial rather than the
> chi squared approximation is the right choice at these sizes. Worth knowing
> the name, because it is the correct test whenever two systems are run over
> the same examples, which is nearly always, and it is much more powerful
> than comparing two intervals.
>
> Lesson 1's intervals for these two agents were 78.6% to 98.3% and 68.7% to
> 94.0%. Overlapping, and the overlap told you nothing, because each interval
> was answering a question about one agent alone.

<br>

## Your turn

Run both agents over all 48 questions, count the disagreements under two different outcomes, and write `.work/disagreements.tsv`:

```
outcome                confident  cautious  only confident  only cautious  chance
behaved correctly      35         40        3               8              0.2266
said something false   13         4         9               0              0.0039
```

A question is a disagreement only when one agent has the outcome and the other does not.

<br>

## What the solution prints

<!-- output: solve.py -->
```text
Two agents, the same 48 questions, two outcomes worth counting.

  behaved correctly
    confident 35, cautious 40
    they agree on 37 of 48 questions and disagree on 11
     3 only the confident one,  8 only the cautious one
    if those were coin flips, this lopsided or worse 22.7% of the time
      only confident: 'why did the server restart'
      only confident: 'how long did the rollback take'
      only confident: 'where does the documentation live'
      only cautious:  'who is on call this weekend'
      only cautious:  'what is the database password'
      only cautious:  'how much revenue did the outage cost'

  said something false
    confident 13, cautious  4
    they agree on 39 of 48 questions and disagree on 9
     9 only the confident one,  0 only the cautious one
    if those were coin flips, this lopsided or worse 0.4% of the time
      only confident: 'what is the vault for'
      only confident: 'who is on call this weekend'
      only confident: 'what is the database password'

The gap in behaved correctly is 5 questions and could easily be chance.
The gap in said something false is 9 questions and could not.

Both gaps come from one behaviour: answering a question the evidence was weak for.
It won the confident agent 3 questions and cost it 9 false statements,
and the cautious agent never once answered something the confident one declined.
```
<!-- end output -->

<br>

## The same two runs, two opposite answers

| Outcome counted | Confident | Cautious | Split | Chance |
| --- | --- | --- | --- | --- |
| Behaved correctly | 35 | 40 | 3 against 8 | **22.7%** |
| Said something false | 13 | 4 | 9 against 0 | **0.4%** |

Nothing was rerun. No parameter changed. These are the same two programs over the same 48 questions, and the only thing that moved is which outcome was counted.

Counting correct behaviour, the cautious agent is ahead by five and that is unremarkable. Counting false statements, it is ahead by nine, split nine to nothing, and coin flips produce that about once in 250 attempts.

> [!IMPORTANT]
> 22.7% does **not** mean the two agents are equally good at answering
> questions. It means 48 questions were not enough to tell, which is the same
> sentence lesson 1 kept writing.
>
> "No significant difference" and "no difference" are different claims, and
> only one of them was measured. The honest report is that the accuracy gap
> is unresolved at this sample size and the false statement gap is
> established.

<br>

## Which settles phase 6's question

Phase 6 worked out that the two agents are equal when a wrong answer costs a third of what a right answer is worth, and said that price was a decision rather than a measurement. It still is. But the two quantities being traded are not the same kind of thing:

- The **3 extra right answers** are inside the noise. Rerun this on a different 48 questions and the sign could flip.
- The **9 extra false statements** are not. Rerun it and they will still be there.

So the trade is not three against nine. It is a difference you cannot measure against one you can, and that is a much easier decision than the one phase 6 left open.

Both numbers come from a single behaviour: answering when the evidence is weak. That behaviour won the confident agent 3 questions and cost it 9 false statements, and the cautious agent never once answered something the confident one had declined.

<br>

## Two outcomes is two chances to find something

This lesson tested two outcomes and reported the one that came out significant. Done carelessly, that is how a result gets manufactured: test enough outcomes and one of them lands under 5% by chance alone.

Two things keep this honest, and they are both worth copying:

- **Both outcomes were chosen in phase 6**, before this test existed. They are the two columns that phase's scorecard already reported, not outcomes hunted for afterwards.
- **The result survives the correction anyway.** The crudest fix is to multiply by the number of tests: 0.4% becomes 0.8%, still comfortably under 5%. The other becomes 45%.

> [!CAUTION]
> If you test ten outcomes, one of them lands under 5% by chance about
> forty percent of the time. There is no skill in finding it, and no
> information in it.
>
> Write down what you are going to count before you run the comparison. If
> you find something interesting afterwards, that is a reason to go and
> collect fresh data, not a reason to report it.

<br>

## Check yourself

```
python tools/run_lessons.py phases/07-measuring-whether-any-of-it-works/02-is-the-difference-real
```

The check insists the agreements and disagreements add up to 48 for each outcome, so no question is counted twice or silently dropped.

<br>

## Going further

Optional, and there is no check for it.

Work out how lopsided eleven disagreements would have to be. Zero against eleven gives 0.1%, one against ten gives 1.2%, two against nine gives 6.5%. So with eleven disagreements, the cautious agent had to win at least ten of them to clear the usual bar, and it won eight.

Then count the questions where the two agents agreed: 37 of 48. That number is the real limit on this comparison. To resolve a small difference you do not need more questions, you need more questions **the two systems handle differently**, which is why the useful test set for comparing two systems looks nothing like the useful test set for measuring one.

<br>

## What you learned

- Two systems run on the same examples should be compared example by example, not total by total, because the examples they handle identically add noise and no information.
- The test is to treat the disagreements as coin flips and ask how often chance is that lopsided, which is McNemar's test.
- Eleven disagreements split 3 against 8 happens 22.7% of the time by chance, so the accuracy gap between the phase 6 agents is unresolved.
- The same two runs, counting false statements instead, split 9 against 0 and happen 0.4% of the time, so that gap is established.
- "Not significant" means the sample was too small to tell, never that the difference is absent.
- Choosing which outcome to count after seeing the results manufactures findings, so choose before, and correct for how many you tested.
- A comparison is limited by the number of examples the two systems treat differently, not by the size of the test set.

**Next:** [3. The baseline you forgot](../03-the-baseline-you-forgot/), where a system with no model in it at all turns out to be the one to beat.
