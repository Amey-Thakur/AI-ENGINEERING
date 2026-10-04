# 5. The block

> **Lesson 4 left a model that cannot tell `plan` from `design`. This lesson
> gives it everything a real transformer wraps around an attention head, and
> it still cannot.**
>
> Two layer norms, two residual connections and a feed forward network. Twice
> the parameters, 1.59 times the work per sentence, and **0 of 45** stage pairs
> separated, which is exactly what the bare head managed.
>
> That is the result. The rest of the lesson is about what it does and does
> not entitle you to conclude.

**You will:** build a transformer block by hand, prove its backward pass is right with finite differences, count what it costs, and measure that it buys nothing here.

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
| **feed forward** | one projection up to four times the width, a ReLU, one projection back down. The width multiple of four is the usual proportion. |

The ReLU is new here. Its slope is 1 where it passed a value through and 0 where it did not, so its backward pass is a single comparison.

<br>

## Your turn

Build the block, check the gradients, then train it and write `.work/measured.tsv`:

```
what                                           trained on  held back  separated
bare head, the nine neighbouring pairs         9/9/9       21/21/21   0/0/0
full block, the nine neighbouring pairs        9/9/9       21/21/21   0/0/0
...
```

Three seeds per row, separated by slashes, because one number from one seed is what lesson 4 nearly got caught by.

> [!IMPORTANT]
> Check the gradients before you train anything.
>
> A layer norm mixes every element of a vector into every other, twice over,
> so its backward pass is the first one in this course that is not obvious.
> A residual sends the same gradient down both of its paths. Both are easy to
> get slightly wrong, and slightly wrong does not announce itself: the loss
> still falls and the training still looks ordinary.

<br>

## What the solution prints

<!-- output: solve.py -->
```text
Every parameter group, by hand against a nudge of 1e-06:

  parameter          by hand      by nudging    relative gap
  embed             5.979e-01      5.979e-01        1.55e-10
  place            -7.268e-01     -7.268e-01        3.37e-10
  gain in          -1.325e-01     -1.325e-01        1.22e-09
  bias in           3.598e-02      3.598e-02        1.41e-08
  query             1.661e-02      1.661e-02        1.86e-08
  key               6.265e-03      6.265e-03        6.35e-08
  value            -1.346e-01     -1.346e-01        5.65e-11
  gain mid         -3.509e-02     -3.509e-02        5.90e-09
  bias mid         -1.318e-01     -1.318e-01        2.06e-09
  up                2.401e-01      2.401e-01        1.37e-09
  up bias           2.906e-01      2.906e-01        6.22e-10
  down              4.657e-02      4.657e-02        6.56e-10
  down bias        -3.207e-01     -3.207e-01        1.50e-11
  out               1.217e+00      1.217e+00        1.78e-10

Largest relative gap across all 14 of them: 6.4e-08. The backward pass is right.

  what it costs                 bare head    full block    times
  parameters                         504          1088     2.16
  multiplies, one sentence          1200          1904     1.59

Lesson 4's two splits, 4000 updates, seeds 7, 11, 23. A pair counts as separated
only if the model answers one way round and not the other.

  trained on the nine neighbouring pairs
    model                    trained on       held back     separated
    bare head                  9/9/9 of 18     21/21/21 of 42     0/0/0 of 45
    full block                 9/9/9 of 18     21/21/21 of 42     0/0/0 of 45

  trained on the nine widest pairs
    model                    trained on       held back     separated
    bare head               18/14/18 of 18     33/25/38 of 42  36/25/41 of 45
    full block               18/9/14 of 18     37/21/25 of 42   40/0/25 of 45

The block does not separate a single pair the head could not. On the adjacent
pairs neither of them separates anything at all, at any seed.

So take the layer norms out of the block and train it again, on the split
where there was something to lose:

    model                    trained on       held back     separated
    full block               18/9/14 of 18     37/21/25 of 42   40/0/25 of 45
    block, no layer norms      9/9/9 of 18     21/21/21 of 42     0/0/0 of 45

Without them it separates nothing, at every seed. The layer norms are not
an improvement to the block. They are what keeps it working at all, and the
bare head needed none of them because it has no residual and no network
adding to its stream.

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

## The bug this lesson actually had

The first version of this block was wrong. In the loop over positions, the input layer norm's gain was updated as each position was handled, so **every position after the first computed its gradient against a gain that had already moved.**

Here is what that bug did:

| | |
|:--|:--|
| the loss | fell normally |
| the training | looked completely ordinary |
| the gradients for 12 of 14 parameter groups | correct to 1 part in 10⁹ |
| the gradients for `embed` and `place` | **4% wrong** |
| the measured result | the broken block separated **9 of 45** pairs on the adjacent split, where the correct one separates 0 |

Read that last row again. The bug did not make the model fail. It made it look like it was **working**, on exactly the task this lesson was asking about, and the number it produced was the interesting one. Had the gradient check not been written first, this lesson would have reported that a block solves what a bare head cannot, and that claim would have been an artefact of a four-line mistake.

The fix is to collect the gain's gradient across all positions and apply it once they are all done.

> [!CAUTION]
> This is the single most useful habit in the whole course, and it costs about
> twenty lines: **compare every hand-written gradient against a finite
> difference of the loss before you believe any number the model produces.**
>
> Automatic differentiation removes the need for this by removing the
> hand-written gradient. It does not remove the need for it when you write a
> custom backward pass, fuse an operation, quantise a layer, or reimplement
> something for speed, and those are exactly the situations where a 4% error
> hides inside a plausible training curve.

<br>

## It does not help

| trained on the nine neighbouring pairs | trained on | held back | separated |
|:--|:--:|:--:|:--:|
| bare head | 9/9/9 of 18 | 21/21/21 of 42 | **0/0/0 of 45** |
| full block | 9/9/9 of 18 | 21/21/21 of 42 | **0/0/0 of 45** |

| trained on the nine widest pairs | trained on | held back | separated |
|:--|:--:|:--:|:--:|
| bare head | 18/14/18 of 18 | 33/25/38 of 42 | 36/25/41 of 45 |
| full block | 18/9/14 of 18 | 37/21/25 of 42 | 40/0/25 of 45 |

On the adjacent pairs, neither separates anything at any seed. On the widest pairs the two are indistinguishable at three seeds: both reach the high thirties at their best seed and both collapse at one.

And it is not free:

| | bare head | full block | times |
|:--|--:|--:|--:|
| parameters | 504 | 1,088 | **2.16** |
| multiplies per sentence | 1,200 | 1,904 | **1.59** |

<br>

## But its own parts are load bearing

Take the two layer norms out and retrain, on the split where there was something to lose:

| | trained on | held back | separated |
|:--|:--:|:--:|:--:|
| full block | 18/9/14 of 18 | 37/21/25 of 42 | 40/0/25 of 45 |
| block, no layer norms | 9/9/9 of 18 | 21/21/21 of 42 | **0/0/0 of 45** |

Without them the block does not work at all, at every seed. And this is the part worth sitting with: **the bare head has no layer norms either, and it works fine.**

So the layer norms are not an improvement to the model. They are what pays for the residual and the network. Adding machinery created a need for more machinery to keep the thing stable, and the net result on this task is zero.

> [!NOTE]
> This is why architecture components cannot be evaluated one at a time. A
> table of "with and without" rows invites the reading that each row is a
> contribution you could add up. Here, removing the layer norm costs
> everything and adding the layer norm to the bare head would do nothing at
> all, because there is no residual stream for it to hold down. The
> components are only meaningful as a set.

<br>

## What the parts are for, then

Depth, which one block cannot show you. So measure it directly, on a stack of plain feed forward sub-blocks with nothing trained: put a unit gradient in at the output and see what size arrives at the input.

| layers | gradient at the input, layer norm only | with both | leaving the stack, residual only | with both |
|--:|--:|--:|--:|--:|
| 1 | 1.80 | 3.52 | 3.09 | 3.2 |
| 8 | 1.04 | 7.35 | 8.16 | 5.4 |
| 32 | **0.0224** | **13.6** | **331** | **11.0** |

At 32 layers the residual is worth **606 times** the gradient reaching the input, and the layer norm holds the stream **30 times** smaller than it would otherwise leave. Neither number exists at one layer.

> [!NOTE]
> These are **geometric** means over 20 seeds, not ordinary ones. Each layer
> multiplies what passes through it, so the sizes are spread the way a product
> of random numbers is spread, and a plain average is dragged around by one
> lucky run. Taking the ordinary mean of the same measurements produces a
> column that is not even monotone in depth, which is how this lesson's first
> version of the table looked before the statistic was corrected.

<br>

## Check yourself

```
python tools/run_lessons.py phases/09-attention-and-the-block/05-the-block
```

The check builds its own block rather than importing this one, because a check that calls the code it is checking can only reproduce a mistake, not find it. It then insists that the backward pass agrees with finite differences, that the block costs more than the head on both counts, that the block separates nothing the head could not on the adjacent split, and that removing the layer norms stops it working.

Put the gain bug back and the check fails in under half a second, naming `place` as the parameter whose gradient has drifted.

<br>

## Going further

Optional, and there is no check for any of it.

Ablate the other two parts on the widest split, three seeds each. Removing the feed forward network gives 37/0/40 separated against the full block's 40/0/25, so it is contributing nothing measurable; removing the residuals gives 0/0/21. Neither is as decisive as the layer norms, and three seeds is not enough to rank them.

Then stack two blocks. Each block will have to produce an output at every position rather than only the last, which is a real change to the code and roughly multiplies the attention cost by the number of positions. The question worth asking of it is whether two blocks can separate adjacent stages, because composing two steps is the one thing a single block provably cannot do.

Last, set `HIDDEN` to the width instead of four times it and see whether anything moves. If nothing does, the conventional proportion is not earning its place at this size either, which is worth knowing before carrying it into something larger.

<br>

## What you learned

- A transformer block is an attention head plus two layer norms, two residual connections and a small feed forward network, and it is about sixty lines more than the head.
- A layer norm's backward pass is not elementwise, because centring and scaling both mix every element into every other.
- A residual sends the same gradient down both of its paths, which is one line and the reason deep stacks train.
- Compare every hand-written gradient against a finite difference before trusting any number. The bug in this lesson left 12 of 14 parameter groups correct to 1 part in 10⁹, made the loss curve look normal, and produced a *better* result than the correct code.
- On this task the block separates nothing the bare head could not, at twice the parameters and 1.59 times the work.
- Removing the block's layer norms stops it working entirely, while the bare head never needed them. Components are only meaningful as a set.
- What the residual and the layer norm are for is depth: at 32 layers they are worth 606 times the gradient and 30 times less drift in the stream. A one-block model cannot show you that, which is the honest reason this lesson's measurements look the way they do.
- A negative result on a task too small to need the mechanism is not evidence the mechanism is useless. It is evidence the task was too small, and saying so is more useful than finding a number that flatters the architecture.

**Next:** nothing. This is the last lesson of the last phase.

You began at [phase 1](../../01-teach-it-to-tell-two-things-apart/) with a model that told two things apart by counting words, and you have just finished writing a transformer block and proving its gradients by hand, on a laptop, with nothing installed. The [glossary](../../../GLOSSARY.md) holds every term the course used and the lesson that measured it, and the [course README](../../../README.md) has the five guarantees every one of these lessons is held to.

What to do with it is the same thing the course has done forty nine times: pick something you believe about a model, work out what measurement would embarrass you if you were wrong, and run that one.
