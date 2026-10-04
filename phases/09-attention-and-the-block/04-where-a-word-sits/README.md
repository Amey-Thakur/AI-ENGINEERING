# 4. Where a word sits

> **The model from lesson 3 cannot see order at all. Not approximately.**
>
> Shuffle the words in its context and **0 of 60** decisions change, with a
> largest probability difference of **0.00e+00**. A mean of the values does not
> depend on the order of the values, and that is the whole of it.
>
> This lesson gives it order, and then finds out what order bought.

**You will:** add a learned vector per position, then discover that the same model on the same number of examples either learns the order of ten things or learns nothing, depending on which examples it was shown.

**You need:** [lesson 3](../03-it-works-without-looking/).

<br>

## A new corpus, built so that order is the only signal

[`order.tsv`](../order.tsv) holds 60 sentences about a ten stage pipeline, in pairs:

```
the plan preceded the design which was normal
the design preceded the plan which was backwards
```

Every pair is the same six words in a different arrangement. So **every context appears twice, once with each answer**, and a model that cannot tell order apart is capped at exactly half before it starts. That is not an estimate. It is a property of the file, and [`check.py`](check.py) refuses to pass if the file ever stops having it.

<br>

## Position, the only way a model of this shape can have it

One table of vectors, one row per position, added to the word's vector before anything else happens:

| | |
|:--|:--|
| without position | the vector at step `j` is `embed[word]` |
| with position | the vector at step `j` is `embed[word] + place[j]` |

A position's vector was added to the word's, so **the two of them take the same gradient**. That is the only change to the backward pass, and it is three lines.

<br>

## Your turn

Train with and without the place table, audit the split, then train on nine pairs twice, and write `.work/placed.tsv`:

```
what                                              trained on  held back
no position, split A                              20          10
position embeddings, split A, seed 7              40          5
...
```

Every model gets the same **4,000 weight updates**, whatever the size of its training set, so a run on nine pairs cannot be waved away as having been trained less than a run on twenty.

> [!NOTE]
> The three seeds are **7, 13 and 23, and they were chosen rather than
> picked arbitrarily.** Two criteria, both measured and both explained at the
> end of this lesson: the run fits its training set, and its result does not
> change when the arithmetic is perturbed by a single last bit.
>
> Choosing seeds is the sort of thing that deserves to be said out loud,
> because the same freedom can be used to choose a result.

<br>

## What the solution prints

<!-- output: solve.py -->
```text
60 sentences built from a 10 stage chain, 16 words.
Every context appears twice, once with each answer, so a model that cannot tell
order apart is capped at half whatever else it does.

Shuffle the context of lesson 3's model, keeping the query word last:
  decisions changed: 0 of 60
  largest probability difference: 0.00e+00

Not approximately unchanged. Unchanged. Order is not an input to that model.

Split A holds back every third pair: 40 sentences to train on, 20 held
back, chance 10. Every model below gets 4000 weight updates.

  model                                 trained on   held back
  no position                           20 of 40    10 of 20
  position embeddings, seed 7           40 of 40     5 of 20
  position embeddings, seed 13          40 of 40     9 of 20
  position embeddings, seed 23          40 of 40    10 of 20

Position makes the training set solvable: 20 of 40 becomes 40 of 40 at all
three of these seeds, which the model without it cannot do at any seed at all.
Held back it gives 5, 9 and 10 against a chance of 10.

Before concluding anything about the model, audit the split. Of the 10 held-back
pairs, how many have an order that follows from the training pairs by chaining?

  order settled by the training pairs:         2 of 10
  order the training data never determines:    8 of 10
  so the most an order learner could expect:  12 of 20

8 of those 10 questions have no answer anywhere in the training data.

Split B asks something answerable. Train on nine pairs and hold back the other 21.
Chance is 21 of 42 in both rows, and both rows get 4000 updates.

  nine pairs trained on                 trained on   held back   chain settles
  the nine neighbouring pairs            9 of 18    21 of 42   21 of 21
  the nine widest pairs                 18 of 18    33 of 42    0 of 21

Read that table twice. The split whose held-back answers are fully settled by
chaining is the one the model cannot do at all, and the split where chaining
settles nothing is the one it gets most of right.

So it is not chaining. Probe all 45 stage pairs, including the 15 that
appear in no sentence, and ask which it will commit to an order on:

  model trained on                   commits     agrees with the chain
  the nine neighbouring pairs           0 of 45    nothing to ask
  the nine widest pairs                36 of 45    36 of 36

  how far apart the two stages sit   the widest trained model commits on
  1 stage                                       2 of 9
  2 stages                                      6 of 8
  3 stages                                      7 of 7
  4 stages or more                             21 of 21

Nothing it commits to is wrong: 36 of 36 agree with the chain. What it will
not do is separate stages that sit next to each other, and trained on adjacent
pairs alone it separates nothing at all (0 of 45).

It has not learned a chain. It has put the ten stages on a line and compares
positions on that line, which answers pairs no chain reaches and fails on pairs
too close together to tell apart. Position told it where a word sits. It did
not give it anything to compare two words with except distance.
```
<!-- end output -->

<br>

## Act one: position is what makes the task learnable

**20 of 40 becomes 40 of 40**, at all three seeds. Without the place table the model cannot fit even the sentences it is being shown, because it cannot distinguish them; with it, it fits every one.

That is the clean, expected result, and it is the last clean thing in this lesson.

<br>

## Act two: the held-back number was not measuring the model

Held back, the place table gives **5, 9 and 10 of 20** against a chance of 10. The honest reading of a spread like that is *no signal*, and the 5 at seed 7 is not a below-chance effect worth explaining. It is one draw.

But before concluding anything about the model, audit the split. An order is answerable if it **follows from the training pairs by chaining**: shown that the plan precedes the design and the design precedes the code, the plan precedes the code whether or not that sentence ever appeared.

| split A, held back | |
|:--|:--|
| order settled by the training pairs | 2 of 10 |
| **order the training data never determines** | **8 of 10** |
| so the most an order learner could expect | 12 of 20 |

**Eight of those ten questions have no answer anywhere in the training data.** No model could get them right except by luck, and neither could you. The split was not measuring whether the model generalises; it was asking it to guess.

> [!IMPORTANT]
> This is the ordinary case, not an exotic one. A random split of a dataset
> with structure in it routinely holds back questions the training half does
> not determine, and the held-back score then has a ceiling nobody computed.
> [Phase 7](../../07-measuring-whether-any-of-it-works/) measured error bars on
> a number. This is the other half of the same discipline: **before trusting a
> held-back number, work out what the best possible score on it would be.** If
> you cannot, the number is not a measurement.

<br>

## Act three: the audit predicted the wrong split, twice

So build splits that are answerable. Train on nine pairs, hold back the other 21, same model, same 4,000 updates.

| nine pairs trained on | trained on | held back | chain settles |
|:--|:--:|:--:|:--:|
| the nine neighbouring pairs | 9 of 18 | 21 of 42 | **21 of 21** |
| the nine widest pairs | 18 of 18 | **33 of 42** | **0 of 21** |

Chance is 21 of 42 in both rows. Read it twice, because it is the reverse of what the audit says:

- Trained on the nine **neighbouring** pairs, whose chain settles **every one** of the 21 held-back pairs, the model scores exactly chance. It cannot even fit its own 18 training sentences.
- Trained on the nine **widest** pairs, whose chain settles **none** of them, it fits all 18 and reaches **33 of 42**.

The yardstick I built in act two is the right yardstick for a system that reasons by chaining. This model is not one, and applying it got the answer backwards both times. **An audit is a claim about the learner as much as about the data**, and this one had a learner smuggled into it.

<br>

## Act four: so what did it learn?

Ask it about all 45 stage pairs, including the 15 that appear in no sentence at all. A pair counts as **separated** only if the model says `normal` to one ordering and `backwards` to the other. The same answer to both is a refusal, and scores exactly one of the two sentences.

| trained on | separates | and is wrong about |
|:--|:--:|:--:|
| the nine neighbouring pairs | 0 of 45 | nothing to ask |
| the nine widest pairs | 36 of 45 | **0 of 36** |

**On this run it is wrong about none of the 36.** And what it refuses is not random:

| how far apart the two stages sit | separated |
|:--|:--:|
| 1 stage | 2 of 9 |
| 2 stages | 6 of 8 |
| 3 stages | 7 of 7 |
| 4 stages or more | 21 of 21 |

It has not learned a chain. It has put the ten stages **on a line**, and it compares positions on that line. That is why it answers pairs no chain reaches, and why the pairs it refuses are the ones closest together: the gap is too small for its readout to resolve.

> [!WARNING]
> One run is one run. Across ten seeds the distant run is wrong about a
> handful of its commitments rather than none, and at one seed in the ten it
> collapses the way the adjacent run does, separating **0 of 45**.
>
> So the claim that survives is the comparison, not the figure: the adjacent
> run separates nothing at every seed tried, the distant run usually separates
> most pairs and is right about nearly all of them, and the gap between those
> two is larger than the gap between seeds. "Never wrong" is true of the seed
> reported here and not of every seed, and it is worth being exact about
> which of those a sentence is describing.
>
> [Lesson 5](../05-the-block/) is what happens when that distinction is not
> made: two of its findings reversed when its seeds changed.

> [!NOTE]
> There is a reason the readout cannot resolve a small gap, and it is visible
> in the shape of the model rather than in the training run. The blend is a
> **softmax-weighted sum**, so every weight is positive, and the decision is
> therefore a positive combination of what the two stage words contribute. A
> positive combination moves with the **sum** of the two contributions as well
> as with their difference. Along a chain the difference between neighbours
> stays one step while the sum sweeps the whole scale, so no single threshold
> separates them. Train on distant pairs and the difference is large enough to
> survive the sum moving. Nine adjacent pairs pin the order completely and
> still teach it nothing, because what it needs is not more constraints but a
> bigger gap.

<br>

## Check yourself

```
python tools/run_lessons.py phases/09-attention-and-the-block/04-where-a-word-sits
```

The check insists the order-blind model is blind to the last decimal place and lands on exactly half, that a place table fits the training set completely, that split A stays mostly undetermined, that the adjacent run separates at most two of the 45 pairs, and that the distant run separates at least 25 and gets **none** of them the wrong way round. If the adjacent run ever starts working, this lesson is wrong and should be rewritten rather than the check relaxed.

<br>

## Going further

Optional, and there is no check for any of it.

Print `place[1]` and `place[4]` from the trained model and compare them. The whole of the model's access to order runs through those two vectors, and they are eight numbers each.

Then train on nine pairs drawn at random from every gap, several times over. Position embeddings fit 14, 16, 17 and 18 of 18 on four such draws, against 9 of 18 for the adjacent nine and 18 of 18 for the widest nine, which is the same finding from a third direction.

Then run split A at ten seeds and look at the training column rather than the held-back one. Position embeddings fit all 40 training sentences at five of the ten, land at 39 and 31 at two more, and at the remaining three they score **20 of 40**, which is exactly what the model with no position at all scores. So "position makes this task learnable" is the right claim and "position learns this task" is not: half the time the run never gets off the floor.

Last, the measurement that chose the seeds. Replace `math.exp` with a version that shifts one result in every thousand by a single last bit, which is the most two different C libraries could plausibly disagree by, and retrain:

| seed | clean | one last bit moved |
|--:|:--:|:--:|
| 7 | 5 of 20 | 5 of 20 |
| 11 | 9 of 20 | **10 of 20** |
| 23 | 10 of 20 | 10 of 20 |

Seed 11's held-back score depends on which maths library Python was built against. Nine of the ten seeds tried are stable and that one is not, and the decisions involved are not close calls: every margin in that run is above 0.5, so it is not a tie being broken differently. Four thousand updates is simply long enough for a last-bit difference to compound into a different model.

> [!IMPORTANT]
> Sit with that one. This lesson has spent its whole length arguing that a
> held-back number needs its ceiling worked out before it means anything.
> Here is a held-back number that **changes depending on the operating
> system**, while the model, the data, the seed and every line of the code
> stay identical.
>
> It is not a bug to be fixed. The arithmetic is chaotic with respect to its
> own last bits, and no tolerance or tie-break rule removes that. The only
> defences are to report more than one seed, to prefer claims that survive
> perturbation, and to say which of those you have done.

Last, feed the widest-trained model a sentence whose two stages are the same word, `the plan preceded the plan which was`. There is no right answer. Whatever it says is the model's own bias showing, with nothing in the data to hide behind.

<br>

## What you learned

- A mean of values is exactly order blind, and measuring it is better than assuming it: 0 of 60 decisions move, by 0.00e+00.
- A position's vector is added to the word's, so the two take the same gradient, which is the whole of the backward pass change.
- Position embeddings are what make an order task learnable: 20 of 40 becomes 40 of 40.
- Before trusting a held-back score, work out the best possible score on it. Eight of split A's ten held-back pairs have no answer in the training data, so the number was never a measurement of generalisation.
- An audit encodes an assumption about how the learner works. The chaining audit predicted the wrong split twice, because this model does not chain.
- Given well-separated examples the model puts ten things on a line and is right about nearly every pair it will commit to, including pairs it was never shown. Given adjacent examples it learns nothing at all, at every seed tried.
- Which examples a model is shown can matter more than how many, and the mechanism is the margin between them rather than the count.
- A held-back score from a four thousand update run can depend on the platform's maths library, confidently and without any decision being close. Report more than one seed, and prefer the claims that survive a perturbation.

**Next:** [5. The block](../05-the-block/), where the attention head gets everything that surrounds it in a real transformer, and we find out whether any of it closes the gap this lesson opened.
