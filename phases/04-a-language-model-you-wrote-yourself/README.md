# Phase 4. A language model you wrote yourself

**Five lessons. About five hours. Still nothing installed.**

Phase 3 ended with a representation that was good and a result that was bad, because averaging word vectors threw away the order the task depended on. This phase makes order the thing the model is built around.

By the end you will have written a language model twice: once by counting, and once by learning. The second beats the first, and it is the first time in this course that anything learned has beaten the simpler thing it was measured against.

<br>

## The lessons

| # | Lesson | The idea underneath it |
| --- | --- | --- |
| 1 | [Predicting the next word](01-predicting-the-next-word/) | The one ability every language model has |
| 2 | [Never say never](02-never-say-never/) | Perplexity, and why zero probability breaks everything |
| 3 | [Making it talk](03-making-it-talk/) | Generation, temperature, and a memory one word long |
| 4 | [A model that generalises](04-a-model-that-generalises/) | Sharing evidence between similar words, and a third data split |
| 5 | [What it knows](05-what-it-knows/) | Structure nobody specified, learned as a side effect |

<br>

## What you will have built

A bigram model with two kinds of smoothing, measured with perplexity. A text generator with greedy decoding and temperature sampling, both of which are exactly what a model API gives you. And a neural language model with learned word vectors, softmax, cross entropy and early stopping chosen on a validation split.

All of it in plain Python, on 217 sentences that live in the repository.

<br>

## Three results worth carrying forward

**77% of held back word pairs never occur in training.** That is a fact about language, not about this corpus. Counting can only describe what has happened, and language is mostly about what has not.

**The best counting model ignores context entirely.** Trusting the previous word more made perplexity steadily worse, from 258 to 980. When evidence is thin, the model that assumes less wins, which is the same finding as phase 1.

**The neural model beat counting by 12%** on a test set nothing had tuned against, because it can share what it learns between similar words. That is the specific advantage, and naming it matters more than the number.

> [!IMPORTANT]
> This phase introduces the three way split: train, validation, test. Anything
> you tune, choose or compare using a set has spent that set, and "when to
> stop training" is a choice like any other.

<br>

## Check the phase

```
python tools/run_lessons.py phases/04-a-language-model-you-wrote-yourself
```

Two of these lessons train a model twice, once in the solution and once in the check, so the phase takes about a minute.

**Next:** [Phase 5](../05-finding-the-right-thing-to-say/), where a model stops trying to hold everything in its weights and learns to look things up.
