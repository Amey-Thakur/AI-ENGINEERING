# 1. It has read it and cannot recall it

> **Twenty questions. Every answer is a sentence inside the corpus the model
> trained on. It gets none of them.**
>
> Not because the information is missing. Because storing something in weights
> and being able to get it back are different problems, and only one of them
> was ever solved.

**You will:** ask a model twenty questions it should be able to answer, watch it fail all twenty, and see the shape of the fix.

**You need:** [phase 4](../../04-a-language-model-you-wrote-yourself/).

<br>

## The setup is deliberately unfair to the alternative

`questions.tsv` holds twenty questions, each paired with the sentence that answers it:

```
how long does the test suite take    the test suite takes twelve minutes to run
how often are credentials rotated    credentials in the vault are rotated every ninety days
```

Every one of those answers is in `corpus.txt`, and the model trains on all of it. There is no held back data here and no trick. The information is inside the thing you are asking.

<br>

## Asking it

Take the last word of the question the model has ever seen, and let it continue. Five attempts per question, and count it as recalled if the reply contains most of the answer's own words.

<br>

## Your turn

Ask all twenty and write `.work/results.tsv`:

```
measure              value
questions            20
answers_in_corpus    20
recalled_by_model    0
```

<br>

## What the solution prints

<!-- output: solve.py -->
```text
The model has read all 217 sentences, 2019 words.
Every one of the 20 answers is a sentence inside that corpus.

  asked:  how long does the test suite take
  model:  suite runs on the token is worse
  wanted: the test suite takes twelve minutes to run
  got it: no

  asked:  how often are credentials rotated
  model:  rotated 
  wanted: credentials in the vault are rotated every ninety days
  got it: no

  asked:  where are the credentials kept
  model:  credentials in the load balancer stopped sending traffic was approved by long meeting was locked
  wanted: the vault holds the credentials the service reads at startup
  got it: no

  asked:  how many users did the incident affect
  model:  incident 
  wanted: the incident lasted twenty minutes and affected four hundred users
  got it: no

Answers recalled in 5 attempts each: 0 of 20
```
<!-- end output -->

<br>

## Zero out of twenty

Read the second one. Asked how often credentials are rotated, the model replies `rotated` and stops. The sentence *credentials in the vault are rotated every ninety days* is in its training data. It has counted that sentence. It cannot produce it.

The third is worse, because it is fluent. Asked where credentials are kept, it produces *credentials in the load balancer stopped sending traffic was approved by long meeting was locked*. Confident, well formed at every pair, and entirely wrong.

> [!IMPORTANT]
> A model does not store sentences. It stores statistics about sentences,
> which is a lossy summary chosen to help with prediction. Specific facts are
> exactly what a summary like that throws away first: they are rare, they are
> arbitrary, and knowing that *twelve* follows *takes* helps with almost
> nothing else.
>
> This is what people are describing when a much larger model invents a
> citation or a version number. It is not lying and it is not broken. It is
> producing the most probable continuation, which is what it was built to do,
> and specific facts were never what it kept.

<br>

## The fix is almost insultingly simple

You have the corpus. It is sitting on disk, 217 sentences, in plain text.

Rather than asking the model to remember *the test suite takes twelve minutes to run*, **go and find that sentence**, then hand it over.

This is **retrieval**, and it is what the rest of this phase builds. The idea is so simple it is easy to miss how much it changes:

| Remembering | Looking up |
| --- | --- |
| The fact must survive training | The fact stays where it is |
| Updating means retraining | Updating means editing a file |
| No way to see where an answer came from | The source sentence is right there |
| Wrong answers are fluent and untraceable | Wrong answers point at what was retrieved |

> [!TIP]
> That third row is the one that matters most in practice. A system that can
> show you the sentence it used can be checked by a person. A system that
> cannot is asking for trust it has no way to earn.

<br>

## Check yourself

```
python tools/run_lessons.py phases/05-finding-the-right-thing-to-say/01-it-has-read-it-and-cannot-recall-it
```

The check verifies for itself that all twenty answers really are corpus sentences, before it believes anything about the failure.

<br>

## Going further

Optional, and there is no check for it.

Raise `TRIES` from 5 to 500 and see whether brute force helps. It does not, and the reason is worth understanding: the model is not failing to find a rare path to the right answer, it is sampling from a distribution that does not concentrate on that answer at all. More samples from the wrong distribution give you more wrong answers, faster.

<br>

## What you learned

- A model stores statistics about text, not the text, and specific facts are what that summary discards first.
- Having read something is not the same as being able to recall it.
- Fluent and wrong is the characteristic failure, and it looks exactly like fluent and right.
- Retrieval keeps facts where they are instead of pressing them into weights.
- Facts that stay in a file can be updated, and cited, and checked by a person.

**Next:** [2. Finding it by the words](../02-finding-it-by-the-words/), where you build the simplest search that works and find out how far it gets.
