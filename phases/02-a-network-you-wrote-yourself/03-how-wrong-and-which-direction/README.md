# 3. How wrong, and in which direction

> **Counting mistakes tells you how many. It never tells you which way to move.**
>
> The perceptron rule got away with this because it had one layer to blame.
> With two, being wrong is not enough information. You need a number that
> changes smoothly as the weights change, so you can ask it which direction is
> downhill.

**You will:** replace the threshold with a curve, measure wrongness as one number, and find the slope of that number against every weight in the network.

**You need:** [lesson 2](../02-a-second-layer/).

<br>

## The threshold has to go

```python
answer = 1 if total > 0 else 0
```

Nudge a weight slightly. The total moves slightly. The answer does not move at all, until the total crosses zero, at which point it jumps.

So the question "does making this weight larger help?" has no answer. Almost everywhere, changing it does nothing. At one point it changes everything. There is no direction to follow.

<br>

## A curve instead

```python
def sigmoid(total):
    return 1.0 / (1.0 + math.exp(-total))
```

The **sigmoid** does what the threshold did, softly. Very negative totals give nearly 0, very positive give nearly 1, and in between it slides smoothly through 0.5.

Now nudging a weight always changes the answer a little, and the size of that change is the information you were missing.

> [!NOTE]
> This is the swap that unblocked the field. Same architecture as lesson 2,
> same forward pass. The only difference is that the units answer 0.982 instead
> of 1, and the cost of that vagueness is that everything becomes trainable.

<br>

## One number for wrongness

```python
gap = predict(point) - label
total += gap * gap
```

The **loss**: square each gap so that errors in both directions count, and errors that are twice as large count four times as much. Average over the four points.

At the start the loss is about 0.2557. Alone that means nothing. It means something the moment you can move it.

<br>

## The slope, measured rather than derived

You want to know, for each weight: if I increase this a little, does the loss go up or down, and how steeply?

That is a **gradient**, and you can measure it without any calculus at all. Nudge the weight up, record the loss. Nudge it down, record the loss. Divide the difference by the distance travelled.

```python
nudged[name] = weights[name] + NUDGE
higher = loss(nudged)

nudged[name] = weights[name] - NUDGE
lower = loss(nudged)

return (higher - lower) / (2 * NUDGE)
```

That is the definition of a slope, written out. Rise over run.

> [!IMPORTANT]
> This is not how real training computes gradients: it costs two full passes
> over the data per weight, which for a real network is hopeless. It is here
> because it needs nothing but arithmetic to believe, and because the next
> lesson's fast method is going to be checked against it.

<br>

## Which way to move

If the slope is **positive**, the loss rises as the weight rises, so make the weight smaller. If **negative**, larger. Either way: move against the gradient.

```python
weights[name] = weights[name] - rate * gradients[name]
```

The `rate` is how big a step to take. That single line is **gradient descent**, and it is how essentially every model you have heard of is trained.

<br>

## Your turn

Measure the slope of the loss against each of the nine weights, at the starting values, and write `.work/gradients.tsv`:

```
weight    value      gradient
h1_w1     0.500000   0.004430
h1_w2     -0.400000  0.002222
```

The check measures them itself and compares.

<br>

## What the solution prints

<!-- output: solve.py -->
```text
Loss at the start: 0.255735

  weight     value     slope     move it
  h1_w1     +0.50   +0.004430   down
  h1_w2     -0.40   +0.002222   down
  h1_b      +0.10   +0.006813   down
  h2_w1     -0.30   -0.003081   up
  h2_w2     +0.60   -0.001772   up
  h2_b      -0.20   -0.004838   up
  out_h1    +0.70   +0.019794   down
  out_h2    -0.50   +0.015647   down
  out_b     +0.15   +0.034473   down

  steps     loss
       1    0.254813
      10    0.251290
     100    0.250439
    1000    0.250014
    2000    0.249863
    5000    0.013732
   10000    0.001051
   20000    0.000345

What it answers now, against what it should:
  0, 0   0.020   wanted 0
  0, 1   0.982   wanted 1
  1, 0   0.982   wanted 1
  1, 1   0.018   wanted 0
```
<!-- end output -->

<br>

## The most important thing in that output

Look at the loss as the steps go by.

| Steps | Loss |
| --- | --- |
| 1 | 0.2548 |
| 100 | 0.2504 |
| 1000 | 0.2500 |
| 2000 | 0.2499 |
| **5000** | **0.0137** |
| 20000 | 0.0003 |

For two thousand steps, **nothing happens**. The loss sits at 0.2500 and refuses to move.

0.25 is exactly what you get by answering 0.5 to everything. The network has found the safest possible position: it has stopped being confidently wrong by refusing to commit at all. The surface there is nearly flat, the gradients are tiny, and every step moves almost nothing.

Then it breaks out, and within a few thousand more steps the problem is solved: 0.020, 0.982, 0.982, 0.018.

> [!WARNING]
> Anyone watching the first two thousand steps would conclude this was broken
> and stop. It is the single most common way people abandon a model that was
> about to work.
>
> Plateaus are not failure. They are the shape of the surface. The answer is
> knowing that this one exists, not staring harder at the loss.

<br>

## Check yourself

```
python tools/run_lessons.py phases/02-a-network-you-wrote-yourself/03-how-wrong-and-which-direction
```

<br>

## Going further

Optional, and there is no check for it.

Change `rate` from 0.5 to 5.0 and watch the plateau nearly vanish: it escapes by around a thousand steps instead of five. Then try 50 and watch it break entirely. The step size is the most consequential number in training, and the range between "too slow to finish" and "too big to work" is narrower than anyone expects.

<br>

## What you learned

- A hard threshold has no useful slope, so nothing can be tuned through it.
- The sigmoid trades crisp answers for the ability to be trained, and that trade built the field.
- The loss squeezes all your errors into one number that moves smoothly.
- A gradient is rise over run, and you can measure it by nudging, with no calculus.
- Move against the gradient. That is gradient descent, and it is nearly all of training.
- Long flat stretches are normal, and they look exactly like failure.

**Next:** [4. Backpropagation](../04-backpropagation/), which computes these same nine numbers in one pass instead of eighteen, and checks itself against what you measured here.
