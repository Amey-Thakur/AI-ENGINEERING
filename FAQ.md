<!--
File: FAQ.md
Purpose: Answer the objections a reader actually has, including the awkward ones.
Description: Written to be read by somebody deciding whether to spend a weekend
  on this. Every answer that makes a claim about the course cites the lesson
  that supports it, and the answers to "is this enough" and "where are
  transformers" say no rather than dressing it up.
License: MIT
Author: Amey Thakur (https://github.com/Amey-Thakur)
-->

# Questions

<br>

## Why is there no PyTorch, NumPy or scikit-learn?

Because a course that installs something has handed its lifespan to somebody else. The popular alternatives stopped working that way: a package was renamed, a dataset was withdrawn, a version was yanked, an install needed a compiler that was not there, and a reader on their first day met an error that had nothing to do with what they came to learn.

The standard library is the one dependency that arrives with Python and cannot be withdrawn. [`tools/check_imports.py`](tools/check_imports.py) enforces it across all 45 lessons.

It also changes what you learn. `model.fit()` teaches you an API. Writing the weighted sum, the sigmoid, the loss and the backward pass teaches you what the API does, and [phase 2 lesson 4](phases/02-a-network-you-wrote-yourself/04-backpropagation/) has you check your gradients against nudging the weights, which is the exercise that makes autodiff stop being magic.

You should absolutely use those libraries afterwards. You will use them better.

<br>

## Where are transformers, attention and LLMs?

Attention is here, in [phase 9](phases/09-attention-and-the-block/), which is being written now. You build one head and its backward pass by hand, and it clears a ceiling that no n-gram of any order can reach on the corpus.

A full transformer is not here. Phase 9 ends at the block rather than at a stack of them, and that is worth being straight about. Two reasons for it:

**The course goes toward engineering, not deeper modelling.** After phase 4 it turns to retrieval, tools, measurement and shipping, which is where most of the work actually is on most jobs. Phases 5 to 8 are about a system that has a model in it, not about the model.

**The corpus is 2,019 words, and that is a real constraint on what a bigger architecture could show.** [Phase 3 lesson 5](phases/03-words-that-know-what-they-mean/05-does-it-help/) measured meaning-based search at zero on paraphrases and the reason was data volume, not method. Attention on this corpus would run, and it would demonstrate the mechanism, and it would not beat the bigram, so the lesson would have to be honest about teaching a shape rather than a result.

Phase 9 earns its place the same way everything else did, by measuring something: the bigram is capped at exactly half on that corpus and one head reaches 16 of 20 on sentences it was not trained on, which luck alone produces 0.59% of the time. What it does not do is stack blocks and claim the result resembles a language model anybody ships.

<br>

## Is this enough to get a job?

No, and no single course is.

What it gives you is the half that interviews and job descriptions do not mention and teams complain about constantly: you will be able to say what a number means, whether a difference is real, what an empty function scores on the same task, and what happens when the corpus is missing. [Phase 7](phases/07-measuring-whether-any-of-it-works/) is that, and it is not in most curricula at all.

What it does not give you: a framework you can list, distributed training, GPUs, production infrastructure, or any transformer experience. Take it as the part that makes the rest make sense.

<br>

## Is 217 sentences and 60 messages too small to be real?

The datasets are small so that every lesson finishes in under a second on any machine and you can read the whole input. That is a teaching decision and it has a cost, which the course states rather than hides.

The cost is measured, not asserted. [Phase 7 lesson 1](phases/07-measuring-whether-any-of-it-works/01-the-number-has-error-bars/) puts a confidence interval on every score in the course and finds most of them establish very little: twenty examples pins a mid-range accuracy to about plus or minus twenty points, and every comparative number in phases 1 to 3 has an interval overlapping every other one.

So the datasets are too small to prove which method is better, and the course says so in a lesson rather than in a footnote. They are the right size to show you what each method does, which is the job.

<br>

## Why does the course keep saying its own lessons were wrong?

Because they were, and because finding that out is the skill.

[Phase 7 lesson 3](phases/07-measuring-whether-any-of-it-works/03-the-baseline-you-forgot/) measures phase 3's word-vector classifier against answering the same way every time and finds it one message better out of twenty, which a coin manages 41% of the time. [Phase 7 lesson 2](phases/07-measuring-whether-any-of-it-works/02-is-the-difference-real/) cannot distinguish the finished agent from one with its entire retrieval half deleted. [Phase 6 lesson 4](phases/06-tools-and-agents/04-a-loop-that-can-stop/) proves its own retry loop was incapable of working before it was written.

A course that only reported its successes would be teaching the opposite of what phases 7 and 8 are about. If a measurement in here contradicts an earlier lesson, the measurement stays and the earlier lesson gets a link to it.

<br>

## How long does it take?

Between two and five hours per phase, and **thirty-three hours in total** by the estimates printed at the top of each phase. Phase 0 is the shortest at two hours, and can be skipped entirely if you are comfortable with a terminal, Git and virtual environments.

There is no order requirement beyond the obvious: each phase builds on the one before it, and each lesson says at the top what it needs.

<br>

## Do I need to be good at mathematics?

No, and there is deliberately no mathematics phase.

Mathematics arrives in the lesson where something breaks without it, which is the only time anybody has wanted to learn it. You meet a weighted sum when your program needs one. You meet a gradient as rise over run, measured by nudging a weight and looking at the loss, before anything mentions calculus. You meet a cosine when raw counts fail to compare two word profiles.

If you can read a `for` loop you can do the whole course.

<br>

## Do I need to know Python?

[Phase 0](phases/00-your-machine/) assumes nothing: it starts with opening a terminal and ends with you having made a commit. Phase 1 assumes you can run a file.

You will not learn Python *from* this course, though, and it is not trying to. If you have never written a loop or a function, spend a few hours on any introduction first and come back.

<br>

## What if I get stuck on a lesson?

Every lesson has a `check.py` that says what is wrong in one line and what to do about it, rather than printing a diff. And every lesson has `solve.py`, the worked solution, written to be read.

Reading `solve.py` when stuck is not cheating. It is a considerably better use of an evening than an hour of guessing, and the lesson's README explains what the solution does and why.

<br>

## Is there a certificate?

There is a **record of completion**, and the distinction is the point.

```bash
python tools/certificate.py --name "Your Name"
```

It runs all 45 lessons before it draws anything and refuses if one fails. There is no flag to skip that. What it then attests to is narrow and checkable: on this date, at this commit, every check in this course passed on your machine. It prints the command to re-verify that on its own face.

It does not say you are good at this, and it does not say anybody assessed you, because neither would be true. Most course certificates assert exactly those two things and no reader can check either.

Running it from your own fork's Actions tab is worth more than running it locally, because the log is public, timestamped, and not editable by the person it is about.

<br>

## Can I use this to teach a class or run a study group?

Yes. MIT licensed, and there is nothing to install or provision, which is usually the part that kills a workshop. Thirty people on thirty different laptops with no network will all get identical output, and [`tools/check_determinism.py`](tools/check_determinism.py) exists to keep that true.

If you do, [open an issue](https://github.com/Amey-Thakur/AI-ENGINEERING/issues) and say how it went. The lessons that confuse a room are the ones worth rewriting.

<br>

## How do I know the material still works?

Because it is checked rather than promised, and you can run the checks yourself:

```bash
python tools/run_lessons.py && python tools/check_output.py && python tools/check_imports.py && python tools/check_determinism.py
```

Every solution and check runs on Linux, macOS and Windows on every change and again nightly. Every number printed in a lesson is compared against what the code actually prints, so no figure in the material is typed by hand. Nothing outside the standard library is imported anywhere. Every solution is run under three different string hash seeds and must print the same thing.

The five guarantees are five programs in [`tools/`](tools/), not four paragraphs in a contributing guide.

<br>

## Was this written by AI?

Parts of the material were drafted with AI assistance, and every number in it was produced by running the code rather than by a model writing a number that looked right. That distinction is the whole point of [`tools/check_output.py`](tools/check_output.py): the printed output in a lesson is mechanically compared against the real output, so a plausible-looking figure cannot survive in the repository.

Several lessons exist because a claim was checked and turned out to be false. [Phase 1 lesson 5](phases/01-teach-it-to-tell-two-things-apart/05-when-it-breaks/) reports a fix that makes the system worse, because measuring it showed that it does.

<br>

## Can I contribute?

Yes. [CONTRIBUTING.md](.github/CONTRIBUTING.md) has the full contract, and it is short: a lesson is accepted when it teaches one thing, its solution runs, its check explains itself on failure, and all five guarantees hold.

The most useful contribution is not a new lesson. It is a measurement that contradicts one that is already in here.

<br>

## Why is it called AI engineering rather than machine learning?

Because more than half of it is not about models. Phases 5 through 8 are retrieval, tool use, measurement, cost, failure and access control, and those are the parts that decide whether something works for anybody other than its author.

The course does build a classifier, a network, word vectors and a language model, all from nothing. It just does not stop there, and the name reflects where it spends its time.
