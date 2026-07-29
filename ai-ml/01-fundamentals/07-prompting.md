# Prompting

A prompt is the entire input a model sees before it starts generating — instructions, context, examples, the actual question. Prompting is the skill of shaping that input so the model's next-token predictions (see [[03-llms|llms]]) land on what you actually want, instead of something plausible-but-off. It's not magic incantation — it works because it's genuinely giving the model more/better information to condition its predictions on.

## Why prompting works at all

An LLM predicts the next token based on everything in its context so far (see [[03-llms|llms]]). A vague prompt gives the model many equally plausible directions to go; a well-specified prompt narrows that space dramatically. "Write about dogs" and "write a 200-word product description for a durable dog leash, in a playful tone, for an Instagram caption" are the same underlying mechanism, but the second gives the model far less room to guess wrong about what you actually wanted.

## System prompt vs user prompt

Most chat-style models distinguish a **system prompt** (persistent instructions about role, tone, constraints, set once for the whole conversation) from the **user prompt** (the actual per-turn request). Put stable, general instructions ("you are a terse code reviewer," "always answer in French") in the system prompt; put the specific task in the user prompt. Mixing them (re-stating role instructions in every user message) works but is redundant and wastes context budget.

## Few-shot prompting — showing instead of telling

Rather than describing the desired output format abstractly, giving the model 1-3 concrete examples of (input, ideal output) pairs directly in the prompt is often more reliable than a paragraph of instructions — the model pattern-matches against the examples the same way it pattern-matches against anything else in its context.

```
Classify the sentiment of these reviews.

Review: "This product broke after two days."
Sentiment: Negative

Review: "Exactly what I needed, works perfectly."
Sentiment: Positive

Review: "Shipping was slow but the product itself is fine."
Sentiment:
```

The model completes this the same way it completes any text — by pattern-matching the shape of what came before — so consistent formatting in the examples matters more than exhaustive explanation.

## Being specific about format and constraints

Models will guess at ambiguous requirements rather than ask for clarification (unless explicitly told to). Stating the output format explicitly ("respond with only valid JSON matching this schema," "answer in exactly 3 bullet points") removes an entire class of failure where the model produces a reasonable-but-wrong-shaped answer.

## Chain-of-thought — letting the model "think" before answering

Asking a model to reason step by step before giving a final answer ("think through this step by step," or a dedicated reasoning/thinking mode where available) measurably improves accuracy on multi-step problems (math, logic, multi-constraint tasks). This works because each intermediate reasoning token becomes part of the context the model conditions on for the next token — reasoning out loud gives the model's own output a scaffold to build the final answer on, rather than forcing it to jump straight to a conclusion in one shot.

## Common failure modes and what actually fixes them

- **Vague output** → be more specific about format, length, audience, tone; give an example.
- **Model ignores part of a long, complex instruction** → break the request into smaller, sequential steps instead of one dense paragraph — this is often more effective than just repeating the missed instruction.
- **Model states something confidently wrong** → this is a knowledge/grounding problem, not a phrasing problem (see the hallucination note in [[03-llms|llms]]) — the fix is usually giving the model the actual source material to work from (pasting the relevant text, or using an agent with search/retrieval, see [[06-agents|agents]]) rather than trusting it to recall the fact correctly.
- **Inconsistent output across runs** → this is expected due to sampling (see [[01-distributions|distributions]]); lowering temperature or setting a fixed seed (where supported) makes output more deterministic, at some cost to creative variation.

## Gotchas

- Overly long, over-qualified prompts can dilute focus — a prompt stuffed with 15 caveats often gets several of them dropped, versus 3-4 clear priorities being reliably followed.
- Prompting can't fix a fundamental capability gap — no amount of prompt engineering makes a small model reliably do something well outside its training/capability range; that's a model-choice problem (see [[09-choosing-the-right-ai-tool|choosing-the-right-ai-tool]]), not a prompting problem.

## Related
- [[03-llms|llms]]
- [[06-agents|agents]]
- [[09-choosing-the-right-ai-tool|choosing-the-right-ai-tool]]
