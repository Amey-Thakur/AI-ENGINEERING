# 5. The block

> **Lesson 4 left a model that cannot tell `plan` from `design`. This lesson
> gives it everything a real transformer wraps around an attention head, and
> then cannot show that any of it helped.**
>
> Two layer norms, two residual connections and a feed forward network. Twice
> the parameters and 1.59 times the work per sentence. And every difference it
> makes turns out to be **smaller than the spread between seeds of the same
> model**.
>
> That is the result. The rest of the lesson is about what it does and does
> not entitle you to conclude, and about the bug that nearly let it conclude
> something else.

**You will:** build a transformer block by hand, prove its backward pass against finite differences, count what it costs, and discover that three seeds cannot tell any of these architectures apart.

**You need:** [lesson 4](../04-where-a-word-sits/), and [phase 2 lesson 4](../../02-a-network-you-wrote-yourself/04-backpropagation/) for the nudging technique.

<br>

## What a block is

Everything so far has been one head and an output layer. A real transformer is a stack of blocks, and a block is a head with four things around it:

```
            the vector going in
                    |
            +-------+-------+
            |               |         layer norm, then attention,
       layer norm           |         and what comes out is ADDED to
            |               |         what went in rather than
        attention           |         replacing it
            |               |
            +-------+-------+
                    |
            +-------+-------+
            |               |         layer norm, then a small network,
       layer norm           |         added to the stream in the same
            |               |         way
       up, ReLU, down       |
            |               |
            +-------+-------+
                    |
            the vector coming out
```

| the part | what it does |
|:--|:--|
| **layer norm** | centres the vector and scales it to unit variance, then applies a learned gain and bias. The gain starts at 1 and the bias at 0, so a fresh layer norm is exactly the centring and scaling. |
| **residual** | adds the sub-layer's output to its input instead of replacing it. Everything downstream sees both. |
| **feed forward** | one projection up to four times the width, a ReLU, one projection back down. The multiple of four is the usual proportion. |

The ReLU is new here. Its slope is 1 where it passed a value through and 0 where it did not, so its backward pass is a single comparison.

<br>

## Your turn

Build the block, check the gradients, then train it and write `.work/measured.tsv`:

```
what                                           trained on  held back  separated
bare head, the nine neighbouring pairs         9/9/9       21/21/21   0/0/0
full block, the nine neighbouring pairs        9/10/9      21/24/21   0/9/0
...
```

Three seeds per row, separated by slashes. Report all three. The whole result of this lesson lives in the variation between them, and an average would have hidden it.

> [!IMPORTANT]
> Check the gradients before you train anything.
>
> A layer norm mixes every element of a vector into every other, twice over,
> so its backward pass is the first in this course that is not obvious. A
> residual sends the same gradient down both of its paths. Both are easy to
> get slightly wrong, and slightly wrong does not announce itself: the loss
> still falls and the training still looks ordinary.

<br>

## What the solution prints

<!-- output: solve.py -->
```text
Every parameter group, by hand against a nudge of 1e-06:

  parameter          by hand      by nudging    agrees
  embed             5.979e-01      5.979e-01    yes
  place            -7.268e-01     -7.268e-01    yes
  gain in          -1.325e-01     -1.325e-01    yes
  bias in           3.598e-02      3.598e-02    yes
  query             1.661e-02      1.661e-02    yes
  key               6.265e-03      6.265e-03    yes
  value            -1.346e-01     -1.346e-01    yes
  gain mid         -3.509e-02     -3.509e-02    yes
  bias mid         -1.318e-01     -1.318e-01    yes
  up                2.401e-01      2.401e-01    yes
  up bias           2.906e-01      2.906e-01    yes
  down              4.657e-02      4.657e-02    yes
  down bias        -3.207e-01     -3.207e-01    yes
  out               1.217e+00      1.217e+00    yes

All 14 agree, every one of them inside 1 part in 1e+05.
The backward pass is right.

  what it costs                 bare head    full block    times
  parameters                         504          1088     2.16
  multiplies, one sentence          1200          1904     1.59

Lesson 4's two splits, 4000 updates, seeds 7, 13, 23. A pair counts as separated
only if the model answers one way round and not the other.

  trained on the nine neighbouring pairs
    model                    trained on       held back     separated
    bare head                  9/9/9 of 18     21/21/21 of 42     0/0/0 of 45
    full block                9/10/9 of 18     21/24/21 of 42     0/9/0 of 45

  trained on the nine widest pairs
    model                    trained on       held back     separated
    bare head               18/14/18 of 18     33/25/38 of 42  36/25/41 of 45
    full block              18/14/14 of 18     37/25/25 of 42  40/25/25 of 45

Now put a number on how much of that is the architecture and how much is the
seed. For each pair of rows, compare the gap between their averages against
the spread within a single row:

  comparison                                   gap between   spread within
  head against block, adjacent pairs                  3.0               9
  head against block, widest pairs                    4.0              16
  block against block without layer norms            17.0              39

Every one of those gaps is smaller than the spread inside a single row. The
block separates 9 pairs the head could not at one seed and none at the other
two. Taking the layer norms out destroys it at two seeds and leaves it better
than the full block at the third.

With three seeds on sixty sentences, none of these architectures has been
shown to differ from any other. That is the honest result, and it is not the
one this lesson was written expecting.

  the three rows, so you can see where the spread comes from
    bare head, adjacent                    [0, 0, 0]
    full block, adjacent                   [0, 9, 0]
    bare head, widest                      [36, 25, 41]
    full block, widest                     [40, 25, 25]
    block without layer norms, widest      [0, 39, 0]

Depth is what they are for, and one block cannot show it. A stack of plain
feed forward sub-blocks, nothing trained, a unit gradient put in at the
output, 20 seeds, geometric mean:

  layers    gradient reaching the input          leaving the stack
            norm only    both      residual only   both   residual only
       1     1.80e+00   3.52e+00       3.60e+00     3.2       3.09e+00
       2     1.47e+00   3.91e+00       4.35e+00     3.4       3.33e+00
       4     1.15e+00   5.52e+00       5.31e+00     3.8       3.92e+00
       8     1.04e+00   7.35e+00       1.13e+01     5.4       8.16e+00
      16     1.81e-01   8.71e+00       3.07e+01     7.5       3.02e+01
      32     2.24e-02   1.36e+01       5.22e+02    11.0       3.31e+02

At 32 layers the residual is worth 606 times the gradient at the input, and
the layer norm holds the stream 30 times smaller than it would otherwise
leave. Neither number exists at one layer, which is the whole reason this
lesson's block cannot show you what a block is for.
```
<!-- end output -->

<br>

## The bug this lesson had

The first version of this block was wrong. In the loop over positions, the input layer norm's gain was updated as each position was handled, so **every position after the first computed its gradient against a gain that had already moved.**

| | |
|:--|:--|
| the loss | fell normally |
| the training | looked completely ordinary |
| the gradients for 12 of 14 parameter groups | correct to about 1 part in 10⁹ |
| the gradients for `embed` and `place` | **4% wrong** |

And here is what the broken version scored, against the correct one, on the same seeds:

| separated, seeds 7 / 13 / 23 | adjacent pairs | widest pairs |
|:--|:--:|:--:|
| the broken block | 9 / 0 / 0 | 21 / 40 / 21 |
| the correct block | 0 / 9 / 0 | 40 / 25 / 25 |

On the adjacent pairs those are **the same three numbers in a different order**. A gradient that is four per cent wrong produced results indistinguishable from a change of seed, and on the widest pairs it produced the better-looking row. Nothing in the loss, the scores or the training curve could have told you which code was correct.

> [!CAUTION]
> This is the most useful habit in the course and it costs about twenty lines:
> **compare every hand-written gradient against a finite difference of the
> loss before you believe any number the model produces.**
>
> Automatic differentiation removes the need for this by removing the
> hand-written gradient. It does not remove it when you write a custom
> backward pass, fuse an operation, quantise a layer, or reimplement something
> for speed, and those are exactly the cases where a four per cent error hides
> inside a plausible training curve.
>
> Put the bug back and [`check.py`](check.py) fails in under half a second,
> naming `place` as the parameter whose gradient has drifted.

<br>

## It costs more

| | bare head | full block | times |
|:--|--:|--:|--:|
| parameters | 504 | 1,088 | **2.16** |
| multiplies per sentence | 1,200 | 1,904 | **1.59** |

Those are exact counts, not estimates, and they are the only numbers in this lesson that do not move.

<br>

## And nothing it buys can be measured here

| separated, of 45 | seeds 7 / 13 / 23 | spread |
|:--|:--:|--:|
| bare head, adjacent pairs | 0 / 0 / 0 | 0 |
| full block, adjacent pairs | 0 / 9 / 0 | **9** |
| bare head, widest pairs | 36 / 25 / 41 | **16** |
| full block, widest pairs | 40 / 25 / 25 | **15** |
| block with no layer norms, widest pairs | 0 / 39 / 0 | **39** |

Now compare each pair of rows:

| comparison | gap between the averages | spread within a row |
|:--|--:|--:|
| head against block, adjacent | 3.0 | 9 |
| head against block, widest | 4.0 | 16 |
| block against block with no layer norms | 17.0 | 39 |

**Every gap is smaller than the spread.** The block separates nine pairs the head could not at one seed and none at the other two. Removing the layer norms destroys the model at two seeds and leaves it *better than the full block* at the third.

So the honest statement is not that the block fails to help. It is that **this experiment cannot tell whether it helps**, and three runs on sixty sentences were never going to.

> [!WARNING]
> An earlier version of this lesson said something cleaner and more
> satisfying: that the block separates nothing the bare head could not, and
> that taking the layer norms out stops it working entirely. Both were true
> of the three seeds it first used. Both are false of the three it uses now.
>
> Nothing about the model changed between those two versions. The seeds
> changed, because one of the originals turned out to produce a number that
> depends on which C library Python was built against
> ([lesson 4](../04-where-a-word-sits/) has that measurement). A conclusion
> that a seed swap can reverse was never a conclusion about the architecture.

<br>

## What the parts are for, then

Depth, which one block cannot show you. So measure it directly, on a stack of plain feed forward sub-blocks with nothing trained: put a unit gradient in at the output and see what size arrives at the input.

| layers | gradient at the input, layer norm only | with both | leaving the stack, residual only | with both |
|--:|--:|--:|--:|--:|
| 1 | 1.80 | 3.52 | 3.09 | 3.2 |
| 8 | 1.04 | 7.35 | 8.16 | 5.4 |
| 32 | **0.0224** | **13.6** | **331** | **11.0** |

At 32 layers the residual is worth **606 times** the gradient reaching the input, and the layer norm holds the stream **30 times** smaller than it would otherwise leave. Neither number exists at one layer, and these are the only architecture measurements in the lesson that are not swamped by their own noise.

> [!NOTE]
> These are **geometric** means over 20 seeds. Each layer multiplies what
> passes through it, so the sizes are spread the way a product of random
> numbers is spread, and an ordinary average is dragged around by one lucky
> run. The ordinary mean of these same measurements gives a column that is
> not even monotone in depth, which is how this table looked before the
> statistic was corrected.

<br>

## Check yourself

```
python tools/run_lessons.py phases/09-attention-and-the-block/05-the-block
```

The check builds its own block rather than importing this one, because a check that calls the code it is checking can only reproduce a mistake instead of finding it. It then insists that the backward pass agrees with finite differences, that the block costs more than the head on both counts, that **no architecture gap exceeds the seed spread**, and that the depth measurement still shows the residual and the layer norm doing their jobs.

That third assertion is deliberately the opposite of the usual one. It fails if the lesson ever finds a real architectural difference, which would mean the lesson needs rewriting rather than the check relaxing.

<br>

## Going further

Optional, and there is no check for any of it.

The obvious next move is the one this lesson could not afford: run every configuration at twenty seeds instead of three and see whether any of the gaps survive. Each run is about seven seconds, so the full set is roughly twenty minutes. That is the actual price of the question, and the reason the lesson reports three and says so.

Then ablate the other two parts. Removing the feed forward network and removing the residuals both land inside the same spread as everything else here, which is worth confirming rather than taking on trust.

Then stack two blocks. Each will have to produce an output at every position rather than only the last, which multiplies the attention cost by the number of positions. The question worth asking is whether two blocks can separate adjacent stages, because composing two steps is the one thing a single block provably cannot do.

Last, set `HIDDEN` to the width instead of four times it. If nothing moves, the conventional proportion is not earning its place at this size either.

<br>

## What you learned

- A transformer block is an attention head plus two layer norms, two residual connections and a small feed forward network, and it is about sixty lines more than the head.
- A layer norm's backward pass is not elementwise, because centring and scaling both mix every element into every other.
- A residual sends the same gradient down both of its paths, which is one line and the reason deep stacks train at all.
- Compare every hand-written gradient against a finite difference before trusting any number. The bug here left 12 of 14 parameter groups correct to 1 part in 10⁹, and its scores were a permutation of the correct code's.
- The block costs 2.16 times the parameters and 1.59 times the work. Those are the only numbers in the lesson that hold still.
- Every architectural difference measured here is smaller than the variation between seeds of a single configuration, so none of them has been demonstrated.
- A conclusion that reverses when you change the seed was never a conclusion about the architecture. Both of this lesson's original findings did exactly that.
- What the residual and the layer norm are for is depth: 606 times the gradient and 30 times less drift at 32 layers. A one-block model cannot show it, which is the honest reason the rest of the lesson looks the way it does.

**Next:** nothing. This is the last lesson of the last phase.

You began at [phase 1](../../01-teach-it-to-tell-two-things-apart/) with a model that told two things apart by counting words, and you have just written a transformer block and proved its gradients by hand, on a laptop, with nothing installed. The [glossary](../../../GLOSSARY.md) holds every term the course used and the lesson that measured it, and the [course README](../../../README.md) has the five guarantees every lesson is held to.

What to do with it is what the course has done fifty times: pick something you believe about a model, work out which measurement would embarrass you if you were wrong, and run that one.
