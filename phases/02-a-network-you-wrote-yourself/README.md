# Phase 2. A network you wrote yourself

**Five lessons. About four hours. Still nothing installed.**

Phase 1 ended with a model that was wrong and certain, and a sentence to sit with: the feature could not see the difference, and no amount of the same feature ever will.

This phase is about that wall. You prove it exists, build the thing that gets past it, work out how to train that thing, and then put it on the real problem and find out what it was actually worth.

<br>

## The lessons

| # | Lesson | The idea underneath it |
| --- | --- | --- |
| 1 | [The thing one line cannot do](01-the-thing-one-line-cannot-do/) | Some limits are properties of the model, and can be proved |
| 2 | [A second layer](02-a-second-layer/) | A hidden layer moves the data until a line works |
| 3 | [How wrong, and in which direction](03-how-wrong-and-which-direction/) | A slope you can measure without any calculus |
| 4 | [Backpropagation](04-backpropagation/) | The same slopes, in one pass instead of two per weight |
| 5 | [Train it on the messages](05-train-it-on-the-messages/) | A better model is not the same as a better answer |

<br>

## What you will have written

A neural network. Not a toy standing in for one: two layers, a forward pass, a loss, a hand written backward pass gradient checked to twelve decimal places, and a training loop. In plain Python, with nothing installed, in about four hours.

> [!NOTE]
> Nothing in this phase is simplified for teaching. The networks with billions
> of parameters differ in size, in the activation they use and in how the
> training is scheduled. The structure is what you write here.

<br>

## How it ends

Badly, and on purpose.

The network you build is trained properly, measured honestly, and **loses to the nine line rule you wrote in phase 1**. That result is real, it is reproducible on your machine, and it is the most useful thing in the phase.

A course that stopped at "the network learns XOR" would have taught you something true and left you believing something false.

<br>

## Check the phase

```
python tools/run_lessons.py phases/02-a-network-you-wrote-yourself
```

**Next:** [Phase 3](../03-words-that-know-what-they-mean/), which goes after the real bottleneck rather than the interesting one.
