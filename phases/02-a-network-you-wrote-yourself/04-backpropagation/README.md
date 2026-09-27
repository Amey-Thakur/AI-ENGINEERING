# 4. Backpropagation

> **Lesson 3 needed eighteen passes over the data to find nine numbers.**
>
> A network with a million weights would need two million passes for one step
> of training. Backpropagation gets all of them in a single pass backwards, and
> that difference is the reason any of this exists.

**You will:** compute every gradient in one backward sweep, and check each one against the nudging you already trust.

**You need:** [lesson 3](../03-how-wrong-and-which-direction/).

<br>

## Blame, handed backwards

The output unit is wrong by some amount. That amount has to be split between the weights that produced it, and then passed further back to the hidden units that fed it.

Each step asks one question: **how much did this contribute to the error, and through what?**

<br>

## Keep the forward values

```python
def forward(point, weights):
    z1 = ...; h1 = sigmoid(z1)
    z2 = ...; h2 = sigmoid(z2)
    zo = ...; out = sigmoid(zo)
    return h1, h2, out
```

Lesson 2 threw the intermediate values away. Here they are kept, because the backward pass needs every one.

> [!NOTE]
> This is why training a network costs far more memory than running one. It is
> not the weights, it is every intermediate value for every example in the
> batch, all held until the backward pass has used them.

<br>

## Working backwards

**At the answer.** The loss is the squared gap averaged over four points, so its slope against the answer is `2 * (out - label) / 4`.

**Through the sigmoid.** A sigmoid whose output is `s` has slope `s * (1 - s)`. That is worth reading twice: to know how steep the curve is, you only need the value it already gave you. Nothing is recomputed.

```python
delta_out = d_loss_d_out * out * (1 - out)
```

`delta_out` is now "how much the total going into the output unit is to blame".

**To the weights.** A weight's gradient is its delta times whatever it was multiplying:

```python
gradients["out_h1"] += delta_out * h1      # it multiplied h1
gradients["out_b"]  += delta_out           # the bias multiplies 1
```

**Back to the hidden units.** Each hidden unit is to blame in proportion to the weight through which it spoke, then through its own sigmoid:

```python
delta_h1 = delta_out * weights["out_h1"] * h1 * (1 - h1)
```

And then the same rule as before: delta times whatever it multiplied.

That is the whole algorithm. It is the **chain rule**, applied one layer at a time, and it goes as deep as you like by repeating those two moves.

<br>

## Check it against something you trust

A hand written backward pass is one sign away from being wrong, and a sign error does not crash. Training just gets worse slowly, and looks like a bad idea rather than a bug.

So compute both ways and compare. This is called **gradient checking**, and it is what anyone writing a backward pass does before trusting it.

<br>

## Your turn

Write `.work/comparison.tsv`:

```
weight    backward      nudged        difference
h1_w1     0.004430      0.004430      2.6e-12
```

<br>

## What the solution prints

<!-- output: solve.py -->
```text
  weight     backward       nudged      difference
  h1_w1     +0.004430   +0.004430   2.6e-12
  h1_w2     +0.002222   +0.002222   3.1e-12
  h1_b      +0.006813   +0.006813   2.1e-13
  h2_w1     -0.003081   -0.003081   4.1e-12
  h2_w2     -0.001772   -0.001772   5.4e-13
  h2_b      -0.004838   -0.004838   2.1e-12
  out_h1    +0.019794   +0.019794   5.2e-12
  out_h2    +0.015647   +0.015647   1.2e-12
  out_b     +0.034473   +0.034473   9.8e-13

Largest disagreement: 5.2e-12

Backward pass: 1 pass over the data for all 9 gradients
Nudging:       18 passes for the same 9
For a network with a million weights, that is 1 against 2,000,000.
```
<!-- end output -->

<br>

## What agreement to twelve decimal places means

The largest disagreement is about **5e-12**. The two methods share no code: one differentiates the network by hand, the other only ever calls `loss()` and watches it move.

Both arriving at `+0.004430` for `h1_w1` means the derivatives are right. Not probably right. Right.

> [!TIP]
> Expect roughly 1e-10 or smaller when both are correct. Around 1e-3 usually
> means a real mistake. An exactly flipped sign means a term was subtracted
> where it should have been added, and it is the most common error of all,
> because everything still runs.

These are also the same nine numbers lesson 3 measured, which is worth noticing: two lessons, two entirely different methods, identical answers.

<br>

## What it bought

| Method | Passes over the data | For a million weights |
| --- | --- | --- |
| Nudging | 2 per weight | 2,000,000 |
| Backward pass | 1, total | 1 |

Backpropagation is not a better approximation. It gives the exact same numbers, in one pass instead of two million. Training a modern model by nudging would take longer than the universe has existed.

The idea dates to the 1970s and reached this field in 1986. The gap between "add a second layer" in lesson 2 and "here is how to train it" is roughly seventeen years of the field being stuck, and this is what unstuck it.

<br>

## Check yourself

```
python tools/run_lessons.py phases/02-a-network-you-wrote-yourself/04-backpropagation
```

<br>

## Going further

Optional, and there is no check for it.

Break it on purpose. Remove the `* h1 * (1 - h1)` from `delta_h1` and run the check: the hidden gradients diverge while the output ones stay perfect, which tells you precisely where the error is. Then flip a sign and watch the difference become exactly twice the value. Learning to read those two signatures will save you a day at some point.

<br>

## What you learned

- Backpropagation is the chain rule applied one layer at a time, working from the answer to the inputs.
- Forward values are kept because the backward pass needs them, which is why training costs the memory it does.
- A sigmoid's slope is `s * (1 - s)`, computable from the value you already have.
- A weight's gradient is its delta times whatever it multiplied.
- Always gradient check a hand written backward pass, because sign errors do not crash.
- One backward pass replaces two per weight, and that ratio is why large models are possible at all.

**Next:** [5. Train it on the messages](../05-train-it-on-the-messages/), where the network meets the real problem from phase 1 and you find out whether it beats nine lines of hand written rule.
