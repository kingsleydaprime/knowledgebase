---
id: 187436d2-61b1-449f-a8c2-581915509757
---

# What is AI, actually

AI means three different things that sit inside each other.

## What AI is
<!-- bite: 0bcbd5c7-8096-4820-a6c1-ffc9f3525317 -->

"AI" gets used for three different things that nest inside each other, and most confusion about the field comes from not being clear which one is meant in a given sentence.

The next bite shows the three, one inside the other.

## The nesting
<!-- bite: 07b8f085-f632-4018-8569-6f623f42b15d -->

```text
Artificial Intelligence  (the broad goal: machines doing tasks that seem to need intelligence)
  └── Machine Learning     (a way to get there: learn patterns from data instead of hand-coded rules)
        └── Deep Learning    (a way to do ML: learn patterns using layered neural networks)
```

- **AI** is the goal/category, not a technique — even a hand-written chess engine with explicit if/else rules and no learning at all is "AI" in the classical sense (this is what AI meant for decades before ML took over as the dominant approach).
- **Machine Learning** is a specific strategy for achieving AI: instead of a human writing the rules, the system infers rules (a function mapping input to output) from examples. Classic ML — linear regression, decision trees, SVMs — falls here.
- **Deep Learning** is a specific strategy for doing ML, using neural networks with many layers ("deep") to learn increasingly abstract representations of the input. This is what powers LLMs, image recognition, and most of what's called "AI" in the current wave.

## Why the distinction matters practically
<!-- bite: 115023a0-6d3e-43fd-bb97-31f3e76e9e39 -->

When someone says "we should use AI for this," the actual decision space is much bigger than "use an LLM." A rules-based system might be the right call if the logic is genuinely well-understood and doesn't need to be learned from data (see [[ai-engineering/01-the-ai-engineer-role|choosing-the-right-ai-tool]]). A small classic-ML model (logistic regression, gradient-boosted trees) might beat a deep learning model on structured/tabular data, train in seconds instead of hours, and be far more interpretable. Deep learning — and LLMs specifically — earn their cost when the problem involves unstructured data (text, images, audio) or patterns too complex to hand-specify.

## Narrow vs general AI
<!-- bite: 64e64e4a-e734-4a04-bdc8-3beb401a9479 -->

- **Narrow AI** (aka weak AI): built for one task or a bounded family of tasks — a spam filter, a recommendation system, an LLM answering questions. Everything that exists today, including LLMs, is narrow AI, regardless of how general-purpose it feels in conversation.
- **General AI** (AGI): a system with human-level, general-purpose reasoning across arbitrary domains, without task-specific training. This doesn't exist yet — it's a research goal and a frequent source of hype-vs-reality confusion, since LLMs can *feel* general because language itself is general-purpose, without the underlying system actually reasoning the way a general intelligence would.

## How a model "learns" at the highest level
<!-- bite: 30a28128-8150-4356-9d5a-5566cedb858f -->

Regardless of whether it's classic ML or deep learning: you give the system a large number of (input, correct output) examples, it makes a guess, you measure how wrong the guess was (the **loss**), and you nudge the model's internal numbers (**parameters**) in the direction that would have made the guess less wrong. Repeat this millions of times and the parameters converge toward something that generalizes to inputs it's never seen. This is covered mechanically in [[machine-learning/00-foundations/02-what-is-a-model|what-is-a-model]] and [[04-optimization|optimization]] — this note is just the map of where that fits in the bigger picture.

## Gotchas
<!-- bite: 15c5208f-9fe6-4da9-aa81-4f4511d60560 -->

- Calling something "AI" says nothing about *how* it works — always ask "is this a hand-coded system, classic ML, or deep learning?" before reasoning about its behavior, cost, or failure modes, since those differ enormously between the three.
- "The AI understands X" is a loose shorthand almost everyone uses (this note included, elsewhere) — worth remembering that what's actually happening is closer to "the model's learned parameters produce outputs that correlate well with X," not literal understanding in the human sense. This matters for calibrating trust in model output.

## Check your understanding
<!-- bite: 85c5ee68-00fe-4c2f-a489-633a704118f3 -->

Try each one before you open the answer.

1. <!-- q: gap id="994f1705" answers="machine learning|ml;deep learning|dl" -->
   Fill in the gaps. AI is the broad goal. ___ is one way to get there, by learning patterns from data. ___ is one way to do that, using layered neural networks.

   <details><summary>Answer</summary>

   Machine learning, then deep learning. They sit inside each other: deep learning is inside machine learning, and machine learning is inside AI.

   </details>

2. <!-- q: mcq id="26b084ba" -->
   A chess engine plays using only if/else rules a programmer wrote by hand. It learns nothing from data. What is it?

   - [x] AI, but not machine learning
   - [ ] Machine learning, but not deep learning
   - [ ] Deep learning
   - [ ] Not AI at all

   <details><summary>Answer</summary>

   AI, but not machine learning. AI is the goal, not a technique. A hand-written rules system still counts as AI in the classical sense, but nothing was learned from data, so it isn't ML.

   </details>

3. <!-- q: mcq id="d2d03d96" -->
   Which kind of AI exists today, including LLMs?

   - [x] Narrow AI
   - [ ] General AI (AGI)

   <details><summary>Answer</summary>

   Narrow AI. Everything that exists today is built for one task or a bounded family of tasks. LLMs feel general because language is general-purpose, but AGI is still a research goal.

   </details>

4. <!-- q: gap id="09c749fd" answers="loss;parameters|parameter|weights" -->
   Fill in the gaps. The model makes a guess, we measure how wrong it was (the ___), and we nudge the model's internal numbers (the ___) so the next guess is less wrong.

   <details><summary>Answer</summary>

   Loss, then parameters. Repeat that millions of times and the parameters settle on values that work for inputs the model has never seen.

   </details>

5. <!-- q: open id="86536574" -->
   Someone says "let's use AI for this". Why is it worth asking whether they mean a rules system, classic ML or deep learning?

   <details><summary>Answer</summary>

   Because the three work differently, cost differently and fail differently. A rules system may be right when the logic is already well understood. A small classic ML model can beat deep learning on tabular data, train in seconds and be easier to explain. Deep learning earns its cost on unstructured data like text, images and audio.

   </details>

## Related
<!-- bite: 0b7335a4-e942-4f75-b338-6ce572cf4eb9 -->
- [[machine-learning/00-foundations/02-what-is-a-model|what-is-a-model]]
- [[ai-engineering/02-how-llms-work/index|llms]]
- [[ai-engineering/03-the-model-landscape|other-model-types]]
- [[ai-engineering/01-the-ai-engineer-role|choosing-the-right-ai-tool]]
