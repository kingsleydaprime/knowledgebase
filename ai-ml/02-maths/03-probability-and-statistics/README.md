# Probability & Statistics for AI/ML

Where linear algebra gives ML its data representation and calculus gives it the mechanism for learning, probability and statistics give it the vocabulary for **uncertainty** — which matters because almost nothing a model outputs is a certainty. An LLM doesn't pick "the" next word, it picks from a probability distribution over possible next words; a classifier doesn't say "this is a cat," it says "97% cat."

## Reading order
1. [[01-distributions|distributions]] — **[Beginner]** — the normal distribution, discrete vs continuous, how LLM token sampling works
2. [[02-expectation-and-variance|expectation-and-variance]] — **[Beginner]** — mean and spread, why both matter for evaluating a model honestly
3. [[03-bayes-theorem|bayes-theorem]] — **[Intermediate]** — conditional probability, and flipping "evidence given hypothesis" into "hypothesis given evidence"

## Why loss functions are built on probability

Training a classifier usually means training it to output something that behaves like a probability distribution over possible classes (summing to 1 across all classes — see [[01-distributions|distributions]]). The standard loss function for this, **cross-entropy loss**, comes directly from probability theory: it measures how far the model's predicted probability distribution is from the true one (which puts 100% on the correct answer). "Minimize cross-entropy loss" is literally "make the model's probability estimates as close to certain-and-correct as possible" — the gradient descent machine in [[04-optimization|optimization]] grinds toward this using the derivatives covered in the calculus notes.

## Why LLM output looks the way it does

Every token an LLM generates comes from a probability distribution over its entire vocabulary (see [[01-distributions|distributions]]) — the model computes "given everything so far, how likely is each possible next token," and a sampling strategy picks one. This is why the same prompt can give different outputs on different runs, and why "temperature" changes how random vs. predictable the output feels.

## Gotchas

- A model reporting "97% confidence" is reporting its *own* estimated probability, which is not the same as it actually being right 97% of the time — see the calibration gotcha in [[02-expectation-and-variance|expectation-and-variance]].
- Average performance hides variance — see [[02-expectation-and-variance|expectation-and-variance]] for why the mean alone can hide a model that's usually great but occasionally catastrophic.

## Related
- [[04-optimization|optimization]] — loss functions are built on these ideas
- [[03-llms|llms]] — token sampling is exactly a probability distribution in action
- [[02-what-is-a-model|what-is-a-model]]
