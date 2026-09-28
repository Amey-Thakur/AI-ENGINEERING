# 3. The baseline you forgot

> **The finished agent handles 40 of 48 questions correctly.**
>
> A function whose entire body is `return None` handles 10 of them correctly
> and has never said anything untrue in its life.

**You will:** build the systems nobody builds, measure them against the agent five phases went into, and find that most of that agent cannot be shown to be doing anything.

**You need:** [lesson 2](../02-is-the-difference-real/).

<br>

## Three systems that barely exist

```python
def always_decline(_):
    return REFUSED


def the_first_sentence(_):
    return sentences[0]


def always_search(question):
    return best(question)[1]
```

None of them looks at the question except the last, and that one has no routing, no tools and no threshold.

And a fourth, which is a different kind of baseline: the finished agent with **the entire search half deleted**. It answers arithmetic and counting, and declines everything else.

```python
def tools_only(question):
    picked = route(question)

    if picked == "search":
        return REFUSED

    return {"calculate": calculate, "count": count}[picked](question)
```

> [!NOTE]
> The first three are **baselines**: floors that any system has to clear
> before its score means anything. The fourth is an **ablation**: the real
> system with one part removed, which answers a different and usually more
> uncomfortable question, namely whether that part is carrying its weight.
>
> Report both. A system that beats the floor has justified existing. Only the
> ablation says which half of it did the work.

<br>

## Your turn

Run all six systems over all 48 questions and write `.work/baselines.tsv`:

```
system                              correct  false  asked
always decline                      10       0      48
always return the first sentence    0        48     48
always search, no routing           12       36     48
the tools only, decline the rest    33       0      48
the confident agent                 35       13     48
the cautious agent                  40       4      48
```

<br>

## What the solution prints

<!-- output: solve.py -->
```text
The phase 6 agent, and four systems that barely exist, over 48 questions.

  system                              correct   said something false
  always decline                      10 of 48    0
  always return the first sentence     0 of 48   48
  always search, no routing           12 of 48   36
  the tools only, decline the rest    33 of 48    0
  the confident agent                 35 of 48   13
  the cautious agent                  40 of 48    4

Against deleting the entire search half of the system:
  the confident agent    wins 12, loses 10, chance alone does this  83.2% of the time
  the cautious agent     wins  9, loses  2, chance alone does this   6.5% of the time

And the classifiers of phases 1 to 3, against saying 'question' every time.
The held back messages are 10 question, 10 statement, so that scores 10 of 20:

  phase 1 lesson 2, the hand written rule    18 of 20  +8    0.02%  beats a coin
  phase 1 lesson 4, the perceptron           15 of 20  +5    2.07%  beats a coin
  phase 2, the network you wrote             15 of 20  +5    2.07%  beats a coin
  phase 3, word vectors averaged             11 of 20  +1   41.19%  does not beat a coin
  phase 3, the first word and the average    13 of 20  +3   13.16%  does not beat a coin
```
<!-- end output -->

<br>

## Doing nothing scores 21%

`always_decline` handles **10 of 48**, because ten of the questions have no answer and declining is the right response to every one of them.

That is the floor. Any system reporting less than 21% on this task is worse than an empty function, and a system reporting 25% has bought four questions with however much machinery it contains.

It is also, and this matters, the only system in the table besides the ablation with **zero false statements**. It cannot be wrong. Nothing that never speaks can be.

> [!TIP]
> The floor is rarely zero and it is rarely obvious. On a balanced two class
> problem it is 50%. On a problem where 95% of the traffic is one class it is
> 95%, which is why fraud and defect models get reported at 97% accuracy by
> people who have not checked what `return False` scores.
>
> It takes an afternoon to write and it is the number your result has to be
> read against for the rest of the project.

<br>

## Deleting the search half costs seven questions

| System | Correct | Said something false |
| --- | --- | --- |
| The tools only, search deleted | 33 of 48 | **0** |
| The confident agent | 35 of 48 | 13 |
| The cautious agent | **40 of 48** | 4 |

Phases 5 and 6 built retrieval: scoring, ranking, a threshold, a fallback, a loop. Take all of it out and the system drops from 40 to 33, and stops saying anything false at all.

Now the paired comparison from lesson 2, against that stripped down version:

- **The confident agent: wins 12, loses 10, chance alone does this 83% of the time.** On this test set, a system with the whole retrieval half bolted on cannot be distinguished from one without it. It also says thirteen false things instead of none.
- **The cautious agent: wins 9, loses 2, 6.5%.** Much better, and still short of the usual bar.

> [!IMPORTANT]
> This does not establish that search is useless. It establishes that **48
> questions cannot tell**, and lesson 2 explained why: only 15 of the 48 are
> questions search can answer, so only those 15 plus the 10 unanswerable ones
> can possibly separate the two systems.
>
> The response to a result like this is not to improve the search. It is to
> go and write forty more search questions, because no improvement you make
> will be visible until the test set can see the component at all.

<br>

## The classifiers, against a coin

The held back messages in phase 1 are ten questions and ten statements, so answering the same way every time scores **10 of 20**.

| System | Score | Against the floor | A coin does this well |
| --- | --- | --- | --- |
| Hand written rule | 18 of 20 | +8 | 0.02% |
| Perceptron | 15 of 20 | +5 | 2.07% |
| The network | 15 of 20 | +5 | 2.07% |
| Word vectors averaged | 11 of 20 | **+1** | **41.19%** |
| First word and the average | 13 of 20 | +3 | 13.16% |

The rule, the perceptron and the network clear the floor by enough that chance is not a plausible explanation. **The word vector systems do not.** Eleven of twenty is one message better than a fixed answer, and a coin manages it four times out of ten.

Phase 3 already reported those two as failures, so nothing here contradicts the course. It sharpens the finding: the word vector classifier was not merely worse than the network, it was **indistinguishable from not having read the message**.

<br>

## Check yourself

```
python tools/run_lessons.py phases/07-measuring-whether-any-of-it-works/03-the-baseline-you-forgot
```

The check insists that declining everything scores exactly the number of unanswerable questions and says nothing false, because a system that never speaks cannot misspeak.

<br>

## Going further

Optional, and there is no check for it.

Add the fifth baseline: answer every question with the corpus sentence that shares the most words with **the question before it**. It is the same code as search with one index changed, it cannot possibly work, and running it tells you how much of search's 12 of 15 comes from the corpus being small enough that any sentence is nearly right.

Then delete the router instead of the search, leaving one tool that tries `calculate` and falls back to search. Measuring the halves separately is the only way to find out that a system's score is coming from a part you were not paying attention to.

<br>

## What you learned

- A score is meaningless until you know what the cheapest possible system scores on the same questions.
- Declining everything scores 10 of 48 here, and on an unbalanced problem the floor can be above 90%.
- A baseline is a floor; an ablation removes one part of the real system and asks whether that part is earning its place.
- Deleting the entire search half costs 7 questions and removes all 13 false statements, and against the confident agent that difference arises by chance 83% of the time.
- A component that cannot be distinguished from its own absence has not been shown to be useless, only to be invisible to the test set you have.
- The fix for an invisible component is more examples that exercise it, not a better component.
- Phase 3's word vector classifier beat a fixed answer by one message out of twenty, which a coin manages four times in ten.

**Next:** [4. The test set you keep looking at](../04-the-test-set-you-keep-looking-at/), where phase 6's threshold meets twenty questions written after it was fixed.
