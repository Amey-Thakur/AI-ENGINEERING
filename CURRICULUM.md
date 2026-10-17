<div align="center">

# The curriculum

### Fifty lessons · Ten phases · About thirty-seven hours · Nothing installed

[![Back to the course](https://img.shields.io/badge/Back%20to-the%20course-1DE9B6.svg)](README.md)
[![Glossary](https://img.shields.io/badge/Read-the%20glossary-0969DA.svg)](GLOSSARY.md)

</div>

<br>

Every lesson on one page, in order, with what you do in each. Each one is a
directory holding a `README.md`, a `solve.py` you write, a `check.py` that
marks it, and the data it needs. Nothing is installed at any point.

**Tick them off as you go.** On [the website](https://amey-thakur.github.io/AI-ENGINEERING/curriculum/)
the boxes remember where you are, in your own browser and nowhere else.

<br>

## [Phase 0. Your machine](phases/00-your-machine/)

*Five lessons. About two hours. Nothing installed beforehand.*

- [ ] **[1. The terminal](phases/00-your-machine/01-the-terminal/)** &nbsp;&middot;&nbsp; open a terminal, run three commands, read what comes back, send the answer to a file, and install Python.
- [ ] **[2. Files and paths](phases/00-your-machine/02-files-and-paths/)** &nbsp;&middot;&nbsp; read a path the way the computer reads it, move around with cd, and make a folder inside a folder.
- [ ] **[3. Your first program](phases/00-your-machine/03-your-first-program/)** &nbsp;&middot;&nbsp; write a file, make the computer run it, break it on purpose, and read the error properly.
- [ ] **[4. An isolated environment](phases/00-your-machine/04-an-isolated-environment/)** &nbsp;&middot;&nbsp; understand why installing a library can break a project you were not touching, and build the wall that prevents it.
- [ ] **[5. Git and your copy](phases/00-your-machine/05-git-and-your-copy/)** &nbsp;&middot;&nbsp; record a version of a folder, see the record, and understand what forking this course actually does.

<br>

## [Phase 1. Teach it to tell two things apart](phases/01-teach-it-to-tell-two-things-apart/)

*Five lessons. About four hours. Nothing installed.*

- [ ] **[1. Words into numbers](phases/01-teach-it-to-tell-two-things-apart/01-words-into-numbers/)** &nbsp;&middot;&nbsp; read a data file, turn sentences into counts, and find out where the signal in a problem actually lives.
- [ ] **[2. A rule by hand](phases/01-teach-it-to-tell-two-things-apart/02-a-rule-by-hand/)** &nbsp;&middot;&nbsp; write a rule, measure how often it is right, and learn why that number on its own can be a lie.
- [ ] **[3. Let it learn](phases/01-teach-it-to-tell-two-things-apart/03-let-it-learn/)** &nbsp;&middot;&nbsp; write a learning loop, watch the mistakes fall, and see the program rediscover what you worked out by hand.
- [ ] **[4. Tell the truth](phases/01-teach-it-to-tell-two-things-apart/04-tell-the-truth/)** &nbsp;&middot;&nbsp; hold data back, score on it, and watch a model you were proud of lose a quarter of its accuracy.
- [ ] **[5. When it breaks](phases/01-teach-it-to-tell-two-things-apart/05-when-it-breaks/)** &nbsp;&middot;&nbsp; read every mistake your model makes, one at a time, and find that they are not all the same mistake.

<br>

## [Phase 2. A network you wrote yourself](phases/02-a-network-you-wrote-yourself/)

*Five lessons. About four hours. Still nothing installed.*

- [ ] **[1. The thing one line cannot do](phases/02-a-network-you-wrote-yourself/01-the-thing-one-line-cannot-do/)** &nbsp;&middot;&nbsp; prove, by exhausting every possibility, that there is a problem no single weighted sum can solve.
- [ ] **[2. A second layer](phases/02-a-network-you-wrote-yourself/02-a-second-layer/)** &nbsp;&middot;&nbsp; build a two layer network by hand, solve the problem lesson 1 proved was impossible, and see exactly why it works.
- [ ] **[3. How wrong, and in which direction](phases/02-a-network-you-wrote-yourself/03-how-wrong-and-which-direction/)** &nbsp;&middot;&nbsp; replace the threshold with a curve, measure wrongness as one number, and find the slope of that number against every weight in the network.
- [ ] **[4. Backpropagation](phases/02-a-network-you-wrote-yourself/04-backpropagation/)** &nbsp;&middot;&nbsp; compute every gradient in one backward sweep, and check each one against the nudging you already trust.
- [ ] **[5. Train it on the messages](phases/02-a-network-you-wrote-yourself/05-train-it-on-the-messages/)** &nbsp;&middot;&nbsp; train the network on the phase 1 messages, score it honestly, and compare it against everything you have built.

<br>

## [Phase 3. Words that know what they mean](phases/03-words-that-know-what-they-mean/)

*Five lessons. About four hours. Still nothing installed.*

- [ ] **[1. The vocabulary wall](phases/03-words-that-know-what-they-mean/01-the-vocabulary-wall/)** &nbsp;&middot;&nbsp; measure how much of the vocabulary is missing, and then prove that the representation has no idea any two words are related.
- [ ] **[2. The company a word keeps](phases/03-words-that-know-what-they-mean/02-the-company-a-word-keeps/)** &nbsp;&middot;&nbsp; count which words appear near which, use those counts as meaning, and watch it fail in an instructive way.
- [ ] **[3. Surprise is the signal](phases/03-words-that-know-what-they-mean/03-surprise-is-the-signal/)** &nbsp;&middot;&nbsp; replace every count with how surprising it is, and watch meaning appear out of the same numbers.
- [ ] **[4. Fewer numbers that say more](phases/03-words-that-know-what-they-mean/04-fewer-numbers-that-say-more/)** &nbsp;&middot;&nbsp; squeeze every profile down to 24 numbers, and find that the words become closer to more meaningful than they were.
- [ ] **[5. Does it help?](phases/03-words-that-know-what-they-mean/05-does-it-help/)** &nbsp;&middot;&nbsp; put the vectors on the real problem, measure honestly, and diagnose a failure properly.

<br>

## [Phase 4. A language model you wrote yourself](phases/04-a-language-model-you-wrote-yourself/)

*Five lessons. About five hours. Still nothing installed.*

- [ ] **[1. Predicting the next word](phases/04-a-language-model-you-wrote-yourself/01-predicting-the-next-word/)** &nbsp;&middot;&nbsp; build a language model, watch it guess the next word, and measure how often it is right on sentences it has never seen.
- [ ] **[2. Never say never](phases/04-a-language-model-you-wrote-yourself/02-never-say-never/)** &nbsp;&middot;&nbsp; measure a language model properly, watch the measurement come out infinite, and fix it two different ways.
- [ ] **[3. Making it talk](phases/04-a-language-model-you-wrote-yourself/03-making-it-talk/)** &nbsp;&middot;&nbsp; generate sentences three ways, and see exactly what a memory of one word can and cannot do.
- [ ] **[4. A model that generalises](phases/04-a-language-model-you-wrote-yourself/04-a-model-that-generalises/)** &nbsp;&middot;&nbsp; train a language model on word vectors instead of counts, and get the first win of this entire course.
- [ ] **[5. What it knows](phases/04-a-language-model-you-wrote-yourself/05-what-it-knows/)** &nbsp;&middot;&nbsp; look inside the vectors a language model invented, and find structure nobody put there.

<br>

## [Phase 5. Finding the right thing to say](phases/05-finding-the-right-thing-to-say/)

*Five lessons. About four hours. Still nothing installed.*

- [ ] **[1. It has read it and cannot recall it](phases/05-finding-the-right-thing-to-say/01-it-has-read-it-and-cannot-recall-it/)** &nbsp;&middot;&nbsp; ask a model twenty questions it should be able to answer, watch it fail all twenty, and see the shape of the fix.
- [ ] **[2. Finding it by the words](phases/05-finding-the-right-thing-to-say/02-finding-it-by-the-words/)** &nbsp;&middot;&nbsp; build the simplest search that works, compare it against four more sophisticated ones, and find out which actually wins.
- [ ] **[3. Finding it by meaning](phases/05-finding-the-right-thing-to-say/03-finding-it-by-meaning/)** &nbsp;&middot;&nbsp; search by meaning instead of by words, on two sets of questions designed to tell the two approaches apart.
- [ ] **[4. Measuring search properly](phases/05-finding-the-right-thing-to-say/04-measuring-search-properly/)** &nbsp;&middot;&nbsp; score the same three searches several ways, and find that which one is best depends on the question you asked.
- [ ] **[5. Retrieve, then answer](phases/05-finding-the-right-thing-to-say/05-retrieve-then-answer/)** &nbsp;&middot;&nbsp; build the full pipeline, measure it against each half alone, and find that adding the model makes the system strictly worse.

<br>

## [Phase 6. Tools and agents](phases/06-tools-and-agents/)

*Five lessons. About four hours. Still nothing installed.*

- [ ] **[1. What a model cannot do](phases/06-tools-and-agents/01-what-a-model-cannot-do/)** &nbsp;&middot;&nbsp; measure a gap the model cannot close, then close it with three small programs, and notice that two of them are a different species from the third.
- [ ] **[2. Choosing the tool](phases/06-tools-and-agents/02-choosing-the-tool/)** &nbsp;&middot;&nbsp; write the rule anyone writes first, measure it, find the rule that fixes it, and then discover that your fix scored 100% because you wrote it with the answers in front of you.
- [ ] **[3. When it chooses wrong](phases/06-tools-and-agents/03-when-it-chooses-wrong/)** &nbsp;&middot;&nbsp; give each tool the power to refuse work, measure what that buys, and find that it rescues one failure out of five and cannot touch the other four.
- [ ] **[4. A loop that can stop](phases/06-tools-and-agents/04-a-loop-that-can-stop/)** &nbsp;&middot;&nbsp; add ten questions that have no answer, give the system a loop with three ways to stop, find that the retrying is worthless for a reason you could have proved in advance, and find that lesson 3 reached the wrong conclusion from a correct measurement.
- [ ] **[5. Measuring an agent](phases/06-tools-and-agents/05-measuring-an-agent/)** &nbsp;&middot;&nbsp; assemble the whole phase into one system, score three versions of it on six numbers instead of one, and work out the exact price at which the ranking flips.

<br>

## [Phase 7. Measuring whether any of it works](phases/07-measuring-whether-any-of-it-works/)

*Five lessons. About three hours. Still nothing installed.*

- [ ] **[1. The number has error bars](phases/07-measuring-whether-any-of-it-works/01-the-number-has-error-bars/)** &nbsp;&middot;&nbsp; compute exactly what each score in this course establishes, find that the course's own comparisons rest on nothing, and work out how many examples a claim actually needs.
- [ ] **[2. Is the difference real?](phases/07-measuring-whether-any-of-it-works/02-is-the-difference-real/)** &nbsp;&middot;&nbsp; compare the two agents question by question instead of total by total, find they disagree about eleven times, and watch the conclusion reverse depending on which outcome you count.
- [ ] **[3. The baseline you forgot](phases/07-measuring-whether-any-of-it-works/03-the-baseline-you-forgot/)** &nbsp;&middot;&nbsp; build the systems nobody builds, measure them against the agent five phases went into, and find that most of that agent cannot be shown to be doing anything.
- [ ] **[4. The test set you keep looking at](phases/07-measuring-whether-any-of-it-works/04-the-test-set-you-keep-looking-at/)** &nbsp;&middot;&nbsp; repeat that sweep against twenty questions written afterwards, find that the warning does not land the way you expect, and find the thing that actually broke.
- [ ] **[5. A test you can actually run](phases/07-measuring-whether-any-of-it-works/05-a-test-you-can-actually-run/)** &nbsp;&middot;&nbsp; watch a score-based test miss a change that moves a quarter of the questions, then write the test that catches it, and find that the whole thing rests on the system being deterministic.

<br>

## [Phase 8. Shipping: cost, latency, failure, safety](phases/08-shipping-cost-latency-failure-safety/)

*Five lessons. About three hours. Still nothing installed.*

- [ ] **[1. Counting the work](phases/08-shipping-cost-latency-failure-safety/01-counting-the-work/)** &nbsp;&middot;&nbsp; meter the system in units that do not depend on your laptop, find that its average describes a question that does not exist, and find that refusing to answer costs more than answering.
- [ ] **[2. When the corpus grows](phases/08-shipping-cost-latency-failure-safety/02-when-the-corpus-grows/)** &nbsp;&middot;&nbsp; build an inverted index, confirm it changes nothing, then take the obvious next step and watch a threshold in another phase silently change meaning.
- [ ] **[3. When something fails](phases/08-shipping-cost-latency-failure-safety/03-when-something-fails/)** &nbsp;&middot;&nbsp; take pieces out of the running agent, measure what each costs, and find that the catastrophic failure is the one no ordinary alarm can see.
- [ ] **[4. What it must not say](phases/08-shipping-cost-latency-failure-safety/04-what-it-must-not-say/)** &nbsp;&middot;&nbsp; put eight sentences in the corpus that must never come out, measure how many leak, and measure the two defences, one of which is the one everybody builds and does not work.
- [ ] **[5. The thing you ship](phases/08-shipping-cost-latency-failure-safety/05-the-thing-you-ship/)** &nbsp;&middot;&nbsp; assemble everything the course built, produce the page you would actually give somebody, and write down what the numbers do not establish.

<br>

## [Phase 9. Attention, and the block](phases/09-attention-and-the-block/)

*Five lessons. About four hours. Still nothing installed.*

- [ ] **[1. The thing a bigram cannot see](phases/09-attention-and-the-block/01-the-thing-a-bigram-cannot-see/)** &nbsp;&middot;&nbsp; train a bigram on the whole corpus, score it on the same corpus, and find it capped at exactly half. Not badly trained. Capped.
- [ ] **[2. Looking at every word at once](phases/09-attention-and-the-block/02-looking-at-every-word-at-once/)** &nbsp;&middot;&nbsp; write one attention head and its backward pass, clear the ceiling, and then find that the head is not doing what the story says it does.
- [ ] **[3. It works without looking](phases/09-attention-and-the-block/03-it-works-without-looking/)** &nbsp;&middot;&nbsp; find the signal by taking things away, and finish with a model that has no query and no key in it and scores within one question of the head.
- [ ] **[4. Where a word sits](phases/09-attention-and-the-block/04-where-a-word-sits/)** &nbsp;&middot;&nbsp; add a learned vector per position, then discover that the same model on the same number of examples either learns the order of ten things or learns nothing, depending on which examples it was shown.
- [ ] **[5. The block](phases/09-attention-and-the-block/05-the-block/)** &nbsp;&middot;&nbsp; build a transformer block by hand, prove its backward pass against finite differences, count what it costs, and discover that three seeds cannot tell any of these architectures apart.

<br>

<br>

---

<div align="center">

**Fifty lessons. Ten phases. About thirty-seven hours.**

Nothing installed, no account, no API key, no GPU, and no network at any point.

[Start at phase 0](phases/00-your-machine/) &nbsp;·&nbsp;
[Read the FAQ](FAQ.md) &nbsp;·&nbsp;
[Read the glossary](GLOSSARY.md)

</div>
