# What is AI, actually

"AI" gets used for three different things that nest inside each other, and most confusion about the field comes from not being clear which one is meant in a given sentence.

## The nesting

```
Artificial Intelligence  (the broad goal: machines doing tasks that seem to need intelligence)
  └── Machine Learning     (a way to get there: learn patterns from data instead of hand-coded rules)
        └── Deep Learning    (a way to do ML: learn patterns using layered neural networks)
```

- **AI** is the goal/category, not a technique — even a hand-written chess engine with explicit if/else rules and no learning at all is "AI" in the classical sense (this is what AI meant for decades before ML took over as the dominant approach).
- **Machine Learning** is a specific strategy for achieving AI: instead of a human writing the rules, the system infers rules (a function mapping input to output) from examples. Classic ML — linear regression, decision trees, SVMs — falls here.
- **Deep Learning** is a specific strategy for doing ML, using neural networks with many layers ("deep") to learn increasingly abstract representations of the input. This is what powers LLMs, image recognition, and most of what's called "AI" in the current wave.

## Why the distinction matters practically

When someone says "we should use AI for this," the actual decision space is much bigger than "use an LLM." A rules-based system might be the right call if the logic is genuinely well-understood and doesn't need to be learned from data (see [[09-choosing-the-right-ai-tool|choosing-the-right-ai-tool]]). A small classic-ML model (logistic regression, gradient-boosted trees) might beat a deep learning model on structured/tabular data, train in seconds instead of hours, and be far more interpretable. Deep learning — and LLMs specifically — earn their cost when the problem involves unstructured data (text, images, audio) or patterns too complex to hand-specify.

## Narrow vs general AI

- **Narrow AI** (aka weak AI): built for one task or a bounded family of tasks — a spam filter, a recommendation system, an LLM answering questions. Everything that exists today, including LLMs, is narrow AI, regardless of how general-purpose it feels in conversation.
- **General AI** (AGI): a system with human-level, general-purpose reasoning across arbitrary domains, without task-specific training. This doesn't exist yet — it's a research goal and a frequent source of hype-vs-reality confusion, since LLMs can *feel* general because language itself is general-purpose, without the underlying system actually reasoning the way a general intelligence would.

## How a model "learns" at the highest level

Regardless of whether it's classic ML or deep learning: you give the system a large number of (input, correct output) examples, it makes a guess, you measure how wrong the guess was (the **loss**), and you nudge the model's internal numbers (**parameters**) in the direction that would have made the guess less wrong. Repeat this millions of times and the parameters converge toward something that generalizes to inputs it's never seen. This is covered mechanically in [[02-what-is-a-model|what-is-a-model]] and [[04-optimization|optimization]] — this note is just the map of where that fits in the bigger picture.

## Gotchas

- Calling something "AI" says nothing about *how* it works — always ask "is this a hand-coded system, classic ML, or deep learning?" before reasoning about its behavior, cost, or failure modes, since those differ enormously between the three.
- "The AI understands X" is a loose shorthand almost everyone uses (this note included, elsewhere) — worth remembering that what's actually happening is closer to "the model's learned parameters produce outputs that correlate well with X," not literal understanding in the human sense. This matters for calibrating trust in model output.

## Related
- [[02-what-is-a-model|what-is-a-model]]
- [[03-llms|llms]]
- [[04-other-model-types|other-model-types]]
- [[09-choosing-the-right-ai-tool|choosing-the-right-ai-tool]]
