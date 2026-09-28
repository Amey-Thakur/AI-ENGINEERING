<!--
File: GLOSSARY.md
Purpose: Map the plain words this course uses onto the words the field uses.
Description: The lessons deliberately avoid jargon, which is good for learning
  and bad for the afternoon you first open a paper or a job description. This
  file is the bridge. Every row names the lesson where the idea is built, so
  the definition is never the only thing you have.
License: MIT
Author: Amey Thakur (https://github.com/Amey-Thakur)
-->

# Glossary

This course teaches the ideas before it teaches their names, and in several places it never uses the standard name at all. Phase 5 measures *found-by-k* and *average reciprocal place*. The literature calls those **recall@k** and **mean reciprocal rank**. Phase 3 spends a lesson on *the company a word keeps*, which is the **distributional hypothesis**. Phase 4 decides when to stop training by holding out data, which is **early stopping**.

That is a deliberate choice: a name learned before the thing it names is a word you can repeat and cannot use. But it leaves a gap, and this file closes it.

**Every row links to the lesson where you built the thing.** A definition you have already implemented reads differently from one you have not, and you will have implemented all of these.

<br>

> [!TIP]
> Read this after a phase, not before. The whole design of the course is that
> the idea arrives first and the vocabulary arrives second, and reading the
> vocabulary first gives it nothing to attach to.

<br>

## Phase 0. Your machine

| In this course | Also called | What it is |
| --- | --- | --- |
| [A window you type into](phases/00-your-machine/01-the-terminal/) | Terminal, shell, command line, REPL | The program that runs your typed commands. `bash` and `zsh` on Linux and macOS, PowerShell on Windows. |
| [Where a file actually is](phases/00-your-machine/02-files-and-paths/) | Absolute and relative paths, working directory | The difference between naming a file from the root of the disk and naming it from where you happen to be standing. |
| [A copy of Python that is only this project's](phases/00-your-machine/04-an-isolated-environment/) | Virtual environment, `venv`, dependency isolation | A private directory of packages, so two projects can want two versions of the same thing. |
| [Saving what you did](phases/00-your-machine/05-git-and-your-copy/) | Version control, commit, repository, fork | A record of every change, and the ability to return to any of them. |

<br>

## Phase 1. Teach it to tell two things apart

| In this course | Also called | What it is |
| --- | --- | --- |
| [Splitting on spaces](phases/01-teach-it-to-tell-two-things-apart/01-words-into-numbers/) | Tokenisation, tokeniser | Cutting text into the units a model counts. `.split()` is the naive one, and the lesson names four things it gets wrong. |
| [Counting which words appear](phases/01-teach-it-to-tell-two-things-apart/01-words-into-numbers/) | Bag of words, feature vector, feature extraction | Representing a document as counts of its words, discarding order entirely. |
| [A rule you wrote by hand](phases/01-teach-it-to-tell-two-things-apart/02-a-rule-by-hand/) | Heuristic, rule-based baseline | A human-written decision rule. In this course it scored 18 of 20 and beat everything learned for three phases. |
| [Letting it find the numbers](phases/01-teach-it-to-tell-two-things-apart/03-let-it-learn/) | Perceptron, supervised learning, weights, bias | The 1958 algorithm that adjusts a weight per feature whenever it gets an example wrong. |
| [Messages it has never seen](phases/01-teach-it-to-tell-two-things-apart/04-tell-the-truth/) | Held-out set, test set, generalisation | Data kept back from training, because a score on data you fitted to is not a score. |
| [Getting it right for the wrong reason](phases/01-teach-it-to-tell-two-things-apart/05-when-it-breaks/) | Overfitting, error analysis, spurious correlation | Learning a pattern that holds in your sample and not in the world. |

<br>

## Phase 2. A network you wrote yourself

| In this course | Also called | What it is |
| --- | --- | --- |
| [The thing one line cannot do](phases/02-a-network-you-wrote-yourself/01-the-thing-one-line-cannot-do/) | Linear separability, the XOR problem | A dataset no single straight cut can divide, which is why one layer is not enough. |
| [A second layer](phases/02-a-network-you-wrote-yourself/02-a-second-layer/) | Hidden layer, multilayer perceptron, MLP, feedforward network | Stacking a transformation before the decision, so the decision can be made in a space where the data is separable. |
| [A curve instead of a cliff](phases/02-a-network-you-wrote-yourself/03-how-wrong-and-which-direction/) | Sigmoid, logistic function, activation function | A smooth threshold. A hard one has no useful slope, so nothing can be tuned through it. |
| [How wrong it is, as one number](phases/02-a-network-you-wrote-yourself/03-how-wrong-and-which-direction/) | Loss function, objective, cost | The single quantity training tries to reduce. |
| [Rise over run, measured by nudging](phases/02-a-network-you-wrote-yourself/03-how-wrong-and-which-direction/) | Gradient, finite differences, numerical gradient | Which way to move each weight, found by changing it slightly and looking, with no calculus. |
| [Working out every nudge at once](phases/02-a-network-you-wrote-yourself/04-backpropagation/) | Backpropagation, the chain rule, reverse-mode autodiff | Computing all the gradients in one backward pass instead of one forward pass per weight. |
| [Checking the fast way agrees with the slow way](phases/02-a-network-you-wrote-yourself/04-backpropagation/) | Gradient checking | Comparing backpropagation against nudging, which is how you find the sign error you would otherwise ship. |
| [How big a step to take](phases/02-a-network-you-wrote-yourself/05-train-it-on-the-messages/) | Learning rate, step size, hyperparameter | The multiplier on each update, with a wrong answer in both directions. |

<br>

## Phase 3. Words that know what they mean

| In this course | Also called | What it is |
| --- | --- | --- |
| [A word the model has never met](phases/03-words-that-know-what-they-mean/01-the-vocabulary-wall/) | Out-of-vocabulary, OOV, the vocabulary problem | A word absent from training, which a count-based model can say nothing about. |
| [The company a word keeps](phases/03-words-that-know-what-they-mean/02-the-company-a-word-keeps/) | The distributional hypothesis, Firth 1957 | The idea that a word's meaning can be read off the words that surround it. |
| [A profile per word](phases/03-words-that-know-what-they-mean/02-the-company-a-word-keeps/) | Co-occurrence matrix, context window | A count of how often each word appears near each other word. |
| [Comparing direction rather than size](phases/03-words-that-know-what-they-mean/02-the-company-a-word-keeps/) | Cosine similarity | The standard way to compare two vectors when their magnitude is not the point. |
| [How much more often than chance](phases/03-words-that-know-what-they-mean/03-surprise-is-the-signal/) | Pointwise mutual information, PMI, PPMI | Dividing a co-occurrence count by what chance alone would produce, which is what makes meaning appear. |
| [Fewer numbers that say more](phases/03-words-that-know-what-they-mean/04-fewer-numbers-that-say-more/) | Dimensionality reduction, SVD, latent semantic analysis, embeddings | Compressing a sparse profile of hundreds of numbers into a dense handful that carry the same facts. |
| [Multiplying and normalising until it settles](phases/03-words-that-know-what-they-mean/04-fewer-numbers-that-say-more/) | Power iteration, eigenvector | Finding the direction the data varies along most, with multiplication and nothing else. |
| [Does it help](phases/03-words-that-know-what-they-mean/05-does-it-help/) | Extrinsic evaluation, downstream task | Judging a representation by whether it improves the job you actually have, rather than by how good its neighbours look. |

<br>

## Phase 4. A language model you wrote yourself

| In this course | Also called | What it is |
| --- | --- | --- |
| [Predicting the next word](phases/04-a-language-model-you-wrote-yourself/01-predicting-the-next-word/) | Language model, n-gram model, bigram, the Markov assumption | Assigning a probability to what comes next, given what came before. |
| [Never say never](phases/04-a-language-model-you-wrote-yourself/02-never-say-never/) | Smoothing, add-k, Laplace smoothing, interpolation, backoff | Giving unseen pairs a floor, because one impossible word makes a model infinitely bad. |
| [An effective vocabulary size](phases/04-a-language-model-you-wrote-yourself/02-never-say-never/) | Perplexity, held-out likelihood | How much probability the model put on what actually happened, read as a number of equally likely options. |
| [Making it talk](phases/04-a-language-model-you-wrote-yourself/03-making-it-talk/) | Decoding, greedy decoding, sampling, temperature, top-k | Turning a distribution over next words into text, and the dial that trades safety for variety. |
| [Turning scores into probabilities](phases/04-a-language-model-you-wrote-yourself/04-a-model-that-generalises/) | Softmax, cross-entropy loss, the log-sum-exp trick | The function that normalises arbitrary scores, and the subtraction that stops it overflowing. |
| [Deciding when to stop](phases/04-a-language-model-you-wrote-yourself/04-a-model-that-generalises/) | Early stopping, validation set, the three-way split | Using a third slice of data to choose when training has gone far enough, because that choice needs its own data. |
| [What it knows](phases/04-a-language-model-you-wrote-yourself/05-what-it-knows/) | Parametric knowledge, memorisation | What a model can state from its weights alone, which turns out to be far less than it has read. |

<br>

## Phase 5. Finding the right thing to say

| In this course | Also called | What it is |
| --- | --- | --- |
| [It has read it and cannot recall it](phases/05-finding-the-right-thing-to-say/01-it-has-read-it-and-cannot-recall-it/) | Closed-book and open-book question answering, knowledge-intensive tasks | Answering from the weights against answering from a document you fetched. The gap between them is the reason retrieval exists. |
| [Finding it by the words](phases/05-finding-the-right-thing-to-say/02-finding-it-by-the-words/) | Lexical retrieval, keyword search, sparse retrieval, BM25, TF-IDF | Ranking documents by the words they share with the question. |
| [Finding it by meaning](phases/05-finding-the-right-thing-to-say/03-finding-it-by-meaning/) | Semantic search, dense retrieval, vector search, embedding search | Ranking by vector similarity instead of shared words. Measured here at zero on paraphrases. |
| [Found-by-k](phases/05-finding-the-right-thing-to-say/04-measuring-search-properly/) | Recall@k, hit rate at k | Whether the right document is anywhere in the top k, rather than only at the top. |
| [Average reciprocal place](phases/05-finding-the-right-thing-to-say/04-measuring-search-properly/) | Mean reciprocal rank, MRR | One over the position of the right answer, averaged. Rewards putting it first without ignoring second. |
| [Retrieve, then answer](phases/05-finding-the-right-thing-to-say/05-retrieve-then-answer/) | Retrieval-augmented generation, RAG, grounding | Fetching a passage and having a model answer from it, rather than from memory. |
| [The number nothing downstream can raise](phases/05-finding-the-right-thing-to-say/05-retrieve-then-answer/) | The retrieval ceiling | If search finds the right passage 75% of the time, the honest maximum for the whole system is 75%. |

<br>

## Phase 6. Tools and agents

| In this course | Also called | What it is |
| --- | --- | --- |
| [A function the system can call](phases/06-tools-and-agents/01-what-a-model-cannot-do/) | Tool use, function calling, tool calling | Letting the system run code instead of predicting what the code would have printed. |
| [Choosing the tool](phases/06-tools-and-agents/02-choosing-the-tool/) | Routing, intent classification, tool selection, dispatch | Working out which function a request needs, which is harder than any of the functions. |
| [A tool that says no](phases/06-tools-and-agents/03-when-it-chooses-wrong/) | Input validation, preconditions, guardrails, graceful refusal | Writing down what a tool requires, so a misroute is declined rather than answered. |
| [A loop that can stop](phases/06-tools-and-agents/04-a-loop-that-can-stop/) | Agent loop, ReAct, agentic loop, the control loop | Call a tool, read the result, decide whether to go again. This is what an agent is. |
| [Running out of budget](phases/06-tools-and-agents/04-a-loop-that-can-stop/) | Step cap, max iterations, iteration limit | The bound that decides whether you or the input controls what a request costs. |
| [Questions with no answer](phases/06-tools-and-agents/04-a-loop-that-can-stop/) | Unanswerable questions, abstention, calibrated refusal | The examples no benchmark contains, and the only ones that can measure whether a system can say it does not know. |
| [Measuring an agent](phases/06-tools-and-agents/05-measuring-an-agent/) | Cost-sensitive evaluation, utility-weighted scoring, the precision and recall tradeoff | Scoring several outcomes at once rather than one, and pricing a wrong answer against a right one so that two systems can be ranked at all. |

<br>

## Phase 7. Measuring whether any of it works

| In this course | Also called | What it is |
| --- | --- | --- |
| [The number has error bars](phases/07-measuring-whether-any-of-it-works/01-the-number-has-error-bars/) | Confidence interval, Clopper-Pearson interval, exact binomial interval | The set of true rates that could plausibly have produced your score. Twenty examples buys about twenty points. |
| [Is the difference real](phases/07-measuring-whether-any-of-it-works/02-is-the-difference-real/) | McNemar's test, paired significance test, p-value | The right test when two systems ran on the same examples, and far more powerful than comparing intervals. |
| [Not enough examples to tell](phases/07-measuring-whether-any-of-it-works/02-is-the-difference-real/) | Statistical power, type II error | Why "no significant difference" and "no difference" are different claims. |
| [What an empty function scores](phases/07-measuring-whether-any-of-it-works/03-the-baseline-you-forgot/) | Baseline, majority-class baseline, trivial baseline | The floor any result has to clear before it means anything. On an unbalanced problem it can be above 90%. |
| [Deleting a part to see if it mattered](phases/07-measuring-whether-any-of-it-works/03-the-baseline-you-forgot/) | Ablation, ablation study | Removing one component and remeasuring. This course's retrieval half did not survive the test. |
| [The test set you keep looking at](phases/07-measuring-whether-any-of-it-works/04-the-test-set-you-keep-looking-at/) | Test-set leakage, hyperparameter overfitting, selection bias, optimism | Tuning against the data you then report from, which inflates the number even when the choice is right. |
| [A test you can actually run](phases/07-measuring-whether-any-of-it-works/05-a-test-you-can-actually-run/) | Regression test, snapshot test, golden file, expectations file | A record of what the system currently does, failures included, so a change reports which examples moved. |

<br>

## Phase 8. Shipping

| In this course | Also called | What it is |
| --- | --- | --- |
| [Counting the work](phases/08-shipping-cost-latency-failure-safety/01-counting-the-work/) | Cost accounting, token accounting, unit economics | Measuring work in units that do not depend on your laptop: tokens, rows examined, documents scanned. |
| [The dearest question](phases/08-shipping-cost-latency-failure-safety/01-counting-the-work/) | Tail latency, p95, p99, the long tail | What the unlucky request costs. The average describes a request that often does not exist. |
| [A dictionary the other way round](phases/08-shipping-cost-latency-failure-safety/02-when-the-corpus-grows/) | Inverted index, postings list | Mapping each word to the documents holding it, so a query costs its own words rather than the whole corpus. |
| [Words that are nearly everywhere](phases/08-shipping-cost-latency-failure-safety/02-when-the-corpus-grows/) | Stop words, document frequency, IDF | The commonest words, whose removal is a speedup and a change to the system rather than an optimisation. |
| [Failing by refusing](phases/08-shipping-cost-latency-failure-safety/03-when-something-fails/) | Graceful degradation, fail-open, fail-closed, fallback | What a system does when a component is unavailable, and why a fallback is only safe if it can tell it is being misused. |
| [The number that noticed](phases/08-shipping-cost-latency-failure-safety/03-when-something-fails/) | Leading indicator, observability, score distribution monitoring | A signal that moves the moment something breaks, needs no labels, and is free on every request. |
| [What it must not say](phases/08-shipping-cost-latency-failure-safety/04-what-it-must-not-say/) | Data leakage, document-level access control, permission-aware retrieval | Keeping a boundary in a system whose scoring function has no concept of who is asking. |
| [The thing you ship](phases/08-shipping-cost-latency-failure-safety/05-the-thing-you-ship/) | Model card, system card, release criteria, evaluation report | The page of sourced numbers you hand somebody, including the section saying what the numbers do not establish. |

<br>

## Words this course does not use, and why

A few terms you will meet constantly are absent from the lessons on purpose.

**Artificial intelligence.** The course says what a thing does instead. Nothing in it becomes clearer for being called intelligent.

**Neural.** Phase 2 builds a multilayer perceptron and calls it a network of weighted sums, because that is what it is, and the biological word imports a claim the mathematics does not make.

**Hallucination.** Phase 6 says *said something false* and counts them. The usual word suggests a malfunction, when producing a fluent wrong answer is the system working exactly as built.

**Reasoning.** Phase 6 builds a loop that calls a tool and decides whether to go again, and describes it in those words.

**Prompt engineering.** No lesson needs it, because no lesson calls a hosted model. The habits it stands in for, measuring a change and keeping the examples that showed the problem, are phases 7 and 8.

<br>

## Where to go after this

Every row above is a search term. The course gave you the thing; these give you the literature.

- **Retrieval**: start at BM25, then Robertson and Zaragoza's survey of the probabilistic relevance framework, which is the method phase 5 lesson 2 measured against.
- **Evaluation**: Clopper-Pearson (1934) for phase 7 lesson 1, McNemar (1947) for lesson 2. Both are short papers and both are readable.
- **Distributional semantics**: Firth (1957) for the sentence phase 3 is built on, then PPMI and SVD.
- **Agents**: read the tool-calling documentation of any provider with phase 6 lesson 3 in mind, and notice how much of it is about what a tool does with input it was never meant to see.

<br>

---

Every entry links to a lesson in this repository, and [`tools/check_glossary.py`](tools/check_glossary.py) fails if one of those links stops resolving.
