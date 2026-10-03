# 5. When it breaks

> **The score tells you how much. Only the failures tell you what.**
>
> 75% is not a finding. It is a summary that has thrown away everything you
> could act on. The five messages behind it are the finding, and reading them
> takes about four minutes.

**You will:** read every mistake your model makes, one at a time, and find that they are not all the same mistake.

**You need:** [lesson 4](../04-tell-the-truth/).

<br>

## How sure was it

Until now the model's score was thrown away the moment it became a yes or a no. That number is worth keeping, because it says how strongly the model believed it.

A message scoring +7 was called a question emphatically. A message scoring +1 was called a question by a whisker. Both come out as "question", and they are not the same event.

So for every failure, record three things: what it really was, what the model said, and **how strongly**.

<br>

## Your turn

Train on the first 40 as before, then write `.work/errors.tsv`, one row for each held back message your model gets wrong:

```
message                      true       predicted   score
who approved this change     question   statement   0
```

The check rebuilds your model from your weights, works out which messages it really gets wrong, and compares. Your list has to be the truth about your model.

<br>

## What the solution prints

<!-- output: solve.py -->
```text
5 wrong out of 20
  questions called statements: 3
  statements called questions: 2

Each failure, with how sure it was and how much it had never seen:

  who approved this change
    really a question, called a statement, score +0
    1 of its 4 words were new to the model

  how the cache works is documented
    really a statement, called a question, score +1
    2 of its 6 words were new to the model

  are the backups working
    really a question, called a statement, score -1
    2 of its 4 words were new to the model

  why is the dashboard so slow
    really a question, called a statement, score -1
    2 of its 6 words were new to the model

  what happened is written in the postmortem
    really a statement, called a question, score +3
    2 of its 7 words were new to the model
```
<!-- end output -->

<br>

## Read them properly

Five failures, and they are three different problems.

### One was a coin toss

> *who approved this change*, really a question but called a statement, **score +0**

Exactly zero. The model had no opinion whatsoever. It came out as "statement" because the code says `total > 0`, and zero is not greater than zero. Write `>=` instead and this message becomes correct, with **nothing about the model changed at all**.

Now the part worth measuring before you reach for that fix. **Four of the twenty** held back messages score exactly zero. One is a question and three are statements. So flipping the tie-break rescues this message and loses the other three, and the honest score goes from 75% down to **65%**.

> [!WARNING]
> A fifth of this result is decided by a convention rather than by the model.
> Ties, rounding, which class wins when nothing wins: it is usually small, it is
> never nothing, and when two systems are a point apart this is often the whole
> difference between them.
>
> Notice also what nearly happened. Looking at one failure suggested an obvious
> one-character fix, and the fix would have made the system worse. That is why
> you measure a change rather than reason about it.

### Three were barely decided

Scores of +0, +1 and −1 on a model whose weights run past ±4. These were not decisions, they were near-ties, and the model would have been about as happy either way.

That matters because it tells you what to do. A model that is wrong and unsure needs more evidence: more data, better features. That is a tractable problem.

### One was confidently wrong

> *what happened is written in the postmortem*, really a statement but called a question, **score +3**

This one it was sure about, and it was wrong. This is the same message that defeated your hand written rule in lesson 2, for the same reason: it opens like a question and then makes a claim.

A model that is wrong and certain is a different and worse problem. More data will not help, because the data agrees with it. The feature itself cannot see the distinction, and no amount of the same feature will fix that.

<br>

## The thread running through all five

Every failure has words the model had never seen. Two of four, two of six, two of seven.

Forty messages was never going to be enough vocabulary. The model is not confused about English, it simply has no weight for *dashboard*, *backups* or *postmortem* and is deciding those messages on the few words it does recognise.

That is one diagnosis with one obvious remedy, and it is more useful than any accuracy figure: **this model needs more data, except for the one case where it needs a better feature.**

> [!TIP]
> This is what error analysis is, and it is the highest value hour in applied
> machine learning. You are not looking for a number. You are sorting failures
> into piles until each pile has an obvious cause, because each cause has a
> different fix and the score cannot tell you which you need.

<br>

## The errors changed sides

In lesson 2 every error was the same direction: statements called questions, never the reverse. Now it is three one way and two the other.

The hand written rule was biased, consistently and predictably. The learned model is unbiased and less accurate. Neither is simply better, and which you want depends on what the mistakes cost, which is a question about your product rather than about your model.

<br>

## Check yourself

```
python tools/run_lessons.py phases/01-teach-it-to-tell-two-things-apart/05-when-it-breaks
```

<br>

## Going further

Optional, and there is no check for it.

Run the tie-break both ways yourself and confirm the 75% and the 65%. Then find the four messages that score exactly zero and read them. They are the ones the model has nothing to say about, and they are the ones worth collecting more data for, which is a far better use of the discovery than changing an operator.

<br>

## What you learned

- A score is a summary that has discarded everything you could act on.
- How strongly a model decided is worth keeping, because wrong-and-unsure and wrong-and-certain need different fixes.
- Ties are broken by convention, and conventions move scores.
- Wrong and unsure usually means not enough evidence. Wrong and certain usually means the feature cannot see the difference.
- Sorting failures into piles by cause is the most valuable hour in the work.
- Which direction your errors lean is a product decision, not just a model property.

<br>

## Phase 1 complete

```
python tools/run_lessons.py phases/01-teach-it-to-tell-two-things-apart
```

You wrote something that learns, in plain Python, with nothing installed. Then you measured it honestly, discovered it lost to nine lines of your own code, and worked out precisely why.

That order matters. Most people learn the first part and never learn the rest, which is how a field ends up full of confident numbers that do not survive contact with anything real.

**Next:** [Phase 2](../../02-a-network-you-wrote-yourself/), where one weighted sum becomes many, and the model can finally see things a single line cannot.
