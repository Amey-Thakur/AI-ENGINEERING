# 2. The company a word keeps

> **"You shall know a word by the company it keeps."**
>
> John Firth wrote that in 1957, and it is the idea the last twenty years of
> this field is built on. Nobody has to define what *server* means. You only
> have to notice that it turns up near *memory*, *restart* and *load*, and that
> *friday* does not.

**You will:** count which words appear near which, use those counts as meaning, and watch it fail in an instructive way.

**You need:** [lesson 1](../01-the-vocabulary-wall/).

<br>

## Something to count

`messages.tsv` has sixty sentences. That is nowhere near enough to learn what words mean, so this lesson brings `corpus.txt`: **217 sentences of ordinary technical English**, written for this course.

```
the server ran out of memory and restarted itself
the query scanned the whole table because the index was missing
the customer reported the issue through a ticket
```

> [!NOTE]
> 217 sentences is still tiny. A real word vector is trained on billions.
> What this corpus is big enough to do is show the mechanism honestly,
> including the places it strains, which a corpus of the proper size would
> hide behind results that simply look good.

<br>

## Counting the company

For every word, count every word that appears near it. Near means **within four words, in the same sentence**.

```python
for position, word in enumerate(sentence):
    start = max(0, position - WINDOW)
    stop = min(len(sentence), position + WINDOW + 1)

    for other in range(start, stop):
        if other != position:
            counts[word][sentence[other]] += 1
```

A word is now no longer a slot. It is a **profile**: the company it keeps, with numbers.

The window size is a real choice. Narrow windows pick up words that behave alike grammatically; wide ones pick up words about the same subject. Four is a reasonable middle, and nothing about it is sacred.

<br>

## Comparing two profiles

Two words are similar if they keep similar company. The standard measure is **cosine**: do these two profiles point the same way?

```python
together = sum(first[word] * second[word] for word in shared)
return together / (size * other)
```

It divides out length deliberately, so a word appearing a hundred times can still be similar to one appearing ten. Only the *direction* of the profile counts, not its size.

> [!TIP]
> Cosine is used everywhere in this field, well beyond words: retrieving
> documents, matching faces, finding duplicates. It answers "point the same
> way?" rather than "are the same size?", and that is almost always the
> question you actually mean.

<br>

## Your turn

Build the profiles, then for the five probe words find their nearest neighbours. Write `.work/neighbours.tsv`:

```
word      neighbour    closeness
server    was          0.820761
```

<br>

## What the solution prints

<!-- output: solve.py -->
```text
217 sentences, 2019 words, 608 distinct
116 words appear at least 4 times

What sits near 'server', most often first:
  the          8
  memory       2
  ran          1
  out          1
  of           1
  restarted    1
  cleanly      1
  and          1

Nearest neighbours, by raw counts:

  server     was 0.82, and 0.78, dashboard 0.77, after 0.77, to 0.76
  deploy     was 0.75, meeting 0.74, on 0.74, and 0.73, pipeline 0.72
  customer   and 0.88, was 0.85, ticket 0.83, the 0.83, because 0.82
  test       a 0.73, the 0.68, token 0.66, review 0.64, suite 0.64
  meeting    was 0.88, in 0.84, and 0.83, dashboard 0.82, after 0.82

Words appearing in at least three of those five lists: and, was
```
<!-- end output -->

<br>

## It does not work, and the reason is visible

Read the neighbours. `server` is closest to **was** and **and**. `meeting` is closest to **was** and **in**. The last line says it plainly: **and** and **was** turn up in three of the five lists.

Now look at the table above it, the company `server` keeps. The most frequent neighbour is **the**, eight times. *memory* appears twice.

That is the whole failure in one table. **The** sits near *server* because **the** sits near everything. It carries no information about *server* at all, and yet by raw count it dominates the profile.

Every profile therefore looks mostly like a list of common English words, and every word ends up similar to every other word, which is the problem lesson 1 was supposed to have solved.

> [!IMPORTANT]
> The signal is genuinely there. `customer` had **ticket** at 0.83, `test` had
> **suite** at 0.64, `deploy` had **pipeline** at 0.72. Those are real and they
> are correct. They are simply outranked by noise.
>
> That is a much better position than it looks. The method works, and the
> weighting is wrong. Weighting is fixable.

<br>

## What is wrong with the count

*server* appears near *the* eight times. Is that surprising? No: *the* is near everything, so of course it is near *server*.

*server* appears near *memory* twice. Is *that* surprising? Very. *memory* is rare, so finding it beside *server* twice is a real coincidence and coincidences are exactly what meaning is made of.

So the number to keep is not how often two words co-occur. It is **how much more often than you would expect by chance**. That is the next lesson, and it turns this from broken into working.

<br>

## Check yourself

```
python tools/run_lessons.py phases/03-words-that-know-what-they-mean/02-the-company-a-word-keeps
```

<br>

## Going further

Optional, and there is no check for it.

Change `WINDOW` from 4 to 1 and re-run. With a window of one you are asking which words appear immediately beside each other, and the neighbours drift towards words that play the same grammatical role rather than words about the same topic. The window is the dial between "behaves like" and "is about".

<br>

## What you learned

- A word can be represented by the company it keeps, an idea from 1957.
- A window turns a corpus into one profile per word.
- Cosine compares direction rather than size, and is used far beyond words.
- Raw counts fail, because common words are common everywhere and drown everything.
- Real signal was present and outranked, which is a weighting problem rather than a method problem.
- What matters is not how often two words appear together, but how much more often than chance.

**Next:** [3. Surprise is the signal](../03-surprise-is-the-signal/), where dividing by chance makes the meaning appear.
