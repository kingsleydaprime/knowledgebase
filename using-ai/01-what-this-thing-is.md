# What This Thing Actually Is

**[Beginner]** — the vocabulary note. Assumes nothing. Read it once so the rest of this course has words to use.

## The kid version first

Imagine someone who has read almost everything ever written, remembers none of it exactly, and cannot look anything up. Ask them a question and they answer from a very strong sense of *how sentences like this usually go*. They're often right, because most of what's been written is roughly right. They're occasionally wrong in a way that sounds exactly as confident as when they're right — because to them, both feel the same.

That is a large language model. Not a database, not a search engine, not a person. A very well-read guesser.

Everything else in this course follows from that one sentence.

## Three words people use interchangeably (they shouldn't)

You'll hear "AI" used for three different things that sit inside each other:

```
Artificial Intelligence   the goal — machines doing things that seem to need intelligence
  └── Machine Learning      one way to get there — learn patterns from examples
        └── Deep Learning     one way to do that — layered networks; this is what powers ChatGPT
```

- **AI** is a category, not a technique. A chess program from 1985 with hand-written rules and no learning at all is AI.
- **Machine learning** means nobody wrote the rules. You show the system thousands of examples and it works out the pattern itself.
- **Deep learning** is the specific flavour behind the current wave — the thing you're chatting with.

Why bother distinguishing? Because "we used AI" tells you nothing about whether a system is trustworthy, expensive, or predictable. Those differ enormously across the three. When a company says their product "uses AI," the honest follow-up is *"which kind, and for what part?"*

## What "the model" means

A **model** is a very large mathematical function with billions of adjustable numbers inside it. Those numbers started as random noise. Training nudged them, over months and enormous expense, toward values that make the model's output resemble the text it was trained on.

Two phases, wildly different, constantly confused:

| | **Training** | **Inference** |
|---|---|---|
| What happens | The model's internal numbers get adjusted | The finished model produces an answer |
| When | Once, before you ever touch it | Every single time you press enter |
| Cost | Months of computing, millions of dollars | Cents or fractions of a cent |
| Does your chat change it? | **No** | — |

That last row matters more than it looks. When you correct a model in conversation, you have not taught it anything. It will make the same mistake tomorrow in a fresh chat. Whatever it "learns" from you inside a session lives only in that session — the model itself is frozen.

(Separately, some products *store* your conversations to help train a *future* version. That's a privacy question, not a learning one — [[using-ai/07-privacy-and-what-not-to-share|note 07]].)

## Narrow vs general — where we actually are

- **Narrow AI**: built for one task or a bounded family of them. A spam filter. A recommendation feed. An LLM answering questions.
- **General AI (AGI)**: human-level reasoning across arbitrary domains. Doesn't exist.

Everything available today is narrow — *including* the chatbots, however general they feel. They feel general because **language itself is general-purpose**. A tool that handles text can appear to handle everything, since almost anything can be discussed in text. Appearing to handle it and handling it are different.

This is the single most common calibration error people make, and it runs in both directions: overestimating the model on things it's merely fluent about, and underestimating it on things it's genuinely excellent at.

## The hype filter

Three claims worth being suspicious of, and what's usually behind them:

| The claim | What's usually true |
|---|---|
| "Our AI understands your business" | It generates text conditioned on some documents you uploaded |
| "The AI decided X" | Someone chose to act on a model's output; the accountability is still human |
| "It's basically thinking" | It is producing the tokens that tend to follow tokens like these |

None of those are lies exactly. They're compressions that hide the thing you'd need to know in order to judge the output.

## Key insight

An LLM is not a system that knows things and reports them. It is a system that produces plausible text. Most of the time, plausible and true overlap heavily — which is precisely why the gap between them is so easy to miss, and why [[using-ai/06-verifying-what-it-tells-you|checking its work]] is a skill rather than an insult.

## Related
- [[using-ai/02-how-llms-work-plainly|How LLMs Work, Plainly]] — the mechanism behind the guessing
- [[using-ai/06-verifying-what-it-tells-you|Verifying What It Tells You]] — what to do about confident wrongness
- [[ai-ml/00-foundations/01-what-is-ai|What is AI, actually]] — the same map, written for someone who'll build with it
- [[ai-ml/00-foundations/02-what-is-a-model|What is a Model]] — parameters, training, generalization, in more depth
