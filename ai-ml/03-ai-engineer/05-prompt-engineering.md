# Prompt Engineering

**Source:** re-homed from the old `01-fundamentals/07-prompting.md`, deepened with the [roadmap.sh prompt-engineering](https://roadmap.sh/prompt-engineering) techniques (role prompting, self-consistency, step-back, structured output, context engineering).

A prompt is the entire input a model sees before generating — instructions, context, examples, the question. Prompt engineering is shaping that input so the model's next-token predictions ([[ai-ml/03-ai-engineer/02-how-llms-work|how LLMs work]]) land on what you want. It's not incantation — it works because it genuinely gives the model more/better information to condition on.

## Why it works

An LLM predicts the next token from everything in context. A vague prompt leaves many plausible directions; a specific one collapses that space. "Write about dogs" vs "write a 200-word product description for a durable dog leash, playful tone, for an Instagram caption" is the same mechanism — the second just leaves far less room to guess wrong.

## System vs user prompts (and roles)

Chat models separate a **system prompt** (persistent role/tone/constraints, set once) from **user prompts** (per-turn requests). Put stable instructions ("you are a terse code reviewer," "always answer in JSON") in the system prompt; put the specific task in the user prompt. Re-stating role instructions every turn works but wastes [[ai-ml/03-ai-engineer/02-how-llms-work|context budget]]. **Role prompting** ("you are an expert epidemiologist") is a lightweight lever that shifts vocabulary and framing.

## Core techniques

- **Zero-shot** — just ask, no examples. The default; often enough for capable models.
- **Few-shot** — give 1–3 concrete (input → ideal output) examples. Often more reliable than describing the format abstractly, because the model pattern-matches the examples:

```
Classify sentiment.
Review: "Broke after two days."  → Negative
Review: "Exactly what I needed." → Positive
Review: "Shipping was slow but the product is fine." →
```

  Consistent formatting in the examples matters more than exhaustive explanation.
- **Be explicit about format/constraints** — models guess at ambiguity rather than ask. "Respond with only valid JSON matching this schema," "exactly 3 bullet points" removes a whole class of reasonable-but-wrong-shaped answers. (For hard guarantees, use [[ai-ml/03-ai-engineer/04-calling-models|structured-output APIs]] rather than hoping the prose prompt holds.)
- **Chain-of-thought (CoT)** — "think step by step" (or a reasoning model's thinking mode) measurably improves multi-step accuracy: each intermediate reasoning token becomes context the final answer builds on, instead of forcing a one-shot leap.
- **Self-consistency** — sample several CoT runs and take the majority answer; trades cost for reliability on hard problems.
- **Step-back prompting** — ask the model to first state the general principle, then apply it — helps on problems where jumping straight in goes wrong.

## Prompt vs context engineering

As systems grow, the harder problem shifts from wording a single prompt to **context engineering** — deciding *what information* to put in the window and in what order: retrieved documents ([[ai-ml/03-ai-engineer/06-rag-and-embeddings|RAG]]), tool results, conversation history, few-shot examples. Given a fixed [[ai-ml/03-ai-engineer/02-how-llms-work|context window]], curating the most relevant context (and compacting/summarizing the rest) often matters more than clever phrasing.

## Common failure modes → the actual fix

- **Vague output** → be more specific about format/length/audience; give an example.
- **Ignores part of a long instruction** → break it into smaller sequential steps rather than one dense paragraph; over-stuffed prompts (15 caveats) reliably drop several.
- **Confidently wrong** → this is a *grounding* problem, not phrasing ([[ai-ml/03-ai-engineer/02-how-llms-work|hallucination]]) — give it the source material ([[ai-ml/03-ai-engineer/06-rag-and-embeddings|RAG]]) rather than trusting recall.
- **Inconsistent across runs** → expected [[ai-ml/03-ai-engineer/02-how-llms-work|sampling]] behavior; lower temperature or fix a seed.

## Gotchas

- Prompting can't fix a capability gap — no phrasing makes a small model reliably do something outside its range; that's a [[ai-ml/03-ai-engineer/01-the-ai-engineer-role|model-choice]] problem.
- User-supplied text inside a prompt is an attack surface — **prompt injection** ([[ai-ml/03-ai-engineer/10-safety-and-production|safety]]) is when that text overrides your instructions. Never trust interpolated input as if it were your own system prompt.

## Related
- [[ai-ml/03-ai-engineer/02-how-llms-work|How LLMs Work]] — why conditioning on better context works
- [[ai-ml/03-ai-engineer/06-rag-and-embeddings|RAG & Embeddings]] — grounding as the fix for hallucination
- [[ai-ml/03-ai-engineer/10-safety-and-production|Safety & Production]] — prompt injection
