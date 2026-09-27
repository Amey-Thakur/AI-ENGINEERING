# 2. A second layer

> **Half a million lines failed. Three of them, arranged in two layers, will not.**
>
> Nothing here learns. You are going to choose the weights yourself, so that
> when XOR falls over you know exactly what did it: not training, not luck, the
> shape of the network.

**You will:** build a two layer network by hand, solve the problem lesson 1 proved was impossible, and see exactly why it works.

**You need:** [lesson 1](../01-the-thing-one-line-cannot-do/).

<br>

## Two questions first, then the answer

A line cannot separate XOR's points. But a line can answer each of these:

- **Is at least one input on?** That is OR, and OR is separable.
- **Are both inputs on?** That is AND, which you proved separable in lesson 1.

Once you know those two facts, XOR is simply: **either, and not both**. Which is itself a line, drawn over the two answers rather than over the original inputs.

<br>

## The weights, and why each one

```python
hidden_either = (1, 1, -0.5)    # fires when the inputs sum past 0.5
hidden_both   = (1, 1, -1.5)    # fires when they sum past 1.5
output        = (1, -1, -0.5)   # fires on either, unless both
```

Read `hidden_either`. Both inputs count for 1, and the bias subtracts 0.5. With no inputs on the total is −0.5 and it stays quiet. With one on it is +0.5 and it fires. The bias is a threshold expressed as a number you add.

`hidden_both` weights the inputs identically and only shifts the bias to −1.5, so it needs two inputs before it clears zero. Same weights, different threshold, completely different question.

`output` is the only new idea. It does not read the inputs at all. It reads the two hidden answers: +1 for *either*, −1 for *both*. So *either* alone clears the bias, and *both* cancels it out again.

<br>

## The forward pass

Inputs go into the hidden units, hidden answers go into the output unit, and that is the answer. Running data through in that direction is called the **forward pass**, and every network in this course does exactly this, with more units.

```python
either = unit(x1, x2, hidden_either)
both   = unit(x1, x2, hidden_both)
answer = unit(either, both, output)
```

<br>

## Your turn

Write `.work/network.tsv`:

```
unit             w1    w2    bias
hidden_either    1     1     -0.5
hidden_both      1     1     -1.5
output           1     -1    -0.5
```

Any weights that solve XOR pass. There are infinitely many, and yours do not have to be these.

<br>

## What the solution prints

<!-- output: solve.py -->
```text
  in      either  both     out   wanted
  0, 0      0      0        0       0
  0, 1      1      0        1       1
  1, 0      1      0        1       1
  1, 1      1      1        0       0

4 of 4 right

Where the four points sit after the first layer:
  (0, 0) <- 00   wanted: 0
  (1, 0) <- 01, 10   wanted: 1
  (1, 1) <- 11   wanted: 0
```
<!-- end output -->

<br>

## Read the bottom of that output again

This is the part worth understanding, and it is not the four correct answers.

| Original input | After the first layer | Wanted |
| --- | --- | --- |
| `0 0` | `(0, 0)` | 0 |
| `0 1` | `(1, 0)` | 1 |
| `1 0` | `(1, 0)` | 1 |
| `1 1` | `(1, 1)` | 0 |

**The two inputs that should answer 1 have landed on the same point.** `01` and `10` were on opposite corners, and after the first layer they are both at `(1, 0)`.

So the output unit is not solving XOR. It is solving a completely different and much easier problem: separate `(1, 0)` from `(0, 0)` and `(1, 1)`. One line does that easily.

> [!IMPORTANT]
> The first layer did not classify anything. It **moved the points**, into a
> position where a line works. That is what every hidden layer in every network
> does, and it is worth saying plainly because the usual descriptions bury it:
> a layer's job is to rewrite the data so the next layer's job is easy.
>
> Deep networks are this, repeated. Each layer hands the next one a version of
> the problem that is a little more separable than the one it received.

<br>

## What you have actually built

This is a **neural network**. Two layers, three units, nine numbers. Not a toy version of one, the real thing: the networks with billions of parameters differ in size, in how they are trained, and in using a smooth activation instead of a hard threshold. The structure is what you just wrote.

<br>

## The problem with what you just built

You chose those nine numbers, by thinking about OR and AND. That works because XOR is small enough to reason about.

It does not scale even slightly. Nobody can reason their way to the weights for a network over a vocabulary of three hundred words, and that is a tiny network. You need the machine to find them, exactly as the perceptron did in phase 1.

The perceptron rule will not do it. It knows how to move the weights on the unit that made the mistake, but when the output unit is wrong, whose fault is it? Its own weights, or the hidden units that handed it bad features? That question is called **credit assignment**, and it is what the rest of this phase answers.

> [!NOTE]
> This was exactly where the field stalled after 1969. The limitation of a
> single layer was proved, the fix of adding layers was obvious, and nobody had
> a way to train the result. That gap lasted into the 1980s.

<br>

## Check yourself

```
python tools/run_lessons.py phases/02-a-network-you-wrote-yourself/02-a-second-layer
```

<br>

## Going further

Optional, and there is no check for it.

Set both hidden units to the same weights and run it. The output unit now receives the same number twice and can do nothing with it, and you are back to one line with extra steps. Two units that ask the same question are one unit. Keep that in mind when you later wonder why a network is not improving as you make it wider.

<br>

## What you learned

- Two layers solve what one provably cannot.
- The bias is a threshold written as a number you add, and shifting it alone turns OR into AND.
- The forward pass is inputs to hidden units, hidden answers to the output.
- A hidden layer moves the data, rather than classifying it, so the next layer's problem becomes separable.
- Choosing weights by hand works at this size and nowhere beyond it.
- When the output is wrong, working out which weights to blame is the hard part, and it has a name: credit assignment.

**Next:** [3. How wrong, and in which direction](../03-how-wrong-and-which-direction/), where you stop counting mistakes and start measuring them.
