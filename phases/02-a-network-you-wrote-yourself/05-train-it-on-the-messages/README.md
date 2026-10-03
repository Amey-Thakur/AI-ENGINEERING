# 5. Train it on the messages

> **You now have a network, a way to train it, and a real problem waiting.**
>
> This is the lesson where the three meet. It is also the lesson where you find
> out that having a better model is not the same as getting a better answer.

**You will:** train the network on the phase 1 messages, score it honestly, and compare it against everything you have built.

**You need:** [lesson 4](../04-backpropagation/).

<br>

## The setup

Same data, same split as phase 1: train on the first 40 messages, score on the last 20.

Each message becomes one number per word in the vocabulary: 1 if the word is there, 0 if not. That vector goes into four hidden units, and those feed one output.

> [!IMPORTANT]
> The vocabulary is built from the **training messages only**. Building it from
> all sixty would let the held back messages shape the model before it is
> scored on them, and the score would quietly stop being honest. This is the
> leak from phase 1 lesson 4, in the place it usually happens: not in the
> training loop, but in the preparation before it.

<br>

## Random starts, and a seed

The hidden units cannot all start at zero. If two units begin identical they receive identical gradients, make identical updates, and stay identical forever. Four units that are all the same unit is one unit.

So the weights start at small random values. But random means a different answer every run, and this course does not do that:

```python
generator = random.Random(SEED)
```

A **seed** fixes which random numbers come out. The starting weights are random in shape and identical on every machine, which is exactly what you want: real experiments are reported with their seed so someone else can get your number back.

<br>

## Your turn

Train it, then write two files.

`.work/predictions.tsv`, the network's call on each held back message. `.work/scores.tsv`:

```
model            right    total    accuracy
network_train    39       40       0.9750
network_test     15       20       0.7500
hand_rule_test   18       20       0.9000
```

> [!NOTE]
> The check scores your predictions itself and compares them with what you
> reported, and it works out the hand written rule's score independently. A
> network that does badly still passes. A comparison that flatters it does not.

<br>

## What the solution prints

<!-- output: solve.py -->
```text
128 words of vocabulary, from 40 training messages
521 weights, trained on 40 examples

  On what it learned from:  39 of 40   97.5%
  On what it never saw:     15 of 20   75.0%

Everything built so far, on the same twenty held back messages:

  Hand written rule, phase 1 lesson 2    18 of 20   90.0%
  Perceptron, phase 1 lesson 4           15 of 20   75.0%
  This network                           15 of 20   75.0%
```
<!-- end output -->

<br>

## Read the first two lines again

**521 weights, trained on 40 examples.**

Thirteen parameters for every message it has ever seen. There is more than enough capacity here to memorise all forty answers outright without learning anything at all about English, and 97.5% on the training data is what that looks like.

<br>

## The scoreboard

| Model | Held back twenty | Built in |
| --- | --- | --- |
| **Hand written rule** | **90%** | Phase 1, lesson 2 |
| Perceptron | 75% | Phase 1, lesson 4 |
| Two layer network | 75% | This lesson |

The network, with backpropagation and a hidden layer and five hundred parameters, **ties the perceptron and loses to nine lines of code**.

<br>

## Why, precisely

Lesson 1 of this phase showed a problem a line cannot solve, and the fix was more layers. It is tempting to carry that lesson here: the model was too simple, so make it deeper.

That diagnosis is wrong, and the evidence was already in front of you. Phase 1 lesson 5 found that the held back messages contained 56 words the model had no weight for. **The bottleneck was never capacity. It was vocabulary.**

A bigger model cannot learn what *dashboard* means from forty messages that never contain the word. It can only use its extra capacity to fit the forty it has more exactly, which is precisely what it did.

The hand written rule sidesteps all of it, because it encodes a fact about English rather than a pattern in this data. Facts about English do not care how many messages you collected.

> [!WARNING]
> "It is not working, make it bigger" is the most expensive wrong instinct in
> this field. Capacity fixes problems of the shape in lesson 1, where the model
> cannot represent the answer. It does nothing for problems of evidence, where
> the model cannot see the answer in the data it has.
>
> Telling those two apart before spending anything is the skill. The diagnosis
> is usually sitting in your error analysis already.

<br>

## Check yourself

```
python tools/run_lessons.py phases/02-a-network-you-wrote-yourself/05-train-it-on-the-messages
```

<br>

## Going further

Optional, and there is no check for it.

Take `HIDDEN` from 4 to 16, and then to 64. The training score climbs towards a perfect 40 out of 40 and the held back score does not follow. Watching that gap widen, on a model you wrote yourself, is worth more than reading about overfitting a dozen times.

Then change `SEED` to another number and run again. The held back score moves by a few points on nothing but the starting weights. Any single result you ever report includes some of that, which is why serious work reports several seeds.

<br>

## Phase 2 complete

```
python tools/run_lessons.py phases/02-a-network-you-wrote-yourself
```

You proved a limit, built the thing that breaks it, measured gradients from first principles, wrote a backward pass and checked it to twelve decimal places, and then put it all on a real problem and found it lost.

That last part is the phase. A course that stopped at "the network learns XOR" would have taught you something true and left you believing something false.

**Next:** [Phase 3](../../03-words-that-know-what-they-mean/), which attacks the actual bottleneck: the model has no idea that *dashboard* and *server* have anything to do with each other.
