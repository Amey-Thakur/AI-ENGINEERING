# 2. Never say never

> **Last lesson's model says that 77% of real sentences are impossible.**
>
> Not unlikely. Impossible, with probability exactly zero. This lesson makes
> that measurable, fixes it, and then produces a result that should genuinely
> annoy you.

**You will:** measure a language model properly, watch the measurement come out infinite, and fix it two different ways.

**You need:** [lesson 1](../01-predicting-the-next-word/).

<br>

## Measuring a language model

Accuracy is the wrong tool. A model that puts 40% on the right word and a model that puts 4% on it both score zero if a third word wins, and those are not equally good models.

What you want is: **how much probability did it put on what actually happened?**

```python
carried += log(chance)
...
return exp(-carried / counted)
```

That is **perplexity**. Multiply the probabilities of every word that actually occurred, take the average, and invert it. Logs are used because multiplying four hundred small numbers underflows to zero on any real computer.

Read the number like this: *the model was as uncertain as if it were choosing uniformly between this many words at every step*. Lower is better. A model that is never surprised scores 1.

> [!TIP]
> The useful anchor is your vocabulary size. There are 610 tokens here, so a
> model that knows nothing and guesses uniformly scores 610. Any real number
> should be read against that, exactly like the baseline in phase 1.

<br>

## And it comes out infinite

One word with probability zero makes the whole product zero, so the perplexity is infinite. That is not a quirk of the arithmetic, it is the arithmetic correctly reporting that your model considers a sentence a human wrote to be impossible.

An unusable model, and an unmeasurable one. Both problems have the same single cause.

<br>

## Fix one: give everything a little

```python
return (seen + amount) / (context.get(word, 0) + amount * vocabulary)
```

Pretend you saw every possible pair slightly more often than you did. Add 1 to every count, or 0.1, or 0.01. Nothing is zero any more, so nothing is impossible.

This is **add-k smoothing**, and `k` is a dial. Too much and real evidence gets drowned in imaginary counts. Too little and rare pairs stay nearly impossible.

## Fix two: fall back on the simpler model

```python
return weight * bigram + (1 - weight) * unigram
```

When the pair is unfamiliar, ask an easier question: how common is this word *at all*, ignoring context? Mix the two answers.

This is **interpolation**, and `weight` says how much to trust the context. At 1.0 you are back to the bigram. At 0.0 you have thrown the context away entirely.

<br>

## Your turn

Measure all eight models and write `.work/results.tsv`:

```
model      perplexity
none       inf
add 1      391.6660
mix 0.5    312.4863
```

<br>

## What the solution prints

<!-- output: solve.py -->
```text
610 words in the vocabulary, counting both markers
A model choosing uniformly would score 610.

  model                       perplexity
  none                     infinite   some real sentences are impossible
  add 1                       391.7
  add 0.1                     349.5
  add 0.01                    477.4
  mix 0                       257.7   ignores the previous word entirely
  mix 0.5                     312.5
  mix 0.8                     586.2
  mix 0.9                     980.4

Best: mix 0, at 257.7
```
<!-- end output -->

<br>

## The result you should not skip past

| Model | Perplexity |
| --- | --- |
| No smoothing | infinite |
| add 1 | 391.7 |
| add 0.1 | 349.5 |
| add 0.01 | 477.4 |
| **mix 0.0** | **257.7** |
| mix 0.5 | 312.5 |
| mix 0.8 | 586.2 |
| mix 0.9 | 980.4 |

**The best model ignores the previous word completely.**

`mix 0.0` uses no context at all. It says "the word *the* is common, so probably *the*", every single time, regardless of what came before. And it beats every model that actually looks at the preceding word.

Worse, the pattern is monotonic. Trusting the context more makes it steadily worse: 257.7, then 312.5, then 586.2, then 980.4.

<br>

## Why, and why it is not a mistake

With 180 sentences, a bigram has on average a handful of observations behind it. Most have one. A count of one is not a probability, it is an anecdote, and a model built on anecdotes is confidently wrong in 610 different directions.

The unigram model has far less information, and what it has, it actually has. It is right for the same reason the nine line rule in phase 1 keeps winning: **when evidence is thin, the model that assumes less wins.**

> [!IMPORTANT]
> This is not an argument that context is useless. Context is where nearly all
> the information in language is. It is an argument that you cannot use context
> by counting it, because contexts are too numerous to ever be counted enough.
>
> What is needed is a model that can *share* what it learns between similar
> contexts, so that seeing *the server restarted* teaches it something about
> *the database restarted*. Counting cannot do that. Phase 3 built exactly the
> thing that can.

<br>

## Check yourself

```
python tools/run_lessons.py phases/04-a-language-model-you-wrote-yourself/02-never-say-never
```

<br>

## Going further

Optional, and there is no check for it.

Train on all 217 sentences instead of 180 and measure again, then on 90. Watch where the best mixture sits each time. As data grows, trusting the context pays off more, and the optimum weight climbs. That curve is the honest answer to "should I use a more powerful model", and it is a measurement rather than an opinion.

<br>

## What you learned

- Perplexity measures how much probability a model put on what actually happened, and reads as an effective vocabulary size.
- One impossible word makes a model infinitely bad, correctly.
- Add-k smoothing gives every pair a floor, and k is a dial with a wrong answer in both directions.
- Interpolation falls back on a simpler model when the context is unfamiliar.
- On this corpus the best language model **uses no context at all**, and the more context it uses the worse it gets.
- Thin evidence rewards the model that assumes less, which is the same lesson as phase 1.

**Next:** [3. Making it talk](../03-making-it-talk/), where the model generates sentences and its limits become impossible to ignore.
