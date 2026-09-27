# 4. Fewer numbers that say more

> **Every word currently carries 608 numbers, and almost all of them are zero.**
>
> A word appears near perhaps thirty others in this corpus, so its profile is
> thirty real values and 578 empty slots. Worse, the values that are there
> include the rare accidents lesson 3 warned about, each shouting at full
> volume.

**You will:** squeeze every profile down to 24 numbers, and find that the words become closer to *more* meaningful than they were.

**You need:** [lesson 3](../03-surprise-is-the-signal/).

<br>

## Why compressing helps rather than hurts

It sounds like a trade: throw away detail, accept a worse answer, gain speed. It is not.

The 608 numbers are not 608 independent facts. Words about deployment move together, words about meetings move together. The data really varies along a much smaller number of directions, and the rest is noise wearing a dimension.

Keeping only the strongest directions keeps the pattern and leaves the noise behind. That is why the answer improves.

> [!NOTE]
> This also fixes the complaint from lesson 3. *server* near *restarting* once
> looked enormously surprising, and in 608 dimensions that accident had a whole
> dimension to itself. Squeezed into 24, it has to share, and there is nothing
> else pointing that way to share with.

<br>

## Finding the directions

Multiply a vector by the matrix, then by its transpose. Whatever direction the data varies along most gets stretched the most, so the vector rotates towards it. Repeat, normalising each time, and it converges.

```python
for row in rows.values():
    along = sum(value * current[slot] for slot, value in row.items())
    for slot, value in row.items():
        carried[slot] += value * along
```

For the next direction, do the same but subtract off everything already found, so it cannot simply rediscover the strongest one:

```python
for earlier in found:
    overlap = sum(a * b for a, b in zip(carried, earlier))
    carried = [a - overlap * b for a, b in zip(carried, earlier)]
```

That is **power iteration**, and it is genuinely how this is done on matrices too large for anything else. Twenty lines, no library.

Then each word becomes its position along those 24 directions.

> [!TIP]
> The starting vector is fixed rather than random: `sin(index * 7 + slot * 0.7)`.
> Uneven, so it is not accidentally perpendicular to what it is looking for,
> and identical on every machine, so the lesson gives the same answer for
> everyone. Real implementations use a random start and a seed.

<br>

## Your turn

Compress the profiles to 24 numbers per word and write `.work/vectors.tsv`:

```
word      d0         d1         d2       ...
server    0.412... -0.883...  0.119...
```

> [!IMPORTANT]
> The check tests a property, not your numbers. A direction is equally valid
> pointing the other way, and two correct implementations can order their
> directions differently, so comparing against stored values would fail honest
> work. What it checks is that *server* stays closer to *memory* than to
> *agenda*, and five more like it. Structure is what has to survive.

<br>

## What the solution prints

<!-- output: solve.py -->
```text
608 words, 608 contexts
Every word was 608 numbers, mostly zero. Now it is 24.
Stored values for the 116 common words: 4216 before, 2784 after

Nearest neighbours, on the squeezed vectors:

  server     memory 0.73, of 0.63, postmortem 0.62, no 0.62, with 0.59
  deploy     failed 0.76, version 0.76, staging 0.69, pipeline 0.64, image 0.58
  customer   too 0.76, were 0.74, account 0.74, issue 0.68, at 0.60
  test       bug 0.79, that 0.77, passed 0.68, never 0.65, failed 0.63
  meeting    document 0.78, agenda 0.77, half 0.71, written 0.59, each 0.55
  incident   an 0.83, postmortem 0.80, written 0.71, monitoring 0.71, token 0.68
```
<!-- end output -->

<br>

## What you have now

**608 numbers became 24**, and the neighbours got better:

| Word | Before, 608 numbers | After, 24 numbers |
| --- | --- | --- |
| `deploy` | failed, version, staging | failed, version, staging, **pipeline**, **image** |
| `meeting` | document, runs, agenda | document, **agenda**, half, written |
| `test` | that, bug, passed, suite | **bug**, that, **passed**, never, **failed** |

`deploy` now has five plausible neighbours where it had three. The similarity scores rose from around 0.2 to around 0.7, because the profiles are no longer mostly empty and two related words now genuinely overlap rather than sharing a handful of scattered slots.

These 24 numbers are what people mean by a **word embedding** or a **word vector**. Modern ones are learned by a network rather than counted, and they use 300 to 1,000 numbers over billions of words, and they behave better. They are the same object: a word as a position in a space, placed by the company it keeps.

<br>

## The honest limits

*incident* is closest to **an**. *customer* has **too** and **were** above *issue*. Filler still leaks in, because 2,019 words of corpus is not enough for the statistics to settle.

A bigger corpus is the real fix. A cleverer formula on 217 sentences is not, and knowing which of those two a problem needs is the thing this course keeps coming back to.

<br>

## Check yourself

```
python tools/run_lessons.py phases/03-words-that-know-what-they-mean/04-fewer-numbers-that-say-more
```

<br>

## Going further

Optional, and there is no check for it.

Set `DIMENSIONS` to 2 and look at the neighbours: everything collapses together, because two directions cannot separate six topics. Then try 200 and watch the noise return as the rare accidents get room to themselves again. Somewhere in between is a sweet spot, it is different for every corpus, and it is found by measuring rather than by reasoning.

<br>

## What you learned

- A sparse profile of 608 numbers holds perhaps thirty real facts.
- The data varies along far fewer directions than it has dimensions.
- Power iteration finds those directions with multiplication and normalising, and nothing else.
- Each new direction must be kept clear of the ones already found.
- Compression improves the answer, because it leaves the noise behind.
- Twenty four numbers per word is a word embedding, and the famous ones differ in scale rather than in kind.

**Next:** [5. Does it help?](../05-does-it-help/), where these vectors go back to the problem from phase 1 and have to earn their place.
