# 2. Looking at every word at once

> **Lesson 1 left a ceiling of exactly half, and it was not a training
> problem.**
>
> The answer depended on a word five positions back and the model could see
> one. Widening the window would work and would need every wide context to
> have been counted before, which is the vocabulary wall again.
>
> Attention takes the other route. Look at every earlier word at the same
> time, score each one, and read a blend.

**You will:** write one attention head and its backward pass, clear the ceiling, and then find that the head is not doing what the story says it does.

**You need:** [lesson 1](../01-the-thing-a-bigram-cannot-see/) for the ceiling, [phase 2 lesson 4](../../02-a-network-you-wrote-yourself/04-backpropagation/) for the backward pass, and [phase 4 lesson 4](../../04-a-language-model-you-wrote-yourself/04-a-model-that-generalises/) for the softmax gradient.

<br>

## Three projections, a softmax, and a weighted sum

Every word in the context becomes three vectors, by three separate matrices:

| | Made from | What it is for |
|:--|:--|:--|
| **query** | the last word seen | what this position is looking for |
| **key** | every word in the context | what each position offers |
| **value** | every word in the context | what each position contributes if chosen |

Score each position by how well its key matches the query, turn the scores into weights that sum to one, and blend the values by those weights:

```python
query = project(vectors[-1], query_w)
keys = [project(vector, key_w) for vector in vectors]
values = [project(vector, value_w) for vector in vectors]

scale = 1.0 / math.sqrt(WIDTH)
scores = [sum(query[i] * key[i] for i in range(WIDTH)) * scale for key in keys]
attention = softmax(scores)

blended = [sum(attention[j] * values[j][i] for j in range(len(values)))
           for i in range(WIDTH)]
```

That is the whole mechanism. Nothing in it needed to have seen a pair of words together before, which is exactly what the n-gram needed.

> [!NOTE]
> The division by the square root of the width is not decoration. A dot
> product of two vectors of `WIDTH` random numbers grows with `WIDTH`, so
> without the scaling the scores arrive at the softmax large, one of them wins
> outright, and the gradient through the others is nearly zero before training
> has learned anything. Dividing keeps the scores in the range where the
> softmax still has a usable slope.

<br>

## The backward pass, in three steps

The blend is linear in both the attention weights and the values, so each one takes the other as its coefficient:

```python
d_attention = [sum(d_blended[i] * values[j][i] for i in range(WIDTH))
               for j in range(seen)]
d_values = [[d_blended[i] * attention[j] for i in range(WIDTH)]
            for j in range(seen)]
```

Then back through the softmax over positions. Changing one score moves every weight, because they are normalised together, so the shared term is subtracted from each:

```python
shared = sum(d_attention[j] * attention[j] for j in range(seen))
d_scores = [attention[j] * (d_attention[j] - shared) * scale for j in range(seen)]
```

That is the same shape as phase 4's softmax gradient, for the same reason.

<br>

## Your turn

Train one head on forty sentences, score it on the twenty held back, and write `.work/scores.tsv`:

```
model                   right  asked
bigram ceiling          30     60
attention, trained on   38     40
attention, held back    16     20
```

The split keeps each pair together and holds back every third pair, so **every subject word appears on both sides**. A noun the model had never met would fail for [phase 3's reason](../../03-words-that-know-what-they-mean/01-the-vocabulary-wall/) rather than this lesson's.

<br>

## What the solution prints

<!-- output: solve.py -->
```text
41 words, 40 sentences to train on, 20 held back.
One head, 8 wide, 150 passes.

  model                    right      of
  bigram ceiling              30      60      50%
  attention, trained on       38      40      95%
  attention, held back        16      20      80%

Two held back sentences, and how the weight was spread:

         the     server       that        the   engineer  restarted
        0.28       0.08       0.16       0.28       0.17       0.04
  said was, wanted was

         the    servers       that        the   engineer  restarted
        0.29       0.06       0.16       0.29       0.17       0.04
  said was, wanted were

Average weight per position, over the training sentences:
  position     0     1     2     3     4     5
  weight    0.16  0.19  0.19  0.16  0.19  0.12

Heaviest: 1, 2, 4, at 0.19 each. Spreading the weight evenly would
give every position 0.17, so the subject at position 1 is not picked out.

The two sentences above need opposite answers and were given almost the same
weights. It still answered one of them correctly, and the next lesson is about how.
```
<!-- end output -->

<br>

## The ceiling is cleared

**16 of 20 on sentences it was not trained on, against a ceiling of 50%.**

That gap is worth testing rather than admiring. A model that could do no better than guess reaches 16 of 20 or higher **0.59% of the time**, so luck is not a plausible explanation. The check computes that figure with [phase 7 lesson 2's](../../07-measuring-whether-any-of-it-works/02-is-the-difference-real/) arithmetic and refuses to pass if it rises above 5%.

Phase 7 also applies in the other direction. 16 of 20 puts the true rate somewhere between **56.3% and 94.3%**, so what has been established is that the head beats the ceiling, not by how much.

> [!IMPORTANT]
> This is the moment the course has been building towards since phase 4, and
> it is worth being clear about what made it possible.
>
> Not scale. Not more data. The corpus is sixty sentences and the model is
> eight numbers wide. What changed is that the model can address a position
> by *content* rather than by *offset*, so a dependency five words away costs
> it no more than one word away.

<br>

## And the head is not doing what the diagram says

Read the last block of output again.

The average weight is **0.16, 0.19, 0.19, 0.16, 0.19, 0.12**. Perfectly even would be 0.17. Position 1 holds the subject, the one word that decides the answer, and it is tied for heaviest with two positions that carry no information at all.

Worse, look at the two held back sentences. They need opposite answers. Their attention weights are **0.28 / 0.08** and **0.29 / 0.06**, which is the same distribution to within a rounding error. The head is not looking at the subject in one and not the other. It is barely looking anywhere.

And yet it answered one of them correctly, and it scores 16 of 20 overall.

> [!WARNING]
> The story attached to attention is that the weights show you what the model
> used. Here is a model that clears a ceiling no n-gram can reach, with
> weights that are nearly flat and nearly identical between the two cases it
> is distinguishing.
>
> Something else is carrying the signal. Working out what, and what that means
> for every attention heatmap you have ever seen presented as an explanation,
> is the next lesson, which is being written.

<br>

## Check yourself

```
python tools/run_lessons.py phases/09-attention-and-the-block/02-looking-at-every-word-at-once
```

The check trains the head again from the same seed, insists your numbers match, insists every subject word appears on both sides of the split, and insists the held back score clears what luck would produce.

<br>

## Going further

Optional, and there is no check for it.

Set `EPOCHS` to 400 and run it. Training goes to **40 of 40** and the held back score does **not** improve, landing at 15 of 20. More passes buy a perfect fit on forty sentences and nothing else, which is [phase 1 lesson 4](../../01-teach-it-to-tell-two-things-apart/04-tell-the-truth/) arriving in a model with a hundred times the parameters.

Then take the scaling out, so the scores reach the softmax undivided, and print the attention weights on the first few passes before the score. Watch how quickly the mass collects on one position. The claim in the note above is that this costs you the gradient through every other position, and the weights on the early passes are where you can see whether that is true here. Measure it rather than trusting the note.

<br>

## What you learned

- Attention scores every earlier position against a query, normalises the scores, and reads a blend of the values.
- Query, key and value are three separate projections of the same words, and they answer three different questions.
- Dividing the scores by the square root of the width keeps the softmax in the range where it still has a gradient.
- The backward pass is the weighted sum's two coefficients, then the softmax's shared term, which is the same shape as phase 4's.
- One head, eight numbers wide, on sixty sentences, clears a ceiling that no n-gram of any order can reach on this corpus.
- What made that possible is addressing a position by content rather than by offset, not scale and not more data.
- The head's weights are nearly flat and nearly identical between the two cases it distinguishes, so they are not an account of how it decided.

**Next:** *3. It works without looking*, being written, where the signal turns out to be somewhere other than the weights.
