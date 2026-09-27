# 1. The thing one line cannot do

> **Phase 1 ended with a model that was wrong and certain.**
>
> More data would not have fixed it. The feature could not see the difference,
> and no amount of the same feature ever will. This lesson is about the wall
> behind that sentence, and it is a real wall with a proof on it.

**You will:** prove, by exhausting every possibility, that there is a problem no single weighted sum can solve.

**You need:** [phase 1](../../01-teach-it-to-tell-two-things-apart/).

<br>

## Two tiny problems

Strip everything away. Two inputs, each 0 or 1. Four possible messages, and an answer for each.

**AND** answers 1 only when both inputs are 1.

| in | in | out |
| --- | --- | --- |
| 0 | 0 | 0 |
| 0 | 1 | 0 |
| 1 | 0 | 0 |
| 1 | 1 | **1** |

**XOR** answers 1 when the inputs differ.

| in | in | out |
| --- | --- | --- |
| 0 | 0 | 0 |
| 0 | 1 | **1** |
| 1 | 0 | **1** |
| 1 | 1 | 0 |

XOR is "one or the other, but not both". People use it constantly: pick one option or the other; the alarm fires if the door is open or the window is, unless maintenance opened both.

<br>

## Your model is a line

The model from phase 1 was one weighted sum compared against a threshold:

```python
total = first_input * w1 + second_input * w2 + bias
answer = 1 if total > 0 else 0
```

Draw the four points on paper, with the first input across and the second up. That formula draws a **straight line**, and answers 1 on one side and 0 on the other. Choosing weights moves and tilts the line. That is all choosing weights can ever do.

Now try to draw a line with both AND's 1s on one side. Easy: a diagonal across the top right corner.

Now do it for XOR. The 1s are at top-left and bottom-right, the 0s at bottom-left and top-right, diagonally opposite each other. Try for a minute. It is worth failing at this by hand before you see it proved.

<br>

## Proving it, rather than observing it

You could train a model on XOR, watch it fail, and conclude it is impossible. That conclusion would not be earned. All you would have shown is that **that run** failed. Perhaps the weights started badly, or it needed more passes.

So do not train. Try every line.

Walk weights and bias from −4 to 4 in steps of a tenth, which is 81 values each, 531,441 combinations. Score all four points for every one. Keep the best.

> [!IMPORTANT]
> This is the difference between evidence and proof, and it shows up constantly
> in this work. "My model could not do it" is a fact about your model. "No model
> of this shape can do it" is a fact about the problem, and only the second one
> tells you to go and get a different shape.

<br>

## Your turn

Search the grid for both problems and write `.work/results.tsv`:

```
problem    best    total
and        4       4
xor        3       4
```

The check runs its own search and compares.

<br>

## What the solution prints

<!-- output: solve.py -->
```text
Tried 531,441 weight combinations on each problem.

AND
  best any single line can do: 4 of 4
  reached with weights 0.1 and 0.1, bias -0.1

XOR
  best any single line can do: 3 of 4
  reached with weights -4 and 0.1, bias 0

AND is separable: one line divides its points and every combination
that does so is found immediately.

XOR is not. No line exists, so the best any of them manages is three
out of four, and the fourth is always wrong.
```
<!-- end output -->

<br>

## Three out of four, always

Half a million lines, and not one of them gets XOR right. The best manage three, and there is always a fourth point on the wrong side.

That is not a training problem, a data problem or a tuning problem. It is the shape of the model. A straight line divides a plane into two pieces, and XOR needs its two 1s separated from its two 0s when they sit diagonally opposite. No straight line does that. It was proved in 1969, and it stopped work on these models for over a decade.

<br>

## What fixes it

Not a bigger line. A **second layer**.

Suppose you first compute two intermediate facts:

- `a` = is at least one input on?
- `b` = are both inputs on?

Each is a straight line, so each is something you already know how to build. Now XOR is simply `a AND NOT b`, which is another straight line, this time drawn over `a` and `b` rather than over the original inputs.

The first layer changes what the question is asked about. Once the inputs have been rewritten into better features, a line is enough again.

> [!TIP]
> That sentence is the entire idea of deep learning, and everything after it is
> engineering. Layers are not stacked because more is better. Each layer builds
> features the next one can separate with a line, and it learns what those
> features should be rather than waiting for you to think of them.

<br>

## Check yourself

```
python tools/run_lessons.py phases/02-a-network-you-wrote-yourself/01-the-thing-one-line-cannot-do
```

<br>

## Going further

Optional, and there is no check for it.

Work out weights for the two intermediate facts by hand. "At least one is on" is a line; so is "both are on". Then find weights over those two that give XOR. It is a pleasant puzzle, it takes about ten minutes with pen and paper, and you will have built a neural network by hand before writing a line of code for one.

<br>

## What you learned

- One weighted sum with a threshold draws a straight line, and choosing weights only moves it.
- AND can be separated by a line. XOR cannot, and that is a property of the problem.
- Failing to train something proves nothing; searching the whole space proves a lot.
- A second layer rewrites the inputs into features that *are* separable.
- Layers exist to make the next layer's job linear, which is the whole idea underneath deep learning.

**Next:** [2. A second layer](../02-a-second-layer/), where you build that network and watch XOR fall over.
