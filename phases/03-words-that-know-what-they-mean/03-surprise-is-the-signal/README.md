# 3. Surprise is the signal

> **Last lesson ended with a question rather than a failure.**
>
> *server* sits near *the* eight times and near *memory* twice. Which of those
> two facts tells you something? The one that should not have happened.

**You will:** replace every count with how surprising it is, and watch meaning appear out of the same numbers.

**You need:** [lesson 2](../02-the-company-a-word-keeps/).

<br>

## The one idea

Ask what chance would predict. If *server* takes up 0.3% of all the word slots and *the* takes up 6% of all the context slots, then by chance alone they should land near each other 0.018% of the time. Multiply by how many pairs there are and you get the number to expect.

Now divide what actually happened by that.

- **Above 1**: they appear together more than chance. That is information.
- **Around 1**: exactly what chance predicts. That is nothing.
- **Below 1**: they avoid each other.

```python
expected = (word_total[word] * context_total[near]) / grand
value = log(count / expected)
```

The logarithm turns "twice as surprising" into one step rather than double, which keeps a handful of extreme pairs from dominating everything.

Then throw away anything below zero. "These two appear together less than chance" is mostly noise in a corpus this size, and keeping it stuffs every profile with words that simply never showed up.

> [!NOTE]
> This is **pointwise mutual information**, and keeping only the positive part
> makes it PPMI. It was the standard way to build word vectors before neural
> methods, and it is still a sensible baseline. Nothing in it is learned and
> nothing is trained: it is counting, divided by chance.

<br>

## Nothing else changes

Same corpus. Same window of four. Same cosine. The only difference is what number sits in each cell of the profile.

<br>

## Your turn

Build the weighted profiles and find the neighbours again. Write `.work/neighbours.tsv`, same shape as last time.

<br>

## What the solution prints

<!-- output: solve.py -->
```text
What sits near 'server', now ranked by surprise rather than count:
  restarting   4.44   (seen together 1 time)
  cleanly      3.88   (seen together 1 time)
  cleared      3.88   (seen together 1 time)
  doubled      3.88   (seen together 1 time)
  percent      3.88   (seen together 1 time)
  cpu          3.74   (seen together 1 time)
  left         3.74   (seen together 1 time)
  during       3.34   (seen together 1 time)

Nearest neighbours:

  server     memory 0.34, an 0.17, no 0.16, load 0.16, incident 0.16
  deploy     failed 0.30, version 0.22, staging 0.19, before 0.18, run 0.15
  customer   issue 0.25, account 0.21, the 0.18, was 0.17, ticket 0.15
  test       that 0.30, bug 0.27, passed 0.25, suite 0.24, a 0.23
  meeting    document 0.32, runs 0.27, agenda 0.25, at 0.19, the 0.19
  incident   an 0.37, postmortem 0.19, monitoring 0.19, is 0.18, first 0.17

Words appearing in at least three of those 6 lists: none
```
<!-- end output -->

<br>

## It works

| Word | Nearest, by surprise |
| --- | --- |
| `server` | **memory**, load, incident |
| `deploy` | **failed**, version, staging |
| `customer` | **issue**, account, ticket |
| `test` | bug, passed, **suite** |
| `meeting` | document, runs, **agenda** |
| `incident` | **postmortem**, monitoring |

Nobody told the program that servers have memory, that deploys go to staging, or that incidents produce postmortems. It counted words in 217 sentences and divided by chance.

And the measurement from last lesson, repeated: **and** and **was** appeared in three of five neighbour lists before. Now no word appears in three of six. The filler is gone from the top of the lists.

> [!IMPORTANT]
> Words that were never adjacent are now close. *server* and *incident* are
> neighbours because they keep the same company, not because they co-occur.
> That is the property phase 1 and 2 needed and could not have: evidence about
> one word now says something about another.

<br>

## Where it strains, and why that is worth seeing

Look at the top of the first table. The most surprising company for *server* is *restarting*, seen together **once**. Then *cleanly*, *cleared*, *doubled*, all once.

This is PPMI's known weakness. A pair seen once, where both words are rare, looks enormously surprising, because chance predicted almost zero and one is infinitely more than almost zero. Rare accidents get the loudest voice.

The usual fixes are to discount rare pairs, or to compress the profiles so that one noisy dimension cannot carry much weight. That compression is the next lesson.

Some filler also survives lower down: *an* under `incident`, *that* under `test`. With 2,019 words of corpus, some of it is luck. A larger corpus mostly cures this, which is the honest answer rather than a cleverer formula.

<br>

## Check yourself

```
python tools/run_lessons.py phases/03-words-that-know-what-they-mean/03-surprise-is-the-signal
```

<br>

## Going further

Optional, and there is no check for it.

Keep the negative values instead of discarding them, and look at the neighbours. Every profile fills up with thousands of words that were merely absent, all of them mildly negative, and they swamp the handful of words that were actually present. Throwing away half the information makes the result better, which is a strange and useful thing to have seen once.

<br>

## What you learned

- What matters is not how often two words co-occur, but how much more often than chance.
- Dividing by expected, taking the log, and keeping the positive part is PPMI.
- The same corpus, window and cosine produce meaning once the weighting is right.
- Words never seen together can still come out close, which is exactly what was needed.
- PPMI over-rewards rare pairs seen once, and that is a real limitation, not a bug.
- Discarding the negative half improves the result.

**Next:** [4. Fewer numbers that say more](../04-fewer-numbers-that-say-more/), where profiles of six hundred numbers become a handful, and the noise gets left behind.
